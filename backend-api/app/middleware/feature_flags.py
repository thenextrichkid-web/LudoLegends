"""Feature flag dependency — inject feature flag checks into endpoints."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.feature_flag_service import FeatureFlagService


def require_feature_flag(flag_key: str):
    async def _check(db: AsyncSession = Depends(get_db)):
        svc = FeatureFlagService(db)
        enabled = await svc.is_enabled(flag_key)
        if not enabled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature '{flag_key}' is not available",
            )
        return True
    return _check
