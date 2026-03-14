# Agents Phase 2.1 Numeric Fix Checkpoint — 2026-03-11

## Fix applied
- improved numeric coercion for TR/EU and mixed separators
- dot-only thousand-separated values now parse correctly
- comma decimals remain supported
- mixed US/EU numeric formats handled more safely

## Example
- 1.310 -> 1310
- 19.220 -> 19220
- 7,1 -> 7.1
- 1.234,56 -> 1234.56
