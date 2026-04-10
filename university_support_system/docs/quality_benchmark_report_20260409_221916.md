# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-09 22:19:16
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 0.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 100.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 2455.7 ms |
| Medyan Sure | 2455.7 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | YANLIS | OK | 3/3 | 2455.7 | - |

## Soru Detaylari

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['finance', 'academic_programs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] ücret
  - [x] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2455.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi yatırmak ve ikamet izni için hangi belgeleri hazırlamalıyım?

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı. Öğrenim ücretimi yatırmak ve ikamet izni için gerekli belgeleri hazırlaması gerekenler, Öğrenim İşleri Birimi'ne başvurmak suretiyle bilgi alabilirler.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
```
