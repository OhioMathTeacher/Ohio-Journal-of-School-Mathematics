# Citation Validator Testing - Command Reference
**Quick reference for all testing commands**

---

## Current Test Data (785 citations)

```
test_citations/
├── real_citations/               # 385 VALID citations
│   ├── arxiv_cs_2024/           # 285 from arXiv papers
│   └── crossref_random/         # 100 from CrossRef API
│
├── false_negative_tests/        # 400 INVALID citations (should be caught)
│   ├── frankenstein/            # 100 (real parts, wrong combo)
│   ├── stolen_doi/              # 100 (real DOI, fake metadata)
│   ├── plausible/               # 100 (totally fake, looks real)
│   └── nonsense/                # 100 (obviously wrong)
│
└── false_positive_tests/        # (empty - to be filled with edge cases)
```

---

## Essential Commands

### Test What You Have Now
```bash
# Test first 20 citations (quick sanity check)
python3 run_all_tests.py --limit 20

# Test all 785 citations (takes ~10 minutes)
python3 run_all_tests.py
```

### Scale to 1,000 Citations (15 minutes)
```bash
# Get 300 more real citations
python3 download_crossref_sample.py 300 real_citations/crossref_random/

# Generate 300 more fakes
python3 generate_fake_citations.py --type all --count 300 --output false_negative_tests/

# Test everything
python3 run_all_tests.py
```

### Scale to 5,000 Citations (1 hour)
```bash
# Real citations from CrossRef
python3 download_crossref_sample.py 2000 real_citations/crossref_2023/ 'from-pub-date:2023'
python3 download_crossref_sample.py 2000 real_citations/crossref_2010s/ 'from-pub-date:2010,until-pub-date:2020'

# More fake citations
python3 generate_fake_citations.py --type frankenstein --count 400 --output false_negative_tests/frankenstein/
python3 generate_fake_citations.py --type stolen_doi --count 400 --output false_negative_tests/stolen_doi/
python3 generate_fake_citations.py --type plausible --count 400 --output false_negative_tests/plausible/
python3 generate_fake_citations.py --type nonsense --count 400 --output false_negative_tests/nonsense/

# Run full test suite
python3 run_all_tests.py --output results_5000.json
```

### Scale to 10,000+ Citations (3-4 hours)
```bash
# Download arXiv bulk data (requires ~5GB space)
# See: https://info.arxiv.org/help/bulk_data_s3.html

# Option 1: Use AWS CLI
aws s3 sync s3://arxiv/src/ ./arxiv_bulk/ --no-sign-request

# Option 2: Direct download
wget https://arxiv.org/src/2604/2604.tar
tar -xf 2604.tar
python3 extract_citations_from_arxiv.py --all

# Scale up fakes to match
python3 generate_fake_citations.py --type all --count 2000 --output false_negative_tests/

# Full validation
python3 run_all_tests.py --output results_10000.json
```

---

## Data Collection Commands

### CrossRef (Random Samples)
```bash
# Basic download
python3 download_crossref_sample.py <count> <output_dir>

# With filters
python3 download_crossref_sample.py 1000 real_citations/recent/ 'from-pub-date:2023'
python3 download_crossref_sample.py 1000 real_citations/journals/ 'type:journal-article'
python3 download_crossref_sample.py 1000 real_citations/orcid/ 'has-orcid:true'
```

### arXiv Papers
```bash
# Extract from existing folders
python3 extract_citations_from_arxiv.py 2604.05875/

# Extract from all folders in directory
python3 extract_citations_from_arxiv.py --all
```

### Google Scholar (Manual)
```bash
# Print URLs to visit
python3 download_scholar_citations.py "machine learning" output.bib

# Automated (requires scholarly library)
pip install scholarly
python3 download_scholar_citations.py --auto "deep learning" output.bib --num 50
```

### Fake Citations
```bash
# Single type
python3 generate_fake_citations.py --type frankenstein --count 100 --output false_negative_tests/frankenstein/
python3 generate_fake_citations.py --type stolen_doi --count 100 --output false_negative_tests/stolen_doi/
python3 generate_fake_citations.py --type plausible --count 100 --output false_negative_tests/plausible/
python3 generate_fake_citations.py --type nonsense --count 100 --output false_negative_tests/nonsense/

# All types at once (splits count evenly)
python3 generate_fake_citations.py --type all --count 400 --output false_negative_tests/
```

---

## Test Running Commands

### Quick Tests
```bash
# Test first N files only
python3 run_all_tests.py --limit 10
python3 run_all_tests.py --limit 50
python3 run_all_tests.py --limit 100
```

### Specific Directories
```bash
# Test only real citations
python3 run_all_tests.py --test-dirs real_citations/

# Test only fake citations
python3 run_all_tests.py --test-dirs false_negative_tests/

# Test multiple specific directories
python3 run_all_tests.py --test-dirs real_citations/arxiv_cs_2024/ false_negative_tests/frankenstein/
```

### Full Test Runs
```bash
# Default: all test directories
python3 run_all_tests.py

# Save results to specific file
python3 run_all_tests.py --output my_results.json

# Specify validator location
python3 run_all_tests.py --validator ../scripts/citation_validator.py
```

---

## Workflow Examples

### Scenario 1: Quick Validation (10 minutes)
```bash
# Use what you already have
cd test_citations/
python3 run_all_tests.py --limit 50

# Review results
cat test_results.json | head -100
```

### Scenario 2: Scale to 1,000 (30 minutes)
```bash
# Get more real citations (5 min)
python3 download_crossref_sample.py 500 real_citations/crossref_random/

# Generate more fakes (2 min)
python3 generate_fake_citations.py --type all --count 500 --output false_negative_tests/

# Run tests (20 min)
python3 run_all_tests.py --output results_1000.json
```

### Scenario 3: Build Complete Test Suite (4 hours)
```bash
# Phase 1: Real citations from multiple sources (2 hours)
python3 download_crossref_sample.py 2000 real_citations/crossref_recent/ 'from-pub-date:2023'
python3 download_crossref_sample.py 2000 real_citations/crossref_older/ 'from-pub-date:2010,until-pub-date:2020'
python3 download_crossref_sample.py 1000 real_citations/crossref_journals/ 'type:journal-article'

# Download arXiv bulk (requires space and time)
# [Manual download from arxiv.org]
python3 extract_citations_from_arxiv.py --all

# Phase 2: Generate comprehensive fakes (30 min)
python3 generate_fake_citations.py --type frankenstein --count 600 --output false_negative_tests/frankenstein/
python3 generate_fake_citations.py --type stolen_doi --count 600 --output false_negative_tests/stolen_doi/
python3 generate_fake_citations.py --type plausible --count 600 --output false_negative_tests/plausible/
python3 generate_fake_citations.py --type nonsense --count 600 --output false_negative_tests/nonsense/

# Phase 3: Run full validation (1 hour)
python3 run_all_tests.py --output results_comprehensive.json

# Phase 4: Analyze
cat results_comprehensive.json | jq '.evaluation.metrics'
```

---

## Parallel Execution (Advanced)

### Run Multiple Downloads in Parallel
```bash
# Open multiple terminals or use background jobs
python3 download_crossref_sample.py 1000 real_citations/batch1/ &
python3 download_crossref_sample.py 1000 real_citations/batch2/ &
python3 download_crossref_sample.py 1000 real_citations/batch3/ &
wait
echo "All downloads complete!"
```

### Generate Fakes in Parallel
```bash
python3 generate_fake_citations.py --type frankenstein --count 500 --output false_negative_tests/frankenstein/ &
python3 generate_fake_citations.py --type stolen_doi --count 500 --output false_negative_tests/stolen_doi/ &
python3 generate_fake_citations.py --type plausible --count 500 --output false_negative_tests/plausible/ &
python3 generate_fake_citations.py --type nonsense --count 500 --output false_negative_tests/nonsense/ &
wait
```

---

## Monitoring Progress

### Check How Many Citations You Have
```bash
# Count .bib files
find real_citations false_negative_tests -name "*.bib" | wc -l

# Count total citations (approximate)
grep -r "^@" real_citations/ false_negative_tests/ | wc -l

# Detailed breakdown
echo "Real citations:"
grep -r "^@" real_citations/ | wc -l
echo "Fake citations:"
grep -r "^@" false_negative_tests/ | wc -l
```

### Watch Test Progress
```bash
# Run in background, watch logs
python3 run_all_tests.py > test_output.log 2>&1 &
tail -f test_output.log
```

---

## Tips & Tricks

### Speed Up CrossRef Downloads
```bash
# Download larger batches (API allows up to 100 per request)
# Script automatically handles pagination
python3 download_crossref_sample.py 5000 real_citations/bulk/
```

### Verify Ground Truth Labels
```bash
# Check what labels are assigned
python3 -c "
from run_all_tests import load_ground_truth
gt = load_ground_truth(['real_citations/', 'false_negative_tests/'])
print(f'Total files: {len(gt)}')
print(f'VALID: {list(gt.values()).count(\"VALID\")}')
print(f'INVALID: {list(gt.values()).count(\"INVALID\")}')
"
```

### Extract Specific Results
```bash
# Using jq to analyze JSON results
cat test_results.json | jq '.evaluation.metrics'
cat test_results.json | jq '.confusion_matrix'
cat test_results.json | jq '.results[] | select(.invalid > 0)'
```

---

**Next Steps:**
1. Start small: `python3 run_all_tests.py --limit 20`
2. Review outputs to verify validator is working
3. Scale up: `python3 download_crossref_sample.py 500`
4. Full test: `python3 run_all_tests.py`
