from argparse import ArgumentParser
from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol

from .campaigns import create, restore, state, store, switch
from .config import load_config
from .errors import CommandError
from .logging import set_logging_level

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import Sequence

    from .config import PalConfig

name = "manage.py"
usage = None
description = "Manager made for mindustry game."
epilog = "epi"


class SubParsersAction[ArgumentParserT: ArgumentParser](Protocol):
    """A protocol providing types of `argparse._SubParsersAction`."""

    def add_parser(
        self,
        name: str,
        *,
        help: str | None = ...,  # noqa: A002
        aliases: Sequence[str] = ...,
    ) -> ArgumentParserT: ...


type CommandFunction = Callable[[Namespace, PalConfig], None]


def add_command(
    commands: SubParsersAction[ArgumentParser],
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
    if aliases is None:
        parser = commands.add_parser(name, help=function.__doc__)
    else:
        parser = commands.add_parser(
            name, help=function.__doc__, aliases=aliases
        )

    parser.set_defaults(command=function)
    return parser


def register_commands(parser: ArgumentParser) -> None:
    """Register all CLI commands of Mindustry-Pal.

    Args:
        parser: Main argument parser.
    """
    commands = parser.add_subparsers(metavar="command", required=True)

    store_parser = add_command(commands, "store", store)
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
