# Citation Validator - Scientific Testing Strategy
**Date:** April 8, 2026  
**Goal:** Test 10,000+ citations systematically with scientific rigor

---

## Testing Philosophy

We need to test **ALL** the ways citations can fail:
1. **True Positives** - Real citations correctly validated ✓
2. **True Negatives** - Fake citations correctly flagged ✗
3. **False Positives** - Real citations incorrectly flagged ✗ (BAD!)
4. **False Negatives** - Fake citations that slip through ✓ (BAD!)

---

## Sampling Strategy

### 1. Real Citations (Ground Truth Positives) - Target: 8,000

#### Source A: arXiv Papers (Bulk Download)
**How:** arXiv provides bulk access to source files including `.bib` files
- **CS papers (2024-2026):** 1,000 citations
- **Physics papers (2020-2023):** 1,000 citations  
- **Biology/q-bio (2022-2025):** 1,000 citations
- **Math papers (2015-2020):** 500 citations

**Why arXiv?**
- Free bulk access via AWS S3: `s3://arxiv/`
- Contains original `.bib` files from authors
- Mix of old and new citations
- Real-world messy data (typos, incomplete metadata)

#### Source B: Semantic Scholar Open Corpus
**How:** Download citation graphs via Semantic Scholar API
- **Top-cited CS papers (2010-2020):** 1,000 citations
- **Cross-disciplinary papers:** 500 citations

#### Source C: Papers with Code
**How:** API access to ML papers + their citations
- **Machine learning papers (2017-2024):** 1,000 citations

#### Source D: CrossRef Random Sample
**How:** CrossRef REST API supports random sampling
- **Random journal articles (all fields):** 2,000 citations
- Ensures we test papers we've never seen before

### 2. False Positive Tests (Real but Problematic) - Target: 1,000

These are REAL citations that might be incorrectly flagged:

**Category A: Non-CrossRef DOIs (200)**
- Zenodo (DataCite): 50
- Figshare (DataCite): 50
- OSF Preprints: 25
- Dryad datasets: 25
- Others (ORCID, ResearchGate): 50

**Category B: Old/Unusual Formats (200)**
- Pre-DOI era papers (1990s-2000): 50
- Non-English characters (umlauts, accents): 50
- Very long author lists (>20 authors): 50
- Minimal metadata (author + year only): 50

**Category C: Edge Cases (200)**
- arXiv versions (v1, v2 ambiguity): 50
- Retracted papers (real but problematic): 50
- Errata/corrections: 50
- Conference papers later published as journal: 50

**Category D: Non-Standard Venues (200)**
- Workshop papers: 50
- Technical reports: 50
- Dissertations/theses: 50
- Government publications: 50

**Category E: Sparse Metadata (200)**
- Missing DOI (but real paper): 100
- Missing journal name: 50
- Missing page numbers: 50

### 3. False Negative Tests (Fake Citations) - Target: 1,000

These are FABRICATED and should be caught:

**Category A: Frankenstein Citations (400)**
- Real author + fake title + real journal: 100
- Real title + fake author + real journal: 100
- Real author + real title + wrong year: 100
- Mix-and-match from 3 different papers: 100

**Category B: Stolen DOIs (200)**
- Real DOI + completely wrong metadata: 200

**Category C: Plausible Fakes (200)**
- Fake but plausible DOI format: 100
- Fake but plausible journal names: 100

**Category D: Nonsense (200)**
- Generic titles ("A Study of X"): 50
- Future years (2027+): 50
- Impossible dates (before journal founded): 50
- Random string DOIs: 50

---

## Folder Structure

```
test_citations/
├── TEST_DESIGN.md (this file)
├── RESULTS_SUMMARY.md (generated after testing)
├── download_scholar_citations.py
├── bulk_download_arxiv.py (NEW)
├── generate_fake_citations.py (NEW)
├── run_all_tests.py (NEW)
│
├── real_citations/ (8,000 files)
│   ├── arxiv_cs_2024/
│   │   ├── paper001.bib
│   │   ├── paper002.bib
│   │   └── ...
│   ├── arxiv_physics_2020/
│   ├── arxiv_bio_2022/
│   ├── semantic_scholar/
│   ├── papers_with_code/
│   └── crossref_random/
│
├── false_positive_tests/ (1,000 files)
│   ├── datacite_dois/
│   ├── old_formats/
│   ├── edge_cases/
│   ├── non_standard_venues/
│   └── sparse_metadata/
│
├── false_negative_tests/ (1,000 files)
│   ├── frankenstein/
│   ├── stolen_dois/
│   ├── plausible_fakes/
│   └── nonsense/
│
└── ground_truth.json (maps each file to expected result)
```

---

## Data Collection Scripts

### Script 1: `bulk_download_arxiv.py`
```bash
# Downloads .bib files from arXiv papers
python bulk_download_arxiv.py --category cs.AI --year 2024 --limit 500 --output real_citations/arxiv_cs_2024/
```

### Script 2: `download_crossref_sample.py`
```bash
# Random sample from CrossRef
python download_crossref_sample.py --count 2000 --output real_citations/crossref_random/
```

### Script 3: `generate_fake_citations.py`
```bash
# Generates Frankenstein citations from real components
python generate_fake_citations.py --type frankenstein --count 400 --source real_citations/ --output false_negative_tests/frankenstein/
```

### Script 4: `run_all_tests.py`
```bash
# Runs validator on all 10,000 citations and compares to ground truth
python run_all_tests.py --validator ../scripts/citation_validator.py --ground-truth ground_truth.json
```

---

## Evaluation Metrics

After testing, calculate:

1. **Accuracy:** (TP + TN) / Total
2. **Precision:** TP / (TP + FP) - "When we say it's real, how often are we right?"
3. **Recall:** TP / (TP + FN) - "Of all real citations, how many did we catch?"
4. **F1 Score:** Harmonic mean of precision and recall
5. **False Positive Rate:** FP / (FP + TN) - "How often do we incorrectly flag real papers?"
6. **False Negative Rate:** FN / (FN + TP) - "How often do fake citations slip through?"

**Target Performance:**
- Precision: >95% (few false alarms)
- Recall: >90% (catch most fakes)
- FPR: <5% (don't annoy users with false flags)

---

## Quick Start (Get 1,000 Citations in 10 Minutes)

Can't wait for 10,000? Start with a quick 1,000:

```bash
# 1. Download from existing arXiv papers in test_citations/
cd test_citations/
python extract_citations_from_arxiv.py 2604.05875/ real_citations/sample_001.bib

# 2. Get random CrossRef samples
python download_crossref_sample.py --count 500 --output real_citations/

# 3. Generate 100 fake citations
python generate_fake_citations.py --count 100 --output false_negative_tests/

# 4. Run tests
python run_all_tests.py --subset --count 1000
```

---

## Timeline

- **Phase 1 (Today):** Build scripts + collect 1,000 citations → Test basic functionality
- **Phase 2 (This Week):** Scale to 10,000 citations → Full evaluation
- **Phase 3 (Next Week):** Analyze results → Tune heuristics → Retest

---

## Scientific Rigor Checklist

- [ ] Stratified sampling (multiple sources, fields, years)
- [ ] Ground truth labels for every citation
- [ ] Balanced test set (not all real or all fake)
- [ ] Reproducible (scripts + data available)
- [ ] Version controlled (track what we tested when)
- [ ] Statistical significance (confidence intervals)
- [ ] Documented methodology (this file)
- [ ] Blinded testing (validator doesn't "know" ground truth)

---

## Notes on Data Sources

### arXiv Bulk Access
- Docs: https://info.arxiv.org/help/bulk_data_s3.html
- S3 bucket: `s3://arxiv/src/`
- No API key needed (public)

### Semantic Scholar
- API: https://api.semanticscholar.org/
- Free tier: 100 requests/5 minutes
- Returns BibTeX via `/paper/{id}/citations`

### CrossRef
- API: https://api.crossref.org/works?sample=1000
- No auth required
- Returns metadata in JSON (convert to BibTeX)

### Papers with Code
- API: https://paperswithcode.com/api/v1/
- Free, no key required
