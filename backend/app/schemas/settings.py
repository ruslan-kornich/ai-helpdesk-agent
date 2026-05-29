from pydantic import BaseModel, Field


class BotSettings(BaseModel):
    working_hours_start: int = Field(ge=0, le=23)
    working_hours_end: int = Field(ge=0, le=23)
    timezone: str
