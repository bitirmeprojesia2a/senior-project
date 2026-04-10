# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-09 22:15:54
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 75.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 2541.4 ms |
| Medyan Sure | 2541.4 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 2541.4 | - |

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
- **Sure**: 2541.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sorunuz: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

Belge Bağlamında yer alan bilgiyi kullanacak olan cevabı veriyorum:

Kayıt dondurma ve kayıt yaptırmamak arasında temel fark, öğrencinin öğrenimine devam etme durumundadır. Kayıt dondurma, bir öğrencinin öğrenimine devam etme haklarını dondurur, ancak kaydını silmez. Kayıt dondurulursa, öğrencinin kaydında değişiklik olmadığına, ancak öğrenimine devam etme hakkı dondurulduğuna dair bir kayıt düşülür. Aksine, kayıt yaptırmamak ise öğrencinin öğrenimine devam etme haklarının kaybolmasına neden olur.

Kayıt yaptırmayan bir öğrenci, kayıt yaptırmadığı dönem için öğrenim süresinden sorumlu tutulur ve kayıtları, mazeretlerinin haklı ve geçerli olduğu takdirde ilgili birimler tarafından kabul edilerek, akademik takvimde belirtilen süre içinde yapılır.

Bu konuda elimdeki kaynaklarda net bilgi bulunmamaktadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
