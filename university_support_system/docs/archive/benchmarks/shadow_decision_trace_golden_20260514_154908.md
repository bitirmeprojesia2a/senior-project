# Shadow Decision Trace Golden Run 20260514_154908

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 1
- Trace kaydi: 1
- Source owner eslesmesi: 1/1
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 1
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (59178.3 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260514_154908.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260514_154908.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | - | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | - | shadow/pass:clean; tokens=- | - | - | primary_specialist expected=registration_agent actual=student_affairs, academic_programs | 4 | 71590.7 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=4
- Provider hatalari: -
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 0
- Retry history provider hata sayisi: 0
- Provider hata nedenleri: -
- Retryable provider hata sayisi: 0
- Tahmini input token: 8586 (4 cagrida)
- Prompt/system char: 7024/27326
- Role bazli cagri sayisi: global_synthesis=1, judge=1, routing=2
- Role bazli tahmini input token: global_synthesis=618, judge=659, routing=7309

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=4 configured_keys=53 used_keys=4
- Key fingerprint cagrilari: {"groq": {"calls": 4, "key_count": 53, "by_fingerprint": {"cc9074971faa": 1, "f1a0600529c4": 1, "fe4490aa7a6a": 1, "c93303cbec45": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 59178.3, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 59178.3}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `71590.66`
- Timeout sinyalleri: capability_planner=0, routing=0

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
- Context: `shadow-golden-20260514_154908-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `student_affairs, academic_programs`
- Specialist selector: `-`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_evidence_claims`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_neutral:repair_not_worse`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Structural checks: `primary_specialist expected=registration_agent actual=student_affairs, academic_programs`
- LLM roles: `routing, judge, global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3036; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~659; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~618`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260514_154908-GT04", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1920.062, "capability_planner_timeout_suspected": false, "routing_ms": 1565.591, "routing_timeout_suspected": false, "conversation_ms": 253.779, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Yatay geçiş ile gelen öğrencilerin muafiyet başvuruları için belirli bir tarih bulunmamaktadır. Öğrenci İşleri ve Akademik Programlar departmanlarına ulaşılamadığından, muafiyet başvurularının ne zaman yapılacağına dair net bir bilgi bulunmamaktadır. Önemli olan, öğrencinin gerekli belgeleri eksiksiz ve zamanında teslim etmesidir. Üretim Türü: - Ogrenci Isleri: Kural - Akademik Programlar: Kural - Routing: parallel - Pipeline: student_affairs -> academic_programs Kaynak Özeti: - Veritabani kaydi: ogrenci isleri
