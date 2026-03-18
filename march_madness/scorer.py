"""
March Madness pool scoring engine.

Scoring categories
------------------
1. **Overall Win-Loss**: 1 point per correct game pick across all 63 games.
   Winner = best record (wins, then fewest losses as tiebreak).

2. **Sleeper**: Each entrant picks one underdog team as their sleeper.
   Sleeper points = team's seed number x number of tournament wins that team
   actually earns.  (e.g. a 12-seed that wins 2 games = 24 pts)

3. **Final Four**: Each entrant picks 4 teams to reach the Final Four.
   1 point per correct Final Four team (max 4).

4. **Champion**: Each entrant picks the overall tournament winner.
   Correct = 1, Incorrect = 0.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class EntrantPicks:
    """One pool entrant's complete set of picks."""
    name: str
    # game_id -> picked winner (team name)
    game_picks: dict[str, str] = field(default_factory=dict)
    sleeper_team: str = ""
    final_four: list[str] = field(default_factory=list)
    champion: str = ""


@dataclass
class TournamentResults:
    """Actual tournament results, updated as games are played."""
    # game_id -> winning team name
    game_winners: dict[str, str] = field(default_factory=dict)
    # team name -> number of tournament wins
    team_wins: dict[str, int] = field(default_factory=dict)
    # teams that actually made the Final Four
    final_four_teams: list[str] = field(default_factory=list)
    # actual champion
    champion: str = ""
    # team name -> (region, seed)
    team_seeds: dict[str, tuple[str, int]] = field(default_factory=dict)


@dataclass
class EntrantScore:
    """Computed scores for one entrant across all categories."""
    name: str
    # Win-Loss
    correct_picks: int = 0
    total_decided: int = 0  # games played so far
    total_games: int = 63
    # Sleeper
    sleeper_team: str = ""
    sleeper_seed: int = 0
    sleeper_team_wins: int = 0
    sleeper_points: int = 0
    # Final Four
    final_four_correct: int = 0
    final_four_picks: list[str] = field(default_factory=list)
    # Champion
    champion_pick: str = ""
    champion_correct: bool = False

    @property
    def win_pct(self) -> float:
        return self.correct_picks / self.total_decided if self.total_decided else 0.0


def score_entrant(picks: EntrantPicks, results: TournamentResults) -> EntrantScore:
    """Score a single entrant against current results."""
    score = EntrantScore(name=picks.name)

    # --- Win-Loss ---
    for game_id, winner in results.game_winners.items():
        score.total_decided += 1
        picked = picks.game_picks.get(game_id, "")
        if picked.strip().lower() == winner.strip().lower():
            score.correct_picks += 1

    # --- Sleeper ---
    score.sleeper_team = picks.sleeper_team
    seed_info = results.team_seeds.get(picks.sleeper_team)
    if seed_info:
        score.sleeper_seed = seed_info[1]
    score.sleeper_team_wins = results.team_wins.get(picks.sleeper_team, 0)
    score.sleeper_points = score.sleeper_seed * score.sleeper_team_wins

    # --- Final Four ---
    score.final_four_picks = picks.final_four
    actual_ff = {t.strip().lower() for t in results.final_four_teams}
    for team in picks.final_four:
        if team.strip().lower() in actual_ff:
            score.final_four_correct += 1

    # --- Champion ---
    score.champion_pick = picks.champion
    if results.champion:
        score.champion_correct = (
            picks.champion.strip().lower() == results.champion.strip().lower()
        )

    return score


def score_pool(
    all_picks: list[EntrantPicks], results: TournamentResults
) -> dict[str, list[EntrantScore]]:
    """
    Score all entrants and return category leaderboards.

    Returns dict with keys:
        "win_loss"  — sorted by correct picks desc
        "sleeper"   — sorted by sleeper points desc
        "final_four" — sorted by final four correct desc
        "champion"  — sorted by champion correct desc
        "all"       — unsorted full list
    """
    scores = [score_entrant(p, results) for p in all_picks]

    return {
        "win_loss": sorted(scores, key=lambda s: s.correct_picks, reverse=True),
        "sleeper": sorted(scores, key=lambda s: s.sleeper_points, reverse=True),
        "final_four": sorted(
            scores, key=lambda s: s.final_four_correct, reverse=True
        ),
        "champion": sorted(
            scores, key=lambda s: (s.champion_correct, s.correct_picks), reverse=True
        ),
        "all": scores,
    }


def format_standings(leaderboards: dict[str, list[EntrantScore]]) -> str:
    """Format all leaderboards as a printable string."""
    lines = []

    # --- Win-Loss ---
    lines.append("=" * 60)
    lines.append("OVERALL WIN-LOSS STANDINGS")
    lines.append("=" * 60)
    for i, s in enumerate(leaderboards["win_loss"], 1):
        games_left = s.total_games - s.total_decided
        lines.append(
            f"  {i:>2}. {s.name:<20s}  {s.correct_picks:>2}-{s.total_decided - s.correct_picks:<2d}"
            f"  ({s.correct_picks}/{s.total_decided} decided"
            f", {games_left} remaining)"
        )
    lines.append("")

    # --- Sleeper ---
    lines.append("=" * 60)
    lines.append("SLEEPER STANDINGS  (seed x wins)")
    lines.append("=" * 60)
    for i, s in enumerate(leaderboards["sleeper"], 1):
        lines.append(
            f"  {i:>2}. {s.name:<20s}  {s.sleeper_points:>3d} pts"
            f"  ({s.sleeper_team} #{s.sleeper_seed}"
            f", {s.sleeper_team_wins} wins)"
        )
    lines.append("")

    # --- Final Four ---
    lines.append("=" * 60)
    lines.append("FINAL FOUR STANDINGS")
    lines.append("=" * 60)
    for i, s in enumerate(leaderboards["final_four"], 1):
        picks_str = ", ".join(s.final_four_picks) if s.final_four_picks else "(none)"
        lines.append(
            f"  {i:>2}. {s.name:<20s}  {s.final_four_correct}/4 correct"
            f"  — picks: {picks_str}"
        )
    lines.append("")

    # --- Champion ---
    lines.append("=" * 60)
    lines.append("CHAMPION PICK")
    lines.append("=" * 60)
    for i, s in enumerate(leaderboards["champion"], 1):
        status = "CORRECT" if s.champion_correct else ("pending" if not leaderboards["champion"][0].champion_correct and not any(x.champion_correct for x in leaderboards["champion"]) else "wrong")
        # Simplify: if no champion decided yet, show "pending"
        lines.append(
            f"  {i:>2}. {s.name:<20s}  {s.champion_pick:<20s}  {status}"
        )
    lines.append("")

    return "\n".join(lines)
