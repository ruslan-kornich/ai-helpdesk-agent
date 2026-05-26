from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.models.enums import Channel
from app.models.ticket import Ticket
from app.utils.repository import SQLAlchemyRepository


class TicketRepository(SQLAlchemyRepository[Ticket]):
    model = Ticket

    async def get_active(
        self, client_id: str, channel: Channel, window_minutes: int
    ) -> Ticket | None:
        threshold = datetime.now(UTC) - timedelta(minutes=window_minutes)
        statement = (
            select(Ticket)
            .where(Ticket.client_id == client_id)
            .where(Ticket.channel == channel)
            .where(Ticket.updated_at >= threshold)
            .order_by(Ticket.updated_at.desc())
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
