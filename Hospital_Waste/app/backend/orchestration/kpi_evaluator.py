from typing import Any, Optional

def evaluate_kpi_state(latest_row: Optional[dict[str, Any]], quality_ratio: float, energy_trend: str) -> dict[str, Any]:
    latest_row = latest_row or {}
    scoring = (latest_row.get("sustainability_scoring") or {})
    scoring_risk = scoring.get("risk")
    scoring_status = scoring.get("status")
    summary = scoring.get("summary") or {}

    if quality_ratio > 0.5:
        severity = "low_confidence"
    elif scoring_risk == "CRITICAL":
        severity = "critical"
    elif scoring_risk == "HIGH":
        severity = "high"
    elif energy_trend == "increasing":
        severity = "monitor"
    elif scoring_status == "score_pending_bed_count_missing":
        severity = "context_missing"
    else:
        severity = "stable"

    return {
        "severity": severity,
        "quality_ratio": round(quality_ratio, 2),
        "energy_trend": energy_trend,
        "scoring_risk": scoring_risk,
        "scoring_status": scoring_status,
        "top_issue": summary.get("top_issue"),
        "quick_action": summary.get("quick_action"),
    }
