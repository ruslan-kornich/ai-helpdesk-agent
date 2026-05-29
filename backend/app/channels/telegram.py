import asyncio
from collections.abc import Awaitable, Callable

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatAction
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from loguru import logger

from app.channels.base import BaseChannel
from app.models.enums import Channel

IncomingHandler = Callable[[str, str, dict], Awaitable[None]]
ResetHandler = Callable[[str], Awaitable[None]]

# Telegram clears the typing indicator after ~5s, so it must be refreshed
# while the agent pipeline is still working on a reply.
_TYPING_REFRESH_SECONDS = 4.0

# /start is a Telegram client command, not a support request. It is answered with a
# static welcome and never reaches the pipeline, so it creates no ticket or escalation.
_WELCOME_MESSAGE = (
    "Вітаю! Я AI-асистент підтримки Gatum. Опишіть, будь ласка, ваше питання — щодо "
    "розсилок, поповнення балансу, доставки повідомлень або технічних проблем, "
    "і я допоможу чи передам його спеціалісту."
)

# /new resets the conversation context so the next message opens a fresh ticket. Like
# /start it is a client command, answered statically and never routed to the pipeline,
# so it creates no ticket on its own.
_RESET_MESSAGE = (
    "Контекст очищено. Починаємо нову розмову — опишіть, будь ласка, ваше питання."
)

# Sent to the client when handling their message fails, so they get a reply instead of
# silence. {working_hours} is filled with the live working-hours label.
_ERROR_FALLBACK_TEMPLATE = (
    "Вітаю! Це AI-асистент підтримки Gatum. Виникла технічна помилка під час обробки "
    "вашого звернення. Ми працюємо у {working_hours} і повернемося до вас якнайшвидше."
)


async def _keep_typing(bot: Bot, chat_id: str) -> None:
    """Refresh the typing indicator until cancelled, so it persists while the pipeline runs."""
    try:
        while True:
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(_TYPING_REFRESH_SECONDS)
    except asyncio.CancelledError:
        pass
    except Exception as error:
        logger.debug("Telegram typing action failed for {chat}: {error}", chat=chat_id, error=error)


class TelegramChannel(BaseChannel):
    """Sends agent replies to a Telegram chat; failures are logged, never raised."""

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


def build_telegram_dispatcher(
    handler: IncomingHandler, reset_handler: ResetHandler
) -> Dispatcher:
    """Wire a dispatcher that answers /start and /new statically and routes text to the handler.

    Command handlers are registered before the catch-all text handler so aiogram matches
    them first; this keeps /new from reaching the pipeline and creating a ticket.
    """
    dispatcher = Dispatcher()

    @dispatcher.message(CommandStart())
    async def on_start_command(message: Message) -> None:
        chat_id = str(message.chat.id)
        logger.info("Telegram /start from {chat}", chat=chat_id)
        await message.answer(_WELCOME_MESSAGE)

    @dispatcher.message(Command("new"))
    async def on_new_command(message: Message) -> None:
        chat_id = str(message.chat.id)
        logger.info("Telegram /new from {chat}", chat=chat_id)
        await reset_handler(chat_id)
        await message.answer(_RESET_MESSAGE)

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
