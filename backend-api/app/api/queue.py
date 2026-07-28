"""Queue API endpoints — join, leave, status, pools, timeout management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.middleware.auth import get_current_user, get_admin_user
from app.models.user import User
from app.services.queue_service import QueueService
from app.services.audit_service import AuditService, AuditAction
from app.services.event_service import EventService, EventType
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/queue", tags=["queue"])


class JoinQueueRequest(BaseModel):
    pool_amount: float = Field(..., gt=0, description="Pool amount to join (e.g., 100, 200, 500)")


@router.get("/pools")
async def list_pools(db: AsyncSession = Depends(get_db)):
    svc = QueueService(db)
    pools = await svc.get_active_pools()
    return {"pools": pools}


@router.post("/join")
async def join_queue(body: JoinQueueRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = QueueService(db)
    try:
        entry = await svc.join_queue(user.id, body.pool_amount)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    audit = AuditService(db)
    await audit.log(
        action=AuditAction.QUEUE_JOIN if hasattr(AuditAction, 'QUEUE_JOIN') else "queue_join",
        user_id=user.id,
        entity_type="queue",
        entity_id=entry.id,
        new_value={"pool_amount": body.pool_amount},
    )

    await EventService.publish(EventType.QUEUE_JOINED, {"pool_amount": body.pool_amount, "entry_id": entry.id}, user.id)

    matched = entry.match_id is not None
    return {
        "message": "Match found!" if matched else "Joined queue",
        "entry_id": entry.id,
        "pool_amount": entry.pool_amount,
        "matched": matched,
        "match_id": entry.match_id,
    }


@router.post("/cancel")
async def cancel_queue(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = QueueService(db)
    try:
        result = await svc.cancel_queue(user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    await EventService.publish(EventType.QUEUE_LEFT, result, user.id)
    return result


@router.get("/status")
async def queue_status(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = QueueService(db)
    status_data = await svc.get_queue_status(user.id)
    if not status_data:
        return {"in_queue": False}
    return {"in_queue": True, **status_data}


@router.post("/expire-stale")
async def expire_stale(admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    svc = QueueService(db)
    count = await svc.expire_stale_entries()
    return {"expired": count}


@router.get("/events")
async def recent_events(limit: int = 50, admin: User = Depends(get_admin_user)):
    return {"events": EventService.get_recent(limit)}
