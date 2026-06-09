import logging
import zipfile
from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .cli import CommandError
from .config import dump_config
from .files import (
    add_to_zip,
    clear_folder,
    resolve_path,
    restore_zip,
    store_to_zip,
)
from .os_utils import GAME_DATA_DIRECTORY

if TYPE_CHECKING:
    from argparse import Namespace

    from .config import PalConfig


logger = logging.getLogger(__name__)


def store(args: Namespace, config: PalConfig) -> None:
    """Store current campaign"""
    if args.name is None:
        name = config.current_campaign

        # 'name' is optional arg
        # by default it is the current campaign
        if name is None:
            msg = (
                "Failed to store current campaign: "
                "for the first time you should specialize name"
            )
            raise CommandError(msg)
    else:
        name = args.name

    dst = resolve_path(Path(name))
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.touch()

    with zipfile.ZipFile(dst, "w") as zfile:
        store_to_zip(zfile)

    config.current_campaign = dst.name
    dump_config(config)
    logger.info("Successfully stored campaign.")


def restore(args: Namespace, config: PalConfig) -> None:
    """Restore campaign"""
    if args.name is None:
        name = config.current_campaign

        if name is None:
            msg = (
                "Failed to restore current campaign. "
                "You should specify name argument or store current campaign"
            )
            raise CommandError(msg)
    else:
        name = args.name

    restore = resolve_path(Path(name))
    restore.parent.mkdir(parents=True, exist_ok=True)
    restore.touch()

    with zipfile.ZipFile(restore, "r") as zrestore:
        restore_zip(zrestore)

    config.current_campaign = restore.name
    dump_config(config)
    logger.info("Successfully stored campaign.")


def create(args: Namespace, config: PalConfig) -> None:
    """Create new campaign and switch to it."""
    err_msg_prefix = "Failed to create new mindustry campaign"

    if config.current_campaign is None:
        msg = (
            f"{err_msg_prefix}: "
            "you should store current campaign before creating new."
        )
        raise CommandError(msg)

    current = resolve_path(Path(config.current_campaign))
    new = resolve_path(Path(args.name))

    if new.exists():
        msg = f"{err_msg_prefix}: you must create new campaign, not existing."
        raise CommandError(msg)

    current.parent.mkdir(parents=True, exist_ok=True)
    current.touch()

    with zipfile.ZipFile(current, "w") as zstore:
        store_to_zip(zstore)

    new.parent.mkdir(parents=True, exist_ok=True)
    new.touch()

    with zipfile.ZipFile(new, "w"):
        pass

    clear_folder(GAME_DATA_DIRECTORY)
    config.current_campaign = new.name
    dump_config(config)
    logger.info("Successfully created new campaign.")


def switch(args: Namespace, config: PalConfig) -> None:
    """Switch mindustry copaign"""
    err_msg_prefix = "Failed to switch mindustry campaign"

    if config.current_campaign is None:
        msg = (
            f"{err_msg_prefix}: "
            "you must store current campaign before switching to another"
        )
        raise CommandError(msg)

    current = resolve_path(Path(config.current_campaign))
    restore = resolve_path(Path(args.name))

    if current == restore:
        msg_0 = (
            f"{err_msg_prefix}: "
            "you must switch to another campaign, not current"
        )
        raise CommandError(msg_0)

    if not restore.exists():
        msg_1 = f"{err_msg_prefix}: campaign {args.name} doesn't exist"
        raise CommandError(msg_1)

    current.parent.mkdir(parents=True, exist_ok=True)
    current.touch()

    with zipfile.ZipFile(current, "w") as zstore:
        store_to_zip(zstore)

    with zipfile.ZipFile(restore, "r") as zrestore:
        restore_zip(zrestore)

    config.current_campaign = restore.name
    dump_config(config)
    logger.info("Successfully switched current campaign to %s.", restore.name)


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


@dataclass(slots=True, frozen=True)
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

    def __init__(self, config: PalConfig) -> None:
        """Initialize class -- store its dependencies.

        Args:
            config: Configuration of the Mindustry-Pal utility.
        """
        self.config = config

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
            add_to_zip(zfile, base / "saves/", base)
            add_to_zip(zfile, base / "mods/", base)
            add_to_zip(zfile, base / "maps/", base)
            add_to_zip(zfile, base / "schematics/", base)
            add_to_zip(zfile, base / "settings.bin", base)

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
        raise NotImplementedError

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
