from pydantic import BaseModel, Field
from datetime import datetime


class WithdrawalCreate(BaseModel):
    """Schema for creating a new withdrawal request."""
    amount: float = Field(..., gt=0, description="Amount to withdraw")
    payment_method: str = Field(..., description="Payment method: 'upi' or 'bank'")
    payment_details: str = Field(..., min_length=1, description="UPI ID or bank account details")


class WithdrawalResponse(BaseModel):
    """Schema for withdrawal request response."""
    id: str
    user_id: str
    amount: float
    status: str
    payment_method: str | None
    payment_details: str | None
    rejection_reason: str | None
    reviewed_by: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class WithdrawalAction(BaseModel):
    """Schema for admin approve/reject action."""
    action: str = Field(..., pattern=r"^(approve|reject)$")
    rejection_reason: str | None = None


class PaginatedWithdrawals(BaseModel):
    """Paginated list of withdrawal requests."""
    withdrawals: list[WithdrawalResponse]
    total: int
    page: int
    per_page: int
