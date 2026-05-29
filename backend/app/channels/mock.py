from loguru import logger

from app.channels.base import BaseChannel
from app.models.enums import Channel


class MockChannel(BaseChannel):
    def __init__(self, channel: Channel) -> None:
        self.channel = channel

    async def send(self, client_id: str, text: str) -> None:
        logger.info(
            "[mock:{channel}] -> {client}: {text}",
            channel=self.channel,
            client=client_id,
            text=text,
        )
