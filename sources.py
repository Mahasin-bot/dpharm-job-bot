# sources.py
# ---------------------------------------------------------------------------
# Configured job sources. Each entry is a page (usually a "Recruitment /
# Notice / Career" listing page) that the scraper will fetch and scan for
# D.Pharm / Pharmacist vacancies.
#
# IMPORTANT: Government site URLs and page structures change often. These
# are starter entries based on the official bodies most relevant to D.Pharm
# Government Pharmacist recruitment in India, with West Bengal prioritized.
# Verify each URL still points to the correct notice/listing page before
# relying on it, and add/remove entries freely -- that's what this file is
# for. No scraper library can promise these stay valid forever.
#
# Fields:
#   name      - human-readable source name (shown in Telegram messages)
#   url       - the listing page to scrape
#   state     - "West Bengal", another state name, or "Central"
#   district  - specific WB district if the source is district-level, else None
#   base_priority - starting priority score before D.Pharm/WB boosts (higher = more important)
# ---------------------------------------------------------------------------

WB_DISTRICTS = [
    "Kolkata", "Howrah", "Hooghly", "North 24 Parganas", "South 24 Parganas",
    "Nadia", "Murshidabad", "Purba Bardhaman", "Paschim Bardhaman", "Birbhum",
    "Purulia", "Bankura", "Paschim Medinipur", "Purba Medinipur", "Jhargram",
    "Malda", "Uttar Dinajpur", "Dakshin Dinajpur", "Darjeeling", "Kalimpong",
    "Jalpaiguri", "Alipurduar", "Cooch Behar",
    # newer/proposed districts (2022 reorganisation) - kept for text matching
    "Sundarban", "Ranaghat", "Bishnupur", "Kandi", "Berhampore",
    "Basirhat", "Ichamati",
]

SOURCES = [
    # ---------------- West Bengal (highest priority) ----------------
    {
        "name": "WBHRB (WB Health Recruitment Board)",
        "url": "https://www.hrb.wb.gov.in",
        "state": "West Bengal",
        "district": None,
        "base_priority": 100,
    },
    {
        "name": "WBPSC (WB Public Service Commission)",
        "url": "https://wbpsc.gov.in",
        "state": "West Bengal",
        "district": None,
        "base_priority": 95,
    },
    {
        "name": "WB Health & Family Welfare Dept.",
        "url": "https://www.wbhealth.gov.in",
        "state": "West Bengal",
        "district": None,
        "base_priority": 95,
    },
    {
        "name": "WBMSC (WB Medical Services Corp.)",
        "url": "https://wbmsc.co.in",
        "state": "West Bengal",
        "district": None,
        "base_priority": 90,
    },
    # District Health & Family Welfare Samitis frequently hire pharmacists
    # on contract. Add each district's page here as you find stable URLs --
    # this is the main place to expand district-level WB coverage.
    {
        "name": "DHFWS Uttar Dinajpur (District Health Society)",
        "url": "https://uttardinajpur.gov.in/notice_category/recruitment/",
        "state": "West Bengal",
        "district": "Uttar Dinajpur",
        "base_priority": 90,
    },
    # Example placeholder for adding more districts later:
    # {
    #     "name": "Purba Bardhaman District Health Society",
    #     "url": "https://<confirm-actual-url>",
    #     "state": "West Bengal",
    #     "district": "Purba Bardhaman",
    #     "base_priority": 85,
    # },

    # ---------------- Central Government ----------------
    {
        "name": "SSC (Staff Selection Commission)",
        "url": "https://ssc.gov.in/home/notice-board",
        "state": "Central",
        "district": None,
        "base_priority": 60,
    },
    {
        "name": "ESIC (Employees' State Insurance Corp.)",
        "url": "https://www.esic.gov.in",
        "state": "Central",
        "district": None,
        "base_priority": 60,
    },
    {
        "name": "DGHS (Directorate General of Health Services)",
        "url": "https://dghs.gov.in",
        "state": "Central",
        "district": None,
        "base_priority": 60,
    },
    {
        "name": "Indian Army - Join Indian Army (AFMS Pharmacist)",
        "url": "https://joinindianarmy.nic.in",
        "state": "Central",
        "district": None,
        "base_priority": 55,
    },
    {
        "name": "RRB (Railway Recruitment - Paramedical)",
        "url": "https://www.rrbapply.gov.in",
        "state": "Central",
        "district": None,
        "base_priority": 55,
    },

    # ---------------- Other States (lower default priority) ----------------
    # Add other State PSCs / Health Recruitment Boards here the same way.
    # {
    #     "name": "Bihar Technical Service Commission",
    #     "url": "https://btsc.bih.nic.in",
    #     "state": "Bihar",
    #     "district": None,
    #     "base_priority": 40,
    # },
]
