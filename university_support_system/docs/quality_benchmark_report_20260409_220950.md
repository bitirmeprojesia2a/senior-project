# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-09 22:09:50
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 60.0% |
| Uretim Modu Dogrulugu | 16.0% |
| Anahtar Bilgi Kapsami | 36.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 7113.6 ms |
| Medyan Sure | 7549.9 ms |
| Intent Analizi Aktif | 13/25 |
| Force LLM Sentez | 13/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | YANLIS (vt) | 0/4 | 1104.8 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 3/3 | 1362.9 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | YANLIS (unknown) | 1/4 | 60.8 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | YANLIS | OK | 3/4 | 1435.6 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | YANLIS | OK | 2/3 | 11811.7 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | YANLIS | YANLIS (kural) | 0/4 | 6662.4 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | YANLIS (vt) | 3/5 | 4000.0 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | YANLIS (rag) | 2/5 | 465.8 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | YANLIS (kural) | 1/5 | 6690.3 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | YANLIS | YANLIS (rag) | 2/4 | 8459.9 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | YANLIS | YANLIS (vt) | 0/4 | 6849.8 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | YANLIS (rag) | 2/4 | 8076.0 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | YANLIS | YANLIS (rag) | 2/5 | 17907.0 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | YANLIS (rag) | 1/4 | 13642.9 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | YANLIS (rag) | 3/3 | 472.9 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | YANLIS (rag) | 2/4 | 7549.9 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | YANLIS (rag) | 1/5 | 11284.3 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 1/4 | 4356.2 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | YANLIS (rag) | 2/6 | 14497.3 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | YANLIS (rag) | 1/4 | 8536.3 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | YANLIS | YANLIS (rag) | 1/5 | 8019.5 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (rag) | 0/0 | 8163.0 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | YANLIS | YANLIS (rag) | 2/4 | 13005.2 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | YANLIS (rag) | 1/4 | 11982.0 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | YANLIS (kural) | 0/3 | 1443.0 | - |

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 1104.8 ms
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
- **Key Facts**: 3/3
  - [x] staj
  - [x] tamamla
  - [x] CC
- **Sure**: 1362.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Soruya cevap olarak:

Ders sınavına girebilmek için stajınızı tamamlamış olmak gerekmez. Kaynaklarımda stajın bir gereklilik olduğu bilgiye rastlamadım.

Notunuz için minimum CC notunuz olması gerekir, çünkü kaynaklarda sınavlarda notun CC olması durumunda başarılı sayıldığı yer yer almıştır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
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
- **Sure**: 60.8 ms
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
- **Sure**: 1435.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Soru: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

Cevap: Pedagojik formasyon dersleri transkript içerisinde yer alabilir mi, bu sorunun yanıtını elimdeki kaynaklar ile vermem olabilir. Ancak, mezuniyet ortalamasına etkisi ile ilgili olarak, transkriptte yer alan notlar mezuniyet ortalamasına etkileyebilmektedir. Ancak bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

Not: Transkript belgesinin 1 (bir) adedi ücretsiz olup, birden fazla talep olması halinde 3 (üç) adet transkript alabilmektedir. Bu durum, öğrencinin mezuniyet ortalamasıyla ilişkili olarak belirtilmemiştir.

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
- **Key Facts**: 2/3
  - [x] ücret
  - [ ] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 11811.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi yatırmak için ÖİDB Katkı Payı ve Öğrenim Ücreti Ofisine başvurmanız gerekir. İlgili bilgiler daha detaylı olarak aşağıdaki belgeden açıkça görülmektedir.

[Kaynak 2: öğrenci_işleri_birimi.txt]
...

Görev Adı: ÖİDB Katkı Payı ve Öğrenim Ücreti Ofisi Personeli Kod: GT158 
Öğrencilerin kayıt yaptırdığı program düzeyinde bilgi yönetim sisteminden borçlandırma işlemini yapmak ve ödemelerini takip etmek.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı. İmza karşılığı bir belge olarak ÖİDB Katkı Payı ve Öğrenim Ücreti Ofisine yönlendirilmesi önerilir.

İkamet izni için hangi belgeleri hazırlamalıyım?
Aynı belgede, Yabancı uyruklu öğrencilerin ders kayıtlanma durumunu göç idaresine göndermek ile alakalı bilgi yer almaktadır.

 [Kaynak 3: öğrenci_işleri_birimi.txt]
Her eğitim öğretim döneminde yabancı uyruklu öğrencilerin ders kayıtlanma durumunu göç idaresine göndermek...

Belgeleri hazırlamak için ÖİDB'e danışılması gerekir.

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
- **Sure**: 6662.4 ms
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
- **Key Facts**: 3/5
  - [ ] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Sure**: 4000.0 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Ders kaydın ardından danışman onay aşaması nasıl işliyor?

Öncelikle 2026-Güz dönemine ait kayıt tarihlerini öğrenmek önemlidir. Ogrenci Isleri departmanı tarafından verdiğiniz bilgilere göre, 2026-Güz dönemine ait tarihler 26 Ağustos 2026 - 06 Eylül 2026 arasında planlıymış gibi görünmektedir.

Ders kaydını yapabilmeniz için önce eğitim ücretini yatırmış olmanız gerekir. Finans departmanı tarafından verilen bilgiye göre, eğitim ücreti öğrenci türüne ve birimine göre değişmektedir. Doğru ücreti almak için, uluslar arası öğrenci misiniz, Türköğrenci misiniz, fakülte ya da bölüm bilgilerinizi belirtmeniz yararlı olacaktır.

Ders kaydınızı yapabilmek için, önce Finans departmanından eğitim ücretinizi onaylatın. Eğitim ücretinizi onayladıktan sonra, Ogreni Isleri departmanına başvurun ve kayıt işlemlerinizi tamamlayın. Danışman onay aşamasına gelecek ve gerekli işlemleri tamamlayarak ders kayıtlarınızı tamamlamanız kolay olacaktır. Ayrıntılı bilgi talepleriniz durumunda ilgili departmanlarla iletişime geçebilirsiniz.

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
- **Sure**: 465.8 ms
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
- **Sure**: 6690.3 ms
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
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/4
  - [x] giremez
  - [ ] devamsızlık
  - [x] bütünleme
  - [ ] tekrar
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 8459.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
MADDE 21 – (1) Mesleki dersler kapsamında ilk üç yılda edinilen bilgi, beceri, tutum ve davranışların klinik uygulamaya nasıl aktarılacağını diş hekimliği disiplinleri kliniklerinde gözlemlemek ve kliniğe hazırlık amacıyla öğretim elemanları rehberliğinde basit uygulamalara katılmak üzere 3. sınıfta öğrencilere klinik gözlem eğitimi yaptırılır. (2) Klinik öncesi uygulama, klinik gözlem ve klinik uygulamaların içeriği, cinsi, niteliği ve sayısı ilgili anabilim dalı tarafından belirlenir ve öğretim yılı başında öğrencilere duyurulur. (3) Eğitim-öğretim yılı başında anabilim dalı tarafından belirlenerek ilan edilen sayıdaki klinik öncesi uygulama, klinik gözlem ve klinik uygulamaların, verilen sürede tamamlanarak teslim edilmesi zorunludur. Belirtilen sayı/puan ve nitelikteki uygulamaları tamamlayamayan veya başarılı olamayan öğrenci, klinik öncesi uygulama blok yılsonu sınavına ve klinik uygulama sonu sınavına alınmaz. (4) Klinik öncesi uygulama, klinik gözlem ve klinik uygulamalarını süresi içerisinde tamamlayamayan öğrenciler, eksik kalan klinik öncesi uygulama ve klinik uygulamalarını bütünleme sınavından 2 gün öncesine kadar tamamlamış olmalıdır. Telafi süresinin ne zaman ve ne şekilde verileceği ilgili anabilim dalınca belirlenerek öğretim yılı başında öğrencilere duyurulur. Telafi süresi içinde eksik işlerin tamamlanması halinde öğrenciye blok veya klinik uygulama bütünleme sınavlarına girme hakkı tanınır. (5) Klinik öncesi uygulama ve klinik uygulamalarını verilen telafi süresinde de tamamlayamayan öğrenci bütünleme sınavına giremez ve blok veya klinik uygulama derslerinden başarısız sayılır. BEŞİNCİ BÖLÜM Ölçme ve Değerlendirme, Sınavlar, Sınavların Yapılış Şekli ve Uygulama Esasları Ölçme ve değerlendirme

(Kaynak: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Ile
... (283 karakter daha)
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
- **Sure**: 6849.8 ms
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
- **Key Facts**: 2/4
  - [ ] transkript
  - [x] Ek Madde
  - [ ] başvuru yapabilir
  - [x] GANO
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 8076.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
▪ Yatay geçiş hakkı kazanan öğrencilerin kayıt işlemleri yüz yüze yapılacak olup, ilan edilen tarihlerde kayıtlarını yaptırmaları gerekecektir. Belirtilen tarihlerde kaydını yaptırmayan öğrenciler kayıt hakkını kaybedeceklerdir. ▪ Ek Madde-1 (Merkezi Yerleşme Puanı) başvurusu için ÖSYS/YKS ile yerleşenler Başvuru modülünde 1. Grubu, DGS ile yerleşenler 2. Grubu seçerek tercih yapacaklardır. ▪ Ek Madde-1 ile Üniversitemizden başka bir üniversiteye yatay geçiş yapıp geri dönme hakkını kullanmak isteyen öğrencilerin, ilgili akademik birimlere dilekçe ile başvuru yapması gerekmektedir. ▪ Başvuru türüne bakılmaksızın bir dönemde en fazla 2 yatay geçiş başvurusu yapılabilir. ▪ Sisteme yansıyan YÖKSİS bilgilerinin doğruluğu öğrencinin öğrenim gördüğü üniversitenin sorumluluğundadır. YÖKSİS bilgilerinde yanlışlık olan öğrenciler (sınıf/dönem bilgisi, GANO, YKS puanları vb.) öğrenim gördükleri üniversite ile irtibat kurarak durumlarının düzeltilmesini

(Kaynak: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 17907.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

Kurum içi yatay geçiş, Ondokuz Mayıs Üniversitesi'ne bağlı bulunan fakülteler ve bölümler arasında yapılan bir geçiş türüdür. Diğer taraftan, kurumlar arası yatay geçiş Ondokuz Mayıs Üniversitesi'ne bağlı bulunan fakülteler ve bölümler ile diğer üniversiteler arasında yapılan bir geçiş türüdür.

Kurumlar arası yatay geçiş, yurt dışı diploma programlarından da yapılabilmektedir. Bu geçiş türü için, Yükseköğretim Kurulu'na en geç Haziran ayının otuzuncu günü mesai saati bitimine kadar yurt dışı yükseköğretim kurumları kontenjanları ve başvuru şartları bildirilir.

Başvuru şartları ve değerlendirme kriterleri farklılık gösterirken, kurum içi yatay geçiş başvuruları, üniversitenin kendi içerisinde yapılan başvurular olduğu için daha esnektir. Já kurumlardan arası geçiş başvuruları, daha katı kurallar ve şartlar çerçevesinde yapılır.

Detaylı olarak bakıldığında, kurum içi yatay geçiş başvuruları, yatay geçiş başarı şartları açısından daha esnektir. Já kurumlardan arası geçiş başvuruları, yurt dışında öğrenim gördüğü yükseköğretim kurumunun ve eğitimin yapıldığı programın ön lisans veya lisans diploması vermeye yetkili bir kurum olarak Yükseköğretim Kurulu'na bildirmek gerekir.

Yine, kurum içi yatay geçiş başvuruları, kontenjanın tamamından faydalanılmak mümkündür. Já kurumlardan arası geçiş başvuruları, bu kontenjanların yarısından fazla tercih edilememektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Akademik Programlar: RAG

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gec
... (86 karakter daha)
```

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/4
  - [x] bağıl
  - [ ] mutlak
  - [ ] 10
  - [ ] öğrenci sayısı
- **Sure**: 13642.9 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
MADDE 25- (1) 5. sınıfın sonunda evre üç olarak tanımlanan sürece ait tüm eğitim etkinliklerini başarı ile tamamlayan öğrenciler Aile Hekimliği eğitimine başlarlar. a) Öğrenci, eğitim gördüğü anabilim dalı tarafından hazırlanmış ve program kurulu tarafından onaylanmış eğitim programına göre eğitimlerini sürdürür. Uygulanan program çerçevesinde anabilim dalı çalışma koşullarına uymak, sağlık hizmetleri ve laboratuvar çalışmalarına mesai ve mesai dışı saatlerde (nöbet) katılmak, hasta viziti, vaka takdimi, konferans, seminer ve benzeri etkinliklere katılmak ve bu etkinliklerle ilgili görevlendirmeleri bizzat yapmak zorundadırlar. Öğrenciler, ilgili stajın beceri karnesinde yer alan ve yapılması gereken uygulamaları sorumlu öğretim elemanına onaylatmakla yükümlüdür. 4. sınıf öğrencilerinin stajlarda alacağı puanlar, Tablo 4'e göre belirlenir. b) Fakültemiz aile hekimliği yılı öğrencilerinden eğitiminin en fazla üç aylık dilimini başka fakültelerde tamamlamak isteyenlerin başvuruları, ilgili anabilim dalının ve staj yapılacak fakültenin olumlu görüşü alınmak koşuluyla Fakülte Yönetim Kurulunun kararı ile gerçekleşebilir. Başvurular, öğrenci için ilgili staj başlama tarihinden en az iki ay önce yapılmalıdır. c) Ülkemizdeki diğer tıp fakülteleri ile yabancı tıp fakültelerinin aile hekimliği yılı öğrencileri, kendi fakültesinin izni ve Fakültemiz Yönetim Kurulu'nun kararı ile stajlardan bir ya da birkaçını Fakültemiz bünyesinde yapabilirler. ç) 6. sınıf öğrencileri mezun olabilmek için intörnlüğe başladığı tarihten itibaren yapılan gelişim sınavlarının en az birinde toplam soru sayısının %25 oranında net yapmak zorundadır. Gelişim PP.1.2.PRS.0021, R3, Şubat 2026 Sayfa 11 / 14 sınavlarında aldığı puan ortalaması, bağıl değerlendirme üzerinden sene sonu puan ortalamasına %5 oranında katılır. d) Aile hekimliği öğrencileri staj değerlendirme formlarında belirlenen kriterlere göre değerlendirilir. e) Başarısız olan öğrenciler için 
... (936 karakter daha)
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
- **Sure**: 472.9 ms
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 7549.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
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
- **Key Facts**: 1/5
  - [ ] UBYS
  - [ ] ders seçimi
  - [ ] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 11284.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
Öğrencinin kayıt olmak istediği derste değişiklik yaptığımda öğrenciye bilgi vermek zorunda mıyım? Evet. Öğrenci ders kaydının kesin kayda dönüştüğünü görüp, dersleri tek tek kontrol etmeyebilir. Bu durumda ise sizin tarafınızdan değiştirilmiş dersi fark etmeme sonucunda, seçmemiş olduğu derse devam etme gibi olumsuz durumlar meydana gelmektedir. O nedenle ders değişikliği ile ilgili olarak öğrenci ile bilgi paylaşılması önemlidir. Öğrenci tarafından onaya gönderilen ve tarafımca onayı gerçekleştirilen ders kaydının, doğru olup olmadığını öğrenci ile birlikte ne zaman kontrol edebilirim? Akademik takvimde tanımlanan ekle-sil haftasında kontrol edebilir, hata varsa düzeltme yoluna gidebilirsiniz. Kesin kayda dönüştürdüğüm fakat değişiklik yapmak istediğim kaydı nasıl açtırabilirim? Biriminizde görevli, yetkilendirilmiş personellere ulaşarak kesin kaydı açtırabileceksiniz.

(Kaynak: sık_sorulan_sorular.txt)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
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
- **Sure**: 4356.2 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Sınav notuma itiraz etmek istediğiniz için gerekli bilgileri sunacağım.

MUTLAK KURALLARA UYGUN OLARAK:

1. Başvuru Süresi: 
Sınav notuna itiraz etmek isteyen öğrenciler, yüzde on hesaplamlarının ilan edilmesinden itibaren en geç 15 gün içerisinde fakülte/yüksekokuluna yazılı olarak başvurabilirler. 

2.Başvuru Süresi Bitim Tarihi:
Sınav notuna itiraz başvuruları 15 gün içerisinde birim yönetim kurulunca karara bağlanır.

3. Sonuçlar:
İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz. Yönetim Kurulunca verilen karar kesindir.

DİKKAT: Bu bilgilerin doğruluğunu kaynak belgelerinden doğrulayınız.

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
- **Sure**: 14497.3 ms
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
```

### Q20: Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/4
  - [ ] 2. nüsha
  - [x] diploma
  - [ ] e-devlet
  - [ ] YÖKSİS
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 8536.3 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
MADDE 17- (1) Diplomasını kaybedenler, yaygın gazetelerden birine diploma kayıp ilanı verirler. Kayıp ilanının yer aldığı gazete, başvuru dilekçesi ve onaylı nüfus cüzdanı sureti ve diploma ücretini yatırdıklarını gösteren banka dekontu ile diploma aldıkları birime müracaat ederler. Bu öğrencilere ilk diplomada yer alan bilgileri içeren yeni bir diploma düzenlenir ve üzerinde İkinci Nüsha olduğu bilgisi yer alır. (2) Bu uygulama esasları kapsam ve koşullarında hazırlanan diploma dışındaki diğer belgelerden birini kaybedenler yaygın gazetelerden birine kayıp ilanı verirler. Kayıp ilanının yer aldığı gazete, başvuru dilekçesi ve onaylı nüfus cüzdanı sureti ile belge aldıkları birime müracaat ederler. Bu durumda yeniden düzenlenecek belgelerde orijinal nüshada bulunan numaralar, kayıtlar ve imza sahiplerinin unvan, ad ve soyadları yazılır ve görev başında bulunan ilgili birimin Müdürü/Dekanı ve/veya Rektör tarafından imzalanır. (3) Tahribata uğrayan ancak orijinal şekil ile ibraz edilen belgeler için de aynı yol izlenerek yenisi verilir. Mahkeme kararına dayalı nüfus kaydı değişikliği

(Kaynak: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
```

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs', 'academic_programs']) - YANLIS
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [ ] %40
  - [ ] %60
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 8019.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
MADDE 5 – (1) Üniversite birimlerinde örgün ve/veya uzaktan eğitim-öğretim uygulanır. Eğitim ve öğretim dönem ve/veya yıl esasına göre düzenlenir. Eğitimin dönem esasına göre benimsenmesi halinde bazı dersler yıl, yıl esasına göre benimsenmesi halinde ise bazı dersler dönem esasına göre de programlanabilir. (2) Türk Dili, Yabancı Dil, Atatürk İlkeleri ve İnkılap Tarihi, İş Sağlığı ve Güvenliği, Mesleki Yabancı Dil, Seçmeli Yabancı Dil, formasyon dersleri ile gerektiğinde diğer dersler ilgili birim kurullarının kararı ile mesai saatleri dışında veya millî ve dinî bayramlar dışındaki cumartesi veya pazar günleri de yapılabilir. Bu dersler örgün veya uzaktan eğitim ile de verilebilir. Akademik takvim

(Kaynak: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 8163.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
sırasında ve sınav salonundan çıkana kadar cep telefonu ile herhangi bir şekilde ilgilenen öğrenciye kopya muamelesi yapılır. 4. Her öğrenci, sınavda kendisine ait malzemeleri kullanmak zorundadır. Hesap makinesi, kalem, silgi veya kullanımına izin verilen tablo gibi araç ve gereçlerin başka bir öğrenci ile paylaşılması yasaktır. Bu tür paylaşımlar kopya olarak değerlendirilir. 5. Hesap makinesi kullanılmasına izin verilen sınavlarda, alfabetik tuş takımı olan, veri kaydedilebilen ve/veya programlama özelliği olan hesap makinaları kullanılamaz. 6. Sınav salonlarında görev yapan gözetmen, sınavın sorunsuz bir biçimde yürütülmesinden sorumludur ve bu konuda tam yetkilidir. Gözetmenler öğrencilerin yerlerini değiştirebilir veya sınav kurallarına aykırı davranışlarda bulunanları salondan çıkartabilir. Öğrenciler sınav görevlilerinin her türlü uyarısına uymak zorundadır. 7. Her öğrenci oturduğu sırada, yerde veya duvarda yazılı olabilecek ders notlarından kendisi yazmamış olsa bile

(Kaynak: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [x] form
  - [x] birim
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 13005.2 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Ogrenci Isleri:
Eldeki en ilgili kaynakta su bilgi yer aliyor:
Danışmanın kayıt olmak istediğim derslerde değişiklik yapma hakkı var mıdır? Evet. Ondokuz Mayıs Üniversitesi Ön Lisans ve Lisans Eğitim Öğretim Yönetmeliği hükümleri kapsamında danışman bu hakkını kullanabilir. Kayıt olacağım derslere devam şartım yoksa yine de ders kaydı yaptırmalı mıyım? Devam şartınız olmasa bile derslerin sınavlarına girebilmek için ders kaydı yapmanız gerekmektedir. Ders ekleme/çıkarma nedir? Bu işlemi nasıl yapmalıyım? Seçmiş olduğunuz derslerden açılmayan seçmeli ders olduğunda veya değiştirmek istediğiniz dersler için Akademik Takvimde belirtilen süreler içerisinde danışmanınızla irtibata geçerek yapabileceğiniz işlemdir. 5-i derslerini (TürkDili, Yabancı Dil ve Atatürk İlke ve İnkılap Tarihi derslerini) uzaktan eğitim yolu ile alabilir miyim? 5-i dersleri için uzaktan eğitim şubesi açılmış ise dersi uzaktan eğitim yolu ile alabilirsiniz.

(Kaynak: sık_sorulan_sorular.txt)

Finans:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Finans: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: zorunlu_gönüllü_staj_başvuru_formu.pdf
- Belge: kayıt_sildirme_formu_lisans_önlisans.pdf
- Belge: idari_ve_mali_işler_birimi.txt
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 11982.0 ms
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 1443.0 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

Uretim Turu:
- Kural
```
