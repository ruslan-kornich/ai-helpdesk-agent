from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.db import DatabaseManager
from app.models.message import Message  # noqa: F401
from app.models.ticket import Ticket  # noqa: F401


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    await manager.create_all()
    async with manager.session_factory() as active_session:
        yield active_session
    await manager.dispose()
