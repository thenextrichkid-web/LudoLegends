"""Wallet API endpoints — balance, deposit, transactions."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.wallet_service import WalletService
from app.schemas.wallet import WalletResponse, TransactionResponse, DepositRequest
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/wallet", tags=["wallet"])


@router.get("/", response_model=WalletResponse)
async def get_wallet(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's wallet balance."""
    svc = WalletService(db)
    return await svc.get_balance(user.id)


@router.post("/deposit", status_code=status.HTTP_200_OK)
async def deposit(
    body: DepositRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deposit funds into the user's wallet."""
    svc = WalletService(db)
    try:
        tx = await svc.deposit(user.id, body.amount, description=f"Deposit via {body.payment_method}")
        return {"message": "Deposit successful", "transaction_id": tx.id, "balance": tx.balance_after}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    page: int = 1,
    per_page: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated wallet transaction history."""
    svc = WalletService(db)
    txs, total = await svc.get_transactions(user.id, page, per_page)
    return txs
