# Shadow Decision Trace Golden Run 20260509_221718

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 1
- Trace kaydi: 1
- Source owner eslesmesi: 0/1
- Hata sayisi: 0
- LLM profile: fast
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260509_221718.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260509_221718.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT09 | personal_auth | personal_student_data | tuition_fee_catalog | - | department_orchestrator | finance | 0 | 16338.3 | CHECK |

## Notlar

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-20260509_221718-GT09`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz. Üretim Türü: - Kural - Routing: direct - Pipeline: finance
