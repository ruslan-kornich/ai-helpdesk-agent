from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.context import AppContext
from app.models.enums import Channel, MessageRole
from app.models.message import Message
from app.models.ticket import Ticket
from app.repositories.message_repository import MessageRepository
from app.schemas.ticket import TicketRead
from app.services.ticket_service import TicketService
from app.utils.time import local_now

_SESSION_WINDOW_MINUTES = 30


def build_history(messages: Sequence[Message]) -> str:
    return "\n".join(f"{message.role.value}: {message.text}" for message in messages)


class ConversationService:
    def __init__(
        self,
        session: AsyncSession,
        ticket_service: TicketService,
        message_repository: MessageRepository,
        context: AppContext,
    ) -> None:
        self.session = session
        self.ticket_service = ticket_service
        self.message_repository = message_repository
        self.context = context

    async def handle_incoming(
        self,
        channel: Channel,
        client_id: str,
        text: str,
        channel_metadata: dict[str, Any] | None = None,
    ) -> tuple[str, Ticket]:
        ticket = await self.ticket_service.get_or_create_session(
            channel, client_id, _SESSION_WINDOW_MINUTES
        )
        prior = await self.message_repository.list_for_ticket(ticket.ticket_id)
        history = build_history(prior)

        await self.message_repository.add(
            Message(ticket_id=ticket.ticket_id, role=MessageRole.CLIENT, text=text, channel=channel)
        )

        now = local_now(self.context.timezone)
        result = await self.context.pipeline.run(text, history, now, self.context.system_prompt)

        await self.message_repository.add(
            Message(
                ticket_id=ticket.ticket_id,
                role=MessageRole.AGENT,
                text=result.reply,
                channel=channel,
            )
        )

        messages = await self.message_repository.list_for_ticket(ticket.ticket_id)
        await self.ticket_service.apply_result(ticket, result, messages, channel_metadata)

        if result.escalation_target is not None:
            await self.context.escalation_service.notify(ticket, result)

        await self.session.commit()
        await self.session.refresh(ticket)

        outbound = self.context.channels.get(channel)
        if outbound is not None:
            await outbound.send(client_id, result.reply)

        await self.context.websocket_manager.broadcast(
            {"type": "ticket", "ticket": TicketRead.model_validate(ticket).model_dump(mode="json")}
        )
        return result.reply, ticket
