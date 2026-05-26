from datetime import datetime

from app.agent.analyzer import AnalysisResult
from app.agent.router import AgentAction, RouterConfig, decide, is_after_hours
from app.models.enums import Category, EscalationTarget, Priority, Sentiment

BUSINESS_HOURS = datetime(2026, 5, 27, 10, 0)
NIGHT = datetime(2026, 5, 27, 2, 0)
WEEKEND = datetime(2026, 5, 30, 10, 0)
CONFIG = RouterConfig(confidence_threshold=0.55, working_hours_start=9, working_hours_end=18)


def _analysis(category: Category, confidence: float = 0.9, sentiment: Sentiment = Sentiment.NEUTRAL) -> AnalysisResult:
    return AnalysisResult(category=category, confidence=confidence, sentiment=sentiment)


def test_is_after_hours_weekday():
    assert is_after_hours(BUSINESS_HOURS, 9, 18) is False
    assert is_after_hours(NIGHT, 9, 18) is True


def test_is_after_hours_weekend():
    assert is_after_hours(WEEKEND, 9, 18) is True


def test_c1_how_to_resolved_by_ai():
    decision = decide(_analysis(Category.HOW_TO), BUSINESS_HOURS, CONFIG)
    assert decision.category == Category.HOW_TO
    assert decision.priority == Priority.NORMAL
    assert decision.escalation_target is None
    assert decision.resolved_by_ai is True
    assert decision.action == AgentAction.ANSWER


def test_c2_billing_to_finance():
    decision = decide(_analysis(Category.BILLING), BUSINESS_HOURS, CONFIG)
    assert decision.category == Category.BILLING
    assert decision.priority == Priority.NORMAL
    assert decision.escalation_target == EscalationTarget.FINANCE
    assert decision.resolved_by_ai is False


def test_c3_delivery_issue_high_to_l2():
    decision = decide(_analysis(Category.DELIVERY_ISSUE), BUSINESS_HOURS, CONFIG)
    assert decision.priority == Priority.HIGH
    assert decision.escalation_target == EscalationTarget.L2_SUPPORT
    assert decision.resolved_by_ai is False


def test_c4_after_hours_overrides_category():
    decision = decide(_analysis(Category.BILLING), NIGHT, CONFIG)
    assert decision.category == Category.AFTER_HOURS
    assert decision.priority == Priority.NORMAL
    assert decision.escalation_target is None
    assert decision.resolved_by_ai is False
    assert decision.action == AgentAction.HOLD
    assert decision.was_after_hours is True


def test_c5_commercial_to_sales():
    decision = decide(_analysis(Category.COMMERCIAL), BUSINESS_HOURS, CONFIG)
    assert decision.escalation_target == EscalationTarget.SALES
    assert decision.priority == Priority.NORMAL
    assert decision.resolved_by_ai is False


def test_c6_outage_urgent_escalates_even_at_night():
    decision = decide(_analysis(Category.OUTAGE), NIGHT, CONFIG)
    assert decision.category == Category.OUTAGE
    assert decision.priority == Priority.URGENT
    assert decision.escalation_target == EscalationTarget.L2_SUPPORT
    assert decision.resolved_by_ai is False
    assert decision.was_after_hours is True


def test_c7_unknown_to_general_support():
    decision = decide(_analysis(Category.UNKNOWN), BUSINESS_HOURS, CONFIG)
    assert decision.escalation_target == EscalationTarget.GENERAL_SUPPORT
    assert decision.resolved_by_ai is False


def test_c8_other_high_to_support_lead():
    decision = decide(
        _analysis(Category.OTHER, sentiment=Sentiment.NEGATIVE), BUSINESS_HOURS, CONFIG
    )
    assert decision.category == Category.OTHER
    assert decision.priority == Priority.HIGH
    assert decision.escalation_target == EscalationTarget.SUPPORT_LEAD
    assert decision.resolved_by_ai is False


def test_low_confidence_becomes_unknown():
    decision = decide(_analysis(Category.BILLING, confidence=0.2), BUSINESS_HOURS, CONFIG)
    assert decision.category == Category.UNKNOWN
    assert decision.escalation_target == EscalationTarget.GENERAL_SUPPORT


def test_resolved_by_ai_invariant_holds_for_all_categories():
    for category in Category:
        decision = decide(_analysis(category), BUSINESS_HOURS, CONFIG)
        expected = decision.escalation_target is None and decision.category != Category.AFTER_HOURS
        assert decision.resolved_by_ai is expected
