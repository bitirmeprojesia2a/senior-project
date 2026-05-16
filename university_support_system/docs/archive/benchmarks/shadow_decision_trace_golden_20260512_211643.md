# Shadow Decision Trace Golden Run 20260512_211643

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 1
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (59444.9 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260512_211643.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260512_211643.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | 5 | 16722.1 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/task_type, legacy=regulation_agent:match; student_affairs:graduation_agent/contract, legacy=registration_agent:diff | 1 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/fail:answer_conflicts_with_evidence_values; missing=4,00, 3, 1, 2 | 6 | 13938.5 | FAIL |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=11
- Provider hatalari: -
- Fallback cagrilari: 0
- Provider hata nedenleri: -
- Retryable provider hata sayisi: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 59444.9, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 59444.9}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `16722.06`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 2 | pass=1 | check=0 | fail=1 | requires_judge=1 | contract_enforceable=0
- Nedenler: answer_conflicts_with_evidence_values=1, query_does_not_require_value_check=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260512_211643-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260512_211643-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1834.117, "capability_planner_timeout_suspected": false, "routing_ms": 1371.749, "routing_timeout_suspected": false, "conversation_ms": 249.636, "final_synthesis_ms": 1556.962}`
- Cevap preview: Benchmark, Çift anadal programına başvurmak için ana dal programında mezuniyet hakkını elde etmiş olunması ve çift anadal programını başarıyla tamamlamış olmak gerekir. Başvuru için ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olmasıdir. Önlisans 120 AKTS, lisans 240 AKTS şartını yerine getirmek gerekir. - Öğrencinin ana dal programında kayıtlı olması, - Çift anadal programını başarıyla tamamlamış olması, - Ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. Başvuru süreci ve gerekli belgelerle ilgili olarak akademik programlar departmanından bilgi alınabilir. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_ger...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260512_211643-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, graduation_agent`
- Specialist selector: `academic_programs:regulation_agent/task_type, legacy=regulation_agent:match; student_affairs:graduation_agent/contract, legacy=registration_agent:diff`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/fail:answer_conflicts_with_evidence_values; missing=4,00, 3, 1, 2`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260512_211643-cap-followup", "status": "FAIL", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1918.624, "capability_planner_timeout_suspected": false, "routing_ms": 4535.864, "routing_timeout_suspected": false, "conversation_ms": 1370.653, "final_synthesis_ms": 1665.905}`
- Cevap preview: Benchmark, CAP başvurusu için gerekli olan not ortalaması bilgisi bulunmamaktadır. Ancak, çift ana dal programına başvuru tarihindeki ana dal genel not ortalamasının dikkate alındığı belirtilmektedir. • ÇAP'ın ayrılığı esastır ve öğrenciler, devam ettikleri her iki ana dal programlarında Ondokuz Mayıs Üniversitesi Ön Lisans ve Lisans Eğitim-Öğretim Yönetmeliği’nin hükümlerine tabidir. • ÇAP'a kayıtlı öğrencilerin bu programları tamamlamaları için, ana dal programında olan dersler dışında, ilgili ÇAP açan bölümce verilen en az 40, en çok 60 kredi ders almaları gerekir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça) - Belge: yonerge_cift_anadal_yandal.pdf (2 parça) - Belge: yonerge_onl...
