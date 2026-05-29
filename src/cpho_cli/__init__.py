"""CPHO CLI package."""

from __future__ import annotations

from importlib import metadata

__all__ = ["__version__", "get_version"]

__version__ = "0.1.0"


def get_version() -> str:
    try:
        return metadata.version("cpho-cli")
    except metadata.PackageNotFoundError:
        return "0.0.0+unknown"
