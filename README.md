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
