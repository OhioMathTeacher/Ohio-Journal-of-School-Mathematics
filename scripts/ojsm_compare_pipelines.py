#!/usr/bin/env python3
"""Compare the regex-pipeline and GROBID-pipeline validation summaries.

Reads:
    datasets/ojsm-audit/validation_summary.regex.json   (snapshot)
    datasets/ojsm-audit/validation_summary.json         (current = GROBID)

Prints a side-by-side breakdown:
- Total candidate counts.
- Per-article candidate count deltas.
- DOIs that *vanished* from the candidate list (likely artifacts the
  regex pipeline produced).
- DOIs that *appeared* in the candidate list (real Frankensteins or
  hallucinations the regex pipeline missed because it never saw the DOI).
- DOIs that *stayed* (the same suspect DOI appears in both — these are
  the strongest Frankenstein signals).
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGEX_PATH = REPO_ROOT / "datasets" / "ojsm-audit" / "validation_summary.regex.json"
GROBID_PATH = REPO_ROOT / "datasets" / "ojsm-audit" / "validation_summary.json"


def load_candidates(path: Path) -> set[tuple[int, str]]:
    """Return {(article_id, doi)} for every candidate in the summary."""
    if not path.exists():
        raise SystemExit(f"missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        (c["article_id"], c["fabricated_doi"])
        for c in data.get("frankenstein_candidates", [])
    }


def main() -> int:
    regex = load_candidates(REGEX_PATH)
    grobid = load_candidates(GROBID_PATH)

    vanished = sorted(regex - grobid)
    appeared = sorted(grobid - regex)
    stayed = sorted(regex & grobid)

    print(f"regex pipeline candidates : {len(regex):4d}")
    print(f"GROBID pipeline candidates: {len(grobid):4d}")
    print(f"  stayed  (in both)       : {len(stayed):4d}  <-- strongest Frankenstein signal")
    print(f"  vanished (regex only)   : {len(vanished):4d}  <-- likely extraction artifacts")
    print(f"  appeared (GROBID only)  : {len(appeared):4d}  <-- new candidates GROBID surfaced")

    if stayed:
        print("\n=== STAYED (real candidates) ===")
        for aid, doi in stayed:
            print(f"  art {aid}: {doi}")
    if vanished:
        print("\n=== VANISHED (regex artifacts cleared) ===")
        for aid, doi in vanished:
            print(f"  art {aid}: {doi}")
    if appeared:
        print("\n=== APPEARED (newly surfaced candidates) ===")
        for aid, doi in appeared:
            print(f"  art {aid}: {doi}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
