# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 19:34:57
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 0.0% |
| Anahtar Bilgi Kapsami | 0.0% |
| Temiz Kalite Orani | 0.0% |
| Ortalama Sure | 54111.2 ms |
| Medyan Sure | 54111.2 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 2 |

## A2A Diagnostics Delta

- Overview delta: queries=1, query_failures=0, agent_tasks=2, agent_task_failures=2

| Agent | Role | Task Delta | Failed Delta | Last Error |
|-------|------|------------|--------------|------------|
| registration_agent | specialist_agent | 1 | 1 | a2a_specialist_transport_failed |
| student_affairs_orchestrator | department_orchestrator | 1 | 1 | a2a_specialist_transport_failed |

Recent failure samples:
- `student_affairs_orchestrator`: a2a_specialist_transport_failed - İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?
- `registration_agent`: a2a_specialist_transport_failed - İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | YANLIS (kural) | 0/5 | 54111.2 | a2a_transport_fallback |

## Soru Detaylari

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
- **Ajan Sureleri**: student_affairs_orchestrator=53822ms
- **API Sureleri**: api_total=54104ms; dispatch=53914ms; compose=9ms; telemetry=10ms
- **Sure**: 54111.2 ms
- **API Response Time**: 54004.0 ms
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
