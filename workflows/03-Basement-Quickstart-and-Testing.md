# Basement quickstart: testing Selmer and wrapping Zhu

Use this one-pager to pull the latest, run the editorial scaffold test on Selmer, and advance Zhu to send.

## TL;DR
- Pull master on the basement machine.
- In VS Code, run the task: “Editorial: Scaffold Review & Letter”.
  - For a safe test, target: 6616 Selmer, decision: minor, editor: Todd, include memo.
- Verify the created artifacts (Selmer):
  - 6616 Selmer/Deliverables/6616 Selmer Feedback OJSM.md (review)
  - 6616 Selmer/Reviews/6616-Selmer_Letter_YYYY-MM-DD.md (letter stub)
  - 6616 Selmer/Deliverables/6616-Selmer_Internal_Editor_Memo_YYYY-MM-DD.md (memo)
- For Zhu, choose the send path (minor revisions) and send the letter that references the one‑pager.

## Detailed steps

### 1) Sync the repo
- Ensure you’re on master and pull the latest.
- If you want a scratch branch for testing, create one before testing (optional).

### 2) Run the editorial scaffold (Selmer test)
- Open the Command Palette → “Run Task” → “Editorial: Scaffold Review & Letter”.
- When prompted:
  - Manuscript: 6616 Selmer
  - Decision: minor
  - Editor: Todd
  - Include memo: yes (optional)
- Check the output files in Selmer’s Deliverables and Reviews.
- These can be safely deleted later; they don’t affect TeX builds.

### 3) Zhu next steps
- Build check: 6617 Zhu compiles with LuaLaTeX (latexmk task available).
- Author artifacts ready in `6617 Zhu/Deliverables` and letter in `6617 Zhu/Reviews`.
- Remaining action: confirm the “minor revisions” send path and dispatch the letter referencing the one‑pager.
- Track a 10‑day return window; on return, integrate mini example, quick‑start steps, and first‑use definitions.

## Handy links
- 00-Start-Here_PROCESS_CHECKLIST.md
- 01-Intake-and-Setup_WORKFLOW.md
- 02-Typesetting-After-Import_GUIDE.md
- PROCESS_CHECKLIST.md
- WORKFLOW.md
- typesetting_process_todd_and_genai.md
