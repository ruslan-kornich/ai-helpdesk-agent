from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import Channel, MessageRole


class MessageCreate(BaseModel):
    role: MessageRole
    text: str
    channel: Channel


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: str
    role: MessageRole
    text: str
    channel: Channel
    created_at: datetime
