# Deterministic Operational State Engine

## The Philosophy of Singular Truth

The Operational State Engine governs the Zero@Trust platform by guaranteeing that the system exposes exactly ONE dominant operational condition at a time. It rejects the "SaaS notification feed" model entirely. 

### 1. Singleton Governance
When multiple operational shifts occur, the system evaluates their severity and only surfaces the most critical one. 
- **Hierarchy:** `degraded` > `constrained` > `observation` > `intact`
- If an `identity_confidence_drop` (constrained) and a `supplier_behavior_shift` (observation) occur simultaneously, the system will ONLY speak about the identity confidence. The lesser event is held in memory, not added to a scrolling feed.

### 2. Slow Behavioral Rhythm
The engine employs **hysteresis**. A risk signal does not immediately trigger a UI state change. It must persist across multiple engine ticks (persistence >= 2) before it is considered mature enough to surface. This prevents rapid state flipping, blinking alerts, and panic.

### 3. State Hierarchy
- **Intact:** Normal, quiet, negative space preserved.
- **Observation:** A drift is detected but has low severity.
- **Constrained:** A significant drift requiring human governance.
- **Degraded:** A severe failure requiring immediate intervention.
- **Restoring:** The slow, deliberate transition back to Intact following a human action.

### 4. Human Governance Logic
The system never autonomously resolves a surfaced trust event to preserve the illusion of AI. It requires a human to click the CTA (e.g., "Request Verification"). 
- The system responds strictly with: "Human control registered. Returning to intact state."
- It then executes a slow 4-second fade out, deliberately ignoring any new signals during this restoration phase to protect executive calmness.
- The UI triggers an API call (`/api/v1/trust/action/resolve`) to formally resolve the underlying risks in the database, closing the loop.

### 5. Frontend Mapping
The frontend `syncTrustState` polling loop reads the `dominant_condition` object from the API. If present, it maps the title, statement, recommendation, and action to the Trust Event Surface, smoothly fading it into view without disrupting the overarching `preserved` atmosphere.
