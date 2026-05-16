# Shadow Decision Trace Golden Run 20260513_185322

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 3
- Trace kaydi: 4
- Source owner eslesmesi: 2/3
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 2
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (48561.7 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_185322.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_185322.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | - | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=3; retry_history=5 | shadow/check:answer_quality_issue; tokens=Routing | - | - | capability expected=calendar.academic_date actual=- | 3 | 20834.7 | CHECK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=2; retry_history=2 | shadow/check:answer_quality_issue; tokens=Routing | - | - | - | 3 | 19795.7 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | curriculum_catalog | none | main_orchestrator | academic_programs | academic_programs:curriculum_agent/contract | 0 | observed: kept=academic_programs; pruned=-; reason=single_branch | shadow/pass:required_values_preserved | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=2,50; competing=- | judge:accept; approved=True | - | shadow/check:answer_quality_issue; tokens=Routing | 2,50 | - | capability expected=student_affairs.policy_lookup actual=none; primary_department expected=student_affairs actual=academic_programs; primary_specialist expected=registration_agent actual=curriculum_agent | 4 | 7385.8 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=10
- Provider hatalari: groq=5
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 5
- Retry history provider hata sayisi: 7
- Provider hata nedenleri: rate_limit=12
- Retryable provider hata sayisi: 12
- Tahmini input token: 25573 (10 cagrida)
- Prompt/system char: 23360/78952
- Role bazli cagri sayisi: final_refinement=3, judge=1, routing=6
- Role bazli tahmini input token: final_refinement=4358, judge=1030, routing=20185

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=10 configured_keys=53 used_keys=10
- Key fingerprint cagrilari: {"groq": {"calls": 10, "key_count": 53, "by_fingerprint": {"19f91860a589": 1, "39659184e1c2": 1, "fc02f5c29d71": 1, "fcb1af18c173": 1, "fabc86c419a2": 1, "80b7f264cbe2": 1, "897ea1ca897e": 1, "5150f63f1a64": 1, "64ee113faff7": 1, "7ebf4c926f8e": 1}}}
- Provider org fingerprintleri: 1916381c41ac=2, 36ac290f66aa=2, 68edacd4ded0=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 48561.7, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 48561.7}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `20834.73`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 3 | pass=3 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: no_query_relevant_required_values=2, required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 3 | pass=1 | check=0 | skipped=2
- Nedenler: not_applicable=2, single_primary_threshold=1

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260513_185322-GT01-retry1`
- Trace owner: `academic_calendar`
- Capability: `-`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract`
- Branch gate: `observed: kept=student_affairs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=3; retry_history=5`
- Answer quality: `shadow/check:answer_quality_issue; tokens=Routing`
- Structural checks: `capability expected=calendar.academic_date actual=-`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4265; groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~2337; groq/llama-3.3-70b-versatile/final_refinement/primary/error/in_tok~1111`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_185322-GT01", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_185322-GT01-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "final_refinement", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 6681.223, "capability_planner_timeout_suspected": false, "routing_ms": 6781.021, "routing_timeout_suspected": false, "conversation_ms": 7.966, "final_synthesis_ms": 6926.251}`
- Cevap preview: Benchmark, Genel akademik takvime gore yariyil sonu/final sinavlari guz donemi icin 03-16 Ocak 2026, bahar donemi icin 01-14 Haziran 2026 tarihlerindedir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - VT - Routing: direct - Pipeline: student_affairs Kaynak Özeti: - Belge: 2025_2026_genel_akademik_takvim.pdf

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260513_185322-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=student_affairs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `-`
- Provider warning: `final_retryable=2; retry_history=2`
- Answer quality: `shadow/check:answer_quality_issue; tokens=Routing`
- Structural checks: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2393; groq/llama-3.3-70b-versatile/final_refinement/primary/error/in_tok~1547`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_185322-GT04", "status": "OK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "final_refinement", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 1913.55, "capability_planner_timeout_suspected": false, "routing_ms": 6635.016, "routing_timeout_suspected": false, "conversation_ms": 7.357, "final_synthesis_ms": 7733.41}`
- Cevap preview: Benchmark, Kaynaklarda bu konuda şu bilgiler yer alıyor: - % 15 - emize yapilacak yatay gecis kontenjanlari senato tarafindan belirlenir --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - RAG - Routing: direct - Pipeline: student_affairs Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_185322-cap-followup`
- Trace owner: `curriculum_catalog`
- Capability: `none`
- Selected specialists: `curriculum_agent`
- Specialist selector: `academic_programs:curriculum_agent/contract`
- Branch gate: `observed: kept=academic_programs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=academic_programs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/pass:single_primary_threshold; primary=2,50; competing=-`
- Judge repair: `judge:accept; approved=True`
- Provider warning: `-`
- Answer quality: `shadow/check:answer_quality_issue; tokens=Routing`
- Structural checks: `capability expected=student_affairs.policy_lookup actual=none; primary_department expected=student_affairs actual=academic_programs; primary_specialist expected=registration_agent actual=curriculum_agent`
- LLM roles: `routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2653; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1700; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1030`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_185322-cap-followup", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2056.234, "capability_planner_timeout_suspected": false, "routing_ms": 1510.305, "routing_timeout_suspected": false, "conversation_ms": 7.349, "final_synthesis_ms": 965.084}`
- Cevap preview: Benchmark, Not ortalamasının 4.00 üzerinden 2,50 olması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - RAG - Routing: direct - Pipeline: academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_yabanci_dil_egitim_ogretim.pdf - Belge: samsun_sağlık_yüksekokulu_eğitim_öğretim_ve_sınav_yönetmeliği.txt - Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf - Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf - Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf
