from pydantic import BaseModel
from datetime import datetime


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    per_page: int
    total_pages: int


class LeaderboardResponse(BaseModel):
    user_id: str
    name: str | None
    avatar_url: str | None
    wins: int
    matches_played: int
    win_rate: float
    total_earnings: float
    rank: int

    class Config:
        from_attributes = True


class LeaderboardPeriod(BaseModel):
    period: str  # "weekly", "monthly", "all_time"
    start_date: datetime | None = None
    end_date: datetime | None = None


class GiveawayResponse(BaseModel):
    id: str
    name: str
    description: str | None
    type: str
    status: str
    prize_amount: float
    winners_count: int
    qualification_threshold: float
    winners: str | None
    drawn_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    body: str
    data: str | None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralStats(BaseModel):
    total_referrals: int
    active_referrals: int
    total_earned: float
    referral_code: str
