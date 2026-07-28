"""Metrics API endpoint — exposes collected metrics for monitoring."""

from fastapi import APIRouter, Depends
from app.middleware.auth import get_admin_user
from app.models.user import User
from app.core.metrics import metrics

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/")
async def get_metrics(admin: User = Depends(get_admin_user)):
    return metrics.snapshot()
