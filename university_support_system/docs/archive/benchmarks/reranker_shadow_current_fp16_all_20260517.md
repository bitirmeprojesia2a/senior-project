# Reranker Skor Dagilim Analizi

**Tarih:** 2026-05-17 16:36
**Model:** BAAI/bge-reranker-v2-m3
**Device:** cuda
**Torch dtype:** float16->torch.float16
**Kalibrasyon:** shift=0.0652, scale=0.5
**Toplam Soru:** 40
**Toplam Skor Ornegi:** 400
**Toplam sure:** 101.0s
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
| p10 | 0.0004 |
| p25 | 0.0075 |
| median | 0.0595 |
| mean | 0.2258 |
| p75 | 0.3408 |
| p90 | 0.8701 |
| max | 1.0 |
| std | 0.3119 |

### Kalibre Edilmis Skorlar (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.4675 |
| p10 | 0.4676 |
| p25 | 0.4712 |
| median | 0.4971 |
| mean | 0.568 |
| p75 | 0.6344 |
| p90 | 0.8334 |
| max | 0.8664 |
| std | 0.1305 |

### Duz Sigmoid Skorlar (Referans)

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.5 |
| p10 | 0.5001 |
| p25 | 0.5019 |
| median | 0.5149 |
| mean | 0.5541 |
| p75 | 0.5844 |
| p90 | 0.7048 |
| max | 0.7311 |
| std | 0.0732 |

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
| mean | 0.623 |
| p75 | 0.9886 |
| p90 | 0.9977 |
| max | 1.0 |
| std | 0.3825 |

### Kalibre Top-1 Skorlari (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.4675 |
| p10 | 0.4886 |
| p25 | 0.6144 |
| median | 0.7733 |
| mean | 0.729 |
| p75 | 0.8638 |
| p90 | 0.8659 |
| max | 0.8664 |
| std | 0.1495 |

### Duz Sigmoid Top-1 Skorlari (Referans)

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.5 |
| p10 | 0.5106 |
| p25 | 0.574 |
| median | 0.6636 |
| mean | 0.6464 |
| p75 | 0.7288 |
| p90 | 0.7306 |
| max | 0.7311 |
| std | 0.0878 |

---

## Sigmoid Kalibrasyon Onerisi

- **Formul:** `sigmoid((score - 0.0595) / 0.5000)`
- **Shift (median):** 0.0595
- **Scale (IQR):** 0.5
- **Onerilen direct-RAG esigi:** 0.637
- **Onerilen min-source esigi:** 0.474

---

## Soru Bazli Detaylar

### Sistem giris sifremi unuttum, ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9883 | 0.8637 | 0.7287 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.0042 | 0.4695 | 0.5011 | student_affairs_policy | öğrenci_toplulukları_yönergesi.pdf |
| 3 | 0.0009 | 0.4679 | 0.5002 | student_affairs_policy | sık_sorulan_sorular.txt |
| 4 | 0.0009 | 0.4679 | 0.5002 | student_affairs_policy | sık_sorulan_sorular.txt |
| 5 | 0.0007 | 0.4678 | 0.5002 | student_affairs_policy | sık_sorulan_sorular.txt |
| 6 | 0.0005 | 0.4677 | 0.5001 | student_affairs_policy | öğrenci_işleri_birimi.txt |
| 7 | 0.0004 | 0.4677 | 0.5001 | student_affairs_policy | kimlik_kartı_yönergesi.pdf |
| 8 | 0.0003 | 0.4676 | 0.5001 | student_affairs_policy | kimlik_kartı_yönergesi.pdf |
| 9 | 0.0003 | 0.4676 | 0.5001 | student_affairs_policy | öğrenci_işleri_birimi.txt |
| 10 | 0.0003 | 0.4676 | 0.5001 | student_affairs_policy | sık_sorulan_sorular.txt |

### UBYS uzerinden ilisik kesme talebini nasil baslatirim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9941 | 0.8650 | 0.7299 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.9526 | 0.8551 | 0.7216 | student_affairs_policy | sık_sorulan_sorular.txt |
| 3 | 0.2417 | 0.5873 | 0.5601 | student_affairs_policy | kimlik_kartı_yönergesi.pdf |
| 4 | 0.0346 | 0.4847 | 0.5087 | international_policy | öğrenci_işleri_birimi.txt |
| 5 | 0.0182 | 0.4765 | 0.5045 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.0093 | 0.4721 | 0.5023 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 7 | 0.0091 | 0.4720 | 0.5023 | international_policy | öğrenci_işleri_birimi.txt |
| 8 | 0.0019 | 0.4684 | 0.5005 | student_affairs_policy | sık_sorulan_sorular.txt |
| 9 | 0.0019 | 0.4684 | 0.5005 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0010 | 0.4679 | 0.5002 | student_affairs_policy | sık_sorulan_sorular.txt |

### Diplomami kaybettim, ikinci nusha icin ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9990 | 0.8662 | 0.7309 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.9766 | 0.8609 | 0.7264 | tuition_fee_catalog | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 3 | 0.1549 | 0.5447 | 0.5386 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 4 | 0.1140 | 0.5244 | 0.5285 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 5 | 0.0370 | 0.4859 | 0.5093 | tuition_fee_catalog | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 6 | 0.0126 | 0.4737 | 0.5032 | student_affairs_policy | sık_sorulan_sorular.txt |
| 7 | 0.0024 | 0.4687 | 0.5006 | international_policy | sık_sorulan_sorular.txt |
| 8 | 0.0014 | 0.4681 | 0.5003 | student_affairs_policy | sık_sorulan_sorular.txt |
| 9 | 0.0013 | 0.4681 | 0.5003 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 10 | 0.0012 | 0.4681 | 0.5003 | student_affairs_policy | sık_sorulan_sorular.txt |

### Diploma eki transkript yerine gecer mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9995 | 0.8663 | 0.7310 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.4294 | 0.6745 | 0.6057 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 3 | 0.1815 | 0.5579 | 0.5453 | international_policy | sık_sorulan_sorular.txt |
| 4 | 0.0319 | 0.4834 | 0.5080 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 5 | 0.0217 | 0.4782 | 0.5054 | student_affairs_policy | sık_sorulan_sorular.txt |
| 6 | 0.0179 | 0.4764 | 0.5045 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 7 | 0.0105 | 0.4727 | 0.5026 | student_affairs_policy | sık_sorulan_sorular.txt |
| 8 | 0.0093 | 0.4721 | 0.5023 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 9 | 0.0084 | 0.4717 | 0.5021 | student_affairs_policy | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 10 | 0.0069 | 0.4709 | 0.5017 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |

### Kayit dondurma ile kayit yaptirmamak arasinda ne fark var?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9810 | 0.8619 | 0.7273 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.2849 | 0.6081 | 0.5707 | student_affairs_policy | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 3 | 0.2737 | 0.6028 | 0.5680 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 4 | 0.0779 | 0.5064 | 0.5195 | student_affairs_policy | sık_sorulan_sorular.txt |
| 5 | 0.0441 | 0.4895 | 0.5110 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 6 | 0.0408 | 0.4878 | 0.5102 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 7 | 0.0234 | 0.4791 | 0.5058 | student_affairs_policy | öğrenci_konseyi_yönergesi.pdf |
| 8 | 0.0180 | 0.4764 | 0.5045 | tuition_fee_catalog | sık_sorulan_sorular.txt |
| 9 | 0.0138 | 0.4743 | 0.5035 | student_affairs_policy | ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf |
| 10 | 0.0011 | 0.4680 | 0.5003 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Hazirlik sinifi okuyan ogrenci transkriptsiz Ek Madde-1 ile yatay gecis basvurusu yapabilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9790 | 0.8615 | 0.7269 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.7798 | 0.8068 | 0.6856 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 3 | 0.5156 | 0.7111 | 0.6261 | international_policy | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 4 | 0.2588 | 0.5956 | 0.5643 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 5 | 0.2218 | 0.5777 | 0.5552 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 6 | 0.2065 | 0.5702 | 0.5515 | international_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 7 | 0.1766 | 0.5555 | 0.5440 | student_affairs_policy | sık_sorulan_sorular.txt |
| 8 | 0.1592 | 0.5469 | 0.5397 | student_affairs_policy | sık_sorulan_sorular.txt |
| 9 | 0.0453 | 0.4900 | 0.5113 | student_affairs_policy | ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf |
| 10 | 0.0302 | 0.4825 | 0.5075 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Birden fazla universiteye yatay gecis basvurusu yapabilir miyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9966 | 0.8656 | 0.7304 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.2891 | 0.6101 | 0.5718 | student_affairs_policy | sık_sorulan_sorular.txt |
| 3 | 0.1664 | 0.5504 | 0.5415 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 4 | 0.0873 | 0.5110 | 0.5218 | student_affairs_policy | sık_sorulan_sorular.txt |
| 5 | 0.0299 | 0.4824 | 0.5075 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.0220 | 0.4784 | 0.5055 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 7 | 0.0172 | 0.4760 | 0.5043 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 8 | 0.0144 | 0.4746 | 0.5036 | student_affairs_policy | sık_sorulan_sorular.txt |
| 9 | 0.0136 | 0.4742 | 0.5034 | student_affairs_policy | ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf |
| 10 | 0.0095 | 0.4722 | 0.5024 | student_affairs_policy | yonerge_onlisans_lisans_yatay_gecis.pdf |

### Ozel ogrenci olarak ne zaman basvuru yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.7266 | 0.7896 | 0.6741 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.2294 | 0.5814 | 0.5571 | student_affairs_policy | sık_sorulan_sorular.txt |
| 3 | 0.1025 | 0.5186 | 0.5256 | student_affairs_policy | sık_sorulan_sorular.txt |
| 4 | 0.0282 | 0.4815 | 0.5070 | student_affairs_policy | sık_sorulan_sorular.txt |
| 5 | 0.0050 | 0.4699 | 0.5013 | student_affairs_policy | sık_sorulan_sorular.txt |
| 6 | 0.0007 | 0.4678 | 0.5002 | curriculum_catalog | sık_sorulan_sorular.txt |
| 7 | 0.0006 | 0.4678 | 0.5002 | student_affairs_policy | yaz_okulu_eğitim_öğretim.pdf |
| 8 | 0.0006 | 0.4677 | 0.5002 | student_affairs_policy | sık_sorulan_sorular.txt |
| 9 | 0.0005 | 0.4677 | 0.5001 | student_affairs_policy | sık_sorulan_sorular.txt |
| 10 | 0.0005 | 0.4677 | 0.5001 | student_affairs_policy | öğrenci_toplulukları_yönergesi.pdf |

### Ozel ogrenci olarak basvuru icin hangi belgeler gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.6147 | 0.7501 | 0.6490 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.3889 | 0.6564 | 0.5960 | student_affairs_policy | sık_sorulan_sorular.txt |
| 3 | 0.3735 | 0.6495 | 0.5923 | - | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 4 | 0.3225 | 0.6259 | 0.5799 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 5 | 0.2922 | 0.6116 | 0.5725 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 6 | 0.1158 | 0.5253 | 0.5289 | student_affairs_policy | sık_sorulan_sorular.txt |
| 7 | 0.0947 | 0.5147 | 0.5236 | international_policy | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 8 | 0.0790 | 0.5069 | 0.5198 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 9 | 0.0605 | 0.4977 | 0.5151 | student_affairs_policy | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 10 | 0.0577 | 0.4963 | 0.5144 | student_affairs_policy | sık_sorulan_sorular.txt |

### Daha once aldigim dersler icin muafiyet basvurusunu ne zaman yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9736 | 0.8602 | 0.7258 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.9199 | 0.8468 | 0.7150 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 3 | 0.8633 | 0.8315 | 0.7033 | student_affairs_policy | sık_sorulan_sorular.txt |
| 4 | 0.4211 | 0.6708 | 0.6038 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 5 | 0.3699 | 0.6478 | 0.5914 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 6 | 0.3464 | 0.6370 | 0.5858 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 7 | 0.3396 | 0.6339 | 0.5841 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 8 | 0.1636 | 0.5490 | 0.5408 | student_affairs_policy | yonerge_ders_yeterlik_muafiyet_intibak.pdf |
| 9 | 0.1432 | 0.5389 | 0.5357 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 10 | 0.1306 | 0.5327 | 0.5326 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |

### Ikamet izni basvurusu icin hangi belgeler gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9863 | 0.8632 | 0.7284 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 2 | 0.9551 | 0.8557 | 0.7221 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 3 | 0.9502 | 0.8545 | 0.7212 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 4 | 0.8901 | 0.8389 | 0.7089 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 5 | 0.8574 | 0.8298 | 0.7021 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 6 | 0.7832 | 0.8078 | 0.6864 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 7 | 0.6758 | 0.7723 | 0.6628 | international_policy | uluslararası_öğrenci_ikamet_işlemleri.pdf |
| 8 | 0.5747 | 0.7348 | 0.6398 | international_policy | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 9 | 0.5674 | 0.7319 | 0.6382 | international_policy | uluslararası_öğrenci.pdf |
| 10 | 0.4866 | 0.6990 | 0.6193 | - | muvafakatname.pdf |

### Denklik belgesi ne zaman gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9116 | 0.8446 | 0.7133 | international_policy | denklik_belgesi.pdf |
| 2 | 0.3589 | 0.6428 | 0.5888 | academic_calendar | tyb.pdf |
| 3 | 0.2742 | 0.6030 | 0.5681 | international_policy | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 4 | 0.0848 | 0.5098 | 0.5212 | international_policy | uluslararası_öğrenci.pdf |
| 5 | 0.0718 | 0.5033 | 0.5180 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |
| 6 | 0.0611 | 0.4979 | 0.5153 | - | denklik_belgesi.pdf |
| 7 | 0.0584 | 0.4966 | 0.5146 | student_affairs_policy | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 8 | 0.0563 | 0.4956 | 0.5141 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 9 | 0.0537 | 0.4943 | 0.5134 | tuition_fee_catalog | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |
| 10 | 0.0258 | 0.4803 | 0.5064 | - | yurda_giriş_çıkış_belgesi.pdf |

### YOS ID numarami nasil ogrenebilirim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0332 | 0.4840 | 0.5083 | international_policy | uluslararası_öğrenci.pdf |
| 2 | 0.0231 | 0.4790 | 0.5058 | international_policy | yös_ıd_no_öğrenme.pdf |
| 3 | 0.0203 | 0.4776 | 0.5051 | international_policy | öğrenci_no_öğrenme.pdf |
| 4 | 0.0015 | 0.4682 | 0.5004 | international_policy | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 5 | 0.0013 | 0.4681 | 0.5003 | - | ön_kayıt_kılavuzu_başvuru_adımları.pdf |
| 6 | 0.0007 | 0.4678 | 0.5002 | international_policy | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 7 | 0.0007 | 0.4678 | 0.5002 | international_policy | yonerge_uluslararasi_ogrenci_yatay_gecis.pdf |
| 8 | 0.0005 | 0.4677 | 0.5001 | international_policy | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 9 | 0.0005 | 0.4677 | 0.5001 | international_policy | uluslararası_öğrenci_kimlik_bilgileri_güncelleme_formu.pdf |
| 10 | 0.0004 | 0.4677 | 0.5001 | international_policy | özel_yetenek_sınavı_yönergesi.pdf |

### Uluslararasi ogrenci kaydinda evrak teslim formu gerekiyor mu?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9858 | 0.8631 | 0.7283 | international_policy | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 2 | 0.9839 | 0.8626 | 0.7279 | international_policy | uluslararası_öğrenci_yönergesi.pdf |
| 3 | 0.9619 | 0.8573 | 0.7235 | international_policy | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 4 | 0.9072 | 0.8434 | 0.7124 | international_policy | uluslararası_öğrenci_evrak_teslim_formu_r1.pdf |
| 5 | 0.8687 | 0.8330 | 0.7045 | international_policy | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 6 | 0.4834 | 0.6977 | 0.6186 | international_policy | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 7 | 0.4675 | 0.6910 | 0.6148 | international_policy | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 8 | 0.1615 | 0.5480 | 0.5403 | international_policy | uluslararası_öğrenci.pdf |
| 9 | 0.1368 | 0.5358 | 0.5342 | international_policy | ön_kayıt_kılavuzu_başvuru_adımları.pdf |
| 10 | 0.1195 | 0.5271 | 0.5298 | international_policy | uluslararası_öğrenci.pdf |

### TOMER ne is yapar?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0426 | 0.4887 | 0.5107 | international_policy | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 2 | 0.0003 | 0.4676 | 0.5001 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 3 | 0.0003 | 0.4676 | 0.5001 | student_affairs_policy | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 4 | 0.0002 | 0.4676 | 0.5001 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 5 | 0.0002 | 0.4676 | 0.5001 | - | dil_ve_konuşma_bozuklukları.pdf |
| 6 | 0.0002 | 0.4676 | 0.5001 | student_affairs_policy | kök_hücre_araştırma_merkezi_yönergesi.pdf |
| 7 | 0.0001 | 0.4675 | 0.5000 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 8 | 0.0001 | 0.4675 | 0.5000 | student_affairs_policy | siber_güvenlik_ve_bilişim_teknolojileri.pdf |
| 9 | 0.0001 | 0.4675 | 0.5000 | student_affairs_policy | kariyer_merkezi_yönergesi.pdf |
| 10 | 0.0001 | 0.4675 | 0.5000 | student_affairs_policy | güvenlik_hizmetlerinin_yürütülmesine_dair_yönerge.pdf |

### Pedagojik formasyon dersleri transkripte dahil edilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 1.0000 | 0.8664 | 0.7311 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.9951 | 0.8653 | 0.7301 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 3 | 0.9922 | 0.8646 | 0.7295 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 4 | 0.5254 | 0.7151 | 0.6284 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 5 | 0.3271 | 0.6281 | 0.5811 | student_affairs_policy | yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf |
| 6 | 0.2883 | 0.6098 | 0.5716 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.2157 | 0.5747 | 0.5537 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 8 | 0.1583 | 0.5464 | 0.5395 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.1072 | 0.5210 | 0.5268 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.1014 | 0.5181 | 0.5253 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |

### Pedagojik formasyon mezuniyet ortalamasina dahil edilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9961 | 0.8655 | 0.7303 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.9927 | 0.8647 | 0.7296 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 3 | 0.9033 | 0.8424 | 0.7116 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 4 | 0.7383 | 0.7935 | 0.6766 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.6128 | 0.7494 | 0.6486 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 6 | 0.5376 | 0.7201 | 0.6313 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.3782 | 0.6516 | 0.5934 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 8 | 0.2844 | 0.6079 | 0.5706 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.2632 | 0.5977 | 0.5654 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.2568 | 0.5947 | 0.5639 | curriculum_catalog | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |

### Pedagojik formasyon alirsam mezuniyet 240 AKTS'nin ustune cikabilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9985 | 0.8661 | 0.7308 | curriculum_catalog | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.8486 | 0.8273 | 0.7003 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 3 | 0.6641 | 0.7681 | 0.6602 | student_affairs_policy | çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf |
| 4 | 0.1874 | 0.5608 | 0.5467 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 5 | 0.1865 | 0.5604 | 0.5465 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 6 | 0.1852 | 0.5597 | 0.5462 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.1213 | 0.5280 | 0.5303 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 8 | 0.0964 | 0.5156 | 0.5241 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.0827 | 0.5088 | 0.5207 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.0764 | 0.5056 | 0.5191 | student_affairs_policy | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |

### Pedagojik formasyon derslerinin tumunu almak zorunlu mu?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9976 | 0.8658 | 0.7306 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.5366 | 0.7197 | 0.6310 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 3 | 0.3562 | 0.6415 | 0.5881 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 4 | 0.3525 | 0.6398 | 0.5872 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 5 | 0.3389 | 0.6335 | 0.5839 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 6 | 0.3081 | 0.6191 | 0.5764 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.2263 | 0.5799 | 0.5563 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 8 | 0.1166 | 0.5257 | 0.5291 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.0989 | 0.5169 | 0.5247 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 10 | 0.0988 | 0.5168 | 0.5247 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |

### Pedagojik formasyon dersleri en erken hangi yariyilda alinabilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9604 | 0.8570 | 0.7232 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 2 | 0.8833 | 0.8370 | 0.7075 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 3 | 0.7378 | 0.7933 | 0.6765 | student_affairs_policy | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 4 | 0.6743 | 0.7718 | 0.6625 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.6421 | 0.7602 | 0.6552 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 6 | 0.6294 | 0.7555 | 0.6524 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 7 | 0.5801 | 0.7369 | 0.6411 | curriculum_catalog | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 8 | 0.5127 | 0.7099 | 0.6254 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 9 | 0.4062 | 0.6642 | 0.6002 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 10 | 0.3914 | 0.6575 | 0.5966 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |

### Yemek bursu basvurulari nereden yapilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9897 | 0.8640 | 0.7290 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 2 | 0.9014 | 0.8419 | 0.7112 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.6748 | 0.7719 | 0.6626 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.3799 | 0.6523 | 0.5938 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.2090 | 0.5714 | 0.5521 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.2064 | 0.5701 | 0.5514 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.1248 | 0.5297 | 0.5311 | student_affairs_policy | kimlik_kartı_yönergesi.pdf |
| 8 | 0.0930 | 0.5139 | 0.5232 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0808 | 0.5078 | 0.5202 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0628 | 0.4988 | 0.5157 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |

### Bursum hangi sartlarda kesilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0677 | 0.5012 | 0.5169 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 2 | 0.0546 | 0.4947 | 0.5136 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.0020 | 0.4685 | 0.5005 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.0011 | 0.4680 | 0.5003 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.0009 | 0.4679 | 0.5002 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.0009 | 0.4679 | 0.5002 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.0008 | 0.4679 | 0.5002 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0008 | 0.4679 | 0.5002 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0008 | 0.4679 | 0.5002 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0004 | 0.4677 | 0.5001 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |

### Kayit ekraninda borclu ya da fazla ucretli gorunuyorsam ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 2 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 5 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 6 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 7 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 9 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 10 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |

### Program suresini asarsam katki payi oder miyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0533 | 0.4941 | 0.5133 | tuition_fee_catalog | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |
| 2 | 0.0014 | 0.4681 | 0.5003 | tuition_fee_catalog | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |
| 3 | 0.0001 | 0.4675 | 0.5000 | international_policy | 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf |
| 4 | 0.0001 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 5 | 0.0001 | 0.4675 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.0001 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 7 | 0.0001 | 0.4675 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0001 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 9 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | öğrenci_yemek_bursu_yönergesi.pdf |

### Harc iadesi icin IBAN ve dekontla nereye basvurmam gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 2 | 0.0000 | 0.4675 | 0.5000 | - | idari_ve_mali_işler_birimi.txt |
| 3 | 0.0000 | 0.4675 | 0.5000 | international_policy | 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf |
| 4 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 5 | 0.0000 | 0.4675 | 0.5000 | - | idari_ve_mali_işler_birimi.txt |
| 6 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 7 | 0.0000 | 0.4675 | 0.5000 | international_policy | 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf |
| 8 | 0.0000 | 0.4675 | 0.5000 | - | idari_ve_mali_işler_birimi.txt |
| 9 | 0.0000 | 0.4675 | 0.5000 | student_affairs_policy | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 10 | 0.0000 | 0.4675 | 0.5000 | tuition_fee_catalog | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |

### Sinava giremedigim ders icin mazeret sinavi basvurusu nasil yapilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.4504 | 0.6836 | 0.6107 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 2 | 0.3989 | 0.6609 | 0.5984 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.2600 | 0.5962 | 0.5646 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 4 | 0.2203 | 0.5770 | 0.5549 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 5 | 0.0898 | 0.5123 | 0.5224 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 6 | 0.0536 | 0.4942 | 0.5134 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.0435 | 0.4891 | 0.5109 | student_affairs_policy | sık_sorulan_sorular.txt |
| 8 | 0.0339 | 0.4844 | 0.5085 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 9 | 0.0204 | 0.4776 | 0.5051 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 10 | 0.0077 | 0.4713 | 0.5019 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |

### Bir dersten kac kez sinav hakkina sahibim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.3459 | 0.6368 | 0.5856 | student_affairs_policy | uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf |
| 2 | 0.0580 | 0.4964 | 0.5145 | student_affairs_policy | mühendislik_fakültesi_ortak_sınav_yönergesi.pdf |
| 3 | 0.0557 | 0.4953 | 0.5139 | student_affairs_policy | uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf |
| 4 | 0.0128 | 0.4738 | 0.5032 | student_affairs_policy | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |
| 5 | 0.0113 | 0.4731 | 0.5028 | student_affairs_policy | bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf |
| 6 | 0.0109 | 0.4729 | 0.5027 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 7 | 0.0090 | 0.4719 | 0.5023 | student_affairs_policy | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 8 | 0.0082 | 0.4715 | 0.5020 | international_policy | yabancı_dil_eğitim_öğretimi_yönergesi.pdf |
| 9 | 0.0053 | 0.4701 | 0.5013 | student_affairs_policy | bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf |
| 10 | 0.0041 | 0.4695 | 0.5010 | student_affairs_policy | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |

### Bagil degerlendirme sistemi nasil isler?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.2440 | 0.5885 | 0.5607 | student_affairs_policy | bağıl_değerlendirme_yönergesi.pdf |
| 2 | 0.0850 | 0.5099 | 0.5212 | student_affairs_policy | bağıl_değerlendirme_yönergesi.pdf |
| 3 | 0.0847 | 0.5097 | 0.5212 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 4 | 0.0828 | 0.5088 | 0.5207 | student_affairs_policy | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 5 | 0.0314 | 0.4831 | 0.5078 | student_affairs_policy | bağıl_değerlendirme_yönergesi.pdf |
| 6 | 0.0302 | 0.4825 | 0.5075 | student_affairs_policy | bağıl_değerlendirme_yönergesi.pdf |
| 7 | 0.0235 | 0.4792 | 0.5059 | student_affairs_policy | bağıl_değerlendirme_yönergesi.pdf |
| 8 | 0.0154 | 0.4751 | 0.5038 | student_affairs_policy | sık_sorulan_sorular.txt |
| 9 | 0.0088 | 0.4718 | 0.5022 | curriculum_catalog | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0070 | 0.4710 | 0.5018 | student_affairs_policy | yonerge_bagil_degerlendirme.pdf |

### Final sinavina girme sarti olarak devam yuzdesi kac olmalidir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0557 | 0.4953 | 0.5139 | international_policy | yonerge_yabanci_dil_egitim_ogretim.pdf |
| 2 | 0.0296 | 0.4822 | 0.5074 | student_affairs_policy | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |
| 3 | 0.0188 | 0.4768 | 0.5047 | international_policy | yabancı_dil_eğitim_öğretimi_yönergesi.pdf |
| 4 | 0.0168 | 0.4758 | 0.5042 | - | lisansüstü_eğitim_ve.pdf |
| 5 | 0.0168 | 0.4758 | 0.5042 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 6 | 0.0148 | 0.4748 | 0.5037 | student_affairs_policy | yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf |
| 7 | 0.0142 | 0.4745 | 0.5035 | student_affairs_policy | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |
| 8 | 0.0090 | 0.4719 | 0.5022 | international_policy | yonerge_yabanci_dil_egitim_ogretim.pdf |
| 9 | 0.0062 | 0.4705 | 0.5016 | student_affairs_policy | sürekli_eğitim_merkezi_yönergesi.pdf |
| 10 | 0.0054 | 0.4701 | 0.5014 | - | tıp_fakültesi_tıp_doktorluğu_programı.pdf |

### Not itirazi icin ne kadar sureye sahibim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.5361 | 0.7195 | 0.6309 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.1685 | 0.5514 | 0.5420 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.1273 | 0.5310 | 0.5318 | student_affairs_policy | yonerge_yuzde_on_basari_degerlendirme.pdf |
| 4 | 0.0844 | 0.5096 | 0.5211 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 5 | 0.0421 | 0.4884 | 0.5105 | student_affairs_policy | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 6 | 0.0310 | 0.4829 | 0.5077 | student_affairs_policy | ders_yeterlilik_sınavı_uygulama_yönergesi.pdf |
| 7 | 0.0234 | 0.4791 | 0.5058 | student_affairs_policy | sık_sorulan_sorular.txt |
| 8 | 0.0147 | 0.4748 | 0.5037 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 9 | 0.0057 | 0.4703 | 0.5014 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 10 | 0.0027 | 0.4688 | 0.5007 | student_affairs_policy | öğrenci_konukevi_uygulama_yönergesi.pdf |

### Yaz okulunda en fazla kac ders alabilirim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9951 | 0.8653 | 0.7301 | student_affairs_policy | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 2 | 0.9937 | 0.8649 | 0.7298 | student_affairs_policy | yaz_okulu_eğitim_öğretim.pdf |
| 3 | 0.9521 | 0.8549 | 0.7215 | international_policy | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 4 | 0.9512 | 0.8547 | 0.7214 | international_policy | yonerge_yaz_okulu_egitim_ogretim.pdf |
| 5 | 0.9492 | 0.8542 | 0.7210 | academic_calendar | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.8843 | 0.8373 | 0.7077 | international_policy | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.7227 | 0.7883 | 0.6732 | tuition_fee_catalog | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 8 | 0.4114 | 0.6665 | 0.6014 | student_affairs_policy | yaz_okulu_eğitim_öğretim.pdf |
| 9 | 0.4114 | 0.6665 | 0.6014 | student_affairs_policy | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 10 | 0.1849 | 0.5596 | 0.5461 | student_affairs_policy | yaz_okulu_eğitim_öğretim.pdf |

### Basarisiz oldugum dersi tekrar almak icin ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.5454 | 0.7232 | 0.6331 | student_affairs_policy | sık_sorulan_sorular.txt |
| 2 | 0.5430 | 0.7222 | 0.6325 | student_affairs_policy | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 3 | 0.5073 | 0.7077 | 0.6242 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 4 | 0.3975 | 0.6603 | 0.5981 | student_affairs_policy | sık_sorulan_sorular.txt |
| 5 | 0.3174 | 0.6235 | 0.5787 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.3086 | 0.6193 | 0.5765 | student_affairs_policy | sık_sorulan_sorular.txt |
| 7 | 0.1863 | 0.5602 | 0.5464 | student_affairs_policy | sık_sorulan_sorular.txt |
| 8 | 0.1810 | 0.5577 | 0.5451 | student_affairs_policy | sık_sorulan_sorular.txt |
| 9 | 0.1675 | 0.5510 | 0.5418 | curriculum_catalog | sık_sorulan_sorular.txt |
| 10 | 0.1405 | 0.5376 | 0.5351 | - | endüstri_mühendisliği_tasarımı_yaptırma_ve_değerlendirme_ı̇lkeleri_güncel.pdf |

### Azami ogrenim suresi dolunca ne olur?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.1594 | 0.5470 | 0.5398 | - | lisansüstü_eğitim_ve.pdf |
| 2 | 0.1061 | 0.5205 | 0.5265 | - | lisansüstü_eğitim_ve.pdf |
| 3 | 0.0419 | 0.4884 | 0.5105 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 4 | 0.0143 | 0.4746 | 0.5036 | - | lisansüstü_eğitim_ve.pdf |
| 5 | 0.0114 | 0.4731 | 0.5028 | student_affairs_policy | çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf |
| 6 | 0.0060 | 0.4705 | 0.5015 | student_affairs_policy | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.0039 | 0.4694 | 0.5010 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 8 | 0.0034 | 0.4691 | 0.5009 | - | lisansüstü_eğitim_ve.pdf |
| 9 | 0.0031 | 0.4690 | 0.5008 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.0028 | 0.4688 | 0.5007 | - | lisansüstü_eğitim_ve.pdf |

### Donem dondurma icin saglik raporu yeterli mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0403 | 0.4875 | 0.5101 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 2 | 0.0035 | 0.4692 | 0.5009 | student_affairs_policy | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 3 | 0.0012 | 0.4681 | 0.5003 | international_policy | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 4 | 0.0012 | 0.4681 | 0.5003 | student_affairs_policy | sık_sorulan_sorular.txt |
| 5 | 0.0011 | 0.4680 | 0.5003 | student_affairs_policy | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 6 | 0.0011 | 0.4680 | 0.5003 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.0010 | 0.4680 | 0.5003 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 8 | 0.0006 | 0.4677 | 0.5001 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 9 | 0.0006 | 0.4677 | 0.5001 | curriculum_catalog | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 10 | 0.0005 | 0.4677 | 0.5001 | curriculum_catalog | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Mezuniyet icin GNO en az kac olmalidir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.4590 | 0.6873 | 0.6128 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 2 | 0.3445 | 0.6361 | 0.5853 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.2104 | 0.5721 | 0.5524 | student_affairs_policy | sık_sorulan_sorular.txt |
| 4 | 0.1060 | 0.5204 | 0.5265 | student_affairs_policy | ön_lisans_ve_lisans.pdf |
| 5 | 0.0204 | 0.4776 | 0.5051 | student_affairs_policy | sık_sorulan_sorular.txt |
| 6 | 0.0132 | 0.4740 | 0.5033 | - | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.0123 | 0.4736 | 0.5031 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 8 | 0.0120 | 0.4734 | 0.5030 | student_affairs_policy | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 9 | 0.0055 | 0.4702 | 0.5014 | student_affairs_policy | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0035 | 0.4692 | 0.5009 | student_affairs_policy | ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf |

### Zorunlu staj icin SGK baslangic islemleri nasil yapilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.3164 | 0.6230 | 0.5784 | student_affairs_policy | staj_iş_akışı.pdf |
| 2 | 0.2064 | 0.5701 | 0.5514 | student_affairs_policy | zorunlu_stajda_izlenecek_yol.pdf |
| 3 | 0.0964 | 0.5156 | 0.5241 | student_affairs_policy | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 4 | 0.0517 | 0.4932 | 0.5129 | student_affairs_policy | document.pdf |
| 5 | 0.0340 | 0.4844 | 0.5085 | student_affairs_policy | document.pdf |
| 6 | 0.0267 | 0.4807 | 0.5067 | student_affairs_policy | staj_bilgilendirme_toplantısı_sunumu_2024_2025.pdf |
| 7 | 0.0265 | 0.4806 | 0.5066 | student_affairs_policy | yonerge_onlisans_lisans_staj.pdf |
| 8 | 0.0207 | 0.4778 | 0.5052 | student_affairs_policy | staj_esaslar.pdf |
| 9 | 0.0170 | 0.4759 | 0.5042 | student_affairs_policy | staj_iş_akışı.pdf |
| 10 | 0.0158 | 0.4753 | 0.5039 | student_affairs_policy | staj_ilkeleri_23122019_inş_müh.pdf |

### Staj defterini teslim etme suresi ne kadardir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9028 | 0.8423 | 0.7115 | student_affairs_policy | çevre_mühendisliği_bölümü_staj_ilkeleri.docx |
| 2 | 0.8950 | 0.8402 | 0.7099 | student_affairs_policy | çevre_mühendisliği_bölümü_staj_ilkeleri.docx |
| 3 | 0.6694 | 0.7700 | 0.6614 | student_affairs_policy | zorunlu_stajda_izlenecek_yol.pdf |
| 4 | 0.3779 | 0.6515 | 0.5934 | student_affairs_policy | zorunlu_stajda_izlenecek_yol.pdf |
| 5 | 0.1638 | 0.5492 | 0.5409 | student_affairs_policy | zorunlu_gönüllü_staj_başvuru_formu.pdf |
| 6 | 0.0774 | 0.5061 | 0.5193 | student_affairs_policy | yonerge_onlisans_lisans_staj.pdf |
| 7 | 0.0433 | 0.4890 | 0.5108 | student_affairs_policy | staj_sıkça_sorulanlar.pdf |
| 8 | 0.0383 | 0.4866 | 0.5096 | student_affairs_policy | staj_sıkça_sorulanlar.pdf |
| 9 | 0.0177 | 0.4763 | 0.5044 | curriculum_catalog | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |
| 10 | 0.0116 | 0.4732 | 0.5029 | student_affairs_policy | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |

### Bitirme projesi danismani nasil belirlenir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.5024 | 0.7057 | 0.6230 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 2 | 0.4446 | 0.6811 | 0.6093 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 3 | 0.3357 | 0.6320 | 0.5831 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 4 | 0.0704 | 0.5026 | 0.5176 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 5 | 0.0521 | 0.4935 | 0.5130 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 6 | 0.0475 | 0.4912 | 0.5119 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 7 | 0.0369 | 0.4859 | 0.5092 | - | mat_bitirme_çalışması_ilkeleri.pdf |
| 8 | 0.0261 | 0.4804 | 0.5065 | - | mat_bitirme_çalışması_ilkeleri.pdf |
| 9 | 0.0243 | 0.4796 | 0.5061 | - | bitirme_projesi_sunum_değerlendirme_formu.docx |
| 10 | 0.0239 | 0.4794 | 0.5060 | - | bitirme_projesi_şablon.docx |

### Staj yerim degisirse ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.4597 | 0.6876 | 0.6129 | student_affairs_policy | zorunlu_gönüllü_staj_başvuru_formu.pdf |
| 2 | 0.0991 | 0.5170 | 0.5248 | student_affairs_policy | staj_esaslar.pdf |
| 3 | 0.0860 | 0.5104 | 0.5215 | student_affairs_policy | staj_ilkeleri_23122019_inş_müh.pdf |
| 4 | 0.0806 | 0.5077 | 0.5201 | student_affairs_policy | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 5 | 0.0703 | 0.5026 | 0.5176 | student_affairs_policy | staj_yönergesi.pdf |
| 6 | 0.0694 | 0.5021 | 0.5173 | student_affairs_policy | 1_elektrik_elektronik_staj_ilkeleri_ve_uygulama_esasları.pdf |
| 7 | 0.0518 | 0.4933 | 0.5130 | student_affairs_policy | işyeri_staj_sözleşmesi.pdf |
| 8 | 0.0349 | 0.4848 | 0.5087 | student_affairs_policy | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |
| 9 | 0.0175 | 0.4762 | 0.5044 | student_affairs_policy | yonerge_onlisans_lisans_staj.pdf |
| 10 | 0.0121 | 0.4735 | 0.5030 | student_affairs_policy | 1_elektrik_elektronik_staj_ilkeleri_ve_uygulama_esasları.pdf |

### Lisansustu ogrenciler icin tez teslim suresi ne kadardir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.6333 | 0.7570 | 0.6532 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 2 | 0.3369 | 0.6326 | 0.5834 | student_affairs_policy | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 3 | 0.1510 | 0.5428 | 0.5377 | curriculum_catalog | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 4 | 0.1205 | 0.5276 | 0.5301 | curriculum_catalog | lisansüstü_eğitim_ve.pdf |
| 5 | 0.0823 | 0.5085 | 0.5206 | - | lisansüstü_eğitim_ve.pdf |
| 6 | 0.0532 | 0.4940 | 0.5133 | student_affairs_policy | yonerge_lisansustu_danismanlik_ders_verme.pdf |
| 7 | 0.0381 | 0.4865 | 0.5095 | academic_calendar | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 8 | 0.0279 | 0.4814 | 0.5070 | - | lisansüstü_eğitim_ve.pdf |
| 9 | 0.0274 | 0.4811 | 0.5068 | academic_calendar | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 10 | 0.0268 | 0.4808 | 0.5067 | curriculum_catalog | lisansüstü_eğitim_ve.pdf |

---

*Bu rapor `scripts/analyze_reranker_scores.py` tarafindan otomatik uretilmistir.*