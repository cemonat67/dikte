(function () {
  "use strict";

  const BRAND = {
    navy: "#02154e",
    green: "#005530",
    orange: "#f9ba00",
    red: "#D51635",
    ink: "#1f2937",
    soft: "#6b7280",
    line: "rgba(2,21,78,0.12)",
    card: "#ffffff"
  };

  const STATE = {
    facility: "Ekoten",
    period: "30d",
    lens: "cfo",
    summary: null
  };

  function q(sel, root = document) {
    return root.querySelector(sel);
  }

  function qa(sel, root = document) {
    return Array.from(root.querySelectorAll(sel));
  }

  function text(el, value) {
    if (el) el.textContent = value;
  }

  function html(el, value) {
    if (el) el.innerHTML = value;
  }

  function num(v, fallback = 0) {
    const n = Number(v);
    return Number.isFinite(n) ? n : fallback;
  }

  function eur(v) {
    return "€ " + num(v).toLocaleString("en-IE", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  }

  function kg(v) {
    return num(v).toLocaleString("en-IE", {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    }) + " kg";
  }

  function pct(v) {
    return num(v).toLocaleString("en-IE", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }) + "%";
  }

  function clamp(v, min, max) {
    return Math.max(min, Math.min(max, v));
  }

  function findFirst(selectors) {
    for (const sel of selectors) {
      const el = q(sel);
      if (el) return el;
    }
    return null;
  }

  function getSummary() {
    const periodFactor =
      STATE.period === "7d" ? 0.88 :
      STATE.period === "30d" ? 1.00 :
      STATE.period === "90d" ? 1.12 : 1.00;

    const base = {
      totalCo2: 38.4,
      costImpact: 12480,
      waterUse: 186,
      energyUse: 9420,
      efficiency: 78,
      trendDelta: -6,
      riskLevel: "MONITOR"
    };

    const summary = {
      totalCo2: +(base.totalCo2 * periodFactor).toFixed(1),
      costImpact: Math.round(base.costImpact * periodFactor),
      waterUse: Math.round(base.waterUse * periodFactor),
      energyUse: Math.round(base.energyUse * periodFactor),
      efficiency: clamp(
        Math.round(base.efficiency + (STATE.period === "7d" ? 3 : STATE.period === "90d" ? -4 : 0)),
        0,
        100
      ),
      trendDelta: base.trendDelta,
      riskLevel: base.riskLevel
    };

    STATE.summary = summary;
    return summary;
  }

  function bindFilters() {
    const periodSelectors = [
      "#periodFilter",
      "#timeFilter",
      "#periodSelect",
      "select[data-role='period-filter']",
      "select[name='period']"
    ];

    const periodEl = findFirst(periodSelectors);
    if (periodEl) {
      periodEl.value = STATE.period;
      periodEl.addEventListener("change", function () {
        STATE.period = this.value || "30d";
        renderAll();
      });
    }

    const facilitySelectors = [
      "#facilitySelect",
      "select[data-role='facility-filter']",
      "select[name='facility']"
    ];

    const facilityEl = findFirst(facilitySelectors);
    if (facilityEl) {
      facilityEl.addEventListener("change", function () {
        STATE.facility = this.value || "Ekoten";
        renderAll();
      });
    }
  }

  function bindExecutiveLenses() {
    const candidates = qa(
      "[data-lens], .lens-btn, .executive-lens, .executive-lenses button, .persona-switch button"
    );

    if (!candidates.length) return;

    candidates.forEach((btn) => {
      btn.addEventListener("click", function () {
        const nextLens =
          this.dataset.lens ||
          this.getAttribute("data-lens") ||
          (this.textContent || "").toLowerCase();

        if (nextLens.includes("ceo")) STATE.lens = "ceo";
        else if (nextLens.includes("cto")) STATE.lens = "cto";
        else STATE.lens = "cfo";

        candidates.forEach((x) => {
          x.style.outline = "none";
          x.style.boxShadow = "none";
          x.style.borderColor = "rgba(2,21,78,0.12)";
          x.style.background = "#fff";
          x.style.color = BRAND.navy;
        });

        this.style.borderColor = BRAND.orange;
        this.style.background = "rgba(249,186,0,0.14)";
        this.style.color = BRAND.navy;

        renderInsight();
      });
    });

    const defaultBtn = candidates.find((b) => {
      const t = ((b.dataset.lens || b.textContent || "") + "").toLowerCase();
      return t.includes(STATE.lens);
    });

    if (defaultBtn) defaultBtn.click();
  }

  function renderKpis() {
    const s = STATE.summary || getSummary();

    const co2El = findFirst([
      "#kpiTotalCo2",
      "[data-kpi='total-co2']",
      ".kpi-total-co2 .kpi-value",
      ".kpi-co2 .kpi-value"
    ]);

    const costEl = findFirst([
      "#kpiCostImpact",
      "[data-kpi='cost-impact']",
      ".kpi-cost-impact .kpi-value",
      ".kpi-cost .kpi-value"
    ]);

    const waterEl = findFirst([
      "#kpiWaterUse",
      "[data-kpi='water-use']",
      ".kpi-water .kpi-value"
    ]);

    const energyEl = findFirst([
      "#kpiEnergyUse",
      "[data-kpi='energy-use']",
      ".kpi-energy .kpi-value"
    ]);

    text(co2El, kg(s.totalCo2 * 1000));
    text(costEl, eur(s.costImpact));
    text(waterEl, s.waterUse.toLocaleString("en-IE") + " m³");
    text(energyEl, s.energyUse.toLocaleString("en-IE") + " kWh");
  }

  function renderTrendSummary() {
    const s = STATE.summary || getSummary();

    const trendEl = findFirst([
      "#finTrendSummary",
      "#trendSummary",
      "[data-role='trend-summary']",
      ".trend-summary",
      ".summary-trend"
    ]);

    if (!trendEl) return;

    const costEl = findFirst([
      "#finTrendCostSummary",
      "#trendCostSummary",
      "[data-role='trend-cost-summary']",
      ".trend-cost-summary",
      ".summary-trend-cost"
    ]);

    const dir = s.trendDelta <= 0 ? "Improving" : "Rising";
    const color = s.trendDelta <= 0 ? BRAND.green : BRAND.red;

    html(
      trendEl,
      '<span style="font-weight:800;color:' + color + ';">' +
        dir +
        "</span> · Finishing CO₂ trend " +
        (s.trendDelta <= 0 ? "down " : "up ") +
        Math.abs(s.trendDelta) +
        "% versus prior period"
    );

    if (costEl) {
      html(
        costEl,
        '<span style="font-weight:800;color:' + BRAND.navy + ';">' +
          eur(s.costImpact) +
          '</span> · Estimated selected-period cost impact'
      );
    }
  }

  function renderGauge() {
    const s = STATE.summary || getSummary();

    const gaugeValue = clamp(s.efficiency, 0, 100);
    const gaugeEl = findFirst([
      "#efficiencyGauge",
      "#co2EfficiencyGauge",
      "[data-role='efficiency-gauge']",
      ".efficiency-gauge"
    ]);

    const gaugeLabel = findFirst([
      "#efficiencyGaugeLabel",
      "#co2EfficiencyLabel",
      "[data-role='efficiency-label']",
      ".efficiency-label"
    ]);

    const gaugeSub = findFirst([
      "#efficiencyGaugeSubtext",
      "[data-role='efficiency-subtext']",
      ".efficiency-subtext"
    ]);

    if (gaugeEl) {
      let status = "GOOD";
      let color = BRAND.green;

      if (gaugeValue < 65) {
        status = "RISK";
        color = BRAND.red;
      } else if (gaugeValue < 80) {
        status = "WATCH";
        color = BRAND.orange;
      }

      gaugeEl.style.width = "260px";
      gaugeEl.style.height = "130px";
      gaugeEl.style.position = "relative";
      gaugeEl.style.overflow = "hidden";
      gaugeEl.style.margin = "0 auto";
      gaugeEl.style.borderTopLeftRadius = "260px";
      gaugeEl.style.borderTopRightRadius = "260px";
      gaugeEl.style.borderBottomLeftRadius = "0";
      gaugeEl.style.borderBottomRightRadius = "0";
      gaugeEl.style.background =
        "conic-gradient(from 180deg, " +
        color + " 0deg " + (gaugeValue * 1.8) + "deg, #dfe3e8 " + (gaugeValue * 1.8) + "deg 180deg, transparent 180deg 360deg)";
      gaugeEl.style.boxShadow = "none";

      gaugeEl.innerHTML = '<div style="position:absolute;left:50%;bottom:0;transform:translateX(-50%);width:180px;height:90px;background:#fff;border-top-left-radius:180px;border-top-right-radius:180px;"></div>';

      if (gaugeLabel) {
        gaugeLabel.textContent = status;
        gaugeLabel.style.color = color;
        gaugeLabel.style.fontSize = "30px";
        gaugeLabel.style.fontWeight = "800";
        gaugeLabel.style.textAlign = "center";
        gaugeLabel.style.marginTop = "-2px";
      }

      if (gaugeSub) {
        gaugeSub.textContent = gaugeValue.toFixed(0) + "% efficiency";
        gaugeSub.style.color = BRAND.soft;
        gaugeSub.style.fontSize = "14px";
        gaugeSub.style.textAlign = "center";
        gaugeSub.style.marginTop = "6px";
      }
    }
  }

  function renderInsight() {
    const s = STATE.summary || getSummary();

    const insightEl = findFirst([
      "#executiveInsightText",
      "#executiveInsight",
      "[data-role='executive-insight']",
      ".executive-insight"
    ]);

    if (!insightEl) return;

    let message = "";

    if (STATE.lens === "ceo") {
      message =
        "Finishing sits in the boardroom line of sight: efficiency is at " +
        pct(s.efficiency) +
        ", with process stability " +
        (s.trendDelta <= 0 ? "improving" : "under pressure") +
        ". This is the story you tell when margin, sustainability and delivery discipline must appear in one sentence.";
    } else if (STATE.lens === "cto") {
      message =
        "Technical view: finishing energy/water balance remains operationally manageable, but low-efficiency drift will first show up in thermal load, reprocess risk and unstable process consistency. Watch utilities before they become defects wearing a suit.";
    } else {
      message =
        "CFO view: finishing cost exposure is currently " +
        eur(s.costImpact) +
        " for the selected period. Efficiency at " +
        pct(s.efficiency) +
        " suggests cost containment is decent, but every hidden rework loop is basically a tiny invoice with a fake moustache.";
    }

    insightEl.textContent = message;
  }

  function bindExecutiveNavigation() {
    const btn = findFirst([
      "#btnExecutiveView",
      "#executiveNavButton",
      "[data-role='executive-nav']",
      ".btn-executive-nav"
    ]);

    if (!btn) return;

    btn.style.background = BRAND.orange;
    btn.style.color = "#fff";
    btn.style.border = "0";
    btn.style.borderRadius = "12px";
    btn.style.fontWeight = "800";
    btn.style.boxShadow = "0 8px 20px rgba(249,186,0,0.25)";

    btn.onclick = function () {
      const facility = encodeURIComponent(STATE.facility || "Ekoten");
      window.location.href = "executive.html?module=finishing&facility=" + facility + "&lens=" + STATE.lens;
    };
  }

  function styleCharts() {
    if (!window.Chart) return;

    Chart.defaults.color = BRAND.ink;
    Chart.defaults.font.family =
      '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif';
    Chart.defaults.borderColor = BRAND.line;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.boxWidth = 10;
    Chart.defaults.plugins.legend.labels.boxHeight = 10;

    const charts = Object.values(Chart.instances || {});
    charts.forEach((chart) => {
      try {
        if (chart.options && chart.options.plugins && chart.options.plugins.legend) {
          chart.options.plugins.legend.position = "bottom";
        }

        if (chart.options && chart.options.scales) {
          Object.values(chart.options.scales).forEach((axis) => {
            axis.grid = axis.grid || {};
            axis.grid.color = BRAND.line;
            axis.ticks = axis.ticks || {};
            axis.ticks.color = BRAND.ink;
          });
        }

        if (chart.data && Array.isArray(chart.data.datasets)) {
          chart.data.datasets.forEach((ds, i) => {
            ds.borderWidth = ds.borderWidth || 3;
            ds.tension = ds.tension ?? 0.35;
            ds.fill = ds.fill ?? false;

            if (i === 0) {
              ds.borderColor = BRAND.navy;
              ds.backgroundColor = "rgba(2,21,78,0.12)";
            } else if (i === 1) {
              ds.borderColor = BRAND.orange;
              ds.backgroundColor = "rgba(249,186,0,0.18)";
            } else if (i === 2) {
              ds.borderColor = BRAND.green;
              ds.backgroundColor = "rgba(0,85,48,0.18)";
            } else {
              ds.borderColor = BRAND.red;
              ds.backgroundColor = "rgba(213,22,53,0.12)";
            }
          });
        }

        chart.update();
      } catch (err) {
        console.warn("[finishing-engine] chart styling skipped:", err);
      }
    });
  }

  function renderAll() {
    getSummary();
    renderKpis();
    renderTrendSummary();
    renderGauge();
    renderInsight();
    bindExecutiveNavigation();
    styleCharts();
    console.log("[finishing-engine] applied:", {
      facility: STATE.facility,
      period: STATE.period,
      lens: STATE.lens,
      summary: STATE.summary
    });
  }

  function bind() {
    bindFilters();
    bindExecutiveLenses();
    bindExecutiveNavigation();
    renderAll();
    console.log("[finishing-engine] bound");
  }

  window.ZeroFinishingSyntheticEngine = {
    bind,
    renderAll
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();
