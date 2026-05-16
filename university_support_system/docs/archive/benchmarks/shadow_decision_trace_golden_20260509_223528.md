# Shadow Decision Trace Golden Run 20260509_223528

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 12
- Trace kaydi: 12
- Source owner eslesmesi: 5/10
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260509_223528.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260509_223528.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | 3 | 6879.6 | OK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | course.detail | main_orchestrator | academic_programs | 3 | 15857.4 | OK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | - | main_orchestrator | finance | 1 | 10966.0 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs | 3 | 60141.6 | OK |
| GT05 | cross_department | - | student_affairs_policy | none | main_orchestrator | academic_programs, student_affairs, finance | 5 | 20923.3 | OK |
| GT06 | international_policy | international_policy | student_affairs_policy | - | main_orchestrator | academic_programs, student_affairs | 5 | 39779.5 | CHECK |
| GT07 | announcement | announcement_search | - | - | clarification | - | 1 | 16958.0 | CHECK |
| GT08 | event | event_search | - | - | clarification | - | 1 | 16577.0 | CHECK |
| GT09 | personal_auth | personal_student_data | tuition_fee_catalog | - | department_orchestrator | finance | 2 | 14786.5 | CHECK |
| GT10 | ambiguous | - | - | - | clarification | - | 2 | 8791.5 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | 4 | 26760.6 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | - | - | department_orchestrator | student_affairs | 4 | 19496.4 | CHECK |

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260509_223528-GT01`
- Trace owner: `academic_calendar`
- Capability: `calendar.academic_date`
- LLM roles: `-`
- Cevap preview: Benchmark, Öğrenci işleri bölümünden gelen bilgiye göre, genel akademik takvime göre yarıyıl sonu/final sınavları güz dönemi için 03-16 Ocak 2026, bahar dönemi için 01-14 Haziran 2026 tarihlerinde gerçekleşiyor. --- Daha iyi yardımcı olabilmem için sorunuzu d...

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-20260509_223528-GT02`
- Trace owner: `curriculum_catalog`
- Capability: `course.detail`
- LLM roles: `-`
- Cevap preview: Benchmark, BIL203 dersinin AKTS'si 5'tir ve ön koşulu BIL104 dersidir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim T...

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-20260509_223528-GT03`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Routing: dir...

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260509_223528-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- LLM roles: `-`
- Cevap preview: Benchmark, Yatay geçişle gelen öğrenciler, başvurdukları yarıyıla intibak ettirilir. Muafiyet başvurusu için ilgili yönetim kurulunun kararını beklemeniz gerekir. Daha önce aldığınız dersler için Dekanlığa/Müdürlüğe muafiyet dilekçesi vermeniz gerekir. Birim Y...

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-20260509_223528-GT05`
- Trace owner: `student_affairs_policy`
- Capability: `none`
- LLM roles: `-`
- Cevap preview: Benchmark, Çift anadal programı başvuru koşulları: • Öğrencinin ana dal programında mezuniyet hakkını elde etmesi gerekir. • Çift anadal programını başarıyla tamamlaması gerekir. • Öğrencinin çift anadal programından mezun olabilmesi için ana dal genel not ort...

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-20260509_223528-GT06`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Yabancı öğrenci kaydı için gereken belgeler ve ikamet izni başvurusu hakkında bilgi bulunmamaktadır. Ancak, ikamet izni başvurusunda 18 yaşından küçük öğrenciler için muvafakatname sahibi kişi tarafından kendi adı soyadı ile talep edilen ikamet izni...

### GT07 - announcement

- Soru: Bilgisayar muhendisligindeki son duyurular neler?
- Not: Announcement DB short-circuit ve bolum filtresi.
- Context: `shadow-golden-20260509_223528-GT07`
- Trace owner: `-`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Sorunuzun hangi alana ait olduğunu net olarak belirleyemedim. Aşağıdaki seçeneklerden birini belirterek tekrar sorabilirsiniz: - Öğrenci İşleri (kayıt, not, staj, mezuniyet) - Akademik Programlar (müfredat, yönetmelik, Erasmus) - Finans (harç, burs,...

### GT08 - event

- Soru: Bu hafta Muhendislik Fakultesinde seminer var mi?
- Not: Event DB short-circuit ve zaman penceresi.
- Context: `shadow-golden-20260509_223528-GT08`
- Trace owner: `-`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Sorunuzun hangi alana ait olduğunu net olarak belirleyemedim. Aşağıdaki seçeneklerden birini belirterek tekrar sorabilirsiniz: - Öğrenci İşleri (kayıt, not, staj, mezuniyet) - Akademik Programlar (müfredat, yönetmelik, Erasmus) - Finans (harç, burs,...

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-20260509_223528-GT09`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz. Üretim Türü: - Kural - Routing: direct - Pipeline: finance

### GT10 - ambiguous

- Soru: Sey basvuru ne zaman?
- Not: Eksik slot/ambiguity davranisi.
- Context: `shadow-golden-20260509_223528-GT10`
- Trace owner: `-`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260509_223528-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Ön lisans veya lisans diploma programlarının ikinci öğretimine kontenjan sınırı olmaksızın yatay geçiş yapılabilir. Ancak disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez. Bir dönem içinde en fazla 2 yatay geçiş başvurusu yap...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260509_223528-cap-followup`
- Trace owner: `-`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Öğrencinin kayıtlı olduğu programda genel not ortalamasının 4'lük sistem kullanan üniversiteler için en az 2.80, 100'lük sistem kullanan üniversiteler için en az 72 olması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklaya...
