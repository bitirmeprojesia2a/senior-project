# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-13 18:03:26
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 0.0% |
| Anahtar Bilgi Kapsami | 16.7% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 2947.1 ms |
| Medyan Sure | 2947.1 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | YANLIS (kural) | 1/6 | 2947.1 | - |

## Soru Detaylari

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 1/6
  - [ ] ders
  - [x] staj
  - [ ] GANO
  - [ ] 2,00
  - [ ] ilişik kesme
  - [ ] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2947.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Kural

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
```
