"""."""

import typing
from importlib import metadata

version: typing.Annotated[str, "Version"] = metadata.version("smart_trade_ai")
