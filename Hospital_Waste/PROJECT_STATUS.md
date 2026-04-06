
## 2026-04-04 Checkpoint
- Hospital dashboard popup/event delegation bug fixed
- Hospital Intake / Intake Hub / Executive Reports Center all working
- Live deploy verified
- Next focus: fill popup contents with meaningful executive/demo content

## 🚨 DATA PIPELINE STATUS — CRITICAL

### Current State
- Latest data in `core_metric_readings`: **2026-03-30**
- API endpoint `/api/dashboard/latest` returns this data correctly
- Dashboard displays **"LIVE"**, but data is **NOT updating**
- `data_quality = "actual"` -> misleading label

### Diagnosis
The data ingestion pipeline is not running.
Possible causes:
- missing cron job
- stopped scheduler
- one-time seed execution only

### Impact
- Dashboard is NOT real-time
- "LIVE" label creates false perception
- Demo / client trust risk: HIGH

### Decision
- Treat system as STATIC DEMO MODE until pipeline is fixed
- Do NOT present as live system in current state

### Next Actions
1. Identify ingestion mechanism (cron / script / job)
2. Restart or rebuild daily data pipeline
3. Add data freshness check (`last_seen_at` vs now)
4. Update UI:
   - show "Last updated: X days ago"
   - disable LIVE if stale > 24h

### Status
- OPEN
- BLOCKER FOR PRODUCTION DEMO


## 🚨 SYNTHETIC GENERATOR STATUS — LEGACY / NOT LIVE-SAFE

### Verified Findings
- Existing script: `/opt/hospital_app/app/scripts/generate_validate_promote_synthetic.py`
- Script runs only with app venv (`.venv`)
- Script is hardcoded to March 2026
- Script is NOT rolling / NOT date-aware / NOT live-safe
- After execution, database still ends at `2026-03-30`
- Check on `2026-03-29` to `2026-03-31` shows only:
  - `2026-03-30 | synthetic | 11`

### Conclusion
Legacy synthetic generator cannot be used as a real-time or daily live pipeline.

### Decision
- Retire legacy generator for production live narrative
- Build new rolling daily generator
- Add cron after new generator is verified

### Status
- OPEN
- BLOCKER FOR LIVE DATA CLAIM
