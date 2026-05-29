from app.models.app_setting import SETTINGS_ROW_ID, AppSetting
from app.repositories.settings_repository import SettingsRepository


class SettingsService:
    def __init__(self, settings_repository: SettingsRepository) -> None:
        self.settings_repository = settings_repository

    async def get_or_create(
        self, working_hours_start: int, working_hours_end: int, timezone: str
    ) -> AppSetting:
        existing = await self.settings_repository.get_settings()
        if existing is not None:
            return existing
        return await self.settings_repository.add(
            AppSetting(
                id=SETTINGS_ROW_ID,
                working_hours_start=working_hours_start,
                working_hours_end=working_hours_end,
                timezone=timezone,
            )
        )

    async def update(
        self, working_hours_start: int, working_hours_end: int, timezone: str
    ) -> AppSetting:
        setting = await self.settings_repository.get_settings()
        if setting is None:
            return await self.get_or_create(working_hours_start, working_hours_end, timezone)
        setting.working_hours_start = working_hours_start
        setting.working_hours_end = working_hours_end
        setting.timezone = timezone
        return await self.settings_repository.add(setting)
