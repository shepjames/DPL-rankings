"""
Google Sheets integration for the March Madness pool.

Two workflows supported:
  1. **Generate a template** — creates a CSV file you can import into Google
     Sheets and share with entrants.
  2. **Read picks back** — reads a Google Sheet (exported as CSV via its public
     "publish to web" URL) and parses entrant picks.

Google Sheets CSV export URL format (no API key needed):
    https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={TAB_NAME}

You can also just download the sheet as CSV and point the tool at the file.
"""

from __future__ import annotations

import csv
import io
import urllib.request
from pathlib import Path

from march_madness.bracket import (
    REGIONS,
    FIRST_ROUND_MATCHUPS,
    ROUND_NAMES,
    get_all_teams,
    get_team_seed,
)
from march_madness.scorer import EntrantPicks, TournamentResults


# ------------------------------------------------------------------ #
#  Template generation
# ------------------------------------------------------------------ #

def generate_pick_template_csv(output_path: str | Path) -> Path:
    """
    Generate a CSV template for collecting bracket picks.

    The template has the following structure:
        Row 1: Header row
        Section 1: Entrant info (name, sleeper, final four, champion)
        Section 2: All 63 games listed by round, entrant picks the winner

    Returns the path to the written file.
    """
    output_path = Path(output_path)
    rows = []

    # --- Header instructions ---
    rows.append(["MARCH MADNESS BRACKET POOL — PICK SHEET"])
    rows.append(["Fill in the 'Your Pick' column for every row below."])
    rows.append([])

    # --- Entrant info ---
    rows.append(["YOUR NAME", "", "(enter your name)"])
    rows.append([])

    # --- Special picks ---
    rows.append(["=== SPECIAL PICKS ==="])
    rows.append(["Category", "Instructions", "Your Pick"])
    rows.append([
        "Sleeper Team",
        "Pick one underdog. You earn (seed x wins) points.",
        "",
    ])
    rows.append([
        "Final Four #1",
        "Pick a team you think makes the Final Four",
        "",
    ])
    rows.append([
        "Final Four #2",
        "Pick a team you think makes the Final Four",
        "",
    ])
    rows.append([
        "Final Four #3",
        "Pick a team you think makes the Final Four",
        "",
    ])
    rows.append([
        "Final Four #4",
        "Pick a team you think makes the Final Four",
        "",
    ])
    rows.append([
        "Champion",
        "Pick the overall tournament winner",
        "",
    ])
    rows.append([])

    # --- Bracket games by region, round by round ---
    rows.append(["=== BRACKET PICKS (pick the winner of each game) ==="])
    rows.append(["Game ID", "Round", "Region", "Team A (seed)", "Team B (seed)", "Your Pick (winner)"])

    # Round of 64
    game_num = 0
    for region in REGIONS:
        for hi, lo in FIRST_ROUND_MATCHUPS:
            game_num += 1
            team_a = REGIONS[region][hi]
            team_b = REGIONS[region][lo]
            game_id = f"G{game_num:02d}"
            rows.append([
                game_id,
                "Round of 64",
                region,
                f"({hi}) {team_a}",
                f"({lo}) {team_b}",
                "",
            ])

    # Rounds 2-6: we list placeholder game slots
    # In subsequent rounds, the matchups depend on earlier picks,
    # so we list them as "Winner of Gxx vs Winner of Gyy"
    round_game_counts = [32, 16, 8, 4, 2, 1]  # R64, R32, S16, E8, FF, Champ
    prev_round_start = 1
    for rnd_idx in range(1, 6):  # rounds 2 through 6
        round_name = ROUND_NAMES[rnd_idx]
        prev_count = round_game_counts[rnd_idx - 1]
        curr_count = round_game_counts[rnd_idx]
        region_label = ""

        for i in range(curr_count):
            game_num += 1
            game_id = f"G{game_num:02d}"
            # Figure out which two previous games feed into this one
            feeder_a = prev_round_start + (i * 2)
            feeder_b = prev_round_start + (i * 2) + 1

            if rnd_idx <= 3:  # Through Elite 8 — still within regions
                region_idx = i // (curr_count // 4) if curr_count >= 4 else i
                region_names = list(REGIONS.keys())
                region_label = region_names[min(region_idx, 3)] if curr_count >= 4 else ""
            elif rnd_idx == 4:
                region_label = "Final Four"
            else:
                region_label = "Championship"

            rows.append([
                game_id,
                round_name,
                region_label,
                f"Winner of G{feeder_a:02d}",
                f"Winner of G{feeder_b:02d}",
                "",
            ])
        prev_round_start += prev_count

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return output_path


# ------------------------------------------------------------------ #
#  Reading picks from CSV (downloaded or fetched from Google Sheets)
# ------------------------------------------------------------------ #

def read_picks_from_csv(source: str | Path) -> EntrantPicks:
    """
    Parse a single entrant's pick sheet CSV.

    `source` can be a local file path or a URL (Google Sheets CSV export).
    """
    if str(source).startswith("http"):
        with urllib.request.urlopen(str(source)) as resp:
            text = resp.read().decode("utf-8")
    else:
        text = Path(source).read_text()

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    picks = EntrantPicks(name="Unknown")

    # Parse entrant name
    for row in rows:
        if row and row[0].strip().upper() == "YOUR NAME" and len(row) >= 3:
            picks.name = row[2].strip()
            break

    # Parse special picks
    final_four = []
    for row in rows:
        if not row or len(row) < 3:
            continue
        label = row[0].strip()
        value = row[2].strip() if len(row) > 2 else ""
        if label == "Sleeper Team":
            picks.sleeper_team = value
        elif label.startswith("Final Four"):
            if value:
                final_four.append(value)
        elif label == "Champion":
            picks.champion = value
    picks.final_four = final_four

    # Parse game picks
    in_bracket = False
    for row in rows:
        if not row:
            continue
        if row[0].strip().startswith("Game ID"):
            in_bracket = True
            continue
        if in_bracket and row[0].strip().startswith("G"):
            game_id = row[0].strip()
            winner = row[5].strip() if len(row) > 5 else ""
            if winner:
                picks.game_picks[game_id] = winner

    return picks


def read_results_from_csv(source: str | Path) -> TournamentResults:
    """
    Parse tournament results from a CSV file.

    Expected format — same game ID column as the pick sheet, with an
    "Actual Winner" column (column index 6 or the last column).

    Also reads team seed info from bracket.py for sleeper scoring.
    """
    if str(source).startswith("http"):
        with urllib.request.urlopen(str(source)) as resp:
            text = resp.read().decode("utf-8")
    else:
        text = Path(source).read_text()

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    results = TournamentResults()

    # Build team_seeds from bracket data
    for region, seed, team in get_all_teams():
        if team != "TBD":
            results.team_seeds[team] = (region, seed)

    # Parse game results
    in_bracket = False
    for row in rows:
        if not row:
            continue
        if row[0].strip().startswith("Game ID"):
            in_bracket = True
            continue
        if in_bracket and row[0].strip().startswith("G"):
            game_id = row[0].strip()
            # Winner is in the last populated column
            winner = ""
            for cell in reversed(row):
                if cell.strip():
                    winner = cell.strip()
                    break
            if winner and not winner.startswith("Winner of"):
                results.game_winners[game_id] = winner
                results.team_wins[winner] = results.team_wins.get(winner, 0) + 1

    return results


def fetch_google_sheet_csv(sheet_id: str, tab_name: str = "Sheet1") -> str:
    """
    Fetch a Google Sheet tab as CSV text (sheet must be published to web).

    To publish: Google Sheets -> File -> Share -> Publish to web -> CSV
    """
    url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        f"/gviz/tq?tqx=out:csv&sheet={tab_name}"
    )
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode("utf-8")
