from enum import StrEnum

from loguru import logger
from pydantic import BaseModel, Field

from app.agent.llm import LLMProvider
from app.agent.prompts import ANALYZER_SYSTEM_PROMPT, ANALYZER_USER_TEMPLATE
from app.models.enums import Category, Sentiment


class LLMCategory(StrEnum):
    HOW_TO = "how_to"
    BILLING = "billing"
    DELIVERY_ISSUE = "delivery_issue"
    COMMERCIAL = "commercial"
    OUTAGE = "outage"
    UNKNOWN = "unknown"
    OTHER = "other"


class ExtractedEntities(BaseModel):
    phone: str | None = None
    time: str | None = None
    sender_id: str | None = None
    route: str | None = None
    error_text: str | None = None
    ip: str | None = None
    account: str | None = None


class LLMAnalysis(BaseModel):
    category: LLMCategory
    confidence: float = Field(ge=0.0, le=1.0)
    sentiment: Sentiment
    summary: str
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)


class AnalysisResult(BaseModel):
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)
    sentiment: Sentiment
    summary: str
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)


class Analyzer:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def analyze(self, text: str, history: str) -> AnalysisResult:
        logger.debug(
            "Analyzer input | text={text!r} history_len={history_len}",
            text=text,
            history_len=len(history),
        )
        user_prompt = ANALYZER_USER_TEMPLATE.format(history=history or "(none)", text=text)
        try:
            llm_result = await self.llm.complete_structured(
                ANALYZER_SYSTEM_PROMPT, user_prompt, LLMAnalysis
            )
            result = AnalysisResult(
                category=Category(llm_result.category.value),
                confidence=llm_result.confidence,
                sentiment=llm_result.sentiment,
                summary=llm_result.summary.strip()[:200],
                entities=llm_result.entities,
            )
            logger.debug(
                "Analyzer result | category={category} confidence={confidence:.2f} "
                "sentiment={sentiment} entities={entities}",
                category=result.category.value,
                confidence=result.confidence,
                sentiment=result.sentiment.value,
                entities=result.entities.model_dump(exclude_none=True),
            )
            return result
        except Exception as error:
            logger.exception("Analyzer LLM call failed: {error}", error=error)
            return AnalysisResult(
                category=Category.UNKNOWN,
                confidence=0.0,
                sentiment=Sentiment.NEUTRAL,
                summary=text[:200],
            )
