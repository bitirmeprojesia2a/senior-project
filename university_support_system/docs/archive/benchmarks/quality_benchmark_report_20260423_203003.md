# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-23 20:30:03
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 92.0% |
| Uretim Modu Dogrulugu | 84.0% |
| Anahtar Bilgi Kapsami | 52.0% |
| Temiz Kalite Orani | 96.0% |
| Ortalama Sure | 22319.6 ms |
| Medyan Sure | 13397.3 ms |
| Intent Analizi Aktif | 0/25 |
| Force LLM Sentez | 0/25 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 3 |

## A2A Diagnostics Delta

- Overview delta: queries=18, query_failures=0, agent_tasks=33, agent_task_failures=3

| Agent | Role | Task Delta | Failed Delta | Last Error |
|-------|------|------------|--------------|------------|
| academic_programs_orchestrator | department_orchestrator | 1 | 1 | a2a_specialist_transport_failed |
| graduation_agent | specialist_agent | 11 | 1 | a2a_specialist_transport_failed |
| regulation_agent | specialist_agent | 2 | 1 | a2a_specialist_transport_failed |

Recent failure samples:
- `academic_programs_orchestrator`: a2a_specialist_transport_failed - Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?
- `regulation_agent`: a2a_specialist_transport_failed - Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?
- `graduation_agent`: a2a_specialist_transport_failed - Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 50373.4 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 2/3 | 45291.7 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 3/4 | 102486.5 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | YANLIS (kural) | 0/4 | 62205.4 | a2a_transport_fallback |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 25532.5 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | YANLIS | YANLIS (vt) | 0/4 | 1452.0 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | YANLIS (vt) | 0/5 | 7903.8 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 31798.0 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 4/5 | 21720.0 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 2/4 | 23449.5 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 4/4 | 12182.1 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 4/4 | 9208.8 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 18194.0 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 3/4 | 17363.3 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 3/3 | 12530.3 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 12676.8 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 4/5 | 8244.0 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 2/4 | 7705.5 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 3/6 | 13484.0 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 15512.1 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | YANLIS | OK | 1/5 | 10754.1 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 11195.8 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 13397.3 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 11913.4 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 1/3 | 11414.6 | - |

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
- **Sure**: 50373.4 ms
- **Kaynak Sayisi**: 12

**Yanit:**
```
Benchmark, Yatay geçişle gelen öğrenci, muafiyet başvurusunu 26.01.2026-01.02.2026 tarihleri arasında yapmalıdır. Bu süre zarfında muafiyet talepleri, derslerin başlamasından itibaren ikinci haftanın sonuna kadar yapılmalıdır. Öğrenciler, kayıt dondurmaksızın devama devam edebilir ve muafiyet talebine bakılmaksızın muafiyet talebinde bulunduğu derslere devam ederler.

Detaylar:

- Yatay geçişle gelen öğrenciler, 2025-2026 EĞİTİM ÖĞRETİM YILI BAHAR YARIYILI ÖN LİSANS İÇİN YATAY GEÇİŞ İLAN METNİ’nde açıkça belirlenen tarih aralığında muafiyet başvurusunu yapmalıdır.
- Yatay geçişle gelen öğrenciler, muafiyet başvurusunu yaparken, kayıt dondurmuşsa durumunu belgelemesi gerekecektir.
- Öğrenciler, muafiyet talebine bakılmaksızın muafiyet talebinde bulunduğu derslere devam edebilirler; muafiyet talepleri, derslerin başlamasından itibaren ikinci haftanın sonuna kadar yapılmalıdır.

Bu bilgiler, yatay geçişle gelen öğrencilerinin muafiyet başvurusunu yapıp, karar çıkana kadar derslere devam etmede gerekli adımları içerir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: sık_sorulan_sorular.txt
- Duyuru kaydi: 2025-2026 Eğitim Öğretim Yılı Bahar Yarıyılı Yatay Geçiş Yedek sonuçları (https://www.omu.edu.tr/tr/icerik/duyuru/2025-2026-egitim-ogretim-yili-bahar-yariyili-yatay-gecis-yedek-sonuclari)
- Duyuru kaydi: 2025
... (339 karakter daha)
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
- **Sure**: 45291.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Staj Sorumluluklarının İncelenmesi

Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekiyor mu? Hayır, staj sınavında başarılı olmannız gerekli değildir.

Staj sınavınızı başarısız olduğunuzda ne olur? Tek ders sınavına girebilirsiniz. 

Tek ders sınavında başarılı sayılmak için minimum not AA (90-100) olmalıdır.

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
- **Key Facts**: 3/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [x] yeni
  - [x] ders
- **Sure**: 102486.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Soruda bahsettiğiniz durum, normal dönemde veya yaz döneminde seçmeli ders yerine başka bir seçmeli ders seçmeniz ile ilgili. 

YÖnetmelik madde 17'den (Kaynak 1) göre, bir öğrenci danışmanın onayı ile başarısız olduğu bir seçmeli ders yerine, devam etmek kaydıyla, bir başka seçmeli ders alabilir. Ancak, devam koşuluna uyacaklardır. Bu durum, seçmeli derslerde geçerlidir.

Yaz döneminde de aynı durum geçerlidir. YÖnetmelik madde 13'den (Kaynak 4) göre, yaz döneminde açılan dersler için devam zorunludur ve seçmeli derslerde aynı kural geçerlidir.

Öylelik, devam zorunluluğunuz değişmez. Devam koşulu, normal dönemde ya da yaz döneminde devam etmek anlamına gelir. 

Yani, yeni seçilen seçmeli ders için de devam koşulu mevcuttur.

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
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] transkript
  - [ ] dahil
  - [ ] ortalama
  - [ ] tamamlamıştır
- **Sure**: 62205.4 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: a2a_transport_fallback

**Yanit:**
```
Benchmark, Regulation Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Uretim Turu:
- Kural
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
- **Sure**: 25532.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Uluslararası öğrenci olarak kaydınızı yaptırdığınız zaman, öğrenim ücretinizi herhangi bir Ziraat Bankası şubesinden öğrenci numaranızla harç ücretini yatırmalısınız. Bunun için, Önlü (ön kayıt yaptıran) veya Ötesi (ilk kayıt yaptıran) bir öğrenci olduğunuza göre, ön kayıt yaptırdığınız tarihte yada kaydıldığınız yılı takip eden son kayıt tarihine kadar ücreti yatırmalısınız. 

İkamet izni başvurunuzu yaptığınız zaman aşağıdaki bilgileri hazırlamalısınız:
- Sağlık raporu
- Not çizelgesi
- Özel öğrenci statüsünde ise kayıtlı olduğu birim yönetim kurulunun olumlu kararı
- Disiplin durumunu gösterir belge ve dilekçe
- Veya kayıt dışı birim yönetimi kurulunun olumlu kararı
- ve pasaportunuz veya ikamet tezkerenizi sunmanız gerekmektedir.

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
- **Departman**: ['finance'] (beklenen: ['academic_programs', 'finance']) - YANLIS
- **Uretim Modu**: vt (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] not ortalaması
  - [ ] harç
  - [ ] ödeme
  - [ ] başvuru
- **Sure**: 1452.0 ms
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
- **Uretim Modu**: vt (beklenen: llm) - YANLIS
- **Key Facts**: 0/5
  - [ ] harç
  - [ ] UBYS
  - [ ] ders
  - [ ] danışman
  - [ ] onay
- **Sure**: 7903.8 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Benchmark, Kayit yenileme ucreti icin Turk ogrenci / Mühendislik Fakültesi bilgisi veritabaninda kayitli. Yillik ucret: 2.397,00 TL. Donemlik ucret: 1.198,50 TL.

(Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf)

Uretim Turu:
- VT

Kaynak Ozeti:
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
- **Sure**: 31798.0 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Sorunuzu çözmek için toplanan bilgiler aşağıdaki gibi özetlenebilir. Soruda belirtildiği gibi, burslu öğrenci yatay geçiş yapmak istiyor ve bursumun kesileceği, yeni üniversiteye harç ödemesi gerekmeyeceği hakkında bilgi istemektedir.

Soru 1: Bursunuzun kesilme durumu

Yatay geçiş yapan burslu öğrencilere burs vermek kabul edildiği için, bursunuzun kesilmeyeceği söylenebilir. Bursunuzun kesilip kesilmeyeceği konusunda bilgiye ulaşmak için burs aldığınız kurumla iletişim kurmanız gerekmektedir.

Soru 2: Yeni üniversitede harç ödemeyi gereksinmi

Yatay geçiş yapan öğrenciler, yeni üniversiteye geçtikten sonra öğrencilik hak ve sorumluluklarını kazanır. Öğrencilik hak ve sorumluluklarını kazandığınız için harç ödemeyi gereksinme duyacaksınız.

Sonuç

Yatay geçiş yapan burslu öğrencilere burs vermek kabul edildiği için, bursunuzun kesilmeyeceği söylenebilir. Yatay geçiş yapan öğrenciler, yeni üniversiteye geçtikten sonra öğrencilik hak ve sorumluluklarını kazanır ve harç ödemmeyi gereksinebilir.

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
- **Key Facts**: 4/5
  - [ ] azami
  - [x] ek
  - [x] süre
  - [x] katkı payı
  - [x] öde
- **Sure**: 21720.0 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Sorunun cevabı:
- Ek süre hakkınız yoktur.
- Normal lisans eğitimi 6 yıl sürmekte ve 1 yıldan fazla geçememektedir.
- Katkı payını/öğretim ücretini süresi içinde ödemeyenler, o dönem için kayıt yaptıramaz ve öğrencilik haklarından yararlanamazlar.

Öğrencinin 4. sınıfında olduğu durumlarda, normal lisans eğitimi 6 yıl sürmekte ve 1 yıldan fazla geçememektedir. Bu nedenle, ek süre hakkınız yoktur.

Tıp Fakültesinde, normal eğitim-öğretim süresi hazırlık sınıfı hariç 6 yıldır. Ek süre hakkınız almanız için 6 yıllık lisans eğitimini tamamlamanız ve 1 yıldan fazla geçmemeniz gerekir. Birlikte normal eğitim-öğretim süresi 7 yıldan fazla olmayacaktır.

Bu sürede katkı payını/öğretim ücretini süresi içinde ödemeyenler, o dönem için kayıt yaptıramaz ve öğrencilik haklarından yararlanamazlar.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Finans: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
```

### Q10: Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs', 'announcement'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [ ] tekrar
- **Sure**: 23449.5 ms
- **Kaynak Sayisi**: 13

**Yanit:**
```
Benchmark, Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim?

Evet, girebilirsiniz. Bütünleme sınavına girebilmek için, zamanında ders kaydının yapılmış ve devam zorunluluğunun yerine getirilmiş olması gerekir. Bu koşul yerine getirildikten sonra, devamsızlıktan kaldığınız dersi sadece bir kez daha alabilirsiniz.

Özetle, devamsızlıktan kaldığınız dersi bütünleme sınavına girebilir ve sadece bir kez daha alabilirsiniz.

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
- **Key Facts**: 4/4
  - [x] öğrenim ücreti
  - [x] gerek yok
  - [x] yönetim kurulu
  - [x] sayılma
- **Sure**: 12182.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, İkinci Öğretim Öğrencisi Kayıt Dondurma Sorunu:

İkinci öğretim öğrencisi olarak kayıt dondurmak istediğinizde, harç ücretini yatırmak zorunda değilsiniz. Kayıt dondurduğunuz süreler eğitim-öğretimden sayılmaz.

Ayarlamalar:

* Kayıt dondurma isteğiniz, ilgili yönetim kurulunca kabul edilirse öğrenim ücretini yatırmanıza gerek yoktur.
* Eğitim-öğretim süresi içinde, öğrenci katkı payı/öğrenim ücretini ödemek yükümlüsünüz. 

Önemli Bilgiler:

* Kayıt dondurduğunuz süreler, eğitim-öğretim süresinden sayılmayacak şekilde belirlenir.
* Eğitim-öğretim süresi içinde, öğrenim ücretini ödemeniz gereken öğrenciler için katkı payı/öğrenim ücretini zamanında ödemek zorunludur.
 
Referans:

Bu bilgi, öğrenci işleri ve finans departmanlarından sağlanan bilgilere dayanmaktadır.

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
- **Sure**: 9208.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Soru:
Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

Yaniti: Evet, ancak transkriptiniz olmadan da başvuru yapabilirsiniz. Ek Madde-1 kapsamında yapılan yatay geçiş başvurularında öğrencinin GANO'su değerlendirme aşamasında etkili değildir.

Kaynak: Sık_Sorulan_Sorular.txt

Yönerge: Ek Madde-1 (Merkezi Yerleştirme Puanı) başvurusu için ÖSYS/YKS ile yerleşenler Başvuru modülünde 1. Grubu, DGS ile yerleşenler 2. Grubu seçerek tercih yapacaklardır.

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
- **Sure**: 18194.0 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Kurum Içi ve Kurumlar Arasinda Yatay Geçiş Farklari

Kurum içi yatay geçiş ve kurumlar arası yatay geçiş arasındaki farklar nelerdir?

* Kurum içi yatay geçişti, Ondokuz Mayıs Üniversitesi (OMU) içinde, aynı düzeydeki diğer diploma programlarına geçişi ifade eder. Bu tür geçişler, OMU içinde gerçekleşmektedir.
* Kurumlar arası yatay geçişti, bir üniversite, yüksek teknoloji enstitüsü veya bir vakıf tarafından kurulan meslek yüksekokullarından OMU'da eğitim veren fakülte, yüksekokul veya bölgeye yapılan geçişi ifade eder. Bu tür geçişler, OMU dışında gerçekleşmektedir.

Başvuru Koşulları ve Değerlendirme Kriterleri

Kurum içi yatay geçiş ve kurumlar arası yatay geçiş başvurularının koşulları ve değerlendirme kriterleri aşağıdaki gibidir:

* Kurum Içi Yatay Geçiş:
 + Öğrenci, mevcut programda bitirdiği dönemlere ait genel not ortalamasının en az 2,80 olması gerekir.
 + Öğrenci, müfredatında yer alan bütün dersleri almış olmalıdır.
* Kurumlar Arası Yatay Geçiş:
 + Öğrencinin kayıtlı olduğu programda bitirmiş olduğu dönemlere ait genel not ortalamasının 4'lük sistem kullanan üniversiteler için en az 2,80, 100'lük sistem kullanan üniversiteler için en az 72 olması gerekir.
 + Öğrencinin, merkezi yerleştirme sınav puanı esas alınır.

Değerlendirme ve Yatay Geçiş Hakkı

Yatay geçiş başvuruları, aynı puan türündeki programlara geçiş için genel not ortalamasının %60’ı ve merkezi yerleştirme puanının %40’i; farklı puan türü bulunan programalara geçiş için genel not ortalamasının %30’ı ve merkezi yerleştirme puanının %70’i esas alınarak yapılır.

Kurum içi yatay geçiş başvuruları kabul ediliyorsa, ilgili yükseköğretim kurumunun disiplin cezası almamış olması ve akademik takvim çerçevesinde yapılacak başvurular, izinli sayılıyor olması gibi şartlar geçerlidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Progr
... (444 karakter daha)
```

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] bağıl
  - [x] mutlak
  - [x] 10
  - [ ] öğrenci sayısı
- **Sure**: 17363.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Yaniti vermeye çalışacağım. 

Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir?

Birincisi, Bağıl Değerlendirmesi: Kaynak 4'te açıkça belirtilen gibi "Başarı notu; tek ders ve muafiyet sınavları dışında, öğrencilerin yarıyıl/yıl içi değerlendirme ile yarıyıl/yılsonu sınavından aldıkları notların öngörülen ağırlıklara göre hesaba katılmasıyla belirlenen ham başarı notunun 4’lük not sistemindeki karşılığını ifade eder." Bu değerlendirme öğrencinin yarıyıl içi ve yarıyıl sonu sınavlarına göre yapılır.

Ikincisi, Mutlak Değerlendirme (4'lük Not Sistemi): Kaynak 4'te yer alan "Mutlak Değerlendirme" tablosuna göre; başarı notuna göre 4,00 (AA), 3,50 (BA), 3,00 (BB), 2,50 (CB), 2,00 (CC), 1,00 (FD), 0,00 (FF) not aralıkları bulunur.

Hangisi uygulanır?

Lisans programları için: Bağıl değerlendirme sistemi kaynaklarda açıkca belirlenmemiş; ancak mutlaktan bahsetmemelidir. O halde lisans programları için mutlak değerlendirme kullanılır (4'lük not sistemi).

Birinci, ikinci, üçüncü, dördüncü, beşinci ve altıncı basamaktaki lisans programları (Bilgisayar Mühendisliği dahil) için: Bağımsız lisans programlarındaki eğitim-öğretim ve sınavların tümünün, başarı notlarının hesabında bağımlı sınavlar yerine, 4'ün tamına eşdeğer olacak 100'lük not sistemine göre değerlendirileceği; 100 üzerinden alınan başarı notuna 4 üzerinden notlar karşılık geleceği belirtilmiştir (Kaynak 1).

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
- **Key Facts**: 3/3
  - [x] diploma eki
  - [x] transkript
  - [x] yerine geçmez
- **Sure**: 12530.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Diploma eki ile transkript arasındaki fark nedir? 

Diploma eki, transkript (not çizelgesi) yerine geçmez. Diplomalarda yer alan bilgiler, diploma sahibinin takip edip başarıyla tamamladığı öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek üzere verilir.

Diploma eki transkript (not çizelgesi) yerine geçemez mi?

Evet, diploma eki transkript (not çizelgesi) yerine geçmez.

Diploma eki neden kullanılır?

Diploma eki, uluslararası saydamlığı pekiştirmeyi hedefleyen ve elde edilmiş yeti ve becerilerin ifade edildiği diploma, derece, sertifika gibi belgelerin, akademik ve mesleki tanınmasını sağlamaya yönelik, bir yükseköğretim diplomasına ek olarak verilen belgedir.

Diploma eki ile transkript arasındaki farkı açıklamalıyız:

Transkript, bir öğrencinin tamamladığı tüm dersleri,notlarını ve kredilerini içerirken,
Diploma eki ise, diploma sahibinin elde etmiş olduğu yeti ve becerilerin detaylı bir şekilde ifade edildiği bir belgedir.

Bu nedenle, diploma eki transkript yerine geçemez.

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
- **Sure**: 12676.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Kayıt dondurma ile kayıt yaptırmamak arasındaki farklar şunlardır:

- Kayıt dondurma: Öğrencinin önemli mazeretlerinden dolayı kaydı bir defada en fazla iki dönem/bir yıl olarak dondurulabilir. Bu durumda öğrenci öğrenimine devam edemez ve kayıt dondurulan döneme/yıla ait sınavlara giremez. Kayıt dondurma süresinin bitiminde öğrenci, ayrıldığı dönemin/yılın başından başlamak koşuluyla, öğrenimine kaldığı yerden devam eder. Kayıt dondurulan dönem/dönemler, süre hesabında dikkate alınmaz.
- Kayıt yaptırmamak: Öğrenci akademik takvimde belirlenen süre içinde ders kaydını yapamazsa, o dönemde öğrenimine devam etme hakkını kaybeder. Kaybedilen dönem, öğrenim süresinden sayılır.

Bu iki durum arasındaki fark, öğrencinin kayıt durumundan ne elde edebileceği konusunda yatmaktadır. Kayıt dondurma, öğrencinin öğrenimine devam etme hakkını korurken, kayıt yaptırmamak da öğrencinin öğrenimine devam etme hakkını kaybeder.

Öğrencilik haklarınızın nasıl etkilenacağını açıklamak gerekirse:

- Kayıt dondurma: Kayıt dondurma süresinin bitiminde öğrenci, öğrenimine kaldığı yerden devam eder. Bu nedenle, öğrencilik hakları etkilenmez.
- Kayıt yaptırmamak: Öğrenci akademik takvimde belirlenen süre içinde ders kaydını yapamıyorsa, o dönemde öğrenimine devam etme hakkını kaybeder. Bu nedenle, öğrencilik hakları etkilenmez.

Yani, iki durum arasında öğrencilik haklarınızın etkilenme durumu benzerdir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
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
- **Sure**: 8244.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Ders kaydından danışman onayına kadar tüm süreci başından sonuna anlatır mısınız?

Ders Kayıt Süreci:

1. Ders Seçimi: Öğrenci, her kayıt dönemi başında akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden alacakları dersleri seçerler.
2. Ders Kaydı: Öğrenciler, seçtikleri dersleri öğrenci bilgi sistemi üzerinden kayıt ederler.
3. Danışman Onayı: Danışman, öğrencinin seçtiği dersleri onaylar. 
4. Kayıt Onaylanması: Danışman onayından sonra, öğrenci adına öğrenci bilgi sistemi üzerinden kaydedilen dersler onaylanır.

Danışman Onayının Önemi:

- Ders Kaydının Kesinleşmesi: Danışman onayı ile ders kaydı kesinleşir.
- Arapça: Danışman onayı, akademik takvimde belirtilen süre içinde alınmazsa, o dönemde öğrenimine devam etme hakkı kaybedilir.

Sınıf Yoklama Listesinde Adın Yoksa:

- Dansmandan onaylanmayan derslerin listesinde adınızı göremezsiniz.
- Bu durumda, sınıfta yoklama listesini imzalamak zorunda değilsiniz.
- Danışmanınıza ulaşıp, onayını almanız gerekir.
- Yoklama listesinde adınızın yoksa, danışmanınıza ulaşıp onayını almanıza gerek yoktur.

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
  - [x] beş iş günü
  - [ ] dilekçe
  - [ ] bölüm başkanlığı
- **Sure**: 7705.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

Sınav notuma itiraz etmek isteyen öğrencilerin 15 gün içerisinde fakülte/yüksekokuluna yazılı olarak başvurması gerekir (Kaynak 2: yüzde_on_başarı_değerlendirme_yönergesi.pdf).

İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz (Kaynak 2: yüzde_on_başarı_değerlendirme_yönergesi.pdf).

İtiraz, sınav kağıtlarının yeniden incelenmesi talebi olarak da yapılabilmektedir. Öğrenciler, sınav sonuçlarının açıklanmasından itibaren 5 iş günü içerisinde ilgili bölüme yazılı olarak başvurmak kaydıyla, sınav kağıtlarının yeniden incelenmesi talebinde bulunabilir (Kaynak 3: yonetmelik_onlisans_lisans_egitim_ogretim.pdf).

Yeniden inceleme, ilgili öğretim elemanı tarafından en geç 3 iş günü içinde yapılır. İtiraz olması halinde sınav kağıdı, ilgili öğretim elemanınca hazırlanmış cevap kağıdı da dikkate alınarak sınav inceleme komisyonu tarafından incelenir. İşlem, en geç 3 iş günü içinde sonuçlandırılır (Kaynak 3: yonetmelik_onlisans_lisans_egitim_ogretim.pdf).

İştiraz süreci, öğrenci bilgi sistemi aracılığıyla ilan edilen sınav sonuçlarından itibaren başlatılır ve en geç 15 gün içinde sonuçlandırılır.

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
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/6
  - [x] ders
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [x] ilişik kesme
  - [x] diploma
- **Sure**: 13484.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Mezun Olduğunuz Program Türüne ve Koşullarınıza Göre İlişkin Kesme Sürecini Adım Adım Açıklamak İhtiyacınız Varsa;

Bir Programın Şartlarını Geri Getirmek için Hangi Adıma Başlamalısınız? Sorusunu Cevaplayalım.

Açıkça Lisansüstü Programdan Bahsedilmemişse:

Yeni bir programı bitirme hakkını kazanan öğrenciler için diploma hazırlanması için aşağıdaki adımları izleyin:
a) Hazırlık hariç 4 yarıyıl süreli meslek yüksekokullarında bir mesleğe yönelik olarak yürütülmekte olan programlardan mezun olan öğrenciler için “Önlisans Diploması”,
b) Türk Ceza Kanununun ikinci kitabının birinci babında yer alan, Devletin şahsiyetine karşı işlediği cürümler sebebiyle hüküm giyenler ile disiplin cezası alarak yükseköğretim kurumlarından uzaklaştırılanlar hariç olmak üzere, 2547 sayılı Kanun hükümleri uyarınca bir lisans programının en az ilk dört yarıyılının bütün derslerinden başarılı olanlara “Önlisans Diploması”,
c) Hazırlık hariç, dört yıl süreli fakülte ve yüksekokul lisans programlarından mezun olan öğrenciler için “Lisans Diploması”,
d) Ana daldaki mezuniyetlerine bağlı olarak ikinci ana dal lisans programını tamamlayan öğrenciler için “Çift Ana dal Lisans Diploması”
e) Ana daldaki mezuniyetlerine bağlı olarak yandal lisans programlarını tamamlayan öğrenciler için “Yandal Sertifikası” 
f) Enstitülerdeki tezli veya tezsiz yüksek lisans programlarını tamamlayanlara “Tezli Yüksek Lisans diploması” veya “Tezsiz Yüksek Lisans diploması”
g) Enstitülerdeki doktora veya sanatta yeterlik programlarını tamamlayanlara “Doktora” veya “Sanatta Yeterlik diploması”

Diploma düzenlenmesi, ilgili enstitü sekreterliği ve Öğrenci İşleri Daire Başkanlığı tarafından kontrol edildikten sonra imzalanır.
Diplomalarda yer alan bilgileri kontrol eder ve diploma hazırlanır.

Lisans veya Yüksek lisans programından bahsettiniz.
Lisans mezunu için 4. Kaynağa göre aşağıdaki adımları izleyin.

Lisans Programı için Diploma Düzenleme Adımları:

4 yıllık programa kayıt yaptıran ve derslerden başarıl
... (2651 karakter daha)
```

### Q20: Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] 2. nüsha
  - [x] diploma
  - [x] e-devlet
  - [ ] YÖKSİS
- **Sure**: 15512.1 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Benchmark, Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Ne yapmalıyım?

Diploma sorunlarına ve e-devlet üzerinden mezuniyet bilgisi görünmemesine ilişkin çözüm adımları aşağıda belirtilmiştir.

* ilk olarak diplomanızın aslını kaybettiğinizden dolayı üzülmeyin. Kayıp ilanınızı yaygın gazetelerden birine yayımlatarak ve başvuru dilekçesi ile onaylı nüfus cüzdanı sureti ve diploma ücretini yatırdığını gösteren banka dekontu ile diploma aldığınız birimden yeni bir diploma alabilirsiniz.
* eğer e-devlet üzerinden mezuniyet bilgileriniz görünmüyor ise, öğrenci işleri birimlerinden sorunu çözmeniz için başvurmanız gereklidir.
* sorunu çözmek için yapmanız gereken şey, diplomanızı kaybettiğiniz veya e-devlet üzerinden mezuniyet bilgilerinizin görünmemesi durumunu Uluslararası Öğrenci Kabul Komisyonuna bildirmek ve bu konuda destek almak necesario olacaktır.
* bu durumda ilk olarak, başvuru sistemi üzerinden şifreniz ile giriş yaparak sorununuza ilişkin bilgi edinmelisiniz. Aksi takdirde, problemine ilişkin bilgi öğrenci işleri daire başkanlığından veya Uluslararası Öğrenci Kabul Komisyonundan edinebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
- Belge: tyb.pdf
- Belge: yurda_giriş_çıkış_belgesi.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: yonerge_uluslararasi_ogrenci_kabul.pdf
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
- **Sure**: 10754.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Yaniti vermeye başlamadan önce, belirtmek gerekir ki belgelere bakıldığında, Bilgisayar Muhendisligi bolumu/programi icin uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve basari degerlendirmesi yüz yüze derslerden farklı mıdır sorusuna ait net bilgi bulunmuyor. Bu nedenle, net bir yaniti veririm ancak bu yaniti desteklemek için belgelere referans vereceğim.

Her ne kadar belgeler 5-i derslerini belirtmese de, genel olarak uzaktan eğitim için 5-i derslerinin yüz yüze eğitimden farklı yapılış şekli hakkında belirtilmiyor. Ancak, Belgelerde 10. maddeye bakıldığında, yüz yüze ve uzaktan eğitim için ortak olarak belirtilen durumlar bulunuyor.

10. maddeye gore "Kosullar elverdiği ölçüde tüm sınavların yüz yüze yapılması esastır." Bu da yüz yüze ve uzaktan eğitim için aynı yöntem kullanılabileceğini gösteriyor. "Tüm sınavların yüz yüze yapılması esastır." cümlesi her iki halde de geçerli.

Dahası, 10. maddeye gore "Tamamı uzaktan veya bir kısmı uzaktan olan derslerin sınavları çevrimiçi olarak da yapılabilir." ifadesinin uzaktan eğitim için kullanılan yöntem için geçerli olduğunu gösterdiğini görebiliyoruz.

Bu nedenler dahilinde, yüz yüze ve uzaktan eğitim için sınavların yapılış şeklinin farklı olmadığı düşünülebilir. Bu durum, Bilgisayar Muhendisligi bolumu/programi icin 5-i derslerinin sınav ve basari degerlendirmesinin yüz yüze derslerden farklı olmayacağının bir sonucu da olabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
- Belge: uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Sure**: 11195.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

Sınavda kopya çekilmesinin cezası:

* Kopya çekmek ve bununla ilgili girişim halinde bulunmak, Ondokuz Mayıs Üniversitesi'nin sınav kurallarına göre disiplin suçudur.
* Bu gibi durumlarda sınav görevlisi veya ilgili öğretim elemanı, uyarıda bulunmaksızın öğrencilerin hakkında işlem yapabilirler.
* Kopya çekmek ve bununla ilgili girişim halinde bulunmak, sınav görevlilerinin her türlü uyarısına uymama ve sınav kurallarına aykırı davranışlarda bulunma olarak değerlendirilir.

Disiplin süreci:

* Disiplin süreçleri, Ondokuz Mayıs Üniversitesi Disiplin Yönetmeliği çerçevesinde yapılır.
* Disiplin süreçleri, 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesine göre yürütülür.
* Disiplin suçlarının tespiti için, sınav görevlileri ve ilgili öğretim elemanlarınca gerekli görülen durumlar üzerine soruşturma açılır.
* Disiplin soruşturması, Fakülte Dekanlığı veya Yükseköğretim Kurumu Öğrenci Disiplin Yönetmeliği hükümlerine göre yürütülür.
* Disiplin sürecinin tamamlanması sonrasında, öğrencilere yazılı olarak duyuru yapılır.

Önemli bilgiler:

* Sınav esnasında, sınav görevlilerinin her türlü uyarısına uymak zorunludur.
* Kopya çekmek ve bununla ilgili girişim halinde bulunmak, sınav kurallarına aykırı davranışlar olarak değerlendirilir.
* Disiplin süreçleri, disiplin suçu tespiti için Fakülte Dekanlığı veya Yükseköğretim Kurumu tarafından yürütülür.

Kaynak:

* [Kaynak 1: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf]
* [Kaynak 2: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf]
* [Kaynak 3: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf]
* Ondokuz Mayıs Üniversitesi Disiplin Yönetmeliği

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: s
... (69 karakter daha)
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
- **Sure**: 13397.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Üniversiteyi bırakıp ayrılmak istiyorsanız, lütfen aşağıdaki adımları izleyin:

1. Yazılı talebiniz: Öğrenci Toplulukları Yönergesi (MADDE 18) göre, öğrencinin yazılı talebiyle üyeliği sonlandırılabilir. Yazılmış talebinizde, nedeni ve talebinizin net bir şekilde ifade edilmesi gerekli. Talebinizi topluluk yönetimINE sunun.
2. Mazeretsiz General Kurul attendance: Geçerli bir mazereti olmaksızın üst üste iki Genel Kurul toplantısına katılmamışsanız, üyeliğiniz sonlandırılabilir. Talebinizi topluluk managementINE sunun.
3. Topluluk amaçlarına aykırı faaliyette bulunma: Topluluk amacına aykırı faaliyette bulunmuşsanız, üyeliğiniz sonlandırılabilir. Talebinizi topluluk managementINE sunun.
4. Görevlerin yerine getirilmemesi: Topluluk görevlerini yerine getirmemişseniz, üyeliğiniz sonlandırılabilir. Talebinizi topluluk managementINE sunun.
5. Kaydın Silinebilmesi: Kaydını sildiren öğrenci, ÖSYM tarafından yeniden yerleştirilmediği veya Üniversite tarafından yapılan ölçme ve değerlendirme sonucunda kayıt hakkı kazanmadığı sürece, Üniversiteye tekrar kaydolamaz.

Kaydı Silebilirken Dikkat Edilecek Hususlar

- *Kaydı silme talebi*: Öncelikle kaydı silme talebinizi yazılı olarak öğrenci bilgi sistemine iletin. Bu talep ile birlikte neden ve talebinizin net bir şekilde ifade edilmesi gerekli.
- *Mazeretinizin olmadığı halde iki genel kurul toplantısını geçirme*: Bu durum öğrenci topluluk yönetimi tarafından değerlendirilir, ve yazılı bir talepte bulunulması gerekebilir.
- *Görevlerin yerine getirilmemesi*: İlgili görevleri yerine getirmemek durumunda, öğrenci görevi icra eden yetkililere yazılı bir uyarı gönderilmelidir.
- *Kaydın silebilirken dikkat edilmesi gereken diğer hususlar:*
 + Yazılı talebiniz onaylandıktan sonra 7 gün içinde SKSDB'ye itiraz başvurusunda bulunabilirsiniz.
 + İtiraz başvurusu, başvuru tarihinden sonra toplanan ilk Etkinlik Kurulunda görüşülerek karara bağlanır.
 + Üyeliğine son verilen öğrenci aynı topluluğa yeniden üye olamaz.

Sonuç

ÜNİ
... (914 karakter daha)
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
- **Sure**: 11913.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Soru:
Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

Yaniti:
Ders seçimini yapabilmeniz için 1. yılında, kayıt döneminde ders seçme işlemlerini gerçekleştirebilirsiniz. Bu işlemler, akademik takvimde belirtilen süre içerisinde öğrenci bilgi sistemi üzerinden gerçekleştirilir.

Belirtilen süre içinde ders kaydını yapmayan öğrenciler, o dönem öğrenimlerine devam etme hakkını kaybederler. Kaybedilen dönem, öğrenim süresinden sayılır. Süresi içinde ders kaydını yapmayan öğrencilerin kayıtları; başvurmaları ve mazeretlerinin haklı ve geçerli olduğu ilgili birim yönetim kurulunca kabul edilmesi koşuluyla, akademik takvimde belirtilen süre içinde yapılabilir.

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
- **Sure**: 11414.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sorunun cevabı:

Hocam, ders notlarımı sisteme girmemişim. Bu durumda ne yapabilirim? 

Sorunun birden fazla alt-sorusu bulunmamaktadır, ama sorunun cevabı farklı alt-sorulara bölünebilir.

1. Ders kaydı yaptırmam gerekir mi?
Evet, yeni kayıt yaptıran öğrencilerimizin de ders kaydı yapması gerekmektedir. 

2. Ders kayıtlarını hangi tarihler arasında yapmam gerekir?
Ders kayıtlarınızı eğitim gördüğünüz birime ait akademik takvimde belirtilen süreler içerisinde yapmak zorundasınız. Akademik takvimlere Öğrenci İşleri Daire Başkanlığı WEB sayfasından ulaşabilirsiniz.

3. Ders kayıt işlemleri ne zaman tamamlanmalı?
Ders kaydın tamamlanması için akademik takvimde belirtilen süre içerisinde danışman onayını almak ve kaydın kesinleşmesi beklenmelidir. 

4. Nasıl davranmalıyız?
Ders kaydında üç önemli hususa dikkat etmeniz gerekir:
 - Eksik ders alarak dönem uzatmamak için her dönem başında müfredat durum kontrolü,
 - Akademik takvimde belirtilen süre içinde kaydın tamamlanması,
 - Danışman onayı işlemidir.

5. Danışman onayını nasıl alabilirim?
Danışman onayını sistem üzerinden alabilir, danışmanın sistem üzerinden iade etmesi durumunda da ders kaydınızı akademi takvimde belirtilen süresinde yeniden düzenleyerek danışmanınıza onaylatmalısınız.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
