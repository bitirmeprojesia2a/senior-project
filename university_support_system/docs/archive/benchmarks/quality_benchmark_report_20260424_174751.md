# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 17:47:51
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 40.0% |
| Anahtar Bilgi Kapsami | 21.4% |
| Temiz Kalite Orani | 20.0% |
| Ortalama Sure | 1276.1 ms |
| Medyan Sure | 1160.2 ms |
| Intent Analizi Aktif | 4/5 |
| Force LLM Sentez | 4/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 10 |

## A2A Diagnostics Delta

- Overview delta: queries=5, query_failures=0, agent_tasks=12, agent_task_failures=10

| Agent | Role | Task Delta | Failed Delta | Last Error |
|-------|------|------------|--------------|------------|
| registration_agent | specialist_agent | 5 | 5 | a2a_specialist_endpoint_missing |
| student_affairs_orchestrator | department_orchestrator | 5 | 5 | a2a_specialist_endpoint_missing |

Recent failure samples:
- `student_affairs_orchestrator`: a2a_specialist_endpoint_missing - Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?
- `registration_agent`: a2a_specialist_endpoint_missing - Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?
- `student_affairs_orchestrator`: a2a_specialist_endpoint_missing - Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?
- `registration_agent`: a2a_specialist_endpoint_missing - Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?
- `student_affairs_orchestrator`: a2a_specialist_endpoint_missing - Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 3648.3 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | YANLIS (kural) | 0/4 | 187.2 | a2a_transport_fallback |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | OK | 0/0 | 180.0 | a2a_transport_fallback |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | YANLIS (kural) | 0/4 | 1160.2 | a2a_transport_fallback |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | YANLIS (kural) | 0/3 | 1204.7 | a2a_transport_fallback |

## Soru Detaylari

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
- **Ajan Sureleri**: international_agent=1550ms; academic_programs_orchestrator=2094ms; student_affairs_orchestrator=51ms; tuition_agent=7ms; finance_orchestrator=105ms
- **API Sureleri**: api_total=3639ms; dispatch=2189ms; global_llm=1273ms; compose=1317ms; telemetry=18ms
- **Sure**: 3648.3 ms
- **API Response Time**: 3575.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Öğrenim ücretinizi nereye yatırmamız gerektiği konusunda net bilgi bulunmuyor. İlgili bilgi için Üniversite'nin uluslararası öğrenci alım kılavuzuna bakabilirsiniz. Ayrıca, öğrenim ücreti ödemenin nereye yapılacağı veya ikamet izni için hangi belgelerin hazırlanması gerektiği konusunda finans birimi ile iletişime geçmeniz öneriliyor.

- Öğrenim ücreti ödenmesi konusunda finans birimi ile iletişime geçmeniz gerekir.
- İkamet izni için gereken belgeler hakkında bilgi bulunamadı.
- Üniversite'nin uluslararası öğrenci alım kılavuzuna bakarak daha fazla bilgi edinebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: Kural
- Finans: VT

Kaynak Ozeti:
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
- Belge: ön_lisans_ve_lisans_programları.pdf
- Veritabani kaydi: ogrenci isleri
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] itiraz
  - [ ] beş iş günü
  - [ ] dilekçe
  - [ ] bölüm başkanlığı
- **Ajan Sureleri**: student_affairs_orchestrator=33ms
- **API Sureleri**: api_total=163ms; dispatch=51ms; compose=1ms; telemetry=10ms
- **Sure**: 187.2 ms
- **API Response Time**: 107.5 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: a2a_transport_fallback

**Yanit:**
```
Kayit Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Uretim Turu:
- Kural

Kaynak Ozeti:
- Veritabani kaydi: ogrenci isleri
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: kural) - OK
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Ajan Sureleri**: student_affairs_orchestrator=32ms
- **API Sureleri**: api_total=170ms; dispatch=51ms; compose=2ms; telemetry=10ms
- **Sure**: 180.0 ms
- **API Response Time**: 114.0 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: a2a_transport_fallback

**Yanit:**
```
Kayit Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Uretim Turu:
- Kural

Kaynak Ozeti:
- Veritabani kaydi: ogrenci isleri
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [ ] birim
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: student_affairs_orchestrator=42ms
- **API Sureleri**: api_total=1150ms; dispatch=70ms; compose=1ms; telemetry=9ms
- **Sure**: 1160.2 ms
- **API Response Time**: 1102.2 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: a2a_transport_fallback

**Yanit:**
```
Kayit Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Uretim Turu:
- Kural

Kaynak Ozeti:
- Veritabani kaydi: ogrenci isleri
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/3
  - [ ] danışman
  - [ ] bölüm
  - [ ] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: student_affairs_orchestrator=46ms
- **API Sureleri**: api_total=1189ms; dispatch=78ms; compose=1ms; telemetry=8ms
- **Sure**: 1204.7 ms
- **API Response Time**: 1128.1 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: a2a_transport_fallback

**Yanit:**
```
Kayit Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Uretim Turu:
- Kural

Kaynak Ozeti:
- Veritabani kaydi: ogrenci isleri
```
