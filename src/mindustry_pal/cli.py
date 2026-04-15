from argparse import ArgumentParser

from .campaigns import create, restore, state, store, switch

name = "manage.py"
usage = None
description = "Manager made for mindustry game."
epilog = "epi"


def cli(args: list[str] | None = None) -> None:
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
