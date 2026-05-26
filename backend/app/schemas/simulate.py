from pydantic import BaseModel

from app.models.enums import Channel
from app.schemas.ticket import TicketRead


class SimulateRequest(BaseModel):
    channel: Channel
    client_id: str
    text: str


class SimulateResponse(BaseModel):
    reply: str
    ticket: TicketRead
