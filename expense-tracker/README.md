# Expense Tracker


Log your spending from the terminal and get instant summaries by category or by month. Data lives in a plain CSV file, so you can open it in Excel or Google Sheets any time.

## Features
- Record expenses with amount, category, note and date
- Summaries by category (largest first) and by month
- Input validation (positive amounts, valid dates)
- No external dependencies, tested with `pytest`

## Usage
```bash
python expenses.py add 12.50 food -n "lunch"
python expenses.py add 800 rent -d 2026-02-01
python expenses.py categories
python expenses.py months
```

Example output:
```
Spending by category
  rent                800.00
  food                 12.50
  TOTAL               812.50
```

## Run the tests
```bash
pip install pytest
pytest
```

## What I practiced
CSV reading and writing, date handling, aggregation with `defaultdict`, and writing testable CLI code.
