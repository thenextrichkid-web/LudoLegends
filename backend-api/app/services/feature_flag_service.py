"""Feature flag service — toggle features without redeployment."""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.feature_flag import FeatureFlag
from app.core.logging import get_logger

logger = get_logger("feature_flag_service")

DEFAULT_FLAGS = {
    "practice_mode": {"name": "Practice Mode", "description": "Allow players to practice without tournaments", "enabled": True},
    "withdrawals": {"name": "Withdrawals", "description": "Enable withdrawal requests", "enabled": True},
    "matchmaking": {"name": "Matchmaking", "description": "Enable automatic match finding", "enabled": False},
    "ai_admin": {"name": "AI Admin", "description": "Enable AI-powered admin automation", "enabled": False},
    "affiliate": {"name": "Affiliate System", "description": "Enable affiliate/referral engine", "enabled": False},
    "playcore": {"name": "PlayCore (Unity)", "description": "Enable Unity game integration", "enabled": False},
    "giveaways": {"name": "Giveaways", "description": "Enable giveaway feature", "enabled": True},
    "leaderboard": {"name": "Leaderboard", "description": "Enable leaderboard display", "enabled": True},
    "referral_bonus": {"name": "Referral Bonus", "description": "Enable referral bonus payouts", "enabled": True},
    "auto_approve_small_withdrawals": {"name": "Auto-approve Small Withdrawals", "description": "Auto-approve withdrawals under threshold", "enabled": False},
    "maintenance_mode": {"name": "Maintenance Mode", "description": "Block all player-facing endpoints", "enabled": False},
    "notifications": {"name": "Notifications", "description": "Enable push/in-app notifications", "enabled": True},
}


class FeatureFlagService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_enabled(self, key: str) -> bool:
        result = await self.db.execute(select(FeatureFlag).where(FeatureFlag.key == key))
        flag = result.scalar_one_or_none()
        if flag is None:
            defaults = DEFAULT_FLAGS.get(key)
            return defaults["enabled"] if defaults else False
        return flag.is_enabled

    async def get(self, key: str) -> FeatureFlag | None:
        result = await self.db.execute(select(FeatureFlag).where(FeatureFlag.key == key))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[FeatureFlag]:
        result = await self.db.execute(select(FeatureFlag).order_by(FeatureFlag.key))
        return list(result.scalars().all())

    async def get_all_as_dict(self) -> dict[str, bool]:
        flags = await self.get_all()
        return {f.key: f.is_enabled for f in flags}

    async def toggle(self, key: str, enabled: bool, updated_by: str | None = None) -> FeatureFlag:
        result = await self.db.execute(select(FeatureFlag).where(FeatureFlag.key == key))
        flag = result.scalar_one_or_none()
        if flag:
            flag.is_enabled = enabled
            if updated_by:
                flag.updated_by = updated_by
        else:
            flag = FeatureFlag(
                id=str(uuid.uuid4()),
                key=key,
                name=key.replace("_", " ").title(),
                is_enabled=enabled,
                updated_by=updated_by,
            )
            self.db.add(flag)
        await self.db.flush()
        await self.db.refresh(flag)

        logger.info("Feature flag toggled: key=%s enabled=%s by=%s", key, enabled, updated_by)
        return flag

    async def seed_defaults(self):
        for key, cfg in DEFAULT_FLAGS.items():
            existing = await self.db.execute(select(FeatureFlag).where(FeatureFlag.key == key))
            if not existing.scalar_one_or_none():
                self.db.add(FeatureFlag(
                    id=str(uuid.uuid4()),
                    key=key, name=cfg["name"], description=cfg["description"],
                    is_enabled=cfg["enabled"],
                ))
        await self.db.flush()
        logger.info("Default feature flags seeded")
