# Citation Validator — Research Roadmap

**Last updated:** April 10, 2026
**Status:** Phase 1 complete.  Phase 2 in progress.

---

## What's Done

### Phase 1: Foundation (COMPLETE)

- [x] Code audit: 6 issues found and fixed (3 critical)
- [x] Confusion matrix corrected (TP/TN were swapped)
- [x] 1,556 lines of dead code removed
- [x] Escalation logic fixed ("not found" = warning, not suspicious)
- [x] Test suite: 19 tests passing (`pytest tests/`)
- [x] False-positive baseline: **0/391 = 0.0% FPR**
  - 285 arXiv CS preprints: 0.0%
  - 96 CrossRef random sample: 0.0%
  - 10 Nature article refs: 0.0%
- [x] RESEARCH_LOG.md with full methodology
- [x] ABSTRACT.md with motivation, ironies, and preliminary results
- [x] README.md rewritten for public audience

---

## What's Next — Critical Path

These are the minimum steps required before the work can be
scrutinized.  Each step includes the exact commands to run.  All steps
can be done locally in VS Code with a terminal.

### Step 2A: Fake-Citation Regression Test (URGENT)

**Why:** The README claims "100/100 fakes detected" but this was
measured BEFORE the escalation fix.  We must re-verify.

**What to do:**

```bash
# No Flask server needed — runs validator directly
python3 scripts/run_fp_baseline.py --step 4
```

This runs 5 fake-citation datasets (Ansari 100, Frankenstein,
Stolen DOI, Plausible, Nonsense) through the deterministic validator.
Every fake that is NOT flagged is a false negative.

**Expected result:** Near 100% detection on Ansari and Stolen DOI.
Plausible fakes (no DOI, no database match) may land at `warning`
rather than `suspicious` — this is the trade-off from the escalation
fix and is expected.

**If Ansari detection drops below 100%:** Investigate which fakes
slipped through and why.  The escalation fix only changed how
*unverifiable* citations are classified.  Fakes with non-existent
DOIs or title mismatches should still be flagged.

**Save the output** — paste it into RESEARCH_LOG.md under a new
section: "## 2026-04-XX — Fake-Citation Regression Test".

---

### Step 2B: AI Comparison (Deterministic vs. Gemini)

**Why:** The project's thesis is that deterministic checks are
sufficient.  We need data to support or refute that claim.

**Prerequisites:**
- Free Gemini API key from https://aistudio.google.com/app/apikey
- Set environment variable: `export GEMINI_API_KEY=your_key_here`
- Flask server running (`python3 scripts/webapp.py`)

**What to do:**

```bash
# Run the same datasets WITH AI (Gemini)
python3 scripts/run_benchmark.py --dataset ojsm-real-arxiv --provider gemini
python3 scripts/run_benchmark.py --dataset ojsm-real-crossref --provider gemini
python3 scripts/run_benchmark.py --dataset ansari100 --provider gemini
```

**What to compare:**
- Does AI change the FPR on real citations? (If it goes up, AI hurts.)
- Does AI change the detection rate on fakes? (If it goes up, AI helps.)
- How much time/cost does AI add per citation?

**Log results** in RESEARCH_LOG.md under: "## 2026-04-XX — AI
Comparison (Deterministic vs. Gemini)".

---

### Step 2C: At Least One Non-CS Dataset

**Why:** 285/391 of our real citations are CS preprints.  A reviewer
will immediately ask: "does this generalize?"

**Options (easiest first):**

1. **Expand CrossRef random sample** — our existing script pulls random
   works from CrossRef.  Get 200–500 more from diverse fields.
   ```bash
   # The script that generated the original sample is in
   # test_citations/real_citations/crossref_random/
   # Expand it to 500 citations across disciplines.
   ```

2. **Add a social science / humanities dataset** — manually extract
   references from a published paper in education, psychology, or
   similar.

3. **Add a biomedical dataset** — pull from PubMed/Europe PMC, which
   have excellent DOI coverage.

**Target:** At least 500 additional real citations from non-CS fields.
Run through the FP baseline and confirm 0% FPR holds.

---

### Step 2D: Update Claims and Numbers

**Why:** After Steps 2A–2C, update all documents to reflect verified
results only.

- [ ] RESEARCH_LOG.md: new sections for each experiment
- [ ] ABSTRACT.md: update results table, add AI comparison findings
- [ ] README.md: update metrics badges, results section
- [ ] Commit and push everything

---

## Phase 3: Scale and External Validation

These steps strengthen the paper but are not strictly required for an
initial credible response.

### 10,000-Citation Study

**Design:**
- 5,000 real citations (diverse fields, years, types)
- 5,000 fabricated citations (multiple deception strategies)
- Run deterministic + AI (Gemini free tier)
- 7 days wall time at ~1,500 citations/day

**Prerequisites:**
- Checkpoint/resume capability (needs development)
- Larger, curated dataset collection
- Gemini API key

### External Benchmark Comparison

- Rao & Callison-Burch 931-paper benchmark (if dataset available)
- CheckIfExist comparison (run same data through both tools)
- HalluCitation dataset from Sakai et al. (if released)

### Independent Validation

- Have someone else run the tool on their own data
- Ideally a journal editor testing on real submissions

---

## What You Can Say Now vs. After Each Step

| Claim | Now | After 2A | After 2B | After 2C | After Phase 3 |
|-------|-----|----------|----------|----------|----------------|
| "0% FPR on 391 real citations" | YES | YES | YES | Update N | Update N |
| "100% detection on 100 fakes" | NO (unverified) | YES or revised | YES or revised | Same | Update N |
| "Deterministic is sufficient" | Hypothesis | Same | YES or NO | Same | Confirmed |
| "Generalizes beyond CS" | NO | NO | NO | Preliminary | YES |
| "Works at scale" | NO | NO | NO | NO | YES |

---

## Environment Notes for VS Code

All experiments run locally.  Requirements:

```bash
# One-time setup
pip install -r scripts/requirements.txt

# For deterministic-only tests (Steps 2A, 2C)
# No API keys needed, no Flask server needed for run_fp_baseline.py
python3 scripts/run_fp_baseline.py --step 1

# For AI tests (Step 2B) and run_benchmark.py
# Need Flask server + API key
python3 scripts/webapp.py  # Terminal 1
export GEMINI_API_KEY=...  # Terminal 2
python3 scripts/run_benchmark.py --dataset ansari100 --provider gemini
```

VS Code with Claude can:
- Run terminal commands
- Edit files
- Read output and analyze results
- Update documentation

Limitation: VS Code Claude has a smaller context window than this
session.  If you need to brief it on the project, point it to
RESEARCH_LOG.md and this ROADMAP.md — they contain everything it needs.

---

## Timeline Estimate

| Step | Time | Priority |
|------|------|----------|
| 2A: Fake regression test | 15 minutes | **Do first** |
| 2B: AI comparison | 1–2 hours | High |
| 2C: Non-CS dataset | 1–2 hours | High |
| 2D: Update docs | 30 minutes | After 2A–2C |
| Phase 3: 10K study | 7+ days | After Phase 2 |

**Minimum credible result:** Steps 2A + 2B + 2D = ~2 hours of work.
After that, you have two verified numbers (FPR and detection rate), a
tested thesis (deterministic vs. AI), and honest documentation.
