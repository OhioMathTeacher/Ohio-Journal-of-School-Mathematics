# Citation Validator — Project Status & Roadmap
**Last updated:** April 2026

---

## What This Tool Does

The OJSM Citation Validator checks academic BibTeX references for signs of AI hallucination — fabricated citations that look real but don't exist. It uses a three-layer pipeline:

1. **CrossRef / arXiv / DOI resolver** — verifies a DOI actually exists and that the metadata matches
2. **OpenAlex title search** — fallback for citations without DOIs
3. **Heuristic pattern detection** — catches suspicious patterns (generic titles, future years, metadata mismatches)
4. **Optional AI analysis** — deeper Frankenstein citation detection via Claude, Gemini, Groq, or OpenAI

The tool runs entirely in the browser (static HTML + JS) or from the command line (Python). No server, no installation required for users.

---

## Current State (April 2026)

### What works
- Full BibTeX parsing with proper brace-depth handling (browser and CLI)
- DOI validation via CrossRef with arXiv and DataCite fallbacks
- Title similarity scoring (Jaccard) for metadata matching
- OpenAlex fallback with similarity gating (threshold ≥ 0.5 to prevent false validation)
- Multi-provider AI analysis (Claude, Gemini, Groq, OpenAI)
- File upload, drag-and-drop, and direct paste input
- Export to HTML, JSON, and CSV

### Validator bug fixes completed (April 2026)
Nine accuracy bugs were identified and fixed. Prior to these fixes, false positives and false negatives were occurring due to:

| Bug | Impact | Fix |
|-----|--------|-----|
| Python BibTeX parser used regex | Silently dropped entries with nested braces | Rewrote with brace-depth tracking |
| OpenAlex accepted any top result | Fabricated titles validated by unrelated papers | Added Jaccard similarity gate (≥ 0.5) |
| JS default status was `'invalid'` | Network failures caused false positives | Changed to `'unknown'` |
| Heuristic warnings overrode confirmed DOIs | Real papers with minor quirks marked suspicious | DOI confirmation now protects against downgrade |
| DOI resolver returned no metadata | Stolen DOIs on DataCite passed unchecked | Added content-negotiation metadata fetch |
| Title comparison was substring-based | Short shared phrases caused false matches | Replaced with Jaccard similarity (threshold 0.4) |
| arXiv check scanned all fields | Any fake with "arxiv" in notes bypassed checks | Now checks DOI field only |
| JS and Python used different OpenAlex endpoints | Inconsistent results between browser and CLI | Both now use structured `filter` endpoint |
| Jaccard tokenization differed JS vs Python | Same citation scored differently by each | Both now use `\w+` word tokenization |

### Test suite
785 citations organized for scientific evaluation:
- **385 real citations** (arXiv CS papers, CrossRef random sample)
- **400 synthetic fakes** (Frankenstein, stolen DOI, plausible, nonsense)
- Per-citation ground truth, not per-file (fixed in the test runner)

---

## Published Research Landscape

In researching the Nature article that inspired this tool, we found five major published datasets and tools from other researchers working on the same problem. These represent the best available external ground truth for benchmarking.

| Paper | Dataset Size | What They Found |
|-------|-------------|-----------------|
| **HalluCitation** — Sakai et al. (arXiv:2601.18724) | ~300 hallucinated papers at ACL/NAACL/EMNLP 2024-2025 | 20 hallucinated papers in 2024 → 275 in 2025; Appendix B lists them |
| **Compound Deception** — Ansari (arXiv:2602.05930) | 100 fabricated citations in 53 NeurIPS 2025 papers | 5-category taxonomy: Total Fabrication 66%, Partial Corruption 27%, Identifier Hijacking 4% |
| **BibTeX Citation Hallucinations** — Rao & Callison-Burch (arXiv:2604.03159) | 931-paper benchmark, ~23K field observations | Only 50.9% of LLM-generated BibTeX fully correct; released benchmark + `clibib` tool |
| **GhostCite** — CiteVerifier (arXiv:2602.06718) | 375K citations from 13 LLMs; 2.2M real citations 2020-2025 | 14–95% hallucination rates depending on LLM; 1.07% of real papers had invalid citations |
| **CheckIfExist** — Abbonato (arXiv:2602.15871) | Open-source tool; CrossRef + Semantic Scholar + OpenAlex | Published code at github.com/zabbonat/References-Validation |
| **Mysterious Citations** — Bienz et al. (arXiv:2602.05867) | 4 HPC conferences 2021 vs 2025 | 0% in 2021 → 2-6% in 2025; source of Nature's headline figure |

These datasets use the same types of hallucinations we already test, and their taxonomies map directly onto ours:

| Our category | Ansari taxonomy equivalent |
|---|---|
| Frankenstein | Partial Attribute Corruption |
| Stolen DOI | Identifier Hijacking |
| Plausible | Total Fabrication (believable) |
| Nonsense | Total Fabrication (obvious) |

---

## Where We're Heading

### Tier 1: Benchmark Library in the HTML App (next priority)
Add a third data source to the validator alongside "paste" and "file upload":

- A **Benchmark Library panel** with dataset cards (name, author, year, citation count, type breakdown)
- **Load** any dataset into the validator with one click
- **Combine** multiple datasets (e.g., "mix 100 real from HalluCitation + 100 fakes from Compound Deception")
- **Filter** across datasets by ground truth label, fabrication type, domain

Data architecture: standard `.bib` files + sidecar `.json` metadata per dataset, organized under `datasets/` with a `manifest.json` index.

### Tier 2: Comparison & Accuracy Dashboard (soon after)
Once we have published ground truth:
- After validation, show a confusion matrix against ground truth labels
- "How did we do?" — TP/TN/FP/FN vs. the published results from each study
- Compare our detection rates to CheckIfExist's published numbers

### Tier 3: Challenge Mode (stretch goal)
- Load a mixed real+fake set with labels hidden
- User flags suspicious citations manually before running the validator
- Side-by-side reveal: human intuition vs. machine results
- Useful for teaching and editorial training

### Test suite expansion
Priority order for dataset integration:
1. **Rao & Callison-Burch 931-paper benchmark** — most rigorous, has field-level ground truth
2. **Compound Deception 100 NeurIPS fakes** — categorized by fabrication type
3. **HalluCitation Appendix B** — real ACL/NAACL/EMNLP data
4. **Bienz et al. HPC conference data** — the source of Nature's 2-6% figure
5. **GhostCite 2.2M real citation corpus** — large-scale real-world baseline

---

## Quick Links

| Resource | Location |
|----------|----------|
| Validator (browser) | `citation-validator.html` |
| Validator (CLI) | `scripts/citation_validator.py` |
| Heuristic enhancements | `scripts/citation_enhancements.py` |
| Test runner | `test_citations/run_all_tests.py` |
| Test data | `test_citations/` |
| Testing methodology | `test_citations/TEST_DESIGN.md` |
| Test infrastructure guide | `test_citations/README_TESTING.md` |
| Historical results | `test_citations/TESTING_SUMMARY.md` |
| Quick commands | `test_citations/COMMANDS.md` |
