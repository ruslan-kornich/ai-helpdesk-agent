from dataclasses import dataclass
from datetime import datetime
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
    """Flatten Zendesk tickets and their comments into a single list of inbound records."""
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


def build_end_user_payload(name: str, email: str) -> dict[str, Any]:
    return {
        "user": {
            "name": name,
            "email": email,
            "role": "end-user",
            "verified": True,
        }
    }


def build_request_ticket_payload(
    requester_id: str, subject: str, text: str
) -> dict[str, Any]:
    return {
        "ticket": {
            "subject": subject,
            "requester_id": requester_id,
            "comment": {"body": text, "author_id": requester_id, "public": True},
            "tags": ["ai-helpdesk-agent"],
        }
    }


def build_requester_comment_payload(requester_id: str, text: str) -> dict[str, Any]:
    return {
        "ticket": {
            "comment": {"body": text, "author_id": requester_id, "public": True},
        }
    }


class ZendeskChannel(BaseChannel):
    """Zendesk REST client for polling requester comments and posting tickets and replies.

    All methods no-op when credentials are missing (see ``enabled``).
    """

    channel = Channel.ZENDESK

    def __init__(self, subdomain: str, email: str, api_token: str) -> None:
        self.subdomain = subdomain
        self.email = email
        self.api_token = api_token

    @property
    def enabled(self) -> bool:
        return bool(self.subdomain and self.email and self.api_token)

    @property
    def base_url(self) -> str:
        return f"https://{self.subdomain}.zendesk.com/api/v2"

    @property
    def auth(self) -> tuple[str, str]:
        return (f"{self.email}/token", self.api_token)

    async def fetch_new_comments(self, since: datetime) -> list[ZendeskInbound]:
        """Search tickets updated since ``since`` and return their comments as inbound records.

        Network or API errors are logged and swallowed as an empty list so the poller keeps running.
        """
        if not self.enabled:
            return []
        query = f"type:ticket updated>={since.strftime('%Y-%m-%d')}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                search = await client.get(
                    f"{self.base_url}/search.json",
                    params={"query": query, "sort_by": "updated_at", "sort_order": "asc"},
                    auth=self.auth,
                )
                search.raise_for_status()
                tickets = search.json().get("results", [])
                comments_by_ticket: dict[str, list[dict]] = {}
                for ticket in tickets:
                    zendesk_ticket_id = str(ticket["id"])
                    response = await client.get(
                        f"{self.base_url}/tickets/{zendesk_ticket_id}/comments.json",
                        params={"sort_order": "asc"},
                        auth=self.auth,
                    )
                    response.raise_for_status()
                    comments_by_ticket[zendesk_ticket_id] = response.json().get("comments", [])
            return parse_inbounds(tickets, comments_by_ticket)
        except Exception as error:
            logger.exception("Zendesk fetch_new_comments failed: {error}", error=error)
            return []

    async def post_reply(
        self, zendesk_ticket_id: str, text: str, fields: ZendeskTicketFields
    ) -> None:
        if not self.enabled:
            logger.warning("Zendesk credentials missing; skipping reply")
            return
        payload = build_reply_payload(text, fields)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.put(
                    f"{self.base_url}/tickets/{zendesk_ticket_id}.json",
                    json=payload,
                    auth=self.auth,
                )
                response.raise_for_status()
                logger.info(
                    "Zendesk reply posted for ticket {ticket_id}",
                    ticket_id=zendesk_ticket_id,
                )
        except Exception as error:
            logger.exception("Zendesk post_reply failed: {error}", error=error)

    async def find_or_create_end_user(self, name: str, email: str) -> str:
        payload = build_end_user_payload(name, email)
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{self.base_url}/users/create_or_update.json",
                json=payload,
                auth=self.auth,
            )
            response.raise_for_status()
            return str(response.json()["user"]["id"])

    async def create_request_ticket(
        self, requester_id: str, subject: str, text: str
    ) -> str:
        payload = build_request_ticket_payload(requester_id, subject, text)
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{self.base_url}/tickets.json", json=payload, auth=self.auth
            )
            response.raise_for_status()
            return str(response.json()["ticket"]["id"])

    async def append_comment_as_requester(
        self, zendesk_ticket_id: str, requester_id: str, text: str
    ) -> None:
        payload = build_requester_comment_payload(requester_id, text)
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.put(
                f"{self.base_url}/tickets/{zendesk_ticket_id}.json",
                json=payload,
                auth=self.auth,
            )
            response.raise_for_status()

    async def send(self, client_id: str, text: str) -> None:
        if not self.enabled:
            logger.warning("Zendesk credentials missing; skipping ticket creation")
            return
        url = f"{self.base_url}/tickets.json"
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
                    url, json=payload, auth=self.auth
                )
                response.raise_for_status()
                logger.info("Zendesk ticket created for {client}", client=client_id)
        except Exception as error:
            logger.exception("Zendesk ticket creation failed: {error}", error=error)
