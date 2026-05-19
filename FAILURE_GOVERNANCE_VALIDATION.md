# Zero@Trust — Failure Governance Validation Pack

This document formalizes the validation protocols for the **v16 Institutional Reliability & Failure Governance** layer. It proves that failure within Zero@Trust is no longer an unhandled exception, but a governed, institutional operating posture.

## 1. Network Disruption (Calm Degradation)
**Objective:** Prove the frontend UI does not panic when the edge proxy or FastAPI container becomes unreachable.
**Execution:**
1. Stand up the production Docker stack.
2. Open the frontend in a browser (`https://zerotrust.zeroatecosystem.com/`).
3. Run `docker compose -f docker-compose.prod.yml stop zerotrust-api`.
4. Observe the frontend polling rhythm.
**Acceptance Criteria:**
- [ ] No red `ECONNREFUSED` or `502 Bad Gateway` errors render on the screen.
- [ ] Polling backoff engages natively, decaying from 10s to 30s intervals.
- [ ] Visual atmosphere slows its transitions, entering the frozen/constrained stillness mode.
- [ ] The core message transitions cleanly to `"System continuity is temporarily constrained."`

## 2. Recovery Governance (Silent Reconciliation)
**Objective:** Prove the UI slowly steps down from a disruption rather than instantly snapping back.
**Execution:**
1. Leave the API stopped for 3 minutes.
2. Run `docker compose -f docker-compose.prod.yml start zerotrust-api`.
3. Monitor the `/health` endpoint and frontend console.
**Acceptance Criteria:**
- [ ] The `/health` endpoint explicitly outputs `"status": "recovering"` for the first 60 seconds after the container boot.
- [ ] The frontend detects the successful response and steps the polling interval down sequentially (e.g., 30s -> 25s -> 20s -> 10s).
- [ ] The frontend displays the phrase `"Operational continuity recovering."` until the rhythm is fully normalized.
- [ ] No rapid "Green Success" flashes or re-rendering bursts occur.

## 3. Database Partition (Read-Only Continuity)
**Objective:** Prove the `last_known_safe_state` isolates the frontend from total database collapse.
**Execution:**
1. Run `docker compose -f docker-compose.prod.yml stop postgres`.
2. Observe the frontend UI.
3. Query the `GET /api/v1/trust/state` endpoint manually.
**Acceptance Criteria:**
- [ ] API does not return a `500 Internal Server Error`.
- [ ] The payload returns cleanly with `"temporal_state": "frozen"`, `"posture": "constrained"`, and `"continuity_mode": "read_only"`.
- [ ] The frontend remains fully structured, preserving the last known safe variables while locking into the constrained visual freeze.

## 4. Admin Snapshots (Governance Continuity)
**Objective:** Prove executive oversight does not shatter under database failure.
**Execution:**
1. While Postgres is stopped, obtain a valid JWT token (assuming login occurred prior to failure, or use a long-lived test token).
2. Query `GET /api/v1/admin/environment/default/summary`.
**Acceptance Criteria:**
- [ ] Endpoint does not crash or leak `SQLAlchemyError` stack traces.
- [ ] Returns the frozen `last_known_admin_summary` with `latest_posture` forced to `"constrained"` and `temporal_state` to `"frozen"`.

## 5. Webhook Deferred Ingestion (Write-Path Integrity)
**Objective:** Prove external pipelines do not drop data when persistence is unreachable.
**Execution:**
1. While Postgres is stopped, send a valid payload to `POST /api/v1/webhooks/signal` with the correct `X-Webhook-Secret`.
**Acceptance Criteria:**
- [ ] Response returns an HTTP `503 Service Unavailable` status code.
- [ ] The JSON payload clearly states: `{"ok": false, "status": "deferred", "message": "Operational continuity preserved. Retry deferred."}`.
- [ ] No Database stack traces are leaked to the external pipeline.

## 6. Tenant Isolation Strictness under Failure
**Objective:** Prove the in-memory fallback cache respects exact multi-tenant boundaries.
**Execution:**
1. Seed the cache by visiting `?env=finance` and `?env=default` while the DB is active.
2. Stop the PostgreSQL container.
3. Query `/trust/state?environment_id=finance` and `/trust/state?environment_id=default`.
**Acceptance Criteria:**
- [ ] `finance` returns its precise frozen state.
- [ ] `default` returns its precise frozen state.
- [ ] An un-cached environment request (`?env=never-seen`) does not crash, but securely returns the baseline frozen JSON template.

## Success Criterion
> Failure is no longer an exception. It is a governed operating posture.
