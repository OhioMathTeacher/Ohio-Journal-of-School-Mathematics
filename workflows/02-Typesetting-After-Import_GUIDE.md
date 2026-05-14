# Typesetting After Import — Todd & GenAI

Use this when: The manuscript folder already exists in the repo and you’re ready to typeset.

Canonical doc: typesetting_process_todd_and_genai.md

Before diving in, verify the standard directories exist (create them if earlier passes omitted them):

- `Submissions/Original Submission/` for the latest author files and `Submissions/Metadata/` for cover notes
- `Deliverables/` for proof PDFs and `Reviews/` for editor communications
- `figures/` and `sections/` for assets and TeX chunks

## Inputs you should find before touching `main.tex`

- `Submissions/Metadata/metadata.png` (or similarly named PNG) — run Tesseract to OCR titles, author names, affiliations, issue info, and starting page. This becomes the source of truth for the front-matter commands.
- `Submissions/Metadata/abstract_keywords.txt` — Abstract copied from Janeway to avoid OCR errors
- Author biography `.txt` files inside `Submissions/Metadata/` named after each author; copy those into `sections/biography.tex` when adding bios and wrap them with the appropriate photo include.
- Author photos in `figures/` named with each last name (`lastname.png`).
- Article figures (`fig1.png`, `fig2.png`, …) and table images (`table1.png`, …) in `figures/` for drop-in placement.

## CRITICAL: Use PDF as Source of Truth for Content

**The submission PDF (not any .txt file) is the authoritative source for typesetting.**

- `.txt` files may contain earlier drafts, OCR errors, or incomplete revisions
- Always extract text from the PDF for typesetting: `pdftotext submission.pdf -`
- Cross-reference text file only for convenience, but verify any discrepancies against the PDF
- When in doubt about wording, paragraph order, or missing content: check the PDF

**Workflow for content migration:**
1. Extract section from PDF: `pdftotext -f [start_page] -l [end_page] submission.pdf -`
2. Typeset the content from PDF extraction
3. Compile and verify
4. Move to next section

## Transparency + "Always Compiles" philosophy

- Narrate progress in chat/logs so Todd can see exactly what changed, what's blocked, and what you plan next. If information is missing, stop and ask; never guess.
- Work in small slices (intro metadata, each section chunk, each figure/table placement, each pagination tweak). After every slice, run the LuaLaTeX task and glance at the PDF so we catch regressions immediately.
- When tackling floats/pagination, expect iterate → compile → review cycles. Document any compromises (e.g., forced float placement) in `Reviews/Notes` so the editorial record stays transparent.

## Special Character & Format Guards

**AI Disclosure in `\thanks{}`:**
- Search submission for AI acknowledgment statements (grep for "AI", "ChatGPT", "Copilot", "generative") before using generic template language
- Replace default `\thanks{}` text with author's actual disclosure if found

**Template Fixes (Before Typesetting):**
- Remove template text from `sections/references.tex` (starts with "Note that our citations...")
- Fix heading fonts: Remove `\sffamily` from `\titleformat` commands (headings should match body serif font)
- Fix tab characters: Search for `^\t` regex — tabs break `\titleformat` and `\title` commands (replace with backslash)

**LaTeX Special Characters (validate after migration):**
- Percent signs: Use `\%` (NOT `\textpercent` — encoding error)
- Ampersands in citations: Use `\&` (NOT `\\&` — no line breaks)
- Hash/pound: Use `\#`
- After migrating any section, grep for `\\\\\s*\\&` to catch accidental line breaks before ampersands

**Abstract/Keywords Format:**
- Keywords MUST be inside `\end{abstract}` (see template)
- Use `\\\\` and `\smallskip` for spacing before keywords line

What it covers:
- Phase-by-phase collaborative process (roles, timings)
- References formatting, figures, spacing, hyphenation
- Common pitfalls and quick fixes

Tip: Keep author-facing requests out of the TeX unless explicitly desired; use `Reviews/` and `Deliverables/`.

Cross-links:
- [00-Start-Here_PROCESS_CHECKLIST.md](00-Start-Here_PROCESS_CHECKLIST.md) — high-level flow
- [01-Intake-and-Setup_WORKFLOW.md](01-Intake-and-Setup_WORKFLOW.md) — scaffolding and directory creation
- [Typesetting_Verification_Checklist.md](Typesetting_Verification_Checklist.md) — QA before proofs go out
