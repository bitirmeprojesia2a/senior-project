# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 01:59:36
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 96.0% |
| Anahtar Bilgi Kapsami | 70.0% |
| Temiz Kalite Orani | 96.0% |
| Ortalama Sure | 13118.9 ms |
| Medyan Sure | 12106.5 ms |
| Intent Analizi Aktif | 23/25 |
| Force LLM Sentez | 19/25 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=25, query_failures=0, agent_tasks=41, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 3/4 | 23492.4 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 3/3 | 20161.0 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 2/4 | 9588.5 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 3/4 | 12681.2 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 17433.6 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 13946.5 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 13672.5 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 5/5 | 14135.5 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 5/5 | 16827.2 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 14285.3 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 2/4 | 12138.6 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 2/4 | 10524.4 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 13922.6 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 3/4 | 11158.0 | uydurma_riski |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 2/3 | 10070.9 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 4/4 | 12106.5 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 11840.7 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 4/4 | 10689.7 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 3/6 | 12245.6 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 10194.6 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 2/5 | 11934.9 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 10540.0 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 3/4 | 12052.3 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 0/4 | 11233.4 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 2/3 | 11097.2 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] üç hafta
  - [x] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=19791ms; academic_programs_orchestrator=19932ms; registration_agent=15440ms; student_affairs_orchestrator=15520ms
- **API Sureleri**: api_total=23505ms; dispatch=20005ms; global_llm=1578ms; compose=1619ms; telemetry=8ms
- **Sure**: 23492.4 ms
- **API Response Time**: 23460.7 ms
- **Kaynak Sayisi**: 11

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, kayıt yaptırdığı öğretim yılının en geç 3. haftasının sonuna kadar transkripti ve ders içerikleri ile birlikte dekanlığa muafiyet başvurusunda bulunabilir. Muafiyet talebi ilgili yönetim kurulu tarafından karara bağlanıncaya kadar öğrenciler, muafiyet talebinde bulunduğu derslere devam etmeli ve mağdur olmamak için dönem derslerine devam etmeniz önem arz etmektedir. Karara itiraz etmek için, muafiyet işleminin kesinleşip tarafınıza bildirildiği tarihten itibaren en geç bir hafta içinde ilgili birime dilekçe ile itirazda bulunabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG
- Ogrenci Isleri: RAG

Kaynak Ozeti:
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: internship_agent=17562ms; student_affairs_orchestrator=17929ms; curriculum_agent=14169ms; academic_programs_orchestrator=14266ms
- **API Sureleri**: api_total=20165ms; dispatch=17990ms; global_llm=1215ms; compose=1247ms; telemetry=11ms
- **Sure**: 20161.0 ms
- **API Response Time**: 20094.9 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Tek ders sınavına girebilmek için stajınızı tamamlamış olmanız gerekmiyor. Sınavda başarılı sayılmak için minimum not CC veya CB olmalıdır. Detaylı olarak:
* CC notu, öğrenci işleri departmanının verdiği bilgiye göre başarılı sayılmanızı sağlar.
* CB notu, akademik programlar departmanının verdiği bilgiye göre başarılı sayılmanızı sağlar.

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
- **Key Facts**: 2/4
  - [ ] değiştirebilir
  - [ ] devam koşulu
  - [x] yeni
  - [x] ders
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=7985ms; student_affairs_orchestrator=8142ms
- **API Sureleri**: api_total=9553ms; dispatch=8172ms; global_llm=1232ms; compose=1256ms; telemetry=15ms
- **Sure**: 9588.5 ms
- **API Response Time**: 9470.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Başarısız olduğunuz seçmeli ders yerine yeni seçtiğiniz seçmeli derse devam şartınız doğacaktır. Devam zorunluluğu, teorik derslerde en az %70, uygulama, atölye ve laboratuvarlarda %80'dir. Bu devam zorunluluğunu yerine getirmeniznecessary. 
- Devam zorunluluğunu yerine getirebilmek için teorik derslere %70, uygulama, atölye ve laboratuvarlara %80 oranında devam etmelisiniz. 
- Başarısız olduğunuz seçmeli ders yerine yeni bir seçmeli ders seçtiğinizde, danışmanınızın onayıyla bu değişikliği yapabilirsiniz.
- Öğretim programı değişikliği bakımından, azami öğrenim süresi içerisinde mezun olamayan öğrenciler için öğretim programında değişiklik yapılabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q4: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: hard
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] transkript
  - [x] dahil
  - [x] ortalama
  - [ ] tamamlamıştır
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: regulation_agent=11224ms; academic_programs_orchestrator=11355ms
- **API Sureleri**: api_total=12674ms; dispatch=11410ms; global_llm=1157ms; compose=1177ms; telemetry=22ms
- **Sure**: 12681.2 ms
- **API Response Time**: 12610.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Pedagojik formasyon dersleri transkriptte yer alır ve mezuniyet ortalamasına dahil edilir. Diplomalarında da pedagojik formasyon eğitimini tamamladıklarına ilişkin bir ibare yer alır. Pedagojik formasyon dersleri seçmeli ders olarak alındığından, transkript içinde yer alır. 
- Alınan pedagojik formasyon dersleri, transkriptte yer alır ve mezuniyet ortalamasına dahil edilir.
- Pedagojik formasyon eğitimini tamamlayan öğrencilerin diplomalarında bu eğitimi tamamladıklarına ilişkin bir ibare bulunur.
- Pedagojik formasyon dersleri 40 AKTS'den oluşur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt
- Belge: lisans_pedagojik_formasyon_derslerine_ilişkin.pdf
- Belge: uygulama_esaslari_lisans_pedagojik_formasyon.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: international_agent=15270ms; academic_programs_orchestrator=15371ms; registration_agent=15093ms; student_affairs_orchestrator=15181ms; tuition_agent=16ms; finance_orchestrator=98ms
- **API Sureleri**: api_total=17397ms; dispatch=15430ms; global_llm=1873ms; compose=1909ms; telemetry=8ms
- **Sure**: 17433.6 ms
- **API Response Time**: 17359.3 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Öğrenim ücretini üniversite hesabına yatırmalısınız. İkamet izni için Göç İdaresi İl Müdürlüğünden ikamet izni almanız zorunludur. İlgili belgelere ve sürelere dikkat etmeniz gerekmektedir. İkamet izni için pasaport, öğrenim vizesi, öğrenci belgesi, sağlık sigortası ve Türkiye'de kalacağı adresi gösteren belge gibi belgeleri hazırlamalısınız. 
- Öğrenim ücreti ve diğer ödemeler hakkında daha detaylı bilgi almak için finans birimi ile iletişime geçebilirsiniz.
- Ödemenin yapılması ve gerekli belgelerin ibraz edilmesiyla kaydınız kesin olarak yapılır. 
- Kayıt işlemlerinin tamamlanması için öğrenim ücretini ödemeniz ve gerekli belgeleri sunmanız zorunludur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: uluslararası_öğrenci_ikamet_işlemleri.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: uluslararası_öğrenci.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
- Belge: öğrenci_konukevi_uygulama_yönergesi.pdf
- Belge: yonerge_onlisans_lisans_staj.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=conditional
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: tuition_agent=17ms; finance_orchestrator=89ms; registration_agent=11367ms; student_affairs_orchestrator=11447ms; regulation_agent=11431ms; academic_programs_orchestrator=11504ms
- **API Sureleri**: api_total=13942ms; dispatch=11564ms; global_llm=1322ms; compose=1354ms; telemetry=14ms
- **Sure**: 13946.5 ms
- **API Response Time**: 13891.2 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
ÇAP programına başvurmak için katkı payı/öğrenim ücreti borcu bulunmaması gerekir. Harç borcunuzu ödemelisiniz. ÇAP başvuru şartları arasında ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında en az %20'de bulunmanız gerekir. Harç borcu olan öğrenciler başvurularını yapabilir ancak kayıt işlemlerini tamamlamak için harç borcunu ödemelidir. 
- Ödemeniz gereken yillik ucret 2.397,00 TL, donemlik ucret 1.198,50 TL'dir.
- Harç borcu ödenmedikçe kayıt işlemleri tamamlanmaz.
- Ana dal diploma programinin ilgili sınıfında en az %20'de bulunmanız Necessarydir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: VT
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=12580ms; student_affairs_orchestrator=12659ms; tuition_agent=12ms; finance_orchestrator=94ms
- **API Sureleri**: api_total=13664ms; dispatch=12729ms; global_llm=834ms; compose=848ms; telemetry=9ms
- **Sure**: 13672.5 ms
- **API Response Time**: 13616.7 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, akademik takvimde belirtilen süre içinde Öğrenci Bilgi Sistemi üzerinden ders kaydını yapabilirsiniz. Ders seçimi tamamladıktan sonra akademik danışmanınızla iletişime geçerek ders seçimini onaylatmanız gerekir. Danışman onay bittikten sonra, kayıtlanmış olduğunuz dersleri kontrol etmeniz ve müfredat bilgilerinizle transkriptinizi karşılaştırmanız önemlidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 5/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [x] bildiri
  - [x] harç
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=12563ms; student_affairs_orchestrator=12693ms; tuition_agent=10801ms; finance_orchestrator=10889ms
- **API Sureleri**: api_total=14117ms; dispatch=12765ms; global_llm=1253ms; compose=1272ms; telemetry=13ms
- **Sure**: 14135.5 ms
- **API Response Time**: 14060.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bursunuzun devri veya kesilip kesilmeyeceği konusunda bilgiye ulaşmak için burs aldığınız kurumla iletişim kurmanız gerekmektedir. Ayrıca, kayıtlı olduğunuz üniversite olan Ondokuz Mayis Universitesi'nden başka bir üniversiteye geçiş yaptığınız takdirde de bursunuz kesilebilir. Bursunuzun devam etmesi için üniversite değişikliğini bildirir dilekçe ile kayıt yaptırdığınız üniversiteye ait öğrenci belgesini burs aldığınız kuruma mutlaka bildiriniz. 
Aşağıdaki önemli noktaları dikkate almalısınız:
* Burs aldığınız kurumla komunikasyon kurunuz
* Üniversite değişikliğini bildiren dilekçe ve öğrenci belgesini sununuz
* İade alabilmek için uygun belgeleri Öğrenci İşleri Daire Başkanlığı harç bürosuna sunmaninz gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs', 'finance'] (beklenen: ['academic_programs', 'student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 5/5
  - [x] azami
  - [x] ek
  - [x] süre
  - [x] katkı payı
  - [x] öde
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=15451ms; academic_programs_orchestrator=15537ms; graduation_agent=15339ms; student_affairs_orchestrator=15506ms; tuition_agent=12413ms; finance_orchestrator=12639ms
- **API Sureleri**: api_total=16802ms; dispatch=15629ms; global_llm=1036ms; compose=1075ms; telemetry=13ms
- **Sure**: 16827.2 ms
- **API Response Time**: 16746.9 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Program süresini aşmanız durumunda ilgili dönem katkı payı ücreti ödenir. Ek süre hakkınız vardır, bu sürede katkı payı ödeyorsunuz. Azami eğitim süresi sonunda kayıtlı olduğunuz öğretim programından mezun olamayan öğrencilere ilave iki dönem ek süre verilir.

Ek süre hakkınızın kullanılması için belirlenen azami süre içinde öğreniminizi tamamlamak zorundasınız. 
Bu süre boyunca katkı payı ödemeniz gerekecektir. 
Azami eğitim süresi sonunda mezun olamayan öğrencilere ilave iki dönem ek süre verilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM
- Finans: RAG + LLM

Kaynak Ozeti:
- Belge: tıp_fakültesi_tıp_doktorluğu_programı.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
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
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [x] tekrar
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=11830ms; student_affairs_orchestrator=12068ms
- **API Sureleri**: api_total=14228ms; dispatch=12203ms; global_llm=805ms; compose=816ms; telemetry=12ms
- **Sure**: 14285.3 ms
- **API Response Time**: 14133.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Bu dersi, sonraki dönemde tekrar alabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] öğrenim ücreti
  - [ ] gerek yok
  - [ ] yönetim kurulu
  - [x] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=10731ms; student_affairs_orchestrator=10828ms; tuition_agent=6ms; finance_orchestrator=86ms
- **API Sureleri**: api_total=12119ms; dispatch=10894ms; global_llm=1127ms; compose=1155ms; telemetry=10ms
- **Sure**: 12138.6 ms
- **API Response Time**: 12069.6 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Kayıt dondurduğunuz süre eğitim süresinden sayılır. Kayıt dondurmak için katkı payı/öğrenim ücreti ödemeniz gerekmez, ancak katkı payı/öğrenim ücreti ödemeyen öğrencilerin kayıt işlemleri yapılmaz. 
- Kayıt dondurma işleminden önce katkı payı/öğrenim ücreti borcu olmaması gerekir.
- Yan dal/çift ana dal öğrencileri için bazı özel durumlar geçerli olabilir.
- Eğitim süresinden sayılması nedeniyle azami süreden önce mezun olma durumunu etkileyebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] transkript
  - [x] Ek Madde
  - [ ] başvuru yapabilir
  - [ ] GANO
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=9285ms; student_affairs_orchestrator=9400ms
- **API Sureleri**: api_total=10517ms; dispatch=9433ms; global_llm=1000ms; compose=1014ms; telemetry=8ms
- **Sure**: 10524.4 ms
- **API Response Time**: 10466.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Evet, hazırlık sınıfındaysanız ve transkriptiniz yoksa dahi, Ek Madde-1 (Merkezi Yerleştirme Puanı) ile başka bir üniversiteye yatay geçiş başvurabilirsiniz. Bu başvurularda transkript gerekliliği olmaz. Bir dönemde en fazla 2 yatay geçiş başvurusu yapabilirsiniz.

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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=11424ms; academic_programs_orchestrator=11507ms; registration_agent=11387ms; student_affairs_orchestrator=11468ms
- **API Sureleri**: api_total=13905ms; dispatch=11594ms; global_llm=1282ms; compose=1320ms; telemetry=7ms
- **Sure**: 13922.6 ms
- **API Response Time**: 13856.9 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
Kurum içi yatay geçiş ve kurumlar arası yatay geçiş arasındaki farklar, başvurunun yapıldığı kurumun aynı olması mı yoksa farklı olması mı olduğuna göre değişir. Kurum içi yatay geçişte, siz aynı üniversite içinde farklı bir programa geçiş yapmak istiyorsanız, genel not ortalamasının 4 üzerinden en az 2,80 olması gerekir. Kurumlar arası yatay geçişte ise, başka bir üniversiteden öğrenci kabul edilir ve genel not ortalamasının en az 2,80 olması gerekir. 
- Disiplin cezası almış olanların yatay geçiş başvuruları kabul edilmez.
- Kurum içi yatay geçişte, programa geçmek istediğiniz yıldaki merkezi yerleştirme puanınızın, geçmek istediğiniz programın taban puanına eşit veya yüksek olması durumunda, herhangi bir başarı şartı aranmaz.
- Başvuruların değerlendirilmesinde, program türlerine göre genel not ortalaması ve merkezi yerleştirme puanı dikkate alınır.

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
- Belge: sık_sorulan_sorular.txt
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=8557ms; academic_programs_orchestrator=8738ms
- **API Sureleri**: api_total=11131ms; dispatch=8778ms; global_llm=1377ms; compose=1416ms; telemetry=16ms
- **Sure**: 11158.0 ms
- **API Response Time**: 11077.0 ms
- **Kaynak Sayisi**: 5
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Bağıl değerlendirme sistemi, öğrencilerin birbirleriyle kıyaslanarak değerlendirildiği bir sistemdir. Mutlak değerlendirme sistemi ise, öğrencilerin mutlak bir ölçekte değerlendirildiği bir sistemdir. Bağıl değerlendirme sistemi, genellikle az sayıda öğrencinin olduğu sınıflarda uygulanır, çünkü bu sistemde öğrencilerin birbirleriyle kıyaslanması daha kolaydır. Mutlak değerlendirme sistemi ise, genellikle daha büyük sınıflarda uygulanır. 
Bazi durumlarda, 
- bagıl değerlendirme sistemi az ogrenci sayısında,
- mutlak değerlendirme sistemi daha büyük ogrenci sayısında uygulanabilir. 
Ogrenci sayisina bagli net bir bilgi bulunamadi.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=7761ms; student_affairs_orchestrator=7864ms
- **API Sureleri**: api_total=10060ms; dispatch=7935ms; global_llm=1236ms; compose=1251ms; telemetry=8ms
- **Sure**: 10070.9 ms
- **API Response Time**: 10016.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Diploma eki, transkript veya diploma yerine geçemez. Diploma eki, kişinin takip edip başarıyla tamamladığı öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek üzere verilir. Transkript, not çizelgesini içerir ve diploma eki bu bilgileri içermemektedir. Dolayısıyla, diploma eki transkript yerine kullanılamaz.

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
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] kayıt dondurma
  - [x] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=9661ms; student_affairs_orchestrator=9789ms; tuition_agent=8749ms; finance_orchestrator=8841ms
- **API Sureleri**: api_total=12081ms; dispatch=9865ms; global_llm=1228ms; compose=1275ms; telemetry=27ms
- **Sure**: 12106.5 ms
- **API Response Time**: 12000.8 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kayıt dondurma ile kayıt yaptırmamak arasında bir fark vardır. Kayıt dondurulan süreler eğitim-öğretimden sayılmaz. Öte yandan, kayıt yaptırmazsanız o dönemde öğrenimine devam etme hakkınızı kaybetmiş olursunuz. Kaydınızın silinmesi ile birlikte öğrencilik hakkınız sona erer. 
- Kayıt dondurma durumunda, öğrenci öğretim dönemine geri döndüğünde haklarına devam edebilir.
- Kayıt yaptırmazsanız, öğretim ücreti ve katkı payı ödemelerine tabi olabilir ve öğrencilik hakları askıya alınabilir.
- Özellikle birden fazla yükseköğretim programında kaydı olan sizler, ikinci ve sonraki programlar için katkı payını ödersiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Key Facts**: 3/5
  - [ ] UBYS
  - [x] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=10332ms; student_affairs_orchestrator=10397ms
- **API Sureleri**: api_total=11833ms; dispatch=10428ms; global_llm=1316ms; compose=1329ms; telemetry=8ms
- **Sure**: 11840.7 ms
- **API Response Time**: 11784.8 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Ders kaydını yapmak için akademik takvimde belirtilen süre içinde Öğrenci Bilgi Sistemi üzerinden kaydınızı yapmalısınız. Sonra akademik danışmanınızla iletişime geçerek ders seçimini onaylatmalısınız. Eğer akademik danışmanınıza ulaşamazsanız, bölüm başkanınıza veya dekan/müdürünüze durumu bildirmelisiniz. 
- Ders kaydında müfredat durum kontrolü, akademik takvimde belirtilen süre içinde kaydın tamamlanması ve danışman onayı önemlidir.
- Her dönem/yıl başında öncelikle başarısız olduğunuz ve alamadığınız alt dönem derslerini almak zorundasınız. 
- Genel akademik not ortalamalarına göre belirli AKTS tutarları kadar üst dönemlerden ders alabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] itiraz
  - [x] beş iş günü
  - [x] dilekçe
  - [x] bölüm başkanlığı
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=9283ms; student_affairs_orchestrator=9412ms
- **API Sureleri**: api_total=10674ms; dispatch=9441ms; global_llm=1155ms; compose=1177ms; telemetry=11ms
- **Sure**: 10689.7 ms
- **API Response Time**: 10632.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Sınav notlarına itiraz etme süreniz, akademik takvimde belirtilen sınav not girişlerinin öğrenci otomasyon sistemine girilmesinin son gününden itibaren beş iş günüdür. İtiraz dilekçesini ilgili birime (Bölüm Başkanlığına) vererek başvurabilirsiniz. 
İtiraz üzerine sınav kağıdı incelenir ve işlem yazılı ve gerekçeli olarak gerçekleştirilir. Öğretim elemanı tarafından fark edilen maddi hataya ilişkin not düzeltme formu, notların ilanından sonra düzenlenebilir. İlgili birim tarafından düzenlenen not düzeltme itiraz formu, üç iş günü içinde Öğrenci İşleri Daire Başkanlığına gönderilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=10026ms; student_affairs_orchestrator=10102ms
- **API Sureleri**: api_total=12237ms; dispatch=10149ms; global_llm=1133ms; compose=1148ms; telemetry=10ms
- **Sure**: 12245.6 ms
- **API Response Time**: 12197.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Mezuniyet için gerekli koşulları ve ilişik kesme sürecini başlatmak için Öğrenci Bilgi Ekranındaki Diğer menüsü altında yer alan "İlişik Kesme Talebinde Bulun" seçeneğini kullanmanız gerekir. Mezuniyet hakkı, öğrenim gördüğünüz programın bütün şartlarını yerine getirmekle kazanılır. İlişik kesme için, yükseköğretim kurumları öğrenci disiplin yönetmeliği ve ilgili mevzuat hükümlerine göre, kaydı silinen veya ders sayısını bire indiremeyen öğrencilerin üniversiteleri ile ilişiği kesilir. Mezuniyet durumunuzu E-Devlet üzerinden kontrol edebilirsiniz. Mezun olduktan sonra, nüfus kaydı değişikliği olması halinde, yeniden diploma düzenlenebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=7596ms; student_affairs_orchestrator=7676ms
- **API Sureleri**: api_total=10171ms; dispatch=7717ms; global_llm=1204ms; compose=1229ms; telemetry=26ms
- **Sure**: 10194.6 ms
- **API Response Time**: 10103.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Diplomanızı kaybetmeniz durumunda, diploma defterinde yer alan bilgilere göre yeni bir diploma düzenlenebilir. Mezuniyet bilgilerinizin e-devlette görünmemesi durumunda, diploma defterinde yer alan bilgiler elektronik ortamda arşivlendiği için, mezun olduğunuz birimin diploma defterine başvurarak mezuniyet bilgilerinizi doğrulatmanız mümkün olabilir. 
Aşağıdaki adımları takip edebilirsiniz:
- Diplomayı kaybetme durumunda diploma defterindeki bilgilerinize göre yeni bir diploma düzenlenebilir.
- Mezuniyet bilgilerinizi doğrulatmak için mezun olduğunuz birimin diploma defterine başvurabilirsiniz.

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
- **Key Facts**: 2/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [x] %40
  - [ ] %60
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=10204ms; student_affairs_orchestrator=10263ms; curriculum_agent=10337ms; academic_programs_orchestrator=10424ms
- **API Sureleri**: api_total=11924ms; dispatch=10494ms; global_llm=1328ms; compose=1364ms; telemetry=12ms
- **Sure**: 11934.9 ms
- **API Response Time**: 11876.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi, yüz yüze derslerden farklı değildir. Koşullar elverdiği ölçüde tüm sınavların yüz yüze yapılması esastır. 
- Uzaktan verilen dersler için dönem içi değerlendirme, başarıya etkisi %40'tan fazla olamaz.
- Kismi uzaktan olan derslerin sınavları çevrimiçi olarak da yapılabilecek, diğer yöntemlerden biri veya birkaçı kullanılarak da yapılabilir.
- Zorunlu haller dışında, derslerin sınavları yüz yüze yapılır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=9210ms; student_affairs_orchestrator=9317ms
- **API Sureleri**: api_total=10510ms; dispatch=9343ms; global_llm=1069ms; compose=1092ms; telemetry=11ms
- **Sure**: 10540.0 ms
- **API Response Time**: 10452.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınavda kopya çekilmesinin cezası hakkında ozel bir bilgiye ulaşılamamıştır, ancak kopya muamelesi yapan sizlere Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre işlem yapılacağı belirtilmiştir. Sınav görevlileri kopya çekme veya çekme girişiminde bulunma durumu tespitine dikkat etmektedir. Ayrıca, sınav salonundan çıkana kadar cep telefonu ile herhangi bir şekilde ilgilenen sizlere kopya muamelesi yapılacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] ilişik kesme
  - [x] UBYS
  - [x] form
  - [ ] birim
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=9065ms; student_affairs_orchestrator=9187ms
- **API Sureleri**: api_total=12029ms; dispatch=9234ms; global_llm=1738ms; compose=1750ms; telemetry=13ms
- **Sure**: 12052.3 ms
- **API Response Time**: 11977.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Üniversiteden ayrılmak için ilişik kesme süreci başlatabilirsiniz. Bunu UBYS üzerinden "İlişik Kesme Talebinde Bulun" seçeneğini kullanarak veya şahsen başvurarak ilişik kesme formunu doldurup teslim ederek gerçekleştirebilirsiniz. Kaydınızın silinmesi ile birlikte öğrencilik hakkınız sona erer. Ayrıca, mezuniyet durumunuzun E-Devlet üzerinden kontrol edilmesini sağlamak önemlidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 0/4
  - [ ] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=10232ms; student_affairs_orchestrator=10288ms
- **API Sureleri**: api_total=11211ms; dispatch=10317ms; global_llm=820ms; compose=832ms; telemetry=14ms
- **Sure**: 11233.4 ms
- **API Response Time**: 11161.1 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Okulumuzu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini akademik takvimde belirtilen sürelerde "Öğrenci Bilgi Sistemi" üzerinden gerçekleştireceksiniz. Ders seçimini tamamladığınızda akademik danışmanınızla iletişime geçerek ders seçimini onaylatmanız gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: öğrenci_konseyi_yönergesi.pdf
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/3
  - [ ] danışman
  - [x] bölüm
  - [x] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=9089ms; student_affairs_orchestrator=9195ms
- **API Sureleri**: api_total=11085ms; dispatch=9224ms; global_llm=877ms; compose=892ms; telemetry=16ms
- **Sure**: 11097.2 ms
- **API Response Time**: 11018.3 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Ders notlarınızı sisteme girmemiş olan hocanızla iletişime geçerek not girişinin yapılması gerektiğini bildirin. Hocanızla ulaşamadığınız takdirde bölüm başkanlığını bilgilendirebilirsiniz. Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
```
