from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import OTPRequest, OTPVerify, TokenResponse, RefreshTokenRequest, LoginResponse
from app.schemas.user import UserResponse
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/otp/request")
async def request_otp(body: OTPRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    result = await svc.request_otp(body.phone)
    return {"message": "OTP sent successfully"}


@router.post("/otp/verify", response_model=LoginResponse)
async def verify_otp(body: OTPVerify, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    try:
        result = await svc.verify_otp_and_login(body.phone, body.otp, body.referral_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    try:
        return await svc.refresh_token(body.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
