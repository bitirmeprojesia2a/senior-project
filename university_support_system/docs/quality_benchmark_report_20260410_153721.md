# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:37:21
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 60.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3146.5 ms |
| Medyan Sure | 3146.5 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 3146.5 | - |

## Soru Detaylari

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [ ] UBYS
  - [x] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3146.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ders kaydı danışmanınızın onayına kadar tüm süreci sırasıyla şöyle açıklıyorum:

1. Ogrenci Kaydı: Öncelikle öğrencinin Ondokuz Mayıs Üniversitesi (OMU) kaydolması gerekiyor. Bu, kaydını yaptıran bir öğrenci olarak süreci baştan sona inceleyeceğim.

2. Ders Seçimi: Öğrenci ders seçimini yaptıktan sonra, seçtiği derslerin onayını danışmanından almaları gerekir. Bu aşamada, ders değişikliği yapılırsa, öğrenciye bilgi verilerek bu durumun önlenmesi önemlidir.

3. Ders Kaydı Onayı: Öğrenci tarafından onaylı ders kaydıyla danışmanınıza başvurun. 
Buna göre, bu noktada danışmanınızın onayını bekleyeceksiniz. Ödemelerin tamamlanması ve herhangi bir borcu bulunmaması sağlandıktan sonra, öğrenci kimlik kartının verilebilmesi için süreç tamamlanmış olur.

Bu şekilde ilk kez üniversite kaydını yaptıran bir öğrencinin ders kaydından danışmanınızın onayına kadar tüm süreci açıklayabilirim.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: kayıt_sildirme_formu_lisans_önlisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
```
