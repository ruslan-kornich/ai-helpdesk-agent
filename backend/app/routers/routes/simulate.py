from fastapi import APIRouter

from app.dependencies import ConversationServiceDep
from app.schemas.simulate import SimulateRequest, SimulateResponse
from app.schemas.ticket import TicketRead

router = APIRouter()


@router.post("", response_model=SimulateResponse)
async def simulate_message(
    payload: SimulateRequest, conversation_service: ConversationServiceDep
) -> SimulateResponse:
    reply, ticket = await conversation_service.handle_incoming(
        payload.channel, payload.client_id, payload.text, deliver=False
    )
    return SimulateResponse(reply=reply, ticket=TicketRead.model_validate(ticket))
