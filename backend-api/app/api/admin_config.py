"""Admin API endpoints — site configuration management."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.middleware.auth import get_admin_user
from app.models.user import User
from app.services.config_service import ConfigService
from app.services.audit_service import AuditService, AuditAction

router = APIRouter(prefix="/api/admin/config", tags=["admin-config"])


@router.get("/")
async def list_configs(category: str | None = None, user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    svc = ConfigService(db)
    configs = await svc.get_all(category)
    return {"configs": [
        {"key": c.key, "value": c.value, "value_type": c.value_type, "category": c.category,
         "description": c.description, "updated_by": c.updated_by, "updated_at": str(c.updated_at)}
        for c in configs
    ]}


@router.get("/{key}")
async def get_config(key: str, user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    svc = ConfigService(db)
    val = await svc.get(key)
    if val is None:
        raise HTTPException(status_code=404, detail=f"Config key '{key}' not found")
    return {"key": key, "value": val}


@router.put("/{key}")
async def update_config(key: str, value: str, user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    svc = ConfigService(db)
    old_val = await svc.get(key)
    config = await svc.set(key, value, updated_by=user.id)
    audit = AuditService(db)
    await audit.log(
        action=AuditAction.CONFIG_CHANGE, user_id=user.id,
        entity_type="config", entity_id=key,
        old_value={"value": old_val}, new_value={"value": value},
    )
    return {"message": "Config updated", "key": key, "value": config.value}


@router.post("/seed")
async def seed_defaults(user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    svc = ConfigService(db)
    await svc.seed_defaults()
    await db.commit()
    return {"message": "Default configs seeded"}
