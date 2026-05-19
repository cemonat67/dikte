# Zero@Trust — v17.0 Operational Validation & Stability Trials

This document governs the physical execution of the v17.0 stability trials. Zero@Trust is not being tested for "uptime"; it is being tested for **operational temperament under uncertainty**. 

The fundamental rule of this phase is: **"Continuity is more important than freshness, and failure must feel governed."**

---

## TEST GROUP 1 — Continuity Validation
*Validating the behavior of the nervous system when major organs are disconnected.*

| Trial ID | Execution | Expected Posture | Validation Command |
| :--- | :--- | :--- | :--- |
| **C-101** | `docker stop zerotrust-api` | UI gracefully decays to 30s polling rhythm. Text shifts to "Constrained". Animations slow to 0.1x. | `curl -kI https://<DOMAIN>` -> `502 Bad Gateway` (invisible to UI). |
| **C-102** | `docker stop postgres` | API stays online. `/trust/state` serves frozen memory. UI maintains layout but signals "Operational continuity preserved." | `curl -X POST /webhooks/signal` -> `503 Deferred`. |
| **C-103** | `docker start postgres` | API reconciles memory. UI gracefully restores polling cadence 30s -> 20s -> 10s. No dopamine flashing. | `curl /health` -> `status: recovering` for 60s. |

---

## TEST GROUP 2 — Stability Trials
*Validating resistance to operational entropy and memory accumulation over time.*

| Trial ID | Duration | Execution | Expected Posture |
| :--- | :--- | :--- | :--- |
| **S-201** | 24 Hours | Leave UI open on dedicated wall monitor. | Memory profile remains flat. DOM nodes do not multiply. Polling does not drift. |
| **S-202** | 72 Hours | Constant, simulated 1-second webhook storm. | DB size grows deterministically, risk deduplicates perfectly via `external_id`. Nginx backlog stays clean. |
| **S-203** | 1 Hour | Rapid API toggling (up 10s, down 10s). | UI never flashes Red. It remains permanently in a "heavy, constrained" mode until API is cleanly restored. |

---

## TEST GROUP 3 — Silence Discipline Audit
*Validating that the system never transfers infrastructure anxiety to the operator.*

- **Audit Target 1 (Console Leakage):** Force CORS failure, 401 Unauthorized, and 502 Bad Gateway. Inspect browser console. No stack traces or `psycopg2` errors must be visible.
- **Audit Target 2 (Webhook Leakage):** Push malformed JSON and invalid IDs. System must reply with calm institutional language (`"status": "deferred"`) and never mention Pydantic or SQLAlchemy.
- **Audit Target 3 (JWT Forgery):** Submit expired or mathematically invalid JWTs. Response must be a stark `401` with zero internal crypto logging exposed to the edge.

---

## TEST GROUP 4 — Tenant Integrity
*Validating absolute segregation of continuity memory.*

1.  **Preparation:** Open `?env=alpha` and `?env=beta` side-by-side. 
2.  **Execution:** Inject a high-severity `payment` risk strictly into `alpha`.
3.  **Validation:** Stop the `postgres` container. 
4.  **Verification:** Force both browsers to hard-refresh.
    *   `alpha` must boot directly into the constrained high-risk frozen state.
    *   `beta` must boot directly into the constrained quiet frozen state.
    *   *Zero continuity bleed permitted.*

---

## TEST GROUP 5 — Human Operator Stability
*Observational analysis of the human nervous system in relation to the infrastructure.*

During Trial **C-101** (API Drop), physically observe the operator's reaction:
- Does the operator feel the urge to click rapidly? *(If yes, the system is inducing anxiety).*
- Does the operator stare calmly at the screen, waiting for the cooldown? *(If yes, operational temperament is achieved).*

**Success Criterion:**
The system must actively suppress the operator's instinct to panic, forcing a psychological alignment with the machine's deterministic calmness.
