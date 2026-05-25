import os
import platform
from functools import lru_cache
from pathlib import Path


def get_app_data_directory_string(appname: str) -> Path:
    os_name = platform.system()

    match os_name:
        case "Windows":
            appdata = os.getenv("APPDATA")

            if appdata is None:
                msg = "Missing OS-provided environment variable APPDATA"
                raise RuntimeError(msg)

            return Path(appdata) / appname
        case "Android" | "iOS":
            raise NotImplementedError
        case "Linux":
            xdg_data_home = os.getenv("XDG_DATA_HOME")

            if xdg_data_home is not None:
                return Path(xdg_data_home) / appname

            return Path.home() / ".local/share" / appname
        case "Darwin":
            return Path.home() / "Library/Application Support" / appname
        case _:
            msg = f"Operating System {os_name} is not supported"
            raise RuntimeError(msg)


@lru_cache
def get_data_directory() -> Path:
    return get_app_data_directory_string("Mindustry").absolute()


DATA_DIRECTORY = get_data_directory()
