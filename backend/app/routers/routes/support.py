import httpx
from fastapi import APIRouter
from loguru import logger

from app.channels.zendesk import ZendeskChannel
from app.dependencies import ContextDep, MessageRepositoryDep, TicketRepositoryDep
from app.models.enums import Channel, MessageRole
from app.schemas.support import (
    SupportChatRequest,
    SupportChatResponse,
    SupportMessageRead,
    SupportMessagesResponse,
)
from app.utils.exceptions import BusinessError

router = APIRouter()


@router.post("/chat", response_model=SupportChatResponse)
async def support_chat(
    payload: SupportChatRequest, context: ContextDep
) -> SupportChatResponse:
    if "@" not in payload.email:
        raise BusinessError("A valid email is required", status_code=400)
    channel = context.channels[Channel.ZENDESK]
    if not isinstance(channel, ZendeskChannel) or not channel.enabled:
        raise BusinessError("Support channel is not configured", status_code=503)
    subject = f"Support chat with {payload.name}"
    try:
        requester_id = await channel.find_or_create_end_user(payload.name, payload.email)
        if payload.zendesk_ticket_id:
            try:
                await channel.append_comment_as_requester(
                    payload.zendesk_ticket_id, requester_id, payload.text
                )
                zendesk_ticket_id = payload.zendesk_ticket_id
            except httpx.HTTPStatusError as error:
                # Stale ticket id from a deleted/foreign ticket: open a fresh one.
                if error.response.status_code != 404:
                    raise
                logger.warning(
                    "Zendesk ticket {ticket_id} not found; creating a new ticket",
                    ticket_id=payload.zendesk_ticket_id,
                )
                zendesk_ticket_id = await channel.create_request_ticket(
                    requester_id, subject, payload.text
                )
        else:
            zendesk_ticket_id = await channel.create_request_ticket(
                requester_id, subject, payload.text
            )
    except httpx.HTTPStatusError as error:
        logger.error(
            "Zendesk API error {status} on {url}: {body}",
            status=error.response.status_code,
            url=error.request.url,
            body=error.response.text[:500],
        )
        raise BusinessError(
            "Failed to deliver message to support", status_code=502
        ) from error
    except httpx.HTTPError as error:
        logger.error("Zendesk request failed: {error}", error=repr(error))
        raise BusinessError(
            "Failed to deliver message to support", status_code=502
        ) from error
    return SupportChatResponse(zendesk_ticket_id=zendesk_ticket_id)


@router.get("/messages", response_model=SupportMessagesResponse)
async def support_messages(
    zendesk_ticket_id: str,
    ticket_repository: TicketRepositoryDep,
    message_repository: MessageRepositoryDep,
    after_id: int = 0,
) -> SupportMessagesResponse:
    ticket = await ticket_repository.get_by_zendesk_ticket_id(zendesk_ticket_id)
    if ticket is None:
        return SupportMessagesResponse(messages=[])
    messages = await message_repository.list_for_ticket(ticket.ticket_id)
    replies = [
        SupportMessageRead.model_validate(message)
        for message in messages
        if message.role == MessageRole.AGENT and message.id > after_id
    ]
    return SupportMessagesResponse(messages=replies)
