import logging
import sys
from typing import ClassVar, override

from termcolor import colored

__all__ = [
    "ColoredFormatter",
    "MaxLevelFilter",
    "set_logging_level",
    "setup_logging",
]


class MaxLevelFilter(logging.Filter):
    def __init__(self, level: int) -> None:
        super().__init__()
        self.level: int = level

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < self.level


class ColoredFormatter(logging.Formatter):
    table: ClassVar[dict[int, str]] = {
        logging.DEBUG: colored("debug:", "blue"),
        logging.WARNING: colored("warning:", "yellow"),
        logging.ERROR: colored("error:", "red"),
        logging.CRITICAL: colored("critical:", "red"),
    }

    def __init__(self) -> None:
        super().__init__("%(message)s")

    @override
    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)

        if record.levelno in self.table:
            prefix = self.table[record.levelno]
            return f"{prefix} {formatted}"

        return formatted


def setup_logging() -> None:
    # Could use .yaml/.ini files but won't, it's easier
    root_handler = logging.getLogger()
    root_handler.setLevel(logging.NOTSET)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.NOTSET)
    stdout_handler.addFilter(MaxLevelFilter(logging.WARNING))

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)

    fmt = ColoredFormatter()
    stdout_handler.setFormatter(fmt)
    stderr_handler.setFormatter(fmt)

    root_handler.addHandler(stdout_handler)
    root_handler.addHandler(stderr_handler)


LOGGING_LEVELS: dict[int, int | None] = {
    -2: logging.NOTSET,
    -1: logging.DEBUG,
    0: logging.INFO,
    1: logging.WARNING,
    2: logging.ERROR,
    3: None,
}


def set_logging_level(verbosity: int, quietness: int) -> None:
    lvl_index = max(min(quietness - verbosity, 3), -2)

    level = LOGGING_LEVELS[lvl_index]
    root_logger = logging.getLogger()

    if level is None:
        root_logger.disabled = True
    else:
        root_logger.setLevel(level)
