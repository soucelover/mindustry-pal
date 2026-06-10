"""Mindustry-Pal configuration class."""

from pathlib import Path
from typing import ClassVar, Self

from pydantic import BaseModel, ConfigDict, DirectoryPath, Field

from mindustry_pal.os_utils import GAME_DATA_DIRECTORY, PAL_DIRECTORY


class PalConfig(BaseModel):
    """Mindustry-Pal configuration class."""

    versions_dir: DirectoryPath | None = Field(
        default=None, alias="versions-dir"
    )
    campaigns_dir: DirectoryPath | None = Field(
        default=None, alias="campaigns-dir"
    )
    current_campaign: str | None = Field(
        default=None, alias="current-campaign"
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
            return cls()

        content = cls.config_file.read_text(encoding="utf-8")
        return cls.model_validate_json(content)

    def save(self) -> None:
        """Save current configuration to a file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.touch()

        content = self.model_dump_json(indent=4, exclude_unset=True)
        self.config_file.write_text(content, encoding="utf-8")


def load_config() -> PalConfig:
    config_file = PAL_DIRECTORY / "config.json"

    if not config_file.is_file():
        return PalConfig()

    return PalConfig.model_validate_json(
        config_file.read_text(encoding="utf-8")
    )


def dump_config(config: PalConfig) -> None:
    config_file = PAL_DIRECTORY / "config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    content = config.model_dump_json()
    config_file.write_text(content, encoding="utf-8")
