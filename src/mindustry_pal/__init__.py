"""A CLI for managing Mindustry game versions and campaigns."""

from importlib import metadata

__all__ = ["__version__"]
PACKAGE_NAME = "mindustry-pal"

try:
    __version__ = metadata.version(PACKAGE_NAME)
except metadata.PackageNotFoundError:
    __version__ = "0.1.dev1+UNKNOWN"
