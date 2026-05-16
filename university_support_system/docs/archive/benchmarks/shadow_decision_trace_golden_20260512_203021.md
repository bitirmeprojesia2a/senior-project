# Shadow Decision Trace Golden Run 20260512_203021

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 1
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260512_203021.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260512_203021.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | 1 | 148152.4 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/check:answer_missing_required_evidence_values; missing=3,00 | 2 | 70970.7 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=3
- Provider hatalari: groq=3
- Fallback cagrilari: 0

## Answer Validator Ozeti

- Kayit: 2 | pass=1 | check=1 | fail=0 | requires_judge=1 | contract_enforceable=0
- Nedenler: answer_missing_required_evidence_values=1, query_does_not_require_value_check=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260512_203021-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- LLM roles: `global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/global_synthesis/primary/error`
- Cevap preview: Benchmark, Ogrenci Isleri: Kaynak bilgisi final cevap için hazırlandı. - ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf: MADDE 4 – (1) Ön lisans ve lisans diploma programlarının hazırlık sınıfına; ön lisans diploma programlarının ilk yarıyılı ile son yarıyılına, lisans diploma programlarının ilk iki yarıyılı ile son iki yarıyılına yatay geçiş yapılamaz. (8) Üniversiteye yapılan yatay geçiş başvuru türüne bakılmaksızın bir dönemde en fazla 2 yatay geçiş başvurusu yapılabilir. - staj_ilkeleri_23122019_inş_müh.pdf: MADDE 10– Yatay ve dikey geçişle gelen öğrencilerin staj muafiyetlerinde, Ondokuz Mayıs Üniversitesi Ders Muafiyeti ve İntibak İşlemleri Uygulama Esasları, çift anadal/yandal yapan öğrencilerde ise Ondokuz Mayıs Üniversitesi Çift Anadal (İkinci Lisans) ve Yandal Programı Yönergesi hükümleri uygulanır. ÜÇÜNCÜ BÖLÜM UYGULAMAYA İLİŞKİN HUSUSLAR Başvuru - yonetmelik_onlisans_lisans_eg...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260512_203021-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `regulation_agent`
- Specialist selector: `academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/check:answer_missing_required_evidence_values; missing=3,00`
- LLM roles: `conversation, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/error; groq/llama-3.3-70b-versatile/final_refinement/primary/error`
- Cevap preview: Benchmark, Kaynak bilgisi final cevap için hazırlandı. - yonerge_cift_anadal_yandal.pdf: ç) ÇAP'a başvurular, Senato tarafından belirlenen ve akademik takvimde belirtilen tarihte, ÖİDB’nin internet sayfasında açılan ilgili link üzerinden elektronik olarak yapılır. d) Öğrenci, duyurulmuş olan ÇAP'a, dört yıllık programlarda ana dal diploma programının en erken üçüncü yarı yılının başında, en geç ise beşinci yarı yılın başında başvurabilir. e)... --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - RAG - Routing: parallel - Pipeline: academic_programs Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf
