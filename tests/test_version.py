"""."""

from importlib import metadata

from app import version


def test_version() -> None:
    """."""
    assert metadata.version("smart_trade_ai") == version.version
