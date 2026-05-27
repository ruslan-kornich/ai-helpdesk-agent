from abc import ABC, abstractmethod

from app.models.enums import Channel


class BaseChannel(ABC):
    channel: Channel

    @abstractmethod
    async def send(self, client_id: str, text: str) -> None: ...
