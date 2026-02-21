#!/usr/bin/env python3
"""
DPL Basketball Rankings — Main Entry Point

Fetches (or loads cached) data from the Dallas Parochial League website
and prints cross-conference rankings for 7th Grade Division 2 Boys.

Usage:
    python main.py                  # Fetch live data, print rankings
    python main.py --use-cache      # Use cached data (no network)
    python main.py --h2h            # Include head-to-head detail
    python main.py --load sample    # Load the bundled sample data
"""

import argparse
import json
import sys
from pathlib import Path

from ranker import rank_teams, format_rankings
from scraper import load_or_fetch, DATA_DIR

SAMPLE_FILE = Path(__file__).parent / "data" / "sample_data.json"


def main():
    parser = argparse.ArgumentParser(
        description="Rank DPL 7th Grade Division 2 Boys basketball teams"
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Load previously cached data instead of fetching live",
    )
    parser.add_argument(
        "--load",
        metavar="FILE",
        help="Load data from a specific JSON file (use 'sample' for bundled sample)",
    )
    parser.add_argument(
        "--h2h",
        action="store_true",
        help="Print head-to-head breakdown after rankings",
    )
    parser.add_argument(
        "--save",
        metavar="FILE",
        help="Save fetched data to a specific JSON file",
    )
    args = parser.parse_args()

    # ------------------------------------------------------------------ #
    # Load data
    # ------------------------------------------------------------------ #
    if args.load:
        path = SAMPLE_FILE if args.load.lower() == "sample" else Path(args.load)
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)
        print(f"Loading data from {path} …")
        with open(path) as f:
            data = json.load(f)
    else:
        data = load_or_fetch(use_cache=args.use_cache)

    if args.save:
        out = Path(args.save)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {out}")

    # ------------------------------------------------------------------ #
    # Rank and display
    # ------------------------------------------------------------------ #
    ranked = rank_teams(data)
    print(format_rankings(ranked, show_h2h=args.h2h))

    if not ranked:
        sys.exit(1)


if __name__ == "__main__":
    main()
