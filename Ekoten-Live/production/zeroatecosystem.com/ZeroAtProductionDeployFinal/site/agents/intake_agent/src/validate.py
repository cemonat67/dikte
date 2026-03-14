from __future__ import annotations

REQUIRED_META_FIELDS = ["source_type", "source_name", "received_at", "facility", "review_status"]

def validate_record(record: dict) -> list[str]:
    errors = []

    meta = record.get("meta", {})
    metrics = record.get("metrics", {})

    for field in REQUIRED_META_FIELDS:
        if not meta.get(field):
            errors.append(f"missing_meta:{field}")

    if not any(v not in (None, "", []) for v in metrics.values()):
        errors.append("missing_metrics:any")

    return errors

def score_confidence(record: dict, errors: list[str]) -> float:
    score = 0.9

    if errors:
        score -= 0.2

    mapped = len(record.get("normalization", {}).get("field_map", {}))
    if mapped < 3:
        score -= 0.15

    if not record.get("meta", {}).get("period_start") and not record.get("meta", {}).get("period_end"):
        score -= 0.05

    if not record.get("meta", {}).get("facility"):
        score -= 0.10

    return max(0.3, min(0.99, round(score, 2)))
