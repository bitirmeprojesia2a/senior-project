# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:36:46
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 0.0% |
| Anahtar Bilgi Kapsami | 100.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 324.2 ms |
| Medyan Sure | 324.2 ms |
| Intent Analizi Aktif | 0/1 |
| Force LLM Sentez | 0/1 |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | YANLIS (rag) | 3/3 | 324.2 | - |

## Soru Detaylari

### Q15: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 3/3
  - [x] diploma eki
  - [x] transkript
  - [x] yerine geçmez
- **Sure**: 324.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Diploma ekini transkript yerine kullanabilir miyim? Diploma eki transkript (not çizelgesi) veya diploma yerine geçmez.

(Kaynak: sık_sorulan_sorular.txt)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
```
