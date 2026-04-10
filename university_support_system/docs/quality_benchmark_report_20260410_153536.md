# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:35:36
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 75.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 2957.3 ms |
| Medyan Sure | 2957.3 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 3/4 | 2957.3 | - |

## Soru Detaylari

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] transkript
  - [x] Ek Madde
  - [ ] başvuru yapabilir
  - [x] GANO
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=factual
- **Sure**: 2957.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

Elimdeki kaynaklar, transkriptin bulunmaması durumunda Ek Madde-1 kapsamında merkezi yerleştirme puanı ile yatay geçiş başvurusu yapılabileceğini söylüyor. Bu durum, Ek Madde-1 kapsamında yapılan yatay geçiş başvurularında öğrencinin GANO'su değerlendirme aşamasında etkili değildir (Kaynak 3: sık_sorulan_sorular.txt). Bu nedenle, transkriptin yok olmasını engellemeyeceğinizden, Ek Madde-1'i kullanarak başka bir üniversiteye yatay geçiş yapabilirsiniz.

Ancak, Ek Madde-1'i kullanabilmek için, Ek Madde-1 (Merkezi Yerleşme Puanı) başvurusu için ÖSYS/YKS ile yerleşenler Başvuru modülünde 1. Grubu, DGS ile yerleşenler 2. Grubu seçerek tercih yapacaklardır (Kaynak 2: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf). 

Bu durumda, Ek Madde-1'i kullanarak başka bir üniversiteye yatay geçiş yapabilmek için ÖSYS/YKS ile yerleşmeniz veya DGS ile yerleşmeniz gerekecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: sık_sorulan_sorular.txt
```
