# Intake and Setup — Workflow (Before Repo)

Use this when: You’re preparing new manuscripts for inclusion in the VS Code repo.

Canonical doc: WORKFLOW.md

What it covers:
- Scrubbing for blind review (metadata/PII)
- Creating the manuscript directory with scripts
- First build sanity checks

## Standard directory scaffold

Whether you use the scaffolding script or create things manually, confirm the following structure exists before handing the folder to typesetting:

- `figures/` and `sections/` for assets and TeX chunks
- `Submissions/Original Submission/` (latest DOCX/PDF/TXT lives here) and `Submissions/Metadata/` for cover letters, decision notes, etc.
- `Deliverables/` for outgoing proof PDFs and `Reviews/` for editor/author letters and memos

If an older folder still has `Original Submission/` at the top level, move it into `Submissions/Original Submission/` so every manuscript matches the same pattern.

## What to drop into `Submissions/Metadata/`

- **Janeway metadata screenshot:** Capture the manuscript’s metadata screen as a PNG and place it here (e.g., `metadata.png`). During typesetting we run Tesseract against that image to extract titles, author spelling, affiliations, issue, and start page without retyping.- **Abstract text file:** Copy the abstract from Janeway and save it as `abstract.txt`. This avoids OCR errors and ensures the abstract matches exactly what was submitted.- **Biographical text files:** Provide one plain-text file per author named with the author’s last name or author index (e.g., `johnson.txt`, `author2.txt`). Each file should contain the 2–3 sentence bio we’ll flow into `sections/biography.tex`.
- **Any supplemental notes:** Use additional `.txt` files for decision notes or reminders the typesetting pass needs to see.

## Figures, author photos, and tables

- Place author headshots inside `figures/`, naming each file with the author’s last name (e.g., `johnson.png`).
- Place article figures in `figures/` as well, using sequential names (`fig1.png`, `fig2.png`, …).
- Place table renderings/screenshots as needed and name them `table1.png`, `table2.png`, etc. (If a table will stay in LaTeX form, that still lives in the appropriate `sections/` file.)

## Cross-links

- [00-Start-Here_PROCESS_CHECKLIST.md](00-Start-Here_PROCESS_CHECKLIST.md) — 10-step overview and quick reminders
- [02-Typesetting-After-Import_GUIDE.md](02-Typesetting-After-Import_GUIDE.md) — what happens once the folder is ready

Next step: Move to 02-Typesetting-After-Import_GUIDE.md once the manuscript folder exists in the repo.
