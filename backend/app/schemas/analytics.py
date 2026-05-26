from pydantic import BaseModel


class DailyBucket(BaseModel):
    date: str
    count: int


class AnalyticsReport(BaseModel):
    total_tickets: int
    by_channel: dict[str, int]
    by_category: dict[str, int]
    by_day: list[DailyBucket]
    escalation_rate: float
    ai_resolution_rate: float
    sentiment_distribution: dict[str, int]
    after_hours_volume: int
