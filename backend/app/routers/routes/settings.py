from fastapi import APIRouter

from app.dependencies import ContextDep, SessionDep
from app.repositories.settings_repository import SettingsRepository
from app.schemas.settings import BotSettings
from app.services.settings_service import SettingsService

router = APIRouter()


@router.get("", response_model=BotSettings)
async def get_settings(context: ContextDep) -> BotSettings:
    return BotSettings(
        working_hours_start=context.router_config.working_hours_start,
        working_hours_end=context.router_config.working_hours_end,
        timezone=context.timezone,
    )


@router.put("", response_model=BotSettings)
async def update_settings(
    payload: BotSettings, context: ContextDep, session: SessionDep
) -> BotSettings:
    service = SettingsService(SettingsRepository(session))
    await service.update(
        payload.working_hours_start, payload.working_hours_end, payload.timezone
    )
    await session.commit()

    # router_config is shared with the pipeline, so writing here makes the change
    # take effect on the next message without restarting the app.
    context.router_config.working_hours_start = payload.working_hours_start
    context.router_config.working_hours_end = payload.working_hours_end
    context.timezone = payload.timezone
    return payload
