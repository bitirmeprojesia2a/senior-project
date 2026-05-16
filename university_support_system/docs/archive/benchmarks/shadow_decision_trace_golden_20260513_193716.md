# Shadow Decision Trace Golden Run 20260513_193716

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 4
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 1
- Value conflict riskli: 0
- Structural check riskli: 2
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (55432.2 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_193716.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_193716.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | final_retryable=1; retry_history=2 | shadow/check:answer_quality_issue; tokens=- | - | - | provider_retryable_error_seen | 4 | 16992.9 | CHECK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | - | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract; student_affairs:registration_agent/contract | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/check:answer_missing_required_evidence_values; missing=4,00 | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:no_answer_threshold_values; primary=-; competing=- | repair:rejected_worse:answer_value_conflict_worsened | final_retryable=1; retry_history=2 | shadow/check:answer_quality_issue; tokens=- | - | - | capability expected=student_affairs.policy_lookup actual=-; provider_retryable_error_seen | 6 | 16921.7 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=10
- Provider hatalari: groq=2
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 2
- Retry history provider hata sayisi: 4
- Provider hata nedenleri: rate_limit=6
- Retryable provider hata sayisi: 6
- Tahmini input token: 25911 (10 cagrida)
- Prompt/system char: 37670/65994
- Role bazli cagri sayisi: conversation=1, global_synthesis=3, judge=2, routing=4
- Role bazli tahmini input token: conversation=3229, global_synthesis=6148, judge=1971, routing=14563

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=10 configured_keys=53 used_keys=10
- Key fingerprint cagrilari: {"groq": {"calls": 10, "key_count": 53, "by_fingerprint": {"fc02f5c29d71": 1, "2075f8b244dc": 1, "64aeba5d5c98": 1, "928ce4d0b4ba": 1, "70bc5df1936d": 1, "9ec28f2ad046": 1, "618f51582a5a": 1, "5150f63f1a64": 1, "7428d4dce055": 1, "a3e421be002a": 1}}}
- Provider org fingerprintleri: 1916381c41ac=1, 36ac290f66aa=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 55432.2, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 55432.2}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `16992.87`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 2 | pass=1 | check=1 | fail=0 | requires_judge=1 | contract_enforceable=0
- Nedenler: answer_missing_required_evidence_values=1, query_does_not_require_value_check=1

## Value Conflict Ozeti

- Kayit: 2 | pass=1 | check=0 | skipped=1
- Nedenler: no_answer_threshold_values=1, not_applicable=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_193716-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `judge:accept; approved=True`
- Provider warning: `final_retryable=1; retry_history=2`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `provider_retryable_error_seen`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2968; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2205; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~914`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_193716-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_193716-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 4808.609, "capability_planner_timeout_suspected": false, "routing_ms": 7038.001, "routing_timeout_suspected": false, "conversation_ms": 10.619, "final_synthesis_ms": 1723.539}`
- Cevap preview: Benchmark, ÇAP başvuruları akademik takvimde belirtilen tarihte yapılır. ÇAP başvurularının değerlendirilmesinde öncelikle ana dal not ortalamasına, ortalamanın eşitliği halinde öğrencinin tamamlamış olduğu toplam kredisine bakılır. • Ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk %20'sinde bulunması gerekir. • Birden fazla ikinci ana dal diploma programına kayıt yapılamaz, ancak aynı anda ikinci ana dal diploma programı ile yan dal programına kayıt yapılabilir. • Fazla kredi tamamlamış olan öğrencilere öncelik verilir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (6 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf - Belge: yonerge_onlisans_lisans_yatay_gecis.pdf - Belge: kalite_el_kitabı_r1.pdf - Belge: uluslara...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_193716-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract; student_affairs:registration_agent/contract`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/check:answer_missing_required_evidence_values; missing=4,00`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/pass:no_answer_threshold_values; primary=-; competing=-`
- Judge repair: `repair:rejected_worse:answer_value_conflict_worsened`
- Provider warning: `final_retryable=1; retry_history=2`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `capability expected=student_affairs.policy_lookup actual=-; provider_retryable_error_seen`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3229; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~3067; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2769; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1057; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1174`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_193716-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_193716-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 6490.538, "capability_planner_timeout_suspected": false, "routing_ms": 2191.356, "routing_timeout_suspected": false, "conversation_ms": 1749.556, "final_synthesis_ms": 1350.899}`
- Cevap preview: Benchmark, Not ortalaması sınırı 3,00'dir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (6 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (4 parça)
