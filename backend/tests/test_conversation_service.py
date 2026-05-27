import pytest

from app.agent.pipeline import AgentResult
from app.context import AppContext
from app.models.enums import Category, Channel, EscalationTarget, Priority, Sentiment
from app.repositories.message_repository import MessageRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.conversation_service import ConversationService
from app.services.escalation_service import EscalationService
from app.services.ticket_service import TicketService
from app.utils.websocket_manager import WebSocketManager


class FakePipeline:
    def __init__(self, result: AgentResult) -> None:
        self.result = result

    async def run(self, text, history, now, persona="", ticket_reference=""):
        return self.result


class FakeChannel:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def send(self, client_id, text):
        self.sent.append((client_id, text))


def _result() -> AgentResult:
    return AgentResult(
        category=Category.BILLING,
        priority=Priority.NORMAL,
        sentiment=Sentiment.NEUTRAL,
        escalation_target=EscalationTarget.FINANCE,
        resolved_by_ai=False,
        was_after_hours=False,
        entities={},
        reply="Here are the top-up instructions.",
    )


def _build_service(session) -> tuple[ConversationService, FakeChannel]:
    ticket_repository = TicketRepository(session)
    message_repository = MessageRepository(session)
    ticket_service = TicketService(ticket_repository)
    websocket_manager = WebSocketManager()
    escalation_service = EscalationService(websocket_manager, support_lead_channel="")
    channel = FakeChannel()
    context = AppContext(
        pipeline=FakePipeline(_result()),
        router_config=None,
        websocket_manager=websocket_manager,
        escalation_service=escalation_service,
        channels={Channel.TELEGRAM: channel},
        timezone="UTC",
        system_prompt="",
    )
    service = ConversationService(
        session=session,
        ticket_service=ticket_service,
        message_repository=message_repository,
        context=context,
    )
    return service, channel


@pytest.mark.asyncio
async def test_handle_incoming_creates_ticket_and_messages(session):
    service, channel = _build_service(session)
    reply, ticket = await service.handle_incoming(Channel.TELEGRAM, "client-1", "how do I top up?")
    assert reply == "Here are the top-up instructions."
    assert ticket.category == Category.BILLING
    assert ticket.escalation_target == EscalationTarget.FINANCE
    assert channel.sent == [("client-1", "Here are the top-up instructions.")]

    history = await service.message_repository.list_for_ticket(ticket.ticket_id)
    assert [message.role.value for message in history] == ["client", "agent"]


@pytest.mark.asyncio
async def test_second_message_appends_to_same_ticket(session):
    service, _ = _build_service(session)
    _, first = await service.handle_incoming(Channel.TELEGRAM, "client-1", "first")
    _, second = await service.handle_incoming(Channel.TELEGRAM, "client-1", "second")
    assert first.ticket_id == second.ticket_id
    history = await service.message_repository.list_for_ticket(first.ticket_id)
    assert len(history) == 4
