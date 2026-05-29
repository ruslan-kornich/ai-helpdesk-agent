import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import cast

from aiogram import Bot
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from loguru import logger

from app.agent.analyzer import Analyzer
from app.agent.llm import OpenAIProvider
from app.agent.pipeline import AgentPipeline
from app.agent.responder import Responder
from app.agent.router import RouterConfig
from app.channels.mock import MockChannel
from app.channels.telegram import (
    _ERROR_FALLBACK_TEMPLATE,
    TelegramChannel,
    build_telegram_dispatcher,
)
from app.channels.zendesk import ZendeskChannel, ZendeskInbound
from app.channels.zendesk_poller import ZendeskPoller
from app.config.db import build_database_manager
from app.config.logger import setup_logging
from app.config.settings import get_settings
from app.context import AppContext
from app.knowledge.retriever import KeywordRetriever
from app.models.app_setting import AppSetting
from app.models.enums import Channel
from app.repositories.settings_repository import SettingsRepository
from app.routers.api import public_router
from app.routers.routes import ws
from app.services.escalation_service import EscalationService
from app.services.settings_service import SettingsService
from app.utils.exceptions import BusinessError, business_exception_handler
from app.utils.time import format_working_hours
from app.utils.websocket_manager import WebSocketManager

_FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
_DEFAULT_PERSONA = (
    "You are a friendly, concise support agent for the Gatum SMS/SMPP platform. "
    "Keep replies clear, professional, and grounded in the provided knowledge base."
)


def _build_context(telegram_bot: Bot | None, persisted: AppSetting) -> AppContext:
    settings = get_settings()
    llm = OpenAIProvider(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)
    retriever = KeywordRetriever()
    router_config = RouterConfig(
        confidence_threshold=settings.CONFIDENCE_THRESHOLD,
        working_hours_start=persisted.working_hours_start,
        working_hours_end=persisted.working_hours_end,
    )
    pipeline = AgentPipeline(
        analyzer=Analyzer(llm),
        responder=Responder(llm, retriever),
        config=router_config,
    )
    websocket_manager = WebSocketManager()
    telegram_channel = (
        TelegramChannel(telegram_bot) if telegram_bot is not None else MockChannel(Channel.TELEGRAM)
    )
    channels = {
        Channel.TELEGRAM: telegram_channel,
        Channel.ZENDESK: ZendeskChannel(
            settings.ZENDESK_SUBDOMAIN, settings.ZENDESK_EMAIL, settings.ZENDESK_API_TOKEN
        ),
        Channel.WHATSAPP: MockChannel(Channel.WHATSAPP),
        Channel.TEAMS: MockChannel(Channel.TEAMS),
    }
    return AppContext(
        pipeline=pipeline,
        router_config=router_config,
        websocket_manager=websocket_manager,
        escalation_service=EscalationService(websocket_manager, settings.SUPPORT_LEAD_CHANNEL),
        channels=channels,
        timezone=persisted.timezone,
        system_prompt=_DEFAULT_PERSONA,
    )


async def _telegram_handler_factory(app: FastAPI):
    from app.repositories.message_repository import MessageRepository
    from app.repositories.ticket_repository import TicketRepository
    from app.services.conversation_service import ConversationService
    from app.services.ticket_service import TicketService

    async def handler(chat_id: str, text: str, metadata: dict) -> None:
        manager = app.state.database_manager
        try:
            async with manager.session_factory() as session:
                service = ConversationService(
                    session=session,
                    ticket_service=TicketService(TicketRepository(session)),
                    message_repository=MessageRepository(session),
                    context=app.state.context,
                )
                await service.handle_incoming(Channel.TELEGRAM, chat_id, text, metadata)
        except Exception as error:
            # The session rolls back automatically when the context manager exits on
            # error. Without this the client would get silence; instead send a greeting
            # with the live working hours so they know we will follow up.
            logger.exception("Telegram message handling failed: {error}", error=error)
            context = app.state.context
            working_hours = format_working_hours(
                context.router_config.working_hours_start,
                context.router_config.working_hours_end,
                context.timezone,
            )
            fallback = _ERROR_FALLBACK_TEMPLATE.format(working_hours=working_hours)
            await context.channels[Channel.TELEGRAM].send(chat_id, fallback)

    return handler


async def _zendesk_handler_factory(app: FastAPI, zendesk_channel: ZendeskChannel):
    from app.channels.zendesk_poller import is_new_comment, map_ticket_fields
    from app.repositories.message_repository import MessageRepository
    from app.repositories.ticket_repository import TicketRepository
    from app.services.conversation_service import ConversationService
    from app.services.ticket_service import TicketService

    async def handler(inbound: ZendeskInbound) -> None:
        manager = app.state.database_manager
        async with manager.session_factory() as session:
            ticket_repository = TicketRepository(session)
            existing = await ticket_repository.get_by_zendesk_ticket_id(inbound.zendesk_ticket_id)
            existing_metadata = existing.ticket_metadata if existing is not None else None
            if not is_new_comment(existing_metadata, inbound.comment_id):
                return
            service = ConversationService(
                session=session,
                ticket_service=TicketService(ticket_repository),
                message_repository=MessageRepository(session),
                context=app.state.context,
            )
            reply, ticket = await service.handle_incoming(
                Channel.ZENDESK,
                inbound.requester_id,
                inbound.text,
                channel_metadata={
                    "zendesk_ticket_id": inbound.zendesk_ticket_id,
                    "zendesk_requester_id": inbound.requester_id,
                    "last_seen_comment_id": inbound.comment_id,
                },
                deliver=False,
            )
            await zendesk_channel.post_reply(
                inbound.zendesk_ticket_id, reply, map_ticket_fields(ticket)
            )

    return handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings = get_settings()
    app.state.database_manager = build_database_manager()
    await app.state.database_manager.create_all()

    async with app.state.database_manager.session_factory() as session:
        persisted = await SettingsService(SettingsRepository(session)).get_or_create(
            settings.WORKING_HOURS_START, settings.WORKING_HOURS_END, settings.TIMEZONE
        )
        await session.commit()

    telegram_bot = Bot(settings.TELEGRAM_BOT_TOKEN) if settings.TELEGRAM_BOT_TOKEN else None
    app.state.context = _build_context(telegram_bot, persisted)

    polling_task = None
    dispatcher = None
    if telegram_bot is not None:
        handler = await _telegram_handler_factory(app)
        dispatcher = build_telegram_dispatcher(handler)
        polling_task = asyncio.create_task(
            dispatcher.start_polling(
                telegram_bot, handle_signals=False, close_bot_session=False
            )
        )
        logger.info("Telegram polling started")
    else:
        logger.warning("TELEGRAM_BOT_TOKEN not set; Telegram polling disabled")

    zendesk_channel = cast(ZendeskChannel, app.state.context.channels[Channel.ZENDESK])
    zendesk_task = None
    if zendesk_channel.enabled:
        zendesk_handler = await _zendesk_handler_factory(app, zendesk_channel)
        zendesk_poller = ZendeskPoller(
            zendesk_channel, zendesk_handler, settings.ZENDESK_POLL_INTERVAL_SECONDS
        )
        zendesk_task = asyncio.create_task(zendesk_poller.run())
        logger.info("Zendesk polling started")
    else:
        logger.warning("Zendesk credentials not set; Zendesk polling disabled")

    yield

    if dispatcher is not None:
        dispatcher.stop_polling()
    if polling_task is not None:
        polling_task.cancel()
        with suppress(asyncio.CancelledError):
            await polling_task
    if zendesk_task is not None:
        zendesk_task.cancel()
        with suppress(asyncio.CancelledError):
            await zendesk_task
    if telegram_bot is not None:
        await telegram_bot.session.close()
    await app.state.database_manager.dispose()


def _register_frontend(app: FastAPI) -> None:
    """Serve the built SPA with a catch-all that falls back to index.html.

    A bare StaticFiles mount on "/" does not fall back to index.html for nested
    React Router paths, so reloading a deep link returns 404. This catch-all
    serves real files when they exist and index.html otherwise, while keeping
    unknown API paths as JSON 404s.
    """
    assets_dir = _FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    index_file = _FRONTEND_DIST / "index.html"

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith(("api/", "api", "ws")):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        candidate = _FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index_file)


def create_app() -> FastAPI:
    app = FastAPI(title="ai-helpdesk-agent", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(public_router)
    app.include_router(ws.router)
    app.add_exception_handler(BusinessError, business_exception_handler)
    add_pagination(app)
    if _FRONTEND_DIST.exists():
        _register_frontend(app)
    return app


app = create_app()
