# Shadow Decision Trace Golden Run 20260513_174308

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
- Warmup mode: retrieval (51149.4 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_174308.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_174308.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | 4 | 7926.6 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/fail:answer_conflicts_with_evidence_values; missing=3,00 | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=3,00; competing=- | 3,00 | - | - | 6 | 24297.0 | FAIL |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=10
- Provider hatalari: -
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 0
- Retry history provider hata sayisi: 3
- Provider hata nedenleri: rate_limit=3
- Retryable provider hata sayisi: 3
- Tahmini input token: 25011 (10 cagrida)
- Prompt/system char: 34062/65994
- Role bazli cagri sayisi: conversation=1, global_synthesis=3, judge=2, routing=4
- Role bazli tahmini input token: conversation=3113, global_synthesis=5389, judge=1890, routing=14619

## API Key Dagilimi

- Provider/key dagilimi: -
- Key fingerprint cagrilari: {}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 10

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 51149.4, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 51149.4}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `7926.6`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 2 | pass=1 | check=0 | fail=1 | requires_judge=1 | contract_enforceable=0
- Nedenler: answer_conflicts_with_evidence_values=1, query_does_not_require_value_check=1

## Value Conflict Ozeti

- Kayit: 2 | pass=1 | check=0 | skipped=1
- Nedenler: not_applicable=1, single_primary_threshold=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_174308-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2976; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2142; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~913`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_174308-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_174308-cap-followup-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1658.005, "capability_planner_timeout_suspected": false, "routing_ms": 1905.53, "routing_timeout_suspected": false, "conversation_ms": 10.734, "final_synthesis_ms": 1980.47}`
- Cevap preview: Benchmark, Çift anadal programına başvuruda bulunmak için bazı koşulları sağlamanız gerekir. Başarı sıralaması şartı aranan programlarda çift anadal yapmak istediğiniz programın kayıt olduğunuz yıldaki başarı sıralaması şartını sağlamış olmanız necessarytir. Çift anadal programına başvuru ve kayıt koşulları hakkında ayrıntılı bilgi için ÖİDB web sayfasını takip edebilirsiniz. Ayrıca, aynı anda birden fazla ikinci ana dal diploma programına kayıt yapılamaz, ancak aynı anda ikinci ana dal diploma programı ile yan dal programına kayıt yapılabilir. Ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. Çift anadal programından mezun olabilmeniz için ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması ve programı başarıyla tamamlamak zorunludur. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (6 parça) -...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_174308-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/fail:answer_conflicts_with_evidence_values; missing=3,00`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/pass:single_primary_threshold; primary=3,00; competing=-`
- Structural checks: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3113; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4268; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3111; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2033; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~977; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1214`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_174308-cap-followup-retry1", "status": "FAIL", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 5701.013, "capability_planner_timeout_suspected": false, "routing_ms": 2277.804, "routing_timeout_suspected": false, "conversation_ms": 4672.608, "final_synthesis_ms": 7528.556}`
- Cevap preview: Benchmark, ÇAP başvurusu için not ortalamasının 4,00 üzerinden en az 2,00 olması gerekir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (2 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (2 parça)
