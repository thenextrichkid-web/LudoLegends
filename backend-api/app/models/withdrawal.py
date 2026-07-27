from sqlalchemy import Column, String, Float, DateTime, Enum as SAEnum, Text
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class WithdrawalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"


class WithdrawalRequest(Base):
    __tablename__ = "withdrawal_requests"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(SAEnum(WithdrawalStatus, values_callable=lambda x: [e.value for e in x]), default=WithdrawalStatus.PENDING, nullable=False)
    payment_method = Column(String(50), nullable=True)
    payment_details = Column(Text, nullable=True)
    reviewed_by = Column(String(36), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
