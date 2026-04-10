# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 16:28:24
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 75.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 14526.9 ms |
| Medyan Sure | 14526.9 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 14526.9 | - |

## Soru Detaylari

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 14526.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sorumla ilgili tüm kaynaklarda net bilgi bulunmuş olmakla beraber, soru sordugu iki durumu açıklıyorum:

Kayıt Dondurma ile Kayıt Yapmama Arasindaki Fark:

Kayıt dondurma, kayıt yapılmasının tam tersidir. Kayıt dondurulan öğrenci, öğrenimine devam edemez ve kayıt dondurduğu döneme/yıla ait sınavlara giremez. Kayıt dondurulan dönem/yıl süre hesabında dikkate alınmaz.

Kayıt yaptırmamış bir öğrenci ise öğrenimine devam edebilir ve kayıtlı olduğu üniversitede öğrenimine devam edebilir.

Her İki Duruma Daffects Eden Öğrencilik Hakları:

- Her iki durumda da öğrenci, öğrenimini uzatmamak kaydıyla öğrenimine devam edebilir.
- Kayıt dondurulan dönem/yıl süre hesabında dikkate alınmaz. Ancak, kayıt yaptırmamış bir öğrenci için geçerli değildir.
- Her iki durumda da öğrenci, kayıt dondurmaz veya kayıt yaptırmazsa ilgili yönetim kurulu kararı ile bir defada en fazla iki dönem/bir yıl olmak üzere, öğrenim süresi boyunca en fazla dört dönem/iki yıl kaydetmektedir.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
```
