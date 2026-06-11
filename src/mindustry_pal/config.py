"""Mindustry-Pal configuration class."""

import logging
from pathlib import Path
from typing import ClassVar, Self

from pydantic import ConfigDict, DirectoryPath, Field
from pydantic_changedetect import ChangeDetectionMixin

from mindustry_pal.os_utils import GAME_DATA_DIRECTORY, PAL_DIRECTORY

logger = logging.getLogger(__name__)


class PalConfig(ChangeDetectionMixin):
    """Mindustry-Pal configuration class."""

    versions_dir: DirectoryPath | None = Field(
        default=None, alias="versions-dir", serialization_alias="versions-dir"
    )
    campaigns_dir: DirectoryPath | None = Field(
        default=None,
        alias="campaigns-dir",
        serialization_alias="campaigns-dir",
    )
    current_campaign: str | None = Field(
        default=None,
        alias="current-campaign",
        serialization_alias="current-campaign",
    )

    def get_versions_dir(self) -> Path:
        """Get path to a directory containing Mindustry versions."""
        if self.versions_dir is not None:
            return self.versions_dir

        return GAME_DATA_DIRECTORY / "versions"

    def get_campaigns_dir(self) -> Path:
        """Get path to a directory containing campaign storage files."""
        if self.campaigns_dir is not None:
            return self.campaigns_dir

        return PAL_DIRECTORY / "campaigns"

    model_config = ConfigDict(serialize_by_alias=True)

    config_file: ClassVar[Path] = PAL_DIRECTORY / "config.json"

    @classmethod
    def load(cls) -> Self:
        """Load Mindustry-Pal configuration from file on disk.

        Uses `<app-directory>/config.json` to load configuration.

        Returns:
            Configuration object.
        """
        if not cls.config_file.is_file():
            logger.debug(
                "Configuration file is missing; returning empty config."
            )
            return cls()

        content = cls.config_file.read_text(encoding="utf-8")
        config = cls.model_validate_json(content)
        logger.debug("Loaded configuration from %s", cls.config_file)

        return config

    def save(self, *, if_changed: bool = True) -> None:
        """Save current configuration to a file.

        Args:
            if_changed: If true, then saves only if configuration was
                changed. Otherwise saves regardless of configuration
                or file state.
        """
        if if_changed is True and not self.model_has_changed:
            logger.debug(
                "Skipped saving configuration: it hasn't changed in this run"
            )
            return

        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.touch()

        content = self.model_dump_json(indent=4, exclude_unset=True)
        length = self.config_file.write_text(content, encoding="utf-8")
        logger.debug(
            "Written %i characters to %s (configuration file)",
            length,
            self.config_file,
        )
