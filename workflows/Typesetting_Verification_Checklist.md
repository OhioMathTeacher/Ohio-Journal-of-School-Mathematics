# Typesetting Verification Checklist

**Purpose:** Ensure typeset manuscripts are accurate and ready for author proof review.

**When to use:** After completing initial typesetting, before sending proof to authors.

**Upstream context:** Intake/scaffolding lives in [01-Intake-and-Setup_WORKFLOW.md](01-Intake-and-Setup_WORKFLOW.md); day-to-day flow in [00-Start-Here_PROCESS_CHECKLIST.md](00-Start-Here_PROCESS_CHECKLIST.md); phase guidance in [02-Typesetting-After-Import_GUIDE.md](02-Typesetting-After-Import_GUIDE.md). This checklist assumes the standard directories (`Submissions/`, `Deliverables/`, `Reviews/`, `figures/`, `sections/`) already exist.

---

## 1. Content Accuracy

- [ ] **Text extraction comparison** (automated check)
  - [ ] Extract text from typeset PDF: `pdftotext main.pdf typeset_text.txt`
  - [ ] Extract text from author's revision PDF: `pdftotext "Submissions/Revision Round 1/submission.pdf" author_text.txt`
  - [ ] Compare for major differences (missing paragraphs, changed wording): `diff -u author_text.txt typeset_text.txt | less`
  - [ ] Investigate any substantial differences to ensure nothing was omitted
  - [ ] Note: Formatting differences (line breaks, hyphenation) are normal; look for content gaps

- [ ] **Manual spot-check** against original submission
  - [ ] All paragraphs present in correct order
  - [ ] No sentences omitted or duplicated
  - [ ] Technical terminology matches exactly
  - [ ] Punctuation preserved
  
- [ ] **Section structure** matches original
  - [ ] All headings present and properly hierarchized
  - [ ] Subsection numbering correct (if applicable)

## 2. Technical Elements

### Tables
- [ ] All tables present and numbered correctly
- [ ] Data values match original exactly
- [ ] Column/row headers correct
- [ ] Table captions match original
- [ ] Formatting appropriate (alignment, spacing, borders)

### Figures
- [ ] All figures included and high quality
- [ ] Figure numbers sequential and correct
- [ ] Captions match original
- [ ] Figures positioned near first reference
- [ ] Image files properly named and organized in `figures/`

### Equations/Mathematics
- [ ] All equations typeset correctly in LaTeX
- [ ] Symbols and notation match original
- [ ] Equation numbers (if used) correct
- [ ] Inline math properly formatted

### References/Citations
- [ ] Complete bibliography present
- [ ] All in-text citations appear in reference list
- [ ] No orphaned references (in list but not cited)
- [ ] Reference formatting consistent (APA, etc.)
- [ ] DOIs and URLs functional and properly formatted

## 3. Metadata & Document Settings

- [ ] **Author information**
  - [ ] All author names spelled correctly
  - [ ] Author order matches submission
  - [ ] Affiliations accurate with correct superscripts
  - [ ] Correspondence email correct (if applicable)
  
- [ ] **\thanks statement** (if present)
  - [ ] Actually applicable to this article
  - [ ] Authors acknowledge grants, funding, AI tools appropriately
  - [ ] Remove generic/template \thanks if not needed
  
- [ ] **Journal metadata**
  - [ ] Volume and issue number correct
  - [ ] Starting page number assigned
  - [ ] Running header: Author names vs "et al." appropriate
  - [ ] Short title accurate
  
- [ ] **Abstract & keywords**
  - [ ] Abstract matches submission
  - [ ] Keywords present and appropriate

## 4. LaTeX Compilation & Technical

- [ ] **Clean compilation**
  - [ ] No errors during compile
  - [ ] Review warnings (note harmless vs. problematic)
  - [ ] No missing references or citations
  - [ ] No multiply defined labels (or document why acceptable)
  
- [ ] **Hyperlinks**
  - [ ] `[hidelinks]` option enabled in `\usepackage{hyperref}`
  - [ ] No blue boxes around links in PDF
  - [ ] URLs clickable but visually clean
  
- [ ] **Fonts**
  - [ ] Correct fonts loaded (Libertinus Serif, Fira Sans, etc.)
  - [ ] Math font appropriate (Libertinus Math)
  - [ ] No font substitution warnings

## 5. Visual/Layout Review (PDF)

- [ ] **Page breaks**
  - [ ] No orphaned section headings (heading at bottom of page)
  - [ ] No widows/orphans in paragraphs
  - [ ] Tables/figures don't create awkward breaks
  - [ ] Conclusion doesn't start mid-page inappropriately
  
- [ ] **Spacing**
  - [ ] Consistent paragraph spacing
  - [ ] No excessive white space
  - [ ] FloatBarriers working correctly
  
- [ ] **Headers & footers**
  - [ ] Page numbers correct and sequential
  - [ ] Running header matches on all pages
  - [ ] Journal name/info appears correctly
  
- [ ] **Figures & tables**
  - [ ] Not too large or too small
  - [ ] Readable resolution
  - [ ] Positioned logically
  
- [ ] **Biography section** (if applicable)
  - [ ] Author photos display correctly
  - [ ] Bios appropriate length (not taller than photos)
  - [ ] Formatting consistent across authors

## 6. Cross-References & Internal Consistency

- [ ] All `\ref{}` commands resolve correctly
- [ ] All `\cite{}` commands resolve correctly
- [ ] Table/Figure numbers sequential (Table 1, Table 2, etc.)
- [ ] Section numbering consistent
- [ ] No "??" appearing in compiled PDF

## 6.5. Formatting & Punctuation Details

**Important:** Use Word document XML to verify formatting, not plain text extraction!  
Extract XML: `unzip -q -o "manuscript.docx" -d temp_docx && cat temp_docx/word/document.xml`  
Look for: `<w:i/>` (italics), `<w:b/>` (bold), formatting tags wrap the affected text.

- [ ] **Quotation marks**
  - [ ] American style: commas and periods inside quotes ("text," not "text",)
  - [ ] LaTeX: Proper conversion to `` (open) and '' (close)
  - [ ] No straight quotes from Word/RTF conversion ("" instead of "")
  
- [ ] **Italics preservation** (check XML for `<w:i/>` tags)
  - [ ] Book/article/lesson titles italicized consistently
  - [ ] Emphasized words/phrases preserved (e.g., *only if*, *informs vs transforms*)
  - [ ] Foreign words and technical terms
  - [ ] Variables in running text (if applicable)
  - [ ] Product/tool names (e.g., *Goodness of Fit Meter*)
  
- [ ] **Bold preservation** (check XML for `<w:b/>` tags)
  - [ ] Section/subsection headings match original emphasis
  - [ ] Key terms or numbered items (e.g., **Strategy 1**, **Strategy 2**)
  - [ ] Table headers and labels
  
- [ ] **Special characters**
  - [ ] Em-dashes (—) not double hyphens (--)
  - [ ] En-dashes (–) for ranges (e.g., pp. 5–10)
  - [ ] Ellipses (…) not three periods (...)
  - [ ] Proper ampersands (\&) in citations
  
- [ ] **Spacing**
  - [ ] No double spaces after periods or elsewhere
  - [ ] Consistent spacing around punctuation
  - [ ] Non-breaking spaces where appropriate (~)

## 7. Content-Specific Checks

- [ ] Special characters render correctly (em dashes, quotes, etc.)
- [ ] Bulleted/numbered lists formatted properly
- [ ] Block quotes (if any) indented appropriately
- [ ] Code listings (if any) properly formatted
- [ ] URLs don't overflow margins

## 8. Final Pre-Send Verification

- [ ] **PDF properties**
  - [ ] File size reasonable (< 5MB preferred)
  - [ ] Page count matches expected
  - [ ] Metadata embedded (title, authors)
  
- [ ] **Deliverables folder & file naming**
  - [ ] Copy final PDF to `Deliverables/` folder
  - [ ] Use naming convention: `LastName_DRAFT_MonDDv#.pdf`
    - Example: `Cox_DRAFT_Nov27v1.pdf`
    - If regenerating same day, increment version: v1 → v2 → v3
    - Check for existing versions: `ls Deliverables/LastName_DRAFT_MonDD*.pdf`
  - [ ] This versioned filename helps track which PDF to upload to Janeway
  
- [ ] **Deliverables folder**
  - [ ] Final PDF copied to `Deliverables/`
  - [ ] Named appropriately (e.g., `AuthorName_Proof.pdf`)
  
- [ ] **Documentation**
  - [ ] Verification checklist filled out and saved
  - [ ] Any known issues documented
  - [ ] Notes for authors prepared (if needed)

---

## Notes Section

Use this space to document any issues found, decisions made, or special handling required:

```
Example:
- Table 1: Complex merged cells required custom LaTeX approach
- Figure 2: Increased from 0.6 to 0.8 textwidth for readability
- References: Used hard-coded bibliography per journal style
- Warnings: 5 "underfull hbox" warnings are cosmetic, not errors
```

---

**Completed by:** ___________________  
**Date:** ___________________  
**Manuscript ID:** ___________________  
**Ready for author proof:** ☐ Yes  ☐ No (see notes)
