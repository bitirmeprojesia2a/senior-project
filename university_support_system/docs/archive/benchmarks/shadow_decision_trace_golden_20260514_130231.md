# Shadow Decision Trace Golden Run 20260514_130231

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
- Warmup mode: retrieval (66526.5 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260514_130231.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260514_130231.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | - | shadow/check:answer_quality_issue; tokens=- | - | - | - | 4 | 10663.1 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=4
- Provider hatalari: -
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 0
- Retry history provider hata sayisi: 0
- Provider hata nedenleri: -
- Retryable provider hata sayisi: 0
- Tahmini input token: 10629 (4 cagrida)
- Prompt/system char: 15200/27326
- Role bazli cagri sayisi: global_synthesis=1, judge=1, routing=2
- Role bazli tahmini input token: global_synthesis=2427, judge=895, routing=7307

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=4 configured_keys=53 used_keys=4
- Key fingerprint cagrilari: {"groq": {"calls": 4, "key_count": 53, "by_fingerprint": {"cc9074971faa": 1, "f1a0600529c4": 1, "fe4490aa7a6a": 1, "c93303cbec45": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 66526.5, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 66526.5}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `10663.08`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 1 | pass=1 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: no_query_relevant_required_values=1

## Value Conflict Ozeti

- Kayit: 1 | pass=0 | check=0 | skipped=1
- Nedenler: not_applicable=1

## Notlar

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260514_130231-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `judge:accept; approved=True`
- Provider warning: `-`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3034; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2427; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~895`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260514_130231-GT04", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1349.349, "capability_planner_timeout_suspected": false, "routing_ms": 1485.273, "routing_timeout_suspected": false, "conversation_ms": 202.834, "final_synthesis_ms": 1172.926}`
- Cevap preview: Benchmark, Kayıt yaptırdığınız öğretim yılının en geç 3. haftasına kadar muafiyet ve intibak talebinde bulunabilirsiniz. Yatay Geçiş İnceleme ve İntibak Komisyonu, sizin muafiyet istediğiniz derslerle ilgili incelemeyi yaparak, daha önce alınıp başarılı olunan ve muafiyet talep edilen tüm dersler için intibakınızı düzenler. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf - Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf - Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf - Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf - Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf - Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
