import pytest

from app.agent.responder import Responder
from app.agent.router import AgentAction, RouterDecision
from app.models.enums import Category, Priority


class _CapturingLLM:
    """Records the system prompt of the last text completion and echoes a canned reply."""

    def __init__(self) -> None:
        self.last_system_prompt = ""

    async def complete_structured(self, system_prompt, user_prompt, schema):
        raise NotImplementedError

    async def complete_text(self, system_prompt: str, user_prompt: str) -> str:
        self.last_system_prompt = system_prompt
        return "ok"


class _StubRetriever:
    def __init__(self, documents: list[str]) -> None:
        self._documents = documents

    def search(self, query: str, top_k: int = 3) -> list[str]:
        return self._documents

    def all_documents(self) -> list[str]:
        return self._documents


def _decision(category: Category, action: AgentAction) -> RouterDecision:
    return RouterDecision(
        category=category,
        priority=Priority.NORMAL,
        escalation_target=None,
        resolved_by_ai=True,
        action=action,
        was_after_hours=False,
    )


@pytest.mark.asyncio
async def test_acknowledge_includes_working_hours_in_system_prompt():
    llm = _CapturingLLM()
    responder = Responder(llm, _StubRetriever([]))

    await responder.build(
        _decision(Category.COMMERCIAL, AgentAction.ACKNOWLEDGE),
        text="When do you work?",
        working_hours_start=9,
        working_hours_end=18,
        timezone="Europe/Kyiv",
    )

    assert "09:00-18:00 Europe/Kyiv" in llm.last_system_prompt


@pytest.mark.asyncio
async def test_how_to_includes_working_hours_in_system_prompt():
    llm = _CapturingLLM()
    responder = Responder(llm, _StubRetriever(["Some FAQ content."]))

    await responder.build(
        _decision(Category.HOW_TO, AgentAction.ANSWER),
        text="How do I send a campaign?",
        working_hours_start=9,
        working_hours_end=18,
        timezone="Europe/Kyiv",
    )

    assert "09:00-18:00 Europe/Kyiv" in llm.last_system_prompt


@pytest.mark.asyncio
async def test_after_hours_states_working_hours_once():
    llm = _CapturingLLM()
    responder = Responder(llm, _StubRetriever([]))

    await responder.build(
        _decision(Category.AFTER_HOURS, AgentAction.HOLD),
        text="Anyone there?",
        working_hours_start=9,
        working_hours_end=18,
        timezone="Europe/Kyiv",
        ticket_reference="GAT-123",
    )

    # After-hours already states the hours in its own instruction; the generic
    # working-hours context must not be added on top, so the string appears once.
    assert llm.last_system_prompt.count("09:00-18:00 Europe/Kyiv") == 1
