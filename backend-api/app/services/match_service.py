"""Match service — submit, verify, list matches."""

import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.match import Match, MatchResult, MatchStatus
from app.models.user import User
from app.services.wallet_service import WalletService
from app.models.wallet import TransactionType


class MatchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit_match(
        self,
        user_id: str,
        tournament_id: str,
        screenshot_url: str,
        result_notes: str | None = None,
    ) -> Match:
        """Submit a match result for admin verification."""
        match = Match(
            id=str(uuid.uuid4()),
            tournament_id=tournament_id,
            user_id=user_id,
            screenshot_url=screenshot_url,
            result_notes=result_notes,
            status=MatchStatus.SUBMITTED,
            submitted_at=datetime.now(timezone.utc),
        )
        self.db.add(match)
        await self.db.flush()
        await self.db.refresh(match)
        return match

    async def verify_match(
        self,
        match_id: str,
        action: str,
        winner_id: str | None = None,
        score: str | None = None,
        prize_awarded: float = 0,
        rejection_reason: str | None = None,
    ) -> Match:
        """Admin verify a match — approve with prize or reject."""
        result = await self.db.execute(select(Match).where(Match.id == match_id))
        match = result.scalar_one_or_none()
        if not match:
            raise ValueError("Match not found")
        if match.status != MatchStatus.SUBMITTED:
            raise ValueError("Match already verified")

        if action == "approve":
            match.status = MatchStatus.VERIFIED
            match.verified_at = datetime.now(timezone.utc)

            match_result = MatchResult(
                id=str(uuid.uuid4()),
                match_id=match_id,
                winner_id=winner_id,
                score=score,
                prize_awarded=prize_awarded,
            )
            self.db.add(match_result)

            if winner_id and prize_awarded > 0:
                wallet_svc = WalletService(self.db)
                await wallet_svc.credit(
                    winner_id, prize_awarded, TransactionType.PRIZE,
                    match_id, f"Prize for match {match_id[:8]}"
                )

            if winner_id:
                winner_result = await self.db.execute(select(User).where(User.id == winner_id))
                winner = winner_result.scalar_one_or_none()
                if winner:
                    winner.total_wins += 1
                    winner.total_earnings += prize_awarded
        else:
            match.status = MatchStatus.REJECTED
            if rejection_reason:
                match.rejection_reason = rejection_reason

        await self.db.flush()
        await self.db.refresh(match)
        return match

    async def get_user_matches(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> tuple[list[Match], int]:
        """Get paginated matches for a user."""
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Match)
            .where(Match.user_id == user_id)
            .order_by(Match.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        matches = list(result.scalars().all())

        count_result = await self.db.execute(
            select(func.count(Match.id)).where(Match.user_id == user_id)
        )
        total = count_result.scalar() or 0
        return matches, total

    async def get_pending_matches(
        self, page: int = 1, per_page: int = 20
    ) -> tuple[list[Match], int]:
        """Get paginated pending matches for admin review."""
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Match)
            .where(Match.status == MatchStatus.SUBMITTED)
            .order_by(Match.submitted_at.asc())
            .offset(offset)
            .limit(per_page)
        )
        matches = list(result.scalars().all())

        count_result = await self.db.execute(
            select(func.count(Match.id)).where(Match.status == MatchStatus.SUBMITTED)
        )
        total = count_result.scalar() or 0
        return matches, total
