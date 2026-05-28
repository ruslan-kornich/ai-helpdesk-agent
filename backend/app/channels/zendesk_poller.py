import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

from loguru import logger

from app.channels.zendesk import ZendeskChannel, ZendeskInbound, ZendeskTicketFields
from app.models.ticket import Ticket

InboundHandler = Callable[[ZendeskInbound], Awaitable[None]]


def is_new_comment(metadata: dict | None, comment_id: str) -> bool:
    if not metadata:
        return True
    last_seen = metadata.get("last_seen_comment_id")
    if last_seen is None:
        return True
    return int(comment_id) > int(last_seen)


def map_ticket_fields(ticket: Ticket) -> ZendeskTicketFields:
    tags = ["ai-helpdesk-agent", f"cat_{ticket.category.value}"]
    if ticket.escalation_target is not None:
        tags.append(f"esc_{ticket.escalation_target.value}")
    status = "solved" if ticket.resolved_by_ai else "open"
    return ZendeskTicketFields(priority=ticket.priority.value, tags=tags, status=status)


class ZendeskPoller:
    def __init__(
        self,
        channel: ZendeskChannel,
        handler: InboundHandler,
        interval_seconds: int,
    ) -> None:
        self.channel = channel
        self.handler = handler
        self.interval_seconds = interval_seconds
        self.watermark = datetime.now(UTC)

    async def poll_once(self) -> None:
        cycle_start = datetime.now(UTC)
        inbounds = await self.channel.fetch_new_comments(self.watermark)
        for inbound in inbounds:
            if inbound.author_id != inbound.requester_id:
                continue
            await self.handler(inbound)
        self.watermark = cycle_start

    async def run(self) -> None:
        while True:
            try:
                await self.poll_once()
            except Exception as error:
                logger.exception("Zendesk poll cycle failed: {error}", error=error)
            await asyncio.sleep(self.interval_seconds)
