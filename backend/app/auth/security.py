from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from app.config.settings import get_settings
from app.models.user import User

security = HTTPBearer(auto_error=False)


def hash_password(raw: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(raw.encode("utf-8"), salt).decode("utf-8")


def verify_password(raw: str, hashed: str) -> bool:
    return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))


def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {**data, "iat": now, "exp": now + expires_delta}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user: User) -> str:
    return _create_token(
        {"sub": str(user.id), "email": user.email, "type": "access"},
        timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user: User) -> str:
    return _create_token(
        {"sub": str(user.id), "type": "refresh"},
        timedelta(days=get_settings().REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as error:
        raise ValueError("Invalid token") from error
