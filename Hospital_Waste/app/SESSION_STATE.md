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

