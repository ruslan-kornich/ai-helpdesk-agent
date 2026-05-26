from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.config.db import Base
from app.models.enums import Channel, MessageRole
from app.utils.model import TimestampMixin


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tickets.ticket_id"), index=True
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole, native_enum=False))
    text: Mapped[str] = mapped_column(Text)
    channel: Mapped[Channel] = mapped_column(Enum(Channel, native_enum=False))
