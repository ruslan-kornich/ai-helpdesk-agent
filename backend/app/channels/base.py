from abc import ABC, abstractmethod

from app.models.enums import Channel


class BaseChannel(ABC):
    """Outbound interface every channel implements to deliver a reply to a client."""

    channel: Channel

    @abstractmethod
    async def send(self, client_id: str, text: str) -> None: ...
