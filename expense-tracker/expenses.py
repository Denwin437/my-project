#!/usr/bin/env python3
"""Expense Tracker: log spending to a CSV file and see summaries."""

import argparse
import csv
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

FIELDS = ["date", "category", "amount", "note"]
DEFAULT_FILE = Path("expenses.csv")


def add_expense(path: Path, amount: float, category: str, note: str = "", on: str = None) -> dict:
    path = Path(path)
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")
    if not category.strip():
        raise ValueError("Category cannot be empty")
    on = on or date.today().isoformat()
    datetime.strptime(on, "%Y-%m-%d")  # raises ValueError for a bad date
    row = {"date": on, "category": category.strip().lower(), "amount": f"{amount:.2f}", "note": note}
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow(row)
    return row


def read_expenses(path: Path) -> list:
    path = Path(path)
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [{**r, "amount": float(r["amount"])} for r in csv.DictReader(f)]


def summarize_by_category(expenses: list) -> dict:
    totals = defaultdict(float)
    for e in expenses:
        totals[e["category"]] += e["amount"]
    return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))


def summarize_by_month(expenses: list) -> dict:
    totals = defaultdict(float)
    for e in expenses:
        totals[e["date"][:7]] += e["amount"]
    return dict(sorted(totals.items()))


def print_summary(title: str, totals: dict) -> None:
    print(title)
    if not totals:
        print("  (no data)")
        return
    for key, total in totals.items():
        print(f"  {key:<15} {total:>10.2f}")
    print(f"  {'TOTAL':<15} {sum(totals.values()):>10.2f}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track your expenses in a CSV file.")
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="record an expense")
    add.add_argument("amount", type=float)
    add.add_argument("category")
    add.add_argument("-n", "--note", default="")
    add.add_argument("-d", "--date", help="YYYY-MM-DD (defaults to today)")

    sub.add_parser("categories", help="totals per category")
    sub.add_parser("months", help="totals per month")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "add":
            row = add_expense(args.file, args.amount, args.category, args.note, args.date)
            print(f"Recorded {row['amount']} in '{row['category']}' on {row['date']}")
        elif args.command == "categories":
            print_summary("Spending by category", summarize_by_category(read_expenses(args.file)))
        elif args.command == "months":
            print_summary("Spending by month", summarize_by_month(read_expenses(args.file)))
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
