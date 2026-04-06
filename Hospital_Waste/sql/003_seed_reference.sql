insert into zeroCare_reference.ref_units (unit_code, unit_name_tr, dimension, to_si_multiplier, si_unit_code)
values
  ('kWh', 'Kilovat-saat', 'energy', 3600000, 'J'),
  ('MWh', 'Megavat-saat', 'energy', 3600000000, 'J'),
  ('m3', 'Metreküp', 'volume', 1, 'm3'),
  ('kg', 'Kilogram', 'mass', 1, 'kg'),
  ('tCO2e', 'Ton CO2e', 'emissions', 1000, 'kgCO2e'),
  ('tCO2e/MWh', 'Ton CO2e / MWh', 'emission_factor', null, null),
  ('kgCO2/TJ', 'kg CO2 / TJ', 'emission_factor', null, null),
  ('kgCO2e/kg', 'kg CO2e / kg', 'emission_factor', null, null),
  ('TRY', 'Türk Lirası', 'currency', 1, 'TRY')
on conflict (unit_code) do nothing;

insert into zeroCare_reference.ref_sources
  (source_name, publisher, publication_date, url, jurisdiction, notes)
values
  ('Türkiye Ulusal Elektrik Şebekesi Emisyon Faktörü 2023', 'T.C. Enerji ve Tabii Kaynaklar Bakanlığı', '2025-12-26', 'https://enerji.gov.tr', 'TR', 'Tüketim noktası emisyon faktörleri'),
  ('Tıbbi Atıkların Kontrolü Yönetmeliği', 'Türkiye', '2017-01-25', 'https://www.resmigazete.gov.tr', 'TR', '48 saat kuralı, UATF, alındı belgesi'),
  ('İzmir Büyükşehir Belediyesi Tıbbi Atık Tarifesi 2026', 'İzmir Büyükşehir Belediyesi', '2026-01-01', 'https://www.izmir.bel.tr/tr/TibbiAtiklar/292/95', 'TR-IZMIR', '30 TL/kg tıbbi atık, 81 TL/kg patolojik'),
  ('WHO Health-care Waste', 'WHO', null, 'https://www.who.int/news-room/fact-sheets/detail/health-care-waste', 'GLOBAL', '%85 genel, %15 tehlikeli'),
  ('ESRS E1 Climate Change', 'EFRAG / EU', null, 'https://www.efrag.org', 'EU', 'Enerji ve emisyon veri noktaları'),
  ('ESRS E5 Resource Use and Circular Economy', 'EFRAG / EU', null, 'https://www.efrag.org', 'EU', 'Atık veri noktaları'),
  ('IPCC 2006 Stationary Combustion', 'IPCC', null, 'https://www.ipcc-nggip.iges.or.jp', 'GLOBAL', 'Yakıt varsayılan CO2 faktörleri'),
  ('GHG Protocol AR6 GWP100', 'GHG Protocol', '2024-08-01', 'https://ghgprotocol.org', 'GLOBAL', 'GWP100 değerleri'),
  ('E5P/EBRD Hospital Energy Benchmarks', 'E5P/EBRD', null, 'https://e5p.eu/public/upload/media/Healthcare.pdf', 'GLOBAL', 'Hastane enerji benchmarkları')
on conflict do nothing;

insert into zeroCare_reference.ref_gwp_sets
  (gwp_set_name, time_horizon_years, source_id, valid_from)
select 'GHG Protocol AR6 GWP100', 100, source_id, '2024-08-01'
from zeroCare_reference.ref_sources
where source_name = 'GHG Protocol AR6 GWP100'
on conflict do nothing;

insert into zeroCare_reference.ref_gwp_values
  (gwp_set_id, gas_code, gas_name, gwp100, unit_code)
select gwp_set_id, 'N2O', 'Nitrous Oxide', 273, 'kgCO2e/kg'
from zeroCare_reference.ref_gwp_sets
where gwp_set_name = 'GHG Protocol AR6 GWP100'
on conflict do nothing;

insert into zeroCare_reference.ref_gwp_values
  (gwp_set_id, gas_code, gas_name, gwp100, unit_code)
select gwp_set_id, 'SEVOFLURANE', 'Sevoflurane', 130, 'kgCO2e/kg'
from zeroCare_reference.ref_gwp_sets
where gwp_set_name = 'GHG Protocol AR6 GWP100'
on conflict do nothing;

insert into zeroCare_reference.ref_gwp_values
  (gwp_set_id, gas_code, gas_name, gwp100, unit_code)
select gwp_set_id, 'ISOFLURANE', 'Isoflurane', 510, 'kgCO2e/kg'
from zeroCare_reference.ref_gwp_sets
where gwp_set_name = 'GHG Protocol AR6 GWP100'
on conflict do nothing;

insert into zeroCare_reference.ref_gwp_values
  (gwp_set_id, gas_code, gas_name, gwp100, unit_code)
select gwp_set_id, 'DESFLURANE', 'Desflurane', 2540, 'kgCO2e/kg'
from zeroCare_reference.ref_gwp_sets
where gwp_set_name = 'GHG Protocol AR6 GWP100'
on conflict do nothing;

insert into zeroCare_reference.ref_emission_factors
  (activity_type, activity_subtype, geography, year, factor_value, factor_unit, scope_hint, source_id, methodology, valid_from, version_tag)
select 'electricity', 'grid_consumption_distribution', 'TR', 2023, 0.469, 'tCO2e/MWh', 'scope2_location', source_id, 'Ulusal tüketim noktası EF', '2023-01-01', 'tr_grid_2023_v1'
from zeroCare_reference.ref_sources
where source_name = 'Türkiye Ulusal Elektrik Şebekesi Emisyon Faktörü 2023'
on conflict do nothing;

insert into zeroCare_reference.ref_emission_factors
  (activity_type, activity_subtype, geography, year, factor_value, factor_unit, scope_hint, source_id, methodology, valid_from, version_tag)
select 'electricity', 'grid_consumption_transmission', 'TR', 2023, 0.436, 'tCO2e/MWh', 'scope2_location', source_id, 'Ulusal tüketim noktası EF', '2023-01-01', 'tr_grid_2023_v1'
from zeroCare_reference.ref_sources
where source_name = 'Türkiye Ulusal Elektrik Şebekesi Emisyon Faktörü 2023'
on conflict do nothing;

insert into zeroCare_reference.ref_emission_factors
  (activity_type, activity_subtype, geography, year, factor_value, factor_unit, scope_hint, source_id, methodology, valid_from, version_tag)
select 'fuel', 'natural_gas', 'GLOBAL', 2006, 56100, 'kgCO2/TJ', 'scope1', source_id, 'IPCC default', '2006-01-01', 'ipcc_2006_v1'
from zeroCare_reference.ref_sources
where source_name = 'IPCC 2006 Stationary Combustion'
on conflict do nothing;

insert into zeroCare_reference.ref_emission_factors
  (activity_type, activity_subtype, geography, year, factor_value, factor_unit, scope_hint, source_id, methodology, valid_from, version_tag)
select 'fuel', 'diesel', 'GLOBAL', 2006, 74100, 'kgCO2/TJ', 'scope1', source_id, 'IPCC default', '2006-01-01', 'ipcc_2006_v1'
from zeroCare_reference.ref_sources
where source_name = 'IPCC 2006 Stationary Combustion'
on conflict do nothing;

insert into zeroCare_reference.ref_emission_factors
  (activity_type, activity_subtype, geography, year, factor_value, factor_unit, scope_hint, source_id, methodology, valid_from, version_tag)
select 'fuel', 'lpg', 'GLOBAL', 2006, 63100, 'kgCO2/TJ', 'scope1', source_id, 'IPCC default', '2006-01-01', 'ipcc_2006_v1'
from zeroCare_reference.ref_sources
where source_name = 'IPCC 2006 Stationary Combustion'
on conflict do nothing;

insert into zeroCare_reference.ref_waste_streams
  (stream_code, stream_name_tr, hazard_class, treatment_default, legal_notes, source_id)
select 'MEDICAL_MIXED', 'Tıbbi Atık', 'hazardous', 'sterilization', 'İzmir belediye tarifesi ana kalem', source_id
from zeroCare_reference.ref_sources
where source_name = 'İzmir Büyükşehir Belediyesi Tıbbi Atık Tarifesi 2026'
on conflict do nothing;

insert into zeroCare_reference.ref_waste_streams
  (stream_code, stream_name_tr, hazard_class, treatment_default, legal_notes, source_id)
select 'PATHOLOGICAL', 'Patolojik Atık', 'hazardous', 'incineration', 'Yakma esaslı', source_id
from zeroCare_reference.ref_sources
where source_name = 'İzmir Büyükşehir Belediyesi Tıbbi Atık Tarifesi 2026'
on conflict do nothing;

insert into zeroCare_reference.ref_waste_streams
  (stream_code, stream_name_tr, hazard_class, treatment_default, legal_notes, source_id)
select 'SHARPS', 'Kesici Delici Atık', 'hazardous', 'sterilization', 'Kesici-delici sağlık atığı', source_id
from zeroCare_reference.ref_sources
where source_name = 'Tıbbi Atıkların Kontrolü Yönetmeliği'
on conflict do nothing;

insert into zeroCare_reference.ref_waste_streams
  (stream_code, stream_name_tr, hazard_class, treatment_default, legal_notes, source_id)
select 'GENERAL', 'Genel Atık', 'non_hazardous', 'landfill', 'WHO tehlikesiz atık grubu', source_id
from zeroCare_reference.ref_sources
where source_name = 'WHO Health-care Waste'
on conflict do nothing;

insert into zeroCare_reference.ref_legal_requirements
  (jurisdiction, regulation_name, clause_ref, requirement_type, requirement_text_tr, numeric_limit, limit_unit, source_id, effective_from)
select 'TR', 'Tıbbi Atıkların Kontrolü Yönetmeliği', 'Bekletme Süresi', 'storage_time',
       'Tıbbi atıklar sağlık kuruluşunda 48 saatten fazla bekletilemez.',
       48, 'hour', source_id, '2017-01-25'
from zeroCare_reference.ref_sources
where source_name = 'Tıbbi Atıkların Kontrolü Yönetmeliği'
on conflict do nothing;

insert into zeroCare_reference.ref_legal_requirements
  (jurisdiction, regulation_name, clause_ref, requirement_type, requirement_text_tr, numeric_limit, limit_unit, source_id, effective_from)
select 'TR', 'Tıbbi Atıkların Kontrolü Yönetmeliği', '+4C İstisnası', 'cold_storage_time',
       '+4°C koşulunda bekletme süresi 1 haftaya kadar uzatılabilir.',
       168, 'hour', source_id, '2017-01-25'
from zeroCare_reference.ref_sources
where source_name = 'Tıbbi Atıkların Kontrolü Yönetmeliği'
on conflict do nothing;

insert into zeroCare_reference.ref_legal_requirements
  (jurisdiction, regulation_name, clause_ref, requirement_type, requirement_text_tr, numeric_limit, limit_unit, source_id, effective_from)
select 'TR', 'Tıbbi Atıkların Kontrolü Yönetmeliği', 'Belge Saklama', 'document_retention',
       'Alındı belgesi / makbuz en az 3 yıl saklanmalıdır.',
       3, 'year', source_id, '2017-01-25'
from zeroCare_reference.ref_sources
where source_name = 'Tıbbi Atıkların Kontrolü Yönetmeliği'
on conflict do nothing;

insert into zeroCare_reference.ref_benchmarks
  (sector, metric_code, metric_name_tr, value_min, value_max, unit_code, geography, notes, source_id)
select 'hospital', 'energy_total_kwh_m2_year', 'Toplam enerji yoğunluğu', 139, 690, 'kWh', 'GLOBAL',
       'kWh/m2-yıl olarak yorumlanır', source_id
from zeroCare_reference.ref_sources
where source_name = 'E5P/EBRD Hospital Energy Benchmarks'
on conflict do nothing;

insert into zeroCare_reference.ref_benchmarks
  (sector, metric_code, metric_name_tr, value_min, value_max, unit_code, geography, notes, source_id)
select 'hospital', 'hazardous_waste_kg_bed_day', 'Tehlikeli sağlık atığı yoğunluğu', 0.2, 0.5, 'kg', 'GLOBAL',
       'kg/yatak/gün', source_id
from zeroCare_reference.ref_sources
where source_name = 'WHO Health-care Waste'
on conflict do nothing;

insert into zeroCare_reference.ref_esrs_metric_map
  (esrs_standard, disclosure_req, metric_code, metric_description_tr, unit_code, required_boolean, source_id)
select 'E1', 'E1-5', 'energy_total_mwh', 'Toplam enerji tüketimi', 'MWh', true, source_id
from zeroCare_reference.ref_sources
where source_name = 'ESRS E1 Climate Change'
on conflict do nothing;

insert into zeroCare_reference.ref_esrs_metric_map
  (esrs_standard, disclosure_req, metric_code, metric_description_tr, unit_code, required_boolean, source_id)
select 'E1', 'E1-6', 'scope1_tco2e', 'Scope 1 emisyonları', 'tCO2e', true, source_id
from zeroCare_reference.ref_sources
where source_name = 'ESRS E1 Climate Change'
on conflict do nothing;

insert into zeroCare_reference.ref_esrs_metric_map
  (esrs_standard, disclosure_req, metric_code, metric_description_tr, unit_code, required_boolean, source_id)
select 'E1', 'E1-6', 'scope2_location_tco2e', 'Scope 2 location-based emisyonları', 'tCO2e', true, source_id
from zeroCare_reference.ref_sources
where source_name = 'ESRS E1 Climate Change'
on conflict do nothing;

insert into zeroCare_reference.ref_esrs_metric_map
  (esrs_standard, disclosure_req, metric_code, metric_description_tr, unit_code, required_boolean, source_id)
select 'E5', 'E5-5', 'waste_total_kg', 'Toplam atık', 'kg', true, source_id
from zeroCare_reference.ref_sources
where source_name = 'ESRS E5 Resource Use and Circular Economy'
on conflict do nothing;

insert into zeroCare_reference.ref_esrs_metric_map
  (esrs_standard, disclosure_req, metric_code, metric_description_tr, unit_code, required_boolean, source_id)
select 'E5', 'E5-5', 'waste_hazardous_kg', 'Tehlikeli atık', 'kg', true, source_id
from zeroCare_reference.ref_sources
where source_name = 'ESRS E5 Resource Use and Circular Economy'
on conflict do nothing;
