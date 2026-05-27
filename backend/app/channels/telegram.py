import asyncio
from collections.abc import Awaitable, Callable

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatAction
from aiogram.types import Message
from loguru import logger

from app.channels.base import BaseChannel
from app.models.enums import Channel

IncomingHandler = Callable[[str, str, dict], Awaitable[None]]

# Telegram clears the typing indicator after ~5s, so it must be refreshed
# while the agent pipeline is still working on a reply.
_TYPING_REFRESH_SECONDS = 4.0


async def _keep_typing(bot: Bot, chat_id: str) -> None:
    try:
        while True:
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(_TYPING_REFRESH_SECONDS)
    except asyncio.CancelledError:
        pass
    except Exception as error:
        logger.debug("Telegram typing action failed for {chat}: {error}", chat=chat_id, error=error)


class TelegramChannel(BaseChannel):
    channel = Channel.TELEGRAM

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def send(self, client_id: str, text: str) -> None:
        try:
            await self.bot.send_message(chat_id=client_id, text=text)
            logger.debug("Telegram message sent to {client}", client=client_id)
        except Exception as error:
            logger.exception(
                "Telegram send failed for {client}: {error}",
                client=client_id,
                error=error,
            )


def build_telegram_dispatcher(handler: IncomingHandler) -> Dispatcher:
    dispatcher = Dispatcher()

    @dispatcher.message(F.text)
    async def on_text_message(message: Message) -> None:
        chat_id = str(message.chat.id)
        text = message.text or ""
        logger.info("Telegram update from {chat}: {text}", chat=chat_id, text=text)
        metadata = {"telegram_chat_id": chat_id}
        typing_task = asyncio.create_task(_keep_typing(message.bot, chat_id))
        try:
            await handler(chat_id, text, metadata)
        except Exception as error:
            logger.exception("Telegram handler failed: {error}", error=error)
        finally:
            typing_task.cancel()

    return dispatcher
