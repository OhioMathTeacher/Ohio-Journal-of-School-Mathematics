# Citation Validator — Quick Command Reference
**Last updated:** April 2026

---

## Validate Citations

### Browser (recommended for most users)
Open `citation-validator.html` in any browser. Paste BibTeX or upload a `.bib` file.

### Command line
```bash
cd scripts/

# Basic validation
python3 citation_validator.py path/to/bibliography.bib

# Verbose output (show progress per citation)
python3 citation_validator.py --verbose bibliography.bib

# With AI analysis (requires API key)
export GROQ_API_KEY='gsk_...'
python3 citation_validator.py --ai bibliography.bib

# Provide key inline
python3 citation_validator.py --ai --groq-key gsk_... bibliography.bib
```

---

## Run the Test Suite

```bash
cd test_citations/

# Quick sanity check (20 citations)
python3 run_all_tests.py --limit 20

# Full synthetic suite (785 citations, ~10 min)
python3 run_all_tests.py

# Save results to file
python3 run_all_tests.py --output test_results_$(date +%Y%m%d).json

# Test a specific category only
python3 run_all_tests.py --test-dirs real_citations/
python3 run_all_tests.py --test-dirs false_negative_tests/
python3 run_all_tests.py --test-dirs false_negative_tests/frankenstein/

# Compare two result files
python3 -c "
import json
for fname in ['test_results_full.json', 'test_results_post_bugfix.json']:
    with open(fname) as f:
        d = json.load(f)
    m = d['evaluation']['metrics']
    print(f'{fname}: F1={m[\"f1_score\"]:.2%}  FPR={m[\"false_positive_rate\"]:.2%}  FNR={m[\"false_negative_rate\"]:.2%}')
"
```

---

## Generate Synthetic Test Data

```bash
cd test_citations/

# Fake citations — individual types
python3 generate_fake_citations.py --type frankenstein --count 100 --output false_negative_tests/frankenstein/
python3 generate_fake_citations.py --type stolen_doi   --count 100 --output false_negative_tests/stolen_doi/
python3 generate_fake_citations.py --type plausible    --count 100 --output false_negative_tests/plausible/
python3 generate_fake_citations.py --type nonsense     --count 100 --output false_negative_tests/nonsense/

# All types at once
python3 generate_fake_citations.py --type all --count 400 --output false_negative_tests/

# Real citations from CrossRef
python3 download_crossref_sample.py 500 real_citations/crossref_random/
python3 download_crossref_sample.py 1000 real_citations/crossref_recent/ 'from-pub-date:2023'
python3 download_crossref_sample.py 1000 real_citations/crossref_older/  'from-pub-date:2010,until-pub-date:2020'

# From arXiv source files
python3 extract_citations_from_arxiv.py --all
```

---

## Inspect and Count Test Data

```bash
cd test_citations/

# Count citations in each category
echo "Real:"; grep -r "^@" real_citations/ | wc -l
echo "Fake:"; grep -r "^@" false_negative_tests/ | wc -l
echo "Total:"; grep -r "^@" real_citations/ false_negative_tests/ | wc -l

# Check ground truth labels
python3 -c "
from run_all_tests import load_ground_truth
gt = load_ground_truth(['real_citations/', 'false_negative_tests/'])
print(f'VALID:   {list(gt.values()).count(\"VALID\")} files')
print(f'INVALID: {list(gt.values()).count(\"INVALID\")} files')
"
```

---

## Dataset Explorer (Incoming)

The `datasets/` directory will hold external benchmark datasets from published research. Once populated:

```bash
# List available datasets
cat datasets/manifest.json | python3 -m json.tool

# Run test against a specific published benchmark
python3 run_all_tests.py --test-dirs ../datasets/compound-deception-ansari-2026/
python3 run_all_tests.py --test-dirs ../datasets/bibtex-hallucinations-rao-2026/

# Compare our results against published numbers
python3 run_all_tests.py \
  --test-dirs ../datasets/compound-deception-ansari-2026/ \
  --output results_ansari_comparison.json
```

The browser app's **Benchmark Library** panel (coming soon) lets you load and combine these datasets without any command line.

---

## Useful One-Liners

```bash
# How many .bib files exist?
find test_citations/ -name "*.bib" | wc -l

# View results metrics from a saved run
cat test_results.json | python3 -c "import json,sys; m=json.load(sys.stdin)['evaluation']['metrics']; [print(f'{k}: {v:.2%}') for k,v in m.items()]"

# Find false negatives in a results file (fakes that passed)
cat test_results.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
fn = data['evaluation']['confusion_matrix']['false_negative']
print(f'False negatives: {fn}')
"

# Syntax-check the validator scripts
python3 -c "import py_compile; py_compile.compile('../scripts/citation_validator.py', doraise=True); print('OK')"
python3 -c "import py_compile; py_compile.compile('../scripts/citation_enhancements.py', doraise=True); print('OK')"
```
