# File Organizer

A command-line tool that sorts a messy folder (Downloads, Desktop, a photo dump) into tidy subfolders by **file type** or by **month**. It never overwrites anything, can preview every change first, and can **undo** the last run.

## Problem
Download and project folders fill up with unrelated files. Sorting them by hand is slow, and most scripts that automate it are risky: they overwrite same-named files and can't be reversed. This tool is built to be safe first.

## Features
- Group by **type** (Images, Documents, Audio, Video, Archives, Code, Installers, Other) or by **modified month** (`2025-03`)
- `--dry-run` previews every move and changes nothing
- **Undo** restores the most recent run exactly, and removes folders it created that are now empty
- **Never overwrites**: name clashes become `photo (1).jpg`, even between two subfolders being merged
- Optional `--recursive` mode; the tool's own output folders are never re-sorted
- Skips hidden files and symlinks by default (`--include-hidden` to opt in)
- Undo journal is validated, so a tampered journal cannot move files outside the target folder
- Zero dependencies, Python 3.10+

## Usage
```bash
# preview first
python -m file_organizer organize ~/Downloads --dry-run

# sort by type, including subfolders
python -m file_organizer organize ~/Downloads --recursive

# sort by modified month instead
python -m file_organizer organize ~/Photos --by date

# changed your mind?
python -m file_organizer undo ~/Downloads
```

Example (`--dry-run`):
```
archive.zip  ->  Archives/archive.zip
old/nested/song.mp3  ->  Audio/song.mp3
old/photo.jpg  ->  Images/photo.jpg
photo.jpg  ->  Images/photo (1).jpg

Dry run: 4 file(s) would move. Nothing was changed.
```

Exit codes: `0` success, `1` undo finished with warnings (for example a file you deleted since), `2` error.

## Install
Run it straight from the folder, or install the `file-organizer` command:
```bash
cd file-organizer
pip install .
file-organizer organize ~/Downloads --dry-run
```

## Configuration
None needed. Categories live in the `CATEGORIES` dictionary in `file_organizer/core.py`; add an extension there to teach it a new type.

## Project structure
```text
file-organizer/
├── file_organizer/
│   ├── core.py        # plan / execute / undo logic
│   ├── cli.py         # argparse interface
│   └── __main__.py    # python -m file_organizer
├── tests/
│   └── test_organizer.py
├── pyproject.toml
└── README.md
```

## Run the tests
```bash
pip install pytest
pytest
```
31 tests cover categorisation, dry run, collisions, recursion, hidden files, symlinks, date mode, idempotence, undo (including edge cases and a tampered journal) and the CLI.

## Known limitations
- Undo reverses only the most recent run, one step at a time
- Date mode uses the file's modified time, not EXIF or creation time
- Files are moved within one folder tree; it does not touch other drives or network paths specially

## Future improvements
- User-defined categories from a config file
- Date mode using EXIF capture time for photos
- Duplicate detection by content hash

## License
MIT, see [LICENSE](LICENSE).
