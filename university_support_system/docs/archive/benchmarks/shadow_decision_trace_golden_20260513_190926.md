# Shadow Decision Trace Golden Run 20260513_190926

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 4
- Trace kaydi: 5
- Source owner eslesmesi: 4/4
- Hata sayisi: 0
- Answer validator riskli: 0
- Value conflict riskli: 0
- Structural check riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (51267.4 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_190926.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_190926.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | final_retryable=1; retry_history=1 | shadow/check:answer_quality_issue; tokens=- | - | - | - | 3 | 14439.2 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | repair:accepted_neutral:repair_not_worse | retry_history=1 | shadow/pass:clean; tokens=- | - | - | - | 5 | 18102.7 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | judge:accept; approved=True | - | shadow/check:answer_quality_issue; tokens=- | - | - | - | 4 | 8184.2 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=3,00; competing=- | repair:accepted_improved:repair_improved | final_retryable=1; retry_history=1 | shadow/pass:clean; tokens=- | 3,00 | - | - | 6 | 16391.1 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=18
- Provider hatalari: groq=2
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 2
- Retry history provider hata sayisi: 3
- Provider hata nedenleri: rate_limit=5
- Retryable provider hata sayisi: 5
- Tahmini input token: 44676 (18 cagrida)
- Prompt/system char: 57993/120737
- Role bazli cagri sayisi: conversation=1, final_refinement=1, global_synthesis=5, judge=3, routing=8
- Role bazli tahmini input token: conversation=3140, final_refinement=1187, global_synthesis=8781, judge=3025, routing=28543

## API Key Dagilimi

- Provider/key dagilimi: groq: calls=18 configured_keys=53 used_keys=18
- Key fingerprint cagrilari: {"groq": {"calls": 18, "key_count": 53, "by_fingerprint": {"fe4490aa7a6a": 1, "5e2c5c185255": 1, "24b9652705b1": 1, "2075f8b244dc": 1, "64aeba5d5c98": 1, "928ce4d0b4ba": 1, "5636cc6375b7": 1, "18694d48e7d3": 1, "897ea1ca897e": 1, "051f59a11b93": 1, "c6e82d5f9ef2": 1, "70bc5df1936d": 1, "9ec28f2ad046": 1, "618f51582a5a": 1, "5150f63f1a64": 1, "7428d4dce055": 1, "a3e421be002a": 1, "2eb4f14b6ad5": 1}}}
- Provider org fingerprintleri: 1916381c41ac=1, 36ac290f66aa=1
- Fingerprint eksik cagrilar: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 51267.4, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 51267.4}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `14439.18`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 4 | pass=4 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: no_query_relevant_required_values=2, query_does_not_require_value_check=1, required_values_preserved=1

## Value Conflict Ozeti

- Kayit: 4 | pass=1 | check=0 | skipped=3
- Nedenler: not_applicable=3, single_primary_threshold=1

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260513_190926-GT01`
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
- Provider warning: `final_retryable=1; retry_history=1`
- Answer quality: `shadow/check:answer_quality_issue; tokens=-`
- Structural checks: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4265; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2337; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1187`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_190926-GT01", "status": "OK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 5060.929, "capability_planner_timeout_suspected": false, "routing_ms": 7050.001, "routing_timeout_suspected": false, "conversation_ms": 219.229, "final_synthesis_ms": 1300.008}`
- Cevap preview: Benchmark, Final sınavları, güz döneminde 03-16 Ocak 2026, bahar döneminde 01-14 Haziran 2026 tarihlerinde başlar. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - VT - Routing: direct - Pipeline: student_affairs -> orchestrator Kaynak Özeti: - Belge: C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\data\raw\student_affairs\takvimler\2025_2026_genel_akademik_takvim.pdf

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260513_190926-GT04-retry1`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Judge repair: `repair:accepted_neutral:repair_not_worse`
- Provider warning: `retry_history=1`
- Answer quality: `shadow/pass:clean; tokens=-`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3051; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2037; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~980; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1258`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_190926-GT04", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260513_190926-GT04-retry1", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1901.062, "capability_planner_timeout_suspected": false, "routing_ms": 1714.727, "routing_timeout_suspected": false, "conversation_ms": 9.179, "final_synthesis_ms": 1403.598}`
- Cevap preview: Benchmark, Yatay geçiş ile gelen öğrenciler, daha önce aldıkları ve başarılı oldukları derslerden muaf olmak için, kayıt yaptırdıkları öğretim yılının en geç 3. haftasının sonuna kadar başvurabilirler. Bu başvurularda, daha önce öğrenim gördükleri yüksek öğretim kurumlarından veya pedagojik formasyon eğitimi sertifika programından alıp başarılı oldukları derslerden muaf olmak için başvuruda bulunabilirler. Yatay Geçiş İnceleme ve İntibak Komisyonu, öğrencinin muafiyet istediği ders/bloklar ile ilgili incelemeyi yaparak, daha önce alınıp başarılı olunan ve muafiyet talep edilen tüm ders/bloklar için intibakını düzenler. Öğrenciler, kayıt yaptırdıkları öğretim yılının en geç 3. haftasının sonuna kadar transkripti ve ders içerikleri ile birlikte başvurularını yapabilirler. Yatay geçiş kontenjanları Senato tarafından belirlenir. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf - Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf...

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_190926-cap-followup`
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
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2976; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2380; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~919`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_190926-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2267.459, "capability_planner_timeout_suspected": false, "routing_ms": 1597.226, "routing_timeout_suspected": false, "conversation_ms": 7.807, "final_synthesis_ms": 1425.705}`
- Cevap preview: Benchmark, Çift anadal programına başvuru yapabilmek için, aynı anda ikinci ana dal diploma programı ile Yan Dal Programı'na (YDP) kayıt yapılabilir. Başvuruların değerlendirilmesinde öncelikle ana dal genel not ortalamasına, ortalamanın eşitliği halinde öğrencinin tamamlamış olduğu toplam kredisine bakılır. Ayrıca, çift anadal programında başarı ve mezuniyet koşulları arasında, ana dal programında mezuniyet hakkını elde eden ve çift anadal programını başarıyla tamamlayan öğrenciye ayrıca ikinci ana dalı yaptığı bölümün lisans diploması verilir. Öğrencinin çift anadal programından mezun olabilmesi için ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Belge: yonerge_onlisans_lisans_yatay_gecis.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2....

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_190926-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/pass:single_primary_threshold; primary=3,00; competing=-`
- Judge repair: `repair:accepted_improved:repair_improved`
- Provider warning: `final_retryable=1; retry_history=1`
- Answer quality: `shadow/pass:clean; tokens=-`
- Structural checks: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3140; groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3105; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1945; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1126; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1161`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_190926-cap-followup", "status": "OK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 1698.172, "capability_planner_timeout_suspected": false, "routing_ms": 6885.601, "routing_timeout_suspected": false, "conversation_ms": 1960.968, "final_synthesis_ms": 1757.28}`
- Cevap preview: Benchmark, Çift anadal programına başvuru yapabilmeniz için ana dal genel not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibari ile en az ilk %20'sinde bulunması gerekir. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (3 parça)
