from pydantic import BaseModel
from datetime import datetime


class MatchSubmit(BaseModel):
    tournament_id: str
    screenshot_url: str
    result_notes: str | None = None


class MatchVerify(BaseModel):
    action: str  # "approve" or "reject"
    winner_id: str | None = None
    score: str | None = None
    prize_awarded: float = 0
    rejection_reason: str | None = None


class MatchResponse(BaseModel):
    id: str
    tournament_id: str
    user_id: str
    status: str
    screenshot_url: str | None
    result_notes: str | None
    rejection_reason: str | None = None
    submitted_at: datetime | None
    verified_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class MatchResultResponse(BaseModel):
    id: str
    match_id: str
    winner_id: str | None
    score: str | None
    prize_awarded: float
    created_at: datetime

    class Config:
        from_attributes = True
