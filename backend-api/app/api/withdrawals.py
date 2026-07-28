"""Withdrawal request API endpoints."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.withdrawal import WithdrawalRequest, WithdrawalStatus
from app.services.wallet_service import WalletService
from app.schemas.withdrawal import WithdrawalCreate, WithdrawalResponse

router = APIRouter(prefix="/api/withdrawals", tags=["withdrawals"])


@router.post("/", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
async def create_withdrawal(
    body: WithdrawalCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a withdrawal request. Freezes the amount in the user's wallet."""
    wallet_svc = WalletService(db)

    try:
        tx = await wallet_svc.withdraw(
            user.id,
            body.amount,
            description=f"Withdrawal request via {body.payment_method}",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    withdrawal = WithdrawalRequest(
        id=str(uuid.uuid4()),
        user_id=user.id,
        amount=body.amount,
        payment_method=body.payment_method,
        payment_details=body.payment_details,
    )
    db.add(withdrawal)
    await db.commit()
    await db.refresh(withdrawal)
    return withdrawal


@router.get("/", response_model=list[WithdrawalResponse])
async def my_withdrawals(
    page: int = 1,
    per_page: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List the current user's withdrawal requests."""
    offset = (page - 1) * per_page
    result = await db.execute(
        select(WithdrawalRequest)
        .where(WithdrawalRequest.user_id == user.id)
        .order_by(WithdrawalRequest.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    return list(result.scalars().all())
