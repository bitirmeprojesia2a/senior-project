# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 04:01:41
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 96.0% |
| Uretim Modu Dogrulugu | 96.0% |
| Anahtar Bilgi Kapsami | 65.0% |
| Temiz Kalite Orani | 96.0% |
| Ortalama Sure | 7030.1 ms |
| Medyan Sure | 5220.2 ms |
| Intent Analizi Aktif | 24/25 |
| Force LLM Sentez | 21/25 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 7663.4 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 2/3 | 11177.0 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 2/4 | 5220.2 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 4/4 | 2686.2 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 8022.8 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 21889.0 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 9135.7 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 7110.4 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 5/5 | 14448.3 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 1833.2 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 2/4 | 3490.2 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 3/4 | 1666.9 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 14866.3 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 4/4 | 10970.1 | uydurma_riski |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 2/3 | 11910.1 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 2984.6 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 2041.5 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 1/4 | 1490.6 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 3/6 | 14799.6 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 9004.9 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | YANLIS | OK | 2/5 | 4698.0 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 1459.3 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 3050.3 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 1348.2 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 3/3 | 2786.7 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs', 'announcement'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=7561ms; dispatch=2061ms; global_llm=1359ms; compose=0ms
- **Sure**: 7663.4 ms
- **API Response Time**: 7558.4 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Benchmark, Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu 26.01.2026 - 01.02.2026 döneminde yapmalı ve karar çıkana kadar derslere devam etmeli değildir. Muafiyet başvurunun ilk sonuç günü 06.02.2026 olarak belirlenmiştir. Başvuru son bulacağı tarih 01.02.2026'dır. 

Bilgisayar Muhendisligi bolumu/programi ile ilgili sorulan sorunun cevabi, yukardaki genel kurala uyumlu olarak verilemez.
 
Yatay geçişle gelen öğrenci muafiyet başvurusunu yatay geçişin kabul edilmesinden sonra yapabilir, fakat akademik yonergeler icerisinde de bu bilgi bulunmamaktadir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Duyuru kaydi: 2025-2026 Eğitim Öğretim Yılı Bahar Yarıyılı Yatay Geçiş Yedek sonuçları (https://www.omu.edu.tr/tr/icerik/duyuru/2025-2026-egitim-ogretim-yili-bahar-yariyili-yatay-gecis-yedek-sonuclari)
- Duyuru kaydi: 2025 - 2026 Güz Dönemi Yatay Geçiş Başvuru Sonuçları (https://eem-muhendislik.omu.edu.tr/tr/haberler/2025-2026-guz-donemi-yatay-gecis-basvuru-sonuclar)
- Duyuru kaydi: 2025-2026 eğitim öğretim yılı bahar yarıyılı yatay geçiş sonuçları (https://www.omu.edu.tr/tr/icerik/duyuru/2025-2026-egitim-ogretim-yili-bahar-yariyili-yatay-gecis-sonuclari)
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=10950ms; dispatch=5246ms; global_llm=4365ms; compose=0ms
- **Sure**: 11177.0 ms
- **API Response Time**: 10947.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Tek ders sınavına girebilmek için stajımın tamamlanmış olması gerekmez. Staj dersini tamamlamış olma kosulu yok. Staj dersimi tamamlamış olmam da sınavdan başarı beklenmez.

Tek ders sınavında başarılı sayılabilmeniz için minimum 50 not alınması gereklidir. 100 üzerinden en az 50 not almayı başarılması, başarılı sayılmana neden olur. Bu sayede staj dersi tamamlanmış olmanı veya bulunmaz. Staj dersimi tamamlamış olmama kosulu yok.

Detay için: Soruda sorulmayan sorular ve durumlar için kaynakta bilgi bulunduğu halde bilgi bulunamadığı için ilgili bilgiler verilmeyecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: yonerge_uluslararasi_ogrenci_kabul.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
```

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [ ] yeni
  - [x] ders
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=5183ms; dispatch=5026ms; compose=0ms
- **Sure**: 5220.2 ms
- **API Response Time**: 5176.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Evet, devam zorunluluğunuz değişir. Başarısız olduğunuz seçmeli ders yerine, başka bir seçmeli ders seçerken, devam zorunluluğu yerine getirilemez. Ancak, danışmanın onayı ile sonraki dönemde devam koşulu ile bir başka seçmeli ders alabilir ve basarısız oldugu dersler icin normal dönemde devam zorunluluğu yerine getirmek koşulu altında derslere devam etmemiş sayılsınız.

Benchmark: Kaynaksız bu durum için net bilgi bulunmuyor.

(2) Öğrenci; danışmanın onayıyla, başarısız olduğu bir seçmeli ders yerine, sonraki dönemde/yılda devam etmek koşuluyla, bir başka seçmeli dersi alabilir.

MADDE 12 Kaynak 2'de belirtilen yonerge_yaz_okulu_egitim_ogretim.pdf belgesinde:
(1) Yaz okulunda derslere devam zorunludur.
(2) Yaz okulunda alınıp devam zorunluluğu yerine getirilen ancak başarısız olunan dersler icin devam zorunda olunmaması gerekir.

MADDE 17 Kaynak 3'te belirtilen yonetmelik_onlisans_lisans_egitim_ogretim.pdf belgesinde:
(1) Derslere devam durumu, dersin öğretim elemanınca yapılan yoklamalarla tespit edilir. eğitimde öğrencilerin yüz yüze yürütülen derslerin teorik saatlerinin en az % 70'ine; ders uygulamaları, atölye ve laboratuvarların ise en az % 80'ine devam etmeleri zorunludur.

Belge/Sistem/Işlem Adı: devam zorunluluğu, ders seçimi, danışman onaylı ders değişiklik

Adım Listesi:
- Seçmeli ders değişikliği yapmak,
- Danışman onayını alma,
- Devam zorunluluğu yerine getirilme.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yonerge_yaz_okulu_egitim_ogretim.pdf
- Belge: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf
```

### Q4: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: hard
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] transkript
  - [x] dahil
  - [x] ortalama
  - [x] tamamlamıştır
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=2638ms; dispatch=2583ms; compose=0ms
- **Sure**: 2686.2 ms
- **API Response Time**: 2629.7 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Benchmark, Soru 1: Pedagojik formasyon dersleri transkripte dahil ediliyor mu?
Evet, pedagojik formasyon dersleri transkripte dahil ediliyor.

Soru 2: Mezuniyet ortalamasına etkisi var mı?
Evet, pedagojik formasyon dersleri mezuniyet ortalamasına dahil edilecek.

Soru 3: Diplomada nasıl bir ibare yer alıyor?
Diplomalarda "Pedagojik formasyon eğitimini tamamlamıştır." ifadesi yer alacaktır.

Soru 4: Pedagojik formasyon eğitiminde hangi dersler verilecek?
- Eğitime Giriş
- Öğretim İlke ve Yöntemleri
- Sınıf Yönetimi
- Özel Öğretim Yöntemleri
- Rehberlik ve Özel Eğitim
- Eğitimde Ölçme ve Değerlendirme
- Eğitim Psikolojisi
- Öğretim Teknolojileri
- Öğretmenlik Uygulaması

Soru 5: Pedagojik formasyon eğitimi derslerinin hepsi alma zorunluluğu var mı?
Hayır, pedagojik formasyon eğitimi derslerini almak öğrencilerin talebine bağlıdır.

Soru 6: Son sınıf öğrencisi olup kayıtlı olduğu programın mezuniyet için gerekli tüm şartlarını yerine getiren öğrenciler, pedagojik formasyon eğitimi uygulamasından yararlanabilecekler mi?
Hayır, son sınıf öğrencisi ancak kayıt oldukları programın mezuniyet için gerekli tüm şartlarını yerine getirdiyse pedagojik formasyon eğitimi uygulamasından yararlanabileceklerdir.

Soru 7: Pedagojik formasyon eğitiminde alınması zorunlu ders var mı?
Hayır, pedagojik formasyon eğitimi derslerini almak öğrencilerin talebine bağlıdır; ancak öğrenciler Öğretmenlik Uygulaması'ni alarak dersleri tamamlamalıdır.

Soru 8: Pedagojik formasyon derslerinin yüz yüze olması zorunlu mu?
Evet, pedagojik formasyon derslerinin yüz yüze olması esastır.

Soru 9: Pedagojik formasyon derslerini sistem üzerinden seçen öğrencilerin durumu nedir?
Sistem üzerinden pedagojik formasyon derslerini seçen öğrenciler, pedagojik formasyon eğitimi uygulamasından yararlanabileceklerdir.

Soru 10: Pedagojik formasyon derslerini aldıktan sonra transkriptte yer almayacak mı?
Hayır, pedagojik formasyon derslerini aldıktan sonra transkriptte yer alacak; ancak öğrenci diplomasında bu eğitimi
... (412 karakter daha)
```

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs', 'finance'] (beklenen: ['academic_programs', 'finance', 'student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] ücret
  - [x] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=7989ms; dispatch=2629ms; global_llm=5233ms; compose=0ms
- **Sure**: 8022.8 ms
- **API Response Time**: 7981.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, İçeriğinizi inceleyince, kullanıcı sorusuna ilgili bilgiler departmanlar arasında dağılmış durumda olduğu anlaşılabilir. Bu bilgileri birleştirmek için, departman bazlı bilgileri kontrol edeceğiz ve ilgili bilgilerin birleştirilmesiyle tutarlı bir final cevap oluşturacağız.

KAYIT YAPTIRMA VE ÖĞRENİM ÜCRETİ:

- Student_Affairsundan elde edilen bilgilere göre kayıt yaptırırken öğrenim ücretini, Üniversitenizin belirlediği bankaya yatırmanız gerekmekte. Ancak bankanın adı bilinememektedir. 
- Academic_Programsundan elde edilen bilgilere göre kayıt yaptırılan öğrenciler için ise Ödemeler için İSTEÇ Hesabına yatırmak üzere belirlenen kanalları kullanarak öğrenim ücretini yatırmanız gerekmektedir.
- Financeundan elde edilen bilgilere göre ise yıllık öğrenim ücreti 2.397,00 TL ve dönemlik öğrenim ücreti 1.198,50 TL'dir. Bu bilgilere göre, öğrencinin kayıt yaptırırken ödemeyeceği bir bankaya veya hesabına ait hiç bilgi verilmiyordir, bu nedenle bu bilginin kullanımı sırasında 'bilgi bulunamadı' yazılmalıdır.

İKAMET İZNİ:

- Student_Affairsundan elde edilen bilgilere göre, ikamet izni için Öğrenim ücretinizi yatırabilmek için bir banka hesabı olmanız gerekmektedir. Bu nedenle, bankanızı bilin.
- Academic_Programsundan elde edilen bilgilere göre ise, uluslararası öğrenci statüsünde ön lisans ve lisans programlarına kayıt yaptıran öğrenciler için öğrenim ücreti iade edilmemektedir.
- Financeundan elde edilen bilgilere göre ise herhangi bir bilginin mevcut olmadigindan, bu alandaki sorulan bilgileri reddetmemiz gerekir.

SONUÇ:

Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi Ödemeler için İSTEÇ Hesabına yatırmak üzere belirlenen kanalları kullanarak yatırmalısınız. Yönetmelikte bu konuya ilişkin herhangi bir bilginin bulunmamaktadır. Ayrıca ikamet izni için, öğrencinin öğrenim ücretini yatırabilmek için bir banka hesabı açması gerekmektedir. Öğrenim ücreti yıllık 2.397,00 TL ve dönemlik 1.198,50 TL'dir. 

Bilgi bulunamadı:

---
Daha iyi yardimci ola
... (487 karakter daha)
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs', 'student_affairs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=factual
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant, google_ai/gemini-2.5-flash-lite [fallback]; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=21852ms; dispatch=10181ms; global_llm=7580ms; compose=0ms
- **Sure**: 21889.0 ms
- **API Response Time**: 21847.3 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Benchmark, * ÇAP programına başvurmak istediğiniz halde harç borcu olan öğrencilere göre farklı bir yaklaşım söz konusu değildir. ÇAP programına başvurabilmek için ana dal lisans programında yer alan tüm derslerini almış ve başarmış olmak; başvuracağı yarı yıla kadar ana dal not ortalamasının 4,00 üzerinden en az 3,00 olmak gerekmektedir. Ayrıca ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk % 20'sinde bulunmanız gerekir.
* Harç borcunu ödemeniz durumunda da ÇAP programına başvurabilir, başvuruda bir sorun olmaz.
* Öğrenim ücreti için Turk Ögrenci/Mühendislik Fakültesi bilgisi veritabanında kayitli. Yillik ücret: 2.397,00 TL, donemlik ücret: 1.198,50 TL.
* Katkı payını veya öğrenim ücretini ödemeyen öğrenciler ders kaydı yaptıramaz ve öğrencilik haklarından yararlanamaz, ödemeleri akademik takvimde belirtilen süreler içinde olması gerekmektedir.
* Bir öğrencinin aynı anda birden fazla ikinci ana dal diploma programına kayıtlı olamayacağına dikkat edilmesi gerekmektedir.
* Aynı anda ikinci ana dal diploma programı ile YDP’ye kaydolmanız mümkün değildir, ancak fazla kredi tamamlamış olan öğrencilere öncelik verilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: VT
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
```

### Q7: Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra ders kaydını nasıl yapacağım, danışmanın onay süreci nasıl işliyor?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=9084ms; dispatch=1606ms; global_llm=7392ms; compose=0ms
- **Sure**: 9135.7 ms
- **API Response Time**: 9078.5 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Ders kaydı yapabilmek için kayıt yenileme dönemi harç ücretinizi yatırmış olmanız gerekir. Bu situationun ardından, aşağıdaki adımları takip edebilirsiniz:

- Öğrenci bilgi yönetim sistemine giriş yaparak müfredat bilgilerinize göre transkriptinizi kontrol ediniz.
- Başarı ettiğiniz dersleri müfredatınızla karşılaştırın.
- Danışman onay bittikten sonra, listeden çıkarılma riski bulunan dersleri kontrol ediniz.
- Sınıf yoklama listesine imza atınız.

Danışman onayına gönderilen dersler için, devam şartınız olmasa da ders kaydı yapabilirsiniz. Seçmeli dersler için veya başka bir sebeple değiştirmek istediğiniz dersler için akademik takvimde belirtilen süre içinde danışmanınıza iltibat ediniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yüzde_on_başarı_değerlendirme_yönergesi.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [ ] bildiri
  - [x] harç
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=7069ms; dispatch=5141ms; global_llm=1841ms; compose=0ms
- **Sure**: 7110.4 ms
- **API Response Time**: 7063.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Burslu öğrencisiniz ve yatay geçiş yapmak istediğinizde bursum kesilebilir ve yeni üniversitede harç ödemek zorunda olabilirsiniz. Yatay geçiş yapan öğrencilerin yemek bursu alma hakları vardır, ancak bu haklar %10'luk kontenjan dahilinde verilir. Yemek bursu alma hakların belirlenmesinde, puan esitligi halinde yaş kucuk olan adaya oncelik verilir.

- Bursunuzun Kesilme Durumu: Yatay geçiş yaparsanız bursunuzun kesilip kesilmeyeceği, burs aldığınız kurumla iletişime geçerek öğrenilebilecek bir durumdur. Bursunuzun devri veya kesilip kesilmeyeceği konusunda bilgiye ulaşmak için burs aldığınız kurumla iletişim kurmanız gerekir.
- Yemek Bursu Alma Hakları: Yatay geçiş yapan öğrencilerin yemek bursu alma hakları vardır. Ancak bu haklar %10'luk kontenjan dahilinde verilir. Yemek bursu alma hakların belirlenmesinde, puan esitligi halinde yaş kucuk olan adaya oncelik verilir.
- Harç Durumu: Yatay geçiş yapan burslu öğrencilerin harç durumları yeni üniversitedeki öğrenci durumuna gore belirlenir. Yatay geçiş yapan öğrenciler, istenen belgeleri E-Devlet üzerinden, UBYS öğrenci bilgi ekranından veya öğrenim gördükleri fakülte/yüksekokuldan temin edebilirler.

Yatay geçiş başvuru tarihlerini https://oidb.omu.edu.tr/tr/ogrenci/yatay-gecis internet sayfasında bulabilirsiniz.

Bilgi bulunamadı: Yatay geçiş başvurunuzun değerlendirilmesi sonucunda bursunuzun kesilip kesilmeyeceği veya harç durumunuzun nasıl belirleneceği hususunda daha detaylı bilgi için burs aldığınız kurumla veya öğrenci işleri iletişime geçmeniz önerilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: idari_ve_mali_işler_birimi.txt
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs', 'finance'] (beklenen: ['academic_programs', 'student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 5/5
  - [x] azami
  - [x] ek
  - [x] süre
  - [x] katkı payı
  - [x] öde
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant, google_ai/gemini-2.5-flash-lite [fallback]; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=14409ms; dispatch=9884ms; global_llm=4410ms; compose=0ms
- **Sure**: 14448.3 ms
- **API Response Time**: 14405.2 ms
- **Kaynak Sayisi**: 15

**Yanit:**
```
Benchmark, Ek süre hakkınız var, ancak bu sürede katkı payı öder misiniz hususunda net bilgi bulunmamaktadır. 4. sınıf öğrencisi olarak program sürenizi 1 yıl aştığınız takdirde azami eğitim süresi sonunda mezun olabilmek için son sınıf öğrencilerine, başarısız oldukları tüm dersler için ek süre verilir. Bu ek süre, öğrenimlerini tamamlayamayan öğrencilere ilave iki dönem olarak tanınır.

Detaylar şu şekilde:

- Tıp Fakültesi için 6 yıllık normal eğitim-öğretim süresi vardır. 4. sınıf öğrencisiyseniz, program sürenizi 1 yıl aştığınızda ek süre hakkınız olur.
- Mühendislik Fakültesi için 4 yıllık normal eğitim-öğretim süresi vardır. 4. sınıf öğrencisiyseniz, program sürenizi 1 yıl aştığınızda ek süre hakkınız eder.
- Öğrenim süresini tamamlamadığınız süreler için katkı payı/öğrenim ücreti ödenmez.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM
- Finans: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
```

### Q10: Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'announcement'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [x] tekrar
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=1798ms; dispatch=1594ms; compose=0ms
- **Sure**: 1833.2 ms
- **API Response Time**: 1792.3 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Hayir.
 
Devamsızlıktan kalan bir öğrenci o dersin bütünleme sınavına giremez.
Devam koşulu yerine getirilmemiş tekrar dersine devamsızlık nedeniyle girmek esastır. Bu nedenle, devamsızlığın % 50'sinden fazlasını aşmış olan öğrenciler, devaamsızlık nedeniyle giremeyeceklerdir.

Ilgili duyurular:
1. 📢 Girişimcilik ve Yenilikçilik Dersinin Derslikleri Hakkında
 Girişimcilik ve Yenilikçilik dersinin dersliklerini öğrenmek için görseli inceleyebilirsiniz.
 Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/girisimcilik-ve-yenilikcilik-dersinin-derslikleri-hakkinda
2. İngilizce II ve İleri İngilizce II Derslerinin Mazeret Sınavları Hakkında
 İngilizce II ve İleri İngilizce II derslerinden mazeret sınavına girecek olan öğrencilerimiz 13 Mayıs Salı günü Saat 09:00'da MF103'te sınava girebilirler.
 Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/ingilizce-ii-ve-ileri-ingilizce-dersleri-mazeret-sinavlari-hakkinda
3. TBFİZ124 Fizik II ve TBFİZ122 Fizik II Dersini Alan Öğrencilerin Dikkatine!
 Laboratuvardan devam almış fakat ders tekrarı olan öğrencilerin laboratuvar notunu belirlemek üzere, LABORATUVAR SINAVI YAPILACAKTIR. Sınavın duyurusu için tıklayınız.
 Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/duyuru-tbfiz124-fizik-ii-ve-tbfiz122-fizik-ii-dersini-alan-ogrencilerin-dikkatine
 Ek baglanti: DUYURU 2025 BAHAR - https://bil-muhendislik.omu.edu.tr/tr/haberler/duyuru-tbfiz124-fizik-ii-ve-tbfiz122-fizik-ii-dersini-alan-ogrencilerin-dikkatine/DUYURU_2025_BAHAR.pdf

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: bağıl_değerlendirme_yönergesi.pdf
- Duyuru kaydi: 📢 Girişimcilik ve Yenilikçilik Dersinin Derslikleri Hakkında (ht
... (534 karakter daha)
```

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] öğrenim ücreti
  - [ ] gerek yok
  - [ ] yönetim kurulu
  - [x] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=3441ms; dispatch=1533ms; global_llm=1852ms; compose=0ms
- **Sure**: 3490.2 ms
- **API Response Time**: 3431.9 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Benchmark, Kayıt Dondurması veöğrenim Ücreti

İkinci öğretim öğrencisi olarak, bir dönem kayıt dondurmak istediğinizde, öğrenci olarak katkı payınızı/öğrenim ücretinizi ödemek zorundasınız. Kayıt dondurma, eğitim süresinden düşürülmesine yol açmayan bir işlem olduğundan, eğitim süresinden sayılır. 

Eğitim Süresinden Sayılma

MADDE 13- (1) Kayıtlı olduğu program gereği katkı payı/öğrenim ücreti ödemesi gereken öğrencilerin

(2) Kayıtlı oldukları programdan azami süre içinde mezun olamayan öğrenciler

(yan dal/çift ana dal öğrencileri dersleri alıp başarılı olan ve başarı ortalamasına göre yapılan sıralamada ilk % 10’a giren) ikinci öğretim öğrencilerinin kayıt dondurma işlemi, eğitim süresinden sayılır.

Ödeme Yükümlülüğü

Yıl genelinde yaptığınız ödemeler için, 2025-2026 yılı Türk Öğrenci Katkı Payı ve Öğrenim Ücretleri belgesine göre, yaptığınız ödemeler için hesabınızı kontrol ediniz.

Detaylar
- Kayıt dondurma işleminden ötürü eğitim süresinden düşürülmenize neden olması durumunda, öğrencilik haklarınızın sona ermesine neden olabilir.
- Kayıt dondurma, öğrencinin katkı payını/öğrenim ücretini ödemekle yükümlü olacağını belirtmektedir.

Kaynak Bilgisi
- KAYNAK 1: yonetmelik_onlisans_lisans_egitim_ogretim.pdf | Güven: yüksek 

Detaylarınız için 2025-2026 yılı Türk Öğrenci Katkı Payı ve Öğrenim Ücretleri belgesini kontrol ediniz.
Bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] transkript
  - [x] Ek Madde
  - [x] başvuru yapabilir
  - [ ] GANO
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=1630ms; dispatch=1605ms; compose=0ms
- **Sure**: 1666.9 ms
- **API Response Time**: 1627.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Evet, Ek Madde-1 kapsamında yatay geçiş başvurusu yapabilirsin. Ancak transkriptin bulunması zorunluluğu bulunmuyor. [1]

Ek Madde-1 kapsamında yatay geçiş için en fazla 2 başvuru yapabilirsin. [2]

Kaynak: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf, Guven: yuksek 

Not: Başvuru esnasında sistemin talebi olan belgelerin eksiksiz olarak ibraz edilmesi gerekmektedir. [3]

Yatay geçiş türleri arasında Ek Madde-1 yatay geçiş türü vardır. Bu türde, öğrenciler aldıkları ÖSYM sınav puanları ile başvuru yapabilir.[4]

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: sık_sorulan_sorular.txt
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=14818ms; dispatch=8587ms; global_llm=4693ms; compose=0ms
- **Sure**: 14866.3 ms
- **API Response Time**: 14808.9 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar:
- Kurum içi yatay geçiş, aynı üniversite içinde gerçekleşirken; kurumlar arası yatay geçiş, farklı üniversite arasında gerçekleşir.
- Yatay geçiş başvurusunda bulunacak öğrencinin, geçmek istedikleri programın eşdeğer program olması ve en az 2,80 genel not ortalamasına sahip olması gerekir.
- Kurum içi yatay geçiş başvurusunda, öğrencinin kayıtlı olduğu kurumdan disiplin cezası almadığı ve akademik olarak temiz olunmalıdır.
- Kurumlar arası yatay geçiş başvurusunda, aynı puan türündeki programlara geçiş için genel not ortalamasının %60’ı ve merkezi yerleştirme puanının %40’ı; farklı puan türlerinde ise genel not ortalamasının %50’si ve merkezi yerleştirme puanının %50’si dikkate alınır.
- Yatay geçiş başvuruları, öğrencinin akademik performansı, ders yükü ve diğer faktörlerle değerlendirilir.
- Kurum içi yatay geçiş başvuruları, öğrencinin kayıtlı olduğu programdaki genel not ortalaması ve disiplin durumuna göre değerlendirilir.
- Kurumlar arası yatay geçiş başvuruları, ilan edilen süre içerisinde gerçekleştirilir ve öğrencinin akademik performansı ve disiplin durumuna göre değerlendirilir.
- Özel yetenek sınavı ile öğrenci kabul edilen diploma programlarına kurum içi yatay geçiş başvurusu yapabilmek için genel not ortalamasının en az 2.80 olması gerekir.
- Yatay geçiş başvuruları, Üniversite'nin Akademik Takvim'de derslere başlama tarihinden 10 gün önce gerçekleşatır.
- Yatay geçiş başvurularında, öğrencinin geçmek istediği programın eşdeğer program olmasına sahip olması gerekir.
- Yatay geçiş başvurusunda, öğrencinin akademik performansı, ders yükü ve diğer faktörler dikkate alınır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogre
... (406 karakter daha)
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=10932ms; dispatch=7684ms; global_llm=1955ms; compose=0ms
- **Sure**: 10970.1 ms
- **API Response Time**: 10925.3 ms
- **Kaynak Sayisi**: 8
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Benchmark, Bağıl değerlendirme sistemi ve mutlak değerlendirme arasındaki fark, öğrencilerin başarılarının hesaplanmasındaki yöntem farklıdır. Bağıl değerlendirme sistemi, öğrencilerin yarıyıl içi ve yarıyıl sonu sınavlarının öngörülen ağırlıklara göre hesaplanan ham başarı notundan oluşur. Mutlak değerlendirme ise, öğrencilerin her sınav sonucuna göre ayrı ayrı değerlendiriliyor ve notu göre hesaplanıyor.

Bağıl değerlendirme sistemi genellikle öğrenci sayısının küçük olduğu veya özel bir durum olan uzaktan eğitim öğrencileri için uygulanır. Öğrenci sayısının 10'dan az olduğu durumlarda veya dersin başarı not ortalaması %80 ve üzeri olduğu durumlarda mutlak değerlendirme kullanılır. Ayrıca, herhangi bir dersten dönem/yıl sonu sınavına girmeyen ve sınavda en az 50 puan alamayanlar başarısız sayılır.

Öğrencilerin not verilmesi de farklı yöntemlerle yapılır. Bağıl değerlendirme sisteminde, öğrenciler Tablo-1’e göre not verilirken, mutlak değerlendirme sisteminde ise öğrenciler doğrudan FF notu alan öğrencilere verilir.

Uzaktan eğitim öğrencileri için ise, lisans not ortalamasına göre adayların sıralaması yapılır ve ilan edilen kontenjanlar dikkate alınarak başarılı adaylar belirlenir. İlgili kaynaklarda belirtilen koşullar ise; mezuniyet not ortalamalarının dönüşüm hesabında adayın mezun olduğu yükseköğretim kurumundan alacağı notların 100’lük sisteme göre değerlendirilmesi, öğrencilerin notları için geçerli olduğudur.

Sonuç olarak, bağıl değerlendirme sistemi öğrencilerin başarılarının diğer öğrencilere göre karşılaştırılması temelinde ve objektif ölçülebilir kriterlere göre değerlendirilmesi temelinde olup, mutlak değerlendirme ise öğrencilerin her sınav sonucuna göre ayrı ayrı değerlendirilmesi temelindedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Ka
... (385 karakter daha)
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant, google_ai/gemini-2.5-flash-lite [fallback]; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=11873ms; dispatch=9084ms; global_llm=1562ms; compose=0ms
- **Sure**: 11910.1 ms
- **API Response Time**: 11869.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

Diploma eki ve transkript farklı belgelerdir. Diploma eki, bir öğrenciye diploma ile birlikte verilen ve eğitim ve derecesinin açıklığı sağlayan belgedir. Diploma eki, transkript yerine kullanılabilir. Buna göre, diploma eki transkript yerine kullanılabilir. Diploma eki, öğrencinin eğitimini tamamlamasıyla birlikte ve diploma verilmeden önce verilebilir. 

Diploma ekisinin amaçlarından biri, uluslararası alanda daha kolay anlaşılabilirlik sağlamasıdır. Ayrıca, diploma eki, transkriptin yerini alabilir, ancak transkriptin bazı özellikleri de vardır. Örneğin, transkript, derslerin detaylı bilgilerini sağlar ve notların olduğu bir çizelgedir. Diploma eki, öğrencinin eğitimi ve derecesini gösterir ancak transkript gibi detaylı değildir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=2957ms; dispatch=1609ms; compose=0ms
- **Sure**: 2984.6 ms
- **API Response Time**: 2953.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Her iki durumda da kayıt dondurma ile kayıt yaptırmamak arasındaki fark, kayıt dondurma durumunda öğrencilerin önemli mazeretlerinin veya eğitim öğretime katkıda kaydı durdurulan dönemin veya sürenin hesabında dikkate alınmayacakken, kayıt yaptırmamış öğrencilerin ders kaydını yapmadığı takdirde öğrenimine devam etme hakkı yoktur.

Kayıtlı oldukları üniversitede öğrenimlerine devam edebilirler.

- 18/8/2012 tarihli ve onaylanan belge.

Ön-Lisans ve Lisans Eğitim-Öğretim Yönetmeliği (MADDE 10)
- 14/7/2019, 1/12/2020 tarihli ve onaylanan belge.

Ön-Lisans ve Lisans Yönetmeliği (MADDE 10)

Sık Sorulan Sorular
- Ek Madde 1 (Merkezi Yerleştirme Puanı) ile yatay geçiş başvurusu yapılabilecek durumda olduğu açıklığa kavuşturulmuştur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=2014ms; dispatch=1967ms; compose=0ms
- **Sure**: 2041.5 ms
- **API Response Time**: 2009.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Ders Kaydı Processi

Öncelikle öğrenci bilgisine girerek öğrenci bilgilerini güncellemeli, ardından kaydını tamamlamalı ve danışman onayı almalıdır.

Adımlar:

1. Öğrenci Bilgi Sistemi'ne (OBS) giriş yaparak öğrenci bilgileri güncellenmelidir.
2. Ders seçimini tamamlayan öğrenciler, akademik takvimde belirtildiği şekilde "Öğrenci Bilgi Sistemi" üzerinden ders kaydını yapmalıdırlar.
3. Ders seçimi tamamlanan öğrenci, akademik takvimde belirtildiği süre içerisinde akademik danışmanıyla iletişime geçerek ders seçimini onaylatmalıdırlar.
4. Ders kaydı, akademik takvimde belirtilen süre içinde tamamlanması gereklidir.
5. Ders kaydında, öğrenciler eksik ders alarak dönem uzatmamak için her dönem başında müfredat durum kontrolü yapmalıdırlar.

İlgili Bilgiler:

* Akademik takvimde belirtilen süre içinde ders kaydını yapan öğrenciler, o dönemde öğrenimlerine bağlı kalmalıdır.
* Ders kaydını yaptırmayan öğrenciler, o dönemde öğrenimlerine bağlı kalmayarak o dönemde öğrenimlerine bağlı kalmamasını sağlayarak, bir sonraki yarıyılda tekrar kayıt yaptırabilirler.
* GANO'su 1,80-2,49 arası olan öğrenciler için

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=1464ms; dispatch=1408ms; compose=0ms
- **Sure**: 1490.6 ms
- **API Response Time**: 1461.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Başvuru süreci, süresi ve olası sonuçları şunlardır:

- Başvuru süresi: 15 gün.
-Başvuru yapılır: Fakülte/yüksekokula yazılı olarak.
- İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz.
- Yönetim Kurulu kararı: Kesindir (15 gün içerisinde karara bağlanır).

- 15 gün: İtiraz süresi ve başvuru süresi (Kaynak 1, 2),
- Kesindir: Yönetim Kurulu kararı (Kaynak 1)

- Kaynak 2 (yonerge_ders_yeterlilik_sinavi_uygulama.pdf) - Güven: yuksek
- Kaynak 3 (ön_lisans_ve_lisans.pdf) - Güven: yuksek
- Kaynak 4 (yonetmelik_onlisans_lisans_egitim_ogretim.pdf) - Güven: yuksek
- Kaynak 5 (yonetmelik_onlisans_lisans_egitim_ogretim.pdf) - Güven: yuksek

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_ders_yeterlilik_sinavi_uygulama.pdf
- Belge: yüzde_on_başarı_değerlendirme_yönergesi.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/6
  - [x] ders
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [x] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=14769ms; dispatch=7773ms; compose=0ms
- **Sure**: 14799.6 ms
- **API Response Time**: 14762.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Mezuniyet için gereken koşulların listesi:
- Önlisans ve lisans diplomaları için: öğrenci eğitim-öğretim programında yer alan bütün şartları yerine getirerek mezuniyet hakkı kazanmış olmalıdır.
- Yüksek lisans, doktora ve sanatta yeterlilik diplomaları için: öğrenci ilgili enstitü müdürü ile Rektör tarafından imzalanarak hazırlanmış olmalıdır.

İlişik kesme sürecinde göz önünde bulundurulması gereken koşullar:

1. Dışlama cezası almış öğrenciler: Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre yükseköğretim kurumlarından çıkarma cezası almış olanlar, kendi istekleriyle kaydını sildiren öğrenciler ile ilgili enstitü tarafından bağlantı kesilir.
2. Dört yıldan fazla katkı payı ve öğrenim ücreti ödemeyen öğrenciler: Dört yıl üst üste katkı payı ve öğrenim ücreti ödemeyen öğrencilerin ilgili biriminin teklifi ve Senato'nın kararı ile YÖK'ün onaylaması halinde, öğrenci ile Üniversite arasında bağlantı kesilir.
3. Ders sayısını bire indiremeyen öğrenciler: 8. Maddenin 3. ve 4. fıkraları kapsamındalerden başarıyı sağlayamayan öğrencilerin programa ilişikleri kesilir.

Bu koşulların gerçekleşmesi halinde, öğrencinin programa ilişkin bağlantısı kesilir.

- [Kaynak 2: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf | Guven: yuksek]
- [Kaynak 3: ön_lisans_ve_lisans.pdf | Guven: yuksek]
- [Kaynak 4: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf | Guven: yuksek]
- [Kaynak 5: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf | Guven: yuksek]

Bu bilgiler doğrultusunda, ilişkisel bağlantının kesilme süreci adım adım açıklanmaktadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=8973ms; dispatch=7684ms; compose=0ms
- **Sure**: 9004.9 ms
- **API Response Time**: 8968.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, 1. Diplomamı kaybettim:
- Diplomamı tekrar düzenletebilmek için dilekçe ile başvurmalısınız.
- Dilekçe, mahkeme kararınıza dayalı nüfus kaydı değişikliği olması durumunda; mahkeme kararı, diploma ücretini yatırdığını gösteren banka dekontu, kimlik fotokopisi ve dilekçe ile başvurulmalı.
- Bu durum [Kaynak 1: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf | Guven: yüksek] MADDE 18- (1) subsectionuna göre düzenlenecek diploma, yenisi düzenlenerek size verilecektir.

2. E-devlette mezuniyet bilgilerim görünmüyor:
- E-devlet üzerinden alınan belgelerde onay şartı aranmayacaktır. 
- [Kaynak 3: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf | Guven: yüksek] kaynakta bu hüküm bulunmakta, ancak bu, sorunuzun tüm yönlerini karşılamamaktadır.

Bilgiye ulaşmak için, diplomanızı tekrar düzenlemek için [Kaynak 1: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf | Guven: yüksek] ve e-devlet üzerinden mezuniyet bilgilerinizin görünmemesi için [Kaynak 3: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf | Guven: yüksek] kaynaklarını tekrar gözden geçirmelisiniz.

Bu konuda elimdeki kaynaklarda tam anlamıyla net bilgi bulunmamamaktadır (e-devlet üzerinden mezuniyet verileri görülmeyen durum için).

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
```

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs', 'academic_programs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [x] %40
  - [ ] %60
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=factual
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=4660ms; dispatch=1240ms; compose=0ms
- **Sure**: 4698.0 ms
- **API Response Time**: 4655.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı değildir. Ancak, bu derslerin dönem içi değerlendirme, başarıya etkisi uzaktan eğitimde %40'tan fazla olamaz.

KAYNAK DOGRULAMA Bilgisi:
Soru ile ilgili direkt bilgisi olan kaynak dosyaları: uzaktan_karma_eğitim_yönergesi.pdf, yonerge_uzaktan_karma_egitim.pdf, lisansüstü_eğitim_ve.pdf

Bu kaynak dosyalarından elde ettiğimiz bilgiler:
- Tüm sınavların yüz yüze yapılması esastır (uzaktan_karma_eğitim_yönergesi.pdf, yonerge_uzaktan_karma_egitim.pdf)
- Uzaktan verilen dersler için dönem içi değerlendirme, başarıya etkisi, uzaktan eğitimde %40’tan fazla olamaz (uzaktan_karma_eğitim_yönergesi.pdf, yonerge_uzaktan_karma_egitim.pdf)
- Lisansüstü programlarda uzaktan eğitim teknolojileri kullanarak sınavlar yapılabilir (lisansüstü_eğitim_ve.pdf)

Bu bilgiler ışığında, Bilgisayar Muhendisligi bolumu/programi icin uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesinin yüz yüze derslerden farklı olmadığı sonucuna varabiliriz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
- Belge: yonerge_uzaktan_egitim_onlisans_lisans.pdf
- Belge: lisansüstü_eğitim_ve.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=1429ms; dispatch=1328ms; compose=0ms
- **Sure**: 1459.3 ms
- **API Response Time**: 1424.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Evet, sınava kopya çekilmesinin cezası vardır. İşte bu cezalar:
- Kopya çekilmesiyle ilgili cezalar, 15 dakika içinde veya sınav görevlisinin izni almadan sınav salonundan çıkılması durumunda geçerli olur.
- Sınav zamanı içinde cep telefonu kullanılmasına izin verilmeyen bir öğrenci, sınav görevlisinin izni almadan veya sınav zamanı içinde cep telefonu ile ilgilenen öğrenciye kopya muamelesi yapılır.

Diğer taraftan, 15 dakika içinde sınav görevlisinin izni almadan sınav salonundan çıkılması durumunda da kopya muamelesi yapılır. İşte bu cezalardan ötürü öğrenci hakkında yapılan disiplin sürecinde öğrencileri haklı çıkaran bir durum bulunmamakta.

Disiplin süreci, Fakülte Dekanlığı/Yüksekokul Müdürlüğü veya Meslek Yüksekokulu Müdürlüğü tarafından Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği hükümlerine göre yürütülür.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=3002ms; dispatch=2047ms; compose=0ms
- **Sure**: 3050.3 ms
- **API Response Time**: 2987.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, 1. Kaydını Sildirme ve Üyelik Kesme:

Kaydını sildirme talebi yazılı olarak üniversiteye iletiniz. Üniversite tarafından kaydınız silinecekse, sizin ile ilişiğiniz kesilecektir.

2. Dört Yıl Üst Üste Kayıt Yenilememen ve Ücret Ödememe:

Dört yıl üst üste kaydınızı yenilememen veya katkı payı ve öğrenim ücreti ödememenin nedeni halinde, ilgili birimlerin teklifi ve Senato kararı ile YÖK'ün onaylaması durumunda, üniversite ile ilişiğiniz kesilebilecektir.

3. Ders Kaydında Problemler:

Ders kaydında sorunlar oluşursa, öğrenci bilgi sistemi üzerinden ders kaydını yapmanızı sağlayacaktır. Ancak, ders kaydını yapmayan öğrenciler, akademik takvimde belirlenen süre içinde ders kaydını yapmamanın cause olduğu öğren-imine devam etme hakkı kaybedecektir.

4. Yazılı Talep ve Yeniden Yerleştirme:

Kaydınızı sildiren öğrenci, ÖSYM tarafından yeniden yerleştirilmediği veya Üniversite tarafından yapılan ölçme ve değerlendirme sonucunda kayıt hakkı kazanmayan öğrenciler, Üniversiteye tekrar kaydolamayacaktır.

5. Dikkat Edilmesi Gereken Hususlar:

Üniversitesinden ayrılacak olan öğrenciler, Üniversite ile ilişiği kesmeleri halinde, öğrenci bilgi sistemi üzerinden üniversiteye giriş yapamayacaktır. Bu nedenle, üniversite ile ilişiğin kesilmesi talebiyle üniversiteye yazılı olarak talepte bulunmak yerinde olacaktır.

- Üniversiteden ayrılmak için öğrenci bilgi sisteminden kaydını silme talebi vermek gereklidir.
- Dört yıl üst üste kaydını yenilememen veya katkı payı ve öğrenim ücreti ödememenin nedeni halinde, ilgili birimlerin teklifi ve Senato kararı ile YÖK'ün onaylaması durumunda, üniversite ile ilişiğiniz kesilebilir.
- Ders kaydını yapmayan öğrenciler, o dönemde öğrenimine devam etme hakkı kaybeder.
- Kaydını sildiren öğrenci, ÖSYM tarafından yeniden yerleştirilmediği veya Üniversite tarafından yapılan ölçme ve değerlendirme sonucu kayıt hakkı kazanmayan öğrenciler, Üniversiteye tekrar kaydolamayacaktır.

- [Kaynak 2: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pd
... (560 karakter daha)
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] kayıt
  - [ ] yenileme
  - [x] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=1313ms; dispatch=1267ms; compose=0ms
- **Sure**: 1348.2 ms
- **API Response Time**: 1308.9 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Evet, 1 yılın ardından ders kaydını yapabilirsin. Ancak akademik takvimde belirtilen süre içinde yapması gerekiyor. 

Benchmark: 1 yıl, akademik takvimde belirtilen süre

Ders kaydını nerede yapabilirim? 
internet ortamında ubys.omu.edu.tr adresine giriş yaparak, interneti bulunan her yerden yapabilirsin.

Akademik takvimde belirtilen süre içinde ders kaydını yapmayan öğrenciler, o dönemde öğrenimlerine sayılabilir mi? 
Evet, akademik takvimde belirtilen süre içinde yapmayanlar, o döneme sayılabilir. 

Güz yarıyılı ders kaydı yaptırmadım, bir sonraki yarıyıl (bahar) ders kaydı yapabilir miyim? 
Evet, bir sonraki yarıyıl ders kaydı yapabilirsin. 

Danışman onayına sistem üzerinden gitme zorunluluğu var mı? 
Hayır, danışman onayına öğrenci bilgi yönetim sistemi üzerinden gitme zorunluluğu yok.

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

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] danışman
  - [x] bölüm
  - [x] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=2748ms; dispatch=1874ms; compose=0ms
- **Sure**: 2786.7 ms
- **API Response Time**: 2738.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Evet, ders kayıt işlemlerine başlamadan önce ders notlarınızı sisteme girmen zorunludur. Ders kaydınızı akademik takvimde belirtilen süre içinde yapman gerekir. Bu süreleri Öğrenci İşleri Daire Başkanlığı WEB sayfasından bulabilirsin.

Daha önce aldığım ders/dersler için Dekanlığa/Müdürlüğe muafiyet dilekçesi verdim, muafiyet başvurum sonuçlanıncaya kadar bu derse kayıt yaptırıp devam etmeli miyim?
Muafiyet başvurun sonucu bekliyorken, danışmanınız ile birlikte almanız gereken derslere kaydınızı yaptırabilirsiniz. Ancak muafiyet başvurun sonuçlandığında, muafiyet onaylanırsa, danışman onayını almanız gerekir.

Danışman sayağıma ulaşamaz ve ders kaydım onaylatamazsam ne yapmam gerekir?
Bu durumdaysan, bölüm başkanınıza ulaşamazsanız Dekan/Müdürünüze durumu bildirerek akademik takvimde belirtilen sürede danışman onayını alınız. Hiçbir yetkiliye ulaşılamadığınız takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yoluyla iletebilirsiniz.

Ders kayıt aşamasında en çok hangi hususlara dikkat etmem gerekir?
Ders kaydında üç önemli hususa dikkat etmeniz gerekir: Eksik ders alarak dönem uzatmamak için her dönem başında müfredat durum kontrolü, akademik takvimde belirtilen süre içinde kaydın tamamlanması ve danışman onayı.

- Kaynak 2: sık_sorulan_sorular.txt
- Kaynak 3: sık_sorulan_sorular.txt
- Kaynak 4: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
