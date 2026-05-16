# Shadow Decision Trace Golden Run 20260509_221801

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 12
- Trace kaydi: 12
- Source owner eslesmesi: 7/10
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260509_221801.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260509_221801.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | calendar.academic_date | main_orchestrator | student_affairs | 3 | 5168.6 | OK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | course.detail | main_orchestrator | academic_programs | 3 | 14852.8 | OK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | finance.tuition_fee | main_orchestrator | finance | 2 | 9223.3 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | 6 | 96985.4 | OK |
| GT05 | cross_department | - | student_affairs_policy | - | main_orchestrator | academic_programs, finance | 3 | 20214.2 | OK |
| GT06 | international_policy | international_policy | international_policy | international.policy_lookup | main_orchestrator | student_affairs, academic_programs | 6 | 17238.5 | OK |
| GT07 | announcement | announcement_search | announcement_search | - | announcement_agent | announcement | 1 | 1524.7 | OK |
| GT08 | event | event_search | - | - | clarification | - | 1 | 16109.6 | CHECK |
| GT09 | personal_auth | personal_student_data | tuition_fee_catalog | finance.tuition_fee | department_orchestrator | finance | 2 | 14512.5 | CHECK |
| GT10 | ambiguous | - | - | - | clarification | - | 2 | 10954.9 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | 5 | 15882.0 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | curriculum_catalog | - | department_orchestrator | academic_programs | 3 | 29248.5 | CHECK |

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260509_221801-GT01`
- Trace owner: `academic_calendar`
- Capability: `calendar.academic_date`
- LLM roles: `-`
- Cevap preview: Benchmark, Final sınavları güz dönemi için 03-16 Ocak 2026, bahar dönemi için 01-14 Haziran 2026 tarihlerinde yapılacak. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İl...

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-20260509_221801-GT02`
- Trace owner: `curriculum_catalog`
- Capability: `course.detail`
- LLM roles: `-`
- Cevap preview: Benchmark, BIL203 dersinin AKTS'si 5'tir ve ön koşulu BIL104'dir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: ...

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-20260509_221801-GT03`
- Trace owner: `tuition_fee_catalog`
- Capability: `finance.tuition_fee`
- LLM roles: `-`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Routing: dir...

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260509_221801-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Yatay geçiş yapan bir öğrenci olarak ders muafiyet başvurunuzu, kayıt yaptırdığınız öğretim yılının en geç 3. haftasının sonuna kadar ilgili dekanlık veya müdürlüğe yapmalısınız. Başvuru ve süreçle ilgili dikkat etmeniz gereken detaylar şunlardır: ...

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-20260509_221801-GT05`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, CAP başvurunuz için ana dal programında mezuniyet hakkını elde eden ve ÇAP'ı başarıyla tamamlayan öğrenci olmanız gerekmektedir. Ayrıca, ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması ve önlisans 120 AKTS, lisans 240 AKTS şartını y...

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-20260509_221801-GT06`
- Trace owner: `international_policy`
- Capability: `international.policy_lookup`
- LLM roles: `-`
- Cevap preview: Benchmark, Uluslararası öğrenci kaydı için gereken belgeler arasında öğrenci belgesi, adli sicil belgesi ve ikamet izni bulunur. İkamet izni almanız zorunludur. Öğrenci belgesi, kaydınızı ve üniversitede aktif olarak eğitim aldığınızı kanıtlamanız için gerekl...

### GT07 - announcement

- Soru: Bilgisayar muhendisligindeki son duyurular neler?
- Not: Announcement DB short-circuit ve bolum filtresi.
- Context: `shadow-golden-20260509_221801-GT07`
- Trace owner: `announcement_search`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: İlgili duyurular: 1. 2025-2026 Bahar Yarıyılı Ara Sınav Programı 2025-2026 Bahar Yarıyılı Ara Sınav Programı için tıklayınız.. Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/2025-2026-bahar-yariyili-ara-sinav-programi 2. Vefat Haberi - Öğrencimiz Mahf...

### GT08 - event

- Soru: Bu hafta Muhendislik Fakultesinde seminer var mi?
- Not: Event DB short-circuit ve zaman penceresi.
- Context: `shadow-golden-20260509_221801-GT08`
- Trace owner: `-`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Sorunuzun hangi alana ait olduğunu net olarak belirleyemedim. Aşağıdaki seçeneklerden birini belirterek tekrar sorabilirsiniz: - Öğrenci İşleri (kayıt, not, staj, mezuniyet) - Akademik Programlar (müfredat, yönetmelik, Erasmus) - Finans (harç, burs,...

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-20260509_221801-GT09`
- Trace owner: `tuition_fee_catalog`
- Capability: `finance.tuition_fee`
- LLM roles: `-`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz. Üretim Türü: - Kural - Routing: direct - Pipeline: finance

### GT10 - ambiguous

- Soru: Sey basvuru ne zaman?
- Not: Eksik slot/ambiguity davranisi.
- Context: `shadow-golden-20260509_221801-GT10`
- Trace owner: `-`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260509_221801-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- LLM roles: `-`
- Cevap preview: Benchmark, Çift anadal programına başvurabilmek için ana dal lisans programında mezuniyet hakkını kazanmış olmak ve kayıtlı olunan programın yükümlülüklerini yerine getirmek gerekir. • Ana dal lisans programında mezuniyet hakkını kazanamayan öğrencilere yan d...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260509_221801-cap-followup`
- Trace owner: `curriculum_catalog`
- Capability: `-`
- LLM roles: `-`
- Cevap preview: Benchmark, Eldeki en ilgili kaynakta su bilgi yer aliyor: MADDE 6 – (1) Lisans diploma programlarının hazırlık sınıfına; ilk yılı ile son yılına yatay geçiş yapılamaz. (Değişik: Senato tarih ve karar sayısı (Kaynak: yonerge_uluslararasi_ogrenci_yatay_gecis.pd...
