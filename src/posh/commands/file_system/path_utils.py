from functools import cache
from os import stat
from pathlib import Path
from re import Pattern
from shutil import copy2, copytree
from stat import FILE_ATTRIBUTE_HIDDEN
from sys import platform

from ...colours import TextStyle, add_styles


@cache
def check_path(path: Path, cwd: Path) -> Path | None:
    """
    Check if a path exists, if not try to prefix ith with the current working directory.
    If the path still doesn't exist return None, otherwise return the path.
    """
    if not path.exists():
        if not (prefixed_path := cwd / path).exists():
            return None
        return prefixed_path
    return path


@cache
def parse_path(path: str | Path, cwd: Path) -> Path:
    """
    Take a str or pathlib.Path and and return a pathlib.Path
    where all special characters are expanded.
    """
    if isinstance(path, Path):
        path = path.as_posix()

    if path[0] == "." and len(path) == 1:
        return cwd
    if path[0] == "/":
        if len(path) == 1:
            return Path(Path.home().anchor)
        path = Path(Path.home().anchor).as_posix() + path[1:]

    new_path = list[str]()
    for part in Path(path).parts:
        if part == "~":
            new_path.extend(Path.home().parts)
        elif part == "..":
            if new_path:
                new_path.pop()
            else:
                new_path.extend(cwd.parent.parts)
        elif part == ".":
            continue
        else:
            new_path.append(part)
    return Path(*new_path)


def is_hidden(path: Path) -> bool:
    if platform.startswith("win"):
        return bool(stat(path).st_file_attributes & FILE_ATTRIBUTE_HIDDEN)
    return path.name.startswith(".")


def check_ignore(
    path: Path, ignores: list[str], ignore_patterns: list[Pattern[str]]
) -> bool:
    return any(ignore in path.parts for ignore in ignores) or any(
        pattern.fullmatch(path.as_posix()) for pattern in ignore_patterns
    )


def backup(path: Path, err_style: TextStyle) -> None:
    backup_path = Path(f"{path.as_posix()}.backup")

    i = 1
    while backup_path.exists():
        backup_path = Path(f"{backup_path.as_posix()}_{i}")

    try:
        if path.is_dir():
            copytree(path, backup_path)
        else:
            copy2(path, backup_path)
    except OSError as err:
        print(add_styles(f"Error: failed to create backup, {err}", err_style))
