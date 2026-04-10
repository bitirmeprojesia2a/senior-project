# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-09 22:35:24
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 100.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 4635.4 ms |
| Medyan Sure | 4635.4 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 4/4 | 4635.4 | - |

## Soru Detaylari

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] kayıt dondurma
  - [x] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4635.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sorunun cevabı şu şekildedir:

Kayıt dondurma ile kayıt yaptırmamak arasında farklılıklar vardır. Kayıt dondurma, öğrencinin ders kayıtlarını sınırlı bir süre için askıya alması anlamını taşımaktadır. Bu durum, öğrencinin ders seçme ve değişme hakkını sınırlı bir süre için kaybetmesine neden olur. Ancak, öğrencinin ders kayıtlarını askıya alması, öğrenim süresinden bir dönemin sayılmasına sebep olmaz.

Diğer yandan, kayıt yaptırmamak, öğrencinin belirtilen süre içinde ders kaydı yapmaması anlamına gelir. Bu durum, öğrencinin öğrenim süresinden o dönemi kaybetmesine ve o dönemi sayılmasına sebep olabilir.

Her iki durumda da öğrencinin öğrenim hakları etkilenebilir. Kayıt dondurma, öğrenciye öğrenim süresinden sınırlı bir süre için bir dönem daha verilmesine sebep olabilir. Ancak, kayıt yaptırmamak durumunda, öğrencinin öğrenim hakkını kaybetmesine ve o dönemi sayılmasına sebep olabilir.

Yanıtla ilgili kaynaklar:

[Kaynak 1: sık_sorulan_sorular.txt]
Yatay geçiş hakkı kazanıp kayıt yaptırmamasam herhangi bir sorun olur mu? Üniversitemize yatay geçişle kayıt hakkı kazanıp, kayıt yaptırmamanız durumunda herhangi bir sorun olmayacaktır.

[Kaynak 2: sık_sorulan_sorular.txt]
Ders ekleme/çıkarma nedir? Bu işlemi nasıl yapmalıyım? Seçmiş olduğunuz derslerden açılmayan seçmeli ders olduğunda veya değiştirmek istediğiniz dersler için Akademik Takvimde belirtilen süreler içerisinde danışmanınızla irtibata geçerek yapabileceğiniz işlemdir.

[Kaynak 3: yonetmelik_onlisans_lisans_egitim_ogretim.pdf]
MADDE 10- (1) Öğrenciler, her dönem/yıl başında akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden alacakları dersleri seçerler. Ders kaydı, danışman onayı ile kesinleşir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egiti
... (73 karakter daha)
```
