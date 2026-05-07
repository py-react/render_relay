import json
import logging
import asyncio
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class HMRManager:
    """Manages WebSocket connections for Hot Module Replacement notifications.
    
    Browsers connect to the /__hmr WebSocket endpoint. When a file change is
    detected, the DevChangeHandler calls broadcast() to notify all connected
    browsers about the change type (css_update, js_update, full_reload).
    """

    def __init__(self):
        self._clients: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self._clients.add(websocket)
        logger.debug(f"HMR client connected. Total: {len(self._clients)}")

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            self._clients.discard(websocket)
        logger.debug(f"HMR client disconnected. Total: {len(self._clients)}")

    async def broadcast(self, message: dict):
        """Send a message to all connected HMR clients."""
        payload = json.dumps(message)
        async with self._lock:
            clients = list(self._clients)
        
        disconnected = []
        for client in clients:
            try:
                await client.send_text(payload)
            except Exception:
                disconnected.append(client)

        if disconnected:
            async with self._lock:
                for client in disconnected:
                    self._clients.discard(client)

    def broadcast_sync(self, message: dict):
        """Synchronous wrapper for broadcast, for use from non-async contexts (file watcher threads)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(self.broadcast(message), loop)
            else:
                loop.run_until_complete(self.broadcast(message))
        except RuntimeError:
            # No event loop available — create a new one
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.broadcast(message))
            loop.close()

    @property
    def client_count(self) -> int:
        return len(self._clients)


# Singleton instance shared between the FastAPI app and the file watcher
hmr_manager = HMRManager()
