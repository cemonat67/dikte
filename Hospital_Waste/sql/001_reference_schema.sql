create extension if not exists "pgcrypto";

create schema if not exists zeroCare_reference;

create table if not exists zeroCare_reference.ref_sources (
  source_id uuid primary key default gen_random_uuid(),
  source_name text not null,
  publisher text,
  publication_date date,
  url text,
  jurisdiction text,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists zeroCare_reference.ref_units (
  unit_code text primary key,
  unit_name_tr text not null,
  dimension text not null,
  to_si_multiplier numeric,
  si_unit_code text,
  created_at timestamptz not null default now()
);

create table if not exists zeroCare_reference.ref_gwp_sets (
  gwp_set_id uuid primary key default gen_random_uuid(),
  gwp_set_name text not null,
  time_horizon_years int not null,
  source_id uuid references zeroCare_reference.ref_sources(source_id),
  valid_from date not null,
  valid_to date,
  created_at timestamptz not null default now()
);

create table if not exists zeroCare_reference.ref_gwp_values (
  gwp_value_id uuid primary key default gen_random_uuid(),
  gwp_set_id uuid not null references zeroCare_reference.ref_gwp_sets(gwp_set_id) on delete cascade,
  gas_code text not null,
  gas_name text,
  gwp100 numeric not null,
  unit_code text not null,
  created_at timestamptz not null default now(),
  unique (gwp_set_id, gas_code)
);

create table if not exists zeroCare_reference.ref_emission_factors (
  ef_id uuid primary key default gen_random_uuid(),
  activity_type text not null,
  activity_subtype text,
  geography text,
  year int,
  factor_value numeric not null,
  factor_unit text not null,
  scope_hint text,
  source_id uuid references zeroCare_reference.ref_sources(source_id),
  methodology text,
  valid_from date not null,
  valid_to date,
  version_tag text not null default 'v1',
  created_at timestamptz not null default now(),
  unique (activity_type, activity_subtype, geography, year, version_tag, valid_from)
);

create table if not exists zeroCare_reference.ref_legal_requirements (
  req_id uuid primary key default gen_random_uuid(),
  jurisdiction text not null,
  regulation_name text not null,
  clause_ref text,
  requirement_type text not null,
  requirement_text_tr text not null,
  numeric_limit numeric,
  limit_unit text,
  source_id uuid references zeroCare_reference.ref_sources(source_id),
  effective_from date,
  effective_to date,
  created_at timestamptz not null default now()
);

create table if not exists zeroCare_reference.ref_benchmarks (
  benchmark_id uuid primary key default gen_random_uuid(),
  sector text not null,
  metric_code text not null,
  metric_name_tr text not null,
  value_min numeric,
  value_max numeric,
  unit_code text not null,
  geography text,
  notes text,
  source_id uuid references zeroCare_reference.ref_sources(source_id),
  created_at timestamptz not null default now()
);

create table if not exists zeroCare_reference.ref_waste_streams (
  waste_stream_id uuid primary key default gen_random_uuid(),
  stream_code text not null unique,
  stream_name_tr text not null,
  hazard_class text not null,
  treatment_default text,
  legal_notes text,
  source_id uuid references zeroCare_reference.ref_sources(source_id),
  created_at timestamptz not null default now()
);

create table if not exists zeroCare_reference.ref_esrs_metric_map (
  map_id uuid primary key default gen_random_uuid(),
  esrs_standard text not null,
  disclosure_req text not null,
  metric_code text not null,
  metric_description_tr text not null,
  unit_code text,
  required_boolean boolean not null default true,
  source_id uuid references zeroCare_reference.ref_sources(source_id),
  created_at timestamptz not null default now(),
  unique (esrs_standard, disclosure_req, metric_code)
);

create index if not exists idx_ref_emission_factors_lookup
  on zeroCare_reference.ref_emission_factors (activity_type, geography, year, valid_from desc);

create index if not exists idx_ref_legal_requirements_jurisdiction
  on zeroCare_reference.ref_legal_requirements (jurisdiction, requirement_type);

create index if not exists idx_ref_benchmarks_metric
  on zeroCare_reference.ref_benchmarks (sector, metric_code, geography);
