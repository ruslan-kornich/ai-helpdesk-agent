import asyncio
from collections.abc import Awaitable, Callable

import httpx
from loguru import logger

from app.channels.base import BaseChannel
from app.models.enums import Channel

IncomingHandler = Callable[[str, str, dict], Awaitable[None]]


class TelegramClient:
    def __init__(self, token: str) -> None:
        self.base_url = f"https://api.telegram.org/bot{token}"

    async def get_updates(self, offset: int, timeout: int = 25) -> list[dict]:
        async with httpx.AsyncClient(timeout=timeout + 5) as client:
            response = await client.get(
                f"{self.base_url}/getUpdates",
                params={"offset": offset, "timeout": timeout},
            )
            response.raise_for_status()
            return response.json().get("result", [])

    async def send_message(self, chat_id: str, text: str) -> None:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{self.base_url}/sendMessage",
                json={"chat_id": chat_id, "text": text},
            )
            response.raise_for_status()


class TelegramChannel(BaseChannel):
    channel = Channel.TELEGRAM

    def __init__(self, client: TelegramClient) -> None:
        self.client = client

    async def send(self, client_id: str, text: str) -> None:
        try:
            await self.client.send_message(client_id, text)
        except Exception as error:
            logger.exception(
                "Telegram send failed for {client}: {error}",
                client=client_id,
                error=error,
            )


async def run_telegram_polling(
    client: TelegramClient,
    handler: IncomingHandler,
    stop_event: asyncio.Event,
) -> None:
    offset = 0
    logger.info("Telegram polling started")
    while not stop_event.is_set():
        try:
            updates = await client.get_updates(offset=offset)
        except Exception as error:
            logger.warning("Telegram getUpdates failed: {error}", error=error)
            await asyncio.sleep(3)
            continue
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message")
            if not message or "text" not in message:
                continue
            chat_id = str(message["chat"]["id"])
            text = message["text"]
            metadata = {"telegram_chat_id": chat_id}
            try:
                await handler(chat_id, text, metadata)
            except Exception as error:
                logger.exception("Telegram handler failed: {error}", error=error)
    logger.info("Telegram polling stopped")
