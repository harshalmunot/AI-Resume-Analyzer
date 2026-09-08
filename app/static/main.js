// AI Resume Analyzer - frontend logic (v2: i18n, cover letter, templates, linkedin, coach)
// Author: Harshal Munot

// ---------- global state ----------
let chart = null;
let currentMode = "full";
let CURRENT_TRANSLATIONS = {};
let brototype = "";
let lastReport = null; // stored for the coach
let currentlySelectedTemplate = null;

// ---------- grab all DOM refs ----------
const $ = (id) => document.getElementById(id);
const form = $("analyze-form");
const btn = $("submit-btn");
const btnLabel = $("btn-label");
const errorBox = $("error");
const errorMsg = $("error-msg");
const results = $("results");
const jobmatchResults = $("jobmatch-results");
const fileInput = $("resume");
const fileDrop = $("file-drop");
const fileLabel = $("file-label");
const jdInput = $("job_description");
const jdField = $("jd-field");
const charCount = $("char-count");
const themeToggle = $("theme-toggle");
const modeButtons = document.querySelectorAll(".mode-btn");
const modeTitle = $("mode-title");
const modeSubtitle = $("mode-subtitle");
const langSelect = $("lang-select");

// ---------- theme ----------
const savedTheme = localStorage.getItem("theme") || "dark";
document.documentElement.setAttribute("data-theme", savedTheme);

themeToggle.addEventListener("click", function () {
  const cur = document.documentElement.getAttribute("data-theme");
  const next = cur === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
  if (chart) renderChart(chart._lastData);
});

// ---------- i18n ----------
function applyTranslations(t) {
  CURRENT_TRANSLATIONS = t;
  document.querySelectorAll("[data-i18n]").forEach(function (el) {
    const key = el.getAttribute("data-i18n");
    if (t[key]) el.textContent = t[key];
  });
  // dynamic bits that depend on languages
  modeSubtitle.textContent =
    currentMode === "jobmatch" ? t["sec1_sub_jobmatch"] : t["sec1_sub"];
}

async function loadLang(lang) {
  try {
    const res = await fetch("/api/i18n/" + lang);
    const data = await res.json();
    applyTranslations(data.translations);
  } catch (e) {
    // offline fallback - english
    const res = await fetch("/api/i18n/en");
    const data = await res.json();
    applyTranslations(data.translations);
  }
}

const savedLang = localStorage.getItem("lang") || "en";
langSelect.value = savedLang;
loadLang(savedLang);

langSelect.addEventListener("change", function () {
  localStorage.setItem("lang", langSelect.value);
  loadLang(langSelect.value);
});

// ---------- mode switcher ----------
modeButtons.forEach(function (b) {
  b.addEventListener("click", function () {
    modeButtons.forEach(function (x) {
      x.classList.remove("active");
    });
    b.classList.add("active");
    currentMode = b.dataset.mode;
    applyMode();
    results.classList.add("hidden");
    jobmatchResults.classList.add("hidden");
    errorBox.classList.add("hidden");
  });
});

function applyMode() {
  if (currentMode === "jobmatch") {
    modeTitle.textContent =
      CURRENT_TRANSLATIONS["tab_jobmatch"] || "Job Match Only";
    modeSubtitle.textContent =
      CURRENT_TRANSLATIONS["sec1_sub_jobmatch"] || "Just drop your resume";
    btnLabel.textContent =
      CURRENT_TRANSLATIONS["btn_jobmatch"] || "Find My Best Jobs";
    jdField.style.display = "none";
    jdInput.required = false;
  } else {
    modeTitle.textContent =
      CURRENT_TRANSLATIONS["sec1_title"] || "Upload & Analyze";
    modeSubtitle.textContent =
      CURRENT_TRANSLATIONS["sec1_sub"] || "PDF or DOCX up to 5 MB";
    btnLabel.textContent =
      CURRENT_TRANSLATIONS["btn_analyze"] || "Analyze My Resume";
    jdField.style.display = "";
    jdInput.required = false; // we validate server-side error for full mode
  }
}

// ---------- file drop UI ----------
fileInput.addEventListener("change", function () {
  if (fileInput.files.length > 0)
    fileLabel.textContent = fileInput.files[0].name;
});
["dragenter", "dragover"].forEach(function (ev) {
  fileDrop.addEventListener(ev, function (e) {
    e.preventDefault();
    fileDrop.classList.add("dragover");
  });
});
["dragleave", "drop"].forEach(function (ev) {
  fileDrop.addEventListener(ev, function (e) {
    e.preventDefault();
    fileDrop.classList.remove("dragover");
  });
});
fileDrop.addEventListener("drop", function (e) {
  if (e.dataTransfer.files.length > 0) {
    fileInput.files = e.dataTransfer.files;
    fileLabel.textContent = e.dataTransfer.files[0].name;
  }
});
jdInput.addEventListener("input", function () {
  charCount.textContent = jdInput.value.length.toLocaleString();
});

// ---------- LinkedIn import ----------
$("btn-linkedin").addEventListener("click", async function () {
  const url = $("linkedin-url").value.trim();
  if (!url) {
    showError("Paste a LinkedIn profile URL first.");
    return;
  }
  this.disabled = true;
  this.textContent = "Importing...";
  try {
    const res = await fetch("/api/linkedin/import", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || "LinkedIn import failed");
      return;
    }
    const p = data.profile || {};
    // prefill the name field in cover letter if available
    if (p.name) {
      $("cl-name").value = p.name.split("|")[0].trim();
      showSuccess("Imported profile: " + p.name.split("|")[0].trim());
    }
    if (data.skills && data.skills.length) {
      showSuccess("Found " + data.skills.length + " skills from your profile.");
    }
  } catch (e) {
    showError("LinkedIn import failed: " + e.message);
  } finally {
    this.disabled = false;
    this.textContent = "Import from LinkedIn";
  }
});

// ---------- submit ----------
form.addEventListener("submit", async function (e) {
  e.preventDefault();
  errorBox.classList.add("hidden");
  results.classList.add("hidden");
  jobmatchResults.classList.add("hidden");
  btn.classList.add("loading");
  btn.disabled = true;

  const endpoint =
    currentMode === "jobmatch" ? "/api/job-match" : "/api/analyze";
  const formData = new FormData(form);

  try {
    const response = await fetch(endpoint, { method: "POST", body: formData });
    const data = await response.json();
    if (!response.ok) {
      // if full mode and no JD, politely tell them to switch mode
      throw new Error(data.error || "Analysis failed");
    }
    if (currentMode === "jobmatch") {
      showJobMatchOnlyResults(data);
      jobmatchResults.scrollIntoView({ behavior: "smooth", block: "start" });
    } else {
      showResults(data);
      lastReport = data;
      results.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  } catch (err) {
    errorMsg.textContent = err.message;
    errorBox.classList.remove("hidden");
  } finally {
    btn.classList.remove("loading");
    btn.disabled = false;
  }
});

// ---------- full results ----------
function showResults(data) {
  animateNumber($("ats-score"), data.ats_score, 1200);
  const R = 52;
  const C = 2 * Math.PI * R;
  makeGradient();
  const ring = $("score-ring");
  ring.style.strokeDasharray = C.toFixed(2);
  ring.style.strokeDashoffset = (C * (1 - data.ats_score / 100)).toFixed(2);

  const verdict = getVerdict(data.ats_score);
  $("score-verdict").textContent = verdict.title;
  $("score-tagline").textContent = verdict.tagline;
  $("processing-ms").textContent = "⚡ " + data.processing_ms + " ms";

  renderTags("matched-list", data.matched_keywords, "No overlaps");
  renderTags("missing-list", data.missing_keywords, "Great match!");
  $("matched-count").textContent = (data.matched_keywords || []).length;
  $("missing-count").textContent = (data.missing_keywords || []).length;

  const list = $("suggestions-list");
  list.innerHTML = "";
  (data.suggestions || []).forEach(function (tip, i) {
    const li = document.createElement("li");
    li.textContent = tip;
    li.style.animationDelay = i * 0.08 + "s";
    list.appendChild(li);
  });

  renderChart(data.breakdown);
  renderJobMatches($("job-matches"), data.job_matches || []);
  results.classList.remove("hidden");
}

// ---------- job-match-only results ----------
function showJobMatchOnlyResults(data) {
  $("jm-meta").textContent =
    "⚡ " +
    data.processing_ms +
    " ms | " +
    (data.detected_skills || []).length +
    " skills detected";
  renderTags("detected-skills", data.detected_skills, "No recognized skills");
  renderJobMatches($("jm-job-matches"), data.matches || []);
  jobmatchResults.classList.remove("hidden");
}

function renderJobMatches(container, matches) {
  container.innerHTML = "";
  if (!matches || !matches.length) {
    container.innerHTML =
      "<p style='color:var(--text-muted);'>No matches found.</p>";
    return;
  }
  matches.forEach(function (job, i) {
    const card = document.createElement("div");
    card.className = "job-card";
    card.style.animationDelay = i * 0.1 + "s";
    let barColor =
      job.match_percent >= 75
        ? "#22c55e"
        : job.match_percent >= 50
          ? "#f59e0b"
          : "#ef4444";
    const rank = i + 1;
    const rankLabel =
      rank === 1
        ? "🏆 Best Match"
        : rank === 2
          ? "🥈 Runner Up"
          : rank === 3
            ? "🥉 3rd Best"
            : "#" + rank;

    card.innerHTML = `
            <div class="job-card-header">
                <div><span class="job-rank">${rankLabel}</span><span class="job-category">${esc(job.category)}</span></div>
                <div class="job-match-badge" style="color:${barColor};">${job.match_percent}<small>%</small></div>
            </div>
            <h4 class="job-title">${esc(job.title)}</h4>
            <p class="job-desc">${esc(job.description || "")}</p>
            <div class="job-progress"><div class="job-progress-fill" style="width:${job.match_percent}%;background:${barColor};"></div></div>
            <div class="job-skill-row">
                <div class="job-skill-group">
                    <span class="job-skill-label matched"><span class="dot-green"></span> You have (${job.total_matched}/${job.total_skills})</span>
                    <ul class="tags matched">
                        ${(job.matched_required || []).map((s) => `<li>${esc(s)}</li>`).join("")}
                        ${(job.matched_preferred || []).map((s) => `<li>${esc(s)}</li>`).join("")}
                    </ul>
                </div>
                ${
                  job.missing_required && job.missing_required.length
                    ? `
                <div class="job-skill-group">
                    <span class="job-skill-label missing"><span class="dot-red"></span> Must-learn</span>
                    <ul class="tags missing">${job.missing_required.map((s) => `<li>${esc(s)}</li>`).join("")}</ul>
                </div>`
                    : ""
                }
                ${
                  job.missing_preferred && job.missing_preferred.length
                    ? `
                <div class="job-skill-group">
                    <span class="job-skill-label neutral"><span class="dot-cyan"></span> Nice-to-have</span>
                    <ul class="tags neutral">${job.missing_preferred.map((s) => `<li>${esc(s)}</li>`).join("")}</ul>
                </div>`
                    : ""
                }
            </div>`;
    container.appendChild(card);
  });
}

// ---------- cover letter ----------
$("btn-cover").addEventListener("click", async function () {
  const file = $("cl-resume").files[0];
  const jd = $("cl-jd").value.trim();
  const name = $("cl-name").value.trim();

  if (!file) {
    showError("Upload a resume for the cover letter.");
    return;
  }
  if (!jd) {
    showError("Paste the job description for the cover letter.");
    return;
  }

  this.disabled = true;
  this.textContent = "Generating...";
  const fd = new FormData();
  fd.append("resume", file);
  fd.append("job_description", jd);
  if (name) fd.append("name", name);

  try {
    const res = await fetch("/api/cover-letter", { method: "POST", body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed");
    $("cover-output").textContent = data.cover_letter;
    $("cover-output-wrap").classList.remove("hidden");
    $("btn-cover-download").classList.remove("hidden");
    $("cover-output-wrap").scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    showError(err.message);
  } finally {
    this.disabled = false;
    this.textContent = "Generate Cover Letter";
  }
});

$("btn-cover-download").addEventListener("click", function () {
  const file = $("cl-resume").files[0];
  const jd = $("cl-jd").value.trim();
  const name = $("cl-name").value.trim();
  const fd = new FormData();
  fd.append("resume", file);
  fd.append("job_description", jd);
  if (name) fd.append("name", name);
  // download via a hidden form to a .docx
  const a = document.createElement("a");
  a.href = "/api/cover-letter/export?" + new URLSearchParams({}).toString();
  const hidden = document.createElement("form");
  hidden.method = "POST";
  hidden.action = "/api/cover-letter/export";
  hidden.style.display = "none";
  document.body.appendChild(hidden);
  // re-append all fields
  const fileInput2 = document.createElement("input");
  fileInput2.type = "file";
  fileInput2.name = "resume";
  // can't set files programmatically on detached? copy from original:
  const dt = new DataTransfer();
  dt.items.add(file);
  fileInput2.files = dt.files;
  hidden.appendChild(fileInput2);
  const jdInput2 = document.createElement("input");
  jdInput2.type = "hidden";
  jdInput2.name = "job_description";
  jdInput2.value = jd;
  hidden.appendChild(jdInput2);
  if (name) {
    const n2 = document.createElement("input");
    n2.type = "hidden";
    n2.name = "name";
    n2.value = name;
    hidden.appendChild(n2);
  }
  hidden.submit();
  setTimeout(() => hidden.remove(), 2000);
});

// ---------- templates ----------
async function loadTemplates() {
  try {
    const res = await fetch("/api/templates");
    const data = await res.json();
    const grid = $("templates-grid");
    grid.innerHTML = "";
    data.templates.forEach(function (t) {
      const card = document.createElement("div");
      card.className = "template-card";
      card.style.setProperty("--accent", "#" + t.accent);
      card.innerHTML = `
                <div class="template-thumb" style="font-family:${t.font};">
                    <div class="thumb-name">${esc(t.name)}</div>
                    <div class="thumb-lines"></div>
                </div>
                <h4>${esc(t.name)}</h4>
                <p>${esc(t.description)}</p>
                <small>${esc(t.layout)}</small>
                <div class="btn-row">
                    <button type="button" class="btn-secondary tpl-preview" data-id="${t.id}">👁 Preview</button>
                    <button type="button" class="btn-primary tpl-export" data-id="${t.id}" style="font-size:.85rem;padding:9px 14px;">⬇ Export</button>
                </div>`;
      grid.appendChild(card);
    });
    // bind events
    document.querySelectorAll(".tpl-preview").forEach(function (b) {
      b.addEventListener("click", function () {
        window.open("/api/templates/" + b.dataset.id + "/preview", "_blank");
      });
    });
    document.querySelectorAll(".tpl-export").forEach(function (b) {
      b.addEventListener("click", function () {
        exportTemplate(b.dataset.id);
      });
    });
  } catch (e) {
    showError("Could not load templates: " + e.message);
  }
}
loadTemplates();

function exportTemplate(templateId) {
  const file = $("tpl-resume").files[0];
  if (!file) {
    showTplMsg("error", "Upload your resume first (PDF or DOCX), then Export.");
    return;
  }
  const fd = new FormData();
  fd.append("resume", file);
  const hidden = document.createElement("form");
  hidden.method = "POST";
  hidden.action = "/api/templates/" + templateId + "/export";
  hidden.style.display = "none";
  document.body.appendChild(hidden);
  const fi = document.createElement("input");
  fi.type = "file";
  fi.name = "resume";
  const dt = new DataTransfer();
  dt.items.add(file);
  fi.files = dt.files;
  hidden.appendChild(fi);
  hidden.submit();
  setTimeout(() => hidden.remove(), 2000);
  showTplMsg("success", "Downloading " + templateId + " template...");
}

function showTplMsg(kind, msg) {
  const box = $("tpl-msg");
  box.className =
    "alert " +
    (kind === "error" ? "alert-error" : "alert-success") +
    " tpl-msg";
  box.textContent = msg;
  setTimeout(() => box.classList.add("hidden"), 4000);
}

// ---------- career coach ----------
const coachMessages = $("coach-messages");
$("coach-fab").addEventListener("click", function () {
  $("coach-panel").classList.toggle("hidden");
  if (
    !$("coach-panel").classList.contains("hidden") &&
    !coachMessages.children.length
  ) {
    addCoachMsg(
      "bot",
      CURRENT_TRANSLATIONS["coach_default_msg"] ||
        "Hi! Ask me about your analysis.",
    );
  }
});
$("coach-close").addEventListener("click", function () {
  $("coach-panel").classList.add("hidden");
});
$("coach-form").addEventListener("submit", async function (e) {
  e.preventDefault();
  const text = $("coach-text").value.trim();
  if (!text) return;
  addCoachMsg("user", text);
  $("coach-text").value = "";
  addCoachMsg("bot", "…", true);
  try {
    const res = await fetch("/api/coach", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, context: buildCoachContext() }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "coach error");
    updateCoachLast(data.reply);
    renderQuickQs(data.quick_questions || []);
  } catch (err) {
    updateCoachLast("Sorry, something went wrong: " + err.message);
  }
});

function buildCoachContext() {
  return lastReport || {};
}

function addCoachMsg(who, text, pending) {
  const div = document.createElement("div");
  div.className = "coach-msg " + who;
  div.textContent = text;
  if (pending) div.classList.add("pending");
  coachMessages.appendChild(div);
  coachMessages.scrollTop = coachMessages.scrollHeight;
}
function updateCoachLast(text) {
  const pending = coachMessages.querySelector(".pending");
  if (pending) {
    pending.textContent = text;
    pending.classList.remove("pending");
  } else addCoachMsg("bot", text);
  coachMessages.scrollTop = coachMessages.scrollHeight;
}
function renderQuickQs(qs) {
  const box = $("coach-quick");
  box.innerHTML = "";
  (qs || []).forEach(function (q) {
    const b = document.createElement("button");
    b.className = "coach-chip";
    b.textContent = q;
    b.addEventListener("click", function () {
      $("coach-text").value = q;
      $("coach-form").dispatchEvent(new Event("submit"));
    });
    box.appendChild(b);
  });
}

// ---------- helpers ----------
function esc(s) {
  if (s === null || s === undefined) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderTags(id, items, emptyMsg) {
  const ul = $(id);
  ul.innerHTML = "";
  if (!items || !items.length) {
    const li = document.createElement("li");
    li.textContent = emptyMsg;
    li.style.background = "rgba(160,160,192,0.1)";
    li.style.color = "var(--text-dim)";
    ul.appendChild(li);
    return;
  }
  items.forEach(function (w, i) {
    const li = document.createElement("li");
    li.textContent = w;
    li.style.animationDelay = i * 0.03 + "s";
    ul.appendChild(li);
  });
}

function getVerdict(score) {
  if (score >= 85)
    return {
      title: "Excellent match 🎯",
      tagline: "Well-aligned with this JD. Small tweaks to push further.",
    };
  if (score >= 70)
    return {
      title: "Strong match ✅",
      tagline: "Solid alignment. Add missing keywords + metrics.",
    };
  if (score >= 50)
    return {
      title: "Moderate match ⚠️",
      tagline: "Room to grow. Mirror the JD's vocabulary.",
    };
  return {
    title: "Needs work 🚀",
    tagline: "Big gap. Rewrite skills/bullets to match the JD.",
  };
}

function animateNumber(el, target, duration) {
  const start = performance.now();
  const from = parseInt(el.textContent, 10) || 0;
  function step(now) {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    el.textContent = Math.round(from + (target - from) * eased);
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function makeGradient() {
  const svg = document.querySelector(".score-ring");
  if (svg.querySelector("#ring-grad")) return;
  const ns = "http://www.w3.org/2000/svg";
  const defs = document.createElementNS(ns, "defs");
  const grad = document.createElementNS(ns, "linearGradient");
  grad.setAttribute("id", "ring-grad");
  grad.setAttribute("x1", "0");
  grad.setAttribute("y1", "0");
  grad.setAttribute("x2", "1");
  grad.setAttribute("y2", "1");
  [
    ["0%", "#7c5cff"],
    ["50%", "#22d3ee"],
    ["100%", "#f472b6"],
  ].forEach(function (pair) {
    const s = document.createElementNS(ns, "stop");
    s.setAttribute("offset", pair[0]);
    s.setAttribute("stop-color", pair[1]);
    grad.appendChild(s);
  });
  defs.appendChild(grad);
  svg.prepend(defs);
}

function renderChart(breakdown) {
  const ctx = $("breakdown-chart").getContext("2d");
  if (chart) chart.destroy();
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  const gridColor = isDark ? "rgba(255,255,255,0.06)" : "rgba(15,23,42,0.08)";
  const tickColor = isDark ? "#a0a0c0" : "#475569";
  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Keyword", "Sections", "Formatting", "Semantic"],
      datasets: [
        {
          label: "Score",
          data: [
            breakdown.keyword_coverage,
            breakdown.section_completeness,
            breakdown.formatting,
            breakdown.semantic_similarity,
          ],
          backgroundColor: ["#7c5cff", "#22d3ee", "#f472b6", "#f59e0b"],
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      animation: { duration: 900, easing: "easeOutCubic" },
      scales: {
        y: {
          beginAtZero: true,
          max: 50,
          grid: { color: gridColor },
          ticks: { color: tickColor },
        },
        x: {
          grid: { display: false },
          ticks: { color: tickColor, weight: 600 },
        },
      },
      plugins: { legend: { display: false } },
    },
  });
  chart._lastData = breakdown;
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorBox.classList.remove("hidden");
  errorBox.scrollIntoView({ behavior: "smooth", block: "center" });
}
function showSuccess(msg) {
  errorBox.classList.remove("hidden", "alert-error");
  errorBox.classList.add("alert-success");
  errorMsg.textContent = "✅ " + msg;
  setTimeout(() => errorBox.classList.add("hidden"), 3500);
}

// tab navigation (smooth scroll)
document.querySelectorAll('a[href^="#"]').forEach(function (a) {
  a.addEventListener("click", function (e) {
    const target = document.querySelector(a.getAttribute("href"));
    if (target && target.id !== "how-it-works") {
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      // make sure it's visible (remove hidden)
      target.classList.remove("hidden");
    }
  });
});
