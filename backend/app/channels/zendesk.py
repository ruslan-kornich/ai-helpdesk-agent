from dataclasses import dataclass
from typing import Any

import httpx
from loguru import logger

from app.channels.base import BaseChannel
from app.models.enums import Channel


@dataclass
class ZendeskInbound:
    zendesk_ticket_id: str
    requester_id: str
    comment_id: str
    author_id: str
    text: str


@dataclass
class ZendeskTicketFields:
    priority: str
    tags: list[str]
    status: str


def parse_inbounds(
    tickets: list[dict[str, Any]], comments_by_ticket: dict[str, list[dict[str, Any]]]
) -> list[ZendeskInbound]:
    inbounds: list[ZendeskInbound] = []
    for ticket in tickets:
        zendesk_ticket_id = str(ticket["id"])
        requester_id = str(ticket["requester_id"])
        for comment in comments_by_ticket.get(zendesk_ticket_id, []):
            inbounds.append(
                ZendeskInbound(
                    zendesk_ticket_id=zendesk_ticket_id,
                    requester_id=requester_id,
                    comment_id=str(comment["id"]),
                    author_id=str(comment["author_id"]),
                    text=comment["body"],
                )
            )
    return inbounds


def build_reply_payload(text: str, fields: ZendeskTicketFields) -> dict[str, Any]:
    return {
        "ticket": {
            "comment": {"body": text, "public": True},
            "priority": fields.priority,
            "status": fields.status,
            "tags": fields.tags,
        }
    }


class ZendeskChannel(BaseChannel):
    channel = Channel.ZENDESK

    def __init__(self, subdomain: str, email: str, api_token: str) -> None:
        self.subdomain = subdomain
        self.email = email
        self.api_token = api_token

    @property
    def enabled(self) -> bool:
        return bool(self.subdomain and self.email and self.api_token)

    async def send(self, client_id: str, text: str) -> None:
        if not self.enabled:
            logger.warning("Zendesk credentials missing; skipping ticket creation")
            return
        url = f"https://{self.subdomain}.zendesk.com/api/v2/tickets.json"
        payload = {
            "ticket": {
                "subject": f"Support conversation with {client_id}",
                "comment": {"body": text},
                "tags": ["ai-helpdesk-agent"],
            }
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    url, json=payload, auth=(f"{self.email}/token", self.api_token)
                )
                response.raise_for_status()
                logger.info("Zendesk ticket created for {client}", client=client_id)
        except Exception as error:
            logger.exception("Zendesk ticket creation failed: {error}", error=error)
