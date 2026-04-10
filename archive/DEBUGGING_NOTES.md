# Citation Validator - Debugging Notes & Status
**Date:** April 8, 2026  
**Context:** Building tool in response to Nature article about 2-6% of 2025 papers containing hallucinated citations

---

## What We're Building

A citation validator that:
1. Parses BibTeX files
2. Validates citations against CrossRef, OpenAlex, arXiv APIs
3. Uses AI to detect "Frankenstein citations" (real metadata mixed to create fake references)
4. Provides a web interface accessible to non-technical users
5. Can be hosted on GitHub Pages (static site, no server required)

---

## Current Status

### ✅ What Works

#### Python CLI (`scripts/citation_validator.py`)
- **Core validation logic:** CrossRef, OpenAlex, arXiv, DOI resolver APIs all working
- **arXiv fix:** DOIs like `10.48550/arXiv.2602.15871` now route to arXiv API instead of failing
- **DataCite fallback:** Uses `doi.org/api/handles/` for Zenodo/Figshare DOIs that CrossRef doesn't know
- **Heuristics:** 8 pattern detectors working (generic titles, temporal anomalies, Jaccard similarity)
- **Test suites:** 
  - `nature_article_refs.bib`: 10 real citations from Nature article (all pass)
  - `test_false_results.bib`: 6 test cases for false positives/negatives
- **AI integration:** Works with Groq (and Anthropic/Gemini/OpenAI) when key provided via env var

#### Flask Webapp (`scripts/webapp.py`)
- **Server runs:** `python3 webapp.py` starts Flask on port 5000
- **Basic UI:** HTML renders, file upload works, textarea input works
- **Styling:** Close-reader inspired design (CSS variables, clean look)
- **Backend validation:** `/validate` endpoint works (tested via curl)

### ❌ What Doesn't Work

#### Flask Webapp - JavaScript Issues
**Problem:** Buttons don't respond to clicks  
**Symptoms:**
- "Configure AI" button does nothing
- "Validate Citations" button does nothing
- Modal doesn't open
- No console errors visible in browser (check DevTools console for actual errors)

**Suspected Causes:**
1. **Jinja2 template interference:** Used `render_template_string()` initially, switched to `Response()` but issue persists
2. **JavaScript curly braces:** Flask/Jinja2 may be eating `{}` in JS code during string processing
3. **Triple-quoted Python string issues:** Python warning about `\{` on line 16 suggests escape sequence problems
4. **Event handlers not wiring:** `onclick="openAIModal()"` in HTML but function may not be defined at runtime

**What we tried:**
- Validated JS syntax with Node.js → no syntax errors found
- Checked all `onclick` handlers exist in HTML → they do
- Verified all DOM element IDs present → they are
- Changed from `.join('\n')` to string concatenation → didn't fix it
- Switched from `render_template_string` to `Response` → didn't fix it

#### Static HTML (`citation-validator.html`)
**Problem:** Same button issue - "Configure AI" button doesn't work  
**Symptoms:**
- JavaScript visible at bottom of page in browser (suggests parsing/execution failure)
- Modal doesn't open when button clicked

**Suspected Causes:**
1. **BibTeX regex too strict:** Initially had `\n\}` pattern (fixed to `\}` but may need testing)
2. **Async/await browser compatibility:** Using modern JS features without transpiling
3. **CORS issues:** CrossRef/OpenAlex APIs may block browser requests (need CORS headers)
4. **Script tag not closing properly:** Single `<script>` tag is 700+ lines

**Key Question:** Does the browser console show errors? Check:
```javascript
// Open browser DevTools (F12)
// Console tab - look for:
// - SyntaxError
// - ReferenceError  
// - Uncaught exceptions
```

---

## Known Limitations

### False Positives
- **Figshare DOIs:** Still return INVALID (DataCite fallback helps but doesn't fully resolve)
- **Sparse BibTeX entries:** Citations with minimal metadata trigger warnings even when real

### False Negatives  
- **Frankenstein citations:** Require AI to catch (metadata mixups look valid to APIs)
- **Non-existent journals:** No comprehensive journal registry to check against

---

## Architecture Decisions

### Why Static Site?
- **Deployment:** GitHub Pages is free and requires no server management
- **Security:** API keys stay in user's browser (localStorage), never touch our servers
- **Scalability:** Pure client-side means unlimited concurrent users
- **close-reader precedent:** https://ohiomathteacher.github.io/close-reader/ works this way

### Why Client-Side AI?
- **Privacy:** BibTeX content never sent to our servers
- **Cost:** We don't pay for API calls
- **Flexibility:** Users choose Claude/Gemini/Groq/OpenAI based on their needs

---

## Next Steps for Debugging

### Immediate (Browser DevTools)
1. Open `citation-validator.html` in Chrome/Firefox
2. Press F12 → Console tab
3. Click "Configure AI" button
4. Check for JavaScript errors
5. Try typing `openAIModal()` directly in console → does it work?

### If Function Not Defined
- Script tag didn't execute
- Check for earlier syntax error stopping execution
- Verify `<script>` tag closes properly

### If Function Defined But Doesn't Run
- Event handler not wiring → change `onclick="openAIModal()"` to:
  ```javascript
  document.getElementById('aiBtn').addEventListener('click', openAIModal);
  ```

### If CORS Errors
- CrossRef/OpenAlex may block browser requests
- Test with browser extension like "CORS Unblock" (dev only)
- Consider using a simple proxy or switching back to server-side validation

### Alternative Approach
1. Keep Python CLI for power users
2. Deploy Flask webapp to Render/Fly.io (not GitHub Pages)
3. Use server-side validation only
4. Skip client-side AI entirely (or make it optional)

---

## Files Modified in Last Commit (2199206)

```
.gitignore                              # Added .env
.env.example                            # Template for API keys
scripts/citation_validator.py          # arXiv + DataCite fixes
citation-validator.html                 # New static version
test_citations/nature_article_refs.bib  # Test: Nature's own citations
test_citations/test_false_results.bib   # Test: false pos/neg cases
```

**Not yet committed:**  
`scripts/webapp.py` - Flask version with close-reader styling (buttons broken)

---

## Testing Commands

### Python CLI
```bash
cd scripts
source .venv/bin/activate
python3 citation_validator.py ../test_citations/nature_article_refs.bib --use-ai --groq-api-key YOUR_KEY
```

### Flask Webapp
```bash
cd scripts
source .venv/bin/activate
python3 webapp.py
# Open http://localhost:5000
```

### Static HTML
```bash
# Just open citation-validator.html in browser
open citation-validator.html  # macOS
xdg-open citation-validator.html  # Linux
```

---

## Contact & Context

- **Goal:** Respond to Nature article, prepare correspondence showing independent validation
- **Timeline:** April 8, 2026 (same day as Nature article)
- **Repo:** https://github.com/OhioMathTeacher/Ohio-Journal-of-School-Mathematics
- **Related Project:** close-reader (works perfectly, same localStorage pattern)

---

## Questions to Answer

1. **Why do buttons work in close-reader but not citation validator?**
   - Both use localStorage for API keys
   - Both have onclick handlers
   - Both are single HTML files
   - What's different?

2. **Should we abandon the static approach?**
   - If CORS is the issue, static won't work for API calls
   - Server-side might be simpler despite deployment overhead

3. **Is the JavaScript actually loading?**
   - Screenshot shows JS code visible at bottom of page
   - This suggests the script tag didn't properly close or execute
   - Check: view source vs inspect element

---

## Success Criteria (When Fixed)

- [ ] Click "Configure AI" → modal opens
- [ ] Select provider (Groq) → key input appears
- [ ] Paste key → Save → button shows "AI: Groq ✓"
- [ ] Paste BibTeX → Click "Validate Citations" → results appear
- [ ] Warning/suspicious entries show AI analysis
- [ ] Export buttons work (HTML/JSON/CSV)
- [ ] All of this works from a static file (no server)

---

## For Next Developer/Session

**Start here:**
1. Check browser console for errors
2. If script not loading, check `<script>` tag syntax
3. If CORS errors, might need server-side approach
4. If event handlers not wiring, try `addEventListener` instead of `onclick`
5. Consider comparing line-by-line with close-reader's working code

**Don't spin wheels on:**
- Node.js syntax validation (already passed)
- Jinja2 fixes (static HTML doesn't use Flask)
- More Python debugging (Python CLI works fine)

**The core issue is:** JavaScript in the browser is not executing or not wiring up event handlers. Everything else is working.
