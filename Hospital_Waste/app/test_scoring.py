from backend.engine.scoring_engine import calculate_total

data = {
    "energy_kwh_per_patient": 22,
    "water_m3_per_patient": 1.1,
    "waste_kg_per_patient": 1.5
}

result = calculate_total(data)

print(result)

