# Pilot Readiness & Testing Script

The Zero@Trust v0.9.0 MVP is formally frozen. The architecture has proven its core philosophy: the user interface exists strictly to reflect operational truth, while intelligence and governance remain exclusively headless.

## Execution Requirements
- Docker and Docker Compose installed
- Port `8000` available
- Port `5432` available (for Postgres)

## Official Pilot Test Flow

**Step 1: Boot the Frozen Baseline**
```bash
cp .env.example .env
docker compose up --build -d
```

**Step 2: Verify Health & API Contract**
```bash
curl http://localhost:8000/health
```
*(Expected: `{"status":"ok","app_env":"production","db_driver":"postgresql","api_prefix":"/api/v1","version":"0.9.0"}`)*

Check OpenAPI Docs:
Navigate to `http://localhost:8000/docs` in your browser.

**Step 3: Establish Dual Atmospheres**
- Open `http://localhost:8000/` in Browser Window A (Default tenant).
- Open `http://localhost:8000/?env=alpha` in Browser Window B (Alpha tenant).

**Step 4: Inject Targeted Risk (Alpha Only)**
```bash
curl -X POST "http://localhost:8000/api/v1/risk/evaluate" \
     -H "Content-Type: application/json" \
     -d '{"environment_id": "alpha", "source": "network", "category": "payment", "severity": 0.85}'
```

**Step 5: Verify Isolation**
- Wait ~10 seconds.
- **Window B (`?env=alpha`)** will visually lock down (e.g., transition to `burdened` or `withheld`).
- **Window A (`default`)** will remain perfectly `quiet`.

**Step 6: Private Administrative Resolution**
```bash
curl -X POST "http://localhost:8000/api/v1/admin/environment/alpha/resolve-risk" \
     -H "X-Admin-Key: change-me-before-production" \
     -H "Content-Type: application/json" \
     -d '{"reviewer": "pilot_admin", "note": "Targeted test completed."}'
```

**Step 7: Verify Recovery**
- Wait ~10 seconds.
- **Window B (`?env=alpha`)** will begin a slow, organic mathematical recovery back toward `quiet` (impeded slightly by the newly applied governance drag).
