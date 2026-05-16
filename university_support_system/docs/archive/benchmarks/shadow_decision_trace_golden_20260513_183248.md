# Shadow Decision Trace Golden Run 20260513_183248

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 12
- Trace kaydi: 15
- Source owner eslesmesi: 10/10
- Hata sayisi: 0
- Answer validator riskli: 1
- Value conflict riskli: 0
- Structural check riskli: 2
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (50713.0 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_183248.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_183248.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | provider_error_seen | 3 | 12367.7 | CHECK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | course.detail | main_orchestrator | academic_programs | academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match | 0 | observed: kept=academic_programs; pruned=-; reason=single_branch | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | - | 3 | 4595.5 | OK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | finance.tuition_fee | main_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | observed: kept=finance; pruned=-; reason=single_branch | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | - | 2 | 6723.7 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/check:answer_missing_required_evidence_values; missing=22.12, 2023, 12 | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted:repair_not_worse | - | - | - | 5 | 16047.9 | CHECK |
| GT05 | cross_department | - | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs, finance | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match; finance:tuition_agent/task_type, legacy=tuition_agent:match | 0 | observed: kept=academic_programs, student_affairs, finance; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted:repair_not_worse | - | - | - | 5 | 14272.4 | OK |
| GT06 | international_policy | international_policy | international_policy | international.policy_lookup | main_orchestrator | academic_programs | academic_programs:international_agent/contract, legacy=international_agent:match | 0 | applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted:repair_not_worse | - | - | - | 5 | 8822.8 | OK |
| GT07 | announcement | announcement_search | announcement_search | - | announcement_agent | announcement | - | 0 | - | - | - | - | - | - | - | - | 1 | 1756.5 | OK |
| GT08 | event | event_search | event_search | - | event_agent | event | - | 0 | - | - | - | - | - | - | - | - | 1 | 1516.7 | OK |
| GT09 | personal_auth | personal_student_data | personal_student_data | - | clarification | finance | - | 0 | - | - | - | - | - | - | - | - | 1 | 1350.6 | OK |
| GT10 | ambiguous | - | - | - | clarification | - | - | 0 | - | - | - | - | - | - | - | - | 1 | 1745.9 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted:repair_not_worse | - | - | - | 5 | 16075.4 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=3,00; competing=- | judge:accept; approved=True | 3,00 | - | provider_error_seen | 5 | 18282.6 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=37
- Provider hatalari: groq=2
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 2
- Retry history provider hata sayisi: 6
- Provider hata nedenleri: rate_limit=8
- Retryable provider hata sayisi: 8
- Tahmini input token: 94779 (37 cagrida)
- Prompt/system char: 103596/275581
- Role bazli cagri sayisi: conversation=1, final_refinement=3, global_synthesis=7, judge=5, routing=20, specialist_synthesis=1
- Role bazli tahmini input token: conversation=3351, final_refinement=4004, global_synthesis=12464, judge=5636, routing=69131, specialist_synthesis=193

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=37 configured_keys=53 used_keys=32
- Key fingerprint cagrilari: {"groq": {"calls": 37, "key_count": 53, "by_fingerprint": {"19f91860a589": 1, "26a01be4304a": 1, "39659184e1c2": 1, "fcb1af18c173": 1, "fabc86c419a2": 1, "f93b795d2a95": 1, "c93303cbec45": 2, "897ea1ca897e": 2, "5150f63f1a64": 2, "64ee113faff7": 2, "7ebf4c926f8e": 2, "1f75827ea381": 1, "5e2c5c185255": 1, "2075f8b244dc": 1, "051f59a11b93": 1, "7428d4dce055": 1, "c1adddf49f35": 1, "d16ee01d06f1": 1, "24b9652705b1": 1, "64aeba5d5c98": 1, "c6e82d5f9ef2": 1, "a3e421be002a": 1, "98aa7a677e13": 1, "34d6c1f77423": 1, "eb9aad1d76ad": 1, "d427d6dcc70e": 1, "928ce4d0b4ba": 1, "70bc5df1936d": 1, "2eb4f14b6ad5": 1, "1d6935952e9a": 1, "cc1a6102eca9": 1, "5636cc6375b7": 1}}}
- Provider org fingerprintleri: 1916381c41ac=1, 68edacd4ded0=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 50713.0, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 50712.9}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `12367.71`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 8 | pass=7 | check=1 | fail=0 | requires_judge=1 | contract_enforceable=0
- Nedenler: answer_missing_required_evidence_values=1, no_evidence_claims=2, no_query_relevant_required_values=1, query_does_not_require_value_check=2, required_values_preserved=2

## Value Conflict Ozeti

- Kayit: 8 | pass=1 | check=0 | skipped=7
- Nedenler: not_applicable=7, single_primary_threshold=1

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260513_183248-GT01-retry1`
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
- Structural checks: `provider_error_seen`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4265; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2337; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1187`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_183248-GT01", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_183248-GT01-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 4329.316, "capability_planner_timeout_suspected": false, "routing_ms": 6399.989, "routing_timeout_suspected": false, "conversation_ms": 7.616, "final_synthesis_ms": 1156.824}`
- Cevap preview: Benchmark, Öğrenci işleri departamento göre genel akademik takvime göre yarıyıl sonu/final sınavları güz dönemi için 03-16 Ocak 2026, bahar dönemi için 01-14 Haziran 2026 tarihlerindedir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - VT - Routing: direct - Pipeline: student_affairs -> orchestrator Kaynak Özeti: - Belge: C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\data\raw\student_affairs\takvimler\2025_2026_genel_akademik_takvim.pdf

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-20260513_183248-GT02-retry1`
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
- Structural checks: `-`
- LLM roles: `routing, specialist_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4267; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2692; groq/llama-3.3-70b-versatile/specialist_synthesis/primary/success/in_tok~193`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_183248-GT02", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_183248-GT02-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1507.541, "capability_planner_timeout_suspected": false, "routing_ms": 1971.556, "routing_timeout_suspected": false, "conversation_ms": 8.612, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, BIL203 dersinin AKTS kredisinin 5 oldugu ve ön koşulunun BIL104 - Programlamaya Giris II oldugu belirlenmistir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - VT - Routing: direct - Pipeline: academic_programs

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-20260513_183248-GT03`
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
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2175`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_183248-GT03", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 4919.982, "capability_planner_timeout_suspected": false, "routing_ms": 1709.544, "routing_timeout_suspected": false, "conversation_ms": 7.145, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Routing: direct - Pipeline: finance Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260513_183248-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/check:answer_missing_required_evidence_values; missing=22.12, 2023, 12`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted:repair_not_worse`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3034; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2227; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1219; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1280`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_183248-GT04", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1904.489, "capability_planner_timeout_suspected": false, "routing_ms": 1902.153, "routing_timeout_suspected": false, "conversation_ms": 7.211, "final_synthesis_ms": 1753.571}`
- Cevap preview: Benchmark, Yatay geçişle gelen öğrenciler, eğitim öğretimin başladığı tarihten itibaren üç hafta içinde daha önce öğrenim gördüğü yükseköğretim kurumlarında aldığı ve başarılı olduğu dersler için muafiyet başvurusunda bulunabilir. • Başvurular, derslerin muaf olunan karşılıklarını içeren bir dilekçe, onaylı transkript ve onaylı ders içerikleriyle birlikte ilgili birime yapılır. • Muafiyet kararı alınana kadar, başvuruda bulunulan derslere kayıt yaptırıp devam edilmesi gerekebilir. Bu süre içinde muafiyet talebinin uygun görülmesi ve muaf olunan derslerin sisteme işlenmesi sonrasında, öğrenci danışmanı ile birlikte alumnoğuz Derslere kaydınızı yaptırabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: sık_sorulan_sorular.txt (3 parça) - ...

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-20260513_183248-GT05`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent, tuition_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match; finance:tuition_agent/task_type, legacy=tuition_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs, finance; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=3; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted:repair_not_worse`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3140; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2077; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1587; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1292`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_183248-GT05", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1664.284, "capability_planner_timeout_suspected": false, "routing_ms": 1448.379, "routing_timeout_suspected": false, "conversation_ms": 5.137, "final_synthesis_ms": 3323.468}`
- Cevap preview: Benchmark, ÇAP başvurularında ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması ve önlisans için 120 AKTS, lisans için 240 AKTS şartını yerine getirmek gerekir. Ayrıca, ÇAP'a kayıtlı öğrencilerin bu programları tamamlamaları için, ana dal programında olan dersler dışında, ilgili ÇAP açan bölümce verilen en az 40, en çok 60 kredi ders almaları gerekir. Öğrenci harcınızı ödemek için yıllık ücret 2.397,00 TL, dönemlik ücret 1.198,50 TL'dir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Finans: VT - Routing: parallel - Pipeline: academic_programs -> student_affairs -> finance -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (5 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf - Belge: sık_sorulan_sorular.txt - Veritabani kaydi: ogrenim ucreti tablosu

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-20260513_183248-GT06`
- Trace owner: `international_policy`
- Capability: `international.policy_lookup`
- Selected specialists: `international_agent`
- Specialist selector: `academic_programs:international_agent/contract, legacy=international_agent:match`
- Branch gate: `applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=academic_programs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted:repair_not_worse`
- Structural checks: `-`
- LLM roles: `routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3045; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1730; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~867; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1087`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_183248-GT06", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1983.531, "capability_planner_timeout_suspected": false, "routing_ms": 1492.82, "routing_timeout_suspected": false, "conversation_ms": 29.051, "final_synthesis_ms": 1225.242}`
- Cevap preview: Benchmark, Yabancı öğrenci olarak kayıt yaptırmak içine belgelerin teslim edilmesi ve kayıt koşullarına uymak gerekmektedir. Kayıt işlemlerine ve koşullarına uluslararası öğrenci alım kılavuzunda yer verilerek, Üniversite'nin ilgili web sayfalarında duyurulur. Kayıt için gerekli belgeler, Senato tarafından belirlenir. İkamet izni başvurusu için ise, • Pasaportun kimlik bilgilerinin yer aldığı ilk sayfa ile varsa vizenin bulunduğu sayfa ve ülkeye giriş yaptığı en son damganın yer aldığı sayfa, her biri ayrı sayfada olacak şekilde fotokopileri, • Talep edilen ikamet izni süresinden 60 gün daha uzun süreli pasaport ya da pasaport yerine geçen belgeye sahip olmak, • Öğrencilik durumunu gösteren belge gereklidir. Üretim Türü: - Final Sentez: LLM - RAG - Routing: parallel - Pipeline: academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_uluslararasi_ogrenci_kabul.pdf - Belge:...

### GT07 - announcement

- Soru: Bilgisayar muhendisligindeki son duyurular neler?
- Not: Announcement DB short-circuit ve bolum filtresi.
- Context: `shadow-golden-20260513_183248-GT07`
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
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~1985`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_183248-GT07", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": null, "routing_timeout_suspected": false, "conversation_ms": 6.039, "final_synthesis_ms": null}`
- Cevap preview: İlgili duyurular: 1. 2025-2026 Bahar Yarıyılı Ara Sınav Programı 2025-2026 Bahar Yarıyılı Ara Sınav Programı için tıklayınız.. Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/2025-2026-bahar-yariyili-ara-sinav-programi 2. Vefat Haberi - Öğrencimiz Mahfuz AGİL Ondokuz Mayıs Üniversitesi Bilgisayar Mühendisliği Bölümü son sınıf öğrencilerimizden Mahfuz Agil’in vefatını derin bir üzüntüyle öğrenmiş bulunmaktay… Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/vefat-haberi-ogrencimiz-mahfuz-agil 3. 2025-26 Bahar Dönemi Lisans Haftalık Ders Programı - (Güncellendi) 2025–2026 Bahar Dönemi Lisans Haftalık Ders Programı yayımlanmıştır. Son güncelleme 11.02.2026 Ders programını görüntülemek için tıklayınız Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/2025-2026-egitim-ogretim-yili-bahar-yariyili-lisans-haftalik-ders-programi 4. 2025-2026 Eğitim-Öğretim Yılı Tek Ders Sınav...

### GT08 - event

- Soru: Bu hafta Muhendislik Fakultesinde seminer var mi?
- Not: Event DB short-circuit ve zaman penceresi.
- Context: `shadow-golden-20260513_183248-GT08`
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
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~1959`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_183248-GT08", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": null, "routing_timeout_suspected": false, "conversation_ms": null, "final_synthesis_ms": null}`
- Cevap preview: Bu sorguya uygun guncel veya yakin tarihli etkinlik bulamadim. Isterseniz fakulte, bolum ya da etkinlik turu belirterek tekrar sorabilirsiniz. Kaynak Özeti: - Veritabanı kaydı: etkinlik araması (uygun kayıt bulunamadı)

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-20260513_183248-GT09`
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
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4261`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_183248-GT09", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": 1324.59, "routing_timeout_suspected": false, "conversation_ms": null, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz.

### GT10 - ambiguous

- Soru: Sey basvuru ne zaman?
- Not: Eksik slot/ambiguity davranisi.
- Context: `shadow-golden-20260513_183248-GT10`
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
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4262`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_183248-GT10", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": 1703.987, "routing_timeout_suspected": false, "conversation_ms": 7.008, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_183248-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted:repair_not_worse`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2976; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2152; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~908; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1197`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_183248-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1672.693, "capability_planner_timeout_suspected": false, "routing_ms": 2041.697, "routing_timeout_suspected": false, "conversation_ms": 7.746, "final_synthesis_ms": 1384.038}`
- Cevap preview: Benchmark, Çift anadal programına başvurmak için bazı koşulları sağlamalısınız. Bu koşullar şunlardır: • Başarı sıralaması şartı aranan programlarda çift anadal yapmak isteyen öğrencinin, kayıt olduğu yıldaki ilgili programın Yükseköğretim Kurulu tarafından belirlenen başarı sıralaması şartını sağlamış olması gerekir. • Aynı anda ikinci ana dal diploma programı ile Yan Dal Programına (YDP) kayıt yapılabilir. • YDP başvurularının değerlendirilmesinde öncelikle ana dal genel not ortalamasına, ortalamanın eşitliği halinde öğrencinin tamamlamış olduğu toplam kredisine bakılır. Toplam kredi sayısının da eşit olması halinde yükseköğretim kurumuna kayıt yapılan yıldaki ÖSYM sıralaması dikkate alınır. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: çift_...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_183248-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/pass:single_primary_threshold; primary=3,00; competing=-`
- Judge repair: `judge:accept; approved=True`
- Structural checks: `provider_error_seen`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/error/in_tok~3351; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4268; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3111; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2239; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1055`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_183248-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_183248-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "conversation", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 1791.853, "capability_planner_timeout_suspected": false, "routing_ms": 5050.664, "routing_timeout_suspected": false, "conversation_ms": 6534.02, "final_synthesis_ms": 1554.254}`
- Cevap preview: Benchmark, ÇAP başvurusu için ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibari ile en az ilk % 20'sinde bulunması gerekir. • Ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması • Başarı sıralaması itibari ile en az ilk % 20'sinde bulunması gerekir Bu şartları sağlayan öğrenciler başvurabilirler. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (2 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (2 parça)
