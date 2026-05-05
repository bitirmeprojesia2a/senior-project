# Reranker Skor Dagilim Analizi

**Tarih:** 2026-05-03 23:46
**Model:** BAAI/bge-reranker-v2-m3
**Kalibrasyon:** shift=0.0, scale=1.0
**Toplam Soru:** 40
**Toplam Skor Ornegi:** 400
**Kapsam:** Candidate pool + reranker analizi; final threshold/filtering adimlari buna dahil degildir.

---

## Tum Skorlar (Tum Adaylar)

### Ham Reranker Skorlari (Logit)

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.0 |
| p10 | 0.0004 |
| p25 | 0.0084 |
| median | 0.0652 |
| mean | 0.2296 |
| p75 | 0.3426 |
| p90 | 0.8765 |
| max | 1.0 |
| std | 0.3115 |

### Kalibre Edilmis Skorlar (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.5 |
| p10 | 0.5001 |
| p25 | 0.5021 |
| median | 0.5163 |
| mean | 0.5551 |
| p75 | 0.5848 |
| p90 | 0.7061 |
| max | 0.7311 |
| std | 0.0731 |

### Duz Sigmoid Skorlar (Referans)

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.5 |
| p10 | 0.5001 |
| p25 | 0.5021 |
| median | 0.5163 |
| mean | 0.5551 |
| p75 | 0.5848 |
| p90 | 0.7061 |
| max | 0.7311 |
| std | 0.0731 |

---

## Top-1 Skorlar (Her Sorunun En Iyi Adayi)

### Ham Top-1 Skorlari (Logit)

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.0 |
| p10 | 0.0424 |
| p25 | 0.2983 |
| median | 0.6799 |
| mean | 0.6219 |
| p75 | 0.9886 |
| p90 | 0.9968 |
| max | 1.0 |
| std | 0.3816 |

### Kalibre Top-1 Skorlari (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.5 |
| p10 | 0.5106 |
| p25 | 0.574 |
| median | 0.6636 |
| mean | 0.6461 |
| p75 | 0.7288 |
| p90 | 0.7304 |
| max | 0.7311 |
| std | 0.0876 |

### Duz Sigmoid Top-1 Skorlari (Referans)

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.5 |
| p10 | 0.5106 |
| p25 | 0.574 |
| median | 0.6636 |
| mean | 0.6461 |
| p75 | 0.7288 |
| p90 | 0.7304 |
| max | 0.7311 |
| std | 0.0876 |

---

## Sigmoid Kalibrasyon Onerisi

- **Formul:** `sigmoid((score - 0.0652) / 0.5000)`
- **Shift (median):** 0.0652
- **Scale (IQR):** 0.5
- **Onerilen direct-RAG esigi:** 0.635
- **Onerilen min-source esigi:** 0.472

---

## Soru Bazli Detaylar

### Sistem giris sifremi unuttum, ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9883 | 0.7287 | 0.7287 | sık_sorulan_sorular.txt |
| 2 | 0.0042 | 0.5011 | 0.5011 | öğrenci_toplulukları_yönergesi.pdf |
| 3 | 0.0009 | 0.5002 | 0.5002 | sık_sorulan_sorular.txt |
| 4 | 0.0009 | 0.5002 | 0.5002 | sık_sorulan_sorular.txt |
| 5 | 0.0007 | 0.5002 | 0.5002 | sık_sorulan_sorular.txt |
| 6 | 0.0005 | 0.5001 | 0.5001 | öğrenci_işleri_birimi.txt |
| 7 | 0.0004 | 0.5001 | 0.5001 | kimlik_kartı_yönergesi.pdf |
| 8 | 0.0003 | 0.5001 | 0.5001 | kimlik_kartı_yönergesi.pdf |
| 9 | 0.0003 | 0.5001 | 0.5001 | öğrenci_işleri_birimi.txt |
| 10 | 0.0003 | 0.5001 | 0.5001 | sık_sorulan_sorular.txt |

### UBYS uzerinden ilisik kesme talebini nasil baslatirim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9941 | 0.7299 | 0.7299 | sık_sorulan_sorular.txt |
| 2 | 0.9526 | 0.7216 | 0.7216 | sık_sorulan_sorular.txt |
| 3 | 0.2417 | 0.5601 | 0.5601 | kimlik_kartı_yönergesi.pdf |
| 4 | 0.0346 | 0.5087 | 0.5087 | öğrenci_işleri_birimi.txt |
| 5 | 0.0182 | 0.5045 | 0.5045 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.0093 | 0.5023 | 0.5023 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 7 | 0.0091 | 0.5023 | 0.5023 | öğrenci_işleri_birimi.txt |
| 8 | 0.0046 | 0.5011 | 0.5011 | sık_sorulan_sorular.txt |
| 9 | 0.0019 | 0.5005 | 0.5005 | sık_sorulan_sorular.txt |
| 10 | 0.0019 | 0.5005 | 0.5005 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |

### Diplomami kaybettim, ikinci nusha icin ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9990 | 0.7309 | 0.7309 | sık_sorulan_sorular.txt |
| 2 | 0.9766 | 0.7264 | 0.7264 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 3 | 0.1549 | 0.5386 | 0.5386 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 4 | 0.1140 | 0.5285 | 0.5285 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 5 | 0.0370 | 0.5093 | 0.5093 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 6 | 0.0126 | 0.5032 | 0.5032 | sık_sorulan_sorular.txt |
| 7 | 0.0024 | 0.5006 | 0.5006 | sık_sorulan_sorular.txt |
| 8 | 0.0014 | 0.5003 | 0.5003 | sık_sorulan_sorular.txt |
| 9 | 0.0013 | 0.5003 | 0.5003 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 10 | 0.0012 | 0.5003 | 0.5003 | sık_sorulan_sorular.txt |

### Diploma eki transkript yerine gecer mi?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9995 | 0.7310 | 0.7310 | sık_sorulan_sorular.txt |
| 2 | 0.4294 | 0.6057 | 0.6057 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 3 | 0.1815 | 0.5453 | 0.5453 | sık_sorulan_sorular.txt |
| 4 | 0.0319 | 0.5080 | 0.5080 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 5 | 0.0217 | 0.5054 | 0.5054 | sık_sorulan_sorular.txt |
| 6 | 0.0179 | 0.5045 | 0.5045 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 7 | 0.0105 | 0.5026 | 0.5026 | sık_sorulan_sorular.txt |
| 8 | 0.0093 | 0.5023 | 0.5023 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 9 | 0.0084 | 0.5021 | 0.5021 | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 10 | 0.0063 | 0.5016 | 0.5016 | sık_sorulan_sorular.txt |

### Kayit dondurma ile kayit yaptirmamak arasinda ne fark var?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9810 | 0.7273 | 0.7273 | sık_sorulan_sorular.txt |
| 2 | 0.2849 | 0.5707 | 0.5707 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 3 | 0.2737 | 0.5680 | 0.5680 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 4 | 0.0779 | 0.5195 | 0.5195 | sık_sorulan_sorular.txt |
| 5 | 0.0737 | 0.5184 | 0.5184 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 6 | 0.0441 | 0.5110 | 0.5110 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 7 | 0.0408 | 0.5102 | 0.5102 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 8 | 0.0234 | 0.5058 | 0.5058 | öğrenci_konseyi_yönergesi.pdf |
| 9 | 0.0180 | 0.5045 | 0.5045 | sık_sorulan_sorular.txt |
| 10 | 0.0138 | 0.5035 | 0.5035 | ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf |

### Hazirlik sinifi okuyan ogrenci transkriptsiz Ek Madde-1 ile yatay gecis basvurusu yapabilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9009 | 0.7111 | 0.7111 | sık_sorulan_sorular.txt |
| 2 | 0.7285 | 0.6745 | 0.6745 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 3 | 0.5156 | 0.6261 | 0.6261 | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 4 | 0.2837 | 0.5705 | 0.5705 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 5 | 0.2588 | 0.5643 | 0.5643 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 6 | 0.2218 | 0.5552 | 0.5552 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 7 | 0.1882 | 0.5469 | 0.5469 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 8 | 0.1766 | 0.5440 | 0.5440 | sık_sorulan_sorular.txt |
| 9 | 0.1592 | 0.5397 | 0.5397 | sık_sorulan_sorular.txt |
| 10 | 0.0457 | 0.5114 | 0.5114 | ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf |

### Birden fazla universiteye yatay gecis basvurusu yapabilir miyim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9966 | 0.7304 | 0.7304 | sık_sorulan_sorular.txt |
| 2 | 0.1664 | 0.5415 | 0.5415 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 3 | 0.1648 | 0.5411 | 0.5411 | sık_sorulan_sorular.txt |
| 4 | 0.0873 | 0.5218 | 0.5218 | sık_sorulan_sorular.txt |
| 5 | 0.0299 | 0.5075 | 0.5075 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.0220 | 0.5055 | 0.5055 | ön_lisans_ve_lisans.pdf |
| 7 | 0.0172 | 0.5043 | 0.5043 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 8 | 0.0144 | 0.5036 | 0.5036 | sık_sorulan_sorular.txt |
| 9 | 0.0136 | 0.5034 | 0.5034 | ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf |
| 10 | 0.0095 | 0.5024 | 0.5024 | yonerge_onlisans_lisans_yatay_gecis.pdf |

### Ozel ogrenci olarak ne zaman basvuru yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.7266 | 0.6741 | 0.6741 | sık_sorulan_sorular.txt |
| 2 | 0.2301 | 0.5573 | 0.5573 | sık_sorulan_sorular.txt |
| 3 | 0.1025 | 0.5256 | 0.5256 | sık_sorulan_sorular.txt |
| 4 | 0.0282 | 0.5070 | 0.5070 | sık_sorulan_sorular.txt |
| 5 | 0.0022 | 0.5005 | 0.5005 | sık_sorulan_sorular.txt |
| 6 | 0.0007 | 0.5002 | 0.5002 | sık_sorulan_sorular.txt |
| 7 | 0.0006 | 0.5002 | 0.5002 | yonerge_yaz_okulu_egitim_ogretim.pdf |
| 8 | 0.0006 | 0.5002 | 0.5002 | sık_sorulan_sorular.txt |
| 9 | 0.0005 | 0.5001 | 0.5001 | sık_sorulan_sorular.txt |
| 10 | 0.0005 | 0.5001 | 0.5001 | öğrenci_toplulukları_yönergesi.pdf |

### Ozel ogrenci olarak basvuru icin hangi belgeler gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.6118 | 0.6484 | 0.6484 | sık_sorulan_sorular.txt |
| 2 | 0.3889 | 0.5960 | 0.5960 | sık_sorulan_sorular.txt |
| 3 | 0.3735 | 0.5923 | 0.5923 | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 4 | 0.3225 | 0.5799 | 0.5799 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 5 | 0.2922 | 0.5725 | 0.5725 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 6 | 0.0947 | 0.5236 | 0.5236 | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 7 | 0.0732 | 0.5183 | 0.5183 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 8 | 0.0679 | 0.5170 | 0.5170 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 9 | 0.0578 | 0.5144 | 0.5144 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 10 | 0.0577 | 0.5144 | 0.5144 | sık_sorulan_sorular.txt |

### Daha once aldigim dersler icin muafiyet basvurusunu ne zaman yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9736 | 0.7258 | 0.7258 | sık_sorulan_sorular.txt |
| 2 | 0.9199 | 0.7150 | 0.7150 | yonerge_ders_yeterlik_muafiyet_intibak.pdf |
| 3 | 0.8633 | 0.7033 | 0.7033 | sık_sorulan_sorular.txt |
| 4 | 0.4211 | 0.6038 | 0.6038 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 5 | 0.3699 | 0.5914 | 0.5914 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 6 | 0.3464 | 0.5858 | 0.5858 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 7 | 0.3396 | 0.5841 | 0.5841 | yonerge_ders_yeterlik_muafiyet_intibak.pdf |
| 8 | 0.1636 | 0.5408 | 0.5408 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 9 | 0.1432 | 0.5357 | 0.5357 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 10 | 0.1306 | 0.5326 | 0.5326 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |

### Ikamet izni basvurusu icin hangi belgeler gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9863 | 0.7284 | 0.7284 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 2 | 0.9551 | 0.7221 | 0.7221 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 3 | 0.9502 | 0.7212 | 0.7212 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 4 | 0.8901 | 0.7089 | 0.7089 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 5 | 0.8574 | 0.7021 | 0.7021 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 6 | 0.7832 | 0.6864 | 0.6864 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 7 | 0.6758 | 0.6628 | 0.6628 | uluslararası_öğrenci_ikamet_işlemleri.pdf |
| 8 | 0.5747 | 0.6398 | 0.6398 | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 9 | 0.5674 | 0.6382 | 0.6382 | uluslararası_öğrenci.pdf |
| 10 | 0.4866 | 0.6193 | 0.6193 | muvafakatname.pdf |

### Denklik belgesi ne zaman gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9492 | 0.7210 | 0.7210 | denklik_belgesi.pdf |
| 2 | 0.7114 | 0.6707 | 0.6707 | denklik_belgesi.pdf |
| 3 | 0.3599 | 0.5890 | 0.5890 | tyb.pdf |
| 4 | 0.3359 | 0.5832 | 0.5832 | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 5 | 0.2742 | 0.5681 | 0.5681 | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 6 | 0.0848 | 0.5212 | 0.5212 | uluslararası_öğrenci.pdf |
| 7 | 0.0584 | 0.5146 | 0.5146 | lisansüstü_eğitim_ve.pdf |
| 8 | 0.0563 | 0.5141 | 0.5141 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 9 | 0.0537 | 0.5134 | 0.5134 | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |
| 10 | 0.0258 | 0.5064 | 0.5064 | yurda_giriş_çıkış_belgesi.pdf |

### YOS ID numarami nasil ogrenebilirim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.0332 | 0.5083 | 0.5083 | uluslararası_öğrenci.pdf |
| 2 | 0.0231 | 0.5058 | 0.5058 | yös_ıd_no_öğrenme.pdf |
| 3 | 0.0203 | 0.5051 | 0.5051 | öğrenci_no_öğrenme.pdf |
| 4 | 0.0015 | 0.5004 | 0.5004 | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 5 | 0.0013 | 0.5003 | 0.5003 | ön_kayıt_kılavuzu_başvuru_adımları.pdf |
| 6 | 0.0007 | 0.5002 | 0.5002 | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 7 | 0.0007 | 0.5002 | 0.5002 | yonerge_uluslararasi_ogrenci_yatay_gecis.pdf |
| 8 | 0.0005 | 0.5001 | 0.5001 | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 9 | 0.0005 | 0.5001 | 0.5001 | uluslararası_öğrenci_kimlik_bilgileri_güncelleme_formu.pdf |
| 10 | 0.0004 | 0.5001 | 0.5001 | özel_yetenek_sınavı_yönergesi.pdf |

### Uluslararasi ogrenci kaydinda evrak teslim formu gerekiyor mu?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9858 | 0.7283 | 0.7283 | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 2 | 0.9839 | 0.7279 | 0.7279 | ön_lisans_ve_lisans_programları.pdf |
| 3 | 0.9619 | 0.7235 | 0.7235 | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 4 | 0.9072 | 0.7124 | 0.7124 | uluslararası_öğrenci_evrak_teslim_formu_r1.pdf |
| 5 | 0.8687 | 0.7045 | 0.7045 | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 6 | 0.4834 | 0.6186 | 0.6186 | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 7 | 0.4675 | 0.6148 | 0.6148 | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 8 | 0.1615 | 0.5403 | 0.5403 | uluslararası_öğrenci.pdf |
| 9 | 0.1368 | 0.5342 | 0.5342 | ön_kayıt_kılavuzu_başvuru_adımları.pdf |
| 10 | 0.1195 | 0.5298 | 0.5298 | uluslararası_öğrenci.pdf |

### TOMER ne is yapar?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.0426 | 0.5107 | 0.5107 | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 2 | 0.0003 | 0.5001 | 0.5001 | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 3 | 0.0003 | 0.5001 | 0.5001 | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 4 | 0.0002 | 0.5001 | 0.5001 | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 5 | 0.0002 | 0.5001 | 0.5001 | kök_hücre_araştırma_merkezi_yönergesi.pdf |
| 6 | 0.0002 | 0.5000 | 0.5000 | lisans_ders_i_erik_2022_2023_den_itibaren_ge_erli_olan.pdf |
| 7 | 0.0001 | 0.5000 | 0.5000 | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 8 | 0.0001 | 0.5000 | 0.5000 | siber_güvenlik_ve_bilişim_teknolojileri.pdf |
| 9 | 0.0001 | 0.5000 | 0.5000 | kariyer_merkezi_yönergesi.pdf |
| 10 | 0.0001 | 0.5000 | 0.5000 | güvenlik_hizmetlerinin_yürütülmesine_dair_yönerge.pdf |

### Pedagojik formasyon dersleri transkripte dahil edilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 1.0000 | 0.7311 | 0.7311 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.9951 | 0.7301 | 0.7301 | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 3 | 0.9873 | 0.7286 | 0.7286 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 4 | 0.5254 | 0.6284 | 0.6284 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 5 | 0.3271 | 0.5811 | 0.5811 | yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf |
| 6 | 0.2883 | 0.5716 | 0.5716 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.2478 | 0.5616 | 0.5616 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 8 | 0.2157 | 0.5537 | 0.5537 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 9 | 0.1805 | 0.5450 | 0.5450 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 10 | 0.1583 | 0.5395 | 0.5395 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |

### Pedagojik formasyon mezuniyet ortalamasina dahil edilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9961 | 0.7303 | 0.7303 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.9927 | 0.7296 | 0.7296 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 3 | 0.9033 | 0.7116 | 0.7116 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 4 | 0.7388 | 0.6767 | 0.6767 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.6128 | 0.6486 | 0.6486 | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 6 | 0.5376 | 0.6313 | 0.6313 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.3782 | 0.5934 | 0.5934 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 8 | 0.2844 | 0.5706 | 0.5706 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.2627 | 0.5653 | 0.5653 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.2568 | 0.5639 | 0.5639 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |

### Pedagojik formasyon alirsam mezuniyet 240 AKTS'nin ustune cikabilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9985 | 0.7308 | 0.7308 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.8486 | 0.7003 | 0.7003 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 3 | 0.6641 | 0.6602 | 0.6602 | yonerge_cift_anadal_yandal.pdf |
| 4 | 0.1874 | 0.5467 | 0.5467 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 5 | 0.1852 | 0.5462 | 0.5462 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 6 | 0.1481 | 0.5370 | 0.5370 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 7 | 0.1213 | 0.5303 | 0.5303 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 8 | 0.0964 | 0.5241 | 0.5241 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.0827 | 0.5207 | 0.5207 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.0518 | 0.5130 | 0.5130 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |

### Pedagojik formasyon derslerinin tumunu almak zorunlu mu?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9951 | 0.7301 | 0.7301 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.5366 | 0.6310 | 0.6310 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 3 | 0.3562 | 0.5881 | 0.5881 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 4 | 0.3525 | 0.5872 | 0.5872 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 5 | 0.3389 | 0.5839 | 0.5839 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 6 | 0.3323 | 0.5823 | 0.5823 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 7 | 0.3081 | 0.5764 | 0.5764 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 8 | 0.2263 | 0.5563 | 0.5563 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 9 | 0.1166 | 0.5291 | 0.5291 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.0988 | 0.5247 | 0.5247 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |

### Pedagojik formasyon dersleri en erken hangi yariyilda alinabilir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9604 | 0.7232 | 0.7232 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 2 | 0.8833 | 0.7075 | 0.7075 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 3 | 0.8765 | 0.7061 | 0.7061 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 4 | 0.6743 | 0.6625 | 0.6625 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.6294 | 0.6524 | 0.6524 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 6 | 0.5801 | 0.6411 | 0.6411 | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 7 | 0.5127 | 0.6254 | 0.6254 | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 8 | 0.4062 | 0.6002 | 0.6002 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 9 | 0.3914 | 0.5966 | 0.5966 | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 10 | 0.3435 | 0.5850 | 0.5850 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |

### Yemek bursu basvurulari nereden yapilir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9897 | 0.7290 | 0.7290 | öğrenci_yemek_bursu_yönergesi.pdf |
| 2 | 0.9014 | 0.7112 | 0.7112 | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.6748 | 0.6626 | 0.6626 | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.3799 | 0.5938 | 0.5938 | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.2090 | 0.5521 | 0.5521 | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.2064 | 0.5514 | 0.5514 | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.1248 | 0.5311 | 0.5311 | kimlik_kartı_yönergesi.pdf |
| 8 | 0.0930 | 0.5232 | 0.5232 | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0808 | 0.5202 | 0.5202 | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0628 | 0.5157 | 0.5157 | öğrenci_yemek_bursu_yönergesi.pdf |

### Bursum hangi sartlarda kesilir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.0677 | 0.5169 | 0.5169 | öğrenci_yemek_bursu_yönergesi.pdf |
| 2 | 0.0546 | 0.5136 | 0.5136 | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.0020 | 0.5005 | 0.5005 | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.0011 | 0.5003 | 0.5003 | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.0009 | 0.5002 | 0.5002 | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.0009 | 0.5002 | 0.5002 | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.0008 | 0.5002 | 0.5002 | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0008 | 0.5002 | 0.5002 | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0008 | 0.5002 | 0.5002 | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0004 | 0.5001 | 0.5001 | öğrenci_yemek_bursu_yönergesi.pdf |

### Kayit ekraninda borclu ya da fazla ucretli gorunuyorsam ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.0000 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 2 | 0.0000 | 0.5000 | 0.5000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.0000 | 0.5000 | 0.5000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.0000 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 5 | 0.0000 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 6 | 0.0000 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 7 | 0.0000 | 0.5000 | 0.5000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0000 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 9 | 0.0000 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 10 | 0.0000 | 0.5000 | 0.5000 | öğrenci_yemek_bursu_yönergesi.pdf |

### Program suresini asarsam katki payi oder miyim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.0533 | 0.5133 | 0.5133 | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |
| 2 | 0.0014 | 0.5003 | 0.5003 | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |
| 3 | 0.0001 | 0.5000 | 0.5000 | 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf |
| 4 | 0.0001 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 5 | 0.0001 | 0.5000 | 0.5000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.0001 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 7 | 0.0001 | 0.5000 | 0.5000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0001 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 9 | 0.0000 | 0.5000 | 0.5000 | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0000 | 0.5000 | 0.5000 | öğrenci_yemek_bursu_yönergesi.pdf |

### Harc iadesi icin IBAN ve dekontla nereye basvurmam gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.0000 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 2 | 0.0000 | 0.5000 | 0.5000 | idari_ve_mali_işler_birimi.txt |
| 3 | 0.0000 | 0.5000 | 0.5000 | 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf |
| 4 | 0.0000 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 5 | 0.0000 | 0.5000 | 0.5000 | idari_ve_mali_işler_birimi.txt |
| 6 | 0.0000 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 7 | 0.0000 | 0.5000 | 0.5000 | 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf |
| 8 | 0.0000 | 0.5000 | 0.5000 | idari_ve_mali_işler_birimi.txt |
| 9 | 0.0000 | 0.5000 | 0.5000 | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 10 | 0.0000 | 0.5000 | 0.5000 | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |

### Sinava giremedigim ders icin mazeret sinavi basvurusu nasil yapilir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.4504 | 0.6107 | 0.6107 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 2 | 0.3987 | 0.5984 | 0.5984 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.2600 | 0.5646 | 0.5646 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 4 | 0.2203 | 0.5549 | 0.5549 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 5 | 0.0899 | 0.5225 | 0.5225 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 6 | 0.0536 | 0.5134 | 0.5134 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.0439 | 0.5110 | 0.5110 | sık_sorulan_sorular.txt |
| 8 | 0.0339 | 0.5085 | 0.5085 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 9 | 0.0204 | 0.5051 | 0.5051 | ön_lisans_ve_lisans.pdf |
| 10 | 0.0077 | 0.5019 | 0.5019 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |

### Bir dersten kac kez sinav hakkina sahibim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.3459 | 0.5856 | 0.5856 | yonerge_uzaktan_egitim_onlisans_lisans.pdf |
| 2 | 0.2397 | 0.5597 | 0.5597 | uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf |
| 3 | 0.0583 | 0.5146 | 0.5146 | mühendislik_fakültesi_ortak_sınav_yönergesi.pdf |
| 4 | 0.0557 | 0.5139 | 0.5139 | uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf |
| 5 | 0.0130 | 0.5033 | 0.5033 | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |
| 6 | 0.0113 | 0.5028 | 0.5028 | bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf |
| 7 | 0.0109 | 0.5027 | 0.5027 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 8 | 0.0090 | 0.5023 | 0.5023 | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 9 | 0.0082 | 0.5020 | 0.5020 | yabancı_dil_eğitim_öğretimi_yönergesi.pdf |
| 10 | 0.0079 | 0.5020 | 0.5020 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |

### Bagil degerlendirme sistemi nasil isler?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.2440 | 0.5607 | 0.5607 | bağıl_değerlendirme_yönergesi.pdf |
| 2 | 0.0850 | 0.5212 | 0.5212 | bağıl_değerlendirme_yönergesi.pdf |
| 3 | 0.0847 | 0.5212 | 0.5212 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 4 | 0.0828 | 0.5207 | 0.5207 | ön_lisans_ve_lisans.pdf |
| 5 | 0.0314 | 0.5078 | 0.5078 | yonerge_bagil_degerlendirme.pdf |
| 6 | 0.0302 | 0.5075 | 0.5075 | bağıl_değerlendirme_yönergesi.pdf |
| 7 | 0.0235 | 0.5059 | 0.5059 | bağıl_değerlendirme_yönergesi.pdf |
| 8 | 0.0154 | 0.5038 | 0.5038 | sık_sorulan_sorular.txt |
| 9 | 0.0087 | 0.5022 | 0.5022 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0070 | 0.5018 | 0.5018 | bağıl_değerlendirme_yönergesi.pdf |

### Final sinavina girme sarti olarak devam yuzdesi kac olmalidir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.0557 | 0.5139 | 0.5139 | yonerge_yabanci_dil_egitim_ogretim.pdf |
| 2 | 0.0296 | 0.5074 | 0.5074 | yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf |
| 3 | 0.0188 | 0.5047 | 0.5047 | yabancı_dil_eğitim_öğretimi_yönergesi.pdf |
| 4 | 0.0168 | 0.5042 | 0.5042 | lisansüstü_eğitim_ve.pdf |
| 5 | 0.0168 | 0.5042 | 0.5042 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 6 | 0.0148 | 0.5037 | 0.5037 | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |
| 7 | 0.0142 | 0.5035 | 0.5035 | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |
| 8 | 0.0090 | 0.5022 | 0.5022 | yonerge_yabanci_dil_egitim_ogretim.pdf |
| 9 | 0.0062 | 0.5016 | 0.5016 | sürekli_eğitim_merkezi_yönergesi.pdf |
| 10 | 0.0054 | 0.5014 | 0.5014 | tıp_fakültesi_tıp_doktorluğu_programı.pdf |

### Not itirazi icin ne kadar sureye sahibim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.5361 | 0.6309 | 0.6309 | sık_sorulan_sorular.txt |
| 2 | 0.1685 | 0.5420 | 0.5420 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.1273 | 0.5318 | 0.5318 | yonerge_yuzde_on_basari_degerlendirme.pdf |
| 4 | 0.0844 | 0.5211 | 0.5211 | ön_lisans_ve_lisans.pdf |
| 5 | 0.0421 | 0.5105 | 0.5105 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 6 | 0.0310 | 0.5077 | 0.5077 | ders_yeterlilik_sınavı_uygulama_yönergesi.pdf |
| 7 | 0.0234 | 0.5058 | 0.5058 | sık_sorulan_sorular.txt |
| 8 | 0.0147 | 0.5037 | 0.5037 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 9 | 0.0057 | 0.5014 | 0.5014 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 10 | 0.0027 | 0.5007 | 0.5007 | öğrenci_konukevi_uygulama_yönergesi.pdf |

### Yaz okulunda en fazla kac ders alabilirim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9951 | 0.7301 | 0.7301 | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 2 | 0.9937 | 0.7298 | 0.7298 | yonerge_yaz_okulu_egitim_ogretim.pdf |
| 3 | 0.9521 | 0.7215 | 0.7215 | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 4 | 0.9512 | 0.7214 | 0.7214 | yaz_okulu_eğitim_öğretim.pdf |
| 5 | 0.9492 | 0.7210 | 0.7210 | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.8843 | 0.7077 | 0.7077 | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.7227 | 0.6732 | 0.6732 | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 8 | 0.4114 | 0.6014 | 0.6014 | yaz_okulu_eğitim_öğretim.pdf |
| 9 | 0.4114 | 0.6014 | 0.6014 | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 10 | 0.1849 | 0.5461 | 0.5461 | yaz_okulu_eğitim_öğretim.pdf |

### Basarisiz oldugum dersi tekrar almak icin ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.5454 | 0.6331 | 0.6331 | sık_sorulan_sorular.txt |
| 2 | 0.5430 | 0.6325 | 0.6325 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 3 | 0.5073 | 0.6242 | 0.6242 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 4 | 0.3975 | 0.5981 | 0.5981 | sık_sorulan_sorular.txt |
| 5 | 0.3174 | 0.5787 | 0.5787 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.3108 | 0.5771 | 0.5771 | sık_sorulan_sorular.txt |
| 7 | 0.2600 | 0.5646 | 0.5646 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 8 | 0.1863 | 0.5464 | 0.5464 | sık_sorulan_sorular.txt |
| 9 | 0.1810 | 0.5451 | 0.5451 | sık_sorulan_sorular.txt |
| 10 | 0.1677 | 0.5418 | 0.5418 | sık_sorulan_sorular.txt |

### Azami ogrenim suresi dolunca ne olur?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.1594 | 0.5398 | 0.5398 | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 2 | 0.1061 | 0.5265 | 0.5265 | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 3 | 0.0419 | 0.5105 | 0.5105 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 4 | 0.0143 | 0.5036 | 0.5036 | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 5 | 0.0114 | 0.5028 | 0.5028 | çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf |
| 6 | 0.0060 | 0.5015 | 0.5015 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.0039 | 0.5010 | 0.5010 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 8 | 0.0034 | 0.5009 | 0.5009 | lisansüstü_eğitim_ve.pdf |
| 9 | 0.0031 | 0.5008 | 0.5008 | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.0028 | 0.5007 | 0.5007 | lisansüstü_eğitim_ve.pdf |

### Donem dondurma icin saglik raporu yeterli mi?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.0403 | 0.5101 | 0.5101 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 2 | 0.0035 | 0.5009 | 0.5009 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 3 | 0.0012 | 0.5003 | 0.5003 | sık_sorulan_sorular.txt |
| 4 | 0.0012 | 0.5003 | 0.5003 | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 5 | 0.0011 | 0.5003 | 0.5003 | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 6 | 0.0011 | 0.5003 | 0.5003 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.0010 | 0.5003 | 0.5003 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 8 | 0.0006 | 0.5001 | 0.5001 | ön_lisans_ve_lisans.pdf |
| 9 | 0.0006 | 0.5001 | 0.5001 | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 10 | 0.0005 | 0.5001 | 0.5001 | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Mezuniyet icin GNO en az kac olmalidir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.4590 | 0.6128 | 0.6128 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 2 | 0.3423 | 0.5847 | 0.5847 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.2104 | 0.5524 | 0.5524 | sık_sorulan_sorular.txt |
| 4 | 0.1060 | 0.5265 | 0.5265 | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 5 | 0.0204 | 0.5051 | 0.5051 | sık_sorulan_sorular.txt |
| 6 | 0.0132 | 0.5033 | 0.5033 | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.0123 | 0.5031 | 0.5031 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 8 | 0.0120 | 0.5030 | 0.5030 | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 9 | 0.0055 | 0.5014 | 0.5014 | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0035 | 0.5009 | 0.5009 | ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf |

### Zorunlu staj icin SGK baslangic islemleri nasil yapilir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.3164 | 0.5784 | 0.5784 | staj_iş_akışı.pdf |
| 2 | 0.2064 | 0.5514 | 0.5514 | zorunlu_stajda_izlenecek_yol.pdf |
| 3 | 0.0964 | 0.5241 | 0.5241 | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 4 | 0.0517 | 0.5129 | 0.5129 | document.pdf |
| 5 | 0.0340 | 0.5085 | 0.5085 | document.pdf |
| 6 | 0.0267 | 0.5067 | 0.5067 | staj_bilgilendirme_toplantısı_sunumu_2024_2025.pdf |
| 7 | 0.0207 | 0.5052 | 0.5052 | staj_esaslar.pdf |
| 8 | 0.0170 | 0.5042 | 0.5042 | staj_iş_akışı.pdf |
| 9 | 0.0158 | 0.5039 | 0.5039 | staj_ilkeleri_23122019_inş_müh.pdf |
| 10 | 0.0141 | 0.5035 | 0.5035 | staj_bilgilendirme_toplantısı_sunumu_2024_2025.pdf |

### Staj defterini teslim etme suresi ne kadardir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.9028 | 0.7115 | 0.7115 | çevre_mühendisliği_bölümü_staj_ilkeleri.docx |
| 2 | 0.8765 | 0.7061 | 0.7061 | çevre_mühendisliği_bölümü_staj_ilkeleri.docx |
| 3 | 0.6685 | 0.6612 | 0.6612 | zorunlu_stajda_izlenecek_yol.pdf |
| 4 | 0.3779 | 0.5934 | 0.5934 | zorunlu_stajda_izlenecek_yol.pdf |
| 5 | 0.1638 | 0.5409 | 0.5409 | zorunlu_gönüllü_staj_başvuru_formu.pdf |
| 6 | 0.0774 | 0.5193 | 0.5193 | yonerge_onlisans_lisans_staj.pdf |
| 7 | 0.0437 | 0.5109 | 0.5109 | staj_sıkça_sorulanlar.pdf |
| 8 | 0.0383 | 0.5096 | 0.5096 | staj_sıkça_sorulanlar.pdf |
| 9 | 0.0177 | 0.5044 | 0.5044 | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |
| 10 | 0.0116 | 0.5029 | 0.5029 | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |

### Bitirme projesi danismani nasil belirlenir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.5024 | 0.6230 | 0.6230 | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 2 | 0.4446 | 0.6093 | 0.6093 | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 3 | 0.3357 | 0.5831 | 0.5831 | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 4 | 0.0704 | 0.5176 | 0.5176 | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 5 | 0.0521 | 0.5130 | 0.5130 | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 6 | 0.0475 | 0.5119 | 0.5119 | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 7 | 0.0369 | 0.5092 | 0.5092 | mat_bitirme_çalışması_ilkeleri.pdf |
| 8 | 0.0261 | 0.5065 | 0.5065 | mat_bitirme_çalışması_ilkeleri.pdf |
| 9 | 0.0243 | 0.5061 | 0.5061 | bitirme_projesi_sunum_değerlendirme_formu.docx |
| 10 | 0.0239 | 0.5060 | 0.5060 | bitirme_projesi_şablon.docx |

### Staj yerim degisirse ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.4597 | 0.6129 | 0.6129 | zorunlu_gönüllü_staj_başvuru_formu.pdf |
| 2 | 0.0991 | 0.5248 | 0.5248 | staj_esaslar.pdf |
| 3 | 0.0983 | 0.5245 | 0.5245 | staj_esaslar.pdf |
| 4 | 0.0860 | 0.5215 | 0.5215 | staj_ilkeleri_23122019_inş_müh.pdf |
| 5 | 0.0806 | 0.5201 | 0.5201 | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 6 | 0.0703 | 0.5176 | 0.5176 | staj_yönergesi.pdf |
| 7 | 0.0518 | 0.5130 | 0.5130 | işyeri_staj_sözleşmesi.pdf |
| 8 | 0.0349 | 0.5087 | 0.5087 | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |
| 9 | 0.0175 | 0.5044 | 0.5044 | yonerge_onlisans_lisans_staj.pdf |
| 10 | 0.0172 | 0.5043 | 0.5043 | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |

### Lisansustu ogrenciler icin tez teslim suresi ne kadardir?

| # | Ham Skor | Kalibre | Sigmoid | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------|
| 1 | 0.6333 | 0.6532 | 0.6532 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 2 | 0.3369 | 0.5834 | 0.5834 | lisansüstü_eğitim_ve.pdf |
| 3 | 0.1510 | 0.5377 | 0.5377 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 4 | 0.1205 | 0.5301 | 0.5301 | lisansüstü_eğitim_ve.pdf |
| 5 | 0.0823 | 0.5206 | 0.5206 | lisansüstü_eğitim_ve.pdf |
| 6 | 0.0532 | 0.5133 | 0.5133 | yonerge_lisansustu_danismanlik_ders_verme.pdf |
| 7 | 0.0381 | 0.5095 | 0.5095 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 8 | 0.0291 | 0.5073 | 0.5073 | lisansüstü_eğitim_ve.pdf |
| 9 | 0.0279 | 0.5070 | 0.5070 | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 10 | 0.0274 | 0.5068 | 0.5068 | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |

---

*Bu rapor `scripts/analyze_reranker_scores.py` tarafindan otomatik uretilmistir.*