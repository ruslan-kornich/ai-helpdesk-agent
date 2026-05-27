import asyncio

from loguru import logger

from app.config.db import build_database_manager
from app.config.logger import setup_logging
from app.models.enums import (
    Category,
    Channel,
    EscalationTarget,
    MessageRole,
    Priority,
    Sentiment,
)
from app.models.message import Message
from app.models.ticket import Ticket
from app.repositories.message_repository import MessageRepository
from app.repositories.ticket_repository import TicketRepository

_DEMO_TICKETS = [
    {
        "channel": Channel.TELEGRAM,
        "client_id": "demo-howto",
        "category": Category.HOW_TO,
        "priority": Priority.NORMAL,
        "summary": "How do I send a bulk campaign?",
        "escalation_target": None,
        "resolved_by_ai": True,
        "sentiment": Sentiment.POSITIVE,
        "was_after_hours": False,
        "client_text": "How do I send a bulk SMS campaign?",
        "agent_text": "Open Campaigns, click New campaign, upload your CSV and send.",
    },
    {
        "channel": Channel.WHATSAPP,
        "client_id": "demo-billing",
        "category": Category.BILLING,
        "priority": Priority.NORMAL,
        "summary": "How do I top up my balance?",
        "escalation_target": EscalationTarget.FINANCE,
        "resolved_by_ai": False,
        "sentiment": Sentiment.NEUTRAL,
        "was_after_hours": False,
        "client_text": "How can I top up my balance and what is the wallet address?",
        "agent_text": "Open Billing, choose Top up balance, then send the transaction confirmation.",
    },
    {
        "channel": Channel.ZENDESK,
        "client_id": "demo-outage",
        "category": Category.OUTAGE,
        "priority": Priority.URGENT,
        "summary": "SMPP connection dropped",
        "escalation_target": EscalationTarget.L2_SUPPORT,
        "resolved_by_ai": False,
        "sentiment": Sentiment.NEGATIVE,
        "was_after_hours": True,
        "client_text": "Our SMPP connection keeps dropping with a bind error.",
        "agent_text": "Please confirm the error text, time, and affected IP. Escalated as urgent.",
    },
]


async def _seed() -> None:
    manager = build_database_manager()
    await manager.create_all()
    async with manager.session_factory() as session:
        ticket_repository = TicketRepository(session)
        message_repository = MessageRepository(session)
        for entry in _DEMO_TICKETS:
            ticket = Ticket(
                channel=entry["channel"],
                client_id=entry["client_id"],
                category=entry["category"],
                priority=entry["priority"],
                summary=entry["summary"],
                conversation_snippet=f"client: {entry['client_text']}\nagent: {entry['agent_text']}",
                escalation_target=entry["escalation_target"],
                resolved_by_ai=entry["resolved_by_ai"],
                sentiment=entry["sentiment"],
                ticket_metadata={"was_after_hours": entry["was_after_hours"]},
            )
            await ticket_repository.add(ticket)
            await message_repository.add(
                Message(
                    ticket_id=ticket.ticket_id,
                    role=MessageRole.CLIENT,
                    text=entry["client_text"],
                    channel=entry["channel"],
                )
            )
            await message_repository.add(
                Message(
                    ticket_id=ticket.ticket_id,
                    role=MessageRole.AGENT,
                    text=entry["agent_text"],
                    channel=entry["channel"],
                )
            )
        await session.commit()
    await manager.dispose()
    logger.info("Seeded {count} demo tickets", count=len(_DEMO_TICKETS))


if __name__ == "__main__":
    setup_logging()
    asyncio.run(_seed())
