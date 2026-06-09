"""Utilities and classes for command line interface of Mindustry-Pal."""

from .errors import CommandError
from .parser import cli

__all__ = ["CommandError", "cli"]
