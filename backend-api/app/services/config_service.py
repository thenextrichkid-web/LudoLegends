"""Site configuration service — admin-editable platform settings."""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.site_config import SiteConfig
from app.core.logging import get_logger

logger = get_logger("config_service")

DEFAULT_CONFIGS = {
    "entry_fees": {"value": "[10,20,50,100,200,500,1000]", "type": "json", "category": "tournaments", "description": "Available entry fee amounts"},
    "queue_timeout_seconds": {"value": "120", "type": "int", "category": "matchmaking", "description": "Seconds before queue times out"},
    "min_withdrawal": {"value": "100", "type": "float", "category": "wallet", "description": "Minimum withdrawal amount"},
    "max_withdrawal": {"value": "50000", "type": "float", "category": "wallet", "description": "Maximum withdrawal amount"},
    "daily_withdrawal_limit": {"value": "100000", "type": "float", "category": "wallet", "description": "Daily withdrawal limit per user"},
    "referral_bonus": {"value": "50", "type": "float", "category": "referrals", "description": "Bonus amount per referral"},
    "cashback_percentage": {"value": "5", "type": "float", "category": "wallet", "description": "Cashback percentage on deposits"},
    "maintenance_mode": {"value": "false", "type": "bool", "category": "system", "description": "Enable maintenance mode"},
    "auto_approve_withdrawals": {"value": "false", "type": "bool", "category": "wallet", "description": "Auto-approve withdrawals under limit"},
    "max_auto_moves": {"value": "3", "type": "int", "category": "matches", "description": "Max auto-moves per match"},
    "auto_move_penalty": {"value": "20", "type": "float", "category": "matches", "description": "Penalty per auto-move"},
    "giveaway_amount": {"value": "500", "type": "float", "category": "giveaways", "description": "Default giveaway prize"},
    "giveaway_winners": {"value": "5", "type": "int", "category": "giveaways", "description": "Number of giveaway winners"},
}


class ConfigService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, key: str) -> str | None:
        result = await self.db.execute(select(SiteConfig).where(SiteConfig.key == key))
        config = result.scalar_one_or_none()
        return config.value if config else None

    async def get_bool(self, key: str, default: bool = False) -> bool:
        val = await self.get(key)
        if val is None:
            return default
        return val.lower() in ("true", "1", "yes")

    async def get_int(self, key: str, default: int = 0) -> int:
        val = await self.get(key)
        if val is None:
            return default
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    async def get_float(self, key: str, default: float = 0.0) -> float:
        val = await self.get(key)
        if val is None:
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    async def get_json(self, key: str, default=None):
        import json
        val = await self.get(key)
        if val is None:
            return default
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return default

    async def set(self, key: str, value: str, category: str = "general", description: str | None = None, value_type: str = "string", updated_by: str | None = None) -> SiteConfig:
        result = await self.db.execute(select(SiteConfig).where(SiteConfig.key == key))
        config = result.scalar_one_or_none()
        if config:
            config.value = value
            config.value_type = value_type
            if description:
                config.description = description
            if updated_by:
                config.updated_by = updated_by
        else:
            config = SiteConfig(
                id=str(uuid.uuid4()),
                key=key, value=value, value_type=value_type,
                category=category, description=description, updated_by=updated_by,
            )
            self.db.add(config)
        await self.db.flush()
        await self.db.refresh(config)
        return config

    async def get_all(self, category: str | None = None) -> list[SiteConfig]:
        query = select(SiteConfig).order_by(SiteConfig.category, SiteConfig.key)
        if category:
            query = query.where(SiteConfig.category == category)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all_as_dict(self) -> dict:
        configs = await self.get_all()
        return {c.key: c.value for c in configs}

    async def seed_defaults(self):
        for key, cfg in DEFAULT_CONFIGS.items():
            existing = await self.db.execute(select(SiteConfig).where(SiteConfig.key == key))
            if not existing.scalar_one_or_none():
                self.db.add(SiteConfig(
                    id=str(uuid.uuid4()),
                    key=key, value=cfg["value"], value_type=cfg["type"],
                    category=cfg["category"], description=cfg["description"],
                ))
        await self.db.flush()
        logger.info("Default site configs seeded")
