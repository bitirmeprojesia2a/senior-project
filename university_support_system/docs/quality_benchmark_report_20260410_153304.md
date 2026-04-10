# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:33:04
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 0.0% |
| Anahtar Bilgi Kapsami | 60.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 478.3 ms |
| Medyan Sure | 478.3 ms |
| Intent Analizi Aktif | 0/1 |
| Force LLM Sentez | 0/1 |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | YANLIS (rag) | 3/5 | 478.3 | - |

## Soru Detaylari

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 3/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [ ] bildiri
  - [ ] harç
- **Sure**: 478.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Yatay gecis sureci icin en ilgili kaynakta su bilgi yer aliyor:
Yatay geçiş yaparsam bursumu devredebilir miyim, bursum kesilir mi? Bursunuzun devri veya kesilip kesilmeyeceği konusunda bilgiye ulaşmak için burs aldığınız kurumla iletişim kurmanız gerekmektedir. Başka bir üniversiteye geçiş yapmak istiyorum. Gerekli belgeleri nereden temin edebilirim? Üniversitemizden başka bir üniversiteye geçiş yapmak isteyen öğrenciler, istenen belgeleri E-Devlet üzerinden, UBYS öğrenci bilgi ekranından veya öğrenim gördükleri fakülte/yüksekokuldan temin edebilirle Yatay geçişle yabancı uyruklu öğrenci alıyor musunuz? Kontenjan tablosunda yabancı uyruklu öğrenci kontenjanı bulunan programlara yatay geçiş başvurusu yapabilirsiniz. Yurt dışında öğrenim görüyorum. Yatay geçiş yapabilir miyim? Yurt dışı öğrenci kontenjanı olduğu belirtilen programlara yatay geçiş başvurusu yapabilirsiniz.

(Kaynak: sık_sorulan_sorular.txt)

Finans:
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
```
