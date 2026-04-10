# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-09 22:36:23
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 75.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3024.1 ms |
| Medyan Sure | 3024.1 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 3024.1 | - |

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
- **Sure**: 3024.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Soru:
Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

Cevap:
Kayıt dondurma ve kayıt yaptırmamak arasındaki temel fark, öğrencinin öğrenimine devam edebilmesi ve öğrencilik haklarının etkilenmesi açısından farklılık göstermektedir.

Kayıt dondurma durumunda, öğrenci ders kaydını yapmamış olsa da, kayıtlı olduğu üniversitede öğrenimine devam edebilir. Ancak, öğrencinin öğrenim süresi uzayacaktır.

Kayıt yaptırmamak durumunda, öğrenci akademik takvimde belirlenen süre içinde ders kaydını yapmayan students, o dönemde öğrenimlerine devam etme hakkı kaybederler. Bu durum, öğrenim süresinin uzamasına neden olunur, ancak öğrenci kayıt yaptırarak, bu haklarını geri kazanabilirler.

Öğrencilik haklarınız etkilenmesiyle ilgili olarak; kayıt dondurma durumu, öğrencinin akademik takvimde belirlenen süreler içinde eğitimine devam etmesine ve öğrenim hakkını kaybetmesine neden olmazken, kayıt yaptırmamak durumu öğrencinin o dönemde öğrenim haklarını kaybetmesine neden olabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
