"""
Job Search Agent — Contact Suggestions

Maps known contacts to companies and industries so the daily report
can suggest warm introductions for each job match.
"""

# ---------------------------------------------------------------------------
# Known contacts: people James has a direct or warm relationship with.
# Each entry includes name, title, org, LinkedIn, and tags for matching.
# ---------------------------------------------------------------------------

CONTACTS = [
    # -- Direct co-panelists / collaborators --
    {
        "name": "Omar Haroun",
        "title": "Co-Founder & CEO",
        "org": "Eudia",
        "linkedin": "https://www.linkedin.com/in/omarharoun/",
        "relationship": "LegalWeek 2025 co-panelist; Eudia customer (Southwest)",
        "tags": ["legal tech", "AI", "eudia", "legal operations", "generative AI", "law firm"],
    },
    {
        "name": "Rob Beard",
        "title": "Chief Legal & Global Affairs Officer",
        "org": "Coherent",
        "linkedin": "https://www.linkedin.com/in/rpbeard/",
        "relationship": "LegalWeek 2025 co-panelist",
        "tags": ["general counsel", "CLO", "AI governance", "technology", "coherent", "mastercard", "micron"],
    },
    {
        "name": "Farrah Pepper",
        "title": "Chief Legal Innovation Counsel",
        "org": "Marsh McLennan",
        "linkedin": "https://www.linkedin.com/in/farrahpepper/",
        "relationship": "LegalWeek 2025 co-panelist",
        "tags": ["legal innovation", "legal operations", "AI", "insurance", "marsh mclennan", "discovery", "CLOC"],
    },
    {
        "name": "Justin Bundick",
        "title": "Managing Director, AI & Data Transformation",
        "org": "Southwest Airlines",
        "linkedin": "https://www.linkedin.com/in/justinbundick/",
        "relationship": "ABA 2024 co-panelist; internal partner at Southwest",
        "tags": ["AI", "data transformation", "southwest airlines", "airline", "aviation"],
    },

    # -- Eudia ecosystem --
    {
        "name": "Gary Hood",
        "title": "General Counsel",
        "org": "Duracell",
        "linkedin": "",
        "relationship": "Eudia Summit speaker; fellow Eudia customer",
        "tags": ["general counsel", "eudia", "AI", "consumer goods", "duracell"],
    },
    {
        "name": "Mark Smolik",
        "title": "Chief Legal Officer",
        "org": "DHL",
        "linkedin": "",
        "relationship": "Eudia Summit speaker; fellow Eudia customer",
        "tags": ["CLO", "general counsel", "eudia", "logistics", "dhl", "supply chain"],
    },
    {
        "name": "Dan Mascaro",
        "title": "Advisor (former CLO, Progressive)",
        "org": "Eudia Counsel",
        "linkedin": "",
        "relationship": "Eudia Counsel advisor",
        "tags": ["general counsel", "CLO", "insurance", "progressive", "eudia", "advisory"],
    },
    {
        "name": "David Onorato",
        "title": "Advisor (former GC, Royal Bank of Canada)",
        "org": "Eudia Counsel",
        "linkedin": "",
        "relationship": "Eudia Counsel advisor",
        "tags": ["general counsel", "banking", "finance", "eudia", "advisory"],
    },

    # -- Ironclad advisory board peers --
    {
        "name": "Mike Russell",
        "title": "Head of Global Legal Ops",
        "org": "Expedia",
        "linkedin": "",
        "relationship": "Ironclad advisory board peer",
        "tags": ["legal operations", "CLM", "ironclad", "expedia", "travel", "technology"],
    },
    {
        "name": "Jason Boehmig",
        "title": "Co-Founder & Executive Chairman",
        "org": "Ironclad",
        "linkedin": "https://www.linkedin.com/in/jboehmig/",
        "relationship": "Ironclad advisory board host",
        "tags": ["legal tech", "CLM", "ironclad", "contracts", "AI"],
    },
    {
        "name": "Jasmine Singh",
        "title": "General Counsel",
        "org": "Ironclad",
        "linkedin": "",
        "relationship": "Ironclad advisory board",
        "tags": ["general counsel", "legal tech", "ironclad", "patreon", "pinterest"],
    },

    # -- CLOC / Legal Ops --
    {
        "name": "Áine Lyons",
        "title": "SVP & Deputy General Counsel",
        "org": "Workday",
        "linkedin": "",
        "relationship": "CLOC President 2026",
        "tags": ["deputy general counsel", "legal operations", "CLOC", "workday", "technology", "SaaS"],
    },
    {
        "name": "Laura Dieudonné",
        "title": "Legal Ops & Administration Director",
        "org": "Delta Air Lines",
        "linkedin": "",
        "relationship": "CLOC Board; airline industry peer",
        "tags": ["legal operations", "CLOC", "delta", "airline", "aviation"],
    },

    # -- ABA / Legal community --
    {
        "name": "Marissa Lefland",
        "title": "Attorney",
        "org": "Condon & Forsyth LLP",
        "linkedin": "",
        "relationship": "ABA 2023 co-panelist",
        "tags": ["aviation", "litigation", "law firm", "AI"],
    },
]


def suggest_contacts(job: dict, max_suggestions: int = 3) -> list[dict]:
    """
    Given a scored job, return up to max_suggestions relevant contacts.

    Matches contacts based on:
    1. Company name overlap (strongest signal)
    2. Tag overlap with job title, company, description, and matched keywords
    """
    title = job.get("title", "").lower()
    company = job.get("company", "").lower()
    description = job.get("description", "").lower()
    matched_keywords = [kw.lower() for kw in job.get("matched_keywords", [])]
    searchable = f"{title} {company} {description} {' '.join(matched_keywords)}"

    scored_contacts = []

    for contact in CONTACTS:
        score = 0

        # Company name match (strongest signal)
        if contact["org"].lower() in company or company in contact["org"].lower():
            score += 50

        # Tag matching against job text
        tag_matches = 0
        for tag in contact["tags"]:
            if tag.lower() in searchable:
                tag_matches += 1
        score += tag_matches * 5

        # Bonus for contacts whose org appears in the description
        if contact["org"].lower() in description:
            score += 15

        if score > 0:
            scored_contacts.append({**contact, "_relevance": score})

    # Sort by relevance, return top N
    scored_contacts.sort(key=lambda c: c["_relevance"], reverse=True)
    return scored_contacts[:max_suggestions]
