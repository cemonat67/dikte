(function () {
  "use strict";

  function byId(id) {
    return document.getElementById(id);
  }

  function num(v) {
    var n = Number(v);
    return Number.isFinite(n) ? n : 0;
  }

  function round1(v) {
    return Math.round((Number(v) || 0) * 10) / 10;
  }

  function euro(v) {
    return "€ " + Math.round(v).toLocaleString("en-US");
  }

  function collectDomInputs() {
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

  function calculateOverlayFallback(data) {
    var co2_kg =
      (data.electricity_kwh * 0.42) +
      (data.natural_gas_m3 * 2.00) +
      (data.steam_ton * 180) +
      (data.forklift_fuel_l * 2.68) +
      (data.vehicle_fuel_l * 2.68) +
      (data.raw_material_transport_tkm * 0.09) +
      (data.product_transport_tkm * 0.09);

    var co2_ton = co2_kg / 1000;

    var energy_load =
      data.electricity_kwh +
      (data.natural_gas_m3 * 10.55) +
      (data.steam_ton * 700);

    var ops_load =
      data.water_m3 +
      ((data.industrial_waste_kg + data.domestic_waste_kg) / 100);

    var signal_velocity = Math.min(35, co2_ton * 1.8);
    var financial_exposure = Math.min(35, co2_ton * 1.5);
    var operational_noise = Math.min(
      30,
      (data.water_m3 / 8) + ((data.industrial_waste_kg + data.domestic_waste_kg) / 120)
    );

    var overlay_risk = Math.round(
      Math.min(100, signal_velocity + financial_exposure + operational_noise)
    );

    return {
      co2_kg: round1(co2_kg),
      co2_ton: round1(co2_ton),
      energy_load: Math.round(energy_load),
      ops_load: Math.round(ops_load),
      overlay_risk: overlay_risk,
      drivers: {
        signal_velocity: round1(signal_velocity),
        financial_exposure: round1(financial_exposure),
        operational_noise: round1(operational_noise)
      }
    };
  }

  function getCurrentData() {
    return window.__ZERO_ESG_ENTRY__ || collectDomInputs();
  }

  function getCurrentOverlay(data) {
    return window.__ZERO_ESG_OVERLAY__ || calculateOverlayFallback(data || getCurrentData());
  }

  function calculateExecutiveRisk(data, overlay) {
    data = data || getCurrentData();
    overlay = overlay || getCurrentOverlay(data);

    var ceo = Math.min(
      100,
      overlay.overlay_risk * 0.55 +
      overlay.drivers.signal_velocity * 0.65 +
      ((data.industrial_waste_kg + data.domestic_waste_kg) / 90)
    );

    var cfo = Math.min(
      100,
      overlay.drivers.financial_exposure * 1.2 +
      (overlay.energy_load / 1400) +
      (data.electricity_kwh / 1800)
    );

    var cto = Math.min(
      100,
      overlay.drivers.operational_noise * 1.15 +
      (data.water_m3 / 10) +
      ((data.industrial_waste_kg + data.domestic_waste_kg) / 110)
    );

    return {
      ceo: Math.round(ceo),
      cfo: Math.round(cfo),
      cto: Math.round(cto)
    };
  }

  function buildExecutiveAlerts(data, overlay, risk) {
    var alerts = [];

    if (overlay.overlay_risk >= 70) {
      alerts.push({
        owner: "CEO",
        severity: "critical",
        title: "Enterprise ESG escalation",
        action: "Prepare board review",
        reason: "OVERLAY_RISK_HIGH"
      });
    }

    if (overlay.energy_load >= 25000 || data.electricity_kwh >= 10000) {
      alerts.push({
        owner: "CFO",
        severity: "high",
        title: "Energy cost pressure",
        action: "Review cost drivers",
        reason: "ENERGY_LOAD_HIGH"
      });
    }

    if (data.water_m3 >= 250 || (data.industrial_waste_kg + data.domestic_waste_kg) >= 1000) {
      alerts.push({
        owner: "CTO",
        severity: "high",
        title: "Operational control load",
        action: "Inspect water and waste pattern",
        reason: "OPS_LOAD_HIGH"
      });
    }

    return alerts;
  }

  function persistExecutiveState(payload) {
    localStorage.setItem("zero_exec_phase2_state", JSON.stringify(payload));
  }

  function setBadge(el, text, mode) {
    if (!el) return;
    el.textContent = text;
    el.className = "badge";
    if (mode === "ok") el.classList.add("ok");
    if (mode === "monitor") el.classList.add("monitor");
    if (mode === "critical") el.classList.add("critical");
    if (mode === "alert") el.classList.add("alert");
  }

  function severityToMode(sev) {
    if (sev === "critical") return "critical";
    if (sev === "high") return "alert";
    if (sev === "medium") return "monitor";
    return "ok";
  }

  function updateExecutiveCards(risk, data, overlay, alerts) {
    var ceoBadge = byId("ceoBadge");
    var ceoKpiValue = byId("ceoKpiValue");
    var ceoDecisionLine = byId("ceoDecisionLine");

    var cfoBadge = byId("cfoBadge");
    var cfoExposureValue = byId("cfoExposureValue");
    var cfoTodayLine = byId("cfoTodayLine");

    var ctoBadge = byId("ctoBadge");
    var ctoKpiValue = byId("ctoKpiValue");
    var ctoKpiUnit = byId("ctoKpiUnit");
    var ctoCheckLine = byId("ctoCheckLine");

    var execRisk = byId("execRisk");

    var totalWaste = data.industrial_waste_kg + data.domestic_waste_kg;
    var todayExposure = Math.max(250, Math.round((overlay.energy_load * 0.045) + (overlay.co2_ton * 18) + (totalWaste * 0.35)));
    var annualExposure = todayExposure * 265;

    if (ceoBadge) {
      if (risk.ceo >= 70) setBadge(ceoBadge, "ALERT", "alert");
      else if (risk.ceo >= 40) setBadge(ceoBadge, "MONITOR", "monitor");
      else setBadge(ceoBadge, "STABLE", "ok");
    }

    if (ceoKpiValue) {
      ceoKpiValue.textContent = overlay.overlay_risk >= 55 ? "ESG Pressure" : "Wastewater";
    }

    if (ceoDecisionLine) {
      ceoDecisionLine.innerHTML = 'Decision status: <b>' + (risk.ceo >= 70 ? 'ESCALATE' : (risk.ceo >= 40 ? 'MONITOR' : 'LIVE')) + '</b>';
    }

    if (cfoBadge) cfoBadge.textContent = "€ / Year";
    if (cfoExposureValue) cfoExposureValue.textContent = euro(annualExposure);
    if (cfoTodayLine) cfoTodayLine.innerHTML = 'Today: <b>' + euro(todayExposure) + '/day</b>';

    if (ctoBadge) {
      if (risk.cto >= 70) setBadge(ctoBadge, "CRITICAL", "critical");
      else if (risk.cto >= 40) setBadge(ctoBadge, "WATCH", "monitor");
      else setBadge(ctoBadge, "STABLE", "ok");
    }

    if (ctoKpiValue) ctoKpiValue.textContent = risk.cto >= 50 ? "Ops / Water" : "Control Layer";
    if (ctoKpiUnit) ctoKpiUnit.textContent = risk.cto >= 50 ? "load" : "integrity";
    if (ctoCheckLine) ctoCheckLine.innerHTML = 'Last check: <b>' + new Date().toLocaleString() + '</b>';

    if (execRisk) {
      execRisk.textContent = risk.ceo >= 70 ? "ALERT" : (risk.ceo >= 40 ? "MONITOR" : "STABLE");
    }

    console.log("[Phase2] cards updated", {
      ceo: risk.ceo,
      cfo: risk.cfo,
      cto: risk.cto,
      annualExposure: annualExposure,
      todayExposure: todayExposure
    });
  }

  function updateAlertsTable(alerts, data, overlay, risk) {
    var body = byId("execAlertsBody");
    var badge = byId("execAlertsBadge");
    var sub = byId("execAlertsSubtext");
    if (!body) {
      console.warn("[Phase2] execAlertsBody not found");
      return;
    }

    var totalWaste = data.industrial_waste_kg + data.domestic_waste_kg;
    var todayExposure = Math.max(250, Math.round((overlay.energy_load * 0.045) + (overlay.co2_ton * 18) + (totalWaste * 0.35)));

    body.innerHTML = "";

    if (!alerts || !alerts.length) {
      if (badge) badge.textContent = "0 alerts";
      if (sub) sub.textContent = "Live table";
      return;
    }

    alerts.forEach(function (a) {
      var tr = document.createElement("tr");
      var trend = risk.ceo >= 70 ? "RISING" : (risk.ceo >= 40 ? "WATCH" : "STABLE");
      var approval = a.severity === "critical" ? "ESCALATE" : "APPROVED";
      var badgeText = risk.ceo >= 70 ? "ALERT" : (risk.ceo >= 40 ? "MONITOR" : "STABLE");
      var pillClass = (a.severity === "critical" || a.severity === "high") ? "action" : "ok";

      tr.innerHTML =
        '<td style="color:rgba(234,240,255,.95);font-weight:500;">' + (data.facility || 'Ekoten') + '</td>' +
        '<td>' + euro(todayExposure) + '</td>' +
        '<td>' + trend + '</td>' +
        '<td>' + approval + '</td>' +
        '<td>' + badgeText + '</td>' +
        '<td><span class="pill ' + pillClass + '">' + a.owner + '</span></td>' +
        '<td>' + a.reason + '</td>';

      body.appendChild(tr);
    });

    if (badge) badge.textContent = alerts.length + (alerts.length === 1 ? " alert" : " alerts");
    if (sub) sub.textContent = "Live table";

    console.log("[Phase2] alerts table updated", { count: alerts.length });
  }

  function setChartData(chart, arr) {
    if (!chart || !chart.data || !chart.data.datasets || !chart.data.datasets[0]) return;
    chart.data.datasets[0].data = arr;
    chart.update();
  }

  function updateMiniCharts(payload) {
    var d = payload.esg;
    var o = payload.overlay;
    var r = payload.risk;

    var cfoSpark = window.__ZERO_CFO_SPARK__;
    var waterChart = window.__ZERO_WATER_CHART__;
    var energyChart = window.__ZERO_ENERGY_CHART__;
    var co2Chart = window.__ZERO_CO2_CHART__;
    var wwChart = window.__ZERO_WW_CHART__;

    var cfoSeries = [
      Math.max(250, Math.round(o.energy_load * 0.020)),
      Math.max(300, Math.round(o.energy_load * 0.026)),
      Math.max(350, Math.round(o.energy_load * 0.030)),
      Math.max(400, Math.round(o.energy_load * 0.028 + o.co2_ton * 3)),
      Math.max(450, Math.round(o.energy_load * 0.032 + o.co2_ton * 5)),
      Math.max(500, Math.round(o.energy_load * 0.034 + o.co2_ton * 7)),
      Math.max(550, Math.round(o.energy_load * 0.045 + o.co2_ton * 18))
    ];

    var waterBase = Math.max(8, round1(d.water_m3 / 18));
    var waterSeries = [
      round1(waterBase * 0.82),
      round1(waterBase * 0.90),
      round1(waterBase * 0.95),
      round1(waterBase * 1.05),
      round1(waterBase * 1.12),
      round1(waterBase * 1.00)
    ];

    var energyBase = Math.max(380, Math.round(o.energy_load / 60));
    var energySeries = [
      Math.round(energyBase * 0.92),
      Math.round(energyBase * 0.98),
      Math.round(energyBase * 0.95),
      Math.round(energyBase * 1.02),
      Math.round(energyBase * 1.08),
      Math.round(energyBase * 1.04)
    ];

    var co2Base = Math.max(8, round1(o.co2_ton / 4));
    var co2Series = [
      round1(co2Base * 0.90),
      round1(co2Base * 0.98),
      round1(co2Base * 0.86),
      round1(co2Base * 1.04),
      round1(co2Base * 1.10),
      round1(co2Base * 0.96)
    ];

    var wwBase = Math.max(18, Math.round(r.cto));
    var wwSeries = [
      Math.round(wwBase * 0.72),
      Math.round(wwBase * 0.80),
      Math.round(wwBase * 0.92),
      Math.round(wwBase * 0.86),
      Math.round(wwBase * 1.00),
      Math.round(wwBase * 1.12)
    ];

    setChartData(cfoSpark, cfoSeries);
    setChartData(waterChart, waterSeries);
    setChartData(energyChart, energySeries);
    setChartData(co2Chart, co2Series);
    setChartData(wwChart, wwSeries);

    console.log("[Phase2] mini charts updated");
  }

  function buildPayloadFromCurrentState() {
    var data = getCurrentData();
    var overlay = getCurrentOverlay(data);
    var risk = calculateExecutiveRisk(data, overlay);
    var alerts = buildExecutiveAlerts(data, overlay, risk);

    return {
      esg: data,
      overlay: overlay,
      risk: risk,
      alerts: alerts,
      ts: new Date().toISOString()
    };
  }

  function savePhase2FromCurrentState() {
    var payload = buildPayloadFromCurrentState();
    updateExecutiveCards(payload.risk, payload.esg, payload.overlay, payload.alerts);
    updateAlertsTable(payload.alerts, payload.esg, payload.overlay, payload.risk);
    updateMiniCharts(payload);
    persistExecutiveState(payload);
    console.log("[Phase2] ESG saved", payload);
    return payload;
  }

  function hookExistingFormSubmit() {
    var form = byId("esgDataEntryForm");
    if (!form || form.__ZERO_PHASE2_HOOKED__) return;
    form.__ZERO_PHASE2_HOOKED__ = true;

    form.addEventListener("submit", function () {
      setTimeout(function () {
        savePhase2FromCurrentState();
      }, 0);
    });

    console.log("[Phase2] hooked existing ESG submit flow");
  }

  function hydrateFromSavedPhase2() {
    try {
      var raw = localStorage.getItem("zero_exec_phase2_state");
      if (!raw) return;
      var payload = JSON.parse(raw);
      if (!payload || !payload.esg || !payload.overlay || !payload.risk || !payload.alerts) return;
      updateExecutiveCards(payload.risk, payload.esg, payload.overlay, payload.alerts);
      updateAlertsTable(payload.alerts, payload.esg, payload.overlay, payload.risk);
      setTimeout(function () {
        updateMiniCharts(payload);
      }, 80);
      console.log("[Phase2] hydrated saved state");
    } catch (e) {
      console.warn("[Phase2] hydrate failed", e);
    }
  }

  window.ZeroExecutivePhase2 = {
    getCurrentData: getCurrentData,
    getCurrentOverlay: getCurrentOverlay,
    calculateExecutiveRisk: calculateExecutiveRisk,
    buildExecutiveAlerts: buildExecutiveAlerts,
    buildPayloadFromCurrentState: buildPayloadFromCurrentState,
    savePhase2FromCurrentState: savePhase2FromCurrentState,
    hookExistingFormSubmit: hookExistingFormSubmit,
    hydrateFromSavedPhase2: hydrateFromSavedPhase2,
    updateMiniCharts: updateMiniCharts
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      hookExistingFormSubmit();
      setTimeout(hydrateFromSavedPhase2, 140);
    });
  } else {
    hookExistingFormSubmit();
    setTimeout(hydrateFromSavedPhase2, 140);
  }

  console.log("[Phase2] executive-phase2-risk loaded");
})();
