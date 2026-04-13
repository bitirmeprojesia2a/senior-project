# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-13 02:12:52
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 88.0% |
| Uretim Modu Dogrulugu | 72.0% |
| Anahtar Bilgi Kapsami | 47.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 2861.5 ms |
| Medyan Sure | 2567.4 ms |
| Intent Analizi Aktif | 23/25 |
| Force LLM Sentez | 21/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 6690.3 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | YANLIS (rag) | 2/3 | 2620.2 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | YANLIS (rag) | 2/4 | 519.6 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | YANLIS (rag) | 3/4 | 2477.5 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 3428.4 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 2/4 | 3243.9 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 2621.1 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 4392.1 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | OK | 4/5 | 2553.4 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 5063.6 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | YANLIS | OK | 3/4 | 2077.7 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 2/4 | 2567.4 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 5209.2 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 2/4 | 2377.2 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 3/3 | 2993.2 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | YANLIS (kural) | 0/4 | 1381.3 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 2/5 | 2878.1 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | YANLIS (rag) | 1/4 | 423.3 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | YANLIS (kural) | 1/6 | 1204.3 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 1/4 | 2235.6 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 1/5 | 3130.9 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 2466.1 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 2413.4 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 0/4 | 4293.7 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 0/3 | 2276.4 | - |

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
- **Sure**: 6690.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, kayıt yaptırdığı öğretim yılının en geç 3. haftasının sonuna kadar muafiyet başvurusunu yapmalıdır. Bu süreçte öğrenci, daha önce aldığı ve başarılı olduğu derslerden muaf olmak için transkripti ve ders içeriklerini birlikte dekanlığa sunmalıdır. Muafiyet başvurusu sonuçlanana kadar öğrenci derslere devam etmelidir.

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
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/3
  - [x] staj
  - [x] tamamla
  - [ ] CC
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 2620.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Tek ders sınavına girebilmek için stajınızı tamamlamış olmanız gerekmez. Bir dersten başarılı sayılmak için minimum not CB olmalıdır.

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
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [ ] yeni
  - [x] ders
- **Sure**: 519.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
MADDE 21 – (1) Lisansüstü öğrenci, başarısız olduğu dersleri tekrar almak ve başarmak zorundadır. Devam koşulunun yerine getirilmediği tekrar derslerine devam etmek esastır. Devam mecburiyeti olmayan öğrenciler de yarıyıl içi değerlendirmelerine katılmak zorundadır. Eğitim programının özelliği gerektirdiğinde, anabilim/anasanat dallarının, devam koşulunu sağlayıp başarısız olmuş öğrencilerin derse devam etmesini istemeleri halinde bu uygulama enstitü kurulunun kararı ile gerçekleştirilir. (2) Başarısız olunan dersin zorunlu dersler hariç, takip eden yarıyılda açılmaması veya programdan kaldırılmış olması halinde danışmanın önerisi ve ilgili anabilim/anasanat dalı başkanlığının uygun görüşü ile bu dersin yerine başka bir lisansüstü ders alabilir. Yarıyıl içi değerlendirme ve yarıyıl sonu sınavları

(Kaynak: yonetmelik_lisansustu_egitim_ogretim.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

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
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 3/4
  - [x] transkript
  - [x] dahil
  - [x] ortalama
  - [ ] tamamlamıştır
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 2477.5 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Pedagojik formasyon dersleri transkripte dahil ediliyor. Mezuniyet ortalamasına etkisi var. Diplomaların arkasına "Pedagojik formasyon" ibaresi yer alıyor. 
- Transkript içinde bu dersler yer alacak. 
- Sadece bir transkript düzenlenecek. 
- Mezuniyet ortalamasına dahil ediliyor.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Akademik Programlar: RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt
- Belge: lisans_pedagojik_formasyon_derslerine_ilişkin.pdf
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
- **Sure**: 3428.4 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Ogrenci Isleri:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

Akademik Programlar:
Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretini nereye yatırmaya gerek duyduğunuz konusunda elimdeki kaynaklarda net bilgi bulunamadı. 

İkamet izni için hangi belgelerin hazırlanması gerektiğini sorduğunuzda, Türkiye’de vize, vize muafiyeti, ikamet izni veya ikamet izni yerine geçen belgeler ile yasal kalış süresi içerisinde olmanız gerektiğini ve öğrenci ikamet izni için Göç İdaresi Başkanlığı’na başvuruda bulunmanız gerektiğini belirten bilgiler kaynaklarda mevcuttur.

Not: Uluslararasi ogrenci harc ucretleri ve odeme detaylari icin finans birimi (tuition_agent) ile iletisime gecmeniz onerilir.

Finans:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

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
- **Key Facts**: 2/4
  - [x] not ortalaması
  - [x] harç
  - [ ] ödeme
  - [ ] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3243.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Akademik Programlar:
ÇAP programa başvurmak için gereken koşullar:
- Ana dal diploma programının en erken üçüncü yarı yılının başında, en geç ise beşinci yarı yılın başında başvurabilirsiniz.
- Başvurduğunuz yarı yıla kadar ana dal lisans programında yer alan tüm dersleri almış ve başarmış olmanız gerekmektedir.
- Ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk % 20'sinde bulunmanız gerekmektedir.

Harç borcunun ödenmesi ile ilgili bilgi:
Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

Finans:
Ogrenim ucreti ogrenci turune ve birime gore degisiyor. Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin.

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
- **Departman**: ['student_affairs', 'finance', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2621.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden ders seçimi yapılır. Daha sonra danışman onaylanması gerekir. Danışman onayı işleminden sonra, kayıtlanmış olduğunuz dersleri kontrol ediniz. Zira danışmanınız tarafından listeden bazı dersler çıkartılmış olabilir.

Danışmanıma ulaşamazsam ne yapmam gerekir?
Bölüm başkanınıza, bölüm başkanına da ulaşamazsanız Dekan/Müdürünüze durumu bildirmek sureti ile akademik takvimde belirtilen sürede danışman onayını muhakkak yaptırınız. Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 4392.1 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Bursunuzun devri veya kesilip kesilmeyeceği konusunda bilgiye ulaşmak için burs aldığınız kurumla iletişim kurmanız gerekmektedir. Bazı durumlarda harç iadesi mümkün olabilir, bu konuda ise bir dilekçe ve IBAN numaranızı bildirerek Öğrenci İşleri Daire Başkanlığı harç bürosuna başvurmanız gerekmektedir. Yatay geçiş işlemleri ise önceden ilan edilen kontenjan ve şartlar çerçevesinde Yükseköğretim Kurulu onayı alınarak yapılır.

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
- **Sure**: 2553.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Akademik Programlar:
Öğrenci program süresini 1 yıl aştığından, ek süre hakkının var olup olmadığını ve bu sürede katkı payı ödeyip ödeyemeyeceğini sormaktadır. Verilen kaynaklar incelendiğinde, bu konuyla ilgili bir bilgi bulunamamıştır. 

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

Finans:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 5063.6 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Bir dersten devamsızlıktan kalan öğrenci o dersin bütünleme sınavına giremez. Bu dersten başarılı olmak için wieder aynı dersi tekrar almanız gerekir.

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
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] öğrenim ücreti
  - [ ] gerek yok
  - [x] yönetim kurulu
  - [x] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2077.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
İkinci öğretim öğrencisi olarak kayıt dondurmak istediğinizde, kayıt dondurma isteğinizin ilgili yönetim kurulunca kabul edilmesi durumunda, öğrenim ücretini yatırmak zorunda değilsiniz. Kayıt dondurduğunuz süreler ise eğitim-öğretimden sayılmaz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
```

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] transkript
  - [x] Ek Madde
  - [ ] başvuru yapabilir
  - [ ] GANO
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2567.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

Akademik Programlar:
Soru: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

Yanit: Bu konuda elimdeki kaynaklarda net bilgi bulunamadi.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: lisansüstü_eğitim_ve.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 5209.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçiş, aynı üniversite içindeki farklı diploma programları arasında yapılan geçiştir. Kurumlar arası yatay geçiş ise farklı üniversiteler arasında yapılan geçiştir. 
Örneğin, disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez ve disiplin cezası almadıklarını belgelemeleri şarttır. 
Kurum içi yatay geçiş kontenjanları, ÖSYM Kılavuzunda öngörülen öğrenci kontenjanının yıllık % 15 ini geçmeyecek biçimde dönemlere bölünerek ilgili yönetim kurulunun önerisi ve Senato’nun kararı ile belirlenir. 
Yatay geçişler, ilgili enstitü içindeki başka bir enstitü anabilim/anasanat dalından veya eşdeğer eğitim veren yurt içi ve Yükseköğretim Kurulu tarafından tanınan yurt dışı lisansüstü programlar arasında yapılır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
```

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] bağıl
  - [x] mutlak
  - [ ] 10
  - [ ] öğrenci sayısı
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 2377.2 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark, öğrencilerin değerlendirilme şeklini ifade eder. Mutlak değerlendirmede, öğrencilerin notları belirli bir ölçeğe göre hesaplanır ve bu ölçek esas alınarak başarılı veya başarısız sayılırlar. Bağıl değerlendirmede ise, öğrencilerin notları genel olarak sınıfın başarısına göre belirlenir.

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
- **Sure**: 2993.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Ogrenci Isleri:
Diploma eki ile transkript arasındaki fark, diploma ekinin bir yükseköğretim diplomasına ek olarak verilen, elde edilmiş yeti ve becerilerin ifade edildiği bir belge olmasıdır. Transkript ise öğrencinin başarı ve not çizelgesini gösteren bir belgedir.

Diploma eki, transkript yerine kullanılamaz. Kaynaklarda açıkça belirtilen bilgiye göre, "Diploma eki transkript (not çizelgesi) veya diploma yerine geçmez." 

Transkript belgesini öğrenimine devam eden öğrenciler, bölüm/program sekreterliklerine şahsen başvurarak alabilirler. Mezun olan öğrenciler ise Öğrenci İşleri Daire Başkanlığı diploma birimine şahsen müracaat ederek alabilir, kendisi gelip alamıyor ise bir dilekçe ile adresine gönderilmesini isteyebilir. Transkript belgesinin 1 adedi ücretsiz olup, birden fazla talep edilmesi durumunda 10₺ yatırıldığına dair dekont gönderilmesi halinde 3 adet transkript alınabilir.

Akademik Programlar:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] kayıt dondurma
  - [ ] sayılma
  - [ ] süre
  - [ ] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=comparative
- **Sure**: 1381.3 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Kural

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
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
- **Sure**: 2878.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci açıklamak için yeterli bilgi bulunmamaktadır. Kayıt sürecinde dikkat edilmesi gereken hususlar ve danışman onayının önemi hakkında bazı bilgilere ulaşılmaktadır. 
- Ders kaydında dikkat edilmesi gereken üç önemli husus şunlardır: Her dönem başında müfredat durum kontrolü, akademik takvimde belirtilen süre içinde kaydın tamamlanması ve danışman onayı işlemleridir.
- Eğitim gördüğünüz birime ait akademik takvimde belirtilen süreler içerisinde ders kaydı yapmak zorunludur.
- Danışman, kayıt olmak istediğiniz derslerde değişiklik yapma hakkına sahiptir.
- Devam şartınız olmasa bile derslerin sınavlarına girebilmek için ders kaydı yapmanız gerekmektedir.
Ancak, tüm süreci başından sonuna anlatmak için bu bilgiler yeterli değildir. Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

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
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/4
  - [x] itiraz
  - [ ] beş iş günü
  - [ ] dilekçe
  - [ ] bölüm başkanlığı
- **Sure**: 423.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
MADDE 8 - (1) Sınav sonuçlarına itiraz Ondokuz Mayıs Üniversitesi Ön Lisans ve Lisans Eğitim-Öğretim Yönetmeliğine uygun olarak yapılır. Tebligat adresi

(Kaynak: yonerge_ders_yeterlilik_sinavi_uygulama.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

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
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [ ] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 1204.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Kural

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2235.6 ms
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 3130.9 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Ogrenci Isleri:
Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi, yüz yüze derslerden farklı değildir. Öğrenciler, ortak zorunlu dersleri yüz yüze veya uzaktan eğitim yoluyla alabilirler ancak "Derslerin yüz yüze veya uzaktan eğitim yoluyla yürütülmüş olmasına bakılmaksızın bu derslerin sınavları, zorunlu hâller dışında, yüz yüze yapılır."

Akademik Programlar:
Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi, yüz yüze derslerden farklı olabilir. Uzaktan eğitimde, sınavlar çevrimiçi olarak da yapılabilir ve dönem içi değerlendirme, dersin özelliğine göre sorumlu öğretim elemanının belirleyeceği sınav, proje, ödev gibi yöntemlerle yapılabilir. Ayrıca, Uzaktan eğitim öğrencilerinin başarı notu, yarıyıl içi sınavının %15’i ile yılsonu/bütünleme sınavında alınan notun %85’inin toplamıdır.

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
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2466.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınavda kopya çekilmesinin cezası hakkında net bilgi bulunamamıştır. Ancak, sınav görevlileri kopya çekme girişiminde bulunan öğrenciler hakkında işlem yapabilirler ve bu durum disiplin suçu olarak değerlendirilir. Disiplin süreci 11.03.2023 tarihli resmî gazetede yayımlanan 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesine göre yürütülmektedir.

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
- **Key Facts**: 0/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [ ] birim
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2413.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Üniversiteyi bırakıp ayrılmak için öğrencilerin Öğrenci İşleri Daire Başkanlığına yazılı başvurmaları gerekir. Ancak bu konuda elimdeki kaynaklarda net bilgi bulunamadı. Öğrenci İşleri Daire Başkanlığı'na başvururken dikkat edilmesi gereken hususlar hakkında bilgi bulunmamaktadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_toplulukları_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: kimlik_kartı_yönergesi.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 0/4
  - [ ] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4293.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Okulumuzu dondurup 1 yıl ara verdikten sonra dönüşümüzde, eğitim öğretim yönetmeliğine göre, önemli mazeretlerin veya eğitim-öğretimimize katkıda bulunacak Üniversite dışı imkânların ortaya çıkması halinde, ilgili birimin yönetim kurulu kararı ile bir defada en fazla iki dönem eğitim-öğretimine ara verebiliriz. Dönüşümüzde ders seçimi için, eğitim öğretim döneminde hem örgün hem uzaktan veya sadece uzaktan verilmesi planlanan dersleri, kontenjanları, dersleri verecek öğretim elemanları ve haftalık ders programlarını dikkate alacağız. Ayrıca, Erasmus Ders Kataloğundan yararlanabileceğiz. 
Önemli mazeretler veya eğitim-öğretimimize katkıda bulunacak imkânların olup olmadığını dikkate alacağız.
Dönüşte alacağı derslerin seçimi için Üniversite internet sayfasından ulaşabileceği katalogdan yararlanacağız.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 0/3
  - [ ] danışman
  - [ ] bölüm
  - [ ] oidb@omu.edu.tr
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 2276.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
