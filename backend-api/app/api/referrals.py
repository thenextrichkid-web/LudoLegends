"""Referral API endpoints — stats, list, processing."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.referral_service import ReferralService
from app.middleware.auth import get_current_user, get_admin_user
from app.models.user import User

router = APIRouter(prefix="/api/referrals", tags=["referrals"])


@router.get("/stats")
async def get_referral_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get referral stats for the current user."""
    svc = ReferralService(db)
    try:
        return await svc.get_referral_stats(user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/list")
async def get_referral_list(
    page: int = 1,
    per_page: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List users referred by the current user."""
    svc = ReferralService(db)
    referrals, total = await svc.get_referral_list(user.id, page, per_page)
    return {
        "referrals": [
            {"id": r.id, "name": r.name, "phone": r.phone, "created_at": r.created_at}
            for r in referrals
        ],
        "total": total,
    }


@router.post("/process/{new_user_id}")
async def process_referral(
    new_user_id: str,
    referrer_code: str,
    user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Process a referral bonus (admin only)."""
    svc = ReferralService(db)
    result = await svc.process_referral(new_user_id, referrer_code)
    return result
