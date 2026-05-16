# Shadow Decision Trace Golden Run 20260513_191504

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 4
- Trace kaydi: 6
- Source owner eslesmesi: 4/4
- Hata sayisi: 0
- Answer validator riskli: 2
- Value conflict riskli: 0
- Structural check riskli: 2
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (51153.3 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_191504.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_191504.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | - | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=1; retry_history=2 | shadow/check:answer_quality_issue; tokens=- | - | - | capability expected=calendar.academic_date actual=-; provider_retryable_error_seen | 3 | 16378.9 | CHECK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/fail:answer_conflicts_with_evidence_values; missing=12, 15 | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | - | shadow/pass:clean; tokens=- | - | - | - | 5 | 21410.3 | FAIL |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | - | shadow/check:answer_quality_issue; tokens=- | - | - | - | 4 | 8888.5 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract; academic_programs:regulation_agent/contract | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/check:answer_missing_required_evidence_values; missing=3,00 | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=2,00; competing=- | repair:rejected_worse:answer_value_conflict_worsened | final_retryable=1; retry_history=2 | shadow/check:answer_quality_issue; tokens=- | 2,00 | - | provider_retryable_error_seen | 6 | 19352.8 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=18
- Provider hatalari: groq=2
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 2
- Retry history provider hata sayisi: 4
- Provider hata nedenleri: rate_limit=6
- Retryable provider hata sayisi: 6
- Tahmini input token: 45839 (18 cagrida)
- Prompt/system char: 62649/120737
- Role bazli cagri sayisi: conversation=1, final_refinement=1, global_synthesis=5, judge=3, routing=8
- Role bazli tahmini input token: conversation=3337, final_refinement=1111, global_synthesis=9390, judge=3521, routing=28480

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=18 configured_keys=53 used_keys=18
- Key fingerprint cagrilari: {"groq": {"calls": 18, "key_count": 53, "by_fingerprint": {"d427d6dcc70e": 1, "3b4187fdfdc3": 1, "2075f8b244dc": 1, "64aeba5d5c98": 1, "928ce4d0b4ba": 1, "5636cc6375b7": 1, "19f91860a589": 1, "897ea1ca897e": 1, "051f59a11b93": 1, "c6e82d5f9ef2": 1, "70bc5df1936d": 1, "9ec28f2ad046": 1, "fba5c0f29033": 1, "fcb1af18c173": 1, "64ee113faff7": 1, "775f860f28a7": 1, "98aa7a677e13": 1, "1d6935952e9a": 1}}}
- Provider org fingerprintleri: 1916381c41ac=1, 68edacd4ded0=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 51153.3, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 51153.3}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `16378.85`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 4 | pass=2 | check=1 | fail=1 | requires_judge=2 | contract_enforceable=0
- Nedenler: answer_conflicts_with_evidence_values=1, answer_missing_required_evidence_values=1, no_query_relevant_required_values=1, query_does_not_require_value_check=1

## Value Conflict Ozeti

- Kayit: 4 | pass=1 | check=0 | skipped=3
- Nedenler: not_applicable=3, single_primary_threshold=1

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260513_191504-GT01-retry1`
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
- Provider warning: `final_retryable=1; retry_history=2`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `capability expected=calendar.academic_date actual=-; provider_retryable_error_seen`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4265; groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~2337; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1111`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_191504-GT01", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_191504-GT01-retry1", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 6786.402, "capability_planner_timeout_suspected": false, "routing_ms": 1293.253, "routing_timeout_suspected": false, "conversation_ms": 7.878, "final_synthesis_ms": 7701.889}`
- Cevap preview: Benchmark, Final sınavları, güz dönemi için 03-16 Ocak 2026, bahar dönemi için 01-14 Haziran 2026 tarihlerinde başlayacak. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - VT - Routing: direct - Pipeline: student_affairs -> orchestrator Kaynak Özeti: - Belge: 2025_2026_genel_akademik_takvim.pdf

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260513_191504-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/fail:answer_conflicts_with_evidence_values; missing=12, 15`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_neutral:repair_not_worse`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3035; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2255; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1208; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1277`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_191504-GT04", "status": "FAIL", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1825.3, "capability_planner_timeout_suspected": false, "routing_ms": 1709.689, "routing_timeout_suspected": false, "conversation_ms": 7.466, "final_synthesis_ms": 1968.099}`
- Cevap preview: Benchmark, Kayıt yaptırdığınız öğretim yılının en geç 3. haftasının sonuna kadar muafiyet ve intibak talebinde bulunabilirsiniz. Muafiyet istediği ders/bloklar ile ilgili incelemeyi yapan Yatay Geçiş İnceleme ve İntibak Komisyonu, daha önce alınıp başarılı olunan ve muafiyet talep edilen tüm ders/bloklar için intibakını düzenler. • Başvuru için transkripti ve ders içerikleri ile birlikte dekanlığa başvurmanız gerekmektedir. • İnceleme ve intibak komisyonu, muafiyet ve intibak işlemlerini düzenler. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf - Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf - Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf - Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf - Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf - Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_191504-cap-followup`
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
- Provider warning: `-`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2976; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2319; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~920`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_191504-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1994.411, "capability_planner_timeout_suspected": false, "routing_ms": 1695.58, "routing_timeout_suspected": false, "conversation_ms": 12.142, "final_synthesis_ms": 1966.068}`
- Cevap preview: Benchmark, Çift anadal programı başvuruları için, kayıt olduğu yıldaki ilgili programın Yükseköğretim Kurulu tarafından belirlenen başarı sıralaması şartını sağlamış olmak gerekmektedir. Ayrıca, ana dal ve çift ana dal programı ilişkileri de dikkate alınmalıdır. • Çift anadal programına başvuru, kabul ve kayıt koşulları yönetmelikte belirlenir. • Başarı sıralaması şartı aranan programlarda, ilgili yılın başarı sıralamasını sağlamış olmak gerekir. Kaynaklarda programın genel not ortalamasına ilişkin bilgiler bulunmakta olup, çift anadal programından mezun olabilmeniz için ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça) - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: yonerge_onlisans_lisans_yatay_gecis.pdf - Belge: yonetm...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_191504-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract; academic_programs:regulation_agent/contract`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/check:answer_missing_required_evidence_values; missing=3,00`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/pass:single_primary_threshold; primary=2,00; competing=-`
- Judge repair: `repair:rejected_worse:answer_value_conflict_worsened`
- Provider warning: `final_retryable=1; retry_history=2`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `provider_retryable_error_seen`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3337; groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3066; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2306; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1393; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1233`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_191504-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "conversation", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_191504-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 2466.282, "capability_planner_timeout_suspected": false, "routing_ms": 6388.418, "routing_timeout_suspected": false, "conversation_ms": 2323.307, "final_synthesis_ms": 1585.356}`
- Cevap preview: Benchmark, Not ortalamasının 4,00 üzerinden en az 2,00 olması şarttır. • Ana dal programındaki not ortalamasının bu şartı sağlamak zorunda olduğunuz için • Not ortalamanızın en az 2,00 olması gerekiyor. Bu şartı sağlayamayan öğrencinin çift ana dal programı kaydı silinir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (5 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (4 parça)
