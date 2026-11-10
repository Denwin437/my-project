"""Core logic: planning, executing and undoing file moves."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

JOURNAL_NAME = ".file-organizer-journal.json"
OTHER = "Other"

CATEGORIES: dict[str, set[str]] = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".heic"},
    "Documents": {
        ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md",
        ".ppt", ".pptx", ".xls", ".xlsx", ".csv",
    },
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Video": {".mp4", ".mkv", ".mov", ".avi", ".webm", ".wmv"},
    "Archives": {".zip", ".tar", ".gz", ".bz2", ".7z", ".rar", ".xz"},
    "Code": {
        ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".go",
        ".rs", ".html", ".css", ".json", ".sh",
    },
    "Installers": {".exe", ".msi", ".dmg", ".deb", ".apk"},
}

_DATE_DIR = re.compile(r"^\d{4}-\d{2}$")
MODES = ("type", "date")


@dataclass(frozen=True)
class Move:
    src: Path
    dst: Path


def category_for(path: Path) -> str:
    """Return the category folder name for a file, based on its extension."""
    suffix = path.suffix.lower()
    for name, extensions in CATEGORIES.items():
        if suffix in extensions:
            return name
    return OTHER


def _is_managed(name: str, mode: str) -> bool:
    """True if a top-level folder name is one this tool creates."""
    if mode == "type":
        return name in CATEGORIES or name == OTHER
    return bool(_DATE_DIR.match(name))


def _folder_for(path: Path, mode: str) -> str:
    if mode == "type":
        return category_for(path)
    return dt.datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m")


def _unique(dst: Path, reserved: set[Path]) -> Path:
    """Return dst, or 'name (n).ext' if it already exists or is reserved."""
    if not dst.exists() and dst not in reserved:
        return dst
    n = 1
    while True:
        candidate = dst.with_name(f"{dst.stem} ({n}){dst.suffix}")
        if not candidate.exists() and candidate not in reserved:
            return candidate
        n += 1


def _walk(directory: Path, include_hidden: bool) -> Iterator[Path]:
    for root, dirs, files in os.walk(directory):
        if not include_hidden:
            dirs[:] = [d for d in dirs if not d.startswith(".")]
        dirs[:] = [d for d in dirs if not (Path(root) / d).is_symlink()]
        for name in files:
            if not include_hidden and name.startswith("."):
                continue
            path = Path(root) / name
            if not path.is_symlink():
                yield path


def _iter_files(source: Path, mode: str, recursive: bool, include_hidden: bool) -> Iterator[Path]:
    for entry in source.iterdir():
        if entry.name == JOURNAL_NAME or entry.is_symlink():
            continue
        if not include_hidden and entry.name.startswith("."):
            continue
        if entry.is_file():
            yield entry
        elif entry.is_dir() and recursive and not _is_managed(entry.name, mode):
            yield from _walk(entry, include_hidden)


def plan(
    source: str | Path,
    mode: str = "type",
    recursive: bool = False,
    include_hidden: bool = False,
) -> list[Move]:
    """Work out which files would move where, without touching anything."""
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    root = Path(source).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"not a directory: {source}")

    moves: list[Move] = []
    reserved: set[Path] = set()
    for file in sorted(_iter_files(root, mode, recursive, include_hidden)):
        dest_dir = root / _folder_for(file, mode)
        if file.parent == dest_dir:
            continue
        dst = _unique(dest_dir / file.name, reserved)
        reserved.add(dst)
        moves.append(Move(file, dst))
    return moves


def _journal_path(root: Path) -> Path:
    return root / JOURNAL_NAME


def _load_journal(root: Path) -> dict:
    path = _journal_path(root)
    if not path.exists():
        return {"runs": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"journal is corrupt: {path}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("runs"), list):
        raise ValueError(f"journal is corrupt: {path}")
    return data


def _save_journal(root: Path, data: dict) -> None:
    path = _journal_path(root)
    if data["runs"]:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    elif path.exists():
        path.unlink()


def execute(moves: list[Move], source: str | Path) -> list[Move]:
    """Perform the moves and record them so they can be undone."""
    root = Path(source).resolve()
    done: list[Move] = []
    for move in moves:
        move.dst.parent.mkdir(parents=True, exist_ok=True)
        dst = _unique(move.dst, set()) if move.dst.exists() else move.dst
        shutil.move(str(move.src), str(dst))
        done.append(Move(move.src, dst))

    if done:
        journal = _load_journal(root)
        journal["runs"].append(
            {
                "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
                "moves": [
                    {"src": m.src.relative_to(root).as_posix(), "dst": m.dst.relative_to(root).as_posix()}
                    for m in done
                ],
            }
        )
        _save_journal(root, journal)
    return done


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root)
        return True
    except ValueError:
        return False


def undo(source: str | Path) -> tuple[list[Move], list[str]]:
    """Reverse the most recent run. Returns (restored moves, skipped messages)."""
    root = Path(source).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"not a directory: {source}")

    journal = _load_journal(root)
    if not journal["runs"]:
        return [], []

    run = journal["runs"].pop()
    restored: list[Move] = []
    skipped: list[str] = []
    for entry in reversed(run["moves"]):
        src = root / entry["src"]
        dst = root / entry["dst"]
        if not (_inside(root, src) and _inside(root, dst)):
            skipped.append(f"refused path outside folder: {entry['dst']}")
            continue
        if not dst.exists():
            skipped.append(f"missing, cannot restore: {entry['dst']}")
            continue
        src.parent.mkdir(parents=True, exist_ok=True)
        target = _unique(src, set()) if src.exists() else src
        shutil.move(str(dst), str(target))
        restored.append(Move(dst, target))
        _prune_empty(dst.parent, root)

    _save_journal(root, journal)
    return restored, skipped


def _prune_empty(directory: Path, root: Path) -> None:
    """Remove directory (and empty parents) up to, but not including, root."""
    while directory != root and _inside(root, directory):
        try:
            directory.rmdir()
        except OSError:
            return
        directory = directory.parent
