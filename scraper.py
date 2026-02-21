"""
DPL Basketball Data Scraper
Fetches standings and game results for 5th Grade Girls from the
Dallas Parochial League website (https://www.dallasparochialleague.com).

The DPL site renders content dynamically via JavaScript (Squarespace/Doodlio).
This scraper uses requests-html or Playwright to render JavaScript before parsing.

Usage:
    python scraper.py                   # Fetch live data and save to data/dpl_data.json
    python scraper.py --use-cache       # Use previously saved data (skip network fetch)
"""

import json
import re
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STANDINGS_URL = "https://www.dallasparochialleague.com/basketball-standings"
SCHEDULE_URL = "https://www.dallasparochialleague.com/basketball-schedule-results"

TARGET_DIVISION = "5th Grade"                  # adjust if label differs on site
TARGET_GENDER = "Girls"
DATA_DIR = Path(__file__).parent / "data"
CACHE_FILE = DATA_DIR / "dpl_data.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# ---------------------------------------------------------------------------
# Scraping helpers
# ---------------------------------------------------------------------------


def _get_html_requests(url: str) -> str:
    """Fetch page HTML using plain requests (works for server-rendered pages)."""
    import requests

    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def _get_html_playwright(url: str) -> str:
    """Fetch fully-rendered HTML using Playwright (handles JavaScript sites)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=60_000)
        # Give extra time for async data to load
        time.sleep(3)
        html = page.content()
        browser.close()
    return html


def get_html(url: str) -> str:
    """Try requests first; fall back to Playwright if JS rendering is needed."""
    try:
        html = _get_html_requests(url)
        # Heuristic: if the page has essentially no real content it's JS-only
        if len(html) < 5_000 or "standings" not in html.lower():
            raise ValueError("Page appears to require JavaScript rendering")
        return html
    except Exception as exc:
        print(f"  Plain request failed ({exc}); trying Playwright …", file=sys.stderr)
        try:
            return _get_html_playwright(url)
        except ImportError:
            print(
                "  Playwright not installed. Run:  pip install playwright && playwright install chromium",
                file=sys.stderr,
            )
            raise


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def parse_standings(html: str) -> dict[str, list[dict]]:
    """
    Parse the standings page HTML.

    Returns a dict keyed by conference name, each value a list of team dicts:
        {
          "team": "St. Rita",
          "wins": 5,
          "losses": 1,
          "conference_wins": 4,
          "conference_losses": 1,
          "conference": "Conference A",
        }
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    conferences: dict[str, list[dict]] = {}

    # The DPL site uses section headings to separate divisions/conferences.
    # We scan for headings that mention our target division and then collect
    # the table or list that follows.

    in_target_division = False
    current_conf = None

    for tag in soup.find_all(True):
        text = tag.get_text(strip=True)

        # Detect division header
        if tag.name in ("h2", "h3", "h4") and TARGET_DIVISION.lower() in text.lower() and TARGET_GENDER.lower() in text.lower():
            in_target_division = True
            continue

        # Detect next division header (exit)
        if tag.name in ("h2", "h3") and in_target_division and text and TARGET_DIVISION.lower() not in text.lower():
            # Only exit if it looks like another division heading
            if re.search(r"\d+(st|nd|rd|th)\s+grade", text, re.IGNORECASE):
                in_target_division = False
                current_conf = None
                continue

        if not in_target_division:
            continue

        # Detect conference sub-header
        if tag.name in ("h4", "h5", "strong", "b") and "conference" in text.lower():
            current_conf = text.strip()
            conferences.setdefault(current_conf, [])
            continue

        # Detect table rows
        if tag.name == "tr":
            cells = [td.get_text(strip=True) for td in tag.find_all(["td", "th"])]
            if len(cells) >= 3 and cells[0] and not cells[0].lower().startswith("team"):
                try:
                    conf_key = current_conf or "Unknown Conference"
                    # Typical columns: Team | W | L  or  Team | W-L | ...
                    team_name = cells[0]
                    wins, losses = _parse_wl(cells[1], cells[2] if len(cells) > 2 else None)
                    conf_wins, conf_losses = (
                        _parse_wl(cells[3], cells[4] if len(cells) > 4 else None)
                        if len(cells) > 4
                        else (wins, losses)
                    )
                    conferences.setdefault(conf_key, []).append(
                        {
                            "team": team_name,
                            "wins": wins,
                            "losses": losses,
                            "conference_wins": conf_wins,
                            "conference_losses": conf_losses,
                            "conference": conf_key,
                        }
                    )
                except (ValueError, IndexError):
                    pass

    return conferences


def _parse_wl(w_cell: str, l_cell: str | None) -> tuple[int, int]:
    """Parse wins and losses from table cells. Handles '3-1' or separate '3','1'."""
    if "-" in w_cell:
        parts = w_cell.split("-")
        return int(parts[0]), int(parts[1])
    return int(w_cell), int(l_cell or "0")


def parse_schedule(html: str) -> list[dict]:
    """
    Parse the schedule/results page HTML.

    Returns a list of game dicts:
        {
          "date": "2026-01-17",
          "home_team": "St. Rita",
          "away_team": "Ursuline",
          "home_score": 42,
          "away_score": 31,
          "division": "7GD2",
          "conference": "Conference A",
        }

    Only returns completed games (both scores present) for our target division.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    games: list[dict] = []

    in_target_division = False
    current_conf = None
    current_date = None

    for tag in soup.find_all(True):
        text = tag.get_text(strip=True)

        # Division header detection
        if tag.name in ("h2", "h3", "h4") and TARGET_DIVISION.lower() in text.lower() and TARGET_GENDER.lower() in text.lower():
            in_target_division = True
            continue

        if tag.name in ("h2", "h3") and in_target_division and text:
            if re.search(r"\d+(st|nd|rd|th)\s+grade", text, re.IGNORECASE) and TARGET_DIVISION.lower() not in text.lower():
                in_target_division = False
                current_conf = None
                current_date = None
                continue

        if not in_target_division:
            continue

        # Date header
        date_match = re.search(r"(\w+ \d{1,2},?\s*\d{4})", text)
        if tag.name in ("h4", "h5", "strong", "b") and date_match:
            try:
                current_date = datetime.strptime(date_match.group(1).replace(",", ""), "%B %d %Y").strftime("%Y-%m-%d")
            except ValueError:
                pass
            continue

        # Conference sub-header
        if tag.name in ("h4", "h5", "strong", "b") and "conference" in text.lower():
            current_conf = text.strip()
            continue

        # Game rows: typically "Team A  42 – Team B  31" or table rows
        if tag.name == "tr":
            cells = [td.get_text(strip=True) for td in tag.find_all(["td", "th"])]
            game = _try_parse_game_row(cells, current_conf, current_date)
            if game:
                games.append(game)
            continue

        # Inline text patterns like "St. Rita 42, Ursuline 31"
        game = _try_parse_game_text(text, current_conf, current_date)
        if game:
            games.append(game)

    return games


def _try_parse_game_row(cells: list[str], conference: str | None, date: str | None) -> dict | None:
    """Attempt to parse a 4-cell game row: [away_team, away_score, home_team, home_score]."""
    if len(cells) < 4:
        return None
    try:
        away_team, away_score_s, home_team, home_score_s = cells[0], cells[1], cells[2], cells[3]
        away_score = int(re.sub(r"\D", "", away_score_s))
        home_score = int(re.sub(r"\D", "", home_score_s))
        if not away_team or not home_team:
            return None
        return {
            "date": date,
            "home_team": home_team.strip(),
            "away_team": away_team.strip(),
            "home_score": home_score,
            "away_score": away_score,
            "conference": conference,
        }
    except (ValueError, IndexError):
        return None


def _try_parse_game_text(text: str, conference: str | None, date: str | None) -> dict | None:
    """Attempt to parse inline game result text like 'St. Rita 42, Ursuline 31'."""
    # Pattern: <team name> <score>, <team name> <score>
    pattern = r"^(.+?)\s+(\d+)[,–-]\s*(.+?)\s+(\d+)$"
    m = re.match(pattern, text.strip())
    if not m:
        return None
    team1, score1, team2, score2 = m.group(1).strip(), int(m.group(2)), m.group(3).strip(), int(m.group(4))
    if team1 == team2:
        return None
    return {
        "date": date,
        "home_team": team1,
        "away_team": team2,
        "home_score": score1,
        "away_score": score2,
        "conference": conference,
    }


# ---------------------------------------------------------------------------
# Main fetch routine
# ---------------------------------------------------------------------------


def fetch_dpl_data() -> dict:
    """Fetch standings and schedule from the DPL website and return combined data."""
    print("Fetching standings …")
    standings_html = get_html(STANDINGS_URL)
    conferences = parse_standings(standings_html)

    print("Fetching schedule/results …")
    schedule_html = get_html(SCHEDULE_URL)
    games = parse_schedule(schedule_html)

    return {
        "fetched_at": datetime.now().isoformat(),
        "division": TARGET_DIVISION,
        "gender": TARGET_GENDER,
        "conferences": conferences,
        "games": games,
        "_note": "DPL site uses JavaScript rendering (Doodlio). If conferences is empty, use --use-cache with a manually built JSON file.",
    }


def load_or_fetch(use_cache: bool = False) -> dict:
    """Load data from cache file or fetch fresh data."""
    DATA_DIR.mkdir(exist_ok=True)

    if use_cache and CACHE_FILE.exists():
        print(f"Loading cached data from {CACHE_FILE} …")
        with open(CACHE_FILE) as f:
            return json.load(f)

    data = fetch_dpl_data()
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {CACHE_FILE}")
    return data


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Scrape DPL basketball data")
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Use previously cached data instead of fetching live",
    )
    args = parser.parse_args()

    data = load_or_fetch(use_cache=args.use_cache)

    print(f"\nDivision: {data.get('division', 'Unknown')} {data.get('gender', '')}")
    print(f"Conferences found: {list(data['conferences'].keys())}")
    total_teams = sum(len(v) for v in data["conferences"].values())
    print(f"Total teams: {total_teams}")
    print(f"Games recorded: {len(data['games'])}")


if __name__ == "__main__":
    main()
