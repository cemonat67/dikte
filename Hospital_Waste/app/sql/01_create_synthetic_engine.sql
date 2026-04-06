create table if not exists public.synthetic_metric_readings_staging (
    batch_id text not null,
    facility_code text not null,
    facility_name text not null,
    metric_date date not null,
    metric_code text not null,
    metric_value numeric(18,4) not null,
    unit text not null,
    anomaly_flag boolean not null default false,
    anomaly_type text null,
    generator_version text not null default 'synthetic-hospital-v1',
    created_at timestamptz not null default now(),
    primary key (batch_id, facility_code, metric_date, metric_code)
);

create table if not exists public.synthetic_validation_results (
    id bigserial primary key,
    batch_id text not null,
    facility_code text not null,
    metric_date date not null,
    metric_code text not null,
    status text not null check (status in ('accepted','warning','rejected')),
    check_name text not null,
    severity text not null check (severity in ('info','warning','critical')),
    message text not null,
    observed_value numeric(18,4),
    reference_value numeric(18,4),
    created_at timestamptz not null default now()
);

create index if not exists idx_synth_stage_facility_date
on public.synthetic_metric_readings_staging (facility_code, metric_date);

create index if not exists idx_synth_val_batch_status
on public.synthetic_validation_results (batch_id, status);
