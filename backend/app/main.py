import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path

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
from app.channels.telegram import TelegramChannel, TelegramClient, run_telegram_polling
from app.channels.zendesk import ZendeskChannel
from app.config.db import build_database_manager
from app.config.logger import setup_logging
from app.config.settings import get_settings
from app.context import AppContext
from app.knowledge.retriever import KeywordRetriever
from app.models.enums import Channel
from app.routers.api import public_router
from app.routers.routes import ws
from app.services.escalation_service import EscalationService
from app.utils.exceptions import BusinessError, business_exception_handler
from app.utils.websocket_manager import WebSocketManager

_FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
_DEFAULT_PERSONA = (
    "You are a friendly, concise support agent for the Gatum SMS/SMPP platform. "
    "Keep replies clear, professional, and grounded in the provided knowledge base."
)


def _build_context() -> AppContext:
    settings = get_settings()
    llm = OpenAIProvider(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)
    retriever = KeywordRetriever()
    router_config = RouterConfig(
        confidence_threshold=settings.CONFIDENCE_THRESHOLD,
        working_hours_start=settings.WORKING_HOURS_START,
        working_hours_end=settings.WORKING_HOURS_END,
    )
    pipeline = AgentPipeline(
        analyzer=Analyzer(llm), responder=Responder(llm, retriever), config=router_config
    )
    websocket_manager = WebSocketManager()
    channels = {
        Channel.TELEGRAM: TelegramChannel(TelegramClient(settings.TELEGRAM_BOT_TOKEN)),
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
        timezone=settings.TIMEZONE,
        system_prompt=_DEFAULT_PERSONA,
    )


async def _telegram_handler_factory(app: FastAPI):
    from app.repositories.message_repository import MessageRepository
    from app.repositories.ticket_repository import TicketRepository
    from app.services.conversation_service import ConversationService
    from app.services.ticket_service import TicketService

    async def handler(chat_id: str, text: str, metadata: dict) -> None:
        manager = app.state.database_manager
        async with manager.session_factory() as session:
            service = ConversationService(
                session=session,
                ticket_service=TicketService(TicketRepository(session)),
                message_repository=MessageRepository(session),
                context=app.state.context,
            )
            await service.handle_incoming(Channel.TELEGRAM, chat_id, text, metadata)

    return handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings = get_settings()
    app.state.database_manager = build_database_manager()
    await app.state.database_manager.create_all()
    app.state.context = _build_context()

    polling_task = None
    stop_event = asyncio.Event()
    if settings.TELEGRAM_BOT_TOKEN:
        handler = await _telegram_handler_factory(app)
        client = TelegramClient(settings.TELEGRAM_BOT_TOKEN)
        polling_task = asyncio.create_task(run_telegram_polling(client, handler, stop_event))
    else:
        logger.warning("TELEGRAM_BOT_TOKEN not set; Telegram polling disabled")

    yield

    stop_event.set()
    if polling_task is not None:
        polling_task.cancel()
        with suppress(asyncio.CancelledError):
            await polling_task
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
