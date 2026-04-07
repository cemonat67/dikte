# ZERO@HOSPITAL — SESSION STATE
## Checkpoint Date: 2026-04-05

---

## ✅ CURRENT VERIFIED STATE

### Backend
- Production backend running and stable
- No legacy facility mapping in main endpoints
- Direct `facility_code` usage across APIs

### API Status

#### Dashboard
- /api/dashboard/latest → ✅ WORKING (multi-hospital)
- /api/dashboard/daily → ✅ WORKING (vw_dashboard_daily)

#### Clinic Layer
- /api/dashboard/clinic-daily → ✅ WORKING (DEMO_BORNOVA verified)
- /api/dashboard/clinic-highlights → ✅ WORKING (DEMO_BORNOVA verified)

### Verified Facilities
- CIGLI_HOSP → OK
- DEMO_BORNOVA → OK
- DEMO_KONAK → OK (latest only)
- DEMO_KSK → OK (latest only)

---

## ⚠️ DATA REALITY

- Clinic-level data originally existed only for Çiğli
- DEMO_BORNOVA → clinic data SEEDED and verified
- DEMO_KONAK → clinic data NOT VERIFIED
- DEMO_KSK → clinic data NOT VERIFIED

---

## ✅ FRONTEND STATUS

- static/app.js cleaned:
  - ❌ demo_hospital REMOVED
  - ❌ hardcoded facility REMOVED
  - ✅ dynamic facility selection ACTIVE

- loadAll() → dynamic
- loadClinicDashboard() → dynamic
- intake payload → dynamic

---

## 🔥 SYSTEM ARCHITECTURE (NOW)

- TRUE multi-hospital system
- No fallback hacks
- No demo-only shortcuts
- Facility-driven pipeline end-to-end

---

## 🎯 NEXT STEPS

1. Verify clinic coverage:
   - DEMO_KONAK
   - DEMO_KSK

2. If missing:
   - Apply same clinic seed pattern as DEMO_BORNOVA

3. UI validation:
   - facility selector behavior
   - ensure correct API calls per selection

4. Optional:
   - production deploy + cache bust

---

## ⚙️ WORKING RULES

- Turkish only
- Terminal-first
- 1 command + 1 control
- No nano
- Diagnose first, then fix
- Do NOT break working components
- Always verify with curl before UI assumptions

---

## 🧠 IMPORTANT INSIGHT

Previous issue was NOT code.

It was:
→ data absence + hardcoded fallback

Now:
→ system is data-driven and scalable

---

## 🚀 STATUS

SYSTEM = STABLE  
ARCHITECTURE = CORRECT  
NEXT = DATA COVERAGE EXPANSION


## 2026-04-05 — Clinic Synthetic Generator v1 (DESIGN LOCK)

### VERIFIED
- `zerocare_operational.daily_metrics` long-format confirmed
- 1 metric = 1 row structure confirmed
- write target confirmed:
  - `facility_id`
  - `department_id`
  - `metric_date`
  - `metric_code`
  - `value`
  - `unit_code`
  - `quality_flag`
  - `calculation_method`
  - `source_system`

### GLOBAL CLINIC CATALOG
- CARDIO
- ER
- ICU
- IM
- LAB
- ONCO
- ORTHO
- RAD
- SURG

### SYNTHETIC METRIC SET
- electricity_kwh
- water_m3
- wastewater_m3
- medical_waste_kg
- pathological_waste_kg

### UNIT STANDARD
- electricity_kwh -> kwh
- water_m3 -> m3
- wastewater_m3 -> m3
- medical_waste_kg -> kg
- pathological_waste_kg -> kg

### WRITE CONTRACT v1
- quality_flag = `synthetic`
- calculation_method = `clinic_behavior_v1`
- source_system = `clinic_synth_v1`

### INSERT POLICY
- overwrite YOK
- update YOK
- sadece missing rows insert
- duplicate guard:
  - facility_id
  - department_id
  - metric_date
  - metric_code
  - source_system

### GENERATOR FLOW
- clinic_behavior.json -> behavior-driven preview
- preview -> validation
- validation -> long-format transform
- long-format -> controlled insert

### PREVIEW STATUS
- 7 gün x 9 clinic = 63 logical preview rows doğrulandı
- wastewater_m3 < water_m3 relation preview’de doğrulandı

### NEXT
1. generator preview script dosyası oluşturulacak
2. facility + department resolver eklenecek
3. long-format payload üretilecek
4. controlled insert phase açılacak
5. clinic endpoint validation yapılacak

## 2026-04-05 — SUSTAINABILITY INTELLIGENCE LAYER v1

### GOAL
- Operational data ile Green Deal + Green Hospital / NHS alignment skor katmanı kuruldu.
- Ayrı schema: `zerocare_sustainability`

### ARCHITECTURE
- Reference tables:
  - `standard_frameworks`
  - `standard_domains`
  - `standard_indicators`
  - `indicator_thresholds`
- Fact tables:
  - `facility_indicator_daily`
  - `facility_standard_scores`
- Adapter view:
  - `vw_daily_metrics_compat`
- Refresh function:
  - `zerocare_sustainability.refresh_sustainability_layer(date, facility_code)`

### PHASE-1 SCORING
- Assessed if data exists:
  - ELECTRICITY_DAILY
  - WATER_DAILY
  - WASTEWATER_DAILY
  - WASTEWATER_TO_WATER_RATIO
  - TOTAL_WASTE_DAILY
- Others:
  - `not_assessed`

### SCORING MODEL
- Phase-1 uses baseline-relative scoring, not universal absolute thresholds.
- Logic:
  - 30-day rolling median baseline
  - <=5% delta => good
  - <=15% delta => monitor
  - >15% delta => action
  - no baseline yet => `baseline_pending`

### NEXT
1. verify metric_code names in `daily_metrics`
2. add API endpoint for sustainability scores
3. add dashboard cards for framework/domain status
4. later add policy / supplier / segregation evidence tables


## 2026-04-05 — SUSTAINABILITY SCORING ENGINE PHASE 2 CHECKPOINT

### VERIFIED
- `backend/engine/scoring_engine.py` hardcoded threshold yerine DB tabanlı çalışacak şekilde güncellendi
- DB threshold framework: `zerocare_sustainability.indicator_thresholds`
- Framework code aktif: `GREEN_HOSPITAL`
- Seed edilen indicator threshold kayıtları:
  - `energy_kwh_per_patient`
  - `water_m3_per_patient`
  - `waste_kg_per_patient`
- Legacy tablo yapısından gelen kısıtlar giderildi:
  - `indicator_id` NOT NULL kaldırıldı
  - `rule_type` ve `comparator` için default verildi
- Python dependency eklendi:
  - `psycopg2-binary`
- `test_scoring.py` başarıyla doğrulandı

### VERIFIED TEST OUTPUT
- framework_code: `GREEN_HOSPITAL`
- energy_kwh_per_patient:
  - value: 22
  - status: monitor
  - score: 52.0
- water_m3_per_patient:
  - value: 1.1
  - status: bad
  - score: 32.2
- waste_kg_per_patient:
  - value: 1.5
  - status: monitor
  - score: 65.0
- total_score: 50.06
- risk: HIGH

### NEXT
1. scoring engine için API endpoint ekle
2. dashboard summary response içine sustainability score katmanı ekle
3. facility bazlı override threshold desteği ekle
4. department bazlı scoring hazırlığı yap
5. framework score + indicator score UI kartlarına bağla


## 2026-04-05 — API INTEGRATION CHECKPOINT (SUSTAINABILITY SCORING ON /api/dashboard/latest)

### VERIFIED
- `server.py` içinde `/api/dashboard/latest` endpoint’ine `sustainability_scoring` katmanı eklendi
- `backend.engine.scoring_engine.calculate_total` import edilerek canlı scoring entegrasyonu yapıldı
- `zerocare_operational.facilities` tablosundan `bed_count` join edildi
- scoring mode bu checkpoint’te `per_bed` olarak çalışıyor
- `bed_count` olmayan tesislerde fallback status tasarlandı:
  - `score_pending_bed_count_missing`
- `fetch_one()` içindeki hatalı `facility_code` referansı kaldırıldı
- `/health` endpoint yeniden doğrulandı
- local API test başarıyla geçti

### VERIFIED API TEST
- endpoint:
  - `/api/dashboard/latest?facility_code=CIGLI_HOSP`
- returned facility:
  - `CIGLI_HOSP`
  - `Demo Hospital Çiğli Hastanesi`
- reading_date:
  - `2026-04-02`
- bed_count:
  - `250`

### VERIFIED SUSTAINABILITY SCORING OUTPUT
- framework_code:
  - `GREEN_HOSPITAL`
- derived_inputs:
  - `energy_kwh_per_bed = 50.4`
  - `water_m3_per_bed = 0.168`
  - `waste_kg_per_bed = 0.088`
- indicator results:
  - energy_kwh_per_bed:
    - status: `bad`
    - score: `0.0`
  - water_m3_per_bed:
    - status: `good`
    - score: `95.8`
  - waste_kg_per_bed:
    - status: `good`
    - score: `98.83`
- total_score:
  - `55.61`
- risk:
  - `HIGH`

### INTERPRETATION
- Current CIGLI_HOSP sustainability scoring shows main pressure on energy intensity
- Water and waste intensity are currently in good band
- Executive reading: hospital sustainability risk is driven primarily by energy inefficiency

### NEXT
1. executive sustainability summary alanı ekle
2. UI dashboard kartlarına `sustainability_scoring` bağla
3. `dashboard/daily` tarafına trend-level sustainability scoring düşün
4. bed_count eksik tesisler için intake / facility master tamamlama akışı kur
5. ileride per-patient mode için denominator genişlet


## 2026-04-05 — DAILY CO2 NULL DIAGNOSIS CHECKPOINT

### VERIFIED STATE
- Multi-hospital backend aktif
- `/api/dashboard/daily` ve `/api/dashboard/latest` akışı `vw_dashboard_daily` tabanlı çalışıyor
- `sustainability_scoring` aktif
- `GREEN_HOSPITAL` scoring engine entegre
- `generate_summary` ile executive summary üretimi aktif
- Executive Sustainability Summary UI'ya bağlı
- KPI kartları çalışıyor
- Trend ve tablo çalışıyor
- Üretim (kg) frontend hesaplama:
  - `medical_waste_kg + pathological_waste_kg + general_waste_kg`
- CO₂ (kg) frontend gösterimi:
  - `scope2_location_tco2e * 1000`
- Null handling düzeltildi:
  - değer null ise `—` gösteriliyor
- Doğru test ortamı:
  - `http://127.0.0.1:8050/`
- `8099` static server yanlış test ortamıydı; API yoktu

### CRITICAL VERIFIED DIAGNOSIS
- Sorun frontend değil
- Sorun `/api/dashboard/daily` → `vw_dashboard_daily` → SQL derivation katmanında
- Doğrulanmış çıktı:
  - `2026-04-05 | Demo Hospital Konak | scope2_location_tco2e = 7.896`
  - `2026-04-04 | Demo Hospital Bornova | scope2_location_tco2e = None`
  - `2026-04-03 | Demo Hospital Bornova | scope2_location_tco2e = None`
  - `2026-04-02 | Demo Hospital Çiğli Hastanesi | scope2_location_tco2e = None`
  - `2026-04-01 | Demo Hospital Bornova | scope2_location_tco2e = None`
  - `2026-03-31 | Demo Hospital Bornova | scope2_location_tco2e = None`
  - `2026-03-30 | Demo Hospital Bornova | scope2_location_tco2e = None`

### NEXT TARGET
- `scope2_location_tco2e` neden yalnızca bugünde dolu, kök neden bulunacak
- Önce backend SQL / view / endpoint zinciri teşhis edilecek
- Gerekirse geçmiş günler için kontrollü fallback CO₂ türetimi eklenecek
- `latest` endpoint bozulmayacak
- scoring mantığı bozulmayacak
- düzeltme öncesi teşhis tamamlanacak

### WORK RULES
- sadece Türkçe
- terminal-first
- 1 komut + 1 kontrol
- no nano
- önce teşhis sonra düzeltme
- çalışan şeyi bozma
- önemli kararları `SESSION_STATE.md` ve `product.md` içine yaz


## 2026-04-05 — BAZEKOL HARDCODE CLEANUP CHECKPOINT

### VERIFIED
- Aktif kod tabanında `Bazekol/bazekol` hardcode araması yapıldı
- Son aktif Bazekol referansları temizlendi
- Aşağıdaki dosyalar parametreli hale getirildi:
  - `scripts/generate_validate_promote_synthetic.py`
  - `scripts/daily_live_generator.py`
  - `scripts/distribute_facility_to_departments.py`
  - `main.py`
- `FACILITY_CODE` ve/veya `FACILITY_NAME` artık env üzerinden zorunlu geliyor
- Default Bazekol fallback tamamen kaldırıldı
- `main.py` içindeki clinic endpoint'leri artık hardcoded `facility_name = 'Bazekol Çiğli Hastanesi'` kullanmıyor
- `clinic-highlights` ve `clinic-daily` endpoint'leri `facility_code` parametresi ile çalışıyor
- Son taramada aktif `.py/.sql` dosyalarında `Bazekol|bazekol` sonucu sıfır bulundu

### MEANING
- Synthetic / orchestration katmanı artık müşteri-bağımsız hale getirildi
- Sistem tek müşteri kimliğine kilitli olmaktan çıkarıldı
- Multi-hospital / demo-hospital üretim akışı için gerekli en kritik temizlik tamamlandı

### NEXT TARGET
- Orchestration pipeline'ını Demo Hospital facility seti için çalıştırmak
- Generated data'nın hangi tabloya yazıldığına göre bridge / promote akışını netleştirmek
- Gerekirse `core_metric_readings` → `daily_metrics` mapping katmanını kurmak
- Sonrasında `refresh_sustainability_layer` ve dashboard doğrulaması yapmak

## 2026-04-05 — N8N ORCHESTRATION LAYER CHECKPOINT

### VERIFIED
- `orchestration_n8n/` klasörü oluşturuldu ve app katmanından ayrıştırıldı
- Amaç netleştirildi:
  - multi-facility synthetic orchestration
  - validation controller
  - core->daily bridge orchestration
  - watchdog / remediation layer
- Docker/Compose doğrulandı:
  - Docker version 29.2.1
  - Docker Compose version v5.1.0
- Lokal n8n stack compose ile ayağa kaldırıldı
- Container:
  - `zh_n8n`
- Health doğrulandı:
  - `http://127.0.0.1:5678/healthz` => `{"status":"ok"}`
- Mimari karar:
  - mevcut dashboard/backend (`app/`) korunacak
  - orchestration katmanı ayrı tutulacak
  - fallback patch yerine data pipeline orchestration yaklaşımı izlenecek

### TARGET WORKFLOWS
- `ZH_MASTER_ORCHESTRATOR`
- `ZH_FACILITY_RUNNER`
- `ZH_VALIDATION_CONTROLLER`
- `ZH_CORE_TO_DAILY_BRIDGE`
- `ZH_HEALTH_WATCHDOG`

### NEXT
1. İlk workflow tasarım dosyalarını çıkar
2. Facility listesi ve metric profile modelini tanımla
3. `core_metric_readings -> daily_metrics` bridge mantığını netleştir
4. n8n içinde master/facility/watchdog akışlarını kur


## 2026-04-06 — KALICI ÇALIŞMA KURALI: ÖNCE PLAN, SONRA KOD

- Kod/proje işlerinde hemen implementasyona girilmeyecek.
- Önce yeterli planlama ve kurgu yapılacak.
- Mimari, kapsam, veri akışı, başarı kriteri ve adım sırası netleştirilmeden kod yazılmayacak.
- Standart sıra:
  1. teşhis
  2. plan/kapsam
  3. çözüm kurgusu
  4. implementasyon
  5. doğrulama
- Bu kural yeni chat promptlarında da taşınacak.


## 2026-04-06 — STAGING LAYER STABLE (CANONICAL INTAKE)

### COMPLETED
- staging_daily_metrics tablosu production-ready
- fingerprint unique constraint ile exact duplicate kontrolü aktif
- versioning (record_version) + supersede mantığı çalışıyor
- active/passive record yönetimi doğrulandı
- updated_at trigger çalışıyor
- v_staging_daily_metrics_status view doğrulandı

### VERIFIED TESTS
- 7 required metric insert → status = READY
- duplicate insert → active set korunuyor
- version upgrade (v1 -> v2) → lineage + active switch OK
- READY durumu version sonrası korunuyor

### CURRENT STATE
- canonical intake layer hazır
- staging → production bridge henüz yok

### NEXT (CRITICAL)
1. promote contract tasarımı (staging → daily_metrics)
2. idempotent promote logic
3. promote sonrası staging flag stratejisi
4. orchestration (n8n / API trigger)


## 2026-04-06 — N8N PROMOTE PRODUCTION GO-LIVE CHECKPOINT

### VERIFIED
- `zerocare_audit.promote_runs` audit tablosu aktif
- `zerocare_operational.run_promote_with_audit(...)` wrapper fonksiyonu aktif
- n8n workflow: `ZH_PROMOTE_PRODUCTION`
- cron schedule: daily 06:00
- webhook endpoint: `POST /webhook/zh-promote-production`
- postgres execution from n8n confirmed
- audit confirmed across:
  - DRY_RUN
  - NO_OP
  - SUCCESS

### GO-LIVE PROOF
- Test amaçlı staging `electricity_kwh` değeri kontrollü artırıldı ve `written_rows = 1` ile SUCCESS doğrulandı
- Test değişikliği geri alındı
- Geri alma sonrası tekrar `written_rows = 1` ile SUCCESS doğrulandı
- Son canlı webhook çağrısı:
  - `selected_rows = 7`
  - `written_rows = 0`
  - `status = NO_OP`
- Bu davranış idempotent production behavior olarak doğrulandı

### CURRENT STATE
- production promote workflow canlı
- tekrar eden aynı veri için `NO_OP` beklenen ve doğru davranış
- yeni version / fingerprint değişiminde `SUCCESS` ve write gerçekleşiyor

### NEXT
1. webhook body ile `facility_code`, `date_from`, `date_to`, `dry_run` parametre alma
2. alert layer (email/slack) ekleme
3. audit summary view / dashboard widget
4. cron run sonrası lightweight notification

## 2026-04-06 — GENERATOR OMURGASI KARARI

- Teşhis kesinleşti: generator pipeline `public.core_metric_readings` üzerinde kalmış legacy hatta bağlı.
- Çalışan production omurgası `zerocare_operational.staging_daily_metrics -> promote -> daily_metrics -> vw_dashboard_daily` zinciri.
- `daily_live_generator.py` ve `generate_validate_promote_synthetic.py` mevcut haliyle yanlış veri omurgasına yazıyor/okuyor.
- `staging_daily_metrics` write target olarak doğrulandı; manuel insert başarılı.
- `daily_metrics` baseline için ham kaynak, ancak department/facility çoğulluğu içeriyor.
- `vw_dashboard_daily` facility-level günlük pivot view olarak doğrulandı ve baseline için V1'de kullanılmasına karar verildi.
- V1 synthetic metric scope kilitlendi: `electricity_kwh`, `water_m3`, `medical_waste_kg`, `pathological_waste_kg`, `general_waste_kg`.
- V1 scope dışı: `wastewater_m3`, `scope2_location_tco2e`, `waste_cost_try`.
- Karar: `daily_live_generator.py` clean rewrite ile `vw_dashboard_daily`den baseline okuyacak, `staging_daily_metrics`e yazacak. Promote ayrı adımda tetiklenecek.

## 2026-04-06 — DAILY LIVE GENERATOR V3 → PROMOTE → DASHBOARD CHECKPOINT

### VERIFIED
- Legacy generator hattının ana kaynak olmayacağı kararı canlı olarak doğrulandı
- Yaşayan omurga doğrulandı:
  `staging_daily_metrics -> run_promote_with_audit / promote_ready_daily_metrics -> daily_metrics -> vw_dashboard_daily`
- `daily_live_generator.py` clean rewrite sonrası `daily_live_generator_v3` şu 7 metrici üretiyor:
  - `electricity_kwh`
  - `water_m3`
  - `medical_waste_kg`
  - `pathological_waste_kg`
  - `general_waste_kg`
  - `scope2_location_tco2e`
  - `waste_cost_try`
- Derived kurallar doğrulandı:
  - `scope2_location_tco2e = electricity_kwh * 0.000460`
  - `waste_cost_try = total_waste_kg * 43.3255`
- `connect()` içinde `conn.prepare_threshold = None` ile prepared statement problemi aşıldı

### LIVE VERIFICATION — DEMO_KONAK / 2026-04-06
- Batch: `7a8a4194-d247-4dc7-aee2-411322a1ab94`
- `staging_daily_metrics` içinde 7/7 metric yazıldı
- Tüm satırlar `VALID`
- Tüm satırlar `is_promotable = true`
- `v_staging_daily_metrics_status` sonucu:
  - `total_metrics = 7`
  - `valid_metrics = 7`
  - `status = READY`
- `run_promote_with_audit('DEMO_KONAK', '2026-04-06', '2026-04-06', false)` sonucu:
  - `selected_days = 1`
  - `selected_rows = 7`
  - `written_rows = 7`
  - `status = SUCCESS`
- `vw_dashboard_daily` üzerinde facility/day pivot satırı eksiksiz doğrulandı

### DECISION
- Enterprise Dogma korunuyor
- READY=7 kuralı gevşetilmeyecek
- Generator yaşayan production omurgasına bağlı kalacak
- `vw_dashboard_daily` artık generator doğrulaması için de resmi okuma katmanı kabul edilecek

### NEXT
1. Aynı doğrulamayı en az 1–2 farklı demo facility için tekrar et
2. `generate_validate_promote_synthetic.py` dosyasını da aynı omurgaya hizalı mı diye doğrula
3. Bu akışı orchestration katmanına bağlayacak günlük run planını netleştir
4. Gerekirse n8n veya scheduler katmanına enterprise-ready günlük akış ekle

## 2026-04-06 — SECOND FACILITY VERIFICATION (DEMO_BORNOVA)

### VERIFIED
- `daily_live_generator_v3` ikinci facility üzerinde de aynı production omurgasıyla doğrulandı
- Test facility: `DEMO_BORNOVA`
- Generator çıktısı:
  - `status = OK`
  - `baseline_day = 2026-04-05`
  - `start_date = 2026-04-06`
  - `end_date = 2026-04-06`
  - `inserted_rows = 7`
  - `batch_id = 67b4ecfc-88ce-46fa-ad28-498ba8098d33`
  - `mode = enterprise_ready_7_metrics`

### LIVE VERIFICATION — DEMO_BORNOVA / 2026-04-06
- `v_staging_daily_metrics_status` sonucu:
  - `total_metrics = 7`
  - `valid_metrics = 7`
  - `status = READY`
- `run_promote_with_audit('DEMO_BORNOVA', '2026-04-06', '2026-04-06', false)` sonucu:
  - `selected_days = 1`
  - `selected_rows = 7`
  - `written_rows = 7`
  - `status = SUCCESS`
- `vw_dashboard_daily` facility/day satırı eksiksiz doğrulandı:
  - `electricity_kwh = 22094.551111`
  - `water_m3 = 481.013447`
  - `medical_waste_kg = 103.746588`
  - `pathological_waste_kg = 24.569223`
  - `general_waste_kg = 389.068558`
  - `scope2_location_tco2e = 10.163494`
  - `waste_cost_try = 22415.936479`

### DECISION
- `daily_live_generator_v3` artık tek-facility değil, çoklu demo facility davranışı açısından da doğrulanmış kabul edilecek
- Yaşayan omurga kararı yalnız `DEMO_KONAK` özel başarısı değil, tekrar üretilebilir sistem davranışı olarak kabul edildi
- Sonraki adımda yeni generator yazmaktan önce orchestration / scheduling planı netleştirilecek

### NEXT
1. `generate_validate_promote_synthetic.py` dosyasının da aynı production omurgasına tam hizalı olup olmadığını doğrula
2. Günlük enterprise run tasarımını netleştir:
   - facility listesi
   - sıra / retry mantığı
   - promote tetik sırası
   - audit / idempotency kuralları
3. Bu akışın n8n mi yoksa Python scheduler mı olacağına karar ver
4. Gerekirse orchestration katmanı için ayrı runner tasarla (`generate -> validate/status -> promote -> verify dashboard`)

## 2026-04-06 — GENERATE_VALIDATE_PROMOTE_SYNTHETIC REWRITE KARARI

### DECISION
- `scripts/generate_validate_promote_synthetic.py` patch edilerek kurtarılmayacak
- Dosya mimari olarak legacy / parallel pipeline mantığı taşıdığı için baştan yazılacak
- Yeni sürüm yalnız yaşayan production omurgasına bağlanacak:
  `vw_dashboard_daily -> staging_daily_metrics -> v_staging_daily_metrics_status -> run_promote_with_audit -> vw_dashboard_daily`
- Yeni sürüm yalnız yaşayan 7 KPI setini üretecek:
  - `electricity_kwh`
  - `water_m3`
  - `medical_waste_kg`
  - `pathological_waste_kg`
  - `general_waste_kg`
  - `scope2_location_tco2e`
  - `waste_cost_try`

### RULES FOR REWRITE
- Legacy tablolar kullanılmayacak:
  - `public.core_metric_readings`
  - `public.synthetic_metric_readings_staging`
  - `public.synthetic_validation_results`
- Custom validation/promote mantığı taşınmayacak
- Script rolü: `generate -> stage -> readiness check -> promote -> verify`
- Multi-facility çalışabilecek şekilde tasarlanacak
- JSON çıktı verecek
- Idempotent olacak
- Önce mimari/net kontrat, sonra clean rewrite

## 2026-04-06 — LEGACY SYNTHETIC ENGINE SQL ARŞİVLENDİ

### VERIFIED
- Repo içi legacy referans taraması yapıldı:
  - aktif yeni scriptte legacy runtime dependency bulunmadı
  - legacy izleri yalnız backup / state / eski SQL artefaktlarında kaldı
- `sql/01_create_synthetic_engine.sql` incelendi
- Dosyanın yalnız aşağıdaki legacy tabloları oluşturduğu doğrulandı:
  - `public.synthetic_metric_readings_staging`
  - `public.synthetic_validation_results`
- Trigger / function / scheduler / view içermediği doğrulandı
- Risk tipi runtime değil, “yanlışlıkla yeniden aktive edilme” riski olarak sınıflandırıldı

### ACTION
- `sql/01_create_synthetic_engine.sql` aktif SQL klasöründen çıkarıldı
- Dosya `archive/legacy/01_create_synthetic_engine.sql` konumuna taşındı
- Böylece production SQL klasörü yalnız yaşayan omurgaya ait migration/DDL dosyalarını içerir hale getirildi

### DECISION
- Legacy synthetic engine artefaktları silinmeyecek, forensic / tarihçe amacıyla arşivde tutulacak
- Ancak aktif production path içinde yer almayacak
- Yeni orchestration runner legacy’ye runtime dependency taşımayacak
- Gerekirse yalnız preflight/read-only audit amaçlı legacy görünürlüğü korunacak

## 2026-04-06 — GENERATE_VALIDATE_PROMOTE_SYNTHETIC ORCHESTRATOR v1 CHECKPOINT

### VERIFIED
- `scripts/generate_validate_promote_synthetic.py` sıfırdan pure orchestrator olarak yeniden yazıldı
- Script artık veri üretmiyor; yalnızca yaşayan hat üzerinde orchestration yapıyor:
  - `daily_live_generator.py`
  - `zerocare_operational.v_staging_daily_metrics_status`
  - `zerocare_operational.run_promote_with_audit`
  - `zerocare_operational.vw_dashboard_daily`
- Legacy synthetic engine runtime dependency kaldırıldı
- Staging manipülasyonu / deactivate logic kaldırıldı
- Tek facility smoke test `DEMO_KONAK / 2026-04-06` için başarıyla doğrulandı
- Doğrulanan çıktı:
  - `generate_status = NOOP: up-to-date`
  - `staging_status = READY`
  - `total_metrics = 7`
  - `valid_metrics = 7`
  - `promote_status = NO_OP`
  - `written_rows = 0`
  - `final_row_exists = true`
- Script tek JSON summary döndürüyor; n8n / API orchestration için uygun

### CURRENT DECISION
- Tüm uygulama baştan yazılmayacak
- Çalışan production omurgası korunacak
- Rewrite yalnız yanlış katmanlarda yapılacak
- Bir sonraki odak:
  1. multi-facility smoke test
  2. orchestration service layer
  3. KPI evaluation + routing + AI commentary contract


## 2026-04-06 — MULTI-FACILITY SMOKE TEST CHECKPOINT

### VERIFIED
- Multi-facility smoke test başarıyla doğrulandı
- Test edilen facility seti:
  - `CIGLI_HOSP`
  - `DEMO_BORNOVA`
  - `DEMO_KONAK`
- Her facility için `scripts/generate_validate_promote_synthetic.py` end-to-end çalıştı
- Her sonuçta aşağıdaki koşullar sağlandı:
  - `status = OK`
  - `generate_status = NOOP: up-to-date`
  - `total_metrics = 7`
  - `valid_metrics = 7`
  - `staging_status = READY`
  - `promote_status = NO_OP`
  - `final_row_exists = true`

### DATA HYGIENE
- `CIGLI_HOSP / 2026-04-06` staging içinde bulunan kirli test kaydı temizlendi:
  - `metric_code = energy_kwh`
  - `source_system = manual_test`
  - `validation_status = PENDING`
- Bu temizlik sonrası staging görünümü üç facility için de `7 / 7 / READY` seviyesine geldi

### CURRENT DECISION
- Orchestrator v1 tek facility ile sınırlı bir demo script olmaktan çıktı
- Yaşayan production omurgası üzerinde multi-facility doğrulanmış çekirdek haline geldi
- Bir sonraki odak:
  1. ayrı multi-facility runner tasarımı
  2. orchestration service layer
  3. KPI evaluation + routing + AI commentary contract


## CHECKPOINT — Multi-Facility Orchestration v1 (2026-04-06)

STATUS: STABLE CORE SYSTEM

- Multi-facility orchestrator aktif
- KPI evaluator deterministic severity (LOW/MEDIUM/HIGH/MISSING)
- Trend-aware değerlendirme aktif
- Routing decision layer gerçek karar üretiyor (ESCALATE/REVIEW/NO_ACTION)
- AI commentary explainable ve KPI bazlı
- Facility naming single source of truth → orchestration.details.facility_name

SYSTEM TYPE:
→ KPI-aware orchestration + decision engine (ML-ready)

NEXT STEP:
→ Action Layer (alerts / tasks / notifications)


## 2026-04-06 — ACTION LAYER CHECKPOINT

### VERIFIED
- Action Layer faz 1 tamamlandı
- `services/action_dispatcher.py` oluşturuldu
- deterministic action contract üretimi aktif
- desteklenen routing kararları:
  - `ESCALATE`
  - `REVIEW`
  - `NO_ACTION`
- action output yapısı:
  - `primary_action`
  - `action_count`
  - `requires_followup`
  - `dispatch_mode=DRY_RUN`
  - `actions[]`
  - `log_payload`
- gerçek dış dispatch yok:
  - mail yok
  - slack yok
  - webhook yok
- action contract yanlışlıkla subprocess wrapper seviyesine bağlandı, sonra geri alındı
- doğru birleşim noktası `scripts/run_multi_facility_orchestrator.py` olarak sabitlendi
- final orchestration payload artık şu katmanları birlikte üretiyor:
  - `kpi_evaluation`
  - `routing_decision`
  - `routing_contract`
  - `ai_commentary`
  - `action_contract`

### LIVE VALIDATION
- test facility: `CIGLI_HOSP`
- doğrulanan çıktı:
  - `facility_name = Demo Hospital Çiğli Hastanesi`
  - `routing_decision = ESCALATE`
  - `action_primary = incident_create`
  - `action_count = 4`

### ARCHITECTURE DECISION
- `services/orchestrator_runner.py` sadece subprocess wrapper olarak kalacak
- action contract üretimi orchestration composer katmanında yapılacak
- Action Layer karar üretmez; routing kararını operasyonel aksiyon kontratına çevirir

### NEXT
1. final payload için API response contract netleştir
2. action contract log/audit persistence tasarla
3. DRY_RUN → future dispatcher adapter arayüzünü tanımla


## 2026-04-06 — API ORCHESTRATION FINAL ENDPOINT CHECKPOINT

### VERIFIED
- yeni endpoint eklendi: `/api/orchestration/final`
- eski `/api/orchestration/summary` endpoint'ine dokunulmadı
- yeni endpoint orchestration composer zincirini API katmanına taşıyor:
  - `run_facility_orchestrator`
  - `evaluate_facility_kpis`
  - `decide_service_route`
  - `build_ai_commentary_contract`
  - `build_action_contract`
- response contract alanları:
  - `facility_code`
  - `facility_name`
  - `report_date`
  - `kpi_evaluation`
  - `routing_decision`
  - `routing_contract`
  - `ai_commentary`
  - `action_contract`
  - `meta.contract_version = orchestration_final_v1`

### LIVE VALIDATION
- endpoint fonksiyon testi doğrudan Python üzerinden doğrulandı
- test facility: `CIGLI_HOSP`
- doğrulanan çıktı:
  - `facility_name = Demo Hospital Çiğli Hastanesi`
  - `report_date = 2026-04-06`
  - `routing_decision = ESCALATE`
  - `action_primary = incident_create`
  - `action_count = 4`
  - `meta.contract_version = orchestration_final_v1`

### ARCHITECTURE DECISION
- API v2/final contract ayrı endpoint olarak açıldı
- mevcut v1 summary endpoint korunuyor
- frontend geçişi kontrollü yapılacak; önce yeni endpoint sabitlenecek, sonra UI tüketimi bağlanacak

### NEXT
1. frontend hangi ekranda bu endpoint'i kullanacak netleştir
2. static/app.js veya ilgili UI dosyasında fetch zincirini yeni endpoint'e bağla
3. routing / AI / action kartlarını frontend'de görünür hale getir


## 2026-04-06 — FRONTEND ORCHESTRATION FINAL INTEGRATION CHECKPOINT

### VERIFIED
- Frontend orchestration entegrasyonu `static/index.html` ve `static/app.js` üzerinden yapıldı
- `static/index.html` içine yeni görünür orchestration blokları eklendi:
  - `routingDecision`
  - `routingContract`
  - `actionContract`
- `static/app.js` içinde `els` map’i yeni orchestration alanları ile genişletildi
- `loadAll()` artık `/api/ai/summary` yerine `/api/orchestration/final` çağrıyor
- `loadAll()` halen `/api/dashboard/latest` ve `/api/dashboard/daily` kaynaklarını koruyor
- Yeni render fonksiyonları eklendi:
  - `renderRoutingDecision(final)`
  - `renderRoutingContract(final)`
  - `renderActionContract(final)`
- `renderAISummary()` ve `renderPersonas()` gerçek `ai_commentary` contract’ine göre yeniden hizalandı
- Canlı contract doğrulandı:
  - `routing_decision = ESCALATE`
  - `ai_commentary` alanları: `highlights`, `kpi_summary`, `orchestration_status`, `routing_decision`, `facility_code`, `facility_name`, `report_date`
  - `action_contract` alanları: `primary_action`, `action_count`, `actions`, `overall_status`, `routing_decision`, vb.
  - `routing_contract` alanları: `decision`, `facility_code`, `reason_codes`
- `node --check static/app.js` temiz geçti

### CURRENT FRONTEND DATA FLOW
- Decision / AI / Action layer:
  - `/api/orchestration/final`
- KPI / executive score layer:
  - `/api/dashboard/latest`
- Trend / chart / table layer:
  - `/api/dashboard/daily`

### IMPORTANT
- Frontend artık eski `/api/ai/summary` bağımlılığından çıkarıldı
- `/api/orchestration/summary` endpoint’i backend’de korunuyor ancak frontend ana akışında kullanılmıyor
- Bu checkpoint sonrası yapılacak doğru sonraki adım:
  1. Browser runtime doğrulaması
  2. UI kart içeriklerinin görsel iyileştirmesi
  3. Gerekirse legacy `/api/ai/summary` kullanımının tamamen emekliye ayrılması


## 2026-04-07 — VERIFIED BOOTSTRAP LAYER CHECKPOINT

### SCOPE
`dashboard_rows = 0` olan facility'ler için canonical 7 KPI bootstrap verisi üretip staging -> readiness -> promote -> dashboard verify akışına sokan Bootstrap Layer tamamlandı.

### IMPLEMENTED
- `scripts/bootstrap_zero_facilities.py` genişletildi
- Profile resolver eklendi:
  - `facility_type`
  - `gross_area_m2`
  - `bed_count`
  bazlı bootstrap profile çözümleme aktif
- Metric generation contract eklendi:
  - electricity_kwh
  - water_m3
  - medical_waste_kg
  - pathological_waste_kg
  - general_waste_kg
  - scope2_location_tco2e
  - waste_cost_try
- Derived rules aktif:
  - `scope2_location_tco2e = electricity_kwh * 0.000460`
  - `waste_cost_try = total_waste_kg * 43.3255`
- Staging payload builder eklendi
- Real schema uyumlu staging insert eklendi
- Readiness check eklendi:
  - `zerocare_operational.v_staging_daily_metrics_status`
- Promote eklendi:
  - `zerocare_operational.run_promote_with_audit(...)`
- Final production verify eklendi:
  - `zerocare_operational.vw_dashboard_daily`
- JSON summary output eklendi

### REAL DB ALIGNMENTS
Bootstrap write logic aşağıdaki gerçek staging şemasına hizalandı:
- `source` = `synthetic`
- `source_system` = `bootstrap_seed`
- `raw_unit`, `metric_unit`, `normalized_unit` alanları kullanıldı
- `metric_value`, `normalized_value`, `raw_payload`, `payload_hash`, `fingerprint`, `batch_id` üretildi
- `psycopg.connect(..., prepare_threshold=None)` kullanıldı
  - sebep: `DuplicatePreparedStatement` hatası

### VERIFIED RESULT
Test facility:
- `MENEMEN_HOSP`
- `facility_type = hospital`
- `bed_count = 120`
- `gross_area_m2 = 18000`

Verified outcome:
- `write_result.status = OK`
- `inserted_rows = 7`
- `readiness.status = OK`
- `readiness.ready = true`
- `staging_status = READY`
- `promote_result.status = OK`
- `promote_status = SUCCESS`
- `written_rows = 7`
- `dashboard_verify.status = OK`
- `present_metric_count = 7`

### GENERATED VERIFIED VALUES
- `electricity_kwh = 3120.0`
- `water_m3 = 108.0`
- `medical_waste_kg = 420.0`
- `pathological_waste_kg = 54.6`
- `general_waste_kg = 798.0`
- `scope2_location_tco2e = 1.435`
- `waste_cost_try = 55136.031`

### IMPORTANT
Bootstrap Layer artık sadece discovery değil, production omurgasına veri sokan verified executable flow durumunda.

### NEXT
1. Kalan zero-dashboard facility'ler için batch bootstrap çalıştır
2. Script'e `--all-zero-facilities` veya benzeri batch mode ekle
3. Bootstrap yapılan facility'leri tekrar seed etmemek için toplu NOOP davranışını doğrula
4. UI tarafında yeni facility coverage'ı kontrol et
5. Sonraki adımda bootstrap sonrası orchestration / AI layer coverage genişlet

## 2026-04-07 — VERIFIED BOOTSTRAP LAYER BATCH MODE CHECKPOINT

### VERIFIED
- `scripts/bootstrap_zero_facilities_batch.py` oluşturuldu
- Batch mode discovery doğrulandı:
  - seçim kuralı: `vw_dashboard_daily` içinde `dashboard_rows = 0` olan facility'ler
- Batch orchestrator, verified tek-facility script olan `scripts/bootstrap_zero_facilities.py` üstünden çalışacak şekilde tasarlandı
- Tek-facility motor korunarak dış kabuk batch orchestration modeli benimsendi
- CLI forwarding düzeltildi:
  - `--facility-type`
  - `--gross-area-m2`
  - `--bed-count`
  - `--facility-name`
- `gross_area_m2` için CLI int normalization düzeltildi
- `promote_result.promote_status` parse düzeltildi
- `NOOP_ALREADY_BOOTSTRAPPED` durumu batch classifier içinde doğru şekilde `NOOP` olarak işaretleniyor
- Idempotent davranış doğrulandı:
  - `BALCOVA_MED` ikinci çalıştırmada `NOOP_ALREADY_BOOTSTRAPPED`
  - `promote_status = NO_OP`
  - `dashboard_verify_status = OK`

### VERIFIED BATCH RUN
- `--all-zero-facilities --continue-on-error` ile gerçek batch run çalıştırıldı
- Batch sonucu:
  - `selected_facility_count = 3`
  - `processed_facility_count = 3`
  - `success_count = 3`
  - `failed_count = 0`
- Başarıyla bootstrap edilen facility'ler:
  - `CIGLI_MED`
  - `DENTAL_CENTER`
  - `EYE_CENTER`

### VERIFIED KPI COVERAGE
Her yeni facility için aşağıdakiler doğrulandı:
- `inserted_rows = 7`
- `readiness_ready = true`
- `staging_status = READY`
- `promote_status = SUCCESS`
- `dashboard_verify_status = OK`
- `present_metric_count = 7`

### VERIFIED UI COVERAGE
`zerocare_operational.vw_dashboard_daily` üzerinde aşağıdaki facility'lerin görünürlüğü doğrulandı:
- `BALCOVA_MED`
- `CIGLI_MED`
- `DENTAL_CENTER`
- `EYE_CENTER`
- `MENEMEN_HOSP`

### CURRENT DECISION
- Bootstrap Layer artık tekil test script’i seviyesinden çıktı
- Batch mode ile zero-coverage facility bootstrap akışı verified hale geldi
- Sonraki mantıklı faz:
  1. batch run için opsiyonel `--pretty` / kısa çıktı ayrımı
  2. batch discovery ve sonuçlarını API veya admin endpoint’e taşıma
  3. frontend facility coverage / dropdown verify

## 2026-04-07 — VERIFIED FRONTEND FACILITY COVERAGE + ORCHESTRATION DATE PROPAGATION CHECKPOINT

### VERIFIED FRONTEND COVERAGE
- `static/index.html` içindeki `#facilitySelect` dropdown aktif kaynak olarak doğrulandı
- `static/app.js` içinde dropdown veri kaynağı `/api/facilities` olarak doğrulandı
- Dropdown datasource testi geçti:
  - `BALCOVA_MED`
  - `CIGLI_MED`
  - `DENTAL_CENTER`
  - `EYE_CENTER`
  - `MENEMEN_HOSP`
  frontend facility listesinde görünür durumda

### VERIFIED FACILITY SELECTION FLOW
`DENTAL_CENTER` ile uçtan uca seçim testi yapıldı:
- `/api/dashboard/latest?facility_code=DENTAL_CENTER` doğru facility verisi döndü
- `/api/dashboard/daily?facility_code=DENTAL_CENTER&days=14` doğru facility verisi döndü
- frontend selection zincirinin dashboard data ayağı verified

### ORCHESTRATION PAYLOAD FINDING
İlk kontrolde `/api/orchestration/final` payload’ında alanların camelCase değil snake_case olduğu doğrulandı:
- doğru alanlar:
  - `routing_decision`
  - `routing_contract`
  - `action_contract`
- ilk False kontrolü backend eksikliği değil, yanlış field adı varsayımı kaynaklıydı

### ROOT CAUSE — DATE PROPAGATION BUG
Yeni bootstrap edilen facility’lerde orchestration error nedeni teşhis edildi:
- `/api/orchestration/final` içinde `final_report_date` hesaplanıyordu
- fakat `run_facility_orchestrator(...)` çağrısına tarih aktarılmıyordu
- `services/orchestrator_runner.py` sadece `FACILITY_CODE` env geçiriyordu
- alt script `scripts/generate_validate_promote_synthetic.py` ise `TARGET_DATE` env destekliyordu
- sonuç olarak orchestration katmanı eski/default target_date ile çalışıyordu

### FIX APPLIED
- `services/orchestrator_runner.py`
  - imza güncellendi:
    - `run_facility_orchestrator(facility_code, target_date=None)`
  - `TARGET_DATE` env forwarding eklendi
- `server.py`
  - `run_facility_orchestrator(facility_key, final_report_date)` şeklinde çağrı düzeltildi

### VERIFIED AFTER FIX
`DENTAL_CENTER` için `/api/orchestration/final` tekrar doğrulandı:
- `facility_name = Demo Hospital Ağız ve Diş Sağlığı Merkezi`
- `orchestrator_status = OK`
- `generate_status = NOOP: up-to-date`
- `staging_status = READY`
- `promote_status = NO_OP`
- `final_row_exists = True`
- `routing_contract = True`
- `action_contract = True`
- `details_target_date = 2026-04-07`

### SERVER HYGIENE
- `server.py` process aktif doğrulandı
- `127.0.0.1:8050` listen doğrulandı
- `/health` endpoint sonucu:
  - `status = ok`
  - `db = connected`

### CURRENT DECISION
- Bootstrap Layer batch mode + frontend facility selection + orchestration coverage zinciri verified
- Bu faz kapanmıştır
- Sonraki mantıklı faz:
  1. dropdown / UI davranışını tarayıcıdan manuel smoke test ile son kez görmek
  2. orchestration coverage’ı diğer yeni bootstrap facility’lerde (`CIGLI_MED`, `EYE_CENTER`, `BALCOVA_MED`) toplu doğrulamak
  3. gerekirse admin/API raporlama katmanı eklemek

## 2026-04-07 — VERIFIED 9/9 FACILITY ORCHESTRATION FINAL SMOKE TEST CHECKPOINT

### VERIFIED SCOPE
Aşağıdaki 9 facility için `/api/orchestration/final` uçtan uca smoke test çalıştırıldı:
- `BALCOVA_MED`
- `CIGLI_HOSP`
- `CIGLI_MED`
- `DEMO_BORNOVA`
- `DEMO_KONAK`
- `DEMO_KSK`
- `DENTAL_CENTER`
- `EYE_CENTER`
- `MENEMEN_HOSP`

### VERIFIED RESULT
Tüm 9 facility için aşağıdakiler doğrulandı:
- `orchestrator_status = OK`
- `staging_status = READY`
- `final_row_exists = True`
- `routing_contract = True`
- `action_contract = True`
- `details_target_date = 2026-04-07`

### OBSERVED EXECUTION MODES
İki normal çalışma modu gözlendi:

1. Up-to-date / idempotent facility'ler
- `generate_status = NOOP: up-to-date`
- `promote_status = NO_OP`

2. Gün içinde veri üreten / promote eden facility'ler
- `generate_status = OK`
- `promote_status = SUCCESS`

Bu fark hata değildir; orchestrator aynı gün bağlamında bazı facility’lerde mevcut veriyi yeniden kullanmış, bazılarında yeni üretim/promote akışını çalıştırmıştır.

### CURRENT DECISION
- Frontend dropdown coverage verified
- facility selection verified
- orchestration final verified
- date propagation bug fixed
- tüm 9 facility için orchestration smoke test geçti

Bu faz production-ready demo doğrulama seviyesiyle kapanmıştır.


## 2026-04-07 — 30 DAY PRODUCTION COVERAGE BACKFILL COMPLETED

### VERIFIED
- Rolling 30-day production coverage hedefi tamamlandı
- Son 30 gün penceresi: 2026-03-09 → 2026-04-07
- Final gap check sonucu: 0 rows
- Aktif 9 facility için coverage tamamlandı
- Final coverage:
  - BALCOVA_MED = 30
  - CIGLI_HOSP = 31
  - CIGLI_MED = 30
  - DEMO_BORNOVA = 30
  - DEMO_KONAK = 30
  - DEMO_KSK = 30
  - DENTAL_CENTER = 30
  - EYE_CENTER = 30
  - MENEMEN_HOSP = 30

### ROOT CAUSE FOUND
- İlk backfill denemesinde DEMO_* facility’lerde failure oluştu
- Kök neden:
  - `scripts/bootstrap_zero_facilities.py`
  - `normalize_facility_type()`
  - `private_hospital` alias desteği yoktu
- Hata:
  - `unsupported facility_type: 'private_hospital'`

### FIX APPLIED
- `normalize_facility_type()` alias map genişletildi
- Eklenen aliaslar:
  - private_hospital -> hospital
  - public_hospital -> hospital
  - state_hospital -> hospital
  - training_research_hospital -> hospital
  - education_research_hospital -> hospital
  - medical_centre -> medical_center

### NEW SCRIPT
- Yeni batch runner eklendi:
  - `scripts/backfill_30day_zero_facilities.py`
- Amaç:
  - aktif facility listesi
  - rolling 30 calendar day window
  - eksik facility+date çiftlerini bul
  - verified single bootstrap layer ile yalnızca eksikleri tamamla
  - aggregate JSON summary üret

### DECISION
- `bootstrap_zero_facilities.py` verified single-facility canonical layer olarak korundu
- `bootstrap_zero_facilities_batch.py` değiştirilmedi
- 30-day historical completion için ayrı runner yaklaşımı benimsendi

### STATUS
- Production dashboard coverage artık demo-safe
- Dropdown seçilen her facility için son 30 günlük veri görünürlüğü hazır

