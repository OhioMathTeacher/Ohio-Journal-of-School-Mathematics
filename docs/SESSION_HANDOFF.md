# Session Handoff — 2026-05-06 (web → local CLI)

**Purpose:** Bridge a multi-day Claude Code conversation from claude.ai/code (web sandbox) to Claude Code CLI on Todd's Fedora machine. The web conversation has detailed context that doesn't transfer automatically. Read this + `docs/paper2-plan.md` first.

---

## Who / where

- **User:** Todd Edwards, Miami University, OJSM editor.
- **Machine now:** ToddGPT, Fedora, local Claude Code CLI. Docker can run here. Java 21 likely already installed.
- **Repo:** `~/Repos/Ohio-Journal-of-School-Mathematics`. Branches `main` and `claude/revise-paper-feedback-e99AJ` are in sync as of handoff. Develop on the feature branch, merge ff-only to main, push both.
- **Note:** Todd is *not* in Vegas. Has not been for over a week. The earlier session summary had this wrong; ignore.

## Current mode

Hypomania-productive. Todd wants to keep momentum. Match the pace, don't pad responses, don't over-question. He's said "fucking install that stuff" — bias toward action when he's clearly green-lit something.

## Two papers in flight

### Paper 1 — methodology / tool announcement

- **Status:** Tier-1 revisions complete. Submission target: ~10 days from 2026-05-05.
- **Title direction:** *"Whose Writing Is This, Anyway?: Lessons from Building an Open-Source Citation Hallucination Detector"*
- **Tool live at:** `https://huggingface.co/spaces/ojsm/citation-validator` (lowercase `ojsm` — case matters)
- **Recent commits:** Voice → first-person singular, Wilson 95% CIs on rate claims, split conflated GhostCite/CiteAudit refs, Frankenstein subsection (§5.3) with Söderström example, acknowledgments section, methods URL fix, draft watermark.
- **Pending:** Venue selection (`docs/possible-venues.md`), cover letter, submit.

### Paper 2 — OJSM citation audit (this session's main thread)

- **Status:** Data collection complete. Manual triage in progress. Writing not started.
- **Plan:** `docs/paper2-plan.md` is the working scaffold. Read it.
- **Co-authors invited 2026-05-06:** Aslı Özgün-Koca (Wayne State), Michael Steele (UNC Charlotte). Friday call planned.
- **Anchor example:** Söderström & Palm in OJSM article 6569 (issue 362). Cited DOI `10.1080/14794802.2024.2444321` is fabricated; real DOI is `10.1080/14794802.2024.2401488`. Pages 1–23 cited, real pages 163–184. Already mentioned in Paper 1 §5.3.

## Triage state — 14 invalid-DOI candidates

App is `scripts/ojsm_triage_app.py`, runs at `localhost:5001`. Three-column layout: queue (left), workflow (center), sticky article-context panel (right). Verdicts saved to `datasets/ojsm-audit/triage_log.json` (file does not yet exist — created on first save).

**My eyeball estimate of the 14:** maybe half are real Frankensteins / hallucinations / typos, half are extraction artifacts (our regex over-merging across reference boundaries). Söderström (art 6569) is the only one mentally pre-classified — it's a confirmed `real_frankenstein`.

Triage hasn't started yet in the app. When Todd resumes, he just runs the app and walks through them.

## Live decision: GROBID setup

This is *why* Todd switched to local CLI. Web sandbox can't run Docker daemon (no systemd, init is `process_api`). Fedora can.

### The bug GROBID solves

`ojsm_extract.py` has two regex weaknesses:

1. **Line-rejoin over-merge** (the "Fagbohun" bug): `DOI_LINE_REJOIN_RE` joins a wrapped DOI with the next line's first chunk, but its continuation pattern `[A-Za-z0-9._\-/:]+` matches pure-alpha text like "Fagbohun" (next reference's author). Visible in art 6574: `10.51204/Anali_PFBU_24405A` got fused with `Fagbohun`.
2. **`trim_fused_author` boundary miss** for uppercase→Capital+lowercase transitions. Boundary regex needs `(?<=[A-Z])[A-Z][a-z]{2,}` added.

Quick regex tightening fixes both in 5 minutes. GROBID replaces the whole heuristic pipeline with a layout-aware ML parser. Todd wants to do GROBID now ("Come on! lol").

### GROBID setup plan (Fedora)

```bash
# Install Docker
sudo dnf install -y docker docker-compose
sudo systemctl start docker && sudo systemctl enable docker
sudo usermod -aG docker $USER   # log out/in to take effect, OR use sudo for docker commands tonight

# Pull GROBID (~3 GB, takes 5-10 min)
docker pull lfoppiano/grobid:0.8.1

# Run as service
docker run -d --rm -p 8070:8070 --name grobid lfoppiano/grobid:0.8.1

# Verify
curl http://localhost:8070/api/isalive   # should return: true
```

Then write `scripts/ojsm_extract_grobid.py` — replaces `ojsm_extract.py`'s pdftotext+regex with a GROBID client. GROBID's `processReferences` endpoint takes a PDF and returns TEI XML with `<biblStruct>` elements containing parsed authors/title/journal/DOI per reference. Re-run validate on the new `.bib` files; the candidate list should drop sharply because extraction artifacts disappear.

**Decision point Todd hasn't made yet:** does triage happen *before* GROBID re-extraction (so the artifact rate becomes a methodology footnote about pipeline reliability) or *after* (cleaner numbers, no artifact category needed)? My vote was triage-first; Todd may have a different view.

## Other open threads

- **Greg Foley** sent a file of references to test with the validator. Attachment not yet shared. Plan: Todd drops it into `test_citations/` or runs it through the HF Space himself, then results inform Paper 1 results section if interesting.
- **Andy Byers (Janeway dev)** replied warmly to Todd's outage email — added Anubis bot protection, shared Todd's kind words with Janeway team. Relationship is good. Future V103 pre-publication audit can lean on this.
- **V103 (Summer 2026) pre-pub audit** is the natural Paper 2 follow-up. Todd has Janeway admin access to pull unpublished PDFs.

## Key UX touches in the triage app (don't undo)

- Three-step color-coded layout: 🔴 Suspect / 🔵 Find / 🟢 Verdict.
- Reference paragraph is a fixed-window extraction (~280 chars before DOI, ~80 after). Earlier we tried year-anchored and capital-letter-anchored parsing; both failed on edge cases. Fixed window is "good enough for a human." Don't replace this with structural parsing unless GROBID is doing it end-to-end.
- Suspect DOI box is click-to-copy (yellow box).
- Step 2 has a textarea with Copy / Use English title (extracts bracketed APA translation) / Reset buttons, plus CrossRef-by-citation, Scholar, Google Translate links that update on every keystroke.
- All lookup buttons are unified gray (no blue "primary" — implied wrongly that one was the main action).
- All buttons have explanatory `title=` tooltips. Don't strip these.
- Right-side sticky panel shows article title, IDs, suspect DOI, reference paragraph — solves "I forget the article name when I tab to Scholar." Collapses below 1100px viewport.

## Useful artifacts to skim before resuming

- `docs/paper2-plan.md` — full Paper 2 scaffold
- `datasets/ojsm-audit/validation_summary.json` — the 14 candidates
- `paper/sections/discussion.tex` §5.3 — Frankenstein definition + Söderström
- `scripts/ojsm_extract.py` — extraction code with the fusion bugs
- `scripts/ojsm_triage_app.py` — the triage app

## Suggested first prompts for the local Claude

> *Read docs/SESSION_HANDOFF.md and docs/paper2-plan.md. We were mid-triage on the OJSM audit and switching to local CLI specifically to set up GROBID. Walk me through Docker install on Fedora, then GROBID, then we'll write the extractor.*

Or if Todd wants to triage first:

> *Read docs/SESSION_HANDOFF.md and docs/paper2-plan.md. I'm going to walk through the 14 triage candidates first. Just be ready to fix any UI annoyances I hit, and to write the GROBID extractor after.*
