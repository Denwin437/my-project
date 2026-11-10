import json
import os
import time
from pathlib import Path

import pytest

from file_organizer import core
from file_organizer.cli import main


def touch(path: Path, text: str = "x", mtime: float | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


def names(root: Path) -> set[str]:
    files = (p for p in root.rglob("*") if p.is_file() and p.name != core.JOURNAL_NAME)
    return {p.relative_to(root).as_posix() for p in files}


# ---------- categorisation ----------

@pytest.mark.parametrize(
    "filename,expected",
    [
        ("a.JPG", "Images"),
        ("report.pdf", "Documents"),
        ("song.mp3", "Audio"),
        ("clip.mkv", "Video"),
        ("bundle.tar", "Archives"),
        ("script.py", "Code"),
        ("setup.exe", "Installers"),
        ("mystery.xyz", "Other"),
        ("Makefile", "Other"),
    ],
)
def test_category_for(filename, expected):
    assert core.category_for(Path(filename)) == expected


# ---------- planning ----------

def test_plan_does_not_touch_files(tmp_path):
    touch(tmp_path / "a.png")
    moves = core.plan(tmp_path)
    assert [m.dst.parent.name for m in moves] == ["Images"]
    assert (tmp_path / "a.png").exists()
    assert not (tmp_path / "Images").exists()


def test_plan_rejects_bad_input(tmp_path):
    with pytest.raises(NotADirectoryError):
        core.plan(tmp_path / "missing")
    with pytest.raises(ValueError):
        core.plan(tmp_path, mode="colour")


def test_hidden_files_skipped_by_default(tmp_path):
    touch(tmp_path / ".secret.txt")
    touch(tmp_path / "visible.txt")
    assert [m.src.name for m in core.plan(tmp_path)] == ["visible.txt"]
    assert {m.src.name for m in core.plan(tmp_path, include_hidden=True)} == {".secret.txt", "visible.txt"}


def test_symlinks_are_ignored(tmp_path):
    target = touch(tmp_path / "real.txt")
    (tmp_path / "link.txt").symlink_to(target)
    assert [m.src.name for m in core.plan(tmp_path)] == ["real.txt"]


# ---------- executing ----------

def test_organize_by_type(tmp_path):
    for name in ["a.png", "b.pdf", "c.mp3", "d.unknown"]:
        touch(tmp_path / name)
    done = core.execute(core.plan(tmp_path), tmp_path)
    assert len(done) == 4
    assert names(tmp_path) == {"Images/a.png", "Documents/b.pdf", "Audio/c.mp3", "Other/d.unknown"}


def test_existing_file_is_never_overwritten(tmp_path):
    touch(tmp_path / "Documents" / "notes.txt", "old")
    touch(tmp_path / "notes.txt", "new")
    core.execute(core.plan(tmp_path), tmp_path)
    assert (tmp_path / "Documents" / "notes.txt").read_text() == "old"
    assert (tmp_path / "Documents" / "notes (1).txt").read_text() == "new"


def test_same_name_in_two_subfolders_does_not_collide(tmp_path):
    touch(tmp_path / "one" / "photo.png", "1")
    touch(tmp_path / "two" / "photo.png", "2")
    core.execute(core.plan(tmp_path, recursive=True), tmp_path)
    assert {p.read_text() for p in (tmp_path / "Images").iterdir()} == {"1", "2"}
    assert len(list((tmp_path / "Images").iterdir())) == 2


def test_non_recursive_leaves_subfolders_alone(tmp_path):
    touch(tmp_path / "sub" / "deep.png")
    touch(tmp_path / "top.png")
    core.execute(core.plan(tmp_path), tmp_path)
    assert names(tmp_path) == {"sub/deep.png", "Images/top.png"}


def test_running_twice_is_idempotent(tmp_path):
    touch(tmp_path / "a.png")
    core.execute(core.plan(tmp_path, recursive=True), tmp_path)
    assert core.plan(tmp_path, recursive=True) == []


def test_organize_by_date(tmp_path):
    jan = time.mktime((2024, 1, 15, 12, 0, 0, 0, 0, -1))
    mar = time.mktime((2025, 3, 2, 12, 0, 0, 0, 0, -1))
    touch(tmp_path / "old.txt", mtime=jan)
    touch(tmp_path / "new.txt", mtime=mar)
    core.execute(core.plan(tmp_path, mode="date"), tmp_path)
    assert names(tmp_path) == {"2024-01/old.txt", "2025-03/new.txt"}


# ---------- undo ----------

def test_undo_restores_everything_and_removes_empty_folders(tmp_path):
    touch(tmp_path / "a.png", "A")
    touch(tmp_path / "sub" / "b.pdf", "B")
    before = names(tmp_path)
    core.execute(core.plan(tmp_path, recursive=True), tmp_path)
    restored, skipped = core.undo(tmp_path)
    assert len(restored) == 2 and skipped == []
    assert names(tmp_path) == before
    assert not (tmp_path / "Images").exists()
    assert not (tmp_path / "Documents").exists()
    assert not (tmp_path / core.JOURNAL_NAME).exists()


def test_undo_only_reverses_latest_run(tmp_path):
    touch(tmp_path / "a.png")
    core.execute(core.plan(tmp_path), tmp_path)
    touch(tmp_path / "b.pdf")
    core.execute(core.plan(tmp_path), tmp_path)
    core.undo(tmp_path)
    assert names(tmp_path) == {"Images/a.png", "b.pdf"}


def test_undo_with_nothing_recorded(tmp_path):
    assert core.undo(tmp_path) == ([], [])


def test_undo_reports_files_the_user_deleted(tmp_path):
    touch(tmp_path / "a.png")
    core.execute(core.plan(tmp_path), tmp_path)
    (tmp_path / "Images" / "a.png").unlink()
    restored, skipped = core.undo(tmp_path)
    assert restored == [] and len(skipped) == 1


def test_undo_does_not_clobber_a_recreated_original(tmp_path):
    touch(tmp_path / "a.png", "first")
    core.execute(core.plan(tmp_path), tmp_path)
    touch(tmp_path / "a.png", "second")
    core.undo(tmp_path)
    assert (tmp_path / "a.png").read_text() == "second"
    assert (tmp_path / "a (1).png").read_text() == "first"


def test_tampered_journal_cannot_escape_the_folder(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    outside = touch(tmp_path / "outside.txt", "keep me")
    touch(root / "Images" / "a.png")
    journal = {"runs": [{"timestamp": "t", "moves": [{"src": "../victim.txt", "dst": "../outside.txt"}]}]}
    (root / core.JOURNAL_NAME).write_text(json.dumps(journal))
    restored, skipped = core.undo(root)
    assert restored == [] and "outside" in skipped[0]
    assert outside.read_text() == "keep me"
    assert not (tmp_path / "victim.txt").exists()


def test_corrupt_journal_raises_clear_error(tmp_path):
    (tmp_path / core.JOURNAL_NAME).write_text("{not json")
    with pytest.raises(ValueError, match="corrupt"):
        core.undo(tmp_path)


# ---------- command line ----------

def test_cli_dry_run_changes_nothing(tmp_path, capsys):
    touch(tmp_path / "a.png")
    assert main(["organize", str(tmp_path), "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "a.png" in out and "Dry run" in out
    assert names(tmp_path) == {"a.png"}


def test_cli_organize_then_undo(tmp_path, capsys):
    touch(tmp_path / "a.png")
    assert main(["organize", str(tmp_path)]) == 0
    assert "Moved 1 file" in capsys.readouterr().out
    assert names(tmp_path) == {"Images/a.png"}
    assert main(["undo", str(tmp_path)]) == 0
    assert "Restored 1 file" in capsys.readouterr().out
    assert names(tmp_path) == {"a.png"}


def test_cli_empty_folder_and_nothing_to_undo(tmp_path, capsys):
    assert main(["organize", str(tmp_path)]) == 0
    assert "Nothing to organize" in capsys.readouterr().out
    assert main(["undo", str(tmp_path)]) == 0
    assert "Nothing to undo" in capsys.readouterr().out


def test_cli_missing_folder_returns_error_code(tmp_path, capsys):
    assert main(["organize", str(tmp_path / "nope")]) == 2
    assert "error:" in capsys.readouterr().err


def test_cli_requires_a_command():
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2
