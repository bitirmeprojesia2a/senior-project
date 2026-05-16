# Shadow Decision Trace Golden Run 20260513_182814

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 3
- Trace kaydi: 4
- Source owner eslesmesi: 3/3
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (50855.7 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_182814.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_182814.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | - | 3 | 10238.7 | OK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | course.detail | main_orchestrator | academic_programs | academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match | 0 | observed: kept=academic_programs; pruned=-; reason=single_branch | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | - | 3 | 11626.5 | OK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | finance.tuition_fee | main_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | observed: kept=finance; pruned=-; reason=single_branch | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | - | 2 | 3993.9 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=8
- Provider hatalari: -
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 0
- Retry history provider hata sayisi: 3
- Provider hata nedenleri: rate_limit=3
- Retryable provider hata sayisi: 3
- Tahmini input token: 21384 (8 cagrida)
- Prompt/system char: 11172/74379
- Role bazli cagri sayisi: final_refinement=1, routing=6, specialist_synthesis=1
- Role bazli tahmini input token: final_refinement=1187, routing=20005, specialist_synthesis=192

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=8 configured_keys=53 used_keys=8
- Key fingerprint cagrilari: {"groq": {"calls": 8, "key_count": 53, "by_fingerprint": {"26a01be4304a": 1, "39659184e1c2": 1, "76f4cfb21ed4": 1, "fe4490aa7a6a": 1, "618f51582a5a": 1, "fcb1af18c173": 1, "fabc86c419a2": 1, "f93b795d2a95": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 50855.7, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 50855.6}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `10238.72`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 3 | pass=3 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: no_evidence_claims=2, no_query_relevant_required_values=1

## Value Conflict Ozeti

- Kayit: 3 | pass=0 | check=0 | skipped=3
- Nedenler: not_applicable=3

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260513_182814-GT01-retry1`
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
- Structural checks: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4265; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2337; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1187`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_182814-GT01", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "final_refinement", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_182814-GT01-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1516.193, "capability_planner_timeout_suspected": false, "routing_ms": 6867.849, "routing_timeout_suspected": false, "conversation_ms": 8.427, "final_synthesis_ms": 1344.185}`
- Cevap preview: Benchmark, Final sınavları, güz dönemi için 03-16 Ocak 2026, bahar dönemi için 01-14 Haziran 2026 tarihlerinde yapılacaktır. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - VT - Routing: direct - Pipeline: student_affairs -> orchestrator Kaynak Özeti: - Belge: C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\data\raw\student_affairs\takvimler\2025_2026_genel_akademik_takvim.pdf

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-20260513_182814-GT02`
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
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4267; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2689; groq/llama-3.3-70b-versatile/specialist_synthesis/primary/success/in_tok~192`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_182814-GT02", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 8589.423, "capability_planner_timeout_suspected": false, "routing_ms": 1866.72, "routing_timeout_suspected": false, "conversation_ms": 7.752, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, BIL203 dersinin AKTS kredisini 5 olarak belirlenmistir. BIL203 dersinin ön koşulu BIL104 Programlamaya Giris II'dir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - VT - Routing: direct - Pipeline: academic_programs

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-20260513_182814-GT03`
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
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_182814-GT03", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2023.246, "capability_planner_timeout_suspected": false, "routing_ms": 1829.528, "routing_timeout_suspected": false, "conversation_ms": 6.556, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Routing: direct - Pipeline: finance Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu
