from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    PLAYER = "player"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    name = Column(String(100), nullable=True)
    avatar_url = Column(Text, nullable=True)
    role = Column(SAEnum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.PLAYER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    fcm_token = Column(Text, nullable=True)
    referral_code = Column(String(20), unique=True, nullable=False, index=True)
    referred_by = Column(String(36), nullable=True)
    vip_level = Column(Float, default=0, nullable=False)
    total_earnings = Column(Float, default=0, nullable=False)
    referral_earnings = Column(Float, default=0, nullable=False)
    total_matches = Column(Float, default=0, nullable=False)
    total_wins = Column(Float, default=0, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    wallet = relationship("Wallet", back_populates="user", uselist=False)
    tournaments = relationship("TournamentParticipant", back_populates="user")
    matches = relationship("Match", back_populates="user", foreign_keys="Match.user_id")
    referrals_made = relationship("Referral", back_populates="referrer", foreign_keys="Referral.referrer_id")
    notifications = relationship("Notification", back_populates="user")
