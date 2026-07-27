from pydantic import BaseModel, Field
from datetime import datetime


class OTPRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{9,14}$")


class OTPVerify(BaseModel):
    phone: str
    otp: str = Field(..., min_length=6, max_length=6)
    referral_code: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    is_new_user: bool
