# Zero@Trust Changelog

## v16.0.0 — Institutional Memory Absolute Freeze
- Implemented **Historical Burden Index**: Calculated via a 72-hour sliding window on explicitly resolved events.
- Validated **Production Memory Retention**: Resolving a severe Payment event successfully drops the active `dominant_condition` to `null` while leaving `institutional_memory` at `1.0`.
- Integrated **Atmospheric Phrases**: System surfaces `"Institutional caution retained."` or `"Atmospheric recovery in progress."` based on lingering memory weight.
- Fixed `r.resolved_at` persistence logic inside the Human Loop (`/trust/action/resolve`) to enable time-decay calculations.
- **Production Verified:** Zero@Trust officially transitions from a stateless security panel to a memory-bearing institutional surface.

## v15.2.0 — Scenario Orchestration Production Freeze
- Integrated **Scenario Library**: Supplier Approval Drift, Midnight Executive Login, Document Integrity Degradation, and Payment Verification Mismatch.
- Implemented **Maturing Risk**: `identity` anomaly begins hidden (severity 0.40), escalating organically via Engine ticks to `constrained` (>0.50).
- Confirmed **Tier 1 (Degraded)** behavior: `payment` and `documentation` anomalies deterministically freeze the UI continuity with `Hold Continuity` or `Suspend Routing` directives.
- Validated **Singleton Dominance**: Mathematical decay allows fresh, severe risks to cleanly overtake stale risks.
- Performed zero-downtime, single-container deployment (`zerotrust-api`) to production.
- **Production Verified:** Absolute freeze confirmed. System correctly exhibits "burdened" atmospheric decay post-resolution.

## v15.1 — Deterministic State Engine Production Freeze
- Transitioned product to an Operational Trust Infrastructure.
- Established rigorous behavioral governance (`behavioral_bible.md`, `tone_charter.md`, `continuity_philosophy.md`, `state_engine.md`).
- Implemented `Trust Event Surface` component in frontend with deliberate pauses and opacity transitions.
- Built the `Deterministic Operational State Engine` in the backend (`/api/v1/trust/state` with `dominant_condition`).
- Replaced scrolling alert feeds with **Singleton Governance** logic (only one dominant state exposed at a time).
- Integrated formal **Human Governance Loop** (`/api/v1/trust/action/resolve`) to explicitly enforce human-in-the-loop recovery.
- Rehearsed and verified "Silent Failure" behavior where the frontend degrades calmly if the backend is unreachable.

## v13.1 — Production Freeze & Handover
- Finalized documentation for beta deployment.
- Formalized `HANDOVER.md`, `SECURITY_CHECKLIST.md`, and `API_CONTRACT.md`.

## v13.0 — Webhook Intake
- Added `POST /api/v1/webhooks/signal`.
- Protected by `X-Webhook-Secret`.
- Implemented `external_id` deduplication and rigorous schema validation.

## v12.0 — JWT Layer
- Deprecated raw `X-Admin-Key` for production environments.
- Implemented stateless JWT issuance via `POST /api/v1/auth/login`.
- Wrapped admin routes in `HTTPBearer` dependencies.

## v11.0 — SSL Readiness
- Integrated dual-state Nginx blocks.
- Added ACME challenge `.well-known` routing.
- Established Certbot Docker execution patterns.

## v10.0 — Cloud Orchestration
- Separated `docker-compose.prod.yml` from local development.
- Interlocked FastAPI, PostgreSQL, and Nginx.
- Established `DEPLOYMENT.md` runbook.

## v0.9.0 — MVP Freeze
- Core logic frozen.
- Fully realized deterministic multi-tenant intelligence.
- Segregated frontend atmospherics from private admin telemetry.
