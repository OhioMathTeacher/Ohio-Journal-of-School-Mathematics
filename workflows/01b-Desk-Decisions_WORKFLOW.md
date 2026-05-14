# Desk Decisions — Editorial Accept & Reject Workflow

Use this when: You've received a new submission and need to decide whether to (a) accept without peer review, (b) reject without peer review, or (c) send to reviewers.

Canonical doc: DESK_DECISIONS.md

## What Are Desk Decisions?

**Desk decisions** are editorial determinations made before (or instead of) formal peer review. They allow the editor to:

- **Desk Accept:** Accept strong, complete manuscripts that clearly fit OJSM's mission and need only minor editorial polish
- **Desk Reject:** Decline manuscripts that are clearly outside scope, incomplete, or not salvageable with revision
- **Send to Review:** Route manuscripts that need expert evaluation to peer reviewers

Desk decisions save reviewer time for manuscripts where the outcome is clear, and speed publication for high-quality submissions.

---

## Decision Criteria

### Desk Accept Criteria (all must be true)

1. **Complete:** The manuscript is finished—no missing sections, figures, or arguments
2. **Clear fit:** Obviously within OJSM's scope (mathematics education, teaching practice, classroom applications)
3. **Well-written:** Readable, organized, minimal editing needed
4. **Low risk:** Content is straightforward (teaching tips, practitioner articles, mathematical expositions)
5. **No red flags:** No ethical concerns, plagiarism indicators, or problematic claims

**Good candidates for desk accept:**
- Teaching Tips with complete activities/templates
- Short mathematical expositions (Proof Without Words, elegant derivations)
- Practitioner articles with clear classroom applications
- Well-executed adaptations of known instructional routines

### Desk Reject Criteria (any may be sufficient)

1. **Out of scope:** Not about mathematics education (pure research math, computational science, etc.)
2. **Incomplete:** Missing critical sections, data, or evidence for claims made
3. **Unfixable quality issues:** Writing quality too poor to salvage with revision
4. **Wrong audience:** Clearly written for a different journal or readership
5. **Ethical concerns:** Plagiarism, fabricated data, undisclosed conflicts

**Common desk reject scenarios:**
- Computational/pure math papers with no education connection
- Papers making strong claims without supporting evidence
- Manuscripts requiring complete rewriting rather than revision
- Student papers that show promise but need significant development

### Send to Review (when in doubt)

If the manuscript:
- Could go either way on quality/fit
- Makes claims requiring expert verification
- Addresses controversial or sensitive topics
- Would benefit from practitioner feedback

...send it to reviewers. When in doubt, review.

---

## Process

### Step 1: Initial Triage with GenAI Review

Run a GenAI editorial review using the standard template (`Review/Template Feedback OJSM.md`). This provides:
- Structured assessment across five criteria
- Identification of strengths and concerns
- Preliminary recommendation

Save the GenAI review to `[Manuscript]/Reviews/GenAI_Review_[Author].md`

### Step 2: Editorial Judgment

Review the GenAI assessment and apply your editorial judgment:
- Does the recommendation align with your read of the manuscript?
- Are there factors the AI missed (author reputation, timely topic, journal needs)?
- What's the risk of accepting without review vs. the delay of sending to reviewers?

### Step 3: Make the Decision

| Decision | Next Steps |
|----------|------------|
| **Desk Accept** | Create acceptance email → Set up for typesetting |
| **Desk Reject** | Create rejection email (encouraging) → Archive or close |
| **Send to Review** | Assign reviewers via Janeway → Monitor for completion |

### Step 4: Document the Decision

For all desk decisions, create an email in `[Manuscript]/Deliverables/` as an HTML file for Janeway:
- Accepts: `Acceptance_Email_[Date].html`
- Rejects: `Decision_Email_[Date].html`

---

## Directory Setup by Decision Type

### Desk Accept → Typesetting Track

```
[ID] [Author]/
├── Deliverables/
│   ├── Acceptance_Email_[Date].html    ← Decision email
│   └── Proof_Review_Email.html         ← Proof review request (after typesetting)
├── Reviews/
│   └── GenAI_Review_[Author].md        ← Triage review
├── Submissions/
│   ├── Original Submission/            ← Source files
│   └── Metadata/                       ← Janeway screenshot, bios
├── figures/
├── sections/
├── main.tex                            ← Typeset source
└── main.pdf                            ← Compiled proof
```

After acceptance, proceed to `02-Typesetting-After-Import_GUIDE.md`.

**After typesetting is complete**, generate the proof review email:

```bash
python3 scripts/generate_proof_email.py "7047 Imaninezhad" \
    --title "Generalizations of a Well-Known Result about the Number e" \
    --authors "Mahdi"

python3 scripts/generate_proof_email.py "7046 Bintz" \
    --title "Recognizing and Celebrating the Life and Times of Raye Montague" \
    --authors "William and Shabnam" \
    --checklist "Your names and affiliation,The accuracy of the abstract and keywords,The ACTSIPP Response Sheet appendix,Your author biographies"
```

The script auto-calculates a 2-week deadline (rounded to Friday).

### Desk Reject → Archive Track

```
[ID] [Author]/
├── Deliverables/
│   └── Decision_Email_[Date].html      ← Rejection email
├── Reviews/
│   └── GenAI_Review_[Author].md        ← Triage review
└── Submissions/
    └── Original Submission/            ← Source files (retain for records)
```

After rejection, the folder can remain in place (for records) or be moved to `archive/` if desired.

### Send to Review → Review Track

```
[ID] [Author]/
├── Reviews/
│   ├── GenAI_Review_[Author].md        ← Triage review (internal only)
│   └── [Reviewer reviews will go here]
└── Submissions/
    └── Original Submission/            ← Source files
```

Assign reviewers in Janeway. When reviews return, proceed to `04-Revision-Evaluation_PROCESS.md`.

---

## Email Templates

### Desk Accept Email

```html
<p>Dear [Author],</p>

<p>Thank you for submitting "[Title]" to the <em>Ohio Journal of School Mathematics</em>.</p>

<p>I am pleased to inform you that we are <strong>accepting your manuscript for publication</strong>. [1-2 sentences of specific praise about the work.]</p>

<p><strong>Next Steps:</strong></p>

<p>We will now move into typesetting. During this process, we may make minor edits for readability and formatting consistency. Once typesetting is complete, we will send you:</p>

<ol>
  <li>A typeset PDF of your article</li>
  <li>A list of any editorial changes we made</li>
</ol>

<p>Please review both carefully. Our goal is to produce a mutually agreeable draft that represents your work well. Once we reach that point, we will publish.</p>

<p>We are targeting <strong>Issue [Number] ([Season Year])</strong>, which releases on <strong>[Date]</strong>. We are aiming to have your work ready for the open.</p>

<p>[Closing congratulations]</p>

<p>Kindest regards,</p>

<p>Todd Edwards<br>
Editor, <em>Ohio Journal of School Mathematics</em></p>
```

### Desk Reject Email (Encouraging)

```html
<p>Dear [Author],</p>

<p>Thank you for submitting "[Title]" to the <em>Ohio Journal of School Mathematics</em>. I appreciate the time and effort you invested in this work.</p>

<p>After careful review, I am writing to let you know that we are not able to accept this manuscript for publication in OJSM. I want to explain why—not to discourage you, but to help guide your next steps.</p>

<p><strong>Why This Manuscript Isn't a Fit for OJSM:</strong></p>

<p>[Specific, constructive explanation of the mismatch—scope, completeness, evidence, etc.]</p>

<p><strong>Suggestions for Strengthening the Work:</strong></p>

<ol>
  <li>[Actionable suggestion 1]</li>
  <li>[Actionable suggestion 2]</li>
  <li>[Alternative venue suggestion if appropriate]</li>
</ol>

<p>[Encouraging closing that acknowledges effort and potential]</p>

<p>Thank you again for thinking of OJSM. I wish you the best with your continued work.</p>

<p>Kindest regards,</p>

<p>Todd Edwards<br>
Editor, <em>Ohio Journal of School Mathematics</em></p>
```

---

## Quick Reference: Decision Flowchart

```
New Submission Received
         │
         ▼
   Run GenAI Triage Review
         │
         ▼
  ┌──────┴──────┐
  │  Editorial   │
  │  Assessment  │
  └──────┬──────┘
         │
    ┌────┼────┐
    │    │    │
    ▼    ▼    ▼
  DESK  SEND  DESK
 ACCEPT  TO  REJECT
    │  REVIEW  │
    │    │     │
    ▼    ▼     ▼
Typeset  Assign  Archive
  Track  Reviewers Track
```

---

## Cross-Links

- [00-Start-Here_PROCESS_CHECKLIST.md](00-Start-Here_PROCESS_CHECKLIST.md) — Overall process overview
- [01-Intake-and-Setup_WORKFLOW.md](01-Intake-and-Setup_WORKFLOW.md) — Directory scaffolding
- [02-Typesetting-After-Import_GUIDE.md](02-Typesetting-After-Import_GUIDE.md) — After desk accept
- [04-Revision-Evaluation_PROCESS.md](04-Revision-Evaluation_PROCESS.md) — After reviews return
- `Review/Template Feedback OJSM.md` — GenAI review template

---

**Document created:** January 16, 2026  
**Last updated:** January 16, 2026
