from fastapi import APIRouter

from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.dependencies import CurrentUserDep, SessionDep
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RefreshRequest, TokenPair, UserRead
from app.utils.exceptions import BusinessError

router = APIRouter()


@router.post("/login")
async def login(form: LoginRequest, session: SessionDep) -> TokenPair:
    user = await UserRepository(session).get_by_email(form.email)
    if user is None or not verify_password(form.password, user.hashed_password):
        raise BusinessError("Invalid email or password", status_code=401)
    return TokenPair(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )


@router.post("/refresh")
async def refresh(form: RefreshRequest, session: SessionDep) -> TokenPair:
    try:
        payload = decode_token(form.refresh_token)
    except ValueError as error:
        raise BusinessError("Invalid or expired refresh token", status_code=401) from error
    if payload.get("type") != "refresh":
        raise BusinessError("Invalid token type", status_code=401)
    user_id = payload.get("sub")
    user = await UserRepository(session).get_by_id(int(user_id)) if user_id else None
    if user is None or not user.is_active:
        raise BusinessError("User not found or inactive", status_code=401)
    return TokenPair(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )


@router.get("/me")
async def me(current_user: CurrentUserDep) -> UserRead:
    return UserRead.model_validate(current_user)
