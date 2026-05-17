# Reranker Skor Dagilim Analizi

**Tarih:** 2026-05-17 17:47
**Model:** seroe/bge-reranker-v2-m3-turkish-triplet
**Device:** cuda
**Torch dtype:** float16->torch.float16
**Kalibrasyon:** shift=0.0405, scale=0.5
**Toplam Soru:** 40
**Toplam Skor Ornegi:** 400
**Toplam sure:** 68.0s
**Kapsam:** Candidate pool + reranker analizi; final threshold/filtering adimlari buna dahil degildir.

---

## Top-1 Source Owner Ozeti

- Expected department match: 33/40
- Top-1 source owner dagilimi: -=7, curriculum_catalog=1, international_policy=6, student_affairs_policy=25, tuition_fee_catalog=1

---

## Tum Skorlar (Tum Adaylar)

### Ham Reranker Skorlari (Logit)

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.0 |
| p10 | 0.0003 |
| p25 | 0.0056 |
| median | 0.0386 |
| mean | 0.1734 |
| p75 | 0.1825 |
| p90 | 0.7452 |
| max | 0.9995 |
| std | 0.2835 |

### Kalibre Edilmis Skorlar (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.4798 |
| p10 | 0.4799 |
| p25 | 0.4826 |
| median | 0.4991 |
| mean | 0.5564 |
| p75 | 0.5705 |
| p90 | 0.8037 |
| max | 0.8719 |
| std | 0.1172 |

### Duz Sigmoid Skorlar (Referans)

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.5 |
| p10 | 0.5001 |
| p25 | 0.5014 |
| median | 0.5097 |
| mean | 0.5416 |
| p75 | 0.5455 |
| p90 | 0.6781 |
| max | 0.731 |
| std | 0.0666 |

---

## Top-1 Skorlar (Her Sorunun En Iyi Adayi)

### Ham Top-1 Skorlari (Logit)

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.0 |
| p10 | 0.0321 |
| p25 | 0.1683 |
| median | 0.6621 |
| mean | 0.5646 |
| p75 | 0.9718 |
| p90 | 0.9911 |
| max | 0.9995 |
| std | 0.401 |

### Kalibre Top-1 Skorlari (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.4798 |
| p10 | 0.4958 |
| p25 | 0.5635 |
| median | 0.773 |
| mean | 0.7137 |
| p75 | 0.8656 |
| p90 | 0.87 |
| max | 0.8719 |
| std | 0.1551 |

### Duz Sigmoid Top-1 Skorlari (Referans)

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.5 |
| p10 | 0.508 |
| p25 | 0.542 |
| median | 0.6591 |
| mean | 0.6327 |
| p75 | 0.7255 |
| p90 | 0.7293 |
| max | 0.731 |
| std | 0.0923 |

---

## Sigmoid Kalibrasyon Onerisi

- **Formul:** `sigmoid((score - 0.0386) / 0.5000)`
- **Shift (median):** 0.0386
- **Scale (IQR):** 0.5
- **Onerilen direct-RAG esigi:** 0.571
- **Onerilen min-source esigi:** 0.484

---

## Soru Bazli Detaylar

### Sistem giris sifremi unuttum, ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9688 | 0.8649 | 0.7249 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.0032 | 0.4814 | 0.5008 | student_affairs_policy | öğrenci_toplulukları_yönergesi.pdf |
| 3 | 0.0006 | 0.4801 | 0.5001 | student_affairs_policy | sık_sorulan_sorular.txt |
| 4 | 0.0005 | 0.4800 | 0.5001 | student_affairs_policy | sık_sorulan_sorular.txt |
| 5 | 0.0004 | 0.4800 | 0.5001 | student_affairs_policy | sık_sorulan_sorular.txt |
| 6 | 0.0003 | 0.4799 | 0.5001 | student_affairs_policy | öğrenci_işleri_birimi.txt |
| 7 | 0.0002 | 0.4799 | 0.5001 | student_affairs_policy | kimlik_kartı_yönergesi.pdf |
| 8 | 0.0002 | 0.4799 | 0.5001 | student_affairs_policy | öğrenci_işleri_birimi.txt |
| 9 | 0.0002 | 0.4799 | 0.5001 | student_affairs_policy | sık_sorulan_sorular.txt |
| 10 | 0.0002 | 0.4799 | 0.5000 | student_affairs_policy | kimlik_kartı_yönergesi.pdf |

### UBYS uzerinden ilisik kesme talebini nasil baslatirim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9888 | 0.8695 | 0.7288 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.8931 | 0.8462 | 0.7095 | student_affairs_policy | sık_sorulan_sorular.txt |
| 3 | 0.1461 | 0.5526 | 0.5365 | student_affairs_policy | kimlik_kartı_yönergesi.pdf |
| 4 | 0.0284 | 0.4939 | 0.5071 | international_policy | öğrenci_işleri_birimi.txt |
| 5 | 0.0095 | 0.4845 | 0.5024 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.0065 | 0.4830 | 0.5016 | international_policy | öğrenci_işleri_birimi.txt |
| 7 | 0.0065 | 0.4830 | 0.5016 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 8 | 0.0012 | 0.4804 | 0.5003 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 9 | 0.0008 | 0.4801 | 0.5002 | student_affairs_policy | sık_sorulan_sorular.txt |
| 10 | 0.0007 | 0.4801 | 0.5002 | student_affairs_policy | sık_sorulan_sorular.txt |

### Diplomami kaybettim, ikinci nusha icin ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9976 | 0.8715 | 0.7306 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.9502 | 0.8605 | 0.7212 | tuition_fee_catalog | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 3 | 0.0605 | 0.5100 | 0.5151 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 4 | 0.0461 | 0.5028 | 0.5115 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 5 | 0.0163 | 0.4879 | 0.5041 | tuition_fee_catalog | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 6 | 0.0062 | 0.4829 | 0.5016 | student_affairs_policy | sık_sorulan_sorular.txt |
| 7 | 0.0009 | 0.4802 | 0.5002 | student_affairs_policy | sık_sorulan_sorular.txt |
| 8 | 0.0006 | 0.4801 | 0.5002 | international_policy | sık_sorulan_sorular.txt |
| 9 | 0.0006 | 0.4800 | 0.5001 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 10 | 0.0006 | 0.4800 | 0.5001 | student_affairs_policy | sık_sorulan_sorular.txt |

### Diploma eki transkript yerine gecer mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9961 | 0.8712 | 0.7303 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.3711 | 0.6595 | 0.5917 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 3 | 0.0659 | 0.5127 | 0.5165 | international_policy | sık_sorulan_sorular.txt |
| 4 | 0.0191 | 0.4893 | 0.5048 | student_affairs_policy | sık_sorulan_sorular.txt |
| 5 | 0.0176 | 0.4886 | 0.5044 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 6 | 0.0093 | 0.4844 | 0.5023 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 7 | 0.0087 | 0.4841 | 0.5022 | student_affairs_policy | sık_sorulan_sorular.txt |
| 8 | 0.0071 | 0.4833 | 0.5018 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 9 | 0.0066 | 0.4830 | 0.5016 | student_affairs_policy | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 10 | 0.0065 | 0.4830 | 0.5016 | international_policy | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |

### Kayit dondurma ile kayit yaptirmamak arasinda ne fark var?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9341 | 0.8566 | 0.7179 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.1819 | 0.5702 | 0.5453 | student_affairs_policy | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 3 | 0.1698 | 0.5643 | 0.5423 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 4 | 0.0477 | 0.5036 | 0.5119 | student_affairs_policy | sık_sorulan_sorular.txt |
| 5 | 0.0416 | 0.5006 | 0.5104 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 6 | 0.0356 | 0.4976 | 0.5089 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 7 | 0.0201 | 0.4898 | 0.5050 | student_affairs_policy | öğrenci_konseyi_yönergesi.pdf |
| 8 | 0.0142 | 0.4868 | 0.5035 | student_affairs_policy | ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf |
| 9 | 0.0095 | 0.4845 | 0.5024 | tuition_fee_catalog | sık_sorulan_sorular.txt |
| 10 | 0.0014 | 0.4805 | 0.5004 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Hazirlik sinifi okuyan ogrenci transkriptsiz Ek Madde-1 ile yatay gecis basvurusu yapabilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.8887 | 0.8451 | 0.7086 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.4204 | 0.6813 | 0.6036 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 3 | 0.2422 | 0.5995 | 0.5603 | international_policy | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 4 | 0.0827 | 0.5211 | 0.5207 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 5 | 0.0704 | 0.5150 | 0.5176 | international_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 6 | 0.0591 | 0.5093 | 0.5148 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 7 | 0.0573 | 0.5084 | 0.5143 | student_affairs_policy | sık_sorulan_sorular.txt |
| 8 | 0.0374 | 0.4984 | 0.5093 | student_affairs_policy | sık_sorulan_sorular.txt |
| 9 | 0.0202 | 0.4899 | 0.5051 | student_affairs_policy | ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf |
| 10 | 0.0095 | 0.4845 | 0.5024 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Birden fazla universiteye yatay gecis basvurusu yapabilir miyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9907 | 0.8699 | 0.7292 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.1365 | 0.5478 | 0.5341 | student_affairs_policy | sık_sorulan_sorular.txt |
| 3 | 0.0651 | 0.5123 | 0.5163 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 4 | 0.0405 | 0.5000 | 0.5101 | student_affairs_policy | sık_sorulan_sorular.txt |
| 5 | 0.0146 | 0.4871 | 0.5037 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.0101 | 0.4848 | 0.5025 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 7 | 0.0077 | 0.4836 | 0.5019 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 8 | 0.0056 | 0.4826 | 0.5014 | student_affairs_policy | sık_sorulan_sorular.txt |
| 9 | 0.0056 | 0.4826 | 0.5014 | student_affairs_policy | ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf |
| 10 | 0.0054 | 0.4824 | 0.5013 | student_affairs_policy | yonerge_onlisans_lisans_yatay_gecis.pdf |

### Ozel ogrenci olarak ne zaman basvuru yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.8110 | 0.8236 | 0.6923 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.2566 | 0.6064 | 0.5638 | student_affairs_policy | sık_sorulan_sorular.txt |
| 3 | 0.1105 | 0.5349 | 0.5276 | student_affairs_policy | sık_sorulan_sorular.txt |
| 4 | 0.0177 | 0.4886 | 0.5044 | student_affairs_policy | sık_sorulan_sorular.txt |
| 5 | 0.0068 | 0.4832 | 0.5017 | student_affairs_policy | sık_sorulan_sorular.txt |
| 6 | 0.0009 | 0.4802 | 0.5002 | student_affairs_policy | sık_sorulan_sorular.txt |
| 7 | 0.0007 | 0.4801 | 0.5002 | student_affairs_policy | yaz_okulu_eğitim_öğretim.pdf |
| 8 | 0.0006 | 0.4801 | 0.5002 | curriculum_catalog | sık_sorulan_sorular.txt |
| 9 | 0.0005 | 0.4800 | 0.5001 | curriculum_catalog | sık_sorulan_sorular.txt |
| 10 | 0.0004 | 0.4800 | 0.5001 | student_affairs_policy | sık_sorulan_sorular.txt |

### Ozel ogrenci olarak basvuru icin hangi belgeler gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.5342 | 0.7286 | 0.6305 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.2964 | 0.6252 | 0.5736 | student_affairs_policy | sık_sorulan_sorular.txt |
| 3 | 0.1843 | 0.5714 | 0.5460 | - | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 4 | 0.1610 | 0.5600 | 0.5402 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 5 | 0.1394 | 0.5493 | 0.5348 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 6 | 0.0984 | 0.5289 | 0.5246 | student_affairs_policy | sık_sorulan_sorular.txt |
| 7 | 0.0441 | 0.5018 | 0.5110 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 8 | 0.0422 | 0.5009 | 0.5106 | international_policy | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 9 | 0.0382 | 0.4988 | 0.5095 | student_affairs_policy | sık_sorulan_sorular.txt |
| 10 | 0.0296 | 0.4945 | 0.5074 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |

### Daha once aldigim dersler icin muafiyet basvurusunu ne zaman yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9546 | 0.8615 | 0.7220 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.8882 | 0.8449 | 0.7085 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 3 | 0.7002 | 0.7891 | 0.6682 | student_affairs_policy | sık_sorulan_sorular.txt |
| 4 | 0.3384 | 0.6447 | 0.5838 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 5 | 0.3108 | 0.6319 | 0.5771 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 6 | 0.2781 | 0.6166 | 0.5691 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 7 | 0.2571 | 0.6066 | 0.5639 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 8 | 0.1176 | 0.5385 | 0.5294 | student_affairs_policy | yonerge_ders_yeterlik_muafiyet_intibak.pdf |
| 9 | 0.1056 | 0.5325 | 0.5264 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 10 | 0.0770 | 0.5182 | 0.5192 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |

### Ikamet izni basvurusu icin hangi belgeler gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9634 | 0.8636 | 0.7238 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 2 | 0.9082 | 0.8501 | 0.7126 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 3 | 0.8970 | 0.8472 | 0.7103 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 4 | 0.7915 | 0.8179 | 0.6882 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 5 | 0.7163 | 0.7944 | 0.6718 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 6 | 0.6631 | 0.7765 | 0.6600 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 7 | 0.5132 | 0.7202 | 0.6256 | international_policy | uluslararası_öğrenci_ikamet_işlemleri.pdf |
| 8 | 0.4399 | 0.6897 | 0.6082 | international_policy | uluslararası_öğrenci.pdf |
| 9 | 0.3960 | 0.6706 | 0.5977 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 10 | 0.3552 | 0.6524 | 0.5879 | - | muvafakatname.pdf |

### Denklik belgesi ne zaman gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.8667 | 0.8392 | 0.7041 | international_policy | denklik_belgesi.pdf |
| 2 | 0.2563 | 0.6063 | 0.5637 | academic_calendar | tyb.pdf |
| 3 | 0.2032 | 0.5807 | 0.5506 | international_policy | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 4 | 0.0648 | 0.5121 | 0.5162 | international_policy | uluslararası_öğrenci.pdf |
| 5 | 0.0499 | 0.5047 | 0.5125 | student_affairs_policy | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 6 | 0.0482 | 0.5039 | 0.5121 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 7 | 0.0479 | 0.5037 | 0.5120 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |
| 8 | 0.0478 | 0.5036 | 0.5119 | - | denklik_belgesi.pdf |
| 9 | 0.0473 | 0.5034 | 0.5118 | tuition_fee_catalog | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |
| 10 | 0.0209 | 0.4902 | 0.5052 | - | yurda_giriş_çıkış_belgesi.pdf |

### YOS ID numarami nasil ogrenebilirim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0334 | 0.4964 | 0.5083 | international_policy | uluslararası_öğrenci.pdf |
| 2 | 0.0169 | 0.4882 | 0.5042 | international_policy | öğrenci_no_öğrenme.pdf |
| 3 | 0.0162 | 0.4879 | 0.5041 | international_policy | yös_ıd_no_öğrenme.pdf |
| 4 | 0.0018 | 0.4807 | 0.5005 | international_policy | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 5 | 0.0011 | 0.4803 | 0.5003 | - | ön_kayıt_kılavuzu_başvuru_adımları.pdf |
| 6 | 0.0006 | 0.4801 | 0.5001 | international_policy | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 7 | 0.0005 | 0.4800 | 0.5001 | international_policy | yonerge_uluslararasi_ogrenci_yatay_gecis.pdf |
| 8 | 0.0005 | 0.4800 | 0.5001 | international_policy | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 9 | 0.0004 | 0.4800 | 0.5001 | international_policy | uluslararası_öğrenci_kimlik_bilgileri_güncelleme_formu.pdf |
| 10 | 0.0004 | 0.4800 | 0.5001 | international_policy | avrupa_birliği_eğitim_ve_gençlik_programları_hayat_boyu_öğrenme_erasmus.pdf |

### Uluslararasi ogrenci kaydinda evrak teslim formu gerekiyor mu?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9702 | 0.8652 | 0.7252 | international_policy | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 2 | 0.9653 | 0.8641 | 0.7242 | international_policy | uluslararası_öğrenci_yönergesi.pdf |
| 3 | 0.9067 | 0.8497 | 0.7123 | international_policy | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 4 | 0.7778 | 0.8138 | 0.6852 | international_policy | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 5 | 0.7505 | 0.8053 | 0.6793 | international_policy | uluslararası_öğrenci_evrak_teslim_formu_r1.pdf |
| 6 | 0.2578 | 0.6070 | 0.5641 | international_policy | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 7 | 0.2054 | 0.5817 | 0.5512 | international_policy | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 8 | 0.1243 | 0.5418 | 0.5310 | international_policy | uluslararası_öğrenci.pdf |
| 9 | 0.0851 | 0.5223 | 0.5213 | international_policy | ön_kayıt_kılavuzu_başvuru_adımları.pdf |
| 10 | 0.0764 | 0.5180 | 0.5191 | international_policy | uluslararası_öğrenci.pdf |

### TOMER ne is yapar?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0330 | 0.4962 | 0.5082 | international_policy | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 2 | 0.0003 | 0.4799 | 0.5001 | student_affairs_policy | kök_hücre_araştırma_merkezi_yönergesi.pdf |
| 3 | 0.0003 | 0.4799 | 0.5001 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 4 | 0.0003 | 0.4799 | 0.5001 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 5 | 0.0002 | 0.4799 | 0.5001 | - | dil_ve_konuşma_bozuklukları.pdf |
| 6 | 0.0002 | 0.4799 | 0.5001 | student_affairs_policy | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 7 | 0.0001 | 0.4798 | 0.5000 | student_affairs_policy | kariyer_merkezi_yönergesi.pdf |
| 8 | 0.0001 | 0.4798 | 0.5000 | student_affairs_policy | siber_güvenlik_ve_bilişim_teknolojileri.pdf |
| 9 | 0.0001 | 0.4798 | 0.5000 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 10 | 0.0001 | 0.4798 | 0.5000 | - | lisansüstü_eğitim_enstitüsü.pdf |

### Pedagojik formasyon dersleri transkripte dahil edilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9995 | 0.8719 | 0.7310 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.9849 | 0.8686 | 0.7281 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 3 | 0.9785 | 0.8672 | 0.7268 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 4 | 0.2534 | 0.6049 | 0.5630 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 5 | 0.1494 | 0.5542 | 0.5373 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 6 | 0.1344 | 0.5468 | 0.5335 | student_affairs_policy | yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf |
| 7 | 0.0899 | 0.5247 | 0.5225 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 8 | 0.0745 | 0.5170 | 0.5186 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.0490 | 0.5042 | 0.5122 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 10 | 0.0439 | 0.5017 | 0.5110 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |

### Pedagojik formasyon mezuniyet ortalamasina dahil edilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9888 | 0.8695 | 0.7288 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.9780 | 0.8670 | 0.7267 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 3 | 0.7446 | 0.8035 | 0.6780 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 4 | 0.4937 | 0.7122 | 0.6210 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.4114 | 0.6774 | 0.6014 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 6 | 0.2996 | 0.6267 | 0.5743 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.2808 | 0.6179 | 0.5697 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 8 | 0.1632 | 0.5610 | 0.5407 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.1506 | 0.5548 | 0.5376 | curriculum_catalog | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 10 | 0.1327 | 0.5460 | 0.5331 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |

### Pedagojik formasyon alirsam mezuniyet 240 AKTS'nin ustune cikabilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9941 | 0.8707 | 0.7299 | curriculum_catalog | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.5879 | 0.7493 | 0.6429 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 3 | 0.4707 | 0.7027 | 0.6156 | student_affairs_policy | çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf |
| 4 | 0.0734 | 0.5165 | 0.5183 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 5 | 0.0479 | 0.5037 | 0.5120 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 6 | 0.0439 | 0.5017 | 0.5110 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 7 | 0.0428 | 0.5012 | 0.5107 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 8 | 0.0401 | 0.4998 | 0.5100 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.0400 | 0.4998 | 0.5100 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 10 | 0.0220 | 0.4907 | 0.5055 | curriculum_catalog | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |

### Pedagojik formasyon derslerinin tumunu almak zorunlu mu?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9844 | 0.8685 | 0.7280 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.2330 | 0.5951 | 0.5580 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 3 | 0.1654 | 0.5621 | 0.5413 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 4 | 0.1575 | 0.5582 | 0.5393 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 5 | 0.1571 | 0.5580 | 0.5392 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 6 | 0.1539 | 0.5565 | 0.5384 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 7 | 0.0825 | 0.5210 | 0.5206 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 8 | 0.0629 | 0.5112 | 0.5157 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.0432 | 0.5014 | 0.5108 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 10 | 0.0404 | 0.4999 | 0.5101 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |

### Pedagojik formasyon dersleri en erken hangi yariyilda alinabilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9043 | 0.8491 | 0.7118 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 2 | 0.7168 | 0.7946 | 0.6719 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 3 | 0.5957 | 0.7522 | 0.6447 | student_affairs_policy | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 4 | 0.4634 | 0.6997 | 0.6138 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.4602 | 0.6983 | 0.6131 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 6 | 0.4143 | 0.6787 | 0.6021 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 7 | 0.3489 | 0.6495 | 0.5863 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 8 | 0.3394 | 0.6451 | 0.5840 | curriculum_catalog | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 9 | 0.2664 | 0.6110 | 0.5662 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.2477 | 0.6021 | 0.5616 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |

### Yemek bursu basvurulari nereden yapilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9766 | 0.8667 | 0.7264 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 2 | 0.8101 | 0.8233 | 0.6921 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.5386 | 0.7303 | 0.6315 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.2268 | 0.5921 | 0.5565 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.1321 | 0.5457 | 0.5330 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.1034 | 0.5314 | 0.5258 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.0916 | 0.5255 | 0.5229 | student_affairs_policy | kimlik_kartı_yönergesi.pdf |
| 8 | 0.0525 | 0.5060 | 0.5131 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0449 | 0.5022 | 0.5112 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0325 | 0.4960 | 0.5081 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |

### Bursum hangi sartlarda kesilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0522 | 0.5059 | 0.5131 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 2 | 0.0438 | 0.5016 | 0.5109 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.0020 | 0.4808 | 0.5005 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.0013 | 0.4804 | 0.5003 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.0011 | 0.4803 | 0.5003 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.0010 | 0.4803 | 0.5002 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.0010 | 0.4802 | 0.5002 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0009 | 0.4802 | 0.5002 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0009 | 0.4802 | 0.5002 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0005 | 0.4800 | 0.5001 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |

### Kayit ekraninda borclu ya da fazla ucretli gorunuyorsam ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 2 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 3 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 4 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 6 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.0000 | 0.4798 | 0.5000 | - | idari_ve_mali_işler_birimi.txt |
| 8 | 0.0000 | 0.4798 | 0.5000 | - | idari_ve_mali_işler_birimi.txt |
| 9 | 0.0000 | 0.4798 | 0.5000 | - | idari_ve_mali_işler_birimi.txt |
| 10 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |

### Program suresini asarsam katki payi oder miyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0247 | 0.4921 | 0.5062 | tuition_fee_catalog | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |
| 2 | 0.0011 | 0.4803 | 0.5003 | tuition_fee_catalog | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |
| 3 | 0.0001 | 0.4798 | 0.5000 | international_policy | 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf |
| 4 | 0.0001 | 0.4798 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 5 | 0.0001 | 0.4798 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.0001 | 0.4798 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 8 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 9 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |

### Harc iadesi icin IBAN ve dekontla nereye basvurmam gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 2 | 0.0000 | 0.4798 | 0.5000 | - | idari_ve_mali_işler_birimi.txt |
| 3 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 4 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 5 | 0.0000 | 0.4798 | 0.5000 | tuition_fee_catalog | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |
| 6 | 0.0000 | 0.4798 | 0.5000 | tuition_fee_catalog | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |
| 7 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0000 | 0.4798 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0000 | 0.4798 | 0.5000 | international_policy | 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf |

### Sinava giremedigim ders icin mazeret sinavi basvurusu nasil yapilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.2459 | 0.6013 | 0.5612 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 2 | 0.2061 | 0.5820 | 0.5513 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.1409 | 0.5500 | 0.5352 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 4 | 0.1235 | 0.5414 | 0.5308 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 5 | 0.0377 | 0.4986 | 0.5094 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 6 | 0.0253 | 0.4924 | 0.5063 | student_affairs_policy | sık_sorulan_sorular.txt |
| 7 | 0.0231 | 0.4913 | 0.5058 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 8 | 0.0155 | 0.4875 | 0.5039 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 9 | 0.0084 | 0.4840 | 0.5021 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 10 | 0.0043 | 0.4819 | 0.5011 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |

### Bir dersten kac kez sinav hakkina sahibim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.1499 | 0.5545 | 0.5374 | student_affairs_policy | uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf |
| 2 | 0.0272 | 0.4934 | 0.5068 | student_affairs_policy | uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf |
| 3 | 0.0202 | 0.4899 | 0.5051 | student_affairs_policy | mühendislik_fakültesi_ortak_sınav_yönergesi.pdf |
| 4 | 0.0116 | 0.4856 | 0.5029 | student_affairs_policy | bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf |
| 5 | 0.0092 | 0.4844 | 0.5023 | student_affairs_policy | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |
| 6 | 0.0061 | 0.4828 | 0.5015 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 7 | 0.0060 | 0.4828 | 0.5015 | international_policy | yabancı_dil_eğitim_öğretimi_yönergesi.pdf |
| 8 | 0.0057 | 0.4826 | 0.5014 | student_affairs_policy | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 9 | 0.0030 | 0.4812 | 0.5007 | student_affairs_policy | bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf |
| 10 | 0.0029 | 0.4812 | 0.5007 | student_affairs_policy | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |

### Bagil degerlendirme sistemi nasil isler?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.2076 | 0.5828 | 0.5517 | student_affairs_policy | bağıl_değerlendirme_yönergesi.pdf |
| 2 | 0.0970 | 0.5282 | 0.5242 | student_affairs_policy | bağıl_değerlendirme_yönergesi.pdf |
| 3 | 0.0868 | 0.5231 | 0.5217 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 4 | 0.0795 | 0.5195 | 0.5199 | student_affairs_policy | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 5 | 0.0363 | 0.4979 | 0.5091 | student_affairs_policy | bağıl_değerlendirme_yönergesi.pdf |
| 6 | 0.0296 | 0.4946 | 0.5074 | student_affairs_policy | bağıl_değerlendirme_yönergesi.pdf |
| 7 | 0.0268 | 0.4932 | 0.5067 | student_affairs_policy | bağıl_değerlendirme_yönergesi.pdf |
| 8 | 0.0159 | 0.4877 | 0.5040 | student_affairs_policy | sık_sorulan_sorular.txt |
| 9 | 0.0132 | 0.4864 | 0.5033 | curriculum_catalog | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0074 | 0.4835 | 0.5019 | student_affairs_policy | yonerge_bagil_degerlendirme.pdf |

### Final sinavina girme sarti olarak devam yuzdesi kac olmalidir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0510 | 0.5052 | 0.5127 | international_policy | yonerge_yabanci_dil_egitim_ogretim.pdf |
| 2 | 0.0277 | 0.4936 | 0.5069 | student_affairs_policy | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |
| 3 | 0.0225 | 0.4910 | 0.5056 | - | lisansüstü_eğitim_ve.pdf |
| 4 | 0.0225 | 0.4910 | 0.5056 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 5 | 0.0144 | 0.4869 | 0.5036 | international_policy | yabancı_dil_eğitim_öğretimi_yönergesi.pdf |
| 6 | 0.0108 | 0.4851 | 0.5027 | student_affairs_policy | yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf |
| 7 | 0.0105 | 0.4850 | 0.5026 | student_affairs_policy | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |
| 8 | 0.0064 | 0.4829 | 0.5016 | international_policy | yonerge_yabanci_dil_egitim_ogretim.pdf |
| 9 | 0.0039 | 0.4817 | 0.5010 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.0036 | 0.4816 | 0.5009 | student_affairs_policy | sürekli_eğitim_merkezi_yönergesi.pdf |

### Not itirazi icin ne kadar sureye sahibim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.3477 | 0.6489 | 0.5860 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.0681 | 0.5138 | 0.5170 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.0623 | 0.5109 | 0.5156 | student_affairs_policy | yonerge_yuzde_on_basari_degerlendirme.pdf |
| 4 | 0.0475 | 0.5035 | 0.5119 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 5 | 0.0227 | 0.4911 | 0.5057 | student_affairs_policy | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 6 | 0.0194 | 0.4894 | 0.5048 | student_affairs_policy | ders_yeterlilik_sınavı_uygulama_yönergesi.pdf |
| 7 | 0.0140 | 0.4868 | 0.5035 | student_affairs_policy | sık_sorulan_sorular.txt |
| 8 | 0.0087 | 0.4841 | 0.5022 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 9 | 0.0036 | 0.4816 | 0.5009 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 10 | 0.0021 | 0.4808 | 0.5005 | student_affairs_policy | öğrenci_konukevi_uygulama_yönergesi.pdf |

### Yaz okulunda en fazla kac ders alabilirim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9893 | 0.8696 | 0.7289 | student_affairs_policy | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 2 | 0.9873 | 0.8692 | 0.7286 | student_affairs_policy | yaz_okulu_eğitim_öğretim.pdf |
| 3 | 0.9097 | 0.8505 | 0.7129 | international_policy | yonerge_yaz_okulu_egitim_ogretim.pdf |
| 4 | 0.8872 | 0.8447 | 0.7083 | international_policy | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 5 | 0.8813 | 0.8431 | 0.7071 | academic_calendar | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.7612 | 0.8087 | 0.6816 | international_policy | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.5366 | 0.7295 | 0.6310 | tuition_fee_catalog | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 8 | 0.1711 | 0.5650 | 0.5427 | student_affairs_policy | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 9 | 0.1705 | 0.5647 | 0.5425 | student_affairs_policy | yaz_okulu_eğitim_öğretim.pdf |
| 10 | 0.0817 | 0.5206 | 0.5204 | student_affairs_policy | yaz_okulu_eğitim_öğretim_yönergesi.pdf |

### Basarisiz oldugum dersi tekrar almak icin ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.2908 | 0.6226 | 0.5722 | student_affairs_policy | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 2 | 0.2527 | 0.6045 | 0.5628 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.2360 | 0.5965 | 0.5587 | student_affairs_policy | sık_sorulan_sorular.txt |
| 4 | 0.2172 | 0.5874 | 0.5541 | student_affairs_policy | sık_sorulan_sorular.txt |
| 5 | 0.1471 | 0.5531 | 0.5367 | student_affairs_policy | sık_sorulan_sorular.txt |
| 6 | 0.1172 | 0.5383 | 0.5293 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.1116 | 0.5355 | 0.5279 | student_affairs_policy | sık_sorulan_sorular.txt |
| 8 | 0.0947 | 0.5271 | 0.5236 | curriculum_catalog | sık_sorulan_sorular.txt |
| 9 | 0.0687 | 0.5141 | 0.5172 | - | endüstri_mühendisliği_tasarımı_yaptırma_ve_değerlendirme_ı̇lkeleri_güncel.pdf |
| 10 | 0.0560 | 0.5078 | 0.5140 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |

### Azami ogrenim suresi dolunca ne olur?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.1065 | 0.5330 | 0.5266 | - | lisansüstü_eğitim_ve.pdf |
| 2 | 0.0757 | 0.5176 | 0.5189 | - | lisansüstü_eğitim_ve.pdf |
| 3 | 0.0357 | 0.4976 | 0.5089 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 4 | 0.0114 | 0.4855 | 0.5029 | student_affairs_policy | çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf |
| 5 | 0.0109 | 0.4852 | 0.5027 | - | lisansüstü_eğitim_ve.pdf |
| 6 | 0.0051 | 0.4823 | 0.5013 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.0032 | 0.4814 | 0.5008 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 8 | 0.0031 | 0.4813 | 0.5008 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.0030 | 0.4813 | 0.5008 | - | lisansüstü_eğitim_ve.pdf |
| 10 | 0.0025 | 0.4810 | 0.5006 | - | lisansüstü_eğitim_ve.pdf |

### Donem dondurma icin saglik raporu yeterli mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0155 | 0.4875 | 0.5039 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 2 | 0.0042 | 0.4819 | 0.5011 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 3 | 0.0010 | 0.4803 | 0.5002 | student_affairs_policy | sık_sorulan_sorular.txt |
| 4 | 0.0007 | 0.4801 | 0.5002 | international_policy | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 5 | 0.0007 | 0.4801 | 0.5002 | student_affairs_policy | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 6 | 0.0006 | 0.4801 | 0.5001 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.0006 | 0.4800 | 0.5001 | curriculum_catalog | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 8 | 0.0005 | 0.4800 | 0.5001 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 9 | 0.0004 | 0.4800 | 0.5001 | curriculum_catalog | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 10 | 0.0004 | 0.4799 | 0.5001 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Mezuniyet icin GNO en az kac olmalidir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.2737 | 0.6145 | 0.5680 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 2 | 0.1940 | 0.5761 | 0.5483 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.1622 | 0.5606 | 0.5405 | student_affairs_policy | sık_sorulan_sorular.txt |
| 4 | 0.0742 | 0.5169 | 0.5185 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 5 | 0.0155 | 0.4875 | 0.5039 | student_affairs_policy | sık_sorulan_sorular.txt |
| 6 | 0.0103 | 0.4849 | 0.5026 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 7 | 0.0087 | 0.4841 | 0.5022 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 8 | 0.0070 | 0.4833 | 0.5018 | - | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 9 | 0.0046 | 0.4820 | 0.5011 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0041 | 0.4818 | 0.5010 | student_affairs_policy | ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf |

### Zorunlu staj icin SGK baslangic islemleri nasil yapilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.1744 | 0.5666 | 0.5435 | student_affairs_policy | staj_iş_akışı.pdf |
| 2 | 0.0981 | 0.5288 | 0.5245 | student_affairs_policy | zorunlu_stajda_izlenecek_yol.pdf |
| 3 | 0.0403 | 0.4999 | 0.5101 | student_affairs_policy | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 4 | 0.0279 | 0.4937 | 0.5070 | student_affairs_policy | document.pdf |
| 5 | 0.0215 | 0.4905 | 0.5054 | student_affairs_policy | document.pdf |
| 6 | 0.0178 | 0.4886 | 0.5044 | student_affairs_policy | staj_bilgilendirme_toplantısı_sunumu_2024_2025.pdf |
| 7 | 0.0146 | 0.4871 | 0.5037 | student_affairs_policy | yonerge_onlisans_lisans_staj.pdf |
| 8 | 0.0109 | 0.4852 | 0.5027 | student_affairs_policy | staj_iş_akışı.pdf |
| 9 | 0.0106 | 0.4851 | 0.5027 | student_affairs_policy | staj_bilgilendirme_toplantısı_sunumu_2024_2025.pdf |
| 10 | 0.0103 | 0.4849 | 0.5026 | student_affairs_policy | staj_esaslar.pdf |

### Staj defterini teslim etme suresi ne kadardir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.7900 | 0.8174 | 0.6878 | student_affairs_policy | çevre_mühendisliği_bölümü_staj_ilkeleri.docx |
| 2 | 0.7891 | 0.8171 | 0.6876 | student_affairs_policy | çevre_mühendisliği_bölümü_staj_ilkeleri.docx |
| 3 | 0.4648 | 0.7003 | 0.6142 | student_affairs_policy | zorunlu_stajda_izlenecek_yol.pdf |
| 4 | 0.2690 | 0.6123 | 0.5669 | student_affairs_policy | zorunlu_stajda_izlenecek_yol.pdf |
| 5 | 0.0997 | 0.5296 | 0.5249 | student_affairs_policy | zorunlu_gönüllü_staj_başvuru_formu.pdf |
| 6 | 0.0513 | 0.5054 | 0.5128 | student_affairs_policy | yonerge_onlisans_lisans_staj.pdf |
| 7 | 0.0218 | 0.4907 | 0.5055 | student_affairs_policy | staj_sıkça_sorulanlar.pdf |
| 8 | 0.0183 | 0.4889 | 0.5046 | student_affairs_policy | staj_sıkça_sorulanlar.pdf |
| 9 | 0.0120 | 0.4858 | 0.5030 | curriculum_catalog | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |
| 10 | 0.0065 | 0.4830 | 0.5016 | student_affairs_policy | 1_elektrik_elektronik_staj_ilkeleri_ve_uygulama_esasları.pdf |

### Bitirme projesi danismani nasil belirlenir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.3296 | 0.6406 | 0.5817 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 2 | 0.3074 | 0.6304 | 0.5762 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 3 | 0.1787 | 0.5687 | 0.5446 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 4 | 0.0472 | 0.5034 | 0.5118 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 5 | 0.0405 | 0.5000 | 0.5101 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 6 | 0.0359 | 0.4977 | 0.5090 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 7 | 0.0259 | 0.4927 | 0.5065 | - | mat_bitirme_çalışması_ilkeleri.pdf |
| 8 | 0.0223 | 0.4909 | 0.5056 | - | mat_bitirme_çalışması_ilkeleri.pdf |
| 9 | 0.0170 | 0.4882 | 0.5042 | - | bitirme_projesi_şablon.docx |
| 10 | 0.0169 | 0.4882 | 0.5042 | - | bitirme_projesi_sunum_değerlendirme_formu.docx |

### Staj yerim degisirse ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.3435 | 0.6470 | 0.5850 | student_affairs_policy | zorunlu_gönüllü_staj_başvuru_formu.pdf |
| 2 | 0.0505 | 0.5050 | 0.5126 | student_affairs_policy | staj_esaslar.pdf |
| 3 | 0.0436 | 0.5016 | 0.5109 | student_affairs_policy | staj_ilkeleri_23122019_inş_müh.pdf |
| 4 | 0.0411 | 0.5003 | 0.5103 | student_affairs_policy | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 5 | 0.0370 | 0.4982 | 0.5092 | student_affairs_policy | staj_yönergesi.pdf |
| 6 | 0.0344 | 0.4969 | 0.5086 | student_affairs_policy | 1_elektrik_elektronik_staj_ilkeleri_ve_uygulama_esasları.pdf |
| 7 | 0.0273 | 0.4934 | 0.5068 | student_affairs_policy | işyeri_staj_sözleşmesi.pdf |
| 8 | 0.0150 | 0.4873 | 0.5038 | student_affairs_policy | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |
| 9 | 0.0070 | 0.4833 | 0.5018 | student_affairs_policy | yonerge_onlisans_lisans_staj.pdf |
| 10 | 0.0070 | 0.4832 | 0.5017 | student_affairs_policy | document.pdf |

### Lisansustu ogrenciler icin tez teslim suresi ne kadardir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.4119 | 0.6776 | 0.6015 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 2 | 0.2100 | 0.5839 | 0.5523 | student_affairs_policy | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 3 | 0.1091 | 0.5343 | 0.5273 | curriculum_catalog | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 4 | 0.0896 | 0.5245 | 0.5224 | curriculum_catalog | lisansüstü_eğitim_ve.pdf |
| 5 | 0.0391 | 0.4993 | 0.5098 | - | lisansüstü_eğitim_ve.pdf |
| 6 | 0.0336 | 0.4965 | 0.5084 | student_affairs_policy | yonerge_lisansustu_danismanlik_ders_verme.pdf |
| 7 | 0.0307 | 0.4951 | 0.5077 | curriculum_catalog | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 8 | 0.0246 | 0.4921 | 0.5062 | curriculum_catalog | lisansüstü_eğitim_ve.pdf |
| 9 | 0.0232 | 0.4914 | 0.5058 | academic_calendar | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 10 | 0.0161 | 0.4878 | 0.5040 | - | lisansüstü_eğitim_ve.pdf |

---

*Bu rapor `scripts/analyze_reranker_scores.py` tarafindan otomatik uretilmistir.*