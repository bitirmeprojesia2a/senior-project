# Shadow Decision Trace Golden Run 20260513_141603

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (90560.8 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_141603.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_141603.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | 5 | 16756.7 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | 5 | 15083.8 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=10
- Provider hatalari: -
- Fallback cagrilari: 0
- Provider hata nedenleri: -
- Retryable provider hata sayisi: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 90560.8, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 90560.1}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `16756.65`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 2 | pass=2 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: query_does_not_require_value_check=1, required_values_preserved=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_141603-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_141603-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1919.031, "capability_planner_timeout_suspected": false, "routing_ms": 1493.702, "routing_timeout_suspected": false, "conversation_ms": 799.446, "final_synthesis_ms": 1701.73}`
- Cevap preview: Benchmark, Çift anadal programına başvuru yapmak için, ana dal programında başarı bakımından belirli bir seviyede olmanız ve diğer koşulları karşıladığınızda başvurabilirsiniz. • Çift anadal programında size, ana dal lisans programı ile ayrılık esastır. • Ana dal programında aldığınız derslerden çift ana dal programına eşdeğerliği verilen dersler ve notlar, çift ana dal transkriptinize yansıtılır. • Çift ana dal programını tamamlamak için, ana dal programında olan dersler dışında, ilgili çift ana dal açan bölümce verilen en az 40, en çok 60 kredi ders almanız gerekir. Bu sınırlar, ilgili birim yönetim kurulunun önerisi ve Senato’nun onayı ile 1/3 oranında artırılabilir. Öğrencinin GANO'su 2,00 veya daha yüksek olmalıdır. Ayrıca, yabancı dil ile eğitim yapan programlara başvuru yapabilmek için, hazırlık sınıfında başarılı/muaf olma veya Yükseköğretim Kurulu tarafından tanınan ulusal veya...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_141603-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/pass:required_values_preserved`
- LLM roles: `conversation, routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/final_refinement/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_141603-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1973.184, "capability_planner_timeout_suspected": false, "routing_ms": 7438.654, "routing_timeout_suspected": false, "conversation_ms": 1387.798, "final_synthesis_ms": 1728.671}`
- Cevap preview: Benchmark, Ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk %20'sinde bulunması gerekir. • Başvuru için asgari sınıf düzeyi fourth veya fifth akademik year'dır. • Başarı sıralaması itibari ile en az ilk %20'sinde bulunması şarttır. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - RAG - Routing: parallel - Pipeline: academic_programs -> orchestrator Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
