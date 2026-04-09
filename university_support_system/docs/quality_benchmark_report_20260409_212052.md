# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-09 21:20:52
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 64.0% |
| Uretim Modu Dogrulugu | 28.0% |
| Anahtar Bilgi Kapsami | 35.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 5103.6 ms |
| Medyan Sure | 3332.7 ms |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | YANLIS (vt) | 0/4 | 306.5 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 2/3 | 28591.1 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | YANLIS (unknown) | 1/4 | 79.1 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | YANLIS | OK | 3/4 | 4624.7 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | YANLIS | OK | 3/3 | 4573.7 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | YANLIS | YANLIS (kural) | 0/4 | 120.2 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | YANLIS (vt) | 4/5 | 1653.8 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | YANLIS (rag) | 2/5 | 3332.7 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | YANLIS (kural) | 1/5 | 115.1 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | YANLIS | OK | 3/4 | 8086.3 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | YANLIS | YANLIS (vt) | 0/4 | 135.8 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | YANLIS (rag) | 1/4 | 2696.2 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | YANLIS (rag) | 1/5 | 5131.0 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 2/4 | 6038.5 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | YANLIS (rag) | 3/3 | 2378.3 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | YANLIS (rag) | 2/4 | 3001.2 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | YANLIS (rag) | 0/5 | 2705.8 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 1/4 | 3996.6 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | YANLIS (rag) | 2/6 | 9917.7 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 4396.5 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | YANLIS | YANLIS (rag) | 1/5 | 3605.4 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 16873.2 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | YANLIS | YANLIS (unknown) | 0/4 | 35.8 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | YANLIS (rag) | 1/4 | 15079.3 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | YANLIS (kural) | 0/3 | 116.1 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: vt (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [ ] derslere devam
- **Sure**: 306.5 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Veritabanindaki en yakin kayit donemi 2026-Guz icin 26.08.2026 - 06.09.2026 tarihleri arasinda planlanmistir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- VT

Kaynak Ozeti:
- Veritabani kaydi: kayit donemi
```

### Q2: Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi ve sınavda başarılı sayılmam için minimum not kaç?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/3
  - [x] staj
  - [x] tamamla
  - [ ] CC
- **Sure**: 28591.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Stajımı tamamlamış olmamın teknik ders sınavına girebilmem için şart olmadığını tespit ediyorum. Açıklamayı yapabilmek için belge kaynağı Madde 10'dan yararlanıyorum:

* Staj, çok özel koşullar dışında kesintisiz olarak başlanıp bitirilmelidir.
* Gerektiği hallerde izin süresi staj süresinin %10’unu aşamaz.

Sınavda başarılı sayılabilmem için minimum notu belirlemem mümkün değil zira kaynaklardaki bilgiler bunu belirtmiyor. Bu soruyla ilgili bir net bilgi elimde yok.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: staj_esaslar.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: 1_elektrik_elektronik_staj_ilkeleri_ve_uygulama_esasları.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: unknown (beklenen: llm) - YANLIS
- **Key Facts**: 1/4
  - [ ] değiştirebilir
  - [ ] devam koşulu
  - [ ] yeni
  - [x] ders
- **Sure**: 79.1 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Bu akademik program sorusunu dogru cevaplayabilmem icin once bolum veya program bilgisini bilmem gerekiyor. Ornegin 'Bilgisayar Muhendisligi icin 1. yariyil dersleri nelerdir?' veya 'Kimya bolumu teknik secmeli dersleri hangileri?' seklinde sorabilirsin. Kisisel ilerleme bilgisi istiyorsan OTP ile giris yapman yeterli; bolum bilgin oturumdan alinabilir.
```

### Q4: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['academic_programs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] transkript
  - [x] dahil
  - [x] ortalama
  - [ ] tamamlamıştır
- **Sure**: 4624.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sorumu cevaplayacak gibi görünen kaynağın bulunmamasına rağmen soru doğrudan uygulanabilir. Pedagojik formasyon dersleri transkriptte dahil edilmeyebilmese de akademik müfredatla alakalıdır. 

Bu nedenle, Pedagojik formasyon dersleri transkripte dahil ediliyor mu?: 
Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

Mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?: 
Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

Nota bağlı olan diğer sorularınız için, yukarıda belirtildiği gibi, ilgili kaynakları incelemenizi ve tekrar sormanızı şiddetle öneririm.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
```

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['finance', 'academic_programs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] ücret
  - [x] ikamet
  - [x] belge
- **Sure**: 4573.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Kendisine hitap ediyorum. Uluslararası öğrenci olarak kayıt yaptırırken, öğrenim ücretini ÖİDB (Öğrenci İşleri ve Destek Hizmetleri Birliği) Katkı Payı ve Öğrenim Ücreti Ofisi'ne yatırmalısınız. 

Ikamet izni için hazırlamanız gereken belgeleri sorgulamak istediğiniz için, aşağıdakileri kontrol edebilirsiniz:

- Öğrenim ücretini yatırmak için gerekli olan bilgiyi ÖİDB Katkı Payı ve Öğrenim Ücreti Ofisi'ne bildirmek için YÖKSİS veri tabanından kayıt olduğunuz program düzeyindeki bilgiyi alma gereklidir.
- Yabancı uyruklu öğrencilerin ders kayıtlanma durumunu göç idaresine göndermek ve yabancı burslulara ait işlemleri için YÖK tarafından yayınlanan 667 KHK kapsamında gelen yazılar doğrultusunda işlem yapılıyor.
- Ancak, ikamet izni başvuruları için gerekli olan detaylı bilgiyi sorgulamak için Öğrenci İşleri birimi ile iletişime geçmeniz gereklidir.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance'] (beklenen: ['academic_programs', 'finance']) - YANLIS
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] not ortalaması
  - [ ] harç
  - [ ] ödeme
  - [ ] başvuru
- **Sure**: 120.2 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

Uretim Turu:
- Kural
```

### Q7: Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra ders kaydını nasıl yapacağım, danışmanın onay süreci nasıl işliyor?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: vt (beklenen: llm) - YANLIS
- **Key Facts**: 4/5
  - [x] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Sure**: 1653.8 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırmış olduğunuzda, aşağıdaki adımları takip edebilirsiniz:

1. Ders Kaydı Yapma: Veritabanından en yakın kayıt dönemi olan 2026-Güz (26.08.2026 - 06.09.2026) için ders kaydı yapabilirsiniz. Bu tarihler arasında öğrenci işlerine müracaat etmeniz gerekecektir.
2. Danışman Onay Süreci: Ders kaydını yaptıktan sonra, danışmanınız tarafından onay süreci başlayacaktır. Bu sürecin ardından, hesabınızda herhangi bir problem oluşmaması için öğrenci işlerine müracaat etmeniz gerekebilir.

Lütfen, bu bilgilere göre gereken herşeyi yapın.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: VT
- Finans: Kural

Kaynak Ozeti:
- Veritabani kaydi: kayit donemi
```

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/5
  - [ ] burs
  - [ ] kesilme
  - [x] kurum
  - [x] bildiri
  - [ ] harç
- **Sure**: 3332.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
MADDE 6 - (1) Üniversitemize yatay geçişler, diğer yükseköğretim kurumlarındaki aynı düzeydeki eşdeğer diploma programlarından yapılır. PP.1.2.PRS.0048, R0, Temmuz Sayfa 2 / 5 2025 (2) Kurumlar arası yatay geçişlerde öğrencinin kayıtlı olduğu programda genel not ortalamasının 4 lük sistem kullanan üniversiteler için en az 2.80, 100 lük sistem kullanan üniversiteler için en az 72 olması gerekir. Transkriptinde iki not sistemi de var ise 100 lük sistemdeki notu kullanılır. (3) Üniversitemizdeki ön lisans ve lisans programları için belirlenen yatay geçiş kontenjanları ile başvuru ve değerlendirme takvimi, Yükseköğretim Kurulu ve Üniversitemiz internet sayfasında ilan edilir. (4) Ön lisans programlarında yatay geçiş kontenjanları ile başvuru ve değerlendirme takvimi ikinci yarıyıl için Ocak ayı, üçüncü yarıyıl için ise Temmuz ayında ilan edilir. (5) Lisans programlarından dört yıllık eğitim verenlerde ikinci ve üçüncü sınıflar için; beş yıllık eğitim verenlerde ikinci, üçüncü ve dördüncü sınıflar için; altı yıllık eğitim verenlerde ikinci, üçüncü, dördüncü ve beşinci sınıflar için yatay geçiş kontenjanları ile başvuru ve değerlendirme takvimi Temmuz ayında ilan edilir. (6) Her yıl düzenli olarak ikinci, üçüncü, dördüncü ve beşinci sınıflar için ÖSYM giriş genel kontenjanı 50 ve 50 den az olan programlarda iki, 51 ve 100 arası olan programlarda üç, 101 ve üzerinde olan programlarda ise dört kurumlar arası yatay geçiş kontenjanı Yükseköğretim Kurulu tarafından belirlenir. Bununla birlikte Üniversitemizdeki ilgili birim kurulları, geçişin yapılacağı programın giriş yılındaki kontenjanı ile yatay geçiş kontenjanı belirlenen yarıyıla kadar programdan ilişiği kesilen veya ayrılan öğrenci sayıları ile bu yarıyıl içinde yatay geçiş yoluyla gelmiş olan öğrenci sayıları arasındaki farkı aşmayacak biçimde ilave kontenjan belirleyebilirler. İlave kontenjan belirlenmesi hâlinde bu kontenjanlar en geç Haziran ayının otuzuncu günü mesai saati bitimine kadar Yükseköğret
... (1404 karakter daha)
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['finance'] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 1/5
  - [ ] azami
  - [x] ek
  - [ ] süre
  - [ ] katkı payı
  - [ ] öde
- **Sure**: 115.1 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Ogrenim ucreti ogrenci turune ve birime gore degisiyor. Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin.

Uretim Turu:
- Kural
```

### Q10: Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [x] tekrar
- **Sure**: 8086.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına girebilir miyorum? 

Elimdeki kaynaklarda göre, bu durumun ne olduğu net olarak ortaya çıkmadı. Ancak, genel olarak lisansüstü eğitim için kaynaklar irtibat kurabilir. Yarıyıl içi değerlendirmelerinde başarısız olan öğrenci, devamlı derslerde tekrar alabilir. Oysaki devamsızlık durumunda kaldığınız bir dersin bütünleme sınavına girebilir miyorsunuz?

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: yonerge_yabanci_dil_egitim_ogretim.pdf
```

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: vt (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] öğrenim ücreti
  - [ ] gerek yok
  - [ ] yönetim kurulu
  - [ ] sayılma
- **Sure**: 135.8 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Veritabanindaki en yakin kayit donemi 2026-Guz icin 26.08.2026 - 06.09.2026 tarihleri arasinda planlanmistir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- VT

Kaynak Ozeti:
- Veritabani kaydi: kayit donemi
```

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/4
  - [ ] transkript
  - [ ] Ek Madde
  - [ ] başvuru yapabilir
  - [x] GANO
- **Sure**: 2696.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Yatay gecis sureci icin en ilgili kaynakta su bilgi yer aliyor:
MADDE 3- (1) Bu Yönergede geçen; a) Birim: İlgili fakülte/yüksekokul/konservatuar/meslek yüksekokulunu, b) Birim yönetim kurulu: İlgili fakülte/yüksekokul/konservatuar/meslek yüksekokulu yönetim kurulunu, c) Diploma programı: Fakülte, yüksekokul, konservatuvar, meslek yüksekokulu veya bölümlerin belirlenen yeterlilikleri sağlayan öğrenciler için ön lisans veya lisans diploması düzenlenen yükseköğretim programlarını, ç) Düzey: Ön lisans veya lisans diploma programlarından her birini, d) Eşdeğer diploma programı: İsimleri aynı olan veya ilgili yönetim kurulları tarafından içeriklerinin en az yüzde sekseni aynı olduğu tespit edilen diploma programlarını, e) Farklı puan türü: Öğrenci Seçme ve Yerleştirme Sistemi’nde yükseköğretim programlarına yerleştirmede kullanılan puanların hesaplanmasında dikkate alınan puan çeşidini, f) Genel Ağırlıklı Not Ortalaması (GANO): Öğrencinin hazırlık sınıfı hariç, geçiş yapmak istediği döneme kadar almış olduğu tüm derslerin kredilerine göre ağırlıklı not ortalamasını, g) Kurum içi yatay geçiş: Ondokuz Mayıs Üniversitesinde aynı düzeydeki diğer diploma programlarına geçişi, ğ) Kurumlar arası yatay geçiş: Bir üniversite, yüksek teknoloji enstitüsü veya bir üniversiteye bağlı olmaksızın vakıflar tarafından kurulan meslek yüksekokullarından Ondokuz Mayıs Üniversitesindeki eşdeğer eğitim veren fakülte, yüksekokul veya bölüme yapılan geçişi, h) Merkezî sınav: Ölçme, Seçme ve Yerleştirme Merkezi (ÖSYM) tarafından yapılan merkezî sınavı, ı) Taban puan: Bir yükseköğretim kurumunun diploma programına Ölçme, Seçme ve Yerleştirme Merkezi (ÖSYM) tarafından merkezî sınavla yerleştirilen en düşük puanlı öğrencinin giriş puanını, i) Üniversite: Ondokuz Mayıs Üniversitesini, ifade eder. İKİNCİ BÖLÜM Genel İlkeler, Yatay geçiş ve Değerlendirme Genel ilkeler

(Kaynak: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsini
... (288 karakter daha)
```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/5
  - [ ] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Sure**: 5131.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Yatay gecis sureci icin en ilgili kaynakta su bilgi yer aliyor:
MADDE 8 – (1) Üniversitemize yatay geçiş başvuruları, yurt dışı yükseköğretim kurumlarındaki aynı düzeydeki eşdeğer diploma programlarından yapılır. (2) Yurt dışındaki yükseköğretim kurumlarından Üniversitemize yapılacak yatay geçiş kontenjanları Senato tarafından belirlenir. Kontenjanlar, her bir program için kurumlar arası yatay geçiş kontenjanının yarısını aşmayacak şekilde olur. Yurt dışı yükseköğretim kurumları kontenjanları, Üniversitemiz senatosu tarafından belirlenen başvuru şartları ve kurumlar arası yatay geçiş kontenjanları Yükseköğretim Kurulu’na en geç Haziran ayının otuzuncu günü mesai saati bitimine kadar bildirilir. Yurt dışı öğrenci kontenjanları ile başvuru şartları ve değerlendirme takvimi Yükseköğretim Kurulu internet sayfasında ilan edilir. (3)Yurt dışındaki yükseköğretim kurumlarından üniversitemize yatay geçiş için bu yönergenin 6’ncı maddesinin ikinci fıkrasında belirlenen kurumlar arası yatay geçiş başarı şartları aranır. (4)Yurt dışındaki yükseköğretim kurumlarından yatay geçiş yapılmak istenen programın ilgili sınıfına öğrenci kabulündeki taban puana sahip öğrenciler için yurt dışında yükseköğrenim gördükleri tüm derslerden başarılı olma şartı aranmaz. Bu yolla başvuran öğrencilerin yatay geçiş başvuruları, yurt dışı yatay geçiş kontenjanı kapsamı dışında değerlendirilir. (5) Yurt dışındaki yükseköğretim kurumlarından başvurularda öğrencinin yurt dışında öğrenim gördüğü yükseköğretim kurumunun ve eğitimin yapıldığı programın ön lisans veya lisans diploması vermeye yetkili bir kurum olarak Yükseköğretim Kurulu tarafından tanınması ve kayıtlı olduğu diploma programının Üniversitemizde yatay geçiş için başvurduğu ön lisans veya lisans diploma programına eşdeğerliğinin ilgili birim tarafından kabul edilmesi şartı aranır. (6) Yurt dışında yükseköğretime başlayan öğrencilerin Türkiye’deki yükseköğretim programlarına geçiş başvurularının değerlendirilmesinde, Yükseköğretim Kurulu tar
... (1033 karakter daha)
```

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] bağıl
  - [x] mutlak
  - [ ] 10
  - [x] öğrenci sayısı
- **Sure**: 6038.5 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Sorusa göre, bağlantılı değerlendirme sistemi ile mutlak değerlendirme arasındaki farkı arayorum.

Belirtilen kaynaklar incelendiğinde, bağlantılı değerlendirme sistemi ile mutlak değerlendirme arasındaki farkın, öğrencilerin yarıyıl/yıl içi (veya yıl içi) değerlendirme ile yarıyıl/yılsonu sınav notlarının oranına bağlı olduğu ortaya çıkıyor.

Bağlantıtlı değerlendirme sistemi (MADDE 23 Kaynak 1:

* Yarıyıl içi değerlendirmenin %40’ı ve yarıyıl sonu sınav notunun %60’ı toplansa
* Yarıyıl içi değerlendirme ve yarıyıl sonu sınavlarının başarı notuna katkı oranları anabilim/anasanat dalı teklifi, enstitü kurulunun kararı ve Senato onayı ile değiştirilebilir.

Mutlak değerlendirmenin olduğu sistemde ise;

* Yarıyıl içi değerlendirmenin %15’i ile yılsonu/bütünleme sınavında alınan notun %85’inin toplamı (KAYNAK 2)
* Yıl içi değerlendirmeden alınan puanın %50’si ile Yılsonu Sınav notunun %50'sinin toplamı (KAYNAK 3)

Ayrıca, belirtilen kaynaklarda her iki sistemin de öğrencilerin yarıyıl/yıl içi (veya yıl içi) değerlendirme ve yarıyıl/yılsonu sınav notlarının birlikte değerlendirilmesi ile elde edilen ham başarı notunun 4’lük not sistemindeki karşılığını ifade ettiği belirtiliyor.

Hangisi hangi öğrenci sayısında uygulanır?

Belgeler incelendiğinde, mutlak değerlendirme sistemi (KAYNAK 2 ve KAYNAK 3) uzaktan eğitim öğrencileri için önerilmemiş gibi görünüyor. Ancak, bağlantılı değerlendirme sisteminin uygulanacağı öğrenci sayısının tam bilinmemesinin sebebi belirtilmemiş.

Yanıt: Bu konularla ilgili elimdeki kaynaklarda tam net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: yabancı_dil_eğitim_öğretimi_yönergesi.pdf
```

### Q15: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 3/3
  - [x] diploma eki
  - [x] transkript
  - [x] yerine geçmez
- **Sure**: 2378.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Diploma ekini transkript yerine kullanabilir miyim? Diploma eki transkript (not çizelgesi) veya diploma yerine geçmez.

(Kaynak: sık_sorulan_sorular.txt)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/4
  - [ ] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [x] hak
- **Sure**: 3001.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
En ilgili ogrenci isleri kaynaginda su bilgi yer aliyor:
Yatay geçiş hakkı kazanıp kayıt yaptırmasam herhangi bir sorun olur mu? Üniversitemize yatay geçişle kayıt hakkı kazanıp, kayıt yaptırmamanız durumunda herhangi bir sorun olmayacaktır. Belirtilen süre sonunda kayıt yaptırmamanız halinde kayıtlı olduğunuz üniversitede öğreniminize devam edebilirsiniz. Hazırlık sınıfı okuduğum için transkriptim bulunmuyor. Ek Madde-1 (Merkezi Yerleştirme Puanı) ile yatay geçiş yapabilir miyim? Hazırlık sınıfı okuyan ve Ek Madde-1 kapsamında merkezi yerleştirme puanı ile yatay geçiş başvurusu yapmak isteyen adaylar, transkriptleri olmadan da başvuru yapabilirler. Ek Madde-1 kapsamında yapılan yatay geçiş başvurularında öğrencinin GANO'su değerlendirme aşamasında etkili değildir. Birden fazla üniversiteye yatay geçiş başvurusu yapabilir miyim? Farklı üniversitelere yatay geçiş başvurusu yapabilirsiniz. Birden çok yere kayıt hakkı kazanmanız durumunda, öğrenim görmek istediğiniz üniversiteye kaydınızı yaptırarak eğitiminize devam edebilirsiniz.

(Kaynak: sık_sorulan_sorular.txt)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 0/5
  - [ ] UBYS
  - [ ] ders seçimi
  - [ ] danışman
  - [ ] onay
  - [ ] yoklama
- **Sure**: 2705.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
ONDOKUZMAYIS ÜNİVERSİTESİ KAYIT SİLDİRME FORMU (LİSANS/ÖNLİSANS) ÖĞRENCİ BİLGİLERİ Öğrenci No T.C. Kimlik No Adı - Soyadı Fakülte/YO/MYO Akademik Yıl Bölümü/Programı Adres İlgili Birim Unvanı, Adı ve Soyadı İmzası Açıklamalar Kaydının silinmesi Bölüm Başkanı uygundur Harç Bürosu Borcu yoktur Güvenlik İlişiği yoktur Kütüphane ve Dokümantasyon Kütüphane ile ilişiği Daire Başkanlığı yoktur Okul Kütüphane Sorumlusu İlişiği yoktur (MYO'lar için) Öğrenci Kimlik Kartı PP1.3.FR.0052, R0, Mayıs 2019

(Kaynak: kayıt_sildirme_formu_lisans_önlisans.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

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
- **Key Facts**: 1/4
  - [x] itiraz
  - [ ] beş iş günü
  - [ ] dilekçe
  - [ ] bölüm başkanlığı
- **Sure**: 3996.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Sınav notuma itiraz etme süreci, süresi ve olası sonuçları şu şekilde işlemektedir:

Başvuru Süresi: Yüzde on hesaplamaları ilan edildikten sonra, 15 gün içerisinde fakülte/yüksekokuluna yazılı olarak başvurabilirsiniz.

Başvuru Yeri: Fakülte/yüksekokula

İtiraz Süresi: 15 gün

İtiraz Süreci: Yapılan başvurular, 15 gün içerisinde birim yönetim kurulunca karara bağlanır ve karar kesindir.

İtiraz Durumu: İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz.

Ancak, belgede sınav sonuçlarının ilan edileceği tarihler hakkında net bir bilgi bulunmamaktadır. Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

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
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/6
  - [x] ders
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [ ] ilişik kesme
  - [x] diploma
- **Sure**: 9917.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
MADDE 5 – (1) Öğrenim gördükleri programların bütün şartlarını yerine getirerek mezuniyet hakkı kazanan öğrenciler için, a)Hazırlık hariç dört yarıyıl süreli meslek yüksekokullarında bir mesleğe yönelik olarak yürütülmekte olan programlardan mezun olan öğrenciler için “Önlisans Diploması”, b)Türk Ceza Kanununun ikinci kitabının birinci babında yer alan, Devletin şahsiyetine karşı işlediği cürümler sebebiyle hüküm giyenler ile disiplin cezası alarak yükseköğretim kurumlarından uzaklaştırılanlar hariç olmak üzere, 2547 sayılı Kanun hükümleri uyarınca bir lisans programının en az ilk dört yarıyılının bütün derslerinden başarılı olanlara “Önlisans Diploması”, c)Hazırlık hariç, dört yıl süreli fakülte ve yüksekokul lisans programlarından mezun olan öğrenciler için “Lisans Diploması”, ç)Ana daldaki mezuniyetlerine bağlı olarak ikinci ana dal lisans programını tamamlayan öğrenciler için “Çift Ana dal Lisans Diploması” d)Ana daldaki mezuniyetlerine bağlı olarak yandal lisans programlarını tamamlayan öğrenciler için “Yandal Sertifikası” e) Enstitülerdeki tezli veya tezsiz yüksek lisans programlarını tamamlayanlara “Tezli Yüksek Lisans diploması” veya “Tezsiz Yüksek Lisans diploması”, f) Enstitülerdeki doktora veya sanatta yeterlik programlarını tamamlayanlara “Doktora” veya “Sanatta Yeterlik diploması” düzenlenir. Diplomaların dili ve şekli

(Kaynak: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
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
- **Sure**: 4396.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

Gerek diplomamı kayıp ilanına vermek gerekse e-devlette gösterilen mezuniyet bilgileri için, aşağıdaki adımları takip edebilirsiniz:

1. Diploma kayıp ilanına vermek için:
 - Bir yaygın gazete ilanını verin.
 - İlana ilişkin dilekçe, onaylı nüfus cüzdanı ve banka dekontu (diploma ücretini göstermek için) ile diploma aldığınız birimimize başvurun.
 - Diploma kayıp ilanı ile birlikte, başvuru dilekçesi ve onaylı nüfus cüzdanı suretiyle diploma aldığınız birimimize müracaat edin.
 - Bu başvuru yöntemine uyularak, diploma yenisi düzenlenecektir.

2. E-devlette gösterilen mezuniyet bilgileri için:
   - Mezuniyetten sonra mahkeme kararına dayalı nüfus kaydı değişikliği olması durumunda, mahkeme kararı, diploma ücretini yatırdığını gösteren banka dekontu, kimlik fotokopisi ve dilekçe ile başvurun.

3. Tahribata uğrayan belge için:
   - Tahribata uğrayan belge için de aynı başvuru yöntemini takip edin, belge aldığınız birime müracaat edin ve orijinal nüshada bulunan numaralar, kayıtlar ve imza sahiplerinin unvan, ad ve soyadlarını yazdırarak yeni belge düzenletilir.

Yine, e-devlette gösterilen mezuniyet bilgilerinin düzeltilmesi için, diploma yenisi düzenlenme adımı tamamlandıktan sonra başvurun.

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
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [ ] %40
  - [ ] %60
- **Sure**: 3605.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
MADDE 5 – (1) UELT uzaktan eğitim programı yıl esasına göre yapılır ve aşağıdaki esaslara göre yürütülür. a) UELT uzaktan eğitim programı iki yıllık bir lisans tamamlama programıdır. b) UELT uzaktan eğitim programında ders geçme sistemi uygulanır. Programın birinci sınıf derslerinden en çok üç tanesinden başarısız olan öğrenci ikinci sınıfın derslerini alır. c) UELT uzaktan eğitim programında üçten daha fazla dersten başarısız olan öğrenciler, bu dersleri tekrar ederler, ikinci sınıftan ders alamazlar. ç) Öğrencilerin Ebelik Lisans Tamamlama Programına kayıt olduğu tarihten itibaren dört yıl içinde tamamlamaları zorunludur. Bu süre sonunda programı tamamlamayan öğrencilerin ilgili lisans tamamlama programından kaydı silinerek, Üniversite ile ilişiği kesilir. Öğrencilerin kayıt yenilemedikleri öğretim yılları bu süre hesabına katılır. Derslerin veriliş şekli

(Kaynak: samsun_sağlık_yüksekokulu_eğitim_öğretim_ve_sınav_yönetmeliği.txt)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

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
- **Sure**: 16873.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınavda kopya çekilmesinin cezası ve disiplin süreci hakkındaki kural ve düzenlemeleri inceleyecek olur isek, kaynaklarımızdan edinilen bilgiler doğrultusunda aşağıdaki sonuca varabiliriz:

* Kopya çekme veya verdiklerin girişiminde bulunulması bir disiplin suçudur. (Kaynak 2, madde 12)
* Görev yapan gözetmen, sınavın sorunsuz bir biçimde yürütülmesinden sorumlu ve tam yetkili olmalıdır. Gözetmenler öğrencilerin yerlerini değiştirebilir veya sınav kurallarına aykırı davranışlarda bulunanları salondan çıkartabilir. (Kaynak 1, madde 6)
* Gözetmenler, sınav kurallarına aykırı davranışlarda bulunan öğrencilere kopya muamelesi yapabilir.
* öğrenciler, sınav esnasında cep telefonlarından faydalanmayacaktır. Telefonların sessizlik moduna veya uçuş moduna da konulamayacaktır. Telefonla ilgili herhangi bir şekilde ilgilenen öğrenciye kopya muamelesi yapılır.
* Sınavda kopya çekme veya verdiklerin girişiminde bulunulduğu tespiti, sınav görevlilerinden alınacak yetkili karar ile yapılacaktır.

Sonuç olarak, sınavda kopya çekilmesinin cezası olarak öğrenciler kopya muamelesine tabi tutulabilir. Görev yapan gözetmenler, sınav kurallarıyla ilgili yetkili ve sorumludurlar.

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
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: unknown (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [ ] birim
- **Sure**: 35.8 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Sorunuzun hangi alana ait oldugunu net olarak belirleyemedim. Asagidaki seceneklerden birini belirterek tekrar sorabilirsiniz:
- Ogrenci Isleri (kayit, not, staj, mezuniyet)
- Akademik Programlar (mufredat, yonetmelik, Erasmus)
- Finans (harc, burs, odeme)
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/4
  - [x] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Sure**: 15079.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
MADDE 31- (1) Öğrencilerin belgelendirecekleri önemli mazeretlerinin veya eğitimöğretimlerine katkıda bulunacak Üniversite dışı burs, staj, araştırma ve benzeri imkânların ortaya çıkması hâlinde, ilgili birimin yönetim kurulu kararı ile bir defada en fazla iki dönem/bir yıl olmak üzere, öğrenim süresi boyunca en fazla dört dönem/iki yıl kaydı dondurulabilir. Bu şekilde kayıt donduran öğrenci, öğrenimine devam edemez ve kayıt dondurduğu döneme/yıla ait sınavlara giremez. Kayıt dondurma süresinin bitiminde öğrenci; ayrıldığı dönemin/yılın başından başlamak koşuluyla, öğrenimine kaldığı yerden devam eder. Kayıt dondurulan dönem/dönemler, süre hesabında dikkate alınmaz. (2) Öğrenimini uzun süre engelleyecek önemli bir hastalık veya ilgili yönetim kurulunca kabul edilen haklı ve geçerli bir nedenle ve belgelendirilmek kaydıyla verilen izin, 8 inci maddede yer alan süreye eklenir. Kayıt dondurma süresinin bitiminde öğrenci; ayrıldığı dönemin/yılın başından başlamak koşuluyla, öğrenimine kaldığı yerden devam eder. (3) Haklı ve geçerli mazeretler şunlardır: a) Öğrencilerin sağlık kuruluşlarından alacakları ve öğrenimlerine en az bir dönem devam etmeleri yönünde sağlık engeli bulunduğunu belirten heyet raporuyla belgelendirilmiş bulunan sağlıkla ilgili mazeretleri. b) İlçelerde kaymakamlıklar, illerde valilikler tarafından verilecek bir belge ile belgelenmiş olması koşuluyla; öğrencinin öğrenimini en az bir dönem olumsuz etkileyecek düzeydeki tabii afetler veya maddi imkânsızlıklar. c) Belgelendirilmek şartıyla, birinci derecede akrabalarının ölümü veya ağır hastalığı gibi durumlarda bakacak başka bir kimsenin bulunmaması. ç) 18/8/2012 tarihli ve 28388 sayılı Resmî Gazete’de yayımlanan Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği hükümlerine göre; azami süreyi aşmamak kaydıyla öğrencinin öğrencilik sıfatını kaldırmayan veya ihracını gerektirmeyen mahkûmiyet veya tutukluluk hâlleri. d) Öğrencinin tecil hakkını kaybetmesi 
... (696 karakter daha)
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/3
  - [ ] danışman
  - [ ] bölüm
  - [ ] oidb@omu.edu.tr
- **Sure**: 116.1 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

Uretim Turu:
- Kural
```
