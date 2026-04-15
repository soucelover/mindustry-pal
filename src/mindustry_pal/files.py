import json
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from mindustry_pal.campaigns import mindustry_dir

if TYPE_CHECKING:
    import zipfile


def resolve_path(path: Path) -> Path:
    if not path.is_absolute():
        path = Path("campaigns") / path

    if path.suffix != ".zip":
        path = path.with_suffix(path.suffix + ".zip")

    return path.resolve()


def clear_folder(path: Path) -> None:
    for path in path.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def store_to_zip(zfile: zipfile.ZipFile) -> None:
    class Frame:
        def __init__(self, iter):
            self.iter = iter

        iter = None
        file = None

    stack = [Frame(mindustry_dir.iterdir())]

    while stack:
        last = stack[-1]

        try:
            last.file = last.iter.__next__()
        except StopIteration:
            del stack[-1]
            continue

        if last.file.is_dir():
            stack.append(Frame(last.file.iterdir()))
            zfile.mkdir(str(last.file.relative_to(mindustry_dir)))
        else:
            zfile.write(last.file, str(last.file.relative_to(mindustry_dir)))


def restore_zip(zrestore: zipfile.ZipFile) -> None:
    clear_folder(mindustry_dir)
    zrestore.extractall(mindustry_dir)


def load_cfg() -> dict:
    Path("config.json").touch()

    with open("config.json") as f:
        cfg = json.load(f)

    if not isinstance(cfg, dict):
        return {}

    return cfg


def dump_cfg(cfg: dict) -> None:
    if not isinstance(cfg, dict):
        cfg = {}

    Path("config.json").touch()

    with open("config.json", "w") as f:
        json.dump(cfg, f)
