import psycopg


def evaluate_factory_state(db_url: str, facility: str = "ekoten"):
    signals = []
    status = "OK"

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select metric_type, avg(value)
                from public.canonical_events
                where facility_id = %s
                  and event_timestamp > now() - interval '24 hours'
                group by metric_type
            """, (facility,))
            metrics = {row[0]: float(row[1]) for row in cur.fetchall()}

    energy = metrics.get("energy_kwh", 0.0)
    production = metrics.get("production_kg", 0.0)
    ph = metrics.get("ph", 7.0)

    if energy > 23000:
        signals.append("energy_spike")

    if production < 20000 and production > 0:
        signals.append("production_drop")

    if ph < 6 or ph > 9:
        signals.append("ph_out_of_range")

    if len(signals) == 1:
        status = "MONITOR"
    elif len(signals) >= 2:
        status = "ALERT"

    return {
        "facility": facility,
        "status": status,
        "signals": signals,
        "metrics_snapshot": metrics,
        "ops_note": "Factory metrics evaluated from the last 24 hours.",
        "finance_note": "Energy and production signals may affect operating cost.",
        "sustainability_note": "Water chemistry and utility usage should be monitored.",
        "recommended_action": "Review the flagged signals and validate process conditions."
    }
