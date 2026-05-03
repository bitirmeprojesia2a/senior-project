# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-23 17:46:11
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 96.0% |
| Anahtar Bilgi Kapsami | 70.0% |
| Temiz Kalite Orani | 96.0% |
| Ortalama Sure | 11299.9 ms |
| Medyan Sure | 10445.8 ms |
| Intent Analizi Aktif | 0/25 |
| Force LLM Sentez | 0/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 3/4 | 13825.5 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 3/3 | 18013.6 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 2/4 | 7304.2 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 4/4 | 9004.8 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 11606.3 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 10596.1 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 8556.9 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 11377.4 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 5/5 | 15301.4 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 3/4 | 11717.3 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 3/4 | 9898.7 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 4/4 | 7401.1 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 11701.3 | uydurma_riski |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 4/4 | 16349.9 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 2/3 | 9568.5 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 18453.1 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 4/5 | 7391.3 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 2/4 | 8215.3 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 3/6 | 10445.8 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 8178.1 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 2/5 | 20466.0 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 12289.0 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 9482.4 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 7202.4 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 2/3 | 8152.2 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs', 'announcement'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] üç hafta
  - [ ] dilekçe
  - [x] komisyon
  - [x] derslere devam
- **Sure**: 13825.5 ms
- **Kaynak Sayisi**: 12

**Yanit:**
```
Benchmark, Yatay geçişle gelen bir öğrenci, muafiyet başvurularını her eğitim-öğretim döneminde derslerin başlamasından itibaren ikinci haftanın sonuna kadar yapmalıdır. Başvuruların sonuçlanmasının ardından, öğrenciler ilgili birim tarafından oluşturulan ders yeterlik ve intibak komisyonu tarafından değerlendirilir. Derslere devam edilebilir mi?

Evet, öğrenciler muafiyet başvurularının sonuçlanmasını beklemek üzere derslere devam etmesi önerilir. Ancak akademik takvime bağlı olarak kayıt yenileyen öğrencilerin bu süre içinde mağdur olmaları önlenmelidir.

Detaylar:

- Yatay geçişle gelen öğrenciler, kayıt yaptırdıkları öğretim yılının en geç 3. haftasının sonuna kadar muafiyet başvurularını yapabilir.
- öğrenciler muafiyet başvurularının sonuçlanmasını beklemek üzere derslere devam etmesi önerilir.
- Disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez.
- Yatay geçişle gelen öğrenciler, muafiyet başvurularını her eğitim-öğretim döneminde derslerin başlamasından itibaren ikinci haftanın sonuna kadar gerçekleştirebilirler.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Duyuru kaydi: 2025-2026 Eğitim Öğretim Yılı Bahar Yarıyılı Yatay Geçiş Yedek sonuçları (https://www.omu.edu.tr/tr/icerik/duyuru/2025-2026-egitim-ogretim-yili-bahar-yariyili-yatay-gecis-yedek-son
... (367 karakter daha)
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
- **Sure**: 18013.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sorusuna ilişkin ayrıntılı yanıtı veriyorum:

1. Yönetmelik On Lisans ve Lisans Eğitimi Yönetmeliği'nin 8. maddesinde yazıyor ama daha spesifik bilgi için diğer kaynaklara bakmamız gerekecektir. Yine de birinciden bahsetmek gerekiyor, bu maddeye göre ön lisans ve lisans düzeyindeki öğrenciler en fazla yedi yıl süreyle eğitim görebilirler.

Yanıtlar:

- "Stajımı tamamlamış olmam gerekmez mi tek ders sınavına girip?" Yanıt: Evet, staj dersini tamamlanmış olmak gerekli değildir. Kaynak: [Kaynak 1: sık_sorulan_sorular.txt] "Tek ders sınavına bir dersten başarılı sayılabilmek için Yarıyıl/Yıl Sonu Sınavı Alt Limiti var mıdır?" Yanıt: Evet, 100 puan üzerinden 50’nin altında not alan öğrenciler başarısız sayılır. Kaynak: [Kaynak 2: sık_sorulan_sorular.txt] "Tek ders sınavı sonucunda hangi not aldığımda başarılı sayılabilirim?" Yanıt: Ara sınav şartı aranmaksızın en az CC alırsanız başarılı sayılırsınız. Kaynak: [Kaynak 4: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf] 
- "Minimum not kaç?" Yanıt: 50. (Ara sınav şartı aranmaksızın 100 üzerinden 50’nin altında not alan öğrenciler başarısız sayılır.) Kaynak: [Kaynak 4: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf]

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
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
- **Sure**: 7304.2 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Soru: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

Yanıt: Devam zorunluluğunuz değişmez. Zira yurutmekle görevli olduğunuz belge baglaminda devamsizligina dair cozum yontemleri "devam koşulu olmayan derslerde dönem içi değerlendirmelerine" ilgili olarak yer almaktadir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yaz_okulu_eğitim_öğretim.pdf
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
- **Sure**: 9004.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Soru 1: Pedagojik formasyon dersleri transkripte dahil ediliyor mu?

YANIT: Evet, pedagojik formasyon dersleri transkripte dahil edilecektir. [Kaynak 1: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt]

Soru 2: Mezuniyet ortalamasına etkisi var mı?

YANIT: Evet, pedagojik formasyon dersleri mezuniyet ortalamasına dahil edilecektir. [Kaynak 1: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt]

Soru 3: Diplomada nasıl bir ibare yer alacak?

YANIT: Diplomaların arkasına “Pedagojik formasyon eğitimini tamamlamıştır.” ifadesi yazılacaktır. [Kaynak 1: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt]

Soru 4: Pedagojik formasyon derslerinin alınması zorunlu mudur?

YANIT: Hayır, pedagojik formasyon dersleri seçmeli derslerdir. [Kaynak 2: lisans_pedagojik_formasyon_derslerine_ilişkin.pdf]

Soru 5: Son sınıf öğrencisi olup kayıtlı olduğu programın mezuniyet için gerekli tüm şartlarını yerine getiren öğrenciler, pedagojik formasyon eğitimi uygulamasından yararlanabilecekler mi?

YANIT: Evet. [Kaynak 4: uygulama_esaslari_lisans_pedagojik_formasyon.pdf]

Ekteki kaynaklar da belirtildiği üzere:
- Pedagojik formasyon derslerinin sayısı 40 AKTS'den oluşur ve bu eğitim öğrencinin lisans programından mezuniyeti için alması gereken asgari AKTS şartının dışında değerlendirilir.
- Bu dersler, öğrencilerin ilgili döneme ait genel ağırlıklı not ortalaması (GANO) hesabına dahil edilir.
- Pedagojik formasyon derslerinin yüz yüze yapılması esastır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt
- Belge: lisans_pedagojik_formasyon_derslerine_ilişkin.pdf
- Belge: uygulama_esaslari_lisans_pedagojik_formasyon.pdf
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
- **Sure**: 11606.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, İkamet İzni ve Öğrenim Ücreti Üzerine Bilgi:

Öğrenim Ücreti
Uluslararası öğrenci olarak öğrenim ücretimi, Ziraat Bankası'ndan öğrenci numaranızla yatırmalısınız. Şehit/Gazi çocuğuyken, öğrencilerin öğrenim ücretinden muaf olduğu unutulmamalıdır.

İkamet İznine İlişkin Bilgiler
- İlk olarak, ikamet izni için Göç İdaresi Başkanlığı'ndan vize muafiyeti başvurusunda bulunmanız gerekmektedir.
- İkamet izni başvurusu tamamlanmasının ardından, uluslararası öğrenci bölümlerinde ikamet izni belgenizi teslim etmeniz gerekecektir.
- İkamet adres değişikliği yaptığınızda ise, bulunduğunuz yerin mahalli-resmi makamlarına 2 iş günü içinde bildirmelisiniz.

Dikkat Edilmesi Gereken Bilgiler
- Öğrenim ücretini öğrenci portalından ön kayıt yaptırmak suretiyle ya da öğrenci işleri daire başkanlığı hesabına yatırmalısınız.
- Uluslararası öğrenci olarak kayıt yaptıranların, Üniversite'ne ödemiş oldukları öğrenim ücretini yatırmak suretiyle öğrenimine devam ettikleri bilinmelidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
- Belge: ön_lisans_ve_lisans_programları.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
- Veritabani kaydi: ogrenim ucreti tablosu
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
- **Sure**: 10596.1 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Benchmark, Sorunuzun cevabinin detaylarına göre, ÇAP başvuru şartları ve harç borcu ödeme bilgileri aşağıdaki kadardır:

ÇAP programına başvurmak için en az 4,00 üzerinden 3,00 not ortalaması, başvuru alınacak yıla kadar dersleri almış ve tamamlamış olma, başvuru alınan yarıyılın başlarından/sonlarında öğrenci listesinde en az ilk %20'inde yer almış olmak, dört yıllık programlarda ana dal diploma programının en erken 3., en geç 5. yarı yılında başvurulabilir olması gerekir. 

Başvuru, ÖİDB'nin internet sayfasında açılan ilgili link üzerinden elektronik olarak yapılır.

Harç borcu ödemesi ilişkin kesin bilgi alınamamaktadır. Ödenek ve belgeye dayanarak ise öğrenci, mühendislik fakültesinde kayıtlı bir öğrenci olmalıdır. Yılık öğrenim ücreti 2.397,00 TL, dönemlik öğrenim ücreti ise 1.198,50 TL'dir.

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
- **Sure**: 8556.9 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Ders Kaydını Yapmak İçin Adım-by-Adım Rehber:
 
- Kayıt yenileme döneminde harç ücretinizi yatırdıktan sonra, öğrenci bilgi sistemi üzerinden ders seçmelisiniz. 
- Bu işlem akademik takvimde belirtilen süre içinde gerçekleştirilmelidir. 
- Belirtilen süre dışında kaydın tamamlanmaması öğrencinin o dönemde öğrenimlerine devam etme hakkını kaybettirir.
- İlgili birim yönetim kurulunca mazeretin haklı ve geçerli belirlenmesi durumunda, ders kaydı başvurunuz dikkate alınır.
- Akademik takvimde belirtilen süre içinde ders kaydınızı tamamladıktan sonra, danışman onayını muhakkak yaptırmalısınız.
 
Yapmanız gereken son aşama; danışman onayından sonra başarılı olduğunuz dersleri müfredatınızla karşılaştırmanızdır. Bu, her kayıt dönemi başında yapılması gereken bir işlem olduğu unutulmamalıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Sure**: 11377.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Sorumuzun dogrudan yaniti: Evet, bursunuz kesilebilir.
 
Yeni üniversiteye geçiş yaptığınızda, bursunuzu devredebilir veya kesilebilir. Bursun devri veya kesilmesi gibi durumlar için ilgili üniversite ile iletişim kurulması gerekmektedir.

Kesin bilgi için, burs aldığınız kurumla iletişim kurmanız gerekmektedir. Gerekli koşullar karşılanmışsa, yeni üniversiteye geçiş yaparak harç ödememeniz mümkündür. 

Gerekli koşullar:
- Önceki üniversitenizden mezun olamayışın ya da bursunu kaybettinizin olmaması.
- Yeni üniversitede kayıtlı programa giriş için gereken genel not oranının karşılanması (en az 2.80 veya 72 oranını).
- Yaptığınız yatay geçiş başvurunun başarı ile tamamlanması.

Talebiniz kabul edilirse, harç ücreti yatırmaya gerek yoktur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
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
- **Sure**: 15301.4 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Benchmark, Katkı Payı ve Ek Süre Hakkı Sorununda Bilgiler

4. sınıf öğrencisi olarak, program süresinin 1 yıl aştığını ve ek süre hakkının olup olmadığını soruyorsunuz. İşte ilgili bilgiler:

* Ek Süre Hakkı: Öğrenciler, program süresini aştığı için ek süre hakkından yararlanamaz. Öğrenim süresinden sayılma veya katkı payı ile ilgili genel kurallar mevcut, ancak program süresinin aşılması ile ilgili spesifik bilgi bulunamadı.
* Katı Payı: Program süresini aştığınızda, katkı payını/öğrenim ücretini değişim programında geçen süre için öğrenci kayıtlı olduğu yükseköğretim kurumuna öder. Bu süre öğretim süresine dahildir.
* Tıp Fakültesi Yönetim Kurulunun Kararı: Tıp Fakültesi Yönetim Kurulu kararı ile en fazla bir yıla kadar izin verilebilir.
* Öğrenim Süresini Tamamlama: Öğrenciler, ders, uygulama, staj ve sınavlara katılabilirler; ancak bunların dışındaki öğrencilik haklarından yararlanamazlar.

Bilgi Kaynağı: Ön lisans ve lisans düzeyindeki program süresinden sayılır ile ilgili madde olan ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf belgesine göre,

- Önlisans ve lisans düzeyinde öğrenim gören öğrencilerin öğrenimlerini tamamlamaları için tanınan azami süreler; bir yıl süreli yabancı dil hazırlık sınıfı hariç kayıt olduğu programa ait derslerin verildiği dönemden başlamak üzere her dönem için 4, 7 ve 9 yıl olarak gösterilmiştir.
- 4. sınıfta olan bir öğrenci program süresini 1 yıldan fazla aştığında, ek süre hakkından yararlanma hakkı yoktur.

Bu bilgileri kullanarak, sonuç olarak: Ek süre hakkınız yoktur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş
... (219 karakter daha)
```

### Q10: Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs', 'announcement'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [x] tekrar
- **Sure**: 11717.3 ms
- **Kaynak Sayisi**: 13

**Yanit:**
```
Benchmark, Devamsızlıktan kaldığınız bir dersin bütünleme sınavına girebilir misiniz? Giremiyorsanız bu dersi ne zaman tekrar alabilirsiniz?

Evet, devamsızlıktan kaldığınız bir dersin bütünleme sınavına girebilirsiniz. Bütünleme sınavına girebilmek için mezuniyetiniz için tek dersi kalan öğrencilerin bütünleme sınav notlarının ilanını takip eden beş iş günü içinde dilekçe ile başvurması gerekir. Bu sayede devamsızlık sürenizin bir dersin o dönemdeki/yıldaki toplam saatinin %50'sini aşmamış olması yeterlidir.

Giremiyorsanız, tekrarlamak istediğiniz dersi/bloğu veya klinik uygulamayı tekrar alabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: bağıl_değerlendirme_yönergesi.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: tıp_fakültesi_tıp_doktorluğu_programı.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Duyuru kaydi: 📢 Girişimcilik ve Yenilikçilik Dersinin Derslikleri Hakkında (https://bil-muhendislik.omu.edu.tr/tr/haberler/girisimcilik-ve-yenilikcilik-dersinin-derslikleri-hakkinda)
- Duyuru kaydi: İngilizce II ve İleri İngilizce II Derslerinin Mazeret Sınavları Hakkında (https://bil-muhendislik.omu.edu.tr/tr/haberler/ingilizce-ii-ve-ileri-ingilizce-dersleri-mazeret-sinavlari-hakkinda)
- Duyuru kaydi: TBFİZ124 Fizik II ve TBFİZ122 Fizik II Dersini Alan Öğrencilerin Dikkatine! (https://bil-muhendislik.omu.edu.tr/tr/haberler/duyuru-tbfiz124-fizik-ii-ve-tbfiz122-fizik-ii-dersini-alan-ogrencilerin-dikkatine)
```

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] öğrenim ücreti
  - [ ] gerek yok
  - [x] yönetim kurulu
  - [x] sayılma
- **Sure**: 9898.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Soru: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondumak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

Cevap: 
- Kayıt dondurma isteğinizin ilgili yönetim kurulunca kabul edilmesi durumunda öğrenim ücretinizi yatırmak zorunda değilsiniz.
- Kayıt dondurduğunuz süreler eğitim-öğretimden sayılmaz.
- Kayıt dondurma ile kayıt yaptıramamak arasında bir fark vardır; kayıt dondurma ile kayıt yaptırmak arasındaki fark öğrencinin öğrenimine devam edebilmesi ve sınavlara girebilmesidir.

Detaylar:
- Öğrenci katkı payı/öğrenim ücreti ödemesi, akademik takvimde belirtilen süreler içinde her eğitim-öğretim döneminde/yılında yapılır.
- Öğrenci katkı payı/öğrenim ücreti, ilgili mevzuatta belirlenen tutarla ödenir (yılık ücret: 2.397,00 TL, dönemlik ücret: 1.198,50 TL).
- Kayıt dondurma isteğinizin ilgili yönetim kurulunca kabul edilmesi, öğrencinin öğrenim ücretini yatırmasına gerek duyurmayacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] transkript
  - [x] Ek Madde
  - [x] başvuru yapabilir
  - [x] GANO
- **Sure**: 7401.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Soru: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

Cevap: Evet, hazırlık sınıfı okuyan ve Ek Madde-1 kapsamında merkezi yerleştirme puanı ile yatay geçiş başvurusu yapmak isteyen adaylar, transkriptleri olmadan da başvuru yapabilirler. Ek Madde-1 kapsamında yapılan yatay geçiş başvurularında öğrencinin GANO'su değerlendirme aşamasında etkili değildir. (Kaynak 4: sık_sorulan_sorular.txt)

Lisans programlarına yatay geçiş yapıp geri dönme hakkını kullanmak isteyen öğrencilerin, ilgili akademik birimlere dilekçe ile başvuru yapması gerekmektedir. Bir dönemde en fazla 2 yatay geçiş başvurusu yapılabilir. (Kaynak 1: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf)

Birden fazla üniversiteye yatay geçiş başvurusu yapabilir miyim? Farklı üniversitelere yatay geçiş başvurusu yapabilirsiniz. (Kaynak 4: sık_sorulan_sorular.txt)

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
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Sure**: 11701.3 ms
- **Kaynak Sayisi**: 5
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Benchmark, Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar;

Kurum içi yatay geçiş için;
- Öğrenci, aynı üniversitede aynı düzeyde diploma programlarına geçiş yapmakta;
- Genellikle aynı birimdeki programlar arası geçiş yapılmaktadır;
- Başvuru için öğrencinin genel not ortalamasının en az 2.80 olması gerekir;
- Disiplin cezasının yoksa bu durumunu belgelemesi gerekir;
- Kayıt dondurulmuş ise bu durumu belgelendirmesi gerekir.

Kurumlararası yatay geçiş için;
- Öğrenci, farklı bir üniversitede aynı düzeyde diploma programlarına geçiş yapmakta;
- Genellikle aynı düzeyde diploma programlarına geçiş yapılmaktadır;
- Başvuru için öğrencinin kayıtlı olduğu programda bitirmiş olduğu dönemlere ait genel not ortalamasının; 4'lük sistem kullanan üniversiteler için en az 2.80, 100'lük sistem kullanan üniversiteler için en az 72 olması gerekir;
- Disiplin cezasının yoksa bu durumunu belgelemesi gerekir;
- Kayıt dondurulmuş ise bu durumu belgelendirmesi gerekir.

Yatay geçiş başvuruları;
- Disiplin cezası almış öğrencilerin başvuruları kabul edilmez;
- Başvuru esnasında disiplin cezası almadıklarını belgelemeleri şarttır;
- Öğrenci kayıt dondurmuş ise yatay geçiş başvurusu sırasında bu durumu belgelendirmesi gerekir.

Yatay geçiş kontenjanları;
- ÖSYM Kılavuzunda öngörülen öğrenci kontenjanının yıllık % 15 ini geçmeyecek biçimde dönemlere bölünerek ilgili yönetim kurulunun önerisi ve Senato’nun kararı ile belirlenir.
- Yatay geçiş kontenjanları, ilgili diploma programının son dört yıla ait taban puanları ve başvuru şartları, son başvurunun kabul edileceği günden en az 15 gün öncesinde üniversite web sayfasında ilan edilir.

Yatay geçiş başvurusunda öğrencinin merkezi sınav puanı esas alınır;
- Öğrencinin aldığı merkezi sınav puanının, yurt içindeki diğer üniversitelerin başvurulan program için geçerli olan puan türündeki en düşük taban puanından az olmaması gerekir.
- Özel yetenek sınavı ile öğrenci kabul edilen diploma programlarına kurum içi yatay geçi
... (1118 karakter daha)
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
- **Sure**: 16349.9 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Bağıl Değerlendirme Sistemi ve Mutlak Değişlendirme Arasındaki Fark
=========================

Bağıl değerlendirme sistemi ve mutlak değerlendirme sistemi arasındaki fark, notların hesaplanmasındaki approaches'tir. Bağıl değerlendirmede, öğrencinin yılları içi ve yılları sonu sınav notu hesaplanırken ağırlıklı puana yer verilir (Kaynak 1, Madde 7), mutlak değerlendirmede ise sadece yıl sonu veya tümlemer sınav notu temel alınır (Kaynak 2, Madde 23).

Hangi Öğrenci Sayısında Hangisi Uygulanır?
-----------------------------------------

- Bağıl Değerlendirme: Bağıl değerlendirmeye katılan öğrenci sayısı 10 ve altında ise öğrenci otomasyon sistemi ham başarı puanını mutlak değerlendirme yaparak harf notuna dönüştürür (Tablo-1). 11-29 öğrenci sayısında ise estudiantes'in ham başarı puanları ders ortalaması dikkate alınarak Tablo-2’ye göre nota dönüştürülür.
- Mutlak Değişlendirme: Bağıl değerlendirmeye katılan öğrenci sayısı 10 ve altında ise mutlak değerlendirme kullanılır (Kaynak 1, Madde 7).

Bağıl Değerlendirme Sistemi Uygulanır:
------------------------------------------

Bağıl değerlendirmede, uzaktan eğitim öğrencilerine uygulanır (Kaynak 2, Madde 23).

Not Hesaplaması:
-------------------

- Mutlak Değişlendirme Sistem:
 - 60 ve üzerinde not: "FF" notu
 - 60-64 arasındaki not: "CC" notu
 - 65-69 arasında not: "CB" notu
 - 70-79 arasında not: "BB" notu
 - 80-89 arasında not: "BA" notu
 - 90 ve üzeri not: "AA" notu
- Bağıl Değerlendirme Yönergesi.pdf (Madde 5)
 - Ön Lisans ve Lisans.pdf (Madde 29)
 - Uzaktan Eğitim Tezsiz Yüksek Lisans Programı Yönergesi.pdf (Madde 7)
 - Lisansüstü Eğitimi ve.pdf (Madde 23)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG

Kaynak Ozeti:
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: lisansüstü_
... (285 karakter daha)
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
- **Sure**: 9568.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Soru: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

Yanıt: Diploma eki, transkriptin aksine, kişinin takip ettiği öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek üzere verilir. Diploma eki, transkriptin yerini alamaz, ancak yurtdışında daha okunabilir ve mukayese edilebilir bir diploma, akademik güzergahının ve yurtiçinde ve yurtdışında edindiği yeti ve becerilerin tam bir tarifi, başarı ve yetilerinin nesnel ve adil değerlendirmesi, geleceğe yönelik olarak yurtdışında iş ve eğitim imkanlarına daha rahat ulaşma olanağı, iş bulma olanaklarını artırma kazanımlarını elde edebilirsiniz. 

Diploma eki, bir yükseköğretim diplomasına ek olarak verilen bir belge olarak tanımlanırken, transkript, diplomanın arkasında yer alan bilgilerin kayıtlara uygunluğu tarafından onaylanır.

Not: Belge kaynaklarından anlaşıldığı kadarıyla diploma eki, transkriptten daha spesifik bilgiler sağlar, ancak her iki belge de farklı amaçlar için kullanılır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
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
- **Sure**: 18453.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Kayıt dondurma ile kayıt yaptırmamak arasındaki farklar ve kayıt yaptırmazsa öğrencilik haklarındaki etkileri aşağıda açıklanmıştır:

Kayıt dondurma, öğrencilerin belirli bir süre için üniversiteden uzaklaşmasına izin verir. Bu durum, öğrencinin ilgili akademik takvimde belirlenen süre içerisinde ders kaydını yaptırmasına gerek olmayacaktır. Kayıt dondurulan yıl, öğrencinin öğrenim süresinden sayılacaktır.

Kayıt yaptırmamak ise, öğrencilerin bir öğrenci bilgi sistemi üzerinden alacağı dersleri seçerek derse kaydını yapmaları durumunu belirtir. Bu durum, öğrencinin ilgili akademik takvimde belirlenen süre içerisinde ders kaydını yaptırmasına gerek vardır ve öğrencinin kaydı yapılmış olsa bile, öğrenimine devam etmesi için kayıt yapması gerekecektir.

Her iki durumda da öğrencinin öğrencilik hakları etkilenir. Kayıt donduran bir öğrencinin öğrenim süresi uzayacak, kayıt yapılmayan bir öğrenci ise öğrenimine devam edemeyerek öğrencilik haklarından yararlanamayacak.Örneğin, uluslararası öğrenciler için kayıt yapılan tarihler, kayıt yapılan yıl için YÖK tarafından belirlenen son kayıt tarihli ile sınırlıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: ön_kayıt_kılavuzu_başvuru_adımları.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] UBYS
  - [ ] ders seçimi
  - [x] danışman
  - [x] onay
  - [x] yoklama
- **Sure**: 7391.3 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Ders kaydı ve danışman onayının süreci hakkında sorularınıza yanıt olarak sunulan bilgiler göre yanıtlayacağım.

Ders kaydın ilk adımı, öğrenci bilgi yönetim sistemine giriş yaparak kayıt işlemini başlatmadır. Bu adımı yapabilmeniz için internetsiz kalmadan internet yoluyla ubys.omu.edu.tr adresine giriş yapmak sureti ile interneti bulunan her yerden yapabilirsiniz.

Ders kaydın ardından, öğrencinin seçmiş olduğu derslerin müfredat bilgileri ile transkriptini karşılaştırması gerekir. Başarılı oldukları dersleri müfredat ile karşılaştırdıktan sonra, danışman onay bittikten sonra öğrencinin yapması gereken bir şey daha vardır. 

Danışman onay işlemi tamamlandıktan sonra öğrenciler, kayıtlanmış oldukları dersleri tek tek kontrol etmelidir. Sizin danışman onayınıza göndermiş olduğunuz derslerden bir veya birkaçı danışmanınız tarafından listeden çıkartılmış olabilir. Bu nedenle, sınıf yoklama listesine imza atmalıdır.

Sınıf yoklama listesinde adınız yoksa, danışmanınıza veya akademik birimınıza başvurmak gerekir.

Bu konuya ilişkin olarak, aşağıdaki bilgiler mevcuttur:

- Öğrenciler, her dönem/yıl başında akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden alacakları dersleri seçerler. (Kaynak 5: ön_lisans_ve_lisans.pdf, md. 10)
- Kayıt dönemi başlamadan transkript/müfredat kontrolünü yaparak akademik takvimde tanımlanan süre içerisinde ders kaydını yapmaları gerektiği, derslere başladığında ise sınıf yoklama listesinde adları yoksa danışmanlarına uğramaları gerektiği bilgisi paylaşılmalıdır. (Kaynak 2: sık_sorulan_sorular.txt)
- Ödenek kaydı yaptırmadığınız dönemler de eğitim süresinden sayılmaktadır. Güz yarıyılı ders kaydı yaptırmadım. Bir sonraki yarıyıl (bahar) ders kaydı yaptırabilir miyim? 
(Kaynak 3: sık_sorulan_sorular.txt)
- Danışman onayını vermek için öğrencinin şahsen gelmesini zorunlu tutabilir miyim? Öğrenci bilginin yönetim sistemi üzerinden internet ortamında ders kaydını yapan öğrenci, danışman onayına sistem üzerinden g
... (812 karakter daha)
```

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] itiraz
  - [x] beş iş günü
  - [ ] dilekçe
  - [ ] bölüm başkanlığı
- **Sure**: 8215.3 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Sizlere Öncelikle OMU içinde sınav notuna itiraz edilmesi için süreci ve süreci ile ilgili bilgiler vereceğim.

SINAV SONUÇLARINA İTİRAZ PROSESİ:
- Soru 15 gün içerisinde fakülte/yüksekokuluna yazı ile itiraz edilebilir. İtirazlar 15 gün içinde birim yönetim kurulunca karara bağlanır ve karar kesindir. (Kaynak 2: yüzde_on_başarı_değerlendirme_yönergesi.pdf)

YENİDEN İNCELEME:
- Öğrenciler, sınavların bitiminde cevap anahtarının yüklenmiş olabileceği Üniversite sisteminde erişebildiği şekilde, sonuçların açıklanmasından itibaren beş iş günü içerisinde ilgili bölüme yazılı olarak başvurmak kaydıyla, sınav kağıtlarının yeniden incelenmesi talebinde bulunabilir. (Kaynak 3: yonetmelik_onlisans_lisans_egitim_ogretim.pdf)

YENİDEN İNCELEMELİK TALEPLERİ İÇİN İTİRAZ DÖNEMİ:
- Soru acikca belirtmedeyse 3 iş gunu icinde itiraz edilebilir. (Kaynak 3: yonetmelik_onlisans_lisans_egitim_ogretim.pdf)

GENEL BELGELER:
- Sınav sonuçlarına itiraz ve not düzeltme 15 gün içerisinde yapılmalıdır. İtiraz süre bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz. (Kaynak 2: yüzde_on_başarı_değerlendirme_yönergesi.pdf)
- Sınavların bitiminde cevap anahtarının bir örneği Üniversitesi tarafından hazırlanmış bir sisteme yüklenir. (Kaynak 3: yonetmelik_onlisans_lisans_egitim_ogretim.pdf)

YENİDEN İNCELEME KOMİSYONU:
- Yeniden incelemeye itiraz edildiginde, ilgili öğretim elemanı tarafından hazırlanmış cevap kağıdı dikkate alınarak sınav inceleme komisyonu tarafından incelenir. (Kaynak 3: yonetmelik_onlisans_lisans_egitim_ogretim.pdf)

YENİDEN İNCELEME KOMİSYONU İÇİN Süre:
- İşlem, en geç 3 iş günü içinde sonuçlandırılır. (Kaynak 3: yonetmelik_onlisans_lisans_egitim_ogretim.pdf)

ÖĞRETCİ İŞLERİ DİREKTÖRLÜĞÜNE GÖNDERİM:
- Notta değişiklik olması durumunda, form ilgili birimin yönetim kurulu kararıyla Öğrenci İşleri Daire Başkanlığına gönderilir. (Kaynak 3: yonetmelik_onlisans_lisans_egitim_ogretim.pdf)

YENİDEN İNCELEME DEĞERLENDİRME FORMU:
- İtiraz değerlendirme formu do
... (615 karakter daha)
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
- **Sure**: 10445.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Soru:
Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

Yanit:
Mezuniyet için gereken koşullar Önlisans ve Lisans Eğitimi Öğretimi Yönetmeliği'nde belirlenmiştir.

Mezuniyet İçin Gereken Koşullar:

- Öğrenciler, öğrenim gördüğü programda yer alan bütün şartları yerine getirerek mezuniyet hakkı kazanır. (Kaynak 3: Madde 7)

- Mezuniyet diploması, Öğrenci İşleri Daire Başkanlığı tarafından ön lisans ve lisans diplomaları hazırlanır. Yüksek lisans ve doktora diploması ise enstitü müdürlüğü tarafından hazırlanır. (Kaynak 3: Madde 7)

- Diplomalar, dekan/müdür ve rektör tarafından imzalanır. İmzalar ıslak imza olmalıdır. Diplomalarda yer alan bilgilerin kayıtlara uygunluğu tasdik edilir. (Kaynak 3: Madde 7)

- Diplomanın düzenlenmesinde, Üniversite tarafından bir hata yapılmasını istemekteyiz. Bu nedenle, iptal edilen diplomanın yenisi düzenlenir. (Kaynak 3: Madde 7)

- Kayıt hakkını kaybeden öğrenci, istenen belgeleri tamamlamayan öğrenci ve yazılı isteği üzerine kaydını sildiren öğrenci, ÖSYM tarafından yeniden yerleştirilmediği sürece Üniversiteye tekrar kaydolamaz. (Kaynak 1: Madde 34, Kaynak 2: Madde 9)

- Yabancı dille eğitimi yapılan programlarda, öğrenciler yeterlilik sınavına girer. Başarı puanını elde edenler, bağlı bulundukları bölüm/programlara kayıt hakkı kazanırlar. Başarısız öğrenciler iki dönem süreli yabancı dil hazırlık sınıfına kaydolurlar. (Kaynak 4: Madde 34)

- İlişik Kesme Koşulları:

 + Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre yükseköğretim kurumlarından çıkarma cezası almış olanlar ile kendi istekleri ile kaydını sildiren öğrencilerin Üniversite ile ilişikleri kesilir. (Kaynak 1: Madde 32, Kaynak 2: Madde 32)
 + Dört yıl üst üste katkı payı ve öğrenim ücreti ödemeyenler ve kayıt yenilememiş durumda olan öğrencilerin, ilgili birimlerin teklifi ve Senato kararı ile YÖK’ün onaylaması durumunda Üniversite ile ilişikleri kesilir. (Kaynak 1: Madde 32, 
... (1122 karakter daha)
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
- **Sure**: 8178.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Mezuniyet ve diploma kayıp işlemleriyle ilgili talebiniz konusunda aşağıdaki adımları takip edebilirsiniz:

1. Diplomayı Kaybetmiş Olmanız halinde:

Diplomasını kaybedenler, yaygın gazetelerden birine diploma kayıp ilanı verirler. Kayıp ilanının yer aldığı gazete, başvuru dilekçesi ve onaylı nüfus cüzdanı sureti, diploma ücretini yatırdıklarını gösteren banka dekontu ile diploma aldıkları birime müracaat ederler. Bu öğrencilere ilk diplomada yer alan bilgileri içeren yeni bir diploma düzenlenir ve üzerinde İkinci Nüsha olduğu bilgisi yer alır.

2. E-Devlet Üzerinden Mezuniyet Bilgileri Görünmemesi:

E-devlet üzerinden mezuniyet bilgilerin görülmemesi durumunda, ön lisans ve lisans diplomaları Öğrenci İşleri Daire Başkanlığında, yüksek lisans ve doktora diplomaları ise ilgili enstitü müdürlüğünde hazırlanır. Diplomaların arka sayfasında yer alan bilgilerin kayıtlara uygunluğu enstitülerde ilgili enstitü sekreterliği tarafından, diğer birimlerde ise Öğrenci İşleri Daire Başkanlığı tarafından tasdik edilir.

E-devlet üzerinden diploma onaylama işlemleri yapılmaktadır. Eksik veya onaysız belge/belgeler ile gelen öğrenciler ile beyanlarında hata olanların kayıt işlemi yerine getirilmeyecektir. E-Devlet üzerinden alınan belgelerde onay şartı aranmayacaktır.

Talep Edilen Belgeler:

* Başvuru formu çıktısı
* Öğrenci belgesi
* Transkript
* ÖSYM sınav sonuç belgesi
* ÖSYM yerleştirme belgesi
* Disiplin cezası almadığına dair belge
* Öğrencinin geldiği yükseköğretim kurumunda öğrenim gördüğü dönemlere ait bütün derslerini gösteren öğretim planı/müfredat
* Öğrencinin aldığı derslere ait ders içerikleri (muafiyet talebi olmayan öğrenciler için)
* Zorunlu hazırlık sınıfı bulunan bölüm/programlara yatay geçiş yapmak isteyen öğrenciler için hazırlık sınıfı ve/veya eşdeğer yabancı dil sınavlarından başarılı olduğunu gösterir belge

Bu bilgiler Ondokuz Mayis Üniversitesi (OMU) içerisinde düzenlenmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklay
... (286 karakter daha)
```

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] uzaktan
  - [ ] %20
  - [x] %80
  - [ ] %40
  - [ ] %60
- **Sure**: 20466.0 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı değildir. 
Bilgiye ulaşıldığında, iki tür sınav türü var: yüz yüze ve uzaktan. Yüz yüze olarak yürütülen derslerin teorik saatlerinin en az % 70'ine; ders uygulamaları, atölye ve laboratuvarların ise en az % 80'ine devam zorunludur. Ancak, soru ve projeksiyon cihazının bulunmaması gibi bir durum olsa bile, yüz yüze veya uzaktan sınav türünden hangisinin kullanılabileceği öğretim elemanı tarafından belirlenir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
- Belge: uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Sure**: 12289.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Yanit:
Sınavda kopya çekilmesinin cezası olarak kopya çekmek, telafi sınavına gitmek, disiplin cezasının uygulanması, sınav görevlisi tarafından uyarı alınması, öğrencinin salondan çıkarılması ve stajda kopya yapmanın cezası olarak, staj raporunun reddedilmesi, disiplin soruşturması başlatılması ve öğrencinin stajdan kaydolması ve mezun olamaması gibi sonuçlar sözkonusu olabilir.

1- Kopya çekmek: Sınav kağıtlarında herhangi bir değişiklik yapmak (karalamak, yırtmak, sayfaları varsa birbirinden ayırmak vb.) ve zarar vermek yasaktır. Bu gibi durumlarda sınav görevlisi veya ilgili öğretim elemanı, uyarıda bulunmaksızın bu öğrenciler hakkında işlem yapabilirler. (Kaynak 1: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf)

2- Telafi sınavına gitme: Öğrenciler sınav görevlilerinin her türlü uyarısına uymak zorundadır ve sınav görevleri tarafından telafi sınavına gidebilirler. (Kaynak 2: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf)

3- Disiplin cezasının uygulanması: Kopya vermek ve çekme girişiminde bulunmak da bir disiplin suçudur. Bu suçun tespitine sınav görevlileri karar verme yetkisine sahiptir. (Kaynak 1: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf)

4- Sınav görevcisi uyarı alması: Bu gibi durumlarda sınav görevlice veya ilgili öğretim elemanı, öğrencilere uyarıda bulunabilirler. (Kaynak 2: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf)

5- Öğrencinin salondan çıkarılması: Her öğrenci, 15 dakikadan daha kısa süre olmamak üzere, yoklama işlemi tamamlanmadan ve sınav görevlisinden izin almadan salondan çıkamaz. (Kaynak 1: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf)

6- Stajda kopya yapma: Staj raporunda benzer içeriklerin olması ve aynı konuları içeren, ders kitabındaki bilgilerin bulunduğu bir rapora kopya izlenimi veriyorsa staj raporunun reddedileceği belirtilmiştir. (Kaynak 3: staj_ilkeleri_23122019_inş_müh.pdf)

7- Stajdan kaydolma ve mezun olmama: Staj raporu reddedildiği takdirde öğrencinin stajın geçersiz sa
... (437 karakter daha)
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
- **Sure**: 9482.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Üniversiteyi bırakıp ayrılmak istediğinizde aşağıdaki işlemler ve dikkat etmeniz gereken hususlar bulunmaktadır:

- Ayrılmak için öğrencinin yazılı talebidır.
- Üyeliğin sonlandırılmasının ardından 7 gün içinde SKSDB’ye itiraz başvurusunda bulunabilir.
- İtiraz başvurusu, başvuru tarihinden sonra toplanan ilk Etkinlik Kurulunda görüşülerek karara bağlanır.
- Üyeliğine son verilen öğrenci aynı topluluğa yeniden üye olamaz.

Kayıtları sonlandırma hususunda dikkat edilecek hususlar ise;

- Kayıt yenilemeyen öğrencilerin ilgili birimin yönetim kurulunca kabul edilmesi halinde akademik takvimde belirtilen süre içinde yapılabilir.
- Kayıt yaptırdıkları dönemde almakla yükümlü oldukları derslerin toplam AKTS kredisi bir dönemde alınabilecek toplam AKTS kredisinden eksik ise dönemdeki AKTS kredisi sınırını aşmamak şartı ile bir üst sınıftan ders alabilirler.
- Sebebi ile değişmese de, öğrenci bilgi sistemi üzerinden alacağı dersleri seçer ve ders kaydı, danışman onayı ile kesinleşir.
- Her dönem/yıl başında akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden alacağı dersleri seçer ve ders kaydı, danışman onayı ile kesinleşir.
- Güz ve bahar dönemlerindeki öğrenim planında tanımlanan derslere kayıt yaptırmak zorundadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: öğrenci_toplulukları_yönergesi.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
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
- **Sure**: 7202.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Soruya göre, okulumuzu dondurup 1 yıl ara verdikten sonra nasıl ders seçeceğiz?

Kurallara göre, kaynaklarda dondurulan kayıtta ders seçimi hakkında açık bir bilgi yoktur. Dolayısıyla, dondurulan kayıt bitiminde yeniden ders seçimi nasıl yapılacak sorusuna cevap oluşturacağız.

Soruya göre, dondurulan kayıt bitiminde ders seçimi nasıl yapılır sorusunu iki ayrı soru olarak ele alabiliriz:

1. Dondurulan kayıt bitiminde ders seçimi nasıl yapılır?
2. Dondurulan kayıt bitiminde ders seçimi yapma süresini neye bağlıdır?

Dondurulan kayıt bitiminde ders seçimi nasıl yapılır?: 

Kursallarda dondurulan kayıt bitiminde, öğrenciler kayıt dönemi başladıktan sonra 1 hafta süreyle ders seçimi yapabilirler. Dondurulan kayıt bitiminde, ders seçimi yapma yetkiniz yoktur.

Dondurulan kayıt bitiminde ders seçimi yapma süresini neye bağlıdır?

Kursallarda dondurulan kayıt bitiminde, ders seçimi yapma yetkiniz öğrenci bilgi yönetim sistemine (SDBS) göre belirlenen süre içinde yapılır. Dondurulan kayıt bitiminde ders seçimi yapma yetkiniz students.dbms sistemine göre 7 günlük bir süre boyunca yapılır.

Yanıtlar:

1. 
Ders seçimi yapma yetkiniz yoktur.
 
2. 
Students.dbms sistemine göre 7 günlük bir süre boyunca yapılır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/3
  - [x] danışman
  - [ ] bölüm
  - [x] oidb@omu.edu.tr
- **Sure**: 8152.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Hocam, sizin ders notlarınızı sisteme girmemişsiniz:

- Soruya DOGRUDAN yanit: Hayır.
- Kaynağa göre cevap: 
- [Kaynak 1]: Ders kayıtlarını hangi tarihler arasında yapmam gerekir? Akademik takvimde belirtilen süreler içerisinde yapmak zorundasınız.
- [Kaynak 2]: Akademik takvimde belirtilen sürede danışman onayını muhakkak yaptırınız. Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz.
- [Kaynak 3]: MADDE 10 – (2) Akademik takvimde belirlenen süre içinde ders kaydını yapmayan öğrenciler, o dönemde öğrenimine devam etme hakkını kaybederler.
- [Kaynak 4]: Muafiyet başvurunuz sonuçlanıncaya kadar, dönem derslerine devam etmeniz önem arz etmektedir.
- [Kaynak 5]: Danışman onayını vermek için, öğrencinin şahsen gelmesini zorunlu tutabilir miyim? Öğrenci bilgi yönetim sistemi üzerinden internet ortamında ders kaydını yapan öğrenci, danışman onayına sistem üzerinden gönderebilmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
