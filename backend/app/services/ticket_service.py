from collections.abc import Sequence
from typing import Any

from app.agent.pipeline import AgentResult
from app.models.enums import Category, Channel, MessageRole, Priority, Sentiment
from app.models.message import Message
from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository


def build_snippet(messages: Sequence[Message], max_messages: int = 10) -> str:
    """Join the first few messages into a short transcript stored on the ticket."""
    selected = list(messages)[:max_messages]
    return "\n".join(f"{message.role.value}: {message.text}" for message in selected)


class TicketService:
    """Resolves conversation sessions to tickets and writes agent results back onto them."""

    def __init__(self, ticket_repository: TicketRepository) -> None:
        self.ticket_repository = ticket_repository

    def _new_ticket(
        self, channel: Channel, client_id: str, metadata: dict[str, Any]
    ) -> Ticket:
        return Ticket(
            channel=channel,
            client_id=client_id,
            category=Category.UNKNOWN,
            priority=Priority.NORMAL,
            summary="",
            conversation_snippet="",
            escalation_target=None,
            resolved_by_ai=False,
            sentiment=Sentiment.NEUTRAL,
            ticket_metadata=metadata,
        )

    async def get_or_create_session(
        self,
        channel: Channel,
        client_id: str,
        window_minutes: int,
        channel_metadata: dict[str, Any] | None = None,
    ) -> Ticket:
        """Return the ticket for this conversation, creating one if none is active.

        Zendesk conversations are keyed by their ``zendesk_ticket_id``; other channels
        reuse the client's last ticket while it stays within ``window_minutes``.
        """
        if (
            channel == Channel.ZENDESK
            and channel_metadata
            and channel_metadata.get("zendesk_ticket_id")
        ):
            zendesk_ticket_id = str(channel_metadata["zendesk_ticket_id"])
            existing = await self.ticket_repository.get_by_zendesk_ticket_id(zendesk_ticket_id)
            if existing is not None:
                return existing
            return await self.ticket_repository.add(
                self._new_ticket(channel, client_id, {"zendesk_ticket_id": zendesk_ticket_id})
            )

        active = await self.ticket_repository.get_active(client_id, channel, window_minutes)
        if active is not None:
            return active
        return await self.ticket_repository.add(
            self._new_ticket(channel, client_id, {})
        )

    async def apply_result(
        self,
        ticket: Ticket,
        result: AgentResult,
        messages: Sequence[Message],
        channel_metadata: dict[str, Any] | None = None,
    ) -> Ticket:
        """Copy the agent result onto the ticket and persist it, deriving a summary if absent."""
        ticket.category = result.category
        ticket.priority = result.priority
        ticket.sentiment = result.sentiment
        ticket.escalation_target = result.escalation_target
        ticket.resolved_by_ai = result.resolved_by_ai
        ticket.conversation_snippet = build_snippet(messages)
        if result.summary:
            ticket.summary = result.summary[:200]
        elif not ticket.summary:
            first_client = next(
                (message.text for message in messages if message.role == MessageRole.CLIENT), ""
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
