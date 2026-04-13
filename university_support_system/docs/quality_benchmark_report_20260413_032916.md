# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-13 03:29:16
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 88.0% |
| Uretim Modu Dogrulugu | 84.0% |
| Anahtar Bilgi Kapsami | 53.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 4092.6 ms |
| Medyan Sure | 3672.2 ms |
| Intent Analizi Aktif | 22/25 |
| Force LLM Sentez | 21/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 24356.6 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 2/3 | 4557.3 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | OK | 2/4 | 1874.6 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 2/4 | 4377.0 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 2/3 | 5310.2 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 4479.6 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 2942.9 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 4343.2 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | OK | 4/5 | 3954.4 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 3998.0 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | YANLIS | OK | 2/4 | 3807.4 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 3/4 | 2267.8 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 5442.7 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 3/4 | 2324.9 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 3/3 | 3672.2 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | YANLIS (kural) | 3/4 | 2773.5 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 2/5 | 2672.2 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 1/4 | 1626.0 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | YANLIS (kural) | 2/6 | 1320.2 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 1/4 | 1968.0 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 1/5 | 4270.2 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 3936.7 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | YANLIS (kural) | 1/4 | 1369.5 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 2192.4 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 0/3 | 2477.7 | - |

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 24356.6 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, kayıt yaptırdığı öğretim yılının en geç 3. haftasının sonuna kadar muafiyet başvurusunu yapmalıdır. Başvuru yapıldıktan sonra karar çıkana kadar derslere devam etmesi gerekir. 

Muafiyet başvuruları için transkript ve ders içerikleri ile birlikte dekanlığa başvurmak gerekmektedir. 
Yatay geçiş başvurusu esnasında disiplin cezası alma durumu başvurunun kabul edilmemesine neden olabilir. 
Kesin kayıt tarihine kadar başvurular değerlendirebilir.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 4557.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Tek ders sınavına girebilmek için stajınızı tamamlamış olmanız gerekmez. Sınavda başarılı sayılmak için minimum not olarak CB almak gerekir. Başarı notu, dönem içi değerlendirmenin %15'i ile yılsonu/bütünleme sınavında alınan notun %85'inin toplamıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

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
- **Sure**: 1874.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sorununuzun cevabı için Kaynak 2: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf, MADDE 20 ve MADDE 6'ya bakıldığında "Başarısız olunan seçmeli dersin yeniden açılmaması halinde, öğrencinin isteği ve danışmanın önerisi doğrultusunda yönetim kurulu kararı ile başka bir seçmeli ders alınabilir" ifadesi yer almaktadır.

Bu ifade ışığında, başarısız olduğunuz seçmeli ders yerine başka bir seçmeli ders seçmeniz durumunda devam zorunluluğunuz değişmez. Devam zorunluluğu devam eder.

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
- **Key Facts**: 2/4
  - [x] transkript
  - [ ] dahil
  - [x] ortalama
  - [ ] tamamlamıştır
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 4377.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Pedagojik formasyon dersleri transkript içinde yer alır. Bu dersler mezuniyet ortalamasına dâhil edilir. Diplomaların arkasına “Pedagojik formasyon eğitimi” ibaresi yer alır. Transkript belgesini öğrenimine devam eden öğrenciler bölüm/program sekreterliklerine, mezun olan öğrenciler ise Öğrenci İşleri Daire Başkanlığı diploma birimine başvurarak alabilirler.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

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
- **Key Facts**: 2/3
  - [x] ücret
  - [ ] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 5310.2 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Ücretinizi yatırırken, ilgili kanitlarda konkrét banka bilgisi yer almasa da, international öğrenci olarak kayıt yaptırırken öğrenim ücretini yatırmanız gerektiğini bilir. Kayıt işlemlerine ve koşullarına ilişkin bilgiler, Ondokuz Mayıs Üniversitesi'nin ilgili web sayfalarında duyurulmaktadır.

İkamet izni içinneeded belgeleri kesin kayıt süreci sırasında sunmanız gerekir, bu belgelerin ne olduğu konusunda net bilgi bulunmasa da, başvuruda doğru ve tarafınıza ait bilgi ve belgeleri sunmanız önemlidir. Önemli olan, başvurunuzda doğru ve eksiksiz bilgi sunmak ve kayıt işlemlerini zamanında tamamlamaktır.

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
- **Key Facts**: 3/4
  - [ ] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 4479.6 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
ÇAP programına başvurmak için hazırlık sınıfında başarılı veya muaf olmanız ya da Yükseköğretim Kurulu tarafından tanınan ulusal veya uluslararası geçerliliği olan yabancı dil sınavlarının herhangi birinden başarılı olmanız gerekmektedir. Harç borcunuz bulunuyor ise bu borcu ödemeniz必要dir, ancak ödenme şekli hakkında departmanlardan alınan bilgilere göre herhangi bir açıklama bulunmamaktadır. ÇAP başvuru koşulları, senato tarafından belirlenen koşullara uygun olması gerekmektedir.

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
- **Departman**: ['student_affairs', 'finance', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2942.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Ders kaydı yenileme döneminde, harç ücretini yatırdıktan sonra ders kaydı yapılır. Danışman onay süreci için öğrenci, akademik takvimde belirtilen süre içinde öğrenci bilgi sistemi üzerinden alacakları dersleri seçer ve danışman onayı ile ders kaydı kesinleşir. 

Danışmandan onay alabilmek için öğrenci, akademik takvimde belirlenen süre içinde kaydını yapmalıdır. Danışman onayını alamayan öğrenciler, bölüm başkanlığına veya Dekan/Müdürlüğe başvurabilir. Eğer hiçbir yetkiliye ulaşılamıyorsa oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yoluyla iletebilirsiniz. 

Öğrenciler, kayıt yapmış oldukları dersleri danışman onayından sonra kontrol etmeli ve herhangi bir değişiklik yapılmış ise bunu göz önünde bulundurmalıdır.

Akademik Programlar:
Bu akademik program sorusunu dogru cevaplayabilmem icin once bolum veya program bilgisini bilmem gerekiyor. Ornegin 'Bilgisayar Muhendisligi icin 1. yariyil dersleri nelerdir?' veya 'Kimya bolumu teknik secmeli dersleri hangileri?' seklinde sorabilirsin. Kisisel ilerleme bilgisi istiyorsan OTP ile giris yapman yeterli; bolum bilgin oturumdan alinabilir.

Finans:
Ogrenim ucreti ogrenci turune ve birime gore degisiyor. Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: Kural
- Akademik Programlar: Kural

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
- **Sure**: 4343.2 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Bursluluk durumunuzun yeni üniversitede etkisini öğrenmek için burs aldığınız kurumla iletişime geçmeniz gerekmektedir. Bursun devri veya kesilmesi konusunda bilgi alabilirsiniz. Öğrenci İşleri Daire Başkanlığı harç bürosuna başvuru yaparak harç iadseniz hakkında da bilgi edinebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
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
- **Sure**: 3954.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
4. sınıf öğrencisi olarak normal öğrenim süresini 1 yıl aşmişsin. Tıp Fakültesi için normal eğitim-öğretim süresi 6 yıldır, ancak katkı payı ve öğrenim ücreti ile ilgili özel durumlar için yönetim kurulunun kararı önemlidir. Ek süre hakkında specific bir bilgi bulunmamaktadır, ancak genel olarak katkı payı ödemen requiredir.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=conditional
- **Sure**: 3998.0 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Bir dersten devamsızlıktan kalan öğrenci o dersin bütünleme sınavına giremez. Bu dersi tekrar almak için ise ders kaydının yapılmış ve devam zorunluluğunun yerine getirilmiş olması gerekir.

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
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] öğrenim ücreti
  - [ ] gerek yok
  - [x] yönetim kurulu
  - [ ] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=conditional
- **Sure**: 3807.4 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Kayıt dondurma isteğinizin ilgili yönetim kurulunca kabul edilmesi durumunda öğrenim ücretini yatırmak zorunda değilsiniz. Ayrıca, kayıt dondurma süresi eğitim süresinden sayılır. 
- Kayıt dondurmak için yönetim kurulunun onayını beklemelisiniz.
- Öğrenci katkı payı/öğrenim ücreti ödemekle yükümlü olmadığınız durumlarda, akademik takvimde belirtilen süreler içinde gerekli işlemleri takip etmelisiniz.
- Kayıt yenileme veya dondurma işlemlerinde, akademik takvimde belirlenen süre ve şartlara dikkat etmelisiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=conditional
- **Sure**: 2267.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Evet, hazırlık sınıfındaysanız ve transkriptiniz yoksa, Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilirsiniz. Ek Madde-1 kapsamında yapılan yatay geçiş başvurularında öğrencinin GANO'su değerlendirme aşamasında etkili değildir.

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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 5442.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçiş, aynı üniversitenin dentro farklı diploma programları arasında yapılır. Kurumlar arası yatay geçiş ise farklı yükseköğretim kurumları arasındaki geçişleri ifade eder. Başvuru şartları olarak disiplin cezası almamış olmak ve kayıt dondurma durumunu belgelemek gereklidir. Öğrenci kontenjanı yıllık %15'i geçmeyecek şekilde dönemlere bölünür. Yatay geçiş kontenjanları ilgili yönetim kurulunun önerisi ve Senato kararı ile belirlenir. Başvurular, önceden ilan edilen kontenjan ve şartlar çerçevesinde yapılır. 
- Kurum içi yatay geçiş için eşdeğer düzeyde diploma programlarına başvurulur.
- Kurumlar arası yatay geçiş için yükseköğretim kurumlarının diploma programları arasındaki geçişler dikkate alınır.
- Yükseköğretim Kurulu tarafından tanınan yurt dışı yükseköğretim kurumlarının diploma programları da yatay geçiş kapsamında değerlendirilir.

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
- **Key Facts**: 3/4
  - [x] bağıl
  - [x] mutlak
  - [ ] 10
  - [x] öğrenci sayısı
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 2324.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark ve hangi öğrenci sayısında hangisinin uygulanacağı konusunda elimdeki kaynaklarda net bilgi bulunamadı.

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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=comparative
- **Sure**: 3672.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Diploma eki, transkript yerine geçmez. Diploma eki, kişinin takip edip başarıyla tamamladığı öğrenimin yapı, düzey, bağlam, içeriği ve statüsünü tarif etmek üzere verilir. Transkript, not çizelgesidir ve diploma yerine de geçmez. Diploma eki ile hangi kazanımları elde edebileceğinizi öğrenmek için, diploma ekinin amaç ve içeriği hakkında bilgi alınabilir. 

Diploma ekinin kullanımı hakkında bazı noktalara dikkat etmek gerekir:
- Diploma eki, yurtdışında daha okunabilir ve mukayese edilebilir bir diploma ve akademik güzergâhının anlaşılmasını sağlar.
- Avrupa’deki bazı kurumlar tarafından tanınır ve kabul edilir. 
- Ancak transkript ile混up edilmemelidir, bunlar birbirinden farklı belgelerdir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: avrupa_birliği_eğitim_ve_gençlik_programları_hayat_boyu_öğrenme_erasmus.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 3/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 2773.5 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Kayıt dondurma ve kayıt yaptırmamak arasındaki temel fark, kayıt dondurmanın belirli bir süre için eğitimöğretimine ara verme anlamına gelirken, kayıt yaptırmamadan anlaşılması gereken, bir dönem veya yıl için ders kaydının yapılmamasıdır. Her iki durumda da öğrencilik hakları etkilenir. Kayıt dondurma durumunda, öğrenci belgelendirecekleri önemli mazeretlerinin veya eğitimöğretimlerine katkıda bulunacak üniversite dışı imkânların ortaya çıkması halinde, ilgili birimin yönetim kurulu kararı ile belirli bir süre için kayıt dondurabilir. Kayıt yaptırmamak durumu ise, akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden ders kaydının yapılmaması anlamına gelir. Ders kaydının yapılmaması, öğrencinin o dönem veya yıl için öğrencilik haklarından yararlanamaması sonucunu doğurur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: Kural
- Finans: Kural

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf
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
- **Sure**: 2672.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatmak için;

Öncelikle, nouvel kayıt yaptıran öğrencilerin de ders kaydı yapması gerekmektedir. Ders kayıtlarını, akademik takvimde belirtilen süreler içerisinde yapmak zorundasınız. Akademik takvimlere Öğrenci İşleri Daire Başkanlığı WEB sayfasından ulaşabilirsiniz.

Ders kaydında üç önemli hususa dikkat etmeniz gerekir: 
1. Eksik ders alarak dönem uzatmamak için her dönem başında müfredat durum kontrolü,
2. Akademik takvimde belirtilen süre içinde kaydın tamamlanması,
3. Danışman onayı işlemi.

Danışman, kayıt olmak istediğiniz derslerde değişiklik yapma hakkını sahiptir. Devam şartınız olmasa bile, derslerin sınavlarına girebilmek için ders kaydı yapmanız gerekmektedir.

Danışmanınıza ulaşamadığınız takdirde, bölüm başkanınıza, bölüm başkanınıza da ulaşamazsanız Dekan/Müdürünüze durumu bildirmek sureti ile akademik takvimde belirtilen sürede danışman onayını muhakkak yaptırınız. Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz.

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
- **Key Facts**: 1/4
  - [x] itiraz
  - [ ] beş iş günü
  - [ ] dilekçe
  - [ ] bölüm başkanlığı
- **Sure**: 1626.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınav notuna itiraz etmek için, sonuçların açıklanmasından itibaren 5 iş günü içerisinde ilgili bölüme yazılı olarak başvurmak gerekir. İtiraz süresi 15 gün olarak belirtilmiştir. İtiraz edilen sınav kağıtları, ilgili öğretim elemanı tarafından en geç 3 iş günü içinde yeniden incelenir. İtiraz durumunda sınav kâğıdı ve cevap kâğıdı, sınav inceleme komisyonu tarafından incelenir ve sonuç, en geç 3 iş günü içinde sonuçlandırılır. Ayrıca, öğretim elemanı tarafından fark edilen maddi hataya ilişkin sınav not bildirim/not düzeltme formu, notların ilanından itibaren en geç 60 gün içinde ilgili birime sunulur. Yeniden incelemeye 3 iş günü içinde itiraz edilebilir. Yönetim Kurulunca verilen karar kesindir.

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
- **Key Facts**: 2/6
  - [ ] ders
  - [x] staj
  - [ ] GANO
  - [ ] 2,00
  - [ ] ilişik kesme
  - [x] diploma
- **Sure**: 1320.2 ms
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
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 1968.0 ms
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
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs', 'academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [ ] %40
  - [ ] %60
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4270.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi, koşullar elverdiği ölçüde, yüz yüze sınav esasına dayanır. Ancak tamamı uzaktan veya bir kısmı uzaktan olan derslerin sınavları çevrimiçi olarak da yapılabilir. 
Öğrencilerin derslere devam durumu, dersin öğretim elemanınca yapılan yoklamalarla tespit edilir. Örgün eğitimde öğrencilerin yüz yüze yürütülen derslerin teorik saatlerinin en az % 70’ine; ders uygulamaları, atölye ve laboratuvarların ise en az % 80’ine devam etmiş olma koşulu aranır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 3936.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Sınavda kopya çekilmesinin cezası, 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesine göre disiplin hükümlerine göre belirlenir. Disiplin süreci, ONDOKUZ MAYIS ÜNİVERSİTESİ MÜHENDİSLİK FAKÜLTESİ SINAVLARDA UYULMASI GEREKEN KURALLAR göre yürütülür. 
- Sınava giren öğrencilerin sınav kağıtlarında değişiklik yapması yasaktır.
- Öğrenciler, sınavlara girebilmek için öğrenci kimlik belgelerini yanlarında bulundurmak zorundadır. 
Disiplin süreci hakkında detaylı bilgi için 11.03.2023 tarihli resmi gazetede yayımlanan 2547 sayılı Yüksek Öğretim Kanunu Madde 54'e başvurulmalıdır.

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
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 1/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [x] birim
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 1369.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Kural

Kaynak Ozeti:
- Belge: öğrenci_toplulukları_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2192.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu konuda elimdeki kaynaklarda net bilgi bulunan husus; kayıt dondurma süresinin bitiminde öğrenci, ayrıldığı dönemin/yılın başından başlamak koşuluyla, öğrenimine kaldığı yerden devam eder. Ancak, ders seçimini hvordan yapılacağına ilişkin spesifik bilgiye ulaşılamamıştır.

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
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 0/3
  - [ ] danışman
  - [ ] bölüm
  - [ ] oidb@omu.edu.tr
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 2477.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu konuda elimdeki kaynaklarda net bilgi bulunamadı. Verilen belgelerde not girişi ile ilgili bir bilgiye rastlanılmadı. Belirtilen durumla ilgili olarak Öğrenci İşleri Daire Başkanlığı ile iletişime geçilmesi рекомендуется.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
