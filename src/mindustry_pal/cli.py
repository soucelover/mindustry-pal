from argparse import ArgumentParser
from typing import TYPE_CHECKING

from mindustry_pal.config import load_config
from mindustry_pal.errors import CommandError
from mindustry_pal.logging import set_logging_level

from .campaigns import create, restore, state, store, switch

if TYPE_CHECKING:
    from argparse import Namespace

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


def process_logging_parameters(args: Namespace) -> None:
    verbosity: int = args.verbosity
    quietness: int = args.quietness

    if verbosity != 0 and quietness != 0:
        msg = "The argument '--quiet...' cannot be used with '--verbose...'"
        raise CommandError(msg)

    set_logging_level(verbosity, quietness)


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

    try:
        process_logging_parameters(parsed)

        config = load_config()
        parsed.command(parsed, config)
    except CommandError as exc:
        exc.log()
