# Shadow Decision Trace Golden Run 20260513_171747

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 4
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 1
- Structural check riskli: 2
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (56246.9 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_171747.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_171747.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/check:application_process:answer_missing_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | - | - | provider_error_seen | 5 | 19717.7 | CHECK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract; academic_programs:regulation_agent/contract | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/check:multiple_competing_threshold_values; primary=2,00; competing=2,50 | 2,00 | 2,50 | provider_error_seen | 6 | 17281.1 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=11
- Provider hatalari: groq=3
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 3
- Retry history provider hata sayisi: 6
- Provider hata nedenleri: rate_limit=9
- Retryable provider hata sayisi: 9
- Tahmini input token: 26269 (11 cagrida)
- Prompt/system char: 37496/67598
- Role bazli cagri sayisi: conversation=1, global_synthesis=4, judge=2, routing=4
- Role bazli tahmini input token: conversation=3315, global_synthesis=6535, judge=1884, routing=14535

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 56246.9, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 56246.9}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `19717.7`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 2 | pass=2 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: query_does_not_require_value_check=1, required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 2 | pass=0 | check=1 | skipped=1
- Nedenler: multiple_competing_threshold_values=1, not_applicable=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_171747-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/check:application_process:answer_missing_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Structural checks: `provider_error_seen`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2968; groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~1861; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~846; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1157`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_171747-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_171747-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 1806.717, "capability_planner_timeout_suspected": false, "routing_ms": 6798.019, "routing_timeout_suspected": false, "conversation_ms": 5.177, "final_synthesis_ms": 6851.203}`
- Cevap preview: Benchmark, Çift Ana Dal Programı'na (ÇAP) başvuru süreci, ÖİDB'nin internet sayfasında açılan ilgili link üzerinden elektronik olarak yapılır. Başvurular, Senato tarafından belirlenen ve akademik takvimde belirtilen tarihte yapılır. • Öğrenci, duyurulmuş olan ÇAP'a, dört yıllık programlarda ana dal diploma programının en erken üçüncü yarıyılda başvurabilir. • ÇAP'a başvurunun kabul ve kayıt koşulları şunlardır: ÖSYM kontenjanının %20'sinden az olmamak üzere, program bazlı olarak tespit edilerek birim yönetim kurulu kararı ile Senato tarafından belirlenir. • Ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibariyle en az ilk %20'sinde bulunması gerekir. Üretim Türü: - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (6 parça)

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_171747-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract; academic_programs:regulation_agent/contract`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/check:multiple_competing_threshold_values; primary=2,00; competing=2,50`
- Structural checks: `provider_error_seen`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3315; groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3039; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2292; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1038; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1225`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_171747-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_171747-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 1450.253, "capability_planner_timeout_suspected": false, "routing_ms": 6881.529, "routing_timeout_suspected": false, "conversation_ms": 2317.46, "final_synthesis_ms": 1516.832}`
- Cevap preview: Benchmark, Not ortalaması 4,00 üzerinden en az 2,00 olmalıdır. Not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibariyle en az ilk %20'sinde bulunması da gerekir. Ana dal genel not ortalamasının 4,00 üzerinden en fazla 2,50’ye kadar düşebilmesi ise bir defaya mahsus olmak üzere mümkündür. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (9 parça)
