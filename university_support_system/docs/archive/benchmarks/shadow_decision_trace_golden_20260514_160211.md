# Shadow Decision Trace Golden Run 20260514_160211

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 1
- Trace kaydi: 1
- Source owner eslesmesi: 1/1
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 1
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (88471.0 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260514_160211.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260514_160211.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | academic_programs:regulation_agent/contract | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_improved:repair_improved | - | shadow/pass:clean; tokens=- | - | - | primary_specialist expected=registration_agent actual=student_affairs, regulation_agent | 5 | 74329.9 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=5
- Provider hatalari: -
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 0
- Retry history provider hata sayisi: 0
- Provider hata nedenleri: -
- Retryable provider hata sayisi: 0
- Tahmini input token: 16363 (5 cagrida)
- Prompt/system char: 36530/28930
- Role bazli cagri sayisi: final_refinement=1, global_synthesis=1, judge=1, routing=2
- Role bazli tahmini input token: final_refinement=5962, global_synthesis=1402, judge=1677, routing=7322

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=5 configured_keys=53 used_keys=5
- Key fingerprint cagrilari: {"groq": {"calls": 5, "key_count": 53, "by_fingerprint": {"cc9074971faa": 1, "f1a0600529c4": 1, "fe4490aa7a6a": 1, "c93303cbec45": 1, "5e2c5c185255": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 88471.0, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 88470.9}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `74329.94`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 1 | pass=1 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=1
- Nedenler: required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 1 | pass=0 | check=0 | skipped=1
- Nedenler: not_applicable=1

## Notlar

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260514_160211-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `student_affairs, regulation_agent`
- Specialist selector: `academic_programs:regulation_agent/contract`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_improved:repair_improved`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Structural checks: `primary_specialist expected=registration_agent actual=student_affairs, regulation_agent`
- LLM roles: `routing, final_refinement, judge, global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3049; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~5962; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1677; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1402`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260514_160211-GT04", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2304.945, "capability_planner_timeout_suspected": false, "routing_ms": 1771.038, "routing_timeout_suspected": false, "conversation_ms": 370.497, "final_synthesis_ms": 2250.731}`
- Cevap preview: Benchmark, Yatay geçiş ile gelen öğrencilerin muafiyet başvuru süreci, daha önce öğrenim gördükleri yüksek öğretim kurumlarından veya pedagojik formasyon eğitimi sertifika programından alıp başarılı oldukları derslerden muaf olmak için, kayıt yaptırdıkları öğretim yılının en geç 3. haftasının sonuna kadar Pedagojik Formasyon Birimine başvuruları gerekmektedir. • Muafiyet için başvuru zamanı, akademik takvimde belirtilen tarihlerde yapılır. • Zorunlu hazırlık sınıfından muafiyet için bir akademik yılda güz dönemi başında ve sonunda olmak üzere toplam 2 defa yeterlik sınavı yapılır. Muaf olunan dersler için öğrencilere ücret iadesi yapılmaz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: Kural - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Veritabani kaydi: ogrenci isleri - Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf - Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf - Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf - Belge: yabancı_dil_eğitim_öğretimi_yönergesi.pdf
