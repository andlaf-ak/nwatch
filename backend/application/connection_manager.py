"""ConnectionManager for WebSocket client connections.

Manages active WebSocket connections, providing functionality to track clients,
broadcast messages to all connected clients, and send messages to individual clients.
"""

import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates.

    Maintains a list of active WebSocket connections and provides methods
    to connect, disconnect, broadcast to all clients, and send to individual
    clients.

    Attributes:
        active_connections: List of currently connected WebSocket clients.
    """

    def __init__(self) -> None:
        """Initialize the ConnectionManager with an empty connections list."""
        self._active_connections: list[WebSocket] = []

    @property
    def active_connections(self) -> list[WebSocket]:
        """Return the list of active WebSocket connections.

        Returns:
            List of connected WebSocket instances.
        """
        return self._active_connections

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection.

        Accepts the WebSocket handshake and adds the connection to the
        active connections list.

        Args:
            websocket: The WebSocket connection to accept and register.
        """
        await websocket.accept()
        self._active_connections.append(websocket)
        logger.info(
            "WebSocket client connected. Total connections: %d",
            len(self._active_connections),
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection from the active list.

        Safely removes the connection if it exists in the active list.
        Does nothing if the connection is not found.

        Args:
            websocket: The WebSocket connection to remove.
        """
        if websocket in self._active_connections:
            self._active_connections.remove(websocket)
            logger.info(
                "WebSocket client disconnected. Total connections: %d",
                len(self._active_connections),
            )
        else:
            logger.debug("Attempted to disconnect unknown WebSocket connection")

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Send a JSON message to all connected clients.

        Broadcasts the message to all active connections. If a client
        has disconnected or an error occurs during send, that client
        is removed from the active connections list and the broadcast
        continues to remaining clients.

        Args:
            message: Dictionary to serialize as JSON and send to all clients.
        """
        json_message = json.dumps(message)
        disconnected_clients: list[WebSocket] = []

        logger.info(
            "Broadcasting message to %d clients: %s",
            len(self._active_connections),
            json_message[:200],
        )

        for connection in self._active_connections:
            try:
                await connection.send_text(json_message)
                logger.info("Message sent successfully to client")
            except Exception as e:
                logger.warning(
                    "Failed to send message to client: %s. Marking for removal.",
                    str(e),
                )
                disconnected_clients.append(connection)

        # Remove disconnected clients after iteration
        for client in disconnected_clients:
            if client in self._active_connections:
                self._active_connections.remove(client)
                logger.info(
                    "Removed disconnected client. Total connections: %d",
                    len(self._active_connections),
                )

    async def send_personal(
        self, websocket: WebSocket, message: dict[str, Any]
    ) -> None:
        """Send a JSON message to a single client.

        Sends the message to the specified WebSocket connection.
        If an error occurs, logs the error but does not remove the
        connection (caller should handle disconnect if needed).

        Args:
            websocket: The WebSocket connection to send the message to.
            message: Dictionary to serialize as JSON and send.

        Raises:
            Exception: Re-raises any exception from the WebSocket send operation.
        """
        json_message = json.dumps(message)
        try:
            await websocket.send_text(json_message)
        except Exception as e:
            logger.error("Failed to send personal message to client: %s", str(e))
            raise
