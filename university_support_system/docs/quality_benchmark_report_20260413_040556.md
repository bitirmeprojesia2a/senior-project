# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-13 04:05:56
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 92.0% |
| Uretim Modu Dogrulugu | 88.0% |
| Anahtar Bilgi Kapsami | 60.0% |
| Temiz Kalite Orani | 96.0% |
| Ortalama Sure | 4374.3 ms |
| Medyan Sure | 3594.9 ms |
| Intent Analizi Aktif | 23/25 |
| Force LLM Sentez | 19/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 2/4 | 22427.4 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 2/3 | 3586.5 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | OK | 3/4 | 2190.7 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 4/4 | 4049.8 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 6286.0 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 6358.2 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 4661.6 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 5202.8 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | OK | 4/5 | 4087.8 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 5048.6 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 3/4 | 3594.9 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 3/4 | 4559.1 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 5836.9 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 4/4 | 3230.3 | uydurma_riski |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 3/3 | 4133.5 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 2/4 | 2474.7 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 2/5 | 2208.1 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 2/4 | 1729.7 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | YANLIS (kural) | 1/6 | 1227.9 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 1/4 | 2181.7 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 1/5 | 4358.4 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 3480.6 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 2646.3 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 2627.3 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | YANLIS (rag) | 0/3 | 1168.8 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 22427.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu eğitim-öğretim dönemlerinde derslerin başlamasından itibaren ikinci haftanın sonuna kadar veya kayıt yaptırdığı öğretim yılının en geç 3. haftasının sonuna kadar yapmalıdır. Muafiyet başvurusu yapılmış olsa da, karar çıkana kadar derslere devam etmeleri gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 3586.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Tek ders sınavına girebilmek için stajınızı tamamlamış olmanız gerekmez. Bir dersten başarılı sayılabilmek için yarıyıl/yıl sonu sınav notunuzun en az 50 olması gerekir. 

- Tek ders sınavından başarı şartını sağlayamadığınız durumlarda bir sonraki dönemlerde tek ders sınavına başvurabilmemiz için dönem başında ders kaydı yaptırmamız zorunlu değildir.
- 100 puan üzerinden 50'nin altında not alan öğrenciler başarısız sayılır. 
- Yarıyıl/yıl sonu veya bütünleme sınav notunun en az 60 olması bazı durumlarda gerekli olabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Akademik Programlar: RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
```

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [x] yeni
  - [x] ders
- **Sure**: 2190.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Soru: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

[Kaynak 2: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf] MADDE 20 (6) Başarısız olunan seçmeli dersin yeniden açılmaması halinde, öğrencinin isteği ve danışmanın önerisi doğrultusunda yönetim kurulu kararı ile başka bir seçmeli ders alınabilir. 

Bu durumda devam zorunluluğunuz değişmez, yeni seçmiş olduğunuz seçmeli derse devam etmeniz gerekir. Devam zorunluluğunuz, seçmeli derslere ilişkin genel kurallara göre belirlenir. [Kaynak 2: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf] MADDE 20 (4) Devam koşulu yerine getirilmemiş blok derslerine, laboratuvar/klinik öncesi uygulamalara/klinik uygulamalara ve seçmeli derslere devam etmek esastır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: yabancı_dil_eğitim_öğretimi_yönergesi.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
```

### Q4: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] transkript
  - [x] dahil
  - [x] ortalama
  - [x] tamamlamıştır
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 4049.8 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Pedagojik formasyon dersleri transkriptte yer alacaktır. Mezuniyet ortalamasına dahil edileceklerdir. Diplomaların arkasına "Pedagojik formasyon eğitimini tamamlamıştır" ifadesi yazılacaktır. Transkript belgelerini bölüm/program sekreterliklerine şahsen başvurarak veya Öğrenci İşleri Daire Başkanlığı diploma birimine şahsen müracaat ederek alınabilir. 

- Transkript belgesinin 1 adedi ücretsiz olup, birden fazla talep edilmesi durumunda belirli bir ücret yatırılarak alınabilir.
- Diplomalar ve transkriptler için başvurularda gerekli işlemler takip edilebilir.
- Pedagojik formasyon eğitiminde verilen derslerin hepsinin alınması zorunludur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Akademik Programlar: RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
- Belge: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt
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
- **Sure**: 6286.0 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Öğrenim ücretini Üniversitenin belirlediği banka hesabına yatırmalısınız. İkamet izni için gerekli belgelerin neler olduğu konusunda, uluslararası öğrencilerin Göç İdaresi Başkanlığı'na başvuruda bulunacağı ve öğrenci ikamet izni için gerekli belgeleri teslim edecekleri belirtilmektedir. Uluslararası Öğrenci Ofisi'ne başvurmanız tavsiye edilir. Ödemiş olduğunuz öğrenim ücretinin iade edilmeyeceğini de dikkate alın.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Finans: Kural
- Ogrenci Isleri: Kural

Kaynak Ozeti:
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: idari_ve_mali_işler_birimi.txt
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 6358.2 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
ÇAP başvuru şartları MADDE 5'te belirtilen koşulları karşıladıkları takdirde öğrenciler başvuru yapabilir. Bu koşullar şunlardır: öğrencinin başvurduğu yarı yıla kadar ana dal lisans programında yer alan tüm dersleri almış ve başarmış olması, başvurusu sırasındaki ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması, ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk % 20'sinde bulunması. Harç borcu ödemesi ile ilgili olarak net bilgi bulunmamaktadır. Öğrenci İşleri'ne başvurarakıntı bilgi alabilirsiniz. 

- ÇAP başvurusu için gerekli koşulları sağlayarak başvuru yapabilirsiniz.
- Harç borcu ödemeniz gerekir, ancak ödeme koşulları ve miktarları hakkında detaylı bilgi bulunamamıştır.
- Öğrenci İşleri'ne başvurarak harç borcu ödemesi hakkında bilgi alabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4661.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, öğrenci bilgi sistemi üzerinden alacakları dersleri seçmeniz gerekir. Ders kaydı, akademik takvimde belirlenen süre içinde yapılmalıdır. Daha sonra, ders kaydının kesinleştirilmesi için danışman onayı gerekir. 
- Ders kaydınızı yaptıktan sonra danışmanınızın onayını beklemelisiniz.
- Danışmanınıza ulaşamıyorsanız, bölüm başkanınıza veya Dekan/Müdürünüze durumu bildirmeniz ve akademik takvimde belirtilen sürede danışman onayını yaptırmanız gerekir.
- Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=factual
- **Sure**: 5202.8 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Yatay geçiş yaptığınızda bursunuz kesilir. Yeni üniversitede harç ödemeniz gerekir. Bursunuzun devri veya kesilip kesilmeyeceği konusunda bilgiye ulaşmak için burs aldığınız kurumla iletişim kurmanız önerilir. 
Ayrıca following bilgiler dikkate alınmalıdır:
- Kurum içi, kurumlar arası ve Yükseköğretim Kurulunca tanınan yurt dışı yükseköğretim kurumlarının diploma programları arasındaki yatay geçişler, önceden ilan edilen kontenjan ve şartlar çerçevesinde yapılır.
- Yatay geçişle gelen öğrenciler, geçiş yılı içerisinde uygulanan harçlara tabidir ve üniversitenin belirlediği ücreti ödemekle yükümlüdür.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 4087.8 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
4. sınıf öğrencisi olarak program süresini 1 yıl aşmışsın, ancak ek süre hakkının olup olmadığı ve bu sürede katkı payı ödeyip ödeyemeyeceğin konusunda net bilgi bulunamadı. 2547 sayılı Kanunun 46. maddesi uyarınca katkı payının ödenmesi gerektiği belirtiliyor. Üniversiteden uzaklaştırma cezası alan öğrencilerin bu süreleri öğrenim süresinden sayılır ve ilgili süreler için katkı payı/öğrenim ücreti ödenir. Ek süre hakkın ve katkı payı ile ilgili detaylı bilgi için ilgili birimle iletişim kurabilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=factual
- **Sure**: 5048.6 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Hayır, devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Bu dersi, dersin açıldığı sonraki dönemlerde tekrar alabilirsiniz. Devam koşulu yerine getirilmemiş tekrar derslerine devam etmek esastır. 
- Devamsızlıktan kaldığınız dersi sonraki dönemde tekrar alın.
- Dersin bütünleme sınavına girme hakkınız yoktur.
- Devam koşuluyla ilgili ayrıntılar için ilgili yönergelere başvurabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: bağıl_değerlendirme_yönergesi.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=comparative
- **Sure**: 3594.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Kayıt dondurma isteğinizin ilgili yönetim kurulunca kabul edilmesi durumunda öğrenim ücretini yatırmak zorunda değilsiniz. Ayrıca, kayıt dondurduğunuz süreler eğitim-öğretimden sayılmaz. 
- Kayıt dondurma talebinizi sunmanız gerekir.
- İlgili yönetim kurulunun kabul etmesi durumunda öğrenim ücretini ödemeyeceksiniz.
- Kayıt dondurulan süreler eğitim sürenize dahil edilmeyecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
```

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] transkript
  - [x] Ek Madde
  - [ ] başvuru yapabilir
  - [x] GANO
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4559.1 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Evet, transkriptiniz olmasa bile Ek Madde-1 (Merkezi Yerleştirme Puanı) ile yatay geçiş başvurusu yapabilirsiniz. Ek Madde-1 kapsamında yapılan yatay geçiş başvurularında öğrencinin Genel Akademik Not Ortalaması (GANO)'su değerlendirme aşamasında etkili değildir. 
- Yatay geçiş hakkı kazanan öğrencilerin kayıt işlemleri yüz yüze yapılacak olup, ilan edilen tarihlerde kayıtlarını yaptırmaları gerekecektir. 
- Belirtilen tarihlerde kaydını yaptırmayan öğrenciler kayıt hakkını kaybedeceklerdir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: lisansüstü_eğitim_ve.pdf
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
- **Sure**: 5836.9 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçiş ve kurumlar arası yatay geçiş arasındaki farklar, başvuru şartları ve değerlendirme kriterleri açısından farklılıklar gösterir. Kurum içi yatay geçiş başvurusu yapabilmek için öğrencinin genel not ortalamasının en az 2.80 olması gerekir ve merkezi yerleştirme sınav puanı da dikkate alınır. Kurumlar arası yatay geçiş için ise, öğrencinin kayıtlı olduğu programda bitirmiş olduğu dönemlere ait genel not ortalamasının, 4'lük sistem kullanan üniversiteler için en az 2.80, 100'lük sistem kullanan üniversiteler için en az 72 olması gerekmektedir. 
Disiplin cezası almış öğrencilerin başvuruları kabul edilmez, öğrenci kayıt dondurmuş ise bu durumu belgelendirmesi gerekir. 
Özel yetenek sınavı ile öğrenci kabul edilen diploma programlarına başvuruda bulunmak isteyenlerin, özel yetenek sınavında da başarılı olma şartı aranır. 
Yatay geçiş kontenjanları, ilgili diploma programının son dört yıla ait taban puanları ve başvuru şartları, son başvurunun kabul edileceği günden en az 15 gün öncesinde Üniversite web sayfasında ilan edilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
```

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] bağıl
  - [x] mutlak
  - [x] 10
  - [x] öğrenci sayısı
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 3230.3 ms
- **Kaynak Sayisi**: 4
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark, değerlendirmenin nasıl yapıldığı ile ilgilidir. Mutlak değerlendirme, öğrencilerin bir ders veya sınavdan aldıkları notların, önceden belirlen standartlar ve not aralıklarına göre değerlendirilmesini ifade eder. Bu sistemde, notlar genellikle 100 puan üzerinden verilir ve öğrencilerin başarısı, aldıkları notların bu standartlara göre değerlendirilmesine göre belirlenir.

Bağıl değerlendirme sistemi ise, öğrencilerin birbirleri ile rekabet haline göre değerlendirilmesini ifade eder. Bu sistemde, öğrencilerin aldıkları notlar, sınıfın geneline göre derecelendirilir ve başarılı sayılan öğrenci sayısı, sınıftaki öğrenci sayısına göre belirlenir.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: hizmet_içi_eğitim_yönergesi.pdf
```

### Q15: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] diploma eki
  - [x] transkript
  - [x] yerine geçmez
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4133.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Diploma eki transkript veya diploma yerine geçmez. Diploma eki, kişinin takip edip başarıyla tamamladığı öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek üzere verilir. Bu belge, diplomanın elde edilmiş yeti ve becerileri ifade ettiği destekleyici bir belgedir. Transkript, öğrenimine devam eden öğrencilerin bölüm/program sekreterliklerine başvurarak alabileceği veya mezun olan öğrencilerin Öğrenci İşleri Daire Başkanlığı'ndan şahsen müracaat ederek alabileceği bir belgedir. 
Diploma eki ile elde edilmiş yeti ve becerileri görebilirsiniz.
Transkriptine devam eden öğrencilerin veya mezun olan öğrencilerin belirli yerlerden alabileceği bir belgedir.
Diploma eki transkript yerine kullanılamaz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: avrupa_birliği_eğitim_ve_gençlik_programları_hayat_boyu_öğrenme_erasmus.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [ ] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 2474.7 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kayıt dondurma ile kayıt yaptırmamak arasında yeterli bilgi bulunamadığından, öğrencinin ilgili birimle iletişime geçerek ayrıntılı bilgi alması önerilir. Öğrencilerin belgelendirecekleri önemli mazeretlerinin veya eğitim-öğretimlerine katkıda bulunacak üniversite dışı imkanların ortaya çıkması halinde, ilgili birimin yönetim kurulu kararı ile kayıt dondurulabilir. Öğrenciler, her dönem/yıl başında akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden alacağı dersleri seçer ve ders kaydı, danışman onayı ile kesinleşir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: Kural
- Akademik Programlar: Kural

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: yonerge_uzaktan_egitim_onlisans_lisans.pdf
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [ ] UBYS
  - [ ] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2208.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatmak için elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ders_yeterlilik_sınavı_uygulama_yönergesi.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
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
- **Sure**: 1729.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınav notuna itiraz etmek için, sonuçların açıklanmasından itibaren 5 iş günü içerisinde ilgili bölüme yazılı olarak başvurmak gerekir. İtiraz üzerine, sınav kağıtlarının yeniden incelenmesi talebinde bulunabilir ve yeniden inceleme, ilgili öğretim elemanı tarafından en geç 3 iş günü içinde yapılır. İtiraz olması halinde, sınav kağıdı, ilgili öğretim elemanınca hazırlanmış cevap kağıdı da dikkate alınarak sınav inceleme komisyonu tarafından incelenir ve işlem, en geç 3 iş günü içinde sonuçlandırılır. Not değişikliği olması durumunda, ilgili birimin yönetim kurulu kararıyla Öğrenci İşleri Daire Başkanlığına bildirilir. Ayrıca, öğretim elemanı tarafından fark edilen maddi hataya ilişkin sınav not bildirim/not düzeltme formu, notların ilanından itibaren en geç 60 gün içinde ilgili birime sunulur.

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
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 1/6
  - [ ] ders
  - [x] staj
  - [ ] GANO
  - [ ] 2,00
  - [ ] ilişik kesme
  - [ ] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 1227.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Kural

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
```

### Q20: Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] 2. nüsha
  - [x] diploma
  - [ ] e-devlet
  - [ ] YÖKSİS
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2181.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Bu konuda elimdeki kaynaklarda net bilgi bulunamadi.

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
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [ ] %40
  - [ ] %60
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4358.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi, yüz yüze derslerden farklıdır. Koşullar elverdiği ölçüde tüm sınavların yüz yüze yapılması esastır. Uzaktan eğitim öğrencilerinin başarı notu, yarıyıl içi sınavının %15'i ile yılsonu/bütünleme sınavında alınan notun %85'inin toplamıdır. 
Derslerin yüz yüze veya uzaktan eğitim yoluyla yürütülmüş olmasına bakılmaksızın, bu derslerin sınavları, zorunlu haller dışında, yüz yüze yapılır. 
Tamamı uzaktan veya bir kısmı uzaktan olan derslerin sınavları çevrimiçi olarak da yapılabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3480.6 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Sınavda kopya çekilmesinin cezası doğrudan belirtilmemiştir. Ancak, kopya vermek ve çekme girişiminde bulunmak bir disiplin suçudur. Disiplin süreci, 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesine göre yürütülmektedir. 
- Sınava girebilmek için öğrenci kimlik belgelerini yanlarında bulundurmak ve görevlilerce istendiğinde göstermek zorundadırlar. 
- Disiplin suçlarına ilişkin hükümler 11.03.2023 tarihli resmi gazetede yayımlanan 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesine göre yürütülmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: Kural
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_ortak_sınav_yönergesi.pdf
- Belge: hizmet_içi_eğitim_yönergesi.pdf
- Belge: özel_yetenek_sınavı_yönergesi.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: koruma_ve_güvenlik_müdürlüğü_ulaşım_güvenliği_yönergesi.pdf
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: staj_ilkeleri_23122019_inş_müh.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [x] birim
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 2646.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Üniversiteyi bırakmak için yazılı talepte bulunmanız gerekmektedir. Ancak elimizdeki bilgiler bu konuda yeterli detalji içermemektedir. Ayrıca Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre yükseköğretim kurumlarından çıkarma cezası almış olanlar veya kendi istekleri ile kaydını sildiren öğrencilerin Üniversite ile ilişiği kesilmektedir. 
- Yazılı talepte bulunmanız,
- Geçerli bir mazeret olmaksızın iki üst üste genel kurul toplantısına katılmamanın ve 
- disiplin yaptırımları gibi konular önemlidir. 
Detaylı bilgi için ilgili birimle iletişime geçmeniz gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: Kural
- Finans: Kural

Kaynak Ozeti:
- Belge: öğrenci_toplulukları_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: idari_ve_mali_işler_birimi.txt
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
- **Sure**: 2627.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Öğrenci, kayıt dondurma süresinin bitiminde öğrenimine kaldığı yerden devam eder. Öğrenci, ayrıldığı dönemin/yılın başından başlamak koşuluyla öğrenimine devam edecektir. Kayıt dondurulan dönem/dönemler, süre hesabında dikkate alınmaz.

Öğrenci, ders seçimini melakukan döneminde (dönem başlangıcında) yapacaktır. Kaynaklarda, kayıt dondurma süresinin bitiminde öğrencinin ders seçimini nasıl yapacağına ilişkin spesifik bir bilgi bulunmamaktadır. Ancak, öğrenci öğrenimine kaldığı yerden devam edeceği için, ilgili döneme ait dersleri seçerek öğrenimine devam edecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 0/3
  - [ ] danışman
  - [ ] bölüm
  - [ ] oidb@omu.edu.tr
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=procedural
- **Sure**: 1168.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Üniversiteyi kazanarak ilk kayıt yaptırdığım yıl ders kaydı yaptırmam gerekir mi? Evet yeni kayıt yaptıran öğrencilerimizin de ders kaydı yapması gerekmektedir. Ders kayıtlarını hangi tarihler arasında yapmam gerekir? Ders kaydınızı eğitim gördüğünüz birime ait akademik takvimde belirtilen süreler içerisinde yapmak zorundasınız. Akademik takvimlere Öğrenci İşleri Daire Başkanlığı WEB sayfasından ulaşabilirsiniz.

(Kaynak: sık_sorulan_sorular.txt)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
