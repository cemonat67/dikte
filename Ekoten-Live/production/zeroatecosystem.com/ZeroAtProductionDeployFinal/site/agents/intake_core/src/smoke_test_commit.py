from agents.intake_core.src.commit_service import CommitService
from agents.intake_core.src.intake_writer import IntakeWriter
from agents.intake_core.src.metric_registry import MetricRegistry
from agents.intake_core.src.facility_registry import build_default_ekoten_registry

csv_bytes = b"""facility,event_timestamp,water_m3,energy_kwh,natural_gas_m3,steam_ton,co2_kg,wastewater_m3,production_kg,cod_mg_l,bod_mg_l,tss_mg_l,ph
ekoten,2026-03-13T08:00:00Z,12,100,5,,44,8,500,210,120,80,7.2
ekoten,2026-03-13T09:00:00Z,13,101,6,,45,9,510,212,121,81,7.1
"""

svc = CommitService(
    intake_writer=IntakeWriter(),
    metric_registry=MetricRegistry(),
    facility_registry=build_default_ekoten_registry(),
)

result = svc.commit_csv_bytes(
    file_bytes=csv_bytes,
    file_name="smoke_commit.csv",
    zero_fill_missing=True,
)

print({
    "inserted": result.inserted,
    "duplicate": result.duplicate,
    "rejected": result.rejected,
    "total_input_rows": result.total_input_rows,
    "total_expanded_events": result.total_expanded_events,
    "zero_filled_fields": result.zero_filled_fields,
    "warnings": result.warnings,
    "rejected_rows": result.rejected_rows,
})
