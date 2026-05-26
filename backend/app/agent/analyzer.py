from pydantic import BaseModel, Field

from app.models.enums import Category, Sentiment


class ExtractedEntities(BaseModel):
    phone: str | None = None
    time: str | None = None
    sender_id: str | None = None
    route: str | None = None
    error_text: str | None = None
    ip: str | None = None
    account: str | None = None


class AnalysisResult(BaseModel):
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)
    sentiment: Sentiment
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
