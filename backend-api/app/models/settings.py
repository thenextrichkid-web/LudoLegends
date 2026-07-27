from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(String(36), primary_key=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    updated_by = Column(String(36), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
