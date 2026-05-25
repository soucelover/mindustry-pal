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


def store(args: Namespace, config: PalConfig) -> None:
    """Store current campaign"""
    err_msg_prefix = "Failed to store current campaign: "

    if args.name is None:
        name = config.current_campaign

        # 'name' is optional arg
        # by default it is the current campaign
        if name is None:
            print(
                err_msg_prefix
                + "for the first time you should specialize name"
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
    print("Successfully stored campaign.")


def restore(args: Namespace, config: PalConfig) -> None:
    """Restore campaign"""
    err_msg_prefix = "Failed to restore %scampaign"

    if args.name is None:
        name = config.current_campaign

        if name is None:
            print(
                (err_msg_prefix % "current ")
                + "You should specify name argument or"
                + " store current campaign"
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
    print("Successfully stored campaign.")


def create(args: Namespace, config: PalConfig) -> None:
    """Create new campaign and switch to it."""
    err_msg_prefix = "Failed to create new mindustry campaign: "

    if config.current_campaign is None:
        print(
            err_msg_prefix
            + "you should store current campaign before creating new."
        )
        return

    current = resolve_path(Path(config.current_campaign))
    new = resolve_path(Path(args.name))

    if new.exists():
        print(err_msg_prefix + "you must create new campaign, not existing.")
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
    print("Successfully created new campaign.")


def switch(args: Namespace, config: PalConfig) -> None:
    """Switch mindustry copaign"""
    err_msg_prefix = "Failed to switch mindustry campaign: "

    if config.current_campaign is None:
        print(
            err_msg_prefix
            + "you must store current campaign before switching to another"
        )
        return

    current = resolve_path(Path(config.current_campaign))
    restore = resolve_path(Path(args.name))

    if current == restore:
        print(
            err_msg_prefix
            + "you must switch to another campaign, not current,"
        )
        return

    if not restore.exists():
        print(err_msg_prefix + f"campaign {args.name} doesn't exist.")
        return

    current.parent.mkdir(parents=True, exist_ok=True)
    current.touch()

    with zipfile.ZipFile(current, "w") as zstore:
        store_to_zip(zstore)

    with zipfile.ZipFile(restore, "r") as zrestore:
        restore_zip(zrestore)

    config.current_campaign = restore.name
    dump_config(config)
    print(f"Successfully switched current campaign to {restore.name}.")


def state(args: Namespace, config: PalConfig) -> None:
    if config.current_campaign is None:
        print("Current campaign wasn't previously stored.")
        current = None
    else:
        current = config.current_campaign
        print(f'Current campaign is "{current}".')

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

        print(msg)  # noqa: T201
