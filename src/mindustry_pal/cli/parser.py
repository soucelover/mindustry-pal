"""Main `ArgumentParser` of the CLI."""

import inspect
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import TYPE_CHECKING

import mindustry_pal
from mindustry_pal.campaigns import create, restore, state, switch
from mindustry_pal.cli.commands import store_command
from mindustry_pal.config import load_config
from mindustry_pal.logging import set_logging_level

from .errors import CommandError

if TYPE_CHECKING:
    from argparse import (
        Namespace,
        _SubParsersAction,  # pyright: ignore[reportPrivateUsage]
    )
    from collections.abc import Sequence

    from .base import CommandFunction


def add_command(
    commands: _SubParsersAction[ArgumentParser],
    name: str,
    function: CommandFunction,
    *,
    aliases: Sequence[str] | None = None,
) -> ArgumentParser:
    """Register a single command in `SubParsersAction`.

    Args:
        commands: `ArgumentParser`'s action representing commands
        name: Name for the command.
        function: Function implementing command and containing its docstrings.
        aliases: Optional list of aliases for the command.

    Returns:
        A newly created parser of the command.
    """
    description = inspect.getdoc(function)

    if description is not None:
        first_line = description.split("\n", maxsplit=1)[0]
    else:
        first_line = None

    if aliases is None:
        parser = commands.add_parser(
            name,
            help=first_line,
            description=description,
            formatter_class=RawDescriptionHelpFormatter,
        )
    else:
        parser = commands.add_parser(
            name,
            help=first_line,
            description=description,
            formatter_class=RawDescriptionHelpFormatter,
            aliases=aliases,
        )

    parser.set_defaults(command=function)
    return parser


def register_commands(parser: ArgumentParser) -> None:
    """Register all CLI commands of Mindustry-Pal.

    Args:
        parser: Main argument parser.
    """
    commands = parser.add_subparsers(metavar="command", required=True)

    store_parser = add_command(commands, "store", store_command)
    store_parser.add_argument("name", nargs="?", help="Name of campaign")

    restore_parser = add_command(commands, "restore", restore)
    restore_parser.add_argument("name", nargs="?", help="Name of campaign")

    create_parser = add_command(commands, "create", create)
    create_parser.add_argument("name", help="Name of new campaign")

    switch_parser = add_command(commands, "switch", switch)
    switch_parser.add_argument("name")

    add_command(commands, "state", state)


def process_logging_parameters(args: Namespace) -> None:
    verbosity: int = args.verbosity
    quietness: int = args.quietness

    if verbosity != 0 and quietness != 0:
        msg = "The argument '--quiet...' cannot be used with '--verbose...'"
        raise CommandError(msg)

    set_logging_level(verbosity, quietness)


def cli(args: list[str] | None = None) -> None:
    body = inspect.getdoc(mindustry_pal)
    parser = ArgumentParser(
        description=body, formatter_class=RawDescriptionHelpFormatter
    )
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
