# Shadow Decision Trace Golden Run shadow_golden_cap_patch_baai_20260517

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 4
- Trace kaydi: 8
- Source owner eslesmesi: 2/3
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 4
- LLM profile: groq_only
- Question cache: bypass
- Warmup mode: none (0.0 ms)
- Provider retry: count=1 backoff=8.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_golden_cap_patch_baai_20260517.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_shadow_golden_cap_patch_baai_20260517.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Retrieval Budget | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Length | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT04 | student_affairs_policy | student_affairs_policy | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | - | shadow/pass:required_values_preserved | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=2; retry_history=4 | shadow/pass:clean; tokens=- | normal/ok; chars=792; sent=3; bullets=4 | - | - | capability expected=student_affairs.policy_lookup actual=calendar.academic_date; provider_retryable_error_seen | 2 | 69190.4 | CHECK |
| GT05 | cross_department | - | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | applied: kept=student_affairs, academic_programs; pruned=finance; reason=answer_contract_cap_debt_policy_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=2; retry_history=4 | shadow/pass:clean; tokens=- | normal/warn; chars=529; sent=3; bullets=7 | - | - | provider_retryable_error_seen | 2 | 83476.7 | CHECK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=2; retry_history=4 | shadow/pass:clean; tokens=- | normal/warn; chars=602; sent=3; bullets=7 | - | - | provider_retryable_error_seen | 2 | 81081.4 | CHECK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/pass:required_values_preserved | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=3,00; competing=- | - | final_retryable=2; retry_history=4 | shadow/pass:clean; tokens=- | normal/warn; chars=556; sent=3; bullets=6 | 3,00 | - | provider_retryable_error_seen | 2 | 91974.2 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=4, google_ai=4
- Provider hatalari: groq=4, google_ai=4
- Fallback cagrilari: 4
- Final attempt provider hata sayisi: 8
- Retry history provider hata sayisi: 16
- Provider hata nedenleri: connection=24
- Retryable provider hata sayisi: 24
- Tahmini input token: 73836 (8 cagrida)
- Prompt/system char: 276180/19184
- Role bazli cagri sayisi: final_refinement=2, global_synthesis=6
- Role bazli tahmini input token: final_refinement=4244, global_synthesis=69592

## API Key Dagilimi

- Provider/key dagilimi: google_ai: calls=4 configured_keys=16 used_keys=4, groq: calls=4 configured_keys=53 used_keys=4
- Key fingerprint cagrilari: {"groq": {"calls": 4, "key_count": 53, "by_fingerprint": {"64aeba5d5c98": 1, "2eb4f14b6ad5": 1, "f93b795d2a95": 1, "051f59a11b93": 1}}, "google_ai": {"calls": 4, "key_count": 16, "by_fingerprint": {"79cca093f2c6": 1, "82d8807b9142": 1, "ed72a4ecf461": 1, "1d5cad59f0ab": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `69190.39`
- Timeout sinyalleri: capability_planner=4, routing=4

## Answer Validator Ozeti

- Kayit: 4 | pass=4 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: no_query_relevant_required_values=1, query_does_not_require_value_check=1, required_values_preserved=2

## Value Conflict Ozeti

- Kayit: 4 | pass=1 | check=0 | skipped=3
- Nedenler: not_applicable=3, single_primary_threshold=1

## Notlar

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-shadow_golden_cap_patch_baai_20260517-GT04-retry1`
- Trace owner: `academic_calendar`
- Capability: `calendar.academic_date`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=student_affairs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=2; retry_history=4`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/ok; chars=792; sent=3; bullets=4`
- Structural checks: `capability expected=student_affairs.policy_lookup actual=calendar.academic_date; provider_retryable_error_seen`
- LLM roles: `final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/final_refinement/primary/error/in_tok~2122; google_ai/gemini-3-flash-preview/final_refinement/fallback/error/in_tok~2122`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_20260517-GT04", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "final_refinement", "reason": "connection"}, {"provider": "google_ai", "role": "final_refinement", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_20260517-GT04-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "final_refinement", "reason": "connection"}, {"provider": "google_ai", "role": "final_refinement", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 15015.995, "capability_planner_timeout_suspected": true, "routing_ms": 12013.439, "routing_timeout_suspected": true, "conversation_ms": 8.117, "final_synthesis_ms": 41631.967}`
- Cevap preview: Benchmark, Genel akademik takvime göre 2025-2026 guz yariyili yatay gecis basvuru tarihleri: merkezi yerlestirme puani (Ek Madde-1) için 01.08.2025 – 06.08.2025, kurumlar arasi/kurum ici için 01.08.2025 – 15.08.2025. Genel akademik takvime göre 2025-2026 bahar yariyili on lisans yatay gecis basvuru tarihleri 26.01.2026 – 01.02.2026 tarihidir. Üretim Türü: - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Kayıt İşleri Kaynak Özeti: - Belge: C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\data\raw\student_affairs\listeler\2025_2026_güz_yatay_geçiş_takvimi.pdf; C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\data\raw\student_affairs\listeler\2025_2026_bahar_yatay_geçiş_takvimi.pdf

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-shadow_golden_cap_patch_baai_20260517-GT05-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `applied: kept=student_affairs, academic_programs; pruned=finance; reason=answer_contract_cap_debt_policy_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=2; retry_history=4`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=529; sent=3; bullets=7`
- Structural checks: `provider_retryable_error_seen`
- LLM roles: `global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~11760; google_ai/gemini-3-flash-preview/global_synthesis/fallback/error/in_tok~11760`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_20260517-GT05", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "connection"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_20260517-GT05-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "connection"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 17602.647, "capability_planner_timeout_suspected": true, "routing_ms": 12042.507, "routing_timeout_suspected": true, "conversation_ms": 8.295, "final_synthesis_ms": 41389.703}`
- Cevap preview: Benchmark, CAP basvurusunda harc borcunun dogrudan basvuruya engel olduguna dair acik bir hukum bulamadim. Ders kaydi veya kayit yenileme icin odeme sarti ayri bir konudur; bu hukum CAP basvurusuna otomatik engel olarak tasinmamalidir. Üretim Türü: - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Çalışma biçimi: Paralel - Ajan akışı: Kayıt İşleri + Mevzuat Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (4 parça) - Belge: ön_lisans_ve_lisans.pdf

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-shadow_golden_cap_patch_baai_20260517-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=2; retry_history=4`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=602; sent=3; bullets=7`
- Structural checks: `provider_retryable_error_seen`
- LLM roles: `global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~11052; google_ai/gemini-3-flash-preview/global_synthesis/fallback/error/in_tok~11052`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_20260517-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "connection"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_20260517-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "connection"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 15009.049, "capability_planner_timeout_suspected": true, "routing_ms": 12020.123, "routing_timeout_suspected": true, "conversation_ms": 8.029, "final_synthesis_ms": 41803.923}`
- Cevap preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB duyuruları ile ilan edilir. Üretim Türü: - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Çalışma biçimi: Paralel - Ajan akışı: Kayıt İşleri + Mevzuat Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (7 parça) - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-shadow_golden_cap_patch_baai_20260517-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/pass:single_primary_threshold; primary=3,00; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=2; retry_history=4`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=556; sent=3; bullets=6`
- Structural checks: `provider_retryable_error_seen`
- LLM roles: `global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~11984; google_ai/gemini-3-flash-preview/global_synthesis/fallback/error/in_tok~11984`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_20260517-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "connection"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_cap_patch_baai_20260517-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "connection"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 15010.398, "capability_planner_timeout_suspected": true, "routing_ms": 12010.548, "routing_timeout_suspected": true, "conversation_ms": 20043.692, "final_synthesis_ms": 32573.434}`
- Cevap preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB duyuruları ile ilan edilir. Üretim Türü: - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Çalışma biçimi: Paralel - Ajan akışı: Kayıt İşleri + Mevzuat Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (3 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça)
