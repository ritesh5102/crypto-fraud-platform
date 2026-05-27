"""WebSocket manager for real-time fraud alerts."""

import asyncio
import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        payload = json.dumps(message, default=str)
        dead: list[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


ws_manager = ConnectionManager()


async def alert_stream_task(get_alert_fn, interval: float = 8.0):
    """Background task: periodically push new alerts to connected clients."""
    while True:
        await asyncio.sleep(interval)
        if not ws_manager.active:
            continue
        try:
            alert = get_alert_fn()
            if asyncio.iscoroutine(alert):
                alert = await alert
            if alert:
                await ws_manager.broadcast({"type": "fraud_alert", "data": alert})
        except Exception:
            pass
