from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from app.models.enums import Channel
from app.models.ticket import Ticket
from app.schemas.ticket import TicketRead
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

    async def get_by_zendesk_ticket_id(self, zendesk_ticket_id: str) -> Ticket | None:
        statement = (
            select(Ticket)
            .where(Ticket.channel == Channel.ZENDESK)
            .where(Ticket.ticket_metadata["zendesk_ticket_id"].as_string() == str(zendesk_ticket_id))
            .order_by(Ticket.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def paginate_filtered(self, filters: dict[str, Any]) -> Page[TicketRead]:
        statement = self._apply_filters(select(Ticket), filters).order_by(Ticket.created_at.desc())
        return await paginate(
            self.session,
            statement,
            transformer=lambda rows: [TicketRead.model_validate(row) for row in rows],
        )

    async def list_all(self) -> Sequence[Ticket]:
        result = await self.session.execute(select(Ticket))
        return result.scalars().all()
