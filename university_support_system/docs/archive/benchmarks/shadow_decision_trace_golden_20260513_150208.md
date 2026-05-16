# Shadow Decision Trace Golden Run 20260513_150208

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (55021.5 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_150208.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_150208.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | 4 | 11171.5 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | 6 | 20841.7 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=10
- Provider hatalari: -
- Fallback cagrilari: 0
- Provider hata nedenleri: -
- Retryable provider hata sayisi: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 55021.5, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 55021.5}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `11171.55`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 2 | pass=2 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: query_does_not_require_value_check=1, required_values_preserved=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_150208-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_150208-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2174.174, "capability_planner_timeout_suspected": false, "routing_ms": 1802.839, "routing_timeout_suspected": false, "conversation_ms": 239.752, "final_synthesis_ms": 1500.603}`
- Cevap preview: Benchmark, Çift anadal programına başvuru, ilgili dönemlerin başlangıcında kesinleşir. Çift anadal programına hak kazanan öğrencilerin kayıt işlemleri ile ilgili süreç, ÖİDB web sayfasında ilan edilir. Aynı anda birden fazla ikinci ana dal diploma programına kayıt yapılamaz. Başvurunun kabul ve kayıt koşulları, ÖİDB web sayfasında ilan edilir. Ana dal ve ikinci ana dal programları ilişkileri, akademik takvim kapsamında değerlendirilir. Genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. Çift anadal programında önlisans için 120 AKTS, lisans için 240 AKTS şartını yerine getirmek gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (7 parça) - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (2 parça)

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_150208-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_150208-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1580.853, "capability_planner_timeout_suspected": false, "routing_ms": 7762.534, "routing_timeout_suspected": false, "conversation_ms": 4582.757, "final_synthesis_ms": 1717.68}`
- Cevap preview: Benchmark, CAP başvurusu için not ortalamasının 4,00 üzerinden en az 2,00 veya 3,00 olması gerekmektedir. İşte başvuru koşulları: • Ana dal diploma programının ilgili sınıfında başarı sıralaması itibari ile en az ilk %20'sinde bulunması gerekir. • Not ortalamasının 4,00 üzerinden en az 3,00 olması da şarttır. Bu koşullar, CAP başvurusu için görülmektedir. CAP'a başvurular, Senato tarafından belirlenen ve akademik takvimde belirtilen tarihte, ÖİDB’nin internet sayfasında açılan ilgili link üzerinden elektronik olarak yapılır. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (3 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça)
