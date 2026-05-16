# Shadow Decision Trace Golden Run 20260509_233736

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260509_233736.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260509_233736.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | 5 | 75009.5 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | - | main_orchestrator | academic_programs, student_affairs | 4 | 40763.0 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: anthropic=9
- Provider hatalari: -
- Fallback cagrilari: 0

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260509_233736-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success; anthropic/claude-sonnet-4-6/judge/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success`
- Cevap preview: Benchmark, Çift ana dal programına (ÇAP) başvurabilmek için kayıtlı olduğun ana dal programının ilgili yükümlülüklerini yerine getirmiş olman gerekir. Başvuru ve kabul süreci bağlı olduğun birimin (fakülte/yüksekokul) yönetim kurulu tarafından yürütülür. Başvuruların hangi dönemde ve nasıl yapılacağına ilişkin ayrıntılar biriminin duyuruları ve akademik takvimle ilan edildiğinden, güncel başvuru takvimi ve koşulları için biriminle veya ilgili öğrenci işleri birimiyle iletişime geçmeni öneririm. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve_lisans.pdf - Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf - Belge: yonerge_onlisans_lisans_yatay_gecis.pdf - Belge: çift_ana_...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260509_233736-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-6/conversation/primary/success; anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success; anthropic/claude-sonnet-4-6/judge/primary/success`
- Cevap preview: Benchmark, Çift anadal programına (ÇAP) başvurabilmek için başvurduğun yarı yıla kadar ana dal lisans programındaki tüm dersleri almış ve başarmış olman, ayrıca başvuru sırasındaki ana dal genel not ortalamanın 4,00 üzerinden en az 2,50 olması gerekir. Bunun yanı sıra başarı sıralaması itibarıyla programının en az ilk %20'sinde bulunman da aranmaktadır. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (4 parça) - Belge: yonerge_cift_anadal_yandal.pdf - Belge: yonerge_onlisans_lisans_yatay_gecis.pdf (2 parça) - Belge: ön_...
