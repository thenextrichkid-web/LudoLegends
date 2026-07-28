"""Site configuration model — admin-editable platform settings."""

from sqlalchemy import Column, String, DateTime, Text, Float, Integer
from sqlalchemy.sql import func
from app.core.database import Base


class SiteConfig(Base):
    __tablename__ = "site_configs"

    id = Column(String(36), primary_key=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), default="string", nullable=False)
    category = Column(String(50), default="general", nullable=False, index=True)
    description = Column(Text, nullable=True)
    updated_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
