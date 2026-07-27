from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.match_service import MatchService
from app.schemas.match import MatchSubmit, MatchVerify, MatchResponse
from app.middleware.auth import get_current_user, get_admin_user
from app.models.user import User

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.post("/submit", response_model=MatchResponse)
async def submit_match(body: MatchSubmit, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = MatchService(db)
    try:
        return await svc.submit_match(user.id, body.tournament_id, body.screenshot_url, body.result_notes)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/my", response_model=list[MatchResponse])
async def get_my_matches(page: int = 1, per_page: int = 20, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = MatchService(db)
    matches, total = await svc.get_user_matches(user.id, page, per_page)
    return matches


@router.get("/pending", response_model=list[MatchResponse])
async def get_pending_matches(page: int = 1, per_page: int = 20, admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    svc = MatchService(db)
    matches, total = await svc.get_pending_matches(page, per_page)
    return matches


@router.post("/{match_id}/verify", response_model=MatchResponse)
async def verify_match(match_id: str, body: MatchVerify, admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    svc = MatchService(db)
    try:
        return await svc.verify_match(
            match_id, body.action, body.winner_id, body.score, body.prize_awarded, body.rejection_reason
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
