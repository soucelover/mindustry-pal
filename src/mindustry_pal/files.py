import logging
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import zipfile


logger = logging.getLogger(__name__)


def _clear_folder(folder: Path) -> None:
    """Remove all entries inside directory and leave it empty.

    Args:
        folder: Path to the folder.
    """
    for path in folder.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def add_to_zip(zfile: zipfile.ZipFile, entry: Path, base: Path) -> None:
    """Add a file or directory to the specified `.zip` file.

    Args:
        zfile: A `.zip` file abstraction new entry is to be added to.
        entry: A file or directory to be added to the `.zip` file.
        base: Base path relative to which new entry's internal name is
            chosen.
    """
    if entry.is_file():
        zfile.write(entry, entry.relative_to(base))
    elif entry.is_dir():
        for subdir, _dirnames, files in os.walk(entry):
            folder = Path(subdir)

            if folder != base:
                zfile.mkdir(str(folder.relative_to(base)))

            for filename in files:
                filepath = folder / filename

                zfile.write(filepath, filepath.relative_to(base))


def restore_from_zip(zfile: zipfile.ZipFile, entry: str, base: Path) -> None:
    """Restore folder or file from `.zip` file.

    Clears destination folder or removes the file before extracting if
    one exists.

    Args:
        zfile: A `.zip` file abstraction entries are restored from.
        entry: A file or directory to be restored from `.zip` file.
        base: Base folder which entries will be extracted into.
    """
    path = base / entry

    if path.exists():
        if path.is_dir():
            _clear_folder(path)
            logger.debug("Cleared existing folder %s", path)
        else:
            path.unlink()
            logger.debug("Removed existing file %s", path)

    members = [
        member for member in zfile.namelist() if member.startswith(entry)
    ]
    zfile.extractall(base, members)
    logger.debug("Restored %s from a `.zip` file.", path)
