"""FastAPI server."""

from typing import Optional

import fastapi
from sgkit import server

from app.containers.application import ApplicationContainer
from app.routes.v1 import router as router_v1


def create_app(container: Optional[ApplicationContainer] = None) -> fastapi.FastAPI:
    """Create app."""
    if container is None:  # pragma: no cover
        container = ApplicationContainer()

    return server.create_app(  # type: ignore
        container, title="Sample service", routes=[router_v1]
    )


def main() -> None:
    """Run fastapi server."""
    server.run_app(app="app.main.api:create_app", reload_dirs=["app/", "config/"])


if __name__ == "__main__":  # pragma: no cover
    main()
