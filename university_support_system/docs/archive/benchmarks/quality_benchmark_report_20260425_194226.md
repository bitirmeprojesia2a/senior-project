# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 19:42:26
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 60.0% |
| Anahtar Bilgi Kapsami | 41.2% |
| Temiz Kalite Orani | 80.0% |
| Ortalama Sure | 15842.6 ms |
| Medyan Sure | 4682.9 ms |
| Intent Analizi Aktif | 5/5 |
| Force LLM Sentez | 4/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 4 |

## A2A Diagnostics Delta

- Overview delta: queries=0, query_failures=0, agent_tasks=0, agent_task_failures=4

| Agent | Role | Task Delta | Failed Delta | Last Error |
|-------|------|------------|--------------|------------|
| registration_agent | specialist_agent | 0 | 1 | a2a_specialist_transport_failed |
| student_affairs_orchestrator | department_orchestrator | 1 | 1 | a2a_specialist_transport_failed |
| academic_programs_orchestrator | department_orchestrator | 1 | 1 | a2a_specialist_transport_failed |
| curriculum_agent | specialist_agent | 0 | 1 | a2a_specialist_transport_failed |

Recent failure samples:
- `academic_programs_orchestrator`: a2a_specialist_transport_failed - Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?
- `student_affairs_orchestrator`: a2a_specialist_transport_failed - Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?
- `registration_agent`: a2a_specialist_transport_failed - Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?
- `curriculum_agent`: a2a_specialist_transport_failed - Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | YANLIS (kural) | 0/4 | 61495.7 | a2a_transport_fallback |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 2/4 | 5855.5 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 4/5 | 4682.9 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 3189.7 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 3989.0 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [ ] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: student_affairs_orchestrator=60306ms; academic_programs_orchestrator=60300ms
- **API Sureleri**: api_total=61484ms; dispatch=60453ms; compose=12ms; telemetry=14ms
- **Sure**: 61495.7 ms
- **API Response Time**: 61385.4 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: a2a_transport_fallback

**Yanit:**
```
Ogrenci Isleri:
Kayit Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Akademik Programlar:
Curriculum Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Uretim Turu:
- Ogrenci Isleri: Kural
- Akademik Programlar: Kural

Kaynak Ozeti:
- Veritabani kaydi: ogrenci isleri
```

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] öğrenim ücreti
  - [x] gerek yok
  - [ ] yönetim kurulu
  - [ ] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2710ms; student_affairs_orchestrator=4251ms; tuition_agent=38ms; finance_orchestrator=352ms
- **API Sureleri**: api_total=5833ms; dispatch=4347ms; final_llm=1312ms; compose=1362ms; telemetry=20ms
- **Sure**: 5855.5 ms
- **API Response Time**: 5754.9 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Kayıt dondurmak istediğiniz dönemde harç ücretini yatırmak zorunda değilsiniz. Kayıt dondurduğunuz süre eğitim sürenizden sayılır. weiber

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
- **Key Facts**: 4/5
  - [x] UBYS
  - [x] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=4487ms; student_affairs_orchestrator=4541ms
- **API Sureleri**: api_total=4659ms; dispatch=4563ms; compose=9ms; telemetry=11ms
- **Sure**: 4682.9 ms
- **API Response Time**: 4596.1 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
İlk kez üniversite kaydını yapan bir öğrenci, akademik takvimde belirtilen sürelerde "Öğrenci Bilgi Sistemi" üzerinden ders kaydını yapar. Ders seçimini tamamladığında, akademik danışmanıyla iletişime geçerek ders seçimini onaylatır. Studentin ders kaydı yapması requiredir ve akademik danışmanının onayı olmadan ders kayıtları geçersizdir.

Öğrenci, başarısız olduğu ve alamadığı alt dönem derslerini öncelikle seçmelidir. Ayrıca, öğrencinin GANO'suna göre belirli bir AKTS sınırı vardır. Öğrenci, akademik takvimde belirtilen süre içerisinde ders kaydını yaptıktan sonra, danışman onayını almak zorundadır. Danışman onayı için öğrenci, öğrenci bilgi yönetim sistemi üzerinden internet ortamında ders kaydını yapan öğrenci, danışman onayına sistem üzerinden gönderebilmektedir.

Eğer öğrenci danışmanına ulaşamazsa, bölüm başkanına veya Dekan/Müdürüne durumu bildirmelidir. Ayrıca, oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz.

Danışman onayı yapıldıktan sonra, öğrenci kayıt etmiş olduğu dersleri tek tek kontrol etmelidir. Öğrencinin danışman onayına göndermiş olduğu derslerden bir veya birkaçı danışman tarafından listeden çıkartılmış olabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
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
- **Ajan Sureleri**: registration_agent=2958ms; student_affairs_orchestrator=3027ms
- **API Sureleri**: api_total=3158ms; dispatch=3047ms; compose=4ms; telemetry=9ms
- **Sure**: 3189.7 ms
- **API Response Time**: 3078.4 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Sınava giren öğrenciye cep telefonu ile herhangi bir şekilde ilgilenmesi durumunda kopya muamelesi yapılacakdır. Kopya çekmenin cezası hakkında especifik bir bilgi bulunmuyor, ancak disiplin süreçlerinin Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre işlediği belirtiliyor.

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
- **Key Facts**: 1/4
  - [ ] kayıt
  - [ ] yenileme
  - [x] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=3304ms; student_affairs_orchestrator=3831ms
- **API Sureleri**: api_total=3974ms; dispatch=3855ms; compose=7ms; telemetry=33ms
- **Sure**: 3989.0 ms
- **API Response Time**: 3877.1 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Okulunuzu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini akademik takvimde belirtilen sürelerde Öğrenci Bilgi Sistemi üzerinden yapacaksınız ve ders seçimini tamamladığınızda akademik danışmanıyla iletişime geçerek ders seçimini onaylatacaksınız. Ders kaydınızı yaparken öncelikle başarısız olduğunuz ve alamadığınız alt dönem derslerini alacaksınız. AKTS kredileri toplamınız GANO'nuzun seviyesine göre değişecek; GANO'su 1,80-2,49 arası olan öğrenciler için

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
