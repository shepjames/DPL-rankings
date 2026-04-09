"""
Job Search Agent — Job Searcher

Queries multiple job search APIs and returns normalized job listings.
Supports JSearch (RapidAPI) and Adzuna, with deduplication across sources.
"""

import json
import hashlib
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

from config import (
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
# JSearch API (RapidAPI) — aggregates LinkedIn, Indeed, Glassdoor, etc.
# Free tier: 200 requests/month
# Sign up: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
# ---------------------------------------------------------------------------

def search_jsearch(query: str, location: str = "Dallas, TX", page: int = 1) -> list[dict]:
    """Search JSearch API for job listings."""
    if not JSEARCH_API_KEY:
        logger.debug("JSearch API key not configured, skipping")
        return []

    url = "https://jsearch.p.rapidapi.com/search"
    params = {
        "query": f"{query} in {location}",
        "page": str(page),
        "num_pages": "1",
        "date_posted": "week",  # only recent postings
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
        salary_min = None
        salary_max = None
        if item.get("job_min_salary"):
            salary_min = int(item["job_min_salary"])
        if item.get("job_max_salary"):
            salary_max = int(item["job_max_salary"])

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


def search_jsearch_remote(query: str) -> list[dict]:
    """Search JSearch specifically for remote positions."""
    if not JSEARCH_API_KEY:
        return []

    url = "https://jsearch.p.rapidapi.com/search"
    params = {
        "query": query,
        "page": "1",
        "num_pages": "1",
        "date_posted": "week",
        "remote_jobs_only": "true",
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
        logger.warning("JSearch remote request failed for '%s': %s", query, e)
        return []

    jobs = []
    for item in data.get("data", []):
        salary_min = None
        salary_max = None
        if item.get("job_min_salary"):
            salary_min = int(item["job_min_salary"])
        if item.get("job_max_salary"):
            salary_max = int(item["job_max_salary"])

        jobs.append(make_job(
            title=item.get("job_title", ""),
            company=item.get("employer_name", ""),
            location="Remote",
            description=item.get("job_description", ""),
            url=item.get("job_apply_link") or item.get("job_google_link", ""),
            salary_min=salary_min,
            salary_max=salary_max,
            date_posted=item.get("job_posted_at_datetime_utc", "")[:10] if item.get("job_posted_at_datetime_utc") else None,
            source="JSearch",
        ))

    return jobs


# ---------------------------------------------------------------------------
# Adzuna API — secondary source
# Free tier: 250 calls/month
# Sign up: https://developer.adzuna.com/
# ---------------------------------------------------------------------------

def search_adzuna(query: str, location: str = "Texas") -> list[dict]:
    """Search Adzuna API for job listings."""
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        logger.debug("Adzuna API credentials not configured, skipping")
        return []

    url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": query,
        "where": location,
        "results_per_page": 20,
        "max_days_old": 7,
        "sort_by": "date",
        "salary_min": 200000,  # filter for senior roles
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
        location_name = item.get("location", {}).get("display_name", "")

        jobs.append(make_job(
            title=item.get("title", ""),
            company=item.get("company", {}).get("display_name", ""),
            location=location_name,
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

    # Determine which sources are available
    has_jsearch = bool(JSEARCH_API_KEY)
    has_adzuna = bool(ADZUNA_APP_ID and ADZUNA_APP_KEY)

    if not has_jsearch and not has_adzuna:
        logger.error(
            "No job search APIs configured. Set JSEARCH_API_KEY or "
            "ADZUNA_APP_ID/ADZUNA_APP_KEY environment variables."
        )
        return []

    # Select a subset of queries to stay within rate limits
    # JSearch free tier: 200/month ≈ 6/day; Adzuna: 250/month ≈ 8/day
    # We rotate through queries daily
    day_of_month = datetime.now().day
    queries_per_day = 5
    start_idx = (day_of_month * queries_per_day) % len(SEARCH_QUERIES)
    daily_queries = []
    for i in range(queries_per_day):
        daily_queries.append(SEARCH_QUERIES[(start_idx + i) % len(SEARCH_QUERIES)])

    logger.info("Today's search queries: %s", daily_queries)

    # JSearch — Dallas + Remote
    if has_jsearch:
        sources_used.append("JSearch")
        for query in daily_queries:
            # Dallas-area search
            jobs = search_jsearch(query, location="Dallas, TX")
            all_jobs.extend(jobs)
            logger.info("JSearch [Dallas] '%s': %d results", query, len(jobs))
            time.sleep(rate_limit_delay)

            # Remote search (use fewer queries to save API calls)
            if "AI" in query or "artificial intelligence" in query.lower():
                jobs = search_jsearch_remote(query)
                all_jobs.extend(jobs)
                logger.info("JSearch [Remote] '%s': %d results", query, len(jobs))
                time.sleep(rate_limit_delay)

    # Adzuna
    if has_adzuna:
        sources_used.append("Adzuna")
        for query in daily_queries[:3]:  # use fewer Adzuna queries
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
