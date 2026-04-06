begin;

create schema if not exists zerocare_operational;

create table if not exists zerocare_operational.staging_daily_metrics (
    staging_id bigint generated always as identity primary key,

    batch_id text not null,
    source text not null,
    source_system text not null,
    source_ref text,
    ingested_at timestamptz not null default now(),
    ingested_by text not null default 'system',

    facility_code text not null,
    metric_date date not null,
    metric_code text not null,

    raw_value text,
    raw_unit text,
    raw_payload jsonb,

    metric_value numeric(18,6) not null,
    metric_unit text not null,
    normalized_value numeric(18,6) not null,
    normalized_unit text not null,
    conversion_rule text not null default 'identity',
    metric_profile_version text,
    facility_profile_version text,

    validation_status text not null default 'PENDING',
    validation_errors jsonb not null default '[]'::jsonb,
    validation_warnings jsonb not null default '[]'::jsonb,
    is_required_metric boolean not null default true,
    is_promotable boolean not null default false,
    validated_at timestamptz,
    validated_by text,

    payload_hash text,
    fingerprint text not null,
    record_version integer not null default 1,
    supersedes_staging_id bigint references zerocare_operational.staging_daily_metrics(staging_id),
    is_active boolean not null default true,

    promote_status text not null default 'NOT_PROMOTED',
    promoted_at timestamptz,
    promote_run_id text,

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint chk_staging_daily_metrics_source
        check (source in ('synthetic', 'live', 'recovered', 'manual')),

    constraint chk_staging_daily_metrics_validation_status
        check (validation_status in ('PENDING', 'VALID', 'INVALID', 'WARN')),

    constraint chk_staging_daily_metrics_promote_status
        check (promote_status in ('NOT_PROMOTED', 'PROMOTED', 'SKIPPED', 'REJECTED')),

    constraint uq_staging_daily_metrics_fingerprint
        unique (fingerprint)
);

create unique index if not exists uq_staging_daily_metrics_active_business_key
    on zerocare_operational.staging_daily_metrics (facility_code, metric_date, metric_code)
    where is_active = true;

create index if not exists idx_staging_daily_metrics_batch_id
    on zerocare_operational.staging_daily_metrics (batch_id);

create index if not exists idx_staging_daily_metrics_facility_date_metric_active
    on zerocare_operational.staging_daily_metrics (facility_code, metric_date, metric_code, is_active);

create index if not exists idx_staging_daily_metrics_promote_queue
    on zerocare_operational.staging_daily_metrics (metric_date, facility_code, validation_status, is_promotable)
    where is_active = true;

create index if not exists idx_staging_daily_metrics_source_ingested_at
    on zerocare_operational.staging_daily_metrics (source, ingested_at desc);

create index if not exists idx_staging_daily_metrics_promote_status
    on zerocare_operational.staging_daily_metrics (promote_status, metric_date);

create index if not exists idx_staging_daily_metrics_raw_payload_gin
    on zerocare_operational.staging_daily_metrics
    using gin (raw_payload);

create or replace function zerocare_operational.set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists trg_set_updated_at on zerocare_operational.staging_daily_metrics;

create trigger trg_set_updated_at
before update on zerocare_operational.staging_daily_metrics
for each row
execute function zerocare_operational.set_updated_at();

create or replace view zerocare_operational.v_staging_daily_metrics_status as
select
    facility_code,
    metric_date,
    count(*) filter (where is_active = true) as total_metrics,
    count(*) filter (where is_active = true and validation_status = 'VALID') as valid_metrics,
    count(*) filter (where is_active = true and metric_code = 'electricity_kwh') as electricity_kwh,
    count(*) filter (where is_active = true and metric_code = 'water_m3') as water_m3,
    count(*) filter (where is_active = true and metric_code = 'medical_waste_kg') as medical_waste_kg,
    count(*) filter (where is_active = true and metric_code = 'pathological_waste_kg') as pathological_waste_kg,
    count(*) filter (where is_active = true and metric_code = 'general_waste_kg') as general_waste_kg,
    count(*) filter (where is_active = true and metric_code = 'scope2_location_tco2e') as scope2_location_tco2e,
    count(*) filter (where is_active = true and metric_code = 'waste_cost_try') as waste_cost_try,
    case
        when count(*) filter (
            where is_active = true
              and validation_status = 'VALID'
              and metric_code in (
                  'electricity_kwh',
                  'water_m3',
                  'medical_waste_kg',
                  'pathological_waste_kg',
                  'general_waste_kg',
                  'scope2_location_tco2e',
                  'waste_cost_try'
              )
        ) = 7 then 'READY'
        when count(*) filter (where is_active = true) = 0 then 'NO_DATA'
        else 'PARTIAL'
    end as status
from zerocare_operational.staging_daily_metrics
group by facility_code, metric_date;

commit;
