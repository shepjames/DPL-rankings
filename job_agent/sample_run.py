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

# Verified job postings from research (April 2026)
# Each posting confirmed via public job board with source URL.
SAMPLE_JOBS = [
    {
        # SOURCE: Genentech careers site
        # Confirmed: https://careers.gene.com/us/en/job/202510-125507
        "id": "sample_001",
        "title": "Senior Counsel Specialist, Assistant General Counsel - Privacy Law",
        "company": "Genentech",
        "location": "South San Francisco, CA",
        "description": (
            "Experienced privacy attorney reporting to the Chief Privacy Officer. "
            "Advising on data protection and privacy laws, developing policies, "
            "understanding of emerging AI legal landscape including Colorado AI Act. "
            "CIPP/US required; AIGP certification a plus. Data privacy, cybersecurity, "
            "information governance, technology transactions, responsible AI."
        ),
        "url": "https://careers.gene.com/us/en/job/202510-125507/Senior-Counsel-Specialist-Assistant-General-Counsel-Privacy-Law",
        "salary_min": 209700,
        "salary_max": 389500,
        "date_posted": "2026-04-01",
        "source": "Genentech Careers",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        # SOURCE: Sony Pictures jobs site
        # Confirmed: https://www.sonypicturesjobs.com/job/culver-city/executive-director-...
        "id": "sample_002",
        "title": "Executive Director, Privacy & AI Governance Technology & Operations",
        "company": "Sony Pictures Entertainment",
        "location": "Culver City, CA",
        "description": (
            "Design strategy and oversee implementation of global Privacy & AI Governance "
            "technology and operations programs. Reports to SPE Chief Privacy Officer. "
            "Operationalizing legal, regulatory, and policy requirements into scalable, "
            "technology-enabled solutions. Leading global team of privacy and AI governance "
            "professionals. CIPP/US, CIPP/E, CIPM, or AIGP preferred."
        ),
        "url": "https://www.sonypicturesjobs.com/job/culver-city/executive-director-privacy-and-ai-governance-technology-and-operations/22978/91664594480",
        "salary_min": None,
        "salary_max": None,
        "date_posted": "2026-04-03",
        "source": "Sony Pictures Jobs",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        # SOURCE: ZipRecruiter / Built In
        # Confirmed: https://www.ziprecruiter.com/c/Shipt/Job/Corporate-Counsel,-Privacy-&-AI/
        "id": "sample_003",
        "title": "Corporate Counsel, Privacy & AI",
        "company": "Shipt",
        "location": "San Francisco, CA / Minneapolis, MN / Birmingham, AL",
        "description": (
            "Supporting Privacy, Cybersecurity, and Artificial Intelligence initiatives "
            "in a highly collaborative, product-driven environment. Working with Product, "
            "Engineering, Security, and Data teams. Privacy by design for new features, "
            "managing Privacy Impact Assessments, enabling responsible AI adoption. "
            "CIPP/US, CIPP/E, or AIGP preferred."
        ),
        "url": "https://www.ziprecruiter.com/c/Shipt/Job/Corporate-Counsel,-Privacy-&-AI/-in-San-Francisco,CA",
        "salary_min": 137400,
        "salary_max": 185000,
        "date_posted": "2026-04-05",
        "source": "ZipRecruiter",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        # SOURCE: Shipt Workday careers
        # Confirmed: https://shipt.wd1.myworkdayjobs.com/Shipt_External/job/.../Director--Counsel-Privacy--Cybersecurity---AI_R4101
        "id": "sample_004",
        "title": "Director, Counsel Privacy, Cybersecurity & AI",
        "company": "Shipt",
        "location": "Minneapolis, MN (Hybrid)",
        "description": (
            "Strategic enabler for product, data, and AI initiatives sitting at the "
            "intersection of technology, business strategy, and regulation. Mandate to "
            "help Shipt innovate faster while managing risk intelligently. Data privacy, "
            "cybersecurity, artificial intelligence governance, AI policy, responsible AI, "
            "team leadership."
        ),
        "url": "https://shipt.wd1.myworkdayjobs.com/Shipt_External/job/Minneapolis-MN/Director--Counsel-Privacy--Cybersecurity---AI_R4101",
        "salary_min": 157000,
        "salary_max": 300000,
        "date_posted": "2026-04-02",
        "source": "Shipt Workday",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        # SOURCE: Greenhouse / Jobright / GoInhouse / Legal.io (multiple boards)
        # Confirmed: https://job-boards.greenhouse.io/peregrinetechnologies/jobs/4669722005
        "id": "sample_005",
        "title": "Associate General Counsel, Product, Privacy and AI",
        "company": "Peregrine Technologies",
        "location": "Washington, DC / San Francisco, CA",
        "description": (
            "Strategic legal partner to Product, Engineering, Security, and Compliance "
            "teams. Reports to CLO. Embeds into product development lifecycle advising on "
            "AI-enabled features, data governance, model development, and regulatory "
            "exposure in public sector environments. Guide AI governance strategy, "
            "monitor evolving privacy standards. CCPA/CPRA, GDPR, AI governance, "
            "responsible AI, model risk assessment."
        ),
        "url": "https://job-boards.greenhouse.io/peregrinetechnologies/jobs/4669722005",
        "salary_min": 270000,
        "salary_max": 345000,
        "date_posted": "2026-04-07",
        "source": "Greenhouse",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        # SOURCE: Glassdoor / Carvana Greenhouse
        # Confirmed: https://www.glassdoor.com/job-listing/senior-manager-data-privacy-and-ai-governance-carvana-...
        "id": "sample_006",
        "title": "Senior Manager, Data Privacy & AI Governance",
        "company": "Carvana",
        "location": "Tempe, AZ",
        "description": (
            "Leader within Carvana's Privacy, Data & AI Governance Team responsible for "
            "supporting development, maintenance, and execution of Carvana's Privacy "
            "Program. Privacy or Governance credentials required: CIPT, CIPM, CIPP/US, "
            "or AIGP. Data privacy, AI governance framework, regulatory compliance, "
            "CCPA, responsible AI, information governance."
        ),
        "url": "https://www.glassdoor.com/job-listing/senior-manager-data-privacy-and-ai-governance-carvana-JV_IC1133917_KO0,45_KE46,53.htm",
        "salary_min": None,
        "salary_max": None,
        "date_posted": "2026-04-04",
        "source": "Glassdoor",
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
