from loguru import logger

from app.agent.llm import LLMProvider
from app.agent.prompts import (
    LANGUAGE_INSTRUCTION,
    RESPONDER_AFTER_HOURS_INSTRUCTION,
    RESPONDER_BASE_SYSTEM_PROMPT,
    RESPONDER_CATEGORY_INSTRUCTIONS,
    RESPONDER_HOWTO_SYSTEM_PROMPT,
    RESPONDER_HOWTO_USER_TEMPLATE,
)
from app.agent.router import AgentAction, RouterDecision
from app.knowledge.retriever import Retriever
from app.models.enums import Category

_FALLBACK_HOWTO_REPLY = "Thanks for reaching out. I am passing your question to a specialist who will follow up shortly."

_CANNED_REPLIES: dict[Category, str] = {
    Category.BILLING: (
        "To top up your balance, open the Billing section and choose Top up balance. "
        "Once you have sent the payment, please reply here with the transaction confirmation "
        "and our finance team will verify it."
    ),
    Category.DELIVERY_ISSUE: (
        "Thanks for the report. To investigate the undelivered messages, could you confirm the "
        "affected phone number(s), the time they were sent, and the Sender ID used? "
        "I have logged this and our L2 support team will look into it."
    ),
    Category.COMMERCIAL: (
        "Thanks for your interest. A sales manager will contact you shortly to discuss commercial "
        "terms tailored to your volume."
    ),
    Category.OUTAGE: (
        "Thanks for flagging this. To escalate immediately, please confirm the exact error text, "
        "the time it started, and the affected account or IP. I have raised this as urgent with our "
        "L2 support team."
    ),
    Category.AFTER_HOURS: (
        "Thanks for your message. Our team is currently outside working hours. We have created a "
        "ticket and will respond as soon as the team is back."
    ),
    Category.UNKNOWN: (
        "Thanks for reaching out. I am passing your request to a specialist who will follow up shortly."
    ),
    Category.OTHER: (
        "Thank you for your feedback. I am sorry to hear about your experience. I have flagged this "
        "to our support lead, who will personally look into it."
    ),
}


class Responder:
    def __init__(
        self,
        llm: LLMProvider,
        retriever: Retriever,
        working_hours_start: int = 9,
        working_hours_end: int = 18,
        timezone: str = "Europe/Kyiv",
    ) -> None:
        self.llm = llm
        self.retriever = retriever
        self.working_hours_start = working_hours_start
        self.working_hours_end = working_hours_end
        self.timezone = timezone

    async def build(
        self, decision: RouterDecision, text: str, persona: str = "", ticket_reference: str = ""
    ) -> str:
        if decision.action == AgentAction.ANSWER and decision.category == Category.HOW_TO:
            return await self._answer_how_to(text, persona)
        return await self._acknowledge(decision.category, text, persona, ticket_reference)

    def _working_hours_label(self) -> str:
        return (
            f"{self.working_hours_start:02d}:00-{self.working_hours_end:02d}:00 {self.timezone}"
        )

    async def _acknowledge(
        self, category: Category, text: str, persona: str, ticket_reference: str
    ) -> str:
        fallback = _CANNED_REPLIES.get(category, _CANNED_REPLIES[Category.UNKNOWN])
        if category == Category.AFTER_HOURS:
            instruction = RESPONDER_AFTER_HOURS_INSTRUCTION.format(
                working_hours=self._working_hours_label(),
                ticket_reference=ticket_reference or "your support ticket",
            )
        else:
            instruction = RESPONDER_CATEGORY_INSTRUCTIONS.get(category.value)
        if instruction is None:
            return fallback
        base = f"{persona}\n\n{RESPONDER_BASE_SYSTEM_PROMPT}" if persona else RESPONDER_BASE_SYSTEM_PROMPT
        system_prompt = f"{base}\n\n{instruction}\n\n{LANGUAGE_INSTRUCTION}"
        try:
            reply = await self.llm.complete_text(system_prompt, text)
            return reply or fallback
        except Exception as error:
            logger.exception("Responder acknowledge LLM call failed: {error}", error=error)
            return fallback

    async def _answer_how_to(self, text: str, persona: str = "") -> str:
        chunks = self.retriever.search(text, top_k=3)
        logger.debug(
            "Responder how_to | query={query!r} faq_chunks_found={count}",
            query=text,
            count=len(chunks),
        )
        if not chunks:
            # Keyword search misses on non-English queries (FAQ is English-only).
            # Hand the full FAQ to the multilingual LLM, which answers in the client's
            # language or declines per the system prompt if the topic is not covered.
            chunks = self.retriever.all_documents()
            logger.debug(
                "Responder how_to | keyword miss, falling back to full FAQ ({count} docs)",
                count=len(chunks),
            )
        if not chunks:
            logger.debug("Responder how_to | knowledge base empty, using fallback reply")
            return _FALLBACK_HOWTO_REPLY
        context = "\n\n---\n\n".join(chunks)
        base = (
            f"{persona}\n\n{RESPONDER_HOWTO_SYSTEM_PROMPT}"
            if persona
            else RESPONDER_HOWTO_SYSTEM_PROMPT
        )
        system_prompt = f"{base}\n\n{LANGUAGE_INSTRUCTION}"
        user_prompt = RESPONDER_HOWTO_USER_TEMPLATE.format(context=context, text=text)
        try:
            return await self.llm.complete_text(system_prompt, user_prompt)
        except Exception as error:
            logger.exception("Responder LLM call failed: {error}", error=error)
            return _FALLBACK_HOWTO_REPLY
