# Zero@Design — Project Structure

This document describes the recommended directory structure for the Zero@Design platform.

The goal is to keep the project organized as it grows.

---

# Root Structure

zerodesign/

docs/  
database/  
seed/  
data/  
dashboard/  
scripts/  
README.md  

---

# docs/

Project documentation.

Files:

PROJECT_STATUS.md  
IMPROVEMENTS.md  
DECISIONS.md  
PROJECT_STRUCTURE.md  

Purpose:

- track project status
- record architectural decisions
- capture future ideas
- document system structure

---

# database/

Database related artifacts.

Subfolders:

schema/  
views/  
migrations/  

---

## database/schema/

SQL definitions of core tables.

Example:

tables.sql

---

## database/views/

SQL views used by the analytics and dashboard layers.

Examples:

v_synthetic_carbon_bands.sql  
v_synthetic_garment_summary.sql  

---

## database/migrations/

Future database schema migrations.

---

# seed/

Seed data used to initialize the platform.

Subfolders:

sql/  
exports/  
scripts/

---

## seed/sql/

Core seed SQL files.

001_processes.sql  
002_emissions.sql  
003_lifecycle_master.sql  
004_fabrics.sql  
005_accessories.sql  

---

## seed/exports/

CSV exports of seed datasets.

Used for:

- inspection
- sharing
- re-import

---

## seed/scripts/

Scripts used for seed management.

bootstrap_zerodesign.sh  
reset_and_reseed.sh  
import_synthetic_garments.sh  
export_seed_csvs.sh  
generate_synthetic_garment_dataset.py  

---

# data/

Data used by the platform.

Subfolders:

synthetic/  
imported/  
curated/  

---

## data/synthetic/

Synthetic datasets used for simulation and testing.

Example:

synthetic_garment_dataset.csv

---

# dashboard/

UI layer.

Subfolders:

executive/  
assets/  

---

## dashboard/executive/

Executive dashboard components.

Examples:

ceo_card.html  
cto_card.html  

---

# scripts/

Utility scripts not directly related to seed or DB setup.

---

# Design Principles

The project structure follows a separation of concerns:

docs/ → documentation  
database/ → database definitions  
seed/ → seed data and initialization scripts  
data/ → datasets  
dashboard/ → UI components  
scripts/ → utility scripts  

---

# Future Growth

Possible future directories:

api/  
services/  
models/  
ml/  

These will support:

- carbon calculation engines
- machine learning models
- scenario simulation
- API services

