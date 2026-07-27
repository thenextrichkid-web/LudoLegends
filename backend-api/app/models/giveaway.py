from sqlalchemy import Column, String, Float, DateTime, Integer, Enum as SAEnum, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class GiveawayStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Giveaway(Base):
    __tablename__ = "giveaways"

    id = Column(String(36), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False, default="weekly")
    status = Column(SAEnum(GiveawayStatus, values_callable=lambda x: [e.value for e in x]), default=GiveawayStatus.UPCOMING, nullable=False)
    prize_amount = Column(Float, nullable=False)
    winners_count = Column(Integer, default=2, nullable=False)
    qualification_threshold = Column(Float, default=0, nullable=False)
    qualification_description = Column(Text, nullable=True)
    winners = Column(Text, nullable=True)
    winner_ids = Column(Text, nullable=True)
    week_start = Column(DateTime(timezone=True), nullable=True)
    week_end = Column(DateTime(timezone=True), nullable=True)
    drawn_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
