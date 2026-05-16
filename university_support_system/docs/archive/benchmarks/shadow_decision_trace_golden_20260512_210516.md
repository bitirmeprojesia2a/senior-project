# Shadow Decision Trace Golden Run 20260512_210516

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 1
- Trace kaydi: 1
- Source owner eslesmesi: 0/1
- Hata sayisi: 0
- Answer validator riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: none (0.0 ms)
- Provider retry: count=0 backoff=0.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260512_210516.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260512_210516.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| GT09 | personal_auth | personal_student_data | tuition_fee_catalog | - | department_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | observed: kept=-; pruned=-; reason=single_branch | shadow/pass:no_evidence_claims | 0 | 28429.7 | CHECK |

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `28429.68`
- Timeout sinyalleri: capability_planner=1, routing=1

## Answer Validator Ozeti

- Kayit: 1 | pass=1 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: no_evidence_claims=1

## Notlar

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-20260512_210516-GT09`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- Selected specialists: `tuition_agent`
- Specialist selector: `finance:tuition_agent/contract, legacy=tuition_agent:match`
- Branch gate: `observed: kept=-; pruned=-; reason=single_branch`
- Answer validator: `shadow/pass:no_evidence_claims`
- LLM roles: `-`
- LLM usage: `-`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260512_210516-GT09", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 16069.461, "capability_planner_timeout_suspected": true, "routing_ms": 12005.061, "routing_timeout_suspected": true, "conversation_ms": null, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresini...
