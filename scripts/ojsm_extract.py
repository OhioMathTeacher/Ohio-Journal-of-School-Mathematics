#!/usr/bin/env python3
"""OJSM Citation Audit — Stage 3: Extract references from PDFs.

For each downloaded PDF, runs pdftotext to get plain text, locates the
"References" section heuristically, extracts every DOI it can find, and
writes a synthetic BibTeX file the existing citation_validator.py can
consume.

Outputs:
    datasets/ojsm-audit/refs/<article_id>.txt   (raw references text)
    datasets/ojsm-audit/bibs/<article_id>.bib   (synthetic BibTeX)
    datasets/ojsm-audit/extract_summary.json    (per-article counts)

Usage:
    # Extract from every downloaded PDF
    python3 scripts/ojsm_extract.py

    # One issue only
    python3 scripts/ojsm_extract.py --issue 379

Requires: pdftotext from poppler-utils (sudo dnf install poppler-utils on Fedora).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_PATH = REPO_ROOT / "datasets" / "ojsm-audit" / "inventory.json"
PDF_DIR = REPO_ROOT / "datasets" / "ojsm-audit" / "pdfs"
REFS_DIR = REPO_ROOT / "datasets" / "ojsm-audit" / "refs"
BIBS_DIR = REPO_ROOT / "datasets" / "ojsm-audit" / "bibs"
SUMMARY_PATH = REPO_ROOT / "datasets" / "ojsm-audit" / "extract_summary.json"

# Headings that mark the start of the references section.
REF_HEADING_RE = re.compile(
    r"^\s*(References|REFERENCES|Works Cited|WORKS CITED|Bibliography|BIBLIOGRAPHY)\s*$",
    re.MULTILINE,
)

# Headings that mark the END of the references section (start of next section).
END_HEADING_RE = re.compile(
    r"^\s*(About the Author|About the Authors|Author Bio|Appendix|Acknowledgments?)",
    re.MULTILINE | re.IGNORECASE,
)

# DOI regex (same as the validator's web-side extractor).
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s,;)\"'>\]]+", re.IGNORECASE)

# Pre-pass to rejoin DOIs split across line breaks.
DOI_LINE_REJOIN_RE = re.compile(r"(10\.\d{4,9}/\S*)\n[ \t]*(\.?\d[^\s,;)\"'>\]]*)", re.IGNORECASE)


def pdftotext(pdf_path: Path) -> str:
    """Run pdftotext on a PDF and return UTF-8 text. Uses -layout for cleaner output."""
    if not shutil.which("pdftotext"):
        raise RuntimeError("pdftotext not found. Install with: sudo dnf install poppler-utils")
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True, check=True,
    )
    return result.stdout.decode("utf-8", errors="replace")


def find_references_section(text: str) -> str:
    """Return just the references section of the PDF text, or '' if not found."""
    start_match = None
    for m in REF_HEADING_RE.finditer(text):
        start_match = m  # take the LAST occurrence — a paper may mention "References" early
    if not start_match:
        return ""
    after = text[start_match.end():]
    end_match = END_HEADING_RE.search(after)
    return after[:end_match.start()] if end_match else after


def extract_dois(text: str) -> list[str]:
    """Extract unique DOIs from a block of text, handling line-wrapped DOIs."""
    joined = DOI_LINE_REJOIN_RE.sub(r"\1\2", text)
    seen: set[str] = set()
    dois: list[str] = []
    for raw in DOI_RE.findall(joined):
        doi = raw.rstrip(".,;)\"'>]")
        if doi.lower() not in seen:
            seen.add(doi.lower())
            dois.append(doi)
    return dois


def estimate_reference_count(refs_text: str) -> int:
    """Rough count: non-empty paragraphs separated by blank lines."""
    if not refs_text.strip():
        return 0
    paragraphs = re.split(r"\n\s*\n", refs_text)
    return sum(1 for p in paragraphs if len(p.strip()) > 30)  # filter out tiny fragments


def build_synthetic_bib(article_id: int, dois: list[str]) -> str:
    """Build a BibTeX file with one @misc entry per extracted DOI."""
    if not dois:
        return f"% Article {article_id}: 0 DOIs extracted\n"
    entries = [f"% Article {article_id}: {len(dois)} DOIs extracted on {datetime.utcnow().date()}\n"]
    for i, doi in enumerate(dois, 1):
        key = f"a{article_id}_ref{i:03d}"
        entries.append(f"@misc{{{key},\n  doi = {{{doi}}}\n}}\n")
    return "\n".join(entries)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--issue", type=int, default=None,
                        help="Limit to articles from this issue ID")
    args = parser.parse_args()

    if not INVENTORY_PATH.exists():
        print(f"ERROR: {INVENTORY_PATH} not found. Run ojsm_inventory.py first.")
        return 1

    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    articles = inventory["articles"]
    if args.issue is not None:
        articles = [a for a in articles if a.get("issue_id") == args.issue]

    REFS_DIR.mkdir(parents=True, exist_ok=True)
    BIBS_DIR.mkdir(parents=True, exist_ok=True)

    summary = {"generated_at": datetime.utcnow().isoformat(timespec="seconds"), "articles": []}
    for art in articles:
        aid = art["article_id"]
        pdf_path = PDF_DIR / f"{aid}.pdf"
        if not pdf_path.exists():
            print(f"  - {aid}: no PDF on disk, skipping (run ojsm_download.py)")
            continue

        try:
            full_text = pdftotext(pdf_path)
        except Exception as e:
            print(f"  ! {aid}: pdftotext failed ({e})")
            continue

        refs_section = find_references_section(full_text)
        dois = extract_dois(refs_section) if refs_section else []
        ref_count = estimate_reference_count(refs_section)

        # Save artifacts.
        (REFS_DIR / f"{aid}.txt").write_text(refs_section, encoding="utf-8")
        (BIBS_DIR / f"{aid}.bib").write_text(
            build_synthetic_bib(aid, dois), encoding="utf-8"
        )

        record = {
            "article_id": aid,
            "issue_id": art.get("issue_id"),
            "title": art.get("title"),
            "references_found": bool(refs_section.strip()),
            "estimated_ref_count": ref_count,
            "doi_count": len(dois),
            "doi_coverage": (len(dois) / ref_count) if ref_count else 0.0,
        }
        summary["articles"].append(record)
        marker = "+" if dois else ("~" if refs_section else "-")
        print(f"  {marker} {aid}: ~{ref_count} refs, {len(dois)} DOIs")

    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    total_refs = sum(a["estimated_ref_count"] for a in summary["articles"])
    total_dois = sum(a["doi_count"] for a in summary["articles"])
    n_articles = len(summary["articles"])
    n_with_refs = sum(1 for a in summary["articles"] if a["references_found"])
    print(f"\nProcessed:           {n_articles} article(s)")
    print(f"References found:    {n_with_refs} ({n_with_refs/n_articles*100:.0f}% of processed)" if n_articles else "")
    print(f"Estimated refs:      {total_refs}")
    print(f"DOIs extracted:      {total_dois}")
    print(f"Avg DOI coverage:    {total_dois/total_refs*100:.0f}%" if total_refs else "")
    print(f"\nWrote {SUMMARY_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
