# Shadow Decision Trace Golden Run shadow_golden_gt05_payment_split_20260517

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 1
- Trace kaydi: 1
- Source owner eslesmesi: 0/0
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 1
- LLM profile: groq_only
- Question cache: bypass
- Warmup mode: none (0.0 ms)
- Provider retry: count=0 backoff=0.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_golden_gt05_payment_split_20260517.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_shadow_golden_gt05_payment_split_20260517.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Retrieval Budget | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Length | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT05 | cross_department | - | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, finance, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; finance:tuition_agent/task_type, legacy=tuition_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, finance, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty; support:tuition_agent:lite; searches=1; mqe=0; early=not_primary_or_empty; primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | final_retryable=2; retry_history=2 | shadow/pass:clean; tokens=- | normal/warn; chars=747; sent=3; bullets=10 | - | - | provider_retryable_error_seen | 6 | 107233.9 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=4, google_ai=2
- Provider hatalari: groq=2
- Fallback cagrilari: 2
- Final attempt provider hata sayisi: 2
- Retry history provider hata sayisi: 2
- Provider hata nedenleri: rate_limit=4
- Retryable provider hata sayisi: 4
- Tahmini input token: 45799 (6 cagrida)
- Prompt/system char: 135583/47624
- Role bazli cagri sayisi: global_synthesis=2, judge=1, routing=3
- Role bazli tahmini input token: global_synthesis=32228, judge=1785, routing=11786

## API Key Dagilimi

- Provider/key dagilimi: google_ai: calls=2 configured_keys=16 used_keys=2, groq: calls=4 configured_keys=53 used_keys=4
- Key fingerprint cagrilari: {"groq": {"calls": 4, "key_count": 53, "by_fingerprint": {"fe4490aa7a6a": 1, "5e2c5c185255": 1, "75d046119efe": 1, "955997d77e17": 1}}, "google_ai": {"calls": 2, "key_count": 16, "by_fingerprint": {"c483e5bb9a2e": 1, "ed72a4ecf461": 1}}}
- Provider org fingerprintleri: 36ac290f66aa=1, ed0dc161a99b=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `107233.89`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 1 | pass=1 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=1
- Nedenler: no_query_relevant_required_values=1

## Value Conflict Ozeti

- Kayit: 1 | pass=0 | check=0 | skipped=1
- Nedenler: not_applicable=1

## Notlar

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-shadow_golden_gt05_payment_split_20260517-GT05`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, tuition_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; finance:tuition_agent/task_type, legacy=tuition_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, finance, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=3; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `judge:accept; approved=True`
- Provider warning: `final_retryable=2; retry_history=2`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=747; sent=3; bullets=10`
- Structural checks: `provider_retryable_error_seen`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4272; google_ai/gemini-3-flash-preview/routing/fallback/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3242; groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~16114; google_ai/gemini-3-flash-preview/global_synthesis/fallback/success/in_tok~16114; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1785`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_gt05_payment_split_20260517-GT05", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 6101.319, "capability_planner_timeout_suspected": false, "routing_ms": 10169.759, "routing_timeout_suspected": false, "conversation_ms": 151.563, "final_synthesis_ms": 21732.663}`
- Cevap preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB duyuruları ile ilan edilir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Finans: RAG - Ogrenci Isleri: RAG - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Mevzuat + Öğrenim Ücreti + Kayıt İşleri; Son: Orkestratör Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (8 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (2 parça) - Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf - Belge: bilişim_cihazları_ve_yazılım_alımı_genelgesi.pdf
