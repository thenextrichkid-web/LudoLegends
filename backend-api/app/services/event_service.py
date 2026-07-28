"""Event service — publish events for inter-service communication."""

import json
from app.core.logging import get_logger

logger = get_logger("event_service")


class EventType:
    MATCH_FOUND = "match_found"
    MATCH_CANCELLED = "match_cancelled"
    QUEUE_JOINED = "queue_joined"
    QUEUE_LEFT = "queue_left"
    QUEUE_EXPIRED = "queue_expired"
    WITHDRAWAL_REQUESTED = "withdrawal_requested"
    WITHDRAWAL_APPROVED = "withdrawal_approved"
    WITHDRAWAL_REJECTED = "withdrawal_rejected"
    TOURNAMENT_JOINED = "tournament_joined"
    TOURNAMENT_CANCELLED = "tournament_cancelled"
    PRIZE_CREDITED = "prize_credited"


class EventService:
    _events: list[dict] = []

    @classmethod
    async def publish(cls, event_type: str, payload: dict, user_id: str | None = None):
        event = {
            "type": event_type,
            "payload": payload,
            "user_id": user_id,
        }
        cls._events.append(event)
        if len(cls._events) > 1000:
            cls._events = cls._events[-500:]

        logger.info("Event published: type=%s user=%s payload=%s", event_type, user_id, json.dumps(payload, default=str))

    @classmethod
    def get_recent(cls, limit: int = 50) -> list[dict]:
        return cls._events[-limit:]

    @classmethod
    def clear(cls):
        cls._events.clear()
