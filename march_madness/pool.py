#!/usr/bin/env python3
"""
March Madness Bracket Pool — CLI

Commands:
    template    Generate a blank pick-sheet CSV to share with entrants
    score       Score all entrant picks against results and print standings
    standings   Alias for score

Usage:
    python -m march_madness.pool template
    python -m march_madness.pool template --output my_bracket.csv
    python -m march_madness.pool score --picks picks/*.csv --results results.csv
"""

import argparse
import sys
from pathlib import Path

from march_madness.sheets import (
    generate_pick_template_csv,
    read_picks_from_csv,
    read_results_from_csv,
)
from march_madness.scorer import score_pool, format_standings


def cmd_template(args):
    output = Path(args.output)
    path = generate_pick_template_csv(output)
    print(f"Template written to: {path}")
    print()
    print("Next steps:")
    print("  1. Import this CSV into Google Sheets (File → Import)")
    print("  2. Share the sheet with your pool entrants")
    print("  3. Each entrant fills in the 'Your Pick' column")
    print("  4. Download each entrant's completed sheet as CSV")
    print("  5. Run:  python -m march_madness.pool score --picks *.csv --results results.csv")


def cmd_score(args):
    if not args.picks:
        print("Error: provide at least one --picks CSV file", file=sys.stderr)
        sys.exit(1)
    if not args.results:
        print("Error: provide a --results CSV file", file=sys.stderr)
        sys.exit(1)

    # Read results
    results = read_results_from_csv(args.results)
    print(f"Results loaded: {len(results.game_winners)} games decided\n")

    # Read all entrant picks
    all_picks = []
    for pick_file in args.picks:
        try:
            picks = read_picks_from_csv(pick_file)
            all_picks.append(picks)
            print(f"  Loaded picks: {picks.name} ({pick_file})")
        except Exception as e:
            print(f"  Warning: could not read {pick_file}: {e}", file=sys.stderr)

    if not all_picks:
        print("No valid pick sheets found.", file=sys.stderr)
        sys.exit(1)

    print()

    # Score and display
    leaderboards = score_pool(all_picks, results)
    print(format_standings(leaderboards))


def main():
    parser = argparse.ArgumentParser(
        description="March Madness Bracket Pool Manager"
    )
    sub = parser.add_subparsers(dest="command")

    # --- template ---
    p_tmpl = sub.add_parser("template", help="Generate a blank pick-sheet CSV")
    p_tmpl.add_argument(
        "--output", "-o",
        default="march_madness_picks_template.csv",
        help="Output CSV file path (default: march_madness_picks_template.csv)",
    )

    # --- score ---
    p_score = sub.add_parser("score", help="Score picks against results")
    p_score.add_argument(
        "--picks", nargs="+", required=True,
        help="One or more entrant pick CSV files",
    )
    p_score.add_argument(
        "--results", required=True,
        help="Tournament results CSV file",
    )

    # --- standings (alias) ---
    sub.add_parser("standings", help="Alias for 'score'", parents=[p_score],
                    add_help=False)

    args = parser.parse_args()

    if args.command in ("score", "standings"):
        cmd_score(args)
    elif args.command == "template":
        cmd_template(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
