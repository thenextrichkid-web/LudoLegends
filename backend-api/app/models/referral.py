from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(String(36), primary_key=True)
    referrer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    referred_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    bonus_awarded = Column(Float, default=0, nullable=False)
    milestone_reached = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    referrer = relationship("User", back_populates="referrals_made", foreign_keys=[referrer_id])
