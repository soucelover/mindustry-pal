from .cli import cli
from .logging import setup_logging


def main() -> None:
    setup_logging()
    cli()


if __name__ == "__main__":
    main()
