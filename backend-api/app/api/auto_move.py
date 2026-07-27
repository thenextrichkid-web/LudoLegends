from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.middleware.auth import get_current_user, get_admin_user
from app.models.user import User
from app.models.settings import Setting
from app.services.auto_move_service import AutoMoveService

router = APIRouter(prefix="/api/auto-move", tags=["auto-move"])


@router.post("/record/{match_id}")
async def record_auto_move(match_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = AutoMoveService(db)
    try:
        return await svc.record_auto_move(match_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{match_id}")
async def get_auto_move_status(match_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = AutoMoveService(db)
    try:
        return await svc.get_match_auto_moves(match_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/config")
async def get_auto_move_config(user: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    svc = AutoMoveService(db)
    return await svc.get_penalty_config()


@router.put("/config")
async def update_auto_move_config(
    limit: int = 3,
    penalty_amount: float = 20.0,
    user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    import uuid
    for key, value in [("AUTO_MOVE_LIMIT", str(limit)), ("AUTO_MOVE_PENALTY_AMOUNT", str(penalty_amount))]:
        result = await db.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
            setting.updated_by = user.id
        else:
            setting = Setting(id=str(uuid.uuid4()), key=key, value=value, updated_by=user.id)
            db.add(setting)

    await db.commit()
    return {"message": "Auto move penalty config updated", "limit": limit, "penalty_amount": penalty_amount}
