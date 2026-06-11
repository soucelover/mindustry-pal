"""Base utilities for commands creation."""

from argparse import Namespace
from collections.abc import Callable
from functools import wraps
from typing import overload

from mindustry_pal import CampaignHelper, PalConfig

YES_ANSWERS = ("Y", "YES")
NO_ANSWERS = ("N", "NO")


@overload
def prompt_yes_no(prompt: str, *, default: None = None) -> bool | None: ...
@overload
def prompt_yes_no(prompt: str, *, default: bool) -> bool: ...


def prompt_yes_no(prompt: str, *, default: bool | None = None) -> bool | None:
    """Prompt a `[Y/n]` question to the user.

    Args:
        prompt: Initial displayed prompt.
        default: Default value if user specified invalid input.

    Returns:
        User's answer, or default value, or `None`.
    """
    answer = input(prompt).upper()

    if answer in YES_ANSWERS:
        return True
    if answer in NO_ANSWERS:
        return False

    return default


type CampaignCommand = Callable[[Namespace, CampaignHelper], None]
type CommandFunction = Callable[[Namespace, PalConfig], None]


def campaign_dependency(function: CampaignCommand) -> CommandFunction:
    """A wrapper injecting `CampaignHelper` dependency into command.

    Note:
        It's not a good way of dependency inversion even if it is
        dependency injection.

    Args:
        function: Command demanding `CampaignHelper`.

    Returns:
        Function ready to use for command registration.
    """

    @wraps(function)
    def wrapper(args: Namespace, config: PalConfig) -> None:
        helper = CampaignHelper(config)

        return function(args, helper)

    return wrapper
