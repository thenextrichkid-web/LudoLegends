"""Wallet and transaction Pydantic schemas."""

from pydantic import BaseModel, Field
from datetime import datetime


class WalletResponse(BaseModel):
    """Wallet balance response."""
    id: str
    balance: float
    frozen: float
    total_deposited: float
    total_withdrawn: float
    total_earned: float

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    """Wallet transaction response."""
    id: str
    type: str
    amount: float
    balance_before: float
    balance_after: float
    reference_id: str | None
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class DepositRequest(BaseModel):
    """Deposit funds request."""
    amount: float = Field(..., gt=0, description="Amount to deposit")
    payment_method: str = Field(..., description="Payment method (e.g., 'upi', 'card')")
