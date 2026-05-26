from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    Category,
    Channel,
    EscalationTarget,
    Priority,
    Sentiment,
)


class TicketCreate(BaseModel):
    channel: Channel
    client_id: str


class TicketUpdate(BaseModel):
    category: Category | None = None
    priority: Priority | None = None
    summary: str | None = None
    conversation_snippet: str | None = None
    escalation_target: EscalationTarget | None = None
    resolved_by_ai: bool | None = None
    sentiment: Sentiment | None = None
    ticket_metadata: dict[str, Any] | None = None


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: str
    created_at: datetime
    channel: Channel
    client_id: str
    category: Category
    priority: Priority
    summary: str
    conversation_snippet: str
    escalation_target: EscalationTarget | None
    resolved_by_ai: bool
    sentiment: Sentiment
    ticket_metadata: dict[str, Any] = Field(default_factory=dict)


class TicketFilter(BaseModel):
    channel: Channel | None = None
    category: Category | None = None
    priority: Priority | None = None
    sentiment: Sentiment | None = None
    escalation_target: EscalationTarget | None = None
    resolved_by_ai: bool | None = None
