from loguru import logger

from app.agent.llm import LLMProvider
from app.agent.prompts import RESPONDER_HOWTO_SYSTEM_PROMPT, RESPONDER_HOWTO_USER_TEMPLATE
from app.agent.router import AgentAction, RouterDecision
from app.knowledge.retriever import Retriever
from app.models.enums import Category

_FALLBACK_HOWTO_REPLY = (
    "Thanks for reaching out. I am passing your question to a specialist who will follow up shortly."
)

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
    def __init__(self, llm: LLMProvider, retriever: Retriever) -> None:
        self.llm = llm
        self.retriever = retriever

    async def build(self, decision: RouterDecision, text: str, persona: str = "") -> str:
        if decision.action == AgentAction.ANSWER and decision.category == Category.HOW_TO:
            return await self._answer_how_to(text, persona)
        return _CANNED_REPLIES.get(decision.category, _CANNED_REPLIES[Category.UNKNOWN])

    async def _answer_how_to(self, text: str, persona: str = "") -> str:
        chunks = self.retriever.search(text, top_k=3)
        if not chunks:
            return _FALLBACK_HOWTO_REPLY
        context = "\n\n---\n\n".join(chunks)
        system_prompt = (
            f"{persona}\n\n{RESPONDER_HOWTO_SYSTEM_PROMPT}" if persona else RESPONDER_HOWTO_SYSTEM_PROMPT
        )
        user_prompt = RESPONDER_HOWTO_USER_TEMPLATE.format(context=context, text=text)
        try:
            return await self.llm.complete_text(system_prompt, user_prompt)
        except Exception as error:
            logger.exception("Responder LLM call failed: {error}", error=error)
            return _FALLBACK_HOWTO_REPLY
