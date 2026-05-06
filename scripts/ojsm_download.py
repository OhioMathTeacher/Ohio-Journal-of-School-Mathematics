#!/usr/bin/env python3
"""OJSM Citation Audit — Stage 2: Download.

Reads inventory.json (produced by ojsm_inventory.py) and downloads the
PDF galley for every article that has a pdf_url.  Skips articles whose
PDF is already on disk so the script is safely re-runnable.

Output: datasets/ojsm-audit/pdfs/<article_id>.pdf

Usage:
    # Download every PDF in inventory
    python3 scripts/ojsm_download.py

    # Download only articles from a specific issue
    python3 scripts/ojsm_download.py --issue 379

    # Force re-download even if file exists
    python3 scripts/ojsm_download.py --force
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests

USER_AGENT = "OJSM-CitationAudit/0.1 (research; +contact: editor@ohiomathjournal.org)"
REQUEST_DELAY_SECONDS = 1.0  # PDFs are heavier; slower pace

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_PATH = REPO_ROOT / "datasets" / "ojsm-audit" / "inventory.json"
PDF_DIR = REPO_ROOT / "datasets" / "ojsm-audit" / "pdfs"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--issue", type=int, default=None,
                        help="Limit to articles from this issue ID")
    parser.add_argument("--force", action="store_true",
                        help="Re-download PDFs that already exist locally")
    args = parser.parse_args()

    if not INVENTORY_PATH.exists():
        print(f"ERROR: {INVENTORY_PATH} not found.")
        print("Run scripts/ojsm_inventory.py first to build the inventory.")
        return 1

    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    articles = inventory["articles"]
    if args.issue is not None:
        articles = [a for a in articles if a.get("issue_id") == args.issue]

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    sess = requests.Session()
    sess.headers.update({"User-Agent": USER_AGENT})

    downloaded = 0
    skipped_existing = 0
    skipped_no_url = 0
    failed = 0

    for art in articles:
        aid = art["article_id"]
        pdf_url = art.get("pdf_url")
        out_path = PDF_DIR / f"{aid}.pdf"

        if pdf_url is None:
            print(f"  - {aid}: no pdf_url in inventory, skipping")
            skipped_no_url += 1
            continue
        if out_path.exists() and not args.force:
            print(f"  = {aid}: already downloaded, skipping")
            skipped_existing += 1
            continue

        try:
            resp = sess.get(pdf_url, timeout=60, allow_redirects=True)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")
            if "pdf" not in content_type.lower() and not resp.content.startswith(b"%PDF"):
                print(f"  ! {aid}: response is not a PDF ({content_type}); skipping")
                failed += 1
                continue
            out_path.write_bytes(resp.content)
            size_kb = len(resp.content) / 1024
            print(f"  + {aid}: {size_kb:.0f} KB -> {out_path.name}")
            downloaded += 1
        except Exception as e:
            print(f"  ! {aid}: download failed ({e})")
            failed += 1
        time.sleep(REQUEST_DELAY_SECONDS)

    print()
    print(f"Downloaded:        {downloaded}")
    print(f"Skipped (cached):  {skipped_existing}")
    print(f"Skipped (no URL):  {skipped_no_url}")
    print(f"Failed:            {failed}")
    print(f"PDFs in {PDF_DIR}: {len(list(PDF_DIR.glob('*.pdf')))}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
