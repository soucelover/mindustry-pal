from __future__ import annotations

import json
import os
import shutil
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

from .campaigns import create, restore, state, store, switch

if TYPE_CHECKING:
    import zipfile

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
