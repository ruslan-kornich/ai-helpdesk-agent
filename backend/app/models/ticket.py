import uuid
from typing import Any

from sqlalchemy import JSON, Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.config.db import Base
from app.models.enums import Category, Channel, EscalationTarget, Priority, Sentiment
from app.utils.model import TimestampMixin


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Ticket(Base, TimestampMixin):
    __tablename__ = "tickets"

    ticket_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    channel: Mapped[Channel] = mapped_column(Enum(Channel, native_enum=False))
    client_id: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[Category] = mapped_column(Enum(Category, native_enum=False))
    priority: Mapped[Priority] = mapped_column(Enum(Priority, native_enum=False))
    summary: Mapped[str] = mapped_column(String(200), default="")
    conversation_snippet: Mapped[str] = mapped_column(Text, default="")
    escalation_target: Mapped[EscalationTarget | None] = mapped_column(
        Enum(EscalationTarget, native_enum=False), nullable=True
    )
    resolved_by_ai: Mapped[bool] = mapped_column(Boolean, default=False)
    sentiment: Mapped[Sentiment] = mapped_column(Enum(Sentiment, native_enum=False))
    ticket_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
