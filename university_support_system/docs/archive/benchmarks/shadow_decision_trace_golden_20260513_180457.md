# Shadow Decision Trace Golden Run 20260513_180457

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 4
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 2
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (56883.3 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_180457.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_180457.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/check:application_process:answer_missing_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | capability expected=student_affairs.policy_lookup actual=-; provider_error_seen | 1 | 58524.0 | CHECK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=3,00; competing=- | - | 3,00 | - | capability expected=student_affairs.policy_lookup actual=-; provider_error_seen | 2 | 77411.0 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=3
- Provider hatalari: groq=3
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 3
- Retry history provider hata sayisi: 6
- Provider hata nedenleri: connection=9
- Retryable provider hata sayisi: 9
- Tahmini input token: 7208 (3 cagrida)
- Prompt/system char: 15894/12946
- Role bazli cagri sayisi: conversation=1, global_synthesis=2
- Role bazli tahmini input token: conversation=3277, global_synthesis=3931

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=3 configured_keys=53 used_keys=3
- Key fingerprint cagrilari: {"groq": {"calls": 3, "key_count": 53, "by_fingerprint": {"618f51582a5a": 1, "24b9652705b1": 1, "928ce4d0b4ba": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 56883.3, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 56883.3}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `58524.03`
- Timeout sinyalleri: capability_planner=2, routing=2

## Answer Validator Ozeti

- Kayit: 2 | pass=2 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: query_does_not_require_value_check=1, required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 2 | pass=1 | check=0 | skipped=1
- Nedenler: not_applicable=1, single_primary_threshold=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_180457-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/check:application_process:answer_missing_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Structural checks: `capability expected=student_affairs.policy_lookup actual=-; provider_error_seen`
- LLM roles: `global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~2165`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_180457-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_180457-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 16239.359, "capability_planner_timeout_suspected": true, "routing_ms": 12009.304, "routing_timeout_suspected": true, "conversation_ms": 10.707, "final_synthesis_ms": 18070.04}`
- Cevap preview: Benchmark, Kaynaklarda bu konuda şu bilgiler yer alıyor: - ndan mezuniyet hakkini elde etmeden cap’in lisans diplomasi verilmez - b) cap ogrencileri arasinda basari siralamasi yapilmaz - iye ayrica ikinci ana dali yaptigi bolumun lisans diplomasi verilir --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (9 parça) - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_180457-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/pass:single_primary_threshold; primary=3,00; competing=-`
- Judge repair: `-`
- Structural checks: `capability expected=student_affairs.policy_lookup actual=-; provider_error_seen`
- LLM roles: `conversation, global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/error/in_tok~3277; groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~1766`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_180457-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "conversation", "reason": "connection"}, {"provider": "groq", "role": "global_synthesis", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_180457-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "conversation", "reason": "connection"}, {"provider": "groq", "role": "global_synthesis", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 16443.411, "capability_planner_timeout_suspected": true, "routing_ms": 12006.056, "routing_timeout_suspected": true, "conversation_ms": 18314.208, "final_synthesis_ms": 18480.471}`
- Cevap preview: Benchmark, Kaynaklarda bu konuda şu bilgiler yer alıyor: - ana dal not ortalamasinin 4,00 uzerinden en az 3,00 olmasi ve ana dal diploma programinin ilgili sinifinda basari siralamasi itibari ile en az ilk % 20'sinde bulunmasi gerekir - % 20 - asari siralamasi itibari ile en az ilk % 20'sinde bulunmasi gerekir - edilerek birim yonetim kurulu karari ile senato tarafindan belirlenir --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (2 parça)
