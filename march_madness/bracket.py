"""
NCAA March Madness bracket structure.

Defines the 64-team bracket with 4 regions, seeds 1-16, and the
fixed first-round matchup pairings (1v16, 2v15, 3v14, ... 8v9).

UPDATE `REGIONS` below with the actual teams once the bracket is announced.
"""

# ---------------------------------------------------------------------------
# Region definitions — fill in team names once the bracket is released.
# Each region maps seed (int) -> team name (str).
# ---------------------------------------------------------------------------

REGIONS = {
    "South": {
        1: "TBD", 2: "TBD", 3: "TBD", 4: "TBD",
        5: "TBD", 6: "TBD", 7: "TBD", 8: "TBD",
        9: "TBD", 10: "TBD", 11: "TBD", 12: "TBD",
        13: "TBD", 14: "TBD", 15: "TBD", 16: "TBD",
    },
    "West": {
        1: "TBD", 2: "TBD", 3: "TBD", 4: "TBD",
        5: "TBD", 6: "TBD", 7: "TBD", 8: "TBD",
        9: "TBD", 10: "TBD", 11: "TBD", 12: "TBD",
        13: "TBD", 14: "TBD", 15: "TBD", 16: "TBD",
    },
    "East": {
        1: "TBD", 2: "TBD", 3: "TBD", 4: "TBD",
        5: "TBD", 6: "TBD", 7: "TBD", 8: "TBD",
        9: "TBD", 10: "TBD", 11: "TBD", 12: "TBD",
        13: "TBD", 14: "TBD", 15: "TBD", 16: "TBD",
    },
    "Midwest": {
        1: "TBD", 2: "TBD", 3: "TBD", 4: "TBD",
        5: "TBD", 6: "TBD", 7: "TBD", 8: "TBD",
        9: "TBD", 10: "TBD", 11: "TBD", 12: "TBD",
        13: "TBD", 14: "TBD", 15: "TBD", 16: "TBD",
    },
}

# Standard first-round seed matchups (higher seed listed first)
FIRST_ROUND_MATCHUPS = [
    (1, 16), (8, 9), (5, 12), (4, 13),
    (6, 11), (3, 14), (7, 10), (2, 15),
]

# Semifinal pairings by region (which regions play each other in Final Four)
# Update if the NCAA changes the bracket layout for the year.
FINAL_FOUR_PAIRINGS = [
    ("South", "West"),
    ("East", "Midwest"),
]

ROUND_NAMES = [
    "Round of 64",
    "Round of 32",
    "Sweet 16",
    "Elite 8",
    "Final Four",
    "Championship",
]


def get_team_seed(team_name):
    """Return (region, seed) for a team name, or None if not found."""
    for region, seeds in REGIONS.items():
        for seed, name in seeds.items():
            if name.strip().lower() == team_name.strip().lower():
                return region, seed
    return None


def get_all_teams():
    """Return a list of (region, seed, team_name) for every team."""
    teams = []
    for region in REGIONS:
        for seed in sorted(REGIONS[region]):
            teams.append((region, seed, REGIONS[region][seed]))
    return teams


def build_first_round_games():
    """
    Return a list of first-round game dicts:
        {"game_id": "S_R1_1", "region": "South", "high_seed": 1,
         "low_seed": 16, "team_a": "Duke", "team_b": "Fairleigh Dickinson"}
    Game IDs use the pattern: {region_initial}_{round}_{game_number}
    """
    games = []
    region_initials = {r: r[0] for r in REGIONS}
    # Handle duplicate initials (South / (none expected, but be safe))
    for region in REGIONS:
        for i, (hi, lo) in enumerate(FIRST_ROUND_MATCHUPS, start=1):
            games.append({
                "game_id": f"{region_initials[region]}_R1_{i}",
                "region": region,
                "round": 1,
                "high_seed": hi,
                "low_seed": lo,
                "team_a": REGIONS[region][hi],
                "team_b": REGIONS[region][lo],
            })
    return games
