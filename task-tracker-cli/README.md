# Task Tracker CLI


A small command-line to-do manager written in pure Python (no dependencies). Tasks are stored in a JSON file and sorted by status and priority.

## Features
- Add tasks with `low`, `medium` or `high` priority
- Mark tasks done, delete tasks, list everything or only pending items
- Custom data file via `--db`
- Fully unit-tested with `pytest`

## Usage
```bash
python tasks.py add "Write project README" -p high
python tasks.py add "Buy groceries" -p low
python tasks.py list
python tasks.py done 1
python tasks.py list --pending
python tasks.py remove 2
```

Example output:
```
[ ]   1  (high  )  Write project README
[ ]   2  (low   )  Buy groceries
```

## Run the tests
```bash
pip install pytest
pytest
```

## What I practiced
Argument parsing with `argparse` subcommands, JSON persistence, input validation, and testing a CLI end to end.
