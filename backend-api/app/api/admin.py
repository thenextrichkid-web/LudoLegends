import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.middleware.auth import get_admin_user, get_super_admin_user
from app.models.user import User, UserRole
from app.models.wallet import Wallet, WalletTransaction, TransactionType
from app.models.withdrawal import WithdrawalRequest, WithdrawalStatus
from app.models.deposit import DepositRequest, DepositStatus
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/dashboard")
async def admin_dashboard(user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func

    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_wallets = (await db.execute(select(func.sum(Wallet.balance)))).scalar() or 0
    pending_withdrawals = (await db.execute(
        select(func.count(WithdrawalRequest.id)).where(WithdrawalRequest.status == WithdrawalStatus.PENDING)
    )).scalar() or 0
    pending_deposits = (await db.execute(
        select(func.count(DepositRequest.id)).where(DepositRequest.status == DepositStatus.PENDING)
    )).scalar() or 0

    return {
        "total_users": total_users,
        "total_wallet_balance": total_wallets,
        "pending_withdrawals": pending_withdrawals,
        "pending_deposits": pending_deposits,
    }


@router.get("/users")
async def list_users(page: int = 1, per_page: int = 20, user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * per_page
    result = await db.execute(select(User).order_by(User.created_at.desc()).offset(offset).limit(per_page))
    users = result.scalars().all()
    total = (await db.execute(select(User))).scalar() or 0
    return {
        "users": [
            {
                "id": u.id, "phone": u.phone, "name": u.name, "email": u.email,
                "role": u.role.value if hasattr(u.role, 'value') else u.role,
                "vip_level": u.vip_level, "total_earnings": u.total_earnings,
                "total_matches": u.total_matches, "total_wins": u.total_wins,
                "is_active": u.is_active, "created_at": str(u.created_at),
            }
            for u in users
        ],
        "total": total,
    }


@router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, role: str, user: User = Depends(get_super_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.role = UserRole(role)
    await db.commit()
    return {"message": f"Role updated to {role}"}


@router.put("/users/{user_id}/status")
async def toggle_user_status(user_id: str, user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.is_active = not target.is_active
    await db.commit()
    return {"message": f"User {'activated' if target.is_active else 'deactivated'}", "is_active": target.is_active}


@router.get("/withdrawals")
async def list_withdrawals(status_filter: str = "pending", page: int = 1, per_page: int = 20, user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * per_page
    query = select(WithdrawalRequest)
    if status_filter != "all":
        query = query.where(WithdrawalRequest.status == WithdrawalStatus(status_filter))
    query = query.order_by(WithdrawalRequest.created_at.desc()).offset(offset).limit(per_page)
    result = await db.execute(query)
    withdrawals = result.scalars().all()
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
    }


@router.post("/withdrawals/{withdrawal_id}/approve")
async def approve_withdrawal(withdrawal_id: str, user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WithdrawalRequest).where(WithdrawalRequest.id == withdrawal_id))
    withdrawal = result.scalar_one_or_none()
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    if withdrawal.status != WithdrawalStatus.PENDING:
        raise HTTPException(status_code=400, detail="Withdrawal already processed")

    withdrawal.status = WithdrawalStatus.APPROVED
    withdrawal.reviewed_by = user.id
    withdrawal.reviewed_at = datetime.now(timezone.utc)

    wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == withdrawal.user_id))
    wallet = wallet_result.scalar_one_or_none()
    if wallet:
        wallet.frozen -= withdrawal.amount

    await db.commit()
    return {"message": "Withdrawal approved"}


@router.post("/withdrawals/{withdrawal_id}/reject")
async def reject_withdrawal(withdrawal_id: str, reason: str = "", user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WithdrawalRequest).where(WithdrawalRequest.id == withdrawal_id))
    withdrawal = result.scalar_one_or_none()
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    if withdrawal.status != WithdrawalStatus.PENDING:
        raise HTTPException(status_code=400, detail="Withdrawal already processed")

    withdrawal.status = WithdrawalStatus.REJECTED
    withdrawal.reviewed_by = user.id
    withdrawal.reviewed_at = datetime.now(timezone.utc)
    withdrawal.rejection_reason = reason

    wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == withdrawal.user_id))
    wallet = wallet_result.scalar_one_or_none()
    if wallet:
        wallet.frozen -= withdrawal.amount
        wallet.balance += withdrawal.amount

        tx = WalletTransaction(
            id=str(uuid.uuid4()), wallet_id=wallet.id,
            type=TransactionType.REFUND, amount=withdrawal.amount,
            balance_before=wallet.balance - withdrawal.amount,
            balance_after=wallet.balance,
            description=f"Withdrawal rejected - refund: {reason}",
        )
        db.add(tx)

    await db.commit()
    return {"message": "Withdrawal rejected, balance refunded"}
