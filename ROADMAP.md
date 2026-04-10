# Citation Validator — Roadmap
**Last updated:** April 10, 2026

---

## Production Readiness Checklist

### Phase 1: False Positive Baseline (NEXT - 30 minutes)

**Goal:** Establish precision metrics on real citations

- [ ] Run benchmark on 285 real arXiv citations
  ```bash
  python3 scripts/run_benchmark.py --dataset ojsm-real-arxiv --ai gemini
  ```
- [ ] Run benchmark on 100 real CrossRef citations
  ```bash
  python3 scripts/run_benchmark.py --dataset ojsm-real-crossref --ai gemini
  ```
- [ ] Analyze false positive rate (should be <5%)
- [ ] Document confidence threshold recommendations
- [ ] If FPR > 5%, investigate systematic patterns

**Success criteria:** FPR < 5% on real citations, understand what causes false alarms

---

### Phase 2: Large-Scale Robustness (2-3 hours dev time)

**Goal:** Enable 10K citation study without manual intervention

- [ ] Add checkpoint/resume to `run_benchmark.py`
  - Save progress every 100 citations
  - Resume from last checkpoint on restart
  - Store in `Test Results/checkpoints/`
- [ ] Add smart rate limit handling
  - Exponential backoff for 429 errors
  - Log rate limit events to experiment metadata
- [ ] Test checkpoint/resume on 1,000 citation run
- [ ] Document recovery procedures

**Success criteria:** Can recover from API failures or interruptions without data loss

---

### Phase 3: 10,000 Citation Study (7 days wall time, $0 cost)

**Goal:** Publication-quality dataset for Nature paper

**Study design:**
- 5,000 real citations (mix of disciplines, years)
- 5,000 fabricated citations (using Ansari taxonomy)
- Gemini free tier (1,500 citations/day)
- Full token tracking and timing data

**Execution:**
```bash
# Day 1-7: Run mixed dataset
python3 scripts/run_benchmark.py --dataset mixed-10k --ai gemini

# Analyze results
python3 scripts/cost_analysis.py --analyze-logs
```

**Data collection:**
- True positive/negative rates
- False positive/negative rates
- Confusion matrix
- Token usage (input/output per citation)
- API error rates
- Timing per validation pass
- Confidence score distributions

**Success criteria:** 
- 100% completion (all 10K citations processed)
- <5% false positive rate
- >95% true negative rate on fakes
- Publication-ready JSON + CSV exports

---

### Phase 4: External Validation (1-2 weeks)

**Goal:** Compare our results to published research

- [ ] Integrate Rao & Callison-Burch 931-paper benchmark
  - Convert their data format to our manifest structure
  - Run through our validator
  - Compare field-level accuracy
- [ ] Run CheckIfExist comparison
  - Same 10K dataset through both tools
  - Document differences in detection rates
  - Analyze where approaches diverge
- [ ] Test on HalluCitation dataset
  - If Sakai et al. release their 275-paper list
  - ACL/NAACL/EMNLP specific validation

**Success criteria:** Our tool performs comparably to or better than existing solutions

---

## Nature Paper Outline

### Abstract (200 words)
- Problem: 2-6% of papers contain AI hallucinations
- Gap: Existing tools expensive or closed-source
- Solution: Free, open-source validator with $0 operating cost
- Results: 10K citation study, X% detection rate, <Y% FPR
- Impact: Accessible to researchers without institutional AI budgets

### Introduction
- Rise of LLM usage in academic writing
- Recent studies documenting hallucination rates
- Need for accessible validation tools
- Our contribution: "research for the rest of us"

### Methods
**Three-tier validation pipeline:**
1. Deterministic checks (DOI validation, database lookups)
2. Heuristic pattern detection (8 categories)
3. AI analysis (optional, provider-agnostic)

**Cost economics:**
- Token tracking methodology
- Gemini free tier vs. paid providers
- Cost projections for different scales

**Test design:**
- 5,000 real citations (description of sampling)
- 5,000 fabricated citations (Ansari taxonomy)
- Ground truth labeling methodology
- Evaluation metrics (precision, recall, F1)

### Results
**Detection accuracy:**
- True positive rate: X%
- False positive rate: <5%
- Confusion matrix
- Comparison to published benchmarks

**Cost analysis:**
- Total tokens: X million
- Cost: $0 (Gemini free tier)
- Time: 7 days wall time
- Cost comparison to alternatives

**Provider comparison:**
- Gemini vs. Groq vs. OpenAI vs. Anthropic
- Token usage per citation
- Accuracy differences
- Rate limit experiences

### Discussion
- Implications for journal editors
- Recommendations for pre-submission checks
- Limitations of automated detection
- False positive handling strategies
- Future work: browser extensions, editorial integration

### Conclusion
- Free tools democratize academic quality control
- Large-scale validation feasible without grants
- Call for open-source solutions
- Code, data, and results publicly available

---

## Future Features (Post-Publication)

### User Interface Enhancements
- **Benchmark library panel** in web app
  - Load datasets from manifest with one click
  - Mix and combine datasets
  - Filter by type, year, discipline
- **Challenge mode**
  - Load mixed real+fake set with labels hidden
  - User flags suspicious citations before running validator
  - Compare human vs. machine results
- **Comparison dashboard**
  - Side-by-side run comparisons
  - Visualize accuracy improvements over time
  - Provider performance charts

### Integration
- **Browser extension**
  - Right-click BibTeX → validate
  - Inline results in Google Scholar
  - Export to Zotero/Mendeley
- **CI/CD hooks**
  - GitHub Action for pull request checks
  - Pre-commit hook for LaTeX repositories
  - Overleaf integration (if possible)

### Analysis Tools
- **Confidence calibration study**
  - Do high-confidence AI calls correlate with accuracy?
  - Optimal threshold recommendations
  - Provider-specific calibration
- **Systematic FP analysis**
  - What citation patterns trigger false positives?
  - Edge case collection (DataCite, pre-DOI era, non-English)
  - Heuristic refinement based on patterns

### Scale-Up
- **Million-citation study**
  - Requires paid Gemini tier or distributed approach
  - Random sample of all 2025 publications
  - Estimate total hallucination count across academia
- **Longitudinal tracking**
  - Quarterly benchmarks on new conference proceedings
  - Track hallucination rate trends over time
  - Measure LLM improvement (if hallucinations decrease)

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| False positive testing | 30 min | None |
| Checkpoint/resume dev | 2-3 hours | None |
| 10K study execution | 7 days | Gemini API key |
| External validation | 1-2 weeks | Benchmark datasets |
| Nature paper draft | 2-3 weeks | All data collected |
| Revisions & submission | 1-2 months | Review feedback |

**Total to submission:** 2-3 months from today (early-mid June 2026)

---

## Open Questions

1. **Optimal confidence threshold?**
   - What AI confidence score should trigger human review?
   - Does this vary by provider or fabrication type?

2. **How to handle edge cases?**
   - DataCite DOIs for datasets
   - Pre-1990s papers (before DOIs existed)
   - Non-English citations
   - Grey literature (theses, reports, preprints)

3. **What's the right mix for 10K study?**
   - 50/50 real/fake?
   - Match Nature's 2-6% ratio (940 fakes, 9060 real)?
   - Stratify by discipline?

4. **How to validate OpenAlex matches?**
   - Current threshold = 0.5 Jaccard similarity
   - Should this vary by field length?
   - How often does this cause FPs?

5. **Which external benchmark first?**
   - Rao (most rigorous, field-level ground truth)
   - Ansari (already integrated, easy comparison)
   - HalluCitation (real-world ACL/NAACL/EMNLP data)

---

## Success Metrics

### Technical
- [ ] <5% false positive rate on real citations
- [ ] >95% true negative rate on fabricated citations
- [ ] 100% of 10K study completed without manual intervention
- [ ] All experiment data reproducible from JSONL logs

### Academic
- [ ] Nature submission accepted
- [ ] Tool cited by other hallucination researchers
- [ ] Adopted by at least one journal for pre-publication checks
- [ ] GitHub repo gets 100+ stars

### Impact
- [ ] "Research for the rest of us" philosophy validated
- [ ] Other researchers publish cost-effective replication studies
- [ ] Tool used in graduate seminars for teaching research ethics
- [ ] Extension to non-academic fact-checking (journalism, policy)
