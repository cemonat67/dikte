# Zero@Trust

> **Production Beta Handover (v13.1):** The codebase is formally frozen for production beta deployment. The system features a fully isolated, multi-tenant deterministic intelligence engine (`FastAPI`/`PostgreSQL`), administered strictly via a private JWT-secured Governance API, capable of receiving native machine webhooks, and rendered purely as a subtractive, atmospheric frontend. 
> 
> **Handover Documentation:**
> - [HANDOVER.md](HANDOVER.md) (Architecture & System Purpose)
> - [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) (Mandatory Go-Live Checks)
> - [API_CONTRACT.md](API_CONTRACT.md) (Full Endpoint Index)
> - [CHANGELOG.md](CHANGELOG.md) (Version History)

The backend architecture is now capable of managing multiple completely isolated "atmospheres" from a single engine process. By introducing `environment_id` across all database models and engine calculators, different tenants, clients, or internal operational environments (e.g. `sun-tekstil`, `finance-ops`, `default`) will accrue persistence, trust posture, and risk severity without cross-contamination.

## Local Setup & Deployment (v7.0)

## Local Setup & Deployment (v7.0/v10.0)

**1. Configure Environment:**
```bash
cp .env.example .env
```
Edit `.env` if deploying to production. For production, set `APP_ENV=production` and use a valid PostgreSQL `DATABASE_URL`. Do NOT deploy with the default `ADMIN_API_KEY`.

**2. Production Deployment (v10.0):**
Zero@Trust v10.0 includes a production-ready Nginx + PostgreSQL orchestration template. See [DEPLOYMENT.md](DEPLOYMENT.md) for the secure deployment runbook.

**3. Local Production Run (Docker Compose):**
This boots a realistic production environment linking the FastAPI backend, a true PostgreSQL 16 database, and automatically serves the static frontend from `/`.
```bash
docker compose up --build
```
Navigate to:
- `http://localhost:8000/` (Default environment)
- `http://localhost:8000/?env=alpha` (Alpha tenant)
- `http://localhost:8000/health` (Telemetry)

**3. Local Dev Run (SQLite Fallback):**
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
*(Note: For local SQLite dev, the background process will automatically detect missing schemas and safely drop `zerotrust.db` to rebuild. This destructive action is strictly blocked in production.)*

## Intelligence Model Testing Flow (v8.0)

**1. Open Default Tenant:**
Open `http://localhost:8000/`

**2. Inject Low-Weight Risk (Network):**
Network category has a 0.90 multiplier, so a 0.5 severity might only cause "watching".
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/risk/evaluate" \
     -H "Content-Type: application/json" \
     -d '{"environment_id": "default", "source": "aws", "category": "network", "severity": 0.50}'
```

**3. Inject High-Weight Risk (Payment):**
Payment category has a 1.25 multiplier. This will push the intelligence model aggressively towards "burdened" or "withheld".
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/risk/evaluate" \
     -H "Content-Type: application/json" \
     -d '{"environment_id": "default", "source": "stripe", "category": "payment", "severity": 0.80}'
```

**4. Introduce Operational Evidence:**
Evidence softens risk pressure mathematically.
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/evidence/record" \
     -H "Content-Type: application/json" \
     -d '{"environment_id": "default", "category": "human_verification", "weight": 0.95}'
```

**5. View Intelligence Scoring via Admin:**
```bash
curl "http://127.0.0.1:8000/api/v1/admin/environment/default/summary" \
     -H "X-Admin-Key: change-me-before-production"
```
*(Observe `weighted_risk_score`, `evidence_confidence`, and `final_trust_pressure` in the response.)*

## Public API Contract

The public surface is strictly atmospheric. Endpoints do not require authentication, but they return zero operational details.

**1. View Posture (GET):**
```bash
curl "http://localhost:8000/api/v1/trust/state?environment_id=default"
```
*(Returns strictly atmospheric variables like `posture`, `silence_locked` and `frontend_phrase`)*

**2. Inject Risk (POST):**
```bash
curl -X POST "http://localhost:8000/api/v1/risk/evaluate" \
     -H "Content-Type: application/json" \
     -d '{"environment_id": "default", "source": "aws", "category": "network", "severity": 0.50}'
```
*(Validation: severity must be 0.0 - 1.0)*

**3. Webhook Intelligence Intake (POST):**
Secure endpoint for external operational systems (Datadog, AWS, Stripe).
```bash
curl -X POST "http://localhost:8000/api/v1/webhooks/signal" \
     -H "X-Webhook-Secret: change-me-before-production" \
     -H "Content-Type: application/json" \
     -d '{
           "environment_id": "alpha",
           "source": "aws-guardduty",
           "event_type": "iam_anomaly",
           "category": "anomaly",
           "severity": 0.90,
           "summary": "Unusual IAM API activity detected",
           "external_id": "evt_998877",
           "metadata": {"region": "us-east-1"}
         }'
```
*(Returns `{"ok": true, "environment_id": "alpha", "accepted": true, ...}`)*

## Private Governance API (v9.0)

Administrative routes explicitly require the `X-Admin-Key` header and return a standardized action envelope.

**1. Obtain Admin JWT Token (POST):**
Admin routes require a JWT Bearer token.
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "change-me-before-production"}'
```
*(Store the `access_token` from the response).*

**2. View Environment Summary (GET):**
```bash
curl "http://localhost:8000/api/v1/admin/environment/alpha/summary" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```
*(Note: In local dev mode, `X-Admin-Key: <YOUR_ADMIN_API_KEY>` is supported as a developer fallback.)*

**3. Resolve Active Risk (POST):**
```bash
curl -X POST "http://localhost:8000/api/v1/admin/environment/alpha/resolve-risk" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"reviewer": "admin_cem", "note": "False positive latency spike confirmed."}'
```
*(Returns `{"ok": true, "environment_id": "alpha", "action": "resolve-risk", ...}`)*

**4. Suppress Risk (POST):**
```bash
curl -X POST "http://localhost:8000/api/v1/admin/environment/alpha/suppress-risk" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"reviewer": "admin_cem", "note": "Investigating identity issue, suppressing immediate lock."}'
```

```bash
curl -X POST "http://localhost:8000/api/v1/admin/environment/alpha/restore-continuity" \
     -H "X-Admin-Key: change-me-before-production" \
     -H "Content-Type: application/json" \
     -d '{"reviewer": "admin_cem", "note": "Manual continuity reset after maintenance."}'
```
