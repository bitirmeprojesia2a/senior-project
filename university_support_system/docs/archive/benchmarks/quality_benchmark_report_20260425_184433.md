# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 18:44:33
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 96.0% |
| Anahtar Bilgi Kapsami | 71.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3787.5 ms |
| Medyan Sure | 3692.9 ms |
| Intent Analizi Aktif | 24/25 |
| Force LLM Sentez | 21/25 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=25, query_failures=0, agent_tasks=42, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 2/4 | 7382.6 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 2/3 | 4062.3 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 3/4 | 2466.2 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 4/4 | 2331.5 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 4612.5 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 4597.0 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 3790.6 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 2625.9 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 4/5 | 3522.0 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 2777.8 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 1/4 | 2844.0 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 2/4 | 3193.5 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 5115.9 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 2/4 | 4986.7 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 3/3 | 4803.7 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 4406.0 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 3598.3 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 4/4 | 2681.4 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 6/6 | 4060.5 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 4143.5 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 2/5 | 3692.9 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 2527.6 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 4270.6 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 0/4 | 2969.3 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 3/3 | 3225.1 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] üç hafta
  - [x] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=1639ms; academic_programs_orchestrator=1695ms; registration_agent=1860ms; student_affairs_orchestrator=2038ms
- **API Sureleri**: api_total=7372ms; dispatch=2129ms; final_llm=1294ms; compose=1332ms; telemetry=13ms
- **Sure**: 7382.6 ms
- **API Response Time**: 7321.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Daha önce alınan dersler için Dekanlığa/Müdürlüğe muafiyet dilekçesi vermelisiniz. Muafiyet başvurunuz sonuçlanıncaya kadar bu derslere kayıt yaptırıp devam etmeniz önemlidir. 
- Danışmanınız ile birlikte alacakacağınız derslere kaydınız yapılır.
- Bu süre zarfında mağdur olmamanız için dönem derslerine devam etmeniz önem arz etmektedir.
- Muafiyet talebi ilgili yönetim kurulu tarafından karara bağlanıncaya kadar siz derslere devam etmelisiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: internship_agent=1723ms; student_affairs_orchestrator=1823ms; curriculum_agent=1342ms; academic_programs_orchestrator=1409ms
- **API Sureleri**: api_total=4051ms; dispatch=1859ms; final_llm=1244ms; compose=1286ms; telemetry=13ms
- **Sure**: 4062.3 ms
- **API Response Time**: 4005.9 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Stajınızı tamamlamadan da tek ders sınavına girebilirsiniz. Sınava başarılı sayılmak için minimum 50 not almak gerekir. 
- Staj durumunuzu tamamlamak zorunda değilsiniz.
- Minimum geçme notu 50'dir.
- Ek sınav hakları ve diğer detalles hakkında departman evidence'lerinde daha detaylı bilgi bulunabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
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
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=1440ms; student_affairs_orchestrator=1531ms
- **API Sureleri**: api_total=2456ms; dispatch=1554ms; final_llm=788ms; compose=807ms; telemetry=19ms
- **Sure**: 2466.2 ms
- **API Response Time**: 2379.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Siz başarmış olduğunuz seçmeli ders yerine başka bir seçmeli seçtiniz ve devam zorunluluğunuz hakkında bilgi edinmek istiyorsunuz. Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli seçtiğinizde, devam şartınız doğacaktır. Daha önce başarısız olduğunuz dersin devam koşulu yerine getirilmiş olsa bile, yeni seçilen seçmeli derse devam etmeli ve öğretim programında belirtilen devam oranlarına uymalısınız. 

Bu nedenle, öğretim programında belirtilen devam oranlarına dikkat etmeniz gerektiğini unutmayın.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_yaz_okulu_egitim_ogretim.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: regulation_agent=1363ms; academic_programs_orchestrator=1446ms
- **API Sureleri**: api_total=2315ms; dispatch=1466ms; final_llm=719ms; compose=768ms; telemetry=16ms
- **Sure**: 2331.5 ms
- **API Response Time**: 2253.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Pedagojik formasyon dersleri sizin transkriptinize dahil ediliyor ve mezuniyet ortalamanıza etki etmekle birlikte diplomaya bir ibare yer alıyor. Diplomanızın arkasına "Pedagojik formasyon eğitimini tamamlamıştır" deniyor.

Dersin 40 AKTS'lik olduğunu ve 3. yarıyıldan itibaren alındığını bilin.

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
- **Ajan Sureleri**: international_agent=1876ms; academic_programs_orchestrator=1936ms; registration_agent=1632ms; student_affairs_orchestrator=1689ms; tuition_agent=6ms; finance_orchestrator=81ms
- **API Sureleri**: api_total=4598ms; dispatch=1987ms; final_llm=2489ms; compose=2534ms; telemetry=20ms
- **Sure**: 4612.5 ms
- **API Response Time**: 4543.4 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Öğrenim ücretini üniversitenin belirtilen hesabına yatırmanız gerekiyor. İkamet izni için gerekli belgeler konusunda Öğrenci İşleri'ne başvurmanız gerekir. Ayrıca, Samsun Göç İdaresi Müdürlüğü'ne başvurarak öğrenci ikamet izni almanız zorunludur. 

- İkamet izni alma işlemleri için gerekli belgelerin tam listesi sağlanmamıştır.
- Öğrenim ücretinin ödenmesi ve ikamet izni alma işlemleri için gereken adımlar konusunda Öğrenci İşleri ve Göç İdaresi ile iletişime geçmeniz önerilir.
- Öğrenim ücreti konusunda finans birimi ile de iletişime geçmeniz önerilir.

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
- Veritabani kaydi: ogrenim ucreti tablosu
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: tuition_agent=29ms; finance_orchestrator=259ms; regulation_agent=1780ms; academic_programs_orchestrator=1853ms; registration_agent=1852ms; student_affairs_orchestrator=1979ms
- **API Sureleri**: api_total=4581ms; dispatch=2232ms; final_llm=1262ms; compose=1299ms; telemetry=10ms
- **Sure**: 4597.0 ms
- **API Response Time**: 4522.3 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
ÇAP programına başvurmak için ana dal diploma programının ilgili sınıfında olmanız, ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve başvuru sırasındaki ana dal not ortalamasına göre belirlenen başarı sıralamasında en az ilk %20'sinde bulunmanız gerekir. Ayrıca, katkı payı/öğrenim ücreti ödemesi gereken öğrencilerin harç borcu olmadığından emin olmak gerekiyor. 
- Harç borcu ödenmeden programa başvuru yapılamaz.
- Katkı payı/öğrenim ücretini hesaplamanız ve ödemeyi gerçekleştirmeniz gerekir. 
- Yillik ucret 2.397,00 TL, donemlik ucret 1.198,50 TL'dir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: VT
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
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
- **Ajan Sureleri**: registration_agent=2333ms; student_affairs_orchestrator=2389ms; tuition_agent=7ms; finance_orchestrator=86ms
- **API Sureleri**: api_total=3782ms; dispatch=2420ms; final_llm=1273ms; compose=1300ms; telemetry=7ms
- **Sure**: 3790.6 ms
- **API Response Time**: 3739.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, öğrenci bilgi yönetim sistemine giriş yaparak akademik takvimde belirlenen süre içinde ders kaydını yapmanız gerekmektedir. Öncelikle başarısız olduğunuz ve alamadığınız alt dönem derslerini dönem içinde almak zorundasınız ve bunların yanı sıra ardışıklık gerektiren dersler için danışman onayı gerekmektedir. GANO'nuzu dikkate alarak AKTS kredileri toplamı 6, 10, 12 veya 15 olabilir ve bu durum da danışman onayı sürecini etkileyebilir. Eğer danışmanınıza ulaşamaz ve ders kaydınızı onaylatamazsanız, bölüm başkanınıza veya Dekan/Müdürünüze durumu bildirmeniz önerilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
  - [x] bildiri
  - [ ] harç
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1270ms; student_affairs_orchestrator=1356ms; tuition_agent=1400ms; finance_orchestrator=1457ms
- **API Sureleri**: api_total=2609ms; dispatch=1493ms; final_llm=1007ms; compose=1037ms; telemetry=12ms
- **Sure**: 2625.9 ms
- **API Response Time**: 2545.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Selamlamakta fayda yok, direkt olarak cevaba baslayalım. Burslu öğrencisi olarak yatay geçiş yapmak istiyorsanız bursunuzun devam etmesi için yeni üniversitenizde kayıt yaptırdığınız zaman üniversite değişikliğini bildirir dilekçe ile öğrenci belgenizi burs aldığınız kuruma mutlaka bildiriniz. Bursum kesilebilir, ancak burs aldığınız kurumla iletişim kurmak suretiyle bursunuzun devrine veya kesilmesine karar verilir. Bursum kesilme riskini giam etmek için zamanında gerekli bildirimler yapmak önemlidir. Bursunuzun devri veya kesilmesine ilişkin detaylı bilgi için burs aldığınız kuruma ulaşabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: sık_sorulan_sorular.txt
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=2472ms; academic_programs_orchestrator=2561ms; graduation_agent=1824ms; student_affairs_orchestrator=1914ms; tuition_agent=1553ms; finance_orchestrator=1618ms
- **API Sureleri**: api_total=3503ms; dispatch=2604ms; final_llm=733ms; compose=776ms; telemetry=23ms
- **Sure**: 3522.0 ms
- **API Response Time**: 3427.3 ms
- **Kaynak Sayisi**: 15

**Yanit:**
```
Program sürenizi aşmanız durumunda ek süre hakkınız vardır. Bu sürede katkı payı ödersiniz.

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
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
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
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=1566ms; student_affairs_orchestrator=1639ms
- **API Sureleri**: api_total=2755ms; dispatch=1662ms; final_llm=859ms; compose=879ms; telemetry=29ms
- **Sure**: 2777.8 ms
- **API Response Time**: 2675.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

Devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Bu dersi tekrar almak için, devam zorunluluğunu yerine getirerek dersi yeniden alabilirsiniz. Devam koşulu, teorik derslerde en az %70, ders uygulamaları, atölye ve laboratuvarlarda en az %80 devam etmektir. Bundan sonra dersi tekrar alabilmek için herhangi bir sınıra ihtiyacınız yok gibi görünüyor ancak bilgi bulunamadı.

Kesin olarak bütünleme sınavı tarihini bilemiyorum fakat devam koşulunu yerine getirdiğiniz zaman dersi tekrar alabilirsiniz.

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

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [x] öğrenim ücreti
  - [ ] gerek yok
  - [ ] yönetim kurulu
  - [ ] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1530ms; student_affairs_orchestrator=1614ms; tuition_agent=4ms; finance_orchestrator=50ms
- **API Sureleri**: api_total=2831ms; dispatch=1657ms; final_llm=1081ms; compose=1098ms; telemetry=12ms
- **Sure**: 2844.0 ms
- **API Response Time**: 2775.0 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Kayıt dondurduğunuz süre eğitim süresinden sayılır. Kayıt dondurmak istediğiniz dönemde harç ücretinizi yatırmak zorunda değilsiniz. Ancak kayıt dondurma işlemi gerceklestirildikten sonra öğrenim ücreti iadesi yapılmaz. 
Ayrıca, başarılı olan ve reussi ortalamasına göre yapılan sıralamada ilk %10’a giren ikinci öğretim öğrencilerinin-contributionsu farklılık gösterebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=2192ms; student_affairs_orchestrator=2355ms
- **API Sureleri**: api_total=3181ms; dispatch=2380ms; final_llm=676ms; compose=707ms; telemetry=8ms
- **Sure**: 3193.5 ms
- **API Response Time**: 3104.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Hazırlık sınıfındasiniz, Ek Madde-1 kapsamında üniversiteyi değiştirme başvurunuz hakkında sorularınız var. 

Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilirsiniz. Transkriptiniz bulunmuyor olsa da, merkezi yerleştirme puanı ile başvurusu yapabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: sık_sorulan_sorular.txt
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2407ms; student_affairs_orchestrator=2463ms; curriculum_agent=2356ms; academic_programs_orchestrator=2432ms
- **API Sureleri**: api_total=5103ms; dispatch=2518ms; final_llm=1601ms; compose=1645ms; telemetry=23ms
- **Sure**: 5115.9 ms
- **API Response Time**: 5040.9 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçiş ve kurumlar arası yatay geçiş arasındaki farklar özellikle kontenjan ve değerlendirme kriterleri açısından farklılık gösterir. Her iki durumda da genel not ortalamasının en az 2,80 olması gerekir. Kurum içi yatay geçişte, öğrencinin kendi üniversitesi içindeki bir başka programa geçiş yapmak istemesi söz konusudur. Kurumlar arası yatay geçişte ise, öğrenci başka bir üniversiteden kendi üniversitesine geçmek istemektedir. 

Aşağıdaki koşullar dikkate alınır:
- Disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez.
- Ön lisans ve lisans diploma programları arasında yatay geçiş yapılabilir, ancak ikinci öğretimden sadece ikinci öğretim diploma programlarına yatay geçiş yapılabilir.
- Bir dönemde en fazla 2 yatay geçiş başvurusu yapılabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=2958ms; academic_programs_orchestrator=3030ms
- **API Sureleri**: api_total=4977ms; dispatch=3075ms; final_llm=1081ms; compose=1107ms; telemetry=9ms
- **Sure**: 4986.7 ms
- **API Response Time**: 4916.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Siz hangi öğrenci sayısında bağlantılı ve mutlak değerlendirme sistemleri arasında ne gibi farklılıkların bulunduğunu öğrenmek istiyorsunuz. Bu farklılıkları ve hangi öğrenci sayısında hangisinin uygulayacağını açıklamak için elimizde verilen kaynaklardan yararlanacağız.

Bağlantılı değerlendirmenin ana özelliği, öğrencilerin başarı notlarının sınıftaki diğer öğrencilerle karşılaştırılmasıdır. Dolayısıyla, bir öğrencinin başarı notu, sınıfın genel performansı dikkate alınarak belirlenen bir skor olacaktır.

Diğer taraftan, mutlak değerlendirmede öğrencilere bir not düzeyinden fazlasına ihtiyaç duyulmaz, yalnızca bir not değerinden daha fazlasını elde etmeleri gerekir. Örneğin, bir dersten başarılı olmak için 60 puan alınması gerekebilir.

Bu farklılıkları göz önünde bulundurmak ve hangi öğrenci sayısında hangisinin uygulanacağını belirlemek zor olabilir. Bu nedenle, bu bilgi bulunmamaktadır.

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
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] diploma eki
  - [x] transkript
  - [x] yerine geçmez
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=2376ms; student_affairs_orchestrator=2463ms; curriculum_agent=2556ms; academic_programs_orchestrator=2656ms
- **API Sureleri**: api_total=4779ms; dispatch=2702ms; final_llm=1161ms; compose=1196ms; telemetry=35ms
- **Sure**: 4803.7 ms
- **API Response Time**: 4686.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Diploma eki ve transkript aynı şey değildir. Diploma eki, elde edilmiş yeti ve becerilerin ifade edildiği, diploma, derece, sertifika gibi belgelerin akademik ve mesleki tanınmasını sağlamaya yönelik bir belgedir. Transkript ise not çizelgesini ifade eder. Diploma eki, transkript yerine geçmez. Diploma eki, kişinin takip edip başarıyla tamamladığı öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek üzere verilir. 
Ayrıca, diploma ekinde eğitim ve değerlendirme sistemi gibi bilgilere yer verilirken, transkriptte öğrencinin not ortalaması ve aldığı dersler bulunur. Diploma eki ve transkript aynı bilgileri içermeyen ayrı belgelerdir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=factual
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1798ms; student_affairs_orchestrator=1895ms; curriculum_agent=1942ms; academic_programs_orchestrator=2045ms
- **API Sureleri**: api_total=4390ms; dispatch=2095ms; final_llm=1381ms; compose=1414ms; telemetry=14ms
- **Sure**: 4406.0 ms
- **API Response Time**: 4325.2 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kayıt dondurma ve kayıt yaptırmamak arasındaki fark, kayıt dondurulan dönem/dönemlerin süre hesabında dikkate alınmamasıdır. Siz, belgelendirecek önemli mazeretlerinizi veya eğitim-öğretimlerinize katkıda bulunacak durumlarından dolayı kayıt dondurabilirsiniz. Her iki durumda da öğrencilik haklarınız etkilenir. Kayıt dondurma döneminde öğrencilik haklarınız kullanılamaz. Kayıt yaptırmaz iseniz o dönemde öğrenimlerinize devam edemezsiniz. Ancak, kayıt dondurma durumunda süreden muaf olunacağı için öğrencilik süresi uzatılır. 
- Kayıt dondurma, kendi isteğinizle kayıt dönemini geçici olarak askıya almanızı ifade eder.
- Kayıt yaptırmamanın anlamı, akademik takvimde belirtilen süre içinde ders kaydını yapmamanızdır. Bu durum akademik ilerlemelerinizi olumsuz etkileyebilir.
- Kayıt dondurma, eğitim-öğretimine ara vermenizi ifade eder ve bu süre boyunca öğrencilik haklarınız askıya alınır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: yonerge_uzaktan_egitim_onlisans_lisans.pdf
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
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2197ms; student_affairs_orchestrator=2251ms
- **API Sureleri**: api_total=3585ms; dispatch=2272ms; final_llm=1233ms; compose=1248ms; telemetry=14ms
- **Sure**: 3598.3 ms
- **API Response Time**: 3538.9 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Ders Kaydından Danışman Onayına Kadar Süreci

Siz ilk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışman onayına kadar tüm süreci başından sonuna anlatmak ister misiniz? İşte süreci:

İlk olarak, akademik takvimde belirtilen süre içinde "Öğrenci Bilgi Sistemi" üzerinden ders kaydınızı yapın. Ders seçimini tamamladığınızda, akademik danışmanınızla iletişime geçerek ders seçimini onaylatın. Danışman onayını, öğrencinizin şahsen gelmesi gerektiği yönünde bağlayıcı bir hüküm bulunmamaktadır. Danışman, onaya gönderilen ders kaydını onaylama veya sistem üzerinden iade etme hakkını kullanabilir.

Eğer danışmanınıza ulaşamaz ve ders kaydınızı onaylatamazsanız, bölüm başkanınıza ulaşamazsanız, Dekan/Müdürünüze durumu bildirmek sureti ile akademik takvimde belirtilen süredeışman onayını yaptırınız. Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu ilgili odeme kanali yolu ile iletebilirsiniz. 

Bilgi bulunamadı.

(Not: Bu cevaptaki bazi bilgiler kaynaklarda dogrudan teyit edilemedi; ilgili birimden dogrulama yapmaniz onerilir.)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
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
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1586ms; student_affairs_orchestrator=1629ms
- **API Sureleri**: api_total=2667ms; dispatch=1648ms; final_llm=928ms; compose=950ms; telemetry=19ms
- **Sure**: 2681.4 ms
- **API Response Time**: 2613.1 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Sınav notuna itiraz etmek için başvurunuzu yaptıktan sonra, ne yapmalıyım?

Sınav notlarına itiraz etmek istiyorsanız, akademik takvimde belirtilen sınav not girişlerinin son gününden itibaren beş iş günü içerisinde Bölüm Başkanlığını ziyaret edebilir ve dilekçe vererek itiraz edebilirsiniz. İtiraz üzerine sınav kağıdı incelenir ve işlem yazılı ve gerekçeli olarak üç iş günü içinde yapılır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 6/6
  - [x] ders
  - [x] staj
  - [x] GANO
  - [x] 2,00
  - [x] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=factual
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=1781ms; student_affairs_orchestrator=1877ms
- **API Sureleri**: api_total=4049ms; dispatch=1897ms; final_llm=1011ms; compose=1026ms; telemetry=17ms
- **Sure**: 4060.5 ms
- **API Response Time**: 3999.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Merhaba, mezun olmak için gerekli koşulları ve ilişik kesme süreci hakkında bilgi arıyorsunuz. İşte adım adım açıklamaları:

Mezuniyet için gerekli koşulları belirlemek için ilk olarak Öğrenci Bilgi Ekranını kontrol etmelisiniz. GANO'nun 2,00 veya daha yüksek olması halinde diploma almaya hak kazanabilirsiniz. Mezuniyet ve ilişik kesme işlemlerini başlatmak için "İlişik Kesme Talebinde Bulun" seçeneğini kullanarak İlişik Kesme Sürecini başlatmanız gerekir. İşlemlerinizi UBYS üzerinden veya şahsen başvurarak ilişik kesme formunu onaylattıktan sonra öğrenim gördüğünüz birime teslim ederek başlatabilirsiniz.

Mezun olabilmek için, öğretim programının tüm ders, uygulama, staj gibi gereklerini başarıyla tamamlamanız ve GANO'nun 2,00 veya daha yüksek olması gereklidir. Mezuniyet durumunu E-Devlet üzerinden kontrol edebilirsiniz. İlişik kesme süreci tamamlanmış olsa da mezun olunduğu anlamına gelmemektedir; mezuniyet ve diploma basım işlemleri sürecini başlatmak için yapılmaktadır.

Bilgi bulunamadı; ilişkin kesisinde kaydın silinmesi için veya ders sayısını 1'e indiremeyenler için somut cevap bulunmamaktadır.

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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=2036ms; student_affairs_orchestrator=2094ms
- **API Sureleri**: api_total=4132ms; dispatch=2113ms; final_llm=1170ms; compose=1188ms; telemetry=20ms
- **Sure**: 4143.5 ms
- **API Response Time**: 4074.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Merhaba, diploma kaybolması ve e-devlette mezuniyet bilgisi görünmeme durumlarıyla ilgili yardımcı olmak için buradayız. Sorunlarınızı bir araya getirerek size yardımcı olmak istiyoruz.

Diplomanızı kaybetmeniz durumunda, nüfus cüzdanınız ile birlikte ilgili birim diploma birimine müracaat edebilirsiniz. Kendiniz gelemiyor iseniz noter vekaleti vererek vekilinize aldırabilir veya kamu kurumunda çalışıyorsanız resmi yazı ile talep edildiği takdirde kurumunuza resmi yazı ile gönderilmektedir.

E-devlette mezuniyet bilgilerinizi görüntüleyememeniz durumunda, Mezuniyet bilgilerinizi görüntüleyebilmek için ilgili birimde mezuniyet belgenizin mevcut olup olmadığını kontrol ettirmeniz ve gerekli işlemleri yapmanız gerekmektedir. Mezuniyet Belgesi için gerekli işlemleri yaptıktan sonra e-devlette bilgilerinizi kontrol edebilirsiniz.

Not: Diploma alana ilişkin somut bir yol göstermemiz mümkün olmadı, lütfen ilgili birim ile temas kurarak yardımcı olun.

(Not: Bu cevaptaki bazi bilgiler kaynaklarda dogrudan teyit edilemedi; ilgili birimden dogrulama yapmaniz onerilir.)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
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
- **Ajan Sureleri**: graduation_agent=1232ms; student_affairs_orchestrator=1302ms; curriculum_agent=1635ms; academic_programs_orchestrator=1701ms
- **API Sureleri**: api_total=3681ms; dispatch=1767ms; final_llm=1816ms; compose=1844ms; telemetry=15ms
- **Sure**: 3692.9 ms
- **API Response Time**: 3633.1 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi, yüz yüze derslerden farklı değildir. Sınavların yüz yüze ve yazılı olarak yapılması esastır. Uzaktan eğitim öğrencilerinin dönem içi sınavlarının nasıl yapılacağına ilişkin karar senato tarafından verilir. 

Ayrıca, uzaktan verilen dersler için dönem içi değerlendirme ve başarıya etkisi, uzaktan eğitimde %40'tan fazla olamaz. 
Uzaktan eğitimde, koşullar elverdiği ölçüde tüm sınavların yüz yüze yapılması esastır, ancak bazı durumlarda çevrimiçi sınav türünden yararlanılabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_egitim_onlisans_lisans.pdf
- Belge: lisansüstü_eğitim_ve.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1543ms; student_affairs_orchestrator=1597ms
- **API Sureleri**: api_total=2516ms; dispatch=1641ms; final_llm=791ms; compose=802ms; telemetry=18ms
- **Sure**: 2527.6 ms
- **API Response Time**: 2463.1 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Sınavda kopya çekilmesinin cezası ve disiplin sürecine dair isteğinizi cevaplamak istiyorum. Sorunuzun yanıtını aşağıdaki gibi özetleyebiliriz.

- Disiplin süreci Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve ilgili diğer mevzuat hükümleri doğrultusunda işlenir.
- Kopya muamelesi, sınav sırasında cep telefonu ile ilgilenmek gibi tutumlarda bulunmak suretiyle gerçekleştirebilmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] ilişik kesme
  - [x] UBYS
  - [x] form
  - [x] birim
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2019ms; student_affairs_orchestrator=2121ms
- **API Sureleri**: api_total=4224ms; dispatch=2142ms; final_llm=1184ms; compose=1197ms; telemetry=19ms
- **Sure**: 4270.6 ms
- **API Response Time**: 4157.9 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Üniversiteyi Bırakmak ve İlişik Kesme İşlemleri

Siz üniversiteyi bırakmak ve tüm işlemleri gerçekleştirmek istiyorsanız, ilk olarak "İlişik Kesme Talebinde Bulun" seçeneğini UBYS üzerinden seçmelisiniz. Eğer bu yolu tercih etmiyor ise, şayet şahsen başvuracağınız durumda ise ilişik kesme formunu doldurup belirtilen merkezlerde onaylattıktan sonra öğrenim gördüğünüz birimlere teslim etmeniz gerekir. 

Kaydınızın silinmesi ile birlikte öğrencilik hakkınız sona erer. E-devlet üzerinden mezuniyet durumunuzu kontrol ediniz ve ilişik kesme süreci tamamlandıktan sonra, mezuniyet ve diploma basım işlemleri başladıktan sonra mezun olunduğunuzu bilgilendirin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
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
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1883ms; student_affairs_orchestrator=1992ms
- **API Sureleri**: api_total=2950ms; dispatch=2017ms; final_llm=849ms; compose=859ms; telemetry=15ms
- **Sure**: 2969.3 ms
- **API Response Time**: 2890.9 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Hocam, okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini yapacağımız süreci öğrenmek istiyorum.

Dönüşte ders seçimini akademik takvimde belirtilen sürelerde "Öğrenci Bilgi Sistemi" üzerinden yapacaksınız. Ders seçimini tamamladığınızda, akademik danışmanınızla iletişime geçerek ders seçimini onaylatacaksınız. Bir de, başarıyla geçmiş ancak alt döneme geçen derslerini almanız gerekir. GANO'nuzun seviyesine göre AKTS kredileri toplamı 6, 10, 12 veya 15 olabilir. Ön koşullu ya da ardışıklık gerektiren dersler için danışman onayınız gerekecek.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: öğrenci_konseyi_yönergesi.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] danışman
  - [x] bölüm
  - [x] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1337ms; student_affairs_orchestrator=1409ms
- **API Sureleri**: api_total=3212ms; dispatch=1431ms; final_llm=870ms; compose=878ms; telemetry=22ms
- **Sure**: 3225.1 ms
- **API Response Time**: 3151.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Merhaba, ders notlarınız sisteme girmemiş. Bu durumda ne yapabilirisiniz? Danışmanınıza ulaşarak durumunuzu bildirmeniz gerektiğini söyleyebiliriz. Danışmanınıza ulaşılamadığı takdirde bölüm başkanınıza veya Dekan/Müdürünüze durumunuzu bildirebilirsiniz. Hiçbir yetkiliye ulaşılamadığı durumda oidb@omu.edu.tr adresine sistemle ilgili sorunuzunuzu e-posta yolu ile iletebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
