from loguru import logger

from app.agent.pipeline import AgentResult
from app.models.enums import EscalationTarget
from app.models.ticket import Ticket
from app.utils.websocket_manager import WebSocketManager


class EscalationService:
    def __init__(self, websocket_manager: WebSocketManager, support_lead_channel: str) -> None:
        self.websocket_manager = websocket_manager
        self.support_lead_channel = support_lead_channel

    async def notify(self, ticket: Ticket, result: AgentResult) -> None:
        logger.info(
            "Escalation: ticket={ticket} target={target} priority={priority}",
            ticket=ticket.ticket_id,
            target=result.escalation_target,
            priority=result.priority,
        )
        if result.escalation_target == EscalationTarget.SUPPORT_LEAD:
            logger.warning(
                "Support lead alert -> {channel} for ticket {ticket}",
                channel=self.support_lead_channel or "(unset)",
                ticket=ticket.ticket_id,
            )
        await self.websocket_manager.broadcast(
            {
                "type": "escalation",
                "ticket_id": ticket.ticket_id,
                "target": result.escalation_target.value if result.escalation_target else None,
                "priority": result.priority.value,
            }
        )
