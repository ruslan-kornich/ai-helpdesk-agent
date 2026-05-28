import pytest

from app.models.enums import Channel, MessageRole
from app.models.message import Message
from app.repositories.ticket_repository import TicketRepository
from app.services.ticket_service import TicketService, build_snippet


def _message(role: MessageRole, text: str) -> Message:
    return Message(ticket_id="t1", role=role, text=text, channel=Channel.TELEGRAM)


def test_build_snippet_orders_and_labels_roles():
    messages = [
        _message(MessageRole.CLIENT, "hello"),
        _message(MessageRole.AGENT, "hi there"),
        _message(MessageRole.CLIENT, "i have a question"),
    ]
    snippet = build_snippet(messages)
    assert "client: hello" in snippet
    assert "agent: hi there" in snippet
    assert snippet.index("client: hello") < snippet.index("agent: hi there")


def test_build_snippet_caps_messages():
    messages = [_message(MessageRole.CLIENT, f"msg {index}") for index in range(20)]
    snippet = build_snippet(messages, max_messages=10)
    assert snippet.count("\n") == 9


@pytest.mark.asyncio
async def test_zendesk_session_reused_by_ticket_id(session):
    service = TicketService(TicketRepository(session))
    first = await service.get_or_create_session(
        Channel.ZENDESK, "requester-1", 30, {"zendesk_ticket_id": "777"}
    )
    second = await service.get_or_create_session(
        Channel.ZENDESK, "requester-1", 30, {"zendesk_ticket_id": "777"}
    )
    assert first.ticket_id == second.ticket_id


@pytest.mark.asyncio
async def test_zendesk_distinct_tickets_for_distinct_ids(session):
    service = TicketService(TicketRepository(session))
    first = await service.get_or_create_session(
        Channel.ZENDESK, "requester-1", 30, {"zendesk_ticket_id": "1"}
    )
    second = await service.get_or_create_session(
        Channel.ZENDESK, "requester-1", 30, {"zendesk_ticket_id": "2"}
    )
    assert first.ticket_id != second.ticket_id
