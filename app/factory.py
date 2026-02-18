"""Default factories for agent, manager, routers, and websocket override.

Override these functions in downstream projects to customize behavior.
"""

from __future__ import annotations

from typing import List

from app.agent import MyAgent
from app.customer_manager import CustomManager
from app.routers import demo_router


def create_manager() -> CustomManager:
    """Create and return an instance of MyManager for websocket connections."""
    return CustomManager(session_steps=["Processing"])


def create_agent(manager: CustomManager) -> MyAgent:
    """Create and return an instance of MyAgent, initialized with the provided manager."""
    return MyAgent(manager)


def get_additional_routers() -> List[object]:
    """Return a list of additional FastAPI routers to include in the app."""
    return [demo_router]
