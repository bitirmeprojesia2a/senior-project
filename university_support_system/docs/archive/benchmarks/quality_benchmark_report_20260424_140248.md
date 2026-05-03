# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 14:02:48
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 40.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3684.5 ms |
| Medyan Sure | 2867.3 ms |
| Intent Analizi Aktif | 7/7 |
| Force LLM Sentez | 5/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=7, query_failures=0, agent_tasks=9, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 2/4 | 1178.9 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 5909.6 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 6755.6 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 4452.1 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 2541.3 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 2086.4 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 2867.3 | - |

## Soru Detaylari

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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=999ms; student_affairs_orchestrator=1080ms
- **API Sureleri**: api_total=1171ms; dispatch=1100ms; compose=3ms; telemetry=13ms
- **Sure**: 1178.9 ms
- **API Response Time**: 1124.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli dersi seçerseniz, sonraki dönemde/yılda devam etmek kaydıyla, devam zorunluluğunuz değişmez. Ancak, yeni seçmeli dersi almanız durumunda, o derse devam etmek zorundasınız.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yaz_okulu_eğitim_öğretim.pdf
- Belge: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] not ortalaması
  - [x] harç
  - [ ] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: tuition_agent=6ms; finance_orchestrator=66ms; regulation_agent=3333ms; academic_programs_orchestrator=3424ms
- **API Sureleri**: api_total=5884ms; dispatch=3463ms; global_llm=1368ms; compose=1387ms; telemetry=21ms
- **Sure**: 5909.6 ms
- **API Response Time**: 5818.6 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
ÇAP başvurularının değerlendirilmesinde öncelikle ana dal not ortalamasına önem verilir ve not ortalamasının %20'sinde bulunmanız gerekir. Ayrıca, fazla kredi tamamlamış olan öğrencilere öncelik verilir. Harç borcu başvuruya engel bir durum değildir, ancak öğrenim süresince genel not ortalamasının 2,75'in altına düşmemeye dikkat etmelisiniz. ÇAP öğrencileri, hem lisans öğrenimi gördükleri ana dala hem ikinci ana dala ait dersleri almalıdır.

- ÇAP başvurularında ana dal not ortalamasına ve ortalamanın en az %20'sinde bulunmaya dikkat etmelisiniz.
- Harç borcunuzu ödeyebilmeniz için gereken bilgi bulunmamaktadır.
- Öğrenim süresince genel not ortalamasının 2,75'in altına düşmemeye dikkat etmeniz gerekir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: VT
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=3406ms; student_affairs_orchestrator=3463ms; international_agent=3706ms; academic_programs_orchestrator=3787ms
- **API Sureleri**: api_total=6737ms; dispatch=3850ms; global_llm=1519ms; compose=1571ms; telemetry=22ms
- **Sure**: 6755.6 ms
- **API Response Time**: 6640.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçiş, öğrencinin kayıtlı olduğu üniversitede farklı bir programa geçiş yapmasını sağlarken, kurumlar arası yatay geçiş, öğrencinin farklı bir üniversiteye geçiş yapmasını sağlar. Her iki tipo yatay geçiş başvurusunda da genel not ortalamasının en az 2,80 olması gerekir ve disiplin cezası almış öğrencilerin başvuruları kabul edilmez. Başvuru şartları ve değerlendirme kriterleri arasında farklılık gösteren bir diğer konu, kontenjanlardır. Kurum içi yatay geçiş kontenjanları, ilgili diploma programının son dört yıla ait taban puanları dikkate alınarak belirlenir. 
Yatay geçiş başvurularında, öğrencilerin kendi üniversitelerinde veya diğer üniversitelerde aldıkları notları ve bu notların genel ortalamalarının hesaplanması önemlidir. Kurum içi yatay geçişte not ortalamasının ve merkezi yerleştirme puanının belirli oranları dikkate alınırken, kurumlar arası yatay geçişte daha fazla kriter söz konusu olabilir. 
Yatay geçiş hakkı kazanan öğrencilerin harçlar ve intibak işlemleri de geçiş türü ve programa göre farklılık gösterebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=3253ms; student_affairs_orchestrator=3303ms
- **API Sureleri**: api_total=4439ms; dispatch=3326ms; compose=4ms; telemetry=9ms
- **Sure**: 4452.1 ms
- **API Response Time**: 4385.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Diploma kaybı ve e-devlette mezuniyet bilgilerinin görünmemesi durumunda, ilk olarak diploma kayıp başvurusu için gerekli belgeleri hazırlamanız gerekmektedir. Mahkeme kararı, diploma ücretini yatırdığını gösteren banka dekontu, kimlik fotokopisi ve dilekçe ile başvurmanız gerekmektedir. Mezuniyet bilgilerinin e-devlette görünmemesi durumunda ise, Islak imzalı belgelerin fotoğrafını, e-posta çıktısını ya da benzer belgeleri sunarak başvuruda bulunabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=2306ms; student_affairs_orchestrator=2397ms
- **API Sureleri**: api_total=2521ms; dispatch=2443ms; compose=3ms; telemetry=10ms
- **Sure**: 2541.3 ms
- **API Response Time**: 2465.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınavda kopya çekilmesinin cezası, disiplin suçudur. Disiplin süreci, 11.03.2023 tarihli resmi gazetede yayımlanan 2547 sayılı Yükseköğretim Kanunu'nda belirtilen hükümler çerçevesinde işler. 
- Sınav görevlileri kopya çekme girişimini tespit eder.
- Cep telefonu ile herhangi bir şekilde ilgilenen öğrenciye kopya muamelesi yapılır.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=991ms; student_affairs_orchestrator=1153ms
- **API Sureleri**: api_total=2073ms; dispatch=1195ms; compose=3ms; telemetry=9ms
- **Sure**: 2086.4 ms
- **API Response Time**: 2029.2 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Üniversiteyi bırakmak için yazılı isteğinizi sunmanız gerekir. Yazılı isteği üzerine kaydınız silinecektir. Ancak ÖSYM tarafından yeniden yerleştirilmediğiniz sürece üniversiteye tekrar kaydolamazsınız. Kaydını sildiren öğrencilerin üniversite ile ilişiği kesilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
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
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2631ms; student_affairs_orchestrator=2706ms
- **API Sureleri**: api_total=2833ms; dispatch=2737ms; compose=12ms; telemetry=12ms
- **Sure**: 2867.3 ms
- **API Response Time**: 2766.3 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kayıt dondurma süresinin bitiminde, ayrıldığınız dönemin/yılın başından başlamak koşuluyla öğrenimine kaldığınız yerden devam edersiniz. Ders seçimi yaparken, öncelikle başarısız olduğunuz ve alamadığınız alt dönem derslerini alınmalıdır. AKTS kredileri toplamı, GANO'nuzun seviyesine göre değişiklik gösterir: GANO'su 1,80-2,49 arası olan öğrenciler için

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
```
