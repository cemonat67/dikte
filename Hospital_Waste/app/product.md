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

