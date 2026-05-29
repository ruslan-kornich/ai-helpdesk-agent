from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decode_token, security
from app.context import AppContext
from app.models.user import User
from app.repositories.message_repository import MessageRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.services.analytics_service import AnalyticsService
from app.services.conversation_service import ConversationService
from app.services.ticket_service import TicketService
from app.utils.exceptions import BusinessError


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    manager = request.app.state.database_manager
    async with manager.session_factory() as session:
        yield session


def get_context(request: Request) -> AppContext:
    return request.app.state.context


SessionDep = Annotated[AsyncSession, Depends(get_session)]
ContextDep = Annotated[AppContext, Depends(get_context)]


async def get_current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(security)],
) -> User:
    if credentials is None:
        raise BusinessError("Not authenticated", status_code=401)
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as error:
        raise BusinessError("Invalid or expired token", status_code=401) from error
    if payload.get("type") != "access":
        raise BusinessError("Invalid token type", status_code=401)
    user_id = payload.get("sub")
    user = await UserRepository(session).get_by_id(int(user_id)) if user_id else None
    if user is None or not user.is_active:
        raise BusinessError("User not found or inactive", status_code=401)
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


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
