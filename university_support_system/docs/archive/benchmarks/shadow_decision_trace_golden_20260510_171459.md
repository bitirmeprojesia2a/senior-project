# Shadow Decision Trace Golden Run 20260510_171459

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260510_171459.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260510_171459.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | 5 | 101424.6 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | 4 | 17646.7 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=9
- Provider hatalari: groq=2
- Fallback cagrilari: 0

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260510_171459-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error; groq/llama-3.3-70b-versatile/routing/primary/error; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Cevap preview: Benchmark, Çift Anadal Programı (ÇAP) başvuruları için genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. Programlar için ön lisans 120 AKTS, lisans 240 AKTS şartını yerine getirmek gerekir. Bir alt sınıfa/yarıyıla yapılan başvurular kabul edilmez. • Birimin yönetim kurulu kararı ile seçilecek bir danışman tarafından programın izlenmesi gerekmektedir. • ÇAP'ta başarı ve mezuniyet koşulları arasında ana dal programında mezuniyet hakkını elde eden ve ÇAP'ı başarıyla tamamlayan öğrencilere ikinci ana dal programının lisans diploması verilir. • ÇAP'tan mezuniyet hakkını elde eden öğrenciye, ana dal programından mezuniyet hakkını elde etmeden ÇAP'ın lisans diploması verilir. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260510_171459-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent`
- Specialist selector: `academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- LLM roles: `conversation, routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/final_refinement/primary/success`
- Cevap preview: Benchmark, Öğrencinin ÇAP'a başvurabilmesi için ana dal not ortalamasının asgari sıralaması itibarı ile en az ilk %20'sinde bulunması gerekir. • Başvurduğu yarı yıla kadar ana dal lisans programında yer alan tüm dersleri almış ve başarmış olması, • Ana dal not ortalamasına göre değerlendirme yapılması gerekir.#+#+Not ortalamasının tam olarak kaç olacağı kaynakta net bir şekilde belirtilmemiştir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - RAG - Routing: parallel - Pipeline: academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf
