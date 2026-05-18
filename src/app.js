const data = window.artifactData;

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const number = new Intl.NumberFormat("en-US");

function scorePill(value) {
  const className = value >= 75 ? "high" : value >= 55 ? "medium" : "low";
  return `<span class="score-pill ${className}">${value}</span>`;
}

function renderScoreStrip() {
  const summary = data.summary;
  const cards = [
    ["ARR monitored", currency.format(summary.arrMonitored), "synthetic account book"],
    ["Daily fact rows", number.format(summary.dailyRows), "warehouse style grain"],
    ["Avg quality", `${summary.avgQuality}%`, "last 30 days"],
    ["AI ready reports", summary.automationCandidates, "candidate queue"],
  ];
  document.getElementById("heroAccounts").textContent = `${summary.accounts} accounts`;
  document.getElementById("scoreStrip").innerHTML = cards
    .map(
      ([label, value, detail]) => `
        <article>
          <span>${label}</span>
          <strong>${value}</strong>
          <small>${detail}</small>
        </article>
      `
    )
    .join("");
}

function renderPriorityQueue() {
  document.getElementById("priorityRows").innerHTML = data.priorityQueue
    .map(
      (row) => `
        <tr>
          <td><strong>${row.account_id}</strong><small>${currency.format(row.arr_at_risk)} ARR at risk</small></td>
          <td>${row.segment}</td>
          <td>${scorePill(row.risk_score)}</td>
          <td>${scorePill(row.trust_gap_score)}</td>
          <td>${scorePill(row.priority_score)}</td>
        </tr>
      `
    )
    .join("");
}

function renderFindings() {
  document.getElementById("findings").innerHTML = data.findings
    .map((finding, index) => `<p><b>${index + 1}</b>${finding}</p>`)
    .join("");
}

function renderMetricCards() {
  document.getElementById("metricCards").innerHTML = data.metricQueue
    .map(
      (metric) => `
        <article>
          <div>
            <strong>${metric.metric_name}</strong>
            <span>${metric.domain} | ${metric.owner}</span>
          </div>
          <dl>
            <dt>Status</dt><dd>${metric.status}</dd>
            <dt>Quality</dt><dd>${metric.quality_score}</dd>
            <dt>Freshness</dt><dd>${metric.current_freshness_hours}h</dd>
          </dl>
          <p>${metric.certification_blocker}</p>
        </article>
      `
    )
    .join("");
}

function renderAutomationQueue() {
  document.getElementById("automationRows").innerHTML = data.automationQueue
    .map(
      (row) => `
        <article>
          <div>
            <strong>${row.report_name}</strong>
            <span>${row.stakeholder_team} | ${row.cadence}</span>
          </div>
          <div class="bar" aria-label="Automation readiness ${row.automation_readiness}">
            <i style="width:${row.automation_readiness}%"></i>
          </div>
          <small>${row.manual_hours} manual hrs | quality ${row.data_quality_score} | AI fit ${row.ai_assist_fit}</small>
        </article>
      `
    )
    .join("");
}

function renderActions() {
  document.getElementById("actionRows").innerHTML = data.actions
    .map(
      (action) => `
        <article>
          <span>${action.domain}</span>
          <strong>${action.account_id}</strong>
          <p>${action.action_type}</p>
          <small>${currency.format(action.expected_value)} expected value | ${action.effort_hours} hrs</small>
        </article>
      `
    )
    .join("");
}

function bindTabs() {
  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      activateTab(button.dataset.tab);
      history.replaceState(null, "", `?surface=${button.dataset.tab}`);
    });
  });
}

function activateTab(tabName) {
  const validTab = document.getElementById(tabName) ? tabName : "cockpit";
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.tab === validTab);
  });
  document.querySelectorAll(".surface").forEach((surface) => {
    surface.classList.toggle("is-active", surface.id === validTab);
  });
}

renderScoreStrip();
renderPriorityQueue();
renderFindings();
renderMetricCards();
renderAutomationQueue();
renderActions();
bindTabs();
activateTab(new URLSearchParams(window.location.search).get("surface") || window.location.hash.replace("#", "") || "cockpit");
