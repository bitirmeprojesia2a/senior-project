# RAG Değerlendirme Raporu

**Tarih:** 04 March 2026  
**Test Sorusu Sayısı:** 20  
**Top-K:** 5  

---

## Özet Metrikler

| Metrik | Değer |
|--------|-------|
| Precision@1 | 35.0% |
| Precision@3 | 60.0% |
| Precision@5 | 75.0% |
| Ortalama Top-1 Skor | 0.7983 |
| Ortalama Yanıt Süresi | 23306 ms |

### Zorluk Seviyesine Göre

| Zorluk | Soru Sayısı | Precision@3 |
|--------|:-----------:|:-----------:|
| easy | 7 | 57.1% |
| medium | 9 | 66.7% |
| hard | 4 | 50.0% |

---

## Detaylı Sonuçlar

| # | Soru | Top-1 Doğru | Top-3 Doğru | Skor | Kaynak | Süre |
|:-:|------|:-----------:|:-----------:|:----:|--------|:----:|
| 1 | ÇAP başvurusu için gereken not ortalaması kaçtır? | ❌ | ✅ | 0.973 | ÇİFT ANA DAL (İKİNCİ LİSANS) VE YAN DAL PROGRAMI.pdf | 27578ms |
| 2 | Yan dal programına başvuru şartları nelerdir? | ✅ | ✅ | 0.875 | ÇİFT ANA DAL (İKİNCİ LİSANS) VE YAN DAL PROGRAMI.pdf | 21400ms |
| 3 | Yatay geçiş için gerekli belgeler nelerdir? | ✅ | ✅ | 0.717 | yonerge_onlisans_lisans_yatay_gecis.pdf | 20736ms |
| 4 | Kayıt dondurma süresi ne kadardır? | ❌ | ❌ | 0.968 | ONDOKUZ MAYIS ÜNİVERSİTESİ ÖN LİSANS VE LİSANS.pdf | 24950ms |
| 5 | Staj süresi kaç gündür? | ✅ | ✅ | 0.778 | yonerge_onlisans_lisans_staj.pdf | 24216ms |
| 6 | Sınav sonucuna itiraz nasıl yapılır? | ❌ | ❌ | 0.990 | TIP FAKÜLTESİ TIP DOKTORLUĞU PROGRAMI.pdf | 26158ms |
| 7 | Mezuniyet için gereken toplam AKTS kaçtır? | ❌ | ❌ | 0.853 | ÖNLİSANS LİSANS ÖĞRETİMİ STAJ YÖNERGESİ.pdf | 31772ms |
| 8 | Devamsızlık sınırı nedir? | ❌ | ❌ | 0.602 | ONDOKUZ MAYIS ÜNİVERSİTESİ ÖN LİSANS VE LİSANS.pdf | 26574ms |
| 9 | Çift ana dal programından çıkarılma koşulları nele... | ❌ | ✅ | 0.521 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf | 19307ms |
| 10 | Yan dal programı kaç yarıyılda tamamlanmalıdır? | ✅ | ✅ | 0.522 | ÇİFT ANA DAL (İKİNCİ LİSANS) VE YAN DAL PROGRAMI.pdf | 17382ms |
| 11 | Not ortalaması nasıl hesaplanır? | ❌ | ❌ | 0.826 | BAĞIL DEĞERLENDİRME YÖNERGESİ.pdf | 41167ms |
| 12 | Ders tekrarı hangi durumlarda yapılır? | ✅ | ✅ | 0.409 | yonetmelik_lisansustu_egitim_ogretim.pdf | 27992ms |
| 13 | Azami öğrenim süresi kaç yıldır? | ✅ | ✅ | 0.985 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf | 20516ms |
| 14 | Bütünleme sınavına kimler girebilir? | ❌ | ✅ | 0.988 | DİŞ HEKİMLİĞİ FAKÜLTESI LİSANS EĞİTİM-ÖĞRETİM YÖNERGESİ.pdf | 20190ms |
| 15 | Ders muafiyeti başvurusu nasıl yapılır? | ❌ | ❌ | 0.990 | DERS YETERLİK, MUAFİYET VE İNTİBAK YÖNERGESİ.pdf | 19686ms |
| 16 | Mazeret sınavı ne zaman yapılır? | ❌ | ✅ | 0.965 | TIP FAKÜLTESİ TIP DOKTORLUĞU PROGRAMI.pdf | 15068ms |
| 17 | Diploma notu nasıl belirlenir? | ❌ | ❌ | 0.297 | yonerge_uluslararasi_ogrenci_yatay_gecis.pdf | 24343ms |
| 18 | Çift ana dal öğrencisi ana daldan mezun olabilir m... | ❌ | ❌ | 0.740 | ONDOKUZ MAYIS ÜNİVERSİTESİ ÖN LİSANS VE LİSANS.pdf | 15253ms |
| 19 | Kurum içi yatay geçişte not ortalaması şartı nedir... | ✅ | ✅ | 0.986 | yonerge_uluslararasi_ogrenci_yatay_gecis.pdf | 15511ms |
| 20 | Öğrenci işleri daire başkanlığının görevleri neler... | ❌ | ✅ | 0.980 | ÖN LİSANS VE LİSANS AKADEMİK DANIŞMANLIK.pdf | 26312ms |

---

## Başarısız Sorgular Analizi

### Soru 4: Kayıt dondurma süresi ne kadardır?
- **Beklenen konu:** kayıt dondurma
- **Dönen kaynak:** ONDOKUZ MAYIS ÜNİVERSİTESİ ÖN LİSANS VE LİSANS.pdf
- **Skor:** 0.9675

### Soru 6: Sınav sonucuna itiraz nasıl yapılır?
- **Beklenen konu:** sınav
- **Dönen kaynak:** TIP FAKÜLTESİ TIP DOKTORLUĞU PROGRAMI.pdf
- **Skor:** 0.9898

### Soru 7: Mezuniyet için gereken toplam AKTS kaçtır?
- **Beklenen konu:** mezuniyet
- **Dönen kaynak:** ÖNLİSANS LİSANS ÖĞRETİMİ STAJ YÖNERGESİ.pdf
- **Skor:** 0.8532

### Soru 8: Devamsızlık sınırı nedir?
- **Beklenen konu:** devamsızlık
- **Dönen kaynak:** ONDOKUZ MAYIS ÜNİVERSİTESİ ÖN LİSANS VE LİSANS.pdf
- **Skor:** 0.6017

### Soru 11: Not ortalaması nasıl hesaplanır?
- **Beklenen konu:** not
- **Dönen kaynak:** BAĞIL DEĞERLENDİRME YÖNERGESİ.pdf
- **Skor:** 0.8255

### Soru 15: Ders muafiyeti başvurusu nasıl yapılır?
- **Beklenen konu:** muafiyet
- **Dönen kaynak:** DERS YETERLİK, MUAFİYET VE İNTİBAK YÖNERGESİ.pdf
- **Skor:** 0.9896

### Soru 17: Diploma notu nasıl belirlenir?
- **Beklenen konu:** diploma
- **Dönen kaynak:** yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- **Skor:** 0.2972

### Soru 18: Çift ana dal öğrencisi ana daldan mezun olabilir mi?
- **Beklenen konu:** çap
- **Dönen kaynak:** ONDOKUZ MAYIS ÜNİVERSİTESİ ÖN LİSANS VE LİSANS.pdf
- **Skor:** 0.7403


---

*Bu rapor `scripts/evaluate_rag.py` tarafından otomatik üretilmiştir.*