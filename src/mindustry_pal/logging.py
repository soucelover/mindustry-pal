import logging
import sys


class MaxLevelFilter(logging.Filter):
    def __init__(self, level: int) -> None:
        super().__init__()
        self.level: int = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < self.level


def setup_logging() -> None:
    # Could use .yaml/.ini files but won't, it's easier
    root_handler = logging.getLogger()
    root_handler.setLevel(logging.NOTSET)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.NOTSET)
    stdout_handler.addFilter(MaxLevelFilter(logging.WARNING))

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)

    fmt = logging.Formatter("%(levelname)s: %(message)s")
    stdout_handler.setFormatter(fmt)
    stderr_handler.setFormatter(fmt)

    root_handler.addHandler(stdout_handler)
    root_handler.addHandler(stderr_handler)
