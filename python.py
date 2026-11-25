#!/usr/bin/env python3
"""A small command-line expense tracker.

Usage:
    python expenses.py add <amount> <category>
    python expenses.py list
    python expenses.py total [category]
    python expenses.py clear

Expenses are stored in expenses.json next to this script (override with
the EXPENSES_FILE environment variable or the --file option).
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DEFAULT_FILE = Path(os.environ.get("EXPENSES_FILE", Path(__file__).with_name("expenses.json")))
CURRENCY = "₹"


# ---------- storage ----------

def load(path):
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        sys.exit(f"Error: {path} is not valid JSON. Fix or delete it and try again.")
    if not isinstance(data, list):
        sys.exit(f"Error: {path} has an unexpected format (expected a list).")
    return data


def save(path, expenses):
    # Write to a temp file first so a crash can't corrupt the data.
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(expenses, f, indent=2)
    os.replace(tmp, path)


# ---------- helpers ----------

def money(value):
    return f"{CURRENCY}{value:,.2f}"


def positive_amount(text):
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{text}' is not a number")
    if value <= 0 or value != value or value == float("inf"):
        raise argparse.ArgumentTypeError("amount must be a positive number")
    return round(value, 2)


def totals_by_category(expenses):
    sums = defaultdict(float)
    for e in expenses:
        sums[e["category"]] += e["amount"]
    return sums


def print_top_categories(expenses, n=3):
    sums = totals_by_category(expenses)
    if not sums:
        return
    grand = sum(sums.values())
    top = sorted(sums.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
    name_w = max(len("Category"), *(len(c) for c, _ in top))
    amt_w = max(len("Total"), *(len(money(v)) for _, v in top))

    print(f"\nTop {len(top)} categories by spending")
    print(f"  {'#':<2}  {'Category':<{name_w}}  {'Total':>{amt_w}}  {'Share':>6}")
    print(f"  {'-' * 2}  {'-' * name_w}  {'-' * amt_w}  {'-' * 6}")
    for i, (cat, amt) in enumerate(top, 1):
        print(f"  {i:<2}  {cat:<{name_w}}  {money(amt):>{amt_w}}  {amt / grand * 100:>5.1f}%")


# ---------- commands ----------

def cmd_add(args, expenses):
    category = args.category.strip().lower()
    if not category:
        sys.exit("Error: category cannot be empty.")
    expenses.append({
        "id": max((e.get("id", 0) for e in expenses), default=0) + 1,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "amount": args.amount,
        "category": category,
    })
    save(args.file, expenses)
    print(f"Added {money(args.amount)} to '{category}'.")


def cmd_list(args, expenses):
    if not expenses:
        print("No expenses recorded yet.")
        return

    id_w = max(len("ID"), len(str(max(e["id"] for e in expenses))))
    date_w = len("Date")
    date_w = max(date_w, *(len(e["date"]) for e in expenses))
    cat_w = max(len("Category"), *(len(e["category"]) for e in expenses))
    amt_w = max(len("Amount"), *(len(money(e["amount"])) for e in expenses))

    header = f"{'ID':>{id_w}}  {'Date':<{date_w}}  {'Category':<{cat_w}}  {'Amount':>{amt_w}}"
    print(header)
    print("-" * len(header))
    for e in expenses:
        print(f"{e['id']:>{id_w}}  {e['date']:<{date_w}}  {e['category']:<{cat_w}}  {money(e['amount']):>{amt_w}}")
    print("-" * len(header))
    total = sum(e["amount"] for e in expenses)
    label = f"Total ({len(expenses)} expense{'s' if len(expenses) != 1 else ''})"
    print(f"{label:<{len(header) - amt_w - 2}}  {money(total):>{amt_w}}")

    print_top_categories(expenses)


def cmd_total(args, expenses):
    if args.category:
        category = args.category.strip().lower()
        matching = [e for e in expenses if e["category"] == category]
        if not matching:
            print(f"No expenses found for category '{category}'.")
            return
        print(f"Total for '{category}': {money(sum(e['amount'] for e in matching))} "
              f"({len(matching)} expense{'s' if len(matching) != 1 else ''})")
    else:
        print(f"Total: {money(sum(e['amount'] for e in expenses))} "
              f"({len(expenses)} expense{'s' if len(expenses) != 1 else ''})")


def cmd_clear(args, expenses):
    if not expenses:
        print("Nothing to clear.")
        return
    if not args.yes:
        answer = input(f"Delete all {len(expenses)} expenses? This cannot be undone [y/N]: ")
        if answer.strip().lower() not in ("y", "yes"):
            print("Cancelled.")
            return
    save(args.file, [])
    print("All expenses cleared.")


# ---------- CLI ----------

def build_parser():
    parser = argparse.ArgumentParser(prog="expenses", description="Track expenses from the command line.")
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE,
                        help=f"JSON data file (default: {DEFAULT_FILE})")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="add an expense")
    p.add_argument("amount", type=positive_amount, help="amount spent, e.g. 250")
    p.add_argument("category", help="category, e.g. food")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("list", help="show all expenses")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("total", help="sum all expenses, or only one category")
    p.add_argument("category", nargs="?", help="optional category to filter by")
    p.set_defaults(func=cmd_total)

    p = sub.add_parser("clear", help="wipe all expenses")
    p.add_argument("-y", "--yes", action="store_true", help="skip the confirmation prompt")
    p.set_defaults(func=cmd_clear)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    expenses = load(args.file)
    args.func(args, expenses)


if __name__ == "__main__":
    main()
