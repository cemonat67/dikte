from typing import Any, Optional

def decide_route(
    facility_context: Optional[dict[str, Any]],
    latest_row: Optional[dict[str, Any]],
    quality_ratio: float,
    energy_trend: str,
) -> dict[str, Any]:
    routing_profile = (facility_context or {}).get("routing_profile", "balanced")
    scoring = (latest_row or {}).get("sustainability_scoring", {}) or {}
    risk = scoring.get("risk")
    scoring_status = scoring.get("status")

    if quality_ratio > 0.5:
        return {
            "route": "low_confidence_data_review",
            "priority": "high",
            "persona": "operations",
            "reason": "estimated_data_ratio_high",
        }

    if risk in {"CRITICAL", "HIGH"}:
        return {
            "route": "sustainability_risk_escalation",
            "priority": "high" if risk == "CRITICAL" else "medium",
            "persona": "executive" if routing_profile != "focused" else "operations",
            "reason": f"scoring_risk_{str(risk).lower()}",
        }

    if energy_trend == "increasing":
        return {
            "route": "efficiency_watch_mode",
            "priority": "medium",
            "persona": "operations",
            "reason": "energy_trend_increasing",
        }

    if scoring_status == "score_pending_bed_count_missing":
        return {
            "route": "missing_capacity_context",
            "priority": "medium",
            "persona": "operations",
            "reason": "bed_count_missing",
        }

    return {
        "route": "executive_stability_summary",
        "priority": "low",
        "persona": (facility_context or {}).get("ai_persona_default", "executive"),
        "reason": "stable_baseline",
    }
