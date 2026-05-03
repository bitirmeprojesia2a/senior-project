# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 13:47:15
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 61.9% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 14030.4 ms |
| Medyan Sure | 13693.6 ms |
| Intent Analizi Aktif | 5/5 |
| Force LLM Sentez | 5/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=5, query_failures=0, agent_tasks=7, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 13693.6 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 9093.5 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 4322.6 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 26564.5 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 1/3 | 16477.9 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=10977ms; student_affairs_orchestrator=11119ms
- **API Sureleri**: api_total=13637ms; dispatch=11181ms; final_llm=882ms; compose=905ms; telemetry=12ms
- **Sure**: 13693.6 ms
- **API Response Time**: 13511.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Merhaba, yatay geçişle gelen bir öğrencisiniz. Muafiyet başvurunu ne zaman yapmanız ve karar çıkana kadar derslere devam edeceğiniz konusunda sorulan sorunun cevabını verdik.

Derslere devam etmeniz tavsiyesidir. 

Bu süre zarfında mağdur olmamak için dönem derslerine devam etmelisiniz.

Ayrıca, derslere kayıt yaparken dikkat etmeniz gereken en önemli durumdur. Bu, özellikle muafiyet başvurunuzun alınma süreci için önemlidir.

Detay olarak, öğrenci işleri personellerince yerine getirilmesi planlanan bu süre zarfında mağdur olmamanız için dönem derslerine devam etmeniz önemlidir.

Not: Mümkünse, muafiyet başvurunuzun sonuçlandı mı diye takip edebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
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
- **Ajan Sureleri**: registration_agent=6200ms; student_affairs_orchestrator=7319ms; tuition_agent=296ms; finance_orchestrator=7182ms
- **API Sureleri**: api_total=9081ms; dispatch=7362ms; final_llm=1174ms; compose=1187ms; telemetry=451ms
- **Sure**: 9093.5 ms
- **API Response Time**: 8577.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Harç ücretini yatırdıktan sonra, akademik takvimde belirtilen süre içerisinde öğrenci bilgi sisteminden ders kaydını yapabilirsiniz. Danışman onay süreci için, ders kaydı yaptıktan sonra danışmanınıza onay için başvurmanız gerekir. Danışmanınız, kaydınızı onayladıktan sonra, sizin onaylanmış derslerinizi kontrol etmeniz gerekir. Eğer danışmanınıza ulaşamazsanız, bölüm başkanınıza veya Dekan/Müdürünüze durumu bildirmek suretiyle akademik takvimde belirtilen sürede danışman onayını yaptırabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
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
- **Ajan Sureleri**: registration_agent=2856ms; student_affairs_orchestrator=3130ms
- **API Sureleri**: api_total=4310ms; dispatch=3159ms; final_llm=1046ms; compose=1061ms; telemetry=11ms
- **Sure**: 4322.6 ms
- **API Response Time**: 4247.4 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Merhaba, öğrenci olarak üniversite kaydı sürecini baştan sona açıklamaya çalışacağım.

Uzun süredir bekleyen öğrenci olarak, üniversite kaydını yaptıktan sonra ilk yapmanız gereken şey akademik takvimde belirtilen süreler dahilinde ders kaydı yapmaktır. Bunun için ÖBS (Öğrenci Bilgi Sistemi)-e giriş yaparak ders seçimi processunu tamamlamanız gerekir. 

Ders seçimini tamamladıktan sonra danışmanınız ile iletişime geçerek onayı isteyebilirsiniz. Danışman onayı alındıktan sonra, kayıtlanmış olduğunuz dersleri kontrol etmeniz gerekir. 

Kayıt yaptığınız derslerden bazıları, danışman onayı sırasında liste dışında bırakılabileceği için, kayıt yaptığınız derslerin listesini kontrol etmeniz önemlidir. Kayıt yaptığınız bir sonraki ders için bu kontrolü tekrar yapmanız gerekebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=21673ms; student_affairs_orchestrator=22831ms
- **API Sureleri**: api_total=26440ms; dispatch=23124ms; final_llm=1053ms; compose=1140ms; telemetry=118ms
- **Sure**: 26564.5 ms
- **API Response Time**: 25312.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Özlem, üniversiteyi bırakmak istiyorsanız ilgili işlemleri başlatabilirsiniz.

Öncelikle, UBYS üzerinden "İlişik Kesme Talebinde Bulun" seçeneğinden İlişik Kesme Sürecini başlatabilirsiniz. Bu seçeneği seçtikten sonra, ilişkinizi kesmeye ilişkin adımları ve gereklilikleri görme şansına sahip olacaksınız. 

Bununla birlikte, ilişik kesme formunu doldurma ve onaylama gerekebilir. Bu formu doldurduktan sonra, öğrenim gördüğünüz birime teslim etmelisiniz. 

Kaydınızın silinmesi ile birlikte öğrencilik hakkınız sona erer. İlişik kesme sürecinin tamamlanmış olması mezun olunduğu anlamına gelmez. Mezuniyet durumunuzu E-Devlet üzerinden kontrol etmeniz gerekmektedir. 

Detaylı bilgi için, öğrenci ilişkisini kestiğiniz halde mezun olmadığınızı ve E-devlet üzerinden mezun durumunuza bakmanızı önerebiliriz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=9154ms; student_affairs_orchestrator=12101ms
- **API Sureleri**: api_total=16415ms; dispatch=12180ms; final_llm=838ms; compose=850ms; telemetry=1462ms
- **Sure**: 16477.9 ms
- **API Response Time**: 14089.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Merhaba, senin ders notlarınız sisteme girmemiş. Sorunuzun cevabına göz atmak için elimden geleni yapacağım.

Ders notlarınızı sisteme girmemiş olan öğretim elemanınıza ulaşarak durumunuzu bildirmelisiniz. Eğer öğretim elemanınıza ulaşamadığınız takdirde, ÖİDB (Öğrenci İşleri Departmanı) Ders Kayıt ve Not İşlemleri Ofisi Sorumlusuna başvuruda bulunabilirsiniz. Ayrıca, oidb@omu.edu.tr adresine de e-posta yoluyla durumunuzu iletebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
