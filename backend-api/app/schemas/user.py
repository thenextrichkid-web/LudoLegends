from pydantic import BaseModel, Field
from datetime import datetime


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str | None = None
    avatar_url: str | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    fcm_token: str | None = None


class UserResponse(BaseModel):
    id: str
    phone: str
    email: str | None
    name: str | None
    avatar_url: str | None
    role: str
    referral_code: str
    vip_level: float
    total_earnings: float
    total_matches: float
    total_wins: float
    created_at: datetime

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    id: str
    name: str | None
    avatar_url: str | None
    vip_level: float
    total_wins: float
    rank: int | None = None
