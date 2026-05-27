from dataclasses import dataclass

from app.agent.pipeline import AgentPipeline
from app.agent.router import RouterConfig
from app.channels.base import BaseChannel
from app.models.enums import Channel
from app.services.escalation_service import EscalationService
from app.utils.websocket_manager import WebSocketManager


@dataclass
class AppContext:
    pipeline: AgentPipeline
    router_config: RouterConfig
    websocket_manager: WebSocketManager
    escalation_service: EscalationService
    channels: dict[Channel, BaseChannel]
    timezone: str
    system_prompt: str
