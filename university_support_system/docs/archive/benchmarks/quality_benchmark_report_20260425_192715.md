# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 19:27:15
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 20.0% |
| Anahtar Bilgi Kapsami | 11.8% |
| Temiz Kalite Orani | 0.0% |
| Ortalama Sure | 4866.6 ms |
| Medyan Sure | 2307.8 ms |
| Intent Analizi Aktif | 5/5 |
| Force LLM Sentez | 4/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 12 |

## A2A Diagnostics Delta

- Overview delta: queries=5, query_failures=0, agent_tasks=14, agent_task_failures=12

| Agent | Role | Task Delta | Failed Delta | Last Error |
|-------|------|------------|--------------|------------|
| registration_agent | specialist_agent | 5 | 5 | a2a_specialist_transport_failed |
| student_affairs_orchestrator | department_orchestrator | 5 | 5 | a2a_specialist_transport_failed |
| academic_programs_orchestrator | department_orchestrator | 1 | 1 | a2a_specialist_transport_failed |
| curriculum_agent | specialist_agent | 1 | 1 | a2a_specialist_transport_failed |

Recent failure samples:
- `student_affairs_orchestrator`: a2a_specialist_transport_failed - Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?
- `registration_agent`: a2a_specialist_transport_failed - Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?
- `student_affairs_orchestrator`: a2a_specialist_transport_failed - Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?
- `registration_agent`: a2a_specialist_transport_failed - Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?
- `student_affairs_orchestrator`: a2a_specialist_transport_failed - İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | YANLIS (kural) | 0/4 | 14622.9 | a2a_transport_fallback |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | YANLIS (vt) | 1/4 | 1883.0 | a2a_transport_fallback |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | YANLIS (kural) | 0/5 | 3316.9 | a2a_transport_fallback |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | OK | 0/0 | 2307.8 | a2a_transport_fallback |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | YANLIS (kural) | 1/4 | 2202.4 | a2a_transport_fallback |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [ ] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: academic_programs_orchestrator=6210ms; student_affairs_orchestrator=6190ms
- **API Sureleri**: api_total=14618ms; dispatch=6298ms; compose=2ms; telemetry=10ms
- **Sure**: 14622.9 ms
- **API Response Time**: 14556.1 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: a2a_transport_fallback

**Yanit:**
```
Ogrenci Isleri:
Kayit Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Akademik Programlar:
Curriculum Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Uretim Turu:
- Akademik Programlar: Kural
- Ogrenci Isleri: Kural

Kaynak Ozeti:
- Veritabani kaydi: ogrenci isleri
```

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: vt (beklenen: llm) - YANLIS
- **Key Facts**: 1/4
  - [x] öğrenim ücreti
  - [ ] gerek yok
  - [ ] yönetim kurulu
  - [ ] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **Ajan Sureleri**: student_affairs_orchestrator=1728ms; tuition_agent=6ms; finance_orchestrator=101ms
- **API Sureleri**: api_total=1872ms; dispatch=1769ms; compose=4ms; telemetry=9ms
- **Sure**: 1883.0 ms
- **API Response Time**: 1822.4 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: a2a_transport_fallback

**Yanit:**
```
Ogrenci Isleri:
Kayit Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Finans:
Ogrenim ucreti icin Turk ogrenci / Mühendislik Fakültesi bilgisi veritabaninda kayitli. Yillik ucret: 2.397,00 TL. Donemlik ucret: 1.198,50 TL.

(Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf)

Uretim Turu:
- Ogrenci Isleri: Kural
- Finans: VT

Kaynak Ozeti:
- Veritabani kaydi: ogrenci isleri
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/5
  - [ ] UBYS
  - [ ] ders seçimi
  - [ ] danışman
  - [ ] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Ajan Sureleri**: student_affairs_orchestrator=3181ms
- **API Sureleri**: api_total=3304ms; dispatch=3201ms; compose=2ms; telemetry=11ms
- **Sure**: 3316.9 ms
- **API Response Time**: 3253.8 ms
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
- **Ajan Sureleri**: student_affairs_orchestrator=2179ms
- **API Sureleri**: api_total=2298ms; dispatch=2200ms; compose=2ms; telemetry=9ms
- **Sure**: 2307.8 ms
- **API Response Time**: 2255.2 ms
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

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 1/4
  - [x] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **Ajan Sureleri**: student_affairs_orchestrator=2084ms
- **API Sureleri**: api_total=2194ms; dispatch=2101ms; compose=1ms; telemetry=9ms
- **Sure**: 2202.4 ms
- **API Response Time**: 2153.3 ms
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
