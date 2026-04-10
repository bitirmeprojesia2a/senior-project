# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 20:38:24
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 80.0% |
| Uretim Modu Dogrulugu | 96.0% |
| Anahtar Bilgi Kapsami | 55.0% |
| Temiz Kalite Orani | 96.0% |
| Ortalama Sure | 8366.9 ms |
| Medyan Sure | 6747.9 ms |
| Intent Analizi Aktif | 22/25 |
| Force LLM Sentez | 21/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 8417.4 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 2/3 | 7128.5 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | OK | 1/4 | 6228.5 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 3/4 | 10151.0 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | YANLIS | OK | 3/3 | 7066.4 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 9216.4 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 3/5 | 6606.0 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 3/5 | 9651.9 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | OK | 4/5 | 5558.3 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 6928.2 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | YANLIS | OK | 2/4 | 7916.3 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 2/4 | 61023.2 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 6747.9 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 4/4 | 3790.0 | uydurma_riski |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 2/3 | 4532.8 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 8328.3 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 7885.9 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 1/4 | 1617.3 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 3/6 | 7084.9 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 5227.1 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | YANLIS | OK | 1/5 | 3939.7 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 4128.2 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 3226.8 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 2766.9 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 1/3 | 4005.3 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 8417.4 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu kayıtlı olduğu programda bitirmiş olduğu döneme ait genel not ortalaması en az 2.80 olana kadar yapmalıdır. Bu durum, öğrencinin disiplin cezası almadan ve kayıt dondurulmaya kadar başvuru yapmasına da bağlıdır. Karar çıkana kadar derslere devam edilmelidir.

Detaylara bakıldığında, yatay geçişle gelen bir öğrenci muafiyet başvurusu için:

- Disiplin cezası almayan ve kayıt dondurulmamış olması,
- Kayıtlı olduğu programa ait genel not ortalamasının en az 2.80 olması gereklidir.
- Karar çıkana kadar derslere devam etmelidir.
- Ayrıca, öğrencinin müfredatında yer alan bütün dersleri almış olması gereklidir, ancak bu derslerin tamamını başarmış olma şartı aranmayacaktır.
Bu detaylar, öğrencinin muafiyet başvurusunu yapmadan önce ve karar çıkana kadar takip etmesi gereken süreçleri ortaya çıkmaktadır.
Tebliğatta yer alan bilgi, yatay geçiş başvurusu yapmadan önce öğrencinin kayıtlı olduğu programa ait genel not ortalaması en az 2.80 olmalıdır. Karar çıkana kadar da derslere devam edilmesi gereklidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
```

### Q2: Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi ve sınavda başarılı sayılmam için minimum not kaç?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/3
  - [x] staj
  - [x] tamamla
  - [ ] CC
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 7128.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi?
Hayır, stajını tamamlamam required değildir. Tek ders sınavına girebilmek için herhangi bir staj zorunluluğu bulunmamaktadır.

Tek ders sınavında başarılı sayılmak için minimum not kaçtır?
Açık bir şekilde verilen departman yanitlarındaki bilgilere göre de minimum not bilgisine ulaşılamamıştır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: yabancı_dil_eğitim_öğretimi_yönergesi.pdf
```

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] değiştirebilir
  - [ ] devam koşulu
  - [ ] yeni
  - [x] ders
- **Sure**: 6228.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli seçer ise devam zorunluluğunuz değişmez. Ancak, baştan itibaren devam zorunluluğu olan seçmeli ders yerine devam zorunluluğu olmayan bir ders seçmeniz mümkündür.

Bu konuda "Lisansüstü eğitim ve öğretim yönetmeliği"nde bir düzenleme bulunmakta; devem koşulu yerine getirilmeyen bir blok dersine, laboratuvar/klinik öncesi uygulamalara/klinik uygulamalara ve seçmeli derslere devam etmek esastır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
```

### Q4: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] transkript
  - [x] dahil
  - [x] ortalama
  - [ ] tamamlamıştır
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=factual
- **Sure**: 10151.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Sen OMU'den mezun olmanız durumunda, pedagojik formasyon dersleri transkripte dahil edilmemekle birlikte, mezuniyet ortalamasına etki edebilen ve seçimle alınan bir ders gibi gözükmektedir.

- Bu dersler 40 AKTS' den oluşur ve öğrencinin lisans programından mezuniyeti için alması gereken asgarî AKTS şartının dışında değerlendirilir.
- Pedagojik formasyon dersleri, öğrencinin seçimle alabileceği bir ders gibidir. 
- Öğrencinin lisans programının diğer bölümlerden seçmeli dersleri yerine bu dersleri alabileceği unutulmamalıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: uygulama_esaslari_lisans_pedagojik_formasyon.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
- Belge: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt
```

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['academic_programs', 'finance', 'student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] ücret
  - [x] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 7066.4 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Ogrenci Isleri:
Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretiminizi, ilgili yönetim kurulunca kabul edildiği takdirde, kayıt dondurma işlemini gerçekleştirdiğinizde ve harç ücretinizi yatırmak zorunda değildir.

Ancak, kayıt işlemlerini gerçekleştirmek ve ikamet izni için gerekli belgeleri hazırlamak üzere, Ondokuz Mayıs Üniversitesi (OMU) Öğrenci İşleri Birimine bağlı olan ÖİDB Katkı Payı ve Öğrenim Ücreti Ofisi'ne (Kod: GT158) başvurmanızı öneririm.

Aşağıdaki bilgiye göre, kayıt işlemlerini tamamlamak için gereken belgeleri hazırlamanız gerekir:
- Diplomanızın aslı ya da düzenlenmiş kaçı,
- Vize belgeniz,
- Pasaportunuz,
- Eğitim ücreti ödemesi yapmanız gerekebilir (Kayıt dondurma işlemleri sırasında ödeme yapmanıza gerek olmaz, ancak diğer işlemler için ödeme yapmanız gerekebilir).
Ayrıca, ikamet izni alma ve uzatılma işlemleri için gerekli olan belgeleri hazırlamanız gerekecektir. Bu belgeler; diploma, pasaport, ikamet izni ve öğrenim ücreti ödeme belgesi olabilir.

Ayrıca, 667 Sayılı KHK kapsamında gelen öğrenciler ile ilgili işlem yapmak, öğrenci taleplerine sözlü veya yazılı cevap vermek için gerekli belgeleri hazırlamanız gerekir.

Akademik Programlar:
Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

Buna göre, uluslararası_öğrenci.pdf belge baglaminda yapılan açıklama göre, ön kayıt yaptıran öğrenciler, uluslararası öğrenim ücretini ödemelidir. Ancak, OMÜ TÜRKÇE ücretini ödemeyen öğrencilerin ön kayıt hakkı verebilir. Bu nedenle, uluslararası öğrenim ücretini Üniversite tarafından belirlenen son kayıt tarihine kadar Üniversite'nin ilgili web sayfalarındaki duyurulara göre öğrenim ücretini ödemelisiniz.
  
Için ikamet izni için gereken belgeleri hazırlamaktan bahsetmek istiyorum: 
İlgili belgeleri sunamayan, Türkiye’de yasal kalış hakkına sahip olmayan veya yasal kalış süresi ihlali içerisinde bulunan öğrencilerin geçici kaydı yapılmış olsa dah
... (629 karakter daha)
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs', 'student_affairs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 9216.4 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
ÇAP programına başvurabilmek için öncelikle başvurulabilirlik şartlarına bakmanız gerekir. ÇAP programına başvurabilmek için öğrencinin hangi şartları karşıladığına bakmanız önemli.

Harç borcunu ödemenin yolları ise şu şekildedir:

- Ödemenizi yapabilmek için ÖİDB (Örgün İktisadi ve İdari Bilimler Fakültesi) hesabınıza giriş yapın.
- Ödeme ekranına girip ödeyeceğiniz tarihlere göre ödemenizi yapın.

Ön koşul olarak harç borcunuzun güncel durumuna bakabilir, borcunuzun varlığı veya yokluğu hakkında bilgi alabilirsiniz. 

Not: Öğretim ücreti öğrenci türüne (Türk öğrencisi, uluslararası öğrenci) ve birimine göre değişmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q7: Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra ders kaydını nasıl yapacağım, danışmanın onay süreci nasıl işliyor?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [ ] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 6606.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Ders kaydını yapma adımları ve danışman onay süreci aşağıdaki gibidir:

* Kayıt yenileme dönemi başında öğrenim ücretini yatırmak suretiyle ders kaydına geçiş yapabilirsiniz.
* Akademik takvimde belirlenen süre içinde kaydınızı yaptırmanız önemlidir.
* Kaydın tamamlanması ve danışman onayı işlemini gerçekleştirmelisiniz.
* Transkript kontrolüne dikkat ederek, doğru ders seçimleri yapmanız ve akademik takvimde belirtilen süre içerisinde ders kaydını gerçekleştirmeniz gerekir.
* Danışman onayınızı aldıktan sonra, akademik takvimde belirtilen süre içinde kaydın tamamlanmasını sağlamanız gerektiğini unutmayın.
* Kayıt dönemi boyunca öğrencilere transkript/müfredat kontrolünü yaparak ders kaydını yapmaları gerektiğini danışmanlar bildirirler.
* Danışmanlar, öğrencilerin akademik takvimde belirtilen süre içerisinde kaydın tamamlanmasını ve danışman onay işlemini gerçekleştirmelerine yardımcı olunmasını sağlarlar.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: Kural
- Akademik Programlar: Kural

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [x] burs
  - [x] kesilme
  - [ ] kurum
  - [ ] bildiri
  - [x] harç
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 9651.9 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Yatay geçiş yapmak istediğinizde, bursumun kesilip kesilmeyeceği durumu, Yükseköğretim Kurulu'nca (YÖK) belirlenen kurallara göre belirlenir. Bursunuzun kesilip kesilmeyeceği durumunu öğrenmek için YÖK ve ÖSYS yetkililerine başvurmanız gerekir.

Yatay geçiş başvurunuz kabul edildikten sonra, ÖSYS tarafından belirlenen kurallara göre bursunuzun kesilme durumu belirlenir. Bu nedenle, yeni üniversiteye geçmeniz durumunda harç ödemmeniz gerekebilir. Kayıt işleminizin tamamlanmasından sonra, yeni üniversite size belirlenen kayıt ve eğitim ücretlerini ödemeniz gerekecektir.

Örneğin, bursun kesileceğine dair bir karar alıncaya kadar, eğitim ücretleriniz ile bursunuzun kalan kısmını birleştirerek ödemelisiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: yaz_okulu_eğitim_öğretim_yönergesi.pdf
- Belge: yonerge_yaz_okulu_egitim_ogretim.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: özel_öğrenci_yönergesi.pdf
- Belge: uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [ ] azami
  - [x] ek
  - [x] süre
  - [x] katkı payı
  - [x] öde
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 5558.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Akademik Programlar:
Sayın öğrenci,

Soruunuza ilişkin ilgili kurallara göre cevap verilmektedir. Ek süre hakkınıza ilişkin olarak, belge kaynagımızdaki ilgili maddeler ışığında, aşağıdaki cevabın verilmesi uygun olacaktır.

Hem yüksek lisans hem doktora programlarında, öğrenci tez çalışmalarını tamamlayamaması durumu için ek süre talep edebilirler. Yüksek lisans programı için 2, doktora programı için en fazla 4 yarıyıl ek süre verilebilir. Ek süre de dahil, belirtilen süreler içinde çalışmalarını tamamlayamayan araştırma görevlileri için mecburi hizmet sözleşmesi uygulanır.

Aygıt ışığında, 4. sınıf öğrencisi için, ek süre talebi hakkında net bir cevap verilememektedir. Ancak, ek süre talebi için, bir kurumın gerekçeyle verdikleri karar ve enstitü yönetim kurulu onayı gereklidir. Bu nedenle, ek süre talebinden önce OMU'nın ilgili kurumlarına danışmanız gerekebilir.

Diğer bir durum ise, program süresini 1 yıl aşarak eğitim görmekte olduğunuzdur. Bu durum ise sizin akademik programınızı etkilememektedir. Dolayısıyla, katkı payı ödemek için bir durumünüz bulunmamaktadır.

Öğrenciler için katkı payı ödemesi, programın normal süresi içinde yapılmaktadır. Ancak, program süresini aşmış olduğunuz durumlarda, katkı payı ödemek zorunluluğu bulunmadığını belirtmemiz önemlidir.

Kısaca söylemek gerekirse, 4. sınıf öğrencisi olarak program süresini aşmış olduğunuz durumunuza, bu durum sizin akademik programınızı etkilememektedir. Hatta, katkı payı ödemek için bir durumunuz da bulunmamaktadır. Dolayısıyla, ek süre talebi için ilgili kurumlara danışmanız gerekebilir ve bu durum hakkında daha net bir cevap alabilirsiniz.

Finans:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Akademik Prog
... (558 karakter daha)
```

### Q10: Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [x] tekrar
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 6928.2 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına girebilir miyim?

Devamsızlıktan kalan öğrenci, o dersin bütünleme sınavına giremez. 

Detaylar: 
Devamsızlık durumunda bütünleme sınavına girilemeyeceğini, öğrenci işleri departmanının belirttiği gibi, resmi kaynaklardan açıkça anlamaktayız. 
Ayrıca, akademik programlarda bu durumun net bir şekilde belirtilmediği ancak devamsız olmadığınız bir dersde başarısız olduğunuzda bütünleme sınavına giremeyeceğiniz belirtilmiştir. 
Dersi tekrar almaktaki süreler ve koşullar, öğrencilerin devamsızlık durumunda tekrar ders alabilecekleri konularında net bir bilgiye sahip değiliz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: yonerge_yabanci_dil_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] öğrenim ücreti
  - [ ] gerek yok
  - [x] yönetim kurulu
  - [x] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 7916.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
İkinci öğretim öğrencisiyseniz ve bir dönem kayıt dondurmak istiyorsanız, harç ücreti yatırmak zorunda değilsiniz. Ancak kayıt dondurma talebi, ilgili yönetim kurulunun onayını gerektirmektedir.

Kayıt dondurulan sürenin eğitim süresinden sayılması durumuna ilişkin olarak, durumun detayları vardır:

* Kayıt dondurulan süreler, eğitim süresinden sayılmaz.
* Kayıt dondurulan dönemler öğrenim süresinden sayılmaz; ancak kayıt dondurma süresinin bitiminde öğrenci, ayrıldığı dönemin/yılın başından başlamayı koşuluyla öğrenimine kaldığı yerden devam eder.
Detaylı bilgi ve belge talepleri, Öğrenci İşleri biriminizde yapılabilmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
```

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] transkript
  - [x] Ek Madde
  - [ ] başvuru yapabilir
  - [ ] GANO
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=factual
- **Sure**: 61023.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Yanlışlıkla verilen departman yanıtını gözden kaçırdım, fakat şimdi anlıyorum. O halde, bir kullanıcıya yardımcı olmak için tüm bilgileri bir araya getireceğim.

Hazırlık sınıfındayım ve transkriptim yok, Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim? İşte bir cevap için gereken adımlar...

- Yapabilir miyim?
Evet, olabilir. Ek Madde-1 kapsamında merkezi yerleştirme puanı ile yatay geçiş başvurusu yapabilirsiniz.
- Başvuru için ne gereklidir?
Dikkat etmeniz gereken önemli nokta, Ek Madde-1 başvurusu için öğrencilerin ÖSYS/YKS/DGS türünden yerleşmiş olmaları gerekir. Bu, başvuru modülünde 1. Grubu veya 2. Grubu seçerek tercih yapacaklardır.
- Transkrip tüketmeniz şart mı?
Hayır, transkrip tüketmeniz gerekmez. Hazırlık sınıfı okuyan öğrenciler ek madde-1 kapsamında yatay geçiş başvurusu yapabilirler.
- Kayıt işlemlerinden sonra ne yapmalıyım?
Kayıt işlemlerinizden sonra ilgili akademik birime dilemma ile başvuru yapmanızı tavsiye ederiz.

Dikkat edilecek en önemli nokta, Ek Madde-1 ile yapılan yatay geçiş başvuruları, programa göre farklılık gösterecektir (Ör: Lisans programlarının hazırlık sınıfına ilk yılı ile son yılına yatay geçiş yapılamayacaktır.)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf
```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 6747.9 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kurum İçi ve Kurumlar Arası Yatay Geçiş Farkları

Kurum içi yatay geçiş ve kurumlar arası yatay geçiş arasındaki farklar şu şekildedir:

Kurum İçi Yatay Geçiş

* İçerik: Aynı üniversitedeki programlar arasında yapılan geçişleri kapsamaktadır.
* Başvuru Şartları:
 + Kayıtlı olduğu programda genel not ortalamasının 4'lük sistem kullanan üniversiteler için en az 2.80, 100'lük sistem kullanan üniversiteler için en az 72 olması gerekir.
 + OMÜ-YÖS sınavından veya diğer sınavlardan en az 50 puan almış olması gereklidir.
 + Geçmek istediği diploma programı için geçerli olan OMÜ-YÖS puan türünde alınan merkezi yerleştirme puanının, geçmek istediği diploma programına eşdeğer olması gerekir.
 + Bir diploma programına yerleştiği yıldaki yerleştirme puanı, geçiş yapmak istediği diploma programının taban puanına eşit veya yüksek olması gerekir.

Kurumlar Arası Yatay Geçiş (Yurt İçinde)

* İçerik: Farklı üniversiteler arasında veya yurt dışı programlarına yapılan geçişleri kapsamaktadır.
* Başvuru Şartları:
 + Uluslararası öğrencilerin, OMÜ-YÖS sınavından veya diğer sınavlardan en az 50 puan almış olması gereklidir.
 + Geçmek istediği diploma programı için geçerli olan OMÜ-YÖS puan türünde alınan merkezi yerleştirme puanının, geçmek istediği diploma programına eşdeğer olması gerekir.
 + Bir diploma programına yerleştiği yıldaki yerleştirme puanı, geçiş yapmak istediği diploma programının taban puanına eşit veya yüksek olması gerekir.

Kurumlar Arası Yatay Geçiş (Yurt Dışı)

* İçerik: Yurt dışı yükseköğretim kurumlarından Üniversiteye yapılan yatay geçiş başvurularını kapsamaktadır.
* Başvuru Şartları: Yurt dışı yükseköğretim kurumlarındaki aynı düzeydeki eşdeğer diploma programlarından yapılması gerekir.

Hatırlatma: Yurt dışı öğrenci kontenjanları ile başvuru şartları ve değerlendirme takvimi, Yükseköğretim Kurulu internet sayfasında ilan edilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim
... (429 karakter daha)
```

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] bağıl
  - [x] mutlak
  - [x] 10
  - [x] öğrenci sayısı
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 3790.0 ms
- **Kaynak Sayisi**: 6
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Ogrenci Isleri:
Bağıl değerlendirme sistemi ve mutlak değerlendirme arasındaki farkı açıklamak için elimdekilerle hareket edeceğiz.

Bağıl değerlendirmenin iki farklı uygulaması var:

- Bağıl Değerlendirmeye katılan öğrenci sayısı 10'dan az ise, Tablo-1'e göre ham başarı puanı mutlak değerlendirmeyle harf notuna dönüştürülür.
- Bağıl Değerlendirmeye katılan öğrenci sayısı 11-29 arasında ise, öğrencilerin ham başarı puanları ders ortalaması dikkate alınarak Tablo-2'ye göre nota dönüştürülür.

Mutlak değerlendirme ise, Tablo-1'e göre harfli not oranlarına göre ham başarı puanı hesaplanır.

Kaynaklarda net bilgi olmadığı için kesin olarak hangi öğrenci sayısında hangisi uygulandığını söylemek kabil değildir.

Akademik Programlar:
Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark:

Bağıl değerlendirme sistemi, öğrencilerin yarıyıl içi değerlendirmesi ve yarıyıl sonu sınavından aldıkları notların öngörülen ağırlıklara göre hesabıyla belirlenen ham başarı notunun 4'lük not sistemindeki karşılığını ifade eder. Bu sistem, öğrencilerin yarıyıl içi performansının öğrencinin genel başarı notuna etkisini gösterir.

Mutlak değerlendirme sistemi ise, öğrencilerin başarı durumu yalnız yarıyıl sonu ya da bütünleme sınav notundan belirlenir. Bu sistemde, öğrenci başarısı, yalnızca yarıyıl sonu sınavına bakılmakta ve öğrenci yarıyıl içi performansı göz ardı edilmektedir.

Hangisi hangi öğrenci sayısında uygulanır:

Bağıl değerlendirme sistemi Ondokuz Mayis Universitesi (OMU) lisans programlarında, yüksek lisans, doktora ve uzaktan eğitim programlarında uygulanabilir. Mutlak değerlendirme sistemi ise, genellikle lisanstırma programlarında ve yarıyıl içi çalışmalarının öğrenci başarısına büyük etkisi olmayan programlarda uygulanabilir.

Ayrıca, OMU'nın lisans programları için bk Kaynak 1'de belirtilen MADDE 25, OMU'nın lisansüstü programları için bk Kaynak 2 ile Kaynak 3'de bahsedilen MADDE 23'i referans alınarak yorumlanabilir.

---
Daha iyi yardimci olabilmem icin 
... (504 karakter daha)
```

### Q15: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/3
  - [x] diploma eki
  - [x] transkript
  - [ ] yerine geçmez
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=comparative
- **Sure**: 4532.8 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Ogrenci Isleri:
Diploma eki ile transkript arasındaki fark;
Diploma eki, diplomaya eklenecek bilgiler olan notlar, alınan krediler, ders başarıları ve mezun olunan program ile ilgili verileri içerir. Transkript ise diplomanın içerisinde yer alan ve not bilgisi ile ilgili verileri gösteren bir belgedir.

Diploma eki, transkript yerine kullanılamaz. Transkript diplomanın içinde yer alır ve diplomanın bir parçası olarak kabul edilirken, diploma ekisi ayrı bir belge olarak sunulur.

Diploma eki transkript yerine kullanılabilir mi?
Hayır, diploma eki transkript yerine kullanılamaz. Diplomaya eklenecek bilgiler olan notlar, alınan krediler, ders başarıları ve mezun olunan program ile ilgili verileri içerir, ancak transkript diplomanın içinde yer alarak diplomanın bir parçası olarak kabul edilir.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

Akademik Programlar:
Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

Diploma eki ile transkript arasındaki en büyük fark, diploma ekinin transkriptin sunduğu tüm bilgiler yerine belirli bir konuya yönelik sınırlı sayıda dersi alma sonucu elde edilen bir belge olmasıdır. Transkript tüm öğrenciye ait bilgileri içerirken, diploma eki yalnızca bir yandal programı kapsamındaki dersleri içerir.

Diploma eki transkript yerine kullanılabilir mi?

Hayır, diploma eki transkript yerine kullanılabilir değildir. Diploması olduğunda, diploma ekinin yerine geçeceği durumlarda olduğu gibi, diploma eki transkriptin yerini alması amaçlanmamıştır. Transkript tüm akademik geçmişinizi gösteren bir dokümandır, diploma eki ise belirli bir program kapsamında alınan dersleri gösteren bir belgedir.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM
... (292 karakter daha)
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 8328.3 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kayıt dondurma ile kayıt yaptırmamak arasındaki farklar, öğrencinin öğrenim hakları ve programda devam etme hakları ile ilgilidir.

Kayıt Dondurma:
- Kayıt dondurma, öğrencinin mevcut kayıtlı olduğu programa devam etmesini sağlayan bir işlem.
- Bu işlem, öğrencinin öğrenim haklarından yararlanmasını sağlar.
- Kayıt dondurma, öğrencinin bir sonraki akademik takvime göre ders kaydı yapmasını da sağlar.

Kayıt Yapmamak:
- Kayıt yapmamak, öğrencinin bir programa kabul edilmediği veya programa devam etmediği demektir.
- Kayıt yapmamak, öğrencinin öğrenim haklarından yararlanmasını sağlar.
- Ancak, bu durum öğrencinin bir programa kabul edilmemiş olduğunu belirtir.

Ayrıca, öğrencinin öğrenim süresi boyunca en fazla dört dönem/iki yıl için kaydınızı dondurabilir ve bu süreler hesabında dikkate alınmaz. Bu durum kaydınızın silinmemiş olmasını sağlar.

Dolayısıyla, kayıt dondurma ve kayıt yaptırmamak arasındaki fark öğrencinin programa devam etme hakkını kullanıp kullanmadığına bağlıdır. Kayıt dondurma, öğrencinin mevcut kayıtlı olduğu programa devam etmesini sağlar, ancak kayıt yapmama durumunda öğrenci bir programda kaydolmamış demektir.

Ondokuz Mayıs Üniversitesi'nde kaydınız dondurularak, kayıt yaptırmadan veya kaydınızın silinmiş olması durumunda öğrencilik haklarınızın etkilenmesini önleyebilirsiniz. 

Eğer kaydınızı donduracak olursanız, bir defada en fazla iki dönem/bir yıl olmak üzere, öğrenim süresi boyunca en fazla dört dönem/iki yıl kayıt dondurabilirsiniz. Buna karşın, kayıt yaptırmamak durumunda ise, öğrencesinin kaydı silinmiş olarak alınır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_prog
... (102 karakter daha)
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [ ] UBYS
  - [x] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 7885.9 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Üniversite Kayıt Süreci

İlk kez üniversite kaydını yaptıran bir öğrenci olarak süreç başından sonuna aşağıdaki adımları takip eder:

1. Ders Seçimi: Öğrenci kayıt olmak istediği dersleri seçer ve ilgili danışmanının onayı için başvurur.
2. Danışman Onayı: Danışman, öğrenci tarafından seçilen derslerin uygun olup olmadığını kontrol eder ve onaylayarak ders kaydını sağlar.
3. Kayıt Onayı: Kayıt sistemi öğrenci tarafından seçilen dersler konusunda onayını alır ve bir bilgilendirme yapılır.
4. Ders Kaydı Kontrolü: Akademik takvimde tanımlanan ekle-sil haftası sonunda, öğrenci ve danışman birlikte ders kaydının kontrolünü gerçekleştirirler.

Diğer detaylar şunlardır:

- Öğrenci belgelerini teslim etmesi gerekir.
- Uluslararası Öğrenci Kabul Komisyonu, öğrencinin sunmuş olduğu bilgi ve belgelerin tutarlılığını kontrol eder.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: kayıt_sildirme_formu_lisans_önlisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ogrenci_staj_degerlendirme_anketi.pdf
- Belge: burslu_uluslararası_öğrenci_yerleştirme_ve_kesin_kayıt_iş_akış_süreci.pdf
- Belge: uluslararası_öğrenci_evrak_teslim_formu_r1.pdf
- Belge: uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: uluslararası_öğrenci.pdf
```

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [x] itiraz
  - [ ] beş iş günü
  - [ ] dilekçe
  - [ ] bölüm başkanlığı
- **Sure**: 1617.3 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Sınav notunuzu itiraz etmek istiyorsanız, aşağıdaki adımları takip etmeniz gerekmektedir.

1. Yüzde on hesaplanmasından sonra, 15 gün içerisinde fakülte/yüksekokulunuza yazılı olarak başvurmanız gerekmektedir.

İtiraz başvurunuz, 15 gün içerisinde birim yönetim kurulunca karara bağlanacaktır. Bu karar kesindir.

3. İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmayacaktır.

Yapılan başvurular, 15 güne kadar birim yönetim kurulunca karara bağlanır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ders_yeterlilik_sınavı_uygulama_yönergesi.pdf
- Belge: yüzde_on_başarı_değerlendirme_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/6
  - [x] ders
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [x] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 7084.9 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklamak için, aşağıda belirtilen adımları takip etmek gerekir:

Mezuniyet Koşulları: 

Bir öğrenci, belirli koşulları karşılıyorsa mezuniyet için gerekli olan koşulları yerine getirmektedir:

1. Ön Kayıt ve Kesin Kayıt: Öğrenci ön kaydın ardından Senato tarafından belirlenen kesin kayıt belgelerini teslim etmelidir.
2. Ana Dal Programına Ait Kredi Tamamlama: Öğrencinin ana dal programına ait kredisi tamamlanmış olmalıdır.
3. ÇAP'tan Ayrılma: Öğrenci, ÇAP'tan ayrıldığında başarısız olduğu dersleri tekrarlamak zorunda değildir.

İlişik Kesme Koşulları:

1. Kayıt Yenileme: Kayıt yenilemeyen öğrenciler, kendi istekleriyle kaydını sildikleri için ilişiği kesilmektedir.
2. Dört Yıl Üste Katkı Payı Ödememe: Dört yıl üst üste katkı payı ve öğrenim ücreti ödemeyen öğrenciler, aynı şekilde ilişiği kesilmektedir.
3. İlişik Kesme Süreci: İlişik kesme işlemleri için UNITe'deki sistem üzerinden ilişiği kesmek isteyen öğrenci, birim amiri tarafından imzalanan “Form–2” belgesinin sunulmasından ardından Strateji Geliştirme Daire Başkanlığı'nca kesinleştirilmelidir.
4. Personelin İlişik Kesme: Personelin ilişiği kesilmeden önce, birim amiri tarafından ilgilinin zimmetinde taşınır (demirbaş) olup olmadığı kontrol edilmelidir.
 
Ögrenicilerin ilişiği UNITe sistemine bağlı kalınacak olup; detaylı bilgi icin öğrenci isleri veya akademik programlar departmanina bakılabilmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: zimmetteki_taşı
... (68 karakter daha)
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 5227.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Yanıt:
İki sorun için de takip edeceğiniz adimsalari alttaki gibi olacaktir.

Diploma kaybınızı gidermek icin:

1. Yaygın bir gazete basildigi surece kayıp ilaninda bulunun. (Kayıp ilaninda bulunma adimi sizin kisisel bilgi yukumluluklari dahilinde olacak).
2. Kayıp ilaninda yer alan bilgileri ve diploma ücretini odemis olacaginiz banka dekontunu ilgili birimimize iletin. (İlgili birimimiz: Ondokuz Mayis Universitesi, öğrenci isleri birimine).
3. İlgili birim sizden diploma aldiginiz birimine baska bir adim atmaz. Sizler kayit oldugunuz birim icin yeni bir diploma alacaksiniz.

e-Devlette mezuniyet bilgilerinizin görünmemesini gidermek icin:

1. Kayit oldugunuz birime gorusunuz. (İlgili birimimiz: Ondokuz Mayis Universitesi, öğrenci isleri birimine).
2. Bu birimdeki personelin size diplomada yer alan bilgiler icin gerekenlere ulaşabilmesi için gereken belge ve bilgileri kendiniz temin ediniz. (Siz kendi belge ve bilgi kaynaklari tarafindan isteyeceksiniz, ilgili birim sizin kisisel bilgi yukumluluklarinizi yerine getirecektir).
3. İlgili birim sizden diplomaninizi kontrol etmeginizi talep edebilir, bu adim da sizin bilgisi ve muvafakatiniz dahilinde olacaktır.
4. Gerekli belge ve bilgiler temin edildiginde, ilgili birim sizlere yeni bilgileri ve güncellenmis mezuniyet bilgilerini ileteceklerdir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: ön_lisans_ve_lisans.pdf
```

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs', 'academic_programs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [ ] %40
  - [ ] %60
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 3939.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Soru: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

Belge Baglaminda Gorunen Bilgi: 
Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi ile yüz yüze derslerin kıstasları farklılık göstermez. (KAYNAK-3: uzaktan_karma_eğitim_yönergesi.pdf) 

MADDE 9 – (1) Uzaktan veya örgün verilen derslere ait devam ve başarı durumu Ondokuz Mayıs Üniversitesi Ön Lisans ve Lisans Eğitim- Öğretim Yönetmeliği ile Ondokuz Mayıs Üniversitesi Lisansüstü Eğitim ve Öğretim Yönetmeliği hükümlerince belirlenir.

Yanit: Bu konuda elimdeki kaynaklarda net bilgi bulunadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: samsun_sağlık_yüksekokulu_eğitim_öğretim_ve_sınav_yönetmeliği.txt
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4128.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınava kopya çekilmesinin cezası ve disiplin sürecine ilişkin olarak yapılan kurallara göre;

- Kopya çekilmesi ve kopya vermek suçudur.
- Gözetmenler öğrencilerin yerlerini değiştirebilir veya sınav kurallarına aykırı davranışlarda bulunanları salondan çıkartabilir.
- Öğrenciler sınav görevlilerinin her türlü uyarısına uymak zorundadır.
- Sınav görevlileri, kopya çekilmesi veya kopya vermenin tespitine karar verme yetkisine sahiptir.
- Uyarıda bulunmaksızın, kopya çekme veya kopya vermek suçundan mahpusen işlem yapabilirler.
- Disiplin süreci, 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesine göre yürütülmektedir.

Bu konuya ilişkin olarak elimdeki kaynaklarda net bir bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [x] form
  - [ ] birim
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 3226.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ayrılmak istediğiniz için özgeçmişinizin ve notunuzun doğru bilgilerini kontrol ediniz. Aksi halde, ayrılmanın ardından oluşabilecek olası sorunlardan kendinizi korumak için önemlidir.

1. Öğrenci Kimlik Belgenizi Kontrol Edin: Ondokuz Mayıs Üniversitesi Mühendislik Fakültesi Öğrenci Kimlik Belgenizi yanında bulundurmakta ve öğrenci işlemlerinizi yapabilmektedir.
2. Cep Telefonunuzu Sırada Kalacak: Sınav zamanında cep telefonlarınız kapalı olmalıdır. Telefonun sessiz modu bile kullanılması yasaktır. 
3. Değerlendirme ve Degerlendirme Süreci: Danışmanınız tarafından, kayıtlı olduğunuz derslerde değişiklik yapma hakkı vardır. Danışmanın bu hakkını kullandığı zaman, kayıtta herhangi bir değişiklik olacaktır.
4. Ders Muafiyet ve Intibak İşi: İntibak işlemi, daha önce Ondokuz Mayıs Üniversitesi veya başka bir üniversite öğrencisiyseniz, başardığınız derslere göre devam ettiğiniz yarıyılları belirleyecektir. Danışmanınız, intibak komisyonu tarafından incelenerek kararlaşılmaktadır.
5. Tüm İşlemleri Tamamlamayı Unutmayın: Ayrılma işlemini başlatırken, tüm öğrenci işlemlerini eksiksiz tamAMLAMANIZ ve Ondokuz Mayıs Üniversitesi öğrenci işleri bölümüne başvurmanızı unutmayın.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: zorunlu_gönüllü_staj_başvuru_formu.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2766.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Gerekli Belgeler:
- Sağlık kuruluşlarından alınacak sağlık raporu (sağlık mazereti için)
- Yerel yetkililerden alınacak belge (tabii afetler veya maddi imkânsızlıklar mazereti için)

Ayarlanacak Süreç:
- İlgili birimin yönetim kurulu kararı ile iki dönem/bir yıl kayıt dondurma kararı almayı planlayın.

Süresi Bitimindeki Durum:
- Kayıt donduran dönem/dönemler süre hesabında dikkate alınmayacaktır.
- Kayıt dondurma süresinin bitiminde öğrenci, ayrıldığı dönemin/yılın başından başlamak koşuluyla, öğrenimine kaldığı yerden devam edecektir.

Ders Seçimi:
- 1 Yarıyıl sonundan itibaren, başarılarınızı ve öğrenim durumunuza göre, bir üst sınıftaki derslerden kredi sınırları içinde ders alabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/3
  - [x] danışman
  - [ ] bölüm
  - [ ] oidb@omu.edu.tr
- **Sure**: 4005.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Soruya gelen cevap:

Ders notlarını sisteme girmemiş olmanız nedeniyle ortaya çıkabilecek sorunları çözmek için, ÖİDB'den (Öğrenci İşleri Bilgi Edepli Daire) destek istemek en doğrusu olacaktır. Onlarla iletişime geçerek durumunuza bağlı olarak gerekli adımları atabilirsiniz.

Belgenizde yer alan kaynaklara göre, öğrencinizin kayıt ve Ders Ek/Sil gibi işlemlerinin yapılması ÖİDB'den destek alındığında mümkün olacağı anlaşılmaktadır.

Daha önce aldığınız dersler için de Dekanlığa muafiyet başvurunuzu yaptımsa, muafiyet başvurunuz sonuçlandıktan sonra danışmanınız ile birlikte alacağınız derslere kaydınız yapılır.

Bununla birlikte, muafiyet kararınız alınana kadar da devan edebileceğinizi, ancak bu süre zarfında akademik takvimde belirtilen işlemler yapılandırıldığınızı anlamaktayız.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
