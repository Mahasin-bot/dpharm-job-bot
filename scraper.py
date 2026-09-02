# scraper.py
# A deliberately generic scraper: most Indian govt "Notices / Recruitment"
# pages are either an HTML <table> or a list of <li>/<a> items containing a
# post title, a date, and a link to a PDF/notice. Rather than writing a
# brittle per-site CSS-selector scraper (which breaks the moment a ministry
# redesigns its site), this walks tables and link-lists generically and lets
# filters.py decide relevance.
#
# If a specific source needs custom handling later, add a function named
# scrape_<something>(html, source) and call it from scrape_source() below.

import requests
from bs4 import BeautifulSoup

from filters import is_relevant, extract_last_date, compute_priority, priority_label

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

TIMEOUT = 20


def fetch(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.text


def _rows_from_tables(soup: BeautifulSoup):
    rows = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            text = tr.get_text(" ", strip=True)
            link_tag = tr.find("a", href=True)
            link = link_tag["href"] if link_tag else None
            if text:
                rows.append((text, link))
    return rows


def _rows_from_lists(soup: BeautifulSoup):
    rows = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        if text and len(text) > 8:  # skip nav/menu links like "Home"
            rows.append((text, a["href"]))
    return rows


def scrape_source(source: dict):
    """
    Returns a list of dicts, one per relevant (D.Pharm/Pharmacist) listing
    found on this source's page.
    """
    results = []
    try:
        html = fetch(source["url"])
    except Exception as e:
        return [{
            "error": True,
            "source": source["name"],
            "message": str(e),
        }]

    soup = BeautifulSoup(html, "lxml")

    candidates = _rows_from_tables(soup)
    if not candidates:
        candidates = _rows_from_lists(soup)

    seen_texts = set()
    for text, link in candidates:
        if text in seen_texts:
            continue
        seen_texts.add(text)

        if not is_relevant(text):
            continue

        if link and not link.startswith("http"):
            base = source["url"].rstrip("/")
            link = base + "/" + link.lstrip("/")

        priority_score = compute_priority(source, text)

        results.append({
            "error": False,
            "title": text[:300],
            "link": link or source["url"],
            "source": source["name"],
            "state": source["state"],
            "district": source.get("district"),
            "last_date": extract_last_date(text),
            "priority_score": priority_score,
            "priority_label": priority_label(priority_score),
        })

    return results


def scrape_all(sources: list):
    all_results = []
    for source in sources:
        all_results.extend(scrape_source(source))
    # highest priority first
    all_results.sort(key=lambda r: r.get("priority_score", 0), reverse=True)
    return all_results
