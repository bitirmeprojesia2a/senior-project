# Shadow Decision Trace Golden Run 20260512_221026

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: retrieval (50303.1 ms)
- Provider retry: count=1 backoff=12.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260512_221026.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260512_221026.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | 4 | 11227.0 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | 6 | 20784.3 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=10
- Provider hatalari: -
- Fallback cagrilari: 0
- Provider hata nedenleri: -
- Retryable provider hata sayisi: 0

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "retrieval", "elapsed_ms": 50303.1, "retrieval": {"enabled": true, "status": "ok", "collections": ["student_affairs_docs", "academic_programs_docs"], "include_reranker": true, "elapsed_ms": 50303.1}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `11227.02`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 2 | pass=2 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: query_does_not_require_value_check=1, required_values_preserved=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260512_221026-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260512_221026-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2726.192, "capability_planner_timeout_suspected": false, "routing_ms": 1525.145, "routing_timeout_suspected": false, "conversation_ms": 144.141, "final_synthesis_ms": 1519.381}`
- Cevap preview: Benchmark, Çift anadal programına başvuruda bulunmak için 01-05 Eylül 2025 tarihleri arasında başvurunuzu yapabilirsiniz. • Başvuruların değerlendirme ve ilanı 08-10 Eylül 2025 tarihleri arasında gerçekleşecektir. • Çift anadal programında mezun olabilmeniz için ana dal genel not ortalamanızın 4,00 üzerinden en az 2,75 olması gerekir. • Ayrıca, önlisans için 120 AKTS ve lisans için 240 AKTS şartını yerine getirmeniz gerekmektedir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: 2025_2026_genel_akademik_takvim.pdf - Belge: sık_sorulan_sorular.txt (2 parça) - Belge: 202...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260512_221026-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/pass:required_values_preserved`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260512_221026-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1953.13, "capability_planner_timeout_suspected": false, "routing_ms": 6429.752, "routing_timeout_suspected": false, "conversation_ms": 5510.096, "final_synthesis_ms": 1509.38}`
- Cevap preview: Benchmark, CAP başvurusu için genel not ortalamasının 4,00 üzerinden en fazla 2,50'ye kadar düşebileceği belirtilmektedir. CAP başvurularında diğer koşulların yanı sıra genel not ortalamasının bu sınırda olması önemlidir. Kurumlararası yatay geçiş için ise 4'lük sistemde en az 2,80, 100'lük sistemde en az 72 genel not ortalaması gerekmektedir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça) - Belge: yonerge_cift_anadal_yandal.pdf (2 parça) - Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf - Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf - Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf - Belge: ön_lisans_ve_lisans...
