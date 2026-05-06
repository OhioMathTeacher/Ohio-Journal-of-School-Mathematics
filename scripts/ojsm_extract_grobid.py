#!/usr/bin/env python3
"""OJSM Citation Audit — Stage 3 (GROBID variant): Extract references from PDFs.

Replaces ``ojsm_extract.py``'s pdftotext + DOI regex pipeline with GROBID's
``processReferences`` endpoint.  GROBID is a layout-aware ML reference
parser; it eliminates the line-rejoin and trim-fused-author bugs that
produced extraction artifacts in the regex pipeline (e.g. the "Fagbohun"
fusion in art 6574).

Outputs (same paths and shapes as ``ojsm_extract.py`` for drop-in
compatibility with ``ojsm_validate.py`` and ``ojsm_triage_app.py``):

    datasets/ojsm-audit/refs/<article_id>.txt   one reference per blank-
                                                line-separated paragraph
    datasets/ojsm-audit/bibs/<article_id>.bib   synthetic BibTeX, one
                                                @misc per DOI-bearing ref
    datasets/ojsm-audit/extract_summary.json    per-article counts

Usage:
    python3 scripts/ojsm_extract_grobid.py
    python3 scripts/ojsm_extract_grobid.py --issue 357
    python3 scripts/ojsm_extract_grobid.py --article 6574

Requires GROBID running on localhost:8070, e.g.::

    podman run -d --rm -p 8070:8070 --name grobid \\
        docker.io/lfoppiano/grobid:0.8.1
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_PATH = REPO_ROOT / "datasets" / "ojsm-audit" / "inventory.json"
PDF_DIR = REPO_ROOT / "datasets" / "ojsm-audit" / "pdfs"
REFS_DIR = REPO_ROOT / "datasets" / "ojsm-audit" / "refs"
BIBS_DIR = REPO_ROOT / "datasets" / "ojsm-audit" / "bibs"
SUMMARY_PATH = REPO_ROOT / "datasets" / "ojsm-audit" / "extract_summary.json"

GROBID_URL = "http://localhost:8070"
TEI_NS = "http://www.tei-c.org/ns/1.0"
NS = {"t": TEI_NS}

# Boundary patterns where a fused next-reference author (or duplicated-
# reference title, e.g. art 4087's "...883LanguageLearners") is starting.
# Ported from ``ojsm_extract.py`` so GROBID DOIs get the same cleanup.
#   a) digit/lowercase followed by Capital+lowercase   ("...0119Feeding")
#   b) period followed by Capital+lowercase            (".Knapp", ".Harrison")
# arXiv DOIs (10.48550/arXiv.YYMM.NNNNN) are preserved by the explicit
# 'Xiv' exception in trim_fused_author.
BOUNDARY_RE = re.compile(r'(?<=[a-z0-9])[A-Z][a-z]|(?<=\.)[A-Z][a-z]')

# Permissive DOI regex used to recover DOIs from raw_reference text when
# GROBID's structured <idno> field has been truncated (e.g. Wiley legacy
# DOIs ending in ".x" — GROBID drops the ".x" in <idno> but the raw text
# still has it).  Same shape as ojsm_extract.py.
DOI_RE = re.compile(r"10\.\d{4,9}/\S+", re.IGNORECASE)


def find_doi_in_raw(raw_text: str) -> str | None:
    """Find the first DOI in raw reference text and normalize it.

    Used when GROBID's <idno> field disagrees with the source PDF text —
    typically because GROBID has truncated a legacy ".x" suffix or similar.
    """
    if not raw_text:
        return None
    m = DOI_RE.search(raw_text)
    if not m:
        return None
    return normalize_doi(m.group(0)) or None


def clean_doi_tail(doi: str) -> str:
    """Strip sentence-ending punctuation from a DOI string.

    Always strips trailing .,;"'> characters.  Strips a trailing ')' only if
    it's unbalanced (preserves old Elsevier DOIs like
    ``10.1016/S0732-3123(01)00109-9`` that legitimately contain parens).
    """
    while doi and doi[-1] in '.,;"\'>':
        doi = doi[:-1]
    if doi.endswith(')') and doi.count('(') < doi.count(')'):
        doi = doi[:-1]
    return doi


def trim_fused_author(raw: str) -> str:
    """Cut the captured DOI at the first sign of a fused next-reference author."""
    pos = 0
    while True:
        m = BOUNDARY_RE.search(raw, pos)
        if not m:
            return raw
        # arXiv exception: '10.48550/arXiv.YYMM.NNNNN' — the 'Xiv' would
        # otherwise trigger at the lowercase-then-Capital boundary.
        if raw[m.start():m.start() + 3] == 'Xiv':
            pos = m.end()
            continue
        return raw[:m.start()]


def normalize_doi(raw: str) -> str:
    """Apply trim_fused_author then clean_doi_tail. Returns '' if empty."""
    return clean_doi_tail(trim_fused_author(raw.strip()))


def grobid_alive() -> bool:
    try:
        r = requests.get(f"{GROBID_URL}/api/isalive", timeout=3)
        return r.ok and r.text.strip().lower() == "true"
    except requests.RequestException:
        return False


def process_references(pdf_path: Path, timeout: int = 180) -> str:
    """POST a PDF to /api/processReferences and return TEI XML."""
    with pdf_path.open("rb") as f:
        files = {"input": (pdf_path.name, f, "application/pdf")}
        data = {
            "consolidateCitations": "0",  # don't enrich via CrossRef — we
                                          # want what the PDF actually says
            "includeRawCitations": "1",   # raw citation strings for refs.txt
        }
        r = requests.post(
            f"{GROBID_URL}/api/processReferences",
            files=files, data=data, timeout=timeout,
        )
    r.raise_for_status()
    return r.text


def _text(elem) -> str:
    """All text content of an element, joined and stripped."""
    if elem is None:
        return ""
    return " ".join("".join(elem.itertext()).split())


def _author_string(analytic_or_monogr) -> str:
    """Render authors as 'Surname, F. M., & Surname2, G.' from a TEI <analytic> or <monogr>."""
    parts = []
    for author in analytic_or_monogr.findall("t:author", NS):
        pers = author.find("t:persName", NS)
        if pers is None:
            # Could be <author>OrgName</author> — fall back to text.
            txt = _text(author)
            if txt:
                parts.append(txt)
            continue
        surname = _text(pers.find("t:surname", NS))
        forenames = [_text(f) for f in pers.findall("t:forename", NS) if _text(f)]
        initials = " ".join(
            (n if len(n) <= 2 else n[0]) + ("" if (len(n) <= 2 and n.endswith(".")) else ".")
            for n in forenames
        ).strip()
        if surname and initials:
            parts.append(f"{surname}, {initials}")
        elif surname:
            parts.append(surname)
        elif initials:
            parts.append(initials)
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + ", & " + parts[-1]


def render_reference(bibl: ET.Element) -> tuple[str, str | None]:
    """Render one <biblStruct> as (apa_text, doi_or_none).

    The text is APA-ish — good enough for a human reading the triage
    paragraph window — not a faithful APA renderer.  GROBID's raw cited
    string from <note type="raw_reference"> is preferred when present.
    """
    # Prefer raw citation if available — closest to what the PDF actually showed.
    raw_note = None
    for note in bibl.findall("t:note", NS):
        if note.attrib.get("type") in ("raw_reference", "raw"):
            raw_note = _text(note)
            break

    # DOI: GROBID's structured <idno> is the primary source — it's the
    # cleanest, post-parse DOI. The raw_reference text is reference-quality
    # (line-wraps preserved as spaces) so a regex over it can break inside
    # multi-segment DOIs. We use raw only as an *extension*: if it contains
    # a DOI that strictly extends the <idno> value, we prefer the longer
    # form (this recovers Wiley legacy '.x' suffixes that <idno> truncates).
    doi = None
    for idno in bibl.iter(f"{{{TEI_NS}}}idno"):
        if idno.attrib.get("type", "").upper() == "DOI" and _text(idno):
            doi = normalize_doi(_text(idno)) or None
            break

    if doi and raw_note:
        raw_doi = find_doi_in_raw(raw_note)
        if (raw_doi
                and raw_doi.lower().startswith(doi.lower())
                and len(raw_doi) > len(doi)):
            doi = raw_doi

    if not doi and raw_note:
        # No <idno> at all — fall back to raw_reference scan.
        doi = find_doi_in_raw(raw_note)

    if raw_note:
        return raw_note, doi

    # Fallback: synthesize from structured fields.
    analytic = bibl.find("t:analytic", NS)
    monogr = bibl.find("t:monogr", NS)

    authors = ""
    if analytic is not None:
        authors = _author_string(analytic)
    if not authors and monogr is not None:
        authors = _author_string(monogr)

    year = ""
    if monogr is not None:
        date = monogr.find(".//t:date[@when]", NS)
        if date is not None and date.attrib.get("when"):
            year = date.attrib["when"][:4]

    title_a = _text(analytic.find("t:title", NS)) if analytic is not None else ""
    title_m = _text(monogr.find("t:title[@level='j']", NS)) if monogr is not None else ""
    if not title_m and monogr is not None:
        title_m = _text(monogr.find("t:title", NS))

    pieces = []
    if authors:
        pieces.append(authors)
    if year:
        pieces.append(f"({year}).")
    elif authors:
        pieces[-1] += "."
    if title_a:
        pieces.append(title_a + ".")
    if title_m:
        pieces.append(f"*{title_m}*.")
    if doi:
        pieces.append(f"https://doi.org/{doi}")

    return " ".join(pieces).strip(), doi


def parse_tei(tei_xml: str) -> list[tuple[str, str | None]]:
    """Return [(rendered_text, doi_or_none), ...] for every biblStruct."""
    root = ET.fromstring(tei_xml)
    out = []
    for bibl in root.iter(f"{{{TEI_NS}}}biblStruct"):
        text, doi = render_reference(bibl)
        if text:
            out.append((text, doi))
    return out


def build_synthetic_bib(article_id: int, dois: list[str]) -> str:
    if not dois:
        return f"% Article {article_id}: 0 DOIs extracted (GROBID)\n"
    today = datetime.now(timezone.utc).date()
    entries = [f"% Article {article_id}: {len(dois)} DOIs extracted on {today} (GROBID)\n"]
    for i, doi in enumerate(dois, 1):
        key = f"a{article_id}_ref{i:03d}"
        entries.append(f"@misc{{{key},\n  doi = {{{doi}}}\n}}\n")
    return "\n".join(entries)


def build_refs_text(refs: list[tuple[str, str | None]]) -> str:
    """One reference per blank-line-separated paragraph, for the triage app."""
    return "\n\n".join(text for text, _ in refs) + ("\n" if refs else "")


def process_article(aid: int) -> dict | None:
    pdf_path = PDF_DIR / f"{aid}.pdf"
    if not pdf_path.exists():
        print(f"  - {aid}: no PDF on disk, skipping")
        return None

    try:
        tei = process_references(pdf_path)
    except requests.RequestException as e:
        print(f"  ! {aid}: GROBID request failed ({e})")
        return None
    except Exception as e:
        print(f"  ! {aid}: unexpected error ({e})")
        return None

    if not tei.strip():
        # GROBID returns HTTP 204 when it found no extractable references
        # (typically very short articles, posters, or scanned PDFs without a
        # text layer).  Not an error — just no signal.
        refs = []
    else:
        try:
            refs = parse_tei(tei)
        except ET.ParseError as e:
            print(f"  ! {aid}: TEI parse failed ({e})")
            return None

    dois: list[str] = []
    seen: set[str] = set()
    for _, doi in refs:
        if doi and doi.lower() not in seen:
            seen.add(doi.lower())
            dois.append(doi)

    (REFS_DIR / f"{aid}.txt").write_text(build_refs_text(refs), encoding="utf-8")
    (BIBS_DIR / f"{aid}.bib").write_text(
        build_synthetic_bib(aid, dois), encoding="utf-8"
    )

    marker = "+" if dois else ("~" if refs else "-")
    print(f"  {marker} {aid}: {len(refs)} refs, {len(dois)} DOIs")
    return {
        "article_id": aid,
        "references_found": bool(refs),
        "estimated_ref_count": len(refs),
        "doi_count": len(dois),
        "doi_coverage": (len(dois) / len(refs)) if refs else 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--issue", type=int, default=None,
                        help="Limit to articles from this issue ID")
    parser.add_argument("--article", type=int, default=None,
                        help="Process a single article by ID (for testing)")
    args = parser.parse_args()

    if not grobid_alive():
        print(f"ERROR: GROBID not responding at {GROBID_URL}/api/isalive")
        print("Start it with:")
        print("  podman run -d --rm -p 8070:8070 --name grobid "
              "docker.io/lfoppiano/grobid:0.8.1")
        return 1

    if not INVENTORY_PATH.exists():
        print(f"ERROR: {INVENTORY_PATH} not found. Run ojsm_inventory.py first.")
        return 1

    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    articles = inventory["articles"]
    if args.article is not None:
        articles = [a for a in articles if a.get("article_id") == args.article]
    elif args.issue is not None:
        articles = [a for a in articles if a.get("issue_id") == args.issue]

    REFS_DIR.mkdir(parents=True, exist_ok=True)
    BIBS_DIR.mkdir(parents=True, exist_ok=True)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "extractor": "grobid-0.8.1",
        "articles": [],
    }
    for art in articles:
        rec = process_article(art["article_id"])
        if rec is None:
            continue
        rec["issue_id"] = art.get("issue_id")
        rec["title"] = art.get("title")
        summary["articles"].append(rec)

    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    n = len(summary["articles"])
    n_with_refs = sum(1 for a in summary["articles"] if a["references_found"])
    total_refs = sum(a["estimated_ref_count"] for a in summary["articles"])
    total_dois = sum(a["doi_count"] for a in summary["articles"])
    print(f"\nProcessed:           {n} article(s)")
    if n:
        print(f"References found:    {n_with_refs} ({n_with_refs / n * 100:.0f}%)")
    print(f"Total references:    {total_refs}")
    print(f"DOIs extracted:      {total_dois}")
    if total_refs:
        print(f"Avg DOI coverage:    {total_dois / total_refs * 100:.0f}%")
    print(f"\nWrote {SUMMARY_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
