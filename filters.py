# filters.py
# Decides whether a scraped listing is a relevant D.Pharm Pharmacist post,
# extracts a probable "last date", tags location, and scores priority
# (West Bengal jobs are boosted to the top as requested).

import re
from datetime import datetime
from sources import WB_DISTRICTS

# Keywords that indicate the post is relevant to D.Pharm / Pharmacist roles
INCLUDE_KEYWORDS = [
    "pharmacist", "pharmacy", "d.pharm", "dpharm", "diploma in pharmacy",
    "drug inspector",  # sometimes requires pharmacy diploma/degree, optional
]

# Keywords that usually signal an unrelated post sharing a listing page
# (kept minimal & conservative so we don't accidentally drop real posts)
EXCLUDE_KEYWORDS = [
    "b.pharm only", "m.pharm only", "pharm.d only",
]

DATE_PATTERNS = [
    r"\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\b",
    r"\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b",
]


def is_relevant(text: str) -> bool:
    t = text.lower()
    if not any(k in t for k in INCLUDE_KEYWORDS):
        return False
    if any(k in t for k in EXCLUDE_KEYWORDS):
        return False
    return True


def extract_last_date(text: str) -> str:
    """Best-effort extraction of a closing/last date mentioned near the post."""
    for pattern in DATE_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return "Not found - check source page"


def detect_district(text: str):
    t = text.lower()
    for d in WB_DISTRICTS:
        if d.lower() in t:
            return d
    return None


def compute_priority(source: dict, text: str) -> int:
    """
    Higher score = shown first / flagged higher priority.
    West Bengal source or a WB district mentioned in the text gets a big boost,
    per the user's requirement to prioritize West Bengal jobs.
    """
    score = source.get("base_priority", 50)

    if source.get("state") == "West Bengal":
        score += 200

    district = detect_district(text)
    if district:
        score += 50

    if "d.pharm" in text.lower() or "diploma in pharmacy" in text.lower():
        score += 20  # exact D.Pharm match ranks above generic "pharmacist"

    return score


def priority_label(score: int) -> str:
    if score >= 250:
        return "🔴 HIGH (West Bengal)"
    if score >= 100:
        return "🟠 MEDIUM (Other State)"
    return "🟡 STANDARD (Central)"
