# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 14:39:56
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 61.9% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 7805.2 ms |
| Medyan Sure | 3960.9 ms |
| Intent Analizi Aktif | 5/5 |
| Force LLM Sentez | 5/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=4, query_failures=0, agent_tasks=5, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 18226.4 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 9485.7 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 3766.9 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 3960.9 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 1/3 | 3586.0 | - |

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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=15196ms; academic_programs_orchestrator=15554ms; registration_agent=2824ms; student_affairs_orchestrator=6314ms
- **API Sureleri**: api_total=18191ms; dispatch=15625ms; final_llm=888ms; compose=917ms; telemetry=8ms
- **Sure**: 18226.4 ms
- **API Response Time**: 18141.4 ms
- **Kaynak Sayisi**: 11

**Yanit:**
```
Muafiyet başvurusunu yaptıktan sonra, karar çıkana kadar derslere devam etmeniz önemlidir. Daha önce aldığınız ve başarılı olduğunuz derslerden muaf tutulacaksınız. Bu süre zarfında mağdur olmamanız için dönem derslerine devam etmenizrecommendedtir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
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
- **Ajan Sureleri**: registration_agent=4073ms; student_affairs_orchestrator=8313ms; tuition_agent=24ms; finance_orchestrator=327ms
- **API Sureleri**: api_total=9407ms; dispatch=8348ms; final_llm=946ms; compose=968ms; telemetry=15ms
- **Sure**: 9485.7 ms
- **API Response Time**: 9336.0 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, ders kaydı akademik takvimde belirtilen süre içinde öğrenci bilgi sistemi üzerinden yapılır. Danışman onay süreci, kayıtlanmış olduğunuz dersleri danışmanınıza göndermeniz ve onların onayını beklemenizi içerir. Danışman onayı tamamlandıktan sonra, sizin onay için gönderdiğiniz derslerden bir veya birkaçı danışmanınız tarafından listeden çıkartılmış olabilir, bu nedenle kayıt yapmış olduğunuz dersleri tek tek kontrol etmeniz ve transkriptinizle karşılaştırmanız gerekmektedir. Ayrıca, bazı dersler için danışman onayı zorunludur, özellikle ardışıklik gerektiren dersler için.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
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
- **Ajan Sureleri**: registration_agent=2568ms; student_affairs_orchestrator=2652ms
- **API Sureleri**: api_total=3725ms; dispatch=2678ms; final_llm=929ms; compose=943ms; telemetry=9ms
- **Sure**: 3766.9 ms
- **API Response Time**: 3654.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Selam, merak ettiğin süreç hakkında bilgi verelim.

Ders kaydından danışman onayına kadar tüm süreci baştan sona açıklamaya çalışacağım. İlk kez üniversite kaydını yaptıran bir öğrenci olarak, akademik takvimde belirtilen süre içinde ders kaydını yapmanız gerekir. 

Bu surec, "Öğrenci Bilgi Sistemi" üzerinden gerçekleşir. Ders seçiminizi tamamladıktan sonra, akademik danışmanınızla iletişime geçerek ders seçiminizi onaylatmanız gerekir. 

Öncelikle, başarısız olduğunuz ve alamadığınız alt dönem derslerini almak zorundasınız. Ayrıca, genel akademik not ortalamalarına (GANO) göre alınabilecek derslerin AKTS kredi toplamı belirliyor: 

- GANO'su 1,80-2,49 arası olan öğrenciler için 6 AKTS, 
- GANO'su 2,50-2,99 arası olan öğrenciler için 10 AKTS,
- GANO'su 3,00-3,49 arası olan öğrenciler için 12 AKTS,
- GANO'su 3,50 ve üzerinde olan öğrenciler için 15 AKTS tutarında artırılabilir. 

Eğer akademik danışmanınıza ulaşamaz ve ders kaydını onaylatamazsanız, bölüm başkanınıza, bölüm başkanına da ulaşamazsanız Dekan/Müdürünüze durumu bildirmeniz gerekir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2025ms; student_affairs_orchestrator=2168ms
- **API Sureleri**: api_total=3930ms; dispatch=2218ms; final_llm=738ms; compose=752ms; telemetry=13ms
- **Sure**: 3960.9 ms
- **API Response Time**: 3874.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Üniversiteyi bırakmak istiyorsanız, ilk olarak İlişik Kesme Sürecini başlatmanız gerekmektedir. Bunu UBYS'den veya şahsen başvurarak ilişik kesme formunu doldurup onaylattıktan sonra öğrenim gördüğünüz birime teslim ederek yapabilirsiniz. Bu procesin tamamlanması mezuniyet durumunuzu temsil etmez, mezun olunduğunu E-Devlet üzerinden kontrol etmenizi sağlar.

Bu sürecinizi başlatmanız ardından, kaydınızın silinmesiyle birlikte öğrencilik hakkınız sona erecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1733ms; student_affairs_orchestrator=1806ms
- **API Sureleri**: api_total=3558ms; dispatch=1826ms; final_llm=807ms; compose=825ms; telemetry=20ms
- **Sure**: 3586.0 ms
- **API Response Time**: 3494.2 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Ders notlarınızı sisteme girmemis oldugunuzdan dolayi notlari veya gecerli olan derslerinizi goremezsiniz. Bu sorunla karsi karsiya kaldiginda ÖİDB Ders Kayıt ve Not İşlemleri Ofisi Sorumlusu ile iletişime geçebilir ve OIDB@omu.edu.tr adresine e-posta yoluyla sorunlarınızı bildirebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
