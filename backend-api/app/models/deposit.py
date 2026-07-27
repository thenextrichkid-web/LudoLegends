from sqlalchemy import Column, String, Float, DateTime, Enum as SAEnum, Text
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DepositStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class DepositRequest(Base):
    __tablename__ = "deposit_requests"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(SAEnum(DepositStatus, values_callable=lambda x: [e.value for e in x]), default=DepositStatus.PENDING, nullable=False)
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
