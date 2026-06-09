"""CLI commands definitions."""

import logging
from textwrap import dedent
from typing import TYPE_CHECKING, override

from mindustry_pal.campaigns import CurrentCampaignNotSetError
from mindustry_pal.cli.base import prompt_yes_no

from .base import campaign_dependency
from .errors import CommandError

if TYPE_CHECKING:
    from argparse import Namespace

    from mindustry_pal.campaigns import CampaignHelper


logger = logging.getLogger(__name__)


class StoreCommandError(CommandError):
    """Error during `store` command."""

    @override
    def format_message(self) -> str:
        return f"Failed to store current campaign: {self!s}"


@campaign_dependency
def store_command(args: Namespace, helper: CampaignHelper) -> None:
    """Store (dump) current Mindustry campaign in a file.

    Stores the following files and folders from current Mindustry campaign:

     *  saves/
     *  mods/
     *  maps/
     *  schematics/
     *  settings.bin

    If corresponding options were not specified and your action is required,
    you will be prompted. Otherwise, command proceeds without terminal
    interactions.
    """
    name: str | None = args.name
    exists_ok: bool | None = args.exists_ok

    try:
        campaign = helper.get_campaign(name)
    except CurrentCampaignNotSetError as exc:
        msg = (
            "Campaign hasn't been stored before, so you have to "
            "specify a name for a new campaign."
        )
        raise StoreCommandError(msg) from exc

    if name is not None and not exists_ok and campaign.exists:
        if exists_ok is False:
            msg = dedent(f"""\
                Campaign storage
                with name '{name}' already exists.

                Tip: This error is shown because you've specified '--no-exists-ok'.
            """)  # noqa: E501
            raise StoreCommandError(msg)

        if exists_ok is None:
            prompt = dedent(f"""\
                i Campaign storage with name '{name}' already exists and thus
                  will be overwritten.
                ? Do you want to proceed?
                > [y/N] """)
            proceed = prompt_yes_no(prompt, default=False)

            if proceed is False:
                return

    helper.store(campaign)
    helper.set_current_campaign(campaign)
    logger.info("Successfully store campaign in a file.")
    logger.info("  Path: %s", campaign)
