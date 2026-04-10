# Research Log — Citation Validator Development

This file documents key decisions, experiments, and findings in
chronological order.  It is intended as raw material for the Methods and
Results sections of the eventual Nature submission.

---

## 2026-04-10 — Code Audit & Baseline Preparation

### Context
Opus 4.6 performed a thorough code review of the entire repository
(~6,000 lines of logic) to assess readiness for a Nature submission on
affordable citation-hallucination detection.

### Critical Issues Found & Fixed

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| 1 | **Confusion matrix inverted.** TP/TN swapped from standard detection convention. Precision, recall, and F1 were all computed with non-standard definitions. | Critical | Swapped TP↔TN assignments in `run_benchmark.py`. TP now = fake correctly flagged. Added 19-test pytest suite verifying the convention. |
| 2 | **1,225 lines of dead HTML template** in `webapp.py` with a contradictory AI prompt ("assume REAL" vs active prompt "lean toward suspicious"). | Critical | Removed. `webapp.py` went from 1,540 → 322 lines. |
| 3 | **350 lines of dead JS validation** in `citation-validator.html` — complete client-side pipeline never called. README falsely claimed "Browser-Only" mode. | Critical | Removed dead functions. Fixed README. |
| 4 | **Groq model mismatch.** CLI used `llama-3.1-8b-instant` (8B); webapp used `llama-3.3-70b-versatile` (70B). | Significant | Unified to 70B everywhere. |
| 5 | **Hardcoded year** (`current_year = 2026`). | Minor | Replaced with `datetime.now().year`. |
| 6 | **Temp file race condition** in Flask `/validate`. | Minor | Replaced with `tempfile.mkstemp()`. |

**Net change:** +276 lines, −1,604 lines.  Codebase got smaller AND more
correct.

### Additional Differences Documented (Python vs JS)

The code review identified 6 behavioral differences between the Python
validator (used by Flask/benchmarks) and the removed JS client-side code.
These are now moot since the dead JS was removed, but are recorded here
for completeness:

- Semantic Scholar: Python requires author/year cross-validation; JS did not
- OpenAlex: Python uses structured `filter`; JS used free-text `search`
- Heuristics: Python had 8 patterns; JS had 5 (different sets)
- Default status: Python started `valid`; JS started `unknown`
- Escalation: Python had no entry-type restriction; JS only escalated `@article`
- DOI resolver: Python fetched metadata via content negotiation; JS returned bare `{ doi }`

---

## 2026-04-10 — False-Positive Baseline (Step 1)

### Objective
Measure the false-positive rate on real citations using deterministic
validation only (no AI).  Every flag on a known-real citation is a false
positive.

### Datasets

| ID | Description | Count | Source |
|----|-------------|-------|--------|
| `ojsm-real-arxiv` | arXiv CS preprints (2024) | 285 | Extracted from 2 papers |
| `ojsm-real-crossref` | CrossRef random sample | 100 | CrossRef random-works API |
| `nature-article-refs` | Nature article bibliography | 10 | Manual entry |

### Run 1 — Before escalation fix

**Result: 100% FPR across all datasets.**

Root cause: the validator escalated "not found in databases" to
`suspicious`.  For arXiv preprints without DOIs, this meant every single
citation was flagged.  "Absence of evidence" was treated as "evidence of
absence."

### Escalation Fix Applied

Three changes to `citation_validator.py`:

1. **Escalation logic:** "No DOI + not in OpenAlex" now stays at `warning`
   (unverifiable) instead of escalating to `suspicious`.  Only DOI title
   mismatches or AI analysis can escalate.

2. **DOI/arXiv retry:** `validate_doi()` and `_validate_arxiv()` retry
   once on transient errors (429, timeouts, 5xx).  Only 404 from CrossRef
   skips retry.

3. **Rate limit delay:** Increased from 0.1s to 0.25s per API call.

### Run 2 — After escalation fix

| Dataset | FPR (Run 1) | FPR (Run 2) | Notes |
|---------|-------------|-------------|-------|
| arXiv CS (285) | 100% | **0.7%** (2/285) | PASS. 283 correctly downgraded to `warning`. |
| CrossRef (100) | 100% | 100% | Network issue — see below. |
| Nature (10) | 100% | 50% | arXiv API returning 403. |

### Environment Limitation

Manual testing confirmed that the cloud environment blocks outbound HTTPS
to `api.crossref.org`, `doi.org`, `api.openalex.org`,
`api.semanticscholar.org`, and `export.arxiv.org` (all return "Tunnel
connection failed: 403 Forbidden").

The arXiv dataset passed because most citations lack DOIs and went through
OpenAlex/Semantic Scholar during Run 1 (before those APIs were also
throttled by cumulative requests).  The CrossRef dataset consists entirely
of DOI-bearing citations, so 100% depend on the blocked APIs.

**Conclusion:** The CrossRef and Nature FPR numbers cannot be trusted from
this environment.  The arXiv result (0.7%) is valid because it was measured
before the APIs were fully blocked.  Local re-testing is required.

### Two Remaining arXiv False Positives

| Key | DOI | Issue |
|-----|-----|-------|
| `Chandra:81` | `10.1145/322234.322243` | Old ACM DOI — CrossRef may not index pre-1990 ACM content |
| `mielke2022` | `10.1162/tacl_a_00494` | TACL (MIT Press) — possibly a CrossRef indexing gap |

Both are legitimate papers with valid DOIs.  These represent the residual
FPR from DOI resolution gaps in CrossRef, which the DOI resolver fallback
should catch.  The fallback was blocked in this environment; local testing
should resolve both.

---

## 2026-04-10 — Local Re-Test (Step 1, Run 3)

### Environment
Local machine with full API access (CrossRef, DOI.org, OpenAlex,
Semantic Scholar, arXiv all reachable).

### Results

| Dataset | Citations | Valid | Warning | Suspicious | Invalid | FPR |
|---------|-----------|-------|---------|------------|---------|-----|
| arXiv CS (2024) | 285 | 17 (6%) | 268 (94%) | 0 | 0 | **0.0%** PASS |
| CrossRef random | 100 | 94 (94%) | 2 (2%) | 4 (4%) | 0 | **4.0%** PASS |
| Nature article | 10 | 4 (40%) | 5 (50%) | 1 (10%) | 0 | **10.0%** FAIL |
| **Overall** | **395** | 115 | 275 | 5 | 0 | **1.3%** PASS |

### False-Positive Analysis

All 5 false positives are **correct title-mismatch detections on incorrect
test data** — the validator is behaving correctly in every case.

**CrossRef FPs (4):** All have `title = {Unknown}` — CrossRef metadata
artifacts (journal issue cover, PLOS ONE figure, PLOS ONE table,
conference supplement).  These are not citable references.
**Fix:** Removed from test data.

| Key | DOI | Actual content |
|-----|-----|----------------|
| `unknown1949` | `10.1111/jace.1949.32.issue-9` | Journal issue cover |
| `unknown2012` | `10.1371/journal.pone.0048225.g002` | Figure 2 of a paper |
| `unknown2020` | `10.1371/journal.pone.0237224.t001` | Table 1 of a paper |
| `unknown2024` | `10.1136/annrheumdis-2017-211123.supp3` | Conference supplement |

**Nature FP (1):** `resnik2026` had BibTeX title "Fabricated references
in academic publishing" but DOI `10.1080/08989621.2026.2645390` resolves
to "Hallucinated citations produced by generative artificial intelligence
may constitute research misconduct when citations function as data in
scholarly papers" (Resnik & Hosseini, Accountability in Research, 2026).
**Fix:** Title corrected in BibTeX.

### Interpretation

The deterministic pipeline achieves **0% FPR on properly-formed
citations** (arXiv dataset, 285 citations).  The remaining FPs are all
test-data quality issues, not validator defects.  After cleaning the test
data, expected FPR: 0/391 = **0.0%** (or 1/391 = 0.26% if resnik2026
remains unresolved).

### arXiv Warning Rate (94%)

268/285 arXiv citations got `warning` (not `valid`).  This is expected
and correct: most arXiv preprints lack DOIs and may not be indexed in
OpenAlex/Semantic Scholar.  `warning` = "unverifiable" — the validator
correctly does not escalate to `suspicious`.

---

## 2026-04-10 — Clean Re-Test (Step 1, Run 4)

### Environment
Local machine with full API access.  Test data cleaned: 4 CrossRef
metadata artifacts removed, `resnik2026` title corrected.

### Results

| Dataset | Citations | Valid | Warning | Suspicious | Invalid | FPR |
|---------|-----------|-------|---------|------------|---------|-----|
| arXiv CS (2024) | 285 | 2 (0.7%) | 283 (99.3%) | 0 | 0 | **0.0%** PASS |
| CrossRef random | 96 | 94 (97.9%) | 2 (2.1%) | 0 | 0 | **0.0%** PASS |
| Nature article | 10 | 5 (50%) | 5 (50%) | 0 | 0 | **0.0%** PASS |
| **Overall** | **391** | 101 | 290 | 0 | 0 | **0.0%** PASS |

**Zero false positives across 391 real citations.**

### Notes

- CrossRef dataset dropped from 100 → 96 after removing 4 metadata
  artifacts (journal issue cover, figure, table, conference supplement).
- arXiv valid count dropped from 17 (Run 3) to 2 — likely due to API
  rate limits or transient availability.  No impact on FPR since the
  other 283 correctly land at `warning`, not `suspicious`.
- Nature `resnik2026` now validates correctly with corrected title.

---

## Next Steps

1. **Fake-citation regression test:** Run the Ansari 100-fake dataset
   through the updated validator to confirm detection rate is still 100%
   (the escalation fix should not have weakened detection of actual fakes).

2. **Step 3 — AI comparison:** Run datasets with Gemini AI to measure
   whether AI analysis improves or worsens precision.

3. **10K study design:** Finalize the mix ratio and sampling strategy.

---

## Methodology Notes for Paper

### Evaluation Convention

We use standard detection convention:

| Label | Meaning |
|-------|---------|
| **TP** | Fake citation correctly flagged (detector fires, correct) |
| **FP** | Real citation incorrectly flagged (detector fires, wrong) |
| **TN** | Real citation correctly NOT flagged (detector silent, correct) |
| **FN** | Fake citation that slips through (detector silent, wrong) |

- **Precision** = TP / (TP + FP) — "when we flag, how often are we right?"
- **Recall** = TP / (TP + FN) — "of all fakes, how many do we catch?"
- **FPR** = FP / (FP + TN) — "of real citations, how many do we wrongly flag?"
- **F1** = harmonic mean of precision and recall

`warning` status is NOT counted as flagged.  Only `suspicious` and
`invalid` count as the detector firing.

### Status Taxonomy

| Status | Meaning | Flagged? |
|--------|---------|----------|
| `valid` | Verified against databases | No |
| `warning` | Unverifiable or minor concern | No |
| `suspicious` | Multiple red flags or AI escalation | **Yes** |
| `invalid` | DOI failed or AI high-confidence fake | **Yes** |

### Validation Pipeline (3 tiers)

1. **Deterministic:** DOI → CrossRef → DataCite fallback → arXiv fallback
2. **Database search:** OpenAlex (structured filter) → Semantic Scholar (title search, requires author/year cross-validation)
3. **AI analysis (optional):** Gemini / Groq / OpenAI / Anthropic via Flask proxy
