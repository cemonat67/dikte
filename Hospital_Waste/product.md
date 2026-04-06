
## 🚀 Data Pipeline — Promote Layer (v1)

### Flow
staging_daily_metrics → READY filter → promote → daily_metrics

### Guarantees
- No duplicates (unique index + NULL-safe scope)
- Idempotent execution (re-run safe)
- Full lineage tracking (staging_id, fingerprint, run_id)

### Function
zerocare_operational.promote_ready_daily_metrics(
  p_facility_id uuid,
  p_start_date date,
  p_end_date date,
  p_dry_run boolean
)

### Behavior
- Only READY days are promoted
- Supports dry-run validation
- Writes only new or changed records
- Marks staging rows as PROMOTED

### Next Phase
- API endpoint integration
- n8n orchestration trigger
- KPI aggregation layer

