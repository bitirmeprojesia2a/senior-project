# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:38:36
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 50.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3481.7 ms |
| Medyan Sure | 3481.7 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 3/6 | 3481.7 | - |

## Soru Detaylari

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/6
  - [x] ders
  - [ ] staj
  - [x] GANO
  - [x] 2,00
  - [ ] ilişik kesme
  - [ ] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3481.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Mezuniyet için gerekli tüm koşulları ve ilişiği kesme sürecini adım adım açıkladığım için aşağıdaki bilgiyi kullanabilirsiniz:

Mezuniyet Koşulları:

* öğrencinin programın 14. maddede belirtilen yükümlülüklerini yerine getirmesi (Kayıtlı olduğu programın 14. maddesindeki yükümlülükleri yerine getirmesi)
* öğrencinin GANO'su 2,00; sınıf geçme sisteminde GANO'su 2,71 ve daha yukarı olması (ders geçme sisteminde GANO'su 2,00 ve sınıf geçme sisteminde GANO'su 2,71 veya daha yüksek olması)
* öğrencinin GANO'su 3,50 ve üzeri olması (Onur öğrencisi olarak mezun olmak için GANO'su 3,50 ve üzeri olması)

İlişkisine Kesme:

* öğrencinin kendi isteği ile kaydını silmesi (Yazılı isteği üzerine kaydını sildi)
* öğrencinin katkı payı ve öğrenim ücreti ödememesi veya kayıt yenilememesi (Dört yıl üst üste katkı payı ve öğrenim ücreti ödemeyen veya kayıt yenilemeyen lisans öğrencilerinin ilişiği kesilir)
* öğrencinin başarısız olduğu ders sayısını bire indirememesi (8. maddenin 3. ve 4. fıkralarına göre başarısız oldukları ders sayısını bire indiremeyen öğrencilerin ilişiği kesilir)
* öğrencinin disiplin cezası alması (Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre yükseköğretim kurumlarından çıkarma cezası almış öğrencilerin ilişiği kesilir)

Ilişkisine Kesme Adetleri:

1. Öğrencinin yazıyla isteği üzerine kaydını sildirmesi
2. İlgili birimlerin teklifi ve Senato kararı ile YÖK'ün onaylaması durumunda
3. Başarısız oldukları ders sayısını bire indiremeyen öğrencilerin ilişiği kesilir
4. Öğrencinin tekrar kaydolmak istediği takdirde ÖSYM tarafından yeniden yerleştirilmediği veya Üniversite tarafından yapılan ölçme ve değerlendirme sonucunda kayıt hakkı kazanmadığı sürece

Not:

* Bu bilgiler belge baglaminda geçmektedir.
* Bu konudaki detaylı bilgi için ilgili kurum ve kuruluşlarla iletişime geçmek önemlidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini payla
... (368 karakter daha)
```
