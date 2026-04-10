# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:37:58
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 25.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 1692.1 ms |
| Medyan Sure | 1692.1 ms |
| Intent Analizi Aktif | 0/1 |
| Force LLM Sentez | 0/1 |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 1/4 | 1692.1 | - |

## Soru Detaylari

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [x] itiraz
  - [ ] beş iş günü
  - [ ] dilekçe
  - [ ] bölüm başkanlığı
- **Sure**: 1692.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Sınav notuna itiraz etmek istiyor ve süreci, süresi ve olası sonuçlarına ilişkin bilgiye sahip olmak istiyorsun. 

Sınav notuma itiraz etmek isteyen öğrenciler, yüzde on hesaplamaları ilan edildikten sonra 15 gün içerisinde fakülte/yüksekokuluna yazılı olarak başvurabilirler. Yapılan başvurular 15 gün içerisinde birim yönetim kurulunca karara bağlanır.

İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz. Ayrıca, itiraz edilen öğrenci tarafından başvuru formunda öğrencinin imzası gerekmektedir. 

İtiraz sürecinin tamamlanması 15 iş günü sürebilir ve yönetim kurulu tarafından en geç 15 iş gün içerisinde karar verilir. Karar kesindir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ders_yeterlilik_sınavı_uygulama_yönergesi.pdf
- Belge: yüzde_on_başarı_değerlendirme_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
