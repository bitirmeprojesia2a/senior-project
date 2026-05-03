# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-23 12:54:50
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 4

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 75.0% |
| Anahtar Bilgi Kapsami | 53.3% |
| Temiz Kalite Orani | 75.0% |
| Ortalama Sure | 30088.0 ms |
| Medyan Sure | 21744.1 ms |
| Intent Analizi Aktif | 0/4 |
| Force LLM Sentez | 0/4 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 2/4 | 16303.7 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 3/3 | 25374.6 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 3/4 | 18113.6 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | YANLIS (kural) | 0/4 | 60560.2 | a2a_transport_fallback |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs', 'announcement'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Sure**: 16303.7 ms
- **Kaynak Sayisi**: 12

**Yanit:**
```
Benchmark, Yatay geçişle gelen bir öğrenci, muafiyet başvurularını 2025-2026 Eğitim Öğretim Yılı Bahar Yarıyılı için 26.01.2026-01.02.2026 tarihleri arasında yapmalıdır. Bu sürenin içinde karar çıkana kadar derslere devam edilmesi önem arz etmektedir.

Eğer öğrenci kayıt yaptırdığı öğretim yılının en geç 3. haftasının sonuna kadar muafiyet başvurunu yaptırsa, karar çıkana kadar derslere devam etmelidir. Bu durum, daha sonra yönetim kurulunca yapılacak karardan önce geçerlidir.

Yani kısaca; 26.01.2026-01.02.2026 tarihleri arasında muafiyet başvurularını yaptıktan sonra veya kayıt yaptırdığı öğretim yılının en geç 3. haftasının sonuna kadar muafiyet başvurunu yaptıktan sonra da derslere devam edilmesi önemlidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Duyuru kaydi: 2025-2026 Eğitim Öğretim Yılı Bahar Yarıyılı Yatay Geçiş Yedek sonuçları (https://www.omu.edu.tr/tr/icerik/duyuru/2025-2026-egitim-ogretim-yili-bahar-yariyili-yatay-gecis-yedek-sonuclari)
- Duyuru kaydi: 2025 - 2026 Güz Dönemi Yatay Geçiş Başvuru Sonuçları (https://eem-muhendislik.omu.edu.tr/tr/haberler/2025-2026-guz-donemi-yatay-gecis-basvuru-sonuclar)
- Duyuru kaydi: 2025-2026 eğitim öğretim yılı bahar yarıyılı yatay geçiş sonuçları (https://www.omu.edu.tr/tr/icerik/duyuru/2025-2026-egitim-ogretim-yili-bahar-ya
... (29 karakter daha)
```

### Q2: Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi ve sınavda başarılı sayılmam için minimum not kaç?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] staj
  - [x] tamamla
  - [x] CC
- **Sure**: 25374.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Soru 1: Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi?

Cevap: Hayır.

Kaynak: [Kaynak 1: sık_sorulan_sorular.txt]

Soru 2: Tek ders sınavında başarılı sayılmam için minimum not kaç?

Cevap: 50 (ara sınav şartı aranmaksızın).

Kaynak: [Kaynak 2: sık_sorulan_sorular.txt] (Not: Tek ders sınavında CC notu alınması başarı sayılabilir, ancak sınavda en az 50 puan alamayanlar başarısız sayılır.) 

Soru 3: Tek ders sınavına başvurabilmem için dönem başında ders kaydı yaptırmam gereken mi?

Cevap: Hayır.

Kaynak: [Kaynak 1: sık_sorulan_sorular.txt]

Soru 4: Başarısız dersten başarılı sayılabilmek için minimum kaç not aldım?

Cevap: Ara sınav şartı aranmaksızın en az CC.

Kaynak: [Kaynak 2: sık_sorulan_sorular.txt]

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [x] yeni
  - [x] ders
- **Sure**: 18113.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Soruya göre, başarısız olduğunuz seçmeli ders yerine başka bir seçmeli seçersem, devam zorunluluğum nasıl değişir?

Dördüncü ve Beşinci maddeye göre, başarısız olduğu bir seçmeli ders yerine, bir başka seçmeli ders alabilirsiniz. Ancak, devam zorunluluğu, devam koşulunun yerine getirilmesiyle birlikte yerine getirilir. Bu nedenle, devam zorunluluğu değişmez, ancak devamsızlık hesabında yeni seçilen dersin kredi değeri ve devam durumuna göre hesabında dikkate alınır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yaz_okulu_eğitim_öğretim.pdf
- Belge: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf
```

### Q4: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: hard
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] transkript
  - [ ] dahil
  - [ ] ortalama
  - [ ] tamamlamıştır
- **Sure**: 60560.2 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: a2a_transport_fallback

**Yanit:**
```
Benchmark, Akademik Programlar agent servisi zamaninda yanit veremedi. Diger mevcut kaynaklarla yanit verilebiliyorsa isleme devam edilecek; gerekirse biraz sonra tekrar deneyin.

Uretim Turu:
- Kural
```
