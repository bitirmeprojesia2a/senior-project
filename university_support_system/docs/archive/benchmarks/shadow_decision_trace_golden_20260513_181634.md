# Shadow Decision Trace Golden Run 20260513_181634

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 3
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (51152.1 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_181634.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_181634.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | - | - | - | 4 | 11210.2 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=3,00; competing=- | judge:accept; approved=True | 3,00 | - | - | 5 | 27146.6 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=9
- Provider hatalari: -
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 0
- Retry history provider hata sayisi: 3
- Provider hata nedenleri: rate_limit=3
- Retryable provider hata sayisi: 3
- Tahmini input token: 23914 (9 cagrida)
- Prompt/system char: 31278/64390
- Role bazli cagri sayisi: conversation=1, global_synthesis=2, judge=2, routing=4
- Role bazli tahmini input token: conversation=3162, global_synthesis=4183, judge=1937, routing=14632

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=9 configured_keys=53 used_keys=9
- Key fingerprint cagrilari: {"groq": {"calls": 9, "key_count": 53, "by_fingerprint": {"26a01be4304a": 1, "39659184e1c2": 1, "76f4cfb21ed4": 1, "fe4490aa7a6a": 1, "618f51582a5a": 1, "fcb1af18c173": 1, "f93b795d2a95": 1, "897ea1ca897e": 1, "5150f63f1a64": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 51152.1, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 51152.1}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `11210.21`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 2 | pass=2 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: query_does_not_require_value_check=1, required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 2 | pass=1 | check=0 | skipped=1
- Nedenler: not_applicable=1, single_primary_threshold=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_181634-cap-followup-retry1`
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
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2989; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1944; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~910`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_181634-cap-followup", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "global_synthesis", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_181634-cap-followup-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2018.481, "capability_planner_timeout_suspected": false, "routing_ms": 4385.355, "routing_timeout_suspected": false, "conversation_ms": 7.338, "final_synthesis_ms": 1750.229}`
- Cevap preview: Benchmark, Çift anadal programı başvurusu, akademik takvimde belirtilen tarihte, ÖİDB’nin internet sayfasında açılan ilgili link üzerinden elektronik olarak yapılır. Başvuru için sisteme yüklenecek evraklar, yapılan duyuruda ilan edilmektedir. • Yabancı dil ile eğitim yapan programlara başvuru yapabilmek için hazırlık sınıfında başarılı/muaf olunması veya yabancı dil sınavlarından en az 70 puan alınması gerekmektedir. • Çift anadal programında başarı ve mezuniyet koşulları arasında, ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması bulunmaktadır. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: sık_sorulan_sorular.txt - Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf - Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_pro...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_181634-cap-followup-retry1`
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
- Structural checks: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3162; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4268; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3111; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2239; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1027`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_181634-cap-followup-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 5666.743, "capability_planner_timeout_suspected": false, "routing_ms": 2181.301, "routing_timeout_suspected": false, "conversation_ms": 7897.585, "final_synthesis_ms": 8833.665}`
- Cevap preview: Benchmark, Ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibari ile en az ilk % 20'sinde bulunması gerekir. Ayrıca, başvuruya ilişkin ayrıntılı koşullar akademik takvimde belirtilen tarihte duyurulur. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (2 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (2 parça)
