from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from mindustry_pal.os_utils import GAME_DATA_DIRECTORY, PAL_DIRECTORY

if TYPE_CHECKING:
    from pathlib import Path

    from pydantic import DirectoryPath


class PalConfig(BaseModel):
    versions_dir: DirectoryPath | None = Field(
        default=None, alias="versions-dir"
    )
    current_campaign: str | None = Field(
        default=None, alias="current-campaign"
    )

    def get_versions_dir(self) -> Path:
        if self.versions_dir is not None:
            return self.versions_dir

        return GAME_DATA_DIRECTORY / "versions"

    config = ConfigDict(serialize_by_alias=True)


def load_config() -> PalConfig:
    config_file = PAL_DIRECTORY / "config.json"

    if not config_file.is_file():
        return PalConfig()

    return PalConfig.model_validate_json(
        config_file.read_text(encoding="utf-8")
    )
