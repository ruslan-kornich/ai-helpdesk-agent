import httpx
from loguru import logger

from app.channels.base import BaseChannel
from app.models.enums import Channel


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
