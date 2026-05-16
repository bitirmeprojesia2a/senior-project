# Shadow Decision Trace Golden Run 20260510_164546

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260510_164546.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260510_164546.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | 5 | 63760.6 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | 5 | 16224.3 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=10
- Provider hatalari: groq=1
- Fallback cagrilari: 0

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260510_164546-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Cevap preview: Benchmark, Çift anadal programı başvurusu için, ana dal programınızda mezuniyet hakkını elde ediyor olmanız ve çift anadal programını başarıyla tamamlamanız gerekir. Ana dal genel not ortalamanızın 4,00 üzerinden en az 2,75 olması ve önlisans 120 AKTS, lisans 240 AKTS şartını yerine getirmeniz necesario. • Ana dal programındaki yükümlülüklerinizi yerine getirmelisiniz. • Başvuru süreci ve koşulları hakkında bilgi almak için akademik takvim ve duyuruları takip edebilirsiniz. Çift anadal programı başvuruları hakkında dahaDetailed bilgi için ilgili birimlerin duyurularını izlemeniz önerilir. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: ön_lisans_ve_lisans.pdf - Belge: 2025_2026_güz_yarıyılı...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260510_164546-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent`
- Specialist selector: `academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- LLM roles: `conversation, routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success; groq/llama-3.3-70b-versatile/routing/primary/error; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/final_refinement/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success`
- Cevap preview: Benchmark, ÇAP başvurularının değerlendirilmesinde öncelikle ana dal not ortalamasına bakılmaktadır. Ana dal genel not ortalamasının 4,00 üzerinden 2,75'in altına düşmesi durumunda, öğrencinin ikinci ana dal diploma programından kaydı silinebilir. • Ana dal not ortalamasının 4,00 üzerinden 2,75'in altına düşmemesi requiredir. • Aynı anda birden fazla ikinci ana dal diploma programına kayıt yapılamaz. • Ana dal programındaki not ortalamasının 4,00 üzerinden yeterli olması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - RAG - Routing: parallel - Pipeline: academic_programs -> orchestrator Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (4 parça)
