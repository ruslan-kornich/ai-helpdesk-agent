from pydantic import BaseModel, Field, model_validator


class BotSettings(BaseModel):
    working_hours_start: int = Field(ge=0, le=23)
    working_hours_end: int = Field(ge=1, le=24)
    timezone: str

    @model_validator(mode="after")
    def validate_hours_window(self) -> "BotSettings":
        if self.working_hours_end <= self.working_hours_start:
            raise ValueError("working_hours_end must be greater than working_hours_start")
        return self
