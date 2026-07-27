import uuid
import secrets
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token, generate_otp
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

OTP_TTL_SECONDS = settings.OTP_EXPIRY_MINUTES * 60


async def _get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def request_otp(self, phone: str) -> dict:
        if settings.ENVIRONMENT == "development":
            otp = "123456"
        else:
            otp = generate_otp()

        redis = await _get_redis()
        await redis.setex(f"otp:{phone}", OTP_TTL_SECONDS, otp)
        await redis.aclose()

        result = await self.db.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                id=str(uuid.uuid4()),
                phone=phone,
                referral_code=f"LL{secrets.token_hex(4).upper()}",
                is_active=True,
            )
            self.db.add(user)

        user.last_login_at = datetime.now(timezone.utc)
        await self.db.commit()

        if settings.TWILIO_ACCOUNT_SID:
            try:
                from twilio.rest import Client
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                client.messages.create(
                    body=f"Your Ludo Legends OTP is: {otp}",
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=phone,
                )
            except Exception as e:
                logger.error(f"Failed to send SMS: {e}")

        return {"message": "OTP sent successfully", "phone": phone}

    async def verify_otp_and_login(self, phone: str, otp: str, referral_code: str | None = None) -> dict:
        redis = await _get_redis()
        stored_otp = await redis.get(f"otp:{phone}")
        await redis.aclose()

        if not stored_otp:
            raise ValueError("OTP expired or not requested. Please request a new OTP.")

        if stored_otp != otp:
            raise ValueError("Invalid OTP. Please try again.")

        redis = await _get_redis()
        await redis.delete(f"otp:{phone}")
        await redis.aclose()

        result = await self.db.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found. Request OTP first.")

        is_new = not user.is_verified
        user.is_verified = True

        if referral_code and is_new:
            ref_result = await self.db.execute(select(User).where(User.referral_code == referral_code))
            referrer = ref_result.scalar_one_or_none()
            if referrer and referrer.id != user.id:
                user.referred_by = referrer.id

        await self.db.commit()

        token_data = {"sub": user.id, "role": user.role.value}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id,
            "role": user.role.value,
            "is_new_user": is_new,
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        from app.core.security import decode_token
        payload = decode_token(refresh_token, "refresh")
        if not payload:
            raise ValueError("Invalid refresh token")

        user_id = payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        token_data = {"sub": user.id, "role": user.role.value}
        new_access = create_access_token(token_data)
        new_refresh = create_refresh_token(token_data)

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "user_id": user.id,
            "role": user.role.value,
        }
