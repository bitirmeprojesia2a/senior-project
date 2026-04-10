# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-09 22:16:59
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 0.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 40.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 11807.0 ms |
| Medyan Sure | 11807.0 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | YANLIS | OK | 2/5 | 11807.0 | - |

## Soru Detaylari

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 11807.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar

Kurum içi yatay geçiş, aynı yükseköğretim kurumunun içinde yer alan programlar arasında yapılan geçişlerdir. Bu tip geçişler, ilgili yükseköğretim kurumunun belirlediği kurallar çerçevesinde realizado olur. Öte yandan, kurumlar arası yatay geçiş, farklı yükseköğretim kurumlarının arasında yapılan geçişlerdir. Bu tür geçişler, Yükseköğretim Kurulu düzenlemeleri çerçevesinde realizado olunur.

Başvuru Şartları ve Değerlendirme Kriterleri
- Kurum içi Yatay Geçiş: 
 - Genel not ortalaması 2,50'den üst olmalıdır.
 - OMÜ-YÖS Sınavının herhangi bir puan türünden en az 50 puan almış ya da üniversite tarafından kabul edilen diğer sınavlardan en az 50 puan almış olmalıdır.
 - Öğrencinin geçmek istediği diploma programına eşdeğer olan merkezi yerleştirme puanına sahip olması gerekir.

- Kurumlar Arası Yatay Geçiş: 
 - OMÜ-YÖS Sınavının herhangi bir puan türünden en az 50 puan almış olmalıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
```
