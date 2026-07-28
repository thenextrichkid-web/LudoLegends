"""In-app notification endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/")
async def list_notifications(page: int = 1, per_page: int = 20, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    notifications, total = await svc.get_user_notifications(user.id, page, per_page)
    return {
        "notifications": [
            {"id": n.id, "type": n.type.value, "title": n.title, "body": n.body,
             "data": n.data, "is_read": n.is_read, "created_at": str(n.created_at)}
            for n in notifications
        ],
        "total": total, "page": page, "per_page": per_page,
    }


@router.get("/unread-count")
async def unread_count(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    count = await svc.get_unread_count(user.id)
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_read(notification_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    try:
        await svc.mark_read(user.id, notification_id)
        return {"message": "Marked as read"}
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/read-all")
async def mark_all_read(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    count = await svc.mark_all_read(user.id)
    return {"message": f"Marked {count} notifications as read"}
