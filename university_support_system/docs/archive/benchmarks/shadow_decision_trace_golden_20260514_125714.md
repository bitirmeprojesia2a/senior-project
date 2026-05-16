# Shadow Decision Trace Golden Run 20260514_125714

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 4
- Trace kaydi: 4
- Source owner eslesmesi: 4/4
- Hata sayisi: 0
- Answer validator riskli: 1
- Value conflict riskli: 0
- Structural check riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (95204.5 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260514_125714.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260514_125714.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | shadow/check:answer_quality_issue; tokens=- | - | - | - | 3 | 7045.9 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/check:answer_missing_required_evidence_values; missing=12 | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | - | shadow/pass:clean; tokens=- | - | - | - | 5 | 15160.3 | CHECK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | - | shadow/check:answer_quality_issue; tokens=- | - | - | - | 4 | 7828.0 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=3,00; competing=- | judge:accept; approved=True | - | shadow/check:answer_quality_issue; tokens=- | 3,00 | - | - | 5 | 10995.5 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=17
- Provider hatalari: -
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 0
- Retry history provider hata sayisi: 0
- Provider hata nedenleri: -
- Retryable provider hata sayisi: 0
- Tahmini input token: 45148 (17 cagrida)
- Prompt/system char: 61491/119133
- Role bazli cagri sayisi: conversation=1, final_refinement=1, global_synthesis=4, judge=3, routing=8
- Role bazli tahmini input token: conversation=3128, final_refinement=1252, global_synthesis=8800, judge=3437, routing=28531

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=17 configured_keys=53 used_keys=17
- Key fingerprint cagrilari: {"groq": {"calls": 17, "key_count": 53, "by_fingerprint": {"cc9074971faa": 1, "f1a0600529c4": 1, "fe4490aa7a6a": 1, "c93303cbec45": 1, "5e2c5c185255": 1, "24b9652705b1": 1, "d427d6dcc70e": 1, "75d046119efe": 1, "955997d77e17": 1, "3b4187fdfdc3": 1, "fc02f5c29d71": 1, "80b7f264cbe2": 1, "2075f8b244dc": 1, "64aeba5d5c98": 1, "928ce4d0b4ba": 1, "5636cc6375b7": 1, "520684406576": 1}}}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 95204.5, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 95203.2}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `7045.88`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 4 | pass=3 | check=1 | fail=0 | requires_judge=1 | contract_enforceable=0
- Nedenler: answer_missing_required_evidence_values=1, no_query_relevant_required_values=1, query_does_not_require_value_check=1, required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 4 | pass=1 | check=0 | skipped=3
- Nedenler: not_applicable=3, single_primary_threshold=1

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260514_125714-GT01`
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
- Provider warning: `-`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4265; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2337; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1252`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260514_125714-GT01", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1357.361, "capability_planner_timeout_suspected": false, "routing_ms": 1592.11, "routing_timeout_suspected": false, "conversation_ms": 760.083, "final_synthesis_ms": 1196.024}`
- Cevap preview: Benchmark, Final sınavları, güz dönemi için 03-16 Ocak 2026, bahar dönemi için 01-14 Haziran 2026 tarihlerinde başlayacaktır. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - VT - Routing: direct - Pipeline: student_affairs -> orchestrator Kaynak Özeti: - Belge: C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\data\raw\student_affairs\takvimler\2025_2026_genel_akademik_takvim.pdf

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260514_125714-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/check:answer_missing_required_evidence_values; missing=12`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_neutral:repair_not_worse`
- Provider warning: `-`
- Answer quality: `shadow/pass:clean; tokens=-`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3037; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2649; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1488; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1295`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260514_125714-GT04", "status": "CHECK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2018.172, "capability_planner_timeout_suspected": false, "routing_ms": 1760.415, "routing_timeout_suspected": false, "conversation_ms": 7.536, "final_synthesis_ms": 1430.954}`
- Cevap preview: Benchmark, Yatay geçiş ile gelen öğrenciler, muafiyet başvurusunu kesin kayıt tarihlerinden sonraki ilk 15 gün içinde yapmalıdır. • Başvuru, daha önce öğrenim gördükleri yüksek öğretim kurumlarından veya pedagojik formasyon eğitimi sertifika programından alıp başarılı oldukları derslerden muaf olmak için yapılır. • Öğrencilerin, muafiyet istediği dersler ile ilgili incelemeyi yaparak, daha önce alınıp başarılı olunan ve muafiyet talep edilen tüm dersler için intibakını düzenlenir. 22.12.2023 tarihli düzenlemenin ardından, öğrencilerin Pedagojik Formasyon Eğitimi sertifika programından aldıkları derslerden muaf olabilmeleri için başvuruda bulunmaları gerekir. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf - Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf - Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf - Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf - Belge: yonerge_dis_h...

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260514_125714-cap-followup`
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
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2976; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2375; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~919`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260514_125714-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1409.455, "capability_planner_timeout_suspected": false, "routing_ms": 1433.553, "routing_timeout_suspected": false, "conversation_ms": 10.003, "final_synthesis_ms": 1912.48}`
- Cevap preview: Benchmark, Çift anadal programına başvuru için kabul ve kayıt koşulları akademik takvim/Duyuru ile ilan edilir. Dönemin başlangıcında kesinleşir. Çift anadal programına hak kazanan öğrencilerin kayıt işlemleri ile ilgili sürecin nasıl gerçekleştirileceği ÖİDB web sayfasında ilan edilir. Aynı anda birden fazla ikinci ana dal diploma programına kayıt yapılamaz; ancak aynı anda ikinci ana dal diploma programı ile Yan Dal Programı'na kayıt yapılabilir. Ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. Öğrencinin çift anadal programından mezun olabilmesi için ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. Çift anadal programında başarılı olan ve ana dalını tamamlayan öğrenciye ayrıca ikinci ana dalı yaptığı bölümün lisans diploması verilir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260514_125714-cap-followup`
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
- Provider warning: `-`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3128; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4268; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3111; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2481; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1030`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260514_125714-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2106.563, "capability_planner_timeout_suspected": false, "routing_ms": 2153.083, "routing_timeout_suspected": false, "conversation_ms": 1733.241, "final_synthesis_ms": 1345.356}`
- Cevap preview: Benchmark, ÇAP başvurusu için not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibari ile en az ilk %20'sinde bulunması gerekir. • Not ortalaması 3,00 ve üzeri olmalıdır. • Başarı sıralaması en az ilk %20'sinde olunmalıdır. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (2 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (2 parça)
