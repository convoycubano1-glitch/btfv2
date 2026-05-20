from fastapi import WebSocket
from typing import Dict, List, Set
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages active WebSocket connections per user and channel."""

    def __init__(self):
        # user_id -> list of websockets
        self._user_connections: Dict[str, List[WebSocket]] = {}
        # channel -> set of user_ids
        self._channel_subscriptions: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self._user_connections:
            self._user_connections[user_id] = []
        self._user_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected: user={user_id}")

    async def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self._user_connections:
            try:
                self._user_connections[user_id].remove(websocket)
            except ValueError:
                pass
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]
        logger.info(f"WebSocket disconnected: user={user_id}")

    async def send_to_user(self, user_id: str, message: dict):
        """Send a JSON message to all connections of a user."""
        connections = self._user_connections.get(user_id, [])
        dead = []
        for ws in connections:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.append(ws)
        for ws in dead:
            try:
                self._user_connections[user_id].remove(ws)
            except ValueError:
                pass

    async def broadcast_to_channel(self, channel: str, message: dict):
        """Broadcast to all users subscribed to a channel."""
        user_ids = self._channel_subscriptions.get(channel, set())
        for user_id in list(user_ids):
            await self.send_to_user(user_id, message)

    def subscribe_to_channel(self, user_id: str, channel: str):
        if channel not in self._channel_subscriptions:
            self._channel_subscriptions[channel] = set()
        self._channel_subscriptions[channel].add(user_id)

    def unsubscribe_from_channel(self, user_id: str, channel: str):
        if channel in self._channel_subscriptions:
            self._channel_subscriptions[channel].discard(user_id)

    @property
    def active_connections(self) -> int:
        return sum(len(v) for v in self._user_connections.values())


ws_manager = WebSocketManager()
