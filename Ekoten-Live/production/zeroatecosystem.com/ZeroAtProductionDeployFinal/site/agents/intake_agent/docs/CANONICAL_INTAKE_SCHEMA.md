# Canonical Intake Schema v1

## Goal
Normalize heterogeneous source inputs into the same structure used by the Executive Dashboard manual ESG input flow.

## Supported source types
- csv
- xlsx
- pdf
- scanned_pdf
- image
- screenshot
- pasted_text
- json
- email_export

## Core principles
- preserve source file
- preserve extraction evidence
- do not overwrite raw values
- keep normalized and review-ready versions separate
- confidence + reviewer gate required before approval

## Core metric groups
1. Meta
2. Operations metrics
3. Wastewater quality
4. Production context
5. Financial overlay
6. Evidence
7. Normalization log
8. Review status

## Minimum required fields for MVP
- source_type
- source_name
- received_at
- facility
- period_start or period_end
- at least one operations metric
- review_status
