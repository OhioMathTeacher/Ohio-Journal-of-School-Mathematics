#!/usr/bin/env python3
"""OJSM Citation Audit — Stage 1: Inventory.

Walks the Janeway sitemap of the Ohio Journal of School Mathematics
to discover every article, then visits each article page to extract
metadata (title, authors, year, DOI, PDF galley URL).

Output: datasets/ojsm-audit/inventory.json
    {
      "generated_at": "2026-05-06T03:14:00",
      "total_articles": 217,
      "articles": [
        {
          "article_id": 4149,
          "issue_id": 170 | null,        # null for orphans
          "url": "https://ohiomathjournal.org/article/id/4149/",
          "title": "...",
          "authors": ["Flick, M.", "Kuchey, D."],
          "year": "2017",
          "doi": "10.18061/ojsm.4149" | null,
          "pdf_url": "https://ohiomathjournal.org/article/4149/galley/.../download/" | null,
          "fetched_at": "2026-05-06T03:14:01"
        },
        ...
      ]
    }

Usage:
    # Process a single issue (use this first for testing)
    python3 scripts/ojsm_inventory.py --issue 379

    # Process the entire journal (run after one-issue test passes)
    python3 scripts/ojsm_inventory.py --all

    # Resume an interrupted run (skips articles already in inventory.json)
    python3 scripts/ojsm_inventory.py --all --resume
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin
from xml.etree import ElementTree as ET

import requests

JOURNAL_BASE = "https://ohiomathjournal.org"
SITEMAP_INDEX = f"{JOURNAL_BASE}/sitemap.xml"
USER_AGENT = "OJSM-CitationAudit/0.1 (research; +contact: editor@ohiomathjournal.org)"
REQUEST_DELAY_SECONDS = 0.5  # be polite to the Janeway server

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "datasets" / "ojsm-audit"
INVENTORY_PATH = OUTPUT_DIR / "inventory.json"

# Sitemap XML namespace used by Janeway.
SM_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

# Article URL patterns accepted from issue sitemaps.
ARTICLE_URL_RE = re.compile(r"/article/(?:id/)?(\d+)/?$")

# DOI pattern (used to extract from "How to Cite" line on article pages).
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>]+")

# PDF galley URL pattern (Janeway).
GALLEY_RE = re.compile(r'href="(/article/\d+/galley/\d+/(?:view|download)/?)"', re.I)


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def fetch_xml(url: str, sess: requests.Session) -> ET.Element:
    resp = sess.get(url, timeout=30)
    resp.raise_for_status()
    return ET.fromstring(resp.content)


def fetch_html(url: str, sess: requests.Session) -> str:
    resp = sess.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def list_issue_sitemaps(sess: requests.Session) -> list[str]:
    """Return URLs of every per-issue sitemap from the journal sitemap index."""
    root = fetch_xml(SITEMAP_INDEX, sess)
    urls = [el.text.strip() for el in root.findall("sm:sitemap/sm:loc", SM_NS) if el.text]
    # Filter to only issue sitemaps (defensive — index may include other types).
    return [u for u in urls if "/issue/" in u and u.endswith("_sitemap.xml")]


def list_articles_in_issue(issue_sitemap_url: str, sess: requests.Session) -> list[tuple[int, str]]:
    """Return (article_id, article_url) tuples for every article in an issue.

    Issue sitemap URL form: https://ohiomathjournal.org/issue/<id>_sitemap.xml
    """
    root = fetch_xml(issue_sitemap_url, sess)
    out = []
    for loc in root.findall("sm:url/sm:loc", SM_NS):
        if not loc.text:
            continue
        url = loc.text.strip()
        m = ARTICLE_URL_RE.search(url)
        if m:
            out.append((int(m.group(1)), url))
    return out


def issue_id_from_sitemap_url(url: str) -> Optional[int]:
    m = re.search(r"/issue/(\d+)_sitemap\.xml$", url)
    return int(m.group(1)) if m else None


def parse_article_metadata(html: str, article_url: str) -> dict:
    """Extract title, authors, year, DOI, and PDF galley URL from a Janeway article page.

    Heuristic-based — Janeway markup varies by theme, so we use multiple
    fallbacks rather than committing to one CSS path.
    """
    meta: dict = {"title": None, "authors": [], "year": None, "doi": None, "pdf_url": None}

    # Title — try citation_title meta, then <h1>, then <title>.
    m = re.search(r'<meta[^>]+name="citation_title"[^>]+content="([^"]+)"', html, re.I)
    if m:
        meta["title"] = m.group(1).strip()
    else:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
        if m:
            meta["title"] = re.sub(r"<[^>]+>", "", m.group(1)).strip()

    # Authors — citation_author meta tags (one per author).
    authors = re.findall(r'<meta[^>]+name="citation_author"[^>]+content="([^"]+)"', html, re.I)
    meta["authors"] = [a.strip() for a in authors]

    # Year — citation_publication_date or citation_date.
    m = re.search(r'<meta[^>]+name="citation_(?:publication_)?date"[^>]+content="(\d{4})', html, re.I)
    if m:
        meta["year"] = m.group(1)

    # DOI — citation_doi meta first, then plain DOI regex on page.
    m = re.search(r'<meta[^>]+name="citation_doi"[^>]+content="([^"]+)"', html, re.I)
    if m:
        meta["doi"] = m.group(1).strip()
    else:
        m = DOI_RE.search(html)
        if m:
            meta["doi"] = m.group(0).rstrip(".,;)\"'")

    # PDF galley URL — citation_pdf_url meta first, then any /galley/.../view link.
    m = re.search(r'<meta[^>]+name="citation_pdf_url"[^>]+content="([^"]+)"', html, re.I)
    if m:
        meta["pdf_url"] = m.group(1).strip()
    else:
        m = GALLEY_RE.search(html)
        if m:
            meta["pdf_url"] = urljoin(article_url, m.group(1))

    return meta


def load_existing_inventory() -> dict:
    if INVENTORY_PATH.exists():
        return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    return {"generated_at": None, "total_articles": 0, "articles": []}


def save_inventory(inventory: dict) -> None:
    INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    inventory["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    inventory["total_articles"] = len(inventory["articles"])
    INVENTORY_PATH.write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--issue", type=int, help="Process a single issue by ID")
    g.add_argument("--all", action="store_true", help="Process every issue in the journal")
    parser.add_argument("--resume", action="store_true",
                        help="Skip articles already in inventory.json")
    args = parser.parse_args()

    sess = session()
    inventory = load_existing_inventory() if args.resume else {
        "generated_at": None, "total_articles": 0, "articles": []
    }
    seen_ids = {a["article_id"] for a in inventory["articles"]}

    # Build the list of issue sitemaps to walk.
    if args.all:
        print(f"Fetching journal sitemap index: {SITEMAP_INDEX}")
        issue_sitemaps = list_issue_sitemaps(sess)
        print(f"  found {len(issue_sitemaps)} issue sitemaps")
    else:
        issue_sitemaps = [f"{JOURNAL_BASE}/issue/{args.issue}_sitemap.xml"]

    # Walk each issue sitemap, then each article inside it.
    for sm_url in issue_sitemaps:
        issue_id = issue_id_from_sitemap_url(sm_url)
        try:
            articles = list_articles_in_issue(sm_url, sess)
        except Exception as e:
            print(f"  ! issue {issue_id}: failed to fetch sitemap ({e})")
            continue
        print(f"\nIssue {issue_id}: {len(articles)} article(s)")
        time.sleep(REQUEST_DELAY_SECONDS)

        for article_id, article_url in articles:
            if article_id in seen_ids:
                print(f"  - skip {article_id} (already in inventory)")
                continue
            try:
                html = fetch_html(article_url, sess)
                meta = parse_article_metadata(html, article_url)
            except Exception as e:
                print(f"  ! {article_id}: failed to fetch ({e})")
                continue

            record = {
                "article_id": article_id,
                "issue_id": issue_id,
                "url": article_url,
                **meta,
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            inventory["articles"].append(record)
            seen_ids.add(article_id)
            print(f"  + {article_id}: {(meta['title'] or '?')[:60]}")
            time.sleep(REQUEST_DELAY_SECONDS)

        # Save after each issue so partial progress isn't lost.
        save_inventory(inventory)

    save_inventory(inventory)
    print(f"\nWrote {INVENTORY_PATH}")
    print(f"  total articles: {inventory['total_articles']}")
    print(f"  with DOI:       {sum(1 for a in inventory['articles'] if a.get('doi'))}")
    print(f"  with PDF URL:   {sum(1 for a in inventory['articles'] if a.get('pdf_url'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
