"""CLI commands definitions."""

import logging
from typing import TYPE_CHECKING, override

from mindustry_pal.campaigns import CurrentCampaignNotSetError

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
    """Store (dump) current Mindustry campaign in a file."""
    name: str | None = args.name

    try:
        campaign = helper.get_campaign(name)
    except CurrentCampaignNotSetError as exc:
        msg = (
            "Campaign hasn't been stored before, so you have to "
            "specify a name for a new campaign."
        )
        raise StoreCommandError(msg) from exc

    helper.store(campaign)
    helper.set_current_campaign(campaign)
    logger.info("Successfully store campaign in a file.")
    logger.info("  Path: %s", campaign)
