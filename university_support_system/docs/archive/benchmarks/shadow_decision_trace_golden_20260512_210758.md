# Shadow Decision Trace Golden Run 20260512_210758

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 3
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: full (60376.7 ms)
- Provider retry: count=1 backoff=8.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260512_210758.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260512_210758.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | 5 | 17114.5 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | 5 | 16483.1 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=10
- Provider hatalari: groq=1
- Fallback cagrilari: 0
- Provider hata nedenleri: rate_limit=1
- Retryable provider hata sayisi: 1

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "full", "elapsed_ms": 60376.7, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 56602.9}, "llm": {"enabled": true, "status": "ok", "roles": ["routing", "evidence_selection", "final_refinement", "specialist_synthesis"], "role_results": [{"role": "routing", "status": "ok", "elapsed_ms": 1096.4}, {"role": "evidence_selection", "status": "ok", "elapsed_ms": 768.2}, {"role": "final_refinement", "status": "ok", "elapsed_ms": 1020.0}, {"role": "specialist_synthesis", "status": "ok", "elapsed_ms": 889.0}], "llm_profile": "balanced", "timeout_seconds": 15, "elapsed_ms": 3773.8}}`
- First-case latency ms: `17114.51`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 2 | pass=2 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: query_does_not_require_value_check=1, required_values_preserved=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260512_210758-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260512_210758-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1889.536, "capability_planner_timeout_suspected": false, "routing_ms": 1291.009, "routing_timeout_suspected": false, "conversation_ms": 325.11, "final_synthesis_ms": 1338.923}`
- Cevap preview: Benchmark, Çift anadal programına başvuru yapabilmek için ana dal lisans programınızın yükümlülüklerini yerine getirmiş ve genel not ortalamasının (GANO) 4,00 üzerinden en az 2,75 olması gerekir. • Çift anadal programında başarı ve mezuniyet koşulları arasında ana dal programında mezuniyet hakkını elde etmek ve çift anadal programını başarıyla tamamlamak bulunur. • Öğrencinin çift anadal programından mezun olabilmesi için ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf - Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: öğrenci_işleri_birimi.txt (2 parça) -...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260512_210758-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent`
- Specialist selector: `academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/pass:required_values_preserved`
- LLM roles: `conversation, routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success; groq/llama-3.3-70b-versatile/routing/primary/error; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/final_refinement/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260512_210758-cap-followup", "status": "OK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}, {"attempt": 2, "context_id": "shadow-golden-20260512_210758-cap-followup", "status": "OK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 4917.005, "capability_planner_timeout_suspected": false, "routing_ms": 6835.828, "routing_timeout_suspected": false, "conversation_ms": 1727.935, "final_synthesis_ms": 1373.928}`
- Cevap preview: Benchmark, Çift anadal programa başvurabilmek için ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibari ile en az ilk %20'sinde bulunması gerekir. • Ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması zorunludur. • Ana dal diploma programının ilgili sınıfında başarı sıralaması itibari ile en az ilk %20'sinde bulunmanız gerekmektedir. Bu koşulları sağladığınızda çift anadal programa başvurabilirsiniz. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - RAG - Routing: parallel - Pipeline: academic_programs -> orchestrator Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
