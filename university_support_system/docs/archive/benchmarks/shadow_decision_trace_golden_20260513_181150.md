# Shadow Decision Trace Golden Run 20260513_181150

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 3
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 1
- Value conflict riskli: 0
- Structural check riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (51859.0 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_181150.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_181150.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | - | - | - | 4 | 7695.9 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/check:answer_missing_required_evidence_values; missing=2,00 | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=3,00; competing=- | repair:rejected:answer_value_conflict_worsened | 3,00 | - | - | 6 | 25042.2 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=10
- Provider hatalari: -
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 0
- Retry history provider hata sayisi: 3
- Provider hata nedenleri: rate_limit=3
- Retryable provider hata sayisi: 3
- Tahmini input token: 24995 (10 cagrida)
- Prompt/system char: 33998/65994
- Role bazli cagri sayisi: conversation=1, global_synthesis=3, judge=2, routing=4
- Role bazli tahmini input token: conversation=3131, global_synthesis=5283, judge=1947, routing=14634

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=10 configured_keys=53 used_keys=10
- Key fingerprint cagrilari: {"groq": {"calls": 10, "key_count": 53, "by_fingerprint": {"26a01be4304a": 1, "39659184e1c2": 1, "76f4cfb21ed4": 1, "fe4490aa7a6a": 1, "618f51582a5a": 1, "fcb1af18c173": 1, "f93b795d2a95": 1, "897ea1ca897e": 1, "5150f63f1a64": 1, "64ee113faff7": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 51859.0, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 51859.0}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `7695.94`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 2 | pass=1 | check=1 | fail=0 | requires_judge=1 | contract_enforceable=0
- Nedenler: answer_missing_required_evidence_values=1, query_does_not_require_value_check=1

## Value Conflict Ozeti

- Kayit: 2 | pass=1 | check=0 | skipped=1
- Nedenler: not_applicable=1, single_primary_threshold=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_181150-cap-followup-retry1`
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
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2991; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1975; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~882`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_181150-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}, {"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_181150-cap-followup-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1742.037, "capability_planner_timeout_suspected": false, "routing_ms": 1461.727, "routing_timeout_suspected": false, "conversation_ms": 7.697, "final_synthesis_ms": 1700.752}`
- Cevap preview: Benchmark, Çift anadal programme başvurmak için ÖİDB’nin internet sayfasında açılan ilgili link üzerinden elektronik başvuru yapılır. • Başvuru için sisteme yüklenecek evraklar, yapılan duyuruda ilan edilir. • Not çizelgesi (transkript) ve dilekçe ile başvuru yapmanız gerekir. • Ana dal not ortalamanın 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibari ile en az ilk %20'sinde bulunmanız gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: sık_sorulan_sorular.txt (2 parça) - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_181150-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/check:answer_missing_required_evidence_values; missing=2,00`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/pass:single_primary_threshold; primary=3,00; competing=-`
- Judge repair: `repair:rejected:answer_value_conflict_worsened`
- Structural checks: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3131; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4268; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3111; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2082; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1065; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1226`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_181150-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 4542.331, "capability_planner_timeout_suspected": false, "routing_ms": 1450.618, "routing_timeout_suspected": false, "conversation_ms": 6816.637, "final_synthesis_ms": 7146.071}`
- Cevap preview: Benchmark, ÇAP başvurusu için not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibari ile en az ilk %20'sinde bulunması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (2 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (2 parça)
