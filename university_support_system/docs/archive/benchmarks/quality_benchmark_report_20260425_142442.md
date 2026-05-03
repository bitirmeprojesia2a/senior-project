# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 14:24:42
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 61.9% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 15653.7 ms |
| Medyan Sure | 4186.1 ms |
| Intent Analizi Aktif | 5/5 |
| Force LLM Sentez | 5/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 4 |

## A2A Diagnostics Delta

- Overview delta: queries=5, query_failures=0, agent_tasks=12, agent_task_failures=4

| Agent | Role | Task Delta | Failed Delta | Last Error |
|-------|------|------------|--------------|------------|
| student_affairs_orchestrator | department_orchestrator | 1 | 1 | a2a_specialist_transport_failed |
| academic_programs_orchestrator | department_orchestrator | 1 | 1 | a2a_specialist_transport_failed |
| registration_agent | specialist_agent | 6 | 1 | a2a_specialist_transport_failed |
| curriculum_agent | specialist_agent | 1 | 1 | a2a_specialist_transport_failed |

Recent failure samples:
- `academic_programs_orchestrator`: a2a_specialist_transport_failed - Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?
- `curriculum_agent`: a2a_specialist_transport_failed - Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?
- `student_affairs_orchestrator`: a2a_specialist_transport_failed - Yatay gecis sonrasi muafiyet basvurusu ne zaman yapilir ve karar cikana kadar derslere devam gerekir mi?
- `registration_agent`: a2a_specialist_transport_failed - Yatay gecis sonrasi muafiyet basvurusu ne zaman yapilir ve karar cikana kadar derslere devam gerekir mi?

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 62315.1 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 4625.2 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 3560.4 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 4186.1 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 1/3 | 3581.8 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [x] dilekçe
  - [ ] komisyon
  - [ ] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1279ms; student_affairs_orchestrator=1565ms; academic_programs_orchestrator=60358ms
- **API Sureleri**: api_total=62313ms; dispatch=60446ms; final_llm=782ms; compose=894ms; telemetry=7ms
- **Sure**: 62315.1 ms
- **API Response Time**: 62261.0 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu Dekanlığa/Müdürlüğe dilekçe vererek yapmalıdır. Muafiyet kararının alınması processo, ders kayıt işleminin yerine getirilmesinden önce gerçekleşeceğinden, mağdur olmamanız için dönem derslerine devam etmeniz önemlidir. Muafiyet kararının alınması sürecinden sonra, danışmanınız ile birlikte alacak olduğunuz derslere kaydınız yapılacaktır. 

Bu süreçte muafiyete ilişkin karara göre işlem yapılacaktır, yani muafiyet kararı çıktıktan sonra sizin için uygun olan derslerin sistem içine işlenmesi sonrasında kaydı yaptırılabilecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: Kural

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
- **Ajan Sureleri**: registration_agent=3440ms; student_affairs_orchestrator=3553ms; tuition_agent=293ms; finance_orchestrator=1084ms
- **API Sureleri**: api_total=4613ms; dispatch=3631ms; final_llm=884ms; compose=900ms; telemetry=22ms
- **Sure**: 4625.2 ms
- **API Response Time**: 4554.8 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, akademik takvimde belirlenen süre içerisinde öğrenci bilgi sistemine girerek ders kaydınızı yapabilirsiniz. Ders kaydınızı yaptıktan sonra, danışmanınıza onay için göndermeniz gerekmektedir. Danışman onay süreci tamamlandıktan sonra, kayıtlanmış olduğunuz dersleri kontrol ediniz. Danışmanınız tarafından listeden çıkartılmış dersler olabilir. Ayrıca, her kayıt döneminde başarılı olduğunuz dersleri müfredatınızla karşılaştırmanız ve başarılı olduğunuz dersleri kontrol etmeniz gerekmektedir.

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
- **Ajan Sureleri**: registration_agent=2283ms; student_affairs_orchestrator=2352ms
- **API Sureleri**: api_total=3538ms; dispatch=2374ms; final_llm=1058ms; compose=1086ms; telemetry=16ms
- **Sure**: 3560.4 ms
- **API Response Time**: 3484.9 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Merhaba, öğrenci. İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışman onayına kadar tüm süreci açıklamayı ister misiniz? 

İlk olarak, akademik takvimde belirtilen süreler içerisinde öğrenci bilgi sistemi üzerinden ders kaydınızı yapmalısınız. Öğrenciler, öncelikle başarısız oldukları ve alamadıkları alt dönem derslerini seçmelidirler. GANO'su ile ilgili tutarı hesab etmek için öğrencinin GANO'sunu 1,80-2,49, 2,50-2,99, 3,00-3,49 veya 3,50 ve üzeri arası aralarındaki bir seviyeye sahip olması gerekir. Bu seviyelere göre, 6, 10, 12 veya 15 AKTS tutarına göre ders miktarı artırılabilir. Ardışık dersler için danışman onayı gereklidir. 

Gerektiğinde öğrenciler danışmanlarıyla iletişime geçerek ders seçimi onaylatabilirler. Bilgi bulunabilir, lütfen öğrenciniz akademik takvimde belirtilen süreler içerisinde kayıt tamamlandıktan sonra, danışman onayı sürecini takibını yapması rica ediyorum.

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
- **Ajan Sureleri**: registration_agent=1998ms; student_affairs_orchestrator=2075ms
- **API Sureleri**: api_total=4174ms; dispatch=2103ms; final_llm=1173ms; compose=1202ms; telemetry=14ms
- **Sure**: 4186.1 ms
- **API Response Time**: 4119.3 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Üniversiteyi bırakıp ayrılmak istediğinizi öğrenmektesiniz. Öncelikle, öğrencilik işlemleri ve dikkat etmeniz gereken hususları aşağıdaki gibi özetleyebiliriz:

Üniversiteyi terk etmek istiyorsanız, UBYS üzerinden "İlişik Kesme Talebinde Bulun" seçeneğini kullanarak ilişik kesme sürecini başlatabilirsiniz. Aynı zamanda, şahsen başvurarak ilişik kesme formunu doldurup belirtilen merkez onaylattıktan sonra öğrenim gördüğünüz birime teslim edebilirsiniz. Kaydınızın silinmesiyle birlikte öğrencilik hakkınız sona erer.

Önerebileceğimiz bazı adımlar:
- Şahsen başvururken, tam ad, T.C. kimlik numarası, kayıt numarası ve eğitim türünü eksiksiz girin.
- Eksik bilgi veya hata yapmamak için ilişkili kesme formunu dikkatlice doldurun.
- Form onaylandıktan sonra, öğrenim gördüğünüz üniversitenin kaydı sildirme processini tamamlamalısınız.

Bilginin onaylı olması durumunda, kaydınızı sildireceğiniz öğrenim birimi, sizden daha sonraki herhangi bir işleme dair bilgi almayacaktır.

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
  - [x] bölüm
  - [ ] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1922ms; student_affairs_orchestrator=1977ms
- **API Sureleri**: api_total=3568ms; dispatch=1997ms; final_llm=691ms; compose=700ms; telemetry=12ms
- **Sure**: 3581.8 ms
- **API Response Time**: 3525.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Ders notlarınızı sisteme girilmemiş. Öğretim elemanı ile iletişime geçilerek not girisinin tamamlanması için gerekli işlemler yapılabilir. Eğer iletişime geçilemiyorsa, bölüm başkanına veya Dekan/Müdüre durum belirtilerek yardımcı olunabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
