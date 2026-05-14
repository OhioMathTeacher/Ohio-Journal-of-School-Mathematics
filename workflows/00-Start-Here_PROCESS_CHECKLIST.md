# Start Here — OJSM Processing (Quick Checklist)

Use this when: You need the short, day-to-day steps for processing any manuscript.

Canonical doc: PROCESS_CHECKLIST.md

- Intake/scrub → Setup → Configure main.tex → Migrate content → Figures → First build → Format refs → Polish → Editorial artifacts → Finalize → Integrate author changes
- During intake/setup, ensure the standard manuscript directories exist (create them if missing):
	- `figures/`, `sections/`
	- `Submissions/Original Submission/` (holds the latest DOCX/PDF/TXT) and `Submissions/Metadata/`
	- `Deliverables/` for proof PDFs and `Reviews/` for letters/memos
- Submissions conventions:
	- Drop the Janeway metadata screenshot PNG into `Submissions/Metadata/` for OCR (Tesseract) when configuring `main.tex`.
	- Store one plain-text bio per author (`lastname.txt`) alongside the screenshot.
	- Keep author photos in `figures/` using the author’s last name; article figures and tables use `figN.png`/`tableN.png` naming.
- Transparency & flow: narrate each step, surface decisions in `Reviews/` notes, and pause whenever context is missing instead of guessing.
- Always-compiles mindset: typeset in small chunks (especially figures/tables/pagination fixes) and run LuaLaTeX after each chunk so the PDF reflects every change.

See also:
- [01-Intake-and-Setup_WORKFLOW.md](01-Intake-and-Setup_WORKFLOW.md) — scrub + scaffolding scripts and directory creation
- [01b-Desk-Decisions_WORKFLOW.md](01b-Desk-Decisions_WORKFLOW.md) — desk accept/reject decisions (skip peer review when appropriate)
- [02-Typesetting-After-Import_GUIDE.md](02-Typesetting-After-Import_GUIDE.md) — collaborative typesetting once the folder exists
- [04-Revision-Evaluation_PROCESS.md](04-Revision-Evaluation_PROCESS.md) — evaluating author revisions after review
- [Typesetting_Verification_Checklist.md](Typesetting_Verification_Checklist.md) — QA pass before sending proofs
