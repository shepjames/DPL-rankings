"""
DPL Basketball Ranking Engine
Ranks 5th Grade Girls teams across all conferences.

Ranking criteria (applied in order as tiebreakers):
  1. Overall win percentage  (primary)
  2. Conference win percentage
  3. Head-to-head record (among tied teams)
  4. Head-to-head score differential (among tied teams)
  5. Overall score differential (capped per game to avoid outliers)

Usage:
    from ranker import rank_teams
    ranked = rank_teams(data)   # data = output of scraper.load_or_fetch()
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

# Cap per-game score differential to limit blowout distortion
MAX_DIFF_PER_GAME = 20


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class Team:
    name: str
    conference: str
    wins: int = 0
    losses: int = 0
    conference_wins: int = 0
    conference_losses: int = 0

    # Populated from game results
    points_for: int = 0
    points_against: int = 0
    games_played: int = 0          # from actual game results

    # Head-to-head record vs other teams {opponent: (wins, losses, point_diff)}
    h2h: dict[str, list[int]] = field(default_factory=lambda: defaultdict(lambda: [0, 0, 0]))

    # ------------------------------------------------------------------ #
    @property
    def win_pct(self) -> float:
        total = self.wins + self.losses
        return self.wins / total if total else 0.0

    @property
    def conf_win_pct(self) -> float:
        total = self.conference_wins + self.conference_losses
        return self.conference_wins / total if total else 0.0

    @property
    def score_diff(self) -> float:
        """Average capped score differential per game."""
        if self.games_played == 0:
            return 0.0
        return self.capped_diff / self.games_played

    @property
    def capped_diff(self) -> int:
        """Sum of per-game differentials capped at MAX_DIFF_PER_GAME."""
        return self._capped_diff

    # ------------------------------------------------------------------ #
    def record_game(self, scored: int, allowed: int, opponent: str) -> None:
        """Record a completed game result."""
        self.points_for += scored
        self.points_against += allowed
        self.games_played += 1

        diff = scored - allowed
        capped = max(-MAX_DIFF_PER_GAME, min(MAX_DIFF_PER_GAME, diff))
        self._capped_diff = getattr(self, "_capped_diff", 0) + capped

        if diff > 0:
            self.h2h[opponent][0] += 1          # h2h win
        elif diff < 0:
            self.h2h[opponent][1] += 1          # h2h loss
        self.h2h[opponent][2] += diff           # raw diff (not capped for H2H clarity)

    def __post_init__(self):
        self._capped_diff = 0


# ---------------------------------------------------------------------------
# Build team objects from scraped data
# ---------------------------------------------------------------------------


def build_teams(data: dict) -> dict[str, Team]:
    """
    Construct Team objects from the combined standings + game data.

    Standings provide the official W/L record (including conference).
    Game results provide head-to-head records and score differential.
    """
    teams: dict[str, Team] = {}

    # --- Seed from standings ---
    for conf_name, conf_teams in data.get("conferences", {}).items():
        for entry in conf_teams:
            name = entry["team"]
            team = Team(
                name=name,
                conference=conf_name,
                wins=entry.get("wins", 0),
                losses=entry.get("losses", 0),
                conference_wins=entry.get("conference_wins", 0),
                conference_losses=entry.get("conference_losses", 0),
            )
            teams[name] = team

    # --- Enrich from game results ---
    for game in data.get("games", []):
        home = game.get("home_team", "")
        away = game.get("away_team", "")
        hs = game.get("home_score")
        as_ = game.get("away_score")

        # Only process completed games
        if hs is None or as_ is None:
            continue

        # Auto-create teams that appear in results but not in standings
        for name, conf in [(home, game.get("conference")), (away, game.get("conference"))]:
            if name and name not in teams:
                teams[name] = Team(name=name, conference=conf or "Unknown")

        if home in teams:
            teams[home].record_game(hs, as_, away)
        if away in teams:
            teams[away].record_game(as_, hs, home)

    return teams


# ---------------------------------------------------------------------------
# Head-to-head helpers
# ---------------------------------------------------------------------------


def h2h_win_pct(team: Team, opponents: list[str]) -> float:
    """Win percentage in head-to-head games against a specific set of opponents."""
    wins = losses = 0
    for opp in opponents:
        w, l, _ = team.h2h.get(opp, [0, 0, 0])
        wins += w
        losses += l
    total = wins + losses
    return wins / total if total else 0.0


def h2h_score_diff(team: Team, opponents: list[str]) -> int:
    """Total raw score differential in head-to-head games against opponents."""
    diff = 0
    for opp in opponents:
        _, _, d = team.h2h.get(opp, [0, 0, 0])
        diff += d
    return diff


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------


def _sort_key(team: Team, tied_opponents: Optional[list[str]] = None) -> tuple:
    """
    Primary sort key for a team.
    tied_opponents is used for head-to-head sub-ranking within a tied group.
    """
    opponents = tied_opponents or []
    return (
        team.win_pct,               # 1) overall W%
        team.conf_win_pct,          # 2) conference W%
        h2h_win_pct(team, opponents),   # 3) H2H W% vs tied teams
        h2h_score_diff(team, opponents),  # 4) H2H score diff vs tied teams
        team.score_diff,            # 5) overall score differential (capped)
    )


def _resolve_ties(tied: list[Team]) -> list[Team]:
    """
    Recursively resolve ties within a group using head-to-head criteria.
    Returns the group in ranked order.
    """
    if len(tied) <= 1:
        return tied

    opponents = [t.name for t in tied]

    # Sort by H2H criteria among the tied group
    sorted_group = sorted(tied, key=lambda t: _sort_key(t, opponents), reverse=True)

    # Check if the sort actually differentiated anyone
    # Group them again by the same key to detect remaining ties
    result: list[Team] = []
    i = 0
    while i < len(sorted_group):
        j = i + 1
        while j < len(sorted_group) and _sort_key(sorted_group[i], opponents) == _sort_key(sorted_group[j], opponents):
            j += 1
        sub_group = sorted_group[i:j]
        if len(sub_group) > 1 and len(sub_group) < len(tied):
            # Subset is still tied but smaller — recurse
            result.extend(_resolve_ties(sub_group))
        else:
            result.extend(sub_group)
        i = j

    return result


def rank_teams(data: dict) -> list[tuple[int, Team]]:
    """
    Rank all 5th Grade Girls teams across all conferences.

    Returns a list of (rank, Team) tuples in ranked order.
    Ties at the same rank share the same rank number.
    """
    teams = build_teams(data)

    if not teams:
        return []

    all_teams = list(teams.values())

    # First pass: sort by primary criteria (overall W%, conf W%)
    all_teams.sort(key=lambda t: (t.win_pct, t.conf_win_pct), reverse=True)

    # Second pass: resolve ties with H2H + diff
    final_order: list[Team] = []
    i = 0
    while i < len(all_teams):
        j = i + 1
        while (
            j < len(all_teams)
            and all_teams[i].win_pct == all_teams[j].win_pct
            and all_teams[i].conf_win_pct == all_teams[j].conf_win_pct
        ):
            j += 1
        group = all_teams[i:j]
        final_order.extend(_resolve_ties(group) if len(group) > 1 else group)
        i = j

    # Assign ranks (ties get the same rank)
    ranked: list[tuple[int, Team]] = []
    rank = 1
    for idx, team in enumerate(final_order):
        if idx > 0:
            prev = final_order[idx - 1]
            if _sort_key(team, []) != _sort_key(prev, []):
                rank = idx + 1
        ranked.append((rank, team))

    return ranked


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def format_rankings(
    ranked: list[tuple[int, Team]],
    show_h2h: bool = False,
    division: str = "5th Grade",
    gender: str = "Girls",
) -> str:
    """Produce a formatted string of the rankings table."""
    if not ranked:
        return "No teams found. Check your data source."

    title = f"DPL {division} {gender} Basketball — Cross-Conference Rankings"
    width = max(78, len(title) + 4)

    lines = [
        "",
        "=" * width,
        f"  {title}",
        "=" * width,
        f"  {'Rank':<6} {'Team':<28} {'Conf':<20} {'W-L':>5} {'Conf W-L':>9} {'Diff/G':>7}",
        "-" * width,
    ]

    for rank, team in ranked:
        wl = f"{team.wins}-{team.losses}"
        conf_wl = f"{team.conference_wins}-{team.conference_losses}"
        diff = f"{team.score_diff:+.1f}" if team.games_played else "  n/a"
        lines.append(
            f"  {rank:<6} {team.name:<28} {team.conference:<20} {wl:>5} {conf_wl:>9} {diff:>7}"
        )

    lines.append("=" * width)
    lines.append("")
    lines.append("  Ranking criteria (in order):")
    lines.append("    1. Overall win percentage")
    lines.append("    2. Conference win percentage")
    lines.append("    3. Head-to-head win % (among tied teams)")
    lines.append("    4. Head-to-head score differential (among tied teams)")
    lines.append(f"    5. Overall score differential (capped at ±{MAX_DIFF_PER_GAME} pts/game)")
    lines.append("")

    if show_h2h:
        lines.append("-" * width)
        lines.append("  Head-to-Head Summary")
        lines.append("-" * width)
        for _, team in ranked:
            if team.h2h:
                lines.append(f"  {team.name}:")
                for opp, (w, l, d) in sorted(team.h2h.items()):
                    lines.append(f"    vs {opp:<26} {w}W-{l}L  (diff: {d:+d})")
        lines.append("")

    return "\n".join(lines)
