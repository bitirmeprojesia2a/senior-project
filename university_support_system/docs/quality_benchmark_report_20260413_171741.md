# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-13 17:17:41
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 84.0% |
| Uretim Modu Dogrulugu | 88.0% |
| Anahtar Bilgi Kapsami | 61.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 5724.1 ms |
| Medyan Sure | 3960.1 ms |
| Intent Analizi Aktif | 23/25 |
| Force LLM Sentez | 18/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 50651.7 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 2/3 | 2952.2 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | OK | 2/4 | 2831.0 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 4/4 | 3562.2 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 6426.9 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 4512.7 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 5156.4 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 2705.8 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | OK | 3/5 | 4048.7 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 5599.7 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 3/4 | 4442.4 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 3/4 | 5125.2 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | YANLIS | OK | 2/5 | 3620.0 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 4/4 | 5906.6 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 3/3 | 3190.7 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 4414.7 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 2/5 | 3425.6 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 2/4 | 2196.4 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | YANLIS (kural) | 1/6 | 1538.4 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 1/4 | 2754.8 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | YANLIS | OK | 3/5 | 2949.4 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 4875.2 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 2/4 | 3960.1 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 4742.2 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | YANLIS (rag) | 0/3 | 1512.7 | - |

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
- **Sure**: 50651.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu derslerin başlamasından itibaren ikinci haftanın sonuna veya en geç kayıt yaptırdığı öğretim yılının üçüncü haftasının sonuna kadar yapmalıdır. Muafiyet başvurusu kararı çıkana kadar derslere devam edilmelidir. Önceki başarılı derslerden muaf olmak için, transkript ve ders içerikleri ile birlikte başvuru yapılmalıdır. 
Öğrenciler, müfredatlarında yer alan bütün dersleri almış olmak zorundadırlar. 
Muafiyet talebi ilgili yönetim kurulu tarafından karara bağlanıncaya kadar öğrenciler muafiyet talebinde bulundukları derse devam ederler.

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
- **Sure**: 2952.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Tek ders sınavına girebilmek için stajınızı tamamlamış olmanız gerekmez. Bir dersten başarılı sayılabilmek için 100 puan üzerinden en az 50 puan almanız gerekir.

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
- **Key Facts**: 2/4
  - [ ] değiştirebilir
  - [ ] devam koşulu
  - [x] yeni
  - [x] ders
- **Sure**: 2831.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Soru: Başarılı olduğunuz seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

Cevap: Kaynaklar incelendiğinde, başarısız olduğunuz seçmeli ders yerine başka bir seçmeli seçmeniz durumunda devam zorunluluğunuzun nasıl değişeceğine ilişkin bilgi bulunmamaktadır.Ancak, Kaynak 2: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf, MADDE 20 (6) 'da başarısız olunan seçmeli dersin yeniden açılmaması halinde, öğrencinin isteği ve danışmanın önerisi doğrultusunda yönetim kurulu kararı ile başka bir seçmeli ders alınabileceği belirtilmiştir. Bu durumda, devam zorunluluğunuzun değişip değişmeyeceği konusunda net bir bilgi bulunmamaktadır.

Kaynak 1: yonetmelik_lisansustu_egitim_ogretim.pdf, MADDE 21 (2) 'de başarısız olunan dersin yerine başka bir ders alınabileceği belirtilmiştir. Ancak bu madde, lisansüstü eğitim için geçerli olup, soruda bahsi geçen lisans veya ön lisans eğitimi için geçerli olup olmadığı konusunda net bir bilgi bulunmamaktadır.

Bu nedenle, "Bu konuda elimdeki kaynaklarda net bilgi bulunamadi" şeklinde cevap verilmesi more uygun görünmektedir.

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
- **Sure**: 3562.2 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Pedagojik formasyon dersleri transkript içinde yer alacaktır. Sadece bir transkript düzenlenecek ve bu dersler bu transkript içinde yer alacaktır. Mezuniyet ortalamasına dahil edilecektir. Diplomaların arkasına "Pedagojik formasyon eğitimini tamamlamıştır" ifadesi yazılacaktır. 
Aşağıdaki noktalar da dikkate alınmalıdır:
* Pedagojik formasyon eğitiminde verilen derslerin hepsinin alınması zorunludur.
* Transkript belgesi öğrenimine devam eden öğrenciler tarafından bölüm/program sekreterliklerine şahsen başvurarak alınabilir. 
* Mezun olan öğrenciler ise Öğrenci İşleri Daire Başkanlığı diploma birimine şahsen müracaat ederek alabilirler.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Akademik Programlar: RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
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
- **Sure**: 6426.9 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Öğrenim ücretini Ondokuz Mayis Universitesi tarafından belirlenen hesaba yatırmalısınız. Ancak banka veya hesap numarası açıkça belirtilmemiştir. İkamet izni için Göç İdaresi Başkanlığı’na başvuruda bulunmanız ve ilgili belgeleri teslim etmeniz gerekmektedir. İlgili birimler ile iletişime geçerek detaylı bilgi alabilirsiniz. 
Ayrıca, 
- kayıt işlemi ve koşulları ile ilgili olarak uluslararası öğrenci alım kılavuzunda yer verilen bilgileri incelemelisiniz.
- öğrenim ücretleri ve ödeme detayları için finans birimi ile iletişim kurabilirsiniz.

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
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 4512.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
ÇAP programa başvurmak için ana dal diploma programının en erken üçüncü yarı yılının başında, en geç ise beşinci yarı yılın başında başvurabilirsiniz. Başvurunuzun başarılı olması için başvurduğunuz yarıyıla kadar ana dal lisans programında yer alan tüm dersleri almış ve başarmış olmanız, başvurunuz sırasındaki ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk %20'sinde bulunmanız gerekir. Harç borcu için ise ödemenin nasıl yapılacağı konusunda elimdeki kaynaklarda net bilgi bulunmamaktadır. 
- Öğrenci türünüz ve birim bilgisi ile ödemenin nasıl yapılacağı konusunda daha detaylı bilgi alınabilir.
- Ödemenin doğru şekilde yapılması için ilgili birime başvurmanız önerilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 5156.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Harç ücretini yatırdıktan sonra ders kaydını, akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden yapacaksınız. Daha sonra danışmanınızın onayını bekleyeceksiniz. Danışman onayı işlemi tamamlandıktan sonra, kayıtlanmış olduğunuz dersleri tek tek kontrol ediniz. Sizin danışman onayına göndermiş olduğunuz derslerden bir veya birkaçı danışmanınız tarafından listeden çıkartılmış olabilir. Danışman onay süreci, akademik takvimde belirtilen sürede gerçekleşir. Danışmanınıza ulaşamaz ve ders kaydınızı onaylatamazsanız, bölüm başkanınıza, bölüm başkanına da ulaşamazsanız Dekan/Müdürünüze durumu bildirmek sureti ile akademik takvimde belirtilen sürede danışman onayını muhakkak yaptırınız. Ayrıca, her dönem başında alıp başarılı olduğunuz dersleri müfredatınızla karşılaştırmanız gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
```

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [ ] bildiri
  - [x] harç
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2705.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Bursumun devri veya kesilip kesilmeyeceği konusunda bilgiye ulaşmak için burs aldığınız kurumla iletişim kurmanız gerekmektedir. Yatay geçiş yaptığınızda, yeni üniversitede harç ödemek zorunda olup olmadığınız konusunda elimdeki kaynaklarda net bilgi bulunamadı.

Finans:
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [ ] azami
  - [x] ek
  - [ ] süre
  - [x] katkı payı
  - [x] öde
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 4048.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Bu konuda elimizdeki kaynaklarda net bilgi bulunamadı. Öğrencilere, belgeleyecekleri öğrenim ve eğitimlerine katkıda bulunacak üniversite dışı imkanların doğması halinde en fazla bir yıla kadar izin verilebileceği belirtilmiştir. Ayrıca, üniversiteden uzaklaştırma cezası alan öğrencilerin katkı payı/öğrenim ücreti ödeyeceği belirtilmiştir. Detaylı bilgi için ilgili birimle iletişime geçebilirsiniz.

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
- Belge: tıp_fakültesi_tıp_doktorluğu_programı.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 5599.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Çünkü bir dersten devamsızlıktan kalan öğrenci o dersin bütünleme sınavına giremez. Bu dersi tekrar alabilmeniz için, derslere devam zorunluluğunu yerine getirmeniz gerekmektedir. Bu zorunluluğun %70 için teorik derslerin ve %80 için ders uygulamaları, atölye ve laboratuvarların tamamlanması gerektiği belirtilmektedir. Ancak, bu konuda net bilgi bulunamadığından, bu konuda daha fazla bilgi için ilgili yönetim kurulu veya akademik birimlere başvurmak gerekebilir.

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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4442.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
İkinci öğretim öğrencisi olarak kayıt dondurmak istiyorsanız, ilgili yönetim kurulunun kabul etmesi durumunda öğrenim ücretini yatırmak zorunda değilsiniz. Kayıt dondurduğunuz süreler eğitim-öğretimden sayılmaz. Ancak, katkı payı veya öğrenim ücreti ödemeniz gereken bir eğitim-öğretim dönemindaysanız, akademik takvimde belirtilen süreler içinde bu ödemeyi yapmak zorundasınız. Ödemeniz gereken ücret, öğrenci türüne ve birime göre değişebilir. Kayıt dondurma talebinizin kabul edilip edilmediğini öğrenmeniz ve gerekli işlemleri tamamlamanız önemlidir. 

Ayrıca, katkı payı veya öğrenim ücreti ödemeleriyle ilgili olarak gerekli ödemeyi akademik takvimde belirtilen süreler içinde gerçekleştirmelisiniz.

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
  - [x] başvuru yapabilir
  - [ ] GANO
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 5125.2 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Evet, hazırlık sınıfı okuyan ve Ek Madde-1 kapsamında merkezi yerleştirme puanı ile yatay geçiş başvurusu yapmak isteyen adaylar, transkriptleri olmadan da başvuru yapabilirler. 
Yatay geçiş için genel not ortalamasının 4.00 üzerinden 2.00 veya üstü olması gerekmektedir. 
Ayrıca, OMÜ-YÖS sınavından herhangi bir puan türünde veya üniversitenin kabul ettiği diğer sınavlardan en az 40 puan almış olmak gerekmektedir.

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
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 3620.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Kurum içi yatay geçiş ve kurumlar arası yatay geçiş arasındaki farklar, başvuru şartları ve değerlendirme kriterleri farklılık gösterir. 

Kurum içi yatay geçiş, aynı üniversite içindeki farklı bölümler arasında yapılan yatay geçişlerdir. Bu तरह geçişlerde, öğrencinin aynı üniversitede başka bir bölüme geçmek istemesi durumunda, genel not ortalaması ve merkezi yerleştirme puanı dikkate alınır.

Kurumlar arası yatay geçiş ise, farklı üniversiteler arasında yapılan yatay geçişlerdir. Bu türlü geçişlerde, öğrencinin diğer üniversiteden aldığı notların ve puanların değerlendirilmesi ile kontenjan dahilinde yerleştirme yapılır.

Başvuru şartları olarak, kurum içi yatay geçiş için öğrencinin en az bir yarıyılı başarı ile tamamlamış olması, genel not ortalamasının %60’ı ve merkezi yerleştirme puanının %40’i esas alınarak başarı puanları hesaplanır. Kurumlar arası yatay geçiş için ise, öğrencinin yükseköğretim kurumunda herhangi bir disiplin cezası almamış olması ve genel not ortalamasına göre değerlendirme yapılır.

Değerlendirme kriterleri olarak, kurum içi yatay geçiş için aynı puan türündeki programlara geçiş için genel not ortalamasının %60’ı ve merkezi yerleştirme puanının %40’i esas alınırken, farklı puan türlerindeki programlara geçiş için ise genel not ortalamasının %30’ı ve merkezi yerleştirme puanının %70’i esas alınır. Kurumlar arası yatay geçiş için ise, genel not ortalaması ve merkezi yerleştirme puanı dikkate alınır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
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
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 5906.6 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark, bağıl değerlendirmede öğrencilerin birbiriyle kıyaslama yapılması, mutlak değerlendirmede ise belirli bir not aralığına göre değerlendirme yapılmasıdır. 10'dan fazla öğrencinin katıldığı durumlarda bağıl değerlendirme, 10 ve altında öğrenci olduğunda mutlak değerlendirme sistemi uygulanır. Öğrenci sayısının 11-29 arasında olduğu durumlarda, ders ortalaması dikkate alınarak nota dönüştürülür. Mutlak değerlendirme sistemi, öğrencilerin başarı notlarını belirli bir ölçek üzerinden hesaplayarak belirler, örneğin 90-100 arasında AA, 80-89 arasında BA, 70-79 arasında BB, 65-69 arasında CB, 60-64 arasında CC, 0-59 arasında FF olarak notlar belirlenir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: hizmet_içi_eğitim_yönergesi.pdf
- Belge: yonerge_bagil_degerlendirme.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: bağıl_değerlendirme_yönergesi.pdf
```

### Q15: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] diploma eki
  - [x] transkript
  - [x] yerine geçmez
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 3190.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Diploma eki ile transkript arasındaki fark nedir? 
Diploma eki, bir yükseköğretim diplomasına ek olarak verilen, elde edilmiş yeti ve becerilerin ifade edildiği belgedir. Diploma eki, transkript (not çizelgesi) veya diploma yerine geçmez. 

Diploma eki transkript yerine kullanılabilir mi? 
Hayır, diploma eki transkript yerine kullanılamaz. Diploma eki ve transkript birbirinin yerini tutmayan, farklı bilgiler sunan belgelerdir.

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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4414.7 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Kayıt dondurma ile kayıt yaptırmamak arasında temel fark, kayıt dondurma işleminin yönetmelik çerçevesinde yapılmasıdır. Kayıt yaptırmamak durumunda ise öğrenci akademik takvimde belirlenen süre içerisinde öğrenim planında tanımlanan derslere kayıt yaptırmaz. 

Kayıt dondurma işlemleri MADDE 17'de yer alan yönetmelik çerçevesinde yapılır. Akademik takvimde belirlenen süre içinde ders kaydını yapmayan öğrenciler, o yılda öğrenimine devam etme hakkını kaybederler. 
Kaybedilen yıl öğrenim süresinden sayılır. Mazeretlerinin haklı ve geçerli olduğu yönetim kurulunca kabul edilmek koşuluyla, süresi içinde ders kaydını yaptıramayan öğrencilerin kayıtları, akademik takvimde belirtilen süre içinde Öğrenci katkı payı/öğrenim ücreti ödenmesi durumunda devam edebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: ön_kayıt_kılavuzu_başvuru_adımları.pdf
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
- **Sure**: 3425.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatmak için elimdeki kaynaklarda net bilgi bulunamadı. Ancak, ders kaydının yapılması gerektiği ve akademik takvimde belirtilen süreler içerisinde kaydın tamamlanması gerektiğini söyleyebiliriz. Ayrıca, danışman onayı işleminin de önemli olduğu ve danışmanın kayıt olmak istediğimiz derslerde değişiklik yapma hakkının bulunduğu belirtilmektedir.

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
- **Sure**: 2196.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınav notuna itiraz sürecinde, öğrenciler sonuçların açıklanmasından itibaren 5 iş günü içerisinde ilgili bölüme yazılı olarak başvurabilirler. İtiraz üzerine, sınav kağıtlarının yeniden incelenmesi talebinde bulunabilirler. Yeniden inceleme, ilgili öğretim elemanı tarafından en geç 3 iş günü içinde yapılır.

İtiraz süresi, sınav sonuçlarının açıklanmasını takiben 5 iş günüdür. Yeniden inceleme sonucunun ardından, öğrenci 3 iş günü içinde itiraz edebilir. İtiraz olması halinde, sınav kağıdı ve öğretim elemanınca hazırlanmış cevap kağıdı da dikkate alınarak sınav inceleme komisyonu tarafından incelenir. İşlem, en geç 3 iş günü içinde sonuçlandırılır.

Öğretim elemanı tarafından fark edilen maddi hataya ilişkin sınav not bildirim/not düzeltme formu, notların ilanından itibaren en geç 60 gün içinde ilgili birime sunulur. İlgili birim yönetim kurulu, not değişiklik teklifini karara bağlar ve Öğrenci İşleri Daire Başkanlığına bildirir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_ders_yeterlilik_sinavi_uygulama.pdf
- Belge: yonerge_yuzde_on_basari_degerlendirme.pdf
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
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [ ] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 1538.4 ms
- **Kaynak Sayisi**: 4

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
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
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
- **Sure**: 2754.8 ms
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
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs', 'academic_programs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [x] %40
  - [x] %60
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 2949.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Uzaktan eğitim yoluyla alınan 5'i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı değildir. Uzaktan eğitimde de sınavlar çevrimiçi olarak yapılabilir ve başarı değerlendirmesi yarıyıl içi değerlendirmesi ve yarıyıl sonu sınavı notlarının birlikte değerlendirilmesiyle yapılır. Uzaktan eğitimde yarıyıl içi değerlendirmenin başarı notuna etkisi %40'tan fazla olamaz.

Ancak, kaynaklarda yer alan bilgilere göre, uzaktan eğitim öğrencilerinin başarı notu, yarıyıl içi sınavının %15'i ile yılsonu/bütünleme sınavında alınan notun %85'inin toplamıdır. Bu, yüz yüze eğitimde kullanılan başarı notu hesabından farklıdır. Yüz yüze eğitimde, yarıyıl içi değerlendirmenin başarı notuna etkisi %40'tır ve yarıyıl sonu sınav notunun etkisi %60'tır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4875.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Sınavda kopya çekilmesinin cezası hakkında net bir bilgi bulunamadı. Ancak kopya çekmenin disiplin suçu olduğu ve sınav görevlilerinin bu suçun tespitine karar verme yetkisine sahip olduğu belirtiliyor. Disiplin süreci 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesine göre yürütülmektedir. 
Ayrıca sınav kurallarına uymamanın da disiplin suçu olarak kabul edildiği ve öğrencilerin sınav kağıtlarında değişiklik yapmasının, sınav evraklarını zarara uğratmasının yasak olduğu belirtiliyor. 
Sınav görevlilerinin disiplin suçu tespitine karar verme yetkisi bulunmakta ve disiplin süreci ilgili kanun maddelerine göre yürütülmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: Kural

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: staj_ilkeleri_23122019_inş_müh.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
- Belge: mühendislik_fakültesi_ortak_sınav_yönergesi.pdf
- Belge: hizmet_içi_eğitim_yönergesi.pdf
- Belge: özel_yetenek_sınavı_yönergesi.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: koruma_ve_güvenlik_müdürlüğü_ulaşım_güvenliği_yönergesi.pdf
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs', 'finance'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [x] form
  - [x] birim
- **Intent Analizi**: complexity=process_chain, force_llm=False, is_personal=False, query_type=procedural
- **Sure**: 3960.1 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Üniversiteyi bırakmak isteyen öğrencilerin yazılı talepleri üzerine üyelikleri sonlandırılabilir. Üyelikten çıkarılan öğrenci, tebliğ tarihinden itibaren 7 gün içinde ilgili birime itiraz başvurusunda bulunabilir. Üniversite ile ilişiğin kesilmesi için, öğrencinin mezuniyet veya benzeri nedenlerle ilişik kesilmesi gibi olağan süreçler dışında, geçerli bir mazereti olmadan üst üste iki Genel Kurul toplantısına katılmaması veya topluluğun amaçlarına aykırı faaliyette bulunması durumlarda üyeliği sonlandırılabilir. 

İlgili işlemler için;
- Derhal Öğrenci İşleri birimine yazılı talepte bulun.
- Üyelikten çıkarılma tebliği aldıktan sonra 7 gün içerisinde itirazda bulunabilirsiniz. 
- İlgili mevzuata uygun diğer işlemler için İkamet İşlemleri Ofisi birimine başvurunuz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Akademik Programlar: RAG
- Finans: RAG

Kaynak Ozeti:
- Belge: öğrenci_toplulukları_yönergesi.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
- Belge: uluslararası_öğrenci_ikamet_işlemleri.pdf
- Belge: tyb.pdf
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: zimmetteki_taşınırların_iadesi_hakkında.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [x] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4742.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Okulumuzu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimi için akademik danışmanınızla görüşebilirsiniz. Bu görüşmede, daha önce aldığınız derslerin durumunu ve kalan derslerinizi değerlendirerek yeni ders seçimi yapabilirsiniz. Ayrıca, kayıt dondurma süresinin bitiminde öğreniminize kaldığınız yerden devam edeceğiniz belirtildiğinden, önceki eğitim durumunuz dikkate alınarak ders seçimi yapılacak. Detaylı bilgi için akademik danışmanınıza danışmanız önerilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: avrupa_birliği_eğitim_ve_gençlik_programları_hayat_boyu_öğrenme_erasmus.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=False, is_personal=True, query_type=factual
- **Sure**: 1512.7 ms
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
