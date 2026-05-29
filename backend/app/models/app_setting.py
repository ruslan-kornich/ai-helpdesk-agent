from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.config.db import Base
from app.utils.model import TimestampMixin

# Settings live in a single row so the bot has one authoritative, restart-surviving
# source for working hours and timezone. The fixed primary key makes the row easy to
# fetch and update without tracking ids.
SETTINGS_ROW_ID = 1


class AppSetting(Base, TimestampMixin):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=SETTINGS_ROW_ID)
    working_hours_start: Mapped[int] = mapped_column(Integer)
    working_hours_end: Mapped[int] = mapped_column(Integer)
    timezone: Mapped[str] = mapped_column(String(64))
