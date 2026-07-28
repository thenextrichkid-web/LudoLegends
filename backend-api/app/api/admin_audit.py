"""Admin audit log API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.middleware.auth import get_admin_user
from app.models.user import User
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/admin/audit", tags=["admin-audit"])


@router.get("/")
async def list_audit_logs(
    user_id: str | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    page: int = 1,
    per_page: int = 20,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AuditService(db)
    logs, total = await svc.get_logs(user_id=user_id, action=action, entity_type=entity_type, page=page, per_page=per_page)
    return {
        "logs": [
            {"id": l.id, "user_id": l.user_id, "action": l.action,
             "entity_type": l.entity_type, "entity_id": l.entity_id,
             "old_value": l.old_value, "new_value": l.new_value,
             "ip_address": l.ip_address, "user_agent": l.user_agent,
             "created_at": str(l.created_at)}
            for l in logs
        ],
        "total": total, "page": page, "per_page": per_page,
    }
