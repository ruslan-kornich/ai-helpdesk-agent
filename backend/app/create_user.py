import asyncio
import getpass

from loguru import logger

from app.auth.security import hash_password
from app.config.db import build_database_manager
from app.config.logger import setup_logging
from app.models.user import User
from app.repositories.user_repository import UserRepository


async def _create_user(email: str, password: str) -> None:
    manager = build_database_manager()
    await manager.create_all()
    async with manager.session_factory() as session:
        repository = UserRepository(session)
        existing = await repository.get_by_email(email)
        if existing is not None:
            existing.hashed_password = hash_password(password)
            existing.is_active = True
            await session.commit()
            logger.info("Updated password for existing user {email}", email=email)
        else:
            await repository.add(User(email=email, hashed_password=hash_password(password)))
            await session.commit()
            logger.info("Created user {email}", email=email)
    await manager.dispose()


def main() -> None:
    setup_logging()
    email = input("Email: ").strip()
    if not email:
        raise SystemExit("Email is required")
    password = getpass.getpass("Password: ")
    if not password:
        raise SystemExit("Password is required")
    if password != getpass.getpass("Confirm password: "):
        raise SystemExit("Passwords do not match")
    asyncio.run(_create_user(email, password))


if __name__ == "__main__":
    main()
