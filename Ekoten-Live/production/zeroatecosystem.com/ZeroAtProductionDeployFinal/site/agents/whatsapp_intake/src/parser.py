def parse_whatsapp_payload(payload):

    record = {
        "facility": payload.get("facility", "unknown"),
        "water_m3": float(payload.get("water_m3", 0)),
        "energy_kwh": float(payload.get("energy_kwh", 0)),
        "natural_gas_m3": float(payload.get("natural_gas_m3", 0)),
        "production_kg": float(payload.get("production_kg", 0)),
        "source": "whatsapp"
    }

    return record
