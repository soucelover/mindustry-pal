"""A CLI for managing Mindustry game versions and campaigns."""

from importlib import metadata

from .campaigns import (
    CampaignDoesntExistError,
    CampaignHelper,
    CampaignStorage,
    CurrentCampaignNotSetError,
)
from .config import PalConfig
from .os_utils import GAME_DATA_DIRECTORY, PAL_DIRECTORY

__all__ = [
    "GAME_DATA_DIRECTORY",
    "PAL_DIRECTORY",
    "CampaignDoesntExistError",
    "CampaignHelper",
    "CampaignStorage",
    "CurrentCampaignNotSetError",
    "PalConfig",
    "__version__",
]
PACKAGE_NAME = "mindustry-pal"

try:
    __version__ = metadata.version(PACKAGE_NAME)
except metadata.PackageNotFoundError:
    __version__ = "0.1.dev1+UNKNOWN"
