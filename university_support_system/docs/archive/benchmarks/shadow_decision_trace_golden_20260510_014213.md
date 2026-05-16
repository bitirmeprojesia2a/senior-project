# Shadow Decision Trace Golden Run 20260510_014213

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 8
- Trace kaydi: 8
- Source owner eslesmesi: 8/8
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260510_014213.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260510_014213.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | 3 | 17381.9 | OK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | course.detail | main_orchestrator | academic_programs | academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match | 0 | 3 | 17316.5 | OK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | finance.tuition_fee | main_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | 2 | 15170.5 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:curriculum_agent/task_type, legacy=curriculum_agent:match | 0 | 6 | 100435.1 | OK |
| GT06 | international_policy | international_policy | international_policy | international.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:international_agent/contract, legacy=international_agent:match | 0 | 3 | 45947.7 | OK |
| GT09 | personal_auth | personal_student_data | personal_student_data | - | clarification | finance | - | 0 | 1 | 5890.1 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | 3 | 41371.2 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | - | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/task_type, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | 5 | 46237.9 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: anthropic=26
- Provider hatalari: -
- Fallback cagrilari: 0

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260510_014213-GT01`
- Trace owner: `academic_calendar`
- Capability: `calendar.academic_date`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract`
- LLM roles: `routing, final_refinement`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/final_refinement/primary/success`
- Cevap preview: Benchmark, 2025-2026 eğitim-öğretim yılı final sınavları şu tarihlerde başlıyor: • Güz dönemi: 3-16 Ocak 2026 • Bahar dönemi: 1-14 Haziran 2026 --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sen...

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-20260510_014213-GT02`
- Trace owner: `curriculum_catalog`
- Capability: `course.detail`
- Selected specialists: `curriculum_agent`
- Specialist selector: `academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match`
- LLM roles: `routing, specialist_synthesis`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/specialist_synthesis/primary/success`
- Cevap preview: Benchmark, BIL203 - Veri Yapıları dersinin AKTS değeri 5'tir. Bu dersin ön koşulu ise BIL104 - Programlamaya Giriş II dersidir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - VT - Routing: direct - Pip...

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-20260510_014213-GT03`
- Trace owner: `tuition_fee_catalog`
- Capability: `finance.tuition_fee`
- Selected specialists: `tuition_agent`
- Specialist selector: `finance:tuition_agent/contract, legacy=tuition_agent:match`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/routing/primary/success`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Routing: direct - Pipeline: finance Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260510_014213-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, curriculum_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:curriculum_agent/task_type, legacy=curriculum_agent:match`
- LLM roles: `routing, specialist_synthesis, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/specialist_synthesis/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success; anthropic/claude-sonnet-4-6/judge/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success`
- Cevap preview: Benchmark, Muafiyet başvurusunun kesin tarihi kaynaklarda yer almamakla birlikte, kayıt yaptırdıktan sonra ilgili Dekanlık veya Müdürlüğe dilekçeyle başvurman gerekmektedir. Süreç şu şekilde işler: • Başvuruyu aldıktan sonra biriminizin muafiyet ve intibak komisyonu bir muafiyet çizelgesi hazırlar; bu çizelge yönetim kurulu kararıyla birlikte san...

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-20260510_014213-GT06`
- Trace owner: `international_policy`
- Capability: `international.policy_lookup`
- Selected specialists: `international_agent`
- Specialist selector: `academic_programs:international_agent/contract, legacy=international_agent:match`
- LLM roles: `routing, final_refinement`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/final_refinement/primary/success`
- Cevap preview: Benchmark, Uluslararası öğrenci olarak OMÜ'ye kayıt yaptırdıktan sonra Samsun Göç İdaresi Müdürlüğü'nden öğrenci ikamet izni almanız zorunludur. Başvuru için gereken temel belgeler şunlardır: • Talep edilen ikamet izni süresinden 60 günden daha uzun süreli geçerli pasaport veya pasaport yerine geçen belge • İkamet izni kayıt/başvuru formu • 18 ya...

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-20260510_014213-GT09`
- Trace owner: `personal_student_data`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz.

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260510_014213-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- LLM roles: `routing, global_synthesis`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success`
- Cevap preview: Benchmark, Çift anadal programına (ÇAP) başvurabilmek için kayıtlı olduğun ana dal programında belirli koşulları yerine getirmen gerekir. Başvuru süreciyle ilgili temel bilgiler şunlardır: • Başvuru hakkı, ana dal programının 14. maddesinde belirtilen yükümlülükleri yerine getiren öğrencilere tanınır. • ÇAP'ta başarıyı sürdürebilmek için ana dal ...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260510_014213-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/task_type, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-6/conversation/primary/success; anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success; anthropic/claude-sonnet-4-6/judge/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success`
- Cevap preview: Benchmark, Çift anadal programına (ÇAP) başvuru koşulları yönergede belirtilmiş olmakla birlikte, başvuru için gereken GNO eşiği ve yüzdelik dilim gibi sayısal kriterler mevcut kaynak içeriğinde açıkça yer almamaktadır. Başvuru, kabul ve kayıt koşullarının tamamı MADDE 5 kapsamında düzenlenmekte; kontenjanlar ise Senato onayıyla belirlenmekte ve Öğ...
