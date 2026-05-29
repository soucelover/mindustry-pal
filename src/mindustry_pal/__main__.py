import contextlib
import logging
import sys
from typing import TYPE_CHECKING

from .cli import cli
from .logging import setup_logging

if TYPE_CHECKING:
    from types import TracebackType


logger = logging.getLogger(__name__)


def _strip_traceback(
    exc_traceback: TracebackType | None,
) -> TracebackType | None:
    if exc_traceback is None:
        return None

    tb: TracebackType | None = exc_traceback

    while tb is not None:
        if tb.tb_frame.f_code is main.__code__:
            return tb

        tb = tb.tb_next

    return exc_traceback


def handle_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    msg = "Unexpected error"
    logger.critical(
        msg, exc_info=(exc_type, exc_value, _strip_traceback(exc_traceback))
    )


def main() -> None:
    sys.excepthook = handle_exception

    with contextlib.suppress(KeyboardInterrupt):
        setup_logging()
        cli()


if __name__ == "__main__":
    main()
