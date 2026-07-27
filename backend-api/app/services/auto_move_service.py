from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.match import Match, MatchStatus
from app.models.wallet import TransactionType
from app.services.wallet_service import WalletService
from app.core.config import get_settings

settings = get_settings()


class AutoMoveService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_penalty_config(self) -> dict:
        from app.models.settings import Setting
        result = await self.db.execute(
            select(Setting).where(Setting.key.in_([
                "AUTO_MOVE_LIMIT", "AUTO_MOVE_PENALTY_AMOUNT"
            ]))
        )
        configs = {s.key: s.value for s in result.scalars().all()}

        return {
            "limit": int(configs.get("AUTO_MOVE_LIMIT", settings.AUTO_MOVE_LIMIT)),
            "penalty_amount": float(configs.get("AUTO_MOVE_PENALTY_AMOUNT", settings.AUTO_MOVE_PENALTY_AMOUNT)),
        }

    async def record_auto_move(self, match_id: str, user_id: str) -> dict:
        result = await self.db.execute(select(Match).where(Match.id == match_id))
        match = result.scalar_one_or_none()
        if not match:
            raise ValueError("Match not found")
        if match.status != MatchStatus.IN_PROGRESS:
            raise ValueError("Match is not in progress")

        config = await self.get_penalty_config()
        match.auto_moves_used += 1

        penalty_applied = 0.0
        if match.auto_moves_used > config["limit"]:
            excess_moves = match.auto_moves_used - config["limit"]
            penalty_applied = excess_moves * config["penalty_amount"]
            match.auto_move_penalty = penalty_applied

            wallet_svc = WalletService(self.db)
            try:
                await wallet_svc.deduct(
                    user_id, penalty_applied, TransactionType.ADJUSTMENT,
                    match_id, f"Auto move penalty ({int(match.auto_moves_used)} moves used)"
                )
            except ValueError:
                pass

        await self.db.commit()
        await self.db.refresh(match)

        return {
            "auto_moves_used": int(match.auto_moves_used),
            "limit": config["limit"],
            "penalty_amount": config["penalty_amount"],
            "total_penalty": match.auto_move_penalty,
            "penalty_applied": penalty_applied > 0,
        }

    async def get_match_auto_moves(self, match_id: str) -> dict:
        result = await self.db.execute(select(Match).where(Match.id == match_id))
        match = result.scalar_one_or_none()
        if not match:
            raise ValueError("Match not found")

        config = await self.get_penalty_config()
        return {
            "match_id": match.id,
            "auto_moves_used": int(match.auto_moves_used),
            "limit": config["limit"],
            "penalty_amount": config["penalty_amount"],
            "total_penalty": match.auto_move_penalty,
            "remaining_free_moves": max(0, config["limit"] - int(match.auto_moves_used)),
        }
