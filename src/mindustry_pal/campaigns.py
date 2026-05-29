import logging
import zipfile
from argparse import Namespace
from pathlib import Path
from typing import TYPE_CHECKING

from mindustry_pal.config import dump_config
from mindustry_pal.files import (
    clear_folder,
    resolve_path,
    restore_zip,
    store_to_zip,
)
from mindustry_pal.os_utils import GAME_DATA_DIRECTORY

if TYPE_CHECKING:
    from argparse import Namespace

    from mindustry_pal.config import PalConfig


logger = logging.getLogger(__name__)


def store(args: Namespace, config: PalConfig) -> None:
    """Store current campaign"""
    if args.name is None:
        name = config.current_campaign

        # 'name' is optional arg
        # by default it is the current campaign
        if name is None:
            logger.error(
                "Failed to store current campaign: "
                "for the first time you should specialize name"
            )
            return
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
            logger.error(
                "Failed to restore current campaign. "
                "You should specify name argument or "
                "store current campaign"
            )
            return
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
        logger.error(
            "%s: you should store current campaign before creating new.",
            err_msg_prefix,
        )
        return

    current = resolve_path(Path(config.current_campaign))
    new = resolve_path(Path(args.name))

    if new.exists():
        logger.error(
            "%s: you must create new campaign, not existing.", err_msg_prefix
        )
        return

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
        logger.error(
            "%s: you must store current campaign before switching to another",
            err_msg_prefix,
        )
        return

    current = resolve_path(Path(config.current_campaign))
    restore = resolve_path(Path(args.name))

    if current == restore:
        logger.error(
            "%s: you must switch to another campaign, not current",
            err_msg_prefix,
        )
        return

    if not restore.exists():
        logger.error(
            "%s: campaign %s doesn't exist", err_msg_prefix, args.name
        )
        return

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
