from collections import Counter
from collections.abc import Sequence

from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository
from app.schemas.analytics import AnalyticsReport, DailyBucket


def _rate(part: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(part / total, 4)


def compute_report(tickets: Sequence[Ticket]) -> AnalyticsReport:
    total = len(tickets)
    by_channel = Counter(ticket.channel.value for ticket in tickets)
    by_category = Counter(ticket.category.value for ticket in tickets)
    by_sentiment = Counter(ticket.sentiment.value for ticket in tickets)
    by_date = Counter(ticket.created_at.date().isoformat() for ticket in tickets)

    resolved = sum(1 for ticket in tickets if ticket.resolved_by_ai)
    escalated = total - resolved
    after_hours = sum(
        1 for ticket in tickets if (ticket.ticket_metadata or {}).get("was_after_hours")
    )

    by_day = [DailyBucket(date=date, count=count) for date, count in sorted(by_date.items())]

    return AnalyticsReport(
        total_tickets=total,
        by_channel=dict(by_channel),
        by_category=dict(by_category),
        by_day=by_day,
        escalation_rate=_rate(escalated, total),
        ai_resolution_rate=_rate(resolved, total),
        sentiment_distribution=dict(by_sentiment),
        after_hours_volume=after_hours,
    )


class AnalyticsService:
    def __init__(self, ticket_repository: TicketRepository) -> None:
        self.ticket_repository = ticket_repository

    async def build_report(self) -> AnalyticsReport:
        tickets = await self.ticket_repository.list_all()
        return compute_report(tickets)
