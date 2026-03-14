# Universal Data Intake Agent — Workflow

## Stage 1 — Receive
Input accepted from:
- upload
- drag/drop
- scan
- screenshot
- pasted text
- batch import

Store original source under:
agents/intake_agent/incoming/

## Stage 2 — Classify
Classify source:
- structured: CSV, XLSX, JSON
- semi-structured: PDF, DOCX export
- unstructured: image, screenshot, pasted text

## Stage 3 — Extract
Generate:
- raw extracted text
- detected tables
- detected values
- metadata

Store under:
agents/intake_agent/staging/

## Stage 4 — Normalize
Map extracted fields into canonical schema.
Generate:
- normalized JSON
- flat CSV export
- confidence score
- transform notes

Store under:
agents/intake_agent/normalized/

## Stage 5 — Review
Human review checks:
- units
- period
- facility
- outliers
- duplicate risk
- missing required fields

Store review draft under:
agents/intake_agent/review/

## Stage 6 — Approve / Reject
If approved:
- move normalized payload to approved/
- preserve raw source in archive/
If rejected:
- move draft to rejected/
- append rejection note

## Stage 7 — Publish-ready handoff
Approved payload becomes import-ready for:
- Executive Dashboard
- Reporting Agent
- future DB/API ingest layer
