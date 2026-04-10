# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:35:01
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 0.0% |
| Uretim Modu Dogrulugu | 0.0% |
| Anahtar Bilgi Kapsami | 0.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 1262.3 ms |
| Medyan Sure | 1262.3 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | YANLIS | YANLIS (vt) | 0/4 | 1262.3 | - |

## Soru Detaylari

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: vt (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] öğrenim ücreti
  - [ ] gerek yok
  - [ ] yönetim kurulu
  - [ ] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 1262.3 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Veritabanindaki en yakin kayit donemi 2026-Guz icin 26.08.2026 - 06.09.2026 tarihleri arasinda planlanmistir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- VT

Kaynak Ozeti:
- Veritabani kaydi: kayit donemi
```
