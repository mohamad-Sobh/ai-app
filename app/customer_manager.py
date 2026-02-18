from __future__ import annotations

from typing import Any, Dict, Optional

from gagent_core.websocket_manager import ConnectionManager
from gagent_core.logs import logger


class CustomManager(ConnectionManager):
    """
    Custom ConnectionManager that lets you attach per-session resources
    (agents, orchestrators, caches, etc).
    """

    def __init__(self, session_steps: Optional[list[str]] = None, enable_citations: bool = False):
        super().__init__(session_steps=session_steps, enable_citations=enable_citations)
        self.active_threads: Dict[str, Any] = {}

    async def initialize_session(self, app, thread_id: str):
        """
        Hook to initialize resources for a session.
        Example: create agent/orchestrator, DB clients, etc.
        """
        # Replace with your actual initializer
        return {"thread_id": thread_id, "status": "ready"}

    async def save_session_state(self, thread_id: str):
        """
        Hook to persist state when a session ends.
        """
        # Replace with actual persistence logic
        logger.info(f"Saving state for session {thread_id}")

    async def connect(
        self,
        websocket,
        thread_id: str,
        created_by: str,
        include_history: bool,
        last_timestamp: str | None,
        session_type: str = "text",
    ):
        # Always call parent first (core DB/cache setup + ws accept)
        await super().connect(websocket, thread_id, created_by, include_history, last_timestamp, session_type)

        # Custom connection logic
        app = websocket.scope["app"]
        self.active_threads[thread_id] = await self.initialize_session(app, thread_id)

    async def disconnect(self, thread_id: str):
        # Custom disconnect logic
        await self.save_session_state(thread_id)
        self.active_threads.pop(thread_id, None)

        # Always call parent last (cleanup core resources)
        await super().disconnect(thread_id)