create extension if not exists "pgcrypto";

create schema if not exists zeroCare_operational;

create table if not exists zeroCare_operational.groups (
  group_id uuid primary key default gen_random_uuid(),
  group_name text not null,
  country_code text not null default 'TR',
  timezone text not null default 'Europe/Istanbul',
  created_at timestamptz not null default now()
);

create table if not exists zeroCare_operational.facilities (
  facility_id uuid primary key default gen_random_uuid(),
  group_id uuid not null references zeroCare_operational.groups(group_id) on delete cascade,
  facility_code text not null,
  facility_name text not null,
  facility_type text not null,
  city text not null,
  district text,
  address text,
  latitude numeric,
  longitude numeric,
  opened_year int,
  bed_count int,
  gross_area_m2 numeric,
  operating_hours_per_day int not null default 24,
  owner_operator text,
  grid_connection_type text,
  notes text,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (group_id, facility_code)
);

create table if not exists zeroCare_operational.departments (
  department_id uuid primary key default gen_random_uuid(),
  facility_id uuid not null references zeroCare_operational.facilities(facility_id) on delete cascade,
  department_code text not null,
  department_name_tr text not null,
  is_clinical boolean not null default true,
  floor text,
  notes text,
  created_at timestamptz not null default now(),
  unique (facility_id, department_code)
);

create table if not exists zeroCare_operational.meters (
  meter_id uuid primary key default gen_random_uuid(),
  facility_id uuid not null references zeroCare_operational.facilities(facility_id) on delete cascade,
  department_id uuid references zeroCare_operational.departments(department_id) on delete set null,
  meter_code text not null,
  meter_type text not null,
  reading_granularity text not null,
  unit_code text not null,
  is_submeter boolean not null default false,
  manufacturer text,
  model text,
  serial_no text,
  installed_at date,
  retired_at date,
  created_at timestamptz not null default now(),
  unique (facility_id, meter_code)
);

create table if not exists zeroCare_operational.meter_readings (
  reading_id uuid primary key default gen_random_uuid(),
  meter_id uuid not null references zeroCare_operational.meters(meter_id) on delete cascade,
  ts timestamptz not null,
  value numeric not null,
  unit_code text not null,
  quality_flag text not null default 'measured',
  source_system text,
  ingestion_batch_id uuid,
  ingested_at timestamptz not null default now(),
  notes text,
  unique (meter_id, ts)
);

create table if not exists zeroCare_operational.daily_metrics (
  metric_id uuid primary key default gen_random_uuid(),
  facility_id uuid not null references zeroCare_operational.facilities(facility_id) on delete cascade,
  department_id uuid references zeroCare_operational.departments(department_id) on delete set null,
  metric_date date not null,
  metric_code text not null,
  value numeric not null,
  unit_code text not null,
  quality_flag text not null default 'derived',
  calculation_method text,
  source_system text,
  created_at timestamptz not null default now(),
  unique (facility_id, department_id, metric_date, metric_code)
);

create table if not exists zeroCare_operational.waste_pickups (
  pickup_id uuid primary key default gen_random_uuid(),
  facility_id uuid not null references zeroCare_operational.facilities(facility_id) on delete cascade,
  pickup_ts timestamptz not null,
  waste_stream_code text not null,
  weight_kg numeric not null,
  treatment text,
  carrier_name text,
  vehicle_plate text,
  carrier_license_no text,
  document_type text not null,
  document_no text,
  document_storage_path text,
  retention_until date,
  fee_tariff_id uuid,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists zeroCare_operational.municipality_contracts (
  contract_id uuid primary key default gen_random_uuid(),
  facility_id uuid not null references zeroCare_operational.facilities(facility_id) on delete cascade,
  municipality_name text not null,
  contract_no text,
  signed_date date,
  start_date date not null,
  end_date date,
  status text not null default 'active',
  contact_phone text,
  contact_email text,
  contract_storage_path text,
  notes text,
  created_at timestamptz not null default now(),
  unique (facility_id, municipality_name, start_date)
);

create table if not exists zeroCare_operational.municipality_tariffs (
  tariff_id uuid primary key default gen_random_uuid(),
  municipality_name text not null,
  year int not null,
  waste_stream_code text not null,
  price_per_kg_try numeric not null,
  vat_included boolean not null default false,
  source_url text,
  effective_from date not null,
  effective_to date,
  created_at timestamptz not null default now(),
  unique (municipality_name, year, waste_stream_code)
);

create table if not exists zeroCare_operational.alerts (
  alert_id uuid primary key default gen_random_uuid(),
  facility_id uuid not null references zeroCare_operational.facilities(facility_id) on delete cascade,
  department_id uuid references zeroCare_operational.departments(department_id) on delete set null,
  alert_ts timestamptz not null default now(),
  alert_type text not null,
  severity text not null,
  title_tr text not null,
  details_tr text,
  related_table text,
  related_id uuid,
  status text not null default 'open',
  created_at timestamptz not null default now()
);

create table if not exists zeroCare_operational.risk_scores_daily (
  risk_id uuid primary key default gen_random_uuid(),
  facility_id uuid not null references zeroCare_operational.facilities(facility_id) on delete cascade,
  metric_date date not null,
  risk_score numeric not null,
  risk_breakdown jsonb not null,
  created_at timestamptz not null default now(),
  unique (facility_id, metric_date)
);

create table if not exists zeroCare_operational.esrs_monthly (
  esrs_id uuid primary key default gen_random_uuid(),
  facility_id uuid references zeroCare_operational.facilities(facility_id) on delete cascade,
  year int not null,
  month int not null check (month between 1 and 12),
  esrs_payload jsonb not null,
  generated_at timestamptz not null default now(),
  version_tag text not null default 'v1',
  unique (facility_id, year, month, version_tag)
);

create index if not exists idx_facilities_group
  on zeroCare_operational.facilities (group_id, facility_code);

create index if not exists idx_meter_readings_meter_ts
  on zeroCare_operational.meter_readings (meter_id, ts desc);

create index if not exists idx_daily_metrics_facility_date
  on zeroCare_operational.daily_metrics (facility_id, metric_date desc);

create index if not exists idx_waste_pickups_facility_ts
  on zeroCare_operational.waste_pickups (facility_id, pickup_ts desc);

create index if not exists idx_alerts_facility_status
  on zeroCare_operational.alerts (facility_id, status, alert_ts desc);
