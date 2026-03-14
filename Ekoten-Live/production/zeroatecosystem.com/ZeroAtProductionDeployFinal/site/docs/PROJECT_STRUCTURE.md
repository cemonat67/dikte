# PROJECT STRUCTURE

## Current Scope

Zero@Ecosystem — Executive Module currently includes:

### UI / Presentation Layer
- `executive.html`
- header action controls
- executive cards
- Operations Layer charts
- Decision Panel
- ESG input modal

### Logic Layer
- Executive Risk Equation Engine
- executive alert consolidation
- decision state mapping
- operations-to-executive signal flow

### Assets / JS
- `assets/js/executive-phase2-risk.js`
- phase-based executive logic additions
- chart rendering helpers and UI event bindings

### Documentation Layer
- project checkpoints
- modal standards
- UI standards
- project status tracking
- changelog and improvements tracking

## Next Planned Structure Expansion

### A. Data Intake Agent Layer
Proposed module group:
- intake source parser
- spreadsheet parser
- PDF parser
- image/scan parser
- normalization mapper
- review queue handler
- CSV export generator

### B. Report Generator Layer
Proposed module group:
- report template selector
- Zero@ standard report renderer
- board report renderer
- ESG report renderer
- audit report renderer
- export adapters (PDF / DOCX / HTML / CSV)

## Suggested Future Folder Expansion

```text
site/
├── assets/
│   ├── js/
│   │   ├── executive-phase2-risk.js
│   │   ├── intake-agent/
│   │   ├── report-agent/
│   │   └── shared/
│   └── css/
├── docs/
├── snapshots/
└── executive.html
---

## 6) `SYSTEM_MAP.md` dosyasını güncelle

```bash
cat > SYSTEM_MAP.md <<'EOF'
# SYSTEM MAP

## Current System

### Core flow
Operations Signals
↓
Executive Risk Engine
↓
Executive Cards
↓
Executive Alert
↓
Decision Panel

## Current operational signal families
- Water
- Energy
- CO2
- Wastewater

## Current executive interpretation layer
- CEO posture
- CFO exposure
- CTO technical integrity

## Current alerting philosophy
Multiple underlying signals may exist, but the Executive Layer consolidates them into a decision-oriented alert when necessary.

Principle:
- operators see signals
- executives see decisions

## Planned Expanded System Map

Raw Data Sources
↓
Universal Data Intake Agent
↓
Canonical Intake Schema
↓
Manual Form / Auto-Fill Draft
↓
Risk Engine
↓
Executive Dashboard
↓
Report Generator Agent
↓
Exports / Archives / Audit Trail

## Supported future source types
- CSV
- XLSX
- PDF
- scanned document
- image upload
- screenshot
- pasted text

## Planned persistent artifacts
- original source file
- extracted raw text
- normalized JSON
- generated CSV
- review status
- audit metadata

## Planned report families
- Zero@Production standard report
- Executive board report
- Sustainability / ESG report
- Data audit report
- custom template report

---

## 2026-03-11 — Agent Layer Additions

### Agent Documents
- `AGENTS.md`
- `AGENTS_PHASE2_CHECKPOINT_2026-03-11.md`
- `AGENTS_PHASE21_HARDENING_CHECKPOINT_2026-03-11.md`
- `AGENTS_PHASE21_NUMERIC_FIX_CHECKPOINT_2026-03-11.md`
- `AGENTS_PHASE21_CSV_STRING_FIX_CHECKPOINT_2026-03-11.md`
- `AGENTS_ROADMAP_2026-03-11.md`
- `DATA_INTAKE_AND_REPORTING_PLAN.md`

### Intake Agent Scope
The Universal Data Intake Agent currently covers:
- multi-source intake architecture
- canonical normalization
- parser layer for CSV and pasted text
- validation and confidence scoring
- review manifest generation
- normalized JSON export
- flat CSV export
- hardening and fingerprinting

### Reporting Agent Status
Reporting is currently defined at architecture / planning level.
Implementation next target:
- Report Generator MVP skeleton


### agents/sap_mock_feeder

Simulates a live **SAP / ERP operational data feed** into Zero@Production.

Structure:

agents/sap_mock_feeder
│
├── config
│   └── feeder_config.json
│
├── exports
│   └── sap_export_live.csv
│
└── src
    ├── sap_event_generator.py
    ├── sap_api_sender.py
    ├── sap_csv_writer.py
    └── sap_feeder_runner.py

Responsibilities:

• Generate realistic production events  
• Simulate ERP → platform ingestion  
• Support API delivery  
• Support CSV export  
• Support burst migration simulation

Used for:

• demo data
• ingestion testing
• dashboard live feed simulation
