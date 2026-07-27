from sqlalchemy import Column, String, Float, DateTime, Integer, Enum as SAEnum, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class TournamentType(str, enum.Enum):
    TWO_PLAYER = "2_player"
    FOUR_PLAYER = "4_player"
    EIGHT_PLAYER = "8_player"
    SIXTEEN_PLAYER = "16_player"
    THIRTY_TWO_PLAYER = "32_player"
    LEAGUE = "league"
    JACKPOT = "jackpot"
    SCHEDULED = "scheduled"


class TournamentStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    REGISTRATION = "registration"
    FULL = "full"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(String(36), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(SAEnum(TournamentType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    status = Column(SAEnum(TournamentStatus, values_callable=lambda x: [e.value for e in x]), default=TournamentStatus.UPCOMING, nullable=False)
    entry_fee = Column(Float, nullable=False)
    prize_pool = Column(Float, nullable=False)
    max_participants = Column(Integer, nullable=False)
    current_participants = Column(Integer, default=0, nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    registration_deadline = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(String(36), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    rules = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    participants = relationship("TournamentParticipant", back_populates="tournament")
    matches = relationship("Match", back_populates="tournament")


class TournamentParticipant(Base):
    __tablename__ = "tournament_participants"

    id = Column(String(36), primary_key=True)
    tournament_id = Column(String(36), ForeignKey("tournaments.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    entry_fee_paid = Column(Float, default=0, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(20), default="registered", nullable=False)

    tournament = relationship("Tournament", back_populates="participants")
    user = relationship("User", back_populates="tournaments")
