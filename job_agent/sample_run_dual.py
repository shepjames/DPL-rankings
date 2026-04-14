#!/usr/bin/env python3
"""
Dual job search reports:
  Report 1: Legal / AI / Technology focused roles (national)
  Report 2: Dallas-area in-house positions (all practice areas)

Format: Company, Title, Summary, Salary, Source with hyperlink.
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from matcher import rank_jobs

# =========================================================================
# REPORT 1: Legal / AI / Technology Focused (National)
# =========================================================================
AI_TECH_JOBS = [
    {
        "id": "ai_001",
        "title": "Senior Counsel Specialist, Assistant General Counsel - Privacy Law",
        "company": "Genentech",
        "location": "South San Francisco, CA",
        "description": (
            "Privacy attorney reporting to CPO. Data protection, privacy laws, AI governance, "
            "Colorado AI Act. CIPP/US required; AIGP a plus. Data privacy, cybersecurity, "
            "information governance, technology transactions, responsible AI."
        ),
        "url": "https://careers.gene.com/us/en/job/202510-125507/Senior-Counsel-Specialist-Assistant-General-Counsel-Privacy-Law",
        "salary_min": 209700, "salary_max": 389500,
        "date_posted": "2026-04-01", "source": "Genentech Careers",
    },
    {
        "id": "ai_002",
        "title": "Executive Director, Privacy & AI Governance Technology & Operations",
        "company": "Sony Pictures Entertainment",
        "location": "Culver City, CA",
        "description": (
            "Strategy and oversight of global Privacy & AI Governance programs. Reports to "
            "SPE CPO. Operationalizing legal/regulatory requirements into scalable solutions. "
            "Leading global team. CIPP/US, CIPP/E, CIPM, or AIGP preferred."
        ),
        "url": "https://www.sonypicturesjobs.com/job/culver-city/executive-director-privacy-and-ai-governance-technology-and-operations/22978/91664594480",
        "salary_min": 220000, "salary_max": 250000,
        "date_posted": "2026-04-03", "source": "Sony Pictures Jobs",
    },
    {
        "id": "ai_003",
        "title": "Corporate Counsel, Privacy & AI",
        "company": "Shipt",
        "location": "San Francisco / Minneapolis / Birmingham",
        "description": (
            "Privacy, Cybersecurity, and AI initiatives. Product, Engineering, Security teams. "
            "Privacy by design, PIAs, responsible AI adoption. CIPP/US, CIPP/E, or AIGP preferred."
        ),
        "url": "https://www.ziprecruiter.com/c/Shipt/Job/Corporate-Counsel,-Privacy-&-AI/-in-San-Francisco,CA",
        "salary_min": 137400, "salary_max": 185000,
        "date_posted": "2026-04-05", "source": "ZipRecruiter",
    },
    {
        "id": "ai_004",
        "title": "Director, Counsel Privacy, Cybersecurity & AI",
        "company": "Shipt",
        "location": "Minneapolis, MN (Hybrid)",
        "description": (
            "Strategic enabler at intersection of technology, business strategy, and regulation. "
            "Data privacy, cybersecurity, AI governance, AI policy, responsible AI, team leadership."
        ),
        "url": "https://shipt.wd1.myworkdayjobs.com/Shipt_External/job/Minneapolis-MN/Director--Counsel-Privacy--Cybersecurity---AI_R4101",
        "salary_min": 157000, "salary_max": 300000,
        "date_posted": "2026-04-02", "source": "Shipt Workday",
    },
    {
        "id": "ai_005",
        "title": "Associate General Counsel, Product, Privacy and AI",
        "company": "Peregrine Technologies",
        "location": "Washington, DC / San Francisco, CA",
        "description": (
            "Strategic legal partner to Product, Engineering, Security, Compliance. Reports to CLO. "
            "AI-enabled features, data governance, model risk, public sector. CCPA/CPRA, GDPR, "
            "AI governance, responsible AI."
        ),
        "url": "https://job-boards.greenhouse.io/peregrinetechnologies/jobs/4669722005",
        "salary_min": 270000, "salary_max": 345000,
        "date_posted": "2026-04-07", "source": "Greenhouse",
    },
    {
        "id": "ai_006",
        "title": "Senior Manager, Data Privacy & AI Governance",
        "company": "Carvana",
        "location": "Tempe, AZ",
        "description": (
            "Leader in Privacy, Data & AI Governance Team. Privacy program development and execution. "
            "CIPT, CIPM, CIPP/US, or AIGP required. AI governance, CCPA, responsible AI."
        ),
        "url": "https://www.glassdoor.com/job-listing/senior-manager-data-privacy-and-ai-governance-carvana-JV_IC1133917_KO0,45_KE46,53.htm",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-04-04", "source": "Glassdoor",
    },
    {
        "id": "ai_007",
        "title": "Privacy-AI Attorney",
        "company": "Texas Instruments",
        "location": "Dallas, TX",
        "description": (
            "SME on privacy, data protection, cybersecurity, and AI. Global cross-functional "
            "guidance. Track new AI/privacy laws globally. Incident response. Reports to "
            "Dallas-based AGC."
        ),
        "url": "https://www.glassdoor.com/job-listing/privacy-ai-attorney-texas-instruments-JV_IC1139977_KO0,19_KE20,37.htm",
        "salary_min": 127000, "salary_max": 185000,
        "date_posted": "2026-03-10", "source": "Glassdoor",
    },
    {
        "id": "ai_008",
        "title": "Sr. Counsel - Privacy, AI & Data Governance",
        "company": "Omnicell",
        "location": "Dallas, TX (Remote eligible)",
        "description": (
            "Legal partner to VP of AI Transformation. AI governance, Privacy by Design, "
            "AI Conformance Assessments, PIAs. HIPAA, GDPR, CCPA/CPRA, EU AI Act. "
            "Negotiate DPAs and BAAs."
        ),
        "url": "https://www.goinhouse.com/jobs/412578727-sr-counsel-privacy-ai-data-governance-remote-at-omnicell",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-03-05", "source": "GoInhouse",
    },
    {
        # SOURCE: Harvey careers / Ashby
        # Confirmed: https://jobs.ashbyhq.com/harvey/37702381-112a-483c-8f0a-f08e6ba0823d
        "id": "ai_009",
        "title": "Operating Partner, Dallas",
        "company": "Harvey",
        "location": "Dallas, TX",
        "description": (
            "Lead Harvey's new Dallas office. Drive business development, establish "
            "company presence in region. Collaborate with Sales and Customer Success. "
            "Represent Harvey at panels and industry events. Partner-level background "
            "at a law firm with strong local reputation, business development expertise, "
            "legal industry expertise, public speaking, AI knowledge."
        ),
        "url": "https://jobs.ashbyhq.com/harvey/37702381-112a-483c-8f0a-f08e6ba0823d",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-03-15", "source": "Harvey Careers (Ashby)",
    },
    {
        # SOURCE: Harvey careers / Ashby
        # Confirmed: https://jobs.ashbyhq.com/harvey/a6ecda75-fbe4-4b91-806a-bb4f36773390
        "id": "ai_010",
        "title": "Legal Innovation Partner, Dallas",
        "company": "Harvey",
        "location": "Dallas, TX",
        "description": (
            "Strategic counsel to innovation leaders defining and executing AI "
            "transformation. Advise innovation and knowledge teams. Support firm and "
            "client collaboration. Advance legal AI thought leadership through industry "
            "forums and publishing. 5+ years in legal innovation at top firm, corporate "
            "legal team, or legal tech org. Executive presence with CIOs/CKOs/CISOs."
        ),
        "url": "https://jobs.ashbyhq.com/harvey/a6ecda75-fbe4-4b91-806a-bb4f36773390",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-03-20", "source": "Harvey Careers (Ashby)",
    },
]

# =========================================================================
# REPORT 2: Dallas-Area In-House Positions (Broader)
# =========================================================================
DALLAS_JOBS = [
    {
        "id": "dal_001",
        "title": "Assistant General Counsel, Global Technology and Sourcing",
        "company": "Thomson Reuters",
        "location": "Dallas, TX / Frisco, TX",
        "description": (
            "Manage attorney team supporting global technology and sourcing. Complex commercial "
            "agreements: cloud, software licensing, IT services, outsourcing. Data privacy, IP. "
            "People leadership."
        ),
        "url": "https://www.goinhouse.com/jobs/512082135-assistant-general-counsel-global-technology-and-sourcing-at-thomson-reuters-corporation",
        "salary_min": 157500, "salary_max": 292500,
        "date_posted": "2026-03-18", "source": "GoInhouse",
    },
    {
        "id": "dal_002",
        "title": "Sr. Counsel - Privacy, AI & Data Governance",
        "company": "Omnicell",
        "location": "Dallas, TX (Remote eligible)",
        "description": (
            "Legal partner to VP of AI Transformation. AI governance, Privacy by Design, "
            "AI Conformance Assessments. HIPAA, GDPR, CCPA/CPRA, EU AI Act. DPAs and BAAs."
        ),
        "url": "https://www.goinhouse.com/jobs/412578727-sr-counsel-privacy-ai-data-governance-remote-at-omnicell",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-03-05", "source": "GoInhouse",
    },
    {
        "id": "dal_003",
        "title": "Privacy-AI Attorney",
        "company": "Texas Instruments",
        "location": "Dallas, TX",
        "description": (
            "SME on privacy, data protection, cybersecurity, and AI. Global cross-functional "
            "guidance. Track new AI/privacy laws globally. Incident response. Reports to "
            "Dallas-based AGC."
        ),
        "url": "https://www.glassdoor.com/job-listing/privacy-ai-attorney-texas-instruments-JV_IC1139977_KO0,19_KE20,37.htm",
        "salary_min": 127000, "salary_max": 185000,
        "date_posted": "2026-03-10", "source": "Glassdoor",
    },
    {
        "id": "dal_004",
        "title": "AVP, Senior Legal Counsel - Litigation",
        "company": "AT&T",
        "location": "Dallas, TX",
        "description": (
            "Senior litigation counsel in AT&T Legal department. Complex commercial litigation "
            "management, class-action and MDL experience a plus. Trial experience. "
            "Reports to VP litigation."
        ),
        "url": "https://www.att.jobs/job/dallas/avp-senior-legal-counsel-litigation/117/90392887488",
        "salary_min": 188100, "salary_max": 282100,
        "date_posted": "2026-01-08", "source": "AT&T Careers",
    },
    {
        "id": "dal_005",
        "title": "AVP, Senior Legal Counsel - Compliance (Investigations)",
        "company": "AT&T",
        "location": "Dallas, TX",
        "description": (
            "Compliance Legal team. Motivated lawyer with investigative experience. "
            "Internal investigations, regulatory compliance, corporate governance."
        ),
        "url": "https://www.att.jobs/job/dallas/avp-senior-legal-counsel/117/90794176592",
        "salary_min": 231700, "salary_max": 347500,
        "date_posted": "2026-01-20", "source": "AT&T Careers",
    },
    {
        "id": "dal_006",
        "title": "AVP, Senior Legal Counsel - Intellectual Property",
        "company": "AT&T",
        "location": "Dallas, TX",
        "description": (
            "Intellectual property lawyer managing fast-paced national patent litigation docket. "
            "Working with in-house colleagues, outside counsel, and business clients. "
            "Trial experience required."
        ),
        "url": "https://www.legal.io/jobs/5456136/Full-time/AVP-Senior-Legal-Counsel-Intellectual-Property",
        "salary_min": 188100, "salary_max": 282100,
        "date_posted": "2026-01-15", "source": "Legal.io",
    },
    {
        "id": "dal_007",
        "title": "AVP, Senior Legal Counsel - Mergers and Acquisitions",
        "company": "AT&T",
        "location": "Dallas, TX",
        "description": (
            "Leading legal due diligence on contracts, regulatory matters, IP, employment, "
            "benefits, litigation, cybersecurity, and data privacy for M&A transactions."
        ),
        "url": "https://www.att.jobs/job/dallas/avp-senior-legal-counsel-mergers-and-acquisitions/117/92697145408",
        "salary_min": 231700, "salary_max": 347500,
        "date_posted": "2026-03-12", "source": "AT&T Careers",
    },
    {
        "id": "dal_008",
        "title": "Senior Legal Counsel",
        "company": "PGA of America",
        "location": "Frisco, TX",
        "description": (
            "Transactional, corporate, and commercial law. Support GC and Deputy GC on "
            "complex and sensitive matters. Assist with litigation management. Texas Bar "
            "required. 6-8 years experience. Law firm and in-house experience preferred."
        ),
        "url": "https://www.teamworkonline.com/golf-tennis-jobs/pga-of-america/pga-of-america-jobs/senior-legal-counsel-2165762",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-04-08", "source": "TeamWork Online",
    },
    {
        "id": "dal_009",
        "title": "HIPAA Officer & Data Regulatory Counsel",
        "company": "Thomson Reuters",
        "location": "Dallas, TX",
        "description": (
            "GC's Office, reporting to AGC Privacy & Cybersecurity. HIPAA and global privacy "
            "and cybersecurity laws. Security incident response. Technology transactions. "
            "People leadership."
        ),
        "url": "https://www.goinhouse.com/jobs/464935589-hipaa-officer-data-regulatory-counsel-at-thomson-reuters",
        "salary_min": 134680, "salary_max": 250120,
        "date_posted": "2026-02-28", "source": "GoInhouse",
    },
    {
        "id": "dal_010",
        "title": "Senior Legal Counsel",
        "company": "NiCE (NICE Ltd)",
        "location": "Dallas, TX (Hybrid)",
        "description": (
            "Americas Legal team. High-value SaaS and technology transactions for CXone Mpower "
            "platform. DPAs, data privacy, cybersecurity, IP. Scalable contracting processes. "
            "Reports to AGC Americas. 8-10 years."
        ),
        "url": "https://www.goinhouse.com/jobs/516597629-senior-legal-counsel-at-nice",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-03-20", "source": "GoInhouse",
    },
    {
        "id": "dal_011",
        "title": "Deputy General Counsel",
        "company": "Beneficient",
        "location": "Dallas, TX",
        "description": (
            "Strategic legal support. Capital markets, securities, corporate governance, "
            "commercial agreements, complex strategic transactions, financial reporting. "
            "Entrepreneurial environment."
        ),
        "url": "https://www.goinhouse.com/jobs/510251140-deputy-general-counsel-at-beneficient",
        "salary_min": 250600, "salary_max": 319100,
        "date_posted": "2026-03-15", "source": "GoInhouse",
    },
    {
        "id": "dal_012",
        "title": "Counsel, Data Governance & Records Retention",
        "company": "Marsh McLennan",
        "location": "Dallas, TX (Hybrid)",
        "description": (
            "Reports to Chief Cybersecurity and Technology Regulation Counsel. Enterprise "
            "data governance, records retention compliance. Collaborate with legal, compliance, IT."
        ),
        "url": "https://www.goinhouse.com/jobs/503198391-counsel-data-governance-records-retention-at-marshmclennan",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-03-12", "source": "GoInhouse",
    },
    {
        "id": "dal_013",
        "title": "Associate General Counsel - Litigation",
        "company": "Kimberly-Clark",
        "location": "Irving, TX",
        "description": (
            "In-house litigation leadership for global consumer products company. Complex "
            "litigation management, trial strategy, outside counsel oversight."
        ),
        "url": "https://www.linkedin.com/jobs/view/associate-general-counsel-litigation-at-kimberly-clark-3496911839",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-03-01", "source": "LinkedIn",
    },
    {
        "id": "dal_014",
        "title": "AVP, Senior Counsel - Office of the General Counsel",
        "company": "JPMorgan Chase",
        "location": "Plano, TX",
        "description": (
            "Office of the General Counsel, Legal Obligations team. Corporate legal support "
            "for one of the world's largest financial institutions. Plano campus."
        ),
        "url": "https://www.legal.io/jobs/5333248/Full-time/AVP-Senior-Counsel-Office-of-the-General-Counsel-Legal-Obligations/Plano/Texas",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-02-15", "source": "Legal.io",
    },
    {
        # SOURCE: Harvey careers / Ashby
        # Confirmed: https://jobs.ashbyhq.com/harvey/37702381-112a-483c-8f0a-f08e6ba0823d
        "id": "dal_015",
        "title": "Operating Partner, Dallas",
        "company": "Harvey",
        "location": "Dallas, TX",
        "description": (
            "Lead Harvey's new Dallas office. Drive business development, establish "
            "company presence in region. Collaborate with Sales and Customer Success. "
            "Represent Harvey at panels and industry events. Partner-level background "
            "at a law firm with strong local reputation, business development expertise, "
            "legal industry expertise, public speaking, AI knowledge."
        ),
        "url": "https://jobs.ashbyhq.com/harvey/37702381-112a-483c-8f0a-f08e6ba0823d",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-03-15", "source": "Harvey Careers (Ashby)",
    },
    {
        # SOURCE: Harvey careers / Ashby
        # Confirmed: https://jobs.ashbyhq.com/harvey/a6ecda75-fbe4-4b91-806a-bb4f36773390
        "id": "dal_016",
        "title": "Legal Innovation Partner, Dallas",
        "company": "Harvey",
        "location": "Dallas, TX",
        "description": (
            "Strategic counsel to innovation leaders defining and executing AI "
            "transformation. Advise innovation and knowledge teams. Support firm and "
            "client collaboration. Advance legal AI thought leadership through industry "
            "forums and publishing. 5+ years in legal innovation at top firm, corporate "
            "legal team, or legal tech org. Executive presence with CIOs/CKOs/CISOs."
        ),
        "url": "https://jobs.ashbyhq.com/harvey/a6ecda75-fbe4-4b91-806a-bb4f36773390",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-03-20", "source": "Harvey Careers (Ashby)",
    },
    {
        # SOURCE: GoInhouse / Federal Reserve Careers
        # Confirmed: https://www.goinhouse.com/jobs/518612296-deputy-general-counsel-at-federal-reserve
        # NOTE: Applications due April 10, 2026
        "id": "dal_017",
        "title": "Deputy General Counsel",
        "company": "Federal Reserve Bank of Dallas",
        "location": "Dallas, TX",
        "description": (
            "Work with General Counsel and management to provide legal, ethics, and "
            "compliance counsel. Collaborate with peers across the Federal Reserve System. "
            "Ensure practices sustain and enhance the Bank's reputation as a trusted "
            "public and financial institution. Leadership role."
        ),
        "url": "https://www.goinhouse.com/jobs/518612296-deputy-general-counsel-at-federal-reserve",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-04-04", "source": "GoInhouse",
    },
    {
        # SOURCE: GoInhouse / Methodist Health System Workday
        # Confirmed: https://www.goinhouse.com/jobs/516019044-senior-counsel-transactions-and-technology-at-methodist-health-system
        "id": "dal_018",
        "title": "Senior Counsel - Transactions and Technology",
        "company": "Methodist Health System",
        "location": "Dallas, TX",
        "description": (
            "Advise on corporate matters, contract negotiation and drafting, real estate "
            "transactions, due diligence. Technology transactions, SaaS agreements. "
            "Collaborate with fellow counsel and business partners at all levels of "
            "hospital management. In-house experience preferred."
        ),
        "url": "https://www.goinhouse.com/jobs/516019044-senior-counsel-transactions-and-technology-at-methodist-health-system",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-03-25", "source": "GoInhouse",
    },
    {
        # SOURCE: D.R. Horton careers / Glassdoor / Ladders
        "id": "dal_019",
        "title": "Head of Litigation",
        "company": "D.R. Horton",
        "location": "Arlington, TX",
        "description": (
            "Senior executive overseeing all litigation, claims management, and "
            "dispute-resolution activities. Directs enterprise-wide litigation strategy. "
            "Leads high-performing team managing complex legal matters, outside counsel, "
            "and litigation risk across all divisions and business units. 12+ years "
            "progressive litigation experience, complex high-exposure matters, proven "
            "leadership overseeing corporate litigation teams or lead counsel."
        ),
        "url": "https://www.glassdoor.com/Jobs/D-R-Horton-attorney-Jobs-EI_IE2195.0,10_KO11,19.htm",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-03-20", "source": "Glassdoor / D.R. Horton Careers",
    },
    {
        # SOURCE: D.R. Horton careers / Ladders
        "id": "dal_020",
        "title": "General Counsel",
        "company": "D.R. Horton",
        "location": "Arlington, TX",
        "description": (
            "Chief legal advisor to CEO, executive team and Board of Directors. "
            "Strategic guidance on all legal, regulatory, and governance matters. "
            "Top-level GC role at Fortune 500 homebuilder. Overall responsibility "
            "for litigation, transactions, regulatory, corporate governance."
        ),
        "url": "https://www.theladders.com/job/general-counsel-drhorton-arlington-tx_84738905",
        "salary_min": None, "salary_max": None,
        "date_posted": "2026-03-10", "source": "Ladders / D.R. Horton Careers",
    },
]


def _salary_str(job: dict) -> str:
    s_min = job.get("salary_min")
    s_max = job.get("salary_max")
    if s_min and s_max:
        return f"${s_min:,} - ${s_max:,}"
    elif s_min:
        return f"${s_min:,}+"
    return "Not listed"


def _truncate(text: str, length: int = 120) -> str:
    text = " ".join(text.split())
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + "..."


def print_report(title: str, jobs: list[dict]):
    ranked = rank_jobs(jobs)
    now = datetime.now().strftime("%B %d, %Y")

    print()
    print("=" * 100)
    print(f"  {title}")
    print(f"  {now} | {len(ranked)} qualified matches from {len(jobs)} postings")
    print("=" * 100)
    print()
    print(f"  {'#':<4} {'Company':<22} {'Title':<45} {'Salary':<22} {'Score'}")
    print(f"  {'-'*4} {'-'*22} {'-'*45} {'-'*22} {'-'*5}")

    for i, job in enumerate(ranked, 1):
        company = job['company'][:20]
        title_str = job['title'][:43]
        salary = _salary_str(job)
        print(f"  {i:<4} {company:<22} {title_str:<45} {salary:<22} {job['score']} pts")

    print()
    print("  DETAILS")
    print("  " + "-" * 98)

    for i, job in enumerate(ranked, 1):
        summary = _truncate(job.get("description", ""), 140)
        salary = _salary_str(job)
        print(f"""
  #{i}  {job['title']}
       {job['company']} | {job['location']}
       Salary: {salary}
       {summary}
       Source: {job['source']} — {job['url']}""")

    print()
    print("  " + "=" * 98)


def main():
    print_report("REPORT 1: LEGAL / AI / TECHNOLOGY ROLES (NATIONAL)", AI_TECH_JOBS)
    print_report("REPORT 2: DALLAS-AREA IN-HOUSE POSITIONS (ALL PRACTICE AREAS)", DALLAS_JOBS)


if __name__ == "__main__":
    main()
