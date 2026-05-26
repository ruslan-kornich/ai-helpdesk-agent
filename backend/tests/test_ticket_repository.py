from datetime import datetime, timedelta, timezone

import pytest

from app.models.enums import Category, Channel, Priority, Sentiment
from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository


def _make_ticket(client_id: str) -> Ticket:
    return Ticket(
        channel=Channel.TELEGRAM,
        client_id=client_id,
        category=Category.UNKNOWN,
        priority=Priority.NORMAL,
        summary="test",
        conversation_snippet="",
        escalation_target=None,
        resolved_by_ai=False,
        sentiment=Sentiment.NEUTRAL,
        ticket_metadata={},
    )


@pytest.mark.asyncio
async def test_add_and_get(session):
    repository = TicketRepository(session)
    created = await repository.add(_make_ticket("client-1"))
    fetched = await repository.get(created.ticket_id)
    assert fetched is not None
    assert fetched.client_id == "client-1"


@pytest.mark.asyncio
async def test_active_within_window_is_reused(session):
    repository = TicketRepository(session)
    await repository.add(_make_ticket("client-1"))
    active = await repository.get_active(
        client_id="client-1", channel=Channel.TELEGRAM, window_minutes=30
    )
    assert active is not None


@pytest.mark.asyncio
async def test_stale_ticket_outside_window_is_not_active(session):
    repository = TicketRepository(session)
    stale = _make_ticket("client-1")
    stale.updated_at = datetime.now(timezone.utc) - timedelta(minutes=45)
    await repository.add(stale)
    active = await repository.get_active(
        client_id="client-1", channel=Channel.TELEGRAM, window_minutes=30
    )
    assert active is None


@pytest.mark.asyncio
async def test_active_is_channel_scoped(session):
    repository = TicketRepository(session)
    await repository.add(_make_ticket("client-1"))
    active = await repository.get_active(
        client_id="client-1", channel=Channel.WHATSAPP, window_minutes=30
    )
    assert active is None
