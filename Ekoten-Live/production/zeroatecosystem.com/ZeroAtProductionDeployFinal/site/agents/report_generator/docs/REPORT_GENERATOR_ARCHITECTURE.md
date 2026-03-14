# Report Generator Agent — Architecture

## Goal
Generate management-ready reports from approved normalized datasets.

## Inputs
- approved normalized JSON
- approved CSV
- optional manual notes
- optional template preset
- optional brand assets

## Report styles
- zero_standard
- executive_board
- sustainability_esg
- audit_pack
- custom_template

## Output formats
- html
- pdf
- docx
- csv
- json

## Core modules
1. data_loader
2. narrative_builder
3. kpi_block_builder
4. chart_spec_builder
5. template_renderer
6. export_router

## Proposed pipeline
approved dataset
-> report config
-> narrative + KPI assembly
-> template rendering
-> export formatting
-> output bundle

## Output bundle
- report.html
- report.json
- report.csv
- metadata.json
- optional pdf/docx
