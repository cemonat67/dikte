# Operational Scenario Orchestration

## The Philosophy of Institutional Realization
Zero@Trust does not "alert" executives; it allows them to *realize* operational shifts. Escalation is a slow, dignified process. The system absorbs noise and only surfaces verified, persistent conditions.

## 1. Severity Choreography & Suppression Hierarchy

### The Dominant Reality Principle
When multiple events occur, the system evaluates their severity weight and exclusively surfaces the highest-ranking truth. 

| Tier | State | Weight | Psychology | UI Behavior |
|---|---|---|---|---|
| 1 | **Degraded** | `> 0.8` | Severe failure. System integrity compromised. | Dimmed background. Slow fade-in of Trust Event. Tone is absolute. |
| 2 | **Constrained** | `0.5 - 0.79` | Operational drift requiring human oversight. | Subdued atmosphere. Patient presentation of the anomaly. |
| 3 | **Observation** | `0.2 - 0.49` | Minor anomalies. | Invisible to the executive. Absorbed by the state engine. Held in memory. |
| 4 | **Intact** | `< 0.2` | Continuity preserved. | Pure negative space. |

*Suppression Rule:* A `Constrained` event is immediately suppressed if a `Degraded` event matures. The executive is never forced to prioritize; the system has already prioritized.

## 2. Operational Scenario Library

### Scenario A: Supplier Approval Drift
* **Trigger:** Procurement logic deviates from historical baseline.
* **Tier:** Constrained (Weight: 0.6)
* **Pacing:** Requires 3 engine ticks (hysteresis) to surface.
* **Title:** Approval Drift
* **Statement:** Deviation from established baseline.
* **Recommendation:** Human oversight required.
* **Action (CTA):** Maintain Constraint
* **Recovery:** "Human control registered. Returning to intact state." (4-second fade)

### Scenario B: Midnight Executive Login
* **Trigger:** High-privilege access attempt outside institutional rhythm.
* **Tier:** Observation (Weight: 0.4) -> Escalates to Constrained (Weight: 0.7) if evidence maturity drops.
* **Title:** Identity Uncertainty
* **Statement:** Rhythm parameter unmet.
* **Recommendation:** Verification recommended.
* **Action (CTA):** Request Verification

### Scenario C: Document Integrity Degradation
* **Trigger:** Critical compliance artifact expires or hash mismatch detected.
* **Tier:** Degraded (Weight: 0.9)
* **Pacing:** Surfaces after 1 tick. Immediate necessity but presented calmly.
* **Title:** Compliance Rupture
* **Statement:** Artifact integrity compromised.
* **Recommendation:** Halt operations pending review.
* **Action (CTA):** Enforce Halt
* **Recovery:** System waits for external DB resolution, then human clicks "Acknowledge Restoration."

### Scenario D: Payment Verification Mismatch
* **Trigger:** Financial routing data conflicts with established vendor payload.
* **Tier:** Degraded (Weight: 0.85)
* **Title:** Routing Inconsistency
* **Statement:** Financial payload parameters conflict.
* **Recommendation:** Verification required.
* **Action (CTA):** Suspend Routing

## 3. Reaction Psychology & Timing

- **The Deliberate Pause:** No scenario appears instantly. The system waits (1.5s - 3s) before rendering the Trust Event Surface. This mimics institutional processing time.
- **The Dignified Recovery:** When a human resolves a scenario, the system does not flash green or show a checkmark. It dims the text, displays "Human control registered", and waits exactly 4 seconds before slowly dissolving back into the Intact state.
- **Silence as a Feature:** Scenarios below weight 0.5 (Observation) never trigger the Trust Event Surface. They only slightly adjust the hidden `atmospheric_weight`, perhaps causing the background to feel slightly "heavier" without explaining why.

---
**Implementation Note (v15.1 - Supplier Approval Drift):**
The `supplier_approval_drift` scenario has been formally mapped in the `Deterministic State Engine` (`backend/engines/trust.py`). It is triggered at a severity of `0.65`, mapped to the "supplier" category, and surfaces with the precise Title, Statement, Recommendation, and Action defined in Scenario A. The hysteresis logic (delaying until persistence >= 2) successfully prevents it from instantly panicking the UI, and the `/trust/action/resolve` loop successfully clears it.

**Implementation Note (v15.1 - Midnight Executive Login):**
The `midnight_executive_login` scenario has been integrated to demonstrate **maturing risk**. It begins at a low severity (`0.40`), remaining hidden initially. After 2 ticks, it surfaces as an `observation` ("Access rhythm shifted."). If left unresolved, the engine scales its effective severity incrementally. By tick 4, it crosses the `0.5` threshold and deterministically matures into a `constrained` state ("Confidence parameter unmet."), cleanly illustrating the shift from passive observation to active human governance.

**Implementation Note (v15.1 - Document Integrity Degradation):**
The `document_integrity_degradation` scenario proves the system's ability to handle **Tier 1 / Degraded** emergencies without losing composure. Triggered at a severity of `0.90` under the `documentation` category, it dominates all lesser constrained or observation states. Despite being the highest tier of failure, the UI remains perfectly calm, mapping strictly to firm, institutional language ("Hold Continuity") instead of resorting to gamified panic or red alerts.

**Implementation Note (v15.2 - Payment Verification Mismatch & Tier 1 Floor):**
The `payment_verification_mismatch` scenario completes the orchestration library. It injects a highly severe financial anomaly. To guarantee it registers as a `degraded` event even after the strict mathematical decay during the hysteresis period, its severity is deliberately weighted at `0.90` upon intake, and backed by a category-specific "Severity Floor" (`eff_severity = max(eff_severity, 0.85)`). When triggered, it forces the system to enact "Suspend Routing," cementing Zero@Trust's capability to natively freeze operational paths when payload parameters logically conflict.

**Production Verification Note (Absolute Freeze):**
The Scenario Orchestration logic has been successfully deployed and verified in production. A key philosophical triumph observed during live testing: even after an event is explicitly resolved (`dominant_condition: null`), the system's underlying posture remains `burdened` for a period due to atmospheric decay. The system does not pretend "nothing happened" instantly; it slowly and organically restores continuity.
