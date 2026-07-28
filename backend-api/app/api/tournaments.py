from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.services.tournament_service import TournamentService
from app.schemas.tournament import TournamentCreate, TournamentResponse, TournamentList
from app.middleware.auth import get_current_user, get_admin_user
from app.models.user import User

router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])


@router.post("/", response_model=TournamentResponse)
async def create_tournament(body: TournamentCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(get_admin_user)):
    svc = TournamentService(db)
    try:
        return await svc.create_tournament(body.model_dump(), admin.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=TournamentList)
async def list_tournaments(status_filter: str | None = None, page: int = 1, per_page: int = 20, db: AsyncSession = Depends(get_db)):
    svc = TournamentService(db)
    tournaments, total = await svc.list_tournaments(status=status_filter, page=page, per_page=per_page)
    return TournamentList(tournaments=tournaments, total=total, page=page, per_page=per_page)


@router.get("/my/joined")
async def my_joined_tournaments(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from app.models.tournament import TournamentParticipant, Tournament
    result = await db.execute(
        select(Tournament)
        .join(TournamentParticipant, TournamentParticipant.tournament_id == Tournament.id)
        .where(TournamentParticipant.user_id == user.id)
        .order_by(Tournament.starts_at.desc())
    )
    tournaments = list(result.scalars().all())
    return [TournamentResponse.model_validate(t) for t in tournaments]


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(tournament_id: str, db: AsyncSession = Depends(get_db)):
    svc = TournamentService(db)
    try:
        return await svc.get_tournament(tournament_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{tournament_id}/join")
async def join_tournament(tournament_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    svc = TournamentService(db)
    try:
        participant = await svc.join_tournament(user.id, tournament_id)
        return {"message": "Joined successfully", "participant_id": participant.id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{tournament_id}/participants")
async def get_participants(tournament_id: str, db: AsyncSession = Depends(get_db)):
    svc = TournamentService(db)
    return await svc.get_participants(tournament_id)


@router.post("/{tournament_id}/cancel")
async def cancel_tournament(tournament_id: str, reason: str = "", db: AsyncSession = Depends(get_db), admin: User = Depends(get_admin_user)):
    svc = TournamentService(db)
    try:
        tournament = await svc.cancel_tournament(tournament_id, reason)
        return {"message": "Tournament cancelled", "status": tournament.status}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
