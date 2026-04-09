"""
Job Search Agent — Configuration

Profile, search parameters, scoring weights, and preferences for
James Sheppard's daily job search report.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------
AGENT_DIR = Path(__file__).parent
DATA_DIR = AGENT_DIR / "data"
SEEN_JOBS_FILE = DATA_DIR / "seen_jobs.json"

# ---------------------------------------------------------------------------
# User Profile
# ---------------------------------------------------------------------------
PROFILE = {
    "name": "James Sheppard",
    "email": "shepjames@gmail.com",
    "location": "Dallas, TX",
    "years_experience": 15,
    "education": [
        "J.D., Georgetown University Law Center, 2009",
        "B.A. History, Boston College, 2002",
    ],
    "current_role": "Associate General Counsel – Information Governance & Legal Operations",
    "current_employer": "Southwest Airlines",
    "target_levels": [
        "Associate General Counsel",
        "Deputy General Counsel",
        "General Counsel",
        "VP Legal",
        "SVP Legal",
        "Chief Legal Officer",
    ],
    "salary_floor": 225000,
    "prefers_equity": True,
}

# ---------------------------------------------------------------------------
# Skills & Keywords (used for matching/scoring)
# ---------------------------------------------------------------------------
# Tier 1: Core differentiators (highest weight)
TIER1_KEYWORDS = [
    "artificial intelligence",
    "AI governance",
    "AI policy",
    "generative AI",
    "responsible AI",
    "AI compliance",
    "AI risk",
    "legal operations",
    "legal technology",
    "legal tech",
    "legaltech",
    "legal ops",
]

# Tier 2: Strong match skills
TIER2_KEYWORDS = [
    "data privacy",
    "privacy counsel",
    "privacy officer",
    "CCPA",
    "GDPR",
    "technology transactions",
    "SaaS agreements",
    "cybersecurity",
    "incident response",
    "information governance",
    "contract lifecycle management",
    "CLM",
    "e-discovery",
    "AIGP",
    "CIPP",
]

# Tier 3: Relevant but broader
TIER3_KEYWORDS = [
    "commercial litigation",
    "intellectual property",
    "trademark",
    "outside counsel management",
    "vendor management",
    "regulatory compliance",
    "enterprise technology",
    "digital transformation",
    "people leadership",
    "team leadership",
]

# ---------------------------------------------------------------------------
# Search Queries (used across job search APIs)
# ---------------------------------------------------------------------------
SEARCH_QUERIES = [
    "Associate General Counsel AI governance",
    "Deputy General Counsel artificial intelligence",
    "General Counsel AI privacy",
    "AI governance counsel",
    "legal operations AI technology",
    "Associate General Counsel data privacy cybersecurity",
    "Associate General Counsel technology transactions",
    "Deputy General Counsel privacy AI",
    "VP Legal AI governance",
    "General Counsel technology",
    "Associate General Counsel information governance",
    "legal counsel AI policy",
    "Associate General Counsel legal technology",
]

# ---------------------------------------------------------------------------
# Location Preferences
# ---------------------------------------------------------------------------
PREFERRED_LOCATIONS = ["Dallas", "DFW", "Fort Worth", "Plano", "Frisco", "Irving"]
ACCEPTABLE_LOCATIONS = ["Remote", "Hybrid", "Anywhere", "United States"]

# ---------------------------------------------------------------------------
# Company / Role Filters
# ---------------------------------------------------------------------------
# Exclude roles clearly below target level
EXCLUDE_TITLE_KEYWORDS = [
    "paralegal",
    "intern",
    "junior",
    "entry level",
    "legal assistant",
    "contract attorney",
    "staff attorney",
    "associate attorney",  # law firm associate, not AGC
    "law clerk",
]

# ---------------------------------------------------------------------------
# Scoring Weights
# ---------------------------------------------------------------------------
SCORING = {
    "tier1_keyword_weight": 10,  # per keyword match
    "tier2_keyword_weight": 5,
    "tier3_keyword_weight": 2,
    "preferred_location_bonus": 25,
    "acceptable_location_bonus": 10,
    "salary_meets_floor_bonus": 15,
    "equity_mention_bonus": 10,
    "seniority_match_bonus": 20,
    "minimum_score_threshold": 15,  # jobs below this are excluded from report
}

# ---------------------------------------------------------------------------
# API Keys & Credentials (loaded from environment variables)
# ---------------------------------------------------------------------------
# JSearch API (RapidAPI) — primary source, aggregates LinkedIn/Indeed/etc.
JSEARCH_API_KEY = os.environ.get("JSEARCH_API_KEY", "")

# Adzuna API — secondary source
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "")

# Gmail SMTP credentials
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "shepjames@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

# ---------------------------------------------------------------------------
# Report Settings
# ---------------------------------------------------------------------------
REPORT_RECIPIENT = "shepjames@gmail.com"
REPORT_SUBJECT_PREFIX = "Daily Legal AI Job Report"
MAX_JOBS_IN_REPORT = 25  # cap the email at top N matches
