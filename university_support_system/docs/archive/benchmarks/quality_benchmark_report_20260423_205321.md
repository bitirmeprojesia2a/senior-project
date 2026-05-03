# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-23 20:53:21
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 92.0% |
| Anahtar Bilgi Kapsami | 57.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 11709.9 ms |
| Medyan Sure | 10779.7 ms |
| Intent Analizi Aktif | 0/25 |
| Force LLM Sentez | 0/25 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=25, query_failures=0, agent_tasks=42, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 14415.9 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 3/3 | 16845.8 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 1/4 | 10545.0 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 4/4 | 8467.9 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 13033.9 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | YANLIS (vt) | 0/4 | 10761.8 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 9251.3 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 3/5 | 9777.1 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 4/5 | 15191.6 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 11803.7 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 3/4 | 9228.6 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 3/4 | 7677.0 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 1/5 | 16164.8 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 3/4 | 12620.9 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 2/3 | 9221.1 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 13973.5 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 4/5 | 8164.2 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 2/4 | 8367.7 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 3/6 | 12365.0 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 10779.7 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 2/5 | 18696.8 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 16244.4 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 11911.2 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 8833.5 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 1/3 | 8405.0 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs', 'announcement'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Sure**: 14415.9 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
Benchmark, Yanit:
Yatay geçişle gelen bir öğrencinin muafiyet başvurusu yapmadan önce, müfredatlarında yer alan bütün dersleri almış olması gerekmektedir. Derslerin tamamını başarmış olma şartı aranmaz. Yatay geçişle gelen öğrencinin derslere devam etmemesi beklenmez; aksine akademik takvimde belirtilen ders kayıt ve ekleme sürelerin sonuna kadar dönem derslerine devam etmeniz önemle belirtmektedir.

Kaynak 2'de belirtildiği gibi, kurumlararası ve kurum içi yatay geçiş başvuruları belirtilen tarihte gerçekleştirilecek olup, ilan edilen süreler dışında işlem talebi için herhangi bir mazeret kabul edilmeyecektir.

Yanıt 4'üncü Maddede belirtildiği üzere, yatay geçişle gelen öğrencilerin staj derslerine ait muafiyet talepleri, kesin kayıtlarının yapıldığı yarıyıl sonuna kadar alınır.

Ders yeterlik başvurusu, akademik takvimde belirtilen tarihe kadar yapılmalıdır. Öğrenciler tarafından belgelendirilen ya da yazılı olarak beyan edilen yeterlik durumları dersin içeriğiyle uyumlu olanlar; ders yeterlik sınavından başarılı olmaları durumunda, ilgili derslerden muaf sayılırlar ve sınavdan aldıkları puanlar, ders notu olarak transkriptlerine işlenir.

Ilgili duyurular:
1. 2025-2026 Eğitim Öğretim Yılı Bahar Yarıyılı Yatay Geçiş Yedek sonuçları (2026-02-13)
 Kayıt hakkı kazanan adaylar, aşağıda yer alan kayıt duyurusunu dikkatlice inceleyerek belirtilen tarihlerde, kayıt için gerekli belgelerle birlikte şahsen başvurarak kayıtlarını yaptırabilirler. Eksik veya onaysız belge ile başvuran öğrencilerin ya da başvuru esnasındaki beyan...
 Detay: https://www.omu.edu.tr/tr/icerik/duyuru/2025-2026-egitim-ogretim-yili-bahar-yariyili-yatay-gecis-yedek-sonuclari
 Ek baglanti: Yedek Kayıt Duyurusu (Kayıt Tarihleri, Kayıt Yerleri ve Gerekli Belgeler) - https://oidb.omu.edu.tr/tr/haberler/2025-2026-eitim-retim-yl-bahar-yaryl-yatay-gei-yedek-sonular/Yedek%20Kay%C4%B1t%20Duyurusu%20(Kay%C4%B1t%20Tarihleri,%20Kay%C4%B1t%20Yerleri%20ve%20Gerekli%20Belgeler).pdf
 Ek baglanti: Yedekten Kayıt Ha
... (1866 karakter daha)
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
- **Sure**: 16845.8 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Tek Ders Sınavına Girebilmek İçin Şartlar

1. Staj Tamamlanması: Staj dersini tamamlamış olmanız gerekmez. Staj tamamlanmamış öğrenciler de sınavlara girebilir.
2. Sınavda Başarı: Sınavda başarılı sayılmak için minimum not CC olarak belirtilmektedir. Bu ise, ders notunun en az 60 olması anlamına gelir.

Not:

* Tek ders sınavına girebilmek için staj dersini tamamlamak zorunda olmayıp, staj tamamlanmamış olarak da sınavlara giriş mümkündür.
* 60'lı not almanız durumunda ilgili dersle ilgili olarak başarılı sayılacaksınız.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Key Facts**: 1/4
  - [ ] değiştirebilir
  - [ ] devam koşulu
  - [ ] yeni
  - [x] ders
- **Sure**: 10545.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

Belirli bir seçmeli dersin başarı elde edilemediği ve yerine başka bir seçmeli ders seçilmesinin durumunu değerlendirdiğimizde, devam zorunluluğun değişimine ilişkin hükümler hakkında bilgi sahibi olma gerekliliği ortaya çıkmaktadır.

Bu konuyla ilgili olarak, yaptığım araştırma kapsamında kaynaklarda aşağıdaki hüküm bulunmuştur:

"Öğrenci; danışmanın onayıyla, başarısız olduğu bir seçmeli ders yerine, sonraki dönemde/yılda devam etmek kaydıyla, bir başka seçmeli dersi alabilir." (Kaynak 1: yonetmelik_onlisans_lisans_egitim_ogretim.pdf, Madde 19)

Ayrıca, devam zorunluluğunun yerine getirilmesi hususunda, kaynaklarımıza göre:

"Derslere devam durumu, dersin öğretim elemanınca yapılan yoklamalarla tespit edilir. Örgün eğitimde öğrencilerin yüz yüze yürütülen derslerin teorik saatlerinin en az % 70’ine; ders uygulamaları, atölye ve laboratuvarların ise en az % 80’ine devam etmeleri zorunludur. Bu oranlar, uzaktan eğitim yoluyla verilen örgün eğitim derslerinde aynı sırayla % 80 ve % 90 olarak uygulanır." (Kaynak 1: yonetmelik_onlisans_lisans_egitim_ogretim.pdf, Madde 17)

Bu hükümlere göre, başarısız olduğum seçmeli ders yerine başka bir seçmeli ders seçtiğimde, devam zorunluluğu devam eder. Ancak, bu hususta belirtilmemişse, devam zorunluluğun yerine getirilmesi hususunda, öğrencinin yüz yüze yürütülen derslerin teorik saatlerinin en az % 70’ine, ders uygulamaları, atölye ve laboratuvarların ise en az % 80’ine devam edeceğidir.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

Bu cevaplarda kullanılan bilgiler esas olarak aşağıdaki kaynaklardır:
Kaynak 1: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
Kaynak 2: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
Kaynak 3: yaz_okulu_eğitim_öğretim.pdf
Kaynak 4: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf

Yanit: Bu konuya ilişkin yukarida verilen bilgiyi esas olarak alan cevabım budur.

---
Daha iyi yardimci olab
... (337 karakter daha)
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
- **Sure**: 8467.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Pedagojik formasyon dersleri transkripte dahil ediliyor mu?
Evet, pedagojik formasyon dersleri transkripte dahil edilecektir (Kaynak 3).

Mezuniyet ortalamasına etkisi var mı?
Evet, pedagojik formasyon dersleri Mezuniyet ortalamasına dahil edilecektir (Kaynak 1).

Diplomada nasıl bir ibare yer alacak?
Diplomaların arkasına “Pedagojik formasyon eğitimini tamamlamıştır.” ifadesi yazılacaktır (Kaynak 1).

Pedagojik formasyon derslerinin tamamlanması zorunlu mudur?
Hayır, pedagojik formasyon dersleri alımı talepline bağlıdır ve tamamlanması zorunlu değildir (Kaynak 3).

Son sınıf öğrencisi olup kayıtlı olduğu programın mezuniyet için gerekli tüm şartlarını yerine getiren öğrenciler, pedagojik formasyon eğitimi uygulamasından yararlanabilecekler mi?
Evet, öğrenciler pedagojik formasyon eğitimi uygulamasından yararlanabileceklerdir, ancak tüm pedagojik formasyon derslerini tamamlamış olması zorunlu değildir (Kaynak 1 ve 4).

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
- **Sure**: 13033.9 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi öğrenim ücreti işlem sistemi üzerinden yatırmanız gereklidir. Yatırılma gereken ücret, 2397,00 TL'dir. İkamet izni için gereken belgeler ise aşağıdaki gibidir:

* İkamet İzin Belgesi
* Pasaport
* Sağlık sigortası belgesi
* Hali hazırda var olan öğrenci bilgi sistemindeki iletişim bilgileri ve güncel e-posta adresi ile telefon bilgisi
* 15 gün önce ikamet tezkeresini veya pasaportunu kaybetmeniz halinde, bu durum için on beş gün içinde ilgili makamlara derhal müracaat ederek yenisini almanız veya ikamet adresinde değişiklik olduğunda bu durumun iki gün içinde bildirimde bulunmanız gerekmektedir.
* Kayıt işlemleri için 15 gün önce öğrenciyi info@omu.edu.tr e-posta adresine bildirmeniz gerekmektedir.

Tüm bu Belgeler kayıt işlemleri için 2 iş gününde ilgili birimlere iletmeniz ve kabul edilmesi gerekmektedir.

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
- **Uretim Modu**: vt (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] not ortalaması
  - [ ] harç
  - [ ] ödeme
  - [ ] başvuru
- **Sure**: 10761.8 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Benchmark, Ogrenim ucreti icin Turk ogrenci / Mühendislik Fakültesi bilgisi veritabaninda kayitli. Yillik ucret: 2.397,00 TL. Donemlik ucret: 1.198,50 TL.

(Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf)

Uretim Turu:
- VT

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
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
- **Sure**: 9251.3 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Kayıt Yenileme Dönemi Harç Ücretini Yatırdıktan Sonra Ders Kaydını Nasıl Yapacağına Dair Bilgiler

Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, derse kaydolmanız için aşağıdaki adımları takip etmelisiniz:

1. Önceki Dönem Derslerini Kontrol Edin: Önceki dönem derslerinizi transkriptinizle karşılaştırarak, her kayıt döneminde almanız gereken dersleri belirleyin.

2. Öğrenci Bilgi Yönetim Sistemine Giriş: Sistemden akademik takvimde belirlenen süre içinde ders kaydı yapmalısınız. İlgili süreye göre sisteme giriş yaparak, müfredat bilgilerine ve transkriptinize göre, hangi dersleri almanız gerektiğini seçin.

3. Seçilen Dersleri Kayıt Yapın ve Onaylayın: Seçilen dersleri, akademik takvimde belirtilen süre içinde öğrenci bilgi yönetim sisteminden kaydolup onaylatılmalıdır. Danışman Onay Süreci, öğrencinin seçtiği derslerin danışman onayına gönderilmesi ile başlar. 
 - *Danışman Onayının Sonucu*: Danışmanın öğrencinin seçtiği dersleri onaylaması ya da iade etmesine karar vermesi ile sonuçlanır. Danışman, öğrencinin şahsen gelmesine gerek yoksa, sistem üzerinden öğrencinin kaydını onaylar. Seçmeli derslere açık olanlara, danışman tarafından sistem üzerinden kayıt yapılır. 
 - *Devamsızlık İmzası Atma*: Danışman onayını almadan, seçilen dersler için devamsızlık imzası atılması gerekebilir.

Yine de unutmayın ki, öğrenci bilgi yönetim sisteminden öğrencilere toplu ya da bireysel mesaj gönderilerek kayıt dönemi başlamadan transkript/müfredat kontrolü yapmaları ve akademik takvimde tanımlanan süre içerisinde ders kaydı yapmaları gerektiği hatırlatılması önemlidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Veritabani kaydi: ogre
... (18 karakter daha)
```

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [x] burs
  - [ ] kesilme
  - [x] kurum
  - [ ] bildiri
  - [x] harç
- **Sure**: 9777.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Yatay geçiş yapmak istediğinizde bursunuz kesilir mi? Sorunuzun tam cevaba ulaşmak için burs aldığınız kurumla iletişim kurmanız gerekmektedir.

Yeni üniversiteye geçişle kayıt yaptırdığınızda harç ödemek zorunda mısınız? Yeni.uniiverite'ye geçiş yaparak kayıt yaptırmakla, harç ücreti yatırmak zorunda olmayacaksınız. Kayıt dondurma isteğinizin ilgili yönetim kurulunca kabul edilmesi durumunda öğrenim ücretini yatırmanıza gerek yoktur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs', 'finance'] (beklenen: ['academic_programs', 'student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [ ] azami
  - [x] ek
  - [x] süre
  - [x] katkı payı
  - [x] öde
- **Sure**: 15191.6 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Benchmark, 4. sınıf öğrencisi olarak program süresini 1 yıl aştığınızı varsayalım. Ek süre hakkınızı kullanabilmeniz için, programa zaman aşımlı sayılmanız ve bu durumla ilgili olarak ilgili mevzuatta herhangi bir sınırlama veya şart bulunmaması gereken durumda ek süre hakkınız vardır.

Bu süreçte, katkı payı ödemesi gerekecektir. Zira program süresini aşan öğrencilerle ilgili madde 13'de belirtildiği gibi katkı payı/öğrenim ücreti ödemesi gereken öğrencilerin akademik takvimde belirtilen süreler içinde öğrenci katkı payını/öğrenim ücretini ödemeleri gerekmektedir.

Ayrıca, muhendislik fakültesine ait 2025-2026 yılı öğrenim ücretleri listesinde görüldüğü üzere öğrencinin katkı payını ödemesi gerekmektedir.

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
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
```

### Q10: Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs', 'announcement'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [x] tekrar
- **Sure**: 11803.7 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim?

Hayır, devamsızlıktan kaldığım bir dersin bütünleme sınavına giremezim. 

Bu konuda elimdeki kaynaklarda net bilgi bulundu. Kaynak 1'den alınan bilgiye göre, bir dersten devamsızlıktan kalan öğrenci o dersin bütünleme sınavına giremez. 

Kaynak 2'den alınmış bilgi, devamsızlıktan kalan öğrenciler girebileceğinin bir durumu ancak bu durumun bir öğrenci devamsızlıktan kaldıktan sonra başarılı olabileceği anlamına gelmektedir. 

Bu, devamsızlıktan kaldığı halde bir dersten başarılı olan öğrencilerin Bütünleme Sınavına girebileceği durumunu açıklamaktadır.

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
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Il
... (920 karakter daha)
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
- **Sure**: 9228.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, ## Kayıt Dondurma Sorumlulukları ve Eğitim Süresi

İkinci öğretim öğrencisiyseniz ve bir dönem kayıt dondurmaya karar veriyorsanız, aşağıdaki bilgileri göz önünde bulundurmanız gerekiyor.

* Kayıt dondurma talebinizin ilgili yönetim kurulunca kabul edilmesi durumunda, öğrenim ücretini yatırmanız gerekmez.
* Kayıt dondurulan süreler, harç ücreti ödenmemesi için eğitim-öğretimden sayılmaz, öğrenim süresinden sayılmaz.

Yükseköğretim Kurulu tarafından belirlenen öğrenci katkı payı/öğrenim ücreti, akademik takvimde belirtilen süreler içinde ödenelidir.

Daha detaylı bilgilere ulaşmak için ilgili yönetim kuruluna başvurmanızı öneririz.

Öğrenim ücreti bilgisine ulaşmak için [Turk Ogrenci/Mühendislik Fakültesi] kaydı bulunan verilerimizden yararlanabilirsiniz.

Örnek olarak, 2025-2026 Eğitim-Öğretim Yılı için öğrenci katkı payı ve öğrenim ücretleri bilgisine erişilebilir.

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
- **Key Facts**: 3/4
  - [x] transkript
  - [x] Ek Madde
  - [ ] başvuru yapabilir
  - [x] GANO
- **Sure**: 7677.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

Evet, hazırlık sınıfındaki ve transkripti olmayan öğrenciler, Ek Madde-1 kapsamında merkezi yerleştirme puanı ile yatay geçiş başvurularını yapabilirler (Kaynak 4: sık_sorulan_sorular.txt). GANO'su değerlendirme aşamasında etkili değildir.

Bu konuda, Ek Madde-1 (Merkezi Yerleştirme Puanı) başvuru için gerekli bir transkript değildir. Sadece öğrencinin Ek Madde-1 kapsamında merkezi yerleştirme puanı ile yatay geçiş başvurusunu yapabilmesi için gerekli belgelerden bazılarıdır:
- Dilekçe
- Tercih listesi (Ek Madde-1 başvurusu için gösterir belge, sisteme yüklenmeyecektir)
- ÖSYS/YKS ile yerleşenler Başvuru modülünde 1. Grubu, DGS ile yerleşenler 2. Grubu seçerek tercih yapacaklardır.

(Yanit: Evet, transkripti olmadan Ek Madde-1 kapsamında yatay geçiş başvuruları yapılabilir. Daha önce Ek Madde-1 başvurularında transkripti aranmamıştır.)

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
- **Key Facts**: 1/5
  - [x] kurum içi
  - [ ] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Sure**: 16164.8 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Kurum içi yatay geçiş ile kurumlararası yatay geçiş arasındaki farklar:

Kurum içi yatay geçiş ile kurumlararası yatay geçişdaki farklar aşağıdaki gibidir:

1. Genel not ortalaması: Kurum içi yatay geçiş için genel not ortalamasının en az 2,80 olması gerekirken, kurumlararası yatay geçiş için 4'lük sistem kullanan üniversiteler için en az 2.80, 100'lük sistem kullanan üniversiteler için en az 72 olması gerekir.
2. Değerlendirme kriterleri: Kurum içi yatay geçiş başvurusunda, öğrencinin kayıtlı olduğu programa ait genel not ortalaması dikkate alınırken, kurumlararası yatay geçiştirakip için öğrencinin merkezi yerleştirme sınav puanı esas alınır.
3. Sınava ilişkin kurallar: Kurum içi yatay geçiş için özel yetenek sınavı ile öğrenci kabul edilen diploma programalarına öğrencilerin özel yetenek sınavında da başarılı olması gerekirken, kurumlararası yatay geçiştirakip için bu şart aranmaz.
4. Yönlendirme: Kurum içi yatay geçiş başvurusu yapabilmek için öğrencinin öğrenim gördüğü programdaki genel not ortalamasının 100 üzerinden 80 veya üzeri olması ya da kayıt olduğu yıldaki merkezi yerleştirme puanının geçmek istediği üniversitedeki programın o yılki taban puanına eşit veya yüksek olması gerekir.
5. İkinci öğretim sınırlaması: Birinci veya ikinci öğretim programlarından uzaktan eğitim programlarına yatay geçiş yapılabilirken, ikinci öğretim diploma programlarından birinci öğretim diploma programlarına yatay geçiş yapılabilir.
6. Yatay geçiş sayısı: Üniversiteye yapılan yatay geçiş başvuru türüne bakılmaksızın bir dönemde en fazla 2 yatay geçiş başvurusu yapılabilir.

Bu farklar, yatay geçiş başvurularının değerlendirilmesinde farklı kriterler ve koşullara dikkat edilmesi gerektirir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yo
... (373 karakter daha)
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
- **Sure**: 12620.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Soru'ya gore, Bilgisayar Muhendisligi bolumu/programi icin "Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?" sorusu cevabini verdigim gibi, ancak kaynaklar bu konuya ilgili degildir. 

Hala da Bilgisayar Muhendisligi bolumu icin lisans ogrencilerinde Mutlak Değerlendirme kullanilirlar. Mutlak Değerlendirme sistemini kullanarak, ogrenciler genel notlari ile degil, sadece bir dersteki notu ile basariyi kontrol ettirirler. Bu nedenle, bu sistemde, ogrenciler bir dersten ancak 60 notu aldiginda basari kaydederler.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
```

### Q15: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/3
  - [x] diploma eki
  - [x] transkript
  - [ ] yerine geçmez
- **Sure**: 9221.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Diploma eki ile transkript arasındaki fark nedir?
Diploma eki ile transkript arasındaki fark, diploma ekisinin bir yükseköğretim diplomasına ek olarak verilen bir belge olmasıdır. Transkript ise öğrencinin not ve kredi bilgilerini gösterir bir belge olarak tanımlanır.

Diploma eki transkript yerine kullanılabilir mi?
Kullanılamamaktadır. Diploma eki ile hangi kazanımları elde edebilirim? Yurtdışında daha okunabilir ve mukayese edilebilir bir diploma, akademik güzergahının ve yurtiçinde ve yurtdışında edindiği yeti ve becerilerin tam bir tarifi, başarı ve yetilerinin nesnel ve adil değerlendirmesi, geleceğe yönelik olarak yurtdışında iş ve eğitim imkanlarına daha rahat ulaşma olanağı, İş bulma olanaklarını artırma kazanımlarını elde edebilirim.

Diploma eki neden verilir?
Diploma eki, kişinin takip edip başarıyla tamamladığı öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek üzere verilir.

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
- **Sure**: 13973.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Kayıt Dondurma ile Kayıt Yaptırmamak Arasındaki Farklar

Kayıt dondurma ve kayıt yaptırmamak arasındaki farklar önemli ve öğrencilerin öğrenim haklarını etkiler. 

Her iki durumda da öğrencinin derse kaydolma hakkı yoktur. Ancak, kayıt dondurulan öğrenci için bu durum erteleme isteğine bağlıdır. Kayıt yaptırmayan öğrenci ise kayıt işlemini yapmaması anlamına gelir ve öğrenim hakkı kaybetmektedir.

Ayrıca, kayıt dondurma öğrencinin ders kaydı yapmama süresi 2 yarıyılı geçemezken, kayıt yaptırmayan öğrenci için bu süre sınırlandırılmamıştır. Ancak, kayıt dondurma işlemini yapabilmek için öğrencinin mazeretlerinin haklı ve geçerli olduğunun yönetim kurulunca kabul edilmesi gereklidir.

Dikkatlice incindiğinde, her iki durumda da öğrencinin öğrenimi durdurulmaktadır ancak kayıt dondurma daha esnek koşullara bağlıdır.

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
  - [ ] UBYS
  - [x] ders seçimi
  - [x] danışman
  - [x] onay
  - [x] yoklama
- **Sure**: 8164.2 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Soruya Yanıtlama:

Öğrenci bilgi yönetim sisteminde yer alan müfredat bilgileri ve transkriptinize ulaşarak, her kayıt dönemi başında alıp başarılı olduğunuz dersleri müfredatınızla karşılaştırmanız gerekmektedir.

1. Ders Kayıt Adımı:
Her akademik takvimde belirtilen süre içinde öğrenci bilgi sistemi üzerinden alacakları dersleri seçerler. Ders kaydı, danışman onayı ile kesinleşir.

Kaynak: [Kaynak 3: ön_lisans_ve_lisans.pdf] - MADDE 10(1)

2. Transkript/Müfredat Kontrolü:
Müfredat durum kontrolü, akademik takvimde belirtilen süre içinde kaydın tamamlanması ve danışman onayı işlemi üç önemli hususa dikkat etmeniz gerekir. [Kaynak 4: sık_sorulan_sorular.txt]

3. Danışman Onayı Adımı:
Kayıt dönemi başlamadan transkript/müfredat kontrolünü yaparak akademik takvimde tanımlanan süre içerisinde ders kaydını yapmaları gerektiği, derslere başladığında ise sınıf yoklama listesinde adları yoksa danışmanlarına uğramaları gerektiği bilgisi paylaşılmalıdır. [Kaynak 2: sık_sorulan_sorular.txt]

4. Sınıf Yoklama Listesine İmza Atma:
Sınıf yoklama listesine imza atmalısınız. Sistemden alınan ve üzerinde adınızın yer aldığı sınıf yoklama listesine devam/devamsızlık imzasını atınız. [Kaynak 1: sık_sorulan_sorular.txt]

5. Danışmanla İletişim:
Danışmanıyla iletişime geçerek ders seçimini onaylatır. [Kaynak 5: ön_lisans_ve_lisans_akademik_danışmanlık.pdf] - (3)

6. Kayıt İşlemlerinin Tamamlanması:
Akademik takvimde belirtilen süre içinde kaydın tamamlanması gerekir. [Kaynak 4: sık_sorulan_sorular.txt]

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
```

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] itiraz
  - [ ] beş iş günü
  - [ ] dilekçe
  - [x] bölüm başkanlığı
- **Sure**: 8367.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

1. Başvuru Süreci:
İtiraz başvurusu, ilgili bölüm başkanlığı veya fakülte/yüksekokuluna yazılı olarak yapılır. (Kaynak 2, Yüzde Oncu Başarı Değerlendirme Yönergesi, MADDE 8)
2. Başvuru Süresi:
İtiraz süresi, Yüzde Oncu Başarı Değerlendirme Yönergesi'nde belirlenmiştir. Buna göre, itirazı olan öğrenciler 15 gün içerisinde fakülte/yüksekokuluna yazılı olarak başvurabilirler. Yapılan başvurular 15 gün içerisinde birim yönetim kurulunca karara bağlanır. Yönetim Kurulunca verilen karar kesindir. (Kaynak 2, Yüzde Oncu Başarı Değerlendirme Yönergesi, MADDE 8)
3. İtiraz Yöntemi:
İtirazlar, ilgili bölüm başkanı veya fakülte/yüksekokuluna yazılı olarak yapılabilir. (Kaynak 2, Yüzde Oncu Başarı Değerlendirme Yönergesi, MADDE 8)
4. İtiraz Süresi Sonrası:
İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz. (Kaynak 2, Yüzde Oncu Başarı Değerlendirme Yönergesi, MADDE 8)
5. Yeniden İnceleme:
Yeniden inceleme, ilgili öğretim elemanı tarafından en geç üç iş günü içinde yapılır. Notta değişiklik olması durumunda form, ilgili birimin yönetim kurulu kararıyla Öğrenci İşleri Daire Başkanlığına gönderilir. (Kaynak 3, Yönetmelik Ön Lisans-Lisans Eğitim-Öğretim, MADDE 27)
6. İtiraz Süresi:
 İtiraz süresi üç iş günüdür. (Kaynak 3, Yönetmelik Ön Lisans-Lisans Eğitim-Öğretim, MADDE 27)
7. İlgili Bölüme Yazılı Başvuru:
İlgili bölümüne yazılı olarak başvurmak kaydıyla, beş iş gün içerisinde sınav kağıtlarının yeniden incelenmesi talebinde bulunabilir. (Kaynak 3, Yönetmelik Ön Lisans-Lisans Eğitim-Öğretim, MADDE 27)

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı:

- Başvuru sonrası süreçteki adımları belirlemek;
- İlgili kuruluşların adlarını ve adreslerini belirtmek, 
- Yeniden incelemeye ilişkin kuralları belirtmek, 
ve diğer açıklamaları belirtmek.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim 
... (271 karakter daha)
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
- **Sure**: 12365.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Mezuniyet için gereken tüm koşulları ve ilişik kesme sürecini adım adım açıklamak mümkün. Bu süreç, iki farklı durumda oluşabilir:

1. Kayıt yenileme ve katkı payı ödemeyen öğrenciler: Bu şekilde ilişik kesme işlemi 4 yıldan uzun süreli olarak gerçekleşebilir. Bu koşulun gerçekleşmesi için; 
- İlgili birimlerin teklifi,
- Senato kararları,
- YÖK onayları gerekir. (KAYNAK 1: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf, Madde 32)
Kayıt yenilememesi ve katkı payı ödemeyen öğrencinin ilişik kesme tarihi, 4 yıldan uzun süredir bu durumdayken gerçekleşecektir.

2. Dışarımdan kazanılmış disiplin cezaları:
- Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği hükümlerine göre yükseköğretim kurumlarından çıkarma cezası almış öğrencilerin Üniversite ile ilişikleri kesilir.
- Aynı şekilde, kendi istekleri ile kaydını sildiren öğrencilerin Üniversite ile ilişikleri kesilir. (KAYNAK 1: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf, Madde 32)

3. 8 inci maddenin üçüncü ve dördüncü fıkraları kapsamındaki öğrenciler:
- Başarısız oldukları ders sayısını bire indiremeyenlerin Üniversite ile ilişiği kesilir. (KAYNAK 1: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf, Madde 32, 2 ve KAYNAK 2: yonetmelik_onlisans_lisans_egitim_ogretim.pdf, Madde 32)

4. Diploma Alma:
- Öğrenim gördüğü eğitim-öğretim programında yer alan bütün şartları yerine getirerek mezuniyet hakkı kazanan öğrencilere verilmek üzere ön lisans ve lisans diplomaları Öğrenci İşleri Daire Başkanlığı tarafından, yüksek lisans, doktora ve sanatta yeterlilik diplomaları ise ilgili enstitü müdürü tarafından hazırlanacaktır. (KAYNAK 3: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf, Madde 7)

5. İlişik Kesme Süreci:
- Bu koşulun gerçekleşmesi için; 
 - İlgili birimlerin teklifi,
 - Senato kararları,
 - YÖK onayları gerekir. (KAYNAK 1: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf, Madde 32)
- Kayıt yenilememesi ve katkı payı ödemeyen öğrencinin ilişik kesme tarihi, 4 yıldan uzun süredir bu dur
... (557 karakter daha)
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
- **Sure**: 10779.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Mezuniyeti ve diplomasını kaybederek e-devlette mezuniyet bilgilerinin görünmemesi durumunu ele alıyoruz. Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- Sorun 1: Diplomasını kaybeden öğrenciler için yapılması gereken ilk adımdır.
- Sorun 2: E-devlette mezuniyet bilgilerinin görünmemesi durumunu ele alıyoruz.

Aşağıda, her iki sorun için neler yapmalıyım?

### Sorun 1: Diplomasını kaybeden öğrenciler için yapılması gereken

Diplomasını kaybeden öğrenciler:
- Yerinden yaygın gazetelerden birine diploma kayıp ilanı verebilirler.
- Başvuru dilekçesi, onaylı nüfus cüzdanı sureti ve diploma ücretini yatırdıklarını gösteren banka dekontu ile diploma aldıkları birime müracaat değerler.
- İlk diplomasında yer alan bilgileri içeren yeni bir diploma düzenlenir.
- Yeni diploma üzerinde "İkinci Nüsha" bilgisi yer alır.
- Aksine bir durum söz konusu ise, yaygın gazeteden diploma kayıp ilanı vermek, başvuru dilekçesi vermek ve onaylı nüfus cüzdanı gibi belgelerle belge aldıkları birime müracaat etmek yeterlidir.
- Bu durumda belge üzerinde görev başında bulunan ilgili birimin Müdürü/Dekanı ve/veya Rektör tarafından imzalanır.

### Sorun 2: Mezuniyet bilgilerinin görünmemesi

Mezuniyet bilgilerinin görünmemesi durumunu ele alacağız.
- E-devlete ait belgeleri ibraz etmek yerine, aslının getirilmesi lazımdır.
- Islak imzalı belgelerin fotoğrafı, e-posta çıktısı vs. kabul edilmemektedir.
- Eksik veya onaysız belge/belgeler ile gelen öğrenciler ile beyanlarında hata olanların kayıt işlemi yerine getirilmeyecektir.

### Kaynaklar
* Uygulama esasları diploması ve mezuniyet belgeleri: [Kaynak 1]
* Diploma ve mezuniyet bilgi düzenleme: [Kaynak 2]
* E-devletten alınan belgelerin onayı: [Kaynak 4]
Diplomasını kaybeden öğrenciler, e-devlette mezuniyet bilgilerinin görünmemesi durumunu ele alınmaktadır. Her iki sorun için yapılması gerekenler şu şekilde sıralanabilir:

- Yerinden yaygın gazetelerden birine diploma
... (654 karakter daha)
```

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs', 'academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] uzaktan
  - [ ] %20
  - [x] %80
  - [ ] %40
  - [ ] %60
- **Sure**: 18696.8 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklıdır.

İki ana farkla uzaktan eğitim yoluyla alınan 5-i dersleri yüz yüze derslerden farklıdır: devam ve sınav koşulları.

Devam Koşulları

O rgün eğitimde öğrencilerin yüz yüze yürütülen derslerin teorik saatlerinin en az % 70’ine; ders uygulamaları, atölye ve laboratuvarların ise en az % 80’ine devam zorunludur. Ancak uzaktan eğitim yoluyla alınan derslerde bu oran en az % 80’leştirilmiştir.

Sınav Koşulları

Sınavlar yüz yüze yapılırken, uzaktan eğitim yoluyla alınan derslerde bu durum öğrenci kayıtlı olduğu programa göre değişmektedir. Yüz yüze sınava yapılan bazı dersler de olabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
- Belge: uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Sure**: 16244.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Sınavda kopya çekilmesinin cezası ve disiplin süreci hakkında bilgi verilmektedir. Cezasız bir sınavda kopya çekilmesinin cezası, kopya verme veya çekme suçudur ve bu durum disiplin suçudur. Görevliler bu suçun tespitine karar verme yetkisine sahiptir. Uyarıda bulunmaksızın bu öğrenciler hakkında işlem yapabilirler.

Disiplin süreci Yükseköğretim Kanununun 54. Maddesine göre yürütülür. Disiplin suçunun tespiti ve cezasının verilmesi ilgili öğretim elemanı veya sınav görevlisi tarafından yapılır. Cezalar, öğrencinin davranışına göre belirlenir.

Disiplin suçu aşağıdaki adımları içerir:

1. Sınav sırasında kopya çekilmediği tespit edilmediyse ve sınav görevlilerince düzenlenen bireysel sınav iptal tutanağın hazırlanması.
2. Öğrencinin sınavı, dersi veren öğretim üyesi tarafından geçersiz sayılması.
3. Gerekli yasal işlemlerin başlatılması.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

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
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 0/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [ ] birim
- **Sure**: 11911.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Üniversiteyi bırakıp ayrılmak istiyorsanız, lütfen aşağıdaki işlemleri dikkat etmeniz gerekmektedir:

1. Öğrenci Disiplin Yönetmeliği'ne göre işlem: Üniversite disiplin kurulundan onay almadan ayrılmak istemiyorsanız, lütfen ilk olarak öğrenci disiplin yönetmeliği'ne göre işlem yapınız. Bu yönetmelek, mezun olmak ya da üniversitenin amacına uymayan faaliyette bulunmanız gibi çeşitli nedenlerle üniversite ile ilişiğin kesilmesi ile ilgili detayları içerir.
2. Kayıt silme talebi: Kayıtınızı sildirmek istiyorsanız, lütfen kayıtlı olduğunuz akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden kaydınızı sildirmek için talepte bulunuz. Bu süre akademik takvime göre değişmektedir.
3. Özür durumunuza göre işlem: Eğer bir mazerete dayanarak üniversiteye gitmediyseniz, lütfen öğrenci disiplin yönetmeliğine göre işlem yapınız.
4. Üniversite ile ilişiğin kesilmesi: Eğer üniversite ile ilişiğinizi kesmek istiyorsanız, lütfen YÖK'ün onayını aldıktan sonra bu işleme geçmelisiniz.
5. Ödemeler ve borçlar: Eğer herhangi bir borçunuz varsa, lütfen bu borçları ödemiş olunuz.
6. Öğrenci bilgi sistemi: Eğer kayıt yaptırmayı unutuyorsanız, lütfen öğrenci bilgi sistemi üzerinden kayıt yaptırmak için talepte bulunuz.
 
Ayrıca, lütfen dikkat etmeniz gereken şeyler şunlardır:

- 4 yıl üst üste katkı payı ve öğrenim ücreti ödemeyen ya da kayıt yenilemeyen öğrencilerin üniversite ile ilişiği kesilebilir.
- Yazılı isteği üzerine kaydını sildiren öğrenci, ÖSYM tarafından yeniden yerleştirilmediği veya Üniversite tarafından yapılan ölçme ve değerlendirme sonucunda kayıt hakkı kazanmadığı sürece, Üniversiteye tekrar kaydolamaz.
- Üyeliğine son verilen öğrenci aynı topluluğa yeniden üye olamaz.

Lütfen yukarıdaki bilgiler doğrultusunda dikkatli bir şekilde işlemlerinizi yapınız.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
... (222 karakter daha)
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
- **Sure**: 8833.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Mezuniyet ve notla ilgili sorular için aşağıdaki kurallara uyunuz:

1. Yalnızca verilen belge bağlamında açıkça geçen bilgileri kullan.
2. Kisisel akademik veriler (GNO, not, kredi) verilmemişse, bu bilgiyi alma.
3. ASLA tahmin etme, genel bilgiyle boşluk doldurma, kavram tanımı uydurma.
4. Yalnızca Türkçe yanıt ver; İngilizce veya başka dilden kelime kullanma.
5. Üniversite adını kaynakta yazmadıysa, uydurma. Bu sistem Ondokuz Mayıs Üniversitesi (OMU) için.

Soru: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

Yanit:
- Okulumuzu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini yapabilmek için, öğrenim süremiz boyunca en fazla 4 dönem/2 yıl kayıt dondurma hakkımız mevcut.
- Kayıt dondurma süresinin bitiminde öğrenci; ayrıldığı dönemin/yılın başından başlamak koşuluyla, öğrenimine kaldığı yerden devam eder.
- Kayıt dondurulan dönem/dönemler, süre hesabında dikkate alınmaz.
- Öğrenimimizi uzun süre engelleyecek önemli bir hastalık veya ilgili yönetim kurulunca kabul edilen haklı ve geçerli bir nedenle ve belgelendirilmek kaydıyla verilen izin de süre hesabına dahil edilmemektedir.
- Ders seçimi için, akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden dersleri seçer; Ders kaydı, danışman onayı ile kesinleşir; öğrenci, ders kaydının kesinleştirilmesi ile ilgili süreci takip etmek zorundadır.

Kaynak: [Kaynak 1: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf], [Kaynak 2: ön_lisans_ve_lisans.pdf], [Kaynak 3: ön_lisans_ve_lisans.pdf]

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
- **Key Facts**: 1/3
  - [x] danışman
  - [ ] bölüm
  - [ ] oidb@omu.edu.tr
- **Sure**: 8405.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Hocam, sizin ders notlarınızı sisteme girmemiş olmanız durumunda ne yapabilirim?

- İlk olarak, akademik takvimde belirtilen süre içinde öğrenci bilgi sistemi üzerinden derslerimi seçerek kayıt yaptırmam gerekir. (Kaynak 1, Kaynak 3)
- Akademik takvimde belirtilen süre içinde kayıt yaptırmayan öğrenciler, o dönemde öğrenimine devam etme hakkını kaybederler. Kaybedilen dönem öğrenim süresinden sayılır. (Kaynak 3)
- Kaydedilecek derslerin AKTS kredileri toplamı, kayıt yaptıracakları dönem içi belirlenmiş olan AKTS kredileri ile bunların yarısının toplamından fazla olamaz. (Kaynak 3)
- Danışman onayını almak için, öğrencinin şahsen gelmesini zorunlu tutacak bir hüküm bulunmamaktadır. Danışman, onaya gönderilen ders kaydını sistem üzerinden onaylayabilir veya iade edebilir. (Kaynak 5)
- Onaylamadığım ve sistem üzerinden iade ettiğim ders kaydını öğrenci takip ederek tamamlamadığı takdirde sorumluluk öğrencide yer alır. (Kaynak 5)

Bilgi Guvenligi Prosedürü: Ders kaydında üç önemli hususa dikkat etmeniz gerekir: Eksik ders alarak dönem uzatmamak için her dönem başında müfredat durum kontrolü, akademik takvimde belirtilen süre içinde kaydın tamamlanması ve danışman onayı işlemidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
