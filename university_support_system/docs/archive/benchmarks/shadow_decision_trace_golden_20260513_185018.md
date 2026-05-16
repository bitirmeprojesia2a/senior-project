# Shadow Decision Trace Golden Run 20260513_185018

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 1
- Trace kaydi: 2
- Source owner eslesmesi: 1/1
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (48528.5 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_185018.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_185018.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=2; retry_history=5 | shadow/check:answer_quality_issue; tokens=Routing | - | - | - | 3 | 17681.3 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=3
- Provider hatalari: groq=2
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 2
- Retry history provider hata sayisi: 5
- Provider hata nedenleri: rate_limit=7
- Retryable provider hata sayisi: 7
- Tahmini input token: 8168 (3 cagrida)
- Prompt/system char: 6864/25813
- Role bazli cagri sayisi: final_refinement=1, routing=2
- Role bazli tahmini input token: final_refinement=1502, routing=6666

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=3 configured_keys=53 used_keys=3
- Key fingerprint cagrilari: {"groq": {"calls": 3, "key_count": 53, "by_fingerprint": {"26a01be4304a": 1, "39659184e1c2": 1, "fc02f5c29d71": 1}}}
- Provider org fingerprintleri: 36ac290f66aa=2
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 48528.5, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 48528.4}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `17681.26`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 1 | pass=1 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: no_query_relevant_required_values=1

## Value Conflict Ozeti

- Kayit: 1 | pass=0 | check=0 | skipped=1
- Nedenler: not_applicable=1

## Notlar

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260513_185018-GT04-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=student_affairs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=2; retry_history=5`
- Answer quality: `shadow/check:answer_quality_issue; tokens=Routing`
- Structural checks: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2393; groq/llama-3.3-70b-versatile/final_refinement/primary/error/in_tok~1502`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_185018-GT04", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "final_refinement", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_185018-GT04-retry1", "status": "OK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "final_refinement", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 1982.385, "capability_planner_timeout_suspected": false, "routing_ms": 6904.404, "routing_timeout_suspected": false, "conversation_ms": 7.174, "final_synthesis_ms": 6340.08}`
- Cevap preview: Benchmark, birim yonetim kurulu’nun muafiyet talebini uygun gormesi ve muaf --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - RAG - Routing: direct - Pipeline: student_affairs Kaynak Özeti: - Belge: sık_sorulan_sorular.txt (2 parça) - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf
