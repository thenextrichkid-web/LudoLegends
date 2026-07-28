"""Queue service — matchmaking queue with timeout, matching, and wallet freeze."""

import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.queue_entry import QueueEntry, QueueStatus
from app.models.match import Match, MatchStatus
from app.services.wallet_service import WalletService
from app.core.logging import get_logger
from app.core.metrics import metrics

logger = get_logger("queue_service")

DEFAULT_QUEUE_TIMEOUT_SECONDS = 120


class QueueService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_pools(self) -> list[dict]:
        from app.services.config_service import ConfigService
        cfg = ConfigService(self.db)
        pool_amounts = await cfg.get_json("entry_fees", [100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000])

        pools = []
        for amount in pool_amounts:
            waiting = await self._count_waiting(amount)
            pools.append({
                "amount": amount,
                "players_waiting": waiting,
                "estimated_wait_seconds": self._estimate_wait(waiting),
            })
        return pools

    async def _count_waiting(self, pool_amount: float) -> int:
        result = await self.db.execute(
            select(func.count(QueueEntry.id)).where(
                QueueEntry.pool_amount == pool_amount,
                QueueEntry.status == QueueStatus.WAITING,
            )
        )
        return result.scalar() or 0

    def _estimate_wait(self, waiting: int) -> int:
        if waiting >= 2:
            return 5
        if waiting == 1:
            return 30
        return 60

    async def join_queue(self, user_id: str, pool_amount: float) -> QueueEntry:
        existing = await self._get_user_active_entry(user_id)
        if existing:
            raise ValueError("You are already in a queue. Cancel first to join another pool.")

        wallet_svc = WalletService(self.db)
        tx = await wallet_svc.deduct(
            user_id, pool_amount,
            reference_id=None,
            description=f"Queue entry freeze for ₹{pool_amount} pool",
        )

        timeout = DEFAULT_QUEUE_TIMEOUT_SECONDS
        queue_entry = QueueEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            pool_amount=pool_amount,
            status=QueueStatus.WAITING,
            frozen_amount=pool_amount,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=timeout),
        )
        self.db.add(queue_entry)
        await self.db.flush()
        await self.db.refresh(queue_entry)

        metrics.increment("queue_joins")
        metrics.increment(f"queue_pool:{int(pool_amount)}")
        logger.info("User %s joined queue: pool=%s entry=%s", user_id, pool_amount, queue_entry.id)

        matched = await self._try_match(queue_entry)
        return queue_entry

    async def _try_match(self, entry: QueueEntry) -> QueueEntry | None:
        opponent_result = await self.db.execute(
            select(QueueEntry).where(
                QueueEntry.pool_amount == entry.pool_amount,
                QueueEntry.status == QueueStatus.WAITING,
                QueueEntry.user_id != entry.user_id,
                QueueEntry.id != entry.id,
                QueueEntry.expires_at > datetime.now(timezone.utc),
            ).order_by(QueueEntry.queued_at.asc()).limit(1).with_for_update()
        )
        opponent = opponent_result.scalar_one_or_none()

        if not opponent:
            return None

        entry.status = QueueStatus.MATCHED
        entry.matched_at = datetime.now(timezone.utc)
        entry.matched_with = opponent.user_id

        opponent.status = QueueStatus.MATCHED
        opponent.matched_at = datetime.now(timezone.utc)
        opponent.matched_with = entry.user_id

        match = Match(
            id=str(uuid.uuid4()),
            tournament_id="queue_match",
            user_id=entry.user_id,
            status=MatchStatus.PENDING,
        )
        self.db.add(match)
        await self.db.flush()

        entry.match_id = match.id
        opponent.match_id = match.id

        metrics.increment("matches_created")
        metrics.increment("queue_matches")
        logger.info("Match created: %s vs %s in pool %s", entry.user_id, opponent.user_id, entry.pool_amount)

        from app.services.notification_service import NotificationService
        notif_svc = NotificationService(self.db)
        await notif_svc.send(entry.user_id, "match_found", body=f"Match found in ₹{entry.pool_amount} pool!")
        await notif_svc.send(opponent.user_id, "match_found", body=f"Match found in ₹{entry.pool_amount} pool!")

        return entry

    async def cancel_queue(self, user_id: str) -> dict:
        entry = await self._get_user_active_entry(user_id)
        if not entry:
            raise ValueError("No active queue entry found.")

        entry.status = QueueStatus.CANCELLED

        wallet_svc = WalletService(self.db)
        await wallet_svc.refund(user_id, entry.frozen_amount)

        metrics.increment("queue_cancels")
        logger.info("User %s cancelled queue entry %s", user_id, entry.id)
        return {"message": "Queue cancelled, balance refunded", "refund": entry.frozen_amount}

    async def get_queue_status(self, user_id: str) -> dict | None:
        entry = await self._get_user_active_entry(user_id)
        if not entry:
            return None

        now = datetime.now(timezone.utc)
        time_left = max(0, (entry.expires_at - now).total_seconds())
        position = await self._get_position(entry)

        return {
            "id": entry.id,
            "pool_amount": entry.pool_amount,
            "status": entry.status.value,
            "position": position,
            "time_remaining_seconds": int(time_left),
            "queued_at": entry.queued_at.isoformat(),
            "expires_at": entry.expires_at.isoformat(),
            "match_id": entry.match_id,
        }

    async def _get_position(self, entry: QueueEntry) -> int:
        result = await self.db.execute(
            select(func.count(QueueEntry.id)).where(
                QueueEntry.pool_amount == entry.pool_amount,
                QueueEntry.status == QueueStatus.WAITING,
                QueueEntry.queued_at < entry.queued_at,
            )
        )
        return (result.scalar() or 0) + 1

    async def _get_user_active_entry(self, user_id: str) -> QueueEntry | None:
        result = await self.db.execute(
            select(QueueEntry).where(
                QueueEntry.user_id == user_id,
                QueueEntry.status == QueueStatus.WAITING,
            )
        )
        return result.scalar_one_or_none()

    async def expire_stale_entries(self) -> int:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(QueueEntry).where(
                QueueEntry.status == QueueStatus.WAITING,
                QueueEntry.expires_at <= now,
            )
        )
        expired = list(result.scalars().all())
        wallet_svc = WalletService(self.db)
        for entry in expired:
            entry.status = QueueStatus.EXPIRED
            try:
                await wallet_svc.refund(entry.user_id, entry.frozen_amount)
                logger.info("Expired queue entry %s, refunded %s to user %s", entry.id, entry.frozen_amount, entry.user_id)
            except Exception as e:
                logger.error("Failed to refund expired entry %s: %s", entry.id, e)
            metrics.increment("queue_expires")

        if expired:
            await self.db.flush()
        return len(expired)
