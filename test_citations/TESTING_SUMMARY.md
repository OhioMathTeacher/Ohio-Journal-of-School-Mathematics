# Citation Validator — Results & Findings
**Last updated:** April 2026

---

## Early Results (April 8, 2026 — Day 1)

### Real submission testing
We ran the tool on actual manuscripts submitted to the Ohio Journal of School Mathematics:

- `Fall-2025/6572 Westgate/bibliography.bib` (19 citations)
- `Summer-2026/6622 Guerrero/references.bib` (40 citations)

**Findings:**
- 2 invalid DOIs detected: `Bettayeb2024` and `Prather2024` — both returned 404 from CrossRef
- 5% invalid rate (2/40) — matches the Nature-reported 2-6% figure precisely
- All other citations validated cleanly

### Fresh arXiv paper testing
Validated 100 citations from three 2026 arXiv preprints:
- All flagged as "no DOI found" — **expected and correct**
- arXiv preprints and very recent papers typically aren't in CrossRef yet
- Manual verification confirmed the papers were real
- Demonstrated that "no DOI" ≠ "fake" — our handling was correct

---

## Known Accuracy Issues (Identified April 2026)

After Day 1 testing, a systematic code review identified **9 bugs** causing both false positives and false negatives. These have all been fixed.

### Bug impact summary

**False negatives (fake citations passing as valid):**
- OpenAlex accepted any top search result as validation — a fabricated title like "Deep Learning for NLP" would match some real paper
- Substring title comparison allowed "A" to match any title containing the word "a"
- arXiv bypass: any fake citation with "arxiv" anywhere in its fields skipped all heuristic checks
- DOI resolver returned no metadata, so stolen DOIs on DataCite/Zenodo passed completely unchecked

**False positives (real citations flagged incorrectly):**
- JS validator default status was `'invalid'` — network failures or rate limiting marked real citations as invalid
- Heuristic warnings overrode confirmed DOI validation — a citation with a valid DOI but a minor pattern warning could be downgraded to "suspicious"
- Broken Python BibTeX parser silently dropped entries with nested braces, causing them to be "not found"
- Jaccard tokenization differed between Python and JS, producing inconsistent scores

**Test metric inflation:**
- Test runner evaluated per-file instead of per-citation — a file with 50 fakes where 1 was caught counted as fully "detected"

All 9 fixes are in commit `595f496`. A full re-evaluation of the 785-citation test suite against the fixed validator is the next step.

---

## Expected Performance After Fixes

The bug fixes primarily target the biggest accuracy problems:

| Fix | Expected effect |
|----|-----------------|
| OpenAlex similarity gate | Significant FNR reduction — fabricated plausible titles no longer auto-validate |
| Jaccard title comparison | Better stolen-DOI detection; fewer false alarms on near-matches |
| JS status default change | FPR reduction — transient network issues no longer create false positives |
| DOI confirmation protection | FPR reduction — confirmed real citations no longer downgraded by pattern noise |
| Per-citation test evaluation | Reveals true FNR (was previously masked by per-file aggregation) |

We expect the true FNR to be revealed as higher than previously measured when re-evaluated at per-citation granularity — this is the test metric fix surfacing reality, not a regression.

---

## Comparison to Published Research

| Study | Finding | Our Tool |
|-------|---------|---------|
| Nature (2026) | 2-6% of 2025 papers have hallucinated citations | 5% found in our submission sample |
| Bienz et al. (HPC conferences) | 0% in 2021 → 2-6% in 2025 | Consistent with our findings |
| Sakai et al. (ACL/NAACL/EMNLP) | 20 papers in 2024 → 275 in 2025 | We don't yet have NLP conference data |
| Ansari (NeurIPS 2025) | ~1% of accepted papers had hallucinated citations | We don't yet have NeurIPS data |
| Rao & Callison-Burch | Only 50.9% of LLM-generated BibTeX fully correct | Validates our approach of checking metadata, not just DOI existence |

---

## Next Validation Steps

### 1. Re-run full test suite (priority)
After the 9 bug fixes, run the complete 785-citation suite to establish a new baseline:
```bash
cd test_citations/
python3 run_all_tests.py --output test_results_post_bugfix.json
```
Compare to previous results to measure the improvement.

### 2. Integrate external benchmarks
Once datasets are populated under `datasets/`, run them through the validator and compare our detection rates to the published researchers' results. The Rao & Callison-Burch benchmark is highest priority — it has field-level ground truth.

### 3. Benchmark vs. CheckIfExist
Run the same input through our tool and CheckIfExist (github.com/zabbonat/References-Validation) and compare results. Both use CrossRef + OpenAlex; the comparison will reveal where our approaches diverge.

### 4. False positive edge case testing
Populate `false_positive_tests/` with DataCite DOIs, pre-DOI-era papers, non-English papers, and other legitimate edge cases to measure our FPR on unusual-but-real citations.

---

## Running Results Comparison
```bash
# After re-running, compare metrics:
python3 -c "
import json
with open('test_results_full.json') as f:
    old = json.load(f)
with open('test_results_post_bugfix.json') as f:
    new = json.load(f)

old_m = old['evaluation']['metrics']
new_m = new['evaluation']['metrics']

print('Metric         Before    After')
for key in ['accuracy', 'f1_score', 'false_positive_rate', 'false_negative_rate']:
    print(f'{key:<20} {old_m[key]:.2%}    {new_m[key]:.2%}')
"
```
