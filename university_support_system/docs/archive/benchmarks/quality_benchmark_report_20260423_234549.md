# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-23 23:45:49
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 52.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 25200.8 ms |
| Medyan Sure | 17242.1 ms |
| Intent Analizi Aktif | 0/7 |
| Force LLM Sentez | 0/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=7, query_failures=0, agent_tasks=9, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 2/4 | 45836.0 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 41648.6 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 59497.0 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 17242.1 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 5803.7 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 3919.0 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 2459.0 | - |

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
- **Sure**: 45836.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Soru:
Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

Yaniti:
Yeniden bir seçmeli ders seçmeniz halinde, önceki dersin devamsızlık sorunuyla bağlantılı olmaması koşulu ile, devamsızlık zorunluluğu ortadan kalkmaz. Ancak, yeni seçilen dersin devamsızlık oranı hesabında hesabta yeni dersin devamsızlık oranı dikkate alınır.

Kaynak Bilgisi:
Ondokuz Mayıs Üniversitesi Eğitim-Öğretim ve Sınav Yönetmeliği (RG-19, 8, 2013) - MADDE 17/ (1)

Buna göre, derslere devam durumu, dersin öğretim elemanınca yapılan yoklamalarla tespit edilir. Örgün eğitimde öğrencilerin yüz yüze yürütülen derslerin teorik saatlerinin en az % 70’ine; ders uygulamaları, atölye ve laboratuvarların ise en az % 80’ine devam etmeleri zorunludur.

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
- **Key Facts**: 4/4
  - [x] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Sure**: 41648.6 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Benchmark, ÇAP Başvurusu Sorumluluk ve Yönergesi

ÇAP programına başvurmak ve harç borcunu ödeyebilmek için, bazı şartlar ve kurallar vardır.

Başvuru Şartları

- Başvuru yapılan yarı yılın sonuna kadar ana dal lisanse programına kayıtlı olmak,
- Başvuru tarihinde ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması,
- Ana dal diploma programının ilk % 20'sinde bulunmak,
- Dört yıllık programlardan dördüncü yarı yılına başvuru yapılabilmektedir. Her iki ana dal programına devam ederken, öğrenci Ondokuz Mayıs Üniversitesi Lisans Eğitim-Öğretim Yönetmeliği hükümlerine uymalıdır.

Harç Borcunun Ödenmesi

Harç borcunun ödenebilmesi için, ilgili akademik birimlerle görüşülerek çözüm bulunması ve öğrencinin borçlarını tamamlaması gereklidir. ÇAP'a kayıtlı öğrencilerin her iki ana dal programında da harçlıklar ödemeleri gereken durumlar söz konusu olup öğrenciler bu durumu kontrol etmelidirler.

Not: 
- ÇAP programı, öğrencinin öğrenim ücretini ödeyerek öğrencilikten ayrılmaması ve aynı zamanda öğrencilikten ayrılmaması gerektirir. 
- Harçlıkların ödendiği tarih çerçevesinde, ÇAP programına başvurmak mümkündür.

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
- **Sure**: 59497.0 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Kurum içi Yatay Geçiş ile Kurumlar Arası Yatay Geçiş Arasındaki Farklar

Kurum içi yatay geçiş ve kurumlar arası yatay geçiş arasında temel farklar vardır. Her iki geçiş tipinde de öğrencinin daha iyi program veya bölümde eğitim görmesi hedeflenir, ancak farklı koşullar ve değerlendirme kriterleri uygulanır.

Kurum İçi Yatay Geçiş

* Aynı yükseköğretim kurumundaki farklı program veya bölümdeki bir öğrencinin farklı programa geçişi anlaşılır.
* Yükseköğretim Kurulu onayı alınarak önceden ilan edilen kontenjan ve şartlar çerçevesinde yapılır.
* Uluslararası öğrencilerin eğitim gördüğü yükseköğretim kurumunda herhangi bir disiplin cezası almamış olması gerekir.
* Başvurular, üniversite tarafından belirlenen ve önceden ilan edilen Akademik Takvim çerçevesinde yapılır.
* Lisans programları arasında geçiş için, genel not ortalamasının %60'ı ve merkezi yerleştirme puanının %40'ı esas alınarak başarı puanları hesaplanır.

Kurumlar arası Yatay Geçiş

* Farklı yükseköğretim kurumundan gelen öğrencilerin aynı yükseköğretim kurumunda farklı program veya bölümdeki bir programa geçişi anlaşılır.
* Yükseköğretim Kurulu onayı alınarak önceden ilan edilen kontenjan ve şartlar çerçevesinde yapılır.
* Uluslararası öğrencilerin eğitim gördüğü yükseköğretim kurumunda herhangi bir disiplin cezası almamış olması gerekir.
* Başvurular, üniversite tarafından belirlenen ve önceden ilan edilen Akademik Takvim çerçevesinde yapılır.
* Lisansüstü programa geçiş için; ilgili üniversite veya yüksek teknoloji enstitüsü içinde başka bir enstitü anabilim/anasanat dalında ve başka bir yükseköğretim kurumunun lisansüstü programına geçişe izin verilir.

Başvuru Şartları ve Derlendirme Kriterleri

* Kurum içi yatay geçiş başvurusu için, genel not ortalamasının en az 2,80 olması koşulu uygulanır.
* Kurumlararası yatay geçiş başvurusunda, merkezi yerleştirme sınav puanı esas alınır ve alınan puanın, uygulanan puan türündeki en düşük taban puanından az olması gerekir.
* Lisans programları arasınd
... (778 karakter daha)
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
- **Sure**: 17242.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. 

1. Diplomamı kaybettim:
Diplomamı kaybettiğinizde, yaygın gazetelerden birine diploma kayıp ilanı vermeniz gerekir. Ardından, bu ilanının yer aldığı gazete, başvuru dilekçesi ve onaylı nüfus cüzdanı sureti ile diploma aldığınız birime müracaat etmelisiniz. İlk diplomada yer alan bilgileri içeren yeni bir diploma düzenlenir ve üzerinde İkinci Nüsha olduğu bilgisi yer alacaktır. (Kaynak 1: Madde 17)

2. E-devlette mezuniyet bilgilerim görünmüyor:
E-devlette mezuniyet bilgilerinizi görünemiyorsanız, muhtemelnin nedeni diploma kayıp ilanı verilmemiş veya diplomanızın onay süreci tamamlanmamış olmalıdır. E-devlette kayıtlarınızla ilgili durumunuzu Öğrenci İşleri Daire Başkanlığından öğrenmelisiniz.

Yaklaşık süreye göre:
- Diploma kaybına bağlı olarak diploma yenilenmesi süresi belgeye bağlı olarak değişmektedir, ancak genel olarak bu işlemin en geç 5-10 gün içinde tamamlanması beklenmektedir.

Güncelleme ve Not:
Gerekli başvurular sonrasında diploma yenilenmesi suretiyle e-devlette kayıtlarınız güncellenmelidir.

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
- **Sure**: 5803.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sınavda kopya çekilmesinin cezası nedir? 
Belge Baglamina gore cevabi veriyorum.

Sınavda kopya çekme disiplin suçu olarak nitelenir. Bu durum, sınav sorunsuz bir biçimde yürütülmesinden sorumludur ve bu konuda tam yetkili olan gözetmen tarafından tespit edilebilir ve uyarıda bulunmaksızın öğrenciler hakkında işlem yapılabilir. (Kaynak 2)

Disiplin suçu tespiti üzerine, öğrenci hakkında disiplin soruşturması açılabilir ve öğrencinin stajını geçersiz sayabilirler. (Kaynak 5)

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
- **Sure**: 3919.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Üniversiteyi bırakıp ayrılmak istediğinizde, aşağıdaki işlemleri dikkat etmeniz ve takip etmeniz gerekir:

1. Yazılı talebi oluşturun: Öğrenci Toplulukları Yönergesine göre (MADDE 18), öğrencinin yazılı talebi ile üyeliği sonlandırılabilir. Bu nedenle, yazılı talebinizi oluşturmanız ve yönetim kuruluna sunmanız gerekir.

2. Tebliğ tarihinden itibaren 7 gün içinde itiraz başvurusunda bulunun: Üyeliğiniz kesildiği tarih itibarıyla, 7 gün içinde SKSDB’ye itiraz başvurusunda bulunabilirsiniz. İtiraz başvurusunu, başvuru tarihinden sonra toplanan ilk Etkinlik Kurulunda görüşülerek karara bağlanır.

3. Kesin kayıtlarını sildirin: Yüksekokul ve lisans programlarından kesin kayıtlarını sildirirken, ÖSYM tarafından kabul gören öğrenciler, YÖK ve Üniversite tarafından belirlenen ilkeler çerçevesinde kaydolurlar. Zamanında başvurmayan ve istenen belgeleri tamamlamayan öğrenci kayıt hakkını kaybeder.

4. Ders kaydı yaptırın: Ders kaydı, kayıt yenileme ve kayıt iptalinde, öğrenciler akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden ders kaydı yaptırmalıdır. Kayıt yaptırmayan öğrenciler, o dönemde öğrenimine devam etme hakkını kaybederler. Kaybedilen dönem öğrenim süresinden sayılır.

5. Özetlemlerinizi alın: Öğrencilik hizmetlerinden ve üniversiteye ait haklarınızı öğrenmek için ilgili birimlerle iletişime geçmelisiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: öğrenci_toplulukları_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
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
- **Sure**: 2459.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Soru: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

Yanit: Soru'nun cevabı, Önlisans ve Lisans Eğitim Öğretim Yönetmeliği belgesindeki kurallara göre şekillendiği için aşağıdaki cevabı verebilirim.

Kayıt Döneminde Ders Seçimi Yapma

- Kayıt dönemi başlamadan transkript/müfredat kontrolü yaparak akademik takvimde tanımlanan süre içerisinde ders kaydını yapmaları gerektiği bilgisini alacaksın.
- Ders kaydınızı akademik takvim dahilinde yapamayan öğrenciler, o dönemde öğrenimlerine devam etme hakkını kaybederler. (Kaynak 2, Madden 31)
- Süresi içinde ders kaydını yapmayan öğrencilerin kayıtları; başvurmaları ve mazeretlerinin haklı ve geçerli olduğu ilgili birim yönetim kurulunca kabul edilmesi koşuluyla, akademik takvimde belirtilen süre içinde yapılabilir.
- Kayıt dönemi başlamadan ders seçmeniz gerekiyor. Ders kayıt yaptırdığınız dönemde/yılda almakla yükümlü olduğunuz derslerin toplam AKTS kredisi bir dönemde/yılda alınabilecek toplam AKTS kredisinin altında ise dönemdeki/yıldaki AKTS kredisi sınırını aşmamak şartı ile üst sınıftan/sınıflardan ders alabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
```
