insert into zeroCare_operational.groups (group_name, country_code, timezone)
values ('Bazekol Sağlık Grubu', 'TR', 'Europe/Istanbul')
on conflict do nothing;

insert into zeroCare_operational.facilities
  (group_id, facility_code, facility_name, facility_type, city, district, bed_count, gross_area_m2, grid_connection_type, notes)
select group_id, 'CIGLI_HOSP', 'Bazekol Çiğli Hastanesi', 'hospital', 'İzmir', 'Çiğli', 250, 34000, 'distribution', 'Ana hastane varsayımsal başlangıç'
from zeroCare_operational.groups
where group_name = 'Bazekol Sağlık Grubu'
on conflict do nothing;

insert into zeroCare_operational.facilities
  (group_id, facility_code, facility_name, facility_type, city, district, bed_count, gross_area_m2, grid_connection_type, notes)
select group_id, 'SADA_HOSP', 'Bazekol Sada Hastanesi', 'hospital', 'İzmir', 'Bornova', 120, 18000, 'distribution', 'Varsayımsal başlangıç'
from zeroCare_operational.groups
where group_name = 'Bazekol Sağlık Grubu'
on conflict do nothing;

insert into zeroCare_operational.facilities
  (group_id, facility_code, facility_name, facility_type, city, district, bed_count, gross_area_m2, grid_connection_type, notes)
select group_id, 'EYE_CENTER', 'Bazekol Göz Tıp Merkezi', 'eye_center', 'İzmir', 'Bornova', null, 4500, 'distribution', 'Varsayımsal başlangıç'
from zeroCare_operational.groups
where group_name = 'Bazekol Sağlık Grubu'
on conflict do nothing;

insert into zeroCare_operational.facilities
  (group_id, facility_code, facility_name, facility_type, city, district, bed_count, gross_area_m2, grid_connection_type, notes)
select group_id, 'CIGLI_MED', 'Bazekol Çiğli Tıp Merkezi', 'medical_center', 'İzmir', 'Çiğli', null, 3500, 'distribution', 'Varsayımsal başlangıç'
from zeroCare_operational.groups
where group_name = 'Bazekol Sağlık Grubu'
on conflict do nothing;

insert into zeroCare_operational.facilities
  (group_id, facility_code, facility_name, facility_type, city, district, bed_count, gross_area_m2, grid_connection_type, notes)
select group_id, 'DENTAL_CENTER', 'Bazekol Ağız ve Diş Sağlığı Merkezi', 'dental_center', 'İzmir', 'Çiğli', null, 3200, 'distribution', 'Varsayımsal başlangıç'
from zeroCare_operational.groups
where group_name = 'Bazekol Sağlık Grubu'
on conflict do nothing;

insert into zeroCare_operational.facilities
  (group_id, facility_code, facility_name, facility_type, city, district, bed_count, gross_area_m2, grid_connection_type, notes)
select group_id, 'BALCOVA_MED', 'Bazekol Balçova Tıp Merkezi', 'medical_center', 'İzmir', 'Balçova', null, 3800, 'distribution', 'Varsayımsal başlangıç'
from zeroCare_operational.groups
where group_name = 'Bazekol Sağlık Grubu'
on conflict do nothing;

insert into zeroCare_operational.departments
  (facility_id, department_code, department_name_tr, is_clinical)
select facility_id, 'ONCO', 'Onkoloji', true
from zeroCare_operational.facilities
where facility_code = 'CIGLI_HOSP'
on conflict do nothing;

insert into zeroCare_operational.departments
  (facility_id, department_code, department_name_tr, is_clinical)
select facility_id, 'CARDIO', 'Kalp Damar', true
from zeroCare_operational.facilities
where facility_code = 'CIGLI_HOSP'
on conflict do nothing;

insert into zeroCare_operational.departments
  (facility_id, department_code, department_name_tr, is_clinical)
select facility_id, 'ORTHO', 'Ortopedi', true
from zeroCare_operational.facilities
where facility_code = 'CIGLI_HOSP'
on conflict do nothing;

insert into zeroCare_operational.departments
  (facility_id, department_code, department_name_tr, is_clinical)
select facility_id, 'SURG', 'Genel Cerrahi', true
from zeroCare_operational.facilities
where facility_code = 'CIGLI_HOSP'
on conflict do nothing;

insert into zeroCare_operational.meters
  (facility_id, meter_code, meter_type, reading_granularity, unit_code, is_submeter)
select facility_id, 'EL_MAIN', 'electricity', 'hourly', 'kWh', false
from zeroCare_operational.facilities
on conflict do nothing;

insert into zeroCare_operational.meters
  (facility_id, meter_code, meter_type, reading_granularity, unit_code, is_submeter)
select facility_id, 'W_MAIN', 'water', 'daily', 'm3', false
from zeroCare_operational.facilities
on conflict do nothing;

insert into zeroCare_operational.meters
  (facility_id, meter_code, meter_type, reading_granularity, unit_code, is_submeter)
select facility_id, 'MW_SCALE', 'medical_waste_scale', 'daily', 'kg', false
from zeroCare_operational.facilities
on conflict do nothing;

insert into zeroCare_operational.meters
  (facility_id, meter_code, meter_type, reading_granularity, unit_code, is_submeter)
select facility_id, 'NG_MAIN', 'natural_gas', 'daily', 'm3', false
from zeroCare_operational.facilities
where facility_type = 'hospital'
on conflict do nothing;

insert into zeroCare_operational.municipality_contracts
  (facility_id, municipality_name, contract_no, signed_date, start_date, end_date, status, contract_storage_path)
select facility_id, 'İzmir Büyükşehir Belediyesi', 'UNSPECIFIED', '2026-01-05', '2026-01-05', '2026-12-31', 'active',
       'contracts/izmir/' || lower(facility_code) || '_2026.pdf'
from zeroCare_operational.facilities
on conflict do nothing;

insert into zeroCare_operational.municipality_tariffs
  (municipality_name, year, waste_stream_code, price_per_kg_try, vat_included, source_url, effective_from, effective_to)
values
  ('İzmir Büyükşehir Belediyesi', 2026, 'MEDICAL_MIXED', 30, false, 'https://www.izmir.bel.tr/tr/TibbiAtiklar/292/95', '2026-01-01', '2026-12-31'),
  ('İzmir Büyükşehir Belediyesi', 2026, 'PATHOLOGICAL', 81, false, 'https://www.izmir.bel.tr/tr/TibbiAtiklar/292/95', '2026-01-01', '2026-12-31')
on conflict do nothing;

insert into zeroCare_operational.daily_metrics
  (facility_id, metric_date, metric_code, value, unit_code, quality_flag, calculation_method, source_system)
select facility_id, '2026-03-01', 'electricity_kwh', 42000, 'kWh', 'estimated', 'mock_seed', 'mock'
from zeroCare_operational.facilities
where facility_code = 'CIGLI_HOSP'
on conflict do nothing;

insert into zeroCare_operational.daily_metrics
  (facility_id, metric_date, metric_code, value, unit_code, quality_flag, calculation_method, source_system)
select facility_id, '2026-03-01', 'water_m3', 380, 'm3', 'estimated', 'mock_seed', 'mock'
from zeroCare_operational.facilities
where facility_code = 'CIGLI_HOSP'
on conflict do nothing;

insert into zeroCare_operational.daily_metrics
  (facility_id, metric_date, metric_code, value, unit_code, quality_flag, calculation_method, source_system)
select facility_id, '2026-03-01', 'medical_waste_kg', 820, 'kg', 'estimated', 'mock_seed', 'mock'
from zeroCare_operational.facilities
where facility_code = 'CIGLI_HOSP'
on conflict do nothing;

insert into zeroCare_operational.daily_metrics
  (facility_id, metric_date, metric_code, value, unit_code, quality_flag, calculation_method, source_system)
select facility_id, '2026-03-01', 'pathological_waste_kg', 45, 'kg', 'estimated', 'mock_seed', 'mock'
from zeroCare_operational.facilities
where facility_code = 'CIGLI_HOSP'
on conflict do nothing;

insert into zeroCare_operational.waste_pickups
  (facility_id, pickup_ts, waste_stream_code, weight_kg, treatment, document_type, document_no, document_storage_path, retention_until)
select facility_id, '2026-03-01 10:30:00+03', 'MEDICAL_MIXED', 820, 'sterilization', 'UATF',
       'UATF-20260301-0001', 'waste_docs/cigli/uattf_20260301_0001.pdf', '2029-03-01'
from zeroCare_operational.facilities
where facility_code = 'CIGLI_HOSP'
on conflict do nothing;

insert into zeroCare_operational.waste_pickups
  (facility_id, pickup_ts, waste_stream_code, weight_kg, treatment, document_type, document_no, document_storage_path, retention_until)
select facility_id, '2026-03-01 11:10:00+03', 'PATHOLOGICAL', 45, 'incineration', 'UATF',
       'UATF-20260301-0002', 'waste_docs/cigli/uattf_20260301_0002.pdf', '2029-03-01'
from zeroCare_operational.facilities
where facility_code = 'CIGLI_HOSP'
on conflict do nothing;
