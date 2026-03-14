
    document.getElementById("t").textContent = new Date().toLocaleString();

    const chartText = getComputedStyle(document.documentElement).getPropertyValue('--muted').trim() || '#aab6d6';
    const chartGrid = 'rgba(255,255,255,0.08)';
    const chartBorder = 'rgba(255,255,255,0.28)';

    function baseOpts(){
      return {
        responsive:true,
        maintainAspectRatio:false,
        plugins:{ legend:{ display:false } },
        scales:{
          x:{ ticks:{ color:chartText, maxTicksLimit:6 }, grid:{ color:chartGrid } },
          y:{ ticks:{ color:chartText, maxTicksLimit:5 }, grid:{ color:chartGrid } }
        }
      };
    }

    setTimeout(() => {
    window.__ZERO_CFO_SPARK__ = new Chart(document.getElementById('cfoSpark'), {
      type: 'line',
      data: {
        labels: ['','','D1','D2','D3','D4','D5','D6','D7','',''],
        datasets: [{
          label: 'Risk',
          data: [1200,1200,1200,1400,1600,1500,1700,1650,1800,1800,1800],
          borderColor: '#f9ba00',
          backgroundColor: 'rgba(249,186,0,.12)',
          fill: true,
          tension: .32,
          pointRadius: 0,
          pointHoverRadius: 0,
          pointHitRadius: 6,
          borderWidth: 2,
          spanGaps: true,
          clip: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: { left: 0, right: 0, top: 0, bottom: 0 }
        },
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false }
        },
        scales: {
          x: {
            display: false,
            offset: false,
            bounds: 'data',
            grid: { display: false }
          },
          y: {
            display: false,
            grid: { display: false }
          }
        },
        elements: {
          point: {
            radius: 0,
            hoverRadius: 0,
            hitRadius: 6
          },
          line: {
            capBezierPoints: false
          }
        }
      }
    });

    window.__ZERO_WATER_CHART__ = new Chart(document.getElementById('waterChart'), {
      type:'line',
      data:{
        labels:['Mon','Tue','Wed','Thu','Fri','Sat'],
        datasets:[{
          label:'Water',
          data:[18,20,21,24,26,23],
          borderColor:'#6aa9ff',
          backgroundColor:'rgba(106,169,255,.14)',
          fill:true,
          tension:.32,
          pointRadius:2,
          pointHoverRadius:3,
          borderWidth:2
        }]
      },
      options: baseOpts()
    });

    window.__ZERO_ENERGY_CHART__ = new Chart(document.getElementById('energyChart'), {
      type:'line',
      data:{
        labels:['Mon','Tue','Wed','Thu','Fri','Sat'],
        datasets:[{
          label:'Energy',
          data:[420,435,428,440,452,446],
          borderColor:'#2ee59d',
          backgroundColor:'rgba(46,229,157,.12)',
          fill:true,
          tension:.32,
          pointRadius:2,
          pointHoverRadius:3,
          borderWidth:2
        }]
      },
      options: baseOpts()
    });

    window.__ZERO_CO2_CHART__ = new Chart(document.getElementById('co2Chart'), {
      type:'line',
      data:{
        labels:['Mon','Tue','Wed','Thu','Fri','Sat'],
        datasets: [
{
label: "Risk",
borderColor: "#f9ba00",
backgroundColor: "rgba(249,186,0,0.15)",
fill: true,
tension: 0.45,
pointRadius: 0,
borderWidth: 2,

          data:[12.2,12.5,12.1,12.8,13.0,12.7],
          borderColor:'#6aa9ff',
          backgroundColor:'rgba(106,169,255,.12)',
          fill:true,
          tension:.35,
          pointRadius:2,
          borderWidth:2
        }]
      },
      options: baseOpts()
    });

    window.__ZERO_WW_CHART__ = new Chart(document.getElementById('wwChart'), {
      type:'line',
      data:{
        labels:['Mon','Tue','Wed','Thu','Fri','Sat'],
        datasets: [
{
label: "Risk",
borderColor: "#f9ba00",
backgroundColor: "rgba(249,186,0,0.15)",
fill: true,
tension: 0.45,
pointRadius: 0,
borderWidth: 2,

          data:[42,46,51,48,55,62],
          borderColor:'#ff4d6d',
          backgroundColor:'rgba(255,77,109,.12)',
          fill:true,
          tension:.35,
          pointRadius:2,
          borderWidth:2
        }]
      },
      options: baseOpts()
    });
    }, 100);
  
function renderCeoMiniTrend() {
  console.log("[CEO mini] render start", !!document.getElementById("ceoMiniTrend"), typeof Chart);
  var el = document.getElementById("ceoMiniTrend");
  if (!el || typeof Chart === "undefined") return;
  if (window.__ceoMiniTrendChart) window.__ceoMiniTrendChart.destroy();

  var ctx = el.getContext("2d");
  var g = ctx.createLinearGradient(0, 0, 0, 140);
  g.addColorStop(0, "rgba(46,229,157,0.24)");
  g.addColorStop(1, "rgba(46,229,157,0.02)");

  window.__ceoMiniTrendChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: ["1","2","3","4","5","6","7"],
      datasets: [{
        data: [42, 47, 54, 51, 59, 57, 63],
        borderColor: "#2ee59d",
        backgroundColor: g,
        fill: true,
        tension: 0.42,
        borderWidth: 2.2,
        pointRadius: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      },
      scales: {
        x: { display: false, grid: { display: false } },
        y: { display: false, min: 35, max: 70, grid: { display: false } }
      }
    }
  });
}

function renderCtoMiniPulse() {
  var el = document.getElementById("ctoMiniPulse");
  if (!el || typeof Chart === "undefined") return;
  if (window.__ctoMiniPulseChart) window.__ctoMiniPulseChart.destroy();

  var ctx = el.getContext("2d");
  var g = ctx.createLinearGradient(0, 0, 0, 140);
  g.addColorStop(0, "rgba(106,169,255,0.24)");
  g.addColorStop(1, "rgba(106,169,255,0.02)");

  window.__ctoMiniPulseChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: ["1","2","3","4","5","6","7","8"],
      datasets: [{
        data: [92, 93, 91, 95, 94, 96, 93, 97],
        borderColor: "#6aa9ff",
        backgroundColor: g,
        fill: true,
        tension: 0.28,
        borderWidth: 2,
        pointRadius: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      },
      scales: {
        x: { display: false, grid: { display: false } },
        y: { display: false, min: 88, max: 100, grid: { display: false } }
      }
    }
  });
}




    (function () {
      const up = new URLSearchParams(window.location.search);

      const moduleName = (up.get("module") || "executive").toLowerCase();
      const facility = up.get("facility") || "Ekoten";
      const line = up.get("line") || "";
      const lens = (up.get("lens") || "overview").toLowerCase();
      const risk = (up.get("risk") || "MONITOR").toUpperCase();

      const subtitleMap = {
        fabric: "Executive decision layer for fabric module performance, cost and operational signals",
        finishing: "Executive decision layer for finishing module quality, cost and risk posture",
        executive: "Sustainable decision support system for production stage"
      };

      const prettyModule = moduleName.charAt(0).toUpperCase() + moduleName.slice(1);
      const subtitle = subtitleMap[moduleName] || "Executive decision layer for production module signals";

      const byId = (id) => document.getElementById(id);

      if (byId("execFacility")) byId("execFacility").textContent = facility;
      if (byId("execModule")) byId("execModule").textContent = prettyModule;
      if (byId("execLens")) byId("execLens").textContent = lens;
      if (byId("execRisk")) byId("execRisk").textContent = risk;
      if (byId("execSubtitle")) byId("execSubtitle").textContent = subtitle;

      if (line) {
        const chips = document.querySelector(".chips");
        if (chips && !byId("execLine")) {
          const span = document.createElement("span");
          span.className = "chip";
          span.innerHTML = 'Line: <b id="execLine"></b>';
          chips.insertBefore(span, byId("execRisk").closest(".chip"));
          byId("execLine").textContent = line;
        }
      }

      const backBtn = byId("btnBackDashboard");
      const fabricBtn = byId("btnGoFabric");
      const finishingBtn = byId("btnGoFinishing");

      if (backBtn) {
        backBtn.setAttribute("href", "index.html");
      }

      if (fabricBtn) {
        fabricBtn.setAttribute("href", "fabric-dpp.html?facility=" + encodeURIComponent(facility) + "&line=" + encodeURIComponent(line || "LINE-1"));
      }

      if (finishingBtn) {
        finishingBtn.setAttribute("href", "finishing-dpp.html?facility=" + encodeURIComponent(facility) + "&lens=" + encodeURIComponent(lens || "overview"));
      }

      if (moduleName === "fabric" && fabricBtn) {
        fabricBtn.classList.add("primary");
        if (finishingBtn) finishingBtn.classList.remove("primary");
      }

      if (moduleName === "finishing" && finishingBtn) {
        finishingBtn.classList.add("primary");
        if (fabricBtn) fabricBtn.classList.remove("primary");
      }

      const openModuleHref =
        moduleName === "fabric"
          ? "fabric-dpp.html?facility=" + encodeURIComponent(facility) + "&line=" + encodeURIComponent(line || "LINE-1")
          : "finishing-dpp.html?facility=" + encodeURIComponent(facility) + "&lens=" + encodeURIComponent(lens || "overview");


      function buildModal(role) {
        const roleMap = {
          ceo: {
            title: "CEO Strategic Layer",
            sub: prettyModule + " module — enterprise risk visibility and board decision posture",
            html: `
              <div class="exec-modal-grid">
                <div class="exec-modal-card">
                  <div class="exec-modal-section-head"><h3>Strategic Risk Index</h3></div>
                  <div class="exec-modal-kpi" id="ceoModalStrategicRiskValue">67 / 100</div>
                  <div class="exec-modal-copy" id="ceoModalStrategicRiskTrend">Trend: <b>Rising</b> — operational signals are beginning to translate into enterprise-level risk exposure.</div>
                  <div class="exec-modal-chart-wrap" style="margin-top:12px;padding:10px 12px 8px 12px;min-height:120px;">
                    <div class="exec-modal-chart-title" style="font-size:12px;margin:0 0 8px 0;color:#aab4c7;">Strategic risk trend</div>
                    <canvas id="ceoRiskTrendChart" height="90"></canvas>
                  </div>
                </div>
                <div class="exec-modal-card">
                  <div class="exec-modal-section-head"><h3>Enterprise Signal Map</h3></div>
                  <ul class="exec-modal-list">
                    <li>Margin compression: <b id="signalMargin">HIGH</b></li>
                    <li>Energy exposure: <b id="signalEnergy">MONITOR</b></li>
                    <li>Delivery volatility: <b id="signalDelivery">MONITOR</b></li>
                    <li>Quality escalation: <b id="signalQuality">LOW</b></li>
                  </ul>
                </div>
                <div class="exec-modal-card">
                  <div class="exec-modal-section-head"><h3>Board Scenario Simulator</h3></div>

                  <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;">
                    <button class="btn" id="ceoModalScenarioStabilize">Stabilize</button>
                    <button class="btn" id="ceoModalScenarioDigital">Digital Control</button>
                    <button class="btn" id="ceoModalScenarioIgnore">Ignore</button>
                  </div>

                  <div style="margin-top:12px;font-size:13px;color:#aab4c7;">
                    Simulate board response scenarios and observe risk shift.
                  </div>

                  <div id="ceoModalScenarioResult" style="margin-top:14px;padding:12px 14px;border-radius:10px;background:rgba(249,186,0,0.08);border:1px solid rgba(249,186,0,0.28);">
                    <div style="font-size:12px;color:#f9ba00;font-weight:700;margin-bottom:6px;">Scenario Result</div>
                    <div id="ceoModalScenarioRisk" style="font-size:24px;font-weight:800;color:#fff;">Projected Risk: <span id="ceoModalScenarioRiskValue">62 / 100</span></div>
<div id="riskEquationWidget" style="margin-top:12px;padding:10px 12px;border-radius:10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);font-size:12px;opacity:.98;">
  <div style="font-weight:800;margin-bottom:8px;color:#ffd86b;letter-spacing:.02em;">Risk Composition</div>

  <div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
    <span style="color:#cfd8ea;">Signal Velocity</span>
    <span id="riskTechValue" style="font-weight:800;color:#ff8da1;">0</span>
  </div>

  <div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
    <span style="color:#cfd8ea;">Financial Exposure</span>
    <span id="riskFinancialValue" style="font-weight:800;color:#ffd86b;">0</span>
  </div>

  <div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
    <span style="color:#cfd8ea;">Operational Noise</span>
    <span id="riskOperationalValue" style="font-weight:800;color:#7ee0ff;">0</span>
  </div>

  <div style="display:flex;justify-content:space-between;padding:3px 0;">
    <span style="color:#cfd8ea;">Scenario</span>
    <span id="riskScenarioValue" style="font-weight:800;color:#ffffff;">Stabilize</span>
  </div>
</div>
                    <div id="ceoModalScenarioNarrative" style="margin-top:6px;font-size:13px;line-height:1.45;color:#dbe3f0;">
                      Current board posture keeps the enterprise in monitor mode.
                    </div>
                    
<div id="financialExposure" style="
margin-top:10px;
font-size:13px;
color:#ffd86b;
font-weight:600;">
Financial Exposure: <span id="exposureValue">–</span> / day
</div>
<div id="aiRecommendation" style="
margin-top:8px;
font-size:12px;
color:#8fd3ff;
font-weight:600;">
AI Recommendation: –
</div>
<div style="display:none">
</div>
<div id="strategicProjection" style="margin-top:14px;">
                      <div style="font-size:13px;color:#cfd7ff;font-weight:700;margin-bottom:8px;">Strategic Projection (90 Days)</div>
                      <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;">
                        <div style="padding:10px 10px;border-radius:12px;background:linear-gradient(180deg,rgba(249,186,0,.16),rgba(249,186,0,.06));border:1px solid rgba(249,186,0,.28);">
                          <div style="font-size:11px;color:#f6d77a;text-transform:uppercase;letter-spacing:.04em;">30 Days</div>
                          <div style="margin-top:4px;font-size:24px;line-height:1;font-weight:800;color:#ffd86b;"><span id="risk30">–</span></div>
                          <div style="margin-top:4px;font-size:11px;color:#d8def0;">Near-term risk</div>
                        </div>
                        <div style="padding:10px 10px;border-radius:12px;background:linear-gradient(180deg,rgba(110,168,255,.16),rgba(110,168,255,.06));border:1px solid rgba(110,168,255,.28);">
                          <div style="font-size:11px;color:#9dc2ff;text-transform:uppercase;letter-spacing:.04em;">60 Days</div>
                          <div style="margin-top:4px;font-size:24px;line-height:1;font-weight:800;color:#cfe1ff;"><span id="risk60">–</span></div>
                          <div style="margin-top:4px;font-size:11px;color:#d8def0;">Mid-term trend</div>
                        </div>
                        <div style="padding:10px 10px;border-radius:12px;background:linear-gradient(180deg,rgba(61,220,151,.16),rgba(61,220,151,.06));border:1px solid rgba(61,220,151,.28);">
                          <div style="font-size:11px;color:#7ae8b4;text-transform:uppercase;letter-spacing:.04em;">90 Days</div>
                          <div style="margin-top:4px;font-size:24px;line-height:1;font-weight:800;color:#49f0a8;"><span id="risk90">–</span></div>
                          <div style="margin-top:4px;font-size:11px;color:#d8def0;">Best outlook</div>
                        </div>
                      </div>
                    </div>

                    <div id="aiCooPanel" style="margin-top:14px;padding:12px 14px;border-radius:12px;background:linear-gradient(180deg,rgba(8,22,56,.92),rgba(6,16,40,.96));border:1px solid rgba(143,211,255,.20);box-shadow:inset 0 1px 0 rgba(255,255,255,.04);">
                      <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;">
                        <div>
                          <div style="font-size:12px;color:#8fd3ff;font-weight:800;letter-spacing:.04em;text-transform:uppercase;">AI COO</div>
                          <div style="font-size:16px;color:#ffffff;font-weight:700;margin-top:2px;">Scenario Q&amp;A</div>
                        </div>
                        <div style="font-size:11px;color:#9fb0cf;">Executive quick reasoning layer</div>
                      </div>

                      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;">
                        <button class="btn" id="aiCooWhyBtn" style="font-size:12px;padding:8px 10px;">Why this risk?</button>
                        <button class="btn" id="aiCooIgnoreBtn" style="font-size:12px;padding:8px 10px;">If we ignore this?</button>
                        <button class="btn" id="aiCooActionBtn" style="font-size:12px;padding:8px 10px;">Best board action?</button>
                      </div>

                      <div id="aiCooAnswer" style="margin-top:12px;padding:12px 12px;border-radius:10px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);font-size:13px;line-height:1.5;color:#dbe3f0;">
                        Ask a scenario question to generate an executive brief.
                      </div>
                    </div>

                  </div>
                </div>
                <div class="exec-modal-card">
                  <div class="exec-modal-section-head"><h3>Executive Narrative</h3></div>
                  <div class="exec-modal-copy">Operational volatility is beginning to translate into structural margin pressure. Without visible intervention, the current signal pattern suggests a rising enterprise risk trajectory.</div>
                  <div class="exec-modal-actions" style="margin-top:18px;">
                    <a class="btn" href="index.html">Back to Dashboard</a>
                    <a class="btn primary" href="${openModuleHref}">Open Module</a>
                  </div>
                  <div style="margin-top:18px;border-top:1px solid rgba(255,255,255,0.08);padding-top:14px;">
                    <div style="font-weight:700;margin-bottom:8px;">Board Intervention Threshold</div>
                  <div style="margin-top:10px;">
                    <input
                      id="boardThresholdSlider"
                      type="range"
                      min="35"
                      max="90"
                      step="1"
                      value="60"
                      style="width:100%;accent-color:#f9ba00;cursor:pointer;"
                    />
                    <div style="margin-top:8px;font-size:12px;color:#94a3b8;display:flex;justify-content:space-between;align-items:center;">
                      <span>Board escalation threshold:
                        <strong id="boardThresholdValue" style="color:#cfd8ea;font-weight:800;">60</strong>
                      </span>
                      <span data-board-threshold-state style="padding:2px 8px;border-radius:999px;border:1px solid rgba(255,255,255,.10);color:#cfd8ea;">
                        Stable
                      </span>
                    </div>
                  </div>

                    <div style="height:6px;background:rgba(255,255,255,0.08);border-radius:999px;position:relative;overflow:visible;">
                      <div class="threshold-marker threshold-marker-premium" style="left:60%;"></div>
                      <div id="boardRiskBar" style="height:100%;width:0%;background:#f9ba00;"></div>
                    </div>

                    <div style="font-size:12px;margin-top:6px;color:#9fb0c8;">
                      
                    </div>


<div style="margin-top:22px;border-top:1px solid rgba(255,255,255,0.08);padding-top:14px;">
<div style="font-weight:700;margin-bottom:12px;">Risk Propagation</div>

<div class="risk-flow">
<div class="risk-node">Energy volatility</div>
<div class="risk-arrow">↓</div>
<div class="risk-node">Production delay</div>
<div class="risk-arrow">↓</div>
<div class="risk-node">Margin compression</div>
<div class="risk-arrow">↓</div>
<div class="risk-node">Strategic risk</div>
</div>
</div>

Risk Drivers</div>

                    <div class="risk-driver">
                      <span class="risk-driver-label">Energy cost volatility</span>
                      <div class="risk-bar-wrap"><div class="risk-bar" data-base="80" style="width:80%;background:linear-gradient(90deg,#f9ba00,#ffd86b);box-shadow:0 0 12px rgba(249,186,0,.18);"></div></div>
                      <span class="risk-driver-value" style="color:#ffd86b;">+14</span>
                    </div>

                    <div class="risk-driver">
                      <span class="risk-driver-label">Supply delay</span>
                      <div class="risk-bar-wrap"><div class="risk-bar" data-base="50" style="width:50%;background:linear-gradient(90deg,#6ea8ff,#9dc2ff);box-shadow:0 0 12px rgba(110,168,255,.16);"></div></div>
                      <span class="risk-driver-value" style="color:#cfe1ff;">+8</span>
                    </div>

                    <div class="risk-driver">
                      <span class="risk-driver-label">Wastewater compliance</span>
                      <div class="risk-bar-wrap"><div class="risk-bar" data-base="35" style="width:35%;background:linear-gradient(90deg,#14b8a6,#6ee7d8);box-shadow:0 0 12px rgba(20,184,166,.16);"></div></div>
                      <span class="risk-driver-value" style="color:#8ff5e8;">+5</span>
                    </div>

                    <div class="risk-driver">
                      <span class="risk-driver-label">Quality deviation</span>
                      <div class="risk-bar-wrap"><div class="risk-bar" data-base="20" style="width:20%;background:linear-gradient(90deg,#ff6b6b,#ff9b9b);box-shadow:0 0 12px rgba(255,107,107,.14);"></div></div>
                      <span class="risk-driver-value" style="color:#ffb3b3;">+3</span>
                    </div>
                  </div>
                </div>
              </div>`
          },
          cfo: {
            title: "CFO Detailed PP",
            sub: prettyModule + " module — exposure, hidden cost and margin protection",
            html: `
              <div class="exec-modal-grid">
                <div class="exec-modal-card exec-fintech-hero">
                  <h3>Financial Exposure</h3>
                  <div class="exec-modal-kpi" id="financialExposureValue">€ 477,440</div>
                  <div class="exec-modal-copy">Estimated annual exposure driven by inefficiency, delay, or quality loss signals.</div>
                  <div style="margin-top:12px;margin-bottom:14px;">
                    <button id="cfoDecisionLayerBtn"
                      style="background:#f9ba00;color:#02154e;border:none;border-radius:8px;padding:6px 10px;font-weight:700;font-size:12px;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.15);">
                      CFO Decision Layer
                    </div>

                  <div id="cfoDecisionPanel"
                       style="display:none;margin-top:10px;padding:12px 14px;
                       background:rgba(249,186,0,0.08);
                       border:1px solid rgba(249,186,0,0.35);
                       border-radius:10px;
                       font-size:13px;line-height:1.4;color:#e6edf6;">

                    <div style="font-weight:700;margin-bottom:6px;color:#f9ba00;">
                      CFO Decision Insight
                    </div>

                    <ul style="margin:0;padding-left:16px;">
                      <li>Margin leakage trend active</li>
                      <li>Escalation timing should be tightened</li>
                      <li>Weekly exposure review recommended</li>
                    </ul>

                  <div id="cfoImpactSimulator"
                       style="margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.1);">
                    <div style="font-size:12px;color:#9fb3c8;margin-bottom:6px;">
                      Impact Simulator
                    </div>

                    <div style="display:flex;gap:8px;margin-bottom:8px;">
                      <button data-impact-rate="0.05"
                        style="background:#02154e;color:#fff;border:1px solid #3a4c63;border-radius:6px;padding:4px 8px;font-size:12px;cursor:pointer;">
                        5%
                      </div>

                      <button data-impact-rate="0.10"
                        style="background:#02154e;color:#fff;border:1px solid #3a4c63;border-radius:6px;padding:4px 8px;font-size:12px;cursor:pointer;">
                        10%
                      </div>

                      <button data-impact-rate="0.20"
                        style="background:#02154e;color:#fff;border:1px solid #3a4c63;border-radius:6px;padding:4px 8px;font-size:12px;cursor:pointer;">
                        20%
                      </div>
                    </div>

                    <div id="cfoImpactResult" style="font-size:13px;color:#f9ba00;font-weight:700;"></div>
                  </div>


                  </div>

                  </div>
                  <div class="exec-summary-strip">
                    <div class="exec-summary-pill">
                      <div class="label">Annualized</div>
                      <div class="value">€ 477k</div>
                    </div>
                    <div class="exec-summary-pill">
                      <div class="label">30D Estimate</div>
                      <div class="value">€ 39.2k</div>
                    </div>
                    <div class="exec-summary-pill">
                      <div class="label">Trend</div>
                      <div class="value">Rising</div>
                    </div>
                  </div>

                  <div class="cfo-kpi-bar">
                    <div class="cfo-kpi">
                      <div class="kpi-label">Margin Impact</div>
                      <div class="kpi-value">-0.8%</div>
                    </div>
                    <div class="cfo-kpi">
                      <div class="kpi-label">Risk Velocity</div>
                      <div class="kpi-value">+€220/day</div>
                    </div>
                    <div class="cfo-kpi">
                      <div class="kpi-label">Shock Index</div>
                      <div class="kpi-value shock-up">▲18%</div>
                    </div>
                  </div>

                  <ul class="exec-modal-list" style="margin-top:18px;">
                    <li>Hidden cost is behaving like margin leakage, not isolated incident cost.</li>
                    <li>${prettyModule} should be treated as a controllable financial pocket.</li>
                    <li>Selected range analysis should guide escalation timing.</li>
                  </ul>
                </div>

                <div class="exec-modal-card exec-fintech-panel">
                  <div style="display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;">
                    <h3 style="margin:0;">Period View</h3>
                    <select id="cfoPeriodSelect" style="background:rgba(9,18,40,.65);color:#eaf0ff;border:1px solid rgba(27,44,85,.95);border-radius:12px;padding:10px 12px;font-size:16px;font-weight:500;">
                      <option value="today">Today</option>
                      <option value="yesterday">Yesterday</option>
                      <option value="last7" selected>Last 7 Days</option>
                      <option value="last30">Last 30 Days</option>
                      <option value="custom">Custom Range</option>
                    </select>

                    <div id="cfoCustomRange" style="display:none;gap:8px;align-items:center;flex-wrap:wrap;">
                      <input type="date" id="cfoFromDate" style="background:#08142b;border:1px solid #1b2c55;color:#eaf0ff;padding:8px;border-radius:8px;">
                      <input type="date" id="cfoToDate" style="background:#08142b;border:1px solid #1b2c55;color:#eaf0ff;padding:8px;border-radius:8px;">
                      <button id="cfoApplyRange" class="btn primary" style="padding:8px 14px;">Apply</div>
                    </div>
                  </div>

                  <div class="exec-modal-kpi" id="cfoRangeValue">€ 12,600</div>
                  <div class="exec-modal-copy" id="cfoRangeLabel">Selected range total exposure</div>

                  <div class="exec-summary-strip">
                    <div class="exec-summary-pill">
                      <div class="label">Average</div>
                      <div class="value" id="cfoAvgValue">€ 1,800</div>
                    </div>
                    <div class="exec-summary-pill">
                      <div class="label">Peak</div>
                      <div class="value" id="cfoPeakValue">€ 2,150</div>
                    </div>
                    <div class="exec-summary-pill">
                      <div class="label">Alert Days</div>
                      <div class="value" id="cfoAlertDays">4</div>
                    </div>
                  </div>

                  <div class="exec-modal-chart-wrap" style="margin-top:18px;">
                    <div class="exec-modal-chart-title">Exposure trend</div>
                    <canvas id="execModalChart"></canvas>
                  </div>
                </div>

                <div class="exec-modal-card exec-fintech-panel">
                  <h3>Exposure Ledger</h3>
                  <div class="exec-modal-copy">Bank-style recent exposure history for executive review.</div>
                  <div class="exec-ledger-wrap">
                    <div class="exec-ledger-head">
                      <div>Date</div><div>Exposure</div><div>Status</div><div>Driver</div>
                    </div>
                    <div class="exec-ledger-row">
                      <div>2026-03-07</div><div><strong>€ 1,800</strong></div><div>ACTION</div><div>Quality drift</div>
                    </div>
                    <div class="exec-ledger-row">
                      <div>2026-03-06</div><div><strong>€ 1,650</strong></div><div>MONITOR</div><div>Delay pressure</div>
                    </div>
                    <div class="exec-ledger-row">
                      <div>2026-03-05</div><div><strong>€ 1,700</strong></div><div>ACTION</div><div>Rework loss</div>
                    </div>
                    <div class="exec-ledger-row">
                      <div>2026-03-04</div><div><strong>€ 1,500</strong></div><div>MONITOR</div><div>Yield variance</div>
                    </div>
                  </div>
                </div>

                <div class="exec-modal-card exec-fintech-panel">
                  <h3>Suggested Actions</h3>
                  <ul class="exec-modal-list">
                    <li>Validate cost drivers against current facility setup: <b>${facility}</b></li>
                    <li>Check line relevance: <b>${line || 'n/a'}</b></li>
                    <li>Use module drill-down before formal escalation.</li>
                  </ul>
                  <div class="exec-modal-actions">
                    <a class="btn" href="index.html">Back to Dashboard</a>
                    <a class="btn primary" href="${openModuleHref}">Open Module</a>
                  </div>
                </div>
              </div>`
          },
          cto: {
            title: "CTO Detailed PP",
            sub: prettyModule + " module — system resilience, execution continuity and signal integrity",
            html: `
              <div class="exec-modal-grid">
                <div class="exec-modal-card">
                  <h3>System Health</h3>
                  <div class="exec-modal-kpi">CRITICAL</div>
                  <div class="exec-modal-copy">Executive automation is now exposed to infrastructure fragility. API, views and signal routing need stabilization before trust can scale.</div>
                </div>

                <div class="exec-modal-card">
                  <h3>Technical Exposure</h3>
                  <ul class="exec-modal-list">
                    <li>API availability is under visible pressure.</li>
                    <li>View consistency is fragile at executive layer.</li>
                    <li>Signal confidence may degrade before failure becomes obvious.</li>
                  </ul>
                </div>

                <div class="exec-modal-card">
                  <h3>Observed Context</h3>
                  <ul class="exec-modal-list">
                    <li>Facility: <b>${facility}</b></li>
                    <li>Module: <b>${prettyModule}</b></li>
                    <li>Lens: <b>${lens}</b></li>
                    <li>Line: <b>${line || 'n/a'}</b></li>
                  </ul>
                </div>

                <div class="exec-modal-card">
                  <h3>Execution Continuity</h3>
                  <div class="exec-modal-copy">The real technical risk is not only downtime. It is slow erosion of decision confidence caused by stale data, broken routing and context mismatch.</div>
                </div>

                <div class="exec-modal-card">
                  <h3>What the CTO needs to know</h3>
                  <ul class="exec-modal-list">
                    <li>Broken trust usually starts with data ambiguity, not code failure alone.</li>
                    <li>Executive pages must never show stale, delayed or contextless numbers.</li>
                    <li>Routing, payload consistency and visual clarity are part of system reliability.</li>
                  </ul>
                </div>

                <div class="exec-modal-card">
                  <h3>Technical Response Simulator</h3>

                  <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;">
                    <button class="btn" id="ctoModalScenarioStabilize">Stabilize Stack</button>
                    <button class="btn" id="ctoModalScenarioPatch">Patch Routing</button>
                    <button class="btn" id="ctoModalScenarioIgnore">Ignore Signals</button>
                  </div>

                  <div id="ctoModalScenarioResult" style="margin-top:14px;padding:12px 14px;border-radius:10px;background:rgba(249,186,0,0.08);border:1px solid rgba(249,186,0,0.22);font-size:13px;color:#dbe3f0;">
                    System Risk: <span id="ctoModalScenarioRiskValue" style="color:#ffd86b;font-weight:800;">79</span>
                    <span style="opacity:.7;"> / projected technical state</span>
                  </div>
                </div>

                <div class="exec-modal-card">
                  <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;">
                    <h3 style="margin:0;">Technical Risk Trajectory</h3>
                    <span id="ctoTrajectoryBadge" style="font-size:11px;font-weight:800;padding:6px 10px;border-radius:999px;background:rgba(249,186,0,.12);color:#ffd86b;border:1px solid rgba(249,186,0,.24);letter-spacing:.04em;">STABLE PATH</span>
                  </div>
                  <div style="height:180px;margin-top:10px;padding-bottom:8px">
                    <canvas id="execModalChart"></canvas>
                  </div>
                </div>

                <div class="exec-modal-card">
                  <h3>AI CTO — Recommended Response</h3>
                  <div class="exec-modal-copy" id="ctoModalScenarioNarrative">Stabilize signal paths first. Lock the executive layer to trusted payloads, reduce ambiguity, and restore a clear technical narrative before scaling automation.</div>
                </div>

                <div class="exec-modal-card">
                  <h3>Immediate Priorities</h3>
                  <ul class="exec-modal-list" id="ctoModalScenarioPriorities">
                    <li>Validate API / view health across the active module.</li>
                    <li>Confirm payload freshness before executive interpretation.</li>
                    <li>Prevent silent degradation from reaching board-facing screens.</li>
                  </ul>
                </div>

                <div class="exec-modal-card">
                  <h3>Suggested Actions</h3>
                  <div class="exec-modal-actions">
                    <a class="btn" href="index.html">Back to Dashboard</a>
                    <a class="btn primary" href="${openModuleHref}">Open Module</a>
                  </div>
                </div>
              </div>`
          }
        };
        return roleMap[role] || roleMap.ceo;
      }


      function getCfoPeriodData(period) {
        const map = {
          today: {
            total: "€ 1,800",
            label: "Today total exposure",
            avg: "€ 1,800",
            peak: "€ 1,800",
            alerts: "1",
            labels: ["08:00","10:00","12:00","14:00","16:00","18:00"],
            data: [180, 260, 320, 410, 300, 330]
          },
          yesterday: {
            total: "€ 1,650",
            label: "Yesterday total exposure",
            avg: "€ 1,650",
            peak: "€ 1,900",
            alerts: "1",
            labels: ["08:00","10:00","12:00","14:00","16:00","18:00"],
            data: [140, 220, 280, 390, 310, 310]
          },
          last7: {
            total: "€ 12,600",
            label: "Selected range total exposure",
            avg: "€ 1,800",
            peak: "€ 2,150",
            alerts: "4",
            labels: ["D1","D2","D3","D4","D5","D6","D7"],
            data: [1200, 1400, 1600, 1500, 1700, 1650, 1800]
          },
          last30: {
            total: "€ 39,200",
            label: "Last 30 days total exposure",
            avg: "€ 1,307",
            peak: "€ 2,250",
            alerts: "11",
            labels: ["W1","W2","W3","W4","W5","W6"],
            data: [5200, 6100, 5800, 6700, 7200, 8200]
          }
        };
        return map[period] || map.last7;
      }

      function renderExecModalChart(role, period, customLabels, customData) {
        const cv = byId("execModalChart");
        if (!cv || !window.Chart) return;
        try {
          if (window.__EXEC_MODAL_CHART__) {
            window.__EXEC_MODAL_CHART__.destroy();
          }
        } catch (e) {}

        let data = [1200, 1400, 1600, 1500, 1700, 1650, 1800];
        let labels = ["D1","D2","D3","D4","D5","D6","D7"];

        if ((role === "cfo" || role === "cto") && period === "custom" && Array.isArray(customLabels) && Array.isArray(customData)) {
          labels = customLabels;
          data = customData;
        } else if (role === "cfo") {
          const cfo = getCfoPeriodData(period || "last7");
          data = cfo.data;
          labels = cfo.labels;
        } else if (role === "ceo") {
          data = [72, 74, 73, 76, 78, 77, 79];
        } else if (role === "cto") {
          data = [91, 88, 86, 84, 80, 82, 79];
        }

        const datasetLabel =
          role === "cto" ? "System Risk" :
          role === "cfo" ? "Financial Exposure" :
          "Risk";

        var lineColor = "#f9ba00";
        var fillTop = "rgba(249,186,0,.24)";
        var fillBottom = "rgba(249,186,0,.03)";

        if (role === "cto") {
          var ctoTheme = window.__ZERO_CTO_ACTIVE_THEME__ || "patch";
          if (ctoTheme === "stabilize") {
            lineColor = "#2ee59d";
            fillTop = "rgba(46,229,157,.24)";
            fillBottom = "rgba(46,229,157,.03)";
          } else if (ctoTheme === "ignore") {
            lineColor = "#ff5c5c";
            fillTop = "rgba(255,92,92,.24)";
            fillBottom = "rgba(255,92,92,.03)";
          } else {
            lineColor = "#69a7ff";
            fillTop = "rgba(105,167,255,.24)";
            fillBottom = "rgba(105,167,255,.03)";
          }
        }

        window.__EXEC_MODAL_CHART__ = new Chart(cv, {
          type: "line",
          data: {
            labels: labels,
            datasets: [
{
label: datasetLabel,
data: data,
borderColor: lineColor,
backgroundColor: function(context){
  var chartObj = context.chart;
  var area = chartObj.chartArea;
  if (!area) return fillTop;
  var g = chartObj.ctx.createLinearGradient(0, area.top, 0, area.bottom);
  g.addColorStop(0, fillTop);
  g.addColorStop(1, fillBottom);
  return g;
},
fill: true,
tension: .35,
pointRadius: 2,
pointBackgroundColor: lineColor,
pointBorderColor: lineColor,
borderWidth: 2
}
]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: {
  display: true,
  position: "top",
  labels: {
    color: "#cfd8ea",
    boxWidth: 12,
    boxHeight: 2,
    usePointStyle: true
  }
} },
            scales: {
              x: { ticks: { color: chartText }, grid: { color: chartGrid } },
              y: { ticks: { color: chartText }, grid: { color: chartGrid } }
            }
          }
        });
      }

      function bindCfoPeriodControls() {
        const sel = byId("cfoPeriodSelect");
        const rangeValue = byId("cfoRangeValue");
        const rangeLabel = byId("cfoRangeLabel");
        const avgValue = byId("cfoAvgValue");
        const peakValue = byId("cfoPeakValue");
        const alertDays = byId("cfoAlertDays");
        const custom = byId("cfoCustomRange");
        const applyBtn = byId("cfoApplyRange");
        const fromEl = byId("cfoFromDate");
        const toEl = byId("cfoToDate");
        if (!sel || !rangeValue || !rangeLabel || !avgValue || !peakValue) return;

        function applyPreset() {
          const cfg = getCfoPeriodData(sel.value || "last7");
          rangeValue.textContent = cfg.total;
          rangeLabel.textContent = cfg.label;
          avgValue.textContent = cfg.avg;
          peakValue.textContent = cfg.peak;
          if (alertDays) alertDays.textContent = cfg.alerts || "0";
          renderExecModalChart("cfo", sel.value || "last7");
        }

        sel.onchange = function () {
          if (sel.value === "custom") {
            if (custom) custom.style.display = "flex";
            return;
          }
          if (custom) custom.style.display = "none";
          applyPreset();
        };

        if (applyBtn) {
          applyBtn.onclick = function (e) {
            e.preventDefault();
            const from = fromEl && fromEl.value;
            const to = toEl && toEl.value;
            if (!from || !to) return;

            const start = new Date(from);
            const end = new Date(to);
            if (String(start) === "Invalid Date" || String(end) === "Invalid Date" || end < start) return;

            const days = Math.max(1, Math.round((end - start) / 86400000) + 1);
            const labels = [];
            const data = [];

            for (let i = 0; i < days; i++) {
              const d = new Date(start.getTime() + i * 86400000);
              labels.push(String(d.getMonth() + 1).padStart(2, "0") + "/" + String(d.getDate()).padStart(2, "0"));
              data.push(1350 + (i * 47) + ((i % 3) * 90));
            }

            const total = data.reduce((a, b) => a + b, 0);
            const avg = Math.round(total / data.length);
            const peak = Math.max(...data);

            rangeValue.textContent = "€ " + total.toLocaleString("en-US");
            rangeLabel.textContent = "Custom range total exposure";
            avgValue.textContent = "€ " + avg.toLocaleString("en-US");
            peakValue.textContent = "€ " + peak.toLocaleString("en-US");
            if (alertDays) alertDays.textContent = String(data.filter(v => v >= 1700).length);
            renderExecModalChart("cfo", "custom", labels, data);
          };
        }

        applyPreset();
      }

      function animateRiskValue(el, target) {
        if (!el) return;
        var current = parseInt(String(el.textContent).replace(/[^0-9]/g, ""), 10);
        if (!Number.isFinite(current)) current = target;

        var start = current;
        var end = target;
        var duration = 320;
        var startTime = null;

        function tick(ts) {
          if (!startTime) startTime = ts;
          var progress = Math.min(1, (ts - startTime) / duration);
          var eased = 1 - Math.pow(1 - progress, 3);
          var value = Math.round(start + ((end - start) * eased));
          el.textContent = value + " / 100";
          if (progress < 1) {
            requestAnimationFrame(tick);
          }
        }

        requestAnimationFrame(tick);
      }

      function aiCooSnapshot() {
        var riskText = (byId("ceoModalScenarioRiskValue") && byId("ceoModalScenarioRiskValue").textContent || "").trim();
        var exposureText = (byId("exposureValue") && byId("exposureValue").textContent || "").trim();
        var thresholdText = document.querySelector("#boardThresholdValue") ? document.querySelector("#boardThresholdValue").textContent.trim() : "";
        var r30 = (byId("risk30") && byId("risk30").textContent || "").trim();
        var r60 = (byId("risk60") && byId("risk60").textContent || "").trim();
        var r90 = (byId("risk90") && byId("risk90").textContent || "").trim();
        var rec = (byId("aiRecommendation") && byId("aiRecommendation").textContent || "").replace("AI Recommendation:", "").trim();

        var activeScenario = "current";
        if (byId("ceoModalScenarioStabilize") && byId("ceoModalScenarioStabilize").classList.contains("ceo-active")) activeScenario = "stabilize";
        if (byId("ceoModalScenarioDigital") && byId("ceoModalScenarioDigital").classList.contains("ceo-active")) activeScenario = "digital";
        if (byId("ceoModalScenarioIgnore") && byId("ceoModalScenarioIgnore").classList.contains("ceo-active")) activeScenario = "ignore";

        return {
          scenario: activeScenario,
          riskText: riskText,
          exposureText: exposureText,
          thresholdText: thresholdText,
          risk30: r30,
          risk60: r60,
          risk90: r90,
          recommendation: rec
        };
      }

      function renderAiCooAnswer(mode) {
        var box = byId("aiCooAnswer");
        if (!box) return;

        var s = aiCooSnapshot();
        var answer = "";

        if (mode === "why") {
          answer = "<strong>AI Brief:</strong> Current strategic risk is driven by the active scenario posture, current financial exposure of <strong>" + (s.exposureText || "–") + "/day</strong>, and the signal stack reflected in the 30/60/90 day path (<strong>" + s.risk30 + " → " + s.risk60 + " → " + s.risk90 + "</strong>). This suggests the enterprise remains below escalation, but still requires visible board discipline.";
        } else if (mode === "ignore") {
          answer = "<strong>Likely Outcome:</strong> If the board delays action, operational noise can compound into margin pressure and raise escalation probability against the current threshold of <strong>" + (s.thresholdText || "–") + "</strong>. The scenario posture may remain manageable in the short term, but governance confidence weakens.";
        } else if (mode === "action") {
          answer = "<strong>Recommended Board Action:</strong> Maintain the current control posture, monitor the dominant driver, and align leadership around a single intervention message. Best current move: <strong>" + (s.recommendation || "Maintain executive monitoring.") + "</strong>";
        } else {
          answer = "Ask a scenario question to generate an executive brief.";
        }

        box.innerHTML = answer;
      }

      function bindAiCooPanel() {
        var whyBtn = byId("aiCooWhyBtn");
        var ignoreBtn = byId("aiCooIgnoreBtn");
        var actionBtn = byId("aiCooActionBtn");

        if (whyBtn && !whyBtn.dataset.bound) {
          whyBtn.dataset.bound = "1";
          whyBtn.addEventListener("click", function(){ renderAiCooAnswer("why"); });
        }
        if (ignoreBtn && !ignoreBtn.dataset.bound) {
          ignoreBtn.dataset.bound = "1";
          ignoreBtn.addEventListener("click", function(){ renderAiCooAnswer("ignore"); });
        }
        if (actionBtn && !actionBtn.dataset.bound) {
          actionBtn.dataset.bound = "1";
          actionBtn.addEventListener("click", function(){ renderAiCooAnswer("action"); });
        }
      }

      function renderCeoRiskTrend(values, risk) {
        var canvas = byId("ceoRiskTrendChart");
        if (!canvas || typeof Chart === "undefined") return;

        var stroke = risk < 40 ? "#3ddc97" : (risk < 70 ? "#f9ba00" : "#ff5c5c");
        var fillTop = risk < 40 ? "rgba(61,220,151,0.22)" : (risk < 70 ? "rgba(249,186,0,0.22)" : "rgba(255,92,92,0.22)");
        var fillBottom = risk < 40 ? "rgba(61,220,151,0.02)" : (risk < 70 ? "rgba(249,186,0,0.02)" : "rgba(255,92,92,0.02)");

        if (window.__ceoRiskTrendChart && typeof window.__ceoRiskTrendChart.destroy === "function") {
          window.__ceoRiskTrendChart.destroy();
        }

        var forecast = [null, null, values[3], Math.min(100, Math.max(0, values[3] + (risk >= 70 ? 12 : (risk >= 40 ? -4 : -8))))];
        var escalationZone = [70, 70, 70, 70];

        window.__ceoRiskTrendChart = new Chart(canvas.getContext("2d"), {
          type: "line",
          data: {
            labels: ["Q-3", "Q-2", "Q-1", "Now"],
            datasets: [
              {
                label: "Escalation Zone",
                data: escalationZone,
                borderColor: "rgba(255,92,92,0.55)",
                borderWidth: 1,
                pointRadius: 0,
                pointHoverRadius: 0,
                tension: 0,
                fill: {
                  target: {value: 100},
                  above: "rgba(255,92,92,0.12)"
                }
              },
              {
                label: "Risk",
                data: values,
                borderColor: stroke,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 0,
                tension: 0.42,
                fill: true,
                backgroundColor: (function(ctx){
                  var chart = ctx.chart;
                  var area = chart.chartArea;
                  if (!area) return fillBottom;
                  var g = chart.ctx.createLinearGradient(0, area.top, 0, area.bottom);
                  g.addColorStop(0, fillTop);
                  g.addColorStop(1, fillBottom);
                  return g;
                })
              },
              {
                label: "Forecast",
                data: forecast,
                borderColor: "#8fd3ff",
                borderDash: [6, 6],
                borderWidth: 1.5,
                pointRadius: 0,
                pointHoverRadius: 0,
                tension: 0.35,
                fill: false
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            plugins: {
              legend: {
  display: true,
  position: "top",
  labels: {
    color: "#cfd8ea",
    boxWidth: 12,
    boxHeight: 2,
    usePointStyle: true
  }
},
              tooltip: { enabled: false }
            },
            scales: {
              x: { display: false, grid: { display: false } },
              y: {
                display: false,
                min: 0,
                max: 100,
                grid: { display: false }
              }
            },
            elements: {
              line: { capBezierPoints: true }
            }
          }
        });
      }

      function updateCeoStrategicModal() {
        function parseMoney(text) {
          if (!text) return 0;
          var cleaned = String(text)
            .replace(/€/g, "")
            .replace(/,/g, "")
            .replace(/[^0-9.\-]/g, "")
            .trim();
          var n = Number(cleaned);
          return Number.isFinite(n) ? n : 0;
        }

        var exposureEl = byId("cfoExposureValue") || byId("financialExposureValue");
        var riskEl = byId("ceoModalStrategicRiskValue");
        var trendEl = byId("ceoModalStrategicRiskTrend");
var scenarioRiskEl = byId("ceoModalScenarioRisk");
        var scenarioNarrativeEl = byId("ceoModalScenarioNarrative");
        var narrativeCard = byId("execModalBody") ? byId("execModalBody").querySelector("h3 + .exec-modal-copy, .exec-modal-card .exec-modal-copy") : null;

        if (!exposureEl || !riskEl || !trendEl) return;

        var exposure = parseMoney(exposureEl.textContent);
        var alerts = document.querySelectorAll(".badge.monitor,.badge.alert,.badge.critical,.shock-up,.action-state").length || 2;
        var velocity = exposure >= 450000 ? 72 : (exposure >= 300000 ? 58 : 42);

        var exposureScore = Math.max(0, Math.min(100, Math.round((exposure / 800000) * 100)));
        var alertScore = Math.max(0, Math.min(100, alerts * 18));
        var baseRisk = Math.max(0, Math.min(100, Math.round(
          (exposureScore * 0.40) +
          (alertScore * 0.30) +
          (velocity * 0.30)
        )));

        function setSignalValue(id, value) {
          var el = byId(id);
          if (!el) return;
          el.textContent = value;
          el.style.color =
            value === "HIGH" ? "#ff5c5c" :
            value === "MONITOR" ? "#f9ba00" :
            "#3ddc97";
        }

        function updateEnterpriseSignalMap(risk, scenarioName) {
          var margin = risk >= 70 ? "HIGH" : (risk >= 45 ? "MONITOR" : "LOW");
          var energy = risk >= 60 ? "HIGH" : (risk >= 35 ? "MONITOR" : "LOW");
          var delivery = risk >= 65 ? "HIGH" : (risk >= 40 ? "MONITOR" : "LOW");
          var quality = risk >= 75 ? "HIGH" : (risk >= 50 ? "MONITOR" : "LOW");

          if (scenarioName === "digital") {
            delivery = risk >= 45 ? "MONITOR" : "LOW";
            quality = risk >= 55 ? "MONITOR" : "LOW";
          }

          if (scenarioName === "ignore") {
            margin = risk >= 55 ? "HIGH" : "MONITOR";
            energy = risk >= 50 ? "HIGH" : "MONITOR";
          }

          setSignalValue("signalMargin", margin);
          setSignalValue("signalEnergy", energy);
          setSignalValue("signalDelivery", delivery);
          setSignalValue("signalQuality", quality);
        }

        function emitScenarioEvent(scenarioName, riskValue) {
          window.__ZERO_AGENT_QUEUE__ = window.__ZERO_AGENT_QUEUE__ || [];
          var payload = {
            module: "executive",
            role: "ceo",
            action: "scenario_selected",
            scenario: scenarioName,
            risk: riskValue,
            facility: "Ekoten",
            ts: new Date().toISOString()
          };
          window.__ZERO_AGENT_QUEUE__.push(payload);
          try {
            window.dispatchEvent(new CustomEvent("zero:scenario", { detail: payload }));
          } catch (e) {}
        }

        function clamp(value, min, max) {
          return Math.max(min, Math.min(max, value));
        }

        function getBoardThresholdValue() {
          var slider = byId("boardThresholdSlider");
          if (slider && slider.value !== undefined && slider.value !== null && slider.value !== "") {
            var parsed = parseInt(slider.value, 10);
            if (!isNaN(parsed)) return parsed;
          }

          var thresholdValueEl = byId("boardThresholdValue");
          if (thresholdValueEl) {
            var parsedText = parseInt(String(thresholdValueEl.textContent || "").replace(/[^0-9]/g, ""), 10);
            if (!isNaN(parsedText)) return parsedText;
          }

          var thresholdText = document.querySelector("#boardThresholdValue")
            ? document.querySelector("#boardThresholdValue").textContent.trim()
            : "";
          var parsedFallback = parseInt(String(thresholdText).replace(/[^0-9]/g, ""), 10);
          return isNaN(parsedFallback) ? 60 : parsedFallback;
        }

        function getScenarioDriverState(name, risk, risk30, risk60, risk90) {
          var exposurePerDay = Math.round(risk * 5.5);
          var financialExposureScore = clamp(Math.round(exposurePerDay / 3), 0, 100);

          var velocityDelta = Math.max(0, risk90 - risk30);
          var signalVelocityScore = clamp(Math.round((velocityDelta * 4) + (name === "ignore" ? 12 : name === "digital" ? -6 : 0)), 0, 100);

          var operationalNoiseScore = 42;
          if (name === "stabilize") operationalNoiseScore = 34;
          if (name === "digital") operationalNoiseScore = 22;
          if (name === "ignore") operationalNoiseScore = 78;

          return {
            exposurePerDay: exposurePerDay,
            financialExposureScore: financialExposureScore,
            signalVelocityScore: signalVelocityScore,
            operationalNoiseScore: operationalNoiseScore
          };
        }

        function calculateExecutiveRiskEquation(drivers) {
          var score =
            (drivers.financialExposureScore * 0.45) +
            (drivers.signalVelocityScore * 0.30) +
            (drivers.operationalNoiseScore * 0.25);

          return clamp(Math.round(score), 0, 100);
        }

        function evaluateBoardThresholdState(risk, threshold) {
          if (risk >= threshold) return "Escalated";
          if (risk >= (threshold - 10)) return "Watch";
          return "Stable";
        }

        function applyBoardEscalationVisual(state, risk, threshold) {
          var boardBar = byId("boardRiskBar");
          if (boardBar) {
            boardBar.style.width = risk + "%";
            boardBar.style.transition = "width .28s ease, box-shadow .25s ease, filter .25s ease";
            boardBar.classList.remove("safe", "alert", "escalation");

            if (state === "Escalated") {
              boardBar.classList.add("alert", "escalation");
              boardBar.style.boxShadow = "0 0 0 2px rgba(255,92,92,.18), 0 0 18px rgba(255,92,92,.28)";
              boardBar.style.filter = "saturate(1.08)";
            } else if (state === "Watch") {
              boardBar.classList.add("alert");
              boardBar.style.boxShadow = "0 0 0 2px rgba(249,186,0,.14), 0 0 12px rgba(249,186,0,.18)";
              boardBar.style.filter = "none";
            } else {
              boardBar.classList.add("safe");
              boardBar.style.boxShadow = "0 0 0 2px rgba(61,220,151,.10)";
              boardBar.style.filter = "none";
            }
          }

          var thresholdValueEl = byId("boardThresholdValue");
          if (thresholdValueEl) {
            thresholdValueEl.textContent = String(threshold);
            thresholdValueEl.style.color =
              state === "Escalated" ? "#ff8da1" :
              state === "Watch" ? "#ffd86b" :
              "#7ae8b4";
            thresholdValueEl.style.fontWeight = "800";
          }

          var thresholdMeta = document.querySelector('[data-board-threshold-state]');
          if (thresholdMeta) {
            thresholdMeta.textContent = state;
            thresholdMeta.style.fontWeight = "800";
            thresholdMeta.style.transition = "all .22s ease";

            if (state === "Escalated") {
              thresholdMeta.style.color = "#ffb3bd";
              thresholdMeta.style.background = "rgba(255,92,92,.14)";
              thresholdMeta.style.borderColor = "rgba(255,92,92,.32)";
              thresholdMeta.style.boxShadow = "0 0 0 1px rgba(255,92,92,.16), 0 0 14px rgba(255,92,92,.12)";
            } else if (state === "Watch") {
              thresholdMeta.style.color = "#ffe08a";
              thresholdMeta.style.background = "rgba(249,186,0,.14)";
              thresholdMeta.style.borderColor = "rgba(249,186,0,.30)";
              thresholdMeta.style.boxShadow = "0 0 0 1px rgba(249,186,0,.12), 0 0 12px rgba(249,186,0,.10)";
            } else {
              thresholdMeta.style.color = "#9af0c2";
              thresholdMeta.style.background = "rgba(61,220,151,.12)";
              thresholdMeta.style.borderColor = "rgba(61,220,151,.26)";
              thresholdMeta.style.boxShadow = "0 0 0 1px rgba(61,220,151,.10)";
            }
          }

          var scenarioRiskValueEl = byId("ceoModalScenarioRiskValue");
          if (scenarioRiskValueEl) {
            scenarioRiskValueEl.style.transition = "color .22s ease, text-shadow .22s ease";
            if (state === "Escalated") {
              scenarioRiskValueEl.style.color = "#ffb3bd";
              scenarioRiskValueEl.style.textShadow = "0 0 16px rgba(255,92,92,.20)";
            } else if (state === "Watch") {
              scenarioRiskValueEl.style.color = "#ffe08a";
              scenarioRiskValueEl.style.textShadow = "0 0 14px rgba(249,186,0,.16)";
            } else {
              scenarioRiskValueEl.style.color = "#9af0c2";
              scenarioRiskValueEl.style.textShadow = "0 0 12px rgba(61,220,151,.14)";
            }
          }
        }

        function syncRiskCompositionWidget(name, drivers, risk30, risk60, risk90, threshold, thresholdState) {
          var riskTechValueEl = byId("riskTechValue");
          var riskFinancialValueEl = byId("riskFinancialValue");
          var riskOperationalValueEl = byId("riskOperationalValue");
          var riskScenarioValueEl = byId("riskScenarioValue");

          if (riskTechValueEl) riskTechValueEl.textContent = String(drivers.signalVelocityScore);
          if (riskFinancialValueEl) riskFinancialValueEl.textContent = String(drivers.financialExposureScore);
          if (riskOperationalValueEl) riskOperationalValueEl.textContent = String(drivers.operationalNoiseScore);

          if (riskScenarioValueEl) {
            riskScenarioValueEl.textContent =
              name === "digital" ? "Digital Control" :
              name === "ignore" ? "Ignore" :
              "Stabilize";
          }

          var r30 = byId("risk30");
          var r60 = byId("risk60");
          var r90 = byId("risk90");
          if (r30) r30.textContent = risk30;
          if (r60) r60.textContent = risk60;
          if (r90) r90.textContent = risk90;

          var driverBars = document.querySelectorAll(".risk-bar");
          driverBars.forEach(function(bar){
            var labelWrap = bar.closest(".risk-driver");
            var labelText = labelWrap ? labelWrap.textContent.toLowerCase() : "";
            var width = parseFloat(bar.dataset.base || "0");

            if (labelText.indexOf("energy") > -1 || labelText.indexOf("signal") > -1) {
              width = clamp(drivers.signalVelocityScore, 8, 100);
            } else if (labelText.indexOf("supply") > -1 || labelText.indexOf("financial") > -1 || labelText.indexOf("margin") > -1) {
              width = clamp(drivers.financialExposureScore, 8, 100);
            } else if (labelText.indexOf("wastewater") > -1 || labelText.indexOf("quality") > -1 || labelText.indexOf("operational") > -1) {
              width = clamp(drivers.operationalNoiseScore, 8, 100);
            }

            bar.style.width = width + "%";
          });

          var scenarioRiskEl = byId("ceoModalScenarioRiskValue");
          if (scenarioRiskEl) {
            scenarioRiskEl.setAttribute("data-threshold-state", thresholdState);
          }
        }


        function renderScenario(name) {
          var risk = baseRisk;
          var trend = "Monitor";
          var narrative = "Current board posture keeps the enterprise in monitor mode.";

          if (name === "stabilize") {
            risk = Math.max(0, baseRisk - 8);
            trend = risk >= 65 ? "Rising" : (risk >= 45 ? "Monitor" : "Stable");
            narrative = "Operational discipline reduces signal noise and lowers enterprise exposure. Board posture shifts toward controlled monitoring.";
          } else if (name === "digital") {
            risk = Math.max(0, baseRisk - 26);
            trend = risk >= 65 ? "Rising" : (risk >= 45 ? "Monitor" : "Stable");
            narrative = "Digital control compresses delay, improves visibility and lowers strategic uncertainty. This is the strongest executive containment path.";
          } else if (name === "ignore") {
            risk = Math.min(100, baseRisk + 14);
            trend = risk >= 65 ? "Rising" : (risk >= 45 ? "Monitor" : "Stable");
            narrative = "Ignoring weak signals increases the probability of margin pressure turning into board-level risk. Enterprise posture worsens.";
          }

          var risk30 = Math.min(100, Math.max(0, risk - 2));
          var risk60 = Math.min(100, Math.max(0, risk - 5));
          var risk90 = Math.min(100, Math.max(0, risk - 8));

          if (name === "digital") {
            risk30 = Math.min(100, Math.max(0, risk - 2));
            risk60 = Math.min(100, Math.max(0, risk - 5));
            risk90 = Math.min(100, Math.max(0, risk - 8));
          } else if (name === "stabilize") {
            risk30 = Math.min(100, Math.max(0, risk - 1));
            risk60 = Math.min(100, Math.max(0, risk - 3));
            risk90 = Math.min(100, Math.max(0, risk - 5));
          } else if (name === "ignore") {
            risk30 = Math.min(100, risk + 6);
            risk60 = Math.min(100, risk + 14);
            risk90 = Math.min(100, risk + 22);
          }

          var drivers = getScenarioDriverState(name, risk, risk30, risk60, risk90);
          risk = calculateExecutiveRiskEquation(drivers);

          if (name === "digital") {
            risk30 = clamp(risk - 1, 0, 100);
            risk60 = clamp(risk - 4, 0, 100);
            risk90 = clamp(risk - 7, 0, 100);
          } else if (name === "stabilize") {
            risk30 = clamp(risk - 1, 0, 100);
            risk60 = clamp(risk - 2, 0, 100);
            risk90 = clamp(risk - 4, 0, 100);
          } else {
            risk30 = clamp(risk + 4, 0, 100);
            risk60 = clamp(risk + 9, 0, 100);
            risk90 = clamp(risk + 15, 0, 100);
          }

          var threshold = getBoardThresholdValue();
          var thresholdState = evaluateBoardThresholdState(risk, threshold);

          riskEl.textContent = risk + " / 100";

          syncRiskCompositionWidget(name, drivers, risk30, risk60, risk90, threshold, thresholdState);

          var exposurePerDay = drivers.exposurePerDay;
          var exposureValueEl = byId("exposureValue");
          if (exposureValueEl) {
            exposureValueEl.textContent = "€" + exposurePerDay;
          }

          var trendValues = [67, 62, 54, risk];
          if (name === "stabilize") trendValues = [67, 62, 58, risk];
          if (name === "digital") trendValues = [67, 62, 54, risk];
          if (name === "ignore") trendValues = [67, 62, 68, risk];

          if (typeof renderCeoRiskTrend === "function") {
            renderCeoRiskTrend(trendValues, risk);
            bindAiCooPanel();
            bindBoardThresholdSlider();
          }
          riskEl.style.transition = "color .25s ease";
          if (risk < 40) {
            riskEl.style.color = "#3ddc97";
          } else if (risk < 70) {
            riskEl.style.color = "#f9ba00";
          } else {
            riskEl.style.color = "#ff5c5c";
          }
          trendEl.innerHTML = "Trend: <b>" + trend + "</b> — strategic risk is now calculated from live financial exposure, alert intensity and signal velocity.";

          if (scenarioRiskEl) {
            var scenarioRiskValueEl = byId("ceoModalScenarioRiskValue");
            if (scenarioRiskValueEl) {
              scenarioRiskValueEl.textContent = risk + " / 100";
            } else {
              scenarioRiskEl.textContent = "Projected Risk: " + risk + " / 100";
            }
          }

          applyBoardEscalationVisual(thresholdState, risk, threshold);
          if (scenarioNarrativeEl) {
            scenarioNarrativeEl.textContent = narrative;
          }

          updateEnterpriseSignalMap(risk, name);
          emitScenarioEvent(name, risk);

          var execNarrativeTitle = Array.from(document.querySelectorAll("#execModalBody .exec-modal-card h3")).find(function(el){
            return el.textContent.trim() === "Executive Narrative";
          });
          if (execNarrativeTitle) {
            var copy = execNarrativeTitle.parentElement.querySelector(".exec-modal-copy");
            if (copy) copy.textContent = narrative;
          }
        }

        function getActiveCeoScenarioName() {
          if (btnDigital && btnDigital.classList.contains("ceo-active")) return "digital";
          if (btnIgnore && btnIgnore.classList.contains("ceo-active")) return "ignore";
          return "stabilize";
        }

        function bindBoardThresholdSlider() {
          var slider = byId("boardThresholdSlider");
          var valueEl = byId("boardThresholdValue");
          if (!slider) return;

          if (!slider.dataset.bound) {
            slider.addEventListener("input", function() {
              var value = parseInt(slider.value, 10);
              if (valueEl && !isNaN(value)) valueEl.textContent = String(value);
              renderScenario(getActiveCeoScenarioName());
            });
            slider.dataset.bound = "1";
          }

          var initial = parseInt(slider.value, 10);
          if (valueEl && !isNaN(initial)) {
            valueEl.textContent = String(initial);
          }
        }

        var btnStabilize = byId("ceoModalScenarioStabilize");
        var btnDigital = byId("ceoModalScenarioDigital");
        var btnIgnore = byId("ceoModalScenarioIgnore");

        [btnStabilize, btnDigital, btnIgnore].forEach(function(btn){
          if (!btn) return;
          btn.onclick = null;
        });

        function setScenarioActive(mode){
          [btnStabilize, btnDigital, btnIgnore].forEach(function(btn){
            if (btn) btn.classList.remove("ceo-active");
          });
          if (mode === "stabilize" && btnStabilize) btnStabilize.classList.add("ceo-active");
          if (mode === "digital" && btnDigital) btnDigital.classList.add("ceo-active");
          if (mode === "ignore" && btnIgnore) btnIgnore.classList.add("ceo-active");
        }

        if (btnStabilize) btnStabilize.onclick = function(){
          renderScenario("stabilize");
          setScenarioActive("stabilize");
          emitScenarioEvent("stabilize", Math.max(0, baseRisk - 8));
        };
        if (btnDigital) btnDigital.onclick = function(){
          renderScenario("digital");
          setScenarioActive("digital");
          emitScenarioEvent("digital", Math.max(0, baseRisk - 26));
        };
        if (btnIgnore) btnIgnore.onclick = function(){
          renderScenario("ignore");
          setScenarioActive("ignore");
          emitScenarioEvent("ignore", Math.min(100, baseRisk + 14));
        };

        setScenarioActive("stabilize");

        renderScenario("stabilize");
      }

      function openExecModal(role) {
        const modalBackdrop = byId("execModalBackdrop");
        const modalTitle = byId("execModalTitle");
        const modalSub = byId("execModalSub");
        const modalBody = byId("execModalBody");
        if (!modalBackdrop || !modalTitle || !modalSub || !modalBody) return;
        const cfg = buildModal(role);
        modalTitle.textContent = cfg.title;
        modalSub.textContent = cfg.sub;
        modalBody.innerHTML = cfg.html;
        modalBackdrop.classList.add("open");
        modalBackdrop.setAttribute("aria-hidden", "false");
        setTimeout(function(){
          if (role === "cfo") {
            bindCfoPeriodControls();
          } else {
            renderExecModalChart(role);
          }
          if (role === "ceo") {
            updateCeoStrategicModal();
          }
          if (role === "cto") {
            bindCtoScenarioControls();
          }
        }, 30);
      }


      function bindCtoScenarioControls() {
        var btnStabilize = byId("ctoModalScenarioStabilize");
        var btnPatch = byId("ctoModalScenarioPatch");
        var btnIgnore = byId("ctoModalScenarioIgnore");
        var riskValue = byId("ctoModalScenarioRiskValue");
        var narrative = byId("ctoModalScenarioNarrative");
        var priorities = byId("ctoModalScenarioPriorities");
        var badge = byId("ctoTrajectoryBadge");

        if (!btnStabilize || !btnPatch || !btnIgnore || !riskValue || !narrative || !priorities) return;

        var buttons = [btnStabilize, btnPatch, btnIgnore];

        function setActive(activeBtn) {
          buttons.forEach(function(btn){
            btn.classList.remove("ceo-active");
          });
          if (activeBtn) activeBtn.classList.add("ceo-active");
        }

        function renderScenario(mode) {
          var risk = 79;
          var copy = "Stabilize signal paths first. Lock the executive layer to trusted payloads, reduce ambiguity, and restore a clear technical narrative before scaling automation.";
          var items = [
            "Validate API / view health across the active module.",
            "Confirm payload freshness before executive interpretation.",
            "Prevent silent degradation from reaching board-facing screens."
          ];

          if (mode === "stabilize") {
            risk = 61;
            copy = "Core stack stabilization should come first. Reduce moving parts, verify service health, and re-establish a trusted baseline before adding new automation pressure.";
            items = [
              "Freeze unstable changes and confirm service baseline.",
              "Run API / view health validation across active executive paths.",
              "Restore a clean trusted state before expanding automation."
            ];
            if (badge) {
              badge.textContent = "STABLE PATH";
              badge.style.background = "rgba(46,229,157,.12)";
              badge.style.color = "#2ee59d";
              badge.style.borderColor = "rgba(46,229,157,.28)";
            }
            setActive(btnStabilize);
            window.__ZERO_CTO_ACTIVE_THEME__ = "stabilize";
          } else if (mode === "patch") {
            risk = 68;
            copy = "Routing correction is the fastest contained response. Fix payload paths, remove ambiguity at the executive layer, and protect decision quality before instability spreads.";
            items = [
              "Patch broken routing and confirm module-to-modal consistency.",
              "Validate signal freshness at key executive touchpoints.",
              "Monitor for silent mismatch between displayed and actual context."
            ];
            if (badge) {
              badge.textContent = "ROUTING FIX";
              badge.style.background = "rgba(105,167,255,.12)";
              badge.style.color = "#69a7ff";
              badge.style.borderColor = "rgba(105,167,255,.28)";
            }
            setActive(btnPatch);
            window.__ZERO_CTO_ACTIVE_THEME__ = "patch";
          } else if (mode === "ignore") {
            risk = 92;
            copy = "Ignoring weak signals will convert technical fragility into executive distrust. Once confidence drops, recovery becomes slower, louder and more expensive.";
            items = [
              "Escalate technical exposure to visible priority immediately.",
              "Protect board-facing views from stale or misleading data.",
              "Prepare containment before degraded trust spreads across modules."
            ];
            if (badge) {
              badge.textContent = "ESCALATING";
              badge.style.background = "rgba(255,92,92,.14)";
              badge.style.color = "#ff5c5c";
              badge.style.borderColor = "rgba(255,92,92,.30)";
            }
            setActive(btnIgnore);
            window.__ZERO_CTO_ACTIVE_THEME__ = "ignore";
          }

          riskValue.textContent = String(risk);
          riskValue.classList.remove("cto-risk-pulse");
          void riskValue.offsetWidth;
          riskValue.classList.add("cto-risk-pulse");
          narrative.textContent = copy;
          priorities.innerHTML = items.map(function(item){
            return "<li>" + item + "</li>";
          }).join("");

          try {
            renderExecModalChart("cto", "custom", ["T0","T+1","T+2","T+3","T+4","T+5","T+6"], 
              mode === "stabilize" ? [79,76,73,70,67,64,61] :
              mode === "patch" ? [79,78,75,73,71,69,68] :
              [79,81,84,86,88,90,92]
            );
          } catch (e) {}
        }

        btnStabilize.addEventListener("click", function(){ renderScenario("stabilize"); });
        btnPatch.addEventListener("click", function(){ renderScenario("patch"); });
        btnIgnore.addEventListener("click", function(){ renderScenario("ignore"); });

        renderScenario("stabilize");
      }

      function closeExecModal() {
        const modalBackdrop = byId("execModalBackdrop");
        if (!modalBackdrop) return;
        modalBackdrop.classList.remove("open");
        modalBackdrop.setAttribute("aria-hidden", "true");
      }

      ["execCardCEO", "execCardCFO", "execCardCTO"].forEach(function(id){
        const el = byId(id);
        if (!el) return;
        el.addEventListener("click", function(){
          openExecModal(el.getAttribute("data-role") || "ceo");
        });
      });

      document.addEventListener("click", function(e){
        const closeBtn = e.target && e.target.closest ? e.target.closest("#execModalClose") : null;
        if (closeBtn) {
          e.preventDefault();
          closeExecModal();
          return;
        }
        const backdrop = byId("execModalBackdrop");
        if (backdrop && e.target === backdrop) {
          closeExecModal();
        }
      });

      document.addEventListener("keydown", function(e){
        if (e.key === "Escape") closeExecModal();
      });

      
function applyCustomRange(){
  const from = byId("cfoFromDate").value;
  const to = byId("cfoToDate").value;
  if(!from || !to) return;

  const rangeValue = byId("cfoRangeValue");
  const avgValue = byId("cfoAvgValue");
  const peakValue = byId("cfoPeakValue");

  const days = 5;
  const base = 1500;

  const data = [];
  const labels = [];

  for(let i=0;i<days;i++){
    data.push(base + Math.round(Math.random()*400));
    labels.push("D"+(i+1));
  }

  const total = data.reduce((a,b)=>a+b,0);
  const avg = Math.round(total/data.length);
  const peak = Math.max(...data);

  rangeValue.textContent = "€ " + total.toLocaleString();
  avgValue.textContent = "€ " + avg.toLocaleString();
  peakValue.textContent = "€ " + peak.toLocaleString();

  renderExecModalChart("cfo","custom",labels,data);
}



      document.title = "Zero@Production — " + prettyModule + " Executive";
    })();
  


document.addEventListener("click", function(e) {
  const btn = e.target.closest("#cfoDecisionLayerBtn");
  if (!btn) return;

  const panel = document.getElementById("cfoDecisionPanel");
  if (!panel) return;

  const current = window.getComputedStyle(panel).display;
  panel.style.display = (current === "none") ? "block" : "none";
});



(function () {
  function parseEuroValue(text) {
    if (!text) return 0;
    const cleaned = String(text)
      .replace(/€/g, "")
      .replace(/,/g, "")
      .replace(/\s+/g, "")
      .trim();
    const value = Number(cleaned);
    return Number.isFinite(value) ? value : 0;
  }

  function formatEuro(value) {
    return "€ " + Math.round(value).toLocaleString("en-IE");
  }

  function findFinancialExposureValue() {
    const all = Array.from(document.querySelectorAll("div,span,p,strong,h1,h2,h3,h4,h5,h6"));
    for (const el of all) {
      const txt = (el.textContent || "").trim();
      if (/€\s*\d[\d,]*/.test(txt)) {
        const parentText = ((el.parentElement && el.parentElement.textContent) || "").toLowerCase();
        const ownText = txt.toLowerCase();
        if (
          parentText.includes("financial exposure") ||
          parentText.includes("estimated impact") ||
          ownText.includes("€")
        ) {
          return parseEuroValue(txt);
        }
      }
    }

    const bodyText = document.body.innerText || "";
    const m = bodyText.match(/Financial Exposure[\s\S]{0,120}?€\s*([\d,]+)/i);
    if (m) return parseEuroValue("€ " + m[1]);

    return 477440;
  }

  function ensureSimulatorButtons() {
    const simulator = document.getElementById("cfoImpactSimulator");
    if (!simulator) return [];

    let buttons = Array.from(simulator.querySelectorAll("button[data-impact-rate]"));

    if (!buttons.length) {
      const candidateButtons = Array.from(simulator.querySelectorAll("button"));
      candidateButtons.forEach((btn) => {
        const txt = (btn.textContent || "").trim();
        const m = txt.match(/(\d+)%/);
        if (m) btn.setAttribute("data-impact-rate", String(Number(m[1]) / 100));
      });
      buttons = Array.from(simulator.querySelectorAll("button[data-impact-rate]"));
    }

    buttons.forEach((btn) => {
      btn.style.transition = "all .18s ease";
      btn.style.border = "1px solid rgba(2,21,78,0.12)";
      btn.style.borderRadius = "10px";
      btn.style.padding = "8px 12px";
      btn.style.cursor = "pointer";
    });

    return buttons;
  }

  function setActiveButton(buttons, activeBtn) {
    buttons.forEach((btn) => {
      const active = btn === activeBtn;
      btn.style.background = active ? "#f9ba00" : "#0b2a5a";
      btn.style.color = active ? "#02154e" : "#ffffff";
      btn.style.fontWeight = active ? "800" : "700";
      btn.style.boxShadow = active ? "0 8px 18px rgba(249,186,0,.28)" : "none";
      btn.style.transform = active ? "translateY(-1px)" : "translateY(0)";
      btn.style.borderColor = active ? "#f9ba00" : "rgba(255,255,255,0.16)";
    });
  }

  function buildExecutiveText(baseExposure, upliftPct, impactValue) {
    const upliftLabel = Math.round(upliftPct * 100) + "%";
    return "Value protection potential: " + formatEuro(impactValue) + " / year — under a " + upliftLabel + " recovery scenario.";
  }

  function bindImpactSimulator() {
    const result = document.getElementById("cfoImpactResult");
    const simulator = document.getElementById("cfoImpactSimulator");
    if (!result || !simulator) return;

    const baseExposure = findFinancialExposureValue();
    const buttons = ensureSimulatorButtons();
    if (!buttons.length) return;

    function update(rate, btn) {
      const impactValue = baseExposure * rate;
      setActiveButton(buttons, btn);
      result.textContent = buildExecutiveText(baseExposure, rate, impactValue);
      result.setAttribute("data-base-exposure", String(baseExposure));
      result.setAttribute("data-impact-rate", String(rate));
      result.setAttribute("data-impact-value", String(Math.round(impactValue)));
    }

    buttons.forEach((btn) => {
      btn.addEventListener("click", function () {
        const rate = Number(btn.getAttribute("data-impact-rate") || "0");
        update(rate, btn);
      });
    });

    const defaultBtn =
      buttons.find((b) => b.textContent.includes("10%")) ||
      buttons[0];

    update(Number(defaultBtn.getAttribute("data-impact-rate") || "0.1"), defaultBtn);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindImpactSimulator);
  } else {
    bindImpactSimulator();
  }
})();



(function () {
  function parseEuroValue(text) {
    if (!text) return 0;
    const cleaned = String(text)
      .replace(/€/g, "")
      .replace(/,/g, "")
      .replace(/\s+/g, "")
      .trim();
    const value = Number(cleaned);
    return Number.isFinite(value) ? value : 0;
  }

  function formatEuro(value) {
    return "€ " + Math.round(value).toLocaleString("en-IE");
  }

  function getBaseExposure() {
    const kpi = document.querySelector(".exec-fintech-hero .exec-modal-kpi");
    if (kpi) {
      const v = parseEuroValue(kpi.textContent || "");
      if (v > 0) return v;
    }

    const all = Array.from(document.querySelectorAll("div,span,strong,h1,h2,h3"));
    for (const el of all) {
      const txt = (el.textContent || "").trim();
      if (/€\s*\d[\d,]*/.test(txt)) {
        const v = parseEuroValue(txt);
        if (v > 1000) return v;
      }
    }
    return 477440;
  }

  function getSimulatorButtons() {
    return Array.from(document.querySelectorAll('#cfoImpactSimulator button[data-impact-rate]'));
  }

  function paintButtons(activeBtn) {
    getSimulatorButtons().forEach((btn) => {
      const active = btn === activeBtn;
      btn.style.background = active ? "#f9ba00" : "#0b2a5a";
      btn.style.color = active ? "#02154e" : "#ffffff";
      btn.style.fontWeight = active ? "800" : "700";
      btn.style.boxShadow = active ? "0 8px 18px rgba(249,186,0,.28)" : "none";
      btn.style.transform = active ? "translateY(-1px)" : "translateY(0)";
      btn.style.borderColor = active ? "#f9ba00" : "rgba(255,255,255,0.16)";
    });
  }

  function updateImpact(rate, btn) {
    const result = document.getElementById("cfoImpactResult");
    if (!result) return;

    const base = getBaseExposure();
    const impact = Math.round(base * rate);

    paintButtons(btn);
    result.textContent =
      "Value protection potential: " + formatEuro(impact) +
      " / year — under a " + Math.round(rate * 100) + "% recovery scenario.";
  }

  document.addEventListener("click", function (e) {
    const btn = e.target.closest('#cfoImpactSimulator button[data-impact-rate]');
    if (!btn) return;

    const rate = Number(btn.getAttribute("data-impact-rate") || "0");
    if (!rate) return;

    updateImpact(rate, btn);
  });

  document.addEventListener("click", function (e) {
    const layerBtn = e.target.closest("#cfoDecisionLayerBtn");
    if (!layerBtn) return;

    setTimeout(function () {
      const buttons = getSimulatorButtons();
      const defaultBtn =
        buttons.find((b) => (b.textContent || "").includes("10%")) ||
        buttons[0];

      if (!defaultBtn) return;

      const panel = document.getElementById("cfoDecisionPanel");
      const result = document.getElementById("cfoImpactResult");
      if (!panel || !result) return;

      const visible = window.getComputedStyle(panel).display !== "none";
      if (!visible) return;

      const rate = Number(defaultBtn.getAttribute("data-impact-rate") || "0.10");
      updateImpact(rate, defaultBtn);
    }, 0);
  });
})();







(function () {
  if (window.__PHASE1_UX_POLISH_APPLIED__) return;
  window.__PHASE1_UX_POLISH_APPLIED__ = true;

  function repulse(el){
    if(!el) return;
    el.classList.remove("phase1-risk-pulse");
    void el.offsetWidth;
    el.classList.add("phase1-risk-pulse");
  }

  function animateResult(){
    var result = document.getElementById("ceoModalScenarioResult");
    if(!result) return;
    result.classList.remove("phase1-result-animate");
    void result.offsetWidth;
    result.classList.add("phase1-result-animate");
    setTimeout(function(){
      result.classList.remove("phase1-result-animate");
    }, 320);
  }

  function findRiskTargets(){
    var ids = [
      "strategicRiskIndexValue",
      "ceoStrategicRiskValue",
      "ceoRiskValue",
      "riskValue",
      "strategicRiskValue"
    ];

    var found = [];
    ids.forEach(function(id){
      var el = document.getElementById(id);
      if(el) found.push(el);
    });

    if(found.length) return found;

    var fallbacks = Array.from(document.querySelectorAll(
      ".risk-value, .strategic-risk-value, [data-role='risk-value']"
    ));

    if(fallbacks.length) return fallbacks;

    var textHits = Array.from(document.querySelectorAll("div,span,strong")).filter(function(el){
      var t = (el.textContent || "").trim();
      return /^(\d{1,3})$/.test(t) || /^(\d{1,3})%$/.test(t);
    }).slice(0, 3);

    return textHits;
  }

  function afterScenarioVisuals(){
    animateResult();
    findRiskTargets().forEach(repulse);
  }

  if (typeof window.renderScenario === "function") {
    var originalRenderScenario = window.renderScenario;
    window.renderScenario = function () {
      var out = originalRenderScenario.apply(this, arguments);
      setTimeout(afterScenarioVisuals, 30);
      return out;
    };
  }

  window.addEventListener("DOMContentLoaded", function(){
    setTimeout(afterScenarioVisuals, 120);
  });
})();



(function(){
  const ESG_ENTRY_STORAGE_KEY = "zero_executive_esg_entry_v1";
  const ESG_EVIDENCE_STORAGE_KEY = "zero_executive_esg_evidence_v1";

  function byId(id){
    return document.getElementById(id);
  }

  function num(v){
    const n = Number(v || 0);
    return Number.isFinite(n) ? n : 0;
  }

  function round1(v){
    return Math.round(v * 10) / 10;
  }

  function getBlankData(){
    return {
      facility: "Ekoten",
      period_label: "",
      electricity_kwh: 0,
      natural_gas_m3: 0,
      steam_ton: 0,
      water_m3: 0,
      industrial_waste_kg: 0,
      domestic_waste_kg: 0,
      forklift_fuel_l: 0,
      vehicle_fuel_l: 0,
      raw_material_transport_tkm: 0,
      product_transport_tkm: 0,
      updated_at: null
    };
  }

  function readStoredData(){
    try{
      const raw = localStorage.getItem(ESG_ENTRY_STORAGE_KEY);
      if(!raw) return getBlankData();
      const parsed = JSON.parse(raw);
      return Object.assign(getBlankData(), parsed || {});
    }catch(e){
      console.warn("ESG storage read failed:", e);
      return getBlankData();
    }
  }

  function writeStoredData(data){
    localStorage.setItem(ESG_ENTRY_STORAGE_KEY, JSON.stringify(data));
  }

  function readEvidence(){
    try{
      const raw = localStorage.getItem(ESG_EVIDENCE_STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    }catch(e){
      console.warn("ESG evidence read failed:", e);
      return null;
    }
  }

  function writeEvidence(data){
    localStorage.setItem(ESG_EVIDENCE_STORAGE_KEY, JSON.stringify(data));
  }

  function clearEvidence(){
    localStorage.removeItem(ESG_EVIDENCE_STORAGE_KEY);
    window.__ZERO_ESG_EVIDENCE__ = null;
    updateEvidenceMeta(null);
    const input = byId("esgInvoiceUpload");
    if(input) input.value = "";
  }

  function updateEvidenceMeta(fileMeta){
    const el = byId("esgInvoiceMeta");
    if(!el) return;
    if(!fileMeta){
      el.textContent = "No invoice uploaded yet.";
      return;
    }
    const kb = Math.round((fileMeta.size || 0) / 1024);
    el.textContent = "Attached: " + (fileMeta.name || "file") + " • " + kb + " KB • " + (fileMeta.type || "unknown") + " • " + new Date(fileMeta.uploaded_at).toLocaleString();
  }

  
function detectInvoiceHint(filename){

  const name = (filename || "").toLowerCase()

  const map = {
    energy:["electric","power","elektrik"],
    water:["water","su"],
    gas:["gas","dogalgaz","naturalgas"]
  }

  let hint=null

  Object.keys(map).forEach(type=>{
    map[type].forEach(k=>{
      if(name.includes(k)) hint=type
    })
  })

  document.querySelectorAll(".esg-section").forEach(el=>{
    el.classList.remove("esg-hint")
  })

  if(!hint) return

  const sectionTitles={
    energy:"Energy",
    water:"Water",
    gas:"Energy"
  }

  document.querySelectorAll(".esg-section h3").forEach(h=>{
    if(h.textContent.trim()===sectionTitles[hint]){
      h.closest(".esg-section").classList.add("esg-hint")
    }
  })

}

function handleEvidenceFile(file){
    if(!file) return;
    const reader = new FileReader();
    reader.onload = function(){
      const payload = {
        name: file.name,
        size: file.size,
        type: file.type,
        uploaded_at: new Date().toISOString(),
        data_url: reader.result
      };
      writeEvidence(payload);
      window.__ZERO_ESG_EVIDENCE__ = payload;
      updateEvidenceMeta(payload);
      detectInvoiceHint(payload.name);
      console.log("ESG evidence saved:", payload.name);
    };
    reader.readAsDataURL(file);
  }

  function collectFormData(){
    return {
      facility: (byId("esgFacility")?.value || "").trim() || "Ekoten",
      period_label: (byId("esgPeriodLabel")?.value || "").trim(),
      electricity_kwh: num(byId("esgElectricityKwh")?.value),
      natural_gas_m3: num(byId("esgNaturalGasM3")?.value),
      steam_ton: num(byId("esgSteamTon")?.value),
      water_m3: num(byId("esgWaterM3")?.value),
      industrial_waste_kg: num(byId("esgIndustrialWasteKg")?.value),
      domestic_waste_kg: num(byId("esgDomesticWasteKg")?.value),
      forklift_fuel_l: num(byId("esgForkliftFuelL")?.value),
      vehicle_fuel_l: num(byId("esgVehicleFuelL")?.value),
      raw_material_transport_tkm: num(byId("esgRawMaterialTransportTkm")?.value),
      product_transport_tkm: num(byId("esgProductTransportTkm")?.value),
      updated_at: new Date().toISOString()
    };
  }

  function fillForm(data){
    byId("esgFacility").value = data.facility || "Ekoten";
    byId("esgPeriodLabel").value = data.period_label || "";
    byId("esgElectricityKwh").value = data.electricity_kwh || "";
    byId("esgNaturalGasM3").value = data.natural_gas_m3 || "";
    byId("esgSteamTon").value = data.steam_ton || "";
    byId("esgWaterM3").value = data.water_m3 || "";
    byId("esgIndustrialWasteKg").value = data.industrial_waste_kg || "";
    byId("esgDomesticWasteKg").value = data.domestic_waste_kg || "";
    byId("esgForkliftFuelL").value = data.forklift_fuel_l || "";
    byId("esgVehicleFuelL").value = data.vehicle_fuel_l || "";
    byId("esgRawMaterialTransportTkm").value = data.raw_material_transport_tkm || "";
    byId("esgProductTransportTkm").value = data.product_transport_tkm || "";
  }

  function computeExecutiveEsgOverlay(data){
    const co2_kg =
      (data.electricity_kwh * 0.42) +
      (data.natural_gas_m3 * 2.00) +
      (data.steam_ton * 180) +
      (data.forklift_fuel_l * 2.68) +
      (data.vehicle_fuel_l * 2.68) +
      (data.raw_material_transport_tkm * 0.09) +
      (data.product_transport_tkm * 0.09);

    const co2_ton = co2_kg / 1000;

    const energyLoad =
      data.electricity_kwh +
      (data.natural_gas_m3 * 10.55) +
      (data.steam_ton * 700);

    const opsLoad =
      data.water_m3 +
      ((data.industrial_waste_kg + data.domestic_waste_kg) / 100);

    const signalVelocity = Math.min(35, co2_ton * 1.8);
    const financialExposure = Math.min(35, co2_ton * 1.5);
    const operationalNoise = Math.min(30, (data.water_m3 / 8) + ((data.industrial_waste_kg + data.domestic_waste_kg) / 120));

    const overlayRisk = Math.round(
      Math.min(100, signalVelocity + financialExposure + operationalNoise)
    );

    return {
      co2_kg: round1(co2_kg),
      co2_ton: round1(co2_ton),
      energy_load: Math.round(energyLoad),
      ops_load: Math.round(opsLoad),
      overlay_risk: overlayRisk,
      drivers: {
        signal_velocity: round1(signalVelocity),
        financial_exposure: round1(financialExposure),
        operational_noise: round1(operationalNoise)
      }
    };
  }

  function updateSummaryCards(overlay){
    const co2e = byId("esgSummaryCo2e");
    const energy = byId("esgSummaryEnergy");
    const ops = byId("esgSummaryOps");
    const risk = byId("esgSummaryRisk");

    if(co2e) co2e.textContent = overlay.co2_ton.toLocaleString("en-US", {minimumFractionDigits:1, maximumFractionDigits:1}) + " t";
    if(energy) energy.textContent = overlay.energy_load.toLocaleString("en-US");
    if(ops) ops.textContent = overlay.ops_load.toLocaleString("en-US");
    if(risk) risk.textContent = overlay.overlay_risk + " / 100";
  }

  function updateStatus(data){
    const el = byId("esgEntryStatus");
    if(!el) return;
    if(data.updated_at){
      el.textContent = "Saved: " + data.facility + (data.period_label ? " • " + data.period_label : "") + " • " + new Date(data.updated_at).toLocaleString();
    }else{
      el.textContent = "No saved ESG record yet.";
    }
  }

  function applyExecutiveEsgOverlay(data, overlay){
    window.__ZERO_ESG_ENTRY__ = data;
    window.__ZERO_ESG_OVERLAY__ = overlay;

    const alertBadge = Array.from(document.querySelectorAll(".badge")).find(function(el){
      return /alert/i.test((el.textContent || "").trim());
    });
    if(alertBadge){
      if(overlay.overlay_risk >= 70){
        alertBadge.textContent = "ESG alert";
      }else if(overlay.overlay_risk >= 40){
        alertBadge.textContent = "ESG watch";
      }else{
        alertBadge.textContent = "ESG stable";
      }
    }

    const heroMetric = document.querySelector(".metric .value");
    if(heroMetric){
      heroMetric.setAttribute("title", "ESG overlay risk: " + overlay.overlay_risk + "/100");
    }
  }

  function openModal(){
    const modal = byId("esgDataEntryModal");
    if(!modal) return;
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
  }

  function closeModal(){
    const modal = byId("esgDataEntryModal");
    if(!modal) return;
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
  }

  function hydrateFromStorage(){
    const data = readStoredData();
    fillForm(data);
    const overlay = computeExecutiveEsgOverlay(data);
    updateSummaryCards(overlay);
    updateStatus(data);
    applyExecutiveEsgOverlay(data, overlay);
  }

  function resetForm(){
    const data = getBlankData();
    fillForm(data);
    const overlay = computeExecutiveEsgOverlay(data);
    updateSummaryCards(overlay);
    updateStatus(data);
    applyExecutiveEsgOverlay(data, overlay);
    localStorage.removeItem(ESG_ENTRY_STORAGE_KEY);
    clearEvidence();
  }

  function bind(){
    const openBtn = byId("openEsgDataEntryBtn");
    const closeBtn = byId("closeEsgDataEntryBtn");
    const backdrop = byId("esgDataEntryModal");
    const form = byId("esgDataEntryForm");
    const resetBtn = byId("resetEsgConsumptionBtn");
    const invoiceInput = byId("esgInvoiceUpload");
    const removeInvoiceBtn = byId("removeEsgInvoiceBtn");

    if(openBtn){
      openBtn.addEventListener("click", openModal);
    }

    if(closeBtn){
      closeBtn.addEventListener("click", closeModal);
    }

    if(backdrop){
      backdrop.addEventListener("click", function(e){
        if(e.target === backdrop) closeModal();
      });
    }

    document.addEventListener("keydown", function(e){
      if(e.key === "Escape"){
        closeModal();
      }
    });

    if(form){
      form.addEventListener("submit", function(e){
        e.preventDefault();
        const data = collectFormData();
        const overlay = computeExecutiveEsgOverlay(data);
        writeStoredData(data);
        updateSummaryCards(overlay);
        updateStatus(data);
        applyExecutiveEsgOverlay(data, overlay);
        closeModal();
        console.log("ESG entry saved:", data, overlay);
      });

      form.addEventListener("input", function(){
        const previewData = collectFormData();
        const overlay = computeExecutiveEsgOverlay(previewData);
        updateSummaryCards(overlay);
      });
    }

    if(resetBtn){
      resetBtn.addEventListener("click", function(){
        resetForm();
      });
    }

    if(invoiceInput){
      invoiceInput.addEventListener("change", function(e){
        const file = e.target.files && e.target.files[0];
        if(file) handleEvidenceFile(file);
      });
    }

    if(removeInvoiceBtn){
      removeInvoiceBtn.addEventListener("click", function(){
        clearEvidence();
      });
    }

    hydrateFromStorage();
    const savedEvidence = readEvidence();
    window.__ZERO_ESG_EVIDENCE__ = savedEvidence;
    updateEvidenceMeta(savedEvidence);
  }

  if(document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", bind);
  }else{
    bind();
  }
})();




window.__ZERO_AGENT_STATE__ = {};

window.addEventListener("zero:scenario", function(e){

  var detail = e.detail || {};
  var scenario = detail.scenario;
  var risk = detail.risk;

  var state = {
    scenario: scenario,
    risk: risk,
    exposure: Math.round(risk * 5.5),
    timestamp: Date.now()
  };

  var priority = "LOW";
  var boardEscalation = false;
  var recommendedAction = "Monitor operational signals.";

  if (risk >= 70) {
    priority = "CRITICAL";
    boardEscalation = true;
    recommendedAction = "Immediate executive intervention required.";
  } else if (risk >= 50) {
    priority = "HIGH";
    recommendedAction = "Increase monitoring and apply operational stabilization.";
  } else if (risk >= 35) {
    priority = "MEDIUM";
    recommendedAction = "Maintain digital control posture.";
  }

  state.priority = priority;
  state.boardEscalation = boardEscalation;
  state.recommendedAction = recommendedAction;

  window.__ZERO_AGENT_STATE__ = state;

  var recEl = document.getElementById("aiRecommendation");
  if(recEl){
    recEl.textContent = "AI Recommendation: " + recommendedAction;
  }

  console.log("ZERO Agent State Updated:", state);

});




(function () {
  function byId(id){ return document.getElementById(id); }

  function setDecision(msg){
    var box = byId("execDecisionStatus");
    if(box) box.textContent = msg;
  }

  var approve = byId("execApproveBtn");
  var reject = byId("execRejectBtn");
  var escalate = byId("execEscalateBtn");

  if (approve) approve.addEventListener("click", function(){
    setDecision("Approved by executive layer. Next step: persist decision to backend.");
  });

  if (reject) reject.addEventListener("click", function(){
    setDecision("Rejected by executive layer. Review threshold, alerts, and source inputs.");
  });

  if (escalate) escalate.addEventListener("click", function(){
    setDecision("Escalated to board review. Immediate follow-up recommended.");
  });
})();



(function(){

function setApproval(value){
  const rows = document.querySelectorAll("#execAlertsBody tr");

  rows.forEach(function(r){
    const approvalCell = r.children[3];
    if(approvalCell){
      approvalCell.textContent = value;
    }
  });

}

function setBadge(type){
  const badge = document.getElementById("execAlertsBadge");
  if(!badge) return;

  if(type==="approve"){
    badge.textContent="0 alerts";
    badge.className="badge ok";
  }

  if(type==="reject"){
    badge.textContent="1 alert";
    badge.className="badge action";
  }

  if(type==="escalate"){
    badge.textContent="BOARD";
    badge.className="badge critical";
  }

}

document.getElementById("execApproveBtn")?.addEventListener("click",function(){
  setApproval("APPROVED");
  setBadge("approve");
});

document.getElementById("execRejectBtn")?.addEventListener("click",function(){
  setApproval("REJECTED");
  setBadge("reject");
});

document.getElementById("execEscalateBtn")?.addEventListener("click",function(){
  setApproval("ESCALATE");
  setBadge("escalate");
});


document.getElementById("openDataIntakeBtn")?.addEventListener("click",function(){
  window.location.href = "intake.html";
});

})();


(function(){
  const STATUS_URL = "agents/sap_mock_feeder/runtime/latest_status.json";

  function setText(id, value){
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? "--";
  }

  function setFeedBadge(ok){
    const el = document.getElementById("liveFeedStatusBadge");
    if (!el) return;
    if (ok) {
      el.textContent = "LIVE";
      el.className = "badge ok";
    } else {
      el.textContent = "OFFLINE";
      el.className = "badge critical";
    }
  }

  function fmtBool(ok){
    if (ok === true) return "OK";
    if (ok === false) return "FAIL";
    return "--";
  }

  function updateLiveMonitor(data){
    setText("liveModeValue", data.mode || "--");
    setText("liveBurstValue", data.burst_size ?? "--");
    setText("liveEventCountValue", data.event_count ?? "--");
    setText("liveApiStatusValue", data.api_ok === true ? "API ONLINE" : (data.api_ok === false ? "API ERROR" : "--"));
    setText("liveCsvStatusValue", fmtBool(data.csv_ok));
    setText("liveOrderValue", data.order_id || "--");
    setText("liveBatchValue", data.batch_id || "--");
    setText("liveProcessValue", data.process_line || "--");
    setText("liveMachineValue", data.asset_id || "--");
    setText("liveUpdateValue", new Date().toLocaleTimeString("en-GB"));
    setFeedBadge(true);
  }

  async function loadLiveMonitor(){
    try {
      const res = await fetch(STATUS_URL + "?ts=" + Date.now(), { cache: "no-store" });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      updateLiveMonitor(data);
    } catch (err) {
      setFeedBadge(false);
      setText("liveUpdateValue", "unreachable");
    }
  }

  loadLiveMonitor();
  setInterval(loadLiveMonitor, 3000);
})();

