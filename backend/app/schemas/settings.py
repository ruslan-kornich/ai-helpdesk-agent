from pydantic import BaseModel


class BotSettings(BaseModel):
    working_hours_start: int
    working_hours_end: int
    timezone: str
    system_prompt: str
