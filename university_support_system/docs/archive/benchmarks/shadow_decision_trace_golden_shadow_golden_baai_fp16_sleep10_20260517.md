# Shadow Decision Trace Golden Run shadow_golden_baai_fp16_sleep10_20260517

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 12
- Trace kaydi: 14
- Source owner eslesmesi: 9/10
- Hata sayisi: 0
- Answer validator riskli: 1
- Value conflict riskli: 1
- Structural check riskli: 1
- LLM profile: groq_only
- Question cache: bypass
- Warmup mode: none (0.0 ms)
- Provider retry: count=1 backoff=8.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_golden_baai_fp16_sleep10_20260517.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_shadow_golden_baai_fp16_sleep10_20260517.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Retrieval Budget | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Length | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | - | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=649; sent=5; bullets=5 | - | - | - | 3 | 7312.8 | OK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | course.detail | main_orchestrator | academic_programs | academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match | 0 | observed: kept=academic_programs; pruned=-; reason=single_branch | - | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=147; sent=3; bullets=3 | - | - | - | 3 | 3827.8 | OK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | finance.tuition_fee | main_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | observed: kept=finance; pruned=-; reason=single_branch | - | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | retry_history=1 | shadow/pass:clean; tokens=- | normal/ok; chars=359; sent=4; bullets=4 | - | - | - | 2 | 2630.8 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | applied: kept=student_affairs; pruned=academic_programs; reason=calendar_owner_single_branch | - | shadow/pass:required_values_preserved | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | - | shadow/pass:clean; tokens=- | normal/warn; chars=937; sent=5; bullets=7 | - | - | capability expected=student_affairs.policy_lookup actual=calendar.academic_date | 4 | 13550.3 | CHECK |
| GT05 | cross_department | - | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | applied: kept=academic_programs, student_affairs; pruned=finance; reason=answer_contract_cap_debt_policy_gate | support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty; primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | - | shadow/pass:clean; tokens=- | normal/warn; chars=707; sent=5; bullets=8 | - | - | - | 5 | 63356.7 | OK |
| GT06 | international_policy | international_policy | international_policy | international.policy_lookup | main_orchestrator | academic_programs | academic_programs:international_agent/contract, legacy=international_agent:match | 0 | applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch | primary:international_agent:full; searches=1; mqe=0; early=strong_primary_evidence | shadow/pass:no_query_relevant_required_values | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | - | shadow/pass:clean; tokens=- | normal/warn; chars=1258; sent=7; bullets=7 | - | - | - | 5 | 18742.9 | OK |
| GT07 | announcement | announcement_search | announcement_search | - | announcement_agent | announcement | - | 0 | - | - | - | - | - | - | - | shadow/pass:clean; tokens=- | exempt/ok; chars=2479; sent=15; bullets=10 | - | - | - | 1 | 2080.0 | OK |
| GT08 | event | event_search | event_search | - | event_agent | event | - | 0 | - | - | - | - | - | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=219; sent=3; bullets=1 | - | - | - | 1 | 4719.2 | OK |
| GT09 | personal_auth | personal_student_data | personal_student_data | - | clarification | finance | - | 0 | - | - | - | - | - | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=180; sent=2; bullets=0 | - | - | - | 1 | 1677.6 | OK |
| GT10 | ambiguous | - | - | - | clarification | - | - | 0 | - | - | - | - | - | - | - | shadow/pass:clean; tokens=- | normal/ok; chars=164; sent=2; bullets=0 | - | - | - | 1 | 1665.3 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | - | shadow/pass:clean; tokens=- | normal/warn; chars=724; sent=3; bullets=9 | - | - | - | 5 | 17607.6 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty; primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence | shadow/fail:answer_conflicts_with_evidence_values; missing=2,50 | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/check:answer_primary_value_conflicts_with_evidence; primary=3,00; competing=2,50 | repair:rejected_worse:evidence_validation_worsened | retry_history=1 | shadow/pass:clean; tokens=- | normal/warn; chars=603; sent=3; bullets=7 | 3,00 | 2,50 | - | 6 | 31760.8 | FAIL |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=37
- Provider hatalari: -
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 0
- Retry history provider hata sayisi: 2
- Provider hata nedenleri: rate_limit=2
- Retryable provider hata sayisi: 2
- Tahmini input token: 127111 (37 cagrida)
- Prompt/system char: 223748/284751
- Role bazli cagri sayisi: conversation=1, final_refinement=4, global_synthesis=6, judge=5, routing=20, specialist_synthesis=1
- Role bazli tahmini input token: conversation=3333, final_refinement=6692, global_synthesis=38014, judge=8964, routing=69905, specialist_synthesis=203

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=37 configured_keys=53 used_keys=34
- Key fingerprint cagrilari: {"groq": {"calls": 37, "key_count": 53, "by_fingerprint": {"cc9074971faa": 1, "fe4490aa7a6a": 2, "c93303cbec45": 1, "5e2c5c185255": 1, "24b9652705b1": 2, "d427d6dcc70e": 1, "80b7f264cbe2": 1, "2075f8b244dc": 2, "64aeba5d5c98": 1, "928ce4d0b4ba": 1, "5636cc6375b7": 1, "18694d48e7d3": 1, "897ea1ca897e": 1, "051f59a11b93": 1, "c6e82d5f9ef2": 1, "70bc5df1936d": 1, "9ec28f2ad046": 1, "618f51582a5a": 1, "5150f63f1a64": 1, "7428d4dce055": 1, "a3e421be002a": 1, "2eb4f14b6ad5": 1, "fba5c0f29033": 1, "26a01be4304a": 1, "fcb1af18c173": 1, "64ee113faff7": 1, "775f860f28a7": 1, "98aa7a677e13": 1, "1d6935952e9a": 1, "39659184e1c2": 1, "fabc86c419a2": 1, "d16ee01d06f1": 1, "eb9aad1d76ad": 1, "fc02f5c29d71": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `7312.75`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 8 | pass=7 | check=0 | fail=1 | requires_judge=1 | contract_enforceable=4
- Nedenler: answer_conflicts_with_evidence_values=1, no_evidence_claims=2, no_query_relevant_required_values=3, query_does_not_require_value_check=1, required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 8 | pass=0 | check=1 | skipped=7
- Nedenler: answer_primary_value_conflicts_with_evidence=1, not_applicable=7

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT01`
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
- Answer length: `normal/ok; chars=649; sent=5; bullets=5`
- Structural checks: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4265; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2422; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1490`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT01", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 3873.739, "capability_planner_timeout_suspected": false, "routing_ms": 1423.265, "routing_timeout_suspected": false, "conversation_ms": 190.006, "final_synthesis_ms": 1140.535}`
- Cevap preview: Benchmark, Güz dönemi için 03-16 Ocak 2026, bahar dönemi için 01-14 Haziran 2026 tarihleri arasında final sınavları yapılacak. Bu tarihler genel akademik takvime göre belirlenmiştir. Yarıyıl sonu sınavlarına ilişkin cu the tarihler için ilgili akademik takvimleri takip edebilirsin. Bahar ve güz dönemi sınav tarihleri bu şekilde planlanmıştır. Üretim Türü: - Final Sentez: LLM - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Kayıt İşleri -> Orkestratör Kaynak Özeti: - Belge: C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\data\raw\student_affairs\takvimler\2025_2026_genel_akademik_takvim.pdf

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT02`
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
- Answer length: `normal/ok; chars=147; sent=3; bullets=3`
- Structural checks: `-`
- LLM roles: `routing, specialist_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4267; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2775; groq/llama-3.3-70b-versatile/specialist_synthesis/primary/success/in_tok~203`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT02", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1526.34, "capability_planner_timeout_suspected": false, "routing_ms": 1401.958, "routing_timeout_suspected": false, "conversation_ms": 12.061, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, BIL203 dersinin AKTS kredi değeri 5'dir. Ön koşulu BIL104 dersidir. Üretim Türü: - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Müfredat

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT03-retry1`
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
- Provider warning: `retry_history=1`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/ok; chars=359; sent=4; bullets=4`
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2274`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT03", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT03-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1236.315, "capability_planner_timeout_suspected": false, "routing_ms": 1289.57, "routing_timeout_suspected": false, "conversation_ms": 10.223, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Öğrenim Ücreti Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT04`
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
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=937; sent=5; bullets=7`
- Structural checks: `capability expected=student_affairs.policy_lookup actual=calendar.academic_date`
- LLM roles: `routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3102; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~2123; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1909`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT04", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1889.804, "capability_planner_timeout_suspected": false, "routing_ms": 1652.162, "routing_timeout_suspected": false, "conversation_ms": 7.874, "final_synthesis_ms": 1971.105}`
- Cevap preview: Benchmark, Yatay geçiş ile gelen öğrenciler, muafiyet başvurularını Genel akademik takvime göre yapmak zorundadır. • Merkezi yerleştirme puanı (Ek Madde-1) için başvurular 01.08.2025 – 06.08.2025 tarihleri arasında yapılmalıdır. • Kurumlar arası/kurum içi yatay geçiş başvuruları ise 01.08.2025 – 15.08.2025 tarihleri arasında yapılmalıdır. Bahar yarıyılı için on lisans yatay geçiş başvuruları 26.01.2026 – 01.02.2026 tarihleri arasındadır. Üretim Türü: - Final Sentez: LLM - VT - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Kayıt İşleri; Son: Orkestratör Kaynak Özeti: - Belge: C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\data\raw\st...

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT05`
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
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=707; sent=5; bullets=8`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3236; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~11509; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1846; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1361`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT05", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2309.084, "capability_planner_timeout_suspected": false, "routing_ms": 2177.843, "routing_timeout_suspected": false, "conversation_ms": 13.858, "final_synthesis_ms": 2292.928}`
- Cevap preview: Benchmark, Çift Ana Dal Programı (ÇAP) başvuruları için ana dal not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. Başvuru koşulları ana dal not ortalaması ve tamamlanmış kredi sayısı esas alınarak belirlenir. Harc borcunuzu Banka ilgili ödeme kanalı'leri veya internet bankacılığı üzerinden ödeyebilirsiniz. İlgili birimden doğrulama yapmanız önerilir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Mevzuat + Kayıt İşleri; Son: Orkestratör Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça) - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: ön_lisans_ve_lis...

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT06`
- Trace owner: `international_policy`
- Capability: `international.policy_lookup`
- Selected specialists: `international_agent`
- Specialist selector: `academic_programs:international_agent/contract, legacy=international_agent:match`
- Branch gate: `applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=academic_programs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_neutral:repair_not_worse`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=1258; sent=7; bullets=7`
- Structural checks: `-`
- LLM roles: `routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3125; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1977; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1404; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1102`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT06", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2786.843, "capability_planner_timeout_suspected": false, "routing_ms": 8028.406, "routing_timeout_suspected": false, "conversation_ms": 17.691, "final_synthesis_ms": 1951.248}`
- Cevap preview: Benchmark, Yabancı öğrenci olarak kayıt ve ikamet izni alma süreci için gerekli evraklar arasında öğrenci bilgileri, beyan ve kabul taahhütnamesi bulunmaktadır. • Öğrenci beyanı ve kabul taahhütnamesinde, Türkiye'de geçireceğiniz öğrencilik sürecinde, Türkiye Cumhuriyeti Devleti tarafından Türkiye'de ikamet eden yabancılar için belirlenmiş tüm yasalara ve Ondokuz Mayıs Üniversitesinin kurallarına uyacağınızı beyan edeceksiniz. • İkamet izni alma süreci için gerekli belgeler ve prosedürler ise uluslararası öğrenci yönergeleri çerçevesinde belirlenir. Kayıt ve ikamet izni başvuru süreci ile ilgili ayrıntılı bilgi için, Ondokuz Mayıs Üniversitesi'nin ilgili birimleri ile irtibata geçebilirsin...

### GT07 - announcement

- Soru: Bilgisayar muhendisligindeki son duyurular neler?
- Not: Announcement DB short-circuit ve bolum filtresi.
- Context: `shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT07`
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
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT07", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": null, "routing_timeout_suspected": false, "conversation_ms": 7.553, "final_synthesis_ms": null}`
- Cevap preview: İlgili duyurular: 1. 2025-2026 Bahar Yarıyılı Ara Sınav Programı 2025-2026 Bahar Yarıyılı Ara Sınav Programı için tıklayınız.. Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/2025-2026-bahar-yariyili-ara-sinav-programi 2. Vefat Haberi - Öğrencimiz Mahfuz AGİL Ondokuz Mayıs Üniversitesi Bilgisayar Mühendisliği Bölümü son sınıf öğrencilerimizden Mahfuz Agil’in vefatını derin bir üzüntüyle öğrenmiş bulunmaktay… Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/vefat-haberi-ogrencimiz-mahfuz-agil 3. 2025-26 Bahar Dönemi Lisans Haftalık Ders Programı - (Güncellendi) 2025–2026 Bahar Dönemi Lisans Haftalık Ders Programı yayımlanmıştır. Son güncelleme 11.02.2026 Ders programını görünt...

### GT08 - event

- Soru: Bu hafta Muhendislik Fakultesinde seminer var mi?
- Not: Event DB short-circuit ve zaman penceresi.
- Context: `shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT08`
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
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT08", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": null, "routing_timeout_suspected": false, "conversation_ms": null, "final_synthesis_ms": null}`
- Cevap preview: Bu sorguya uygun guncel veya yakin tarihli etkinlik bulamadim. Isterseniz fakulte, bolum ya da etkinlik turu belirterek tekrar sorabilirsiniz. Kaynak Özeti: - Veritabanı kaydı: etkinlik araması (uygun kayıt bulunamadı)

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT09`
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
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT09", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": 1616.527, "routing_timeout_suspected": false, "conversation_ms": null, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz.

### GT10 - ambiguous

- Soru: Sey basvuru ne zaman?
- Not: Eksik slot/ambiguity davranisi.
- Context: `shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT10`
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
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-GT10", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": 1624.788, "routing_timeout_suspected": false, "conversation_ms": 7.116, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-cap-followup`
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
- Answer length: `normal/warn; chars=724; sent=3; bullets=9`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3060; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~10330; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1776; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1390`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2165.744, "capability_planner_timeout_suspected": false, "routing_ms": 1592.211, "routing_timeout_suspected": false, "conversation_ms": 16.378, "final_synthesis_ms": 2793.939}`
- Cevap preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB duyuruları ile ilan edilir. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Kayıt İşleri + Mevzuat; Son: Orkestratör Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: yonerge_onlisans_lisans_yatay_gecis.pdf - Belge: bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf (2 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_da...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/fail:answer_conflicts_with_evidence_values; missing=2,50`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/check:answer_primary_value_conflicts_with_evidence; primary=3,00; competing=2,50`
- Judge repair: `repair:rejected_worse:evidence_validation_worsened`
- Provider warning: `retry_history=1`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=603; sent=3; bullets=7`
- Structural checks: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3333; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3224; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~12071; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~2029; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1353`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_baai_fp16_sleep10_20260517-cap-followup", "status": "FAIL", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 7893.011, "capability_planner_timeout_suspected": false, "routing_ms": 1838.904, "routing_timeout_suspected": false, "conversation_ms": 1808.074, "final_synthesis_ms": 8776.42}`
- Cevap preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB duyuruları ile ilan edilir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Mevzuat + Kayıt İşleri; Son: Orkestratör Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (3 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (4 parça)
