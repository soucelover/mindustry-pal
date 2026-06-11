"""Base utilities for commands creation."""

from argparse import Namespace
from collections.abc import Callable
from functools import wraps

from mindustry_pal import CampaignHelper, PalConfig

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
