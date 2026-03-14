# Zero@Production — Dashboard Registry

Project Root
~/Desktop/Ekoten-Live/production/zeroatecosystem.com/ZeroAtProductionDeployFinal

Local Server
http://127.0.0.1:8099

Purpose
This document tracks all dashboards, modules, and navigation flow used in the Zero@Production Ekoten demo.

---

# Demo Navigation Flow

index.html
↓
finishing-dpp.html
↓
fabric-dpp.html
↓
index.html#executive-personas

---

# Dashboard Registry

| Dashboard | File | Local URL | Role | Description | Links To |
|-----------|------|----------|------|-------------|----------|
| Main Dashboard | site/index.html | /index.html | Entry | Main landing page + executive layer | Finishing / Fabric |
| Executive Personas | site/index.html#executive-personas | /index.html#executive-personas | Executive | CEO/CFO/CTO decision layer | Modals / PDF export |
| Finishing DPP | site/finishing-dpp.html | /finishing-dpp.html | Module | Finishing production KPIs | Fabric |
| Fabric DPP | site/fabric-dpp.html | /fabric-dpp.html | Module | Fabric production KPIs | Executive |

---

# Detailed Descriptions

## Executive Personas Layer

File
site/index.html

Components
CEO card  
CFO card  
CTO card  
CFO Shock modal  
Executive PDF export  

Purpose
Provide board-level decision overview combining risk, financial exposure and operational data.

---

## Finishing Dashboard

File
site/finishing-dpp.html

Purpose
Finishing production monitoring dashboard.

Key Metrics
batch volume  
energy cost  
chemical cost  
rework  
yield loss  

Feeds
Executive hidden cost aggregation.

---

## Fabric Dashboard

File
site/fabric-dpp.html

Purpose
Fabric production monitoring dashboard.

Key Metrics
throughput  
rework  
yield loss  
energy cost  
hidden cost  

Feeds
Executive hidden cost aggregation.

---

# Change Log

2026-03-07
Executive dashboard confirmed inside site/index.html

2026-03-07
Fabric executive navigation target defined:

index.html?facility=ekoten#executive-personas

