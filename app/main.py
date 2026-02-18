"""
PACI Agent Main Application

Using extended g-agent-ai-core-backend with unified audio WebSocket support.
Audio messages (audio-input-start/chunk/end) are handled in the same WebSocket
as text messages, eliminating the need for a separate STT WebSocket.
"""
from gagent_core.base_app import create_app

from app.config import AppSettings
from app.factory import (
    create_agent,
    create_manager,
    get_additional_routers,
)


def build_app(settings: AppSettings | None = None):
    settings = settings or AppSettings()

    # Initialize - these are exposed for use by routers
    manager = create_manager()
    agent = create_agent(manager)

    # Create the app with optional additional routers
    app = create_app(agent, manager, additional_routers=get_additional_routers())

    # Store agent in app state for access by routers
    app.state.agent = agent
    app.state.manager = manager

    return app


# Initialize application instance for ASGI servers
app = build_app()


if __name__ == "__main__":
    import uvicorn

    settings = AppSettings()
    uvicorn.run(app, host=settings.host, port=settings.port)
