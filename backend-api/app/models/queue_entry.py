"""Queue entry model — tracks players waiting for matchmaking."""

from sqlalchemy import Column, String, Float, DateTime, Integer, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class QueueStatus(str, enum.Enum):
    WAITING = "waiting"
    MATCHED = "matched"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    pool_amount = Column(Float, nullable=False, index=True)
    status = Column(
        SAEnum(QueueStatus, values_callable=lambda x: [e.value for e in x]),
        default=QueueStatus.WAITING,
        nullable=False,
        index=True,
    )
    position = Column(Integer, nullable=True)
    matched_with = Column(String(36), nullable=True)
    match_id = Column(String(36), nullable=True)
    frozen_amount = Column(Float, nullable=False)
    queued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    matched_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User")
