import zipfile
from argparse import Namespace
from pathlib import Path
from typing import TYPE_CHECKING

from mindustry_pal.files import (
    clear_folder,
    dump_cfg,
    load_cfg,
    resolve_path,
    restore_zip,
    store_to_zip,
)

if TYPE_CHECKING:
    from argparse import Namespace


def store(args: Namespace) -> None:
    """Store current campaign"""
    err_msg_prefix = "Failed to store current campaign: "
    cfg = load_cfg()

    if args.name is None:
        # 'name' is optional arg
        # by default it is the current campaign
        if cfg.get("current-campaign", None) is None:
            print(
                err_msg_prefix
                + "for the first time you should specialize name"
            )
            return

        name = cfg["current-campaign"]
    else:
        name = args.name

    dst = resolve_path(Path(name))
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.touch()

    with zipfile.ZipFile(dst, "w") as zfile:
        store_to_zip(zfile)

    cfg["current-campaign"] = dst.name
    dump_cfg(cfg)
    print("Successfully stored campaign.")


def restore(args: Namespace) -> None:
    """Restore campaign"""
    err_msg_prefix = "Failed to restore %scampaign"
    cfg = load_cfg()

    if args.name is None:
        name = cfg.get("current-campaign", None)

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

    cfg["current-campaign"] = restore.name
    dump_cfg(cfg)
    print("Successfully stored campaign.")


mindustry_dir = Path(os.getenv("APPDATA")) / "Mindustry"


def create(args: Namespace) -> None:
    """Create new campaign and switch to it."""
    err_msg_prefix = "Failed to create new mindustry campaign: "
    cfg = load_cfg()

    if "current-campaign" not in cfg:
        print(
            err_msg_prefix
            + "you should store current campaign before creating new."
        )
        return
    current = resolve_path(Path(cfg["current-campaign"]))

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

    with zipfile.ZipFile(new, "w") as znew:
        pass

    clear_folder(mindustry_dir)
    cfg["current-campaign"] = new.name
    dump_cfg(cfg)
    print("Successfully created new campaign.")


def switch(args: Namespace) -> None:
    """Switch mindustry copaign"""
    err_msg_prefix = "Failed to switch mindustry campaign: "
    cfg = load_cfg()

    if "current-campaign" not in cfg:
        print(
            err_msg_prefix
            + "you must store current campaign before switching to another"
        )
        return
    current = resolve_path(Path(cfg["current-campaign"]))

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

    cfg["current-campaign"] = restore.name
    dump_cfg(cfg)
    print(f"Successfully switched current campaign to {restore.name}.")


def state(args: Namespace) -> None:
    cfg = load_cfg()

    if "current-campaign" not in cfg:
        print("Current campaign wasn't previously stored.")
        current = None
    else:
        current = cfg["current-campaign"]
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
