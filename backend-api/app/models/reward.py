from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class RewardType(str, enum.Enum):
    REFERRAL_BONUS = "referral_bonus"
    CASHBACK = "cashback"
    WEEKLY_GIVEAWAY = "weekly_giveaway"
    MONTHLY_GIVEAWAY = "monthly_giveaway"
    ANNIVERSARY_GIVEAWAY = "anniversary_giveaway"
    ACHIEVEMENT = "achievement"
    VIP = "vip"


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    type = Column(SAEnum(RewardType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    amount = Column(Float, default=0, nullable=False)
    description = Column(String(500), nullable=True)
    claimed = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
