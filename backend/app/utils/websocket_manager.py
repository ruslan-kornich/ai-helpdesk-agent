from typing import Any

from fastapi import WebSocket
from loguru import logger


class WebSocketManager:
    def __init__(self) -> None:
        self.connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.connections.discard(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for websocket in list(self.connections):
            try:
                await websocket.send_json(message)
            except Exception as error:
                logger.warning("WebSocket send failed, dropping connection: {error}", error=error)
                stale.append(websocket)
        for websocket in stale:
            self.connections.discard(websocket)
