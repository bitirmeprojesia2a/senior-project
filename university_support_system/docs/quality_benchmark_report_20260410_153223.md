# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:32:23
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 0.0% |
| Anahtar Bilgi Kapsami | 80.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 1515.6 ms |
| Medyan Sure | 1515.6 ms |
| Intent Analizi Aktif | 0/1 |
| Force LLM Sentez | 0/1 |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | YANLIS (vt) | 4/5 | 1515.6 | - |

## Soru Detaylari

### Q7: Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra ders kaydını nasıl yapacağım, danışmanın onay süreci nasıl işliyor?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: vt (beklenen: llm) - YANLIS
- **Key Facts**: 4/5
  - [x] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Sure**: 1515.6 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Ders kaydınızı nasıl yapacağınızı ve danışmanınızın onay sürecini anlayamadıysanız, şu adımları takip edin:

Ders kaydı için, kayıt yenileme döneminde harç ücretinizi yatırdıktan sonra Veritabanındaki en yakın kayıt dönemi için tarih aralığını kontrol edin. Öğrenci İşleri departmanı verdiğiniz bilgilere göre 2026-2026-Güz dönemi için 26 Ağustos -6 Eylül 2026 tarihleri arasında planlanmıştır.

Ögrenci Turunuzu ve biriminizi belirledikten sonra, Finans departmasından öğrenim ücreti bilgisini alın. Eğer öğrenci turunuza ve bölüm bilgilerini paylaşmanız gerekiyorsa, Finans departmanı size göre öğrenim ücreti ile ilgili bilgi verecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: VT
- Finans: Kural

Kaynak Ozeti:
- Veritabani kaydi: kayit donemi
```
