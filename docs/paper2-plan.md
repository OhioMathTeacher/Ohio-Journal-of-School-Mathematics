# Paper 2 — OJSM Citation Audit

**Working title:** *Frankenstein Citations in a Small Math-Education Journal: Auditing Nine Years of OJSM Back Issues*

**Status:** Data collection complete; manual triage in progress; writing not yet started.

**Last updated:** 2026-05-06

---

## What this paper is

An empirical, editorial-policy paper. Paper 1 introduces the citation-validation methodology (the tool and how it works). Paper 2 *applies* the methodology to a real corpus — every DOI-bearing reference in nine years of *Ohio Journal of School Mathematics* — and uses the findings to argue for a concrete editorial policy that small society journals can adopt at submission time.

It is **not** a methodology paper (Paper 1 already is). It is **not** a tool announcement. It is a small-journal case study with a policy recommendation grounded in the data.

## Co-authors (planned)

- **Todd Edwards** (Miami University) — first author, ran the audit, owns the editorial-policy framing as OJSM editor.
- **Aslı Özgün-Koca** (Wayne State University) — invited 2026-05-06. Long-time collaborator, OSU PhD.
- **Michael Steele** (UNC Charlotte) — invited 2026-05-06. Long-time collaborator, OSU PhD.

Asli and Michael's invitation framed them as Paper 2 co-authors and Paper 1 friendly readers. Both bring editorial experience the audit-policy story benefits from.

## Research questions

1. **How many fabricated DOIs appear in OJSM's published record?** (Prevalence — baseline rate per year, per article.)
2. **What proportion of fabrications are *Frankenstein citations* (real paper, fake DOI) vs. pure hallucinations (paper does not exist)?** (Taxonomy — these have different detection signatures and different editorial implications.)
3. **Has the rate changed since the introduction of widely-available LLMs (≈Nov 2022)?** (Time-series — does the data show an AI-era inflection?)
4. **What submission-time editorial policy would have caught these before publication?** (Policy — concrete recommendations for small society journals.)

## Dataset (current state, 2026-05-06)

| Metric | Count |
|---|---|
| Articles in inventory | 210 |
| Articles with PDF on disk | 209 |
| Articles with extractable references section | TBD (see `extract_summary.json`) |
| DOI-bearing references extracted | 249 |
| References with valid DOI in CrossRef | 235 |
| References with **invalid** DOI (Frankenstein candidates) | 14 |
| Articles contributing to validation pool | 64 |
| Confirmed real Frankensteins (post-triage) | TBD |
| Confirmed pure hallucinations (post-triage) | TBD |
| Extraction artifacts (pipeline error, not author error) | TBD |

**Coverage caveat:** Only ~15% of OJSM references include a DOI. Books, theses, NCTM publications, and state-DOE documents are common in math-education writing and dominate the non-DOI tail. This paper's claims are explicitly restricted to **DOI-bearing references**. Title-search validation for non-DOI refs (via Anystyle or a CrossRef title-match step) is future work.

## Pipeline (scripts/ojsm_*.py)

1. `ojsm_inventory.py` — walks Janeway sitemap, builds `inventory.json`
2. `ojsm_download.py` — fetches each article PDF
3. `ojsm_extract.py` — pdftotext + DOI regex → per-article `.bib`
4. `ojsm_validate.py` — runs each `.bib` through CitationValidator, aggregates
5. `ojsm_triage_app.py` — Flask UI for manually classifying each invalid candidate

**Known extraction limitations** (relevant to Methods section):
- DOI line-rejoin regex over-merges across reference boundaries when next-line author names start with letters (the "Fagbohun" bug, art 6574).
- `trim_fused_author` boundary detector misses uppercase→Capital+lowercase transitions.
- Approximately N/14 of the invalid-DOI hits are extraction artifacts rather than author errors. The exact N drops out of triage.

These are documented honestly in the paper as methodology limitations. A subsequent revision cycle plans to replace the regex pipeline with Anystyle or GROBID; the current results are presented as a lower bound on detectable problems.

## Confirmed example (anchor for the paper)

**Article 6569** (issue 362, 2026): Söderström & Palm reference.

- Cited DOI: `10.1080/14794802.2024.2444321` (does not resolve)
- Real DOI: `10.1080/14794802.2024.2401488`
- Cited pages: 1–23. Real pages: 163–184. (Off by an order of magnitude — not a transcription typo.)
- Authors, title, journal correct.

This is the prototypical Frankenstein and matches §5.3 of Paper 1.

## Methodology (planned section structure)

1. **Corpus** — OJSM 2017–2026, n articles, sourced from Janeway sitemap.
2. **Extraction** — pdftotext + heuristic reference-section detection + DOI regex. Honest about extraction reliability (the N/14 artifact rate).
3. **Validation** — CrossRef + DOI resolver via the open-source citation-validator tool (Paper 1).
4. **Manual triage** — every invalid candidate classified by a human reviewer into: `real_frankenstein`, `pure_hallucination`, `transcription_typo`, `extraction_artifact`, `unsure`. Triage tool: `scripts/ojsm_triage_app.py`. Inter-rater reliability *if Asli or Michael also triages a sample* — worth doing for ~3 candidates each as a methodological flourish.
5. **Time-series** — group by article publication year; report rates pre- and post-Nov 2022.

## Findings (placeholders — fill in post-triage)

- Frankenstein rate per 100 DOI-bearing references: TBD
- Pure hallucination rate: TBD
- Pre-2023 vs. post-2023 comparison: TBD
- Year of first detected Frankenstein in OJSM: TBD

## Editorial-policy recommendations (draft outline)

- **Submission-time DOI validation.** Every DOI in the manuscript bibliography must resolve in CrossRef before peer review begins. Tool: the open-source validator from Paper 1, or any equivalent.
- **Page-number cross-check** for journal-article citations. CrossRef returns the canonical pagination; mismatches flag for review.
- **Author disclosure of AI assistance** in citation drafting. Not prohibitive — disclosive.
- **Editor-side spot-check on accepted manuscripts.** A 5-minute final-pass before typesetting.

These are framed as low-cost, high-yield. The paper is not arguing for full reproducibility audits; it is arguing for a 5-minute submission filter that catches the Söderström pattern.

## Pre-publication audit (V103 follow-up)

Todd has Janeway admin access and can pull unpublished V103 PDFs. Running the same pipeline pre-publication is a natural follow-up section: *"Applying the audit prospectively, we found N issues in M submissions for V103 — corrected before press time."* Ideally this happens before the paper goes to review so it can be reported in-paper rather than as future work.

## Target venues (initial brainstorm)

- *Journal of Scholarly Publishing* — fits the editorial-policy angle.
- *Learned Publishing* — practitioner audience, scholarly-comms readership.
- *Mathematics Teacher Educator* (NCTM) — discipline-aligned, but less editorial-policy focused.
- *Research Integrity and Peer Review* (BMC) — open access, fits the integrity framing.

Decision: defer until first draft exists.

## Open questions (Todd, Asli, Michael — discuss on Friday)

- Do we want to anonymize OJSM in the paper, or name it directly? (My instinct: name it. The audit is OJSM's because Todd is the editor; that's the story.)
- Do we contact authors of Frankenstein-citing articles before publication, or after? (Ethical question; affects framing.)
- Single-author manuscripts vs. multi-author — is the rate different? Worth checking if N permits.
- Do we want a comparison corpus (e.g., a similar small math-ed journal) or stay single-journal?

## Next steps

1. **Finish triage of all 14 candidates** in the triage app. (In progress, 2026-05-06.)
2. **Tighten extract regex** to drop false candidates from the artifact bucket — clean numbers for the Methods section.
3. **Run V103 pre-publication audit** once Todd pulls the unpublished PDFs.
4. **Draft Methods + Findings sections** in `paper2/sections/` once triage numbers settle.
5. **Send paper2-plan.md to Asli and Michael** as a working scaffold ahead of the Friday call.
