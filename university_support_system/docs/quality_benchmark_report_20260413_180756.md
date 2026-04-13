# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-13 18:07:56
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 33.3% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 2521.9 ms |
| Medyan Sure | 2521.9 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 2/6 | 2521.9 | - |

## Soru Detaylari

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/6
  - [ ] ders
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [x] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2521.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Mezuniyet için gerekli koşulları ve ilişik kesme sürecini adım adım açıklamak mümkün değil. Çünkü verilen belge bağlamında bu konuda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
```
