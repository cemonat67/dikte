# Agents Phase 2.1 CSV String Parsing Fix Checkpoint — 2026-03-11

## Root cause
CSV values with dot thousand separators were being auto-cast by pandas before custom normalization.
Example:
- "1.310" became 1.31 too early

## Fix applied
- CSV files now load with dtype=str and keep_default_na=False
- XLSX files also load as strings before normalization
- custom numeric coercion now receives raw textual values

## Expected behavior
- 1.310 -> 1310
- 19.220 -> 19220
- 13.340 -> 13340
- 26.100 -> 26100
