# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:36:15
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 50.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 6904.0 ms |
| Medyan Sure | 6904.0 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 2/4 | 6904.0 | - |

## Soru Detaylari

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] bağıl
  - [x] mutlak
  - [ ] 10
  - [ ] öğrenci sayısı
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 6904.0 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark aşağıda açıklanmıştır. 

Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki temel fark, öğrencilerin başarısının hesaplanmasına kullanılan ağırlıklar veya katsayıların farklı olmasıdır.

Bağıl değerlendirme sisteminde, öğrencilerin başarısının hesaplanmasında, yarıyıl içi değerlendirmenin %40’ı ve yarıyıl sonu sınav notunun %60’ı birlikte dikkate alınır.

Örneğin, [Kaynak 1: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf] ve [Kaynak 2: lisansüstü_eğitim_ve.pdf] belgelerine göre, bir derste öğrencilerin başarı notu, hem yarıyıl içi değerlendirmelerinden hem de yarıyıl sonu sınavından alınacak notların 4’lük not sistemindeki karşılığın hesaplanmak suretiyle belirlenmektedir.

Bağıl değerlendirme sisteminde, öğrencilerin başarı notuna katkı oranları anabilim/anasanat dalı teklifi, enstitü kurulu kararı ve Senato onayı ile değiştirilebilir.

Öte yandan, mutlak değerlendirme sisteminde ise öğrencilerin başarısı, sadece bir belirli kritere veya notaya bağlıdır. Örneğin, [Kaynak 3: yabancı_dil_eğitim_öğretimi_yönergesi.pdf] belgesine göre, yıl içi değerlendirmeden alınacak puanın %50’si ile yıl sonu sınav notunun %50’si birlikte dikkate alınır.

Bu şekilde, mutlak değerlendirmede öğrencilerin başarısının hesaplanmasındaki yaklaşım, bağıl değerlendirmede olduğu kadar karmaşıklıkmaz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: yabancı_dil_eğitim_öğretimi_yönergesi.pdf
```
