# ZERO@HOSPITAL — PRODUCT NOTES

## Tarih
2026-04-05

## Konu
Clinic Synthetic Generator v1

## Problem
Multi-hospital dashboard çalışıyor; ancak clinic katmanında veri kapsamı eksik olduğunda bazı facility’lerde clinic endpoint’leri boş veya zayıf kalıyor.

## Ürün Kararı
Manuel seed yaklaşımı bırakılıyor.
Yerine behavior-driven, preview-first çalışan bir Synthetic Clinic Generator kuruluyor.

## Kapsam
- 9 facility
- 9 global clinic
- 7 günlük synthetic clinic data
- metric set:
  - electricity_kwh
  - water_m3
  - wastewater_m3
  - medical_waste_kg
  - pathological_waste_kg

## Teknik Karar
Write target:
- `zerocare_operational.daily_metrics`

Storage modeli:
- long-format
- 1 metric = 1 row

Write standardı:
- `quality_flag = synthetic`
- `calculation_method = clinic_behavior_v1`
- `source_system = clinic_synth_v1`

## Guardrails
- preview-first
- validation before insert
- no overwrite
- no update
- only missing rows insert

## Stratejik Rol
Bu katman sadece demo doldurma aracı değil:
- data completeness engine
- clinic simulation layer
- future forecasting / ML foundation

## Sonraki Adım
Preview generator script + controlled insert pipeline.

## 2026-04-05 — Sustainability Intelligence Layer

### Decision
Zero@Hospital içine operational dashboard’dan ayrı bir sustainability intelligence katmanı eklendi.

### Why
Operational KPI tek başına yetmiyor.
Sistem artık hastanenin enerji, su, atık su ve atık performansını:
- WHO Green Hospital direction
- NHS Green Plan direction
- EU Green Deal / Zero Pollution direction
ile hizalayacak.

### Product Principle
- Existing production dashboard untouched
- New DB schema isolated
- Measurable indicators scored
- Non-measurable indicators marked `not_assessed`
- No fake compliance claim

### v1 Scope
- Schema: `zerocare_sustainability`
- Framework/domain/indicator registry
- Facility daily indicator fact table
- Facility framework/domain score table
- Baseline-relative scoring
- Minimal refresh pipeline

### Next Product Step
- Sustainability API
- Executive sustainability cards
- Domain drilldown
- Gap map: assessed vs not_assessed


## 2026-04-05 — Sustainability Scoring Engine Phase 2

Bu fazda Zero@Hospital için gerçek indicator-bazlı scoring engine doğrulandı.

### Tamamlananlar
- Threshold mantığı kod içinden çıkarılıp DB’ye taşındı
- `GREEN_HOSPITAL` framework yapısı oluşturuldu
- Indicator threshold seed kayıtları eklendi:
  - energy_kwh_per_patient
  - water_m3_per_patient
  - waste_kg_per_patient
- Dynamic status mantığı aktif:
  - good / monitor / bad
- Weighted total score mantığı aktif
- Risk katmanı aktif:
  - LOW / MEDIUM / HIGH / CRITICAL
- Engine DB’den threshold okuyarak test edildi ve doğrulandı

### Stratejik Anlamı
Bu adım ile ürün klasik KPI dashboard seviyesinden çıkıp karar destek motoruna geçti.
Artık skorlar:
- açıklanabilir
- yönetilebilir
- framework bazlı genişletilebilir
- facility / department override destekleyecek yapıya uygun

### Sonraki Ürün Adımı
Bir sonraki aşamada bu scoring katmanı API response içine taşınacak ve dashboard kartlarında canlı gösterilecek.


## 2026-04-05 — API-Level Sustainability Scoring Live

Sustainability scoring engine artık yalnızca izole test değil, canlı dashboard API response’una bağlandı.

### Bu Fazda Doğrulananlar
- `/api/dashboard/latest` artık `sustainability_scoring` alanı döndürüyor
- Scoring hesaplaması DB threshold + framework mantığıyla çalışıyor
- İlk aktif mod: `per_bed`
- `CIGLI_HOSP` için canlı test doğrulandı

### Canlı Test Sonucu
- Energy intensity yüksek bulundu:
  - `50.4 kWh/bed`
  - status: `bad`
- Water ve waste intensity iyi bantta
- Total score:
  - `55.61`
- Risk:
  - `HIGH`

### Ürün Anlamı
Bu aşamayla birlikte ürün ham KPI ekranı olmaktan çıkıp yorum yapan karar destek katmanına geçti.
Artık API seviyesi şu soruya cevap veriyor:
- “Hastane sürdürülebilirlik açısından şu an ne durumda ve ana problem nerede?”

### Sonraki Ürün Adımı
Bir sonraki aşamada bu veriden executive-friendly özet üretilecek:
- top issue
- quick action
- score summary
- role-based interpretation (CEO / CFO / CTO / Başhekim)


## 2026-04-05 — PRODUCT CHECKPOINT — DAILY CO2 BACKFILL DIAGNOSIS

### Current Product Reality
Production dashboard genel olarak stabil:
- multi-hospital backend aktif
- daily/latest veri akışı çalışıyor
- scoring + executive summary aktif
- KPI / trend / tablo / null handling doğru
- UI tarafı bugünkü CO₂ değerini doğru gösteriyor

### Confirmed Problem
Geçmiş günlerde CO₂ görünmeme sebebi frontend değil.
Kritik problem:
- `scope2_location_tco2e` sadece bugünde dolu
- geçmiş günlerde `null`
- bu nedenle tabloda yalnızca bugünde CO₂ görünüyor

### Technical Decision
Öncelik sırası:
1. `/api/dashboard/daily` endpoint inceleme
2. `vw_dashboard_daily` view inceleme
3. CO₂ türetim SQL zinciri inceleme
4. hangi join / aggregate / derivation katmanında null oluştuğunu bulma
5. yalnızca gerekirse kontrollü fallback ekleme

### Guardrails
- `latest` endpoint davranışı korunacak
- scoring engine korunacak
- frontend hesap mantığı korunacak
- fallback eklenirse yalnızca geçmiş günler için ve kontrollü olacak
- teşhis tamamlanmadan patch yapılmayacak

### Next Execution Focus
İlk teknik hedef:
- backend içinde `scope2_location_tco2e` alanının hangi kaynak kolondan geldiğini bulmak
- view ve endpoint zincirinde null kırılımını netleştirmek


## 2026-04-05 — PRODUCT CHECKPOINT — BAZEKOL IDENTITY REMOVAL

### What Changed
System-wide active Bazekol hardcodes were removed from runtime code.

### Why This Matters
The platform was behaving like a multi-hospital dashboard on the surface, but critical generators and clinic endpoints were still bound to a single historical customer identity. This created a silent architecture conflict.

### Resolved
- Generators are no longer defaulting to Bazekol
- Facility context must now be provided explicitly
- Clinic endpoints no longer force Bazekol data
- Active runtime code is now tenant-neutral / facility-aware

### Product Impact
This is a foundational cleanup step for turning the system from a client-specific demo artifact into a reusable hospital sustainability product.

### Next Product Step
Run orchestration for the Demo Hospital facility set and ensure the generated operational data flows into the dashboard path cleanly.

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


## STAGING → CANONICAL DATA LAYER DECISION

System artık raw veri değil, **validated & versioned canonical intake layer** üzerinden ilerler.

Staging katmanı:
- immutable değil, versioned
- duplicate-aware (fingerprint)
- lineage-aware (supersede)
- KPI completeness-aware (READY / PARTIAL)

Bu katman, tüm AI / KPI / dashboard logic’inin upstream kaynağıdır.

Bir sonraki faz:
→ "PROMOTE LAYER" (operational truth creation)


## 2026-04-06 — Production Promote Workflow Live

Zero@Hospital orchestration katmanında production-grade promote akışı canlı doğrulandı.

### Live capabilities
- n8n orchestration
- daily 06:00 cron trigger
- manual webhook trigger
- Postgres-backed promote execution
- per-run audit trail
- idempotent promote behavior

### Proven execution states
- DRY_RUN
- NO_OP
- SUCCESS

### Product meaning
The orchestration layer is no longer a placeholder. It is now a real operational promote engine with traceability, controlled execution, and duplicate-safe behavior.

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

## 2026-04-06 — GENERATE_VALIDATE_PROMOTE_SYNTHETIC REWRITE + LEGACY CLEANUP CHECKPOINT

### VERIFIED
- `daily_live_generator_v3` yaşayan production omurgasında iki facility için uçtan uca doğrulandı:
  - `DEMO_KONAK`
  - `DEMO_BORNOVA`
- Doğrulanan yaşayan hat:
  `vw_dashboard_daily -> staging_daily_metrics -> v_staging_daily_metrics_status -> run_promote_with_audit -> vw_dashboard_daily`
- `generate_validate_promote_synthetic.py` incelendi ve mimari olarak legacy / parallel pipeline taşıdığı doğrulandı
- Legacy bağımlılıklar eski sürümde tespit edildi:
  - `public.core_metric_readings`
  - `public.synthetic_metric_readings_staging`
  - `public.synthetic_validation_results`

### DECISION
- `scripts/generate_validate_promote_synthetic.py` patch edilerek kurtarılmayacak
- Dosya baştan rewrite edilecek
- Yeni sürüm yalnız yaşayan production omurgasına bağlanacak
- Yeni sürüm yalnız yaşayan 7 KPI setini üretecek:
  - `electricity_kwh`
  - `water_m3`
  - `medical_waste_kg`
  - `pathological_waste_kg`
  - `general_waste_kg`
  - `scope2_location_tco2e`
  - `waste_cost_try`

### REWRITE CONTRACT
- Legacy tablolar runtime dependency olarak kullanılmayacak:
  - `public.core_metric_readings`
  - `public.synthetic_metric_readings_staging`
  - `public.synthetic_validation_results`
- Yeni script rolü:
  `generate -> stage -> readiness check -> promote -> verify`
- Multi-facility çalışabilecek
- JSON çıktı verecek
- Idempotent olacak
- Validation kuralının sahibi script değil, yaşayan sistem olacak:
  `v_staging_daily_metrics_status`
- Promote yalnız resmi function ile yapılacak:
  `run_promote_with_audit(...)`

### LEGACY CLEANUP
- Repo içi legacy referans taraması yapıldı
- Aktif yeni scriptte legacy runtime dependency bulunmadı
- `sql/01_create_synthetic_engine.sql` incelendi
- Bu dosyanın yalnız aşağıdaki legacy tabloları oluşturduğu doğrulandı:
  - `public.synthetic_metric_readings_staging`
  - `public.synthetic_validation_results`
- Trigger / function / scheduler / view içermediği doğrulandı
- Risk tipi runtime değil, yanlışlıkla yeniden aktive edilme riski olarak sınıflandırıldı

### ACTION
- `sql/01_create_synthetic_engine.sql` aktif SQL klasöründen çıkarıldı
- Yeni konum:
  `archive/legacy/01_create_synthetic_engine.sql`
- Böylece production SQL klasöründe yalnız yaşayan omurgaya ait DDL/migration dosyaları bırakıldı

### ARCHITECTURAL NOTE
- Yeni orchestration runner legacy’ye runtime dependency taşımayacak
- Ancak legacy dünya tamamen kör noktaya atılmayacak
- Gerekirse read-only / preflight audit görünürlüğü korunacak
- Ama production run kararları yalnız yaşayan omurga üzerinden verilecek

### NEXT
1. Yeni `generate_validate_promote_synthetic.py` için tek facility smoke test planını netleştir
2. Kontrollü smoke test çalıştır
3. Gerekirse preflight legacy audit alanını yeni script çıktısına ekle
4. Sonra günlük orchestration / scheduling kararını ver:
   - n8n
   - Python scheduler

## 2026-04-06 — Orchestrator v1 kararı

### Alınan karar
`generate_validate_promote_synthetic.py` dosyası baştan yazıldı ve pure orchestrator rolüne indirildi.

### Neyi çözüyor
- Synthetic üretim akışını yaşayan production omurgasına bağlar
- Validate + promote + verify zincirini tek giriş noktasında toplar
- JSON özet çıktısı ile n8n ve API orchestration katmanına hazır hale gelir

### Bağlı olduğu yaşayan hat
- `daily_live_generator.py`
- `zerocare_operational.v_staging_daily_metrics_status`
- `zerocare_operational.run_promote_with_audit`
- `zerocare_operational.vw_dashboard_daily`

### Özellikle kaldırılanlar
- Legacy synthetic engine runtime dependency
- Staging manipülasyonu
- Deactivate / override tipi yan etkiler
- Script içinde yeniden metric üretme mantığı

### Doğrulama
`DEMO_KONAK / 2026-04-06` için smoke test başarıyla geçti:
- generate = `NOOP: up-to-date`
- staging = `READY`
- metrics = `7/7`
- promote = `NO_OP`
- final dashboard verify = `OK`

### Sonraki ürün seviyesi adım
- multi-facility smoke test
- orchestration service layer
- KPI evaluation + routing + AI commentary contract


## 2026-04-06 — MULTI-FACILITY ORCHESTRATION PLAN KİLİDİ

### CONTEXT
Doğrulanmış yaşayan hat:
`daily_live_generator.py -> v_staging_daily_metrics_status -> run_promote_with_audit -> vw_dashboard_daily`

Doğrulanmış durum:
- `scripts/generate_validate_promote_synthetic.py` pure orchestrator olarak rewrite edildi
- tek facility smoke test geçti
- multi-facility smoke test geçti (`CIGLI_HOSP`, `DEMO_BORNOVA`, `DEMO_KONAK`)
- `CIGLI_HOSP` içindeki kirli `energy_kwh / manual_test` staging kaydı temizlendi
- üç facility için staging görünümü `7 / 7 / READY`
- tüm testlerde orchestrator sonucu `status=OK`, `promote_status=NO_OP`, `final_row_exists=true`

### ARCHITECTURE DECISION
Yeni yapı tek script içinde şişirilmeyecek.

Katmanlı tasarım:
1. `run_multi_facility_orchestrator.py` -> entrypoint / coordinator
2. service layer
3. KPI evaluation
4. routing decision
5. AI commentary contract

Temel karar:
- script sadece orchestration başlatacak
- asıl iş mantığı service layer içinde yaşayacak
- tek ve standart JSON output contract üretilecek
- aynı contract CLI + API + n8n + dashboard + AI layer tarafından kullanılacak

### TARGET COMPONENTS

#### 1. `scripts/run_multi_facility_orchestrator.py`
Sorumluluk:
- facility listesini almak
- her facility için mevcut pure orchestrator akışını çalıştırmak
- sonuçları toplamak
- KPI evaluation + routing + AI commentary contract oluşturmak
- final aggregate JSON üretmek

Kural:
- business logic burada birikmeyecek
- bu dosya koordinasyon katmanı olacak

#### 2. `services/facility_registry.py`
Sorumluluk:
- aktif facility listesini almak
- tek / çoklu facility çözümlemek
- ileride `enabled_for_orchestration`, `tier`, `region`, `facility_type` gibi alanları desteklemek

Örnek fonksiyonlar:
- `get_active_facilities()`
- `get_facility_context(facility_code)`
- `resolve_requested_facilities(args)`

#### 3. `services/orchestrator_runner.py`
Sorumluluk:
- her facility için mevcut doğrulanmış hattı çalıştırmak
- orchestrator sonucunu normalize etmek

Beklenen normalize çıktı örneği:
```json
{
  "facility_code": "CIGLI_HOSP",
  "orchestrator_status": "OK",
  "generate_status": "NOOP: up-to-date",
  "staging_status": "READY",
  "promote_status": "NO_OP",
  "final_row_exists": true
}


## UPDATE — Decision Engine Layer

System artık sadece veri pipeline değil:
→ KPI-aware decision engine haline geldi

Core components:
- Orchestration Engine
- KPI Evaluation Engine
- Routing Decision Engine
- Explainable AI Commentary

Key capability:
→ System detects, evaluates and explains operational risk

Positioning:
→ "Operating System for Sustainable Hospital Operations"

Next milestone:
→ Action Layer (automated response system)


## 2026-04-06 — Action Layer Faz 1 tamamlandı

Bugün Zero@Hospital orchestration mimarisinde Action Layer ilk fazı canlı olarak bağlandı.

### Karar
Action Layer, routing kararını üreten katman olmayacak.
Karar üretimi ayrı kalacak:
- KPI evaluation
- routing decision
- AI commentary

Yeni katman sadece bu kararı standart operasyonel aksiyon kontratına çevirecek.

### Uygulanan Mimari
`services/action_dispatcher.py` ile deterministic action contract üretimi kuruldu.

Desteklenen kararlar:
- ESCALATE
- REVIEW
- NO_ACTION

Üretilen kontrat bileşenleri:
- primary_action
- requires_followup
- action_count
- actions listesi
- log_payload
- dispatch_mode = DRY_RUN

### Kritik Mimari Düzeltme
İlk denemede action layer yanlışlıkla subprocess wrapper seviyesine bağlandı.
Bu yaklaşım geri alındı.
Doğru birleşim noktası `scripts/run_multi_facility_orchestrator.py` olarak sabitlendi.

Bu sayede final orchestration JSON artık tek payload içinde şunları taşıyor:
- operational orchestration sonucu
- kpi_evaluation
- routing_decision
- routing_contract
- ai_commentary
- action_contract

### Canlı Doğrulama
CIGLI_HOSP üzerinde doğrulandı:

- facility_name = Demo Hospital Çiğli Hastanesi
- routing_decision = ESCALATE
- action_primary = incident_create
- action_count = 4

### Not
Bu fazda gerçek dispatch yoktur.
Mail / Slack / webhook entegrasyonu özellikle devreye alınmadı.
Sistem önce explainable + loggable contract üretir.
Gerçek dispatch bir sonraki fazın işidir.


## 2026-04-06 — API Final Orchestration Endpoint hazır

Bugün Action Layer sonrası orchestration composer çıktısı API katmanına taşındı.

### Karar
Eski orchestration summary endpoint'i bozulmadı.
Yeni contract için ayrı bir endpoint açıldı:

- `/api/orchestration/final`

Bu yaklaşım bilinçli seçildi.
Amaç, çalışan v1 akışı bozmadan yeni orchestration payload'ını frontend-ready şekilde sunmak.

### Yeni API Contract
Yeni endpoint artık tek payload içinde şunları döndürüyor:
- facility_code
- facility_name
- report_date
- kpi_evaluation
- routing_decision
- routing_contract
- ai_commentary
- action_contract
- meta.contract_version = orchestration_final_v1

### İç Zincir
Endpoint içinde kullanılan orchestration sırası:
- run_facility_orchestrator
- evaluate_facility_kpis
- decide_service_route
- build_ai_commentary_contract
- build_action_contract

### Canlı Doğrulama
CIGLI_HOSP ile doğrulandı:

- facility_name = Demo Hospital Çiğli Hastanesi
- report_date = 2026-04-06
- routing_decision = ESCALATE
- action_primary = incident_create
- action_count = 4
- meta.contract_version = orchestration_final_v1

### Not
Bu aşamada backend contract hazırdır.
Bir sonraki faz frontend tüketimi ve kart/alan eşlemesidir.
Önce backend contract sabitlenmiş oldu.


## 2026-04-06 — PRODUCT DECISION: FRONTEND ORCHESTRATION FINAL CONTRACT

### Decision
Zero@Hospital executive frontend için ana karar katmanı artık `/api/orchestration/final` contract’idir.

### Why
Önceki yapı AI yorumunu ayrı endpoint (`/api/ai/summary`) üzerinden alıyordu ve karar zinciri UI tarafında parçalıydı.
Bu yaklaşım:
- routing kararını görünmez bırakıyordu
- action contract’i UI’da göstermiyordu
- AI / routing / action akışını tek sözleşmede toplamıyordu

Yeni ürün kararıyla frontend şu prensibe geçti:

- **Decision layer** → `/api/orchestration/final`
- **Operational KPI layer** → `/api/dashboard/latest`
- **Trend / history layer** → `/api/dashboard/daily`

### Product Impact
Frontend artık yalnızca “yorum gösteren dashboard” değil,
**routing + action + executive insight** üreten bir yönetim paneli haline geldi.

### Visible UI Changes
Yeni görünür alanlar:
- Routing Decision
- Routing Contract
- Action Contract

### Technical Product Rule
Frontend tarafında eski `/api/ai/summary` bağımlılığı artık ana akıştan çıkarılmıştır.
Gelecekte AI commentary ayrı endpoint olarak korunabilir, ancak executive UI’nın birincil contract’i değildir.

### Contract Principle
Tek executive karar zinciri şu alanları birlikte taşımalıdır:
- `kpi_evaluation`
- `routing_decision`
- `routing_contract`
- `ai_commentary`
- `action_contract`

Bu ilke bundan sonraki frontend ve orchestration geliştirmelerinde korunacaktır.


## 2026-04-07 — Bootstrap Layer v1 doğrulandı

### Problem
Sistemde `/api/facilities` tarafında aktif facility seti doğru görünse de bazı facility'lerde `vw_dashboard_daily` coverage = 0 idi. Bu nedenle frontend seçim yapılınca boş facility'lerde veri görünmüyor, orchestration katmanı da bu facility'ler için çalışabilir veri tabanı bulamıyordu.

Zero coverage facility seti:
- BALCOVA_MED
- CIGLI_MED
- DENTAL_CENTER
- EYE_CENTER
- MENEMEN_HOSP

### Ürün Kararı
Bu boş facility'ler için manuel veri beklemek yerine kontrollü bir **Bootstrap Layer** eklendi.

Amaç:
- `dashboard_rows = 0` olan facility'ler için 1 günlük canonical 7 KPI üretmek
- bu veriyi production omurgasına sokmak
- facility coverage'ı hızlıca ayağa kaldırmak
- orchestration / routing / AI layer için boş facility problemini kapatmak

### Canonical KPI Seti
- electricity_kwh
- water_m3
- medical_waste_kg
- pathological_waste_kg
- general_waste_kg
- scope2_location_tco2e
- waste_cost_try

### Derived Kurallar
- `scope2_location_tco2e = electricity_kwh * 0.000460`
- `waste_cost_try = total_waste_kg * 43.3255`

### Tasarım Kararı
Bootstrap üretimi discovery script’i üzerine inşa edildi:
- dosya: `scripts/bootstrap_zero_facilities.py`

Script artık şu tam akışı çalıştırıyor:
1. facility profile resolver
2. metric generation contract
3. staging payload builder
4. real-schema insert
5. readiness check
6. promote
7. dashboard verify
8. JSON summary output

### Profil Mantığı
Bootstrap verisi sabit hardcode sayıdan değil, facility metadata’dan türetiliyor:
- `facility_type`
- `gross_area_m2`
- `bed_count`

Desteklenen profile tipleri:
- hospital
- medical_center
- dental_center
- eye_center

### Teknik Kararlar
Gerçek staging şemasına hizalama yapıldı:
- `source = 'synthetic'`
- `source_system = 'bootstrap_seed'`
- `raw_unit`, `metric_unit`, `normalized_unit` kullanıldı
- `metric_value`, `normalized_value`, `raw_payload`, `payload_hash`, `fingerprint`, `batch_id` üretildi

Ayrıca:
- `psycopg.connect(..., prepare_threshold=None)` kullanıldı
- sebep: psycopg prepared statement çakışması

### Verified Sonuç
İlk uçtan uca doğrulama şu facility ile yapıldı:
- `MENEMEN_HOSP`
- `facility_type = hospital`
- `bed_count = 120`
- `gross_area_m2 = 18000`

Verified sonuç:
- staging insert başarılı
- readiness = READY
- promote = SUCCESS
- `vw_dashboard_daily` içinde 7 KPI görünür
- bootstrap flow production seviyesinde doğrulandı

Verified KPI çıktısı:
- `electricity_kwh = 3120.0`
- `water_m3 = 108.0`
- `medical_waste_kg = 420.0`
- `pathological_waste_kg = 54.6`
- `general_waste_kg = 798.0`
- `scope2_location_tco2e = 1.435`
- `waste_cost_try = 55136.031`

### Ürün Anlamı
Bu katman sayesinde sistem artık sadece mevcut veriyi göstermiyor; veri hiç olmayan facility'leri de kontrollü şekilde bootstrap edip dashboard coverage sağlayabiliyor.

Bu, özellikle şu iki alan için kritik:
- orchestration coverage
- AI commentary / routing coverage

### Sonraki Ürün Adımı
- Kalan zero-dashboard facility'ler için batch bootstrap
- batch mode (`--all-zero-facilities`) ekleme
- bootstrap sonrası UI coverage doğrulama
- orchestration katmanının yeni facility'lerde de çalıştığını doğrulama


## 2026-04-07 — Bootstrap Layer Batch Mode karar kaydı

### Karar
Verified tek-facility bootstrap motoru korunarak, bunun üstüne ayrı bir batch orchestration katmanı eklendi.

### Neden bu yaklaşım seçildi
- çalışan E2E bootstrap motorunu bozma riskini azaltmak
- batch davranışını orchestration seviyesi olarak izole etmek
- tek facility ve çoklu facility kullanımını aynı çekirdek mantık üzerinden yürütmek
- idempotent davranışı korumak

### Uygulanan yapı
- Tek facility motor:
  - `scripts/bootstrap_zero_facilities.py`
- Batch orchestration katmanı:
  - `scripts/bootstrap_zero_facilities_batch.py`

### Batch seçim mantığı
- kaynak görünüm: `zerocare_operational.vw_dashboard_daily`
- seçim kuralı: `dashboard_rows = 0` olan facility’ler
- desteklenen modlar:
  - `--facility-code`
  - `--all-zero-facilities`
  - `--limit`
  - `--dry-run`
  - `--continue-on-error`

### Verified sonuç
- `BALCOVA_MED` ile tek facility canlı test yapıldı
- idempotent NOOP davranışı doğrulandı
- toplu gerçek batch run’da aşağıdaki facility’ler başarıyla bootstrap edildi:
  - `CIGLI_MED`
  - `DENTAL_CENTER`
  - `EYE_CENTER`

### İş kuralı sonucu
Bootstrap Layer artık sadece tek facility tohumlama aracı değil; kontrollü toplu coverage tamamlama katmanıdır.

### Sonraki adım
- UI tarafında facility dropdown / coverage davranışının tam doğrulaması
- gerekirse batch sonuçlarının API response contract içine alınması

## 2026-04-07 — Frontend facility coverage ve orchestration date propagation karar kaydı

### Karar
Bootstrap sonrası UI dropdown doğrulaması sadece liste görünürlüğü ile sınırlı tutulmadı; facility selection sonrası dashboard ve orchestration payload zinciri de uçtan uca doğrulandı.

### Tespit
Yeni bootstrap edilen facility’lerde dashboard verisi görünürken orchestration katmanı hata veriyordu. Kök neden veri eksikliği değil, tarih aktarım zincirinin kopuk olmasıydı.

### Kök neden
- API katmanı `report_date` üretiyordu
- orchestration wrapper bu tarihi alt script’e geçmiyordu
- alt script `TARGET_DATE` desteğine sahipti ama beslenmiyordu
- bu nedenle orchestration eski/default gün ile çalışıyordu

### Uygulanan düzeltme
- `services/orchestrator_runner.py` target_date destekler hale getirildi
- `TARGET_DATE` env forwarding eklendi
- `server.py` içindeki orchestration çağrısı `final_report_date` ile bağlandı

### Ürün etkisi
Bu düzeltme ile yeni bootstrap edilen facility’ler sadece dashboard’da görünür hale gelmedi; orchestration, routing ve action contract katmanları tarafından da aynı gün bağlamında işlenebilir hale geldi.

### Verified ürün sonucu
`DENTAL_CENTER` üzerinde şu zincir verified:
- dropdown listede görünür
- facility seçimi dashboard verisini doğru getirir
- orchestration final payload üretir
- routing_contract doludur
- action_contract doludur
- target_date doğru güne hizalanır

### Sonraki ürün adımı
- diğer yeni facility’lerde orchestration final toplu smoke test
- UI tarafında gerçek tarayıcı smoke test
- gerekirse orchestration/admin coverage raporu

## 2026-04-07 — 9/9 facility orchestration smoke test karar kaydı

### Karar
Sistemde görünen tüm 9 facility için `/api/orchestration/final` smoke test çalıştırıldı ve tamamı başarıyla geçti.

### Ürün anlamı
Bu sonuçla birlikte platform artık sadece seçili birkaç facility için değil, aktif görünen tüm demo tesis seti için:
- dashboard
- orchestration
- routing
- action contract

zincirini aynı gün bağlamında çalıştırabildiğini kanıtladı.

### Verified kapsam
Smoke test geçen 9 facility:
- `BALCOVA_MED`
- `CIGLI_HOSP`
- `CIGLI_MED`
- `DEMO_BORNOVA`
- `DEMO_KONAK`
- `DEMO_KSK`
- `DENTAL_CENTER`
- `EYE_CENTER`
- `MENEMEN_HOSP`

### Verified sonuç
Tüm facility’lerde:
- `orchestrator_status = OK`
- `staging_status = READY`
- `final_row_exists = True`
- `routing_contract` dolu
- `action_contract` dolu
- target date doğru güne hizalı

### Sonraki adım
- tarayıcı üstünden manuel UI smoke test
- gerekirse executive/demo script hazırlığı
- istenirse admin rapor veya coverage özeti endpoint’i


## Checkpoint — 2026-04-07 — 30 Day Coverage Sealed

Bugün production veri omurgasında kritik bir eşik geçildi.

Sorun UI değil, historical coverage eksikliğiydi. Sistem çalışıyordu ama bazı hastaneler için yalnızca 1–3 günlük veri görünüyordu. Yapılan analiz sonunda hedef, tüm aktif facility’ler için rolling son 30 takvim gününün production’da eksiksiz bulunması olarak sabitlendi.

Bu hedef için yeni bir batch backfill katmanı oluşturuldu:
- `scripts/backfill_30day_zero_facilities.py`

Bu script verified bootstrap layer’ı yeniden kullanır:
- eksik facility+date çiftlerini bulur
- sadece eksik günleri üretir
- staging -> readiness -> promote -> dashboard verify zincirini çalıştırır

İlk backfill çalıştırmasında DEMO_* facility’lerde hata görüldü. Kök neden `private_hospital` değerinin bootstrap profile resolver tarafından tanınmamasıydı. Bu nedenle `normalize_facility_type()` içine alias map eklendi ve `private_hospital -> hospital` başta olmak üzere çeşitli tip eşleştirmeleri tanımlandı.

Son yeniden çalıştırma sonrası son 30 günlük coverage tamamen kapandı.

Final durum:
- BALCOVA_MED = 30
- CIGLI_HOSP = 31
- CIGLI_MED = 30
- DEMO_BORNOVA = 30
- DEMO_KONAK = 30
- DEMO_KSK = 30
- DENTAL_CENTER = 30
- EYE_CENTER = 30
- MENEMEN_HOSP = 30

Final gap query sonucu:
- 0 rows

Bu checkpoint ile Zero@Hospital production veri omurgası artık 30-day demo-safe historical görünürlüğe ulaştı.

