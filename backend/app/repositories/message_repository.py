from collections.abc import Sequence

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from app.models.message import Message
from app.schemas.message import MessageRead
from app.utils.repository import SQLAlchemyRepository


class MessageRepository(SQLAlchemyRepository[Message]):
    model = Message

    async def list_for_ticket(self, ticket_id: str) -> Sequence[Message]:
        statement = select(Message).where(Message.ticket_id == ticket_id).order_by(Message.id.asc())
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def paginate_for_ticket(self, ticket_id: str) -> Page[MessageRead]:
        statement = select(Message).where(Message.ticket_id == ticket_id).order_by(Message.id.asc())
        return await paginate(
            self.session,
            statement,
            transformer=lambda rows: [MessageRead.model_validate(row) for row in rows],
        )
