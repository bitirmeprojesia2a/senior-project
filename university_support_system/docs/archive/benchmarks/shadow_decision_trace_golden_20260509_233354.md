# Shadow Decision Trace Golden Run 20260509_233354

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 1/2
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260509_233354.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260509_233354.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | 5 | 88742.2 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | curriculum_catalog | - | clarification | academic_programs | 1 | 3738.1 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: anthropic=6
- Provider hatalari: -
- Fallback cagrilari: 0

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260509_233354-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success; anthropic/claude-sonnet-4-6/judge/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success`
- Cevap preview: Benchmark, Çift anadal programına başvuru koşulları ve süreci hakkında elimdeki kaynaklarda yeterince ayrıntılı bilgi bulunmamaktadır. Güncel başvuru koşullarını, tarihleri ve gerekli belgeleri öğrenmek için bağlı olduğunuz fakültenin öğrenci işleri birimiyle doğrudan iletişime geçmenizi öneririm. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: öğrenci_işleri_birimi.txt (3 parça) - Belge: yonerge_cift_anadal_yandal.pdf (3 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (2 parça)

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260509_233354-cap-followup`
- Trace owner: `curriculum_catalog`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success`
- Cevap preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.
