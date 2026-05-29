from datetime import UTC, datetime, timedelta

import pytest

from app.models.enums import Category, Channel, MessageRole, Priority, Sentiment
from app.models.message import Message
from app.models.ticket import Ticket
from app.repositories.message_repository import MessageRepository
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
    stale.updated_at = datetime.now(UTC) - timedelta(minutes=45)
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


@pytest.mark.asyncio
async def test_messages_for_ticket_ordered(session):
    ticket_repository = TicketRepository(session)
    ticket = await ticket_repository.add(_make_ticket("client-1"))
    message_repository = MessageRepository(session)
    await message_repository.add(
        Message(
            ticket_id=ticket.ticket_id,
            role=MessageRole.CLIENT,
            text="first",
            channel=Channel.TELEGRAM,
        )
    )
    await message_repository.add(
        Message(
            ticket_id=ticket.ticket_id,
            role=MessageRole.AGENT,
            text="second",
            channel=Channel.TELEGRAM,
        )
    )
    history = await message_repository.list_for_ticket(ticket.ticket_id)
    assert [message.text for message in history] == ["first", "second"]


@pytest.mark.asyncio
async def test_get_by_zendesk_ticket_id_found_and_missing(session):
    repository = TicketRepository(session)
    ticket = _make_ticket("requester-1")
    ticket.channel = Channel.ZENDESK
    ticket.ticket_metadata = {"zendesk_ticket_id": "555"}
    await repository.add(ticket)

    found = await repository.get_by_zendesk_ticket_id("555")
    assert found is not None
    assert found.ticket_metadata["zendesk_ticket_id"] == "555"

    missing = await repository.get_by_zendesk_ticket_id("999")
    assert missing is None
