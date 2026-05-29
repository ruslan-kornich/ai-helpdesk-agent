from datetime import datetime
from zoneinfo import ZoneInfo


def local_now(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


def format_working_hours(start: int, end: int, timezone: str) -> str:
    return f"{start:02d}:00-{end:02d}:00 {timezone}"
