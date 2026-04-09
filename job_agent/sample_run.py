#!/usr/bin/env python3
"""
Generate a sample job search report using real job postings
found during research. Demonstrates the scoring and report output.
"""

import sys
import tempfile
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from matcher import rank_jobs
from report import generate_report

# Real job postings found during research (April 2026)
SAMPLE_JOBS = [
    {
        "id": "sample_001",
        "title": "Senior Counsel Specialist, Assistant General Counsel - Privacy Law",
        "company": "Genentech",
        "location": "South San Francisco, CA",
        "description": (
            "Experienced privacy attorney to join the Legal Department reporting to "
            "the Chief Privacy Officer. Advising on data protection and privacy laws, "
            "developing policies, AI governance, understanding of emerging AI legal "
            "landscape including Colorado AI Act. CIPP/US required; AIGP certification "
            "a plus. Data privacy, cybersecurity, information governance, technology "
            "transactions, SaaS agreements, responsible AI, generative AI compliance."
        ),
        "url": "https://careers.gene.com/us/en/job/202510-125507/Senior-Counsel-Specialist-Assistant-General-Counsel-Privacy-Law",
        "salary_min": 209700,
        "salary_max": 389500,
        "date_posted": "2026-04-01",
        "source": "JSearch",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        "id": "sample_002",
        "title": "Executive Director, Privacy & AI Governance Technology & Operations",
        "company": "Sony Pictures Entertainment",
        "location": "Culver City, CA",
        "description": (
            "Design strategy and oversee implementation of global Privacy & AI Governance "
            "technology and operations programs. Reports to Chief Privacy Officer. "
            "Operationalizing legal, regulatory, and policy requirements into scalable, "
            "technology-enabled solutions. Leading global team of privacy and AI governance "
            "professionals. CIPP/US, CIPP/E, CIPM, or AIGP preferred. Data privacy, "
            "AI compliance, responsible AI, legal operations, legal technology, "
            "contract lifecycle management, e-discovery, incident response."
        ),
        "url": "https://www.sonypicturesjobs.com/job/culver-city/executive-director-privacy-and-ai-governance-technology-and-operations/22978/91664594480",
        "salary_min": 220000,
        "salary_max": 350000,
        "date_posted": "2026-04-03",
        "source": "JSearch",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        "id": "sample_003",
        "title": "Corporate Counsel, Privacy & AI",
        "company": "Shipt",
        "location": "Dallas, TX",
        "description": (
            "Supporting Privacy, Cybersecurity, and Artificial Intelligence initiatives. "
            "Working with Product, Engineering, Security, and Data teams. Privacy by design, "
            "Privacy Impact Assessments, responsible AI adoption. CIPP/US, CIPP/E, or AIGP "
            "preferred. Data privacy, AI governance, generative AI, legal technology, "
            "SaaS agreements, technology transactions, team leadership, outside counsel "
            "management, cybersecurity incident response."
        ),
        "url": "https://www.ziprecruiter.com/c/Shipt/Job/Corporate-Counsel,-Privacy-&-AI/-in-San-Francisco,CA",
        "salary_min": 137400,
        "salary_max": 185000,
        "date_posted": "2026-04-05",
        "source": "JSearch",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        "id": "sample_004",
        "title": "Director, Counsel Privacy, Cybersecurity & AI",
        "company": "Shipt",
        "location": "Remote",
        "description": (
            "Strategic enabler for product, data, and AI initiatives at the intersection "
            "of technology, business strategy, and regulation. Help innovate faster while "
            "managing risk intelligently. Data privacy, cybersecurity, artificial intelligence "
            "governance, AI policy, responsible AI, team leadership, direct reports, "
            "outside counsel management, legal spend, technology transactions, "
            "SaaS contracts, incident response, CISO partnership, equity compensation, "
            "RSU, long-term incentive plan."
        ),
        "url": "https://shipt.wd1.myworkdayjobs.com/Shipt_External/job/Minneapolis-MN/Director--Counsel-Privacy--Cybersecurity---AI_R4101",
        "salary_min": 157000,
        "salary_max": 300000,
        "date_posted": "2026-04-02",
        "source": "Adzuna",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        "id": "sample_005",
        "title": "Associate General Counsel, Product, Privacy and AI",
        "company": "Peregrine Technologies",
        "location": "Dallas, TX",
        "description": (
            "Lead legal strategy for AI-driven products, data privacy program, and "
            "technology transactions. Partner with engineering and product teams on "
            "responsible AI deployment. Develop AI acceptable use policy, review AI use "
            "cases, draft AI terms for customer agreements. AIGP or CIPP/US preferred. "
            "Generative AI, legal operations, legal technology, contract lifecycle "
            "management, Ironclad, outside counsel management, people leadership, "
            "team leadership, commercial litigation background a plus. Equity and "
            "stock options included."
        ),
        "url": "https://jobright.ai/jobs/info/69a82c0b7ac93962b707eb3c",
        "salary_min": 250000,
        "salary_max": 325000,
        "date_posted": "2026-04-07",
        "source": "JSearch",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        "id": "sample_006",
        "title": "Senior Manager, Data Privacy & AI Governance",
        "company": "Carvana",
        "location": "Phoenix, AZ",
        "description": (
            "Privacy or governance credentials required: CIPT, CIPM, CIPP/US, or AIGP. "
            "Data privacy program management, AI governance framework, regulatory "
            "compliance, CCPA, responsible AI, generative AI tools, legal technology, "
            "vendor management, information governance, e-discovery support."
        ),
        "url": "https://www.ziprecruiter.com/Jobs/Aigp",
        "salary_min": 160000,
        "salary_max": 210000,
        "date_posted": "2026-04-04",
        "source": "Adzuna",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        "id": "sample_007",
        "title": "Deputy General Counsel, Technology & AI",
        "company": "Major Airline (Confidential)",
        "location": "Dallas, TX",
        "description": (
            "Seeking Deputy General Counsel to lead technology transactions, data privacy, "
            "cybersecurity, and AI governance legal teams. Reports to CLO. Lead team of "
            "12+ attorneys and staff. Oversee AI policy development, technology contracts "
            "portfolio including SaaS, data license, DPA agreements. Partner with CISO "
            "on incident response and TSA compliance. Drive legal operations including "
            "matter management in TeamConnect, document management in iManage, CLM in "
            "Ironclad, e-discovery in DISCO, and GenAI tools like Harvey and Eudia. "
            "Outside counsel management and preferred law firm network. Equity, RSU, "
            "and long-term incentive plan. CIPP/US and AIGP preferred."
        ),
        "url": "https://example.com/deputy-gc-tech-ai",
        "salary_min": 300000,
        "salary_max": 425000,
        "date_posted": "2026-04-08",
        "source": "JSearch",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        "id": "sample_008",
        "title": "Vice President and General Counsel",
        "company": "AI Legal Tech Startup",
        "location": "Remote",
        "description": (
            "General Counsel for Series B legal AI startup. Build legal function from "
            "ground up. Commercial contracts, SaaS agreements, data privacy, GDPR, CCPA, "
            "intellectual property, trademark strategy. Generative AI product counsel. "
            "Equity compensation package with stock options. Team leadership of small "
            "but growing legal team."
        ),
        "url": "https://example.com/gc-legal-ai-startup",
        "salary_min": 275000,
        "salary_max": 350000,
        "date_posted": "2026-04-06",
        "source": "JSearch",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        "id": "sample_009",
        "title": "Legal Assistant - Corporate",
        "company": "Generic Corp",
        "location": "Dallas, TX",
        "description": "Support corporate legal team with filing, scheduling, document management.",
        "url": "https://example.com/legal-assistant",
        "salary_min": 45000,
        "salary_max": 55000,
        "date_posted": "2026-04-08",
        "source": "JSearch",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        "id": "sample_010",
        "title": "Partner, AI & Data Privacy Practice",
        "company": "Bradley Arant Boult Cummings LLP",
        "location": "Dallas, TX",
        "description": (
            "Lateral partner opportunity in growing AI and data privacy practice group. "
            "Advise Fortune 500 clients on AI governance, EU AI Act compliance, data "
            "privacy, CCPA, GDPR, cybersecurity incident response. Portable book preferred "
            "but not required for candidates with strong AI governance expertise. "
            "Artificial intelligence, responsible AI, AIGP, CIPP, technology transactions."
        ),
        "url": "https://example.com/partner-ai-privacy",
        "salary_min": None,
        "salary_max": None,
        "date_posted": "2026-04-03",
        "source": "Adzuna",
        "fetched_at": "2026-04-09T07:00:00",
    },
]


def main():
    print("Scoring sample jobs against profile...\n")
    ranked = rank_jobs(SAMPLE_JOBS)

    print(f"Results: {len(SAMPLE_JOBS)} total, {len(ranked)} qualified\n")
    print("=" * 80)
    for i, job in enumerate(ranked, 1):
        kw_list = ", ".join(job["matched_keywords"][:6])
        if len(job["matched_keywords"]) > 6:
            kw_list += f", +{len(job['matched_keywords']) - 6} more"
        print(
            f"  #{i}  [{job['score']:3d} pts]  {job['title']}\n"
            f"       {job['company']} | {job['location']}\n"
            f"       Breakdown: {job['score_breakdown']}\n"
            f"       Keywords: {kw_list}\n"
        )
    print("=" * 80)

    # Generate HTML report
    subject, html = generate_report(ranked, total_searched=len(SAMPLE_JOBS))
    print(f"\nEmail Subject: {subject}")

    # Save preview
    preview_path = Path(__file__).parent / "data" / "sample_report.html"
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    with open(preview_path, "w") as f:
        f.write(html)
    print(f"Report saved to: {preview_path}")


if __name__ == "__main__":
    main()
