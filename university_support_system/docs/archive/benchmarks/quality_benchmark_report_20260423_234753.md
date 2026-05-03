# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-23 23:47:53
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 44.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 4581.2 ms |
| Medyan Sure | 3897.6 ms |
| Intent Analizi Aktif | 0/7 |
| Force LLM Sentez | 0/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=7, query_failures=0, agent_tasks=9, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 2/4 | 2944.7 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 3897.6 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 7608.1 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 2504.4 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 5347.6 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 8012.9 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 1752.8 | - |

## Soru Detaylari

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] değiştirebilir
  - [ ] devam koşulu
  - [x] yeni
  - [x] ders
- **Sure**: 2944.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Sorunun cevabı:
Eğer bir seçmeli ders yerine başka bir seçmeli ders seçerlerseniz, devama devam zorunluluğunuz değişmez. Ancak, devama devam zorunluluğu olan dersleri başarısız olduğunuz takdirde, sonraki dönemde/yıl devamınızı kaydederek bir başka seçmeli dersi alabilirsiniz.

Yaniti verebilmek için referans aldığım yonetmelik:
[Kaynak 1: yonetmelik_onlisans_lisans_egitim_ogretim.pdf]
MADDE 2: (1) Bu Yönetmelik, Ondokuz Mayıs Üniversitesi (OMU) ön lisans ve lisans eğitim-öğretim programlarına ilişkin esaslara açıklık getirmek, öğrencilerin hak ve sorumluluklarını belirlemek ve eğitim-öğretim etkinliklerinin planlanması, uygulanması ve değerlendirilmesine ilişkin usul ve esasları düzenlemektir.
 

Devama devam zorunluluğu MADDE 19- (1) Azami öğrenim süresi içerisinde mezun olamayan öğrenciler bakımından, öğretim programı değişikliği veya ders içeriğinin değişmesi halinde, daha önce başarılı olunan derslerden hangilerinin yeniden alınacağı, ilgili birim/bölüm kurulu önerisi üzerine Senato tarafından belirlenir. (2) Öğrenci; danışmanın onayıyla, başarısız olduğu bir seçmeli ders yerine, sonraki dönemde/yılda devam etmek kaydıyla, bir başka seçmeli dersi alabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yaz_okulu_eğitim_öğretim.pdf
- Belge: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] not ortalaması
  - [x] harç
  - [ ] ödeme
  - [x] başvuru
- **Sure**: 3897.6 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Benchmark, ÇAP programına başvurmak için harç borcu olan öğrencilerin başvuru şartları şunlardır:

* ÇAP'a başvurabilmek için ana dal lisans programında yer alan tüm dersleri almış ve başarmış olmanız gerekir.
* Başvurduğunuz yarı yıla kadar ana dal lisans programında yer alan tüm dersleri almış ve başarmış olmanız gerekir.
* Başvurusu sırasında ana dal not ortalaması en az 3,00 olmalıdır.

Harç borcunu ödeyebileceğiniz bazı seçenekler şunlardır:

* ÖİDB'ye başvurabilir ve ilgili bölüme başvurabilirsiniz.
* ÖİDB'nin internet sayfasını ziyaret edebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: VT
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Sure**: 7608.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki temel farklar nelerdir?

Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasında bazı farklar bulunmaktadır. Kurum içi yatay geçiş, aynı üniversite içinde öğrencinin diplomalı bir programdan diğer diplomalı bir programa geçişini ifade ederken, kurumlar arası yatay geçiş, farklı üniversiteler arasında veya vakıf üniversiteleri ile öğrencinin diplomalı bir programdan diğer diplomalı bir programa geçişini ifade eder.

Kurum içi yatay geçişimde;
- Aynı üniversitede öğrencinin diplomasız veya diplomalı bir programdan diplomasız veya diplomalı bir programa geçişi,
- Ön lisans ve lisans diploma programlarının hazırlık sınıfına, ön lisans diploma programlarının ilk yarıyılı ile son yarıyılına, lisans diploma programlarının ilk iki yarıyılı ile son iki yarıyılına yatay geçiş yapılamaz,
- Bir alt sınıfa/yarı yıla yapılan başvurular kabul edilmez.

Kurumlar arası yatay geçişimde;
- Farklı üniversiteler arasında veya vakıf üniversiteleri ile öğrencinin diplomalı bir programdan diğer diplomalı bir programa geçişi,
- Aynı düzey programlar arasındaki yatay geçişlerde öğrencinin merkezi yerleştirme sınav puanı esas alınır. Öğrencinin aldığı merkezi yerleştirme puanının yurt içindeki diğer üniversitelerin başvurulan program için geçerli olan puan türündeki en düşük taban puanından az olmaması gerekir,
- Özel yetenek sınavı ile öğrenci kabul edilen diploma programlarına kurum içi yatay geçişlerde diğer şartların yanı sıra özel yetenek sınavında da başarılı olma şartı aranır.

Kurum içi yatay geçiş başvuruları, ilan edilen süre içinde üniversitede bulunan Disiplin Kurulu kararı ile öğrencinin diplomasız veya diplomalı bir programa geçişi yapılır. Öğrenci kayıt dondurulmuş ise yatay geçiş başvurusu sırasında bu durumu belgelendirmesi gerekir. Disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez. Başvuru esnasında disiplin cezası almadıklarını belgelemeleri şarttır.

Yürütülen yatay geçi
... (1086 karakter daha)
```

### Q20: Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] 2. nüsha
  - [x] diploma
  - [x] e-devlet
  - [ ] YÖKSİS
- **Sure**: 2504.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için neler yapmalıyım?

Diplomamı kaybettim:
- Evet, diplomanızı kaybederseniz yaygın gazetelerden birine diploma kayıp ilanı vermelisiniz.
- Diploma kayıp ilanı, başvuru dilekçesinden, onaylı nüfus cüzdanının sureti ve diploma ücretini yatırdığını gösteren banka dekontunuza ekleyerek, diploma aldığınız birimden diploma talep etmelisiniz.
- İlk diplomada yer alan bilgileri içeren yeni bir diploma düzenlenecek ve üzerinde "İkinci Nüsha" bilgisi yer alacaktır.

E-Devlet mezuniyet bilgilerimin görünmüyor:
- Evet, bu durumda başvuru formu çıktısı, öğrenci belgesi, transkript, ÖSYM sınav sonuç belgesi ve ÖSYM yerleştirme belgesi ile beraber kayıt başvurunuzu yaptırmalısınız.

Soru acikca lisansüstü (yuksek lisans/doktora) programı bahsetmediği için, lisans programı kurallarını kullanacağım.

Kayitlarinizin yerine getirilmesinde, asil belgelerin getirmesi zorunludur (belgenin fotokopisi, e-posta çıktısı vb kabul edilmemektedir).

Ayrıca, belgenizin aslına dayanarak onay işlemi gerçeklebilir; ancak e-devlet üzerinden alınan belgeler için onay şartı aranmayacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Sure**: 5347.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sınavlarda kopya çekilmesinin cezası nedir?

Kaynaklar, sınavlarda kopya çekilmesinin ve bununla ilgili girişimlerin bir disiplin suçu olduğunu açıklamaktadır.

Bu konuda elimdeki kaynaklarda net bilgi bulunan bir düzenleme 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesinde yapılmaktadır. Ancak, kopya çekilmesinin cezası ile ilgili detaylı bir bilgi bulmamaktadır.

Kaynaklardan, kopya çekilmesinin disiplin suçu olarak değerlendirildiği ve sınav görevlileri tarafından öğrenciler hakkında işlem yapabilecekleri görülmektedir. Ancak, ceza ve disiplin süreci ile ilgili detaylı bir bilgi bulunmamaktadır.

Oluşturulan düzenlemede, bu konuda elimdeki kaynaklarda net bilgi bulunamadığından, bu soruya net bir yanıt veremiyorum.

Sınav esnasında başka bir öğrenciyle not paylaşılması veya cep telefonu ile ilgilenilmesi hallerinde öğrencilere kopya muamelesi yapılır mı?

Evet, sınav esnasında başka bir öğrenciyle not paylaşılması veya cep telefonu ile ilgilenilmesi hallerinde öğrencilere kopya muamelesi yapılır.

Bu konuda kaynaklar, sınav esnasında sıraların üzerinde, altında veya yan oturaklarda bulunan eşyalardan her öğrenci sorumlu olduğu ve cep telefonunun sınav esnasında kesinlikle kapalı tutulacağı belirtmektedir. Hesap makinesi, kalem, silgi veya kullanımına izin verilen tablo gibi araç ve gereçlerin başka bir öğrenci ile paylaşılması yasaktır ve bu tür paylaşımlar kopya olarak değerlendirilir.

Bu konudaki düzenleme 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesi ve OMÜ Mühendislik Fakültesi Öğrenci Kimlik Belgesini yanında bulundurmak mecburiyeti ile ilgili düzenlemede yer almakta olup, disiplin süreci ile ilgili daha detaylı bir bilgi bulunmamaktadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: staj_ilkeleri_231
... (53 karakter daha)
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [x] birim
- **Sure**: 8012.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Siz üniversiteyi bırakmak istiyorsanız, ilk olarak yazılı talebinizle üyeliğinizin sonlandırılması için öğrenci organizasyonuna başvurmalısınız. Bu durumda, yönetim kurulu kararı ile üyeliğiniz sonlandırılacak ve 7 gün içinde SKSDB'ye itiraz başvurusunda bulunabilirsiniz.

Eğer üyeliğiniz sonlandırılmasaydı, disiplin cezası alırsanız veya öğrenci kayıt kaydı iptal edilirse üyeliğiniz kendiliğinden sona erecektir. Bu durumda 7 gün içinde SKSDB'ye itiraz başvurusunda bulunabilirsiniz.

Üncü durumda, üyeliğiniz sonlandırılan öğrenciler aynı topluluğa tekrar üye olamaz. Bu gibi durumlarda, siz tekrar üye olmak istemediğinizden, üyeliğinizle ilgili işlemlerinizi tamamlamış olacaksınız.

Kayıt yaptırmak ve kayıt yenilemek ile ilgili konularda, ÖSYM tarafından yerine getirilen öğrenci kayıtları, YÖK ve üniversite tarafından belirlenen ilkeler çerçevesinde yapılacaktır. İlgili birimin yönetim kurulu tarafından karar verilerek, öğrenci kaydı yenilenir.

Ders kaydı ve seçmeli derslerde, öğrenciler akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden ders kayıtlarını yaptıralacak ve danışman onayı ile kayıt işlemi kesinleşecektir. Kayıt yaptırmayan öğrenciler, kayıt yenileme hakkını kaybedeceklerdir.

Kayıt yaptırmaya dair konularda, öğrenciler akademik takvimde belirtilen süre içinde mazeretlerinin haklı ve geçerli olduğu ilgili birimin yönetim kurulunca kabul edilmek koşuluyla öğrenci bilgi sistemi üzerinden kayıt yaptırabilirler.

Ancak akademik takvimde belirtilen süre içinde kayıtlarını yenilemeyen öğrenciler, kayıt yaptıramayacaklardır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: öğrenci_toplulukları_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: işyeri_staj_sözleşmesi
... (4 karakter daha)
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [x] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Sure**: 1752.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Soru: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

Yanit: Ders seçimini yapabilmek için, Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği'nde belirtilen kayıt dondurma ve süresi uzatma kuralarına uymamız gerekiyor. Kayıt donduran öğrenci, öğrenimine devam edemez ve kayıt dondurduğu döneme/yıla ait sınavlara giremez.

Kesin yanıt için kaynaklardan devam ediyoruz:

MADDE 31 – (1) Kayıt donduran öğrenci, öğrenimine devam edemez ve kayıt dondurduğu döneme/yıla ait sınavlara giremez. Kayıt dondurma süresinin bitiminde öğrenci; ayrıldığı dönemin/yılın başından başlamak koşuluyla, öğrenimine kaldığı yerden devam eder.

Akademik takvimde belirlenen süre içinde ders kaydını yapmayan öğrenciler, o dönemde öğrenimlerine devam etme hakkını kaybederler. Kaybedilen dönem, öğrenim süresinden sayılır.

Ön lisans ve lisans programlarında, ders kayıt esnasında öğrenciler, dersler UZAKTAN EĞİTİM ve YÜZYÜZE EĞİTİM şeklinde iki alternatifle sunulacaktır. Dilediğiniz eğitim şeklini ilk kayıt aşamasında tercih etmek durumundasınız. Uzaktan eğitimi seçmeniz durumunda ücretini ödemek durumundasınız.

Bu doğrultuda, ders seçimini yapabilmek için, akademik takvimde belirtilmiş olan süre içinde öğrenci bilgi sistemi üzerinden alacakları dersleri seçmeleri gerekiyor. Bu süreç, danışman onayı ile kesinleşir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
```
