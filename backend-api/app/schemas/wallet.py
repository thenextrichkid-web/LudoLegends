from pydantic import BaseModel, Field
from datetime import datetime


class WalletResponse(BaseModel):
    id: str
    balance: float
    frozen: float
    total_deposited: float
    total_withdrawn: float
    total_earned: float

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
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
    amount: float = Field(..., gt=0)
    payment_method: str


class WithdrawalRequest(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: str
    payment_details: str


class WithdrawalAction(BaseModel):
    action: str = Field(..., pattern=r"^(approve|reject)$")
    rejection_reason: str | None = None
