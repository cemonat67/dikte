# Report Generator MVP — Next Phase (2026-03-11)

## Status
Planned next implementation phase after Universal Data Intake Agent Phase 2 / 2.1.

## Preconditions already completed
- intake architecture docs
- canonical intake schema
- review / approval flow
- parser layer
- normalized JSON output
- flat CSV output
- review manifest output
- validation
- confidence scoring
- hardening
- locale-aware numeric fixes
- CSV raw string preservation before normalization

## MVP Goal
Create the first Report Generator implementation skeleton that can consume reviewed intake outputs and produce structured report artifacts.

## Proposed MVP Scope
- report input contract
- generator skeleton
- report manifest
- markdown output
- JSON summary output
- zero-standard output path
- compatibility with review / approval state

## Out of Scope for this MVP
- advanced templating
- rich PDF rendering
- external connectors
- auto-distribution
- UI changes

## Definition of Done
- generator skeleton exists
- input and output contracts are documented
- sample artifact path is defined
- docs reflect generator status
