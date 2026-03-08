# Zero@Design — Project Status

Last updated: 2026-03-08

---

# Platform Overview

Zero@Design is a carbon estimation and simulation platform for textile products.

The platform models:

- textile lifecycle processes
- material compositions
- accessories
- process emissions
- garment level CO₂ estimates

The goal is to support **design, sourcing and executive decision making**.

---

# Environment

Host:

MacBook M1  
Docker

Database:

PostgreSQL 16 (postgres:16-alpine)

Container:

zerodesign-db

Port:

5432

Database name:

zero_design_co2

---

# Database Structure

Core tables:

processes  
emissions  
lifecycle_master  
fabrics  
accessories  

Synthetic simulation table:

synthetic_garments

---

# Baseline Seed Data

processes        : 7  
emissions        : 7  
lifecycle_master : 7  
fabrics          : 5  
accessories      : 5  

---

# Synthetic Dataset

Table:

synthetic_garments

Rows:

~500 synthetic garment SKUs

Purpose:

- simulation
- demo scenarios
- UI dataset
- CO₂ estimation testing

---

# Data Views

v_synthetic_carbon_bands  
v_synthetic_garment_summary

Used by:

- dashboard
- UI layer
- analytics

---

# Seed & Data Scripts

seed/scripts/bootstrap_zerodesign.sh  
seed/scripts/reset_and_reseed.sh  
seed/scripts/import_synthetic_garments.sh  
seed/scripts/export_seed_csvs.sh  
seed/scripts/generate_synthetic_garment_dataset.py  

---

# Current Product Focus

Executive Layer

Priority sequence:

1️⃣ CEO Card (finalize)

2️⃣ CTO Card (design + implement)

3️⃣ Executive dashboard structure

The database layer is considered **stable enough for UI development**.

Further DB changes should only happen if required by executive features.

---

# Architectural Layers

Data Layer
PostgreSQL + seed datasets

Simulation Layer
synthetic garment generator

Analytics Layer
SQL views

Executive Layer
Dashboard cards (CEO / CTO)

---

# Next Milestone

Finish CEO Strategic Card.

After that:

Implement CTO Technical Health Card.

