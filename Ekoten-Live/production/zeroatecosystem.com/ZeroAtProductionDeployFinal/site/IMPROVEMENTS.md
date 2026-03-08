# Zero@Design — Improvements & Ideas Backlog

Last updated: 2026-03-08

This document captures ideas and improvements that are **not implemented yet** but should not be forgotten.

---

# Data Layer

## Larger Synthetic Dataset

Current dataset:

~500 garments

Potential expansion:

- 5,000 garments
- regional production factors
- supplier variability
- transport emissions
- washing lifecycle impact

---

## Carbon Calculator Engine

Develop a product-level carbon calculator.

Formula concept:

fabric_weight × fabric_co2_factor  
+ accessories_co2  
+ process_emissions  
+ lifecycle emissions

= estimated garment CO₂ footprint

---

## Material Substitution Simulation

Example:

Cotton → Recycled Cotton  
Polyester → Recycled Polyester

Calculate CO₂ impact difference.

---

## Carbon Benchmark Bands

Add industry benchmark comparison:

LOW  
MEDIUM  
HIGH  

based on product category averages.

---

# Platform

## Scenario Simulation Engine

Allow scenarios like:

Base  
Stress  
Shock

Used by executive dashboard.

---

## Recommendation Engine

Suggest:

- lower carbon fabric alternatives
- process improvements
- accessory substitutions

---

## ML Readiness

Prepare dataset for:

- similarity search
- carbon prediction
- material substitution modeling

---

# Executive Layer

## CEO Card

Strategic overview

Elements:

- Strategic Risk Index
- Enterprise Signals
- Executive Narrative
- Scenario Toggle

---

## CTO Card

Platform technical health

Elements:

- platform stability
- architecture integrity
- execution velocity
- deployment risk

---

## CFO Card (future)

Financial carbon exposure.

Possible metrics:

carbon cost exposure  
carbon price risk  
supplier carbon intensity

---

# UI

## Product Simulation Page

User selects:

- fabric
- accessories
- processes

System calculates estimated CO₂ footprint.

---

## Carbon Impact Visualizations

Charts:

- CO₂ by product
- CO₂ by fabric
- CO₂ by lifecycle stage

---

# Data Import

Future:

Import real ERP / PLM / supplier data.

Synthetic dataset will then act as fallback baseline.

