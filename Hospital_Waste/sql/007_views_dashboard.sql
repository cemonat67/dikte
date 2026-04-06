create or replace view zeroCare_operational.vw_dashboard_daily as
select
  f.facility_code,
  f.facility_name,
  dm.metric_date,
  max(case when dm.metric_code = 'electricity_kwh' then dm.value end) as electricity_kwh,
  max(case when dm.metric_code = 'water_m3' then dm.value end) as water_m3,
  max(case when dm.metric_code = 'medical_waste_kg' then dm.value end) as medical_waste_kg,
  max(case when dm.metric_code = 'pathological_waste_kg' then dm.value end) as pathological_waste_kg,
  max(case when dm.metric_code = 'general_waste_kg' then dm.value end) as general_waste_kg,
  max(case when dm.metric_code = 'scope2_location_tco2e' then dm.value end) as scope2_location_tco2e,
  max(case when dm.metric_code = 'waste_cost_try' then dm.value end) as waste_cost_try
from zeroCare_operational.daily_metrics dm
join zeroCare_operational.facilities f
  on f.facility_id = dm.facility_id
group by
  f.facility_code,
  f.facility_name,
  dm.metric_date;

create or replace view zeroCare_operational.vw_dashboard_latest as
select distinct on (facility_code)
  facility_code,
  facility_name,
  metric_date,
  electricity_kwh,
  water_m3,
  medical_waste_kg,
  pathological_waste_kg,
  general_waste_kg,
  scope2_location_tco2e,
  waste_cost_try
from zeroCare_operational.vw_dashboard_daily
order by facility_code, metric_date desc;

create or replace view zeroCare_operational.vw_facility_summary as
select
  facility_code,
  facility_name,
  min(metric_date) as first_day,
  max(metric_date) as last_day,
  round(avg(electricity_kwh)::numeric, 2) as avg_electricity_kwh,
  round(avg(water_m3)::numeric, 2) as avg_water_m3,
  round(avg(medical_waste_kg)::numeric, 2) as avg_medical_waste_kg,
  round(avg(scope2_location_tco2e)::numeric, 4) as avg_scope2_location_tco2e,
  round(avg(waste_cost_try)::numeric, 2) as avg_waste_cost_try,
  round(sum(waste_cost_try)::numeric, 2) as total_waste_cost_try
from zeroCare_operational.vw_dashboard_daily
group by facility_code, facility_name;
