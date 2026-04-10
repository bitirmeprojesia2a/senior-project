# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:34:27
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 0.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 75.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 6751.5 ms |
| Medyan Sure | 6751.5 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | YANLIS | OK | 3/4 | 6751.5 | - |

## Soru Detaylari

### Q10: Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [x] tekrar
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 6751.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Devamsızlık sonucunda kaldığın bir dersin bütünleme sınavına girebilir miyim cevabını verebilmek ve bütünleme sınavından sonra ne zaman dersi tekrar alabilirim cevabını vermeyi amaçlarım.

Gerekli kuralları gözden geçirmiş ve konuyu inceleyerek, kaynak belgelerini esas alınarak cevap vermeye geçiş yaparak;

Devamsızlık sonucunda kaldığın bir dersin bütünleme sınavına girebilir miyim cevabı;
Eğer dersin bütünleme sınavına girebilmem konusunda net bir bilgi bulamadım.

Bütünleme sınavından sonra ne zaman dersi tekrar alabilirim cevabı;
Eğer kaldığı dersin telafi süresi içerisinde eksik işlerin tamamlanması halinde öğrenciye blok veya klinik uygulama bütünleme sınavlarına girme hakkı tanınır. (Kaynak 1) ve bütünleme sınavı sonrası eğer o yılı tekrar etmek durumda olanlar o yılı tekrar ederler. (Kaynak 3).

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: yonerge_yabanci_dil_egitim_ogretim.pdf
```
