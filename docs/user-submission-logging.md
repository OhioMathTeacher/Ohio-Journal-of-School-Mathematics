# Future feature: Log user-submitted references for research

**Status:** Idea, not yet implemented. Captured 2026-05-06 to avoid losing it.

**Where it would live:** Citation Validator tool (HF Space `ojsm/citation-validator`).

---

## The idea

Capture references submitted to the public validator (with opt-out consent) as a growing real-world dataset of citation strings — including the tool's verdicts. Use the corpus to:

- Improve detection: real submissions surface edge cases that synthetic benchmarks miss (regional journals, non-English sources, weird formatting, novel hallucination patterns).
- Build a public benchmark dataset of curated Frankenstein examples — itself a research contribution.
- Direct future development by seeing which patterns stump the tool in the wild.
- Add empirical weight to follow-up papers beyond the OJSM-only audit.

## Why it's worth doing

- The validator already ingests references; the marginal cost of *retaining* them is small.
- Real user submissions are more valuable than synthetic benchmarks for the long-tail problem.
- Curated Frankensteins from real submissions become citable evidence in policy arguments.

## What to think through before turning it on

### 1. IRB

This is the one to settle *first*. Collecting reference data from human users (even anonymously) for the purpose of publishing research findings probably qualifies as human-subjects research at Miami. Likely outcome: exempt or expedited review, but ask the IRB office before turning logging on. Retroactive approval is much harder than asking first.

**Action:** Email Miami's IRB office with a one-paragraph description: tool, what's logged, opt-out mechanism, planned use. Ask whether this qualifies for exempt review.

### 2. Consent UX

User suggested an opt-out checkbox: *"Help improve the tool by allowing your submissions to be used in research,"* default-checked, near the input field, with a "learn more" link.

Tradeoffs:
- **Opt-out (default checked)** — matches user expectations for research-tool audiences; lower friction; defensible for non-sensitive data (reference strings, not PII).
- **Opt-in (default unchecked)** — IRBs often prefer this for research data collection; weaker consent argument with opt-out; some users won't notice.

Likely-good design:
- Opt-out for *aggregate* tool-improvement use.
- Separate opt-in checkbox (default unchecked) for *"OK if individual examples appear in a public benchmark dataset."*
- Both states logged alongside each submission.
- Defer to whatever the IRB says; document the decision either way.

### 3. What to log

- The reference string(s) and the tool's verdict.
- The consent state at time of submission.
- A timestamp.
- **Not:** IP address, session data, browser fingerprint, anything that ties a submission to a person.

### 4. What to *not* log

If a user unchecks the box, the submission isn't retained at all — not "retained but flagged do-not-use." Cleaner, easier to defend.

### 5. Storage

HF Space filesystems are ephemeral (rebuilds wipe them). Need persistent storage outside the Space:
- Lightweight option: append-only JSONL pushed to a private GitHub-controlled repo or HF Dataset.
- Heavier option: managed database (Supabase, Turso, plain Postgres). Probably overkill for v1.
- v1 recommendation: HF Dataset (private, owned by `ojsm` user), JSONL append, daily sync from the Space.

### 6. Curation workflow

Periodic (weekly? monthly?) review pass:
- Filter out anything potentially identifying — e.g., someone testing their own unpublished manuscript's references.
- Sanitize edge cases that look like personal/private documents.
- Tag interesting examples for the benchmark set.
- Anything published from this corpus needs the tag to indicate the user opted in to public-benchmark use.

### 7. Disclosure on the tool

Required regardless of consent model:
- Banner near input: *"Submissions may be retained (with your consent) to improve the tool and support published research. No personal information is collected."*
- Link to a short data-use page describing what's logged, what isn't, and how to request deletion.
- HF Space description text mentions data use.

## Risks / things that could go wrong

- **Researcher tests their own unpublished references** — corpus contains pre-publication material. Mitigated by curation pass + opt-out + explicit second checkbox for public-benchmark use.
- **Submission contains author personal info** — references shouldn't, but free-text input mode could (e.g., a copy-pasted draft with track-changes comments). Curation should strip these.
- **GDPR / Miami data-protection rules** — anonymous reference strings are low-risk but worth confirming with IRB / general counsel.
- **HF Space TOS** — verify HF allows research data collection in Spaces (it does, but review the terms).

## Implementation outline (when ready)

1. IRB conversation. Wait for approval.
2. Add consent UI to the validator HTML.
3. Wire up the Flask backend to write JSONL when consent is granted.
4. Set up persistent storage (HF Dataset).
5. Daily sync job (cron or on-submission push).
6. Curation script: read JSONL, output a flagged subset for human review.
7. First curation pass after ~100 submissions to validate the workflow.
8. Decide on benchmark-dataset release schedule (annual? per-paper?).

## Connection to existing papers

- **Paper 1 (methodology):** mention the planned data-collection program as future work; cite no submitted data yet.
- **Paper 2 (OJSM audit):** independent; user-submitted data not part of this corpus.
- **Future Paper 3:** the user-submission corpus as the primary dataset, once it's large enough and IRB-approved.
