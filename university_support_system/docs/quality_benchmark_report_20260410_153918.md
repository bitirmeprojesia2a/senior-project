# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:39:18
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 0.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 20.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3059.7 ms |
| Medyan Sure | 3059.7 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | YANLIS | OK | 1/5 | 3059.7 | - |

## Soru Detaylari

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs', 'academic_programs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [ ] %40
  - [ ] %60
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 3059.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sorusuna karşılık olarak vermek için elimdeki kaynakları inceledim:

Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

KAYNAK 1 ve KAYNAK 2'de uzaktan eğitim programının genel kuralları ve derslerin veriliş şekli ile devam ve başarı durumlarının nasıl belirleneceği hakkında bilgi bulunmakta ise de sınav ve başarı değerlendirmesi ile ilgili detaylı bilgiye KAYNAK 3'te yer verilmemektedir.

Bu nedenle, "UZAKTAN_ATAKIM" adlı belgeye bakıldığında Ondokuz Mayıs Üniversitesi (OMU) Ön Lisans ve Lisans Eğitim- Öğretim Yönetmeliği ile OMU Lisansüstü Eğitim ve Öğretim Yönetmeliği hükümlerince belirlendiğinden bahsedilmektedir.

Buna göre, Ondokuz Mayıs Üniversitesi'nde uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı değildir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: samsun_sağlık_yüksekokulu_eğitim_öğretim_ve_sınav_yönetmeliği.txt
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
```
