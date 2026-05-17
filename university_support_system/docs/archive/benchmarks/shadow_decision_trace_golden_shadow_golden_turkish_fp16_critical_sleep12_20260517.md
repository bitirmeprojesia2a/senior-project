# Shadow Decision Trace Golden Run shadow_golden_turkish_fp16_critical_sleep12_20260517

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 6
- Trace kaydi: 11
- Source owner eslesmesi: 4/5
- Hata sayisi: 0
- Answer validator riskli: 1
- Value conflict riskli: 1
- Structural check riskli: 3
- LLM profile: groq_only
- Question cache: bypass
- Warmup mode: none (0.0 ms)
- Provider retry: count=1 backoff=8.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_golden_turkish_fp16_critical_sleep12_20260517.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_shadow_golden_turkish_fp16_critical_sleep12_20260517.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Retrieval Budget | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Length | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | finance.tuition_fee | main_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | observed: kept=finance; pruned=-; reason=single_branch | - | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | retry_history=1 | shadow/pass:clean; tokens=- | normal/ok; chars=359; sent=4; bullets=4 | - | - | - | 2 | 3589.8 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | applied: kept=student_affairs; pruned=academic_programs; reason=calendar_owner_single_branch | - | shadow/pass:required_values_preserved | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | final_retryable=1; retry_history=3 | shadow/pass:clean; tokens=- | normal/warn; chars=931; sent=4; bullets=8 | - | - | capability expected=student_affairs.policy_lookup actual=calendar.academic_date; provider_retryable_error_seen; provider_error_seen | 6 | 16863.5 | CHECK |
| GT05 | cross_department | - | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | applied: kept=student_affairs, academic_programs; pruned=finance; reason=answer_contract_cap_debt_policy_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | retry_history=2 | shadow/pass:clean; tokens=- | normal/warn; chars=916; sent=4; bullets=8 | - | - | - | 5 | 14018.9 | OK |
| GT06 | international_policy | international_policy | international_policy | international.policy_lookup | main_orchestrator | academic_programs | academic_programs:international_agent/contract, legacy=international_agent:match | 0 | applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch | primary:international_agent:full; searches=1; mqe=0; early=strong_primary_evidence | shadow/pass:no_query_relevant_required_values | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | - | shadow/pass:clean; tokens=- | normal/warn; chars=1165; sent=5; bullets=10 | - | - | - | 5 | 11379.1 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | final_retryable=1; retry_history=2 | shadow/pass:clean; tokens=- | normal/warn; chars=724; sent=3; bullets=9 | - | - | provider_retryable_error_seen | 5 | 29776.8 | CHECK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty; primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence | shadow/fail:answer_conflicts_with_evidence_values; missing=2,50 | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/check:answer_primary_value_conflicts_with_evidence; primary=3,00; competing=2,50 | repair:accepted_improved:repair_improved | final_retryable=1; retry_history=4 | shadow/pass:clean; tokens=- | normal/warn; chars=556; sent=3; bullets=6 | 3,00 | 2,50 | provider_retryable_error_seen; provider_error_seen | 7 | 23088.8 | FAIL |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=27, google_ai=3
- Provider hatalari: groq=3, google_ai=2
- Fallback cagrilari: 3
- Final attempt provider hata sayisi: 5
- Retry history provider hata sayisi: 12
- Provider hata nedenleri: other=6, rate_limit=11
- Retryable provider hata sayisi: 15
- Tahmini input token: 128321 (30 cagrida)
- Prompt/system char: 316307/197022
- Role bazli cagri sayisi: conversation=1, final_refinement=4, global_synthesis=7, judge=5, routing=13
- Role bazli tahmini input token: conversation=3293, final_refinement=9349, global_synthesis=60219, judge=9039, routing=46421

## API Key Dagilimi

- Provider/key dagilimi: google_ai: calls=3 configured_keys=16 used_keys=3, groq: calls=27 configured_keys=53 used_keys=21
- Key fingerprint cagrilari: {"groq": {"calls": 27, "key_count": 53, "by_fingerprint": {"24b9652705b1": 2, "d427d6dcc70e": 1, "5636cc6375b7": 1, "18694d48e7d3": 1, "897ea1ca897e": 1, "051f59a11b93": 1, "c6e82d5f9ef2": 1, "a3e421be002a": 2, "2eb4f14b6ad5": 2, "fba5c0f29033": 2, "26a01be4304a": 1, "fcb1af18c173": 1, "64ee113faff7": 2, "775f860f28a7": 2, "98aa7a677e13": 1, "1d6935952e9a": 1, "2ba462e17db4": 1, "1f75827ea381": 1, "eb9aad1d76ad": 1, "2075f8b244dc": 1, "5150f63f1a64": 1}}, "google_ai": {"calls": 3, "key_count": 16, "by_fingerprint": {"aac8ead26ad8": 1, "79cca093f2c6": 1, "1d5cad59f0ab": 1}}}
- Provider org fingerprintleri: 36ac290f66aa=1, 59386eb18df7=1, 9670657e8ae2=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `3589.77`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 6 | pass=5 | check=0 | fail=1 | requires_judge=1 | contract_enforceable=4
- Nedenler: answer_conflicts_with_evidence_values=1, no_evidence_claims=1, no_query_relevant_required_values=2, query_does_not_require_value_check=1, required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 6 | pass=0 | check=1 | skipped=5
- Nedenler: answer_primary_value_conflicts_with_evidence=1, not_applicable=5

## Notlar

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-GT03-retry1`
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
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2275`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-GT03", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-GT03-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1473.505, "capability_planner_timeout_suspected": false, "routing_ms": 1981.609, "routing_timeout_suspected": false, "conversation_ms": 6.64, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Öğrenim Ücreti Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-GT04-retry1`
- Trace owner: `academic_calendar`
- Capability: `calendar.academic_date`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `applied: kept=student_affairs; pruned=academic_programs; reason=calendar_owner_single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_neutral:repair_not_worse`
- Provider warning: `final_retryable=1; retry_history=3`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=931; sent=4; bullets=8`
- Structural checks: `capability expected=student_affairs.policy_lookup actual=calendar.academic_date; provider_retryable_error_seen; provider_error_seen`
- LLM roles: `routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~3115; google_ai/gemini-3-flash-preview/routing/fallback/error/in_tok~3115; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~2130; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1931; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1077`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-GT04", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-GT04-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "google_ai", "role": "routing", "reason": "other"}]}]`
- Timeout signals: `{"capability_planner_ms": 9149.739, "capability_planner_timeout_suspected": false, "routing_ms": 2004.016, "routing_timeout_suspected": false, "conversation_ms": 29.056, "final_synthesis_ms": 1663.819}`
- Cevap preview: Benchmark, Yatay geçiş ile gelen öğrenciler, muafiyet başvurularını akademik takvimde belirtilen tarihlerde yapmalıdır. • Merkezi yerleştirme puanı (Ek Madde-1) için 01.08.2025 – 06.08.2025, • Kurumlar arası/kurum içi için 01.08.2025 – 15.08.2025, • Bahar yarıyılı için 26.01.2026 – 01.02.2026 tarihleri arasında başvurular yapılacaktır. Bu başvurular için gerekli belgelerin tam listesi öğrenci işleri biriminden öğrenilebilecektir. Üretim Türü: - Final Sentez: LLM - VT - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Kayıt İşleri; Son: Orkestratör Kaynak Özeti: - Belge: C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\data\raw\student_...

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-GT05-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `applied: kept=student_affairs, academic_programs; pruned=finance; reason=answer_contract_cap_debt_policy_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_neutral:repair_not_worse`
- Provider warning: `retry_history=2`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=916; sent=4; bullets=8`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2916; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~11505; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1863; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1370`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-GT05", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "other"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-GT05-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1849.888, "capability_planner_timeout_suspected": false, "routing_ms": 1927.734, "routing_timeout_suspected": false, "conversation_ms": 16.353, "final_synthesis_ms": 2257.251}`
- Cevap preview: Benchmark, ÇAP başvuruları için ana dal programında mezuniyet hakkını elde eden ve ÇAP’ı başarıyla tamamlayan öğrenciye ayrıca ikinci ana dalı yaptığı bölümün lisans diploması verilir. Öğrencinin ÇAP’tan mezun olabilmesi için ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması ve önlisans için 120 AKTS, lisans için 240 AKTS şartını yerine getirmesi gerekir. Harc borcu ödeme koşullarıyla ilgili olarak kaynaklarda net bilgi bulunamadığından bu konuda yardım alabilmek için ilgili sekreterin iletişim bilgilerini paylaşabilirim. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Kayıt İşleri + Mevzuat; ...

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-GT06`
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
- Answer length: `normal/warn; chars=1165; sent=5; bullets=10`
- Structural checks: `-`
- LLM roles: `routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3116; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~4856; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1438; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1286`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-GT06", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2356.531, "capability_planner_timeout_suspected": false, "routing_ms": 1837.895, "routing_timeout_suspected": false, "conversation_ms": 18.001, "final_synthesis_ms": 1658.329}`
- Cevap preview: Benchmark, Yabancı öğrenci olarak kayıt için Senato tarafından belirlenen kesin kayıt belgelerini teslim etmeniz ve ön kayıtlarınızı kesin kayda dönüştürmeniz zorunludur. İkamet izni başvuru süreci ile ilgili olarak, Türkiye'de geçireceğiniz öğrencilik sürecinde Türkiye Cumhuriyeti Devleti tarafından Türkiye'de ikamet eden yabancılar için belirlenmiş yasalara ve Ondokuz Mayıs Üniversitesinin kurallarına uymayı taahhüt etmeniz gerekmektedir. • Öğrenci işleri daire başkanlığına şahsen başvurmanız, • Senato tarafından belirlenen kayıt belgelerini teslim etmeniz, • Ön kayıtlarınızı kesin kayda dönüştürmeniz gerekmektedir. Kayıt belgelerinin teslim edilmesi ve ön kayıtların kesin kayda dönüştü...

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-cap-followup-retry1`
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
- Provider warning: `final_retryable=1; retry_history=2`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=724; sent=3; bullets=9`
- Structural checks: `provider_retryable_error_seen`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3060; groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~10148; google_ai/gemini-3-flash-preview/global_synthesis/fallback/success/in_tok~10148; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1830`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "judge", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-cap-followup-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 5672.409, "capability_planner_timeout_suspected": false, "routing_ms": 4752.992, "routing_timeout_suspected": false, "conversation_ms": 10.477, "final_synthesis_ms": 10873.523}`
- Cevap preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB duyuruları ile ilan edilir. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Kayıt İşleri + Mevzuat; Son: Orkestratör Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: yonerge_onlisans_lisans_yatay_gecis.pdf - Belge: bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf (2 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_da...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-cap-followup-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/fail:answer_conflicts_with_evidence_values; missing=2,50`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/check:answer_primary_value_conflicts_with_evidence; primary=3,00; competing=2,50`
- Judge repair: `repair:accepted_improved:repair_improved`
- Provider warning: `final_retryable=1; retry_history=4`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=556; sent=3; bullets=6`
- Structural checks: `provider_retryable_error_seen; provider_error_seen`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3293; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4268; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3202; groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~12827; google_ai/gemini-3-flash-preview/global_synthesis/fallback/error/in_tok~12827; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1977; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1394`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-cap-followup-retry1", "status": "FAIL", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "other"}]}, {"attempt": 2, "context_id": "shadow-golden-shadow_golden_turkish_fp16_critical_sleep12_20260517-cap-followup-retry1", "status": "FAIL", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}, {"provider": "google_ai", "role": "global_synthesis", "reason": "other"}]}]`
- Timeout signals: `{"capability_planner_ms": 2461.487, "capability_planner_timeout_suspected": false, "routing_ms": 4817.632, "routing_timeout_suspected": false, "conversation_ms": 1836.841, "final_synthesis_ms": 2894.167}`
- Cevap preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB duyuruları ile ilan edilir. Üretim Türü: - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Çalışma biçimi: Paralel - Ajan akışı: Mevzuat + Kayıt İşleri Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (5 parça)
