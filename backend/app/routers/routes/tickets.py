from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import Page

from app.dependencies import MessageRepositoryDep, TicketRepositoryDep
from app.schemas.message import MessageRead
from app.schemas.ticket import TicketFilter, TicketRead
from app.utils.exceptions import BusinessError

router = APIRouter()


@router.get("", response_model=Page[TicketRead])
async def list_tickets(
    repository: TicketRepositoryDep,
    filters: Annotated[TicketFilter, Depends()],
) -> Page[TicketRead]:
    return await repository.paginate_filtered(filters.model_dump(exclude_none=True))


@router.get("/{ticket_id}", response_model=TicketRead)
async def get_ticket(ticket_id: str, repository: TicketRepositoryDep) -> TicketRead:
    ticket = await repository.get(ticket_id)
    if ticket is None:
        raise BusinessError("Ticket not found", status_code=404)
    return TicketRead.model_validate(ticket)


@router.get("/{ticket_id}/messages", response_model=Page[MessageRead])
async def list_ticket_messages(
    ticket_id: str, repository: MessageRepositoryDep
) -> Page[MessageRead]:
    return await repository.paginate_for_ticket(ticket_id)
