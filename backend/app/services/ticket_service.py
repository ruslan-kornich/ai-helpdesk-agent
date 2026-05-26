from collections.abc import Sequence
from typing import Any

from app.agent.pipeline import AgentResult
from app.models.enums import Channel
from app.models.message import Message
from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository


def build_snippet(messages: Sequence[Message], max_messages: int = 10) -> str:
    selected = list(messages)[:max_messages]
    return "\n".join(f"{message.role.value}: {message.text}" for message in selected)


class TicketService:
    def __init__(self, ticket_repository: TicketRepository) -> None:
        self.ticket_repository = ticket_repository

    async def get_or_create_session(
        self, channel: Channel, client_id: str, window_minutes: int
    ) -> Ticket:
        from app.models.enums import Category, Priority, Sentiment

        active = await self.ticket_repository.get_active(client_id, channel, window_minutes)
        if active is not None:
            return active
        ticket = Ticket(
            channel=channel,
            client_id=client_id,
            category=Category.UNKNOWN,
            priority=Priority.NORMAL,
            summary="",
            conversation_snippet="",
            escalation_target=None,
            resolved_by_ai=False,
            sentiment=Sentiment.NEUTRAL,
            ticket_metadata={},
        )
        return await self.ticket_repository.add(ticket)

    async def apply_result(
        self,
        ticket: Ticket,
        result: AgentResult,
        messages: Sequence[Message],
        channel_metadata: dict[str, Any] | None = None,
    ) -> Ticket:
        ticket.category = result.category
        ticket.priority = result.priority
        ticket.sentiment = result.sentiment
        ticket.escalation_target = result.escalation_target
        ticket.resolved_by_ai = result.resolved_by_ai
        ticket.conversation_snippet = build_snippet(messages)
        if not ticket.summary:
            first_client = next(
                (message.text for message in messages if message.role.value == "client"), ""
            )
            ticket.summary = first_client[:200]
        metadata = dict(ticket.ticket_metadata or {})
        metadata["was_after_hours"] = result.was_after_hours
        if result.entities:
            metadata["entities"] = result.entities
        if channel_metadata:
            metadata.update(channel_metadata)
        ticket.ticket_metadata = metadata
        return await self.ticket_repository.add(ticket)
