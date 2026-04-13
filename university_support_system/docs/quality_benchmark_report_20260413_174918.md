# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-13 17:49:18
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 92.0% |
| Uretim Modu Dogrulugu | 92.0% |
| Anahtar Bilgi Kapsami | 64.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 7843.5 ms |
| Medyan Sure | 6523.3 ms |
| Intent Analizi Aktif | 23/25 |
| Force LLM Sentez | 22/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 48469.5 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 3/3 | 7117.3 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | OK | 3/4 | 3182.0 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 4/4 | 6137.2 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 9656.5 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 8240.1 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 6523.3 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 8101.1 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | OK | 4/5 | 6048.6 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 6646.3 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 3/4 | 7409.0 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 3/4 | 7438.8 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 1/5 | 7730.9 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 3/4 | 4830.2 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 2/3 | 6461.1 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 5062.4 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 2/5 | 4552.2 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 2/4 | 3323.9 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | YANLIS (kural) | 1/6 | 3026.5 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 4651.6 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 3/5 | 8436.5 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 7290.1 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 2/4 | 4501.7 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 7393.3 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 1/3 | 3857.1 | - |

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
- **Sure**: 48469.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu derslerin başlamasından itibaren ikinci haftanın sonuna kadar veya kayıt yaptırdığı öğretim yılının en geç üçüncü haftasının sonuna kadar yapmalıdır. Muafiyet talebi karara bağlanıncaya kadar öğrenciler, muafiyet talebinde bulunduğu derslere devam etmek zorundadırlar. Özetle:
- Derslerin başlamasından sonra belirlenen sürede muafiyet başvurusu yapılır.
- Karar çıkana kadar derslere devam edilmelidir.
- Öğrenci, daha önce aldığı ve başarılı olduğu derslerden muaf olmak için başvuru yapmalıdır.

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
- **Key Facts**: 3/3
  - [x] staj
  - [x] tamamla
  - [x] CC
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 7117.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Tek ders sınavına girebilmek için stajınızı tamamlamış olmanız gerekmez. Sınavda başarılı sayılmak için minimum not, 100 puan üzerinden en az CC almaktadır. 
- Tek ders sınavına girmek için stajı tamamlamak zorunlu değildir.
- Başarılı sayılmak için en az CC notu alınmalıdır, bu da 100 puan üzerinden belirli bir puan eşdeğeridir.
- Bir dersten başarılı sayılmak için yarıyıl veya yıl sonu sınav notunun en az 60 olması gerekir ki bu da en az CC notuna karşılık gelir.

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
- **Key Facts**: 3/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [x] yeni
  - [x] ders
- **Sure**: 3182.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli seçerseniz devam zorunluluğunuz değişmez. [Kaynak 2: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf], Madde 6'da bahsedildiği üzere, "Devam koşulunu yerine getirmiş ancak sınavlarda başarısız olan öğrenciler eğitim öğretim yılı başından itibaren en geç 7 gün içinde devamdan muafiyet dilekçeleri ile başvurdukları takdirde yönetim kurulu kararı ile dersin devamından muaf tutulabilirler." Ancak seçmeli bir ders yerine başka bir seçmeli ders alınması durumunda, devam zorunluluğu için herhangi bir değişiklik öngörülmemiştir. [Kaynak 2: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf], Madde 20'de devam zorunluluğu %70 ve %80 olarak belirlenmiştir. Başarısız olunan seçmeli dersin yeniden açılmaması halinde, öğrencinin isteği ve danışmanın önerisi doğrultusunda yönetim kurulu kararı ile başka bir seçmeli ders alınabilir. [Kaynak 2: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf], Madde 20, fıkra 6.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 6137.2 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Pedagojik formasyon dersleri transkripte dahil ediliyor. Mezuniyet ortalamasına etkisi var. Diplomaların arkasına "Pedagojik formasyon eğitimini tamamlamıştır" ifadesi yazılacaktır. 
Aşağıdaki bilgiler dikkate alınabilir:
- Dersler transkript içinde yer alacaktır.
- Sadece bir transkript düzenlenecek ve bu dersler bu transkript içinde yer alacaktır.
- Mezuniyet ortalamasına dahil edilecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 9656.5 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Öğrenim ücreti ödenmesi gereken yeri belirtmeyen kaynaklar nedeniyle net bilgi bulunamadı. Ancak, öğrenim ücreti ve ödeme detayları için finans birimi ile iletişime geçmeniz önerilir. İkamet izni için Göç İdaresi Başkanlığı'na başvuruda bulunacağınızı, ikamet izni belgesini teslim edeceğinizi ve öğrenci ikamet izni için gereken belgeleri ve sürelere uymakla yükümlü olduğunuzu belirtebiliriz. İlgili yetkili merciler ile iletişime geçmenizi öneririz.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 8240.1 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
ÇAP programına başvurmak için, dört yıllık programlarda ana dal diploma programının en erken üçüncü yarı yılının başında, en geç ise beşinci yarı yılın başında başvurabilirsiniz. Başvurunuz sırasında ana dal lisans programında yer alan tüm dersleri almış ve başarmış olmanız, ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk %20'sinde bulunmanız gerekir. Harç borcunuzu ödemek için, ödemenin yapılacağı birim veya ödeme türü konusundaElimizdeki kaynaklarda net bilgi bulunamadı. Ödemenin nasıl yapılacağı konusunda daha fazla bilgi almak için, size en uygun ödemesini sorgulayabilmeniz için ogrenci turune ve birime gore degisiklik gosterebilecegini dusunerek Turk ogrenci misiniz, uluslararasi ogrenci misiniz, mumkunse fakulte veya bolum bilginizi paylaşmaniz gerekebilir.

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 6523.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, öğrenci bilgi sistemi üzerinden ders kaydı yapılır. Ders kaydı, danışman onayıyla kesinleşir. Öğrenci, akademik takvimde belirlenen süre içinde ders kaydını yapmak zorundadır. Danışman onayı, derslerin doğruluğunun kontrol edilmesi gerekir. Danışman onayı işleminin ardından, ders kayıtlarının güncellenip güncellenmediğinin takip edilmesi önemlidir. Eğer danışmanına ulaşılamıyorsa, bölüm başkanına veya Dekan/Müdürüne başvurulması gerekir. Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine e-posta yoluyla iletişim kurulabilir. Kayıt yaptıracakları derslerin AKTS kredilerinin toplamının belirlenmiş olan AKTS kredileri ile bunların yarısının toplamından fazla olmamasına dikkat edilmelidir. 
- Kayıt dönemi başlamadan transkript/müfredat kontrolü yapılmalıdır.
- Bir seçmeli dersin açılabilmesi için derse kayıtlı öğrenci sayısının ulusal kredi hesabında uygulaması teoriden yüksek olan dersler için en az on kişi, diğer seçmeli dersler için ise en az on beş kişi olması gerekir.
- Ders kaydı, akademik takvimde belirtilen süre içinde tamamlanmalıdır.

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
- **Departman**: ['finance', 'student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [ ] bildiri
  - [x] harç
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=conditional
- **Sure**: 8101.1 ms
- **Kaynak Sayisi**: 13

**Yanit:**
```
Yatay geçiş yaptığınızda, bursunuz kesilir ve yeni üniversitede harç ödemeniz gerekir. Bursunuzun devri veya kesilip kesilmeyeceği konusunda net bilgi almak için burs aldığınız kurumla iletişim kurmanız recommand edilir. 
- Burs aldığınız kurumla iletişime geçip bursunuzun durumunu öğrenin.
- Yatay geçiş başvurunuzun kabul edilmesi durumunda, yeni üniversitenin belirlediği harçları ödeyeceğinizi bilin.
- Herhangi bir net bilgiye ulaşamamanız durumunda, İdari ve Mali İşlere başvurabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: RAG + LLM
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
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
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 6048.6 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Program süresini 1 yıl aşmış bir 4. sınıf öğrencisi olarak katkı payı ödemeniz gerekiyor. Öğrenciler her öğretim yılında belirlenen miktarlarda katkı payını/öğrenim ücretini akademik takvimde belirlenen sürede ödemekle yükümlüdürler. Öğrencinin katkı payını/öğrenim ücretini ödemediği yarıyıl/yıllar, öğrenim süresinden sayılır. Ek süre hakkıyla ilgili net bilgi bulunmamaktadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: tıp_fakültesi_tıp_doktorluğu_programı.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: yonerge_cift_anadal_yandal.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 6646.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Hayır, devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Devamsızlıktan kalmış olduğunuz dersi, bir sonraki dönemde tekrar alabilirsiniz. 
Bu durum için iki önemli nokta dikkat çekiyor: 
- Devamsızlıktan kaldığınız bir dersin bütünleme sınavına girmeniz mümkün değildir.
- Dersi bir sonraki dönemde tekrar alma hakkınız bulunmaktadır.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 7409.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Kayıt dondurmak istediğinde, ilgili yönetim kurulunca kabul edilmesi durumunda öğrenim ücretini yatırmak zorunda değilsin. Kayıt dondurduğun süreler eğitim-öğretimden sayılmaz. 
- Öğrenim ücreti yatırmana gerek olmayacak.
- Kayıt dondurma ile kayıt yaptırmamak arasında fark bulunmakta.
- Eğitim-öğretim süresinden sayılmayacak süreler için rieng bir ücret ödemezsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: Kural

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
- **Key Facts**: 3/4
  - [x] transkript
  - [x] Ek Madde
  - [x] başvuru yapabilir
  - [ ] GANO
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **Sure**: 7438.8 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Hazırlık sınıfındasın ve transkriptin yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilirsin. 
- Ek Madde-1 kapsamında merkezi yerleştirme puanı ile yatay geçiş başvurusu yapmak isteyen adaylar, transkriptleri olmadan da başvuru yapabilirler.
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
- **Key Facts**: 1/5
  - [x] kurum içi
  - [ ] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 7730.9 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçiş ve kurumlararası yatay geçiş arasındaki farklar, başvuru şartları ve değerlendirme kriterleri açısından farklılıklar gösterir. Kurum içi yatay geçiş, aynı üniversite içinde farklı bir diploma programına geçişi ifade eder. Kurumlararası yatay geçiş ise, farklı üniversiteler arasında yatay geçişi ifade eder. 
- Her iki tür yatay geçiş başvurusunda da disiplin cezası almamış olmak ve kayıt dondurma durumunu belgelendirmek gereklidir.
- Kurum içi yatay geçiş başvurusu için genel not ortalamasının en az 2.80 olması gerekir.
- Kurumlararası yatay geçiş için ise, 4’lük sistem kullanan üniversiteler için genel not ortalamasının en az 2.80, 100’lük sistem kullanan üniversiteler için genel not ortalamasının en az 72 olması gerekmektedir. 
Ayrıca, her iki başvuru türü için de, başvuru yapacakları döneme kadar müfredatlarında yer alan bütün dersleri almış olmaları gerekmektedir.

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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4830.2 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Bu konuda elimdeki kaynaklarda net bilgi bulunamadi. Kaynaklar, Mutlak Değerlendirme sistemi hakkında bilgi vermektedir. Ancak, Bağıl Değerlendirme sistemi ile Mutlak Değerlendirme sistemi arasındaki fark ve bunların hangi öğrenci sayısında uygulanacağı konusunda net bilgi bulunmamaktadır.

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
- **Key Facts**: 2/3
  - [x] diploma eki
  - [x] transkript
  - [ ] yerine geçmez
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 6461.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Diploma eki ve transkript arasındaki fark, diploma ekinin elde edilmiş yeti ve becerilerin ifade edildiği, akademik ve mesleki tanınmasını sağlamaya yönelik bir belge olması, transkriptin ise öğrencinin öğrenimine devam ettiği veya mezun olduğu eğitim-öğretim programındaki bütün notlarını gösteren bir belge olmasıdır. Diploma eki transkript yerine kullanılamaz, çünkü diploma eki, diploma ve transkriptten farklı bir belge olup, ayrı bir amacı vardır. Diploma eki, kişinin takip edip başarıyla tamamladığı öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek üzere verilir. 

- Diploma eki, diploma ve transkriptten farklı bir belgedir. 
- Diploma eki, elde edilmiş yeti ve becerilerin ifade edildiği bir belgedir. 
- Diploma eki, personne takip edip başarıyla tamamladığı öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek üzere verilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf
- Belge: samsun_sağlık_yüksekokulu_eğitim_öğretim_ve_sınav_yönetmeliği.txt
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=comparative
- **Sure**: 5062.4 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Kayıt dondurma ile kayıt yaptırmamak arasındaki fark net olarak belirlenemese de, her iki durumda da öğrencinin eğitim sürecinin kesintiye uğradığı anlaşılabilir. Öğrencilerin belgelendirecekleri önemli mazeretlerinin veya eğitimlerine katkıda bulunacak Möglichkeitenin ortaya çıkması halinde, ilgili birimin yönetim kurulu kararı ile bir defada en fazla bir dönem kayıt dondurma imkanı olabilir. Ders kaydının kesinleştirilmesi ile ilgili süreci öğrenci takip etmelidir. Kayıt dondurma veya kayıt yaptırmama durumunun öğrencilik haklarına olan etkileri net olarak belum belirtilmiştir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: Kural
- Finans: Kural

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 4552.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatmak için:

- Öncelikle, akademik takvimde belirtilen süreler içerisinde ders kaydı yapılmalıdır. 
- Ders kaydında üç önemli hususa dikkat edilmelidir: müfredat durum kontrolü, akademik takvimde belirtilen süre içinde kaydın tamamlanması ve danışman onayı.
- Danışman, kayıt olmak istediğimiz derslerde değişiklik yapma hakkına sahiptir.
- Ders kaydını yaptırmak için danışman onayına ihtiyaç vardır. Danışmana ulaşılamadığı takdirde bölüm başkanına, bölüm başkanına da ulaşamazsanız Dekan/Müdürünüze durumu bildirmek sureti ile akademik takvimde belirtilen sürede danışman onayını muhakkak yaptırınız.
- Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz.

Ders kayıtları akademik takvimde belirtilen süreler içerisinde yapılmalıdır. Öğrenci İşleri Daire Başkanlığı WEB sayfasından akademik takvimlere ulaşılabilir.

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
- **Sure**: 3323.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınav notuna itiraz etmek isteyen öğrencilerin, sonuçların açıklanmasından itibaren 5 iş günü içerisinde ilgili bölüme yazılı olarak başvuruda bulunmaları gerekir. İtiraz süreci, ilgili öğretim elemanı tarafından en geç 3 iş günü içinde yapılmaktadır. Ayrıca, öğrenciler yeniden inceleme talebinde bulunabilir ve bu süreç en geç 3 iş günü içinde sonuçlandırılır. 

Yeniden inceleme ve itiraz süresi tentangında; 
- Sonuçların açıklanmasından itibaren 5 iş günü 
- Yeniden inceleme talebinde 3 iş günü
- İtiraz olması halinde 3 iş günü süreleri bulunmaktadır.

İtiraz sonucu, ilgili birimin yönetim kurulu kararıyla Öğrenci İşleri Daire Başkanlığına bildirilir. İtiraz süreci bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz. 

Not düzeltme talebi, öğretim elemanı tarafından notların ilanından itibaren en geç 60 gün içinde ilgili birime sunulur. İlgili birim yönetim kurulu, not değişiklik teklifini karara bağlar ve Öğrenci İşleri Daire Başkanlığına bildirir.

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
  - [x] staj
  - [ ] GANO
  - [ ] 2,00
  - [ ] ilişik kesme
  - [ ] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3026.5 ms
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
- Belge: işyeri_staj_sözleşmesi.pdf
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
- **Sure**: 4651.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Mezuniyet belgesi kaybı durumunda, Ogrenci Isleri Daire Baskanligina basinizi ve kimlik fotokopinizi ekleyerek kayip belgesi talebinde bulunabilirsiniz. E-devlette mezuniyet bilgilerinizin görünmemesi durumunda, Ogrenci Isleri Daire Baskanligina basvurup, sorunla ilgili bilgi alabilirsiniz.

Kaynaklarda spesifik bilgiler veya adim listeleri verilmemistir. Bu konuda elimdeki kaynaklarda net bilgi bulunamadi.

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
- **Key Facts**: 3/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [x] %40
  - [x] %60
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 8436.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi, yüz yüze derslerden farklı değildir. Ancak, ortak zorunlu derslerin sınavları, zorunlu haller dışında, yüz yüze yapılır. Uzaktan eğitim öğrencilerinin başarı notu, yarıyıl içi sınavının %15’i ile yılsonu/bütünleme sınavında alınan notun %85’inin toplamıdır. Yüz yüze eğitimde ise ders başarı notu, öğrencinin yarıyıl içindeki sınavlar, uygulamalı çalışmalar, ödevler gibi çalışmalarda gösterdiği başarı ve yarıyıl sonu sınavının birlikte değerlendirilmesi ile elde edilir. Yarıyıl içi değerlendirmenin %40’ı ve yarıyıl sonu sınav notunun da %60’ı toplanmak suretiyle öğrencinin başarı notu hesaplanır. 

Ayrıca, uzaktan eğitim yoluyla alınan derslerin sınavları, koşullar elverdiği ölçüde yüz yüze yapılır; ancak, tamamlan uzaktan veya bir kısmı uzaktan olan derslerin sınavları çevrimiçi olarak da yapılabilir.

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 7290.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Sınavda kopya çekilmesinin cezası hakkında spesifik bir bilgi bulunmamaktadır. Ancak, sınavda kopya çekme girişiminde bulunmak bir disiplin suçu olarak tanımlanmaktadır. Disiplin süreci, 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesine göre yürütülmektedir. 
- Disiplin soruşturması, Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği hükümlerine göre yürütülür.
- Sınav kağıtlarında herhangi bir değişiklik yapmak ve zarar vermek yasaktır.
- Öğrenciler, sınavlara girebilmek için öğrenci kimlik belgelerini yanlarında bulundurmak ve görevlilerce istendiğinde göstermek zorundadırlar.

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
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [x] form
  - [x] birim
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 4501.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Üniversiteyi bırakıp ayrılmak istiyorsanız, ilgili birime iletisime gecmeniz ve yazılı talebinizi iletmeniz olabilir. Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre yükseköğretim kurumlarından çıkarma cezası almış olanlar ve kendi istekleri ile kaydını sildiren öğrencilerin Üniversite ile ilişiği kesilebilir. Eğitim-öğretim döneminde ders kaydınızı yaptırmamanız durumunda yasal olarak sorunla karşılaşabilirsiniz. Bu nedenle, her eğitim-öğretim döneminde mutlaka ders kaydınızı yaptırmanız ve öğrencilik durumunuzu aktif olarak sürdürmeniz gerekir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: Kural
- Akademik Programlar: Kural

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
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] kayıt
  - [x] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 7393.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kayıt dondurma süresinin bitiminde, öğrenimine kaldığı yerden devam edersin. 1 yıl ara verdikten sonra dönüşte ders seçimini, öğrenimine kaldığı yerden devam edecek şekilde yapacaksın. 
- Öğrenimine devam edeceğini bildirmeli ve gerekli kayıtları yenilemelisin.
- Ayrıldığın dönemin veya yılın başından başlamak koşuluyla öğrenimine devam edeceksin.
- Kayıt dondurduğun döneme ait sınavlara giremeyeceksin.

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
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/3
  - [ ] danışman
  - [ ] bölüm
  - [x] oidb@omu.edu.tr
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3857.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Öğrenci İşleri Daire Başkanlığı WEB sayfasında veya akademik takvimde belirtilen süreler içerisinde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
