-- daily_metrics_mock -> zeroCare_operational.daily_metrics

insert into zeroCare_operational.daily_metrics
(
  facility_id,
  metric_date,
  metric_code,
  value,
  unit_code,
  quality_flag,
  calculation_method,
  source_system
)
select
  f.facility_id,
  s.metric_date,
  s.metric_code,
  s.value,
  s.unit_code,
  coalesce(s.quality_flag, 'estimated'),
  coalesce(s.calculation_method, 'staging_import'),
  coalesce(s.source_system, 'staging_csv')
from zeroCare_staging.daily_metrics_mock s
join zeroCare_operational.facilities f
  on f.facility_code = s.facility_code
on conflict (facility_id, department_id, metric_date, metric_code)
do nothing;

-- daily_kpis_mock -> zeroCare_operational.daily_metrics
-- KPI rows are stored as metric rows for dashboard simplicity

insert into zeroCare_operational.daily_metrics
(
  facility_id,
  metric_date,
  metric_code,
  value,
  unit_code,
  quality_flag,
  calculation_method,
  source_system
)
select
  f.facility_id,
  k.metric_date,
  'scope2_location_tco2e',
  k.scope2_location_tco2e,
  'tCO2e',
  'derived',
  'kpi_import',
  'staging_csv'
from zeroCare_staging.daily_kpis_mock k
join zeroCare_operational.facilities f
  on f.facility_code = k.facility_code
on conflict (facility_id, department_id, metric_date, metric_code)
do nothing;

insert into zeroCare_operational.daily_metrics
(
  facility_id,
  metric_date,
  metric_code,
  value,
  unit_code,
  quality_flag,
  calculation_method,
  source_system
)
select
  f.facility_id,
  k.metric_date,
  'waste_cost_try',
  k.waste_cost_try,
  'TRY',
  'derived',
  'kpi_import',
  'staging_csv'
from zeroCare_staging.daily_kpis_mock k
join zeroCare_operational.facilities f
  on f.facility_code = k.facility_code
on conflict (facility_id, department_id, metric_date, metric_code)
do nothing;

-- optional daily risk seed
insert into zeroCare_operational.risk_scores_daily
(
  facility_id,
  metric_date,
  risk_score,
  risk_breakdown
)
select
  f.facility_id,
  k.metric_date,
  least(
    100,
    round(
      (coalesce(k.scope2_location_tco2e,0) * 2.5) +
      (coalesce(k.waste_cost_try,0) / 250.0)
    , 2)
  ) as risk_score,
  jsonb_build_object(
    'climate_proxy', round(coalesce(k.scope2_location_tco2e,0) * 2.5, 2),
    'cost_proxy', round(coalesce(k.waste_cost_try,0) / 250.0, 2),
    'source', 'staging_seed_v1'
  )
from zeroCare_staging.daily_kpis_mock k
join zeroCare_operational.facilities f
  on f.facility_code = k.facility_code
on conflict (facility_id, metric_date)
do nothing;
