create extension if not exists pgcrypto;
create schema if not exists zerocare_sustainability;

create table if not exists zerocare_sustainability.standard_frameworks (
    framework_id uuid primary key default gen_random_uuid(),
    framework_code text not null unique,
    framework_name text not null,
    framework_version text,
    framework_family text not null,
    source_url text,
    scoring_mode text not null default 'alignment',
    is_active boolean not null default true,
    created_at timestamptz not null default now()
);

create table if not exists zerocare_sustainability.standard_domains (
    domain_id uuid primary key default gen_random_uuid(),
    framework_id uuid not null references zerocare_sustainability.standard_frameworks(framework_id) on delete cascade,
    domain_code text not null,
    domain_name text not null,
    domain_description text,
    weight_pct numeric(5,2) not null default 0,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    unique(framework_id, domain_code)
);

create table if not exists zerocare_sustainability.standard_indicators (
    indicator_id uuid primary key default gen_random_uuid(),
    framework_id uuid not null references zerocare_sustainability.standard_frameworks(framework_id) on delete cascade,
    domain_id uuid not null references zerocare_sustainability.standard_domains(domain_id) on delete cascade,
    indicator_code text not null,
    indicator_name text not null,
    indicator_description text,
    unit text,
    calculator_key text not null,
    source_metric_codes text[] not null default '{}',
    default_assessment_state text not null default 'not_assessed',
    weight_pct numeric(5,2) not null default 0,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    unique(framework_id, indicator_code)
);

create table if not exists zerocare_sustainability.indicator_thresholds (
    threshold_id uuid primary key default gen_random_uuid(),
    indicator_id uuid not null references zerocare_sustainability.standard_indicators(indicator_id) on delete cascade,
    effective_from date not null default current_date,
    effective_to date,
    rule_type text not null,
    comparator text not null,
    green_min numeric,
    green_max numeric,
    amber_min numeric,
    amber_max numeric,
    red_min numeric,
    red_max numeric,
    score_green numeric(5,2) not null default 100,
    score_amber numeric(5,2) not null default 70,
    score_red numeric(5,2) not null default 40,
    bootstrap_score numeric(5,2) not null default 70,
    notes text,
    created_at timestamptz not null default now()
);

create table if not exists zerocare_sustainability.facility_indicator_daily (
    facility_indicator_daily_id uuid primary key default gen_random_uuid(),
    metric_date date not null,
    facility_id uuid not null references zerocare_operational.facilities(facility_id) on delete cascade,
    indicator_id uuid not null references zerocare_sustainability.standard_indicators(indicator_id) on delete cascade,
    observed_value numeric,
    baseline_value numeric,
    delta_pct numeric,
    score numeric(5,2),
    status text not null,
    assessment_state text not null,
    unit text,
    source_metrics jsonb not null default '{}'::jsonb,
    scoring_detail jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique(metric_date, facility_id, indicator_id)
);

create table if not exists zerocare_sustainability.facility_standard_scores (
    facility_standard_score_id uuid primary key default gen_random_uuid(),
    metric_date date not null,
    facility_id uuid not null references zerocare_operational.facilities(facility_id) on delete cascade,
    framework_id uuid not null references zerocare_sustainability.standard_frameworks(framework_id) on delete cascade,
    domain_id uuid references zerocare_sustainability.standard_domains(domain_id) on delete cascade,
    score_level text not null,
    assessed_count integer not null default 0,
    not_assessed_count integer not null default 0,
    total_count integer not null default 0,
    score numeric(5,2),
    status text not null,
    score_detail jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique(metric_date, facility_id, framework_id, domain_id, score_level)
);

create index if not exists idx_sus_indicator_daily_facility_date
    on zerocare_sustainability.facility_indicator_daily(facility_id, metric_date);

create index if not exists idx_sus_scores_facility_date
    on zerocare_sustainability.facility_standard_scores(facility_id, metric_date);

create or replace view zerocare_sustainability.vw_daily_metrics_compat as
select
    dm.metric_date::date as metric_date,
    dm.facility_id,
    f.facility_code,
    lower(dm.metric_code) as metric_code,
    dm.metric_value::numeric as metric_value
from zerocare_operational.daily_metrics dm
join zerocare_operational.facilities f
  on f.facility_id = dm.facility_id;

insert into zerocare_sustainability.standard_frameworks (
    framework_code, framework_name, framework_version, framework_family, source_url, scoring_mode
)
values
    ('WHO_GREEN_HOSPITAL', 'WHO Climate-resilient and environmentally sustainable health care facilities', '2023/2025-aligned', 'WHO', 'https://www.who.int/', 'alignment'),
    ('NHS_GREEN_PLAN', 'NHS Green Plan Guidance', '2025', 'NHS', 'https://www.england.nhs.uk/', 'alignment'),
    ('EU_GREEN_DEAL', 'European Green Deal / Zero Pollution alignment', 'current', 'EU', 'https://commission.europa.eu/', 'alignment')
on conflict (framework_code) do update
set framework_name = excluded.framework_name,
    framework_version = excluded.framework_version,
    framework_family = excluded.framework_family,
    source_url = excluded.source_url,
    scoring_mode = excluded.scoring_mode,
    is_active = true;

with f as (
    select framework_id, framework_code
    from zerocare_sustainability.standard_frameworks
    where framework_code in ('WHO_GREEN_HOSPITAL','NHS_GREEN_PLAN','EU_GREEN_DEAL')
)
insert into zerocare_sustainability.standard_domains (
    framework_id, domain_code, domain_name, domain_description, weight_pct
)
select framework_id, domain_code, domain_name, domain_description, weight_pct
from (
    select framework_id, framework_code,
           'ENERGY_CARBON'::text as domain_code,
           'Energy & Carbon'::text as domain_name,
           'Electricity use and energy-related sustainability alignment'::text as domain_description,
           35.00::numeric as weight_pct
    from f
    union all
    select framework_id, framework_code,
           'WATER_WASTEWATER',
           'Water & Wastewater',
           'Water stewardship and wastewater control alignment',
           35.00
    from f
    union all
    select framework_id, framework_code,
           'WASTE_CIRCULARITY',
           'Waste & Circularity',
           'Waste generation, segregation and circularity alignment',
           20.00
    from f
    union all
    select framework_id, framework_code,
           'GOVERNANCE_REPORTING',
           'Governance & Reporting',
           'Policies, plans, supplier disclosure and formal reporting',
           10.00
    from f
) x
on conflict (framework_id, domain_code) do update
set domain_name = excluded.domain_name,
    domain_description = excluded.domain_description,
    weight_pct = excluded.weight_pct,
    is_active = true;

with fw as (
    select framework_id, framework_code
    from zerocare_sustainability.standard_frameworks
    where framework_code in ('WHO_GREEN_HOSPITAL','NHS_GREEN_PLAN','EU_GREEN_DEAL')
),
dm as (
    select d.domain_id, d.framework_id, f.framework_code, d.domain_code
    from zerocare_sustainability.standard_domains d
    join fw f on f.framework_id = d.framework_id
)
insert into zerocare_sustainability.standard_indicators (
    framework_id, domain_id, indicator_code, indicator_name, indicator_description, unit,
    calculator_key, source_metric_codes, default_assessment_state, weight_pct
)
select framework_id, domain_id, indicator_code, indicator_name, indicator_description, unit,
       calculator_key, source_metric_codes, default_assessment_state, weight_pct
from (
    select framework_id, domain_id,
           'ELECTRICITY_DAILY'::text as indicator_code,
           'Daily electricity consumption'::text as indicator_name,
           'Operational electricity consumption captured from daily metrics'::text as indicator_description,
           'kWh'::text as unit,
           'baseline_delta'::text as calculator_key,
           array['electricity_kwh']::text[] as source_metric_codes,
           'assessed_if_data'::text as default_assessment_state,
           35.00::numeric as weight_pct
    from dm where domain_code='ENERGY_CARBON'

    union all
    select framework_id, domain_id,
           'WATER_DAILY',
           'Daily water consumption',
           'Operational water use captured from daily metrics',
           'm3',
           'baseline_delta',
           array['water_m3'],
           'assessed_if_data',
           20.00
    from dm where domain_code='WATER_WASTEWATER'

    union all
    select framework_id, domain_id,
           'WASTEWATER_DAILY',
           'Daily wastewater generation',
           'Operational wastewater captured from daily metrics',
           'm3',
           'baseline_delta',
           array['wastewater_m3'],
           'assessed_if_data',
           15.00
    from dm where domain_code='WATER_WASTEWATER'

    union all
    select framework_id, domain_id,
           'WASTEWATER_TO_WATER_RATIO',
           'Wastewater to water ratio',
           'Derived ratio = wastewater / water * 100',
           '%',
           'ratio_baseline_delta',
           array['water_m3','wastewater_m3'],
           'assessed_if_data',
           65.00
    from dm where domain_code='WATER_WASTEWATER'

    union all
    select framework_id, domain_id,
           'TOTAL_WASTE_DAILY',
           'Daily total waste generation',
           'Operational total waste captured from daily metrics',
           'kg',
           'baseline_delta',
           array['total_waste_kg'],
           'assessed_if_data',
           60.00
    from dm where domain_code='WASTE_CIRCULARITY'

    union all
    select framework_id, domain_id,
           'HAZARDOUS_WASTE_SHARE',
           'Hazardous / medical waste share',
           'Derived share of hazardous waste within total waste',
           '%',
           'not_assessed',
           array['medical_waste_kg','hazardous_waste_kg','total_waste_kg'],
           'not_assessed',
           40.00
    from dm where domain_code='WASTE_CIRCULARITY'

    union all
    select framework_id, domain_id,
           'NET_ZERO_PLAN_STATUS',
           'Net zero / sustainability plan status',
           'Formal organisation-level sustainability plan presence',
           'flag',
           'not_assessed',
           array[]::text[],
           'not_assessed',
           40.00
    from dm where domain_code='GOVERNANCE_REPORTING'

    union all
    select framework_id, domain_id,
           'SUPPLIER_DISCLOSURE_STATUS',
           'Supplier carbon disclosure status',
           'Supplier-level carbon disclosure / reduction-plan maturity',
           'flag',
           'not_assessed',
           array[]::text[],
           'not_assessed',
           30.00
    from dm where domain_code='GOVERNANCE_REPORTING'

    union all
    select framework_id, domain_id,
           'WASTE_SEGREGATION_POLICY_STATUS',
           'Waste segregation policy status',
           'Presence of segregation / handling / reporting policy',
           'flag',
           'not_assessed',
           array[]::text[],
           'not_assessed',
           30.00
    from dm where domain_code='GOVERNANCE_REPORTING'
) x
on conflict (framework_id, indicator_code) do update
set domain_id = excluded.domain_id,
    indicator_name = excluded.indicator_name,
    indicator_description = excluded.indicator_description,
    unit = excluded.unit,
    calculator_key = excluded.calculator_key,
    source_metric_codes = excluded.source_metric_codes,
    default_assessment_state = excluded.default_assessment_state,
    weight_pct = excluded.weight_pct,
    is_active = true;

insert into zerocare_sustainability.indicator_thresholds (
    indicator_id, effective_from, rule_type, comparator,
    green_min, green_max, amber_min, amber_max, red_min, red_max,
    score_green, score_amber, score_red, bootstrap_score, notes
)
select
    si.indicator_id,
    current_date,
    case
        when si.calculator_key in ('baseline_delta','ratio_baseline_delta') then 'baseline_delta_pct'
        when si.calculator_key = 'not_assessed' then 'not_assessed'
        else 'baseline_delta_pct'
    end as rule_type,
    case
        when si.calculator_key in ('baseline_delta','ratio_baseline_delta') then 'lower_better'
        else 'na'
    end as comparator,
    0, 5,
    5, 15,
    15, null,
    100, 70, 40, 70,
    'Phase-1 internal alignment thresholds. Absolute legal/clinical norms not yet loaded.'
from zerocare_sustainability.standard_indicators si
where not exists (
    select 1
    from zerocare_sustainability.indicator_thresholds it
    where it.indicator_id = si.indicator_id
);

create or replace function zerocare_sustainability.refresh_sustainability_layer(
    p_metric_date date default null,
    p_facility_code text default null
)
returns void
language plpgsql
as $$
begin
    with src as (
        select
            v.metric_date,
            v.facility_id,
            v.facility_code,
            sum(case when v.metric_code = 'electricity_kwh' then v.metric_value end) as electricity_kwh,
            sum(case when v.metric_code = 'water_m3' then v.metric_value end) as water_m3,
            sum(case when v.metric_code = 'wastewater_m3' then v.metric_value end) as wastewater_m3,
            sum(case when v.metric_code = 'total_waste_kg' then v.metric_value end) as total_waste_kg,
            sum(case when v.metric_code in ('medical_waste_kg','hazardous_waste_kg') then v.metric_value end) as hazardous_waste_kg
        from zerocare_sustainability.vw_daily_metrics_compat v
        where (p_metric_date is null or v.metric_date = p_metric_date)
          and (p_facility_code is null or v.facility_code = p_facility_code)
        group by v.metric_date, v.facility_id, v.facility_code
    ),
    expanded as (
        select metric_date, facility_id, facility_code, 'ELECTRICITY_DAILY'::text as indicator_code, electricity_kwh::numeric as observed_value, 'kWh'::text as unit,
               jsonb_build_object('electricity_kwh', electricity_kwh) as source_metrics
        from src
        union all
        select metric_date, facility_id, facility_code, 'WATER_DAILY', water_m3::numeric, 'm3',
               jsonb_build_object('water_m3', water_m3)
        from src
        union all
        select metric_date, facility_id, facility_code, 'WASTEWATER_DAILY', wastewater_m3::numeric, 'm3',
               jsonb_build_object('wastewater_m3', wastewater_m3)
        from src
        union all
        select metric_date, facility_id, facility_code, 'WASTEWATER_TO_WATER_RATIO',
               case when coalesce(water_m3,0) = 0 then null else round((wastewater_m3 / nullif(water_m3,0)) * 100.0, 4) end::numeric,
               '%',
               jsonb_build_object('water_m3', water_m3, 'wastewater_m3', wastewater_m3)
        from src
        union all
        select metric_date, facility_id, facility_code, 'TOTAL_WASTE_DAILY', total_waste_kg::numeric, 'kg',
               jsonb_build_object('total_waste_kg', total_waste_kg)
        from src
        union all
        select metric_date, facility_id, facility_code, 'HAZARDOUS_WASTE_SHARE', null::numeric, '%',
               jsonb_build_object('hazardous_waste_kg', hazardous_waste_kg, 'total_waste_kg', total_waste_kg)
        from src
    ),
    candidate as (
        select
            e.metric_date,
            e.facility_id,
            si.indicator_id,
            si.framework_id,
            si.domain_id,
            si.indicator_code,
            si.calculator_key,
            e.observed_value,
            e.unit,
            e.source_metrics,
            it.rule_type,
            it.green_max,
            it.amber_max,
            it.score_green,
            it.score_amber,
            it.score_red,
            it.bootstrap_score
        from expanded e
        join zerocare_sustainability.standard_indicators si
          on si.indicator_code = e.indicator_code
         and si.is_active = true
        left join lateral (
            select *
            from zerocare_sustainability.indicator_thresholds it
            where it.indicator_id = si.indicator_id
              and current_date >= it.effective_from
              and (it.effective_to is null or current_date <= it.effective_to)
            order by it.effective_from desc
            limit 1
        ) it on true
    ),
    scored as (
        select
            c.metric_date,
            c.facility_id,
            c.indicator_id,
            c.observed_value,
            b.baseline_value,
            case
                when c.calculator_key = 'not_assessed' then null
                when c.observed_value is null then null
                when b.baseline_value is null or b.baseline_value = 0 then null
                else round(abs((c.observed_value - b.baseline_value) / b.baseline_value) * 100.0, 4)
            end as delta_pct,
            case
                when c.calculator_key = 'not_assessed' then null
                when c.observed_value is null then null
                when b.baseline_value is null or b.baseline_value = 0 then c.bootstrap_score
                when abs((c.observed_value - b.baseline_value) / nullif(b.baseline_value,0)) * 100.0 <= c.green_max then c.score_green
                when abs((c.observed_value - b.baseline_value) / nullif(b.baseline_value,0)) * 100.0 <= c.amber_max then c.score_amber
                else c.score_red
            end as score,
            case
                when c.calculator_key = 'not_assessed' then 'not_assessed'
                when c.observed_value is null then 'not_assessed'
                when b.baseline_value is null or b.baseline_value = 0 then 'baseline_pending'
                when abs((c.observed_value - b.baseline_value) / nullif(b.baseline_value,0)) * 100.0 <= c.green_max then 'good'
                when abs((c.observed_value - b.baseline_value) / nullif(b.baseline_value,0)) * 100.0 <= c.amber_max then 'monitor'
                else 'action'
            end as status,
            case
                when c.calculator_key = 'not_assessed' then 'not_assessed'
                when c.observed_value is null then 'not_assessed'
                when b.baseline_value is null or b.baseline_value = 0 then 'assessed_bootstrap'
                else 'assessed'
            end as assessment_state,
            c.unit,
            c.source_metrics,
            jsonb_build_object(
                'calculator_key', c.calculator_key,
                'rule_type', c.rule_type,
                'green_max_pct', c.green_max,
                'amber_max_pct', c.amber_max
            ) as scoring_detail
        from candidate c
        left join lateral (
            select percentile_cont(0.5) within group (order by fid.observed_value) as baseline_value
            from zerocare_sustainability.facility_indicator_daily fid
            where fid.facility_id = c.facility_id
              and fid.indicator_id = c.indicator_id
              and fid.metric_date between (c.metric_date - interval '30 day')::date and (c.metric_date - interval '1 day')::date
              and fid.observed_value is not null
        ) b on true
    )
    insert into zerocare_sustainability.facility_indicator_daily (
        metric_date, facility_id, indicator_id, observed_value, baseline_value, delta_pct,
        score, status, assessment_state, unit, source_metrics, scoring_detail, updated_at
    )
    select
        metric_date, facility_id, indicator_id, observed_value, baseline_value, delta_pct,
        score, status, assessment_state, unit, source_metrics, scoring_detail, now()
    from scored
    on conflict (metric_date, facility_id, indicator_id) do update
    set observed_value = excluded.observed_value,
        baseline_value = excluded.baseline_value,
        delta_pct = excluded.delta_pct,
        score = excluded.score,
        status = excluded.status,
        assessment_state = excluded.assessment_state,
        unit = excluded.unit,
        source_metrics = excluded.source_metrics,
        scoring_detail = excluded.scoring_detail,
        updated_at = now();

    delete from zerocare_sustainability.facility_standard_scores
    where (p_metric_date is null or metric_date = p_metric_date)
      and (
            p_facility_code is null
            or facility_id in (
                select facility_id
                from zerocare_operational.facilities
                where facility_code = p_facility_code
            )
          );

    insert into zerocare_sustainability.facility_standard_scores (
        metric_date, facility_id, framework_id, domain_id, score_level,
        assessed_count, not_assessed_count, total_count, score, status, score_detail, updated_at
    )
    select
        fid.metric_date,
        fid.facility_id,
        si.framework_id,
        si.domain_id,
        'domain',
        count(*) filter (where fid.assessment_state like 'assessed%')::int as assessed_count,
        count(*) filter (where fid.assessment_state = 'not_assessed')::int as not_assessed_count,
        count(*)::int as total_count,
        round(avg(fid.score) filter (where fid.score is not null), 2) as score,
        case
            when count(*) filter (where fid.assessment_state like 'assessed%') = 0 then 'not_assessed'
            when avg(fid.score) filter (where fid.score is not null) >= 85 then 'good'
            when avg(fid.score) filter (where fid.score is not null) >= 60 then 'monitor'
            else 'action'
        end as status,
        jsonb_build_object(
            'aggregation', 'domain',
            'assessed_ratio_pct',
            round(
                case when count(*) = 0 then 0
                     else (count(*) filter (where fid.assessment_state like 'assessed%')::numeric / count(*)::numeric) * 100
                end, 2
            )
        ) as score_detail,
        now()
    from zerocare_sustainability.facility_indicator_daily fid
    join zerocare_sustainability.standard_indicators si
      on si.indicator_id = fid.indicator_id
    where (p_metric_date is null or fid.metric_date = p_metric_date)
      and (
            p_facility_code is null
            or fid.facility_id in (
                select facility_id
                from zerocare_operational.facilities
                where facility_code = p_facility_code
            )
          )
    group by fid.metric_date, fid.facility_id, si.framework_id, si.domain_id

    union all

    select
        fid.metric_date,
        fid.facility_id,
        si.framework_id,
        null::uuid as domain_id,
        'framework',
        count(*) filter (where fid.assessment_state like 'assessed%')::int as assessed_count,
        count(*) filter (where fid.assessment_state = 'not_assessed')::int as not_assessed_count,
        count(*)::int as total_count,
        round(avg(fid.score) filter (where fid.score is not null), 2) as score,
        case
            when count(*) filter (where fid.assessment_state like 'assessed%') = 0 then 'not_assessed'
            when avg(fid.score) filter (where fid.score is not null) >= 85 then 'good'
            when avg(fid.score) filter (where fid.score is not null) >= 60 then 'monitor'
            else 'action'
        end as status,
        jsonb_build_object(
            'aggregation', 'framework',
            'assessed_ratio_pct',
            round(
                case when count(*) = 0 then 0
                     else (count(*) filter (where fid.assessment_state like 'assessed%')::numeric / count(*)::numeric) * 100
                end, 2
            )
        ) as score_detail,
        now()
    from zerocare_sustainability.facility_indicator_daily fid
    join zerocare_sustainability.standard_indicators si
      on si.indicator_id = fid.indicator_id
    where (p_metric_date is null or fid.metric_date = p_metric_date)
      and (
            p_facility_code is null
            or fid.facility_id in (
                select facility_id
                from zerocare_operational.facilities
                where facility_code = p_facility_code
            )
          )
    group by fid.metric_date, fid.facility_id, si.framework_id;
end;
$$;
