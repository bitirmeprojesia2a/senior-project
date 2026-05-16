# Shadow Decision Trace Golden Run 20260510_161303

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260510_161303.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260510_161303.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | 1 | 137184.0 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | 1 | 81348.7 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=2
- Provider hatalari: groq=2
- Fallback cagrilari: 0

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260510_161303-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- LLM roles: `global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/global_synthesis/primary/error`
- Cevap preview: Benchmark, Ogrenci Isleri: Kaynak bilgisi final cevap için hazırlandı. - ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf: MADDE 4 – (1) Ön lisans ve lisans diploma programlarının hazırlık sınıfına; ön lisans (12) Öğrenci kayıt dondurmuş ise yatay geçiş başvurusu sırasında bu durumu belgelendirmesi - staj_ilkeleri_23122019_inş_müh.pdf: MADDE 10– Yatay ve dikey geçişle gelen öğrencilerin staj muafiyetlerinde, - yonetmelik_onlisans_lisans_egitim_ogretim.pdf: MADDE 30- (1) Kayıtlı olduğu programın 14 ...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260510_161303-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- LLM roles: `global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/global_synthesis/primary/error`
- Cevap preview: Benchmark, Ogrenci Isleri: Kaynak bilgisi final cevap için hazırlandı. - yonerge_onlisans_lisans_yatay_gecis.pdf: gördüğü programdaki genel not ortalamasının 100 üzerinden 80 veya üzeri olması ya da kayıt (12) Öğrenci kayıt dondurmuş ise yatay geçiş başvurusu sırasında bu durumu belgelendirmesi - ön_lisans_ve_lisans.pdf: MADDE 30- (1) Kayıtlı olduğu programın 14 üncü maddede belirtilen yükümlülüklerini yerine getiren, ders (5) Ana dal lisans programında mezuniyet hakkını kazanamayan öğrenciye ya...
