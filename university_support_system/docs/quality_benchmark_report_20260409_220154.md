# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-09 22:01:54
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 52.0% |
| Uretim Modu Dogrulugu | 24.0% |
| Anahtar Bilgi Kapsami | 34.0% |
| Temiz Kalite Orani | 96.0% |
| Ortalama Sure | 8116.3 ms |
| Medyan Sure | 7138.9 ms |
| Intent Analizi Aktif | 12/25 |
| Force LLM Sentez | 12/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | YANLIS (vt) | 0/4 | 1644.4 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 3/3 | 2427.0 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | YANLIS (unknown) | 1/4 | 74.5 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | YANLIS | OK | 3/4 | 2217.9 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | YANLIS | OK | 3/3 | 3734.9 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | YANLIS | YANLIS (kural) | 0/4 | 4620.3 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | YANLIS (vt) | 4/5 | 8075.3 | uydurma_riski |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | YANLIS (rag) | 2/5 | 781.9 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | YANLIS (kural) | 1/5 | 8878.4 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | YANLIS | OK | 2/4 | 22458.2 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | YANLIS | YANLIS (vt) | 0/4 | 6957.1 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | YANLIS (rag) | 1/4 | 7138.9 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | YANLIS | YANLIS (rag) | 2/5 | 23323.1 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 1/4 | 15232.0 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | YANLIS (rag) | 3/3 | 853.1 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | YANLIS (rag) | 2/4 | 7302.5 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | YANLIS (rag) | 0/5 | 12295.2 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 1/4 | 2255.1 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | YANLIS (rag) | 2/6 | 14705.3 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | YANLIS | YANLIS (rag) | 1/4 | 9426.3 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | YANLIS | YANLIS (rag) | 1/5 | 8158.3 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | YANLIS | YANLIS (rag) | 0/0 | 17348.8 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | YANLIS | YANLIS (unknown) | 0/4 | 6682.3 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | YANLIS (rag) | 1/4 | 11903.7 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | YANLIS (kural) | 0/3 | 4413.3 | - |

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
- **Sure**: 1644.4 ms
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
- **Sure**: 2427.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi?

Belge Baglami:
[Kaynak 1: sık_sorulan_sorular.txt]
Tek ders sınavına ne zaman başvurmam gerekir? Müfredatınızda tanımlı bütün dersleri almış fakat mezuniyetiniz için daha önce devam şartını sağladığınız tek dersinizin kalmış olması durumunda o dersten tek ders sınavına girebilirsiniz... Bu sorunun doğrudan yanıtını kaynakta bulmakta güçlük çekiyorum ve bu nedenle cevap vermekle ilgili bir bilgiye ulaşamadım.

Belge Baglami:
[Kaynak 3: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf]
Azami eğitim süresi sonunda kayıtlı olduğu öğretim programından mezun olabilmek için, son sınıf öğrencilerine alıp da başarısız oldukları bütün dersler için iki ek sınav hakkı verilir. Bu sınavlarda alınan not; ara sınav şartı aranmaksızın en az CC ise öğrenci, ilgili dersten başarılı sayılır. Ancak, staj tamamlatılmasına dair bir şart söz konusu değildir.

Sonuç olarak, Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi sorusuna net bir yanıt veremem, çünkü bu konudaki net bir bilgi elimdeki kaynaklarda bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
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
- **Sure**: 74.5 ms
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
- **Sure**: 2217.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Pedagojik formasyon dersleri transkripte dahil ediliyor mu?
Elimiğdekilerde net bilgi bulunamadı.

Mezuniyet ortalamasına etkisi var mı?
Elimiğdekilerde net bilgi bulunamadı.

Diplomada nasıl bir ibare yer alıyor?
Elimiğdekilerde bu konuda net bilgi bulunamadı.

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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3734.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sizi kislasiyormusum? 

Sen Uzman Isletmen, Ondokuz Mayis Universitesi (OMU) öğrenci işleri biriminden. 

Her soruya net ve düzgün bir şekilde cevap verecek ve sadece verıldıgı belge baglaminda gecen bilgileri kullanacagim.

Sorunuzu cevaplamağa başliyorum:

Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

Yanıt: 

Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretinizi Ondokuz Mayis Universitesi (OMU) Öğrenim Ücreti Ofisine yatırmalısınız. İkamet izni için ise aşağıdaki belgeleri hazırlamanız gerekmektedir. 

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı. Bu nedenle, öğrenci işleri birimi ile temasa geçirerek detaylı bilgi almanız önerilir.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4620.3 ms
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
- **Sure**: 8075.3 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Ders kaydı yaptıktan sonra danışmanınızın onay süreci işleyişi hakkında bilgi veriyorum:

Ders Kaydı Onay Süreci:

- Ders Kaydı: Kayıt yenileme döneminde harç ücretini yatırmanızın ardından, e-öğretim sistemi üzerinden seçeceğiniz dersler ve birimler için öğrenci portalına girip, "Ders Kayıt" sekmesine tıklamanız gerekir. Seçtiğiniz dersleriniz sisteme kaydedilir ve bir onay süreci başlar.
- Danışman Onayına Bakış:
  - Ogrenci Isleri departmanı verdigi bilgiye gore en yakin kayit donemi 2026-Guz icin 26.08.2026 - 06.09.2026 tarihleri arasinda planlanmistir. Bu tarih aralığında, danışman onayınızı gerçekleştirebilmeleri muhtemeldir.

- Finans Bilgisi:
  - Finans departmanı verdigi bilgiye gore, ogretim ucreti ogrenci turune ve birime gore degisiyor. Dogru ucreti paylasabilmem icin, Turk ogrenci misiniz, uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin. Bu bilgilere sahip olmak, hesabınızı doğru bir şekilde güncellemenizi ve harç ücretini doğru bir şekilde ödemelerini sağlayacaktır.

Dikkat Edilmesi Gerekenler:

* E-öğretim sistemi üzerinden seçeceğiniz dersler ve birimler için öğrenci portalına girip, "Ders Kayıt" sekmesine tıklamanız gerekir.
* Seçtiğiniz dersleriniz sisteme kaydedilir ve bir onay süreci başlar. 
* Bu onay süreci, genellikle 1-3 iş günü arasında tamamlanır.

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
- **Sure**: 781.9 ms
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
- **Sure**: 8878.4 ms
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
- **Key Facts**: 2/4
  - [ ] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [ ] tekrar
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 22458.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim?

Girebilirsiniz. Kaynak 1'e göre, klinik öncesi uygulama ve klinik uygulamaları tamamlanmazsa öğrenci, eksik kalanları bütünleme sınavından 2 gün öncesine kadar tamamlamış olmalıdır. Telafi süresi içinde eksik işlerin tamamlanması halinde öğrenciye blok veya klinik uygulama bütünleme sınavlarına girme hakkı tanınır.

Allah nasidir bu telafi süresini? 

Telafi süresi ilgili anabilim dalınca belirlenerek ve öğretim yılı başında öğrencilere duyurulur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 6957.1 ms
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
- **Sure**: 7138.9 ms
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
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 23323.1 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar:

Kurum içi yatay geçiş, Öndokuz Mayıs Üniversitesi içinde gerçekleşen geçişler için kullanılır. Burada, öğrenciler aynı üniversite içerisinde farklı programlara geçiş yapabilirler.

Kurumlar arası yatay geçiş ise, farklı üniversitelere ait programlara geçiş için kullanılır. Burada, öğrenciler farklı üniversite içerisinde farklı programlara geçiş yapabilirler.

Başvuru şartları ve değerlendirme kriterleri arasında aşağıdaki farklılıklar bulunmaktadır:

- Kurum içi yatay geçişlerde, öğrenciler Öndokuz Mayıs Üniversitesi Senatosu tarafından belirlenen kontenjanları kullanabilirler. Bu kontenjanlar, her bir program için kurum içi yatay geçiş kontenjanının yarısını aşmayacak şekilde belirlenir.
- Kurumlar arası yatay geçişlerde, öğrenciler Öndokuz Mayıs Üniversitesi Senatosu tarafından belirlenen kontenjanları kullanabilirler. Bu kontenjanlar, yurt dışı yükseköğretim kurumları kontenjanının yarısını aşayacak şekilde belirlenir.
- Kurum içi yatay geçişlerde, öğrencilerin yurt dışındaki yükseköğretim kurumlarındaki aynı düzeydeki eşdeğer diploma programlarından başvuruda bulunmaları gerekir.
- Kurumlar arası yatay geçişlerde, yurt dışı öğrenci kontenjanları ile başvuru şartları ve değerlendirme takvimi Yükseköğretim Kurulu internet sayfasında ilan edilir.
- Kurum içi yatay geçişlerde, başvurulan programın taban puana sahip öğrenciler için yurt içerisinde yükseköğrenim gördükleri tüm derslerden başarılı olma şartı aranmaz. 
- Kurumlar arası yatay geçişlerde, başvurulan programın taban puana sahip öğrenciler için yurt içerisinde yükseköğrenim gördükleri tüm derslerden başarılı olma şartı aranır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Akademik Programlar: RAG

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf

... (238 karakter daha)
```

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] bağıl
  - [x] mutlak
  - [ ] 10
  - [ ] öğrenci sayısı
- **Sure**: 15232.0 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Belirtilen bilgiler ışığında, bağlantılı değerlendirme sistemi ile mutlak değerlendirme arasındaki farkı ortaya koymaya çalışacağım:

Görüleceği üzere, bağlantılı değerlendirme sisteminde öğrencilerin yarıyıl içi değerlendirmesi ile yarıyıl sonu sınavı arasındaki oranlar belirlenmiştir. Buna göre, öğrencilerin başarı notu yarıyıl içi değerlendirmesinin %40’ı ile yarıyıl sonu sınavının %60’ı olan bir oranla hesaplanır. Bir başka ifadeyle, bağlantılı değerlendirme sisteminde öğrencilerin başarı notunu etkileyen faktörler birlikte değerlendirilir ve birbiriyle bağlantılı bir şekilde işlenir.

Diğer yandan, mutlak değerlendirme sistemi ise öğrencilerin başarı durumlarının yalnızca yarıyıl sonu sınavı veya bütünleme sınavı esas alınarak değerlendirildiği bir modeldir. Bu modele göre, öğrenci başarı notu yalnızca yarıyıl sonu sınavından aldığını notun %60’ı ile bütünlemede aldığını notun %40’ı olarak hesaplanır.

Örneğin, OMU'da bağlantılı değerlendirme sistemiyle çalışıldığından, öğrenci başarı notu yarıyıl içi Değerlendirmenin %40’ı ile yarıyıl sonu sınav notunun %60’ı toplanmak suretiyle hesaplanır. Bir başka deyişle, OMU'da bağlantılı değerlendirme sisteminin uygulanmasıyla, öğrenci başarı notunda yarıyıl içi değerlendirmenin oranı %40 olarak belirlenmiştir.

Sonuç olarak, OMU'da bağlantılı değerlendirme sistemi ile mutlak değerlendirme arasındaki fark, öğrenci başarı notunu hesapladığı şekilde ortak olmaktan çok farklılık gösterir.

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
- **Sure**: 853.1 ms
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
- **Sure**: 7302.5 ms
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 12295.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
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
- **Sure**: 2255.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Sınav notumuza itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

Sınav notumuza itiraz etmek istiyorsanız başvuru süreci aşağıdaki şekildedir:

1. İtiraz süresi: Yüzde on hesaplamaları ilan edildikten sonra, itirazı olan öğrenciler 15 gün içerisinde fakülte/yüksekokuluna yazılı olarak başvurabilirler.
2. Başvuru süresi: 15 gün
3. Yapılan başvurular: 15 gün içerisinde birim yönetim kurulunca karara bağlanır.

İtiraz sonucunda possible sonuçlar:

 * İtirazınız kabul edildiğinde notunuz yeniden hesaplanabilir ve değişebilir.
 * İtirazınız reddedildiğinde, önceki notunuz uygulanacaktır.
 * Yönetim Kurulunca verilen karar kesindir.

Lütfen 15 gün içerisinde itirazınızı yapmanız gerekir, yoksa bildirilen not ve not düzeltmeleri dikkate alınmayacaklardır.

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
- **Sure**: 14705.3 ms
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
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
```

### Q20: Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/4
  - [ ] 2. nüsha
  - [x] diploma
  - [ ] e-devlet
  - [ ] YÖKSİS
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 9426.3 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Ogrenci Isleri:
Eldeki en ilgili kaynakta su bilgi yer aliyor:
MADDE 17- (1) Diplomasını kaybedenler, yaygın gazetelerden birine diploma kayıp ilanı verirler. Kayıp ilanının yer aldığı gazete, başvuru dilekçesi ve onaylı nüfus cüzdanı sureti ve diploma ücretini yatırdıklarını gösteren banka dekontu ile diploma aldıkları birime müracaat ederler. Bu öğrencilere ilk diplomada yer alan bilgileri içeren yeni bir diploma düzenlenir ve üzerinde İkinci Nüsha olduğu bilgisi yer alır. (2) Bu uygulama esasları kapsam ve koşullarında hazırlanan diploma dışındaki diğer belgelerden birini kaybedenler yaygın gazetelerden birine kayıp ilanı verirler. Kayıp ilanının yer aldığı gazete, başvuru dilekçesi ve onaylı nüfus cüzdanı sureti ile belge aldıkları birime müracaat ederler. Bu durumda yeniden düzenlenecek belgelerde orijinal nüshada bulunan numaralar, kayıtlar ve imza sahiplerinin unvan, ad ve soyadları yazılır ve görev başında bulunan ilgili birimin Müdürü/Dekanı ve/veya Rektör tarafından imzalanır. (3) Tahribata uğrayan ancak orijinal şekil ile ibraz edilen belgeler için de aynı yol izlenerek yenisi verilir. Mahkeme kararına dayalı nüfus kaydı değişikliği

(Kaynak: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf)

Finans:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Finans: Kural

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: idari_ve_mali_işler_birimi.txt
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 8158.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
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
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: rag (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 17348.8 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Sınavda kopya çekilmesinin cezası olarak, sınav görevlilerince düzenlenen bireysel sınav iptal tutanağı düzenlenerek gerekli yasal işlemler başlatılır. Bu durumla ilgili olarak, öğrenciler hakkında gerekli yasal işlem başlatılır.

Bu durumun nasıl işlediği konusunda detayda yer alan bilgi ve kurallar şöyledir:

- Öğrenci kimlik belgesini yanlarında bulundurmayan öğrenci sınava giremez.
- Sınav sırasında kopya çekilmesinin cezası ile ilgili olarak, kopya çeken, çekmeye teşebbüs eden, kopya veren, alan veya kopya çekilmesine yardım edenler için, sınav görevlilerince düzenlenen bireysel sınav iptal tutanağı düzenlenerek gerekli yasal işlemler başlatılır.
- Görev yapan gözetmen, sınavin sorunsuz bir biçimde yürütülmesinden sorumludur. Gözetmenler öğrencilerin yerlerini değiştirebilir veya sınav kurallarına aykırı davranışlarda bulunanları salondan çıkartabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG
- Ogrenci Isleri: RAG

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_ortak_sınav_yönergesi.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: hizmet_içi_eğitim_yönergesi.pdf
- Belge: özel_yetenek_sınavı_yönergesi.pdf
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf
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
- **Sure**: 6682.3 ms
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 11903.7 ms
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 4413.3 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

Uretim Turu:
- Kural
```
