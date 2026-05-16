# Shadow Decision Trace Golden Run 20260514_182641

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 1
- Trace kaydi: 1
- Source owner eslesmesi: 1/1
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: none (0.0 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260514_182641.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260514_182641.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Retrieval Budget | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | primary:registration_agent:full; searches=1; mqe=0; early=strong_primary_evidence; support:regulation_agent:lite; searches=1; mqe=0; early=not_primary_or_empty | shadow/pass:required_values_preserved | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_improved:repair_improved | - | shadow/pass:clean; tokens=- | - | - | - | 5 | 21765.0 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=5
- Provider hatalari: -
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 0
- Retry history provider hata sayisi: 0
- Provider hata nedenleri: -
- Retryable provider hata sayisi: 0
- Tahmini input token: 20539 (5 cagrida)
- Prompt/system char: 53239/28930
- Role bazli cagri sayisi: global_synthesis=2, judge=1, routing=2
- Role bazli tahmini input token: global_synthesis=11774, judge=1451, routing=7314

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=5 configured_keys=53 used_keys=5
- Key fingerprint cagrilari: {"groq": {"calls": 5, "key_count": 53, "by_fingerprint": {"f1a0600529c4": 1, "c93303cbec45": 1, "5e2c5c185255": 1, "24b9652705b1": 1, "d427d6dcc70e": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `21765.05`
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
- Context: `shadow-golden-20260514_182641-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_improved:repair_improved`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3041; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~10506; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1451; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1268`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260514_182641-GT04", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 5820.011, "capability_planner_timeout_suspected": false, "routing_ms": 4224.495, "routing_timeout_suspected": false, "conversation_ms": 273.193, "final_synthesis_ms": 1962.327}`
- Cevap preview: Benchmark, Kayıt yaptırdığınız öğretim yılının en geç 3. haftasına kadar muafiyet başvurunuzu yapabilirsiniz. • Muafiyet sürecinde, daha önce aldığınız ve başarılı olduğunuz derslerden muaf olmak için başvuruda bulunabilirsiniz. • Yatay Geçiş İnceleme ve İntibak Komisyonu, başvurunuzla ilgili incelemeyi yaparak intibakınızı düzenler. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf - Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf - Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf - Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
