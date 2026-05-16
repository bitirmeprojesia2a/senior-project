# Shadow Decision Trace Golden Run 20260514_184228

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
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260514_184228.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260514_184228.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Retrieval Budget | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | final_retryable=1; retry_history=2 | shadow/pass:clean; tokens=- | - | - | provider_retryable_error_seen | 5 | 16005.1 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=5
- Provider hatalari: groq=1
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 1
- Retry history provider hata sayisi: 2
- Provider hata nedenleri: rate_limit=3
- Retryable provider hata sayisi: 3
- Tahmini input token: 14839 (5 cagrida)
- Prompt/system char: 30435/28930
- Role bazli cagri sayisi: final_refinement=2, judge=1, routing=2
- Role bazli tahmini input token: final_refinement=6977, judge=1196, routing=6666

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=5 configured_keys=53 used_keys=5
- Key fingerprint cagrilari: {"groq": {"calls": 5, "key_count": 53, "by_fingerprint": {"3b4187fdfdc3": 1, "fc02f5c29d71": 1, "80b7f264cbe2": 1, "2075f8b244dc": 1, "64aeba5d5c98": 1}}}
- Provider org fingerprintleri: 68edacd4ded0=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `16005.06`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 1 | pass=1 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=1
- Nedenler: no_query_relevant_required_values=1

## Value Conflict Ozeti

- Kayit: 1 | pass=0 | check=0 | skipped=1
- Nedenler: not_applicable=1

## Notlar

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260514_184228-GT04-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=student_affairs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_neutral:repair_not_worse`
- Provider warning: `final_retryable=1; retry_history=2`
- Answer quality: `shadow/pass:clean; tokens=-`
- Structural checks: `provider_retryable_error_seen`
- LLM roles: `routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2393; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~6077; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1196; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~900`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260514_184228-GT04", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260514_184228-GT04-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 2612.001, "capability_planner_timeout_suspected": false, "routing_ms": 7866.613, "routing_timeout_suspected": false, "conversation_ms": 6.942, "final_synthesis_ms": 1374.528}`
- Cevap preview: Benchmark, Yatay geçişle gelen öğrencinin muafiyet başvurusu için bir zamanlama bulunamadı. Bylo sayısal veya tarih bilgisi kaynağı bulunamadı. Öğrenciler başvurularını yapmadan önce diploma programının şartlarını kontrol etmelidir. Üretim Türü: - Final Sentez: LLM - RAG - Routing: direct - Pipeline: student_affairs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
