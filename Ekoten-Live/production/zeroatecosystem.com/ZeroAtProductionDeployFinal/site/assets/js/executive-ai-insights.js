(function () {
  const API_URL = "http://127.0.0.1:8010/api/brain/status?facility=ekoten";

  function byId(id) {
    return document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function safe(value, fallback = "—") {
    if (value === null || value === undefined || value === "") return fallback;
    if (typeof value === "object") return JSON.stringify(value, null, 2);
    return String(value);
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
        data?.ops_note ||
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
        data?.signals ||
        data?.alerts ||
        data?.issues ||
        [],
      financeNote:
        data?.finance_note ||
        data?.financeNote ||
        "",
      sustainabilityNote:
        data?.sustainability_note ||
        data?.sustainabilityNote ||
        "",
      lastUpdated:
        data?.last_updated ||
        data?.updated_at ||
        data?.timestamp ||
        data?.checked_at ||
        "—"
    };
  }

  function asList(items) {
    const arr = Array.isArray(items) ? items : (items ? [items] : []);
    if (!arr.length) {
      return '<div style="opacity:.78;">No active reasons reported.</div>';
    }
    return '<ul style="margin:8px 0 0 18px; padding:0;">' +
      arr.map(item => `<li style="margin:0 0 6px 0;">${escapeHtml(safe(item))}</li>`).join("") +
      '</ul>';
  }

  function card(label, value) {
    return `
      <div style="
        border:1px solid rgba(100,170,255,.14);
        background:rgba(255,255,255,.03);
        border-radius:14px;
        padding:14px;
        margin-bottom:12px;">
        <div style="
          font-size:11px;
          text-transform:uppercase;
          letter-spacing:.06em;
          color:rgba(220,230,255,.62);
          margin-bottom:8px;">${escapeHtml(label)}</div>
        <div style="font-size:15px; line-height:1.5; color:#f4f7ff;">${value}</div>
      </div>
    `;
  }

  function pill(status) {
    const s = String(status || "").toLowerCase();
    let fg = "#ff8da1";
    let border = "rgba(255,106,136,.30)";
    let bg = "rgba(125,24,47,.18)";

    if (["ok", "healthy", "online", "active"].includes(s)) {
      fg = "#8ff7c1";
      border = "rgba(63,230,138,.28)";
      bg = "rgba(25,94,58,.20)";
    } else if (["warning", "warn", "monitor", "degraded", "pending"].includes(s)) {
      fg = "#ffd166";
      border = "rgba(255,209,102,.30)";
      bg = "rgba(124,95,16,.18)";
    }

    return `<span style="
      display:inline-flex;
      align-items:center;
      gap:6px;
      border-radius:999px;
      padding:5px 10px;
      font-size:12px;
      font-weight:600;
      color:${fg};
      border:1px solid ${border};
      background:${bg};">${escapeHtml(safe(status))}</span>`;
  }

  function renderLoading() {
    return card("Status", "Loading AI insights...");
  }

  function renderError(message) {
    return [
      card("Brain Status", pill("unavailable")),
      card("Message", escapeHtml(message || "AI Insights endpoint is unavailable."))
    ].join("");
  }

  function renderSuccess(view) {
    const blocks = [
      card("Brain Status", pill(view.status)),
      card("Mode", escapeHtml(safe(view.mode))),
      card("Summary", escapeHtml(safe(view.summary))),
      card("Recommended Action", escapeHtml(safe(view.recommendation))),
      card("Reasons / Signals", asList(view.reasons))
    ];

    if (view.financeNote) {
      blocks.push(card("Financial View", escapeHtml(safe(view.financeNote))));
    }

    if (view.sustainabilityNote) {
      blocks.push(card("Sustainability View", escapeHtml(safe(view.sustainabilityNote))));
    }

    blocks.push(card("Last Updated", escapeHtml(safe(view.lastUpdated))));
    return blocks.join("");
  }

  function openModalWithHtml(title, subtitle, html) {
    const backdrop = byId("execModalBackdrop");
    const modalTitle = byId("execModalTitle");
    const modalSub = byId("execModalSub");
    const modalBody = byId("execModalBody");

    if (!backdrop || !modalTitle || !modalSub || !modalBody) {
      console.error("[AI Insights] executive modal elements not found");
      return false;
    }

    modalTitle.textContent = title;
    modalSub.textContent = subtitle;
    modalBody.innerHTML = html;
    backdrop.classList.add("open");
    backdrop.setAttribute("aria-hidden", "false");
    return true;
  }

  function updateModalBody(html) {
    const modalBody = byId("execModalBody");
    if (modalBody) modalBody.innerHTML = html;
  }

  async function openAiInsights() {
    openModalWithHtml(
      "AI Insights",
      "Executive Summary / Brain Status",
      renderLoading()
    );

    try {
      const res = await fetch(API_URL, { cache: "no-store" });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status} on ${API_URL}`);
      }
      const data = await res.json();
      const view = normalizeBrainPayload(data.brain || data);
      updateModalBody(renderSuccess(view));
    } catch (err) {
      updateModalBody(renderError(err?.message || "Unknown error"));
    }
  }

  function boot() {
    const btn = byId("openAiInsightsBtn");
    if (!btn) {
      console.warn("[AI Insights] button not found");
      return;
    }

    btn.addEventListener("click", openAiInsights);
    console.log("[AI Insights] bound to #openAiInsightsBtn");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
