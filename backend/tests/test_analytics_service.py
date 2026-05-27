from datetime import datetime

import pytest

from app.models.enums import Category, Channel, EscalationTarget, Priority, Sentiment
from app.models.ticket import Ticket
from app.services.analytics_service import AnalyticsService, compute_report


def _ticket(
    channel: Channel,
    category: Category,
    sentiment: Sentiment,
    resolved_by_ai: bool,
    was_after_hours: bool,
    created_at: datetime,
    escalation_target: EscalationTarget | None = None,
) -> Ticket:
    return Ticket(
        channel=channel,
        client_id="client",
        category=category,
        priority=Priority.NORMAL,
        summary="s",
        conversation_snippet="",
        escalation_target=escalation_target,
        resolved_by_ai=resolved_by_ai,
        sentiment=sentiment,
        ticket_metadata={"was_after_hours": was_after_hours},
        created_at=created_at,
    )


def _sample() -> list[Ticket]:
    return [
        _ticket(Channel.TELEGRAM, Category.HOW_TO, Sentiment.POSITIVE, True, False, datetime(2026, 5, 20, 10, 0)),
        _ticket(Channel.TELEGRAM, Category.BILLING, Sentiment.NEUTRAL, False, False, datetime(2026, 5, 20, 11, 0), EscalationTarget.FINANCE),
        _ticket(Channel.WHATSAPP, Category.AFTER_HOURS, Sentiment.NEUTRAL, False, True, datetime(2026, 5, 21, 2, 0)),
        _ticket(Channel.ZENDESK, Category.OUTAGE, Sentiment.NEGATIVE, False, False, datetime(2026, 5, 21, 9, 0), EscalationTarget.L2_SUPPORT),
    ]


def test_total_and_distributions():
    report = compute_report(_sample())
    assert report.total_tickets == 4
    assert report.by_channel == {"telegram": 2, "whatsapp": 1, "zendesk": 1}
    assert report.by_category == {"how_to": 1, "billing": 1, "after_hours": 1, "outage": 1}
    assert report.sentiment_distribution == {"positive": 1, "neutral": 2, "negative": 1}


def test_rates_and_after_hours():
    report = compute_report(_sample())
    assert report.ai_resolution_rate == 0.25
    assert report.escalation_rate == 0.75
    assert report.after_hours_volume == 1


def test_daily_buckets_sorted():
    report = compute_report(_sample())
    assert [bucket.date for bucket in report.by_day] == ["2026-05-20", "2026-05-21"]
    assert [bucket.count for bucket in report.by_day] == [2, 2]


def test_empty_report_is_zeroed():
    report = compute_report([])
    assert report.total_tickets == 0
    assert report.escalation_rate == 0.0
    assert report.ai_resolution_rate == 0.0
    assert report.by_day == []


class FakeTicketRepository:
    def __init__(self, tickets: list[Ticket]) -> None:
        self._tickets = tickets

    async def list_all(self) -> list[Ticket]:
        return self._tickets


@pytest.mark.asyncio
async def test_service_delegates_to_repository():
    service = AnalyticsService(FakeTicketRepository(_sample()))
    report = await service.build_report()
    assert report.total_tickets == 4
    assert report.escalation_rate == 0.75
