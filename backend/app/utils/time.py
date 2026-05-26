from datetime import datetime
from zoneinfo import ZoneInfo


def local_now(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))
