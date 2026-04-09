#!/usr/bin/env python3
"""
Job Search Agent — Main Orchestrator

Searches for legal/AI job postings matching the configured profile,
scores and ranks them, generates an HTML report, and emails it.

Usage:
    python main.py                  # Full run: search, score, email
    python main.py --dry-run        # Search and score, but don't send email
    python main.py --preview        # Generate report and open in browser
    python main.py --include-seen   # Include previously seen jobs in report
"""

import argparse
import json
import logging
import sys
import tempfile
import webbrowser
from datetime import datetime
from pathlib import Path

# Ensure job_agent directory is on the path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env file if present (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass  # python-dotenv not installed; rely on actual env vars

from config import DATA_DIR, MAX_JOBS_IN_REPORT
from searcher import run_all_searches, load_seen_jobs, save_seen_jobs, filter_new_jobs, prune_seen_jobs
from matcher import rank_jobs
from report import generate_report
from emailer import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("job_agent")


def main():
    parser = argparse.ArgumentParser(description="Daily Legal AI Job Search Agent")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Search and score jobs but don't send the email",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Generate report HTML and open in browser (implies --dry-run)",
    )
    parser.add_argument(
        "--include-seen",
        action="store_true",
        help="Include previously seen jobs (skip deduplication)",
    )
    parser.add_argument(
        "--save-results",
        metavar="FILE",
        help="Save raw scored results to a JSON file",
    )
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Step 1: Search
    # ------------------------------------------------------------------
    logger.info("Starting job search...")
    all_jobs = run_all_searches()
    total_searched = len(all_jobs)
    logger.info("Found %d raw job listings", total_searched)

    if not all_jobs:
        logger.warning(
            "No jobs returned from any source. Check that at least one API key "
            "is configured (JSEARCH_API_KEY or ADZUNA_APP_ID/ADZUNA_APP_KEY)."
        )
        # Still generate and send a "no results" report
        subject, html = generate_report([], total_searched=0)
        if not args.dry_run and not args.preview:
            send_email(subject, html)
        return

    # ------------------------------------------------------------------
    # Step 2: Deduplicate
    # ------------------------------------------------------------------
    if args.include_seen:
        new_jobs = all_jobs
        logger.info("Including all jobs (--include-seen)")
    else:
        seen = load_seen_jobs()
        seen = prune_seen_jobs(seen)
        new_jobs = filter_new_jobs(all_jobs, seen)
        save_seen_jobs(seen)
        logger.info("%d new jobs after deduplication (%d previously seen)", len(new_jobs), len(seen))

    # ------------------------------------------------------------------
    # Step 3: Score and rank
    # ------------------------------------------------------------------
    ranked = rank_jobs(new_jobs)
    logger.info("%d qualified jobs after scoring and filtering", len(ranked))

    # ------------------------------------------------------------------
    # Step 4: Save results (optional)
    # ------------------------------------------------------------------
    if args.save_results:
        out_path = Path(args.save_results)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(ranked[:MAX_JOBS_IN_REPORT], f, indent=2, default=str)
        logger.info("Saved %d results to %s", min(len(ranked), MAX_JOBS_IN_REPORT), out_path)

    # ------------------------------------------------------------------
    # Step 5: Generate report
    # ------------------------------------------------------------------
    subject, html = generate_report(ranked, total_searched=total_searched)
    logger.info("Report generated: %s", subject)

    # ------------------------------------------------------------------
    # Step 6: Preview or send
    # ------------------------------------------------------------------
    if args.preview:
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(html)
            preview_path = f.name
        logger.info("Preview saved to %s", preview_path)
        webbrowser.open(f"file://{preview_path}")
        print(f"\nPreview: {preview_path}")
        return

    if args.dry_run:
        print(f"\n--- DRY RUN ---")
        print(f"Subject: {subject}")
        print(f"Jobs found: {total_searched}")
        print(f"New jobs: {len(new_jobs)}")
        print(f"Qualified matches: {len(ranked)}")
        if ranked:
            print(f"\nTop matches:")
            for i, job in enumerate(ranked[:5], 1):
                print(f"  {i}. [{job['score']}pts] {job['title']} @ {job['company']} ({job['location']})")
        return

    # Send email
    success = send_email(subject, html)
    if success:
        logger.info("Daily report sent successfully to shepjames@gmail.com")
    else:
        logger.error("Failed to send daily report")
        sys.exit(1)


if __name__ == "__main__":
    main()
