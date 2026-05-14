# OJSM Revision Evaluation Process

**Purpose:** Guide Copilot through evaluating author revisions against editorial requests.

---

## CRITICAL PRINCIPLE

**Evaluate what EXISTS in the final manuscript, not what CHANGED.**

The diff is supplementary. The final text is the source of truth. Authors often add new sections at the end (limitations, implementation boxes) that won't show as "changes" to existing text.

---

## PROCESS

### Step 1: Gather Materials

```
LOCATE:
  - Original submission: {manuscript}/Submissions/Original Submission/
  - Revised submission: {manuscript}/Submissions/Revision Round 1/
  - Revision requests: {manuscript}/Reviews/*Decision*.html or *Decision*.md
  - Author response (if provided): {manuscript}/Submissions/Revision Round 1/*response* or *statement*
```

### Step 2: Extract and Index the Revised Manuscript

```
FOR revised_manuscript:
  EXTRACT full text with paragraph indices
  DISPLAY paragraphs with [index] prefix
  NOTE total paragraph count
  
  # This allows targeted searching and quoting
```

**Command pattern:**
```python
from docx import Document
doc = Document('path/to/revised.docx')
for i, para in enumerate(doc.paragraphs):
    if para.text.strip():
        print(f'[{i}] {para.text[:150]}...')
```

### Step 3: List Revision Requests

```
EXTRACT each specific request from the decision email/letter
NUMBER them (1, 2, 3...)
CREATE checklist format:

  [ ] 1. Request description
  [ ] 2. Request description
  ...
```

### Step 4: Search Final Manuscript for Evidence

```
FOR EACH revision_request:
  
  IDENTIFY key terms to search:
    - "pilot" / "exploratory" for pilot framing
    - "limitations" / "should be acknowledged" for limitations
    - "control group" / "generalizability" for methodology limits
    - "Teacher Implementation" / "guidance" for practical advice
    - "ethics" / "privacy" / "safeguards" for ethics discussion
  
  SEARCH the full manuscript text for these terms
  
  IF found:
    QUOTE the relevant paragraph(s)
    NOTE the paragraph index [n]
    MARK as ✅ CLEARLY MET or 🟡 PARTIALLY MET
  
  IF not found after thorough search:
    MARK as ❌ NOT MET
    EXPLAIN what was searched for
```

**Search command pattern:**
```python
full_text = '\n'.join([p.text for p in doc.paragraphs])
if 'search_term'.lower() in full_text.lower():
    # Find and quote context
```

### Step 5: Pay Special Attention to End Sections

```
ALWAYS examine the LAST 20 paragraphs carefully

Authors commonly add:
  - Limitations section (before or in Conclusion)
  - Implementation guidance (as boxed text or appendix)
  - Ethics statements
  - Acknowledgment of study constraints

These are easily missed by diff-based evaluation.
```

### Step 6: Compile Evaluation

```
FOR EACH request:
  STATUS: ✅ CLEARLY MET | 🟡 PARTIALLY MET | ❌ NOT MET
  EVIDENCE: Quote specific text with [paragraph index]
  
DETERMINE overall_status:
  IF all requests ✅ or mostly ✅ with minor 🟡 → CLEARLY_MET
  IF mix of ✅, 🟡, and 1-2 minor ❌ → PARTIALLY_MET  
  IF multiple critical ❌ → NOT_MET
```

### Step 7: Decide Next Action

```
IF CLEARLY_MET:
  → Proceed to typesetting
  → Consider minor editorial polish if needed
  → Draft acceptance email

IF PARTIALLY_MET (minor gaps):
  → Editor judgment call
  → Option A: Make small edits ourselves, offer author opt-out
  → Option B: Quick clarification request to author
  → Option C: Accept as-is if gaps are truly minor

IF NOT_MET (significant gaps):
  → Draft revision request email
  → Specify exactly what's still needed
  → Set deadline (typically 4 weeks)
```

---

## COMMON PITFALLS TO AVOID

1. **Trusting the diff alone** — New sections don't show as modifications
2. **Truncating manuscript text** — Limitations/conclusions are often at the end
3. **Keyword tunnel vision** — Authors may address requests with different wording
4. **Assuming absence** — Always verify with explicit text search before marking ❌

---

## EXAMPLE EVALUATION

**Request:** "Add a limitations section noting lack of control group"

**Search terms:** `limitations`, `control group`, `generalizability`, `should be acknowledged`

**Search result:**
```
✅ Found at [73]: "Some limitations of this study should be acknowledged. 
First, the absence of a control or comparison group prevents attributing 
observed learning gains exclusively to the use of FACTY. Second, the study 
was conducted with a small convenience sample drawn from a single 
institutional setting, which constrains the transferability of the findings..."
```

**Verdict:** ✅ CLEARLY MET — Comprehensive limitations paragraph addresses control group, sample size, setting constraints, and generalizability.

---

## QUICK REFERENCE

| Request Type | Search Terms |
|--------------|--------------|
| Pilot framing | `pilot`, `exploratory`, `proof of concept` |
| Limitations | `limitations`, `should be acknowledged`, `constraints` |
| Control group | `control group`, `comparison group`, `absence of` |
| Generalizability | `generalizability`, `transferability`, `cannot generalize` |
| Teacher guidance | `Teacher Implementation`, `instructors`, `guidance`, `practical` |
| Ethics | `ethics`, `privacy`, `consent`, `safeguards`, `oversight` |
| Methodology | `analysis`, `coding`, `reliability`, `how we identified` |

---

## WHEN IN DOUBT

Read the last 20 paragraphs of the manuscript manually. Most "missing" content lives there.
