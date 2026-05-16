# Shadow Decision Trace Golden Run 20260509_233027

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 3
- Trace kaydi: 3
- Source owner eslesmesi: 2/3
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260509_233027.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260509_233027.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | - | main_orchestrator | student_affairs | 2 | 16361.2 | OK |
| GT06 | international_policy | international_policy | international_policy | - | main_orchestrator | academic_programs, student_affairs | 4 | 89716.3 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | curriculum_catalog | - | clarification | academic_programs | 1 | 3732.8 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: anthropic=7
- Provider hatalari: -
- Fallback cagrilari: 0

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260509_233027-GT01`
- Trace owner: `academic_calendar`
- Capability: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/final_refinement/primary/success`
- Cevap preview: Benchmark, 2025-2026 eğitim öğretim yılı için final sınavları şu tarihlerde gerçekleştirilecek: • Güz dönemi: 3-16 Ocak 2026 • Bahar dönemi: 1-14 Haziran 2026 --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - VT - Routing: direct - Pipeline: student_affairs -> orchestrator Kaynak Özeti: - Belge: 2025_2026_genel_akademik_takvim.pdf

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-20260509_233027-GT06`
- Trace owner: `international_policy`
- Capability: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success; anthropic/claude-sonnet-4-6/judge/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success`
- Cevap preview: Benchmark, İkamet izni başvurusu için önce e-ikamet.goc.gov.tr üzerinden başvuru formu oluşturman, ardından tüm belgelerle birlikte formun oluşturulduğu tarihten itibaren en geç 7 gün içinde Öğrenci İşleri Daire Başkanlığı / İkamet İşlemleri Ofisi'ne teslim etmen gerekmektedir. Gerekli belgeler şunlardır: 1. İkamet izni kayıt/başvuru formu: e-ikamet.goc.gov.tr sistemi üzerinden alınan ve öğrenci tarafından imzalanmış form. 2. Pasaport fotokopisi: Kimlik bilgilerinin yer aldığı ilk sayfa, varsa vizenin bulunduğu sayfa ve ülkeye en son girişte alınan damganın yer aldığı sayfa; her biri ayrı ayrı fotokopi edilmelidir. Belgenin aslı dosya teslim günü yanında bulunmak zorundadır. Pasaportun, talep edilen ikamet izni süresinden en az 60 gün daha uzun geçerli olması zorunludur. 3. Öğrencilik ...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260509_233027-cap-followup`
- Trace owner: `curriculum_catalog`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success`
- Cevap preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.
