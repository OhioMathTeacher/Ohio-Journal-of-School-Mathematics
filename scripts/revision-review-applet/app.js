const defaultIssues = [
  {
    id: "7158-E01",
    priority: "medium",
    location: "howourframeworkadvancessota.tex",
    title: "Tone down remaining SOTA body wording",
    problemArea:
      "The section title was softened, but the opening sentence still claims State-of-the-Art.",
    currentText:
      "Our proposed novel framework achieves the State-of-the-Art through the culmination of the following three strategies...",
    suggestedRevision:
      "Our framework improves performance over the single-LLM baselines in this study through three complementary design strategies."
  },
  {
    id: "7158-E02",
    priority: "high",
    location: "evaluation_methodology.tex",
    title: "Rewrite manual filtering paragraph",
    problemArea:
      "Opening method paragraph is contradictory and informal.",
    currentText:
      "Our first step of evaluation began with the manual filtering... Though models nowadays are powerful enough to not make mistakes... (Lianmin et al, 2023)",
    suggestedRevision:
      "We manually removed incoherent or malformed outputs before scoring. We then evaluated the remaining outputs using a rubric-guided LLM-as-a-judge protocol, following recent work on automated LLM evaluation."
  },
  {
    id: "7158-E03",
    priority: "medium",
    location: "related_work.tex",
    title: "Define NLP at first use",
    problemArea:
      "NLP appears without expansion for broad education readership.",
    currentText:
      "Recent work has begun to explore multi-LLM frameworks for complex NLP tasks.",
    suggestedRevision:
      "Recent work has begun to explore multi-LLM frameworks for complex natural language processing (NLP) tasks."
  },
  {
    id: "7158-E04",
    priority: "high",
    location: "related_work.tex + references.tex",
    title: "Replace pseudo-citations for tool docs",
    problemArea:
      "Citations like 'CrewAI Documentation' and 'LangGraph Documentation' are not full references.",
    currentText:
      "CrewAI (CrewAI Documentation) ... LangGraph (LangGraph Documentation) ...",
    suggestedRevision:
      "Convert these to proper citations with organization/author, year or version date, URL, and access date; add matching entries in references.tex."
  },
  {
    id: "7158-E05",
    priority: "high",
    location: "results.tex",
    title: "Fix remaining Tukey table reference",
    problemArea:
      "One paragraph still says 'presented in Table 3' after relabeling.",
    currentText:
      "The results, presented in Table 3, indicate...",
    suggestedRevision:
      "The results, presented in Table~\\ref{tab:tukey_overall}, indicate..."
  },
  {
    id: "7158-E06",
    priority: "high",
    location: "results.tex",
    title: "Adjust ANOVA assumption wording",
    problemArea:
      "Text explicitly describes model groups as independent, which may be misleading for prompt-paired outputs.",
    currentText:
      "...comparing the means of more than two independent groups...",
    suggestedRevision:
      "Use neutral wording: 'comparing mean scores across model conditions under the current evaluation setup,' and add a short caveat that paired-prompt structure may affect inferential assumptions."
  },
  {
    id: "7158-E07",
    priority: "medium",
    location: "references.tex",
    title: "Fix citation integrity issues",
    problemArea:
      "Reference list appears to contain mismatches/missing entries (e.g., Cohen benchmark mention vs muller entry).",
    currentText:
      "According to widely accepted benchmarks (e.g., Cohen, 1988) ... while references include muller1989 entry.",
    suggestedRevision:
      "Run a full citation audit: every in-text citation must map to a complete reference, and mismatched entries should be corrected or removed."
  },
  {
    id: "7158-E08",
    priority: "medium",
    location: "related_work.tex",
    title: "Normalize venue/citation style consistency",
    problemArea:
      "Mixed style like 'Wu et al., ICLR 2024' is inconsistent with bibliography style.",
    currentText:
      "AutoGen (Wu et al., ICLR 2024) introduces...",
    suggestedRevision:
      "Use standard in-text citation form (e.g., Wu et al., 2024), and keep venue details only in the reference entry."
  }
];

let issues = structuredClone(defaultIssues);
let decisions = {};
let currentIndex = 0;
let pendingAction = null;

const progressText = document.getElementById("progressText");
const countsText = document.getElementById("countsText");
const priorityPill = document.getElementById("priorityPill");
const locationText = document.getElementById("locationText");
const issueTitle = document.getElementById("issueTitle");
const problemArea = document.getElementById("problemArea");
const currentText = document.getElementById("currentText");
const suggestedText = document.getElementById("suggestedText");
const decisionView = document.getElementById("decisionView");

const feedbackCard = document.getElementById("feedbackCard");
const feedbackTitle = document.getElementById("feedbackTitle");
const feedbackPrompt = document.getElementById("feedbackPrompt");
const feedbackInput = document.getElementById("feedbackInput");

const importFile = document.getElementById("importFile");
const resetBtn = document.getElementById("resetBtn");
const exportBtn = document.getElementById("exportBtn");
const acceptBtn = document.getElementById("acceptBtn");
const rejectBtn = document.getElementById("rejectBtn");
const reviseBtn = document.getElementById("reviseBtn");
const cancelFeedbackBtn = document.getElementById("cancelFeedbackBtn");
const saveFeedbackBtn = document.getElementById("saveFeedbackBtn");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");

function priorityClass(priority) {
  if (priority === "high") return "High";
  if (priority === "medium") return "Medium";
  return "Low";
}

function updateCounts() {
  const values = Object.values(decisions);
  const accepted = values.filter((d) => d.action === "accept").length;
  const rejected = values.filter((d) => d.action === "reject").length;
  const revise = values.filter((d) => d.action === "revise").length;
  const pending = issues.length - values.length;
  countsText.textContent = `Accepted: ${accepted} | Rejected: ${rejected} | Revise: ${revise} | Pending: ${pending}`;
}

function renderIssue() {
  if (!issues.length) {
    issueTitle.textContent = "No issues loaded";
    problemArea.textContent = "Import a JSON file with issues to start.";
    currentText.textContent = "";
    suggestedText.textContent = "";
    progressText.textContent = "Issue 0 of 0";
    locationText.textContent = "Location: n/a";
    priorityPill.textContent = "No priority";
    decisionView.textContent = "No decision yet.";
    updateCounts();
    return;
  }

  const issue = issues[currentIndex];
  progressText.textContent = `Issue ${currentIndex + 1} of ${issues.length}`;
  priorityPill.textContent = `Priority: ${priorityClass(issue.priority)}`;
  locationText.textContent = `Location: ${issue.location}`;
  issueTitle.textContent = issue.title;
  problemArea.textContent = issue.problemArea;
  currentText.textContent = issue.currentText;
  suggestedText.textContent = issue.suggestedRevision;

  const decision = decisions[issue.id];
  if (!decision) {
    decisionView.textContent = "No decision yet.";
  } else {
    decisionView.textContent = JSON.stringify(decision, null, 2);
  }

  feedbackCard.classList.add("hidden");
  updateCounts();
}

function saveDecision(action, note = "") {
  const issue = issues[currentIndex];
  decisions[issue.id] = {
    issueId: issue.id,
    action,
    note,
    timestamp: new Date().toISOString()
  };
  renderIssue();
  if (currentIndex < issues.length - 1) {
    currentIndex += 1;
    renderIssue();
  }
}

function requestFeedback(action) {
  pendingAction = action;
  feedbackCard.classList.remove("hidden");
  feedbackInput.value = "";

  if (action === "reject") {
    feedbackTitle.textContent = "Reject Suggestion";
    feedbackPrompt.textContent = "Tell me what is wrong with this suggestion so I can improve it.";
    feedbackInput.placeholder = "Example: This weakens the claim too much. Keep strength but add one caveat.";
    return;
  }

  feedbackTitle.textContent = "Revise Suggestion";
  feedbackPrompt.textContent = "Share your revision idea and I will use your wording approach.";
  feedbackInput.placeholder = "Type your preferred revision language here...";
}

function nextIssue() {
  if (currentIndex < issues.length - 1) {
    currentIndex += 1;
    renderIssue();
  }
}

function prevIssue() {
  if (currentIndex > 0) {
    currentIndex -= 1;
    renderIssue();
  }
}

function exportDecisions() {
  const payload = {
    exportedAt: new Date().toISOString(),
    totalIssues: issues.length,
    decisions,
    issues
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  const ts = new Date().toISOString().replace(/[:.]/g, "-");
  a.href = URL.createObjectURL(blob);
  a.download = `revision-decisions-${ts}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}

function importIssues(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const parsed = JSON.parse(reader.result);
      const loaded = Array.isArray(parsed) ? parsed : parsed.issues;
      if (!Array.isArray(loaded) || !loaded.length) {
        throw new Error("No issues array found.");
      }
      issues = loaded;
      decisions = {};
      currentIndex = 0;
      renderIssue();
    } catch (err) {
      alert(`Import failed: ${err.message}`);
    }
  };
  reader.readAsText(file);
}

acceptBtn.addEventListener("click", () => saveDecision("accept"));
rejectBtn.addEventListener("click", () => requestFeedback("reject"));
reviseBtn.addEventListener("click", () => requestFeedback("revise"));

saveFeedbackBtn.addEventListener("click", () => {
  if (!pendingAction) return;
  const note = feedbackInput.value.trim();
  if (!note) {
    alert("Please add a note before saving.");
    return;
  }
  saveDecision(pendingAction, note);
  pendingAction = null;
  feedbackCard.classList.add("hidden");
});

cancelFeedbackBtn.addEventListener("click", () => {
  pendingAction = null;
  feedbackCard.classList.add("hidden");
});

prevBtn.addEventListener("click", prevIssue);
nextBtn.addEventListener("click", nextIssue);

resetBtn.addEventListener("click", () => {
  if (!confirm("Clear all decisions for the currently loaded issues?")) return;
  decisions = {};
  currentIndex = 0;
  renderIssue();
});

exportBtn.addEventListener("click", exportDecisions);

importFile.addEventListener("change", (e) => {
  const file = e.target.files?.[0];
  if (file) importIssues(file);
});

renderIssue();
