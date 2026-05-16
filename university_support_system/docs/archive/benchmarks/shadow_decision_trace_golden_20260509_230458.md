# Shadow Decision Trace Golden Run 20260509_230458

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 12
- Trace kaydi: 12
- Source owner eslesmesi: 4/10
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260509_230458.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260509_230458.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | student_affairs_policy | - | main_orchestrator | student_affairs | 3 | 4680.8 | CHECK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | - | main_orchestrator | academic_programs | 2 | 2833.5 | OK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | - | main_orchestrator | finance | 2 | 2243.1 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs | 3 | 54403.6 | OK |
| GT05 | cross_department | - | student_affairs_policy | - | main_orchestrator | academic_programs, finance | 4 | 16188.8 | OK |
| GT06 | international_policy | international_policy | student_affairs_policy | - | main_orchestrator | academic_programs, student_affairs | 4 | 6087.4 | CHECK |
| GT07 | announcement | announcement_search | - | - | clarification | - | 1 | 12338.0 | CHECK |
| GT08 | event | event_search | - | - | clarification | - | 2 | 3266.6 | CHECK |
| GT09 | personal_auth | personal_student_data | tuition_fee_catalog | - | department_orchestrator | finance | 2 | 2837.0 | CHECK |
| GT10 | ambiguous | - | - | - | clarification | - | 1 | 1242.7 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | 4 | 6548.0 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | - | - | department_orchestrator | student_affairs | 3 | 6265.0 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: anthropic=31
- Provider hatalari: anthropic=31
- Fallback cagrilari: 0

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260509_230458-GT01`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/final_refinement/primary/error`
- Cevap preview: Benchmark, Genel akademik takvime gore yariyil sonu/final sinavlari guz donemi icin 03-16 Ocak 2026, bahar donemi icin 01-14 Haziran 2026 tarihlerindedir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - VT - Routing: direct - Pipeline: student_affairs Kaynak Özeti: - Belge: 2025_2026_genel_akademik_takvim.pdf

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-20260509_230458-GT02`
- Trace owner: `curriculum_catalog`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/routing/primary/error`
- Cevap preview: Benchmark, BIL203 Veri Yapilari (3 kredi, 5 AKTS) dersinin önkoşulları: BIL104 Programlamaya Giris II. Önkoşullu derslerden en az DD alınmış olması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - VT - Routing: direct - Pipeline: academic_programs Kaynak Özeti: - Veritabani kaydi: ders onkosulu

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-20260509_230458-GT03`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/routing/primary/error`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Routing: direct - Pipeline: finance Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260509_230458-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/final_refinement/primary/error`
- Cevap preview: Benchmark, Kaynak bilgisi final cevap için hazırlandı. - ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf: MADDE 6 - (1) Komisyon, öğrencilerin yeterlik başvurusunda bulundukları, daha önce (2) Yeterlik ve/veya muafiyet talebi, ilgili yönetim kurulu tarafından karara bağlanıncaya - sık_sorulan_sorular.txt: Daha önceden başardığım derslerden muaf tutulabilmem için ne yapmam gerekir? Fakülteye/yüksekokula/meslek yüksekokuluna ilk kez kayıt yaptıran öğrenciler, eğitim öğretimin başladığı tarihten itibaren üç hafta içinde daha önce öğrenim gördüğü yükseköğretim kurumlarında aldığı ve başarılı olduğu dersler için muaf olmak istediği dersleri içeren bir dilekçe,... - sık_sorulan_sorular.txt: Yatay geçişle gelen öğrenciler, başvurdukları yarıyıla; dikey geçişle gelen öğrenciler, beşinci yarıyıla; merkezi yerleştirme sınavları ile gelen öğrenciler ise birinci yarıyıla intibak ettirilir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - RAG - Routing: direct - Pipeline: student_affairs Kaynak Özeti: - Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf - Belge: sık_sorulan_sorular.txt (3 parça) - Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-20260509_230458-GT05`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/global_synthesis/primary/error; anthropic/claude-sonnet-4-20250514/judge/primary/error`
- Cevap preview: Benchmark, Akademik Programlar: Kaynak bilgisi final cevap için hazırlandı. - yonerge_cift_anadal_yandal.pdf: MADDE 8 - (1) ÇAP'ta başarı ve mezuniyet koşulları şunlardır: a) Ana dal programında mezuniyet hakkını elde eden ve ÇAP’ı başarıyla tamamlayan f) Öğrencinin ÇAP’tan mezun olabilmesi için ana dal genel not ortalamasının 4,00 üzerinden - yonerge_cift_anadal_yandal.pdf: MADDE 3 - (1) Bu Yönergede geçen; - yonerge_cift_anadal_yandal.pdf: MADDE 15 - (1) Ana dal programından mezuniyet hakkını elde eden ve YDP’yi 4,00 (5) Azami süre içinde YDP öğreniminin tamamlanamaması nedeniyle ilave ders alınması Finans: Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Akademik Programlar: RAG - Finans: VT - Routing: parallel - Pipeline: academic_programs -> finance Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Veritabani kaydi: ogrenim ucreti tablosu

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-20260509_230458-GT06`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/global_synthesis/primary/error; anthropic/claude-sonnet-4-20250514/judge/primary/error`
- Cevap preview: Benchmark, Ogrenci Isleri: Kaynak bilgisi final cevap için hazırlandı. - öğrenci_konukevi_uygulama_yönergesi.pdf: MADDE 12 - (1) Uzun süreli konaklama, 1 (bir) aydan daha uzun süreli Akademik Programlar: - ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf: İKAMET İZNİ KAYIT/BAŞVURU FORMU i 18 yaşından küçük öğrenciler için muvafakatname sahibi kişi tarafından kendi adı soyadı - ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf: i Talep edilen ikamet izni süresinden 60 (altmış) gün daha uzun süreli pasaport ya da pasaport - ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf: Ofisimize gelirken öğrenci ikamet izni başvurusu için gerekli belgeleri eksiksiz olarak bitmeden) en geç 7 gün içerisinde belgelerinizin Ofisimize teslim edilmesi gerekmektedir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs Kaynak Özeti: - Belge: ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf (4 parça) - Belge: uluslararası_öğrenci_yönergesi.pdf - Belge: öğrenci_konukevi_uygulama_yönergesi.pdf

### GT07 - announcement

- Soru: Bilgisayar muhendisligindeki son duyurular neler?
- Not: Announcement DB short-circuit ve bolum filtresi.
- Context: `shadow-golden-20260509_230458-GT07`
- Trace owner: `-`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-20250514/routing/primary/error`
- Cevap preview: Benchmark, Sorunuzun hangi alana ait olduğunu net olarak belirleyemedim. Aşağıdaki seçeneklerden birini belirterek tekrar sorabilirsiniz: - Öğrenci İşleri (kayıt, not, staj, mezuniyet) - Akademik Programlar (müfredat, yönetmelik, Erasmus) - Finans (harç, burs, ödeme)

### GT08 - event

- Soru: Bu hafta Muhendislik Fakultesinde seminer var mi?
- Not: Event DB short-circuit ve zaman penceresi.
- Context: `shadow-golden-20260509_230458-GT08`
- Trace owner: `-`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/routing/primary/error`
- Cevap preview: Benchmark, Sorunuzun hangi alana ait olduğunu net olarak belirleyemedim. Aşağıdaki seçeneklerden birini belirterek tekrar sorabilirsiniz: - Öğrenci İşleri (kayıt, not, staj, mezuniyet) - Akademik Programlar (müfredat, yönetmelik, Erasmus) - Finans (harç, burs, ödeme)

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-20260509_230458-GT09`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/routing/primary/error`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz. Üretim Türü: - Kural - Routing: direct - Pipeline: finance

### GT10 - ambiguous

- Soru: Sey basvuru ne zaman?
- Not: Eksik slot/ambiguity davranisi.
- Context: `shadow-golden-20260509_230458-GT10`
- Trace owner: `-`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-20250514/routing/primary/error`
- Cevap preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260509_230458-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/global_synthesis/primary/error; anthropic/claude-sonnet-4-20250514/judge/primary/error`
- Cevap preview: Benchmark, Ogrenci Isleri: Kaynak bilgisi final cevap için hazırlandı. - ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf: MADDE 4 – (1) Ön lisans ve lisans diploma programlarının hazırlık sınıfına; ön lisans (12) Öğrenci kayıt dondurmuş ise yatay geçiş başvurusu sırasında bu durumu belgelendirmesi - staj_ilkeleri_23122019_inş_müh.pdf: MADDE 10– Yatay ve dikey geçişle gelen öğrencilerin staj muafiyetlerinde, - yonetmelik_onlisans_lisans_egitim_ogretim.pdf: MADDE 30- (1) Kayıtlı olduğu programın 14 üncü maddede belirtilen yükümlülüklerini yerine getiren, ders (5) Ana dal lisans programında mezuniyet hakkını kazanamayan öğrenciye yan dal sertifikası verilmez. Akademik Programlar: - yonerge_cift_anadal_yandal.pdf: b) ÇAP öğrencileri arasında başarı sıralaması yapılmaz. c) ÇAP öğrenimi sırasında lisans öğrenimi gördükleri ana daldan mezun olan öğrencilerin d) Azami süre içinde ÇAP öğreniminin tamamlanamaması nedeniyle ilave ders alınması - yonerge_cift_anadal_yandal.pdf: MADDE 6 - (1) ÇAP, ilgili bölümün önerisi ve birim yönetim kurulu kararı ile üç yıl için (2) ÇAP öğrencisine, ikinci ana dal programında da ilgili bölüm başkanlığı tarafından - yonerge_cift_anadal_yandal.pdf: MADDE 3 - (1) Bu Yönergede geçen; --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260509_230458-cap-followup`
- Trace owner: `-`
- Capability: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/routing/primary/error; anthropic/claude-sonnet-4-20250514/final_refinement/primary/error`
- Cevap preview: Benchmark, Eldeki en ilgili kaynakta su bilgi yer aliyor: MADDE 6 - (1) Üniversitemize yatay geçişler, diğer yükseköğretim kurumlarındaki aynı düzeydeki eşdeğer diploma programlarından yapılır. PP.1.2.PRS.0048, R0, Temmuz Sayfa 2 / 5 2025 (2) Kurumlar arası yatay geçişlerde öğrencinin kayıtlı olduğu programda genel not ortalamasının 4 lük sistem kullanan üniversiteler için en az 2.80, 100 lük sistem kullanan üniversiteler için en az 72 olması gerekir. Transkriptinde iki not sistemi de var ise 100 lük sistemdeki notu kullanılır. (3) Üniversitemizdeki ön lisans ve lisans programları için belirlenen yatay geçiş kontenjanları ile başvuru ve (Kaynak: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf) --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - RAG - Routing: direct - Pipeline: student_affairs Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf - Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf - Belge: yonerge_onlisans_lisans_yatay_gecis.pdf - Belge: ön_lisans_ve_lisans.pdf
