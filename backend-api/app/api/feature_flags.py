"""Feature flag admin API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.middleware.auth import get_admin_user, get_current_user
from app.models.user import User
from app.services.feature_flag_service import FeatureFlagService
from app.services.audit_service import AuditService, AuditAction

router = APIRouter(prefix="/api/admin/feature-flags", tags=["feature-flags"])


@router.get("/")
async def list_flags(user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    svc = FeatureFlagService(db)
    flags = await svc.get_all()
    return {"flags": [
        {"key": f.key, "name": f.name, "description": f.description,
         "is_enabled": f.is_enabled, "updated_by": f.updated_by, "updated_at": str(f.updated_at)}
        for f in flags
    ]}


@router.put("/{key}")
async def toggle_flag(key: str, enabled: bool, user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    svc = FeatureFlagService(db)
    old_flag = await svc.get(key)
    old_val = old_flag.is_enabled if old_flag else False
    flag = await svc.toggle(key, enabled, updated_by=user.id)
    audit = AuditService(db)
    await audit.log(
        action=AuditAction.FEATURE_FLAG_TOGGLE, user_id=user.id,
        entity_type="feature_flag", entity_id=key,
        old_value={"enabled": old_val}, new_value={"enabled": enabled},
    )
    return {"message": f"Feature flag '{key}' {'enabled' if enabled else 'disabled'}", "is_enabled": flag.is_enabled}


@router.post("/seed")
async def seed_flags(user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    svc = FeatureFlagService(db)
    await svc.seed_defaults()
    await db.commit()
    return {"message": "Default feature flags seeded"}


@router.get("/public")
async def public_flags(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = FeatureFlagService(db)
    flags = await svc.get_all_as_dict()
    return flags
