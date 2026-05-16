# Shadow Decision Trace Golden Run 20260513_185819

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 4
- Trace kaydi: 5
- Source owner eslesmesi: 4/4
- Hata sayisi: 0
- Answer validator riskli: 1
- Value conflict riskli: 1
- Structural check riskli: 1
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (48975.6 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_185819.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_185819.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=2; retry_history=2 | shadow/check:answer_quality_issue; tokens=Routing | - | - | - | 3 | 16310.8 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/check:answer_missing_required_evidence_values; missing=% 50, 60 | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=2; retry_history=5 | shadow/check:answer_quality_issue; tokens=Routing | - | - | capability expected=student_affairs.policy_lookup actual=- | 3 | 19029.1 | CHECK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | - | shadow/check:answer_quality_issue; tokens=Routing | - | - | - | 4 | 9055.4 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/check:multiple_competing_threshold_values; primary=2,00; competing=3,00 | judge:accept; approved=True | - | shadow/check:answer_quality_issue; tokens=Routing | 2,00 | 3,00 | - | 5 | 11203.2 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=15
- Provider hatalari: groq=4
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 4
- Retry history provider hata sayisi: 7
- Provider hata nedenleri: rate_limit=11
- Retryable provider hata sayisi: 11
- Tahmini input token: 40397 (15 cagrida)
- Prompt/system char: 45605/116016
- Role bazli cagri sayisi: conversation=1, final_refinement=2, global_synthesis=2, judge=2, routing=8
- Role bazli tahmini input token: conversation=3115, final_refinement=2904, global_synthesis=4414, judge=2052, routing=27912

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=15 configured_keys=53 used_keys=15
- Key fingerprint cagrilari: {"groq": {"calls": 15, "key_count": 53, "by_fingerprint": {"520684406576": 1, "45862dc92a25": 1, "f5268dbc83f6": 1, "fcb1af18c173": 1, "c93303cbec45": 1, "897ea1ca897e": 1, "5150f63f1a64": 1, "64ee113faff7": 1, "7ebf4c926f8e": 1, "1f75827ea381": 1, "5e2c5c185255": 1, "2075f8b244dc": 1, "051f59a11b93": 1, "7428d4dce055": 1, "775f860f28a7": 1}}}
- Provider org fingerprintleri: 1916381c41ac=2, 68edacd4ded0=1, ed0dc161a99b=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 48975.6, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 48975.6}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `16310.81`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 4 | pass=3 | check=1 | fail=0 | requires_judge=1 | contract_enforceable=0
- Nedenler: answer_missing_required_evidence_values=1, no_query_relevant_required_values=1, query_does_not_require_value_check=1, required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 4 | pass=0 | check=1 | skipped=3
- Nedenler: multiple_competing_threshold_values=1, not_applicable=3

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260513_185819-GT01`
- Trace owner: `academic_calendar`
- Capability: `calendar.academic_date`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract`
- Branch gate: `observed: kept=student_affairs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=2; retry_history=2`
- Answer quality: `shadow/check:answer_quality_issue; tokens=Routing`
- Structural checks: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4265; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2337; groq/llama-3.3-70b-versatile/final_refinement/primary/error/in_tok~1187`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_185819-GT01", "status": "OK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "final_refinement", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 1547.716, "capability_planner_timeout_suspected": false, "routing_ms": 6840.834, "routing_timeout_suspected": false, "conversation_ms": 189.172, "final_synthesis_ms": 6894.209}`
- Cevap preview: Benchmark, Kaynaklarda bu konuda şu bilgiler yer alıyor: - guz donemi - bahar donemi --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - VT - Routing: direct - Pipeline: student_affairs Kaynak Özeti: - Belge: C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\data\raw\student_affairs\takvimler\2025_2026_genel_akademik_takvim.pdf

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260513_185819-GT04-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=student_affairs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/check:answer_missing_required_evidence_values; missing=% 50, 60`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=2; retry_history=5`
- Answer quality: `shadow/check:answer_quality_issue; tokens=Routing`
- Structural checks: `capability expected=student_affairs.policy_lookup actual=-`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~2393; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1717`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_185819-GT04", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "final_refinement", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_185819-GT04-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 6834.444, "capability_planner_timeout_suspected": false, "routing_ms": 6877.567, "routing_timeout_suspected": false, "conversation_ms": 7.464, "final_synthesis_ms": 5053.409}`
- Cevap preview: Benchmark, Yatay geçişle gelen öğrenciler, başvurdukları yarıyıla intibak ettirilir. Daha önce öğrenim gördüğü yükseköğretim kurumlarında aldığı ve başarılı olduğu dersler için muaf olmak isteyen öğrenciler, eğitim öğretimin başladığı tarihten itibaren üç hafta içinde bir dilekçe, onaylı transkript ve onaylı ders içerikleriyle birlikte başvuruda bulunmalıdır. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - RAG - Routing: direct - Pipeline: student_affairs -> orchestrator Kaynak Özeti: - Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf - Belge: sık_sorulan_sorular.txt (3 parça) - Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_185819-cap-followup`
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
- Provider warning: `-`
- Answer quality: `shadow/check:answer_quality_issue; tokens=Routing`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2976; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2162; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~881`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_185819-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1692.726, "capability_planner_timeout_suspected": false, "routing_ms": 1654.603, "routing_timeout_suspected": false, "conversation_ms": 7.43, "final_synthesis_ms": 1621.688}`
- Cevap preview: Benchmark, Çift anadal programı başvuruları, ilgili bölüme yapılır. • Başvurunun değerlendirilmesinde öncelikle ana dal genel not ortalamasına, ortalamanın eşitliği halinde ise öğrencinin tamamlamış olduğu toplam kredisine bakılır. • Aynı anda birden fazla ikinci ana dal diploma programına kayıt yapılamaz, ancak aynı anda ikinci ana dal diploma programı ile Yan Dal Programına (YDP) kayıt yapılabilir. Ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması vyzad. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça) - Belge: yonerge_cift_anadal_yandal.pdf (6 parça) - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_185819-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/check:multiple_competing_threshold_values; primary=2,00; competing=3,00`
- Judge repair: `judge:accept; approved=True`
- Provider warning: `-`
- Answer quality: `shadow/check:answer_quality_issue; tokens=Routing`
- Structural checks: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3115; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3132; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2252; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1171`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_185819-cap-followup", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2441.5, "capability_planner_timeout_suspected": false, "routing_ms": 1856.762, "routing_timeout_suspected": false, "conversation_ms": 1764.299, "final_synthesis_ms": 1498.457}`
- Cevap preview: Benchmark, Çift anadal programına başvurmak için not ortalamasının 4,00 üzerinden en az 2,00 olması şarttır. Ayrıca, bir diğer koşula göre ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk %20'sinde bulunması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (3 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça)
