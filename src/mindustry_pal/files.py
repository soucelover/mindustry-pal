import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from mindustry_pal.os_utils import GAME_DATA_DIRECTORY

if TYPE_CHECKING:
    import zipfile
    from collections.abc import Iterator


def resolve_path(path: Path) -> Path:
    if not path.is_absolute():
        path = Path("campaigns") / path

    if path.suffix != ".zip":
        path = path.with_suffix(path.suffix + ".zip")

    return path.resolve()


def clear_folder(folder: Path) -> None:
    for path in folder.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


@dataclass(slots=True)
class _StoreToZipFrame:
    def __init__(self, iterable: Iterator[Path]) -> None:
        self.iterable = iterable

    iterable: Iterator[Path]
    file: Path


def store_to_zip(zfile: zipfile.ZipFile) -> None:
    stack = [_StoreToZipFrame(GAME_DATA_DIRECTORY.iterdir())]

    while stack:
        last = stack[-1]

        try:
            last.file = next(last.iterable)
        except StopIteration:
            del stack[-1]
            continue

        if last.file.is_dir():
            stack.append(_StoreToZipFrame(last.file.iterdir()))
            zfile.mkdir(str(last.file.relative_to(GAME_DATA_DIRECTORY)))
        else:
            zfile.write(
                last.file, str(last.file.relative_to(GAME_DATA_DIRECTORY))
            )


def restore_zip(zrestore: zipfile.ZipFile) -> None:
    clear_folder(GAME_DATA_DIRECTORY)
    zrestore.extractall(GAME_DATA_DIRECTORY)
