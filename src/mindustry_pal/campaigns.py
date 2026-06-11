import logging
import zipfile
from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from .files import add_to_zip, restore_from_zip
from .os_utils import GAME_DATA_DIRECTORY

if TYPE_CHECKING:
    from argparse import Namespace

    from .config import PalConfig


logger = logging.getLogger(__name__)


def state(args: Namespace, config: PalConfig) -> None:
    if config.current_campaign is None:
        logger.info("Current campaign wasn't previously stored.")
        current = None
    else:
        current = config.current_campaign
        logger.info("Current campaign is %r.", current)

    other_campaigns = [
        i for i in Path("./campaigns").iterdir() if i.name != current
    ]

    if other_campaigns:
        msg = f"{'Also' if current else 'But'} there "

        if len(other_campaigns) == 1:
            msg += (
                f"is {'another' if current else 'one'} stored campaign "
                f"named {other_campaigns[0]}"
            )
        else:
            msg += "are also other campaigns:\n"
            msg += "\n".join(
                f"  - {campaign.name}" for campaign in other_campaigns
            )

        logger.info(msg)


class CurrentCampaignNotSetError(Exception):
    """Current config is missing value for `current-campaign`."""


@dataclass(slots=True, frozen=True, eq=True)
class CampaignStorage:
    """Dataclass representing campaign storage file."""

    path: Path

    @property
    def name(self) -> str:
        """Name of the campaign storage (name of the file)."""
        return self.path.stem

    @property
    def exists(self) -> bool:
        """Check if the storage file does exist."""
        return self.path.is_file()

    def __str__(self) -> str:
        """String representation of campaign file path."""
        return str(self.path)


class CampaignHelper:
    """A helper class for working with campaign files."""

    config: PalConfig
    campaign_members: ClassVar[list[str]] = [
        "saves/",
        "mods/",
        "maps/",
        "schematics/",
        "settings.bin",
    ]

    def __init__(self, config: PalConfig) -> None:
        """Initialize class -- store its dependencies.

        Args:
            config: Configuration of the Mindustry-Pal utility.
        """
        self.config = config

    def create(self, storage: CampaignStorage) -> None:
        """Create a new storage file.

        If file already exists, it gets overriden.

        Args:
            storage: Path to a `.zip` file to be created.
        """
        dst = storage.path
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.touch()

        with zipfile.ZipFile(dst, "w"):
            pass

        logger.debug("Created empty campaign at %s", storage)

    def store(self, storage: CampaignStorage) -> None:
        """Store current campaign to `storage`.

        Args:
            storage: A `.zip` storage file where current Mindustry
                campaign gets stored to.
        """
        dst = storage.path
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.touch()
        base = GAME_DATA_DIRECTORY

        with zipfile.ZipFile(dst, "w") as zfile:
            for member in self.campaign_members:
                add_to_zip(zfile, base / member, base)

        logger.debug("Stored campaign to %s", storage)

    def restore(self, storage: CampaignStorage) -> None:
        """Restore Mindustry campaign from a `storage`.

        Args:
            storage: A `.zip` storage file where Mindustry campaign is
                restored from.
        """
        base = GAME_DATA_DIRECTORY
        base.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(storage.path, "r") as zfile:
            for member in self.campaign_members:
                restore_from_zip(zfile, member, base)

        logger.debug("Restored campaign from %s", storage)

    def get_campaign_path(self, name: str) -> Path:
        """Get path of the campaign storage file by its name.

        Args:
            name: Name of the campaign.

        Returns:
            Path of the campaign file with `.zip` suffix.
        """
        campaigns = self.config.get_campaigns_dir()
        path = campaigns / name
        return path.with_suffix(path.suffix + ".zip")

    def set_current_campaign(self, storage: CampaignStorage) -> None:
        """Set curently selected campaign pointer to this file in the config.

        Args:
            storage: Campaign storage file that will be marked as current.
        """
        self.config.current_campaign = storage.name
        logger.debug(
            "Changed current campaign to %r", self.config.current_campaign
        )

    def is_current_campaign(self, storage: CampaignStorage) -> bool:
        """Specified storage is current campaign.

        Args:
            storage: The storage being compared.

        Returns:
            True if the storage is specified as `current-campaign` in config.
        """
        current_campaign = self.get_campaign(check_exists=False)
        return storage == current_campaign

    def get_campaign(
        self, name: str | None = None, *, check_exists: bool = False
    ) -> CampaignStorage:
        """Get campaign file by name.

        Args:
            name: Name of the campaign. If `None`, current campaign is
                returned instead (see `.get_current_campaign()`).
            check_exists: Check if file is missing.

        Raises:
            CurrentCampaignNotSetError: If name is `None` and config is
                missing `current-campaign` entry.
            FileNotFoundError: If `check_exists` was specified and campaign
                does not exist.
        """
        if name is None:
            if self.config.current_campaign is None:
                msg = (
                    "Current configuration doesn't contain "
                    "`current-campaign` key"
                )
                raise CurrentCampaignNotSetError(msg)

            name = self.config.current_campaign

        campaign = CampaignStorage(self.get_campaign_path(name))

        if check_exists and not campaign.exists:
            msg_0 = f"Campaign file {campaign} does not exist"
            raise FileNotFoundError(msg_0)

        return campaign
