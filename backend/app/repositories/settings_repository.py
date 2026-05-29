from app.models.app_setting import SETTINGS_ROW_ID, AppSetting
from app.utils.repository import SQLAlchemyRepository


class SettingsRepository(SQLAlchemyRepository[AppSetting]):
    model = AppSetting

    async def get_settings(self) -> AppSetting | None:
        return await self.session.get(AppSetting, SETTINGS_ROW_ID)
