from collections.abc import Sequence

from sqlalchemy import select

from app.models.message import Message
from app.utils.repository import SQLAlchemyRepository


class MessageRepository(SQLAlchemyRepository[Message]):
    model = Message

    async def list_for_ticket(self, ticket_id: str) -> Sequence[Message]:
        statement = select(Message).where(Message.ticket_id == ticket_id).order_by(Message.id.asc())
        result = await self.session.execute(statement)
        return result.scalars().all()
