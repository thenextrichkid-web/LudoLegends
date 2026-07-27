from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "Ludo Legends"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://ludo:ludo_secret@localhost:5432/ludo_legends"
    DATABASE_URL_SYNC: str = "postgresql://ludo:ludo_secret@localhost:5432/ludo_legends"

    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_REFRESH_SECRET_KEY: str = "CHANGE_ME_REFRESH_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    OTP_EXPIRY_MINUTES: int = 5
    OTP_LENGTH: int = 6

    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    FIREBASE_CREDENTIALS_PATH: str = ""

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""

    GIVEAWAY_AMOUNT: float = 500.0
    GIVEAWAY_WINNERS: int = 2
    REFERRAL_BONUS: float = 50.0
    REFERRAL_BONUS_AMOUNT: float = 50.0

    AUTO_MOVE_LIMIT: int = 3
    AUTO_MOVE_PENALTY_AMOUNT: float = 20.0

    ENVIRONMENT: str = "development"

    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
