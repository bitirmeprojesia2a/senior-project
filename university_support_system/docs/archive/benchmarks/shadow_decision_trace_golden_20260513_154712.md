# Shadow Decision Trace Golden Run 20260513_154712

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (52857.5 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_154712.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_154712.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | 5 | 23388.7 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=-; pruned=-; reason=single_branch | shadow/pass:required_values_preserved | 5 | 16993.0 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=10
- Provider hatalari: groq=2
- Fallback cagrilari: 0
- Provider hata nedenleri: rate_limit=4
- Retryable provider hata sayisi: 4
- Tahmini input token: 23707 (10 cagrida)
- Prompt/system char: 28845/65994
- Role bazli tahmini input token: conversation=3087, final_refinement=1340, global_synthesis=3259, judge=1767, routing=14254

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 52857.5, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 52857.4}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `23388.72`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 2 | pass=2 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: query_does_not_require_value_check=1, required_values_preserved=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_154712-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~2968; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2065; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~870; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1194`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_154712-cap-followup", "status": "OK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 6958.174, "capability_planner_timeout_suspected": false, "routing_ms": 8720.337, "routing_timeout_suspected": false, "conversation_ms": 174.031, "final_synthesis_ms": 1765.406}`
- Cevap preview: Benchmark, ÇAP (Çift Anadal Programı) başvurusu için ana dal programında mezuniyet hakkını elde eden ve ÇAP’ı başarıyla tamamlayan öğrencilere ayrıca ikinci ana dalı yapılan bölümün lisans diploması verilir. • Ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. • Genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. • Önlisans 120 AKTS, lisans 240 AKTS şartını yerine getirmek gerekir. Başvuru adımları hakkında bilgi almak için ilgili sekreterin iletişim bilgilerine başvurabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (9 parça) - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_154712-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=-; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:required_values_preserved`
- LLM roles: `conversation, routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3087; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4268; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2754; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1340; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~897`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_154712-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1949.592, "capability_planner_timeout_suspected": false, "routing_ms": 4247.954, "routing_timeout_suspected": false, "conversation_ms": 1520.481, "final_synthesis_ms": 7120.348}`
- Cevap preview: Benchmark, CAP başvurusu için ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk %20'sinde bulunması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - RAG - Routing: direct - Pipeline: academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf
