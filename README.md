# DPL Basketball Rankings

Cross-conference ranking tool for **Dallas Parochial League 7th Grade Division 2 Boys** basketball.

## Ranking Criteria

Teams are ranked across all conferences using the following tiebreakers (in order):

1. **Overall win percentage**
2. **Conference win percentage**
3. **Head-to-head win %** (among tied teams only)
4. **Head-to-head score differential** (among tied teams only)
5. **Overall score differential** — capped at ±20 pts per game to limit blowout distortion

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# (Optional) Install Playwright if the DPL site requires JS rendering
pip install playwright && playwright install chromium

# Run with live data from DPL website
python main.py

# Run with cached data (skip network fetch)
python main.py --use-cache

# Run with sample/demo data
python main.py --load sample

# Show head-to-head breakdown
python main.py --use-cache --h2h

# Save fetched data to a custom file
python main.py --save data/2026-02-21.json
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point — orchestrates fetch + rank + display |
| `scraper.py` | Fetches standings and results from dallasparochialleague.com |
| `ranker.py` | Ranking algorithm implementation |
| `data/sample_data.json` | Illustrative data for testing (not real DPL data) |
| `data/dpl_data.json` | Auto-generated cache of the last live fetch |

## Data Source

Live data is pulled from:
- **Standings:** https://www.dallasparochialleague.com/basketball-standings
- **Schedule/Results:** https://www.dallasparochialleague.com/basketball-schedule-results

The DPL website renders content via JavaScript. If plain HTTP requests fail,
the scraper automatically falls back to **Playwright** (headless Chromium) to
render the page before parsing.

## Updating Data

Run `python main.py` at any point during the season to pull the latest standings
and recalculate rankings. Data is cached in `data/dpl_data.json`.

## Notes

- The DPL website may require Playwright to render JavaScript content. Install it with:
  `pip install playwright && playwright install chromium`
- All 7GD2 teams advance to the playoffs, so cross-conference ranking is important for seeding.

---

## March Madness Bracket Pool

A pick-every-game bracket pool with four scoring categories:

| Category | How it works |
|----------|-------------|
| **Overall Win-Loss** | 1 point per correct game pick across all 63 games. Best record wins. |
| **Sleeper** | Pick one underdog team. Points = seed number x that team's tournament wins. (e.g. 12-seed with 2 wins = 24 pts) |
| **Final Four** | Pick 4 teams to reach the Final Four. 1 point per correct team. |
| **Champion** | Pick the overall tournament winner. |

### Setup

**1. Fill in the bracket** — Edit `march_madness/bracket.py` with the actual teams once the bracket is announced. Update the `REGIONS` dict with team names for each seed.

**2. Generate the pick template:**
```bash
python -m march_madness.pool template
# or specify an output path:
python -m march_madness.pool template --output my_pool.csv
```

**3. Share with entrants via Google Sheets:**
- Import the CSV into Google Sheets (File → Import)
- Make a copy of the sheet for each entrant (or use one sheet per tab)
- Share the sheet — each person fills in the "Your Pick" column
- Once picks are locked, download each entrant's sheet as CSV

**4. Record results** — As games are played, fill in the "Your Pick (winner)" column of a results CSV with actual winners.

**5. Score the pool:**
```bash
python -m march_madness.pool score --picks entrant1.csv entrant2.csv --results results.csv
# or use a glob:
python -m march_madness.pool score --picks picks/*.csv --results results.csv
```

### Files

| File | Purpose |
|------|---------|
| `march_madness/bracket.py` | Bracket structure — 4 regions, 16 seeds each. **Edit this with actual teams.** |
| `march_madness/scorer.py` | Scoring engine for all 4 categories |
| `march_madness/sheets.py` | CSV template generation and pick/result parsing |
| `march_madness/pool.py` | CLI entry point (`python -m march_madness.pool`) |
