from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.context import AppContext
from app.repositories.message_repository import MessageRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.analytics_service import AnalyticsService
from app.services.conversation_service import ConversationService
from app.services.ticket_service import TicketService


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    manager = request.app.state.database_manager
    async with manager.session_factory() as session:
        yield session


def get_context(request: Request) -> AppContext:
    return request.app.state.context


SessionDep = Annotated[AsyncSession, Depends(get_session)]
ContextDep = Annotated[AppContext, Depends(get_context)]


def get_ticket_repository(session: SessionDep) -> TicketRepository:
    return TicketRepository(session)


def get_message_repository(session: SessionDep) -> MessageRepository:
    return MessageRepository(session)


TicketRepositoryDep = Annotated[TicketRepository, Depends(get_ticket_repository)]
MessageRepositoryDep = Annotated[MessageRepository, Depends(get_message_repository)]


def get_conversation_service(
    session: SessionDep,
    ticket_repository: TicketRepositoryDep,
    message_repository: MessageRepositoryDep,
    context: ContextDep,
) -> ConversationService:
    return ConversationService(
        session=session,
        ticket_service=TicketService(ticket_repository),
        message_repository=message_repository,
        context=context,
    )


ConversationServiceDep = Annotated[ConversationService, Depends(get_conversation_service)]


def get_analytics_service(ticket_repository: TicketRepositoryDep) -> AnalyticsService:
    return AnalyticsService(ticket_repository)


AnalyticsServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]
