"""Bot polling."""

import argparse
import asyncio
import logging
import typing

from app.containers.application import ApplicationContainer
from app.version import version

logger = logging.getLogger(__name__)


async def start_polling(
        container: ApplicationContainer | None = None, log_level: str = "INFO"
) -> None:
    """Create app."""
    if container is None:
        container = ApplicationContainer()

    debug: bool = container.config.get("debug")
    logging.basicConfig(level=log_level)

    if debug is False:
        # Disable httpx logs
        logging.getLogger("httpx").handlers = []
        logging.getLogger("httpx").propagate = False

    ws_service = container.services.bybit_stream()

    try:
        await ws_service.start()
    finally:
        await ws_service.stop()
        logger.info("Bybit Stream stopped.")


class ArgsNamespace(argparse.Namespace):
    """Args namespace."""

    log_level: str = "info"


def server_parser_args() -> typing.Type[ArgsNamespace]:  # noqa: WPS213
    """Server parser args."""
    parser = argparse.ArgumentParser(description="Smart Trade polling.")
    parser.add_argument(
        "--log-level",
        dest="log_level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Log level.",
    )
    return parser.parse_args(namespace=ArgsNamespace)


def main() -> None:
    """."""
    args: typing.Type[ArgsNamespace] = server_parser_args()
    log_level: str = args.log_level.upper()
    logging.basicConfig(level=getattr(logging, log_level))
    logger.info("Starting smart trade ai in pooling mode, v%s", version)
    asyncio.run(start_polling(log_level=log_level))


if __name__ == "__main__":  # pragma: no cover
    main()
