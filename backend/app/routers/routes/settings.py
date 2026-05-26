from fastapi import APIRouter

from app.dependencies import ContextDep
from app.schemas.settings import BotSettings

router = APIRouter()


@router.get("", response_model=BotSettings)
async def get_settings(context: ContextDep) -> BotSettings:
    return BotSettings(
        working_hours_start=context.router_config.working_hours_start,
        working_hours_end=context.router_config.working_hours_end,
        timezone=context.timezone,
        system_prompt=context.system_prompt,
    )


@router.put("", response_model=BotSettings)
async def update_settings(payload: BotSettings, context: ContextDep) -> BotSettings:
    context.router_config.working_hours_start = payload.working_hours_start
    context.router_config.working_hours_end = payload.working_hours_end
    context.timezone = payload.timezone
    context.system_prompt = payload.system_prompt
    return payload
