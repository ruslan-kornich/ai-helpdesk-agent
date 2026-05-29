import pytest

from app.models.app_setting import SETTINGS_ROW_ID
from app.repositories.settings_repository import SettingsRepository
from app.services.settings_service import SettingsService


@pytest.mark.asyncio
async def test_get_or_create_seeds_defaults(session):
    service = SettingsService(SettingsRepository(session))
    setting = await service.get_or_create(9, 18, "Europe/Kyiv")
    assert setting.id == SETTINGS_ROW_ID
    assert setting.working_hours_start == 9
    assert setting.working_hours_end == 18
    assert setting.timezone == "Europe/Kyiv"


@pytest.mark.asyncio
async def test_get_or_create_is_idempotent(session):
    service = SettingsService(SettingsRepository(session))
    first = await service.get_or_create(9, 18, "Europe/Kyiv")
    second = await service.get_or_create(0, 1, "UTC")
    assert second.id == first.id
    assert second.working_hours_start == 9
    assert second.timezone == "Europe/Kyiv"


@pytest.mark.asyncio
async def test_update_persists_changes(session):
    service = SettingsService(SettingsRepository(session))
    await service.get_or_create(9, 18, "Europe/Kyiv")
    updated = await service.update(0, 1, "UTC")
    assert updated.working_hours_start == 0
    assert updated.working_hours_end == 1
    assert updated.timezone == "UTC"

    reloaded = await SettingsRepository(session).get_settings()
    assert reloaded is not None
    assert reloaded.working_hours_start == 0
    assert reloaded.timezone == "UTC"
