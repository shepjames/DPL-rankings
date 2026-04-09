#!/usr/bin/env python3
"""
Generate a Dallas-focused job search report using verified in-house
legal postings from the Dallas/DFW area.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from matcher import rank_jobs
from report import generate_report

# All verified Dallas-area in-house legal postings (April 2026)
DALLAS_JOBS = [
    {
        # SOURCE: GoInhouse.com / LinkedIn
        # Confirmed: https://www.goinhouse.com/jobs/510251140-deputy-general-counsel-at-beneficient
        "id": "dallas_001",
        "title": "Deputy General Counsel",
        "company": "Beneficient",
        "location": "Dallas, TX",
        "description": (
            "Strategic legal support of the Beneficient business, actively engaging "
            "with leadership team. Broad range of complex legal matters in a fast-paced, "
            "entrepreneurial environment. Advising on core business operations, capital "
            "markets and securities transactions, general corporate matters, commercial "
            "agreements, corporate governance, complex strategic transactions, and "
            "financial reporting. 4-8 years corporate, securities, or M&A experience."
        ),
        "url": "https://www.goinhouse.com/jobs/510251140-deputy-general-counsel-at-beneficient",
        "salary_min": None,
        "salary_max": None,
        "date_posted": "2026-03-15",
        "source": "GoInhouse",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        # SOURCE: GoInhouse.com / Jobright / Glassdoor
        # Confirmed: https://www.goinhouse.com/jobs/516597629-senior-legal-counsel-at-nice
        "id": "dallas_002",
        "title": "Senior Legal Counsel",
        "company": "NiCE (NICE Ltd)",
        "location": "Dallas, TX (Hybrid)",
        "description": (
            "Americas Legal team supporting high-value commercial and technology "
            "transactions for CXone Mpower platform. Structuring, negotiating and "
            "managing sophisticated SaaS and technology agreements including Data "
            "Processing Agreements. Strong working knowledge of data privacy, "
            "cybersecurity, and intellectual property law. Development of scalable "
            "contracting processes, legal playbooks, and operational improvements. "
            "Reports to Associate General Counsel, NiCE Americas. 8-10 years experience."
        ),
        "url": "https://www.goinhouse.com/jobs/516597629-senior-legal-counsel-at-nice",
        "salary_min": None,
        "salary_max": None,
        "date_posted": "2026-03-20",
        "source": "GoInhouse",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        # SOURCE: Glassdoor / GoInhouse / LinkedIn / Legal.io
        # Confirmed: https://www.glassdoor.com/job-listing/privacy-ai-attorney-texas-instruments-...
        "id": "dallas_003",
        "title": "Privacy-AI Attorney",
        "company": "Texas Instruments",
        "location": "Dallas, TX",
        "description": (
            "Individual contributor serving as subject matter expert providing legal "
            "advice and guidance on privacy, data protection, cybersecurity, and "
            "artificial intelligence. Legal guidance to global, cross-functional privacy, "
            "data protection, cybersecurity, and AI teams. Advise on external terms and "
            "internal policies. Track, analyze, and communicate new AI and privacy laws "
            "globally. Support investigations and responses to data breaches and security "
            "events. Reports to Dallas-based Assistant General Counsel. CCPA, GDPR, "
            "AI governance, responsible AI, data privacy, cybersecurity, incident response."
        ),
        "url": "https://www.glassdoor.com/job-listing/privacy-ai-attorney-texas-instruments-JV_IC1139977_KO0,19_KE20,37.htm",
        "salary_min": None,
        "salary_max": None,
        "date_posted": "2026-03-10",
        "source": "Glassdoor",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        # SOURCE: GoInhouse.com
        # Confirmed: https://www.goinhouse.com/jobs/464935589-hipaa-officer-data-regulatory-counsel-at-thomson-reuters
        "id": "dallas_004",
        "title": "HIPAA Officer & Data Regulatory Counsel",
        "company": "Thomson Reuters",
        "location": "Dallas, TX",
        "description": (
            "General Counsel's Office role reporting to Assistant General Counsel, "
            "Privacy & Cybersecurity. Focus on HIPAA and global privacy laws and "
            "cybersecurity laws governing sensitive data. Serve as HIPAA Privacy and "
            "Data Regulatory Counsel. Monitor emerging data protection regulations. "
            "Assist in design and implementation of Privacy Program. Requires technical "
            "knowledge of global privacy laws, experience managing security incident "
            "responses, advising product and technology teams on privacy, significant "
            "technology transactions experience, and people leadership skills."
        ),
        "url": "https://www.goinhouse.com/jobs/464935589-hipaa-officer-data-regulatory-counsel-at-thomson-reuters",
        "salary_min": 134680,
        "salary_max": 250120,
        "date_posted": "2026-02-28",
        "source": "GoInhouse",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        # SOURCE: GoInhouse.com / Ladders
        # Confirmed: https://www.goinhouse.com/jobs/512082135-assistant-general-counsel-global-technology-and-sourcing-at-thomson-reuters-corporation
        "id": "dallas_005",
        "title": "Assistant General Counsel, Global Technology and Sourcing",
        "company": "Thomson Reuters",
        "location": "Dallas, TX / Frisco, TX",
        "description": (
            "Manage a team of attorneys supporting global technology, sourcing and "
            "marketing events teams. Drafting, review and negotiation of complex global "
            "commercial agreements with third party suppliers including cloud, software "
            "licensing, hardware, IT/consulting services, telecommunications and "
            "outsourcing. Expert legal advice on software licensing, cloud services, "
            "data privacy, and intellectual property. People leadership, team leadership, "
            "technology transactions, SaaS agreements, vendor management."
        ),
        "url": "https://www.goinhouse.com/jobs/512082135-assistant-general-counsel-global-technology-and-sourcing-at-thomson-reuters-corporation",
        "salary_min": 157500,
        "salary_max": 292500,
        "date_posted": "2026-03-18",
        "source": "GoInhouse",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        # SOURCE: GoInhouse.com / LinkedIn / Ladders
        # Confirmed: https://www.goinhouse.com/jobs/412578727-sr-counsel-privacy-ai-data-governance-remote-at-omnicell
        "id": "dallas_006",
        "title": "Sr. Counsel - Privacy, AI & Data Governance",
        "company": "Omnicell",
        "location": "Dallas, TX (Remote eligible)",
        "description": (
            "Reports to Assistant General Counsel, Global Privacy, AI & Data Governance. "
            "Primary legal partner to VP of AI Transformation, leading AI governance "
            "activities. Implement Privacy by Design framework. Assess privacy, AI and "
            "data governance matters for full product lifecycle. Lead negotiations on "
            "privacy and AI components including BAAs and DPAs. Conduct AI Conformance "
            "Assessments and Privacy Impact Assessments. Advise on HIPAA/HITECH, GDPR, "
            "CCPA/CPRA, EU AI Act. Collaborate on data incidents and incident response. "
            "Artificial intelligence, AI governance, responsible AI, data privacy, "
            "cybersecurity, technology transactions."
        ),
        "url": "https://www.goinhouse.com/jobs/412578727-sr-counsel-privacy-ai-data-governance-remote-at-omnicell",
        "salary_min": None,
        "salary_max": None,
        "date_posted": "2026-03-05",
        "source": "GoInhouse",
        "fetched_at": "2026-04-09T07:00:00",
    },
    {
        # SOURCE: GoInhouse.com / LinkedIn
        # Confirmed: https://www.goinhouse.com/jobs/503198391-counsel-data-governance-records-retention-at-marshmclennan
        "id": "dallas_007",
        "title": "Counsel, Data Governance & Records Retention",
        "company": "Marsh McLennan",
        "location": "Dallas, TX (Hybrid)",
        "description": (
            "Reports to Chief Cybersecurity and Technology Regulation Counsel within "
            "Privacy Center of Excellence. Supporting enterprise-wide Data Governance "
            "initiatives with emphasis on Records Retention compliance. Developing and "
            "implementing data governance policies, standards, and procedures. "
            "Maintaining enterprise records retention policy. Collaborating with legal, "
            "compliance, IT stakeholders. Monitoring emerging legal and regulatory "
            "developments. Information governance, regulatory compliance, data privacy."
        ),
        "url": "https://www.goinhouse.com/jobs/503198391-counsel-data-governance-records-retention-at-marshmclennan",
        "salary_min": None,
        "salary_max": None,
        "date_posted": "2026-03-12",
        "source": "GoInhouse",
        "fetched_at": "2026-04-09T07:00:00",
    },
]


def main():
    print("=" * 80)
    print("  DALLAS IN-HOUSE LEGAL POSITIONS REPORT")
    print("=" * 80)
    print(f"\nScoring {len(DALLAS_JOBS)} verified Dallas-area postings...\n")

    ranked = rank_jobs(DALLAS_JOBS)

    print(f"Results: {len(DALLAS_JOBS)} total, {len(ranked)} qualified\n")
    print("-" * 80)
    for i, job in enumerate(ranked, 1):
        kw_list = ", ".join(job["matched_keywords"][:6])
        if len(job["matched_keywords"]) > 6:
            kw_list += f", +{len(job['matched_keywords']) - 6} more"

        sal = ""
        if job.get("salary_min") and job.get("salary_max"):
            sal = f"${job['salary_min']:,} - ${job['salary_max']:,}"
        elif job.get("salary_min"):
            sal = f"${job['salary_min']:,}+"
        else:
            sal = "Not listed"

        print(
            f"  #{i}  [{job['score']:3d} pts]  {job['title']}\n"
            f"       {job['company']} | {job['location']}\n"
            f"       Salary: {sal}\n"
            f"       Breakdown: {job['score_breakdown']}\n"
            f"       Keywords: {kw_list}\n"
        )
    print("-" * 80)

    # Generate HTML report
    subject, html = generate_report(ranked, total_searched=len(DALLAS_JOBS))
    preview_path = Path(__file__).parent / "data" / "dallas_report.html"
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    with open(preview_path, "w") as f:
        f.write(html)
    print(f"\nHTML report saved to: {preview_path}")


if __name__ == "__main__":
    main()
