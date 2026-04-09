# Reranker Skor Dagilim Analizi

**Tarih:** 2026-04-08 21:18
**Model:** seroe/bge-reranker-v2-m3-turkish-triplet
**Toplam Soru:** 40
**Toplam Skor Ornegi:** 400

---

## Tum Skorlar (Tum Adaylar)

### Ham Reranker Skorlari

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.0 |
| p10 | 0.0002 |
| p25 | 0.0021 |
| median | 0.0405 |
| mean | 0.1783 |
| p75 | 0.203 |
| p90 | 0.7329 |
| max | 0.9976 |
| std | 0.2851 |

### Sigmoid Donusturulmus Skorlar

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.5 |
| p10 | 0.5001 |
| p25 | 0.5005 |
| median | 0.5101 |
| mean | 0.5428 |
| p75 | 0.5506 |
| p90 | 0.6754 |
| max | 0.7306 |
| std | 0.067 |

---

## Top-1 Skorlar (Her Sorunun En Iyi Adayi)

### Ham Top-1 Skorlari

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.0 |
| p10 | 0.014 |
| p25 | 0.0593 |
| median | 0.4443 |
| mean | 0.5093 |
| p75 | 0.9546 |
| p90 | 0.9788 |
| max | 0.9976 |
| std | 0.4029 |

### Sigmoid Top-1 Skorlari

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.5 |
| p10 | 0.5035 |
| p25 | 0.5148 |
| median | 0.6093 |
| mean | 0.62 |
| p75 | 0.722 |
| p90 | 0.7269 |
| max | 0.7306 |
| std | 0.0932 |

---

## Sigmoid Kalibrasyon Onerisi

- **Formul:** `sigmoid((score - 0.0405) / 0.5000)`
- **Shift (median):** 0.0405
- **Scale (IQR):** 0.5
- **Onerilen direct-RAG esigi:** 0.581
- **Onerilen min-source esigi:** 0.481

---

## Soru Bazli Detaylar

### Sistem giris sifremi unuttum, ne yapmaliyim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.8774 | 0.7063 | 0.0000 | sık_sorulan_sorular.txt |
| 2 | 0.0009 | 0.5002 | 0.0000 | sık_sorulan_sorular.txt |
| 3 | 0.0008 | 0.5002 | -0.0223 | sık_sorulan_sorular.txt |
| 4 | 0.0007 | 0.5002 | 0.0335 | sık_sorulan_sorular.txt |
| 5 | 0.0005 | 0.5001 | 0.0321 | sık_sorulan_sorular.txt |
| 6 | 0.0004 | 0.5001 | 0.0000 | sık_sorulan_sorular.txt |
| 7 | 0.0004 | 0.5001 | 0.0405 | öğrenci_işleri_birimi.txt |
| 8 | 0.0002 | 0.5001 | 0.0000 | öğrenci_işleri_birimi.txt |
| 9 | 0.0002 | 0.5001 | 0.0430 | kimlik_kartı_yönergesi.pdf |
| 10 | 0.0002 | 0.5001 | -0.0226 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |

### UBYS uzerinden ilisik kesme talebini nasil baslatirim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9516 | 0.7214 | 0.0000 | sık_sorulan_sorular.txt |
| 2 | 0.9467 | 0.7205 | 0.0000 | sık_sorulan_sorular.txt |
| 3 | 0.1625 | 0.5405 | 0.0000 | kimlik_kartı_yönergesi.pdf |
| 4 | 0.0344 | 0.5086 | 0.0000 | öğrenci_işleri_birimi.txt |
| 5 | 0.0119 | 0.5030 | 0.0442 | öğrenci_toplulukları_yönergesi.pdf |
| 6 | 0.0115 | 0.5029 | 0.0000 | öğrenci_işleri_birimi.txt |
| 7 | 0.0094 | 0.5024 | 0.0614 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 8 | 0.0064 | 0.5016 | 0.0622 | ön_lisans_ve_lisans.pdf |
| 9 | 0.0048 | 0.5012 | 0.0000 | sık_sorulan_sorular.txt |
| 10 | 0.0030 | 0.5008 | 0.0000 | sık_sorulan_sorular.txt |

### Diplomami kaybettim, ikinci nusha icin ne yapmaliyim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9551 | 0.7221 | 0.0000 | sık_sorulan_sorular.txt |
| 2 | 0.9500 | 0.7211 | 0.4317 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 3 | 0.0600 | 0.5150 | 0.3103 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 4 | 0.0456 | 0.5114 | 0.0000 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 5 | 0.0160 | 0.5040 | 0.2616 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 6 | 0.0022 | 0.5005 | 0.0000 | sık_sorulan_sorular.txt |
| 7 | 0.0017 | 0.5004 | 0.2325 | sık_sorulan_sorular.txt |
| 8 | 0.0011 | 0.5003 | 0.2320 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 9 | 0.0009 | 0.5002 | 0.0000 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 10 | 0.0009 | 0.5002 | 0.2558 | sık_sorulan_sorular.txt |

### Diploma eki transkript yerine gecer mi?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9944 | 0.7300 | 0.0000 | sık_sorulan_sorular.txt |
| 2 | 0.9767 | 0.7264 | 0.0000 | sık_sorulan_sorular.txt |
| 3 | 0.4585 | 0.6127 | 0.0000 | sık_sorulan_sorular.txt |
| 4 | 0.3698 | 0.5914 | 0.0000 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 5 | 0.0176 | 0.5044 | 0.3346 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 6 | 0.0093 | 0.5023 | 0.0000 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 7 | 0.0065 | 0.5016 | 0.0000 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 8 | 0.0065 | 0.5016 | 0.2420 | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 9 | 0.0057 | 0.5014 | 0.2332 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 10 | 0.0054 | 0.5014 | 0.0000 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |

### Kayit dondurma ile kayit yaptirmamak arasinda ne fark var?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.8740 | 0.7056 | 0.0000 | sık_sorulan_sorular.txt |
| 2 | 0.1697 | 0.5423 | -0.1498 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.1588 | 0.5396 | 0.0000 | ön_lisans_ve_lisans.pdf |
| 4 | 0.0855 | 0.5214 | -0.1786 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 5 | 0.0786 | 0.5196 | 0.0000 | sık_sorulan_sorular.txt |
| 6 | 0.0610 | 0.5152 | -0.1590 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 7 | 0.0418 | 0.5104 | -0.1749 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 8 | 0.0352 | 0.5088 | -0.2109 | ön_lisans_ve_lisans.pdf |
| 9 | 0.0212 | 0.5053 | 0.0000 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0142 | 0.5035 | -0.2498 | yonerge_onlisans_lisans_yatay_gecis.pdf |

### Hazirlik sinifi okuyan ogrenci transkriptsiz Ek Madde-1 ile yatay gecis basvurusu yapabilir mi?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.7023 | 0.6687 | 0.0000 | sık_sorulan_sorular.txt |
| 2 | 0.3638 | 0.5900 | 0.0000 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 3 | 0.2410 | 0.5600 | 0.0000 | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 4 | 0.0890 | 0.5222 | 0.0000 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 5 | 0.0717 | 0.5179 | 0.0000 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 6 | 0.0584 | 0.5146 | 0.1941 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 7 | 0.0565 | 0.5141 | 0.0000 | sık_sorulan_sorular.txt |
| 8 | 0.0529 | 0.5132 | 0.2286 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 9 | 0.0333 | 0.5083 | 0.2233 | sık_sorulan_sorular.txt |
| 10 | 0.0094 | 0.5023 | 0.1795 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Birden fazla universiteye yatay gecis basvurusu yapabilir miyim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.4118 | 0.6015 | 0.0000 | sık_sorulan_sorular.txt |
| 2 | 0.0773 | 0.5193 | 0.1589 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 3 | 0.0641 | 0.5160 | 0.1557 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 4 | 0.0443 | 0.5111 | 0.0000 | yonerge_onlisans_lisans_yatay_gecis.pdf |
| 5 | 0.0401 | 0.5100 | 0.0000 | sık_sorulan_sorular.txt |
| 6 | 0.0399 | 0.5100 | 0.0000 | sık_sorulan_sorular.txt |
| 7 | 0.0144 | 0.5036 | 0.1888 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 8 | 0.0114 | 0.5028 | 0.1534 | yonerge_onlisans_lisans_yatay_gecis.pdf |
| 9 | 0.0083 | 0.5021 | 0.1644 | yonerge_onlisans_lisans_yatay_gecis.pdf |
| 10 | 0.0083 | 0.5021 | 0.1784 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Ozel ogrenci olarak ne zaman basvuru yapmaliyim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.7307 | 0.6750 | 0.0000 | sık_sorulan_sorular.txt |
| 2 | 0.2412 | 0.5600 | 0.0000 | sık_sorulan_sorular.txt |
| 3 | 0.0011 | 0.5003 | 0.0000 | sık_sorulan_sorular.txt |
| 4 | 0.0009 | 0.5002 | 0.0954 | sık_sorulan_sorular.txt |
| 5 | 0.0005 | 0.5001 | 0.0000 | sık_sorulan_sorular.txt |
| 6 | 0.0005 | 0.5001 | 0.0000 | sık_sorulan_sorular.txt |
| 7 | 0.0004 | 0.5001 | 0.0325 | yaz_okulu_eğitim_öğretim.pdf |
| 8 | 0.0004 | 0.5001 | 0.0708 | sık_sorulan_sorular.txt |
| 9 | 0.0003 | 0.5001 | 0.0580 | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0003 | 0.5001 | 0.0415 | document.pdf |

### Ozel ogrenci olarak basvuru icin hangi belgeler gerekir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.3602 | 0.5891 | 0.1389 | sık_sorulan_sorular.txt |
| 2 | 0.2960 | 0.5735 | 0.0000 | sık_sorulan_sorular.txt |
| 3 | 0.1828 | 0.5456 | 0.2068 | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 4 | 0.1743 | 0.5435 | 0.0000 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 5 | 0.1225 | 0.5306 | 0.1649 | sık_sorulan_sorular.txt |
| 6 | 0.0422 | 0.5106 | 0.1410 | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 7 | 0.0393 | 0.5098 | 0.1800 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 8 | 0.0343 | 0.5086 | 0.1164 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 9 | 0.0282 | 0.5070 | 0.1211 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 10 | 0.0248 | 0.5062 | 0.1594 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Daha once aldigim dersler icin muafiyet basvurusunu ne zaman yapmaliyim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9545 | 0.7220 | 0.0000 | sık_sorulan_sorular.txt |
| 2 | 0.8877 | 0.7084 | 0.0000 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 3 | 0.6994 | 0.6681 | 0.0000 | sık_sorulan_sorular.txt |
| 4 | 0.3392 | 0.5840 | 0.0000 | yonerge_ders_yeterlik_muafiyet_intibak.pdf |
| 5 | 0.3107 | 0.5770 | 0.0000 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 6 | 0.2926 | 0.5726 | 0.2754 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 7 | 0.2568 | 0.5638 | 0.3752 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 8 | 0.1494 | 0.5373 | 0.0000 | sık_sorulan_sorular.txt |
| 9 | 0.0796 | 0.5199 | 0.0000 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 10 | 0.0681 | 0.5170 | 0.2817 | ders_yeterlilik_sınavı_uygulama_yönergesi.pdf |

### Ikamet izni basvurusu icin hangi belgeler gerekir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9747 | 0.7261 | 0.0000 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 2 | 0.9079 | 0.7126 | 0.0000 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 3 | 0.8867 | 0.7082 | 0.2809 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 4 | 0.8470 | 0.6999 | 0.0000 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 5 | 0.7879 | 0.6874 | 0.0000 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 6 | 0.6618 | 0.6597 | 0.0000 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 7 | 0.5120 | 0.6253 | 0.0000 | uluslararası_öğrenci_ikamet_işlemleri.pdf |
| 8 | 0.4872 | 0.6194 | 0.1453 | uluslararası_öğrenci.pdf |
| 9 | 0.4236 | 0.6043 | 0.1446 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 10 | 0.3534 | 0.5874 | 0.0000 | muvafakatname.pdf |

### Denklik belgesi ne zaman gerekir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9000 | 0.7110 | 0.0000 | denklik_belgesi.pdf |
| 2 | 0.5475 | 0.6335 | 0.0000 | denklik_belgesi.pdf |
| 3 | 0.2267 | 0.5564 | 0.0000 | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 4 | 0.2225 | 0.5554 | 0.0000 | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 5 | 0.1725 | 0.5430 | 0.0000 | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 6 | 0.0928 | 0.5232 | 0.0000 | tyb.pdf |
| 7 | 0.0806 | 0.5201 | 0.0000 | lisansüstü_eğitim_enstitüsü.pdf |
| 8 | 0.0645 | 0.5161 | 0.0000 | uluslararası_öğrenci.pdf |
| 9 | 0.0478 | 0.5120 | 0.0000 | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |
| 10 | 0.0473 | 0.5118 | 0.0000 | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |

### YOS ID numarami nasil ogrenebilirim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.0284 | 0.5071 | 0.2520 | öğrenci_no_öğrenme.pdf |
| 2 | 0.0276 | 0.5069 | 0.0000 | uluslararası_öğrenci.pdf |
| 3 | 0.0161 | 0.5040 | 0.0000 | yös_ıd_no_öğrenme.pdf |
| 4 | 0.0023 | 0.5006 | 0.0000 | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 5 | 0.0005 | 0.5001 | 0.1584 | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 6 | 0.0004 | 0.5001 | 0.1973 | avrupa_birliği_eğitim_ve_gençlik_programları_hayat_boyu_öğrenme_erasmus.pdf |
| 7 | 0.0004 | 0.5001 | 0.0000 | uluslararası_öğrenci_kimlik_bilgileri_güncelleme_formu.pdf |
| 8 | 0.0003 | 0.5001 | 0.2290 | özel_yetenek_sınavı_yönergesi.pdf |
| 9 | 0.0002 | 0.5001 | 0.0000 | uluslararası_öğrenci_evrak_teslim_formu_r1.pdf |
| 10 | 0.0002 | 0.5000 | 0.1637 | yonerge_uluslararasi_ogrenci_kabul.pdf |

### Uluslararasi ogrenci kaydinda evrak teslim formu gerekiyor mu?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9699 | 0.7251 | 0.0000 | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 2 | 0.9653 | 0.7242 | 0.0000 | uluslararası_öğrenci_yönergesi.pdf |
| 3 | 0.8479 | 0.7001 | 0.0000 | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 4 | 0.7483 | 0.6788 | 0.0000 | uluslararası_öğrenci_evrak_teslim_formu_r1.pdf |
| 5 | 0.7165 | 0.6718 | 0.0000 | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 6 | 0.3647 | 0.5902 | 0.0000 | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 7 | 0.1794 | 0.5447 | 0.2456 | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 8 | 0.0988 | 0.5247 | 0.0000 | avrupa_birliği_eğitim_ve_gençlik_programları_hayat_boyu_öğrenme_erasmus.pdf |
| 9 | 0.0982 | 0.5245 | 0.2318 | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 10 | 0.0854 | 0.5213 | 0.2977 | ön_kayıt_kılavuzu_başvuru_adımları.pdf |

### TOMER ne is yapar?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.0003 | 0.5001 | 0.0187 | kök_hücre_araştırma_merkezi_yönergesi.pdf |
| 2 | 0.0003 | 0.5001 | 0.1173 | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 3 | 0.0003 | 0.5001 | 0.0652 | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 4 | 0.0003 | 0.5001 | 0.0000 | veteriner_fakültesi_eğitim_uygulama_ve_araştırma_hastanesi_işletme_yönergesi.pdf |
| 5 | 0.0002 | 0.5001 | 0.0097 | dil_ve_konuşma_bozuklukları.pdf |
| 6 | 0.0002 | 0.5001 | 0.0732 | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 7 | 0.0002 | 0.5000 | 0.0000 | sağlık_uygulama_ve_araştırma_merkezi_tıp_laboratuvarları_yönergesi.pdf |
| 8 | 0.0001 | 0.5000 | 0.0000 | toplumsal_katkı_politikası.pdf |
| 9 | 0.0001 | 0.5000 | 0.0472 | kariyer_merkezi_yönergesi.pdf |
| 10 | 0.0001 | 0.5000 | 0.0000 | güvenlik_hizmetlerinin_yürütülmesine_dair_yönerge.pdf |

### Pedagojik formasyon dersleri transkripte dahil edilir mi?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9976 | 0.7306 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.9846 | 0.7280 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 3 | 0.9828 | 0.7277 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 4 | 0.9743 | 0.7260 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.2521 | 0.5627 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 6 | 0.1398 | 0.5349 | 0.2641 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.1332 | 0.5333 | 0.1782 | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |
| 8 | 0.0900 | 0.5225 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 9 | 0.0759 | 0.5190 | 0.2134 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 10 | 0.0693 | 0.5173 | 0.0000 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |

### Pedagojik formasyon mezuniyet ortalamasina dahil edilir mi?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9778 | 0.7267 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 2 | 0.9738 | 0.7259 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 3 | 0.7435 | 0.6778 | 0.0000 | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 4 | 0.5519 | 0.6346 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.4799 | 0.6177 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 6 | 0.4540 | 0.6116 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 7 | 0.3055 | 0.5758 | 0.2682 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 8 | 0.1628 | 0.5406 | 0.2573 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.1124 | 0.5281 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 10 | 0.0687 | 0.5172 | 0.0000 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |

### Pedagojik formasyon alirsam mezuniyet 240 AKTS'nin ustune cikabilir mi?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9885 | 0.7288 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.5728 | 0.6394 | 0.0000 | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 3 | 0.4372 | 0.6076 | 0.0000 | çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf |
| 4 | 0.0930 | 0.5232 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.0730 | 0.5182 | 0.2596 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 6 | 0.0475 | 0.5119 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 7 | 0.0427 | 0.5107 | 0.1975 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 8 | 0.0350 | 0.5088 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 9 | 0.0319 | 0.5080 | 0.2305 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.0297 | 0.5074 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |

### Pedagojik formasyon derslerinin tumunu almak zorunlu mu?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9775 | 0.7266 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.8931 | 0.7095 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 3 | 0.2311 | 0.5575 | 0.2763 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 4 | 0.2133 | 0.5531 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.1647 | 0.5411 | 0.0000 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 6 | 0.1565 | 0.5390 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 7 | 0.1563 | 0.5390 | 0.2716 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 8 | 0.1533 | 0.5383 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 9 | 0.1220 | 0.5305 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 10 | 0.1051 | 0.5262 | 0.0000 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |

### Pedagojik formasyon dersleri en erken hangi yariyilda alinabilir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9004 | 0.7110 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 2 | 0.8964 | 0.7102 | 0.3561 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 3 | 0.7425 | 0.6776 | 0.3342 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 4 | 0.7318 | 0.6752 | 0.3768 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.4549 | 0.6118 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 6 | 0.2652 | 0.5659 | 0.0000 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.2466 | 0.5613 | 0.2433 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 8 | 0.2215 | 0.5552 | 0.0000 | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 9 | 0.2161 | 0.5538 | 0.0000 | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 10 | 0.2039 | 0.5508 | 0.0000 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |

### Yemek bursu basvurulari nereden yapilir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9764 | 0.7264 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 2 | 0.8343 | 0.6973 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.5376 | 0.6313 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.2255 | 0.5561 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.1314 | 0.5328 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.1030 | 0.5257 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.0914 | 0.5228 | 0.0000 | kimlik_kartı_yönergesi.pdf |
| 8 | 0.0526 | 0.5131 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0445 | 0.5111 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0378 | 0.5094 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |

### Bursum hangi sartlarda kesilir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.0483 | 0.5121 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 2 | 0.0434 | 0.5108 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.0020 | 0.5005 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.0013 | 0.5003 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.0011 | 0.5003 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.0010 | 0.5002 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.0009 | 0.5002 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0009 | 0.5002 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0009 | 0.5002 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0005 | 0.5001 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |

### Kayit ekraninda borclu ya da fazla ucretli gorunuyorsam ne yapmaliyim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.0000 | 0.5000 | 0.0000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 2 | 0.0000 | 0.5000 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.0000 | 0.5000 | -0.1243 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 4 | 0.0000 | 0.5000 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.0000 | 0.5000 | -0.1933 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 6 | 0.0000 | 0.5000 | 0.0000 | idari_ve_mali_işler_birimi.txt |
| 7 | 0.0000 | 0.5000 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0000 | 0.5000 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0000 | 0.5000 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0000 | 0.5000 | 0.0000 | idari_ve_mali_işler_birimi.txt |

### Program suresini asarsam katki payi oder miyim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.0243 | 0.5061 | 0.0000 | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |
| 2 | 0.0011 | 0.5003 | 0.0000 | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |
| 3 | 0.0001 | 0.5000 | 0.0000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 4 | 0.0001 | 0.5000 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.0000 | 0.5000 | -0.2086 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 6 | 0.0000 | 0.5000 | -0.1887 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 7 | 0.0000 | 0.5000 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0000 | 0.5000 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0000 | 0.5000 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0000 | 0.5000 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |

### Harc iadesi icin IBAN ve dekontla nereye basvurmam gerekir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.0000 | 0.5000 | -0.0200 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 2 | 0.0000 | 0.5000 | 0.0000 | idari_ve_mali_işler_birimi.txt |
| 3 | 0.0000 | 0.5000 | 0.0000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 4 | 0.0000 | 0.5000 | 0.0000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 5 | 0.0000 | 0.5000 | 0.0000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 6 | 0.0000 | 0.5000 | 0.0000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.0000 | 0.5000 | 0.0000 | idari_ve_mali_işler_birimi.txt |
| 8 | 0.0000 | 0.5000 | 0.0000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 9 | 0.0000 | 0.5000 | 0.0000 | idari_ve_mali_işler_birimi.txt |
| 10 | 0.0000 | 0.5000 | 0.0000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |

### Sinava giremedigim ders icin mazeret sinavi basvurusu nasil yapilir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.2440 | 0.5607 | 0.0000 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 2 | 0.2028 | 0.5505 | 0.0000 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.1397 | 0.5349 | 0.0000 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 4 | 0.1232 | 0.5308 | 0.0000 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 5 | 0.0386 | 0.5097 | 0.0000 | sık_sorulan_sorular.txt |
| 6 | 0.0229 | 0.5057 | 0.0453 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.0176 | 0.5044 | 0.0377 | ön_lisans_ve_lisans.pdf |
| 8 | 0.0159 | 0.5040 | 0.0000 | sık_sorulan_sorular.txt |
| 9 | 0.0070 | 0.5017 | 0.0000 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 10 | 0.0062 | 0.5015 | 0.1011 | ön_lisans_ve_lisans.pdf |

### Bir dersten kac kez sinav hakkina sahibim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.1487 | 0.5371 | 0.2127 | uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf |
| 2 | 0.1115 | 0.5278 | 0.0000 | uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf |
| 3 | 0.0270 | 0.5068 | 0.1508 | uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf |
| 4 | 0.0200 | 0.5050 | 0.1394 | mühendislik_fakültesi_ortak_sınav_yönergesi.pdf |
| 5 | 0.0119 | 0.5030 | 0.1373 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 6 | 0.0116 | 0.5029 | 0.1785 | bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf |
| 7 | 0.0062 | 0.5016 | 0.1331 | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |
| 8 | 0.0060 | 0.5015 | 0.1442 | yabancı_dil_eğitim_öğretimi_yönergesi.pdf |
| 9 | 0.0057 | 0.5014 | 0.1316 | lisansüstü_eğitim_ve.pdf |
| 10 | 0.0055 | 0.5014 | 0.1300 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |

### Bagil degerlendirme sistemi nasil isler?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.0015 | 0.5004 | -0.0565 | tıp_fakültesi_tıp_doktorluğu_programı.pdf |
| 2 | 0.0011 | 0.5003 | -0.1397 | risk_ve_fırsat_yönetimi_prosedürü.pdf |
| 3 | 0.0008 | 0.5002 | -0.1210 | eğitim_öğretim_perfomansını_değerlendirme_prosedürü.pdf |
| 4 | 0.0004 | 0.5001 | -0.1290 | personel_performans_değerlendirme_yönergesi.pdf |
| 5 | 0.0004 | 0.5001 | 0.0000 | bilgi_güvenliği_yedekleme_prosedürü.pdf |
| 6 | 0.0002 | 0.5001 | -0.1154 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.0001 | 0.5000 | -0.0269 | satın_alma_prosedürü.pdf |
| 8 | 0.0001 | 0.5000 | 0.0000 | eğitim_öğretim_perfomansını_değerlendirme_prosedürü.pdf |
| 9 | 0.0001 | 0.5000 | 0.0000 | sağlık_uygulama_ve_araştırma_merkezi_tıp_laboratuvarları_yönergesi.pdf |
| 10 | 0.0001 | 0.5000 | -0.1366 | eğitim_öğretim_perfomansını_değerlendirme_prosedürü.pdf |

### Final sinavina girme sarti olarak devam yuzdesi kac olmalidir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.0507 | 0.5127 | 0.0000 | yabancı_dil_eğitim_öğretimi_yönergesi.pdf |
| 2 | 0.0263 | 0.5066 | 0.0000 | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |
| 3 | 0.0142 | 0.5036 | 0.1643 | yabancı_dil_eğitim_öğretimi_yönergesi.pdf |
| 4 | 0.0107 | 0.5027 | 0.0000 | yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf |
| 5 | 0.0036 | 0.5009 | 0.1481 | sürekli_eğitim_merkezi_yönergesi.pdf |
| 6 | 0.0027 | 0.5007 | 0.0000 | lisansüstü_eğitim_ve.pdf |
| 7 | 0.0027 | 0.5007 | 0.0000 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 8 | 0.0011 | 0.5003 | 0.0000 | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |
| 9 | 0.0011 | 0.5003 | 0.1564 | tıp_fakültesi_tıp_doktorluğu_programı.pdf |
| 10 | 0.0010 | 0.5002 | 0.1671 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |

### Not itirazi icin ne kadar sureye sahibim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.0676 | 0.5169 | 0.1463 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 2 | 0.0614 | 0.5154 | 0.2518 | yonerge_yuzde_on_basari_degerlendirme.pdf |
| 3 | 0.0587 | 0.5147 | 0.2317 | sık_sorulan_sorular.txt |
| 4 | 0.0473 | 0.5118 | 0.0910 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 5 | 0.0224 | 0.5056 | 0.1032 | ön_lisans_ve_lisans.pdf |
| 6 | 0.0193 | 0.5048 | 0.1621 | ders_yeterlilik_sınavı_uygulama_yönergesi.pdf |
| 7 | 0.0131 | 0.5033 | 0.0623 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 8 | 0.0038 | 0.5009 | 0.1875 | sık_sorulan_sorular.txt |
| 9 | 0.0011 | 0.5003 | 0.0990 | öğrenci_konukevi_uygulama_yönergesi.pdf |
| 10 | 0.0010 | 0.5003 | 0.0393 | ön_lisans_ve_lisans.pdf |

### Yaz okulunda en fazla kac ders alabilirim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.9891 | 0.7289 | 0.0000 | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 2 | 0.9842 | 0.7279 | 0.0000 | yaz_okulu_eğitim_öğretim.pdf |
| 3 | 0.9093 | 0.7128 | 0.0000 | yonerge_yaz_okulu_egitim_ogretim.pdf |
| 4 | 0.8808 | 0.7070 | 0.3979 | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 5 | 0.8743 | 0.7056 | 0.0000 | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 6 | 0.5356 | 0.6308 | 0.3914 | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.1689 | 0.5421 | 0.0000 | yaz_okulu_eğitim_öğretim.pdf |
| 8 | 0.1689 | 0.5421 | 0.0000 | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 9 | 0.0810 | 0.5202 | 0.0000 | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 10 | 0.0771 | 0.5193 | 0.0000 | yonerge_yaz_okulu_egitim_ogretim.pdf |

### Basarisiz oldugum dersi tekrar almak icin ne yapmaliyim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.4332 | 0.6066 | 0.0000 | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 2 | 0.3500 | 0.5866 | 0.1909 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.3131 | 0.5776 | 0.0000 | sık_sorulan_sorular.txt |
| 4 | 0.2894 | 0.5718 | 0.1713 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 5 | 0.2811 | 0.5698 | 0.3475 | sık_sorulan_sorular.txt |
| 6 | 0.2615 | 0.5650 | 0.0000 | sık_sorulan_sorular.txt |
| 7 | 0.1504 | 0.5375 | 0.0000 | sık_sorulan_sorular.txt |
| 8 | 0.1367 | 0.5341 | 0.0000 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 9 | 0.1160 | 0.5290 | 0.1671 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.1112 | 0.5278 | 0.2356 | sık_sorulan_sorular.txt |

### Azami ogrenim suresi dolunca ne olur?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.0423 | 0.5106 | 0.0000 | yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf |
| 2 | 0.0108 | 0.5027 | 0.0000 | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 3 | 0.0089 | 0.5022 | 0.0000 | lisansüstü_eğitim_ve.pdf |
| 4 | 0.0085 | 0.5021 | 0.0000 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 5 | 0.0032 | 0.5008 | 0.0000 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 6 | 0.0030 | 0.5008 | 0.0000 | lisansüstü_eğitim_ve.pdf |
| 7 | 0.0024 | 0.5006 | -0.0466 | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 8 | 0.0019 | 0.5005 | 0.0000 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 9 | 0.0019 | 0.5005 | 0.0000 | lisansüstü_eğitim_ve.pdf |
| 10 | 0.0016 | 0.5004 | 0.0000 | tıpta_uzmanlık_eğitimi_yönergesi.pdf |

### Donem dondurma icin saglik raporu yeterli mi?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.0154 | 0.5038 | 0.0000 | ön_lisans_ve_lisans.pdf |
| 2 | 0.0042 | 0.5010 | 0.0477 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 3 | 0.0015 | 0.5004 | 0.0000 | staj_yönergesi.pdf |
| 4 | 0.0008 | 0.5002 | 0.0000 | 1_elektrik_elektronik_staj_ilkeleri_ve_uygulama_esasları.pdf |
| 5 | 0.0007 | 0.5002 | 0.0249 | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 6 | 0.0007 | 0.5002 | 0.0000 | sık_sorulan_sorular.txt |
| 7 | 0.0007 | 0.5002 | 0.0000 | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 8 | 0.0006 | 0.5002 | 0.0000 | staj_esaslar.pdf |
| 9 | 0.0006 | 0.5001 | 0.0000 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0006 | 0.5001 | -0.0460 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |

### Mezuniyet icin GNO en az kac olmalidir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.2724 | 0.5677 | 0.0000 | ön_lisans_ve_lisans.pdf |
| 2 | 0.1926 | 0.5480 | 0.2774 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.0657 | 0.5164 | 0.2623 | ön_lisans_ve_lisans.pdf |
| 4 | 0.0242 | 0.5060 | 0.0000 | ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf |
| 5 | 0.0087 | 0.5022 | 0.0000 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 6 | 0.0070 | 0.5017 | 0.0000 | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.0064 | 0.5016 | 0.0000 | ön_lisans_ve_lisans.pdf |
| 8 | 0.0046 | 0.5011 | 0.0000 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 9 | 0.0036 | 0.5009 | 0.0000 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 10 | 0.0031 | 0.5008 | 0.0000 | yaz_okulu_eğitim_öğretim.pdf |

### Zorunlu staj icin SGK baslangic islemleri nasil yapilir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.1726 | 0.5430 | 0.0000 | staj_iş_akışı.pdf |
| 2 | 0.1399 | 0.5349 | 0.0000 | staj_bilgilendirme_toplantısı_sunumu_2024_2025.pdf |
| 3 | 0.0605 | 0.5151 | 0.0000 | zorunlu_stajda_izlenecek_yol.pdf |
| 4 | 0.0401 | 0.5100 | 0.1819 | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 5 | 0.0276 | 0.5069 | 0.0000 | document.pdf |
| 6 | 0.0260 | 0.5065 | 0.0000 | document.pdf |
| 7 | 0.0105 | 0.5026 | 0.0000 | 1_elektrik_elektronik_staj_ilkeleri_ve_uygulama_esasları.pdf |
| 8 | 0.0103 | 0.5026 | 0.0000 | staj_esaslar.pdf |
| 9 | 0.0092 | 0.5023 | 0.0000 | staj_ilkeleri_23122019_inş_müh.pdf |
| 10 | 0.0088 | 0.5022 | 0.2030 | staj_iş_akışı.pdf |

### Staj defterini teslim etme suresi ne kadardir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.4971 | 0.6218 | 0.0000 | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 2 | 0.4384 | 0.6079 | 0.0000 | staj_esaslar.pdf |
| 3 | 0.2009 | 0.5501 | 0.2555 | 1_elektrik_elektronik_staj_ilkeleri_ve_uygulama_esasları.pdf |
| 4 | 0.2009 | 0.5501 | 0.0000 | staj_bilgilendirme_toplantısı_sunumu_2024_2025.pdf |
| 5 | 0.1417 | 0.5354 | 0.2318 | zorunlu_stajda_izlenecek_yol.pdf |
| 6 | 0.0991 | 0.5247 | 0.2424 | zorunlu_gönüllü_staj_başvuru_formu.pdf |
| 7 | 0.0952 | 0.5238 | 0.0000 | staj_yönergesi.pdf |
| 8 | 0.0739 | 0.5185 | 0.0000 | staj_sıkça_sorulanlar.pdf |
| 9 | 0.0667 | 0.5167 | 0.0000 | 1_elektrik_elektronik_staj_ilkeleri_ve_uygulama_esasları.pdf |
| 10 | 0.0636 | 0.5159 | 0.0000 | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |

### Bitirme projesi danismani nasil belirlenir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.0622 | 0.5155 | 0.0000 | endüstri_mühendisliği_tasarımı_yaptırma_ve_değerlendirme_ı̇lkeleri_güncel.pdf |
| 2 | 0.0408 | 0.5102 | -0.0250 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 3 | 0.0258 | 0.5065 | 0.0000 | mat_bitirme_çalışması_ilkeleri.pdf |
| 4 | 0.0222 | 0.5056 | 0.0000 | mat_bitirme_çalışması_ilkeleri.pdf |
| 5 | 0.0176 | 0.5044 | 0.0000 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 6 | 0.0154 | 0.5039 | 0.0000 | bağıl_değerlendirme_yönergesi.pdf |
| 7 | 0.0153 | 0.5038 | 0.0000 | mat_bitirme_çalışması_ilkeleri.pdf |
| 8 | 0.0092 | 0.5023 | 0.0092 | mat_bitirme_çalışması_ilkeleri.pdf |
| 9 | 0.0056 | 0.5014 | -0.0466 | mat_bitirme_çalışması_ilkeleri.pdf |
| 10 | 0.0054 | 0.5014 | 0.0000 | mup_ilke_ve_esasları.pdf |

### Staj yerim degisirse ne yapmaliyim?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.3438 | 0.5851 | 0.3340 | zorunlu_gönüllü_staj_başvuru_formu.pdf |
| 2 | 0.0501 | 0.5125 | 0.2707 | staj_esaslar.pdf |
| 3 | 0.0408 | 0.5102 | 0.0000 | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 4 | 0.0366 | 0.5091 | 0.0000 | staj_yönergesi.pdf |
| 5 | 0.0273 | 0.5068 | 0.3189 | işyeri_staj_sözleşmesi.pdf |
| 6 | 0.0192 | 0.5048 | 0.0000 | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 7 | 0.0149 | 0.5037 | 0.2875 | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |
| 8 | 0.0130 | 0.5033 | 0.0000 | 1_elektrik_elektronik_staj_ilkeleri_ve_uygulama_esasları.pdf |
| 9 | 0.0092 | 0.5023 | 0.0000 | staj_yönergesi.pdf |
| 10 | 0.0079 | 0.5020 | 0.2622 | işyeri_staj_sözleşmesi.pdf |

### Lisansustu ogrenciler icin tez teslim suresi ne kadardir?

| # | Ham Skor | Sigmoid | Pre-Rerank | Kaynak |
|:-:|:--------:|:-------:|:----------:|--------|
| 1 | 0.4553 | 0.6119 | 0.0000 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 2 | 0.3498 | 0.5866 | 0.0000 | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 3 | 0.2115 | 0.5527 | 0.0000 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 4 | 0.2112 | 0.5526 | 0.0000 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 5 | 0.2094 | 0.5522 | 0.2441 | lisansüstü_eğitim_ve.pdf |
| 6 | 0.1766 | 0.5440 | 0.2280 | lisansüstü_eğitim_ve.pdf |
| 7 | 0.1710 | 0.5427 | 0.0000 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 8 | 0.1201 | 0.5300 | 0.0000 | lisansüstü_eğitim_ve.pdf |
| 9 | 0.1088 | 0.5272 | 0.2595 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 10 | 0.0906 | 0.5226 | 0.0000 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |

---

*Bu rapor `scripts/analyze_reranker_scores.py` tarafindan otomatik uretilmistir.*