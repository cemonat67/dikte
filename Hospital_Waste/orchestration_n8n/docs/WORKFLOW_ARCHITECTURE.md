# Zero@Hospital — n8n Workflow Architecture

## 1. Amaç
Bu orchestration katmanı aşağıdaki işi yapar:
- multi-facility synthetic data üretimi
- validation kontrolü
- core_metric_readings -> daily_metrics bridge orchestration
- 7/24 health/watchdog kontrolü
- hata halinde retry / remediation / alert

## 2. Ana Workflowlar

### ZH_MASTER_ORCHESTRATOR
Tetikleyici:
- Schedule Trigger

Görev:
- aktif facility listesini al
- her facility için ZH_FACILITY_RUNNER çağır
- sonuçları topla
- başarısız facility varsa logla ve remediation kuyruğuna gönder
- run summary üret

Input:
- run_date
- mode=daily|backfill
- optional facility filter

Output:
- total_facilities
- ok_count
- failed_count
- warning_count
- total_generated_rows
- total_promoted_rows
- total_bridged_rows

---

### ZH_FACILITY_RUNNER
Görev:
- facility config al
- baseline kontrol et
- ilgili metric producer’ları çalıştır
- validation controller çağır
- accepted kayıtları core katmanına geçir
- bridge workflow ile daily_metrics tarafına akıt
- facility summary üret

Input:
- facility_code
- facility_name
- run_date
- metric_profile

Output:
- facility_code
- status
- generated_rows
- validation_rows
- accepted_pairs
- promoted_rows
- bridged_rows

---

### ZH_VALIDATION_CONTROLLER
Görev:
- hard range check
- soft range warning
- ratio validation
- missing metric validation
- duplicate control
- impossible combination control

Output:
- validation_rows
- accepted_pairs
- rejected_pairs
- warning_pairs

---

### ZH_CORE_TO_DAILY_BRIDGE
Görev:
- accepted synthetic core kayıtlarını oku
- metric mapping uygula
- daily_metrics upsert et
- gerekiyorsa aggregation/refresh tetikle
- dashboard katmanına veri akışını doğrula

Output:
- bridged_rows
- missing_mappings
- failed_rows

---

### ZH_HEALTH_WATCHDOG
Tetikleyici:
- Schedule Trigger (sık)

Görev:
- master workflow son run kontrolü
- facility bazlı son veri tarihi kontrolü
- promoted_rows / bridged_rows sıfır mı kontrolü
- n8n container health
- dashboard endpoint health
- stale data tespiti
- remediation tetikleme

Output:
- health_status
- stale_facilities
- failed_workflows
- remediation_actions

## 3. Metric Producer Grupları

### ZH_METRIC_PRODUCER_UTILITIES
- water_m3
- wastewater_m3
- energy_kwh
- natural_gas_m3
- steam_ton

### ZH_METRIC_PRODUCER_EMISSIONS
- co2_kg
- scope1_tco2e
- scope2_location_tco2e
- scope2_market_tco2e

### ZH_METRIC_PRODUCER_OPERATIONS
- production_kg
- patient_count
- surgery_count
- occupancy_rate

### ZH_METRIC_PRODUCER_WASTE
- total_waste_kg
- medical_waste_kg
- pathological_waste_kg
- recycled_waste_kg

## 4. Çalışma Prensibi
- App katmanı ile orchestration katmanı ayrıdır
- Önce deterministic üretim
- Sonra deterministic validation
- Sonra bridge
- En son AI yorum katmanı (opsiyonel)
- AI karar vermez, sadece yorumlar

## 5. Sonraki Teknik Adım
1. facility registry dosyası oluştur
2. metric profile dosyası oluştur
3. ZH_MASTER_ORCHESTRATOR workflow JSON skeleton üret
