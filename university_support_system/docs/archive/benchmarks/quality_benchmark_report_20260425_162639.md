# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 16:26:39
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 66.7% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 4667.9 ms |
| Medyan Sure | 3291.0 ms |
| Intent Analizi Aktif | 5/5 |
| Force LLM Sentez | 5/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 2 |

## A2A Diagnostics Delta

- Overview delta: queries=5, query_failures=0, agent_tasks=9, agent_task_failures=2

| Agent | Role | Task Delta | Failed Delta | Last Error |
|-------|------|------------|--------------|------------|
| registration_agent | specialist_agent | 5 | 1 | a2a_specialist_endpoint_missing |
| student_affairs_orchestrator | department_orchestrator | 1 | 1 | a2a_specialist_endpoint_missing |

Recent failure samples:
- `student_affairs_orchestrator`: a2a_specialist_endpoint_missing - Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?
- `registration_agent`: a2a_specialist_endpoint_missing - Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 8389.2 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 5928.7 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 2/5 | 3291.0 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 3171.0 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 3/3 | 2559.5 | - |

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: student_affairs_orchestrator=36ms; curriculum_agent=6231ms; academic_programs_orchestrator=6402ms
- **API Sureleri**: api_total=8370ms; dispatch=6454ms; final_llm=476ms; compose=507ms; telemetry=27ms
- **Sure**: 8389.2 ms
- **API Response Time**: 8231.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Hocam, yatay geçiş ile gelen bir öğrenci tarafından muafiyet başvurusunu yapma ve devam etmeyle ilgili sorununuz var. 

Yatay geçiş ile gelen öğrenci, muafiyet başvurusunu yapması gereken an da öğrencinin daha önce aldığı ve başarılı olduğu derslerdir. Bu durumda öğrenci, karar çıkana kadar derslere devam etmelidir. 

Ayrıca, muafiyet talebi ilgili yönetim kurulu tarafından karara bağlanıncaya kadar öğrenciler derslere devam etmek zorundadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: ogrenci isleri
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
- **Ajan Sureleri**: registration_agent=4501ms; student_affairs_orchestrator=4673ms; tuition_agent=9ms; finance_orchestrator=58ms
- **API Sureleri**: api_total=5872ms; dispatch=4778ms; final_llm=965ms; compose=999ms; telemetry=8ms
- **Sure**: 5928.7 ms
- **API Response Time**: 5820.3 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Harç ücretini ödedikten sonra, akademik takvimde belirtilen süre içinde ders kaydınızı yapabilirsiniz. Öncelikle başarısız olduğunuz ve alamadıkları alt dönem derslerini dikkate almanız gerekir. Danışman onayı, ardışıklik gerektiren dersler için gereklidir. Ayrıca, GANO'nuzu dikkate alarak AKTS kredileri toplamını da kontrol etmelisiniz. 
- GANO'nuz 1,80-2,49 arası ise 6 AKTS,
- 2,50-2,99 arası ise 10 AKTS,
- 3,00-3,49 arası ise 12 AKTS,
- 3,50 ve üzerinde ise 15 AKTS tutarı kadar artırabilirsiniz. 
Ders kaydında, müfredat durum kontrolü, akademik takvimde belirtilen süre içinde kaydın tamamlanması ve danışman onayı işlemine dikkat etmelisiniz.

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
- **Key Facts**: 2/5
  - [ ] UBYS
  - [ ] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2348ms; student_affairs_orchestrator=2415ms
- **API Sureleri**: api_total=3271ms; dispatch=2439ms; final_llm=706ms; compose=754ms; telemetry=12ms
- **Sure**: 3291.0 ms
- **API Response Time**: 3201.9 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Selamlar. Öğrenci olarak ders kaydından danışman onayına kadar sürecin detayını öğrenmek istiyorsun. 

Bir öğrenci olarak, akademik takvimde belirtilen zamanakaret içinde öğrenci bilgi sistemine girerek ders kayıtlı yapmalısınız. Seçtiğiniz dersleri tamamladıktan sonra, akademik danışmanınızla iletişime geçerek ders seçimlerinizi onaylatmanızı gerektirir. 

Kayıt yaparken, başarısız olduğunuz ve alamadığınız alt dönem derslerini aldıktan sonra üst dönem derslerine kaydolabilirsiniz. AKTS kredileriniz toplamı; GANO'su 1,80-2,49 arası olan öğrenciler için

Ders kaydı yaptıktan sonra, akademik danışmanınıza onay için başvurmalı ve danışmanınızın onayını sistem üzerinden göndermelisiniz. Onaylanan ders kayıtlarınızın takip edilmesinden siz sorumlusunuz.

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1868ms; student_affairs_orchestrator=1929ms
- **API Sureleri**: api_total=3141ms; dispatch=1967ms; final_llm=600ms; compose=621ms; telemetry=7ms
- **Sure**: 3171.0 ms
- **API Response Time**: 3080.3 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Merhaba, üniversiteyi terk etmek için hangi adımları takip edeceğini öğrenmek istediğinizi biliyoruz. Aşağıdaki bilgilere göre işlemleri ve dikkat etmeniz gereken hususları sizin için özetledik:

Tüm işlemleri ve dikkat etmeniz gereken hususları şöyle özetleyebiliriz:

- Üniversite terk etmek ya da ayrılmak için ilişik kesme sürecini başlatın.
- UBYS'den "İlişik Kesme Talebinde Bulun" seçeneğinden ya da şahsen başvurarak ilişik kesme formunu doldurup onaylattıktan sonra öğrenim gördüğünüz birime teslim ediniz.
- Kaydınızın silinmesiyle birlikte öğrencilik hakkınız sona erecektir.

Sizden ayrıca herhangi bir ek bilginin gerekli olduğu veya dikkat edilmesi gereken hususların olup olmadığı sorulmadı.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1307ms; student_affairs_orchestrator=1380ms
- **API Sureleri**: api_total=2526ms; dispatch=1420ms; final_llm=604ms; compose=618ms; telemetry=29ms
- **Sure**: 2559.5 ms
- **API Response Time**: 2453.1 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Ders notlarınızı sisteme girmemiş olan durumunuza çözüm bulmak için, öncelikle danışmanınıza ulaşarak talepte bulunabilirsiniz. Eğer danışmanınıza ulaşamazsanız bölüm başkanınıza veya Dekan/Müdürünüze durumu bildirerek yardım alabilirsiniz. Ayrıca akademik takvimde belirtilen sürede danışman onayını muhakkak yaptırmanız gerekir. Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz.

Detay olarak:
- Danışmanınıza ulaşmak için gerekli iletişim kurunun bilinmesini rica ediyorum.
- Gerekli kişilerle iletişime geçilerek problem çözümlenmesi gerekir.

Bilgiler: 
- Takvimde belirtilen süre: Bilinmektedir.
- Danışman onayı için gerekli tarih: Bilinmemektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
