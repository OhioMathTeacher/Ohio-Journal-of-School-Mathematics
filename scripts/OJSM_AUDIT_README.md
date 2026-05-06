# OJSM Citation Audit Pipeline

Four composable scripts that walk the Ohio Journal of School
Mathematics' Janeway site, download every article PDF, extract DOIs
from each article's reference list, and validate them against
CrossRef.  Produces the empirical foundation for the citation-hygiene
audit paper (Paper 2).

## Stages

| # | Script | Input | Output |
|---|--------|-------|--------|
| 1 | `ojsm_inventory.py` | Janeway sitemap | `datasets/ojsm-audit/inventory.json` |
| 2 | `ojsm_download.py`  | inventory.json  | `datasets/ojsm-audit/pdfs/<id>.pdf` |
| 3 | `ojsm_extract.py`   | PDFs            | `datasets/ojsm-audit/refs/<id>.txt`, `bibs/<id>.bib` |
| 4 | `ojsm_validate.py`  | .bib files      | `datasets/ojsm-audit/validation/<id>.json`, `validation_summary.json` |

## Prerequisites

```bash
# Python deps (already in scripts/requirements.txt)
pip install -r scripts/requirements.txt

# pdftotext (poppler-utils)
sudo dnf install poppler-utils      # Fedora
sudo apt install poppler-utils      # Ubuntu/Debian
```

## Usage — start with one issue, then go wide

**Test the whole pipeline on one recent issue first.**  Pick any issue
ID from the journal sitemap — the most recent at the time of writing
is 379.

```bash
python3 scripts/ojsm_inventory.py --issue 379
python3 scripts/ojsm_download.py  --issue 379
python3 scripts/ojsm_extract.py   --issue 379
python3 scripts/ojsm_validate.py  --issue 379
```

Inspect outputs at each stage.  Look at one or two of the extracted
`.bib` files to confirm DOIs were found correctly.  Look at
`validation_summary.json` for the aggregate.

**When that's working, run the full corpus.**  Stages 1 and 2 are the
slow ones (network).  Run them overnight if necessary.

```bash
python3 scripts/ojsm_inventory.py --all
python3 scripts/ojsm_download.py
python3 scripts/ojsm_extract.py
python3 scripts/ojsm_validate.py
```

All four scripts are **idempotent** — re-running skips already-completed
work.  If the inventory script is interrupted, add `--resume` to pick
up where it left off.

## What to look for in the results

Open `datasets/ojsm-audit/validation_summary.json` after Stage 4.

- **`totals.invalid`** counts DOIs that didn't resolve in CrossRef.
  These are Frankenstein candidates (real-paper, fabricated-DOI) like
  the Söderström example in the manuscript.

- **`frankenstein_candidates`** lists each one with article ID, title,
  and the fabricated DOI.  Manually verify a sample by searching for
  the actual paper — confirm whether the cited paper exists at all
  (then it's a Frankenstein) or whether there's no such paper (pure
  hallucination).

- **`totals.valid` / `total`** is the clean-citation rate among
  DOI-bearing references — the baseline for the editorial-policy story.

## Limitations and caveats

- **DOI coverage only.**  References without DOIs (books, theses,
  state-DOE documents, NCTM publications) are extracted as text into
  `refs/<id>.txt` but not validated.  Stage 5 (clibib title-search
  for non-DOI references) is not yet built.

- **Heuristic reference-section detection.**  We look for "References",
  "Works Cited", or "Bibliography" headings.  Articles that label
  their references differently — or use no heading — will yield
  empty `refs/<id>.txt` files.  Inspect the empties manually.

- **PDF parsing is fragile.**  Two-column layouts and footnotes can
  trip up `pdftotext -layout`.  Spot-check a sample of extracted
  reference text against the source PDFs.

- **No rate-limit retry.**  If CrossRef returns 429, the validator
  records the error but doesn't back off.  For the full corpus run,
  watch for transient errors in `validation/*.json` and re-run the
  affected articles.

## Future improvements

- **Switch reference extraction to Anystyle.**  The current
  `ojsm_extract.py` uses regex heuristics to find DOIs in
  references text — fast and dependency-free, but limited to
  citations that already include a DOI.  [Anystyle](https://anystyle.io/)
  is a Ruby gem trained on real reference data; it parses a
  single reference string into structured fields (author, year,
  title, journal, DOI).  Plugging it in at Stage 3 would let us
  validate references that lack DOIs but match a CrossRef record
  by title+author+year, expanding coverage from the current
  ~15% DOI density to a much larger fraction.  Heavier alternative:
  [GROBID](https://github.com/kermitt2/grobid) — ML-based,
  takes raw PDF in and returns structured XML; overkill for our
  pipeline (we already have pdftotext output) but the industry
  standard for full-PDF bibliometric work.
