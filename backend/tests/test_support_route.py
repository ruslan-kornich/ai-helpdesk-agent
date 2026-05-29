from collections.abc import AsyncIterator
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.channels.zendesk import ZendeskChannel
from app.dependencies import get_context, get_session
from app.main import create_app
from app.models.enums import Channel


@pytest_asyncio.fixture
async def support_setup(
    session: AsyncSession,
) -> AsyncIterator[tuple[AsyncClient, ZendeskChannel]]:
    app = create_app()

    channel = ZendeskChannel("sub", "admin@example.com", "token")
    channel.find_or_create_end_user = AsyncMock(return_value="555")
    channel.create_request_ticket = AsyncMock(return_value="2")
    channel.append_comment_as_requester = AsyncMock()

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_context] = lambda: SimpleNamespace(
        channels={Channel.ZENDESK: channel}
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, channel
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_support_chat_creates_ticket_when_no_id(support_setup):
    client, channel = support_setup
    response = await client.post(
        "/api/support/chat",
        json={"name": "Jane", "email": "jane@example.com", "text": "hello"},
    )
    assert response.status_code == 200
    assert response.json()["zendesk_ticket_id"] == "2"
    channel.create_request_ticket.assert_awaited_once()
    channel.append_comment_as_requester.assert_not_awaited()


@pytest.mark.asyncio
async def test_support_chat_appends_when_id_present(support_setup):
    client, channel = support_setup
    response = await client.post(
        "/api/support/chat",
        json={
            "name": "Jane",
            "email": "jane@example.com",
            "text": "second",
            "zendesk_ticket_id": "42",
        },
    )
    assert response.status_code == 200
    assert response.json()["zendesk_ticket_id"] == "42"
    channel.append_comment_as_requester.assert_awaited_once()
    channel.create_request_ticket.assert_not_awaited()


def _zendesk_status_error(status_code: int) -> httpx.HTTPStatusError:
    request = httpx.Request("PUT", "https://sub.zendesk.com/api/v2/tickets/42.json")
    response = httpx.Response(status_code, request=request, json={"error": "boom"})
    return httpx.HTTPStatusError("boom", request=request, response=response)


@pytest.mark.asyncio
async def test_support_chat_recreates_ticket_when_stale(support_setup):
    client, channel = support_setup
    channel.append_comment_as_requester = AsyncMock(
        side_effect=_zendesk_status_error(404)
    )
    response = await client.post(
        "/api/support/chat",
        json={
            "name": "Jane",
            "email": "jane@example.com",
            "text": "second",
            "zendesk_ticket_id": "42",
        },
    )
    assert response.status_code == 200
    assert response.json()["zendesk_ticket_id"] == "2"
    channel.append_comment_as_requester.assert_awaited_once()
    channel.create_request_ticket.assert_awaited_once()


@pytest.mark.asyncio
async def test_support_chat_returns_502_on_non_404_error(support_setup):
    client, channel = support_setup
    channel.append_comment_as_requester = AsyncMock(
        side_effect=_zendesk_status_error(403)
    )
    response = await client.post(
        "/api/support/chat",
        json={
            "name": "Jane",
            "email": "jane@example.com",
            "text": "second",
            "zendesk_ticket_id": "42",
        },
    )
    assert response.status_code == 502
    channel.create_request_ticket.assert_not_awaited()


@pytest.mark.asyncio
async def test_support_chat_rejects_invalid_email(support_setup):
    client, _ = support_setup
    response = await client.post(
        "/api/support/chat",
        json={"name": "Jane", "email": "not-an-email", "text": "hello"},
    )
    assert response.status_code == 400
