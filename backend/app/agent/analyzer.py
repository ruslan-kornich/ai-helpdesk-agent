from loguru import logger
from pydantic import BaseModel, Field

from app.agent.llm import LLMProvider
from app.agent.prompts import ANALYZER_SYSTEM_PROMPT, ANALYZER_USER_TEMPLATE
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


class Analyzer:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def analyze(self, text: str, history: str) -> AnalysisResult:
        user_prompt = ANALYZER_USER_TEMPLATE.format(history=history or "(none)", text=text)
        try:
            return await self.llm.complete_structured(
                ANALYZER_SYSTEM_PROMPT, user_prompt, AnalysisResult
            )
        except Exception as error:
            logger.exception("Analyzer LLM call failed: {error}", error=error)
            return AnalysisResult(
                category=Category.UNKNOWN, confidence=0.0, sentiment=Sentiment.NEUTRAL
            )
