# Citation Validator Testing - Current Status
**Updated:** April 8, 2026  
**Test Data Generated:** 785+ citations organized scientifically

---

## ✓ What We Have Now

### Real Citations (Ground Truth: VALID) - 385 citations
```
real_citations/
├── arxiv_cs_2024/
│   ├── arxiv_2604.05875.bib (205 citations)
│   └── arxiv_2604.05952.bib (80 citations)
└── crossref_random/
    ├── crossref_sample_0001.bib (50 citations)
    └── crossref_sample_0002.bib (50 citations)
```

### Fake Citations (Ground Truth: INVALID) - 400 citations
```
false_negative_tests/
├── frankenstein/ (100 citations - real components mixed wrong)
│   ├── frankenstein_0001.bib (50)
│   ├── frankenstein_0002.bib (50)
│   └── ground_truth_frankenstein.json
├── stolen_doi/ (100 citations - real DOIs, fake metadata)
│   ├── stolen_doi_0001.bib (50)
│   ├── stolen_doi_0002.bib (50)
│   └── ground_truth_stolen_doi.json
├── plausible/ (100 citations - completely fake but looks real)
│   ├── plausible_0001.bib (50)
│   ├── plausible_0002.bib (50)
│   └── ground_truth_plausible.json
└── nonsense/ (100 citations - obviously fake)
    ├── nonsense_0001.bib (50)
    ├── nonsense_0002.bib (50)
    └── ground_truth_nonsense.json
```

**Total Test Citations: 785**
- Real citations: 385 (49%)
- Fake citations: 400 (51%)
- Balanced test set ✓

---

## 🚀 Quick Start

Run the first test batch:
```bash
cd test_citations/
python3 run_all_tests.py --limit 20
```

---

## 📈 Scaling to 10,000 Citations

### Phase 1: More Real Citations (Target: 8,000)

#### From CrossRef (Easy - Just API Calls)
```bash
# Download 2,000 recent papers
python3 download_crossref_sample.py 2000 real_citations/crossref_recent/ 'from-pub-date:2023'

# Download 2,000 older papers
python3 download_crossref_sample.py 2000 real_citations/crossref_2010s/ 'from-pub-date:2010,until-pub-date:2020'

# Download 1,000 with ORCID (high quality)
python3 download_crossref_sample.py 1000 real_citations/crossref_orcid/ 'has-orcid:true'
```

*Time: ~30 minutes (API rate limits)*
*Cost: $0 (free API)*

#### From arXiv (Bulk Download)
```bash
# Use arXiv bulk data access
# Download .tar files from: https://info.arxiv.org/help/bulk_data_s3.html
wget https://arxiv.org/src/2604/2604.tar
tar -xf 2604.tar
python3 extract_citations_from_arxiv.py --all
```

*Time: ~1-2 hours (download + extraction)*
*Cost: $0*
*Result: ~2,000-5,000 citations from hundreds of papers*

#### From Semantic Scholar (API)
```bash
# Coming soon - semantic_scholar_downloader.py
# Uses: https://api.semanticscholar.org/
```

### Phase 2: More Fake Citations (Target: 2,000)

```bash
# Generate 500 of each type
python3 generate_fake_citations.py --type frankenstein --count 500 --output false_negative_tests/frankenstein/
python3 generate_fake_citations.py --type stolen_doi --count 500 --output false_negative_tests/stolen_doi/
python3 generate_fake_citations.py --type plausible --count 500 --output false_negative_tests/plausible/
python3 generate_fake_citations.py --type nonsense --count 500 --output false_negative_tests/nonsense/
```

*Time: ~5 minutes*
*Cost: $0*

### Phase 3: False Positive Test Cases

Create edge cases that are REAL but might be flagged:

```bash
# Manual curation needed for these
# - Zenodo DOIs (DataCite registry)
# - Figshare datasets
# - Old papers (pre-2000, no DOI)
# - Non-English papers
# - Retracted papers
```

---

## 🧪 Running Tests at Scale

### Quick Test (100 citations)
```bash
python3 run_all_tests.py --limit 100
```

### Full Test (All citations)
```bash
python3 run_all_tests.py --output test_results_full.json
```

### Parallel Testing (10x faster)
```bash
# Coming soon - parallel test runner
./run_tests_parallel.sh --workers 10
```

---

## 📊 Expected Timeline

| Phase | Task | Time | Result |
|-------|------|------|--------|
| ✓ Done | Initial setup | 1 hour | 785 citations |
| Today | CrossRef bulk download | 1 hour | +5,000 citations |
| Today | Generate more fakes | 10 min | +1,600 fakes |
| This week | arXiv bulk extract | 2 hours | +3,000 citations |
| This week | Manual edge cases | 1 hour | +200 edge cases |
| **Total** | | **~5 hours** | **10,585 citations** |

---

## 🎯 Target Metrics

After running full test suite, we want:
- **Precision > 95%** - Don't flag real papers incorrectly
- **Recall > 90%** - Catch most fake citations
- **F1 Score > 92%** - Balanced performance
- **False Positive Rate < 5%** - Low false alarms
- **Tested on 10,000+ papers** - Statistical significance

---

## 📝 Test Categories

### Real Citations (Ground Truth: VALID)
- [x] arXiv CS papers (2024) - 285 citations
- [x] CrossRef random sample - 100 citations
- [ ] CrossRef recent (2023-2026) - Target: 2,000
- [ ] CrossRef older (2010-2020) - Target: 2,000
- [ ] Physics papers - Target: 1,000
- [ ] Biology papers - Target: 1,000
- [ ] Math papers - Target: 500

### Fake Citations (Ground Truth: INVALID)
- [x] Frankenstein (mixed real components) - 100
- [x] Stolen DOIs - 100
- [x] Plausible fakes - 100
- [x] Nonsense (future years, etc.) - 100
- [ ] Scale each category to 500 citations

### Edge Cases (Real but Tricky)
- [ ] Zenodo DOIs (DataCite)
- [ ] Figshare datasets
- [ ] Pre-2000 papers (no DOI)
- [ ] Retracted papers
- [ ] Non-English papers
- [ ] Very long author lists
- [ ] Workshop papers
- [ ] arXiv version ambiguity

---

## 🔧 Scripts Available

1. **extract_citations_from_arxiv.py** - Extract from arXiv papers
2. **download_crossref_sample.py** - Download random samples from CrossRef
3. **download_scholar_citations.py** - Get citations from Google Scholar
4. **generate_fake_citations.py** - Create synthetic fake citations
5. **run_all_tests.py** - Run validator and calculate metrics
6. **quick_start.sh** - One-command demo

---

## 💡 Tips for Scaling

### Efficient CrossRef Downloads
```bash
# Download in background, check later
nohup python3 download_crossref_sample.py 5000 real_citations/bulk/ &
tail -f nohup.out
```

### Parallel Fake Citation Generation
```bash
# Generate 4 batches in parallel
python3 generate_fake_citations.py --type frankenstein --count 500 --output false_negative_tests/frankenstein/ &
python3 generate_fake_citations.py --type stolen_doi --count 500 --output false_negative_tests/stolen_doi/ &
python3 generate_fake_citations.py --type plausible --count 500 --output false_negative_tests/plausible/ &
python3 generate_fake_citations.py --type nonsense --count 500 --output false_negative_tests/nonsense/ &
wait
```

### Testing Workflow
```bash
# 1. Generate test data
./quick_start.sh

# 2. Run initial validation
python3 run_all_tests.py --limit 50

# 3. Scale up gradually
python3 download_crossref_sample.py 1000
python3 generate_fake_citations.py --type all --count 1000

# 4. Full validation
python3 run_all_tests.py

# 5. Analyze results
python3 analyze_results.py test_results.json
```

---

## 📚 Data Sources

### ✓ Currently Using
- **CrossRef API**: https://api.crossref.org/ (free, no key)
- **arXiv Papers**: Local extraction from downloaded papers
- **Synthetic Generation**: Python random generation

### 🔜 Coming Soon
- **arXiv Bulk Data**: https://info.arxiv.org/help/bulk_data_s3.html
- **Semantic Scholar**: https://api.semanticscholar.org/
- **OpenAlex**: https://openalex.org/
- **Papers with Code**: https://paperswithcode.com/api/v1/

---

**Next Action:** Run `python3 run_all_tests.py --limit 50` to validate your first 50 citations!
