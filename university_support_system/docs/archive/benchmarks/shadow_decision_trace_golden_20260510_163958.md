# Shadow Decision Trace Golden Run 20260510_163958

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260510_163958.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260510_163958.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | 5 | 56616.0 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/task_type, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | 6 | 13801.2 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=11
- Provider hatalari: -
- Fallback cagrilari: 0

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260510_163958-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Cevap preview: Benchmark, Çift anadal programına başvuru yapmak için ana dal programında kayıtlı olmak ve bazı koşulları sağlamak gerekiyor. Ana dal programında mezuniyet hakkını elde etmek, çift anadal programını başarıyla tamamlayarak ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması ve önlisans 120 AKTS, lisans 240 AKTS şartını yerine getirmek gerekiyor. Önlisans ve lisans diploma programlarının çift anadal başvurularında, ana dal programındaki sınıfa ve not ortalamasına göre değerlendirme yapılır. Başvuru birim komisyonlarınca değerlendirilerek uygun görülen sınıfa öğrencinin intibakı yapılır. Yabancı dil ile eğitim veren programlara başvuru yapabilmek için yabancı dil sınavlarının h...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260510_163958-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/task_type, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Cevap preview: Benchmark, CAP başvurusu için not ortalamasının en az 2,80 olması gerekir. 100'lük sistem kullanan üniversiteler için en az 72 olması se de, bu bilgi bulunamadığı için sadece 2,80 olan genel not ortalaması şartı geçerlidir. Önceki yarıyıllarda aldığınız notların ortalaması da önemlidir, ancak başvuruda genel not ortalamasının yeterli olması ana şarttır. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (4 parça) - Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf - Belge: ön_lisans_ve_lisans_ya...
