# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 19:55:47
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 80.0% |
| Anahtar Bilgi Kapsami | 76.5% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 4277.5 ms |
| Medyan Sure | 2471.4 ms |
| Intent Analizi Aktif | 5/5 |
| Force LLM Sentez | 4/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=3, query_failures=0, agent_tasks=6, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 3/4 | 5522.7 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 3/4 | 9826.0 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 5/5 | 2471.4 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 1520.4 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 2046.8 | - |

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=2959ms; academic_programs_orchestrator=3118ms; registration_agent=1512ms; student_affairs_orchestrator=1666ms
- **API Sureleri**: api_total=5510ms; dispatch=3207ms; final_llm=1410ms; compose=1478ms; telemetry=9ms
- **Sure**: 5522.7 ms
- **API Response Time**: 5424.0 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Eğitim öğretimin başladığı tarihten itibaren üç hafta içinde daha önce öğrenim gördüğü yükseköğretim kurumlarında aldığı ve başarılı olduğu dersler için muaf olmak istediği dersleri içeren bir dilekçe, onaylı transkript ve onaylı ders içeriğiyle birlikte ilgili birime başvurmanız gerekir. Muafiyet başvurusu sonuçlanıncaya kadar bu derslere kayıt yaptırıp devam etmeniz önemlidir.

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

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] öğrenim ücreti
  - [x] gerek yok
  - [ ] yönetim kurulu
  - [x] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1866ms; student_affairs_orchestrator=1931ms; tuition_agent=22ms; finance_orchestrator=147ms
- **API Sureleri**: api_total=9817ms; dispatch=1972ms; final_llm=7732ms; compose=7750ms; telemetry=16ms
- **Sure**: 9826.0 ms
- **API Response Time**: 9741.3 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Kayıt dondurmak istediğiniz döneme ait katkı payı veya öğrenim ücretini ödemek zorunda değilsiniz. Kayıt dondurulan süre, azami öğrenim süresinden sayılmaz. 
Örnek bazı katkı payı ve ücretlere ilişkin bilgiler:
- Yıllik ücret: 2.397,00 TL
- Dönemlik ücret: 1.198,50 TL 

Önemli not: Bu ücretler Turk öğrenci katkı payı ve öğrenim ücretine ilişkindir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 5/5
  - [x] UBYS
  - [x] ders seçimi
  - [x] danışman
  - [x] onay
  - [x] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2238ms; student_affairs_orchestrator=2302ms
- **API Sureleri**: api_total=2454ms; dispatch=2345ms; compose=7ms; telemetry=8ms
- **Sure**: 2471.4 ms
- **API Response Time**: 2378.4 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Akademik takvimde belirtilen süre içinde öğrenci bilgi sisteminden ders kaydını yapmanız gerekir. Ders seçimini tamamladığınızda akademik danışmanınızla iletişime geçerek ders seçimini onaylatınız. Ön koşullu veya ardışıklık gerektiren dersler için danışman onayına ihtiyacınız vardır. Kayıt dönemi başlamadan önce transkript/müfredat kontrolü yaparak akademik takvimde tanımlanan süre içerisinde ders kaydını yapmanız gerektiği ve derslere başladığında sınıf yoklama listesinde adınızın olup olmadığını kontrol etmeniz önemlidir.

Ders kaydını yaptıktan sonra danışman onayına göndermelisiniz. onaylanma sürecini takip etmeniz ve danışman onayı olmadan ders kayıtlarının geçersiz olacağını unutmamalısınız. Danışman onayından emin olduktan sonra kayıtlanmış olduğunuz dersleri tek tek kontrol etmelisiniz. Danışmanınız tarafından listeden çıkartılmış dersler olabilir.

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

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1353ms; student_affairs_orchestrator=1403ms
- **API Sureleri**: api_total=1506ms; dispatch=1423ms; compose=4ms; telemetry=11ms
- **Sure**: 1520.4 ms
- **API Response Time**: 1448.5 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Sınava giren öğrencinin sınav sırasında cep telefonu ile herhangi bir şekilde ilgilenmesi durumunda kopya muamelesi yapılır. Disiplin Suçlarına İlişkin hükümler 2547 sayılı Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği'ne göre belirlenir. Bu yönetmelik hükümlerine göre kaydını sildiren öğrencilerin üniversite ile ilişiği kesilir. Ancak, kopya çekilmesinin cezası ve disiplin süreci hakkında daha spesifik bilgi bulunmamaktadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] kayıt
  - [ ] yenileme
  - [x] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1858ms; student_affairs_orchestrator=1919ms
- **API Sureleri**: api_total=2007ms; dispatch=1940ms; compose=5ms; telemetry=7ms
- **Sure**: 2046.8 ms
- **API Response Time**: 1963.4 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kayıt dondurma sonrasında ders seçimini yapmak için, akademik takvimde belirtilen sürelerde Öğrenci Bilgi Sistemi üzerinden ders kaydını yapmanız ve ders seçimini tamamladığınızda akademik danışmanınızla iletişime geçerek ders seçimini onaylatmanız gerekir. Ayrıca, başarısız olduğunuz ve alamadığınız alt dönem derslerini öncelikle almanız gerekir. AKTS kredileri toplamı, GANO'nuzun seviyesine göre 6, 10, 12 veya 15 AKTS tutarında artırılabilir. Ön koşullu veya sistematik olarak ardışıklık gerektiren dersler için danışman onayı gerekir.

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
