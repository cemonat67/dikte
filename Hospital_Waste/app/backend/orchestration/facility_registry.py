from typing import Optional, Any

FACILITY_REGISTRY = {
    "BALCOVA_MED": {
        "facility_code": "BALCOVA_MED",
        "facility_name": "Demo Hospital Balçova Tıp Merkezi",
        "facility_type": "medical_center",
        "bed_count": None,
        "department_count": 9,
        "routing_profile": "balanced",
        "ai_persona_default": "operations",
        "threshold_profile": "outpatient_standard",
    },
    "CIGLI_HOSP": {
        "facility_code": "CIGLI_HOSP",
        "facility_name": "Demo Hospital Çiğli Hastanesi",
        "facility_type": "hospital",
        "bed_count": 250,
        "department_count": 9,
        "routing_profile": "balanced",
        "ai_persona_default": "executive",
        "threshold_profile": "hospital_standard",
    },
    "CIGLI_MED": {
        "facility_code": "CIGLI_MED",
        "facility_name": "Demo Hospital Çiğli Tıp Merkezi",
        "facility_type": "medical_center",
        "bed_count": None,
        "department_count": 9,
        "routing_profile": "balanced",
        "ai_persona_default": "operations",
        "threshold_profile": "outpatient_standard",
    },
    "DEMO_BORNOVA": {
        "facility_code": "DEMO_BORNOVA",
        "facility_name": "Demo Hospital Bornova",
        "facility_type": "private_hospital",
        "bed_count": 260,
        "department_count": 9,
        "routing_profile": "proactive",
        "ai_persona_default": "executive",
        "threshold_profile": "hospital_standard",
    },
    "DEMO_KONAK": {
        "facility_code": "DEMO_KONAK",
        "facility_name": "Demo Hospital Konak",
        "facility_type": "private_hospital",
        "bed_count": 200,
        "department_count": 9,
        "routing_profile": "balanced",
        "ai_persona_default": "executive",
        "threshold_profile": "hospital_standard",
    },
    "DEMO_KSK": {
        "facility_code": "DEMO_KSK",
        "facility_name": "Demo Hospital Karşıyaka",
        "facility_type": "private_hospital",
        "bed_count": 220,
        "department_count": 9,
        "routing_profile": "balanced",
        "ai_persona_default": "executive",
        "threshold_profile": "hospital_standard",
    },
    "DENTAL_CENTER": {
        "facility_code": "DENTAL_CENTER",
        "facility_name": "Demo Hospital Ağız ve Diş Sağlığı Merkezi",
        "facility_type": "dental_center",
        "bed_count": None,
        "department_count": 9,
        "routing_profile": "focused",
        "ai_persona_default": "operations",
        "threshold_profile": "specialty_center",
    },
    "EYE_CENTER": {
        "facility_code": "EYE_CENTER",
        "facility_name": "Demo Hospital Göz Tıp Merkezi",
        "facility_type": "eye_center",
        "bed_count": None,
        "department_count": 9,
        "routing_profile": "focused",
        "ai_persona_default": "operations",
        "threshold_profile": "specialty_center",
    },
    "MENEMEN_HOSP": {
        "facility_code": "MENEMEN_HOSP",
        "facility_name": "Demo Hospital Menemen Kampüsü",
        "facility_type": "hospital",
        "bed_count": 120,
        "department_count": 9,
        "routing_profile": "conservative",
        "ai_persona_default": "executive",
        "threshold_profile": "hospital_standard",
    },
}

ALIASES = {
    "demo_hospital": "CIGLI_HOSP",
}

def resolve_facility_code(facility_id: Optional[str], facility_code: Optional[str]) -> Optional[str]:
    value = facility_code or facility_id
    if not value:
        return value
    raw = str(value).strip()
    return ALIASES.get(raw.lower(), raw)

def get_facility_context(facility_id: Optional[str] = None, facility_code: Optional[str] = None) -> Optional[dict[str, Any]]:
    resolved = resolve_facility_code(facility_id, facility_code)
    if not resolved:
        return None
    ctx = FACILITY_REGISTRY.get(resolved)
    if not ctx:
        return {
            "facility_code": resolved,
            "facility_name": resolved,
            "facility_type": "unknown",
            "bed_count": None,
            "department_count": None,
            "routing_profile": "balanced",
            "ai_persona_default": "executive",
            "threshold_profile": "hospital_standard",
        }
    return dict(ctx)
