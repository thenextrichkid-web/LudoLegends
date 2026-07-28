"""Admin API endpoints — dashboard, user management, withdrawal processing."""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.middleware.auth import get_admin_user, get_super_admin_user
from app.models.user import User, UserRole
from app.models.wallet import Wallet, WalletTransaction, TransactionType
from app.models.withdrawal import WithdrawalRequest, WithdrawalStatus
from app.models.deposit import DepositRequest as DepositRequestModel, DepositStatus
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/dashboard")
async def admin_dashboard(
    user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get admin dashboard stats."""
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_wallets = (await db.execute(select(func.sum(Wallet.balance)))).scalar() or 0
    pending_withdrawals = (await db.execute(
        select(func.count(WithdrawalRequest.id)).where(WithdrawalRequest.status == WithdrawalStatus.PENDING)
    )).scalar() or 0
    pending_deposits = (await db.execute(
        select(func.count(DepositRequestModel.id)).where(DepositRequestModel.status == DepositStatus.PENDING)
    )).scalar() or 0

    return {
        "total_users": total_users,
        "total_wallet_balance": total_wallets,
        "pending_withdrawals": pending_withdrawals,
        "pending_deposits": pending_deposits,
    }


@router.get("/users")
async def list_users(
    page: int = 1,
    per_page: int = 20,
    user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List all users with pagination."""
    offset = (page - 1) * per_page
    result = await db.execute(select(User).order_by(User.created_at.desc()).offset(offset).limit(per_page))
    users = result.scalars().all()
    total = (await db.execute(select(func.count(User.id)))).scalar() or 0
    return {
        "users": [
            {
                "id": u.id, "phone": u.phone, "name": u.name, "email": u.email,
                "role": u.role.value if hasattr(u.role, 'value') else u.role,
                "vip_level": u.vip_level, "total_earnings": u.total_earnings,
                "total_matches": int(u.total_matches), "total_wins": int(u.total_wins),
                "is_active": u.is_active, "created_at": str(u.created_at),
            }
            for u in users
        ],
        "total": total,
    }


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: str,
    user: User = Depends(get_super_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a user's role (super admin only)."""
    try:
        user_role = UserRole(role)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role: {role}")

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    target.role = user_role
    await db.commit()
    return {"message": f"Role updated to {role}"}


@router.put("/users/{user_id}/status")
async def toggle_user_status(
    user_id: str,
    user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a user's active status."""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if target.id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate yourself")

    target.is_active = not target.is_active
    await db.commit()
    return {"message": f"User {'activated' if target.is_active else 'deactivated'}", "is_active": target.is_active}


@router.get("/withdrawals")
async def list_withdrawals(
    status_filter: str = "pending",
    page: int = 1,
    per_page: int = 20,
    user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List withdrawal requests for admin review."""
    try:
        status_enum = WithdrawalStatus(status_filter) if status_filter != "all" else None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status filter: {status_filter}. Use: pending, approved, rejected, processed, all",
        )
    offset = (page - 1) * per_page
    query = select(WithdrawalRequest)
    if status_enum is not None:
        query = query.where(WithdrawalRequest.status == status_enum)
    query = query.order_by(WithdrawalRequest.created_at.desc()).offset(offset).limit(per_page)
    result = await db.execute(query)
    withdrawals = result.scalars().all()

    count_query = select(func.count(WithdrawalRequest.id))
    if status_enum is not None:
        count_query = count_query.where(WithdrawalRequest.status == status_enum)
    total = (await db.execute(count_query)).scalar() or 0

    return {
        "withdrawals": [
            {
                "id": w.id, "user_id": w.user_id, "amount": w.amount,
                "status": w.status.value, "payment_method": w.payment_method,
                "payment_details": w.payment_details, "rejection_reason": w.rejection_reason,
                "created_at": str(w.created_at),
            }
            for w in withdrawals
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.post("/withdrawals/{withdrawal_id}/approve")
async def approve_withdrawal(
    withdrawal_id: str,
    user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a withdrawal request. Creates a WITHDRAWAL_PROCESSED transaction."""
    result = await db.execute(select(WithdrawalRequest).where(WithdrawalRequest.id == withdrawal_id))
    withdrawal = result.scalar_one_or_none()
    if not withdrawal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Withdrawal not found")
    if withdrawal.status != WithdrawalStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Withdrawal already processed")

    withdrawal.status = WithdrawalStatus.APPROVED
    withdrawal.reviewed_by = user.id
    withdrawal.reviewed_at = datetime.now(timezone.utc)

    wallet_svc = WalletService(db)
    await wallet_svc.unfreeze(withdrawal.user_id, withdrawal.amount)

    # Create a transaction record for the processed withdrawal
    wallet = await wallet_svc.get_or_create_wallet(withdrawal.user_id)
    tx = WalletTransaction(
        id=str(uuid.uuid4()),
        wallet_id=wallet.id,
        type=TransactionType.WITHDRAWAL,
        amount=withdrawal.amount,
        balance_before=wallet.balance,
        balance_after=wallet.balance,
        reference_id=withdrawal_id,
        description=f"Withdrawal approved via {withdrawal.payment_method}",
    )
    db.add(tx)

    await db.commit()
    return {"message": "Withdrawal approved"}


@router.post("/withdrawals/{withdrawal_id}/reject")
async def reject_withdrawal(
    withdrawal_id: str,
    reason: str = "",
    user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject a withdrawal request. Returns frozen funds to user balance."""
    result = await db.execute(select(WithdrawalRequest).where(WithdrawalRequest.id == withdrawal_id))
    withdrawal = result.scalar_one_or_none()
    if not withdrawal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Withdrawal not found")
    if withdrawal.status != WithdrawalStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Withdrawal already processed")

    withdrawal.status = WithdrawalStatus.REJECTED
    withdrawal.reviewed_by = user.id
    withdrawal.reviewed_at = datetime.now(timezone.utc)
    withdrawal.rejection_reason = reason

    wallet_svc = WalletService(db)
    await wallet_svc.refund(withdrawal.user_id, withdrawal.amount)

    # Create a refund transaction record
    wallet = await wallet_svc.get_or_create_wallet(withdrawal.user_id)
    tx = WalletTransaction(
        id=str(uuid.uuid4()),
        wallet_id=wallet.id,
        type=TransactionType.REFUND,
        amount=withdrawal.amount,
        balance_before=wallet.balance - withdrawal.amount,
        balance_after=wallet.balance,
        reference_id=withdrawal_id,
        description=f"Withdrawal rejected: {reason}" if reason else "Withdrawal rejected",
    )
    db.add(tx)

    await db.commit()
    return {"message": "Withdrawal rejected, balance refunded"}
