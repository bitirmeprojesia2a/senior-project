# Shadow Decision Trace Golden Run 20260512_211012

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 3
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: full (63669.2 ms)
- Provider retry: count=1 backoff=8.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260512_211012.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260512_211012.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | 5 | 14053.5 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | 5 | 22277.5 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=10
- Provider hatalari: -
- Fallback cagrilari: 0
- Provider hata nedenleri: -
- Retryable provider hata sayisi: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "full", "elapsed_ms": 63669.2, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 57950.5}, "llm": {"enabled": true, "status": "ok", "roles": ["routing", "evidence_selection", "final_refinement", "specialist_synthesis"], "role_results": [{"role": "routing", "status": "ok", "elapsed_ms": 2233.7}, {"role": "evidence_selection", "status": "ok", "elapsed_ms": 1850.8}, {"role": "final_refinement", "status": "ok", "elapsed_ms": 807.6}, {"role": "specialist_synthesis", "status": "ok", "elapsed_ms": 826.4}], "llm_profile": "balanced", "timeout_seconds": 15, "elapsed_ms": 5718.7}}`
- First-case latency ms: `14053.5`
- Timeout sinyalleri: capability_planner=0, routing=1

## Answer Validator Ozeti

- Kayit: 2 | pass=2 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: query_does_not_require_value_check=1, required_values_preserved=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260512_211012-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260512_211012-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2454.087, "capability_planner_timeout_suspected": false, "routing_ms": 2426.327, "routing_timeout_suspected": false, "conversation_ms": 247.996, "final_synthesis_ms": 1679.878}`
- Cevap preview: Benchmark, Çift anadal programı başvurunuz için ana dal programında mezuniyet hakkını elde etmiş olmanız ve çift ana dal programını başarıyla tamamlayarak, ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. • Çift anadal programında başarı ve mezuniyet koşulları MADDE 8 - (1) ÇAP'ta başarı ve mezuniyet koşulları şunlardır: • Önlisans 120 AKTS, lisans 240 AKTS şartını yerine getirmeniz gerekir. Başvuru işlemleri internet sitesi üzerinden online olarak yapılacak ve kesin kayıt esnasında başvuruya esas teşkil edecek evraklar eksiksiz olarak ibraz edilecektir. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf - Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf - Belge: 202...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260512_211012-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent`
- Specialist selector: `academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/pass:required_values_preserved`
- LLM roles: `conversation, routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/final_refinement/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260512_211012-cap-followup", "status": "FAIL", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260512_211012-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2046.013, "capability_planner_timeout_suspected": false, "routing_ms": 10857.089, "routing_timeout_suspected": true, "conversation_ms": 4821.597, "final_synthesis_ms": 1837.208}`
- Cevap preview: Benchmark, CAP başvurusu için not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk % 20'sinde bulunması gerekir. • Not ortalamasının en az 3,00 olması şarttır. • Başarı sıralaması itibarı ile sınıfın ilk % 20'sinde yer almak gerekmektedir. Bu koşulları sağlayarak başvurunuzü gerçekleştirebilirsiniz. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - RAG - Routing: parallel - Pipeline: academic_programs -> orchestrator Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
