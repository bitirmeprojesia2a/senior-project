# Shadow Decision Trace Golden Run shadow_golden_current_baai_fp16_contractfix_20260517

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 12
- Trace kaydi: 15
- Source owner eslesmesi: 9/10
- Hata sayisi: 0
- Answer validator riskli: 1
- Value conflict riskli: 0
- Structural check riskli: 2
- LLM profile: groq_only
- Question cache: bypass
- Warmup mode: none (0.0 ms)
- Provider retry: count=1 backoff=5.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_golden_current_baai_fp16_contractfix_20260517.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_shadow_golden_current_baai_fp16_contractfix_20260517.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Retrieval Budget | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Length | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | - | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=579; sent=4; bullets=5 | - | - | - | 3 | 4459.7 | OK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | course.detail | main_orchestrator | academic_programs | academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match | 0 | observed: kept=academic_programs; pruned=-; reason=single_branch | - | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=158; sent=3; bullets=3 | - | - | - | 3 | 5206.8 | OK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | finance.tuition_fee | main_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | observed: kept=finance; pruned=-; reason=single_branch | - | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=359; sent=4; bullets=4 | - | - | - | 2 | 3588.1 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | applied: kept=student_affairs; pruned=academic_programs; reason=calendar_owner_single_branch | - | shadow/pass:required_values_preserved | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | retry_history=1 | shadow/pass:clean; tokens=- | normal/ok; chars=859; sent=2; bullets=5 | - | - | capability expected=student_affairs.policy_lookup actual=calendar.academic_date | 4 | 7059.6 | CHECK |
| GT05 | cross_department | - | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | applied: kept=student_affairs, academic_programs; pruned=finance; reason=answer_contract_cap_debt_policy_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/check:answer_missing_required_evidence_values; missing=120, 240, 46 | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_improved:repair_improved | final_retryable=1; retry_history=3 | shadow/pass:clean; tokens=- | normal/warn; chars=826; sent=4; bullets=8 | - | - | provider_retryable_error_seen; provider_error_seen | 6 | 12439.1 | CHECK |
| GT06 | international_policy | international_policy | international_policy | international.policy_lookup | main_orchestrator | academic_programs | academic_programs:international_agent/contract, legacy=international_agent:match | 0 | applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch | primary:international_agent:full; searches=1; mqe=0; early=strong_primary_evidence | shadow/pass:query_does_not_require_value_check | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | - | shadow/pass:clean; tokens=- | normal/warn; chars=984; sent=8; bullets=10 | - | - | - | 4 | 8468.6 | OK |
| GT07 | announcement | announcement_search | announcement_search | - | announcement_agent | announcement | - | 0 | - | - | - | - | - | - | - | shadow/pass:clean; tokens=- | exempt/ok; chars=2479; sent=15; bullets=10 | - | - | - | 1 | 1651.4 | OK |
| GT08 | event | event_search | event_search | - | event_agent | event | - | 0 | - | - | - | - | - | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=219; sent=3; bullets=1 | - | - | - | 1 | 1659.7 | OK |
| GT09 | personal_auth | personal_student_data | personal_student_data | - | clarification | finance | - | 0 | - | - | - | - | - | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=180; sent=2; bullets=0 | - | - | - | 1 | 1924.4 | OK |
| GT10 | ambiguous | - | - | - | clarification | - | - | 0 | - | - | - | - | - | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=164; sent=2; bullets=0 | - | - | - | 1 | 2679.7 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | - | shadow/pass:clean; tokens=- | normal/warn; chars=754; sent=3; bullets=10 | - | - | - | 5 | 12654.2 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty; primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence | shadow/pass:no_query_relevant_required_values | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=3,00; competing=- | judge:accept; approved=True | retry_history=2 | shadow/pass:clean; tokens=- | normal/warn; chars=643; sent=4; bullets=7 | 3,00 | - | - | 5 | 13604.2 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=35, google_ai=1
- Provider hatalari: groq=1, google_ai=1
- Fallback cagrilari: 1
- Final attempt provider hata sayisi: 2
- Retry history provider hata sayisi: 6
- Provider hata nedenleri: json_validate_failed=1, other=3, rate_limit=4
- Retryable provider hata sayisi: 7
- Tahmini input token: 140436 (36 cagrida)
- Prompt/system char: 279453/282353
- Role bazli cagri sayisi: conversation=1, final_refinement=3, global_synthesis=6, judge=5, routing=20, specialist_synthesis=1
- Role bazli tahmini input token: conversation=3293, final_refinement=8429, global_synthesis=49800, judge=9178, routing=69540, specialist_synthesis=196

## API Key Dagilimi

- Provider/key dagilimi: google_ai: calls=1 configured_keys=16 used_keys=1, groq: calls=35 configured_keys=53 used_keys=35
- Key fingerprint cagrilari: {"groq": {"calls": 35, "key_count": 53, "by_fingerprint": {"cc9074971faa": 1, "f1a0600529c4": 1, "fe4490aa7a6a": 1, "c93303cbec45": 1, "5e2c5c185255": 1, "24b9652705b1": 1, "d427d6dcc70e": 1, "75d046119efe": 1, "2075f8b244dc": 1, "64aeba5d5c98": 1, "928ce4d0b4ba": 1, "5636cc6375b7": 1, "c6e82d5f9ef2": 1, "70bc5df1936d": 1, "9ec28f2ad046": 1, "45862dc92a25": 1, "496eecc507d0": 1, "618f51582a5a": 1, "5150f63f1a64": 1, "7428d4dce055": 1, "a3e421be002a": 1, "2eb4f14b6ad5": 1, "fba5c0f29033": 1, "5985794291cf": 1, "26a01be4304a": 1, "fcb1af18c173": 1, "64ee113faff7": 1, "775f860f28a7": 1, "98aa7a677e13": 1, "1d6935952e9a": 1, "cc1a6102eca9": 1, "f5268dbc83f6": 1, "76f4cfb21ed4": 1, "1f75827ea381": 1, "d16ee01d06f1": 1}}, "google_ai": {"calls": 1, "key_count": 16, "by_fingerprint": {"aac8ead26ad8": 1}}}
- Provider org fingerprintleri: 9670657e8ae2=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `4459.66`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 8 | pass=7 | check=1 | fail=0 | requires_judge=1 | contract_enforceable=4
- Nedenler: answer_missing_required_evidence_values=1, no_evidence_claims=2, no_query_relevant_required_values=2, query_does_not_require_value_check=2, required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 8 | pass=1 | check=0 | skipped=7
- Nedenler: not_applicable=7, single_primary_threshold=1

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT01`
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
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/ok; chars=579; sent=4; bullets=5`
- Structural checks: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4265; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2422; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1490`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT01", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1221.493, "capability_planner_timeout_suspected": false, "routing_ms": 1320.069, "routing_timeout_suspected": false, "conversation_ms": 149.853, "final_synthesis_ms": 1153.27}`
- Cevap preview: Benchmark, Final sınavları güz dönemi için 03-16 Ocak 2026, bahar dönemi için 01-14 Haziran 2026 arasında yapılacak. Bu tarihler genel akademik takvime göre belirlen. Bu tarih aralıkları içinde yapılacak sınavların detayları akademik takvim ve duyurular ile açıklanacaktır. Üretim Türü: - Final Sentez: LLM - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Kayıt İşleri -> Orkestratör Kaynak Özeti: - Belge: C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_suppor...

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT02`
- Trace owner: `curriculum_catalog`
- Capability: `course.detail`
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
- Answer length: `normal/ok; chars=158; sent=3; bullets=3`
- Structural checks: `-`
- LLM roles: `routing, specialist_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4267; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2771; groq/llama-3.3-70b-versatile/specialist_synthesis/primary/success/in_tok~196`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT02", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2049.602, "capability_planner_timeout_suspected": false, "routing_ms": 1763.493, "routing_timeout_suspected": false, "conversation_ms": 9.24, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, BIL203 dersinin AKTS kredisi 5'dir. BIL203 dersinin ön koşulu BIL104 dersidir. Üretim Türü: - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Müfredat

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT03`
- Trace owner: `tuition_fee_catalog`
- Capability: `finance.tuition_fee`
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
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2274`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT03", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1695.186, "capability_planner_timeout_suspected": false, "routing_ms": 1741.082, "routing_timeout_suspected": false, "conversation_ms": 14.422, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Öğrenim Ücreti Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT04-retry1`
- Trace owner: `academic_calendar`
- Capability: `calendar.academic_date`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `applied: kept=student_affairs; pruned=academic_programs; reason=calendar_owner_single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `judge:accept; approved=True`
- Provider warning: `retry_history=1`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/ok; chars=859; sent=2; bullets=5`
- Structural checks: `capability expected=student_affairs.policy_lookup actual=calendar.academic_date`
- LLM roles: `routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3102; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~2123; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1886`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT04", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "json_validate_failed"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT04-retry1", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1973.635, "capability_planner_timeout_suspected": false, "routing_ms": 1736.403, "routing_timeout_suspected": false, "conversation_ms": 8.078, "final_synthesis_ms": 1573.06}`
- Cevap preview: Benchmark, Yatay geçiş ile gelen öğrenciler muafiyet başvurularını, genel akademik takvime göre 2025-2026 güz yarıyılı için merkezi yerleştirme puanı ile gelenler 01.08.2025 – 06.08.2025, kurumlararası/kurum içi yatay geçiş yapanlar 01.08.2025 – 15.08.2025 tarihleri arasında, 2025-2026 bahar yarıyılı için ise 26.01.2026 – 01.02.2026 tarihleri arasında yapmalıdır. Üretim Türü: - Final Sentez: LLM - VT - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Kayıt İşleri; Son: Orkestratör Kaynak Özeti: ...

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT05-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `applied: kept=student_affairs, academic_programs; pruned=finance; reason=answer_contract_cap_debt_policy_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/check:answer_missing_required_evidence_values; missing=120, 240, 46`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_improved:repair_improved`
- Provider warning: `final_retryable=1; retry_history=3`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=826; sent=4; bullets=8`
- Structural checks: `provider_retryable_error_seen; provider_error_seen`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2916; groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~12557; google_ai/gemini-3-flash-preview/global_synthesis/fallback/error/in_tok~12557; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~2764; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1444`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT05", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT05-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "other"}]}]`
- Timeout signals: `{"capability_planner_ms": 1904.427, "capability_planner_timeout_suspected": false, "routing_ms": 1973.177, "routing_timeout_suspected": false, "conversation_ms": 11.634, "final_synthesis_ms": 3388.69}`
- Cevap preview: Benchmark, CAP basvurusu icin genel kosullar: ana dal not ortalamasinin 4,00 uzerinden en az 3,00 olmasi ve ana dal diploma programinin ilgili sinifinda basari siralamasi itibariyla en az ilk %20 icinde bulunmak gerekir. Harc borcunun dogrudan CAP basvurusuna engel olduguna dair acik bir hukum bulamadim; ders kaydi veya kayit yenileme icin odeme sarti ayri bir konudur. Harc borcu odeme kanalina iliskin ayri bir kaynak yoksa bunu basvuru uygunlugu ile karistirmamak gerekir. Üretim Türü: - Ogrenc...

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT06`
- Trace owner: `international_policy`
- Capability: `international.policy_lookup`
- Selected specialists: `international_agent`
- Specialist selector: `academic_programs:international_agent/contract, legacy=international_agent:match`
- Branch gate: `applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=academic_programs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `judge:accept; approved=True`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=984; sent=8; bullets=10`
- Structural checks: `-`
- LLM roles: `routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3110; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~4816; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1244`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT06", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1873.519, "capability_planner_timeout_suspected": false, "routing_ms": 1964.091, "routing_timeout_suspected": false, "conversation_ms": 7.821, "final_synthesis_ms": 1961.162}`
- Cevap preview: Benchmark, Yabancı öğrenci olarak kayıt için gerekli belgeler arasında pasaport, ikamet izni belgesi ve lise diploması bulunur. İkamet izni almak için Göç İdaresi e-ikamet sistemi üzerinden başvuru formu doldurularak imzalanmalıdır. Ayrıca, 18 yaşından küçük öğrenciler için muvafakatname sahibi kişi tarafından imzalı bir belge sunulmalıdır. Talep edilen ikamet izni süresinden 60 gün daha uzun süreli pasaport ya da pasaport yerine geçen belgeye sahip olunması gereklidir. • İkamet izni süresi 6 ...

### GT07 - announcement

- Soru: Bilgisayar muhendisligindeki son duyurular neler?
- Not: Announcement DB short-circuit ve bolum filtresi.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT07`
- Trace owner: `announcement_search`
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
- Answer length: `exempt/ok; chars=2479; sent=15; bullets=10`
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2016`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT07", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": null, "routing_timeout_suspected": false, "conversation_ms": 11.53, "final_synthesis_ms": null}`
- Cevap preview: İlgili duyurular: 1. 2025-2026 Bahar Yarıyılı Ara Sınav Programı 2025-2026 Bahar Yarıyılı Ara Sınav Programı için tıklayınız.. Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/2025-2026-bahar-yariyili-ara-sinav-programi 2. Vefat Haberi - Öğrencimiz Mahfuz AGİL Ondokuz Mayıs Üniversitesi Bilgisayar Mühendisliği Bölümü son sınıf öğrencilerimizden Mahfuz Agil’in vefatını derin bir üzüntüyle öğrenmiş bulunmaktay… Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/vefat-haberi-ogrencimiz-...

### GT08 - event

- Soru: Bu hafta Muhendislik Fakultesinde seminer var mi?
- Not: Event DB short-circuit ve zaman penceresi.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT08`
- Trace owner: `event_search`
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
- Answer length: `normal/ok; chars=219; sent=3; bullets=1`
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~1990`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT08", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": null, "routing_timeout_suspected": false, "conversation_ms": null, "final_synthesis_ms": null}`
- Cevap preview: Bu sorguya uygun guncel veya yakin tarihli etkinlik bulamadim. Isterseniz fakulte, bolum ya da etkinlik turu belirterek tekrar sorabilirsiniz. Kaynak Özeti: - Veritabanı kaydı: etkinlik araması (uygun kayıt bulunamadı)

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT09`
- Trace owner: `personal_student_data`
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
- Answer length: `normal/ok; chars=180; sent=2; bullets=0`
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4261`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT09", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": 1894.181, "routing_timeout_suspected": false, "conversation_ms": null, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz.

### GT10 - ambiguous

- Soru: Sey basvuru ne zaman?
- Not: Eksik slot/ambiguity davranisi.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT10`
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
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4262`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-GT10", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": 2638.929, "routing_timeout_suspected": false, "conversation_ms": 10.319, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-cap-followup`
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
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=754; sent=3; bullets=10`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3060; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~9828; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1654; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1397`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1935.369, "capability_planner_timeout_suspected": false, "routing_ms": 1780.286, "routing_timeout_suspected": false, "conversation_ms": 8.176, "final_synthesis_ms": 2199.93}`
- Cevap preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB duyuruları ile ilan edilir. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Kayıt İşleri + Mevzuat; Son: Orkestratör Kaynak Özeti: - Belge: yonerge...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-cap-followup`
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
- Provider warning: `retry_history=2`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=643; sent=4; bullets=7`
- Structural checks: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3293; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4268; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3202; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~12017; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1630`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "other"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_current_baai_fp16_contractfix_20260517-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1828.05, "capability_planner_timeout_suspected": false, "routing_ms": 1844.885, "routing_timeout_suspected": false, "conversation_ms": 1693.014, "final_synthesis_ms": 5164.683}`
- Cevap preview: Benchmark, CAP başvurunuz için not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20'sinde bulunması gerekir. Ayrıca, ana dal not ortalamasının 4,00 üzerinden hesaplanması önemlidir. Başvurunun kabul edilmesi için bu koşulların sağlanması şarttır. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Mevzuat + Kayıt İşleri; Son: Ork...
