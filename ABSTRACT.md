# Affordable Citation-Hallucination Detection: A Deterministic-First Approach

**Todd Grundmeier**
Ohio Journal of School Mathematics

---

## Why This Work Exists

In early 2026, Nature reported that 2–6% of recently published papers
contain fabricated citations — references that look plausible but point
to papers that do not exist.  These "hallucinated citations" are a
byproduct of large language models used in academic writing: the models
generate fluent-sounding references with invented authors, titles, and
DOIs.  Once published, these ghost references pollute citation networks,
corrupt meta-analyses, and undermine the trust infrastructure that
science depends on.

The existing responses to this problem share a common assumption: that
detecting fake citations requires expensive AI.  Commercial plagiarism
checkers are adding citation-verification features at institutional
subscription prices.  Research prototypes rely on large language models
to judge whether a citation "looks real."  These approaches work, but
they exclude the researchers, small journals, and independent reviewers
who most need protection — and who can least afford it.

This project asks a simple question: **how far can you get with free
APIs and no AI at all?**

## What We Built

The Citation Validator is an open-source tool that checks academic
references against public databases — CrossRef, OpenAlex, Semantic
Scholar, and arXiv — using only deterministic logic.  No machine
learning, no API keys, no subscription fees.  A reviewer pastes a
BibTeX bibliography into a web interface (or runs a command-line
script), and within minutes receives a per-citation verdict: *valid*,
*warning*, *suspicious*, or *invalid*.

The validation pipeline works in three tiers:

1. **DOI resolution.** If a citation includes a DOI, the tool resolves
   it through CrossRef (with DataCite and DOI.org fallbacks) and
   cross-checks the returned metadata — title, author, year — against
   the BibTeX entry.  A DOI that resolves to a different paper, or
   doesn't resolve at all, is strong evidence of fabrication.

2. **Database search.** Citations without DOIs are searched in OpenAlex
   (structured title filter) and Semantic Scholar (title search with
   author/year cross-validation).  If no matching record is found, the
   citation is marked *warning* (unverifiable) — not *suspicious*.
   This distinction is critical: many legitimate citations (arXiv
   preprints, non-English journals, older publications) are absent from
   these databases.  Absence of evidence is not evidence of fabrication.

3. **AI analysis (optional).** For users who want a second opinion, the
   tool can route suspicious citations through Gemini, GPT-4o, Claude,
   or Groq for AI-assisted judgment.  Gemini's free tier provides 1
   million tokens per day — enough to analyze approximately 1,500
   citations at zero cost.  But the deterministic tiers handle the vast
   majority of cases without AI.

## What We Found

### Code Audit

A thorough code review (by Claude Opus 4.6) of the ~6,000-line
codebase revealed six issues, three of them critical:

- The **confusion matrix was inverted**: true positives and true
  negatives were swapped, meaning all published accuracy metrics used
  non-standard definitions.
- Over **1,500 lines of dead code** (an abandoned browser-side
  validation pipeline) remained in production, including a
  contradictory AI prompt.
- The **escalation logic** treated "not found in any database" as
  evidence of fabrication, producing 100% false-positive rates on
  legitimate citations.

After fixes, the codebase shrank by 1,604 lines while gaining
correctness, tests, and a proper evaluation framework.

### False-Positive Baseline

We tested the deterministic pipeline (no AI) against 391 real citations
from three sources:

| Dataset | Citations | Source | FPR |
|---------|-----------|--------|-----|
| arXiv CS preprints (2024) | 285 | Extracted from 2 published papers | 0.0% |
| CrossRef random sample | 96 | CrossRef random-works API | 0.0% |
| Nature article bibliography | 10 | Manual entry | 0.0% |
| **Total** | **391** | | **0.0%** |

Zero real citations were incorrectly flagged as suspicious or invalid.
The Wilson 95% confidence interval is [0.0%, 0.96%] — we can claim less
than 1% false-positive rate with 95% confidence, but not exactly zero.

These results should be interpreted with appropriate caution.  The test
set is small (391 citations), heavily weighted toward computer science
preprints, and does not yet include books, dissertations, non-English
publications, or very old works.  The planned 10,000-citation validation
study will address these gaps.

### What Remains

- **Fake-citation recall:** The Ansari 100-fake dataset must be re-run
  to confirm the escalation fix did not weaken detection of actual
  fabrications.  Prior results showed 100% detection rate; we expect
  this to hold since the fix only changed how *unverifiable* citations
  are classified, not how *mismatched* or *non-existent* DOIs are
  handled.

- **AI comparison:** Running the same datasets with and without AI
  analysis will quantify whether AI improves precision, or whether the
  deterministic pipeline alone is sufficient.

- **Scale validation:** A 10,000-citation study with diverse,
  independently-sourced datasets is needed to confirm these results
  generalize beyond CS preprints.

## Why It Matters

Citation hallucination is a solvable problem, and solving it should not
require an institutional budget.  The databases that index legitimate
scholarship — CrossRef, OpenAlex, Semantic Scholar — are free and
public.  The logic to query them is straightforward.  The hardest part
turned out to be getting the epistemology right: understanding that a
citation absent from databases is *unverifiable*, not *fake*.

If these preliminary results hold at scale, they suggest that the
academic community already has the infrastructure to detect most
hallucinated citations — we just need to use it.  An open-source tool
running on free APIs, requiring no AI and no budget, could be deployed
by any journal, any reviewer, any researcher, anywhere.

That is the hypothesis this project is testing.
