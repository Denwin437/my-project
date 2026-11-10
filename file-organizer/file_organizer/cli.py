"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from . import __version__
from .core import MODES, execute, plan, undo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Sort files in a folder into category or date folders, with undo.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    org = sub.add_parser("organize", help="move files into folders")
    org.add_argument("source", help="folder to organize")
    org.add_argument("--by", choices=MODES, default="type", help="group by file type or modified month")
    org.add_argument("-r", "--recursive", action="store_true", help="also organize files in subfolders")
    org.add_argument("--include-hidden", action="store_true", help="include dotfiles and hidden folders")
    org.add_argument("-n", "--dry-run", action="store_true", help="show what would happen, move nothing")

    und = sub.add_parser("undo", help="reverse the most recent organize run")
    und.add_argument("source", help="folder that was organized")
    return parser


def _summarize(moves, root: Path) -> None:
    counts = Counter(m.dst.parent.relative_to(root).as_posix() for m in moves)
    for folder, count in sorted(counts.items()):
        print(f"  {folder}/  {count} file{'s' if count != 1 else ''}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "organize":
            root = Path(args.source).resolve()
            moves = plan(root, args.by, args.recursive, args.include_hidden)
            if not moves:
                print("Nothing to organize.")
                return 0
            if args.dry_run:
                for m in moves:
                    print(f"{m.src.relative_to(root)}  ->  {m.dst.relative_to(root)}")
                print(f"\nDry run: {len(moves)} file(s) would move. Nothing was changed.")
                return 0
            done = execute(moves, root)
            print(f"Moved {len(done)} file(s):")
            _summarize(done, root)
            return 0

        restored, skipped = undo(args.source)
        for message in skipped:
            print(f"warning: {message}", file=sys.stderr)
        if not restored and not skipped:
            print("Nothing to undo.")
        else:
            print(f"Restored {len(restored)} file(s).")
        return 1 if skipped else 0
    except (NotADirectoryError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
