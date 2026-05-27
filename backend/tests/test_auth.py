from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import hash_password
from app.dependencies import get_session
from app.main import create_app
from app.models.user import User

TEST_EMAIL = "demo@example.com"
TEST_PASSWORD = "secret123"


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    session.add(User(email=TEST_EMAIL, hashed_password=hash_password(TEST_PASSWORD)))
    await session.commit()

    app = create_app()

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_success_returns_tokens(client: AsyncClient):
    response = await client.post(
        "/api/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_is_rejected(client: AsyncClient):
    response = await client.post(
        "/api/auth/login", json={"email": TEST_EMAIL, "password": "wrong"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token_is_unauthorized(client: AsyncClient):
    response = await client.get("/api/tickets")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_token_succeeds(client: AsyncClient):
    login = await client.post(
        "/api/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    access_token = login.json()["access_token"]
    response = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == TEST_EMAIL


@pytest.mark.asyncio
async def test_refresh_issues_new_access_token(client: AsyncClient):
    login = await client.post(
        "/api/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    refresh_token = login.json()["refresh_token"]
    response = await client.post(
        "/api/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
