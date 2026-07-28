from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    REJECTED = "rejected"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class Match(Base):
    __tablename__ = "matches"

    id = Column(String(36), primary_key=True)
    tournament_id = Column(String(36), ForeignKey("tournaments.id"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(SAEnum(MatchStatus, values_callable=lambda x: [e.value for e in x]), default=MatchStatus.PENDING, nullable=False)
    screenshot_url = Column(Text, nullable=True)
    result_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    auto_moves_used = Column(Float, default=0, nullable=False)
    auto_move_penalty = Column(Float, default=0, nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    tournament = relationship("Tournament", back_populates="matches")
    user = relationship("User", back_populates="matches", foreign_keys=[user_id])
    result = relationship("MatchResult", back_populates="match", uselist=False)


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(String(36), primary_key=True)
    match_id = Column(String(36), ForeignKey("matches.id"), unique=True, nullable=False)
    winner_id = Column(String(36), nullable=True)
    score = Column(String(50), nullable=True)
    prize_awarded = Column(Float, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    match = relationship("Match", back_populates="result")
