from collections.abc import Sequence
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.context import AppContext
from app.models.enums import Channel, MessageRole
from app.models.message import Message
from app.models.ticket import Ticket
from app.repositories.message_repository import MessageRepository
from app.schemas.ticket import TicketRead
from app.services.ticket_service import TicketService
from app.utils.time import local_now


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
        self.session_window_minutes: int = get_settings().SESSION_WINDOW_MINUTES

    async def handle_incoming(
        self,
        channel: Channel,
        client_id: str,
        text: str,
        channel_metadata: dict[str, Any] | None = None,
    ) -> tuple[str, Ticket]:
        logger.debug(
            "Incoming message | channel={channel} client_id={client_id} text={text!r}",
            channel=channel.value,
            client_id=client_id,
            text=text,
        )
        ticket = await self.ticket_service.get_or_create_session(
            channel, client_id, self.session_window_minutes
        )
        prior = await self.message_repository.list_for_ticket(ticket.ticket_id)
        history = build_history(prior)
        logger.debug(
            "Session resolved | ticket_id={ticket_id} prior_messages={count}",
            ticket_id=ticket.ticket_id,
            count=len(prior),
        )

        await self.message_repository.add(
            Message(ticket_id=ticket.ticket_id, role=MessageRole.CLIENT, text=text, channel=channel)
        )

        now = local_now(self.context.timezone)
        ticket_reference = f"#{ticket.ticket_id[:8]}"
        result = await self.context.pipeline.run(
            text, history, now, self.context.system_prompt, ticket_reference
        )

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
            logger.debug(
                "Escalating ticket | ticket_id={ticket_id} target={target} priority={priority}",
                ticket_id=ticket.ticket_id,
                target=result.escalation_target.value,
                priority=result.priority.value,
            )
            await self.context.escalation_service.notify(ticket, result)

        await self.session.commit()
        await self.session.refresh(ticket)

        outbound = self.context.channels.get(channel)
        if outbound is not None:
            logger.debug(
                "Sending reply | channel={channel} client_id={client_id} reply={reply!r}",
                channel=channel.value,
                client_id=client_id,
                reply=result.reply,
            )
            await outbound.send(client_id, result.reply)
        else:
            logger.debug("No outbound channel registered for {channel}", channel=channel.value)

        await self.context.websocket_manager.broadcast(
            {"type": "ticket", "ticket": TicketRead.model_validate(ticket).model_dump(mode="json")}
        )
        return result.reply, ticket
