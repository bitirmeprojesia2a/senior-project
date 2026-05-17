# Shadow Decision Trace Golden Run shadow_golden_gt05_payment_coverage_20260517

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
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_golden_gt05_payment_coverage_20260517.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_shadow_golden_gt05_payment_coverage_20260517.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Retrieval Budget | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Length | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT05 | cross_department | - | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs, finance | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match; finance:tuition_agent/task_type, legacy=tuition_agent:match | 0 | observed: kept=academic_programs, student_affairs, finance; pruned=-; reason=student_affairs_policy_contract_gate | support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty; primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:tuition_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/pass:no_query_relevant_required_values | shadow/check:payment_process:answer_missing_payment_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=3; retry_history=4 | shadow/pass:clean; tokens=- | normal/warn; chars=689; sent=3; bullets=9 | - | - | provider_retryable_error_seen; provider_error_seen | 7 | 74713.5 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=4, google_ai=3
- Provider hatalari: groq=3, google_ai=1
- Fallback cagrilari: 3
- Final attempt provider hata sayisi: 4
- Retry history provider hata sayisi: 4
- Provider hata nedenleri: other=2, rate_limit=6
- Retryable provider hata sayisi: 7
- Tahmini input token: 47606 (7 cagrida)
- Prompt/system char: 141124/49313
- Role bazli cagri sayisi: global_synthesis=2, judge=2, routing=3
- Role bazli tahmini input token: global_synthesis=32218, judge=3608, routing=11780

## API Key Dagilimi

- Provider/key dagilimi: google_ai: calls=3 configured_keys=16 used_keys=3, groq: calls=4 configured_keys=53 used_keys=4
- Key fingerprint cagrilari: {"groq": {"calls": 4, "key_count": 53, "by_fingerprint": {"fe4490aa7a6a": 1, "5e2c5c185255": 1, "75d046119efe": 1, "fc02f5c29d71": 1}}, "google_ai": {"calls": 3, "key_count": 16, "by_fingerprint": {"c483e5bb9a2e": 1, "ed72a4ecf461": 1, "aac8ead26ad8": 1}}}
- Provider org fingerprintleri: 36ac290f66aa=2, ed0dc161a99b=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `74713.53`
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
- Context: `shadow-golden-shadow_golden_gt05_payment_coverage_20260517-GT05`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent, tuition_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match; finance:tuition_agent/task_type, legacy=tuition_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs, finance; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=3; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/check:payment_process:answer_missing_payment_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=3; retry_history=4`
- Answer quality: `shadow/pass:clean; tokens=-`
- Answer length: `normal/warn; chars=689; sent=3; bullets=9`
- Structural checks: `provider_retryable_error_seen; provider_error_seen`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4272; google_ai/gemini-3-flash-preview/routing/fallback/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3236; groq/llama-3.3-70b-versatile/global_synthesis/primary/error/in_tok~16109; google_ai/gemini-3-flash-preview/global_synthesis/fallback/success/in_tok~16109; groq/llama-3.3-70b-versatile/judge/primary/error/in_tok~1804; google_ai/gemini-3-flash-preview/judge/fallback/error/in_tok~1804`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-shadow_golden_gt05_payment_coverage_20260517-GT05", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}, {"provider": "groq", "role": "judge", "reason": "rate_limit"}, {"provider": "google_ai", "role": "judge", "reason": "other"}]}]`
- Timeout signals: `{"capability_planner_ms": 4215.085, "capability_planner_timeout_suspected": false, "routing_ms": 8974.46, "routing_timeout_suspected": false, "conversation_ms": 149.646, "final_synthesis_ms": 9346.701}`
- Cevap preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB duyuruları ile ilan edilir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Finans: RAG - Çalışma biçimi: Paralel - Ajan akışı: Paralel: Mevzuat + Kayıt İşleri + Öğrenim Ücreti; Son: Orkestratör Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça) - Belge: yonerge_cift_anadal_yandal.pdf (8 parça) - Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
