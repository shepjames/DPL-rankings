"""
NCAA March Madness 2026 bracket structure.

Defines the 68-team bracket with 4 regions, seeds 1-16, and the
fixed first-round matchup pairings (1v16, 2v15, 3v14, ... 8v9).

First Four play-in games are noted with "/" between the two teams.
Once those games are decided, replace the entry with the winner.
"""

# ---------------------------------------------------------------------------
# 2026 NCAA Tournament — Official bracket (announced March 15, 2026)
# Duke is the No. 1 overall seed. Final Four in Indianapolis (April 4-6).
#
# First Four play-in games (Dayton, OH — March 17-18):
#   16-seed: Prairie View A&M vs Lehigh  → South
#   16-seed: UMBC vs Howard              → Midwest
#   11-seed: Texas vs NC State           → West
#   11-seed: Miami (OH) vs SMU           → Midwest
# ---------------------------------------------------------------------------

# Region order matters: consecutive pairs meet in the Final Four.
# East vs South (semifinal 1), West vs Midwest (semifinal 2).
REGIONS = {
    "East": {
        1: "Duke", 2: "UConn", 3: "Michigan State", 4: "Kansas",
        5: "St. John's", 6: "Louisville", 7: "UCLA", 8: "Ohio State",
        9: "TCU", 10: "UCF", 11: "South Florida", 12: "Northern Iowa",
        13: "Cal Baptist", 14: "North Dakota State", 15: "Furman", 16: "Siena",
    },
    "South": {
        1: "Florida", 2: "Houston", 3: "Illinois", 4: "Nebraska",
        5: "Vanderbilt", 6: "North Carolina", 7: "Saint Mary's", 8: "Clemson",
        9: "Iowa", 10: "Texas A&M", 11: "VCU", 12: "McNeese",
        13: "Troy", 14: "Penn", 15: "Idaho", 16: "Prairie View A&M/Lehigh",
    },
    "West": {
        1: "Arizona", 2: "Purdue", 3: "Gonzaga", 4: "Arkansas",
        5: "Wisconsin", 6: "BYU", 7: "Miami", 8: "Villanova",
        9: "Utah State", 10: "Missouri", 11: "Texas/NC State", 12: "High Point",
        13: "Hawaii", 14: "Kennesaw State", 15: "Queens", 16: "LIU",
    },
    "Midwest": {
        1: "Michigan", 2: "Iowa State", 3: "Virginia", 4: "Alabama",
        5: "Texas Tech", 6: "Tennessee", 7: "Kentucky", 8: "Georgia",
        9: "Saint Louis", 10: "Santa Clara", 11: "Miami (OH)/SMU", 12: "Akron",
        13: "Hofstra", 14: "Wright State", 15: "Tennessee State", 16: "UMBC/Howard",
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
    ("East", "South"),
    ("West", "Midwest"),
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
