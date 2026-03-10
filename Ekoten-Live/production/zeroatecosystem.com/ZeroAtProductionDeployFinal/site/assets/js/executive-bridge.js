(function () {
  function getState() {
    return {
      fibre: window.__ZERO_FIBRE_STATE__ || null,
      fabric: window.__ZERO_FABRIC_STATE__ || null,
      finishing: window.__ZERO_FINISHING_STATE__ || null
    };
  }

  function sum(arr) {
    return arr.reduce((a, b) => a + (Number(b) || 0), 0);
  }

  function hiddenCostFromModule(name, state) {
    if (!state || !state.kpis) return 0;
    const k = state.kpis;

    if (name === "fibre") {
      const reworkKg = (k.throughput_kg || 0) * ((k.rework_pct || 0) / 100);
      const yieldLossKg = (k.throughput_kg || 0) * ((k.yield_loss_pct || 0) / 100);
      return Math.round(
        reworkKg * ((k.energy_cost_eur_per_kg || 0) + (k.labor_cost_eur_per_kg || 0)) +
        yieldLossKg * ((k.material_cost_eur_per_kg || 0) + (k.energy_cost_eur_per_kg || 0) + (k.labor_cost_eur_per_kg || 0))
      );
    }

    if (name === "fabric") {
      const reworkM = (k.throughput_meters || 0) * ((k.rework_pct || 0) / 100);
      const yieldLossM = (k.throughput_meters || 0) * ((k.yield_loss_pct || 0) / 100);
      return Math.round(
        reworkM * ((k.energy_cost_eur_per_meter || 0) + (k.chemical_cost_eur_per_meter || 0) + (k.labor_cost_eur_per_meter || 0)) +
        yieldLossM * ((k.material_cost_eur_per_meter || 0) + (k.energy_cost_eur_per_meter || 0) + (k.chemical_cost_eur_per_meter || 0) + (k.labor_cost_eur_per_meter || 0))
      );
    }

    return 0;
  }

  function aggregate() {
    const state = getState();
    const totalHiddenCost = sum([
      hiddenCostFromModule("fibre", state.fibre),
      hiddenCostFromModule("fabric", state.fabric),
      hiddenCostFromModule("finishing", state.finishing)
    ]);

    return {
      state,
      totalHiddenCost
    };
  }

  window.ZeroExecutiveBridge = { aggregate };
})();
