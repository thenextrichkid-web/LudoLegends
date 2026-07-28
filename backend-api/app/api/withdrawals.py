import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.wallet import Wallet, WalletTransaction, TransactionType
from app.models.withdrawal import WithdrawalRequest, WithdrawalStatus
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/withdrawals", tags=["withdrawals"])


class WithdrawalCreate(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: str
    payment_details: str


class WithdrawalResponse(BaseModel):
    id: str
    amount: float
    status: str
    payment_method: str | None
    payment_details: str | None
    rejection_reason: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=WithdrawalResponse)
async def create_withdrawal(body: WithdrawalCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == user.id))
    wallet = wallet_result.scalar_one_or_none()
    if not wallet or wallet.balance < body.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

    balance_before = wallet.balance
    wallet.balance -= body.amount
    wallet.frozen += body.amount
    wallet.total_withdrawn += body.amount

    tx = WalletTransaction(
        id=str(uuid.uuid4()),
        wallet_id=wallet.id,
        type=TransactionType.WITHDRAWAL,
        amount=body.amount,
        balance_before=balance_before,
        balance_after=wallet.balance,
        description=f"Withdrawal request via {body.payment_method}",
    )
    db.add(tx)

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
async def my_withdrawals(page: int = 1, per_page: int = 20, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * per_page
    result = await db.execute(
        select(WithdrawalRequest)
        .where(WithdrawalRequest.user_id == user.id)
        .order_by(WithdrawalRequest.created_at.desc())
        .offset(offset).limit(per_page)
    )
    return list(result.scalars().all())
