"use strict";

// ─────────────────────────────────────────────────────────────
// State
// ─────────────────────────────────────────────────────────────
let selectedFile = null;
let rawJsonData = null;

// ─────────────────────────────────────────────────────────────
// DOM References
// ─────────────────────────────────────────────────────────────
const startScreen = document.getElementById("startScreen");
const loadingSection = document.getElementById("loadingSection");
const resultsSection = document.getElementById("resultsSection");
const errorSection = document.getElementById("errorSection");

const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const dropPlaceholder = document.getElementById("dropPlaceholder");
const filePreview = document.getElementById("filePreview");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const processBtn = document.getElementById("processBtn");
const processBtnText = document.getElementById("processBtnText");

const loadingStage = document.getElementById("loadingStage");

// ─────────────────────────────────────────────────────────────
// View Management
// ─────────────────────────────────────────────────────────────
function showView(viewElement) {
  [startScreen, loadingSection, resultsSection, errorSection].forEach(el => {
    if (el) {
      el.classList.add("hidden");
      el.classList.remove("active-view");
    }
  });
  if (viewElement) {
    viewElement.classList.remove("hidden");
    // tiny delay to allow CSS transitions
    setTimeout(() => viewElement.classList.add("active-view"), 10);
  }
}

// ─────────────────────────────────────────────────────────────
// File Input Handling
// ─────────────────────────────────────────────────────────────
fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (file) handleFileSelect(file);
});

function handleFileSelect(file) {
  const ext = file.name.split(".").pop().toLowerCase();
  if (!["pdf", "txt"].includes(ext)) {
    showError(
      `Unsupported file type '.${ext}'`,
      "Please upload a PDF (.pdf) or TXT (.txt) file."
    );
    return;
  }

  selectedFile = file;
  dropPlaceholder.classList.add("hidden");
  filePreview.classList.remove("hidden");
  dropZone.classList.add("has-file");
  fileName.textContent = file.name;
  fileSize.textContent = formatBytes(file.size);
  processBtn.disabled = false;
}

function clearFile(event) {
  if (event) event.stopPropagation();
  selectedFile = null;
  fileInput.value = "";
  filePreview.classList.add("hidden");
  dropPlaceholder.classList.remove("hidden");
  dropZone.classList.remove("has-file");
  processBtn.disabled = true;
}

// ─────────────────────────────────────────────────────────────
// Drag & Drop
// ─────────────────────────────────────────────────────────────
dropZone.addEventListener("dragenter", (e) => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragleave", (e) => {
  if (!dropZone.contains(e.relatedTarget)) dropZone.classList.remove("drag-over");
});
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file) handleFileSelect(file);
});

// ─────────────────────────────────────────────────────────────
// Document Processing
// ─────────────────────────────────────────────────────────────
async function processDocument() {
  if (!selectedFile) return;

  showView(loadingSection);
  processBtn.disabled = true;

  const stages = ["upload", "extract", "validate", "route"];
  const delays = [0, 1500, 3500, 5000];
  const msgs = ["Uploading...", "Extracting with AI...", "Validating...", "Routing..."];
  let timers = [];
  
  stages.forEach((s, i) => {
    timers.push(setTimeout(() => {
      setStageActive(s, i, stages);
      loadingStage.textContent = msgs[i];
    }, delays[i]));
  });

  try {
    const formData = new FormData();
    formData.append("file", selectedFile);
    const response = await fetch("/process-claim", { method: "POST", body: formData });
    timers.forEach(clearTimeout);
    markAllStagesDone(stages);
    
    const data = await response.json();
    if (!response.ok) throw { message: data.error || "Processing failed", detail: data.detail };
    
    rawJsonData = data;
    sessionStorage.setItem("synapx_claim_result", JSON.stringify(data));
    await delay(500);
    
    // Hide full report initially
    document.getElementById("fullReportSection").classList.add("hidden");
    document.getElementById("fullReportBtn").textContent = "View Full Report";
    document.getElementById("fullReportBtn").style.display = "inline-block";

    renderResults(data);
    showView(resultsSection);
  } catch (err) {
    timers.forEach(clearTimeout);
    resetStages(stages);
    showError(err.message || "Error", err.detail);
  } finally {
    processBtn.disabled = false;
  }
}

// ─────────────────────────────────────────────────────────────
// Results Rendering
// ─────────────────────────────────────────────────────────────
function renderResults(data) {
  const { extractedFields, missingFields, recommendedRoute, reasoning } = data;

  // 1. Primary Output (Route & Reasoning)
  renderRouteBadge(recommendedRoute);
  document.getElementById("reasoningText").textContent = reasoning;
  
  const summaryJson = { recommendedRoute, reasoning };
  document.getElementById("summaryJsonContent").innerHTML = syntaxHighlight(JSON.stringify(summaryJson, null, 2));

  // 2. Full Report Stats
  const missingMandatory = missingFields.length;

  // 3. Missing Fields
  const mCard = document.getElementById("missingFieldsCard");
  if (missingFields.length > 0) {
    mCard.classList.remove("hidden");
    document.getElementById("missingCountBadge").textContent = `${missingMandatory} Missing`;
    const list = document.getElementById("missingFieldsList");
    list.innerHTML = "";
    missingFields.forEach(f => {
      const chip = document.createElement("div");
      chip.className = "missing-chip";
      chip.textContent = f;
      list.appendChild(chip);
    });
  } else {
    mCard.classList.add("hidden");
  }

  // 4. Extracted Fields Grid
  const grid = document.getElementById("extractedFieldsContainer");
  grid.innerHTML = "";
  
  // Define nice labels for display
  const LABELS = {
    policyNumber: "Policy No", claimNumber: "Claim No", policyholderName: "Policyholder", effectiveDates: "Dates",
    address: "Address", city: "City", pinCode: "PIN", mobile: "Mobile", email: "Email",
    incidentDate: "Inc. Date", incidentTime: "Inc. Time", incidentLocation: "Inc. Location", incidentDescription: "Description",
    claimant: "Claimant", thirdParties: "3rd Parties", contactDetails: "Contact",
    assetType: "Asset", assetId: "Asset ID", estimatedDamage: "Est. Damage", initialEstimate: "Init. Estimate", claimType: "Type", attachments: "Attachments",
    declaration: "Declaration", declarationDate: "Decl. Date", signature: "Signature"
  };

  const MONETARY = new Set(["estimatedDamage", "initialEstimate"]);
  const valueColor = recommendedRoute === "Manual Review" ? "var(--green)" : "var(--text-main)";

  Object.entries(extractedFields).forEach(([key, val]) => {
    const isNull = val === null || val === "" || val === undefined;
    const isMon = MONETARY.has(key);
    
    const div = document.createElement("div");
    div.className = `field-item ${isNull ? "missing" : ""}`;
    
    const label = document.createElement("div");
    label.className = "field-label";
    label.textContent = LABELS[key] || key;
    
    const valDiv = document.createElement("div");
    if (isNull) {
      valDiv.className = "field-value null-value";
      valDiv.textContent = "NULL";
    } else if (isMon) {
      valDiv.className = "field-value numeric-value";
      valDiv.textContent = `₹${Number(val).toLocaleString("en-IN")}`;
      valDiv.style.color = valueColor;
    } else {
      valDiv.className = "field-value";
      valDiv.textContent = String(val);
      valDiv.style.color = valueColor;
    }
    
    div.appendChild(label);
    div.appendChild(valDiv);
    grid.appendChild(div);
  });

  // 5. Full JSON
  document.getElementById("jsonContent").innerHTML = syntaxHighlight(JSON.stringify(data, null, 2));
}

function toggleFullReport() {
  const section = document.getElementById("fullReportSection");
  const btn = document.getElementById("fullReportBtn");
  if (section.classList.contains("hidden")) {
    section.classList.remove("hidden");
    btn.style.display = "none";
    setTimeout(() => section.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
  }
}

// ─────────────────────────────────────────────────────────────
// Utilities
// ─────────────────────────────────────────────────────────────
function setStageActive(stageId, activeIdx, stages) {
  stages.forEach((s, idx) => {
    const el = document.getElementById(`stage-${s}`);
    if (!el) return;
    if (idx < activeIdx) el.className = "process-stage done";
    else if (idx === activeIdx) el.className = "process-stage active";
    else el.className = "process-stage";
  });
}
function markAllStagesDone(stages) {
  stages.forEach(s => {
    const el = document.getElementById(`stage-${s}`);
    if (el) el.className = "process-stage done";
  });
  loadingStage.textContent = "Finalizing...";
}
function resetStages(stages) {
  stages.forEach(s => {
    const el = document.getElementById(`stage-${s}`);
    if (el) el.className = "process-stage";
  });
}

const ROUTE_CONFIG = {
  "Manual Review": { cls: "route-manual-review", color: "var(--red)" },
  "Investigation Flag": { cls: "route-investigation-flag", color: "var(--amber)" },
  "Specialist Queue": { cls: "route-specialist-queue", color: "var(--purple)" },
  "Fast-track": { cls: "route-fast-track", color: "var(--green)" },
  "Standard Processing": { cls: "route-standard", color: "var(--blue)" }
};

function renderRouteBadge(route) {
  const badge = document.getElementById("routeBadge");
  const config = ROUTE_CONFIG[route] || { cls: "route-standard", color: "var(--blue)" };
  badge.className = `route-badge-huge ${config.cls}`;
  badge.innerHTML = `<span>${escapeHtml(route)}</span>`;
}

function syntaxHighlight(json) {
  json = json.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, (match) => {
    let cls = "json-number";
    if (/^"/.test(match)) cls = /:$/.test(match) ? "json-key" : "json-string";
    else if (/true|false/.test(match)) cls = "json-bool";
    else if (/null/.test(match)) cls = "json-null";
    return `<span class="${cls}">${match}</span>`;
  });
}

async function copyJson() {
  if (!rawJsonData) return;
  const btn = document.getElementById("copyJsonBtn");
  const orig = btn.textContent;
  try {
    await navigator.clipboard.writeText(JSON.stringify(rawJsonData, null, 2));
    btn.textContent = "Copied!";
    setTimeout(() => btn.textContent = orig, 2000);
  } catch (e) {
    const t = document.createElement("textarea");
    t.value = JSON.stringify(rawJsonData, null, 2);
    document.body.appendChild(t);
    t.select();
    document.execCommand("copy");
    document.body.removeChild(t);
  }
}

function showError(msg, detail = null) {
  document.getElementById("errorMessage").textContent = msg;
  const dEl = document.getElementById("errorDetail");
  if (detail) { dEl.textContent = detail; dEl.classList.remove("hidden"); }
  else { dEl.classList.add("hidden"); }
  showView(errorSection);
}

function clearResults() {
  clearFile();
  rawJsonData = null;
  sessionStorage.removeItem("synapx_claim_result");
  resetStages(["upload", "extract", "validate", "route"]);
  showView(startScreen);
}

function formatBytes(bytes) {
  if (bytes === 0) return "0 B";
  const k = 1024, sizes = ["B", "KB", "MB", "GB"], i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}
function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
function delay(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

// Restore state on reload
document.addEventListener("DOMContentLoaded", () => {
  const saved = sessionStorage.getItem("synapx_claim_result");
  if (saved) {
    try {
      const data = JSON.parse(saved);
      rawJsonData = data;
      document.getElementById("fullReportSection").classList.add("hidden");
      document.getElementById("fullReportBtn").textContent = "View Full Report";
      document.getElementById("fullReportBtn").style.display = "inline-block";
      renderResults(data);
      showView(resultsSection);
    } catch (e) {
      sessionStorage.removeItem("synapx_claim_result");
    }
  }
});
