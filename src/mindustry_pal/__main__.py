from __future__ import annotations

import json
import os
import shutil
import zipfile
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace

name = "manage.py"
usage = None
description = "Manager made for mindustry game."
epilog = "epi"
mindustry_dir = Path(os.getenv("APPDATA")) / "Mindustry"


def resolve_path(path: Path) -> Path:
    if not path.is_absolute():
        path = Path("campaigns") / path

    if path.suffix != ".zip":
        path = path.with_suffix(path.suffix + ".zip")

    return path.resolve()


def clear_folder(path: Path) -> None:
    for path in path.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def store_to_zip(zfile: zipfile.ZipFile) -> None:
    class Frame:
        def __init__(self, iter):
            self.iter = iter

        iter = None
        file = None

    stack = [Frame(mindustry_dir.iterdir())]

    while stack:
        last = stack[-1]

        try:
            last.file = last.iter.__next__()
        except StopIteration:
            del stack[-1]
            continue

        if last.file.is_dir():
            stack.append(Frame(last.file.iterdir()))
            zfile.mkdir(str(last.file.relative_to(mindustry_dir)))
        else:
            zfile.write(last.file, str(last.file.relative_to(mindustry_dir)))


def restore_zip(zrestore: zipfile.ZipFile) -> None:
    clear_folder(mindustry_dir)
    zrestore.extractall(mindustry_dir)


def load_cfg() -> dict:
    Path("config.json").touch()

    with open("config.json") as f:
        cfg = json.load(f)

    if not isinstance(cfg, dict):
        return {}

    return cfg


def dump_cfg(cfg: dict) -> None:
    if not isinstance(cfg, dict):
        cfg = {}

    Path("config.json").touch()

    with open("config.json", "w") as f:
        json.dump(cfg, f)


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


def main(args: list[str] | None = None) -> None:
    parser = ArgumentParser(name, usage, description, epilog)
    parsers = parser.add_subparsers(metavar="command", required=True)

    store_parser = parsers.add_parser("store", help=store.__doc__)
    store_parser.add_argument("name", nargs="?", help="Name of campaign")
    store_parser.set_defaults(command=store)

    restore_parser = parsers.add_parser("restore", help=store.__doc__)
    restore_parser.add_argument("name", nargs="?", help="Name of campaign")
    restore_parser.set_defaults(command=restore)

    create_parser = parsers.add_parser("create", help=create.__doc__)
    create_parser.add_argument("name", help="Name of new campaign")
    create_parser.set_defaults(command=create)

    switch_parser = parsers.add_parser("switch", help=switch.__doc__)
    switch_parser.add_argument("name")
    switch_parser.set_defaults(command=switch)

    state_parser = parsers.add_parser("state", help=state.__doc__)
    state_parser.set_defaults(command=state)

    parsed = parser.parse_args(args)
    parsed.command(parsed)


if __name__ == "__main__":
    main()
