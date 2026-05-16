# Shadow Decision Trace Golden Run 20260513_192355

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 3
- Trace kaydi: 5
- Source owner eslesmesi: 3/3
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 1
- Structural check riskli: 1
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (50668.5 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_192355.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_192355.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=1; retry_history=2 | shadow/check:answer_quality_issue; tokens=- | - | - | provider_retryable_error_seen | 3 | 15861.6 | CHECK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | retry_history=1 | shadow/check:answer_quality_issue; tokens=- | - | - | - | 4 | 14895.4 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/check:multiple_competing_threshold_values; primary=3,00; competing=2,00 | judge:accept; approved=True | - | shadow/check:answer_quality_issue; tokens=- | 3,00 | 2,00 | - | 5 | 10026.9 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=12
- Provider hatalari: groq=1
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 1
- Retry history provider hata sayisi: 3
- Provider hata nedenleri: rate_limit=4
- Retryable provider hata sayisi: 4
- Tahmini input token: 32122 (12 cagrida)
- Prompt/system char: 38299/90203
- Role bazli cagri sayisi: conversation=1, final_refinement=1, global_synthesis=2, judge=2, routing=6
- Role bazli tahmini input token: conversation=3101, final_refinement=1502, global_synthesis=4249, judge=1985, routing=21285

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=12 configured_keys=53 used_keys=12
- Key fingerprint cagrilari: {"groq": {"calls": 12, "key_count": 53, "by_fingerprint": {"fc02f5c29d71": 1, "2075f8b244dc": 1, "64aeba5d5c98": 1, "c6e82d5f9ef2": 1, "70bc5df1936d": 1, "9ec28f2ad046": 1, "618f51582a5a": 1, "5150f63f1a64": 1, "7428d4dce055": 1, "a3e421be002a": 1, "2eb4f14b6ad5": 1, "fba5c0f29033": 1}}}
- Provider org fingerprintleri: 36ac290f66aa=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 50668.5, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 50668.5}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `15861.65`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 3 | pass=3 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: no_query_relevant_required_values=1, query_does_not_require_value_check=1, required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 3 | pass=0 | check=1 | skipped=2
- Nedenler: multiple_competing_threshold_values=1, not_applicable=2

## Notlar

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260513_192355-GT04-retry1`
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
- Provider warning: `final_retryable=1; retry_history=2`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `provider_retryable_error_seen`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2393; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1502`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_192355-GT04", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_192355-GT04-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 5177.014, "capability_planner_timeout_suspected": false, "routing_ms": 6644.654, "routing_timeout_suspected": false, "conversation_ms": 8.317, "final_synthesis_ms": 1513.313}`
- Cevap preview: Benchmark, Eğitim öğretimin başladığı tarihten itibaren üç hafta içinde daha önce öğrenim gördüğü yükseköğretim kurumlarında aldığı ve başarılı olduğu dersler için muaf olmak istediği dersleri içeren bir dilekçe ile başvurabilirsiniz. • Dilekçenize onaylı transkript ve onaylı ders içeriklerini eklemelisiniz. • Muafiyet talebiniz uygun görüldükten ve muaf olunan dersler sisteme işlendikten sonra danışmanınız ile birlikte alacak olduğunuz derslere kaydınız yapılır. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - RAG - Routing: direct - Pipeline: student_affairs -> orchestrator Kaynak Özeti: - Belge: sık_sorulan_sorular.txt (2 parça)

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_192355-cap-followup-retry1`
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
- Provider warning: `retry_history=1`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2976; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1974; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~902`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_192355-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_192355-cap-followup-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2329.657, "capability_planner_timeout_suspected": false, "routing_ms": 1408.765, "routing_timeout_suspected": false, "conversation_ms": 7.682, "final_synthesis_ms": 1824.622}`
- Cevap preview: Benchmark, Çift anadal programına başvuru, Senato tarafından belirlenen ve akademik takvimde belirtilen tarihte, ÖİDB'nin internet sayfasında açılan ilgili link üzerinden elektronik olarak yapılır. • Başvuru için program bazlı olarak tespit edilerek birim yönetim kurulu kararı ile Senato tarafından belirlenen kontenjanın %20'sinden az olmamak üzere bir oran uygulanır. • Öğrencinin ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk %20'sinde bulunması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (2 parça)

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_192355-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/check:multiple_competing_threshold_values; primary=3,00; competing=2,00`
- Judge repair: `judge:accept; approved=True`
- Provider warning: `-`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3101; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4268; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3111; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2275; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1083`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_192355-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1574.444, "capability_planner_timeout_suspected": false, "routing_ms": 1474.964, "routing_timeout_suspected": false, "conversation_ms": 1809.366, "final_synthesis_ms": 1679.565}`
- Cevap preview: Benchmark, ÇAP başvurusu için not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibari ile en az ilk % 20'sinde bulunması gerekir. Ayrıca, bazı kaynaklarda ana dal programındaki not ortalamasının 4,00 üzerinden en az 2,00 olması şartı da geçmektedir. Ancak, daha spesifik şartlar için senato tarafından belirlenen ve akademik takvimde belirtilen tarihlerde yapılan duyuruları takip etmeniz önerilir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (2 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça)
