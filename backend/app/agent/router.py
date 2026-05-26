from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.agent.analyzer import AnalysisResult
from app.models.enums import Category, EscalationTarget, Priority


class AgentAction(StrEnum):
    ANSWER = "answer"
    ACKNOWLEDGE = "acknowledge"
    HOLD = "hold"


@dataclass
class RouterConfig:
    confidence_threshold: float = 0.55
    working_hours_start: int = 9
    working_hours_end: int = 18


@dataclass
class RouterDecision:
    category: Category
    priority: Priority
    escalation_target: EscalationTarget | None
    resolved_by_ai: bool
    action: AgentAction
    was_after_hours: bool


_CATEGORY_RULES: dict[Category, tuple[Priority, EscalationTarget | None, AgentAction]] = {
    Category.HOW_TO: (Priority.NORMAL, None, AgentAction.ANSWER),
    Category.BILLING: (Priority.NORMAL, EscalationTarget.FINANCE, AgentAction.ACKNOWLEDGE),
    Category.DELIVERY_ISSUE: (Priority.HIGH, EscalationTarget.L2_SUPPORT, AgentAction.ACKNOWLEDGE),
    Category.COMMERCIAL: (Priority.NORMAL, EscalationTarget.SALES, AgentAction.ACKNOWLEDGE),
    Category.OUTAGE: (Priority.URGENT, EscalationTarget.L2_SUPPORT, AgentAction.ACKNOWLEDGE),
    Category.UNKNOWN: (Priority.NORMAL, EscalationTarget.GENERAL_SUPPORT, AgentAction.ACKNOWLEDGE),
    Category.OTHER: (Priority.HIGH, EscalationTarget.SUPPORT_LEAD, AgentAction.ACKNOWLEDGE),
}


def is_after_hours(now: datetime, working_hours_start: int, working_hours_end: int) -> bool:
    if now.weekday() >= 5:
        return True
    return not (working_hours_start <= now.hour < working_hours_end)


def decide(analysis: AnalysisResult, now: datetime, config: RouterConfig) -> RouterDecision:
    category = analysis.category
    if analysis.confidence < config.confidence_threshold:
        category = Category.UNKNOWN

    after_hours = is_after_hours(now, config.working_hours_start, config.working_hours_end)
    if after_hours and category != Category.OUTAGE:
        category = Category.AFTER_HOURS

    if category == Category.AFTER_HOURS:
        priority, escalation_target, action = Priority.NORMAL, None, AgentAction.HOLD
    else:
        priority, escalation_target, action = _CATEGORY_RULES[category]

    resolved_by_ai = escalation_target is None and category != Category.AFTER_HOURS

    return RouterDecision(
        category=category,
        priority=priority,
        escalation_target=escalation_target,
        resolved_by_ai=resolved_by_ai,
        action=action,
        was_after_hours=after_hours,
    )
