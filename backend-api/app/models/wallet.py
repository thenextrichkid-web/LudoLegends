from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TOURNAMENT_ENTRY = "tournament_entry"
    TOURNAMENT_WIN = "tournament_win"
    ENTRY_FEE = "entry_fee"
    PRIZE = "prize"
    REFUND = "refund"
    REFERRAL_BONUS = "referral_bonus"
    GIVEAWAY = "giveaway"
    CASHBACK = "cashback"
    ADJUSTMENT = "adjustment"


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Float, default=0, nullable=False)
    frozen = Column(Float, default=0, nullable=False)
    total_deposited = Column(Float, default=0, nullable=False)
    total_withdrawn = Column(Float, default=0, nullable=False)
    total_earned = Column(Float, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="wallet")
    transactions = relationship("WalletTransaction", back_populates="wallet")


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(String(36), primary_key=True)
    wallet_id = Column(String(36), ForeignKey("wallets.id"), nullable=False)
    type = Column(SAEnum(TransactionType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    amount = Column(Float, nullable=False)
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    reference_id = Column(String(36), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    wallet = relationship("Wallet", back_populates="transactions")
