# Zero@Design

Zero@Design is a textile carbon simulation and decision-support platform.

The system models:

- textile lifecycle emissions
- fabric composition
- accessories
- garment-level CO₂ estimates

The platform is designed to support:

- design teams
- sourcing teams
- executive decision making

---

# Architecture

Layers:

Data Layer
PostgreSQL + seed datasets

Simulation Layer
Synthetic garment generator

Analytics Layer
SQL views

Executive Layer
Dashboard cards (CEO / CTO)

---

# Development Priority

Current milestone:

Finish CEO Strategic Card.

Next milestone:

Implement CTO Technical Health Card.

---

# Database

Postgres container:

zerodesign-db

Database:

zero_design_co2

---

# Synthetic Dataset

Synthetic garments are used for:

- simulations
- UI testing
- CO₂ estimation

They are stored in:

synthetic_garments table

and generated via:

seed/scripts/generate_synthetic_garment_dataset.py

