# Shadow Decision Trace Golden Run 20260509_231253

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 12
- Trace kaydi: 12
- Source owner eslesmesi: 7/10
- Hata sayisi: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260509_231253.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260509_231253.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | student_affairs_policy | - | main_orchestrator | student_affairs | 2 | 11887.5 | CHECK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | - | main_orchestrator | academic_programs | 1 | 7789.4 | OK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | - | main_orchestrator | finance | 1 | 7447.8 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | 3 | 69386.0 | OK |
| GT05 | cross_department | - | student_affairs_policy | - | main_orchestrator | academic_programs, student_affairs, finance | 4 | 37278.9 | OK |
| GT06 | international_policy | international_policy | student_affairs_policy | - | main_orchestrator | academic_programs, student_affairs | 4 | 40721.2 | CHECK |
| GT07 | announcement | announcement_search | announcement_search | - | announcement_agent | announcement | 1 | 7674.3 | OK |
| GT08 | event | event_search | event_search | - | event_agent | event | 1 | 7368.9 | OK |
| GT09 | personal_auth | personal_student_data | personal_student_data | - | clarification | finance | 1 | 3422.2 | OK |
| GT10 | ambiguous | - | - | - | clarification | - | 1 | 3883.5 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | 4 | 30298.5 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | curriculum_catalog | - | clarification | academic_programs | 1 | 3655.3 | CHECK |

## LLM Kullanim Ozeti

- Provider cagrilari: anthropic=24
- Provider hatalari: -
- Fallback cagrilari: 0

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260509_231253-GT01`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/final_refinement/primary/success`
- Cevap preview: Benchmark, 2025-2026 eğitim öğretim yılı final sınavları şu tarihlerde gerçekleşecek: • Güz dönemi final sınavları: 3-16 Ocak 2026 • Bahar dönemi final sınavları: 1-14 Haziran 2026 --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - VT - Routing: direct - Pipeline: student_affairs -> orchestrator Kaynak Özeti: - Belge: 2025_2026_genel_akademik_takvim.pdf

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-20260509_231253-GT02`
- Trace owner: `curriculum_catalog`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success`
- Cevap preview: Benchmark, BIL203 Veri Yapilari (3 kredi, 5 AKTS) dersinin önkoşulları: BIL104 Programlamaya Giris II. Önkoşullu derslerden en az DD alınmış olması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - VT - Routing: direct - Pipeline: academic_programs Kaynak Özeti: - Veritabani kaydi: ders onkosulu

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-20260509_231253-GT03`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Routing: direct - Pipeline: finance Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260509_231253-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success; anthropic/claude-sonnet-4-6/judge/primary/success`
- Cevap preview: Benchmark, Yatay geçişle gelip ilk kez kayıt yaptıran öğrenciler, ders muafiyeti başvurusunu eğitim öğretimin başladığı tarihten itibaren üç hafta içinde yapmalıdır. Başvuru için dilekçenin yanı sıra onaylı transkript ve onaylı ders içeriklerini ilgili fakülte, yüksekokul veya meslek yüksekokuluna teslim etmen gerekir. Başvurun sonuçlanana kadar mağdur olmamak için dönem derslerine devam etmeye özen göster. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf - Belge: sık_sorulan_sorular.txt (3 parça) - Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf - Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf - Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf - Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf - Belge: bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-20260509_231253-GT05`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success; anthropic/claude-sonnet-4-6/judge/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success`
- Cevap preview: Benchmark, ÇAP'ta başarı ve mezuniyet koşulları şunlardır: • ÇAP'ı başarıyla tamamlayan ve ana dal programında mezuniyet hakkını elde eden öğrenciye ikinci ana dalın lisans diploması verilir; ancak ana daldan mezuniyet hakkı elde edilmeden ÇAP lisans diploması verilmez. • ÇAP öğrencileri arasında sınıf içinde başarı sıralaması yapılmaz. • ÇAP danışmanı, ilgili bölümün önerisi ve birim yönetim kurulu kararıyla üç yıl için seçilir; her iki programın danışmanları birlikte öğrencinin ders programını hazırlar. Harç ve öğrenim ücreti ödemesine gelince, yönetmeliğe göre öğrencilerin akademik takvimde belirtilen süreler içinde her öğretim döneminde ilgili mevzuatta belirlenen katkı payını veya öğrenim ücretini ödemesi gerekmektedir. Ödemenin hangi kanal üzerinden yapılacağı ve tam ücret tutarı kaynaklarda yer almadığından bu konuyu öğrenci işleri ya da finans birimi ile doğruca teyit etmen gerekir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Finans: VT - Routing: parallel - Pipeline: academic_programs -> student_affairs -> finance -> orchestrator Kaynak Özeti: - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf - Belge: yonerge_cift_anadal_yandal.pdf (3 parça) - Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf - Belge: yonerge_onlisans_lisans_yatay_gecis.pdf - Belge: ön_lisans_ve_lisans.pdf (2 parça) - Veritabani kaydi: ogrenim ucreti tablosu

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-20260509_231253-GT06`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success; anthropic/claude-sonnet-4-6/judge/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success`
- Cevap preview: Benchmark, Kayıt işlemleri, Öğrenci İşleri Daire Başkanlığı tarafından şahsen yapılan kesin kayıt veya elektronik ortamda yapılan ön kayıt biçiminde iki farklı yöntemle yürütülür. Kesin kayıt için gerekli belgeler senato tarafından belirlenerek uluslararası öğrenci alım kılavuzunda ilan edilir; bu listeye kılavuzdan ya da Öğrenci İşleri Daire Başkanlığı'ndan ulaşabilirsin. İkamet izni başvurusu için gereken belgeler şunlardır: • İkamet izni kayıt/başvuru formu: e-ikamet.goc.gov.tr adresi üzerinden oluşturulan ve öğrenci tarafından imzalanmış form. • Pasaport fotokopileri: Kimlik bilgilerinin yer aldığı ilk sayfa, varsa vizenin bulunduğu sayfa ve ülkeye en son giriş yapılan damganın yer aldığı sayfa, her biri ayrı sayfada olacak şekilde fotokopi olarak sunulmalıdır. Belgenin aslı dosya teslim gününde yanında bulunmalıdır. Pasaport, talep edilen ikamet izni süresinden en az 60 gün daha uzun süreli geçerliliğe sahip olmalıdır. • Öğrencilik durumunu gösterir belge: Kayıtlı olduğun fakülte, yüksekokul veya meslek yüksekokulundan alınan belge. Tüm belgeler hazırlandıktan sonra başvuru formu oluşturulduğu tarihten itibaren en geç 7 gün içinde Öğrenci İşleri Daire Başkanlığı İkamet İşlemleri Ofisi'ne teslim edilmesi gerekir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf (3 parça) - Belge: uluslararası_öğrenci_yönergesi.pdf - Belge: uluslararası_öğrenci_ikamet_işlemleri.pdf - Belge:...

### GT07 - announcement

- Soru: Bilgisayar muhendisligindeki son duyurular neler?
- Not: Announcement DB short-circuit ve bolum filtresi.
- Context: `shadow-golden-20260509_231253-GT07`
- Trace owner: `announcement_search`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success`
- Cevap preview: İlgili duyurular: 1. Vefat Haberi - Öğrencimiz Mahfuz AGİL Ondokuz Mayıs Üniversitesi Bilgisayar Mühendisliği Bölümü son sınıf öğrencilerimizden Mahfuz Agil’in vefatını derin bir üzüntüyle öğrenmiş bulunmaktay… Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/vefat-haberi-ogrencimiz-mahfuz-agil 2. 2024-2025 Eğitim Öğretim Yılı Ek Sınav I ve II Sınav Programları 2024-2025 Eğitim Öğretim Yılı Bilgisayar Mühendisliği Bölümü Ek Sınav I ve II Sınav Programları için tıklayınız. Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/2024-2025-egitim-ogretim-yili-ek-sinav-i-sinav-programi 3. TBFİZ121 FİZİK I ve TBFİZ123 FİZİK I DERSİNİ ALAN ÖĞRENCİLERİN DİKKATİNE! Laboratuvardan Devam Almış fakat Ders Tekrarı Olan Öğrencilerin Laboratuvar Notunu Belirlemek Üzere, LABORATUVAR SINAVI YAPILACAKTIR. Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/tbfiz121-fizik-i-ve-tbfiz123-fizik-i-dersini-alan-ogrencilerin-dikkatine 4. Sayısal Denetim 2 ve Bilgisayarlı Görüye Giriş Derslerinin Değerlendirmeleri Hakkında 2023-2024 Bahar dönenimdeki Sayısal Denetim 2 ve Bilgisayarlı Görüye Giriş derslerinin değerlendirmeleri hakkında bilgi almak için tıklayınız. Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/sayisal-denetim-2-ve-bilgisayarli-goerueye-giris-derslerinin-degerlendirmeleri-hakkinda Ek bağlantı: Bahar Dönemi Değerlendirme Usulü Hakkında Duyuru - https://bil-muhendislik.omu.edu.tr/tr/haberler/sayisal-denetim-2-ve-bilgisayarli-goerueye-giris-derslerinin-degerlendirmeleri-hakkinda/Bahar Dönemi Değerlendirme Usulü Hakkında Duyuru.pdf 5. 2. Ek Sınav Gün ve Tarihleri Bi...

### GT08 - event

- Soru: Bu hafta Muhendislik Fakultesinde seminer var mi?
- Not: Event DB short-circuit ve zaman penceresi.
- Context: `shadow-golden-20260509_231253-GT08`
- Trace owner: `event_search`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success`
- Cevap preview: Bu sorguya uygun guncel veya yakin tarihli etkinlik bulamadim. Isterseniz fakulte, bolum ya da etkinlik turu belirterek tekrar sorabilirsiniz. Kaynak Özeti: - Veritabanı kaydı: etkinlik araması (uygun kayıt bulunamadı)

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-20260509_231253-GT09`
- Trace owner: `personal_student_data`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz.

### GT10 - ambiguous

- Soru: Sey basvuru ne zaman?
- Not: Eksik slot/ambiguity davranisi.
- Context: `shadow-golden-20260509_231253-GT10`
- Trace owner: `-`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success`
- Cevap preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260509_231253-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success; anthropic/claude-sonnet-4-6/judge/primary/success; anthropic/claude-sonnet-4-6/global_synthesis/primary/success`
- Cevap preview: Benchmark, Çift anadal programına (ÇAP) başvuru yapmak için öncelikle kayıtlı olduğun ana dal programındaki yükümlülüklerini yerine getirmiş olman gerekir. Kaynakta bu konuda ayrıntılı başvuru koşulları ve süreci tam olarak yer almamaktadır. Kesin başvuru koşullarını, gerekli not ortalamasını ve başvuru takvimini öğrenmek için bağlı olduğun fakülte ya da yüksekokulun öğrenci işleri birimine danışman en doğru yol olacaktır. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: ön_lisans_ve_lisans.pdf - Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf - Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf - Belge: yonerge_onlisans_lisans_yatay_gecis.pdf - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (2 parça) - Belge: yonerge_cift_anadal_yandal.pdf (3 parça)

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260509_231253-cap-followup`
- Trace owner: `curriculum_catalog`
- Capability: `-`
- LLM roles: `routing`
- LLM usage: `anthropic/claude-sonnet-4-6/routing/primary/success`
- Cevap preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.
