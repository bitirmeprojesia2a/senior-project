# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 01:22:50
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 52.0% |
| Temiz Kalite Orani | 85.7% |
| Ortalama Sure | 6102.6 ms |
| Medyan Sure | 2910.6 ms |
| Intent Analizi Aktif | 7/7 |
| Force LLM Sentez | 5/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=7, query_failures=0, agent_tasks=10, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 3/4 | 1558.6 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 19280.1 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 8808.0 | uydurma_riski |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 6119.9 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 2438.4 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 2910.6 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 1602.5 | - |

## Soru Detaylari

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [x] yeni
  - [x] ders
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=1351ms; student_affairs_orchestrator=1408ms
- **API Sureleri**: api_total=1529ms; dispatch=1427ms; compose=7ms; telemetry=7ms
- **Sure**: 1558.6 ms
- **API Response Time**: 1452.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Soru:
Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

Yanit: 

Devam zorunluluğunuz değmez. 

Kaynak: [Kaynak 1: yonetmelik_onlisans_lisans_egitim_ogretim.pdf]

MADDE 19-(1) Azami öğrenim süresi içerisinde mezun olamayan öğrenciler bakımından, öğretim programı değişikliği veya ders içeriğinin değişmesi halinde, daha önceki derslerden hangilerinin yeniden alınacağı, ilgili birim/bölüm kurulu önerisi üzerine Senato tarafından belirlenir. 

Devam zorunluluğu koşulu yerine getirilmediği durumlarda tekrar derslere devam esastır. Bu durumda, devam koşulunu yerine getirmeyen öğrencilerin listesi sorumlu öğretim elemanı tarafından öğrencilere duyurulmak üzere ilgili bölüme/birime teslim edilir. [Kaynak 2: yonetmelik_onlisans_lisans_egitim_ogretim.pdf]

MADDE 17-(1) Derslere devam durumu, dersin öğretim elemanınca yapılan yoklamalarla tespit edilir. 

Bu durumda, devam koşulu olmayan derslerde dönem içi değerlendirmelerine katılmak zorunludur. 

Yaz okulunda açıklandığı gibi derslere devam zorunluluğu devam etmektedir. [Kaynak 3: yaz_okulu_eğitim_öğretim.pdf]

MADDE 12 - (1) Yaz okulunda derslere devam zorunludur.

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
- **Departman**: ['finance', 'student_affairs', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: tuition_agent=19ms; finance_orchestrator=245ms; registration_agent=3192ms; student_affairs_orchestrator=3260ms; regulation_agent=13363ms; academic_programs_orchestrator=13827ms
- **API Sureleri**: api_total=19216ms; dispatch=13979ms; global_llm=4064ms; compose=4075ms; telemetry=16ms
- **Sure**: 19280.1 ms
- **API Response Time**: 19131.1 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
Benchmark, ÇAP Programına Başvuru ve Harç Borçu

ÇAP programına başvurmak istediğinizde, harç borcunuzun varlığından dolayı endişe etmenize gerek yoktur. Harç borcunuzun ödenmesi ile ilgili olarak sorunun cevabı "hayır" ve kaynaklarda da net bir ifade yoktur; yani ÇAP programına başvuru yaptığınızda harç borcunu ödemenize gerek yoktur.

Sorusuna Doğru Cevap

- ÇAP programına başvurmak için bazı şartlar bulunmaktadır. Bu şartlar; ÇAP açılması uygun görülen birimler, en geç eğitim-öğretim yılı sonunda alınacak öğrenci sayılarını belirler ve birim kuruluna sunarlar.
- İlgili birim kurul, her akademik yılın haziran ayının ortasına kadar bölümlerin önerdiği kontenjanları karara bağlar. Senato’nun onayı ile kontenjan kesinleşir.
- ÖİDB, Senato’nun onayladığı kontenjanları temmuz ayının başında duyurur.
- ÇAP kontenjanları, mühendislik programları hariç, programların başvuru alınan yıla ait ÖSYM kontenjanının % 20’sinden az olmamak üzere, program bazlı olarak tespit edilerek birim yönetim kurulu kararı ile Senato tarafından belirlenir.

Harç Borcu Ödenmesi

- Belirtildiği gibi harç borcu ödeyebilirisiniz ve öğrencilik haklarınızı kullanabilirsiniz.
- Ödemeler, akademik takvimde belirtilen süreler içinde her eğitim-öğretim döneminde/yılında öğrenci katkı payını/öğrenim ücretini ödemelidir.

Gereken Adım

- Ödemeleri zamanında yapmayı ihmal etmeyin.
- Öğrenim ücreti 2025-2026 yılları için 2.397,00 TL ve her dönemlik öğrenim ücreti 1.198,50 TL’dir.

Kanit Bilgi

- Öğrenci katkı payını/öğrenim ücretini ödemeyen öğrenciler ders kaydı yaptıramaz ve öğrencilik haklarından yararlanamaz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: VT
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yone
... (250 karakter daha)
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=3056ms; student_affairs_orchestrator=3119ms; international_agent=6228ms; academic_programs_orchestrator=6332ms
- **API Sureleri**: api_total=8746ms; dispatch=6380ms; global_llm=1354ms; compose=1372ms; telemetry=32ms
- **Sure**: 8808.0 ms
- **API Response Time**: 8645.1 ms
- **Kaynak Sayisi**: 10
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Benchmark, Kurum İçi Yatay Geçiş ile Kurumlar Arası Yatay Geçiş Arasındaki Farklar

Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? 

Bunlar arasında temel fark, geçiş yapma hakkı kazanan kimselerin olduğu husustur. Kurum içi yatay geçiş, bir üniversite içinde farklı bir bölüm veya program arasında yapılabilirken, kurumlar arası yatay geçiş ise farklı üniversiteler arasında yapılabilir.

Ayrıca, kurum içi yatay geçiş başvurusu genellikle öğrencinin bir ders ya da yarıyıl sonrasında yapılırken, kurumlar arası yatay geçiş başvurusu genellikle öğrencinin bir akademik yılın sonuna doğru yapılır.

Genel olarak, öğrencilerin hangi şartlar altında yatay geçiş yapabildikleri hususunda bazı farklılıklar görülmektedir.

* Kurum İçi Yatay Geçiş: İsimleri aynı olan veya ilgili yönetim kurulları tarafından içeriklerinin en az yüzde sekseni mesma olduğu tespit edilen diploma programlarına yatay geçiş yapılır.
* Kurumlararası Yatay Geçiş: Bir üniversite, yüksek teknoloji enstitüsü veya bir üniversiteye bağlı olmaksızın vakıflar tarafından kurulan meslek yüksekokullarından Ondokuz Mayıs Üniversitesindeki eşdeğer eğitim veren fakülte, yüksekokul veya bölüme yapılan geçiş yapılır.

Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir? 

Bunlar arasında temel farklılık, öğrencilerin hangi değerlendirme kriterlerine göre değerlendirileceği husustur.

* Kurum İçi Yatay Geçiş: Öğrencilerin önceki not ortalamaları veya merkezi yerleştirme puanları dikkate alınır.
* Kurumlararası Yatay Geçiş: Öğrencilerin önceki not ortalaması, merkezi yerleştirme puanı ve genel not ortalaması dikkate alınır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisan
... (301 karakter daha)
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=5010ms; student_affairs_orchestrator=5127ms
- **API Sureleri**: api_total=6103ms; dispatch=5160ms; compose=9ms; telemetry=11ms
- **Sure**: 6119.9 ms
- **API Response Time**: 6043.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Sorunun cevabı:

1. Diplomasını kaybeden öğrenci ilk olarak yaygın gazeteden diploma kayıp ilanı vermeli ve ardından başvuru dilekçesi ve onaylı nüfus cüzdanı sureti ile diploma ücretini yatırdıklarını gösteren banka dekontu ile diploma aldıkları birime müracaat etmelidir. Bu öğrencilere ilk diplomada yer alan bilgileri içeren yeni bir diploma düzenlenir ve üzerinde İkinci Nüsha olduğu bilgisi yer alır.

Kaynak: Uygulama esasları - Diploma ve mezuniyet belgeleri - Kaynak 1, Madde 17 (1)

2. E-Devlet üzerinden mezuniyet bilgilerinin görünmemesi için öğrenci, e-Devlet üzerinden ilgili diplomayı alma işlemini gerçekleştirerek, diplomasını alabilir ve ardından mevcutta öğrencilikle ilgili bilgileri ve diplomasını Öğrenci İşleri Daire Başkanlığı'na teslim etmelidir.

Kaynak: Belgeler - E-Devlet Belgesi - Kaynak 4, Sayfa 2

Bilgi:
- e-Devlet üzerinden diplomanın alındığında, e-Devlet belgesini Öğrenci İşleri Daire Başkanlığı'na iletmeniz gerekir.

Kaynak Doğrulama:
- E-Devlet belgesi hakkında bilgi bulunmamaktadır.

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=2203ms; student_affairs_orchestrator=2283ms
- **API Sureleri**: api_total=2421ms; dispatch=2329ms; compose=5ms; telemetry=12ms
- **Sure**: 2438.4 ms
- **API Response Time**: 2351.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

Yanit: 
- Kopya çekilmesinin cezası, sınavda öğrenciye kopya muamelesi yapılmasıdır. Bu, öğrencinin sınav sırasında ve sonrasındaki davranışıyla ilişkilidir.
- Disiplin süreci, 2547 sayılı Yükseköğretim Kanununun 54. Maddesine göre yürütülmektedir. 
- Sınav görevlisi veya ilgili öğretim elemanı, öğrencinin sınav sırasında kopya çekilmesine veya başka bir disiplin suçu işlemesine göz kulak olurlar. 
- Gözlenen bir suçu bildirdiklerinde, sınav görevlisi veya ilgili öğretim elemanı, sınavı durdurabilir veya öğrenciyi salondan çıkarabilir. 
- Disiplin soruşturması, Fakülte Dekanlığı/Yüksekokul Müdürlüğü veya Meslek Yüksekokulu Müdürlüğü tarafından yükseköğretim kurumları öğrenci disiplin yönetmeliğine göre yürütülür.
- Sonuç, işletmeye veya ilgili birimlere yazılı olarak bildirilir.
- Soruşturmanın tamamlanmasıyla birlikte, öğrencinin durumu Fakülte Dekanlığı/Yüksekokul Müdürlüğü veya Meslek Yüksekokulu Müdürlüğü tarafından yeniden değerlendirilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: staj_ilkeleri_23122019_inş_müh.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=1602ms; student_affairs_orchestrator=1697ms
- **API Sureleri**: api_total=2889ms; dispatch=1721ms; compose=9ms; telemetry=11ms
- **Sure**: 2910.6 ms
- **API Response Time**: 2826.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Soru: Üniversitesi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misiniz?

Soruya Doğru Yanıt:
Evet, sizi desteklemeye hazırlız. Öncelikle, Üniversitemizde öğrencinin üyeliğini sona erdirme sürecine tabi olacak durumlar var. Bu durumlarda, öğrenci yazılı talebi, üyeliğe son veren Yönetim Kurulu ve Danışman onayı da gerektirir.

Yönetmelik Onayları:
- Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği gereğince öğrencinin disiplin cezası aldıktan sonra üyeliği kendiliğinden sona erer.
- Toplulukların adı ve logosu için 10 öğrencinin üye bulunması gerekir. Bu sayının azalması halinde, öğrenci danışman onayı ile öğrenci bilgi sistemi üzerinden açılabilir yeni derslere kaydı.
Kayıt Yenileme: 
- Akademik takvimde belirlenen süre içinde ders kaydını yapmayan öğrenciler o dönemde öğrenimine devam etme hakkı kaybeder.
- Kayıt yenileme süresi içerisinde öğrenci mazeretinin haklı ve geçerli olduğu durumda, kayıt yenilemesi ilgili birimin yönetim kurulu tarafından kabul edilebilir.
- Öğrenci, kayıt yaptıracakları derslerin AKTS kredileri toplamı, ilgili AKTS kredisi sınırını aşmamak koşuluyla, bir üst sınıftan ders alabilir. Yandal ve çift anadal öğrencilerinin AKTS kredisi üst sınırı, ilgili birimin yönetim kurulu tarafından belirlenir.
Tebliğ ve Adres Bildirme:
- Üyeliği sona eren öğrenciye, tebliğ tarihinden itibaren 7 gün içinde SKSDB’ye itiraz başvurusunda bulunma hakkı verilir.

Sonuç:
- Üyeliğiniz sona erdiren durumlar için, Yönetim Kurulu kararı ve Danışman onayı gereklidir.
- Kayıt yenileme süreleri dışında öğrenci ders kaydı yapmayınca o döneme ait hakkı kaybeder.
- Öğrenim planına uygun ders kaydı yapmayan öğrenci kaydı iptal edilebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: öğrenci_toplulukları_yönergesi.pdf
- Belge: yonetmelik
... (131 karakter daha)
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [x] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=1246ms; student_affairs_orchestrator=1478ms
- **API Sureleri**: api_total=1591ms; dispatch=1505ms; compose=7ms; telemetry=14ms
- **Sure**: 1602.5 ms
- **API Response Time**: 1529.2 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Soru: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

Yanit: Ders seçiminizi, kayıt dönemi başlamadan transkript/müfredat kontrolünü yaparak akademik takvimde tanımlanan süre içerisinde öğrenci bilgi yönetim sistemi üzerinden yapabilirsiniz. 

Detaylar:
- Transkript/müfredat kontrolünü akademik takvimde belirtilen süre içerisinde yapın.
- Ders seçiminizi öğrenci bilgi yönetim sistemi üzerinden yapın.
- Sistem üzerinden ders seçiminizi onaylamanız için danışmanınıza göndermeniz gerekebilir.
- Danışmanınız, onaylandıktan sonra ders seçiminin kesin kayda dönüştüğünü takip edebilir.

 Kayıt dondurma süresinin bitiminde öğrenci ayrıldığı dönemin/yılın başından başlamak koşuluyla, öğrenimine kaldığı yerden devam eder. Bu nedenle 1 yıl ara verdikten sonra dönüşte ders seçimini yaparken ayrıldığınız dönemin/yılın başından başlamak koşuluyla öğrenimine kaldığı yerden devam edeceğiniz dersleri seçmelisiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
