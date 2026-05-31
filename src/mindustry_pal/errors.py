import logging

logger = logging.getLogger()


class CommandError(Exception):
    """An expected logical error raised by CLI command.

    Such errors should be logged without traceback.
    """

    def log(self) -> None:
        msg = str(self)

        if type(self) is not CommandError:
            msg = f"{type(self).__name__}: {msg}"

        logger.error(msg)
