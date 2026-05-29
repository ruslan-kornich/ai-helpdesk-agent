import sys

from loguru import logger

from app.config.settings import get_settings


def setup_logging() -> None:
    level = get_settings().LOG_LEVEL.upper()
    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        backtrace=True,
        diagnose=False,
    )
