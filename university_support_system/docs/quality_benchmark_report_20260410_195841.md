# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 19:58:41
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 80.0% |
| Uretim Modu Dogrulugu | 76.0% |
| Anahtar Bilgi Kapsami | 55.0% |
| Temiz Kalite Orani | 92.0% |
| Ortalama Sure | 5421.8 ms |
| Medyan Sure | 5483.2 ms |
| Intent Analizi Aktif | 22/25 |
| Force LLM Sentez | 21/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 4339.6 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | YANLIS (rag) | 3/3 | 6687.3 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | YANLIS (unknown) | 1/4 | 107.1 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 2/4 | 8956.9 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | YANLIS | OK | 3/3 | 6703.2 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 8927.3 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | YANLIS (vt) | 4/5 | 4132.1 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 8806.6 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | OK | 3/5 | 6663.7 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 2/4 | 4200.1 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | YANLIS | YANLIS (vt) | 0/4 | 2493.6 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 2/4 | 8078.3 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 1/5 | 5356.1 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 4/4 | 7072.2 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 3/3 | 6460.0 | uydurma_riski |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 4702.6 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 3925.5 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 1/4 | 2180.7 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 5/6 | 7731.8 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 6023.8 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | YANLIS | OK | 1/5 | 4503.2 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 4701.1 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 2/4 | 6038.2 | uydurma_riski |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 5483.2 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | YANLIS (kural) | 0/3 | 1271.7 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4339.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Muafiyet başvurusunun konusuna gelmeden önce, yatay geçişle gelen öğrencilerin genel olarak muafiyet başvurusunu yapmaları gerektiği ve bu başvurulara ilişkin kararın kesinleşene kadar öğrencilerin derslere devam etmeleri gerekir.

Muafiyet başvurusunun detaylarına gelmek için, en yakın kayıt dönemi bilgisi gerekmektedir. 26.08.2026 - 06.09.2026 tarihleri arasındaki 2026-Guz kayıt dönemi planlanmıştır.

Muafiyet başvurusu, kayıt döneminin sona ermesinin ardından 7 gün içerisinde yapıldığı varsayımı ile birlikte, yatay geçişle gelen öğrenciler kayıt yaptırma tarihinden itibaren 15 gün içersinde muafiyet başvurusunu yapmalidir.

Derslere devam etme hususunda akademik bir düzenleme olmaması nedeniyle, kayıt yaptırılmasına bağlı olarak öğrencilerin derslere devam etme zorunluluğu mevcuttur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: VT
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: kayit donemi
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
```

### Q2: Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi ve sınavda başarılı sayılmam için minimum not kaç?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 3/3
  - [x] staj
  - [x] tamamla
  - [x] CC
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 6687.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi? 

Hayır, staj tamamlama zorunluluğu yoktur. 

Sınavda başarılı sayılmam için minimum not kaç? 

Not CC.

Detaylar:

- Öğrenciler, bütünleme sınav notlarının ilanını takip eden beş iş günü içinde dilekçe ile staj durumuna bakılmaksızın bütünleme sınavına girme şartlarını yerine getirmiş olmak şartıyla akademik takvimde belirtilen tarihte açılacak tek ders mezuniyet sınavına girerler.
- Tek ders mezuniyet sınavlarında alınan not, ara sınav şartı aranmaksızın en az CC ise öğrenci başarılı sayılır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Akademik Programlar: RAG

Kaynak Ozeti:
- Belge: staj_esaslar.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: yabancı_dil_eğitim_öğretimi_yönergesi.pdf
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
- **Sure**: 107.1 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Bu akademik program sorusunu dogru cevaplayabilmem icin once bolum veya program bilgisini bilmem gerekiyor. Ornegin 'Bilgisayar Muhendisligi icin 1. yariyil dersleri nelerdir?' veya 'Kimya bolumu teknik secmeli dersleri hangileri?' seklinde sorabilirsin. Kisisel ilerleme bilgisi istiyorsan OTP ile giris yapman yeterli; bolum bilgin oturumdan alinabilir.
```

### Q4: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] transkript
  - [ ] dahil
  - [x] ortalama
  - [x] tamamlamıştır
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 8956.9 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Sonuç

Pedagojik formasyon dersleri, öğrenci müfredatlarından bağımsız olarak alınıp alınmadığı hakkında bilgi bulunmasa da, Akademik Programlar departmanının verdiği bilgilere göre, mezuniyet ortalamasına dâhildir. Diplomalara ise "Pedagojik formasyon eğitimini tamamlamıştır" ifadesi yazılacaktır. 

Diploma eki ile ilgili olarak, daha okunabilir ve mukayese edilebilir bir diploma oluşturacak olup, akademik güzergâhının ve yurtiçinde ve yurtdışında edindiği yeti ve becerilerin tam bir tarifi olacaktır.

Detaylar

- Mezuniyet ortalamasına etkisi: Pedagojik formasyon dersleri mezuniyet ortalamasına dâhil edilir.
- Diplomada ibare: Diplomaların arkasına "Pedagojik formasyon eğitimini tamamlamıştır" ifadesi yazılacaktır.
- Diploma eki: Daha okunabilir ve mukayese edilebilir bir diploma oluşturacak, akademik güzergâhının ve yurtiçinde ve yurtdışında edindiği yeti ve becerilerin tam bir tarifi olacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt
- Belge: uygulama_esaslari_lisans_pedagojik_formasyon.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
```

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['academic_programs', 'finance', 'student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] ücret
  - [x] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 6703.2 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Ogrenci Isleri:
Öğrenci Isleri'nin sundugu bilgiler ışığında, uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretini Ziraat Bankası'nın herhangi bir şubesinden öğrenci numaranızla yatırmalısınız. 

Öte yandan, ikamet izni için gereken belgeleri belirlemek hususunda elimdeki kaynaklarda net bilgi bulunamadı. Önerimiz bu konuda öğrencinin öğrenci isleri biriminize müracaat etmesi ve gereken bilgilere ulaşması olacaktır.

Akademik Programlar:
Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretini nereye yatırmak gerekiyor?

Kaynak 1'de, "Öğrencinin kesin kaydı, asıl belgelerini şahsen Öğrenci İşleri Daire Başkanlığına teslim etmeleri ile gerçekleşir." diye yazıyor. Başka bir kaynakta öğrenim ücretinin nereye yatırılacağına dair net bilgi bulunmuyor.

Öte yandan, kaynak 3'te, öğrencilerin "öğrenim payını yatırmak suretiyle öğrenimine devam edilir." deniliyor. Bu ifade, öğrenim ücretinin neye benzediğini veya hangi adla adlandırıldığını göstermiyor.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı. İlgili sorunun sorulduğunun Üniversite'sinin Uluslararası İlişkiler Ofisi'ne yollanması daha uygun olacaktır.

İkamet izni için hangi belgeleri hazırlamalıyım?

Kaynak 2'de, "Ön kayıt koşulları şunlardır: Türkçe yeterliliklerine ilişkin belge talebinde bulunulmayacak olan öğrencilere uluslararası öğrenim ücretini ödemeleri, Türkçe yeterliliklerine ilişkin belge talebinde bulunulacak öğrencilere ise uluslararası öğrenim ücreti ve OMÜ TÜRKÇE ücretini ödemeleri" deniliyor. Ancak, ikamet izni için gerekli belgilerin neler olduğu konusunda net bir bilgi yok.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı. İlgili sorunun sorulduğunun Üniversite'sinin Uluslararası İlişkiler Ofisi'ne yollanması daha uygun olacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RA
... (216 karakter daha)
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs', 'student_affairs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] not ortalaması
  - [x] harç
  - [ ] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 8927.3 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
ÇAP Programına başvurmak istediğinizden ve harç borununuz olduğundan bahsettiniz. Başvuru koşulları ile ilgili bilgiler aşağıda sunulmuştur:

### Başvuru Koşunları
- Ön lisans veya lisans diploması sahibi olmak
- Başvuru zamanı senato tarafından duyurulmuş olan ÇAP'a, dört yıllık programlarda ana dal diploma programının en erken üçüncü yarı yılının başında, en geç ise beşinci yarı yılın başında başvurmak
- Başvuru koşulları için, başvurduğunuz yarı yıla kadar ana dal lisans programında yer alan tüm dersleri almış ve başarmış olmak, başvurunuzun sırasındaki ana dal not ortalaması 4,00 üzerinden en az 3,00 oluşturmak ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk % 20'sinde bulunmak

### Harç Borçunuz
OİDB ile temas kurarak harç borcunuzu öğrenip ödeyebilirsiniz. Başvuru koşullarıyla ilgili detaylı bilgi için kaynak belgelerden yararlanabilir veya akademik danışmanınıza danışabilirsiniz.

### Dikkat Edilmesi Gerekenler
- Harç borcu olamayacak şekilde öğrenci işleri birimine danışmanız yerinde olabilir
- Başvuru koşullarıyla ilgili detaylı bilgi için kaynak belgelerden yararlanabilirsiniz
- Akademik danışmanınıza danışabilirsiniz

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4132.1 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Kayıt yenileme döneminde harç ücretinizi yatırdıktan sonra ders kaydını yapmanıza yardımcı olacak adımlar:

1. Veritabanını Güncelle:
26.08.2026 - 06.09.2026 tarihleri arasında 2026-Güz dönemi planlanmakta olduğu için veritabanını bu tarih aralığından sonra güncellemeniz gerekir.

2. Ödemelerin Doğru Olması:
Öğrenim ücretinizin doğru olduğunu kontrol ediniz. Turu, birime, Türk veya uluslararası öğrenci olup, fakülte veya bölümünüzü belirten Finans Departmanı size bilgi verecektir.

3. Ders Kaydı Onayı:
Danışmanınızın ders kaydınızı onaylaması gerekir. Aday olduğunuz dersleri ve danışmanınızın onayını aldıktan sonra, kayıt işleminiz tamamlanacaktır.

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
- **Departman**: ['finance', 'student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [ ] bildiri
  - [x] harç
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 8806.6 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Burslu öğrenci olarak yatay geçiş yapmak istediğinizde bursunuzun kesilip kesilmeyeceği hususunda net bilgi bulunamadı. Ancak, OMU Vakfı bursu için 1 dersten fazla dersten başarısız olduğunuz takdirde bursunuzun kesileceği belirtilmiştir. Ayrıca, Kredi Yurtlar Kurumu ve diğer kurum/kuruluşlar tarafından verilen burslar hakkında bilgiye ilgili kurumlardan erişmeniz gerekmekte.

Yatay geçişle yeni bir programa geçiş yaptığınızda bursunuzun kesilme durumu ile ilgili olarak, aşağıdaki adımları takip edebilirsiniz:
- Öncelikle, yeni üniversiteye geçiş yaptığınızı ve burşunuzun kesilip kesilmeyeceğini öğrenmek için OMU Vakfı'yla iletişim kurun.
- Yeni üniversitede kaydolduktan sonra, OMU Vakfı'yla gerekli başvuruları yapın.
- Bursınızın kesilip kesilmeyeceği konusunda net bilgi alana kadar bekleyin.
Yeni üniversitede harç ödeme hususu ise, yatay geçişle yeni bir programa geçtiğiniz takdirde harç ödemek zorunda kalırsınız.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [ ] azami
  - [x] ek
  - [x] süre
  - [ ] katkı payı
  - [x] öde
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 6663.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Akademik Programlar:
Özelliginiza gore ek süre hakkınız var mi sorusu cevabini vermeye calisirim. 

Sen ÖYP'nin bir öğrencisisin, dolayısıyla ek süre hakkınızı ÖYP'siz bir öğrenci gibi değil, ÖYP'li bir öğrenci olarak değerlendirmeliyiz. Belge baglaminda yer alan kaynaklardan gördügümüzüze göre, ÖYP'lere 4 yarıyıl öğrenim süresi tanınmıştır. Bu nedenle, ek süre hakkınız olduğunu söyleyebiliriz. 

Yaptığınız öğrenim süresini 1 yıl aştığınız halde, ek süre hakkınız olduğunu gördüğümüzde, ek süre için ÖYP'li bir öğrenci olarak ne olduğunu merak ediyorum. Ek süre için mecburi hizmet sözleşmesi uygulamasına tabi olacağınıza göre bir çok soruya cevabım bulunamadı. 
Bu konuya dair detaylara erişim sağlayamadım, ek sure için ödemeler hakkında net bilgi edemedim.

Belge baglaminda yer alan maddeler gereği öğrencilerde değişim için 12 aya kadar süre tanınabilir; ancak bu süre öğrencinin normal eğitim süresinden sayılır. Dolayısıyla, normal eğitim sürenizin 1 yıl aştığını düşünürsek, öğrenci olarak ek süre için nasıl bir durumda olacağınıza dair daha detaylı bilgiye ulaşamadım.

Finans:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: öğretim_üyesi_yetiştirme_programı_yönergesi.pdf
- Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf
- Belge: tıp_fakültesi_tıp_doktorluğu_programı.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönerg
... (7 karakter daha)
```

### Q10: Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [ ] tekrar
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 4200.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

Akademik Programlar:
Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim?

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: Kural

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 2493.6 ms
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
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] transkript
  - [x] Ek Madde
  - [ ] başvuru yapabilir
  - [ ] GANO
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 8078.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Hazırlık sınıfındaydınız ancak transkriptinizin bulunmaması nedeniyle endişeleniyorsunuzdur. Öncelikle Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapma imkanınızı değerlendiriyoruz. 

Ek Madde-1 ile yatay geçiş, üniversite tarafından belirlenen kurallara ve koşullara göre yapabileceğiniz bir süreçtir. Önlisans diploma programlarının 1. yılında yatay geçiş yapımılmaz.

Hazırlık sınıfını tamamladıktan sonra Ek Madde-1 ile yatay geçiş başvurunuzu yapabilirsiniz. Tercih başvurunuzu yapacak olduğunuz akademik birim size gerekli başvuru süreçlerini açıklamış olacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf
- Belge: uluslararası_öğrenci.pdf
```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/5
  - [ ] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Sure**: 5356.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Yapılan açıklamalar ve verilen belgeler değerlendirildiğinde, Öndokuz Mayis Üniversitesi (OMU) içinde yurt içinde ve yurt dışından yapılan yatay geçişler arasında bazı farklar olduğu göze çıkmaktadır. İşte bu farklar:

- Yurt içi yatay geçiş: Yurt içi yatay geçişler, diğer yükseköğretim kurumlarındaki aynı düzeydeki eşdeğer diploma programlarından öğrencilerin OMU ye yapılan başvurulardır. Başvuru ve değerlendirme kriterleri için [Kaynak 2: yonerge_onlisans_lisans_yatay_gecis.pdf] referans alınabilir.
 - _Kurumlar arası yatay geçiş: _Yurt dışından OMU ye yatay geçiş başvurusu yapan öğrencilerin başvuruları için [Kaynak 1: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf] ve [Kaynak 2: yonerge_onlisans_lisans_yatay_gecis.pdf] kaynaklarına bakılması gerekir.
 
- Yurt içi yatay geçiş başvuruları: Yurt içi yatay geçiş başvuruları, yurt içi yükseköğretim kurumlarındaki aynı düzeydeki eşdeğer diploma programlarından yapılır. Başvuru şartları ve değerlendirme kriterleri için yurt içi yatay geçiş için [Kaynak 2: yonerge_onlisans_lisans_yatay_gecis.pdf] kaynakları referans alınabilir.
- Yurt dışı yatay geçiş başvuruları: Yurt dışı yatay geçiş başvuruları, yurt dışı yükseköğretim kurumlarındaki aynı düzeydeki eşdeğer diploma programlarından yapılır ([Kaynak 1: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf] , 8. madde). Başvuru şartları ve değerlendirme kriterleri için yurt dışı yatay geçiş için [Kaynak 1: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf], 8. madde ve [Kaynak 2: yonerge_onlisans_lisans_yatay_gecis.pdf] kaynakları referans alınabilir.
 
- Yurt içi yatay geçiş kontenjanları: Yurt içi yatay geçiş kontenjanları, Yükseköğretim Kurulu ve OMU nin internet sitelerinde ilan edilir ([Kaynak 2: yonerge_onlisans_lisans_yatay_gecis.pdf] , 3. madde).
- Yurt dışı yatay geçiş kontenjanları: Yurt dışı yatay geçiş kontenjanları, Senato tarafından belirlenir. Kontenjanlar, her bir program için kurumlar arası yatay geçiş kontenjanının yarısını aşmayacak şekilde olur ([Kaynak 1: ön_lisa
... (433 karakter daha)
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 7072.2 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Ogrenci Isleri:
Bağıl değerlendirme sistemi ile mutlak değerlendirmede arasındaki fark, öğrencilerin ders performansının değerlendirilme yaklaşımında yatmaktadır.

BaĞIL DEĞERİLEME SİSTEMİ:
- Öğrenci sayısının 10 ve altında olması durumunda, öğrencilerin ham başarı puanları mutlak değerlendirme sistemi olarak Tablo-1'e göre nota dönüştürülür.
- Öğrenci sayısının 11-29 arasında olması durumunda, öğrencilerin ham başarı puanları ders ortalaması dikkate alınarak Tablo-2'ye göre nota dönüştürülür.

MUTLAK DEĞERİLEME SİSTEMİ:
- Mutlak değerlendirme sistemi, öğrencilerin ham başarı puanlarının Tablo-1'e göre nota dönüştürülmesi ile gerçekleştirilir. Bu sistemde, öğrencilerin ham başarı puanları AA, BA, BB, CC, DC, DD, FD, FF harfleri arasında sınıflandırılır.
- Mutlak değerlendirme sisteminde, her bir harfli notun için belirlenen yüzde oranlarına göre, öğrencilere not verilir.

Ayrıca, kaynaklar belirlenen öğrenci sayısından bağımsız olarak öğrenci sayısının 30'a ve üzerinde olması durumunda, mutlak değerlendirme sisteminin uygulanacağı görülmektedir.

Bu konuda elimdeki kaynaklarda net bilgi bulunmadaki.

Akademik Programlar:
Soruya karşılık olarak cevap vermeyeceğim, ancak bilgiyi aktarmak için gerekenleri görecek ve net bir cevap vereceğim.

Ondokuz Mayıs Üniversitesi (OMU) bağlamında mutlak değerlendirme sistemi ile bağıl değerlendirme sistemi arasındaki fark, lisansüstü eğitim ve öğretim yönetmeliğinde belirtildiği gibi.

Mutlak değerlendirme sistemi, yarıyıl içi (veya yıl içi) değerlendirme ile yarıyıl sonu (veya yıl sonu) sınav notlarının öngörülen ağırlıklara göre hesaba katılmasıyla belirlenen ham başarı notunun 4'lü not sistemindeki karşılığını ifade eder. Bu sistemin temel özellikleri şunlardır:

- Yarıyıl içi (veya yıl içi) değerlendirme ile yarıyıl sonu (veya yıl sonu) sınav notlarının öngörülen ağırlıklara göre hesaba katılması,
- Ham başarı notunun 4'lü not sistemindeki karşılığını ifade eder,
- Bir dersten başarılı sayılabilme notu 60'dır.

Ayrıca, OMU'nda
... (1135 karakter daha)
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
- **Sure**: 6460.0 ms
- **Kaynak Sayisi**: 10
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Ogrenci Isleri:
Diploma eki ile transkript arasındaki fark:
Diploma eki, öğrencinin diploma alma durumunu gösterirken, transkript (not çizelgesi), öğrencinin aldıkları ders notlarını ve durumunu gösterir. Diploma eki transkript yerine kullanılamaz, ikisine de farklı amaçlar için talep edilir.

Diploma eki transkript yerine kullanılabilir mi?
Hayır, diploma eki transkript yerine kullanılamaz.

Akademik Programlar:
Diploma eki ile transkript arasındaki fark nedir?

Diploma eki ve transkript iki farklı dokümanentir. Diploma eki, bir öğrencinin belirli konularda derecesini veya becerisini gösteren bir belgedir, ancak diploma yerine geçmez. Transkript ise, bir öğrencinin aldığını ders ve notların tam listesidir ve genellikle mezun olduktan sonra verilen bir belgedir.

Diploma eki transkript yerine kullanılabilir mi?

Hayır, diploma eki transkript yerine kullanılamaz. Diploma eki, diplomanın eşdeğer bir belgedir ve diploma yerine geçmezken, transkript bir öğrencinin ders ve notlarının tam listesidir. Diplomaya göre transkript daha detaylı bir dokümentir ve bir öğrencinin akademik geçmişini gösterir.

Belgelerde transkript ve diploma eki arasında farklar gösteren tanımlar:

* [Kaynak 2] maddesinde, "yandal sertifikası" olarak tanımlanmakla birlikte, diploma eki bir öğrencinin bir programa kayıt olduğu durumlar, bu öğrencinin aldıkları sınırlı sayıda dersler, konuya yönelik, belirli bir programa göre düzenlenmektedir. 
* [Kaynak 1] maddesinde, diploma programı ve yatay geçiş kontenjanları ile ilgilenmekteyken, transkript hakkında direkt olarak bilgi vermemektedir.

Bu nedenle, diploması ile transkript arasındaki farkın belirlenmesi için bu belgelere bakmak gerekebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge
... (252 karakter daha)
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4702.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Kayıt dondurma ile kayıt yaptırmamak arasında önemli farklar vardır. Kayıt dondurma, belirli mazeretler nedeniyle öğrencinin öğrenimine ara verilmesini sağlar. Bu durum öğrenciyi, dondurulan dönem/dönemler için sınavlara girmekten ve öğrenimine kaldığı yerden devam etmesine engel olmakla birlikte, öğrenim süresi boyunca öğrencinin haklı ve geçerli mazeretleri nedeniyle öğrenimine ara verebilme hakkı sağlar.

Ayrıca, kaydetme ve dondurma arasındaki diğer fark, öğrencinin öğrenimlerine katkıda bulunacak Üniversite dışı burs, staj, araştırma ve benzeri imkânların ortaya çıkması gibi durumlarda kayıt dondurmaya başvurmasıdır.

Kayıt dondurma ile kayıt yaptırmamak arasındaki etkileri de incelemek gerekir. Kayıt donduran bir öğrencinin hakları, kaydını yaptırmamış bir öğrencinin haklarından farklı olabilir. Kayıt donduran öğrenci, kayıt dondurduğu dönem/dönemler için öğrenimine devam edemez ve söz konusu döneme/yıla ait sınavlara giremez. Bu öğrenci, kaydını yaptırmamış bir öğrenciyle aynı haklara sahip değildir. Kaydı yaptırmamış bir öğrenci, öğrenimine devam edebilir ve sınavlara girebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [ ] UBYS
  - [x] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3925.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Uygulamada sürecin başından sonuna kadar tüm adımları anlatayım:

- Kayıt işlemlerine başlamak:
Bir öğrenci ilk kez kayıt yapmak istiyorsa, kayıt işlemlerine başlamadan önce öğrenci numarası ve T.C. kimlik numarası ile sisteme giriş yapmalıdır. Eğer öğrenci bu bilgileri bilmiyorsa, öğrenci hizmetleri bölümüne başvurmalıdır.

- Ders seçme:
Student sistemimize giriş yaptıktan sonra, öğrenci seçmek istedikleri dersleri seçmelidir. Ders seçimi yapan öğrenci, seçtikleri derslerin durumunu kontrol edebilir.

- Onay:
Seçilen dersler öğrenci tarafından onaylandıktan sonra, danışmanın onayına gönderilir. Danışman, onaylı derslere ilişkin bilgileri kontrol eder ve varsa hataları düzeltmek için gerekli adımları atar.

- Dönem değişikliği:
Ekle-sil haftasında, öğrenci seçtiği dersleri kontrol edebilir. Eğer bir sorun varsa, öğrenci hizmetleri bölümü ile temasa geçebilir.

- Ders.muafiyet başvurumu yapmaktayım:
Öğrenciler, muafiyet taleplerini ilgili dekanlığa/müdürlüğe sunmaları gerekir. Bu, öğrencinin daha önceki yükseköğretim kurumundan alınan ders içerikleri ve onaylı not döküm belgesiyle gerçekleştirilir. Bu başvuruların süresi derslerin başlamasından ikici hafta sonuna kadardır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

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
- **Sure**: 2180.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Yazıma başlamadan önce, belirtilmiş olan kuralları hatırlatmak isterim.

Sınav notuma itiraz etmek istediğinizde, takip edeceğiniz başvuru süreci şöyledir:

1. Başvuru Süresi: Yüzde on hesaplamaları ilan edildikten sonra 15 gün süreyle fakülte/yüksekokuluna yazılı olarak başvurabilirsiniz.
2. Başvuru İşlemi:
 * İtirazınızı fakülte/yüksekokuluna 15 gün içinde yazılı olarak iletin.
 * Yapılan başvurular 15 gün içerisinde birim yönetim kurulunca karara bağlanır.
3. İtiraz Süresi Bittiği Tarihten Sonra:
 * İtiraz süresi bittikten sonra bildiren not ve not düzeltmeleri dikkate alınmaz.

Yapılacak başvuruların sonucunda management kurulu karar kesindir. Elbette bu süreç hakkında daha detaylı bilgi için fakülte/yüksekokulunuza danışmanız ve başvurunuzu ilgili birimlere iletmeniz önemlidir.

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
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 5/6
  - [x] ders
  - [x] staj
  - [ ] GANO
  - [x] 2,00
  - [x] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 7731.8 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Mezuniyet Koşulları ve İlişik Kesme Süreci

Mezuniyet için gerekli koşullarını ve ilişik kesme sürecini adım adım açıklamak için, aşağıdaki bilgilerin dikkate alınması gereklidir.

Mezuniyet Koşulları:

1. Kayıtlı olduğunuz programın tüm ders, uygulama ve staj gereklerini başarıyla tamamlamış olmanız ve genel not ortalamanızın (GNO) 2,00 veya daha yüksek olması gerekir.
2. Programınızın tüm şartlarını yerine getiren öğrenciler için mezuniyet hakkı kazanılır.
3. Farklı diploma türleri şunlardır:
 * Önlisans Diploması: Dört yarıyıl süreli meslek yüksekokullarından mezun olanlar için.
 * Lisans Diploması: Hazırlık hariç, dört yıl süreli fakülte ve yüksekokul lisans programlarından mezun olan öğrenciler için.
 * Çift Ana Dal Lisans Diploması: Ana daldaki mezuniyetlerine bağlı olarak ikinci ana dal lisans programını tamamlayan öğrenciler için.
 * Yandal Sertifikası: Ana daldaki mezuniyetlerine bağlı olarak yandal lisans programlarını tamamlayan öğrenciler için.
 * Tezli Yüksek Lisans Diploması: Enstitülerdeki tezli yüksek lisans programlarını tamamlayanlara.
 * Tezsiz Yüksek Lisans Diploması: Enstitülerdeki tezsiz yüksek lisans programlarını tamamlayanlara.

İlişkin Kesme Süreci:

1. İlişkin kesme formu, üniversite personelinin ilişiği kesilmeden önce, birim amiri tarafından zimmetinde taşınır (demirbaş) olup olmadığını kontrol etmeniz gerekir.
2. Form-1 belgesi, personelin zimmetinde taşınır (demirbaş) olmadığı kontrol edildikten sonra, düzenlenen belge ile ilişiğinizin kesilmesi gerekir.
3. Form-2 belgesi, personelin ilişiği kesilmeden önce, ilçe belediyeye müracaat ederek, belge almanız gerekir.

Sonuç:
Mezuniyet koşulları ve ilişik kesme süresini adil ve düzenli bir şekilde tamamlayırsanız, başarıyla mezun olmanın koşullarını yerine getirebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LL
... (385 karakter daha)
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 6023.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
İlk olarak diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Bu iki sorunu için ne yapmalıyım?

Gerek diplomamı alma probleminin, gerekse de e-devlette mezuniyet bilgilerimin Görünmemesinin çözümü için, uygulama esaslarında bulunan ilgili maddeye bakmak en uygun yöntem olacaktır.

Diploma alımlarına yönelik madde MADDE 17'dir. Bu maddeden, diplomanızı kaybederseniz ilk diplomada yer alan bilgileri içeren yeni bir diploma düzenlenir ve üzerinde İkinci Nüsha bilgisi yer alır. Dolayısıyla diplomanızı alma işlemine geçmek için;

- Kayıp ilanınızı yaygın bir gazetedeki kayıp ilanlar bölümüne duyurman gerekli,
- Dilekçe sunmanız,
- Onaylı nüfus cüzdanını sunmanız,
- Diploma ücretini yatırdığınızı gösteren banka dekontunu sunmanız,
- Diploma aldığınız birime müracaat edilmesi ve ilgili birim müdürü/dekanı/veya Rektör tarafından imza atılması gerekli,

Bu maddede belirtildiği şekilde hareket etmeniz durumunda, ilk diplomada yer alan bilgileri içeren yeni bir diploma alınacaktır.

Ayrıca diplomanız için, diploma tescil işlemleriyle  alakalı MADDE 8'den bahsetmemiz de gerekecektir. Bu maddeye göre, diplomatızın arka yüzünde yer alan bilgilerin eksiksiz olması gerekmektedir. 

Sonuç olarak diplomanızı alma işlemine geçmek için, ilk diplomanızdaki bilgiye dayalı olarak yeni bir diploma düzenlemek için MADDE 17'ye, diplomada yer alan bilgilerin eksiksiz olması için MADDE 8'e bakınız.

Ayrıca e-devlette mezuniyet bilgilerin görülmemesini de çözmek için, diploma tescil işlemleriyle ilgili MADDE 8 ile birlikte bakmamız yeterli olacaktır. 

Diğer bilgilerin, diploma ücreti için banker dekontu veya diploma aldığınız kurumda gerekli başvurular için MADDE 17 ve diploma tescil işlemleri için MADDE 8'den elde edeceğimiz bilgilerle yeterli olacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kayna
... (66 karakter daha)
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4503.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

Belge kaynaklarımızda, uzaktan eğitim yoluyla alınan derslerin sınav ve başarı değerlendirmesi ile yüz yüze derslerin farklılık göstermediği bir hüküm bulunmamaktadır. Belirlenen esaslara göre, uzaktan veya örgün eğitim yoluyla verilen derslere ait devam ve başarı durumu, Ondokuz Mayıs Üniversitesi eğitim-öğretim yönetmelikleri hükümlerince belirlenir. Bu nedenle, uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı değildir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4701.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınavda kopya çekilmesinin cezası:
Belge baglaminda sınav görevlisi, öğrencilerin yerlerini değiştirebilir veya sınav kurallarına aykırı davranışlarda bulunanları salondan çıkartabilir (Kaynak 1: 6.). Bu gibi durumlarda sınav görevlisi veya ilgili öğretim elemanı, uyarıda bulunmaksızın bu öğrenciler hakkında işlem yapabilirler (Kaynak 2: 12.).

Bu durumda, öğrencinin disiplin suçu işlemiş olduğudur. Disiplin suçu işlemiş öğrencilerin cezaları, disiplin kuruluna bırakılacaktır. Disiplin kurulu, bu tür durumları inceler ve ilgili öğrencinin cezaını belirler.

Disiplin süreci:
Sınavda kopya çekilmesinin cezası, disiplin suçu işlemiş öğrenciye verilecek cezayı etkiler. Disiplin suçu işlemiş öğrenciler, disiplin kuruluna gönderilir ve bu kurul, öğrencilerin cezalarını belirler.

Bu süreç, Yüksek Öğretim Kanununun 54. Maddesine göre yürütülür (Kaynak 3: On Dokuz Mayıs Üniversitesi Mühendislik Fakültesi Sınavlarda Uyumlanması Gereken Kurallar Disiplin Suçlarına İlişkin Hükümler). Disiplin kurulu, öğrencilerin durumunu inceler ve onlara uygun cezayı verir.

Disiplin süreci, öğrencinin suçu işlemiş olduğu durumda başlar ve öğrenciler, disiplin kurulu tarafından cezalandırılır.

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
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [x] form
  - [x] birim
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 6038.2 ms
- **Kaynak Sayisi**: 5
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Sizden istifa ederek üniversiteyi bırakmak istiyorsunuz. Bu durumda, Ondokuz Mayıs Üniversitesi (OMÜ) öğrencisi olarak aşağıdaki adımları takip etmelisiniz:

1. Öğrenci İşleri Birimi'ne başvurmanız: Üniversite öğrencisi işleri bakanınızla (öğrenci işleri birimi) görüştüğünüz sırada istifa istemisiniz. İsteğinizi ve nedenlerinizi açıkladıktan sonra, işlemlerin başlatılması gerekir.

2. İstifa Bildirimi: Öyle bir form veya belge olabilir mi? Evet, istifa bildirimi için genellikle "öğrenci istifa bildirimi formu" doldurulur. Bu form sizin istifa sebebini, öğrenci kimlik numaranızı ve istifa etmek istediğiniz tarihi içerir. Bu formun nerede ve nasıl bulunduğunu bilmen gerekir ama benim elimde bu konuyla ilgili bilgi yok.

3. Not İsimlendirmeleri: İstifa etmeden önce notlarınizi izinsiz alabilme imkanınız yoktur. Notlarınız için istifaya bağlı kalınmalıdır. Herhangi bir sebepten dolayı akademik notlarınız için istifayı durdurmazsanız.

4. Kredi ve Not Transferi: Eğer üniversite değişim süreci içindeyiz ve başka bir üniversiteye istifaya gitmektense kredi ve not transferi sürecini tamamlamak istiyorsanız, bu sürecin başlangıcından itibaren 1-2 ay içinde gerçekleştirilmesi gerekir. Aksi halde bu istisna geçerliliğini yitirecektir.

5. Ödevleri ve Çalışmaları Tamamlama: Öğrenci işlerini tamamlamak için, çalışmanız ve ödevler için zamanınızı ayırmanız gerekecektir. Bu, sizin öğrencilik hayatınızın son aşamalarını olumlu bir sonuca ulaşmanızı sağlayacaktır.

6. Borcunuz: Oluşan borcların ödemesi ve bu konuda işlemin tamamlanması gerekir. Aksi halde bu durum sizin istifanıza engel oluşturacaktır.

Bu adımları takip ettiğinizden emin olun. İleri adımlarınız için, bu noktadan başlayarak süreçlerin nasıl ilerlediğini belirlemelisiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakül
... (220 karakter daha)
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] kayıt
  - [x] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 5483.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Dönüşte ders seçimini yaparken dikkat etmeniz gereken bazı hususlar vardır. İlk olarak, kayıt dondurma süresinin bitiminde, öğrenci ayrıldığı dönemin/yılın başından başlamak koşuluyla öğrenimine kaldığı yerden devam eder. Bu durumda, ders seçiminde öğrenci, kaydını yaptıktan sonra derslerini seçebilir.

Kayıt dondurma süresinden sonra, öğrenci en fazla dört dönem/iki yıl kaydı dondurabilir. Bu şekilde kayıt donduran öğrenci, öğrenimine devam edemez ve kayıt dondurduğu dönem/yıla ait sınavlara giremez.

Daha sonra, sık sorulan sorular dosyamızda bulunan bilgilerden de yararlanılarak, dersleri seçmenin bir yolu daha ortaya koyulmuştur. Bu göre, üst sınıftan ders alma koşulları, genel not ortalamasının üst sınıftan ders alma için gerekliliği olan kriterler doğrultusunda belirlenmelidir.

Dönüşte ders seçimini yaparken, aşağıdaki adımları izleyebilirsiniz:

1. Kayıt dondurma süresini tamamladıktan sonra, kaydını yenileyin.
2. Kayıt dondurma süresinin bitiminde öğrenimine kaldığı yerden devam etmesini sağlayın.
3. Genel not ortalaması hesabını yaptıktan sonra, üst sınıftan ders alma koşullarını değerlendirin.
4. Üst sınıftan ders alma koşullarını sağlayan dersleri seçin.

Dikkat edilmesi gereken, kayıt dondurma süresini tamamladıktan sonra, öğrencinin kaydını yenilemek ve öğrenimine kaldığı yerden devam etmesini sağlamak zorunda olduğudur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Sure**: 1271.7 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

Uretim Turu:
- Kural
```
