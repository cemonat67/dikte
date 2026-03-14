(function () {
  const API_URL = "/api/brain/status";

  function safe(v, fallback = "—") {
    if (v === null || v === undefined || v === "") return fallback;
    if (typeof v === "object") return JSON.stringify(v);
    return String(v);
  }

  function escapeHtml(str) {
    return String(str)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function normalizeBrainPayload(data) {
    return {
      status:
        data?.status ||
        data?.health ||
        data?.brain_status ||
        "unknown",
      mode:
        data?.mode ||
        data?.lens ||
        data?.active_mode ||
        "executive",
      summary:
        data?.summary ||
        data?.message ||
        data?.insight ||
        data?.description ||
        "No summary available.",
      recommendation:
        data?.recommendation ||
        data?.next_action ||
        data?.recommended_action ||
        "No recommendation available.",
      reasons:
        data?.reasons ||
        data?.alerts ||
        data?.issues ||
        [],
      lastUpdated:
        data?.last_updated ||
        data?.updated_at ||
        data?.timestamp ||
        data?.checked_at ||
        "—",
      raw: data
    };
  }

  function pillClass(status) {
    const s = String(status || "").toLowerCase();
    if (["ok", "healthy", "online", "active"].includes(s)) return "ok";
    if (["warning", "warn", "monitor", "degraded", "pending"].includes(s)) return "warn";
    return "error";
  }

  function ensureDrawer() {
    if (document.getElementById("aiInsightsDrawer")) return;

    const backdrop = document.createElement("div");
    backdrop.id = "aiInsightsBackdrop";
    backdrop.className = "ai-insights-backdrop";

    const drawer = document.createElement("aside");
    drawer.id = "aiInsightsDrawer";
    drawer.className = "ai-insights-drawer";
    drawer.setAttribute("aria-hidden", "true");

    drawer.innerHTML = `
      <div class="ai-insights-header">
        <div>
          <h3 class="ai-insights-title">AI Insights</h3>
          <div class="ai-insights-subtitle">Executive Summary / Brain Status</div>
        </div>
        <button class="ai-insights-close" id="aiInsightsCloseBtn" type="button">Close</button>
      </div>

      <div class="ai-insights-body" id="aiInsightsBody">
        <div class="ai-insights-card">
          <div class="ai-insights-loading">Loading AI insights...</div>
        </div>
      </div>

      <div class="ai-insights-actions">
        <button class="ai-insights-btn primary" id="aiInsightsRefreshBtn" type="button">Refresh</button>
        <button class="ai-insights-btn" id="aiInsightsCloseBtn2" type="button">Close</button>
      </div>
    `;

    document.body.appendChild(backdrop);
    document.body.appendChild(drawer);

    backdrop.addEventListener("click", closeDrawer);
    document.getElementById("aiInsightsCloseBtn").addEventListener("click", closeDrawer);
    document.getElementById("aiInsightsCloseBtn2").addEventListener("click", closeDrawer);
    document.getElementById("aiInsightsRefreshBtn").addEventListener("click", loadInsights);

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeDrawer();
    });
  }

  function openDrawer() {
    ensureDrawer();
    document.getElementById("aiInsightsBackdrop")?.classList.add("open");
    document.getElementById("aiInsightsDrawer")?.classList.add("open");
    document.getElementById("aiInsightsDrawer")?.setAttribute("aria-hidden", "false");
    loadInsights();
  }

  function closeDrawer() {
    document.getElementById("aiInsightsBackdrop")?.classList.remove("open");
    document.getElementById("aiInsightsDrawer")?.classList.remove("open");
    document.getElementById("aiInsightsDrawer")?.setAttribute("aria-hidden", "true");
  }

  function renderInsights(view) {
    const body = document.getElementById("aiInsightsBody");
    if (!body) return;

    const reasons = Array.isArray(view.reasons)
      ? view.reasons
      : (view.reasons ? [view.reasons] : []);

    body.innerHTML = `
      <div class="ai-insights-card">
        <div class="ai-insights-label">Brain Status</div>
        <div class="ai-insights-value">
          <span class="ai-insights-pill ${pillClass(view.status)}">${escapeHtml(safe(view.status))}</span>
        </div>
      </div>

      <div class="ai-insights-card">
        <div class="ai-insights-label">Mode</div>
        <div class="ai-insights-value">${escapeHtml(safe(view.mode))}</div>
      </div>

      <div class="ai-insights-card">
        <div class="ai-insights-label">Summary</div>
        <div class="ai-insights-value">${escapeHtml(safe(view.summary))}</div>
      </div>

      <div class="ai-insights-card">
        <div class="ai-insights-label">Recommended Action</div>
        <div class="ai-insights-value">${escapeHtml(safe(view.recommendation))}</div>
      </div>

      <div class="ai-insights-card">
        <div class="ai-insights-label">Reasons / Signals</div>
        <div class="ai-insights-value">
          ${
            reasons.length
              ? `<ul class="ai-insights-list">${reasons.map(r => `<li>${escapeHtml(safe(r))}</li>`).join("")}</ul>`
              : `<div class="ai-insights-empty">No active reasons reported.</div>`
          }
        </div>
      </div>

      <div class="ai-insights-card">
        <div class="ai-insights-label">Last Updated</div>
        <div class="ai-insights-value">${escapeHtml(safe(view.lastUpdated))}</div>
      </div>
    `;
  }

  function renderError(message) {
    const body = document.getElementById("aiInsightsBody");
    if (!body) return;
    body.innerHTML = `
      <div class="ai-insights-card">
        <div class="ai-insights-label">Status</div>
        <div class="ai-insights-value">
          <span class="ai-insights-pill error">unavailable</span>
        </div>
      </div>
      <div class="ai-insights-card">
        <div class="ai-insights-label">Message</div>
        <div class="ai-insights-value">${escapeHtml(message || "AI Insights endpoint is unavailable.")}</div>
      </div>
    `;
  }

  async function loadInsights() {
    const body = document.getElementById("aiInsightsBody");
    if (body) {
      body.innerHTML = `
        <div class="ai-insights-card">
          <div class="ai-insights-loading">Loading AI insights...</div>
        </div>
      `;
    }

    try {
      const res = await fetch(API_URL, { cache: "no-store" });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      const view = normalizeBrainPayload(data);
      renderInsights(view);
    } catch (err) {
      renderError(err?.message || "Unknown error");
    }
  }

  function mountTrigger() {
    if (document.getElementById("openAiInsightsBtn")) return;

    const candidates = [
      ".hero-actions",
      ".header-actions",
      ".top-actions",
      ".header-controls",
      ".hero-controls"
    ];

    let host = null;
    for (const sel of candidates) {
      host = document.querySelector(sel);
      if (host) break;
    }

    if (!host) {
      console.warn("[AI Insights] header action container not found");
      return;
    }

    const btn = document.createElement("button");
    btn.id = "openAiInsightsBtn";
    btn.type = "button";
    btn.className = "btn header-green";
    btn.textContent = "AI Insights";
    btn.addEventListener("click", openDrawer);

    host.appendChild(btn);
  }

  function boot() {
    ensureDrawer();
    mountTrigger();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
