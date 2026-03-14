(function () {
  const host = window.location.hostname;
  const port = window.location.port;

  // Geçiş aşaması:
  // local html server (8080) -> FastAPI (8010)
  // ileride same-origin reverse proxy olursa "/api" yapılacak.
  let API_BASE = "http://127.0.0.1:8010";

  if (host === "127.0.0.1" || host === "localhost") {
    API_BASE = "http://127.0.0.1:8010";
  }

  window.ZeroIntakeConfig = {
    API_BASE,
    opsUrl(facility) {
      return `${API_BASE}/api/intake/ops?facility=${encodeURIComponent(facility)}`;
    },
    preflightUrl() {
      return `${API_BASE}/api/intake/preflight`;
    },
    commitUrl() {
      return `${API_BASE}/api/intake/commit`;
    }
  };

  console.log("[intake-api-config] active", window.ZeroIntakeConfig);
})();
