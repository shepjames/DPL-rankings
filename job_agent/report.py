"""
Job Search Agent — HTML Report Generator

Builds a clean, mobile-friendly HTML email summarizing today's job matches.
"""

from datetime import datetime

from config import MAX_JOBS_IN_REPORT, PROFILE


def _salary_display(job: dict) -> str:
    """Format salary range for display."""
    s_min = job.get("salary_min")
    s_max = job.get("salary_max")
    if s_min and s_max:
        return f"${s_min:,} – ${s_max:,}"
    elif s_min:
        return f"${s_min:,}+"
    elif s_max:
        return f"Up to ${s_max:,}"
    return "Not listed"


def _score_bar(score: int, max_score: int = 150) -> str:
    """Generate a simple visual score bar."""
    pct = min(100, int((score / max_score) * 100))
    filled = pct // 5
    return f"{'█' * filled}{'░' * (20 - filled)} {score}pts"


def _keyword_badges(keywords: list[str]) -> str:
    """Generate HTML badges for matched keywords."""
    if not keywords:
        return "<em>No specific keyword matches</em>"
    badges = []
    for kw in keywords[:8]:  # cap at 8 to keep it clean
        badges.append(
            f'<span style="display:inline-block;background:#e8f4f8;color:#1a5276;'
            f'padding:2px 8px;margin:2px;border-radius:12px;font-size:12px;">{kw}</span>'
        )
    if len(keywords) > 8:
        badges.append(
            f'<span style="display:inline-block;background:#f0f0f0;color:#666;'
            f'padding:2px 8px;margin:2px;border-radius:12px;font-size:12px;">'
            f'+{len(keywords) - 8} more</span>'
        )
    return " ".join(badges)


def _job_card(job: dict, rank: int) -> str:
    """Generate HTML for a single job card."""
    breakdown = job.get("score_breakdown", {})
    location = job.get("location", "Not specified")

    # Location badge color
    loc_lower = location.lower()
    if "dallas" in loc_lower or "dfw" in loc_lower or "fort worth" in loc_lower:
        loc_color = "#27ae60"
        loc_label = f"📍 {location}"
    elif "remote" in loc_lower:
        loc_color = "#2980b9"
        loc_label = f"🏠 {location}"
    else:
        loc_color = "#7f8c8d"
        loc_label = f"📍 {location}"

    return f"""
    <div style="border:1px solid #e0e0e0;border-radius:8px;padding:16px;margin:12px 0;
                background:#ffffff;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
                <div style="font-size:11px;color:#888;font-weight:600;">#{rank}</div>
                <h3 style="margin:4px 0 6px 0;color:#1a1a2e;font-size:17px;">
                    <a href="{job.get('url', '#')}" style="color:#1a5276;text-decoration:none;">{job.get('title', 'Untitled')}</a>
                </h3>
                <div style="color:#555;font-size:14px;margin-bottom:4px;">
                    <strong>{job.get('company', 'Unknown')}</strong>
                </div>
            </div>
            <div style="text-align:right;min-width:80px;">
                <div style="background:#1a5276;color:white;padding:4px 10px;border-radius:16px;
                            font-size:13px;font-weight:700;">{job.get('score', 0)} pts</div>
            </div>
        </div>

        <div style="margin:8px 0;font-size:13px;">
            <span style="color:{loc_color};font-weight:600;">{loc_label}</span>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <span style="color:#666;">💰 {_salary_display(job)}</span>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <span style="color:#888;">📅 {job.get('date_posted', 'Recent')}</span>
        </div>

        <div style="margin:8px 0;">
            {_keyword_badges(job.get('matched_keywords', []))}
        </div>

        <div style="font-size:12px;color:#999;margin-top:8px;">
            Score: Keywords({breakdown.get('keywords', 0)}) +
            Location({breakdown.get('location', 0)}) +
            Seniority({breakdown.get('seniority', 0)}) +
            Salary({breakdown.get('salary', 0)}) +
            Equity({breakdown.get('equity', 0)})
            &nbsp;·&nbsp; via {job.get('source', 'Unknown')}
        </div>
    </div>
    """


def generate_report(jobs: list[dict], total_searched: int = 0) -> tuple[str, str]:
    """
    Generate the HTML email body and a plain-text subject line.

    Returns (subject, html_body).
    """
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    display_jobs = jobs[:MAX_JOBS_IN_REPORT]
    n_jobs = len(display_jobs)

    # Subject line
    if n_jobs == 0:
        subject = f"Daily Legal AI Job Report – {now.strftime('%m/%d')} – No new matches"
    else:
        top_title = display_jobs[0]["title"] if display_jobs else ""
        subject = f"Daily Legal AI Job Report – {now.strftime('%m/%d')} – {n_jobs} match{'es' if n_jobs != 1 else ''}"

    # Stats
    dallas_count = sum(
        1 for j in display_jobs
        if any(loc.lower() in j.get("location", "").lower() for loc in ["dallas", "dfw", "fort worth", "plano", "frisco", "irving"])
    )
    remote_count = sum(1 for j in display_jobs if "remote" in j.get("location", "").lower())
    avg_score = int(sum(j.get("score", 0) for j in display_jobs) / max(n_jobs, 1))

    # Job cards
    job_cards = ""
    for i, job in enumerate(display_jobs, 1):
        job_cards += _job_card(job, i)

    # No-results message
    if n_jobs == 0:
        job_cards = """
        <div style="text-align:center;padding:40px;color:#888;">
            <div style="font-size:48px;">🔍</div>
            <h3 style="color:#555;">No new matching jobs today</h3>
            <p>The agent searched across configured sources but didn't find new
            postings matching your profile. This is normal — senior legal roles
            don't post daily. Check back tomorrow!</p>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
                 background:#f5f6fa;color:#333;">
        <div style="max-width:640px;margin:0 auto;padding:16px;">

            <!-- Header -->
            <div style="background:linear-gradient(135deg,#1a5276,#2980b9);border-radius:12px;
                        padding:24px;color:white;margin-bottom:16px;">
                <h1 style="margin:0 0 4px 0;font-size:22px;">Daily Legal AI Job Report</h1>
                <div style="opacity:0.85;font-size:14px;">{date_str}</div>
            </div>

            <!-- Stats Bar -->
            <div style="display:flex;justify-content:space-around;background:white;border-radius:8px;
                        padding:12px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
                <div style="text-align:center;">
                    <div style="font-size:24px;font-weight:700;color:#1a5276;">{n_jobs}</div>
                    <div style="font-size:11px;color:#888;">NEW MATCHES</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:24px;font-weight:700;color:#27ae60;">{dallas_count}</div>
                    <div style="font-size:11px;color:#888;">DALLAS AREA</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:24px;font-weight:700;color:#2980b9;">{remote_count}</div>
                    <div style="font-size:11px;color:#888;">REMOTE</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:24px;font-weight:700;color:#8e44ad;">{avg_score}</div>
                    <div style="font-size:11px;color:#888;">AVG SCORE</div>
                </div>
            </div>

            <!-- Job Listings -->
            {job_cards}

            <!-- Footer -->
            <div style="text-align:center;padding:20px;color:#aaa;font-size:11px;">
                <p>Generated by Job Search Agent · Searched {total_searched} postings across configured sources</p>
                <p>Target: {', '.join(PROFILE['target_levels'][:3])} · Dallas preferred, remote OK · $225K+ floor</p>
            </div>
        </div>
    </body>
    </html>
    """

    return subject, html
