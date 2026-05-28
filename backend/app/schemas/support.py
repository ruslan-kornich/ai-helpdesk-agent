from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import MessageRole


class SupportChatRequest(BaseModel):
    name: str
    email: str
    text: str
    zendesk_ticket_id: str | None = None


class SupportChatResponse(BaseModel):
    zendesk_ticket_id: str


class SupportMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: MessageRole
    text: str
    created_at: datetime


class SupportMessagesResponse(BaseModel):
    messages: list[SupportMessageRead]
