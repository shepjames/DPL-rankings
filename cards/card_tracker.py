#!/usr/bin/env python3
"""
Sports Card Tracker — CLI

Track your sports card collection and figure out which cards are worth
sending to PSA or Beckett for professional grading.

Usage:
    python cards/card_tracker.py add
    python cards/card_tracker.py list [--sport football] [--min-value 50] [--sort raw_value]
    python cards/card_tracker.py view <card_id>
    python cards/card_tracker.py update <card_id> --raw-value 120
    python cards/card_tracker.py remove <card_id>
    python cards/card_tracker.py grade <card_id> --expected-grade 9
    python cards/card_tracker.py grade-all --expected-grade 9
    python cards/card_tracker.py grade-check --raw-value 200 --expected-grade 9.5
    python cards/card_tracker.py summary
    python cards/card_tracker.py import-csv cards.csv
"""

import argparse
import csv
import sys

from collection import (
    add_card,
    collection_summary,
    get_card,
    list_cards,
    remove_card,
    update_card,
)
from grading import (
    format_analysis,
    format_batch_analysis,
    grading_analysis,
)


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def _prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"  {label}{suffix}: ").strip()
    return val or default


def _prompt_float(label: str, default: float | None = None) -> float:
    while True:
        raw = _prompt(label, str(default) if default is not None else "")
        try:
            return float(raw)
        except ValueError:
            print("  Please enter a number.")


# ------------------------------------------------------------------ #
# Commands
# ------------------------------------------------------------------ #

def cmd_add(_args):
    """Interactively add a card."""
    print("\n  Add a new card to your collection\n")
    card = add_card(
        player=_prompt("Player name"),
        year=_prompt("Year"),
        card_set=_prompt("Card set (e.g. Topps Chrome, Prizm)"),
        card_number=_prompt("Card number", "—"),
        sport=_prompt("Sport", "basketball"),
        condition=_prompt("Condition (Mint/NM/EX/VG/Good/Fair/Poor)", "NM"),
        raw_value=_prompt_float("Estimated raw value ($)"),
        notes=_prompt("Notes (optional)", ""),
    )
    print(f"\n  Card added!  ID: {card['id']}")
    print(f"  {card['year']} {card['set']} — {card['player']}\n")


def cmd_list(args):
    """List cards in the collection."""
    cards = list_cards(
        sort_by=args.sort,
        sport=args.sport,
        min_value=args.min_value,
    )
    if not cards:
        print("\n  No cards in your collection yet.  Use 'add' to get started.\n")
        return

    print(f"\n  {'ID':<10} {'Player':<22} {'Year':<6} {'Set':<22} {'Cond':<6} {'Value':>8}")
    print("  " + "-" * 78)
    for c in cards:
        print(
            f"  {c['id']:<10} {c['player']:<22} {c['year']:<6} "
            f"{c['set']:<22} {c['condition']:<6} ${c['raw_value']:>7,.2f}"
        )
    print()


def cmd_view(args):
    """View details of a single card."""
    card = get_card(args.card_id)
    if not card:
        print(f"  Card '{args.card_id}' not found.")
        return
    print()
    for k, v in card.items():
        label = k.replace("_", " ").title()
        if k == "raw_value":
            print(f"  {label:<16} ${v:,.2f}")
        else:
            print(f"  {label:<16} {v}")
    print()


def cmd_update(args):
    """Update fields on a card."""
    fields = {}
    if args.player:
        fields["player"] = args.player
    if args.year:
        fields["year"] = args.year
    if args.card_set:
        fields["set"] = args.card_set
    if args.card_number:
        fields["card_number"] = args.card_number
    if args.sport:
        fields["sport"] = args.sport
    if args.condition:
        fields["condition"] = args.condition
    if args.raw_value is not None:
        fields["raw_value"] = args.raw_value
    if args.notes is not None:
        fields["notes"] = args.notes

    if not fields:
        print("  No fields to update. Use flags like --player, --raw-value, etc.")
        return

    updated = update_card(args.card_id, **fields)
    if updated:
        print(f"  Updated card {args.card_id}.")
    else:
        print(f"  Card '{args.card_id}' not found.")


def cmd_remove(args):
    """Remove a card from the collection."""
    card = get_card(args.card_id)
    if not card:
        print(f"  Card '{args.card_id}' not found.")
        return
    print(f"  Removing: {card['year']} {card['set']} — {card['player']}")
    confirm = input("  Are you sure? (y/n): ").strip().lower()
    if confirm == "y":
        remove_card(args.card_id)
        print("  Card removed.")
    else:
        print("  Cancelled.")


def cmd_grade(args):
    """Analyze grading ROI for a single card in the collection."""
    card = get_card(args.card_id)
    if not card:
        print(f"  Card '{args.card_id}' not found.")
        return

    grade = args.expected_grade
    if grade is None:
        grade = _prompt_float("Expected grade (1–10)")

    print(f"\n  Card: {card['year']} {card['set']} — {card['player']}")
    analysis = grading_analysis(card["raw_value"], grade)
    print(format_analysis(analysis))


def cmd_grade_all(args):
    """Analyze grading ROI for every card in the collection."""
    cards = list_cards(sort_by="raw_value")
    if not cards:
        print("\n  No cards in your collection.\n")
        return

    grade = args.expected_grade
    if grade is None:
        grade = _prompt_float("Expected grade for all cards (1–10)")

    pairs = []
    for card in cards:
        analysis = grading_analysis(card["raw_value"], grade)
        pairs.append((card, analysis))

    print()
    print(format_batch_analysis(pairs))
    print()


def cmd_grade_check(args):
    """Quick grading check without adding a card to the collection."""
    raw = args.raw_value
    grade = args.expected_grade
    if raw is None:
        raw = _prompt_float("Estimated raw value ($)")
    if grade is None:
        grade = _prompt_float("Expected grade (1–10)")

    analysis = grading_analysis(raw, grade)
    print(format_analysis(analysis))


def cmd_summary(_args):
    """Print collection summary statistics."""
    s = collection_summary()
    if s["total_cards"] == 0:
        print("\n  No cards in your collection yet.\n")
        return

    print(f"\n  Total cards:  {s['total_cards']}")
    print(f"  Total value:  ${s['total_value']:,.2f}")
    print(f"\n  By sport:")
    for sport, count in s["by_sport"].items():
        print(f"    {sport:<16} {count}")
    print(f"\n  By year:")
    for year, count in s["by_year"].items():
        print(f"    {year:<16} {count}")
    print()


def cmd_import_csv(args):
    """Import cards from a CSV file.

    Expected columns: player, year, set, card_number, sport, condition,
                      raw_value, notes
    """
    path = args.file
    try:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                add_card(
                    player=row.get("player", ""),
                    year=row.get("year", ""),
                    card_set=row.get("set", ""),
                    card_number=row.get("card_number", ""),
                    sport=row.get("sport", "basketball"),
                    condition=row.get("condition", "NM"),
                    raw_value=float(row.get("raw_value", 0)),
                    notes=row.get("notes", ""),
                )
                count += 1
            print(f"  Imported {count} card(s) from {path}.")
    except FileNotFoundError:
        print(f"  File not found: {path}")
    except (KeyError, ValueError) as e:
        print(f"  Error reading CSV: {e}")


# ------------------------------------------------------------------ #
# Argument parser
# ------------------------------------------------------------------ #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="card_tracker",
        description="Track your sports card collection and analyze grading ROI",
    )
    sub = parser.add_subparsers(dest="command")

    # add
    sub.add_parser("add", help="Add a card interactively")

    # list
    p_list = sub.add_parser("list", help="List cards")
    p_list.add_argument("--sort", default="player",
                        help="Sort by: player, year, raw_value, sport, date_added, set")
    p_list.add_argument("--sport", help="Filter by sport")
    p_list.add_argument("--min-value", type=float, help="Minimum raw value")

    # view
    p_view = sub.add_parser("view", help="View card details")
    p_view.add_argument("card_id")

    # update
    p_up = sub.add_parser("update", help="Update card fields")
    p_up.add_argument("card_id")
    p_up.add_argument("--player")
    p_up.add_argument("--year")
    p_up.add_argument("--card-set")
    p_up.add_argument("--card-number")
    p_up.add_argument("--sport")
    p_up.add_argument("--condition")
    p_up.add_argument("--raw-value", type=float)
    p_up.add_argument("--notes")

    # remove
    p_rm = sub.add_parser("remove", help="Remove a card")
    p_rm.add_argument("card_id")

    # grade (single card from collection)
    p_grade = sub.add_parser("grade", help="Analyze grading ROI for a card")
    p_grade.add_argument("card_id")
    p_grade.add_argument("--expected-grade", type=float,
                         help="Expected grade (1–10)")

    # grade-all
    p_ga = sub.add_parser("grade-all", help="Analyze grading ROI for all cards")
    p_ga.add_argument("--expected-grade", type=float,
                      help="Expected grade (1–10)")

    # grade-check (no card needed)
    p_gc = sub.add_parser("grade-check",
                          help="Quick grading ROI check (no card needed)")
    p_gc.add_argument("--raw-value", type=float, help="Card raw value ($)")
    p_gc.add_argument("--expected-grade", type=float,
                      help="Expected grade (1–10)")

    # summary
    sub.add_parser("summary", help="Collection summary stats")

    # import-csv
    p_csv = sub.add_parser("import-csv", help="Import cards from CSV")
    p_csv.add_argument("file", help="Path to CSV file")

    return parser


COMMAND_MAP = {
    "add": cmd_add,
    "list": cmd_list,
    "view": cmd_view,
    "update": cmd_update,
    "remove": cmd_remove,
    "grade": cmd_grade,
    "grade-all": cmd_grade_all,
    "grade-check": cmd_grade_check,
    "summary": cmd_summary,
    "import-csv": cmd_import_csv,
}


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    COMMAND_MAP[args.command](args)


if __name__ == "__main__":
    main()
