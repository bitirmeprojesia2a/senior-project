# Shadow Decision Trace Golden Run shadow_golden_current_baai_fp16_20260517

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 12
- Trace kaydi: 18
- Source owner eslesmesi: 6/10
- Hata sayisi: 0
- Answer validator riskli: 1
- Value conflict riskli: 0
- Structural check riskli: 10
- LLM profile: groq_only
- Question cache: bypass
- Warmup mode: none (0.0 ms)
- Provider retry: count=1 backoff=5.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_golden_current_baai_fp16_20260517.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_shadow_golden_current_baai_fp16_20260517.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Retrieval Budget | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Length | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | - | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | - | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=2; retry_history=4 | shadow/pass:clean; tokens=- | normal/ok; chars=272; sent=2; bullets=4 | - | - | capability expected=calendar.academic_date actual=-; provider_retryable_error_seen | 2 | 61450.6 | CHECK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | - | main_orchestrator | academic_programs | academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match | 0 | observed: kept=academic_programs; pruned=-; reason=single_branch | - | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=274; sent=3; bullets=4 | - | - | capability expected=course.detail actual=- | 0 | 29160.6 | CHECK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | - | main_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | observed: kept=finance; pruned=-; reason=single_branch | - | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=359; sent=4; bullets=4 | - | - | capability expected=finance.tuition_fee actual=- | 0 | 27139.1 | CHECK |
| GT04 | student_affairs_policy | student_affairs_policy | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | - | shadow/pass:required_values_preserved | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=2; retry_history=4 | shadow/pass:clean; tokens=- | normal/ok; chars=792; sent=3; bullets=4 | - | - | capability expected=student_affairs.policy_lookup actual=calendar.academic_date; provider_retryable_error_seen | 2 | 60774.3 | CHECK |
| GT05 | cross_department | - | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | applied: kept=student_affairs, academic_programs; pruned=finance; reason=answer_contract_cap_debt_policy_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/check:answer_missing_required_evidence_values; missing=4,00, 2,75, 120, 240 | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=2; retry_history=4 | shadow/pass:clean; tokens=- | normal/warn; chars=528; sent=3; bullets=7 | - | - | provider_retryable_error_seen | 2 | 75073.1 | CHECK |
| GT06 | international_policy | international_policy | international_policy | - | main_orchestrator | academic_programs | academic_programs:international_agent/contract, legacy=international_agent:match | 0 | applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch | primary:international_agent:full; searches=1; mqe=0; early=strong_primary_evidence | shadow/pass:query_does_not_require_value_check | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=2; retry_history=4 | shadow/pass:clean; tokens=- | normal/warn; chars=486; sent=1; bullets=10 | - | - | capability expected=international.policy_lookup actual=-; provider_retryable_error_seen | 2 | 59165.3 | CHECK |
| GT07 | announcement | announcement_search | - | - | clarification | - | - | 0 | - | - | - | - | - | - | - | shadow/pass:clean; tokens=- | exempt/ok; chars=267; sent=2; bullets=3 | - | - | primary_department expected=announcement actual=- | 0 | 28929.6 | CHECK |
| GT08 | event | event_search | - | - | clarification | - | - | 0 | - | - | - | - | - | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=267; sent=2; bullets=3 | - | - | primary_department expected=event actual=- | 0 | 28925.4 | CHECK |
| GT09 | personal_auth | personal_student_data | tuition_fee_catalog | - | department_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | observed: kept=finance; pruned=-; reason=single_branch | - | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=258; sent=3; bullets=3 | - | - | - | 0 | 27634.6 | CHECK |
| GT10 | ambiguous | - | - | - | clarification | - | - | 0 | - | - | - | - | - | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=164; sent=2; bullets=0 | - | - | - | 0 | 12140.1 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=2; retry_history=4 | shadow/pass:clean; tokens=- | normal/warn; chars=602; sent=3; bullets=7 | - | - | provider_retryable_error_seen | 2 | 73205.4 | CHECK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/pass:required_values_preserved | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=3,00; competing=- | - | final_retryable=3; retry_history=6 | shadow/pass:clean; tokens=- | normal/warn; chars=556; sent=3; bullets=6 | 3,00 | - | provider_retryable_error_seen | 3 | 94963.2 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=7, google_ai=6
- Provider hatalari: groq=7, google_ai=6
- Fallback cagrilari: 6
- Final attempt provider hata sayisi: 13
- Retry history provider hata sayisi: 26
- Provider hata nedenleri: connection=39
- Retryable provider hata sayisi: 39
- Tahmini input token: 90228 (13 cagrida)
- Prompt/system char: 322415/38514
- Role bazli cagri sayisi: conversation=1, final_refinement=6, global_synthesis=6
- Role bazli tahmini input token: conversation=3284, final_refinement=15642, global_synthesis=71302

## API Key Dagilimi

- Provider/key dagilimi: google_ai: calls=6 configured_keys=16 used_keys=5, groq: calls=7 configured_keys=53 used_keys=6
- Key fingerprint cagrilari: {"groq": {"calls": 7, "key_count": 53, "by_fingerprint": {"520684406576": 1, "34d6c1f77423": 2, "80b7f264cbe2": 1, "2eb4f14b6ad5": 1, "19f91860a589": 1, "64ee113faff7": 1}}, "google_ai": {"calls": 6, "key_count": 16, "by_fingerprint": {"79cca093f2c6": 2, "82d8807b9142": 1, "ed72a4ecf461": 1, "1d5cad59f0ab": 1, "83f71e22e9f6": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `61450.63`
- Timeout sinyalleri: capability_planner=9, routing=12

## Answer Validator Ozeti

- Kayit: 9 | pass=8 | check=1 | fail=0 | requires_judge=1 | contract_enforceable=0
- Nedenler: answer_missing_required_evidence_values=1, no_evidence_claims=3, no_query_relevant_required_values=1, query_does_not_require_value_check=2, required_values_preserved=2

## Value Conflict Ozeti

- Kayit: 9 | pass=1 | check=0 | skipped=8
- Nedenler: not_applicable=8, single_primary_threshold=1

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_20260517-GT01-retry1`
- Trace owner: `academic_calendar`
- Capability: `-`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract`
- Branch gate: `observed: kept=student_affairs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=2; retry_history=4`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/ok; chars=272; sent=2; bullets=4`
- Structural checks: `capability expected=calendar.academic_date actual=-; provider_retryable_error_seen`
- LLM roles: `final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/final_refinement/primary/error/in_tok~1418; google_ai/gemini-3-flash-preview/final_refinement/fallback/error/in_tok~1418`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT01", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "final_refinement", "reason": "connection"}, {"provider": "google_ai", "role": "final_refinement", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT01-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "final_refinement", "reason": "connection"}, {"provider": "google_ai", "role": "final_refinement", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 15023.811, "capability_planner_timeout_suspected": true, "routing_ms": 13979.004, "routing_timeout_suspected": true, "conversation_ms": 27.692, "final_synthesis_ms": 32032.487}`
- Cevap preview: Benchmark, Genel akademik takvime göre yarıyıl sonu/final sınavları: güz dönemi için 03-16 Ocak 2026, bahar dönemi için 01-14 Haziran 2026. Üretim Türü: - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Kayıt İşleri Kaynak Özeti: - Belge: 2025_2026_genel_akademik_takvim.pdf

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_20260517-GT02`
- Trace owner: `curriculum_catalog`
- Capability: `-`
- Selected specialists: `curriculum_agent`
- Specialist selector: `academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match`
- Branch gate: `observed: kept=academic_programs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=academic_programs`
- Answer validator: `shadow/pass:no_evidence_claims`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/ok; chars=274; sent=3; bullets=4`
- Structural checks: `capability expected=course.detail actual=-`
- LLM roles: `-`
- LLM usage: `-`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT02", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 15001.285, "capability_planner_timeout_suspected": true, "routing_ms": 13913.557, "routing_timeout_suspected": true, "conversation_ms": 16.84, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, BIL203 Veri Yapilari (3 kredi, 5 AKTS) dersinin önkoşulları: BIL104 Programlamaya Giris II. Önkoşullu derslerden en az DD alınmış olması gerekir. Üretim Türü: - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Müfredat Kaynak Özeti: - Veritabani kaydi: ders onkosulu

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_20260517-GT03`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- Selected specialists: `tuition_agent`
- Specialist selector: `finance:tuition_agent/contract, legacy=tuition_agent:match`
- Branch gate: `observed: kept=finance; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=finance`
- Answer validator: `shadow/pass:no_evidence_claims`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/ok; chars=359; sent=4; bullets=4`
- Structural checks: `capability expected=finance.tuition_fee actual=-`
- LLM roles: `-`
- LLM usage: `-`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT03", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 15005.849, "capability_planner_timeout_suspected": true, "routing_ms": 12009.126, "routing_timeout_suspected": true, "conversation_ms": 8.375, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Öğrenim Ücreti Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_20260517-GT04-retry1`
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
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT04", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "final_refinement", "reason": "connection"}, {"provider": "google_ai", "role": "final_refinement", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT04-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "final_refinement", "reason": "connection"}, {"provider": "google_ai", "role": "final_refinement", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 15008.425, "capability_planner_timeout_suspected": true, "routing_ms": 13840.979, "routing_timeout_suspected": true, "conversation_ms": 20.789, "final_synthesis_ms": 31615.455}`
- Cevap preview: Benchmark, Genel akademik takvime göre 2025-2026 guz yariyili yatay gecis basvuru tarihleri: merkezi yerlestirme puani (Ek Madde-1) için 01.08.2025 – 06.08.2025, kurumlar arasi/kurum ici için 01.08.2025 – 15.08.2025. Genel akademik takvime göre 2025-2026 bahar yariyili on lisans yatay gecis basvuru tarihleri 26.01.2026 – 01.02.2026 tarihidir. Üretim Türü: - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Kayıt İşleri Kaynak Özeti: - Belge: C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\universi...

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_20260517-GT05-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `applied: kept=student_affairs, academic_programs; pruned=finance; reason=answer_contract_cap_debt_policy_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/check:answer_missing_required_evidence_values; missing=4,00, 2,75, 120, 240`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=2; retry_history=4`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=528; sent=3; bullets=7`
- Structural checks: `provider_retryable_error_seen`
- LLM roles: `global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~12615; google_ai/gemini-3-flash-preview/global_synthesis/fallback/error/in_tok~12615`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT05", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "connection"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT05-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "connection"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 15058.273, "capability_planner_timeout_suspected": true, "routing_ms": 13908.906, "routing_timeout_suspected": true, "conversation_ms": 8.181, "final_synthesis_ms": 31855.413}`
- Cevap preview: Benchmark, ÇAP başvurusu için harç borcunun doğrudan başvuruya engel olduğuna dair açık bir hüküm bulamadım. Ders kaydı veya kayıt yenileme için ödeme şartı ayrı bir konudur; bu hükmü ÇAP başvurusuna otomatik engel olarak taşımıyorum. Üretim Türü: - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Çalışma biçimi: Paralel - Ajan akışı: Kayıt İşleri + Mevzuat Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (4 parça) - Be...

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_20260517-GT06-retry1`
- Trace owner: `international_policy`
- Capability: `-`
- Selected specialists: `international_agent`
- Specialist selector: `academic_programs:international_agent/contract, legacy=international_agent:match`
- Branch gate: `applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=academic_programs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=2; retry_history=4`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=486; sent=1; bullets=10`
- Structural checks: `capability expected=international.policy_lookup actual=-; provider_retryable_error_seen`
- LLM roles: `final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/final_refinement/primary/error/in_tok~4281; google_ai/gemini-3-flash-preview/final_refinement/fallback/error/in_tok~4281`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT06", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "final_refinement", "reason": "connection"}, {"provider": "google_ai", "role": "final_refinement", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT06-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "final_refinement", "reason": "connection"}, {"provider": "google_ai", "role": "final_refinement", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 15015.008, "capability_planner_timeout_suspected": true, "routing_ms": 12018.701, "routing_timeout_suspected": true, "conversation_ms": 7.378, "final_synthesis_ms": 31942.681}`
- Cevap preview: Benchmark, Kaynaklarda bu konuda şu bilgiler yer alıyor: - 7 gun - 6 ay - eslim etmeleri ve on kayitlarini kesin kayda donusturmeleri zorunludur - rencilerin on kayitlari yapilmis olsa dahi, kesin kayitlari yapilmaz - kesin kayit icin istenen belgeler, senato tarafindan belirlenir Üretim Türü: - RAG - Çalışma biçimi: Paralel - Ajan akışı: Uluslararası Kaynak Özeti: - Belge: ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf (3 parça) - Belge: ön_lisans_ve_lisans_programları.pdf

### GT07 - announcement

- Soru: Bilgisayar muhendisligindeki son duyurular neler?
- Not: Announcement DB short-circuit ve bolum filtresi.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_20260517-GT07`
- Trace owner: `-`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- Response filter: `-`
- Answer validator: `-`
- Answer coverage: `-`
- Value conflict: `-`
- Judge repair: `-`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `exempt/ok; chars=267; sent=2; bullets=3`
- Structural checks: `primary_department expected=announcement actual=-`
- LLM roles: `-`
- LLM usage: `-`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT07", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": 13862.645, "routing_timeout_suspected": true, "conversation_ms": 7.95, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Sorunuzun hangi alana ait olduğunu net olarak belirleyemedim. Aşağıdaki seçeneklerden birini belirterek tekrar sorabilirsiniz: - Öğrenci İşleri (kayıt, not, staj, mezuniyet) - Akademik Programlar (müfredat, yönetmelik, Erasmus) - Finans (harç, burs, ödeme)

### GT08 - event

- Soru: Bu hafta Muhendislik Fakultesinde seminer var mi?
- Not: Event DB short-circuit ve zaman penceresi.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_20260517-GT08`
- Trace owner: `-`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- Response filter: `-`
- Answer validator: `-`
- Answer coverage: `-`
- Value conflict: `-`
- Judge repair: `-`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/ok; chars=267; sent=2; bullets=3`
- Structural checks: `primary_department expected=event actual=-`
- LLM roles: `-`
- LLM usage: `-`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT08", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": 13877.211, "routing_timeout_suspected": true, "conversation_ms": 5.643, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Sorunuzun hangi alana ait olduğunu net olarak belirleyemedim. Aşağıdaki seçeneklerden birini belirterek tekrar sorabilirsiniz: - Öğrenci İşleri (kayıt, not, staj, mezuniyet) - Akademik Programlar (müfredat, yönetmelik, Erasmus) - Finans (harç, burs, ödeme)

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_20260517-GT09`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- Selected specialists: `tuition_agent`
- Specialist selector: `finance:tuition_agent/contract, legacy=tuition_agent:match`
- Branch gate: `observed: kept=finance; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=finance`
- Answer validator: `shadow/pass:no_evidence_claims`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/ok; chars=258; sent=3; bullets=3`
- Structural checks: `-`
- LLM roles: `-`
- LLM usage: `-`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT09", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 15009.002, "capability_planner_timeout_suspected": true, "routing_ms": 12013.647, "routing_timeout_suspected": true, "conversation_ms": null, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz. Üretim Türü: - Kural - Çalışma biçimi: Doğrudan - Ajan akışı: Öğrenim Ücreti

### GT10 - ambiguous

- Soru: Sey basvuru ne zaman?
- Not: Eksik slot/ambiguity davranisi.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_20260517-GT10`
- Trace owner: `-`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- Response filter: `-`
- Answer validator: `-`
- Answer coverage: `-`
- Value conflict: `-`
- Judge repair: `-`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/ok; chars=164; sent=2; bullets=0`
- Structural checks: `-`
- LLM roles: `-`
- LLM usage: `-`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-GT10", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": 12022.523, "routing_timeout_suspected": true, "conversation_ms": 12.983, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_20260517-cap-followup-retry1`
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
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "connection"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "connection"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 15011.238, "capability_planner_timeout_suspected": true, "routing_ms": 13832.81, "routing_timeout_suspected": true, "conversation_ms": 7.395, "final_synthesis_ms": 31984.56}`
- Cevap preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB duyuruları ile ilan edilir. Üretim Türü: - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Çalışma biçimi: Paralel - Ajan akışı: Kayıt İşleri + Mevzuat Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (7 parça) - Belge: ön_l...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_20260517-cap-followup-retry1`
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
- Provider warning: `final_retryable=3; retry_history=6`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=556; sent=3; bullets=6`
- Structural checks: `provider_retryable_error_seen`
- LLM roles: `conversation, global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/error/in_tok~3284; groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~11984; google_ai/gemini-3-flash-preview/global_synthesis/fallback/error/in_tok~11984`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "conversation", "reason": "connection"}, {"provider": "groq", "role": "global_synthesis", "reason": "connection"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "connection"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_20260517-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "conversation", "reason": "connection"}, {"provider": "groq", "role": "global_synthesis", "reason": "connection"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "connection"}]}]`
- Timeout signals: `{"capability_planner_ms": 15002.432, "capability_planner_timeout_suspected": true, "routing_ms": 13885.118, "routing_timeout_suspected": true, "conversation_ms": 20040.577, "final_synthesis_ms": 31913.236}`
- Cevap preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB duyuruları ile ilan edilir. Üretim Türü: - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Çalışma biçimi: Paralel - Ajan akışı: Kayıt İşleri + Mevzuat Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (3 parça) - Belge: çift...
