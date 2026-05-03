# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 18:31:21
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 71.4% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3708.1 ms |
| Medyan Sure | 3550.1 ms |
| Intent Analizi Aktif | 5/5 |
| Force LLM Sentez | 5/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=5, query_failures=0, agent_tasks=8, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 4322.9 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 3936.8 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 3347.8 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 3550.1 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 3/3 | 3382.7 | - |

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1938ms; student_affairs_orchestrator=2002ms; curriculum_agent=1932ms; academic_programs_orchestrator=1991ms
- **API Sureleri**: api_total=4312ms; dispatch=2045ms; final_llm=1109ms; compose=1192ms; telemetry=18ms
- **Sure**: 4322.9 ms
- **API Response Time**: 4237.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kaydınızı yaptırdıktan sonra muafiyet başvurusu yapabilirsiniz. Karar çıkana kadar derslere devam etmeniz önemlidir. Birim Yönetim Kurulu’nun muafiyet talebini uygun görmesi ve muaf olunan derslerin sisteme işlenmesi sonrasında, danışman ile birlikte almanız gereken derslere kaydınız yapılır. Magdur olmamanız için dönem derslerine devam etmeniz önemlidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
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
- **Ajan Sureleri**: registration_agent=2261ms; student_affairs_orchestrator=2338ms; tuition_agent=8ms; finance_orchestrator=68ms
- **API Sureleri**: api_total=3927ms; dispatch=2378ms; final_llm=1450ms; compose=1484ms; telemetry=12ms
- **Sure**: 3936.8 ms
- **API Response Time**: 3880.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Harç ücretini yatırdıktan sonra, akademik takvimde belirlenen süre içinde ders kaydını yapmanız gerekmektedir. Ders kaydında öncelikle başarısız olduğunuz ve alamadıkları alt dönem derslerini dikkate almanız gerekir. GANO'nuzun durumuna göre AKTS kredileri toplamı 6, 10, 12 veya 15 olabilir. Danışman onay süreci için, ders kaydını tamamladıktan sonra danışmanınıza başvurmanız ve onayını almanız gerekmektedir. Danışmanınıza ulaşılamazsa, bölüm başkanınıza veya Dekan/Müdürünüze durumu bildirebilirsiniz. 
Aşağıdaki durumlar için ayrıca dikkat etmeniz gerekenler:
- Başarısız olduğunuz ve alamadıkları alt dönem derslerini dikkate almanız gerekir.
- GANO'nuzun durumuna göre AKTS kredileri toplamını belirleyebilirsiniz.
- Danışman onayını aldıktan sonra ders kaydınız tamamlanmış blir.

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
- **Ajan Sureleri**: registration_agent=2057ms; student_affairs_orchestrator=2114ms
- **API Sureleri**: api_total=3333ms; dispatch=2134ms; final_llm=1105ms; compose=1120ms; telemetry=19ms
- **Sure**: 3347.8 ms
- **API Response Time**: 3270.8 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Merhaba, ilk kez üniversite kaydını yaptıran bir öğrencisin. İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışman onayına kadar tüm süreci anlatacak olurum.

İlk olarak, Öğrenci Bilgi Sistemi üzerinden akademik takvimde belirtilen sürelerde ders kaydınızı yapmalısınız. Derse kayıt yaptıktan sonra, akademik takvimde belirtilen süreler içinde ders seçimi onaylatmak için akademik danışmanınızla iletişim kurmalısınız. 

Ders kaydı yaptıktan sonra danışman onayını sistem üzerinden gönderebilirsiniz. Danışman onayına sistemin üzerinden gitmeniz gerekirken danışmanın size gelmesi zorunluluğu bulunmamaktadır. 

Anıtlarını gönderdikten sonra onayı almazsanız, danışmanınıza ulaşıp onay alamıyorsanız, bölüm başkanınıza ulaşın. 

Dekan/Müdürüne ulaşılamıyorsa da durumunuzu oidb@omu.edu.tr adresine ilgili odeme kanali ile belirtmeniz gerekir.

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
- **Ajan Sureleri**: registration_agent=1587ms; student_affairs_orchestrator=1661ms
- **API Sureleri**: api_total=3527ms; dispatch=1682ms; final_llm=946ms; compose=963ms; telemetry=16ms
- **Sure**: 3550.1 ms
- **API Response Time**: 3462.5 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Siz üniversiteyi bırakıp ayrılmak istediğinizi söylediniz. İlk olarak, Önlisans ve Lisans Kayıt Sorgulama Sistemi (UBYS) üzerinden "İlişik Kesme Talebinde Bulun" seçeneği aracılığıyla ilişik kesme sürecini başlatabilirsiniz. Ayrıca, şahsen başvurarak ilişik kesme formunu doldurup belirtilen merkezlerde onaylattıktan sonra öğrenim gördüğünüz birime teslim edebilirsiniz. İlişik kesme sürecinin tamamlanması, mezun olunduğu anlamına gelmez; mezuniyet ve diploma basım işlemlerinin başlatılması için yapılır.

Birkaç hususa dikkat etmeniz gerekiyor: 

- Mezuniyet durumunuzu E-Devlet üzerinden kontrol etmeniz önerilir.
- Kaydınızın silinmesiyle birlikte öğrencilik hakkınız sona erecektir.
- İlişik kesme formunu doldurmakta ve gerekli onayları almakecta zorlanmayacağını belirtmek gerekir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1498ms; student_affairs_orchestrator=1590ms
- **API Sureleri**: api_total=3360ms; dispatch=1619ms; final_llm=884ms; compose=902ms; telemetry=25ms
- **Sure**: 3382.7 ms
- **API Response Time**: 3289.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Ders notlarınızı sisteme girmemiş durumunuzdan bahsettiniz, bu konudaki en hızlı çözüm danışmanınıza ulaşarak derstenizi sisteme girilmesini istemektir. Eğer danışmanınıza ulaşamazsanız, bölüm başkanınıza ya da Dekan/Müdüre durumu bildirebilirsiniz. Son olarak, herhangi bir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine e-posta yoluyla sorununuzu iletebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
