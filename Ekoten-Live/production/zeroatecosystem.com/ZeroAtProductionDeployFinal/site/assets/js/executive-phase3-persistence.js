(function () {
  "use strict";

  var STATE_KEY = "zero_exec_phase2_state";
  var QUEUE_KEY = "zero_exec_phase3_queue";
  var LAST_HASH_KEY = "zero_exec_phase3_last_persisted_hash";
  var SAVE_TIMER = null;
  var FLUSH_LOCK = false;

  function log() {
    try { console.log.apply(console, ["[Phase3]"].concat([].slice.call(arguments))); } catch (e) {}
  }

  function parseJson(value, fallback) {
    try { return JSON.parse(value); } catch (e) { return fallback; }
  }

  function stringify(obj) {
    try { return JSON.stringify(obj); } catch (e) { return "{}"; }
  }

  function toNumber(v) {
    if (v === null || v === undefined || v === "") return null;
    var n = Number(v);
    return Number.isFinite(n) ? n : null;
  }

  function normalizeSeverity(v) {
    var s = String(v || "MONITOR").trim().toUpperCase();
    if (s === "CRITICAL" || s === "HIGH") return "ALERT";
    if (s === "WATCH" || s === "MEDIUM" || s === "LOW") return "MONITOR";
    if (s === "SAFE" || s === "NORMAL") return "OK";
    if (s === "ALERT" || s === "MONITOR" || s === "OK") return s;
    return "MONITOR";
  }

  function stableSort(input) {
    if (Array.isArray(input)) return input.map(stableSort);
    if (input && typeof input === "object") {
      var out = {};
      Object.keys(input).sort().forEach(function (k) {
        out[k] = stableSort(input[k]);
      });
      return out;
    }
    return input;
  }

  async function sha256(text) {
    if (window.crypto && window.crypto.subtle && window.TextEncoder) {
      var buf = new TextEncoder().encode(text);
      var hash = await window.crypto.subtle.digest("SHA-256", buf);
      return Array.from(new Uint8Array(hash)).map(function (b) {
        return b.toString(16).padStart(2, "0");
      }).join("");
    }
    var h = 0;
    for (var i = 0; i < text.length; i++) {
      h = ((h << 5) - h) + text.charCodeAt(i);
      h |= 0;
    }
    return "fallback_" + String(h);
  }

  function getConfig() {
    var cfg = window.__ZERO_SUPABASE__ || {};
    return {
      url: cfg.url || "",
      anonKey: cfg.anonKey || ""
    };
  }

  function getClient() {
    var cfg = getConfig();
    if (!cfg.url || !cfg.anonKey) return null;
    if (!window.supabase || !window.supabase.createClient) return null;
    if (cfg.anonKey.indexOf("SUPABASE_ANON_KEY_BURAYA") !== -1) return null;
    if (!window.__ZERO_SUPABASE_CLIENT__) {
      window.__ZERO_SUPABASE_CLIENT__ = window.supabase.createClient(cfg.url, cfg.anonKey, {
        auth: { persistSession: false, autoRefreshToken: false }
      });
    }
    return window.__ZERO_SUPABASE_CLIENT__;
  }

  function getState() {
    return parseJson(localStorage.getItem(STATE_KEY), null);
  }

  function getQueue() {
    var q = parseJson(localStorage.getItem(QUEUE_KEY), []);
    return Array.isArray(q) ? q : [];
  }

  function setQueue(queue) {
    localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
  }

  function enqueue(payload) {
    if (!payload || !payload.entry || !payload.entry.state_hash) return;
    var queue = getQueue() || [];
    var exists = queue.some(function (q) {
      return q && q.entry && q.entry.state_hash === payload.entry.state_hash;
    });
    if (!exists) {
      queue.push(payload);
      setQueue(queue);
      log("queued", payload.entry.state_hash, "size=", queue.length);
    }
  }

  function removeFromQueue(stateHash) {
    var queue = (getQueue() || []).filter(function (q) {
      return !(q && q.entry && q.entry.state_hash === stateHash);
    });
    setQueue(queue);
  }

  function deriveStatus(state) {
    var overlay = state.overlay || {};
    var risk = state.risk || {};
    var alerts = Array.isArray(state.alerts) ? state.alerts : [];

    var maxRisk = Math.max(
      toNumber(risk.ceo) || 0,
      toNumber(risk.cfo) || 0,
      toNumber(risk.cto) || 0,
      toNumber(overlay.overlay_risk != null ? overlay.overlay_risk : overlay.overlayRisk) || 0
    );

    var hasAlert = alerts.some(function (a) {
      return normalizeSeverity(a && (a.severity || a.level || a.status)) === "ALERT";
    });

    if (hasAlert || maxRisk >= 80 || alerts.length >= 3) return "ALERT";
    if (maxRisk >= 50 || alerts.length > 0) return "MONITOR";
    return "OK";
  }

  async function buildPayload(state) {
    if (!state) return null;

    var esg = state.esg || {};
    var overlay = state.overlay || {};
    var risk = state.risk || {};
    var alerts = Array.isArray(state.alerts) ? state.alerts : [];
    var facility = esg.facility || "Ekoten";
    var periodLabel = esg.period_label || "";
    var ts = state.ts || new Date().toISOString();

    var canonical = stableSort({
      esg: esg,
      overlay: overlay,
      risk: risk,
      alerts: alerts,
      ts: ts
    });

    var stateHash = await sha256(stringify(canonical));

    return {
      entry: {
        facility: facility,
        period_label: periodLabel,
        source: "executive_phase2_modal",
        ts: ts,
        state_hash: stateHash,
        esg: esg
      },
      snapshot: {
        facility: facility,
        status: deriveStatus(state),
        alert_count: alerts.length,
        co2_kg: toNumber(overlay.co2_kg != null ? overlay.co2_kg : overlay.co2Kg),
        co2_ton: toNumber(overlay.co2_ton != null ? overlay.co2_ton : overlay.co2Ton),
        energy_load: toNumber(overlay.energy_load != null ? overlay.energy_load : overlay.energyLoad),
        ops_load: toNumber(overlay.ops_load != null ? overlay.ops_load : overlay.opsLoad),
        overlay_risk: toNumber(overlay.overlay_risk != null ? overlay.overlay_risk : overlay.overlayRisk),
        ceo_risk: toNumber(risk.ceo),
        cfo_risk: toNumber(risk.cfo),
        cto_risk: toNumber(risk.cto),
        annual_exposure: toNumber(overlay.annual_exposure != null ? overlay.annual_exposure : overlay.annualExposure),
        today_exposure: toNumber(overlay.today_exposure != null ? overlay.today_exposure : overlay.todayExposure),
        snapshot: {
          overlay: overlay,
          risk: risk
        }
      },
      alerts: alerts.map(function (a) {
        return {
          facility: facility,
          severity: normalizeSeverity(a && (a.severity || a.level || a.status)),
          title: (a && (a.title || a.label || a.name || a.alert)) || "Executive alert",
          message: (a && (a.message || a.description || a.reason || a.text)) || "",
          area: (a && (a.area || a.owner || a.role || a.type)) || null,
          metric: (a && (a.metric || a.signal || a.kpi)) || null,
          value: toNumber(a && (a.value != null ? a.value : (a.score != null ? a.score : a.risk))),
          payload: a || {}
        };
      })
    };
  }

  async function rpcPersist(client, payload) {
    var res = await client.rpc("persist_exec_phase3", { p_payload: payload });
    if (res.error) throw res.error;
    return res.data;
  }

  async function persistCurrent(reason) {
    var state = getState();
    if (!state) {
      log("no state");
      return;
    }

    var payload = await buildPayload(state);
    if (!payload) return;

    var stateHash = payload.entry.state_hash;
    var lastHash = localStorage.getItem(LAST_HASH_KEY);

    if (lastHash === stateHash) {
      log("skip duplicate", stateHash, reason);
      return;
    }

    if (!navigator.onLine) {
      enqueue(payload);
      return;
    }

    var client = getClient();
    if (!client) {
      enqueue(payload);
      log("no supabase client -> queued");
      return;
    }

    try {
      var result = await rpcPersist(client, payload);
      localStorage.setItem(LAST_HASH_KEY, stateHash);
      removeFromQueue(stateHash);
      log("persisted", stateHash, result);
    } catch (err) {
      enqueue(payload);
      log("persist failed -> queued", err && (err.message || err));
    }
  }

  async function flushQueue() {
    if (FLUSH_LOCK) return;
    FLUSH_LOCK = true;
    try {
      if (!navigator.onLine) return;
      var client = getClient();
      if (!client) return;

      var queue = getQueue() || [];
      if (!queue.length) return;

      for (var i = 0; i < queue.length; i++) {
        var payload = queue[i];
        if (!payload || !payload.entry || !payload.entry.state_hash) continue;
        try {
          var result = await rpcPersist(client, payload);
          localStorage.setItem(LAST_HASH_KEY, payload.entry.state_hash);
          removeFromQueue(payload.entry.state_hash);
          log("flushed", payload.entry.state_hash, result);
        } catch (err) {
          log("flush stopped", err && (err.message || err));
          break;
        }
      }
    } finally {
      FLUSH_LOCK = false;
    }
  }

  function schedulePersist(reason) {
    clearTimeout(SAVE_TIMER);
    SAVE_TIMER = setTimeout(function () {
      persistCurrent(reason);
    }, 350);
  }

  function hookStorageWrite() {
    if (window.__ZERO_PHASE3_STORAGE_HOOKED__) return;
    window.__ZERO_PHASE3_STORAGE_HOOKED__ = true;

    var originalSetItem = Storage.prototype.setItem;
    Storage.prototype.setItem = function (key, value) {
      originalSetItem.apply(this, arguments);
      if (key === STATE_KEY) {
        schedulePersist("state_write");
      }
    };
  }

  function boot() {
    hookStorageWrite();

    window.addEventListener("online", function () {
      flushQueue();
      persistCurrent("online");
    });

    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible") flushQueue();
    });

    flushQueue();
    persistCurrent("boot");

    window.ZeroExecutivePhase3 = {
      buildPayload: buildPayload,
      persistCurrent: persistCurrent,
      flushQueue: flushQueue,
      getQueue: getQueue
    };

    log("ready");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
