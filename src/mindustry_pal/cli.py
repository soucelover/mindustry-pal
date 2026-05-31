from argparse import ArgumentParser

from mindustry_pal.config import load_config
from mindustry_pal.errors import CommandError

from .campaigns import create, restore, state, store, switch

name = "manage.py"
usage = None
description = "Manager made for mindustry game."
epilog = "epi"


def register_commands(parser: ArgumentParser) -> None:
    commands = parser.add_subparsers(metavar="command", required=True)

    store_parser = commands.add_parser("store", help=store.__doc__)
    store_parser.add_argument("name", nargs="?", help="Name of campaign")
    store_parser.set_defaults(command=store)

    restore_parser = commands.add_parser("restore", help=store.__doc__)
    restore_parser.add_argument("name", nargs="?", help="Name of campaign")
    restore_parser.set_defaults(command=restore)

    create_parser = commands.add_parser("create", help=create.__doc__)
    create_parser.add_argument("name", help="Name of new campaign")
    create_parser.set_defaults(command=create)

    switch_parser = commands.add_parser("switch", help=switch.__doc__)
    switch_parser.add_argument("name")
    switch_parser.set_defaults(command=switch)

    state_parser = commands.add_parser("state", help=state.__doc__)
    state_parser.set_defaults(command=state)


def cli(args: list[str] | None = None) -> None:
    parser = ArgumentParser(name, usage, description, epilog)
    parser.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        dest="quietness",
        help="Use quiet output",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        dest="verbosity",
        help="Use verbose output",
    )

    register_commands(parser)

    parsed = parser.parse_args(args)
    config = load_config()

    try:
        parsed.command(parsed, config)
    except CommandError as exc:
        exc.log()
