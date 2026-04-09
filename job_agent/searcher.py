"""
Job Search Agent — Job Searcher

Queries job search APIs and returns normalized job listings.
Primary source: Serper.dev (Google Search API — 2,500 free searches)
Optional: JSearch (RapidAPI), Adzuna
"""

import json
import hashlib
import logging
import re
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

from config import (
    SERPER_API_KEY,
    JSEARCH_API_KEY,
    ADZUNA_APP_ID,
    ADZUNA_APP_KEY,
    SEARCH_QUERIES,
    PREFERRED_LOCATIONS,
    DATA_DIR,
    SEEN_JOBS_FILE,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Normalized job schema
# ---------------------------------------------------------------------------

def make_job(
    title: str,
    company: str,
    location: str,
    description: str,
    url: str,
    salary_min: int | None = None,
    salary_max: int | None = None,
    date_posted: str | None = None,
    source: str = "unknown",
) -> dict:
    """Create a normalized job dict."""
    job_id = hashlib.md5(f"{title}|{company}|{url}".encode()).hexdigest()
    return {
        "id": job_id,
        "title": title.strip(),
        "company": company.strip(),
        "location": location.strip() if location else "Not specified",
        "description": description.strip() if description else "",
        "url": url.strip(),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "date_posted": date_posted,
        "source": source,
        "fetched_at": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------------
# Seen-jobs tracking (deduplication across runs)
# ---------------------------------------------------------------------------

def load_seen_jobs() -> dict:
    """Load previously seen job IDs with their first-seen date."""
    if SEEN_JOBS_FILE.exists():
        with open(SEEN_JOBS_FILE) as f:
            return json.load(f)
    return {}


def save_seen_jobs(seen: dict) -> None:
    """Persist seen job IDs."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(seen, f, indent=2)


def filter_new_jobs(jobs: list[dict], seen: dict) -> list[dict]:
    """Return only jobs not previously seen, and update the seen dict."""
    new_jobs = []
    for job in jobs:
        if job["id"] not in seen:
            seen[job["id"]] = datetime.now().isoformat()
            new_jobs.append(job)
    return new_jobs


def prune_seen_jobs(seen: dict, max_age_days: int = 60) -> dict:
    """Remove entries older than max_age_days to prevent unbounded growth."""
    cutoff = (datetime.now() - timedelta(days=max_age_days)).isoformat()
    return {k: v for k, v in seen.items() if v > cutoff}


# ---------------------------------------------------------------------------
# Serper.dev — Primary source (Google Search API)
# Free tier: 2,500 searches total
# Sign up: https://serper.dev/
# ---------------------------------------------------------------------------

def _parse_salary_from_text(text: str) -> tuple[int | None, int | None]:
    """Try to extract salary range from snippet text."""
    # Patterns like "$200,000 - $300,000" or "$200K - $300K"
    pattern = r'\$(\d{1,3}(?:,\d{3})*(?:K)?)\s*[-–to]+\s*\$(\d{1,3}(?:,\d{3})*(?:K)?)'
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None, None

    def parse_amount(s: str) -> int:
        s = s.replace(",", "")
        if s.upper().endswith("K"):
            return int(float(s[:-1]) * 1000)
        return int(s)

    try:
        return parse_amount(match.group(1)), parse_amount(match.group(2))
    except (ValueError, IndexError):
        return None, None


def search_serper(query: str) -> list[dict]:
    """Search Google via Serper.dev for job listings."""
    if not SERPER_API_KEY:
        logger.debug("Serper API key not configured, skipping")
        return []

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "q": query,
        "num": 10,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.warning("Serper request failed for '%s': %s", query, e)
        return []

    jobs = []
    for item in data.get("organic", []):
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        link = item.get("link", "")

        # Skip non-job results
        if not any(kw in title.lower() + snippet.lower() for kw in
                   ["counsel", "attorney", "legal", "lawyer", "general counsel",
                    "privacy", "compliance", "governance"]):
            continue

        # Skip job board index pages (not actual postings)
        if any(skip in link.lower() for skip in
               ["/search?", "/jobs?q=", "/salary/", "/salaries/", "/company/"]):
            continue

        # Try to extract company from title patterns like "... at CompanyName"
        company = ""
        for sep in [" at ", " - ", " | "]:
            if sep in title:
                parts = title.split(sep)
                if len(parts) >= 2:
                    company = parts[-1].strip()
                    title = sep.join(parts[:-1]).strip()
                break

        # Try to extract location from snippet
        location = "Not specified"
        loc_match = re.search(
            r'(Dallas|Frisco|Plano|Irving|Fort Worth|Austin|Houston|'
            r'San Francisco|New York|Remote|Hybrid|Los Angeles|Chicago|'
            r'Washington|Culver City|Tempe|Minneapolis|Birmingham)'
            r'(?:[,\s]+(?:TX|CA|NY|AZ|MN|AL|DC|IL))?',
            snippet, re.IGNORECASE
        )
        if loc_match:
            location = loc_match.group(0)

        # Try to parse salary from snippet
        salary_min, salary_max = _parse_salary_from_text(snippet)

        # Extract date if present
        date_posted = None
        date_match = re.search(r'(\d{1,2})\s+(days?|hours?)\s+ago', snippet, re.IGNORECASE)
        if date_match:
            days_ago = int(date_match.group(1))
            if "hour" in date_match.group(2).lower():
                days_ago = 0
            date_posted = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        jobs.append(make_job(
            title=title,
            company=company,
            location=location,
            description=snippet,
            url=link,
            salary_min=salary_min,
            salary_max=salary_max,
            date_posted=date_posted,
            source="Google (Serper)",
        ))

    return jobs


# ---------------------------------------------------------------------------
# JSearch API (RapidAPI) — optional secondary source
# ---------------------------------------------------------------------------

def search_jsearch(query: str, location: str = "Dallas, TX", page: int = 1) -> list[dict]:
    """Search JSearch API for job listings."""
    if not JSEARCH_API_KEY:
        return []

    url = "https://jsearch.p.rapidapi.com/search"
    params = {
        "query": f"{query} in {location}",
        "page": str(page),
        "num_pages": "1",
        "date_posted": "week",
        "remote_jobs_only": "false",
    }
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.warning("JSearch request failed for '%s': %s", query, e)
        return []

    jobs = []
    for item in data.get("data", []):
        salary_min = int(item["job_min_salary"]) if item.get("job_min_salary") else None
        salary_max = int(item["job_max_salary"]) if item.get("job_max_salary") else None

        jobs.append(make_job(
            title=item.get("job_title", ""),
            company=item.get("employer_name", ""),
            location=f"{item.get('job_city', '')}, {item.get('job_state', '')}".strip(", "),
            description=item.get("job_description", ""),
            url=item.get("job_apply_link") or item.get("job_google_link", ""),
            salary_min=salary_min,
            salary_max=salary_max,
            date_posted=item.get("job_posted_at_datetime_utc", "")[:10] if item.get("job_posted_at_datetime_utc") else None,
            source="JSearch",
        ))

    return jobs


# ---------------------------------------------------------------------------
# Adzuna API — optional secondary source
# ---------------------------------------------------------------------------

def search_adzuna(query: str, location: str = "Texas") -> list[dict]:
    """Search Adzuna API for job listings."""
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return []

    url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": query,
        "where": location,
        "results_per_page": 20,
        "max_days_old": 7,
        "sort_by": "date",
        "salary_min": 200000,
        "category": "legal-jobs",
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.warning("Adzuna request failed for '%s': %s", query, e)
        return []

    jobs = []
    for item in data.get("results", []):
        salary_min = int(item["salary_min"]) if item.get("salary_min") else None
        salary_max = int(item["salary_max"]) if item.get("salary_max") else None

        jobs.append(make_job(
            title=item.get("title", ""),
            company=item.get("company", {}).get("display_name", ""),
            location=item.get("location", {}).get("display_name", ""),
            description=item.get("description", ""),
            url=item.get("redirect_url", ""),
            salary_min=salary_min,
            salary_max=salary_max,
            date_posted=item.get("created", "")[:10] if item.get("created") else None,
            source="Adzuna",
        ))

    return jobs


# ---------------------------------------------------------------------------
# Main search orchestrator
# ---------------------------------------------------------------------------

def deduplicate_jobs(jobs: list[dict]) -> list[dict]:
    """Remove duplicate jobs based on ID (title + company + url hash)."""
    seen_ids = set()
    unique = []
    for job in jobs:
        if job["id"] not in seen_ids:
            seen_ids.add(job["id"])
            unique.append(job)
    return unique


def run_all_searches(rate_limit_delay: float = 1.0) -> list[dict]:
    """
    Run all configured search queries across all sources.
    Returns a deduplicated list of normalized job dicts.
    """
    all_jobs = []
    sources_used = []

    has_serper = bool(SERPER_API_KEY)
    has_jsearch = bool(JSEARCH_API_KEY)
    has_adzuna = bool(ADZUNA_APP_ID and ADZUNA_APP_KEY)

    if not has_serper and not has_jsearch and not has_adzuna:
        logger.error(
            "No job search APIs configured. Set SERPER_API_KEY, "
            "JSEARCH_API_KEY, or ADZUNA_APP_ID/ADZUNA_APP_KEY."
        )
        return []

    # Select a subset of queries to stay within rate limits
    # Serper: 2,500 total (generous); rotate 6 queries/day
    day_of_month = datetime.now().day
    queries_per_day = 6
    start_idx = (day_of_month * queries_per_day) % len(SEARCH_QUERIES)
    daily_queries = []
    for i in range(queries_per_day):
        daily_queries.append(SEARCH_QUERIES[(start_idx + i) % len(SEARCH_QUERIES)])

    logger.info("Today's search queries: %s", daily_queries)

    # Serper (Google Search) — primary source
    if has_serper:
        sources_used.append("Serper")
        for query in daily_queries:
            # Add "job posting" to help Google surface actual listings
            search_query = f'{query} job posting Dallas OR remote'
            jobs = search_serper(search_query)
            all_jobs.extend(jobs)
            logger.info("Serper '%s': %d results", query, len(jobs))
            time.sleep(rate_limit_delay)

    # JSearch — optional secondary
    if has_jsearch:
        sources_used.append("JSearch")
        for query in daily_queries[:4]:
            jobs = search_jsearch(query, location="Dallas, TX")
            all_jobs.extend(jobs)
            logger.info("JSearch '%s': %d results", query, len(jobs))
            time.sleep(rate_limit_delay)

    # Adzuna — optional secondary
    if has_adzuna:
        sources_used.append("Adzuna")
        for query in daily_queries[:3]:
            jobs = search_adzuna(query, location="Texas")
            all_jobs.extend(jobs)
            logger.info("Adzuna '%s': %d results", query, len(jobs))
            time.sleep(rate_limit_delay)

    # Deduplicate
    unique_jobs = deduplicate_jobs(all_jobs)
    logger.info(
        "Search complete: %d total results, %d unique (sources: %s)",
        len(all_jobs), len(unique_jobs), ", ".join(sources_used),
    )

    return unique_jobs
