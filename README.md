# Citation Validator — AI Hallucination Detection for Academic References

**Detect fabricated citations in academic papers before publication**

> Inspired by a Nature article reporting that 2-6% of 2025 papers contain AI-hallucinated citations, this tool provides a free, open-source solution for journals, reviewers, and researchers.

[![Status](https://img.shields.io/badge/status-beta-yellow)]()
[![Cost](https://img.shields.io/badge/cost-%240-green)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

---

## Quick Start

### Web App (Recommended)
```bash
# Start the Flask server
cd scripts/
python3 webapp.py

# Open http://localhost:5000 in your browser
# Drag-and-drop your .bib file or paste BibTeX entries
```

### Command Line
```bash
# Install dependencies
pip install -r scripts/requirements.txt

# Validate citations
python3 scripts/citation_validator.py path/to/bibliography.bib
```

### Browser Interface
The web app at `localhost:5000` serves `citation-validator.html` with full validation.
The Flask server handles all API calls (CrossRef, OpenAlex, Semantic Scholar) server-side.

---

## What This Tool Does

**Three-tier validation pipeline:**
1. **Deterministic checks** — CrossRef, OpenAlex, arXiv APIs verify DOIs and metadata
2. **Heuristic analysis** — 8 pattern detectors catch generic titles, temporal anomalies, etc.
3. **AI deep inspection** (optional) — Gemini, Groq, OpenAI, or Anthropic analyze suspicious patterns

**Cost-effective research:**
- Gemini free tier: 1M tokens/day = ~1,500 citations at **$0 cost**
- 10,000 citation study: **$0** over 7 days with Gemini
- "Research for the rest of us" — no grants or institutional AI budgets required

---

## Documentation

| Document | Purpose |
|----------|---------|
| **[PROJECT_STATUS.md](PROJECT_STATUS.md)** | Current state, completed features, production readiness |
| **[ROADMAP.md](ROADMAP.md)** | What's next, timeline to publication, success metrics |
| **[scripts/README.md](scripts/README.md)** | User guide, installation, cost analysis |
| **[scripts/TOKEN_TRACKING.md](scripts/TOKEN_TRACKING.md)** | Token usage tracking, cost projections |
| **[test_citations/TEST_DESIGN.md](test_citations/TEST_DESIGN.md)** | Scientific methodology, evaluation metrics |
| **[test_citations/COMMANDS.md](test_citations/COMMANDS.md)** | Quick command reference |

---

## Features

### ✅ Completed
- Full BibTeX parser with proper brace-depth handling
- Multi-provider AI integration (Gemini, Groq, OpenAI, Anthropic)
- Token usage tracking with cost analysis
- Benchmark framework with experiment logging
- Dataset registry with manifest-based loading
- Web interface with drag-and-drop

### 🟡 In Progress
- False positive testing on real citation datasets
- Checkpoint/resume capability for large-scale runs

### 📋 Planned
- Comparison dashboard (before/after fixes, provider comparisons)
- Browser extension for inline validation
- Integration with Zotero/Mendeley

---

## Test Results

### Compound Deception Benchmark (100 NeurIPS 2025 Fakes)
- **100% detection** via deterministic checks alone
- All 100 flagged as suspicious or invalid
- Runtime: ~58 seconds (no AI)

### Real-World Testing
- **5% hallucination rate** in OJSM submissions (2/40 citations)
- Matches Nature's 2-6% finding
- No false positives on 100 arXiv citations

---

## Cost Analysis

| Scale | Gemini 2.5 Flash | Groq Llama 3.3 | OpenAI GPT-4o | Anthropic Claude |
|-------|------------------|----------------|---------------|------------------|
| 100 citations | **FREE** | $0.04 | $0.35 | $0.50 |
| 1,000 citations | **FREE** | $0.43 | $3.50 | $4.95 |
| 10,000 citations | **FREE** (7 days) | $4.33 | $35.00 | $49.50 |

**Typical usage:** ~650 tokens per citation (400 input + 250 output)

---

## Published Research Context

This tool builds on five major studies from early 2026:

| Study | Key Finding |
|-------|-------------|
| Bienz et al. | 2-6% hallucination rate in HPC papers (source of Nature's headline) |
| Ansari | 100 fakes in NeurIPS 2025, 5-category taxonomy |
| Sakai et al. | 275 hallucinated papers in ACL/NAACL/EMNLP 2025 |
| Rao & Callison-Burch | 931-paper benchmark, field-level ground truth |
| Abbonato (CheckIfExist) | Open-source tool, direct competitor |

---

## Contributing

We welcome contributions! Areas of interest:
- **Dataset curation**: Add published benchmarks to `datasets/`
- **False positive analysis**: Test on edge cases (DataCite, pre-DOI era, non-English)
- **Provider comparison**: Run identical datasets through different AI models
- **UI enhancements**: Benchmark library panel, comparison dashboard

---

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{edwards2026citationvalidator,
  author = {Edwards, Todd},
  title = {Citation Validator: AI Hallucination Detection for Academic References},
  year = {2026},
  url = {https://github.com/toddgr/Ohio-Journal-of-School-Mathematics},
  note = {Version 1.0}
}
```

---

## License

MIT License — [LICENSE](LICENSE)

---

## Contact

**Todd Edwards**  
*Ohio Journal of School Mathematics*  
**Goal:** Publish Nature-quality paper on affordable hallucination detection
