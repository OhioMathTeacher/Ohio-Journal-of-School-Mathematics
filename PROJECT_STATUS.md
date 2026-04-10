# Citation Validator — Project Status
**Last updated:** April 10, 2026

---

## Overview

The OJSM Citation Validator detects AI-hallucinated citations in academic papers. Inspired by a Nature article reporting that 2-6% of 2025 papers contain fabricated references, this tool provides a free, open-source alternative to catch these before publication.

**Three-tier validation pipeline:**
1. **Deterministic checks** — CrossRef, OpenAlex, arXiv APIs verify DOIs and metadata
2. **Database lookups** — Fallback searches for non-DOI citations
3. **AI analysis** — Optional deep inspection via Gemini, Groq, OpenAI, or Anthropic

**Interfaces:**
- Web app (Flask) at localhost:5000 with drag-and-drop interface
- Browser-only static HTML (no server needed)
- Python CLI for batch processing

---

## Current State (April 10, 2026)

### ✅ Completed Features

#### Core Validation
- Full BibTeX parser with proper brace-depth handling
- DOI validation via CrossRef with arXiv/DataCite fallbacks
- Metadata similarity scoring (Jaccard distance)
- OpenAlex fallback with similarity gate (≥ 0.5 threshold)
- 8 heuristic pattern detectors (future years, generic titles, etc.)
- Multi-provider AI integration (4 providers)

#### Accuracy Fixes (9 bugs squashed April 8-9)
All major accuracy issues resolved:
- Python BibTeX parser rewrote with brace-depth tracking (was dropping nested entries)
- OpenAlex similarity gate prevents false validation
- JavaScript default status changed from 'invalid' to 'unknown' (prevents network errors → false positives)
- DOI confirmation now protects against heuristic downgrade
- Jaccard similarity standardized between Python and JS
- arXiv check scopes to DOI field only

#### Testing Infrastructure
- 100 fabricated citations from NeurIPS 2025 study (compound-deception-ansari dataset)
- 10 real citations from Nature article
- Benchmark framework (`run_benchmark.py`) with manifest-based datasets
- Experiment logging to JSONL with full reproducibility

#### Cost Tracking (NEW — April 10, 2026)
- **Token usage tracking** across all 4 AI providers
- **Metadata capture**: input/output/total tokens per citation
- **Cost analysis tool** (`cost_analysis.py`) projects costs at scale
- **Gemini free tier economics**: 1M tokens/day = ~1,500 citations at $0
- **"Research for the rest of us"**: 10K citation study costs $0 over 7 days with Gemini

#### Web Interface
- Localhost Flask server with localStorage API key management
- Drag-and-drop BibTeX upload
- Dataset selector (loads from manifest.json)
- Export to HTML, CSV, JSON
- Real-time validation progress

#### Documentation
- Comprehensive README ([scripts/README.md](scripts/README.md))
- Token tracking guide ([scripts/TOKEN_TRACKING.md](scripts/TOKEN_TRACKING.md))
- Testing methodology ([test_citations/TEST_DESIGN.md](test_citations/TEST_DESIGN.md))
- Quick command reference ([test_citations/COMMANDS.md](test_citations/COMMANDS.md))

### 🟡 In Progress

#### False Positive Testing
**Status:** Not yet run on real citations  
**Critical for publication:** Need precision/recall metrics on legitimate citations

Available real citation datasets:
- 285 arXiv CS papers (ojsm-real-arxiv in manifest)
- 100 CrossRef random sample (ojsm-real-crossref in manifest)
- 10 citations from Nature article (nature-article dataset)

**Next step:** Run benchmark on real datasets to establish false positive rate

```bash
python3 scripts/run_benchmark.py --dataset ojsm-real-arxiv --ai gemini
python3 scripts/run_benchmark.py --dataset ojsm-real-crossref --ai gemini
```

### ❌ Not Started

#### Production Features
1. **Checkpoint/resume capability** — For large-scale runs (10K citations), save progress every N citations
2. **Rate limit handling** — Smart backoff for API 429 errors
3. **Batch processing modes** — CLI flag to process entire directory of .bib files

#### Analysis Tools
1. **Comparison dashboard** — Compare runs side-by-side (before/after fixes, different providers)
2. **False positive analysis** — Identify systematic patterns in FP errors
3. **Confidence calibration** — Does AI confidence score correlate with accuracy?

---

## Test Results

### Benchmark: Compound Deception (100 Fake Citations)
**Deterministic only (no AI):**
- True negatives: 100/100 (100% detection)
- False negatives: 0/100
- Time: ~58s

**With Gemini AI:**
- All 100 correctly flagged as suspicious/invalid
- Perfect detection via database checks alone
- AI adds detailed reasoning and confidence scores

**With Groq AI:**
- 77/100 rate-limited (429 errors)
- 23/100 successful analyses
- Demonstrates need for Gemini free tier for batch work

### Real-World Testing
**6622 Guerrero bibliography (40 citations):**
- 2 invalid DOIs detected (5% failure rate)
- Matches Nature's 2-6% finding
- Both flagged for manual review

**arXiv papers (100 citations):**
- All correctly identified as valid (no DOIs expected for preprints)
- No false positives

---

## Production Readiness Assessment

**Ready for:**
- ✅ Single-file validation (web or CLI)
- ✅ Batch testing on datasets up to ~500 citations
- ✅ Reproducible experiments with token tracking

**Not ready for:**
- ❌ 10,000 citation study without false positive baseline
- ❌ Long-running jobs without checkpoint/resume
- ❌ Publication without precision/recall on real citations

**Estimated timeline to production:**
1. False positive testing (30 min runtime) → Establish precision baseline
2. Add checkpoint/resume (2-3 hours dev time) → Enable robust large-scale runs
3. Run 10K study with Gemini free tier (7 days wall time, $0 cost)

---

## Published Research Context

Five major studies inform our approach:

| Study | Key Finding | Relevance |
|-------|-------------|-----------|
| **Bienz et al.** (arXiv:2602.05867) | 2-6% hallucination rate in 2025 HPC papers | Our real-world test matched this (5%) |
| **Ansari** (arXiv:2602.05930) | 100 fakes in NeurIPS 2025, 5-category taxonomy | We use this as test dataset |
| **Sakai et al.** (arXiv:2601.18724) | 275 hallucinated papers in ACL/NAACL/EMNLP 2025 | Potential future benchmark |
| **Rao & Callison-Burch** (arXiv:2604.03159) | 931-paper benchmark, field-level ground truth | High-priority external validation target |
| **Abbonato (CheckIfExist)** (arXiv:2602.15871) | Open-source tool, CrossRef + Semantic Scholar | Direct competitor for comparison |

---

## Next Priorities

### Immediate (before 10K study)
1. **Run false positive tests** — Establish precision on real citations
2. **Add checkpoint/resume** — Enable large-scale robustness
3. **Document confidence thresholds** — What AI confidence = what action?

### Short-term (for Nature paper)
1. **10K citation study** — Mix of real + NeurIPS fakes using Gemini free tier
2. **Compare to CheckIfExist** — Run identical dataset through both tools
3. **Integrate Rao benchmark** — Test against 931-paper ground truth
4. **Write methods section** — Document validation pipeline, token costs, accuracy

### Long-term (stretch goals)
1. **Challenge mode UI** — Educational tool for training editors
2. **Benchmark library panel** — Load published datasets in web interface
3. **Comparison dashboard** — Visualize our results vs. published studies
4. **Browser extension** — Validate citations directly in Google Scholar

---

## File Inventory

### Core Application
- `citation-validator.html` — Browser-only static app
- `scripts/webapp.py` — Flask server (localhost:5000)
- `scripts/citation_validator.py` — Python CLI + core logic
- `scripts/citation_enhancements.py` — Heuristic pattern detection

### Testing & Benchmarks
- `scripts/run_benchmark.py` — Systematic testing framework
- `scripts/cost_analysis.py` — Token usage and cost projections
- `scripts/compare_runs.py` — Compare experiment results
- `datasets/manifest.json` — Dataset registry
- `datasets/compound-deception-ansari/` — NeurIPS 2025 fakes (100 citations)
- `datasets/nature-article/` — Citations from Nature article (10 citations)

### Documentation
- `PROJECT_STATUS.md` — This file (consolidated status)
- `scripts/README.md` — User guide and quick start
- `scripts/TOKEN_TRACKING.md` — Cost tracking documentation
- `test_citations/TEST_DESIGN.md` — Scientific methodology
- `test_citations/COMMANDS.md` — Quick command reference
- `ROADMAP.md` — What's left to do

---

## Contact

**Todd Grundmeier** — *Ohio Journal of School Mathematics*  
**Goal:** Publish Nature-quality paper on affordable hallucination detection  
**Philosophy:** "Research for the rest of us" — accessible, reproducible, and cheap
