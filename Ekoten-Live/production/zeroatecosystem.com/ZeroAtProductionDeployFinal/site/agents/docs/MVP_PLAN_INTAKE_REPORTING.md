# MVP Plan — Data Intake + Reporting

## Phase 1 — Architecture Freeze
- canonical intake schema
- folder structure
- workflow docs
- review flow docs
- report architecture docs

## Phase 2 — Intake MVP
- CSV/XLSX parser
- pasted text parser
- PDF text extraction adapter placeholder
- image/OCR placeholder
- normalized JSON writer
- flat CSV writer
- review draft generator

## Phase 3 — Reporting MVP
- zero_standard html template
- executive_board html template
- json input to html report
- export manifest
- optional pdf/docx hook placeholders

## Phase 4 — Integration Layer
- connect approved intake payloads to dashboard import path
- connect approved payloads to report generator
- keep manual modal as fallback

## MVP success criteria
- one CSV source can be normalized
- one pasted text source can be normalized
- one PDF-derived text payload can be normalized
- one approved dataset can generate zero_standard html report
- one approved dataset can generate executive board summary
