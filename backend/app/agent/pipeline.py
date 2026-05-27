from dataclasses import dataclass
from datetime import datetime
from typing import Any

from loguru import logger

from app.agent.analyzer import Analyzer
from app.agent.responder import Responder
from app.agent.router import RouterConfig, decide
from app.models.enums import Category, EscalationTarget, Priority, Sentiment


@dataclass
class AgentResult:
    category: Category
    priority: Priority
    sentiment: Sentiment
    escalation_target: EscalationTarget | None
    resolved_by_ai: bool
    was_after_hours: bool
    entities: dict[str, Any]
    reply: str


class AgentPipeline:
    def __init__(self, analyzer: Analyzer, responder: Responder, config: RouterConfig) -> None:
        self.analyzer = analyzer
        self.responder = responder
        self.config = config

    async def run(
        self,
        text: str,
        history: str,
        now: datetime,
        persona: str = "",
        ticket_reference: str = "",
    ) -> AgentResult:
        analysis = await self.analyzer.analyze(text, history)
        decision = decide(analysis, now, self.config)
        logger.debug(
            "Router decision | category={category} priority={priority} action={action} "
            "escalation_target={target} resolved_by_ai={resolved} was_after_hours={after_hours}",
            category=decision.category.value,
            priority=decision.priority.value,
            action=decision.action.value,
            target=decision.escalation_target.value if decision.escalation_target else None,
            resolved=decision.resolved_by_ai,
            after_hours=decision.was_after_hours,
        )
        reply = await self.responder.build(decision, text, persona, ticket_reference)
        logger.debug("Agent reply | {reply!r}", reply=reply)
        return AgentResult(
            category=decision.category,
            priority=decision.priority,
            sentiment=analysis.sentiment,
            escalation_target=decision.escalation_target,
            resolved_by_ai=decision.resolved_by_ai,
            was_after_hours=decision.was_after_hours,
            entities=analysis.entities.model_dump(exclude_none=True),
            reply=reply,
        )
