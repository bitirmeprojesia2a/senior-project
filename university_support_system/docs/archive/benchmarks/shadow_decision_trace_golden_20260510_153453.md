# Shadow Decision Trace Golden Run 20260510_153453

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 8
- Trace kaydi: 8
- Source owner eslesmesi: 8/8
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260510_153453.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260510_153453.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=-; pruned=-; reason=single_branch | 3 | 5692.2 | OK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | course.detail | main_orchestrator | academic_programs | academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match | 0 | observed: kept=-; pruned=-; reason=single_branch | 3 | 10187.6 | OK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | finance.tuition_fee | main_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | observed: kept=-; pruned=-; reason=single_branch | 2 | 7666.1 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | applied: kept=student_affairs; pruned=academic_programs; reason=student_affairs_policy_contract_gate | 5 | 101312.1 | OK |
| GT06 | international_policy | international_policy | international_policy | international.policy_lookup | main_orchestrator | academic_programs | academic_programs:international_agent/contract, legacy=international_agent:match | 0 | applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch | 5 | 24725.2 | OK |
| GT09 | personal_auth | personal_student_data | personal_student_data | - | clarification | finance | - | 0 | - | 1 | 5204.6 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | 5 | 18637.5 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:internship_agent/contract, legacy=registration_agent:diff; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 1 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | 6 | 19467.0 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=30
- Provider hatalari: groq=3
- Fallback cagrilari: 0

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260510_153453-GT01`
- Trace owner: `academic_calendar`
- Capability: `calendar.academic_date`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract`
- Branch gate: `observed: kept=-; pruned=-; reason=single_branch`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/final_refinement/primary/success`
- Cevap preview: Benchmark, Güz döneminde final sınavları 03-16 Ocak 2026, bahar döneminde ise 01-14 Haziran 2026 tarihlerinde yapılacak. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - VT - Routing:...

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-20260510_153453-GT02`
- Trace owner: `curriculum_catalog`
- Capability: `course.detail`
- Selected specialists: `curriculum_agent`
- Specialist selector: `academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match`
- Branch gate: `observed: kept=-; pruned=-; reason=single_branch`
- LLM roles: `routing, specialist_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/specialist_synthesis/primary/success`
- Cevap preview: Benchmark, BIL203 dersinin AKTS'si 5'dir. BIL203 dersinin ön koşulu BIL104'dir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - VT - Routing: direct - Pipeline: academic_programs

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-20260510_153453-GT03`
- Trace owner: `tuition_fee_catalog`
- Capability: `finance.tuition_fee`
- Selected specialists: `tuition_agent`
- Specialist selector: `finance:tuition_agent/contract, legacy=tuition_agent:match`
- Branch gate: `observed: kept=-; pruned=-; reason=single_branch`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Routing: direct - Pipeline: finance Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260510_153453-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `applied: kept=student_affairs; pruned=academic_programs; reason=student_affairs_policy_contract_gate`
- LLM roles: `routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/error; groq/llama-3.3-70b-versatile/final_refinement/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/final_refinement/primary/success`
- Cevap preview: Benchmark, Yatay geçişle gelen öğrenciler için muafiyet başvurusu süreci, akademik takvimde belirtilen tarihler dentro işler. Önce, öğrenci daha önce aldıkları dersler için muafiyet dilekçesi verir. Ardından, danışman ile birlikte muafiyet başvuruları yapılır ve birim yönetim kurulunun muafiyet talebini uygun görmesi durumunda, muaf olunan dersleri...

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-20260510_153453-GT06`
- Trace owner: `international_policy`
- Capability: `international.policy_lookup`
- Selected specialists: `international_agent`
- Specialist selector: `academic_programs:international_agent/contract, legacy=international_agent:match`
- Branch gate: `applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch`
- LLM roles: `routing, final_refinement, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/final_refinement/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/final_refinement/primary/success`
- Cevap preview: Benchmark, Yabancı öğrenci olarak kayıt için gereken belgeler arasında kayıtlı olduğunuz Fakülte/Yüksekokul/MYO'dan alınacak öğrenim durumunuzu gösteren belge bulunmaktadır. Ayrıca, ikamet izni almanız zorunludur. İkamet izni başvuruları için: • Pasaportun kimlik bilgilerinin yer aldığı ilk sayfa, • Vizenin bulunduğu sayfa ve • Ülkeye giriş yap...

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-20260510_153453-GT09`
- Trace owner: `personal_student_data`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz.

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260510_153453-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Cevap preview: Benchmark, Çift anadal programına başvuruda, ana dal programında mezuniyet hakkını elde edilmemiş olsa bile, öğrencinin ana dal programında kayıtlı olduğu dönemde bu programa başvurabilir. Çift ana dal programının lisans diploması verilebilmesi için, ana dal lisans programından mezuniyet hakkını elde etmiş olmak ve çift ana dal lisans programını ba...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260510_153453-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `internship_agent, regulation_agent`
- Specialist selector: `student_affairs:internship_agent/contract, legacy=registration_agent:diff; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success; groq/llama-3.3-70b-versatile/routing/primary/error; groq/llama-3.3-70b-versatile/routing/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success; groq/llama-3.3-70b-versatile/judge/primary/success; groq/llama-3.3-70b-versatile/global_synthesis/primary/success`
- Cevap preview: Benchmark, Çift anadal programı başvurusu için genel not ortalaması (GANO) koşulu, başvurulacak programa göre değişebilir. Çift anadal programında başarı ve mezuniyet koşulları arasında, ana dal programında mezuniyet hakkını elde etmek ve çift anadal programını başarıyla tamamlamak yer alır. Diploma almaya hak kazanmak için, ders geçme sisteminde G...
