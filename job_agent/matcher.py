"""
Job Search Agent — Job Matcher / Scorer

Scores each job against James's profile using keyword matching,
location preference, seniority level, salary, and equity signals.
"""

import re
import logging

from config import (
    TIER1_KEYWORDS,
    TIER2_KEYWORDS,
    TIER3_KEYWORDS,
    LEGAL_TECH_VENDORS,
    PREFERRED_LOCATIONS,
    ACCEPTABLE_LOCATIONS,
    EXCLUDE_TITLE_KEYWORDS,
    PROFILE,
    SCORING,
)

logger = logging.getLogger(__name__)


def _text_contains(text: str, keyword: str) -> bool:
    """Case-insensitive check if keyword appears in text."""
    return keyword.lower() in text.lower()


def _count_keyword_matches(text: str, keywords: list[str]) -> tuple[int, list[str]]:
    """Count how many keywords appear in the text. Return count and matched list."""
    matched = [kw for kw in keywords if _text_contains(text, kw)]
    return len(matched), matched


def score_job(job: dict) -> dict:
    """
    Score a job posting against the profile.

    Returns the job dict with added fields:
        - score: int (composite score)
        - score_breakdown: dict of component scores
        - matched_keywords: list of matched keywords
        - excluded: bool (True if job should be filtered out)
        - exclude_reason: str (why it was excluded, if applicable)
    """
    title = job.get("title", "")
    description = job.get("description", "")
    location = job.get("location", "")
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")
    searchable_text = f"{title} {description}"

    # ------------------------------------------------------------------
    # Check exclusions first
    # ------------------------------------------------------------------
    title_lower = title.lower()
    for exclude_kw in EXCLUDE_TITLE_KEYWORDS:
        if exclude_kw.lower() in title_lower:
            job["score"] = 0
            job["score_breakdown"] = {}
            job["matched_keywords"] = []
            job["excluded"] = True
            job["exclude_reason"] = f"Title contains excluded keyword: '{exclude_kw}'"
            return job

    # ------------------------------------------------------------------
    # Keyword scoring (Tiers 1-3: resume skills, Tier 4: legal tech vendors)
    # ------------------------------------------------------------------
    t1_count, t1_matched = _count_keyword_matches(searchable_text, TIER1_KEYWORDS)
    t2_count, t2_matched = _count_keyword_matches(searchable_text, TIER2_KEYWORDS)
    t3_count, t3_matched = _count_keyword_matches(searchable_text, TIER3_KEYWORDS)
    vendor_count, vendor_matched = _count_keyword_matches(searchable_text, LEGAL_TECH_VENDORS)

    keyword_score = (
        t1_count * SCORING["tier1_keyword_weight"]
        + t2_count * SCORING["tier2_keyword_weight"]
        + t3_count * SCORING["tier3_keyword_weight"]
        + vendor_count * SCORING["vendor_keyword_weight"]
    )

    # ------------------------------------------------------------------
    # Location scoring
    # ------------------------------------------------------------------
    location_score = 0
    location_lower = location.lower()
    if any(loc.lower() in location_lower for loc in PREFERRED_LOCATIONS):
        location_score = SCORING["preferred_location_bonus"]
    elif any(loc.lower() in location_lower for loc in ACCEPTABLE_LOCATIONS):
        location_score = SCORING["acceptable_location_bonus"]
    elif "remote" in location_lower or "anywhere" in location_lower:
        location_score = SCORING["acceptable_location_bonus"]

    # ------------------------------------------------------------------
    # Seniority scoring
    # ------------------------------------------------------------------
    seniority_score = 0
    seniority_patterns = [
        r"general counsel",
        r"deputy general counsel",
        r"associate general counsel",
        r"chief legal",
        r"CLO",
        r"VP.*legal",
        r"vice president.*legal",
        r"SVP.*legal",
        r"senior vice president.*legal",
        r"head of legal",
        r"director.*legal",
    ]
    for pattern in seniority_patterns:
        if re.search(pattern, title, re.IGNORECASE):
            seniority_score = SCORING["seniority_match_bonus"]
            break

    # ------------------------------------------------------------------
    # Salary scoring
    # ------------------------------------------------------------------
    salary_score = 0
    if salary_min and salary_min >= PROFILE["salary_floor"]:
        salary_score = SCORING["salary_meets_floor_bonus"]
    elif salary_max and salary_max >= PROFILE["salary_floor"]:
        salary_score = SCORING["salary_meets_floor_bonus"]

    # ------------------------------------------------------------------
    # Equity / LTI bonus
    # ------------------------------------------------------------------
    equity_score = 0
    equity_terms = ["equity", "stock", "RSU", "long-term incentive", "LTI", "shares", "option grant"]
    if any(_text_contains(searchable_text, term) for term in equity_terms):
        equity_score = SCORING["equity_mention_bonus"]

    # ------------------------------------------------------------------
    # Composite score
    # ------------------------------------------------------------------
    total_score = keyword_score + location_score + seniority_score + salary_score + equity_score

    job["score"] = total_score
    job["score_breakdown"] = {
        "keywords": keyword_score,
        "location": location_score,
        "seniority": seniority_score,
        "salary": salary_score,
        "equity": equity_score,
    }
    job["matched_keywords"] = t1_matched + t2_matched + t3_matched + vendor_matched
    job["excluded"] = False
    job["exclude_reason"] = ""

    return job


def rank_jobs(jobs: list[dict]) -> list[dict]:
    """
    Score all jobs, filter exclusions and low scores, sort by score descending.
    """
    scored = [score_job(job) for job in jobs]

    # Filter out excluded jobs and those below threshold
    threshold = SCORING["minimum_score_threshold"]
    qualified = [
        j for j in scored
        if not j.get("excluded") and j.get("score", 0) >= threshold
    ]

    # Sort by score descending, then by date posted (newest first)
    qualified.sort(key=lambda j: (j["score"], j.get("date_posted") or ""), reverse=True)

    logger.info(
        "Scoring complete: %d total, %d excluded, %d below threshold, %d qualified",
        len(scored),
        sum(1 for j in scored if j.get("excluded")),
        sum(1 for j in scored if not j.get("excluded") and j.get("score", 0) < threshold),
        len(qualified),
    )

    return qualified
