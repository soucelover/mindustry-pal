"""Logical errors classes for CLI commands."""

import logging

logger = logging.getLogger()


class CommandError(Exception):
    """An expected logical error raised by CLI command.

    Such errors should be logged without traceback.
    """

    def format_message(self) -> str:
        """Format errors message."""
        msg = str(self)

        if type(self) is not CommandError:
            msg = f"{type(self).__name__}: {msg}"

        return msg

    def log(self) -> None:
        """Log error onto the screen."""
        logger.error(self.format_message())
