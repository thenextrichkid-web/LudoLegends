from pydantic import BaseModel, Field
from datetime import datetime


class TournamentCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    description: str | None = None
    type: str
    entry_fee: float = Field(..., ge=0)
    prize_pool: float = Field(..., gt=0)
    max_participants: int = Field(..., gt=1)
    starts_at: datetime
    ends_at: datetime | None = None
    registration_deadline: datetime | None = None
    rules: str | None = None


class TournamentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    rules: str | None = None


class TournamentResponse(BaseModel):
    id: str
    name: str
    description: str | None
    type: str
    status: str
    entry_fee: float
    prize_pool: float
    max_participants: int
    current_participants: int
    starts_at: datetime
    ends_at: datetime | None
    registration_deadline: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class TournamentList(BaseModel):
    tournaments: list[TournamentResponse]
    total: int
    page: int
    per_page: int


class JoinTournament(BaseModel):
    tournament_id: str
