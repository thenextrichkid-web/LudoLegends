from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.services.wallet_service import WalletService
from app.models.wallet import TransactionType
from app.core.config import get_settings

settings = get_settings()


class ReferralService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_referral(self, new_user_id: str, referrer_id: str) -> dict:
        if new_user_id == referrer_id:
            return {"credited": False, "reason": "self_referral"}

        referrer_result = await self.db.execute(select(User).where(User.id == referrer_id))
        referrer = referrer_result.scalar_one_or_none()
        if not referrer:
            return {"credited": False, "reason": "referrer_not_found"}

        wallet_svc = WalletService(self.db)
        wallet = await wallet_svc.get_balance(referrer_id)

        if wallet.balance < settings.REFERRAL_BONUS_AMOUNT:
            return {"credited": False, "reason": "insufficient_platform_balance"}

        await wallet_svc.credit(
            referrer_id,
            settings.REFERRAL_BONUS_AMOUNT,
            TransactionType.REFERRAL_BONUS,
            new_user_id,
            f"Referral bonus for inviting user",
        )

        new_user_result = await self.db.execute(select(User).where(User.id == new_user_id))
        new_user = new_user_result.scalar_one_or_none()
        if new_user:
            new_user.referred_by = referrer_id
            referrer.referral_earnings += settings.REFERRAL_BONUS_AMOUNT

        await self.db.commit()
        return {"credited": True, "amount": settings.REFERRAL_BONUS_AMOUNT}

    async def get_referral_stats(self, user_id: str) -> dict:
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        all_referrers = await self.db.execute(
            select(User).where(User.referred_by == user_id)
        )
        all_referrals = list(all_referrers.scalars().all())

        return {
            "total_referrals": len(all_referrals),
            "active_referrals": sum(1 for r in all_referrals if r.is_verified),
            "total_earned": user.referral_earnings,
            "referral_code": user.referral_code,
        }

    async def get_referral_list(self, user_id: str, page: int = 1, per_page: int = 20) -> tuple[list[User], int]:
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(User)
            .where(User.referred_by == user_id)
            .order_by(User.created_at.desc())
            .offset(offset).limit(per_page)
        )
        referrals = list(result.scalars().all())
        count_result = await self.db.execute(select(User).where(User.referred_by == user_id))
        total = len(count_result.scalars().all())
        return referrals, total
