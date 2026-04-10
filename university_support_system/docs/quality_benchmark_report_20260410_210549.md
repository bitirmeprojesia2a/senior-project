# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 21:05:49
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 92.0% |
| Uretim Modu Dogrulugu | 92.0% |
| Anahtar Bilgi Kapsami | 66.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 5541.6 ms |
| Medyan Sure | 5038.1 ms |
| Intent Analizi Aktif | 23/25 |
| Force LLM Sentez | 21/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 9186.1 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 3/3 | 10725.4 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | OK | 2/4 | 5004.9 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 3/4 | 5156.6 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 4685.2 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 6467.7 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 4648.7 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 4732.9 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | OK | 4/5 | 4077.5 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 12590.8 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 3/4 | 6194.4 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | YANLIS (rag) | 1/4 | 4336.6 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 6280.4 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 3/4 | 4110.8 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 2/3 | 4317.1 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 3039.1 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 5038.1 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 3/4 | 1940.9 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 5/6 | 6123.7 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 5278.6 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 1/5 | 6392.2 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 5044.9 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 5053.5 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 4907.1 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 3/3 | 3207.7 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 9186.1 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu en geç  öğretim yılının 3. haftasının sonuna kadar yapmak zorundadır. Öğrenci, karar çıkana kadar kararın verilmesini takip eden gün derslere devam etmeniz zorunludur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```

### Q2: Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi ve sınavda başarılı sayılmam için minimum not kaç?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] staj
  - [x] tamamla
  - [x] CC
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 10725.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Tek Ders Sınavına Girebilmek için Stajını Tamamlamam Gerekir mi ve Sınavda Başarıya Sayılma için Minimum Not Kaç?

Ogrenciler, stajını tamamlamamış olmak şartıyla tek ders sınavına girebilirler. Bunun için "bütünleme sınav notlarının ilanını takip eden beş iş günü içinde dilekçe ile başvurma" şarta tabi olan öğrenciler, bütünleme sınavına girme şartlarını yerine getirmiş olmak şartıyla tek ders mezuniyet sınavına girebilirler.

Lisans programları için, tek ders sınavında minimum not CC'dir. Bu not 60-64 aralığında olan nottır.

Doktora programı için ise tek ders sınavında minimum not bulunmamaktadır. Yarıyıl/yıl sonu veya Bütünleme sınav notunun en az 60 olması yeterli değildir. Doktora yeterlik sınavında minimum 75 puan alınamazsa başarısız sayılır.

Ancak öğrenciler, stajını tamamlamaya devam ederek tek ders sınavına girebilirler.

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
- **Key Facts**: 2/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [ ] yeni
  - [x] ders
- **Sure**: 5004.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Sorusuna yanıt olarak:

Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli seçersek, devam zorunluluğunuzun değişmesi durumunu ele aldıktan sonra, kaynaklarda yer alan bilgiler ışığında, şu şekilde yanıt vermek mümkün:

Devam zorunluluğunuzun değişmesi, başarısız olduğunuz ders yerine başka bir ders seçmenizde direkt olarak etkilidir. Yönetmelikte belirtilen kurala göre, başarısız olduğu dersin yerine başka bir ders seçilebiliyor ve öğrencinin devam zorunluluğu devam etmekte.

Kaynak 2'de yer alan madde 20, bloğun blok sonu veya klinik uygulama sonu sınavına girebilmek için teorik derslerin en az %70'ine, laboratuvar uygulamalar/klinik öncesi uygulamaları ve klinik uygulamaların her birinin en az % 80'ine devamlarına ilişkin olarak hükme bağlanmaktadır. Öğrencilere ait devamsızlıkların hesaplanmasında her bir bloğun toplam saati esas alınacağı ifade edilmektedir.

Devam koşulunun yerine getirilmemesi durumunun, başarısız olan dersi yerine başka bir ders seçmenize direkt olarak etkisinin var olması, devam mecburiyetinizin değişmesine yol açacaktır.

Ayrıca, yönetmelikte belirtildiği üzere, başarısız olan öğrenci, başarısız olduğu yazılı ve sözlü ve/veya uygulamalı sınavdan bir sonraki yarıyılda tekrar sınava alınır. Bu sınavda da başarısız olan öğrencinin sanatta yeterlik programı ile ilişiği kesilir.

Bu noktada, devam zorunluluğunuzun değişmesi, başarısız olduğunuz ders yerine başka bir ders seçmenizde direkt olarak etkilidir. Ancak, devam koşulunun yerine getirilmemesi ve devam mecburiyetinizin değişmesi için, öğrenci tarafından yönetim kurulu kararına istinaden dersin devamından muafiyet dilekçesi ile başvurulması ve bu talebin kabul edilmesi gerekecektir.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_lisansustu
... (197 karakter daha)
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 5156.6 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Pedagojik formasyon dersleri, transkripte dahil edilmez. Bu dersler, öğrencinin öğrenim planında veya kaydı dondurulan öğrencilerin durumunu gösteren belgelerde yer alabilir. Mezuniyet ortalamasına etkisi de yoktur. Diplomaya da pedagojik formasyon ile ilgili bir ibare yer verilmeyecektir.

Not: Diploma eki (Diploma Supplement) bulunabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: lisans_pedagojik_formasyon_derslerine_ilişkin.pdf
- Belge: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
- Belge: uygulama_esaslari_lisans_pedagojik_formasyon.pdf
```

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'finance', 'student_affairs'] (beklenen: ['academic_programs', 'finance', 'student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] ücret
  - [x] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4685.2 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Ogrenci Isleri:
Özelliği:

Soru: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

Yanit:
Uluslararası öğrenci olarak kayıt yaptırmak istediğinizde Ondokuz Mayıs Üniversitesi (OMU) için her hangi Ziraat Bankası şubesinden öğrenci numaranızla harç ücretini yatırmalısınız. 

Uluslararası öğrenci olarak ikamet izni için hazırlamanız gereken belgeler elimdeki kaynaklarda net bilgi bulundurmuyor. 
Yurt disi öğrencilerin ikamet izni icin gereken bilgileri https://omufb.omu.edu.tr adresinden veya Öğrenci İşleri birimiyle iletişime geçerek öğrenebilirsiniz.

Akademik Programlar:
Sen Ondokuz Mayıs Üniversitesi (OMU) Uluslararası Öğrenci Asistanısıs olarak, aşağıdaki yanıtı verebilirim:

Sorunun iki temel parçasını ele alabiliriz:

1. Öğrenim ücretini nereye yatırmam gerekiyor?
2. İkamet izni için hangi belgeleri hazırlamalıyım?

Hesaplamalarım ve yanıtlarım, kaynaklarda bulunan bilgiler ve kurallara bağlı olacaktır.

1. Öğrenim ücretini nereye yatırmam gerekiyor?

Sorunu ele aldığım kaynaklardan, öğrenim ücretini yatıracak yer açıkça belirtilmemiştir. Ancak, "Uluslararası öğrenciler yükümlülükleri" başlıklı bölümde, uluslararası öğrencilerin öğrenim ücretlerini Üniversite'ye ödemesi gerektiği yazar. Bu nedenle, öğrenim ücreti, ön kayıt yaptıran öğrenciler tarafından Üniversite'ye ödenecektir.

2. İkamet izni için hangi belgeleri hazırlamalıyım?

Belgeler konusunu ele aldığımda, kaynaklardan öğreniyoruz ki, öğrencilerin Üniversite'ye yaptırdıkları ön kayıtlarını kesin kayda dönüştürme aşamasında Türkiye'de yasal kalış süresi içerisinde olduklarını pasaport, vize veya benzeri belgeler ile ibraz etmeleri gerekir. Ayrıca, öğrencilerin, kayıtlandıkları yıl için YÖK tarafından belirlenen son kayıt tarihine kadar Şahsen Öğrenci İşleri Daire Başkanlığına başvuracakları ve kayıt belgelerini teslim ettikleri de kaynaklarda yazar.

Sonuç

- Öğrenim ücretimi Öndokuz Mayıs Üniversitesi (OMU
... (1145 karakter daha)
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 6467.7 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
Soru: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

Cevap:
ÇAP programa başvurabilmek için ön koşul, başvuru şartlarının karşılanmasıdır. Bu şartlar aşağıdaki gibidir:
- Ön lisans ve lisans diploma programlarına yatay geçiş yapacak öğrencilerin, bu programlara başvuru yapacakları dönemden önceki iki yarıyılı tamamlamış ve en az 2.00 genel not ortalaması almış olmaları gerekir.
- İlk dört dönemlik lisans programını başarıyla tamamlamış ve en az 2.00 genel not ortalamasını sağlayan öğrenciler, sorumluluk şartı ile ön lisans diploması alabilir.
- Harç borcunuz varsa, bunun ödemeye devam etmelisiniz. ÇAP programa başvurmak harç borcunuzun ödeme durumu için bir değişiklik yapmaz.

Detaylar için:
- Yatay geçiş şartları için [Ogrenci Isleri] departmanının açıklamalarına bakabilirsiniz.
- Harç borcunuzun ödemeye devam etmeniz gerektiği ve ÇAP programında bir değişiklik yapmayacağı hk. [Ogrenci Isleri] departmanının açıklamasından anlaşılmaktadır.
- Harç borcunuzu ödeyebilmeniz için, ÖİDB'nin internet sayfasından bilgi alınız.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yonerge_cift_anadal_yandal.pdf
```

### Q7: Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra ders kaydını nasıl yapacağım, danışmanın onay süreci nasıl işliyor?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4648.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Ders Kaydı ve Danışman Onayı

Ders kaydı ve danışman onay süreçleri, öğrencinin kayıt yenileme döneminde harç ücretini yatırdıktan sonra devam etmektedir. İşte, bu süreçleri adım adım açıklayan bir rehber:

Ders Kaydı

*   Akademik takvimde belirtilen süre içinde, öğrenci bilgi yönetim sisteminden öğrencilere toplu ya da bireysel mesaj gönderilerek ders kaydı yapılabilir.
*   Kayıt yenileme döneminde harç ücretini yatırmış olan öğrenciler, transkript/müfredat kontrolünü yaparak akademik takvimde tanımlanan süre içerisinde ders kaydını yapması gerektiği bilgileri paylaşılmalıdır.
*   Derslere başladığında sınıf yoklama listesinde adları yoksa danışmanlarına uğramaları gerektiği bilgisi paylaşılmalıdır.

Danışman İle İlgili

*   Danışmanına ulaşılamaması durumunda, bölüme ulaşılması imkansız olan hallerde Dekan/Müdürüne durum bildirilmelidir.
*   Danışman onayını  akademik takvimde belirtilen süre içinde yaptırmak gereklidir; aksi takdirde kayıt yenileme süreci iptal edilir.

Öğretim Ücreti

Öğretim ücreti öğrenci türüne ve birime göre değişkenlik gösterir. İşte, bu bilgiye ulaşmak için gereken adımlar:

*   Öğrenci türünüz:  Türk Öğrenci  mi, Uluslar arası Öğrenci mi?
*   Fakülte veya bölüm bilginizi paylaşmak isteyorsanız, bu bilgiyi de ekleyebilirsiniz.

Teklif:

- Tür:
 *   Türk Öğrencisiniz  Fakülte: ...  Bölüm: ...
 
  ... ya da ... Uluslararasi Öğrencisiniz

 
*   Öğretim Ücreti: ... (bu bilgi öğrenci türüne ve birime göre değişkenlik gösterecektir)

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
- **Key Facts**: 4/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [ ] bildiri
  - [x] harç
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4732.9 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Yatay geçişle ilgili sorunuzun cevabı şöyledir:

Bursum kesilmez. Ancak, yeni üniversitede harç ödememeniz için Öğrenci İşleri Daire Başkanlığına başvurmanız gerekir. Yürütmeniz gereken ilk adım:

Öğrenci İşleri Daire Başkanlığına başvurular:
Başvuru tarihlerini https://oidb.omu.edu.tr/tr/ogrenci/yatay-gecis adresinden öğrenebilirsiniz.

Başvuru türleri:
Üniversite içi yatay geçiş, kurumlar arası yatay geçiş ve Ek Madde-1 yatay geçiş türlerinde bursum kesilmeyecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: yonerge_uzaktan_egitim_onlisans_lisans.pdf
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4077.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Akademik Programlar:
Soru 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

Açıkça cevabi: Evet ve Hayır.

Yanit açiklamasi:
- Ek süre hakkım var, ancak bunun için ilgili bölüm yönetim kurulunun onayi neededdır.
- Bu ek zaman içinde katkı payı ödeyeceğim, ancak bu konuda ilgili Cumhurbaşkanlığı kararına göre katkı payımın hesaplanmasi ile ilgili bilgilere ulaşamadim. Öylelikle ek zaman süresinde katkı payı da dâhil olarak normal programa göre öğrenim süresi içinde sayacagim.

Aciklamai:
- Belgenin 7. maddesindeki "Devam zorunluluğunu yerine getirmesi koşuluyla" ifadesi nedeniyle 4. sınıfa devam edebilme imkanım mevcuttur.
- Belgenin 1. bölümünde 6. madeninden öğrenme süresinin normal olarak 6 yıl oldugu ve bu süreler içinde derslerin alinmasi gerektigi ortaya konustu, bu sürelere eklemeden öğrenci katkı payı ödenemez, bunun için ise öğrenci ek zaman süresini alabilme izni needed.
- 4. bölümde 15. maddede Yandal Programi (YDP) için iki yarıyil ek süre verecekleri ve bu süre de dâhil olarak öğrencilik işlemlerinin Yandal bağlı olduğu bölüm tarafından yürütülecegi belirtilmştir. Belirtilenden yola çıkacak olursak ben yandal programıma kayıtlı olmadigim için bu kurallara uymak zorunda değiliz.
- 5. bölümde yer alan 11. madde de Ulusal ve Uluslararası öğrenci değişim programlarına (Erasmus, Mevlana, Farabi vb.) katılması ve eğitimi, kendi programına eşdeğer sayılması durumunda geçen süre, eğitim süresinden sayılır. Bu maddeye göre ise ben ulusal ve uluslararası öğrenci değişim programlarına katilmadigim için bu kurallarimiza uygulanmaz.
- 6. bölümde YDP yapan öğrenciler, lisans öğrenimi gördükleri ana daldan mezun oluncaya kadar sadece bu ana dala ait, mezun olduktan sonra ise sadece YDP’ye ait öğrenci katkı payını öderler. Bu öğrenciler lisansüstü bir programa kayıt yaptırırsalar bu programın katkı payını da ayrıca öderler. Ben yandal programi yaptığım için, ben lisans öğrenimi gortuk oldugum ana daldan mez
... (1476 karakter daha)
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 12590.8 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Devamsızlıktan kaldığının bir dersin bütünleme sınavına giremezsiniz. Devamsızlıktan kaldığınız dersi tekrar alabilirsiniz, ancak devamsızlık şartını yerine getirmeniz gerekir.

Devamsızlıktan kalkan bir öğrenci, en erken dersi tekrar alabilecek tarih, öğrencinin devamsızlık şartını yerine getireceği tarihe bağlıdır.

Devamsızlık Şartını Nereden Öğrenirim?

Oluşan devamsızlık durumu, öğrenci isminin bağlı olduğu öğrenci işleri birimi tarafından tespit edilir ve öğrenciye bildirilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
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
- **Departman**: ['student_affairs', 'academic_programs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] öğrenim ücreti
  - [x] gerek yok
  - [ ] yönetim kurulu
  - [x] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 6194.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kayıt Dondurma Sorununda Detaylı Bilgi

İkinci öğretim öğrencisi olarak kayıtlarınıza devam edemeyecek durumda bulunuyorsanız, bu konudaki detaylı bilgileri aşağıdaki maddelere dikkat ederek inceleyiniz.

Kayıt Donurumda Harç Ücreti ve Kayıt Dondurma Sorumluluğu
İkincil öğretim öğrencisi olarak kayıtlarınızı dondurmaya karar vermeniz halinde, öncelikle kayıt donduran öğrencilerin harç ücretini yatırmak zorunda olup olmadığına bakmalısınız. Kayıt donduran öğrenciler için, öğrencinin geldiği yükseköğretim kurumunda öğrenim gördüğü dönemlere ait bütün derslerinin gösteren belgesine ve öğrencinin kayıt dondurduğunu gösteren belgesine göre, öğrenim ücretini yatırmanıza gerek yoktur. Ayrıca harç ücretini yatırmak zorunda değilsiniz.

Kayıt Dondurma Süresinin Eğitim Süresinden Sayımı
Kayıt donduruda öğrencinin eğitim sürecinden sayılır mı? Evet, kayıt dondurduğunuz süre eğitim süresinden sayılır. Kayıtları yaptırılmayan öğrencilerin de kaybedilen yarıyıl öğretime devam etme hakkı kaybetmelerini ve bu sürenin öğrenim sürelerinden sayılmasını gerektirir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM
- Finans: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
```

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/4
  - [ ] transkript
  - [x] Ek Madde
  - [ ] başvuru yapabilir
  - [ ] GANO
- **Intent Analizi**: complexity=complex, force_llm=False, is_personal=False, query_type=procedural
- **Sure**: 4336.6 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilmek için bazı şartlar uygulanır. Bunlardan biri de ilk yılında yapılan yatay geçişler ve son tahunun yatay geçişleri yasaklanmasıdır. 

Ayrıca öğrencinin kayıtlı olduğu programa ait genel not ortalaması, 4.00 üzerinden 2,50 olması gerekir (Öğrenci İşleri - Akademik Mevzuat).

Kurum içi yatay geçiş için, studentsın, OMÜ-YÖS Sınavından herhangi bir puan türünden veya üniversitenin kabul ettiği diğer sınavlardan en az 50 puan almış olması gerekir. Ayrıca, öğrencinin geçme istediği diploma programı için geçerli olan OMÜ-YÖS puan türü ile aldığı merkezi yerleştirme puanının, geçmek istediği diploma programına eşdeğer olması ve öğrencinin bir diploma programına yerleştiği yıldaki yerleştirme puanının, geçiş yapmak istediği diploma programının taban puanına eşit veya yüksek olması gerekir (Akademik Programlar).

Bu nedenle, öğrenci için en önemli adım, OMÜ-YÖS Sınavından en az 50 puan almak ve diploma programı için geçerli olan OMÜ-YÖS puan türü ile ilgili işlemlerin tamamlanmasıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Akademik Programlar: RAG

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
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
- **Sure**: 6280.4 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir, başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

Kurum içi yatay geçiş, aynı üniversiteden başka programlara geçiş için yapılır, enquanto kurumlar arası yatay geçiş, aynı üniversiteden farklı üniversitelere geçiş için yapılır. Aşağıdaki farklılıklar göz önünde bulundurmanız gerekir:

Başvuru Türü: Kurum içi yatay geçiş, aynı üniversiteden başka programlara geçiş için yapılır. Kurumlar arası yatay geçiş ise, aynı üniversiteden farklı üniversitelere geçiş için yapılır.

Başvuru Kriterleri:
- Kurum İçi Yatay Geçiş: Yıl bazında ilan edilen kontenjan sayısınca başvurmayan asıl adaylar yerine daha önce belirlenen sırayla yedeklere kayıt hakkı tanınır.
- Kurumlar arası Yatay Geçiş: Yurt dışı yatay geçişimlerde, yurt dışı yükseköğretim kurumları kontenjanlarının belirlenmesi ise, Üniversitemiz senatosu tarafından belirlenen başvuru şartları ve kurumlar arası yatay geçiş kontenjanları Yükseköğretim Kurulu’na en geç Haziran ayının otuzuncu günü bildirilir.

Başvuru Süresi:
- Kurum İçi Yatay Geçiş: Takvimde belirlenen süre içindeki başvurmayan asıl adaylar yerine daha önce belirlenen sırayla yedeklere kayıt hakkı tanınır.
- Kurumlar arası Yatay Geçiş: Birim yönetim kurulları kontenjanın yarısından fazla başvuru olmadığını belirttiler.

Başvuru Yöntemi: Başvurular, Yönergede yer alan hükümler çerçevesinde yapılır.

Notlar: 
- Üzerinde Bilgi: OMÜ-YÖS Sınavından veya Üniversitemizin kabul ettiği diğer sınavlardan en az 50 puan alınması zorunludur.
- Diğer Not: Yurtiçi veya yurtdışındaki yükseköğretim kurumlarından Üniversitemize yapılan yatay geçiş başvurularda öğrencinin genel not ortalaması 60 veya 4 üzerinden en az 2,00 olmalıdır.

Bunlar arasındaki farklılıkları göz önünde bulundurarak başvurularınızı yapabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yaz
... (405 karakter daha)
```

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] bağıl
  - [x] mutlak
  - [ ] 10
  - [x] öğrenci sayısı
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4110.8 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Yanit:
Bağıl değerleme sistemi ile mutlak değerlendirme arasındaki fark nedir?

Bağıl değerlendirme sistemi ve mutlak değerlendirme arasında temel fark, başarı notunun hesaplanmasında kullanılan oranlar ile başarı notunun ifade ettiği anlamdır. Bağlı değerleme sisteminde, yarıyıl içi değerlendirme ve yarıyıl sonu sınav notlarının birlikte değerlendirilmesi ile başarı notu hesaplanır. Bu sistemin ayrıntıları ilgili kaynaktan alıntılarla aşağıda verilmektedir:

- "Yarıyıl içi değerlendirmenin %40’ı ve yarıyıl sonu sınav notunun da %60’ı toplanmak suretiyle öğrencinin başarı notu hesaplanır." (Kaynak: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf, MADDE 23/2)

- "Uzaktan eğitim öğrencilerinin başarı notu, yarıyıl içi sınavının %15’i ile yılsonu/bütünleme sınavında alınan notun %85’inin toplamıdır." (Kaynak: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf, MADDE 23/3)

- "Yıl içi değerlendirmenin %40’ı ve yarıyıl sonu sınav notunun da %60’ı toplanmak suretiyle öğrencinin başarı notu hesaplanır." (Kaynak: lisansüstü_eğitim_ve.pdf, MADDE 23/2)

- "Uzaktan eğitim öğrencilerinin başarı notu, yarıyıl içi değerlendirmenin %15’i ile yılsonu/bütünleme sınavında alınan notun %85’inin toplamıdır." (Kaynak: lisansüstü_eğitim_ve.pdf, MADDE 23/3)

Bu sistemle, öğrencilerin yarıyıl içi çalışmalarından ve yarıyıl sonu sınavından aldıkları notların belirli oranlarda birlikte değerlendirılması ile başarı notu hesaplanır.

Mutlak değerlendirme sisteminde ise, başarı notu daha basit bir şekilde hesaplanır. Sadece yarıyıl sonu sınav notuna veya diğer değerlendirmelere bakılmaktadır. Bu sistemin ayrıntıları ilgili kaynaktan alıntılarla aşağıda verilmektedir:

- "Mutlak Değerlendirme Başarı Notu Harf Karşılığı Sistemindeki Not Aralıkları" (Kaynak: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf, MADDE 23/4 ve lisansüstü_eğitim_ve.pdf, MADDE 23/4)

- "Hazırlık sınıfında başarılı sayılma notu 60’dır." (Kaynak: yabancı_dil_eğitim_öğretimi_yönergesi.pdf, MADDE 22/3)

Bu sistemle, öğrencilerin başarı no
... (1062 karakter daha)
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4317.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Ogrenci Isleri:
Soru:
Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

Kurallara göre cevap veriyorum:

Diploma eki ile transkript arasındaki fark, diploma eki ile tanınma ve akademik geçerliliğin sağlanmasıdır. Diploma eki, uluslararası saydamlığı pekiştirmeyi hedefleyen ve elde edilmiş yeti ve becerilerin ifade edildiği diploma, derece, sertifika gibi belgelerin, akademik ve meslekî tanınmasını sağlamaya yönelik, bir yükseköğretim diplomasına ek olarak verilen belgedir.

Transkript ise, öğrenim geçmişi ve alınan derslerin bilgileri içerir. Diploma eki, transkript yerine kullanılması halinde geçersizdir. (Kaynak 1: sık_sorulan_sorular.txt)

Diploma eki, transkript yerini alamaz, ancak yurtdışında daha okunabilir ve mukayese edilebilir bir diploma, akademik güzergâhının ve yurtiçinde ve yurtdışında edindiği yeti ve becerilerin tam bir tarifi, başarı ve yetilerinin nesnel ve âdil değerlendirmesi, geleceğe yönelik olarak yurtdışında iş ve eğitim imkânlarına daha rahat ulaşma olanağı, iş bulma olanaklarını artırma kazanımlarını elde edebilir. (Kaynak 2: sık_sorulan_sorular.txt)

Diploma eki nin verilme nedenleri, kişinin takip edip başarıyla tamamladığı öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek içindir. (Kaynak 3: sık_sorulan_sorular.txt)

Diploma eki yerine transkript kullanılması halinde, diploma eki nin kazanım ve özelliklerinin elde edilememesi anlamına gelir.

Akademik Programlar:
Diploma eki ile transkript arasındaki fark nedir?

Diploma eki ile transkript arasındaki temel fark, diploma eki'nin bir yüksek öğrenim programına kayıtlı olduğu süre boyunca alınan sınırsız sayılarda dersi almak ve bu dersleri herhangi bir geçiş yaptırmadan diploma yerine geçmeyen bir belgeye (yandal sertifikası) alma hakkı vermesi, bir yanda transkriptin, diploma programına kayıtlı olduğu süre boyunca alınan dersleri detaylı bir şekilde listelererek, programı tamamladıktan sonra diploma alımı için gereken koşulları
... (1118 karakter daha)
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=comparative
- **Sure**: 3039.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var?

Kayıt dondurma ve kayıt yaptırmamak iki farklı süreçtir. Kayıt dondurma, kayıt yaptırmayanın aksine öğrenciye haklı ve geçerli bir mazeret durumunda öğrenimine ara verme imkanı sunar. Kayıt dondurma, öğrenim süreinden dikkate alınmayan bir sürece denk gelirken, kayıt yaptırmayan öğrenci bu süre içinde öğrenimine devam etme hakkını kaybeder.

Kayıt donduran öğrenci, öğrenimine devam edemez ve kayıt dondurduğu döneme/yıla ait sınavlara giremez. Kayıt dondurulan dönem/dönemler, süre hesabında dikkate alınmaz.

Kayıt yaptırmayan öğrenci ise, o dönemde öğrenimlerine devam etme hakkını kaybeder ve kaybedilen dönem, öğrenim süreinden sayılır.

Her iki durumda da öğrencilik haklarını etkileyen önemli bir nokta, kayıt yaptırmayan öğrencinin kaybedilen dönemi öğrenim süresinden sayacak olmasıdır. Bu şekilde, öğrencinin öğrenim süresi uzayacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [ ] UBYS
  - [x] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 5038.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

Tabii ki, süreci açıklamak istiyorum.

1. Kayıt Onayı

İlk olarak, kayıt onayı almanız gerekir. Bu, öğrenci işleri daire başkanlığınca gönderilen kaydı onaylama yönteminden geçecektir. Onaylama yönteminden geçtikten sonra, ders kaydı işlemlerine geçilebilir.

2. Ders Seçimi

İkinci olarak, öğrenci işleri daire başkanlığından aldığınız ders seçmeli formu doldurmalısınız. Bu formda, sizce hangi dersler alınmalı, bunları nasıl bir düzenle göreceksiniz bunlardan bahsedecek ve dersleri seçeceksiniz. Sonra bu formu danışmanınıza veya Öğrenci İşleri Daire Başkanlığına sunacaksınız.

3. Danışman Onayı

Ders seçiminizi danışmanınıza sunup görüşünüzü almak, öğrenci işleri daire başkanlığının takdirine bağlıdır. Eğer öğrence işlemleri onaylandırsa o zaman danışman onayını da görecek ve öğrenci işleri daire başkanlığının onayını da görecek bir işlemdir.

4. Kayıt İşlemleri

Daha sonra, öğrenci işleri daire başkanlığınca kayıt işlemleri başlatılacaktır. İşte bu noktada, öğrenci işlemleri onaylandıktan sonra, öğrenci işleri daire başkanlığınca öğrenci kaydı başlatılır.

5. Ders Kayıt Onayı

Sonuç olarak, öğrenci işleri daire başkanlığınca öğrenci kaydı onaylandıktan sonra, ders kayıtları onaylanır ve öğrenci derslerine devam olabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: kayıt_sildirme_formu_lisans_önlisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
```

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] itiraz
  - [x] beş iş günü
  - [ ] dilekçe
  - [x] bölüm başkanlığı
- **Sure**: 1940.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Sınav notuma itiraz etmek istiyorsanız, aşağıdaki adımları takip etmelisiniz:

1. İtiraz süresi: İtirazınızı yüzdeli başarı hesaplamalarını ilan edildikten sonra 15 gün içinde fakülte/yüksekokuluna yazılı olarak başvurmanız gerekir.

2. İtiraz süresi bitmeden yapılan başvurular: Bitmeden yapılan başvurular 15 gün içerisinde birim yönetim kurulunca karara bağlanır. Yönetim Kurulunca verilen karar kesindir.

3. İtiraz Süresi Bittikten After Bildirilen Not ve Not Düzeltmeleri: İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz.

4. Yeniden İnceleme: Sınavın bitiminden sonra, öğrenciler beş iş günü içerisinde ilgili bölüme yazılı olarak başvurmak kaydıyla, sınav kâğıtlarının yeniden incelenmesi talebinde bulunabilir. Yeniden inceleme, ilgili öğretim elemanı tarafından en geç üç iş günü içinde yapılır ve sonuca göre doldurulan yeniden inceleme formu bölüm başkanlığına teslim edilir.

Yine de, sınav sonuçlarına itiraz etmeden önce, ilk olarak sınav sorularının cevap anahtarının bir örneğini kontrol etmek zorunludur. Cevap anahtarının bir örneği, üniversite tarafından hazırlanmış bir sisteme yüklenmiştir. Öğrenciler bu sistemi kullanarak cevap anahtarını kontrol edebilir.

Yeniden İnceleme ve İtiraz Süresi: Öğrenciler yeniden incelenmeye üç iş günü içinde itiraz edebilir. İtiraz edilmesi hâlinde sınav kâğıdı, ilgili öğretim elemanınca hazırlanmış cevap kâğıdı da dikkate alınarak sınav inceleme komisyonu tarafından incelenir. İşlem, en geç üç iş günü içinde sonuçlandırılır ve itiraz değerlendirme formu doldurulur.

Sonuç olarak, sınav notuma itiraz etmek için, 15 gün içerisinde yazılı başvuru yapmalı ve itiraz süre bitmeden yapılan başvuruları 15 gün içerisinde birim yönetim kurulunca karara bağlanması gerekir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ders_ye
... (146 karakter daha)
```

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 5/6
  - [x] ders
  - [ ] staj
  - [x] GANO
  - [x] 2,00
  - [x] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 6123.7 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklamak mümkün. Bu süreci iki kısımda ele aldık: Mezuniyet Koşulları ve İlişik Kesme Koşulları.

Mezuniyet Koşulları:

1. Önlisans Diploması: Hazırlık hariç bốn yarıyıl süreli meslek yüksekokullarında bir mesleğe yönelik olarak yürütülmekte olan programlardan mezuniyet hakkı kazanan öğrenciler için “Önlisans Diploması” düzenlenir.
 * Kaynak: Uygulama Esasları - Diploma ve Mezuniyet Belgeleri (pdf), MADDE 5.
2. Lisans Diploması: Hazırlık hariç, dört yıl süreli fakülte ve yüksekokul lisans programlarından mezuniyet hakkı kazanan öğrenciler için “Lisans Diploması” düzenlenir.
 * Kaynak: Uygulama Esasları - Diploma ve Mezuniyet Belgeleri (pdf), MADDE 5.
3. Çift Ana Dal Lisans Diploması: Ana daldaki mezuniyetlerine bağlı olarak ikinci ana dal lisans programını tamamlayan öğrenciler için “Çift Ana Dal Lisans Diploması” düzenlenir.
 * Kaynak: Uygulama Esasları - Diploma ve Mezuniyet Belgeleri (pdf), MADDE 5.
4. Yandal Sertifikası: Ana daldaki mezuniyetlerine bağlı olarak yandal lisans programlarını tamamlayan öğrenciler için “Yandal Sertifikası” düzenlenir.
 * Kaynak: Uygulama Esasları - Diploma ve Mezuniyet Belgeleri (pdf), MADDE 5.
5. Tezli Yüksek Lisans Diploması: Enstitülerdeki tezli yüksek lisans programlarını tamamlayanlara “Tezli Yüksek Lisans Diploması” düzenlenir.
 * Kaynak: Uygulama Esasları - Diploma ve Mezuniyet Belgeleri (pdf), MADDE 5.
6. Tezsiz Yüksek Lisans Diploması: Enstitülerdeki tezsiz yüksek lisans programlarını tamamlayanlara “Tezsiz Yüksek Lisans Diploması” düzenlenir.
 * Kaynak: Uygulama Esasları - Diploma ve Mezuniyet Belgeleri (pdf), MADDE 5.
7. Doktora Diploması: Enstitülerdeki doktora programlarını tamamlayanlara “Doktora Diploması” düzenlenir.
 * Kaynak: Uygulama Esasları - Diploma ve Mezuniyet Belgeleri (pdf), MADDE 5.
8. Sanatta Yeterlik Diploması: Enstitülerdeki sanatta yeterlik programlarını tamamlayanlara “Sanatta Yeterlik Diploması” düzenlenir.
 * Kaynak: Uygulama E
... (2479 karakter daha)
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 5278.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Siz diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. 

Ayrılan iki sorun için ne yapmalıyım?

1) Diplomamı kaybettim:

Bu durum için, "KAYIPLARI VE DEĞİŞİKLİKLERİ YÖNETME" madde 17 gereğince  yaygın gazetelerden birine diploma kayıp ilanını vermeniz ve daha sonra başvuru dilekçesi, onaylı nüfus cüzdanı ve banka dekontu ile diploma aldığınız üniversiteye müracaat etmeniz necessário. Bu öğrencilere ilk diplomada yer alan bilgileri içeren yeni bir diploma düzenlenir. İkinci Nüsha olduğunu belirten bilgiler de yer alır.

2) E-devlette mezuniyet bilgilerim görünmüyor:

Bir başka problem için, "MEZUNİYET BELGELERİ" madde 8 gereğince diploma eki bilgilerinin elektronik ortamda arşivlenmesi gerektiğini hatırlıyoruz, fakat diploma defterine kaydedilen bilgilerin elektronik ortamda hazırlanıp arşivlenebilmesi için "MEZUNİYET BELGELERİ" madde 11 gereğince diploma defterine diploma eki bilgilerinin ve teslim edildiği tarih ile diplomanın teslim alanının imzasının atılmasını gerektirir. Bundan başka, diploma defterince diploma numaralarına göre kaydolmadıkları durumda diploma bilgilerinin kaydedilmemesi anlamına gelir. Dolayısı ile diploma defterinin kontrolüne ihtiyacınız var.

Hatta, bir başka problem için, "HÜKMÜ BULUNAN HALER" madde 18 gereğince diplomanın yeniden düzenlenmesi durumunu hatırlıyoruz. Eğer diplomanızda mahkeme kararına dayalı nüfus kaydı değişikliği varsa, diplomanız yeniden düzenlense de e-devlette mezuniyet bilgilerin görünmemesi durumunda diploma defterindeki kontrolü kontrol edebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
```

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [ ] %40
  - [ ] %60
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 6392.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Ogrenci Isleri:
Soruunuzun cevabına göre, uzaktan eğitim yoluyla alınan 5-1 derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı değildir. Ancak bazı belirtilerde farklılıklar mevcuttur.

Doğrudan cevap: Evet.

1. Uzaktan eğitim yoluyla yürütülen dersler için, yüz yüze derslere göre devam koşulunun artırılmış oranı % 80'dir (Kaynak 3, MADDE 17).
2. Uzaktan eğitim yoluyla yürütülen yüz yüze dersler için, yüz yüze dersler gibi devam koşulunu yerine getirmeyen öğrencilerin listesi, öğretim elemanı tarafından öğrencilere duyurulmak üzere ilgili bölgeye/birime teslim edilir (Kaynak 3, MADDE 17).
3. Atatürk İlkeleri ve İnkılap Tarihi, Türk Dili, Yabancı Dil, İş Sağlığı ve Güvenliği ve Yabansız Mesleki Dil dersleri, face-to-face (yüz yüze ders) olarak yürütülerek, yüz yüze derslere benzeyen şekilde sınavlar yapılır (Kaynak 2, MADDE 5).
4. Uzaktan eğitim ön lisans ve lisans öğrencilerinin dönem içi sınavları internet üzerinden yapılır (Kaynak 5, MADDE 25).
5. Sınav kâğıtları ilgili birimde en az iki yıl süre ile saklanır (Kaynak 5, MADDE 25).
6. Öğrenciler, sınav kâğıtları ve diğer belgelerini, sınava ilan edilen gün, saat ve yerde girmek ve öğrenci kimlik belgeleri ile istenen diğer belgeleri yanlarında bulundurmak zorundadır (Kaynak 5, MADDE 25).
7. Sınav kâğıtları, ilgili birim arşivine verilir ve en az iki yıl süre ile saklanır.
8. Sınav kâğıtları için, ilgili birim arşivine teslim edilen belge tarihine ilişkin bir madde yok, ancak sınav kâğıtları en az iki yıl süre ile saklanacağı belirlenmiş.

Akademik Programlar:
Soru 1:
Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

Yanit:
HAYIR

Soru 1.1:
Uzaktan eğitim yoluyla alınan derslerin sınav ve başarı değerlendirme hükümleri ne şekildedir?

Yanit:
Uzaktan veya örgün verilen derslere ait devam ve başarı durumu Ondokuz Mayıs Üniversitesi Ön Lisans ve Lisans Eğitim-Öğretim Yönetmeliği ile Ondokuz Mayıs Üniversitesi Lisansüstü Eğitim ve Öğretim
... (1188 karakter daha)
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 5044.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınava kopya çekilmesinin cezası nedir?

Cep telefonu ile herhangi bir şekilde ilgilenen öğrenciye kopya muamelesi yapılır.

Kaynak: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf, ilgili madde: 3

Sınavduringe kopya çekilmesinin disiplin süreci nasıl işler?

Sınav görevlileri, sınav kurallarına aykırı davranışlarda bulunan öğrencilere kopya vermek ve çekme girişiminde bulunmak da bir disiplin suçudur. Sınav görevlileri bu suçun tespitine karar verme yetkisine sahiptir. Bu gibi durumlarda sınav görevlisi veya ilgili öğretim elemanı, uyarıda bulunmaksızın öğrenciler hakkında işlem yapabilirler.

Kaynak: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf, ilgili madde: 12

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
- **Sure**: 5053.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Üniversiteyi Bıraktırmak İsteği

Eğer üniversiteyi bırakmak istiyorsanız, öğrenci işleri bölümüne başvurmanız gerekir. Bu başvuruda, nedenlerini açıklamak ve gerekli документleri temin etmek gerekir.

Gerekli Belgeler

Aşağıdaki belgelerin tamamlanması gerekir:

* Öğrenci işleri bölümüne dilekçe ile başvurmak
* Kimlik belgesi (T.C. Kimlik Numarası ile)
* Eğitim ücretlerin ödenmesi için makbuzlar (eğer ödenmediyse)
* Öğrenci işleri bölümünden alınacak belge (ders dışı aktivitelere katılımdan ve kredisiz derslerden sorumluluğa ilişkin)

Belgeleri tamamladıktan sonra, Öğrenci İşleri bölümüne başvurmalı ve üniversiteyi bırakmak istediğinizni belirtmelisiniz.

İşlemler

Üniversiteyi bırakmak için yapılan işlemler;

1. Davetiye Alma: Öğrenci İşleri bölümüne başvurarak, üniversiteyi bırakmak istediğinizni belirtmeniz gerekir.
2. Belgelerin Elde Edilmesi: Öğrenci işleri bölümü tarafından, gerekli belgeler elde edilir.
3. Kredi ve Öğrenim Borçları: Üniversite tarafından, kredi ve öğrenim borçlarınızın ödendiğini doğrulamak gerekir.
4. Kayıt Silinme İşlemleri: Kayıt silinme işlemlerinin tamamlanması gerekir.
5. Ödemenin Geri Bildirilmesi: Öğrencilikten çıkışın ardından, öğrenim ücretlerinizin geri ödendiğini doğrulamak gerekir.

Dikkat Edilmesi Gereken Hususlar

1. Takvim: Takvim dikkate alınarak işlemler gerçekleştirilmelidir.
2. Gerekli Belgelerin Tamamlanması: Gerekli belgelerin tamamlanması ve öğrenci işleri bölümüne teslim edilmesi gerekir.
3. Kredi ve Öğrenim Borçları: Öğrenim borçlarınızın ödendiğini doğrulamak gerekir.
4. Kayıt Silinme İşlemleri: İşlemlerin tamamlanması gerekir.
5. Ödemenin Geri Bildirilmesi: Öğrenim ücretlerinizin geri ödendiğini doğrulamak gerekir.

Sonuç

Üniversiteyi bıraktığınızda, öğrencilikten çıkış yapacağınızdan emin olduktan sonra işlemlerinizi tamamlayabilirsiniz. İşlemler, öğrenci işleri bölümü tarafından yürütülür.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini p
... (318 karakter daha)
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] kayıt
  - [x] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4907.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sizi 1 yıl aradan sonra okulumuza döndüğünüz için ders seçimini yapmanız gerektiğine ilişkin sorunuz var.

Bu soruya doğru yanıtı vermek için, lütfen referans olarak sunduğunuz kaynakları inceleyeceğim.

Soru: "Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?"

Yanit: 
Bilindiği gibi bir öğrencinin önlisans ve lisans programlarında öğrenimine devam etmeyeceği bir durum (hastalık, akrabanın ölümü, tabii afetler vs.) olunca veya Üniversite dışı burs, staj, araştırma ve benzeri imkânların olması durumunda öğrencinin kaydı dondurulabiliyor. Kayıt dondurulan süre boyunca öğrenci öğrenimine devam edemez ve kayıt dondurduğu döneme/yıla ait sınavlara giremez. Kayıt dondurma süresi bitince öğrenci, ayrıldığı dönemin/yılın başından başlamak koşuluyla öğrenimine kaldığı yerden devam eder ve süre hesabında dikkate alınmaz.

Sizin 1 yılında öğrenimine ara verdiği için ve kayıt dondurma süresinin bitiminde öğrenimine kaldığı yerden devam edeceğini düşünüyorum. Dolayısıyla, ders seçimine ilişkin süreç ile ilgili şu kurallara göre ilerletebilir:
Birinci yarıyıl sonundan itibaren; varsa öncelikle daha önce alıp başarısız olduğunuz dersleri ve öğrenim gördüğünüz yarıyıllarda almadığınız ders veya dersleri aldıktan sonra, her yarıyıl sonunda oluşan, genel not ortalamasına göre bir üst sınıftan kredi sınırları içerisinde kalarak ders alabilirsiniz. Kayıt yenileme sırasında öncelikle başarısız olduğunuz ders/dersler ve kredi sınırları içinde alt yarıyılda almadığınız dersleri alıp seçerek kayıt yaptırmanız gerekmektedir.

Ders seçiminizi yapabilmeniz için akademik takvimde belirlenen süre içinde ders kaydını yapman gerekmektedir. Süresi içinde ders kaydını yapmayan öğrenciler, o dönemde öğrenimlerine devam etme hakkını kaybederler. Kaybedilen dönem, öğrenim süresinden sayılır. Süresi içinde ders kaydını yapmayan öğrencilerin kayıtları; başvurmaları ve mazeretlerinin haklı ve geçerli olduğu ilgili birim yönetim kurulunca kabul edilmesi koşuluyla, akademik
... (638 karakter daha)
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] danışman
  - [x] bölüm
  - [x] oidb@omu.edu.tr
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=procedural
- **Sure**: 3207.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Hocam, sizin ders notlarınızı sisteme girmemiş olmanız durumunda ne yapabilirim?

İçindekiler:

1. Akademik Takvimde Belirlenen Süre İçinde Kayıt Yapın
2. Danışman Onayını Alın
3. Bölüm Başkanı veya Dekan/Müdürüne Bildirin

1. Akademik Takvimde Belirlenen Süre İçinde Kayıt Yapın

Kaynak 1: sık_sorulan_sorular.txt

*Akademik takvimde belirtilen süre içinde ders kaydınızı yapmanız gerekir.*

Akademik takvimde belirtilen süre içinde ders kaydınızı yapmanız önemlidir. Bu tarihler Öğrenci İşleri Daire Başkanlığı WEB sayfasından bulabilirsiniz.

2. Danışman Onayını Alın

Kaynak 3: sık_sorulan_sorular.txt

*Danışman onayını muhakkak yaptırmanız gerekir.*

Danışman onayını almayan öğrenciler, akademik takvimde belirtilen süre içinde kayıt yapmaya zorlanabilir. Eğer danışmanınıza ulaşamaz ve onayını alamazsınız:

* Bölüm başkanınıza ulaşın
* Bölüm başkanı ile ulaşamazsanız Dekan/Müdürene bildirmek sureti ile akademik takvimde belirtilen sürede danışman onayını muhakkak yaptırınız
* Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz.

3. Bölüm Başkanı veya Dekan/Müdürüne Bildirin

Kaynak 3: sık_sorulan_sorular.txt

*Nihayetinde Dekan/Müdürüne durumunuzu bildirmek zorundasınız.*

Bölüm başkanı veya Dekan/Müdürene bildirdiğiniz tarihte, akademik takvimde belirtilen süre içinde kayıt yaptırılacaktır.

Sonuç

Akademik takvimde belirtilen süre içinde kayıt yaptırmak ve danışman onayını almak önemlidir. Sorunuz birden fazla alt-soruyu içeriyorsa her birini ayrı ayrı cevapla.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
