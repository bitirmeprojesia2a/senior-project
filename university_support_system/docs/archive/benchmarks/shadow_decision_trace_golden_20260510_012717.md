# Shadow Decision Trace Golden Run 20260510_012717

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 8
- Trace kaydi: 8
- Source owner eslesmesi: 7/8
- Hata sayisi: 0
- LLM profile: fast
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260510_012717.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260510_012717.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | - | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | 1 | 46635.7 | OK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | - | main_orchestrator | academic_programs | academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match | 0 | 0 | 29921.5 | OK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | - | main_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | 0 | 29497.3 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs | student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | 1 | 93866.1 | OK |
| GT06 | international_policy | international_policy | international_policy | - | main_orchestrator | academic_programs, student_affairs | academic_programs:international_agent/contract, legacy=international_agent:match; student_affairs:registration_agent/task_type, legacy=registration_agent:match | 0 | 1 | 71926.0 | OK |
| GT09 | personal_auth | personal_student_data | tuition_fee_catalog | - | department_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | 0 | 28555.6 | CHECK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | 1 | 60192.9 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | student_affairs:internship_agent/contract, legacy=registration_agent:diff; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 1 | 2 | 77881.5 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=6
- Provider hatalari: groq=6
- Fallback cagrilari: 0

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260510_012717-GT01`
- Trace owner: `academic_calendar`
- Capability: `-`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract`
- LLM roles: `final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/final_refinement/primary/error`
- Cevap preview: Benchmark, Genel akademik takvime gore yariyil sonu/final sinavlari guz donemi icin 03-16 Ocak 2026, bahar donemi icin 01-14 Haziran 2026 tarihlerindedir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: -...

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-20260510_012717-GT02`
- Trace owner: `curriculum_catalog`
- Capability: `-`
- Selected specialists: `curriculum_agent`
- Specialist selector: `academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match`
- LLM roles: `-`
- LLM usage: `-`
- Cevap preview: Benchmark, BIL203 Veri Yapilari (3 kredi, 5 AKTS) dersinin önkoşulları: BIL104 Programlamaya Giris II. Önkoşullu derslerden en az DD alınmış olması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü:...

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-20260510_012717-GT03`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- Selected specialists: `tuition_agent`
- Specialist selector: `finance:tuition_agent/contract, legacy=tuition_agent:match`
- LLM roles: `-`
- LLM usage: `-`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Routing: direct - Pipeline: finance Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260510_012717-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match`
- LLM roles: `final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/final_refinement/primary/error`
- Cevap preview: Benchmark, Kaynak bilgisi final cevap için hazırlandı. - ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf: MADDE 6 - (1) Komisyon, öğrencilerin yeterlik başvurusunda bulundukları, daha önce (2) Yeterlik ve/veya muafiyet talebi, ilgili yönetim kurulu tarafından karara bağlanıncaya - sık_sorulan_sorular.txt: Daha önceden başardığım derslerden muaf tut...

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-20260510_012717-GT06`
- Trace owner: `international_policy`
- Capability: `-`
- Selected specialists: `international_agent, registration_agent`
- Specialist selector: `academic_programs:international_agent/contract, legacy=international_agent:match; student_affairs:registration_agent/task_type, legacy=registration_agent:match`
- LLM roles: `global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/global_synthesis/primary/error`
- Cevap preview: Benchmark, Ogrenci Isleri: Kaynak bilgisi final cevap için hazırlandı. - öğrenci_konukevi_uygulama_yönergesi.pdf: MADDE 12 - (1) Uzun süreli konaklama, 1 (bir) aydan daha uzun süreli Akademik Programlar: - ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf: İKAMET İZNİ KAYIT/BAŞVURU FORMU i 18 yaşından küçük öğrenciler için muvafakatname sahibi ...

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-20260510_012717-GT09`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- Selected specialists: `tuition_agent`
- Specialist selector: `finance:tuition_agent/contract, legacy=tuition_agent:match`
- LLM roles: `-`
- LLM usage: `-`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz. Üretim Türü: - Kural - Routing: direct - Pipeline: finance

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260510_012717-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- LLM roles: `global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/global_synthesis/primary/error`
- Cevap preview: Benchmark, Ogrenci Isleri: Kaynak bilgisi final cevap için hazırlandı. - ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf: MADDE 4 – (1) Ön lisans ve lisans diploma programlarının hazırlık sınıfına; ön lisans (12) Öğrenci kayıt dondurmuş ise yatay geçiş başvurusu sırasında bu durumu belgelendirmesi - staj_ilkeleri_23122019_inş_müh.pdf: MADDE 10– Yatay...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260510_012717-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `internship_agent, regulation_agent`
- Specialist selector: `student_affairs:internship_agent/contract, legacy=registration_agent:diff; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- LLM roles: `conversation, global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/error; groq/llama-3.3-70b-versatile/global_synthesis/primary/error`
- Cevap preview: Benchmark, Ogrenci Isleri: Kaynak bilgisi final cevap için hazırlandı. - yonerge_onlisans_lisans_yatay_gecis.pdf: gördüğü programdaki genel not ortalamasının 100 üzerinden 80 veya üzeri olması ya da kayıt (12) Öğrenci kayıt dondurmuş ise yatay geçiş başvurusu sırasında bu durumu belgelendirmesi - ön_lisans_ve_lisans.pdf: MADDE 30- (1) Kayıtlı olduğ...
