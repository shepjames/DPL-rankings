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
    "team_size": 16,
    "contract_portfolio": "$1B+ TCV, 90+ active agreements",
    "key_vendors": [
        "AWS", "Anthropic", "Microsoft", "Workday",
        "CrowdStrike", "ServiceNow",
    ],
    "legal_tech_stack": [
        "Ironclad (CLM)", "iManage (DMS)", "TeamConnect (matter mgmt)",
        "DISCO (e-discovery)", "Zapproved/Exterro (preservation)",
        "Eudia (AI-augmented legal)", "Harvey (AI pilot, 30+ users)",
    ],
    "notable_achievements": [
        "$1M+ outside counsel spend reduction FY 2025",
        "22-firm preferred panel network, $1M+ savings Q1 2026",
        "Ironclad CLM: 1,000+ contract workflows in first 3 months",
        "Two California jury trial defense verdicts ($60M+ and $25M+)",
        "$76M cyber insurance claim ($50M paid by four carriers)",
        "Hertz creditors' committee chair: 100% recovery on $35M+ claim",
    ],
    "target_levels": [
        "Associate General Counsel",
        "Deputy General Counsel",
        "General Counsel",
        "VP Legal",
        "SVP Legal",
        "Chief Legal Officer",
        "Operating Partner",
        "Legal Innovation Partner",
    ],
    "salary_floor": 225000,
    "prefers_equity": True,
}

# ---------------------------------------------------------------------------
# Skills & Keywords (used for matching/scoring)
#
# Organized around the 9 resume skill areas, plus a legal tech vendor tier.
# ---------------------------------------------------------------------------

# Tier 1: Core differentiators (highest weight — 10 pts each)
# Maps to: Artificial Intelligence, Legal Technology/Legal Operations, Data Privacy
TIER1_KEYWORDS = [
    # -- Artificial Intelligence --
    "artificial intelligence",
    "AI governance",
    "AI policy",
    "generative AI",
    "responsible AI",
    "AI compliance",
    "AI risk",
    "AI acceptable use",
    "AI ethics",
    "AIGP",
    # -- Litigation Leadership (core differentiator) --
    "head of litigation",
    "chief litigation counsel",
    "vice president litigation",
    "VP litigation",
    "senior litigation counsel",
    # -- Legal Technology / Legal Operations --
    "legal operations",
    "legal technology",
    "legal tech",
    "legaltech",
    "legal ops",
    "legal innovation",
    "legal innovation partner",
    "operating partner",
    "AI transformation",
    # -- Data Privacy --
    "data privacy",
    "privacy counsel",
    "privacy officer",
    "chief privacy officer",
    "CCPA",
    "GDPR",
    "CIPP",
]

# Tier 2: Strong match skills (5 pts each)
# Maps to: Technology Transactions, Cybersecurity Incident Response,
#          People Leadership, Outside Counsel Management
TIER2_KEYWORDS = [
    # -- Technology Transactions --
    "technology transactions",
    "SaaS agreements",
    "SaaS contracts",
    "data license",
    "DPA",
    "data processing agreement",
    "software licensing",
    "cloud agreements",
    "technology contracts",
    "IT agreements",
    # -- Cybersecurity Incident Response --
    "cybersecurity",
    "cyber incident",
    "incident response",
    "CISO",
    "information security",
    "data breach",
    "TSA compliance",
    "cyber insurance",
    "third-party risk management",
    "third party risk",
    # -- People Leadership --
    "people leadership",
    "team leadership",
    "managing team",
    "direct reports",
    "lead a team",
    "leadership of legal",
    # -- Outside Counsel Management --
    "outside counsel management",
    "outside counsel",
    "law firm management",
    "legal spend",
    "preferred law firm",
    "vendor management",
    # -- Airline / Aviation / Transportation --
    "airline",
    "aviation",
    "transportation",
    "FAA",
    "DOT",
    "TSA",
]

# Tier 3: Relevant but broader (2 pts each)
# Maps to: Commercial Litigation, Trademark/IP Litigation,
#          and adjacent skills
TIER3_KEYWORDS = [
    # -- Commercial Litigation --
    "commercial litigation",
    "complex litigation",
    "class action",
    "multi-district litigation",
    "MDL",
    "trial experience",
    "jury trial",
    "litigation management",
    "litigation strategy",
    "claims management",
    "dispute resolution",
    "high-exposure",
    # -- Trademark / IP Litigation --
    "intellectual property",
    "trademark",
    "IP litigation",
    "patent",
    "trade secret",
    "data scraping",
    # -- Adjacent / General --
    "information governance",
    "e-discovery",
    "regulatory compliance",
    "enterprise technology",
    "digital transformation",
    "contract lifecycle management",
    "CLM",
    "insurtech",
    "insurance",
    "financial services",
]

# Tier 4: Legal tech vendor references (1 pt each — small signal boost)
# Indicates tech-forward legal team using tools James has experience with.
LEGAL_TECH_VENDORS = [
    # -- Matter Management --
    "TeamConnect",
    "matter management",
    "legal matter management",
    # -- Document Management --
    "iManage",
    "document management system",
    "NetDocuments",
    # -- E-Billing --
    "Collaborati",
    "e-billing",
    "legal billing",
    "BrightFlag",
    # -- Contract Lifecycle Management --
    "Ironclad",
    "Agiloft",
    "Icertis",
    "DocuSign CLM",
    "ContractPodAi",
    # -- E-Discovery & Legal Preservation --
    "CS Disco",
    "DISCO",
    "Relativity",
    "Logikcull",
    "Zapproved",
    "Exterro",
    # -- GenAI Legal Tools --
    "Harvey",
    "Harvey AI",
    "Legora",
    "Eudia",
    "CoCounsel",
    "Luminance",
    "Spellbook",
    "EvenUp",
    "Casetext",
    "Robin AI",
    "Klarity",
    "Anthropic",
    # -- Enterprise Tech Vendors (from contract portfolio) --
    "AWS",
    "Workday",
    "CrowdStrike",
    "ServiceNow",
]

# ---------------------------------------------------------------------------
# Search Queries (used across job search APIs)
# ---------------------------------------------------------------------------
SEARCH_QUERIES = [
    # In-house AI governance / privacy roles
    "Associate General Counsel AI governance",
    "Deputy General Counsel artificial intelligence",
    "General Counsel AI privacy",
    "AI governance counsel",
    "Associate General Counsel data privacy cybersecurity",
    "Deputy General Counsel privacy AI",
    "VP Legal AI governance",
    # In-house technology / legal ops roles
    "Associate General Counsel technology transactions",
    "General Counsel technology",
    "Associate General Counsel information governance",
    "Associate General Counsel legal technology",
    "legal operations AI technology",
    "legal counsel AI policy",
    # Legal tech company roles (Harvey, Eudia, Ironclad, etc.)
    "legal tech company operating partner Dallas",
    "legal innovation partner AI",
    "Harvey AI legal jobs Dallas",
    "legal tech startup general counsel VP legal",
    "legal AI company customer success director",
    # Litigation leadership roles (leverages James's trial experience)
    "Head of Litigation in-house job",
    "VP Litigation Dallas Texas",
    "Chief Litigation Counsel",
    "Director of Litigation corporate",
    "senior litigation counsel in-house Dallas",
    # Airline / aviation / transportation legal roles
    "airline general counsel VP legal",
    "airline associate general counsel",
    "aviation general counsel deputy",
    "transportation company VP legal counsel",
    # Dallas-specific broader search
    "Dallas Associate General Counsel in-house",
    "Dallas Deputy General Counsel",
    "Dallas senior counsel in-house hiring",
    "Dallas General Counsel in-house new posting",
    "Frisco Plano Irving general counsel senior counsel",
    "Dallas in-house legal department hiring counsel",
    # Dallas major employers — legal departments actively hiring
    "Integrity Marketing Group Dallas legal counsel",
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

# Jobs already applied to — exclude specific postings (by URL substring)
APPLIED_JOBS = [
    "harvey/37702381",   # Harvey Operating Partner, Dallas
    "harvey/a6ecda75",   # Harvey Legal Innovation Partner, Dallas
]

# ---------------------------------------------------------------------------
# Scoring Weights
# ---------------------------------------------------------------------------
SCORING = {
    "tier1_keyword_weight": 10,  # per match — AI, legal tech, data privacy
    "tier2_keyword_weight": 5,   # per match — tech transactions, cyber, leadership, OCM
    "tier3_keyword_weight": 2,   # per match — litigation, IP, adjacent
    "vendor_keyword_weight": 1,  # per match — legal tech vendor/tool references
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
# Serper.dev — primary source (Google Search API for job postings)
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")

# JSearch API (RapidAPI) — optional secondary source
JSEARCH_API_KEY = os.environ.get("JSEARCH_API_KEY", "")

# Adzuna API — optional secondary source
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
