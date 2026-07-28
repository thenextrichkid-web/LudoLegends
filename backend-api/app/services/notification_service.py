"""Generic notification service — reusable across all features."""

import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.notification import Notification, NotificationType
from app.core.logging import get_logger

logger = get_logger("notification_service")


class EventNotificationType:
    MATCH_FOUND = "match_found"
    MATCH_CANCELLED = "match_cancelled"
    WITHDRAWAL_APPROVED = "withdrawal_approved"
    WITHDRAWAL_REJECTED = "withdrawal_rejected"
    TOURNAMENT_JOINED = "tournament_joined"
    TOURNAMENT_CANCELLED = "tournament_cancelled"
    PRIZE_CREDITED = "prize_credited"
    REFERRAL_BONUS = "referral_bonus"


EVENT_TITLES = {
    EventNotificationType.MATCH_FOUND: "Match Found!",
    EventNotificationType.MATCH_CANCELLED: "Match Cancelled",
    EventNotificationType.WITHDRAWAL_APPROVED: "Withdrawal Approved",
    EventNotificationType.WITHDRAWAL_REJECTED: "Withdrawal Rejected",
    EventNotificationType.TOURNAMENT_JOINED: "Tournament Joined",
    EventNotificationType.TOURNAMENT_CANCELLED: "Tournament Cancelled",
    EventNotificationType.PRIZE_CREDITED: "Prize Credited!",
    EventNotificationType.REFERRAL_BONUS: "Referral Bonus!",
}

EVENT_CATEGORY_MAP = {
    EventNotificationType.MATCH_FOUND: NotificationType.TOURNAMENT,
    EventNotificationType.MATCH_CANCELLED: NotificationType.TOURNAMENT,
    EventNotificationType.WITHDRAWAL_APPROVED: NotificationType.WALLET,
    EventNotificationType.WITHDRAWAL_REJECTED: NotificationType.WALLET,
    EventNotificationType.TOURNAMENT_JOINED: NotificationType.TOURNAMENT,
    EventNotificationType.TOURNAMENT_CANCELLED: NotificationType.TOURNAMENT,
    EventNotificationType.PRIZE_CREDITED: NotificationType.WALLET,
    EventNotificationType.REFERRAL_BONUS: NotificationType.REFERRAL,
}


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send(
        self,
        user_id: str,
        event_type: str,
        title: str | None = None,
        body: str = "",
        data: str | None = None,
    ) -> Notification:
        category = EVENT_CATEGORY_MAP.get(event_type, NotificationType.SYSTEM)
        final_title = title or EVENT_TITLES.get(event_type, "Notification")

        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=category,
            title=final_title,
            body=body,
            data=data,
        )
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)

        logger.info("Notification sent: user=%s event=%s title=%s", user_id, event_type, final_title)
        return notification

    async def get_user_notifications(self, user_id: str, page: int = 1, per_page: int = 20) -> tuple[list[Notification], int]:
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(offset).limit(per_page)
        )
        notifications = list(result.scalars().all())
        count_result = await self.db.execute(
            select(func.count(Notification.id)).where(Notification.user_id == user_id)
        )
        total = count_result.scalar() or 0
        return notifications, total

    async def mark_read(self, user_id: str, notification_id: str) -> Notification:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.id == notification_id, Notification.user_id == user_id)
        )
        notification = result.scalar_one_or_none()
        if not notification:
            raise ValueError("Notification not found")
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        await self.db.flush()
        return notification

    async def mark_all_read(self, user_id: str) -> int:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
        )
        notifications = list(result.scalars().all())
        now = datetime.now(timezone.utc)
        for n in notifications:
            n.is_read = True
            n.read_at = now
        await self.db.flush()
        return len(notifications)

    async def get_unread_count(self, user_id: str) -> int:
        result = await self.db.execute(
            select(func.count(Notification.id))
            .where(Notification.user_id == user_id, Notification.is_read == False)
        )
        return result.scalar() or 0
