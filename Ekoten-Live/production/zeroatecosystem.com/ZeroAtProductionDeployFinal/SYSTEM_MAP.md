# Zero@Production — System Map

Project Root
~/Desktop/Ekoten-Live/production/zeroatecosystem.com/ZeroAtProductionDeployFinal

Local Server
http://127.0.0.1:8099

Purpose
This document maps the core structure of the Zero@Production Ekoten demo system:
pages, modules, navigation, data loaders, and executive flow.

---

## Core Navigation

index.html
↓
finishing-dpp.html
↓
fabric-dpp.html
↓
index.html#executive-personas

---

## Main Pages

- site/index.html
- site/finishing-dpp.html
- site/fabric-dpp.html
- site/fibre-dpp.html
- site/yarn-dpp.html
- site/chemicals-dyes-management.dpp.html
- site/GarmentDPP.html
- site/packaging-dpp.html
- site/delivery-dpp.html
- site/transport-dpp.html
- site/energy-dpp.html
- site/office-dpp.html
- site/retail-dpp.html
- site/it-dpp.html

---

## Executive Layer

Host File
site/index.html

Anchor
#executive-personas

Components
- CEO persona card
- CFO persona card
- CTO persona card
- CFO Shock modal
- Executive PDF export
- Role/focus demo logic

Target URL
index.html?facility=ekoten#executive-personas

---

## Module Pages

### Finishing
File
site/finishing-dpp.html

Role
Production KPI module for finishing operations.

### Fabric
File
site/fabric-dpp.html

Role
Production KPI module for fabric operations.

---

## JS / Data Layer

Potential key assets
- site/assets/js/data-loader.js
- site/assets/js/finishing-synthetic-engine.js
- site/assets/js/executive-bridge.js

Notes
- finishing-synthetic-engine.js is active in finishing flow
- executive-bridge.js may be used for aggregated executive summary logic
- data-loader.js is part of module loading flow

---

## Documentation Files

- DASHBOARD_REGISTRY.md
- SYSTEM_MAP.md

---

## Change Log

2026-03-07
Created initial SYSTEM_MAP.md

