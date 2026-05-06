#!/usr/bin/env python3
"""OJSM Citation Audit — Stage 4: Validate extracted DOIs.

Runs every per-article BibTeX file (built by ojsm_extract.py) through
the existing CitationValidator and aggregates results.

Outputs:
    datasets/ojsm-audit/validation/<article_id>.json   per-article results
    datasets/ojsm-audit/validation_summary.json        aggregate report

Usage:
    python3 scripts/ojsm_validate.py                   # all articles with .bib files
    python3 scripts/ojsm_validate.py --issue 379       # one issue only

Note: deterministic mode by default (no AI keys needed).  Pass --use-ai
if you want Tier-3 AI analysis on warning citations.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from citation_validator import CitationValidator  # noqa: E402

INVENTORY_PATH = REPO_ROOT / "datasets" / "ojsm-audit" / "inventory.json"
BIBS_DIR = REPO_ROOT / "datasets" / "ojsm-audit" / "bibs"
VALIDATION_DIR = REPO_ROOT / "datasets" / "ojsm-audit" / "validation"
SUMMARY_PATH = REPO_ROOT / "datasets" / "ojsm-audit" / "validation_summary.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--issue", type=int, default=None,
                        help="Limit to articles from this issue ID")
    parser.add_argument("--use-ai", action="store_true",
                        help="Enable Tier-3 AI analysis (requires GROQ_API_KEY env var)")
    args = parser.parse_args()

    if not INVENTORY_PATH.exists():
        print(f"ERROR: {INVENTORY_PATH} not found. Run ojsm_inventory.py first.")
        return 1

    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    articles = inventory["articles"]
    if args.issue is not None:
        articles = [a for a in articles if a.get("issue_id") == args.issue]

    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    validator = CitationValidator(verbose=False, use_ai=args.use_ai)

    aggregate = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ai_enabled": args.use_ai,
        "totals": {"valid": 0, "warnings": 0, "suspicious": 0, "invalid": 0, "total": 0},
        "frankenstein_candidates": [],   # invalid DOIs are likely Frankensteins
        "articles": [],
    }

    for art in articles:
        aid = art["article_id"]
        bib_path = BIBS_DIR / f"{aid}.bib"
        if not bib_path.exists():
            print(f"  - {aid}: no .bib on disk, skipping (run ojsm_extract.py)")
            continue
        if bib_path.stat().st_size < 50:  # comment-only file = no DOIs extracted
            print(f"  = {aid}: 0 DOIs extracted, skipping")
            continue

        try:
            results = validator.validate_file(bib_path)
        except Exception as e:
            print(f"  ! {aid}: validation failed ({e})")
            continue

        # Save per-article results.
        out_path = VALIDATION_DIR / f"{aid}.json"
        out_path.write_text(
            json.dumps(results, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        # Update aggregate.
        for k in ("valid", "warnings", "suspicious", "invalid", "total"):
            aggregate["totals"][k] += results.get(k, 0)

        # Frankenstein candidates: invalid DOIs in the source.
        for detail in results.get("details", []):
            if detail.get("status") == "invalid":
                aggregate["frankenstein_candidates"].append({
                    "article_id": aid,
                    "article_title": art.get("title"),
                    "issue_id": art.get("issue_id"),
                    "fabricated_doi": detail.get("fields", {}).get("doi"),
                    "issues": detail.get("issues", []),
                })

        aggregate["articles"].append({
            "article_id": aid,
            "issue_id": art.get("issue_id"),
            "title": art.get("title"),
            "valid": results.get("valid", 0),
            "warnings": results.get("warnings", 0),
            "suspicious": results.get("suspicious", 0),
            "invalid": results.get("invalid", 0),
            "total": results.get("total", 0),
        })

        marker = "!" if results.get("invalid", 0) else ("~" if results.get("suspicious", 0) else "+")
        print(f"  {marker} {aid}: {results.get('valid', 0)}v {results.get('warnings', 0)}w "
              f"{results.get('suspicious', 0)}s {results.get('invalid', 0)}x  "
              f"({(art.get('title') or '?')[:50]})")

    SUMMARY_PATH.write_text(
        json.dumps(aggregate, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    t = aggregate["totals"]
    print(f"\n=== Aggregate (n={t['total']} citations across {len(aggregate['articles'])} articles) ===")
    if t["total"]:
        print(f"  valid:       {t['valid']:5d}  ({t['valid']/t['total']*100:.1f}%)")
        print(f"  warnings:    {t['warnings']:5d}  ({t['warnings']/t['total']*100:.1f}%)")
        print(f"  suspicious:  {t['suspicious']:5d}  ({t['suspicious']/t['total']*100:.1f}%)")
        print(f"  invalid:     {t['invalid']:5d}  ({t['invalid']/t['total']*100:.1f}%)  <-- Frankenstein candidates")
    print(f"\nFrankenstein candidates: {len(aggregate['frankenstein_candidates'])}")
    for fc in aggregate["frankenstein_candidates"][:5]:
        print(f"  - article {fc['article_id']}: {fc['fabricated_doi']}")
    if len(aggregate["frankenstein_candidates"]) > 5:
        print(f"  (+ {len(aggregate['frankenstein_candidates']) - 5} more — see {SUMMARY_PATH})")
    print(f"\nWrote {SUMMARY_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
