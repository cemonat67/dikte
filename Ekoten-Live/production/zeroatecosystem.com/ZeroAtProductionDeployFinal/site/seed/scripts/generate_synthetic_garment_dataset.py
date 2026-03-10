import csv
import random
from pathlib import Path

random.seed(42)

out_dir = Path("seed/generated")
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "synthetic_garment_dataset.csv"

genders = ["Men", "Women", "Unisex"]
categories = {
    "Top": ["Basic T-Shirt", "Fashion Tee", "Polo Shirt", "Tank Top", "Long Sleeve Tee"],
    "Bottom": ["Jogger", "Shorts", "Legging", "Sweatpant"],
    "Activewear": ["Performance Tee", "Training Top", "Active Legging", "Gym Short"],
    "Outerwear": ["Hoodie", "Sweatshirt", "Zip Hoodie"]
}

fabric_options = [
    {"fabric_type": "Single Jersey", "composition": "100% Cotton", "gsm_range": "140-180", "fabric_co2": 4.65},
    {"fabric_type": "Pique Knit", "composition": "95% Cotton / 5% Elastane", "gsm_range": "180-220", "fabric_co2": 5.10},
    {"fabric_type": "Interlock", "composition": "88% Polyester / 12% Elastane", "gsm_range": "180-240", "fabric_co2": 6.20},
    {"fabric_type": "Fleece", "composition": "70% Cotton / 30% Polyester", "gsm_range": "240-320", "fabric_co2": 5.80},
    {"fabric_type": "Rib Knit", "composition": "97% Cotton / 3% Elastane", "gsm_range": "180-260", "fabric_co2": 5.00},
    {"fabric_type": "French Terry", "composition": "80% Cotton / 20% Polyester", "gsm_range": "220-300", "fabric_co2": 5.55},
]

accessory_sets = [
    {"accessory_profile": "Label Set", "accessory_co2": 0.03},
    {"accessory_profile": "Label + Hangtag", "accessory_co2": 0.05},
    {"accessory_profile": "Label + Button Set", "accessory_co2": 0.07},
    {"accessory_profile": "Label + Drawcord", "accessory_co2": 0.08},
]

process_profiles = [
    {"process_profile": "Standard Knit Route", "process_co2": 1.95},
    {"process_profile": "Dyed Knit Route", "process_co2": 2.35},
    {"process_profile": "Performance Route", "process_co2": 2.75},
]

weights = {
    "Basic T-Shirt": (0.16, 0.24),
    "Fashion Tee": (0.14, 0.22),
    "Polo Shirt": (0.22, 0.32),
    "Tank Top": (0.10, 0.18),
    "Long Sleeve Tee": (0.20, 0.30),
    "Jogger": (0.35, 0.55),
    "Shorts": (0.18, 0.28),
    "Legging": (0.20, 0.32),
    "Sweatpant": (0.38, 0.58),
    "Performance Tee": (0.14, 0.24),
    "Training Top": (0.16, 0.28),
    "Active Legging": (0.20, 0.34),
    "Gym Short": (0.16, 0.26),
    "Hoodie": (0.45, 0.75),
    "Sweatshirt": (0.40, 0.70),
    "Zip Hoodie": (0.50, 0.80),
}

def rand_weight(product):
    lo, hi = weights[product]
    return round(random.uniform(lo, hi), 3)

def generate_rows(n=250):
    rows = []
    for i in range(1, n + 1):
        category = random.choice(list(categories.keys()))
        product = random.choice(categories[category])
        gender = random.choice(genders)
        fabric = random.choice(fabric_options)
        accessories = random.choice(accessory_sets)
        process = random.choice(process_profiles)

        weight_kg = rand_weight(product)
        garment_fabric_co2 = round(weight_kg * fabric["fabric_co2"], 3)
        total_co2 = round(garment_fabric_co2 + accessories["accessory_co2"] + process["process_co2"], 3)

        rows.append({
            "sku_code": f"ZD-SYN-{i:05d}",
            "gender": gender,
            "category": category,
            "product": product,
            "fabric_type": fabric["fabric_type"],
            "composition": fabric["composition"],
            "gsm_range": fabric["gsm_range"],
            "garment_weight_kg": weight_kg,
            "accessory_profile": accessories["accessory_profile"],
            "process_profile": process["process_profile"],
            "fabric_co2_factor_kg_per_kg": fabric["fabric_co2"],
            "accessory_co2_kg": accessories["accessory_co2"],
            "process_co2_kg": process["process_co2"],
            "estimated_total_co2_kg": total_co2,
            "data_source": "synthetic_v1"
        })
    return rows

rows = generate_rows(250)

with out_file.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated: {out_file}")
print(f"Rows: {len(rows)}")
