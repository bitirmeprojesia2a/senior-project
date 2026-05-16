# Shadow Decision Trace Golden Run 20260513_163757

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 4
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 0
- Structural check riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (47835.0 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_163757.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_163757.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | - | 4 | 10413.8 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract; student_affairs:registration_agent/contract | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | shadow/pass:eligibility_value:answer_contains_eligibility_markers | - | 6 | 15276.4 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=10
- Provider hatalari: -
- Fallback cagrilari: 0
- Provider hata nedenleri: rate_limit=3
- Retryable provider hata sayisi: 3
- Tahmini input token: 25162 (10 cagrida)
- Prompt/system char: 34666/65994
- Role bazli tahmini input token: conversation=3319, global_synthesis=5334, judge=1939, routing=14570

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 47835.0, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 47834.9}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `10413.83`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 2 | pass=2 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: query_does_not_require_value_check=1, required_values_preserved=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_163757-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2976; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1874; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~912`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_163757-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_163757-cap-followup-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1660.559, "capability_planner_timeout_suspected": false, "routing_ms": 4104.857, "routing_timeout_suspected": false, "conversation_ms": 7.817, "final_synthesis_ms": 1653.926}`
- Cevap preview: Benchmark, Çift anadal programına başvuru, Senato tarafından belirlenen ve akademik takvimde belirtilen tarihte, ÖİDB’nin internet sayfasında açılan ilgili link üzerinden elektronik olarak yapılır. • Başvuru için ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk %20'sinde bulunması gerekir. • Çift anadal programını başarıyla tamamlayan öğrenciye ayrıca ikinci ana dalı yaptığı bölümün lisans diploması verilir. Bu programa başvurmak için ÖSYM kontenjanının %20’sinden az olmamak üzere, program bazlı olarak tespit edilerek birim yönetim kurulu kararı ile Senato tarafından belirlenen koşulları taşımanıznecessarytir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (2 parça)

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_163757-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract; student_affairs:registration_agent/contract`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Structural checks: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3319; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3066; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2226; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1027; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1234`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_163757-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_163757-cap-followup-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1659.089, "capability_planner_timeout_suspected": false, "routing_ms": 1863.62, "routing_timeout_suspected": false, "conversation_ms": 1792.558, "final_synthesis_ms": 4557.818}`
- Cevap preview: Benchmark, Not ortalamasının 4,00 üzerinden en az 2,00 olması zorunludur. Fakat bazı durumlarda ana dal not ortalaması 4,00 üzerinden en az 3,00 olması gerekebilir. Ayrıca, ana dal genel not ortalamasının 4,00 üzerinden en fazla 2,50'ye kadar düşmesi mümkün olabilir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (6 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (4 parça)
