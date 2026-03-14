# DATA INTAKE AND REPORTING PLAN

## Objective

Extend the Executive Module with two major capabilities:

1. Universal Data Intake
2. Report Generation

---

## A. Universal Data Intake

### Goal
Enable the system to accept data from many different formats and convert all of them into one trusted schema.

### Input channels
- manual form
- CSV upload
- Excel upload
- PDF upload
- scan upload
- image upload
- screenshot upload
- pasted text

### Processing stages
1. ingest
2. extract
3. normalize
4. map to canonical schema
5. generate CSV
6. store artifacts
7. route to review / approval

### Stored artifacts
- original source
- extracted raw content
- normalized JSON
- generated CSV
- confidence score
- review status
- import metadata

---

## B. Report Generator

### Goal
Generate reports in requested standards and in Zero@ standard.

### Report families
- Zero@Production standard report
- Executive board report
- Sustainability / ESG report
- Data audit report
- custom report template

### Export targets
- PDF
- DOCX
- HTML
- CSV
- JSON

### Processing stages
1. collect source data
2. assemble sections
3. apply standard/template
4. generate report
5. export and archive

---

## Canonical Principle

Any source in
↓
one trusted schema out

This schema must remain aligned with the manual input form and executive calculation logic.

---

## Recommended Build Order

### Phase 1
- canonical schema definition
- CSV/XLSX import
- preview mapping
- CSV generation
- storage of source + normalized JSON

### Phase 2
- PDF import
- image/scan assisted extraction
- confidence scoring
- review queue

### Phase 3
- full report generator
- standard templates
- executive export set
- audit-ready archive

---

## 2026-03-11 — Plan Update After Intake Agent Phase 2 / 2.1

### Intake Track
The intake track has now passed the following checkpoints:
- architecture defined
- canonical schema defined
- parser MVP live
- output writers live
- validation live
- confidence scoring live
- hardening live
- locale-aware numeric normalization fixed
- CSV raw numeric string preservation fixed

### Reporting Track
Current state:
- reporting architecture draft exists

Next implementation target:
- Report Generator MVP skeleton

### Immediate Goals for Reporting MVP
- define report input contract
- define report manifest structure
- create first generator skeleton
- support zero-standard output path
- keep review / approval compatibility with intake outputs
