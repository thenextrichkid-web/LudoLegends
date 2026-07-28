"""Tournament service — CRUD, join with wallet deduction, cancellation with refunds."""

import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.tournament import Tournament, TournamentParticipant, TournamentStatus
from app.models.wallet import TransactionType
from app.services.wallet_service import WalletService


class TournamentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tournament(self, data: dict, created_by: str) -> Tournament:
        """Create a new tournament."""
        tournament = Tournament(
            id=str(uuid.uuid4()),
            name=data["name"],
            description=data.get("description"),
            type=data["type"],
            entry_fee=data["entry_fee"],
            prize_pool=data["prize_pool"],
            max_participants=data["max_participants"],
            starts_at=data["starts_at"],
            ends_at=data.get("ends_at"),
            registration_deadline=data.get("registration_deadline"),
            rules=data.get("rules"),
            created_by=created_by,
        )
        self.db.add(tournament)
        await self.db.flush()
        await self.db.refresh(tournament)
        return tournament

    async def join_tournament(self, user_id: str, tournament_id: str) -> TournamentParticipant:
        """Join a tournament — checks capacity, deducts entry fee atomically."""
        result = await self.db.execute(
            select(Tournament).where(Tournament.id == tournament_id).with_for_update()
        )
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise ValueError("Tournament not found")
        if tournament.status != TournamentStatus.UPCOMING:
            raise ValueError("Tournament not accepting registrations")
        if tournament.current_participants >= tournament.max_participants:
            raise ValueError("Tournament is full")

        existing = await self.db.execute(
            select(TournamentParticipant)
            .where(TournamentParticipant.tournament_id == tournament_id, TournamentParticipant.user_id == user_id)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Already registered for this tournament")

        wallet_svc = WalletService(self.db)
        await wallet_svc.deduct(
            user_id, tournament.entry_fee, TransactionType.ENTRY_FEE,
            tournament_id, f"Entry fee for {tournament.name}"
        )

        participant = TournamentParticipant(
            id=str(uuid.uuid4()),
            tournament_id=tournament_id,
            user_id=user_id,
            entry_fee_paid=tournament.entry_fee,
        )
        self.db.add(participant)
        tournament.current_participants += 1
        await self.db.flush()
        await self.db.refresh(participant)
        return participant

    async def get_tournament(self, tournament_id: str) -> Tournament:
        """Get a single tournament by ID."""
        result = await self.db.execute(select(Tournament).where(Tournament.id == tournament_id))
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise ValueError("Tournament not found")
        return tournament

    async def list_tournaments(
        self, status: str | None = None, page: int = 1, per_page: int = 20
    ) -> tuple[list[Tournament], int]:
        """List tournaments with optional status filter and pagination."""
        query = select(Tournament)
        count_query = select(func.count(Tournament.id))

        if status:
            query = query.where(Tournament.status == status)
            count_query = count_query.where(Tournament.status == status)

        query = query.order_by(Tournament.starts_at.desc())
        offset = (page - 1) * per_page
        result = await self.db.execute(query.offset(offset).limit(per_page))
        tournaments = list(result.scalars().all())

        total = (await self.db.execute(count_query)).scalar() or 0
        return tournaments, total

    async def get_participants(self, tournament_id: str) -> list[TournamentParticipant]:
        """Get all participants for a tournament."""
        result = await self.db.execute(
            select(TournamentParticipant).where(TournamentParticipant.tournament_id == tournament_id)
        )
        return list(result.scalars().all())

    async def cancel_tournament(self, tournament_id: str, reason: str) -> Tournament:
        """Cancel a tournament and refund all participants."""
        tournament = await self.get_tournament(tournament_id)
        if tournament.status not in [TournamentStatus.UPCOMING]:
            raise ValueError("Can only cancel upcoming tournaments")

        participants = await self.get_participants(tournament_id)
        wallet_svc = WalletService(self.db)
        for p in participants:
            await wallet_svc.credit(
                p.user_id, p.entry_fee_paid, TransactionType.REFUND,
                tournament_id, f"Refund for cancelled tournament: {tournament.name}"
            )
            p.status = "refunded"

        tournament.status = TournamentStatus.CANCELLED
        await self.db.commit()
        return tournament
