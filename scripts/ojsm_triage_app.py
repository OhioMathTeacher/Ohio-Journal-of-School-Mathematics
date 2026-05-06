#!/usr/bin/env python3
"""OJSM Citation Audit — Stage 5: Manual triage of Frankenstein candidates.

Local web app for systematically reviewing each invalid-DOI candidate
flagged by ojsm_validate.py.  For each candidate, you record a verdict
(real Frankenstein / pure hallucination / transcription typo / extraction
artifact / unsure) plus the correct DOI if you found it and free-text notes.

The verdicts are written to datasets/ojsm-audit/triage_log.json — that file
is the structured ground-truth dataset for the audit paper.

Usage:
    python3 scripts/ojsm_triage_app.py
    # then open http://localhost:5001 in your browser

Re-run safe: existing verdicts are loaded on startup so you can
resume across sessions.  Saving a verdict for an already-decided
candidate overwrites the previous entry.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

from flask import Flask, jsonify, request

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPO_ROOT / "datasets" / "ojsm-audit" / "validation_summary.json"
INVENTORY_PATH = REPO_ROOT / "datasets" / "ojsm-audit" / "inventory.json"
REFS_DIR = REPO_ROOT / "datasets" / "ojsm-audit" / "refs"
PDF_DIR = REPO_ROOT / "datasets" / "ojsm-audit" / "pdfs"
TRIAGE_LOG_PATH = REPO_ROOT / "datasets" / "ojsm-audit" / "triage_log.json"

VERDICT_OPTIONS = [
    ("real_frankenstein",   "Real Frankenstein (paper exists, DOI fabricated)"),
    ("pure_hallucination",  "Pure hallucination (paper does not exist)"),
    ("transcription_typo",  "Transcription typo (DOI is close to correct)"),
    ("extraction_artifact", "Extraction artifact (our pipeline mis-captured)"),
    ("unsure",              "Unsure — needs more investigation"),
]


def load_candidates() -> list[dict]:
    """Build the triage queue from validation_summary.json + inventory.json."""
    if not SUMMARY_PATH.exists():
        sys.exit(f"ERROR: {SUMMARY_PATH} not found. Run ojsm_validate.py first.")
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    inventory_by_id = {}
    if INVENTORY_PATH.exists():
        inv = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        inventory_by_id = {a["article_id"]: a for a in inv["articles"]}

    out = []
    for i, fc in enumerate(summary["frankenstein_candidates"]):
        aid = fc["article_id"]
        meta = inventory_by_id.get(aid, {})
        refs_path = REFS_DIR / f"{aid}.txt"
        refs_text = refs_path.read_text(encoding="utf-8") if refs_path.exists() else ""
        out.append({
            "idx": i,
            "article_id": aid,
            "issue_id": fc.get("issue_id"),
            "article_title": fc.get("article_title"),
            "article_url": meta.get("url"),
            "article_doi": meta.get("doi"),
            "candidate_doi": fc.get("fabricated_doi"),
            "issues": fc.get("issues", []),
            "refs_text": refs_text,
        })
    return out


def load_verdicts() -> dict:
    if TRIAGE_LOG_PATH.exists():
        return json.loads(TRIAGE_LOG_PATH.read_text(encoding="utf-8"))
    return {"verdicts": {}}


def save_verdict(key: str, payload: dict) -> dict:
    log = load_verdicts()
    log["verdicts"][key] = payload
    log["last_updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    TRIAGE_LOG_PATH.write_text(
        json.dumps(log, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return log


CANDIDATES = load_candidates()


def candidate_key(c: dict) -> str:
    """Stable key per (article, candidate-doi) pair."""
    return f"{c['article_id']}::{c['candidate_doi']}"


# ---------- HTML page (single-file, vanilla JS) -----------------------------

PAGE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>OJSM Frankenstein Triage</title>
<style>
  :root {
    --bg: #f8f9fb; --card: #fff; --line: #e5e7eb; --primary: #2563eb;
    --text: #111827; --muted: #6b7280;
    --green: #10b981; --yellow: #f59e0b; --red: #ef4444; --gray: #9ca3af;
  }
  body { font-family: system-ui, -apple-system, sans-serif; margin: 0; background: var(--bg); color: var(--text); }
  .layout { display: grid; grid-template-columns: 320px 1fr; min-height: 100vh; }
  .sidebar { background: var(--card); border-right: 1px solid var(--line); padding: 16px; overflow-y: auto; }
  .sidebar h1 { font-size: 16px; margin: 0 0 4px; }
  .progress { font-size: 13px; color: var(--muted); margin-bottom: 12px; }
  .queue { list-style: none; padding: 0; margin: 0; }
  .queue li { padding: 8px 10px; border: 1px solid var(--line); border-radius: 6px; margin-bottom: 6px; cursor: pointer; font-size: 13px; }
  .queue li:hover { border-color: var(--primary); }
  .queue li.active { border-color: var(--primary); background: #eff6ff; }
  .queue .badge { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; vertical-align: middle; background: var(--gray); }
  .queue .badge.real_frankenstein   { background: var(--red); }
  .queue .badge.pure_hallucination  { background: #7c3aed; }
  .queue .badge.transcription_typo  { background: var(--yellow); }
  .queue .badge.extraction_artifact { background: var(--green); }
  .queue .badge.unsure              { background: #f97316; }
  .main { padding: 24px 32px; max-width: 900px; }
  .main h2 { margin: 0 0 4px; font-size: 22px; }
  .main .meta { color: var(--muted); font-size: 13px; margin-bottom: 16px; }
  .doi-line { font-family: 'JetBrains Mono', 'Courier New', monospace; background: #fef3c7; padding: 8px 12px; border-radius: 6px; word-break: break-all; }
  .quick-actions a { display: inline-block; background: var(--primary); color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; margin-right: 6px; font-size: 13px; }
  .quick-actions a:hover { opacity: 0.85; }
  .quick-actions a.secondary { background: #f3f4f6; color: var(--text); border: 1px solid var(--line); }
  .refs-box { background: white; border: 1px solid var(--line); border-radius: 6px; padding: 14px; max-height: 600px; overflow-y: auto; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.5; white-space: pre-wrap; }
  .refs-box mark { background: #fde68a; padding: 1px 3px; font-weight: bold; }
  .refs-help { font-size: 12px; color: var(--muted); margin-bottom: 6px; }
  .verdict-form { background: white; border: 1px solid var(--line); border-radius: 6px; padding: 18px; margin-top: 18px; }
  .verdict-form label { display: block; font-size: 14px; font-weight: 600; margin: 12px 0 4px; }
  .verdict-form input, .verdict-form textarea, .verdict-form select { width: 100%; padding: 8px; border: 1px solid var(--line); border-radius: 4px; font-size: 14px; box-sizing: border-box; font-family: inherit; }
  .verdict-form textarea { min-height: 80px; resize: vertical; }
  .actions { display: flex; gap: 10px; margin-top: 16px; }
  .actions button { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; }
  .btn-save { background: var(--primary); color: white; }
  .btn-save:hover { background: #1d4ed8; }
  .btn-skip { background: #f3f4f6; color: var(--text); border: 1px solid var(--line); }
  .saved-marker { color: var(--green); font-size: 13px; margin-left: 8px; opacity: 0; transition: opacity 0.3s; }
  .saved-marker.show { opacity: 1; }
  section { margin-bottom: 18px; }
  section h3 { font-size: 14px; font-weight: 600; color: var(--muted); margin: 0 0 6px; text-transform: uppercase; letter-spacing: 0.04em; }
</style>
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <h1>Frankenstein Triage</h1>
    <div class="progress" id="progress">Loading…</div>
    <ul class="queue" id="queue"></ul>
  </aside>
  <main class="main" id="main">
    <p>Loading…</p>
  </main>
</div>

<script>
let candidates = [];
let verdicts = {};
let activeIdx = 0;

async function load() {
  const r = await fetch('/api/candidates');
  const data = await r.json();
  candidates = data.candidates;
  verdicts = data.verdicts;
  renderQueue();
  renderActive();
}

function keyFor(c) { return c.article_id + '::' + c.candidate_doi; }

function renderQueue() {
  const ul = document.getElementById('queue');
  ul.innerHTML = '';
  let done = 0;
  candidates.forEach((c, i) => {
    const v = verdicts[keyFor(c)];
    if (v) done++;
    const li = document.createElement('li');
    if (i === activeIdx) li.classList.add('active');
    const badgeClass = v ? v.verdict : '';
    li.innerHTML = '<span class="badge ' + badgeClass + '"></span>' +
                   '<strong>art ' + c.article_id + '</strong> · ' +
                   (c.candidate_doi || '?').slice(0, 40);
    li.onclick = () => { activeIdx = i; renderActive(); renderQueue(); };
    ul.appendChild(li);
  });
  document.getElementById('progress').textContent =
    done + ' of ' + candidates.length + ' verified';
}

function renderActive() {
  const c = candidates[activeIdx];
  if (!c) return;
  const v = verdicts[keyFor(c)] || {};
  const refsHtml = highlight(c.refs_text || '(no references text saved for this article)', c.candidate_doi);
  const titleQuery = encodeURIComponent((c.article_title || '').replace(/&#x27;/g, "'").replace(/&amp;/g, '&').slice(0, 80));
  const doiUrl = 'https://doi.org/' + (c.candidate_doi || '');
  const localPdf = '/pdf/' + c.article_id;

  document.getElementById('main').innerHTML = `
    <h2>art ${c.article_id} — ${escapeHtml((c.article_title || '?').replace(/&#x27;/g, "'").replace(/&amp;/g, '&'))}</h2>
    <div class="meta">issue ${c.issue_id || '—'} · article DOI: ${c.article_doi || '—'} · <a href="${c.article_url}" target="_blank">view on Janeway</a></div>

    <section>
      <h3>Suspect DOI</h3>
      <div class="doi-line">${escapeHtml(c.candidate_doi || '')}</div>
      <p class="meta" style="margin-top:6px">${(c.issues || []).join(' · ')}</p>
    </section>

    <section class="quick-actions">
      <a href="${doiUrl}" target="_blank">Try DOI in browser ↗</a>
      <a href="https://scholar.google.com/scholar?q=${titleQuery}" target="_blank" class="secondary">Search Google Scholar ↗</a>
      <a href="https://search.crossref.org/?q=${titleQuery}" target="_blank" class="secondary">Search CrossRef ↗</a>
      <a href="${localPdf}" target="_blank" class="secondary">Open article PDF ↗</a>
    </section>

    <section>
      <h3>References Section (DOI highlighted)</h3>
      <div class="refs-help">The suspect DOI is highlighted below — scroll within this box to find it. PDF text often splits long DOIs across lines, so look for the parts (e.g. <code>14794802.</code> on one line, <code>2024.2444321</code> on the next).</div>
      <div class="refs-box" id="refs-box">${refsHtml}</div>
    </section>

    <section class="verdict-form">
      <label for="verdict">Verdict</label>
      <select id="verdict">
        <option value="">— choose —</option>
        ${[
          ["real_frankenstein", "Real Frankenstein (paper exists, DOI fabricated)"],
          ["pure_hallucination", "Pure hallucination (paper does not exist)"],
          ["transcription_typo", "Transcription typo (DOI is close to correct)"],
          ["extraction_artifact", "Extraction artifact (our pipeline mis-captured)"],
          ["unsure", "Unsure — needs more investigation"]
        ].map(([k,l]) => '<option value="'+k+'"'+(v.verdict===k?' selected':'')+'>'+l+'</option>').join('')}
      </select>

      <label for="correct_doi">Correct DOI (if found)</label>
      <input type="text" id="correct_doi" value="${escapeHtml(v.correct_doi || '')}" placeholder="e.g. 10.1080/14794802.2024.2401488">

      <label for="notes">Notes</label>
      <textarea id="notes" placeholder="Anything noteworthy: pages don't match, paper is from 2023 not 2024, source PDF actually shows different DOI, etc.">${escapeHtml(v.notes || '')}</textarea>

      <div class="actions">
        <button class="btn-save" onclick="saveVerdict()">Save & Next</button>
        <button class="btn-skip" onclick="nextCandidate()">Skip</button>
        <span class="saved-marker" id="saved">✓ Saved</span>
      </div>
    </section>
  `;
  setTimeout(scrollHighlightIntoView, 0);
}

function scrollHighlightIntoView() {
  // After renderActive, scroll the references box so the first <mark> is visible.
  const box = document.getElementById('refs-box');
  if (!box) return;
  const mark = box.querySelector('mark');
  if (!mark) return;
  const boxRect = box.getBoundingClientRect();
  const markRect = mark.getBoundingClientRect();
  box.scrollTop = mark.offsetTop - box.offsetTop - 60;
}

async function saveVerdict() {
  const c = candidates[activeIdx];
  const verdict = document.getElementById('verdict').value;
  if (!verdict) { alert('Please choose a verdict first.'); return; }
  const payload = {
    article_id: c.article_id,
    article_title: c.article_title,
    issue_id: c.issue_id,
    candidate_doi: c.candidate_doi,
    verdict: verdict,
    correct_doi: document.getElementById('correct_doi').value.trim() || null,
    notes: document.getElementById('notes').value.trim() || null,
    saved_at: new Date().toISOString()
  };
  const r = await fetch('/api/verdict', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ key: keyFor(c), payload: payload })
  });
  if (r.ok) {
    verdicts[keyFor(c)] = payload;
    document.getElementById('saved').classList.add('show');
    setTimeout(() => document.getElementById('saved').classList.remove('show'), 800);
    nextCandidate();
  }
}

function nextCandidate() {
  // Find next un-verdicted candidate; wrap around if none left.
  const total = candidates.length;
  for (let step = 1; step <= total; step++) {
    const i = (activeIdx + step) % total;
    if (!verdicts[keyFor(candidates[i])]) {
      activeIdx = i; renderActive(); renderQueue(); return;
    }
  }
  // All done.
  activeIdx = (activeIdx + 1) % total;
  renderActive(); renderQueue();
}

function highlight(text, doi) {
  // Highlights the suspect DOI inside the references text, even if the DOI
  // is split across line breaks in the source (PDF text-wrap is common).
  // Strategy: insert optional whitespace between every character of the DOI
  // pattern so a DOI like "10.1080/14794802.2024.2444321" matches even when
  // pdftotext wrote it as "10.1080/14794802.\n2024.2444321".
  if (!doi) return escapeHtml(text);
  const escaped = escapeHtml(text);
  // Build a regex that lets ANY whitespace appear between consecutive DOI chars.
  const pattern = doi.split('').map(c => escapeRe(c)).join('\\s*');
  const re = new RegExp(pattern, 'g');
  return escaped.replace(re, m => '<mark>' + m + '</mark>');
}

function escapeHtml(s) {
  return (s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

load();
</script>
</body>
</html>
"""

app = Flask(__name__)


@app.route('/')
def index():
    return PAGE_HTML


@app.route('/api/candidates')
def api_candidates():
    log = load_verdicts()
    return jsonify({"candidates": CANDIDATES, "verdicts": log["verdicts"]})


@app.route('/api/verdict', methods=['POST'])
def api_verdict():
    data = request.get_json(force=True)
    save_verdict(data["key"], data["payload"])
    return jsonify({"ok": True})


@app.route('/pdf/<int:article_id>')
def serve_pdf(article_id: int):
    from flask import send_file, abort
    pdf = PDF_DIR / f"{article_id}.pdf"
    if not pdf.exists():
        abort(404, f"PDF for article {article_id} not on disk")
    return send_file(pdf, mimetype='application/pdf')


if __name__ == "__main__":
    print(f"\nFrankenstein triage app — {len(CANDIDATES)} candidate(s) to review")
    print(f"Open in browser: http://localhost:5001")
    print(f"Verdicts saved to: {TRIAGE_LOG_PATH}\n")
    app.run(debug=False, host='127.0.0.1', port=5001)
