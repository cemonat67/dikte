
## ✅ PROMOTE LAYER v1 — COMPLETED (2026-04-06)

### Scope
- staging_daily_metrics → daily_metrics promote pipeline implemented
- READY day-based promotion logic active
- NULL-safe unique constraint applied on daily_metrics
- Duplicate records cleaned

### Features
- Idempotent promote function: zerocare_operational.promote_ready_daily_metrics(...)
- Dry-run support (write=false)
- Audit fields on target:
  - staging_id
  - record_version
  - fingerprint
  - promote_run_id
  - promoted_at
  - updated_at

### Validation
- Initial promote: 7 rows written
- Re-run: written_rows = 0 (idempotent OK)
- staging rows marked as PROMOTED with promote_run_id

### Status
✔ Production-ready (v1)
✔ Safe for orchestration (n8n / API trigger)

