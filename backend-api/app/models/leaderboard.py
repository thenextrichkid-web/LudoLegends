from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.sql import func
from app.core.database import Base


class Leaderboard(Base):
    __tablename__ = "leaderboards"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    period = Column(String(20), nullable=False, default="weekly")
    wins = Column(Integer, default=0, nullable=False)
    matches_played = Column(Integer, default=0, nullable=False)
    total_earnings = Column(Float, default=0, nullable=False)
    win_rate = Column(Float, default=0, nullable=False)
    rank = Column(Integer, default=0, nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
