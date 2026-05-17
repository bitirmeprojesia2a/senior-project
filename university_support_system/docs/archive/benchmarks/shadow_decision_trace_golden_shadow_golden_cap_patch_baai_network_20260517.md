# Shadow Decision Trace Golden Run shadow_golden_cap_patch_baai_network_20260517

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 4
- Trace kaydi: 8
- Source owner eslesmesi: 2/3
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 2
- LLM profile: groq_only
- Question cache: bypass
- Warmup mode: none (0.0 ms)
- Provider retry: count=1 backoff=8.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_golden_cap_patch_baai_network_20260517.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_shadow_golden_cap_patch_baai_network_20260517.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Retrieval Budget | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Length | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT04 | student_affairs_policy | student_affairs_policy | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | - | shadow/pass:required_values_preserved | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | final_retryable=1; retry_history=2 | shadow/pass:clean; tokens=- | normal/warn; chars=959; sent=3; bullets=8 | - | - | capability expected=student_affairs.policy_lookup actual=calendar.academic_date; provider_retryable_error_seen | 4 | 22475.4 | CHECK |
| GT05 | cross_department | - | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | applied: kept=academic_programs, student_affairs; pruned=finance; reason=answer_contract_cap_debt_policy_gate | support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty; primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | retry_history=2 | shadow/pass:clean; tokens=- | normal/warn; chars=775; sent=4; bullets=8 | - | - | - | 5 | 20400.5 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | final_retryable=1; retry_history=4 | shadow/pass:clean; tokens=- | normal/warn; chars=721; sent=3; bullets=9 | - | - | provider_retryable_error_seen | 6 | 27766.0 | CHECK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty; primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence | shadow/pass:no_query_relevant_required_values | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=3,00; competing=- | judge:accept; approved=True | retry_history=5 | shadow/pass:clean; tokens=- | normal/warn; chars=664; sent=5; bullets=9 | 3,00 | - | - | 5 | 22574.4 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=19, google_ai=1
- Provider hatalari: groq=2
- Fallback cagrilari: 1
- Final attempt provider hata sayisi: 2
- Retry history provider hata sayisi: 13
- Provider hata nedenleri: other=4, rate_limit=11
- Retryable provider hata sayisi: 15
- Tahmini input token: 81114 (20 cagrida)
- Prompt/system char: 189631/134855
- Role bazli cagri sayisi: conversation=1, final_refinement=1, global_synthesis=5, judge=4, routing=9
- Role bazli tahmini input token: conversation=3320, final_refinement=2122, global_synthesis=36452, judge=7126, routing=32094

## API Key Dagilimi

- Provider/key dagilimi: google_ai: calls=1 configured_keys=16 used_keys=1, groq: calls=19 configured_keys=53 used_keys=16
- Key fingerprint cagrilari: {"groq": {"calls": 19, "key_count": 53, "by_fingerprint": {"955997d77e17": 1, "3b4187fdfdc3": 1, "fc02f5c29d71": 1, "2075f8b244dc": 1, "c6e82d5f9ef2": 2, "70bc5df1936d": 2, "9ec28f2ad046": 2, "45862dc92a25": 1, "5150f63f1a64": 1, "1d6935952e9a": 1, "fabc86c419a2": 1, "7ebf4c926f8e": 1, "c1adddf49f35": 1, "34d6c1f77423": 1, "64aeba5d5c98": 1, "5636cc6375b7": 1}}, "google_ai": {"calls": 1, "key_count": 16, "by_fingerprint": {"79cca093f2c6": 1}}}
- Provider org fingerprintleri: 1916381c41ac=1, ed0dc161a99b=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `22475.36`
- Timeout sinyalleri: capability_planner=0, routing=1

## Answer Validator Ozeti

- Kayit: 4 | pass=4 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=2
- Nedenler: no_query_relevant_required_values=2, query_does_not_require_value_check=1, required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 4 | pass=1 | check=0 | skipped=3
- Nedenler: not_applicable=3, single_primary_threshold=1

## Notlar

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-shadow_golden_cap_patch_baai_network_20260517-GT04-retry1`
- Trace owner: `academic_calendar`
- Capability: `calendar.academic_date`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=student_affairs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `judge:accept; approved=True`
- Provider warning: `final_retryable=1; retry_history=2`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=959; sent=3; bullets=8`
- Structural checks: `capability expected=student_affairs.policy_lookup actual=calendar.academic_date; provider_retryable_error_seen`
- LLM roles: `routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2459; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~2122; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1917`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_network_20260517-GT04", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_network_20260517-GT04-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 2204.256, "capability_planner_timeout_suspected": false, "routing_ms": 12008.353, "routing_timeout_suspected": true, "conversation_ms": 8.881, "final_synthesis_ms": 2498.224}`
- Cevap preview: Benchmark, Yatay geçişle gelen öğrenci muafiyet başvurusunu, akademik takvime göre 2025-2026 güz yarıyılı için 01.08.2025 – 06.08.2025 veya 01.08.2025 – 15.08.2025 tarihleri arasında, 2025-2026 bahar yarıyılı için ise 26.01.2026 – 01.02.2026 tarihleri arasında yapmalıdır. Önemli tarihler: • 01.08.2025 – 06.08.2025: Merkezi yerleştirme puanı (Ek Madde-1) için • 01.08.2025 – 15.08.2025: Kurumlar arası/kurum içi için • 26.01.2026 – 01.02.2026: Bahar yarıyılı için tarihleri. Üretim Türü: - Final Sentez: LLM - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Kayıt İşleri -> Orkestratör Kaynak Özeti: - Belge: C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\data\raw\student_affairs\listeler\2025_2026_güz_yatay_geçiş_takvimi.pdf; C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\data\raw\stude...

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-shadow_golden_cap_patch_baai_network_20260517-GT05-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `applied: kept=academic_programs, student_affairs; pruned=finance; reason=answer_contract_cap_debt_policy_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_neutral:repair_not_worse`
- Provider warning: `retry_history=2`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=775; sent=4; bullets=8`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3236; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~11756; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1840; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1337`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_network_20260517-GT05", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "other"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_network_20260517-GT05-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2298.991, "capability_planner_timeout_suspected": false, "routing_ms": 2980.829, "routing_timeout_suspected": false, "conversation_ms": 7.351, "final_synthesis_ms": 2520.387}`
- Cevap preview: Benchmark, CAP başvuruları için Ana Dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması, önlisans programları için 120 AKTS ve lisans programları için 240 AKTS şartını yerine getirmeniz gerekir. Harc borcu ödeme yöntemi ile ilgili olarak net bilgi bulunamadı. Harc borcu ödemeleri hakkında bilgi almak için ilgili sekreterin iletişim bilgilerini öğrenebilir veya doğrudan Öğrenci İşleri Daire Başkanlığına başvurabilirsiniz. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Mevzuat + Kayıt İşleri; Son: Orkestratör Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça) - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: ön_lisans_ve_lisans.pdf

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-shadow_golden_cap_patch_baai_network_20260517-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_neutral:repair_not_worse`
- Provider warning: `final_retryable=1; retry_history=4`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=721; sent=3; bullets=9`
- Structural checks: `provider_retryable_error_seen`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~3060; google_ai/gemini-3-flash-preview/routing/fallback/success/in_tok~3060; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~9986; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1725; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1355`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_network_20260517-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "other"}, {"provider": "groq", "role": "judge", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_network_20260517-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 12242.216, "capability_planner_timeout_suspected": false, "routing_ms": 6099.937, "routing_timeout_suspected": false, "conversation_ms": 8.376, "final_synthesis_ms": 2283.891}`
- Cevap preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB duyuruları ile ilan edilir. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Kayıt İşleri + Mevzuat; Son: Orkestratör Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça) - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf - Belge: bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-shadow_golden_cap_patch_baai_network_20260517-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/pass:single_primary_threshold; primary=3,00; competing=-`
- Judge repair: `judge:accept; approved=True`
- Provider warning: `retry_history=5`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=664; sent=5; bullets=9`
- Structural checks: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3320; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4268; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3202; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~12018; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1644`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_network_20260517-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "conversation", "reason": "rate_limit"}, {"provider": "google_ai", "role": "conversation", "reason": "other"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "google_ai", "role": "routing", "reason": "other"}, {"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_network_20260517-cap-followup-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 8255.685, "capability_planner_timeout_suspected": false, "routing_ms": 1915.89, "routing_timeout_suspected": false, "conversation_ms": 5834.142, "final_synthesis_ms": 2381.266}`
- Cevap preview: Benchmark, ÇAP başvurunuz için not ortalamasının en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibari ile en az ilk %20'sinde bulunması gerekir. • Not ortalaması 4,00 üzerinden hesaplanır. • Başarı sıralaması itibari ile ilk %20'de yer almakandatory. Bu koşulları karşıladığınız takdirde başvurunuz değerlendirilir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Mevzuat + Kayıt İşleri; Son: Orkestratör Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (3 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça)
