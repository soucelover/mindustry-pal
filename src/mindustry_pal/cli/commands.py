"""CLI commands definitions."""

import logging
from textwrap import dedent
from typing import TYPE_CHECKING, override

from mindustry_pal import CampaignDoesntExistError, CurrentCampaignNotSetError
from mindustry_pal.cli.base import prompt_yes_no

from .base import campaign_dependency
from .errors import CommandError

if TYPE_CHECKING:
    from argparse import Namespace

    from mindustry_pal import CampaignHelper


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
    current_campaign: bool = args.current_campaign

    if name is not None and current_campaign is True:
        msg = "'--current-campaign' cannot be specified along with 'name'."
        raise CommandError(msg)

    try:
        campaign = helper.get_campaign(name)
    except CurrentCampaignNotSetError as exc:
        if current_campaign is True:
            msg = (
                "Mindustry campaign hasn't been stored before, so you have "
                "to specify a name for a new campaign."
            )
            raise StoreCommandError(msg) from exc

        msg = dedent("""\
            i Mindustry campaign hasn't been stored before, so we need to create
              a new campaign storage.
            ? How would you name it? Leave empty if you don't want to proceed.
            > """)  # noqa: E501
        name = input(msg)

        if not name:
            return

        campaign = helper.get_campaign(name)

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
                i Campaign storage with name '{name}' already exists and thereby
                  will be overwritten.
                ? Do you want to proceed?
                > [y/N] """)  # noqa: E501
            proceed = prompt_yes_no(prompt, default=False)

            if proceed is False:
                return

    helper.store(campaign)
    helper.set_current_campaign(campaign)
    logger.info("Successfully stored campaign in a file.")
    logger.info("  Path: %s", campaign)


class RestoreCommandError(CommandError):
    """Error during `restore` command."""

    @override
    def format_message(self) -> str:
        return f"Failed to restore campaign: {self!s}"


@campaign_dependency
def restore_command(args: Namespace, helper: CampaignHelper) -> None:
    """Restore (load) Mindustry campaign from a file.

    Replaces current files with those from stored Mindustry campaign.
    """
    name: str | None = args.name

    try:
        campaign = helper.get_campaign(name)
        # TODO(@soucelover): Add check_exists=True
    except CurrentCampaignNotSetError as exc:
        msg = (
            "Campaign hasn't been stored before, so you have to "
            "specify a name or store current campaign first."
        )
        raise RestoreCommandError(msg) from exc

    helper.restore(campaign)
    helper.set_current_campaign(campaign)
    logger.info("Successfully restored campaign from the file.")


class CreateCommandError(CommandError):
    """Error during `create` command."""

    @override
    def format_message(self) -> str:
        return f"Failed to create a new campaign: {self!s}"


@campaign_dependency
def create_command(args: Namespace, helper: CampaignHelper) -> None:
    """Create a new empty Mindustry campaign and switch to it."""
    name: str = args.name

    try:
        current_campaign = helper.get_campaign()
    except CurrentCampaignNotSetError as exc:
        msg = "You should store current campaign before creating a new one."
        raise CreateCommandError(msg) from exc

    new_campaign = helper.get_campaign(name)

    if new_campaign.exists:
        msg = "Campaign with this name already exists"
        raise CreateCommandError(msg)

    helper.store(current_campaign)
    logger.info(
        "Current campaign (%s) was stored to a file", current_campaign.name
    )

    helper.create(new_campaign)
    helper.restore(new_campaign)
    helper.set_current_campaign(new_campaign)
    logger.info("Successfully created new empty campaign and switched to it.")
    logger.info("  Path: %s", new_campaign)


class SwitchCommandError(CommandError):
    """Error during `switch` command."""

    @override
    def format_message(self) -> str:
        return f"Failed to switch to another campaign: {self!s}"


@campaign_dependency
def switch_command(args: Namespace, helper: CampaignHelper) -> None:
    """Switch between Mindustry campaigns."""
    name: str = args.name

    try:
        current_campaign = helper.get_campaign()
    except CurrentCampaignNotSetError as exc:
        msg = "You must store current campaign before switching to another."
        raise SwitchCommandError(msg) from exc

    try:
        restore_campaign = helper.get_campaign(name, check_exists=True)
    except CampaignDoesntExistError as exc:
        msg = f"Campaign file for {exc.campaign.name} doesn't exist on disk"
        raise SwitchCommandError(msg) from exc

    if restore_campaign == current_campaign:
        logger.info("Already on campaign '%s'", current_campaign.name)
        return

    helper.store(current_campaign)
    logger.info(
        "Current campaign (%s) was stored to a file", current_campaign.name
    )

    helper.restore(restore_campaign)
    helper.set_current_campaign(restore_campaign)
    logger.info(
        "Successfully switched to campaign '%s'.", restore_campaign.name
    )


@campaign_dependency
def status_command(args: Namespace, helper: CampaignHelper) -> None:
    """Get status for the state of current campaign."""
    try:
        current_campaign = helper.get_campaign(check_exists=True)
    except CurrentCampaignNotSetError:
        msg = dedent("""\
            Campaign hasn't been stored yet.
            Use `mindustry-pal store` to store current campaign to a file.
        """)
        logger.info(msg)
    except CampaignDoesntExistError as exc:
        msg = dedent("""\
            Current campaign is '%s' but storage file doesn't exist on disk.
            Use `mindustry-pal store` to store current campaign to a file.
        """)
        logger.info(msg, exc.campaign.name)
    else:
        msg = dedent("""\
            Current campaign is '%s'

              Path: %s
              Size: %s
              Timestamp: %s
        """)
        logger.info(
            msg,
            current_campaign.name,
            current_campaign,
            current_campaign.size_str,
            current_campaign.timestamp,
        )


@campaign_dependency
def list_command(args: Namespace, helper: CampaignHelper) -> None:
    """Get the list of all stored campaigns."""
    campaigns = helper.list_campaigns()

    for campaign in campaigns:
        is_current = helper.is_current_campaign(campaign)

        if is_current:
            logger.info("%s (current)", campaign.name)
        else:
            logger.info(campaign.name)
