# Shadow Decision Trace Golden Run 20260514_133518

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 1
- Trace kaydi: 2
- Source owner eslesmesi: 1/1
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 1
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: none (0.0 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260514_133518.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260514_133518.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=1; retry_history=2 | shadow/check:answer_quality_issue; tokens=- | - | - | capability expected=student_affairs.policy_lookup actual=-; provider_retryable_error_seen | 1 | 33863.5 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=1
- Provider hatalari: groq=1
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 1
- Retry history provider hata sayisi: 2
- Provider hata nedenleri: connection=3
- Retryable provider hata sayisi: 3
- Tahmini input token: 2393 (1 cagrida)
- Prompt/system char: 2349/7226
- Role bazli cagri sayisi: routing=1
- Role bazli tahmini input token: routing=2393

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=1 configured_keys=53 used_keys=1
- Key fingerprint cagrilari: {"groq": {"calls": 1, "key_count": 53, "by_fingerprint": {"3b4187fdfdc3": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `33863.51`
- Timeout sinyalleri: capability_planner=1, routing=1

## Answer Validator Ozeti

- Kayit: 1 | pass=1 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: no_evidence_claims=1

## Value Conflict Ozeti

- Kayit: 1 | pass=0 | check=0 | skipped=1
- Nedenler: not_applicable=1

## Notlar

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260514_133518-GT04-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=student_affairs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_evidence_claims`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=1; retry_history=2`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `capability expected=student_affairs.policy_lookup actual=-; provider_retryable_error_seen`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~2393`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260514_133518-GT04", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-20260514_133518-GT04-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 18714.352, "capability_planner_timeout_suspected": true, "routing_ms": 12007.741, "routing_timeout_suspected": true, "conversation_ms": 6.278, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Bu konuda elimde yeterli kaynak bulunamadı. Soruyu biraz daha detaylandırırsan veya ilgili birimle iletişime geçersen daha net yardımcı olabilirim. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Kural - Routing: direct - Pipeline: student_affairs
