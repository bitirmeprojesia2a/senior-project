# Reranker Skor Dagilim Analizi

**Tarih:** 2026-05-17 13:26
**Model:** BAAI/bge-reranker-v2-m3
**Device:** cuda
**Torch dtype:** auto->None
**Kalibrasyon:** shift=0.0652, scale=0.5
**Toplam Soru:** 40
**Toplam Skor Ornegi:** 400
**Toplam sure:** 702.0s
**Kapsam:** Candidate pool + reranker analizi; final threshold/filtering adimlari buna dahil degildir.

---

## Top-1 Source Owner Ozeti

- Expected department match: 0/38
- Top-1 source owner dagilimi: -=40

---

## Tum Skorlar (Tum Adaylar)

### Ham Reranker Skorlari (Logit)

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.0 |
| p10 | 0.0004 |
| p25 | 0.007 |
| median | 0.0595 |
| mean | 0.2257 |
| p75 | 0.3412 |
| p90 | 0.87 |
| max | 0.9998 |
| std | 0.3119 |

### Kalibre Edilmis Skorlar (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.4675 |
| p10 | 0.4676 |
| p25 | 0.4709 |
| median | 0.4972 |
| mean | 0.568 |
| p75 | 0.6346 |
| p90 | 0.8333 |
| max | 0.8664 |
| std | 0.1305 |

### Duz Sigmoid Skorlar (Referans)

| Metrik | Deger |
|--------|-------|
| count | 400 |
| min | 0.5 |
| p10 | 0.5001 |
| p25 | 0.5017 |
| median | 0.5149 |
| mean | 0.5541 |
| p75 | 0.5845 |
| p90 | 0.7047 |
| max | 0.731 |
| std | 0.0732 |

---

## Top-1 Skorlar (Her Sorunun En Iyi Adayi)

### Ham Top-1 Skorlari (Logit)

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.0 |
| p10 | 0.0424 |
| p25 | 0.298 |
| median | 0.6797 |
| mean | 0.623 |
| p75 | 0.9887 |
| p90 | 0.9975 |
| max | 0.9998 |
| std | 0.3825 |

### Kalibre Top-1 Skorlari (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.4675 |
| p10 | 0.4886 |
| p25 | 0.6142 |
| median | 0.7732 |
| mean | 0.7289 |
| p75 | 0.8638 |
| p90 | 0.8658 |
| max | 0.8664 |
| std | 0.1495 |

### Duz Sigmoid Top-1 Skorlari (Referans)

| Metrik | Deger |
|--------|-------|
| count | 40 |
| min | 0.5 |
| p10 | 0.5106 |
| p25 | 0.5739 |
| median | 0.6636 |
| mean | 0.6464 |
| p75 | 0.7288 |
| p90 | 0.7306 |
| max | 0.731 |
| std | 0.0877 |

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
| 1 | 0.9883 | 0.8637 | 0.7287 | - | sık_sorulan_sorular.txt |
| 2 | 0.0042 | 0.4695 | 0.5011 | - | öğrenci_toplulukları_yönergesi.pdf |
| 3 | 0.0009 | 0.4679 | 0.5002 | - | sık_sorulan_sorular.txt |
| 4 | 0.0009 | 0.4679 | 0.5002 | - | sık_sorulan_sorular.txt |
| 5 | 0.0007 | 0.4678 | 0.5002 | - | sık_sorulan_sorular.txt |
| 6 | 0.0005 | 0.4677 | 0.5001 | - | öğrenci_işleri_birimi.txt |
| 7 | 0.0004 | 0.4677 | 0.5001 | - | kimlik_kartı_yönergesi.pdf |
| 8 | 0.0003 | 0.4676 | 0.5001 | - | kimlik_kartı_yönergesi.pdf |
| 9 | 0.0003 | 0.4676 | 0.5001 | - | öğrenci_işleri_birimi.txt |
| 10 | 0.0003 | 0.4676 | 0.5001 | - | sık_sorulan_sorular.txt |

### UBYS uzerinden ilisik kesme talebini nasil baslatirim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9942 | 0.8651 | 0.7299 | - | sık_sorulan_sorular.txt |
| 2 | 0.9524 | 0.8550 | 0.7216 | - | sık_sorulan_sorular.txt |
| 3 | 0.2417 | 0.5874 | 0.5601 | - | kimlik_kartı_yönergesi.pdf |
| 4 | 0.0345 | 0.4847 | 0.5086 | - | öğrenci_işleri_birimi.txt |
| 5 | 0.0183 | 0.4766 | 0.5046 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.0093 | 0.4721 | 0.5023 | - | ön_lisans_ve_lisans.pdf |
| 7 | 0.0091 | 0.4720 | 0.5023 | - | öğrenci_işleri_birimi.txt |
| 8 | 0.0019 | 0.4684 | 0.5005 | - | sık_sorulan_sorular.txt |
| 9 | 0.0019 | 0.4684 | 0.5005 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0010 | 0.4679 | 0.5002 | - | sık_sorulan_sorular.txt |

### Diplomami kaybettim, ikinci nusha icin ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9989 | 0.8662 | 0.7308 | - | sık_sorulan_sorular.txt |
| 2 | 0.9765 | 0.8609 | 0.7264 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 3 | 0.1552 | 0.5449 | 0.5387 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 4 | 0.1139 | 0.5243 | 0.5284 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 5 | 0.0370 | 0.4859 | 0.5092 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 6 | 0.0126 | 0.4737 | 0.5031 | - | sık_sorulan_sorular.txt |
| 7 | 0.0025 | 0.4687 | 0.5006 | - | sık_sorulan_sorular.txt |
| 8 | 0.0014 | 0.4681 | 0.5003 | - | sık_sorulan_sorular.txt |
| 9 | 0.0013 | 0.4681 | 0.5003 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 10 | 0.0012 | 0.4681 | 0.5003 | - | sık_sorulan_sorular.txt |

### Diploma eki transkript yerine gecer mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9994 | 0.8663 | 0.7309 | - | sık_sorulan_sorular.txt |
| 2 | 0.4281 | 0.6739 | 0.6054 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 3 | 0.1814 | 0.5579 | 0.5452 | - | sık_sorulan_sorular.txt |
| 4 | 0.0319 | 0.4833 | 0.5080 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 5 | 0.0217 | 0.4783 | 0.5054 | - | sık_sorulan_sorular.txt |
| 6 | 0.0178 | 0.4763 | 0.5045 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 7 | 0.0106 | 0.4727 | 0.5026 | - | sık_sorulan_sorular.txt |
| 8 | 0.0093 | 0.4721 | 0.5023 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 9 | 0.0084 | 0.4717 | 0.5021 | - | uygulama_esaslari_diploma_mezuniyet_belgeler.pdf |
| 10 | 0.0069 | 0.4709 | 0.5017 | - | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |

### Kayit dondurma ile kayit yaptirmamak arasinda ne fark var?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9812 | 0.8620 | 0.7273 | - | sık_sorulan_sorular.txt |
| 2 | 0.2846 | 0.6080 | 0.5707 | - | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 3 | 0.2736 | 0.6027 | 0.5680 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 4 | 0.0778 | 0.5063 | 0.5194 | - | sık_sorulan_sorular.txt |
| 5 | 0.0441 | 0.4895 | 0.5110 | - | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 6 | 0.0409 | 0.4878 | 0.5102 | - | ön_lisans_ve_lisans.pdf |
| 7 | 0.0234 | 0.4791 | 0.5058 | - | öğrenci_konseyi_yönergesi.pdf |
| 8 | 0.0179 | 0.4764 | 0.5045 | - | sık_sorulan_sorular.txt |
| 9 | 0.0138 | 0.4743 | 0.5035 | - | ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf |
| 10 | 0.0011 | 0.4680 | 0.5003 | - | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Hazirlik sinifi okuyan ogrenci transkriptsiz Ek Madde-1 ile yatay gecis basvurusu yapabilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9788 | 0.8614 | 0.7269 | - | sık_sorulan_sorular.txt |
| 2 | 0.7797 | 0.8067 | 0.6856 | - | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 3 | 0.5154 | 0.7110 | 0.6261 | - | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 4 | 0.2595 | 0.5959 | 0.5645 | - | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 5 | 0.2210 | 0.5773 | 0.5550 | - | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 6 | 0.2072 | 0.5705 | 0.5516 | - | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 7 | 0.1771 | 0.5557 | 0.5442 | - | sık_sorulan_sorular.txt |
| 8 | 0.1590 | 0.5468 | 0.5397 | - | sık_sorulan_sorular.txt |
| 9 | 0.0453 | 0.4900 | 0.5113 | - | ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf |
| 10 | 0.0302 | 0.4825 | 0.5075 | - | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Birden fazla universiteye yatay gecis basvurusu yapabilir miyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9965 | 0.8656 | 0.7304 | - | sık_sorulan_sorular.txt |
| 2 | 0.2902 | 0.6107 | 0.5721 | - | sık_sorulan_sorular.txt |
| 3 | 0.1666 | 0.5505 | 0.5415 | - | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 4 | 0.0878 | 0.5113 | 0.5219 | - | sık_sorulan_sorular.txt |
| 5 | 0.0301 | 0.4825 | 0.5075 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.0220 | 0.4784 | 0.5055 | - | ön_lisans_ve_lisans.pdf |
| 7 | 0.0172 | 0.4760 | 0.5043 | - | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 8 | 0.0145 | 0.4747 | 0.5036 | - | sık_sorulan_sorular.txt |
| 9 | 0.0136 | 0.4742 | 0.5034 | - | ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf |
| 10 | 0.0095 | 0.4722 | 0.5024 | - | yonerge_onlisans_lisans_yatay_gecis.pdf |

### Ozel ogrenci olarak ne zaman basvuru yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.7259 | 0.7894 | 0.6739 | - | sık_sorulan_sorular.txt |
| 2 | 0.2290 | 0.5812 | 0.5570 | - | sık_sorulan_sorular.txt |
| 3 | 0.1011 | 0.5180 | 0.5253 | - | sık_sorulan_sorular.txt |
| 4 | 0.0280 | 0.4814 | 0.5070 | - | sık_sorulan_sorular.txt |
| 5 | 0.0051 | 0.4700 | 0.5013 | - | sık_sorulan_sorular.txt |
| 6 | 0.0007 | 0.4678 | 0.5002 | - | sık_sorulan_sorular.txt |
| 7 | 0.0006 | 0.4678 | 0.5002 | - | yaz_okulu_eğitim_öğretim.pdf |
| 8 | 0.0006 | 0.4677 | 0.5002 | - | sık_sorulan_sorular.txt |
| 9 | 0.0005 | 0.4677 | 0.5001 | - | sık_sorulan_sorular.txt |
| 10 | 0.0005 | 0.4677 | 0.5001 | - | öğrenci_toplulukları_yönergesi.pdf |

### Ozel ogrenci olarak basvuru icin hangi belgeler gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.6116 | 0.7489 | 0.6483 | - | sık_sorulan_sorular.txt |
| 2 | 0.3884 | 0.6562 | 0.5959 | - | sık_sorulan_sorular.txt |
| 3 | 0.3730 | 0.6492 | 0.5922 | - | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 4 | 0.3218 | 0.6255 | 0.5798 | - | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 5 | 0.2930 | 0.6120 | 0.5727 | - | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 6 | 0.1165 | 0.5256 | 0.5291 | - | sık_sorulan_sorular.txt |
| 7 | 0.0945 | 0.5147 | 0.5236 | - | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 8 | 0.0787 | 0.5067 | 0.5197 | - | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 9 | 0.0604 | 0.4976 | 0.5151 | - | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 10 | 0.0577 | 0.4962 | 0.5144 | - | sık_sorulan_sorular.txt |

### Daha once aldigim dersler icin muafiyet basvurusunu ne zaman yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9734 | 0.8601 | 0.7258 | - | sık_sorulan_sorular.txt |
| 2 | 0.9205 | 0.8469 | 0.7151 | - | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 3 | 0.8626 | 0.8313 | 0.7032 | - | sık_sorulan_sorular.txt |
| 4 | 0.4199 | 0.6703 | 0.6035 | - | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 5 | 0.3699 | 0.6478 | 0.5914 | - | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 6 | 0.3467 | 0.6372 | 0.5858 | - | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 7 | 0.3404 | 0.6342 | 0.5843 | - | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 8 | 0.1645 | 0.5495 | 0.5410 | - | yonerge_ders_yeterlik_muafiyet_intibak.pdf |
| 9 | 0.1437 | 0.5392 | 0.5359 | - | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 10 | 0.1307 | 0.5327 | 0.5326 | - | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |

### Ikamet izni basvurusu icin hangi belgeler gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9863 | 0.8632 | 0.7284 | - | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 2 | 0.9549 | 0.8556 | 0.7221 | - | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 3 | 0.9504 | 0.8545 | 0.7212 | - | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 4 | 0.8904 | 0.8389 | 0.7090 | - | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 5 | 0.8575 | 0.8299 | 0.7021 | - | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 6 | 0.7832 | 0.8078 | 0.6864 | - | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 7 | 0.6747 | 0.7719 | 0.6626 | - | uluslararası_öğrenci_ikamet_işlemleri.pdf |
| 8 | 0.5737 | 0.7344 | 0.6396 | - | ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf |
| 9 | 0.5660 | 0.7314 | 0.6379 | - | uluslararası_öğrenci.pdf |
| 10 | 0.4871 | 0.6993 | 0.6194 | - | muvafakatname.pdf |

### Denklik belgesi ne zaman gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9117 | 0.8446 | 0.7134 | - | denklik_belgesi.pdf |
| 2 | 0.3593 | 0.6429 | 0.5889 | - | tyb.pdf |
| 3 | 0.2746 | 0.6032 | 0.5682 | - | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 4 | 0.0846 | 0.5097 | 0.5211 | - | uluslararası_öğrenci.pdf |
| 5 | 0.0718 | 0.5033 | 0.5179 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |
| 6 | 0.0609 | 0.4978 | 0.5152 | - | denklik_belgesi.pdf |
| 7 | 0.0586 | 0.4967 | 0.5147 | - | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 8 | 0.0563 | 0.4956 | 0.5141 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 9 | 0.0536 | 0.4942 | 0.5134 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |
| 10 | 0.0256 | 0.4802 | 0.5064 | - | yurda_giriş_çıkış_belgesi.pdf |

### YOS ID numarami nasil ogrenebilirim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0332 | 0.4840 | 0.5083 | - | uluslararası_öğrenci.pdf |
| 2 | 0.0232 | 0.4790 | 0.5058 | - | yös_ıd_no_öğrenme.pdf |
| 3 | 0.0203 | 0.4776 | 0.5051 | - | öğrenci_no_öğrenme.pdf |
| 4 | 0.0016 | 0.4682 | 0.5004 | - | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 5 | 0.0013 | 0.4681 | 0.5003 | - | ön_kayıt_kılavuzu_başvuru_adımları.pdf |
| 6 | 0.0007 | 0.4678 | 0.5002 | - | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 7 | 0.0007 | 0.4678 | 0.5002 | - | yonerge_uluslararasi_ogrenci_yatay_gecis.pdf |
| 8 | 0.0005 | 0.4677 | 0.5001 | - | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 9 | 0.0005 | 0.4677 | 0.5001 | - | uluslararası_öğrenci_kimlik_bilgileri_güncelleme_formu.pdf |
| 10 | 0.0004 | 0.4677 | 0.5001 | - | özel_yetenek_sınavı_yönergesi.pdf |

### Uluslararasi ogrenci kaydinda evrak teslim formu gerekiyor mu?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9859 | 0.8631 | 0.7283 | - | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 2 | 0.9839 | 0.8626 | 0.7279 | - | uluslararası_öğrenci_yönergesi.pdf |
| 3 | 0.9622 | 0.8574 | 0.7236 | - | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 4 | 0.9073 | 0.8434 | 0.7124 | - | uluslararası_öğrenci_evrak_teslim_formu_r1.pdf |
| 5 | 0.8685 | 0.8329 | 0.7044 | - | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 6 | 0.4869 | 0.6992 | 0.6194 | - | uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf |
| 7 | 0.4687 | 0.6915 | 0.6151 | - | uluslararası_öğrenci_alımı_ve_kesin_kayıt_iş_akış_süreci.pdf |
| 8 | 0.1629 | 0.5487 | 0.5406 | - | uluslararası_öğrenci.pdf |
| 9 | 0.1371 | 0.5359 | 0.5342 | - | ön_kayıt_kılavuzu_başvuru_adımları.pdf |
| 10 | 0.1183 | 0.5265 | 0.5295 | - | uluslararası_öğrenci.pdf |

### TOMER ne is yapar?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0427 | 0.4887 | 0.5107 | - | yonerge_uluslararasi_ogrenci_kabul.pdf |
| 2 | 0.0003 | 0.4676 | 0.5001 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 3 | 0.0003 | 0.4676 | 0.5001 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 4 | 0.0002 | 0.4676 | 0.5001 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 5 | 0.0002 | 0.4676 | 0.5001 | - | dil_ve_konuşma_bozuklukları.pdf |
| 6 | 0.0002 | 0.4676 | 0.5001 | - | kök_hücre_araştırma_merkezi_yönergesi.pdf |
| 7 | 0.0001 | 0.4675 | 0.5000 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi_yönetmeliği.txt |
| 8 | 0.0001 | 0.4675 | 0.5000 | - | siber_güvenlik_ve_bilişim_teknolojileri.pdf |
| 9 | 0.0001 | 0.4675 | 0.5000 | - | kariyer_merkezi_yönergesi.pdf |
| 10 | 0.0001 | 0.4675 | 0.5000 | - | güvenlik_hizmetlerinin_yürütülmesine_dair_yönerge.pdf |

### Pedagojik formasyon dersleri transkripte dahil edilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9998 | 0.8664 | 0.7310 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.9952 | 0.8653 | 0.7301 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 3 | 0.9923 | 0.8646 | 0.7295 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 4 | 0.5253 | 0.7151 | 0.6284 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 5 | 0.3269 | 0.6279 | 0.5810 | - | yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf |
| 6 | 0.2886 | 0.6099 | 0.5716 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.2152 | 0.5744 | 0.5536 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 8 | 0.1582 | 0.5463 | 0.5395 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.1072 | 0.5210 | 0.5268 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.1013 | 0.5181 | 0.5253 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |

### Pedagojik formasyon mezuniyet ortalamasina dahil edilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9961 | 0.8655 | 0.7303 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.9925 | 0.8647 | 0.7296 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 3 | 0.9030 | 0.8423 | 0.7116 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 4 | 0.7379 | 0.7934 | 0.6765 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.6136 | 0.7497 | 0.6488 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 6 | 0.5369 | 0.7198 | 0.6311 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.3769 | 0.6510 | 0.5931 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 8 | 0.2852 | 0.6083 | 0.5708 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.2634 | 0.5978 | 0.5655 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.2568 | 0.5946 | 0.5639 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |

### Pedagojik formasyon alirsam mezuniyet 240 AKTS'nin ustune cikabilir mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9983 | 0.8660 | 0.7307 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.8491 | 0.8275 | 0.7004 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 3 | 0.6640 | 0.7681 | 0.6602 | - | çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf |
| 4 | 0.1897 | 0.5619 | 0.5473 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 5 | 0.1859 | 0.5601 | 0.5463 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 6 | 0.1853 | 0.5597 | 0.5462 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.1207 | 0.5277 | 0.5301 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 8 | 0.0963 | 0.5155 | 0.5240 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.0827 | 0.5087 | 0.5207 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.0767 | 0.5058 | 0.5192 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |

### Pedagojik formasyon derslerinin tumunu almak zorunlu mu?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9974 | 0.8658 | 0.7306 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 2 | 0.5364 | 0.7196 | 0.6310 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 3 | 0.3568 | 0.6418 | 0.5883 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 4 | 0.3534 | 0.6402 | 0.5874 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 5 | 0.3392 | 0.6337 | 0.5840 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 6 | 0.3071 | 0.6186 | 0.5762 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.2253 | 0.5794 | 0.5561 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 8 | 0.1165 | 0.5256 | 0.5291 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 9 | 0.0993 | 0.5171 | 0.5248 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 10 | 0.0988 | 0.5168 | 0.5247 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |

### Pedagojik formasyon dersleri en erken hangi yariyilda alinabilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9602 | 0.8569 | 0.7232 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 2 | 0.8834 | 0.8370 | 0.7075 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 3 | 0.7382 | 0.7935 | 0.6766 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 4 | 0.6741 | 0.7717 | 0.6624 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 5 | 0.6429 | 0.7605 | 0.6554 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 6 | 0.6289 | 0.7554 | 0.6522 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 7 | 0.5808 | 0.7372 | 0.6413 | - | pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt |
| 8 | 0.5130 | 0.7100 | 0.6255 | - | lisans_pedagojik_formasyon_derslerine_ilişkin.pdf |
| 9 | 0.4067 | 0.6644 | 0.6003 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |
| 10 | 0.3907 | 0.6573 | 0.5965 | - | uygulama_esaslari_lisans_pedagojik_formasyon.pdf |

### Yemek bursu basvurulari nereden yapilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9899 | 0.8640 | 0.7291 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 2 | 0.9017 | 0.8420 | 0.7113 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.6746 | 0.7718 | 0.6625 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.3792 | 0.6520 | 0.5937 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.2083 | 0.5711 | 0.5519 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.2064 | 0.5701 | 0.5514 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.1249 | 0.5298 | 0.5312 | - | kimlik_kartı_yönergesi.pdf |
| 8 | 0.0935 | 0.5141 | 0.5233 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0807 | 0.5077 | 0.5202 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0627 | 0.4988 | 0.5157 | - | öğrenci_yemek_bursu_yönergesi.pdf |

### Bursum hangi sartlarda kesilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0677 | 0.5012 | 0.5169 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 2 | 0.0546 | 0.4947 | 0.5136 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.0020 | 0.4685 | 0.5005 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.0011 | 0.4680 | 0.5003 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 5 | 0.0009 | 0.4679 | 0.5002 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.0009 | 0.4679 | 0.5002 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 7 | 0.0008 | 0.4679 | 0.5002 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0008 | 0.4679 | 0.5002 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 9 | 0.0008 | 0.4679 | 0.5002 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0004 | 0.4677 | 0.5001 | - | öğrenci_yemek_bursu_yönergesi.pdf |

### Kayit ekraninda borclu ya da fazla ucretli gorunuyorsam ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0000 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 2 | 0.0000 | 0.4675 | 0.5000 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 3 | 0.0000 | 0.4675 | 0.5000 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 4 | 0.0000 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 5 | 0.0000 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 6 | 0.0000 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 7 | 0.0000 | 0.4675 | 0.5000 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0000 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 9 | 0.0000 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 10 | 0.0000 | 0.4675 | 0.5000 | - | öğrenci_yemek_bursu_yönergesi.pdf |

### Program suresini asarsam katki payi oder miyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0532 | 0.4940 | 0.5133 | - | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |
| 2 | 0.0014 | 0.4681 | 0.5003 | - | 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf |
| 3 | 0.0001 | 0.4675 | 0.5000 | - | 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf |
| 4 | 0.0001 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 5 | 0.0001 | 0.4675 | 0.5000 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 6 | 0.0001 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 7 | 0.0001 | 0.4675 | 0.5000 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0001 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 9 | 0.0000 | 0.4675 | 0.5000 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 10 | 0.0000 | 0.4675 | 0.5000 | - | öğrenci_yemek_bursu_yönergesi.pdf |

### Harc iadesi icin IBAN ve dekontla nereye basvurmam gerekir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0000 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 2 | 0.0000 | 0.4675 | 0.5000 | - | idari_ve_mali_işler_birimi.txt |
| 3 | 0.0000 | 0.4675 | 0.5000 | - | 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf |
| 4 | 0.0000 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 5 | 0.0000 | 0.4675 | 0.5000 | - | idari_ve_mali_işler_birimi.txt |
| 6 | 0.0000 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |
| 7 | 0.0000 | 0.4675 | 0.5000 | - | öğrenci_yemek_bursu_yönergesi.pdf |
| 8 | 0.0000 | 0.4675 | 0.5000 | - | 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf |
| 9 | 0.0000 | 0.4675 | 0.5000 | - | idari_ve_mali_işler_birimi.txt |
| 10 | 0.0000 | 0.4675 | 0.5000 | - | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf |

### Sinava giremedigim ders icin mazeret sinavi basvurusu nasil yapilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.4510 | 0.6839 | 0.6109 | - | ön_lisans_ve_lisans.pdf |
| 2 | 0.3988 | 0.6609 | 0.5984 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.2598 | 0.5961 | 0.5646 | - | ön_lisans_ve_lisans.pdf |
| 4 | 0.2203 | 0.5769 | 0.5548 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 5 | 0.0896 | 0.5122 | 0.5224 | - | ön_lisans_ve_lisans.pdf |
| 6 | 0.0534 | 0.4941 | 0.5133 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.0434 | 0.4891 | 0.5108 | - | sık_sorulan_sorular.txt |
| 8 | 0.0337 | 0.4842 | 0.5084 | - | ön_lisans_ve_lisans.pdf |
| 9 | 0.0205 | 0.4776 | 0.5051 | - | ön_lisans_ve_lisans.pdf |
| 10 | 0.0077 | 0.4713 | 0.5019 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |

### Bir dersten kac kez sinav hakkina sahibim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.3464 | 0.6370 | 0.5858 | - | uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf |
| 2 | 0.0583 | 0.4965 | 0.5146 | - | mühendislik_fakültesi_ortak_sınav_yönergesi.pdf |
| 3 | 0.0556 | 0.4952 | 0.5139 | - | uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf |
| 4 | 0.0129 | 0.4739 | 0.5032 | - | türkçe_öğretimi_uygulama_ve_araştırma_merkezi.pdf |
| 5 | 0.0113 | 0.4731 | 0.5028 | - | bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf |
| 6 | 0.0109 | 0.4729 | 0.5027 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 7 | 0.0090 | 0.4719 | 0.5022 | - | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 8 | 0.0081 | 0.4715 | 0.5020 | - | yabancı_dil_eğitim_öğretimi_yönergesi.pdf |
| 9 | 0.0053 | 0.4701 | 0.5013 | - | bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf |
| 10 | 0.0041 | 0.4695 | 0.5010 | - | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |

### Bagil degerlendirme sistemi nasil isler?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.2441 | 0.5885 | 0.5607 | - | bağıl_değerlendirme_yönergesi.pdf |
| 2 | 0.0852 | 0.5100 | 0.5213 | - | bağıl_değerlendirme_yönergesi.pdf |
| 3 | 0.0844 | 0.5096 | 0.5211 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 4 | 0.0830 | 0.5089 | 0.5207 | - | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 5 | 0.0314 | 0.4831 | 0.5078 | - | bağıl_değerlendirme_yönergesi.pdf |
| 6 | 0.0301 | 0.4825 | 0.5075 | - | bağıl_değerlendirme_yönergesi.pdf |
| 7 | 0.0234 | 0.4791 | 0.5059 | - | bağıl_değerlendirme_yönergesi.pdf |
| 8 | 0.0153 | 0.4751 | 0.5038 | - | sık_sorulan_sorular.txt |
| 9 | 0.0090 | 0.4719 | 0.5022 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0070 | 0.4709 | 0.5018 | - | yonerge_bagil_degerlendirme.pdf |

### Final sinavina girme sarti olarak devam yuzdesi kac olmalidir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0557 | 0.4952 | 0.5139 | - | yonerge_yabanci_dil_egitim_ogretim.pdf |
| 2 | 0.0296 | 0.4822 | 0.5074 | - | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |
| 3 | 0.0188 | 0.4768 | 0.5047 | - | yabancı_dil_eğitim_öğretimi_yönergesi.pdf |
| 4 | 0.0169 | 0.4759 | 0.5042 | - | lisansüstü_eğitim_ve.pdf |
| 5 | 0.0169 | 0.4759 | 0.5042 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 6 | 0.0148 | 0.4748 | 0.5037 | - | yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf |
| 7 | 0.0141 | 0.4745 | 0.5035 | - | diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf |
| 8 | 0.0090 | 0.4719 | 0.5022 | - | yonerge_yabanci_dil_egitim_ogretim.pdf |
| 9 | 0.0062 | 0.4706 | 0.5016 | - | sürekli_eğitim_merkezi_yönergesi.pdf |
| 10 | 0.0054 | 0.4701 | 0.5013 | - | tıp_fakültesi_tıp_doktorluğu_programı.pdf |

### Not itirazi icin ne kadar sureye sahibim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.5362 | 0.7195 | 0.6309 | - | sık_sorulan_sorular.txt |
| 2 | 0.1687 | 0.5516 | 0.5421 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.1278 | 0.5313 | 0.5319 | - | yonerge_yuzde_on_basari_degerlendirme.pdf |
| 4 | 0.0838 | 0.5093 | 0.5209 | - | ön_lisans_ve_lisans.pdf |
| 5 | 0.0423 | 0.4886 | 0.5106 | - | yonetmelik_onlisans_lisans_egitim_ogretim.pdf |
| 6 | 0.0310 | 0.4829 | 0.5078 | - | ders_yeterlilik_sınavı_uygulama_yönergesi.pdf |
| 7 | 0.0236 | 0.4792 | 0.5059 | - | sık_sorulan_sorular.txt |
| 8 | 0.0057 | 0.4703 | 0.5014 | - | ön_lisans_ve_lisans.pdf |
| 9 | 0.0027 | 0.4688 | 0.5007 | - | öğrenci_konukevi_uygulama_yönergesi.pdf |
| 10 | 0.0012 | 0.4680 | 0.5003 | - | işyeri_staj_sözleşmesi.pdf |

### Yaz okulunda en fazla kac ders alabilirim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9953 | 0.8653 | 0.7301 | - | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 2 | 0.9938 | 0.8650 | 0.7298 | - | yaz_okulu_eğitim_öğretim.pdf |
| 3 | 0.9521 | 0.8549 | 0.7215 | - | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 4 | 0.9511 | 0.8547 | 0.7213 | - | yonerge_yaz_okulu_egitim_ogretim.pdf |
| 5 | 0.9490 | 0.8542 | 0.7209 | - | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.8839 | 0.8372 | 0.7076 | - | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.7227 | 0.7884 | 0.6732 | - | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 8 | 0.4096 | 0.6657 | 0.6010 | - | yaz_okulu_eğitim_öğretim.pdf |
| 9 | 0.4096 | 0.6657 | 0.6010 | - | yaz_okulu_eğitim_öğretim_yönergesi.pdf |
| 10 | 0.1848 | 0.5595 | 0.5461 | - | yaz_okulu_eğitim_öğretim.pdf |

### Basarisiz oldugum dersi tekrar almak icin ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.5451 | 0.7231 | 0.6330 | - | sık_sorulan_sorular.txt |
| 2 | 0.5408 | 0.7214 | 0.6320 | - | ön_lisans_ve_lisans.pdf |
| 3 | 0.5075 | 0.7078 | 0.6242 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 4 | 0.3967 | 0.6599 | 0.5979 | - | sık_sorulan_sorular.txt |
| 5 | 0.3186 | 0.6241 | 0.5790 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 6 | 0.3084 | 0.6193 | 0.5765 | - | sık_sorulan_sorular.txt |
| 7 | 0.1852 | 0.5597 | 0.5462 | - | sık_sorulan_sorular.txt |
| 8 | 0.1806 | 0.5575 | 0.5450 | - | sık_sorulan_sorular.txt |
| 9 | 0.1673 | 0.5509 | 0.5417 | - | sık_sorulan_sorular.txt |
| 10 | 0.1402 | 0.5374 | 0.5350 | - | endüstri_mühendisliği_tasarımı_yaptırma_ve_değerlendirme_ı̇lkeleri_güncel.pdf |

### Azami ogrenim suresi dolunca ne olur?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.1598 | 0.5472 | 0.5399 | - | lisansüstü_eğitim_ve.pdf |
| 2 | 0.1065 | 0.5206 | 0.5266 | - | lisansüstü_eğitim_ve.pdf |
| 3 | 0.0420 | 0.4884 | 0.5105 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 4 | 0.0144 | 0.4746 | 0.5036 | - | lisansüstü_eğitim_ve.pdf |
| 5 | 0.0114 | 0.4731 | 0.5029 | - | çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf |
| 6 | 0.0061 | 0.4705 | 0.5015 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 7 | 0.0039 | 0.4694 | 0.5010 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 8 | 0.0034 | 0.4692 | 0.5009 | - | lisansüstü_eğitim_ve.pdf |
| 9 | 0.0031 | 0.4690 | 0.5008 | - | mezunlar_için_pedagojik_formasyon_eğitimi.pdf |
| 10 | 0.0028 | 0.4688 | 0.5007 | - | lisansüstü_eğitim_ve.pdf |

### Donem dondurma icin saglik raporu yeterli mi?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0401 | 0.4875 | 0.5100 | - | ön_lisans_ve_lisans.pdf |
| 2 | 0.0036 | 0.4692 | 0.5009 | - | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |
| 3 | 0.0012 | 0.4681 | 0.5003 | - | 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf |
| 4 | 0.0012 | 0.4681 | 0.5003 | - | sık_sorulan_sorular.txt |
| 5 | 0.0011 | 0.4680 | 0.5003 | - | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 6 | 0.0011 | 0.4680 | 0.5003 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.0010 | 0.4680 | 0.5003 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 8 | 0.0006 | 0.4677 | 0.5001 | - | ön_lisans_ve_lisans.pdf |
| 9 | 0.0006 | 0.4677 | 0.5001 | - | 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf |
| 10 | 0.0005 | 0.4677 | 0.5001 | - | 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf |

### Mezuniyet icin GNO en az kac olmalidir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.4591 | 0.6873 | 0.6128 | - | ön_lisans_ve_lisans.pdf |
| 2 | 0.3437 | 0.6358 | 0.5851 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 3 | 0.2104 | 0.5721 | 0.5524 | - | sık_sorulan_sorular.txt |
| 4 | 0.1065 | 0.5206 | 0.5266 | - | ön_lisans_ve_lisans.pdf |
| 5 | 0.0204 | 0.4776 | 0.5051 | - | sık_sorulan_sorular.txt |
| 6 | 0.0132 | 0.4740 | 0.5033 | - | yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf |
| 7 | 0.0123 | 0.4736 | 0.5031 | - | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 8 | 0.0121 | 0.4735 | 0.5030 | - | ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf |
| 9 | 0.0055 | 0.4702 | 0.5014 | - | ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf |
| 10 | 0.0035 | 0.4692 | 0.5009 | - | ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf |

### Zorunlu staj icin SGK baslangic islemleri nasil yapilir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.3159 | 0.6228 | 0.5783 | - | staj_iş_akışı.pdf |
| 2 | 0.2063 | 0.5701 | 0.5514 | - | zorunlu_stajda_izlenecek_yol.pdf |
| 3 | 0.0962 | 0.5155 | 0.5240 | - | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 4 | 0.0515 | 0.4931 | 0.5129 | - | document.pdf |
| 5 | 0.0339 | 0.4844 | 0.5085 | - | document.pdf |
| 6 | 0.0266 | 0.4807 | 0.5067 | - | staj_bilgilendirme_toplantısı_sunumu_2024_2025.pdf |
| 7 | 0.0264 | 0.4806 | 0.5066 | - | yonerge_onlisans_lisans_staj.pdf |
| 8 | 0.0207 | 0.4778 | 0.5052 | - | staj_esaslar.pdf |
| 9 | 0.0170 | 0.4759 | 0.5042 | - | staj_iş_akışı.pdf |
| 10 | 0.0158 | 0.4753 | 0.5039 | - | staj_ilkeleri_23122019_inş_müh.pdf |

### Staj defterini teslim etme suresi ne kadardir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.9030 | 0.8423 | 0.7116 | - | çevre_mühendisliği_bölümü_staj_ilkeleri.docx |
| 2 | 0.8952 | 0.8402 | 0.7100 | - | çevre_mühendisliği_bölümü_staj_ilkeleri.docx |
| 3 | 0.6689 | 0.7698 | 0.6612 | - | zorunlu_stajda_izlenecek_yol.pdf |
| 4 | 0.3778 | 0.6514 | 0.5934 | - | zorunlu_stajda_izlenecek_yol.pdf |
| 5 | 0.1640 | 0.5492 | 0.5409 | - | zorunlu_gönüllü_staj_başvuru_formu.pdf |
| 6 | 0.0771 | 0.5060 | 0.5193 | - | yonerge_onlisans_lisans_staj.pdf |
| 7 | 0.0438 | 0.4893 | 0.5110 | - | staj_sıkça_sorulanlar.pdf |
| 8 | 0.0383 | 0.4866 | 0.5096 | - | staj_sıkça_sorulanlar.pdf |
| 9 | 0.0178 | 0.4763 | 0.5044 | - | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |
| 10 | 0.0115 | 0.4732 | 0.5029 | - | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |

### Bitirme projesi danismani nasil belirlenir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.5027 | 0.7058 | 0.6231 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 2 | 0.4438 | 0.6807 | 0.6092 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 3 | 0.3344 | 0.6314 | 0.5828 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 4 | 0.0706 | 0.5027 | 0.5176 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 5 | 0.0524 | 0.4936 | 0.5131 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 6 | 0.0473 | 0.4911 | 0.5118 | - | bitirme_projesi_hazırlama_sunma_ve_değerlendirme_ilkeleri_taslak.docx |
| 7 | 0.0369 | 0.4859 | 0.5092 | - | mat_bitirme_çalışması_ilkeleri.pdf |
| 8 | 0.0263 | 0.4806 | 0.5066 | - | mat_bitirme_çalışması_ilkeleri.pdf |
| 9 | 0.0242 | 0.4795 | 0.5061 | - | bitirme_projesi_sunum_değerlendirme_formu.docx |
| 10 | 0.0239 | 0.4794 | 0.5060 | - | bitirme_projesi_şablon.docx |

### Staj yerim degisirse ne yapmaliyim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.4596 | 0.6876 | 0.6129 | - | zorunlu_gönüllü_staj_başvuru_formu.pdf |
| 2 | 0.0988 | 0.5168 | 0.5247 | - | staj_esaslar.pdf |
| 3 | 0.0860 | 0.5104 | 0.5215 | - | staj_ilkeleri_23122019_inş_müh.pdf |
| 4 | 0.0806 | 0.5077 | 0.5201 | - | mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf |
| 5 | 0.0702 | 0.5025 | 0.5175 | - | staj_yönergesi.pdf |
| 6 | 0.0695 | 0.5021 | 0.5174 | - | 1_elektrik_elektronik_staj_ilkeleri_ve_uygulama_esasları.pdf |
| 7 | 0.0519 | 0.4934 | 0.5130 | - | işyeri_staj_sözleşmesi.pdf |
| 8 | 0.0349 | 0.4848 | 0.5087 | - | endüstri_mühendisliği_bölümü_staj_ilkeleri_06_01_2022.pdf |
| 9 | 0.0175 | 0.4762 | 0.5044 | - | yonerge_onlisans_lisans_staj.pdf |
| 10 | 0.0121 | 0.4735 | 0.5030 | - | 1_elektrik_elektronik_staj_ilkeleri_ve_uygulama_esasları.pdf |

### Lisansustu ogrenciler icin tez teslim suresi ne kadardir?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.6335 | 0.7571 | 0.6533 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 2 | 0.3359 | 0.6321 | 0.5832 | - | yonetmelik_lisansustu_egitim_ogretim.pdf |
| 3 | 0.1508 | 0.5427 | 0.5376 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 4 | 0.1207 | 0.5277 | 0.5301 | - | lisansüstü_eğitim_ve.pdf |
| 5 | 0.0823 | 0.5086 | 0.5206 | - | lisansüstü_eğitim_ve.pdf |
| 6 | 0.0531 | 0.4939 | 0.5133 | - | yonerge_lisansustu_danismanlik_ders_verme.pdf |
| 7 | 0.0383 | 0.4865 | 0.5096 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 8 | 0.0279 | 0.4813 | 0.5070 | - | lisansüstü_eğitim_ve.pdf |
| 9 | 0.0275 | 0.4812 | 0.5069 | - | lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf |
| 10 | 0.0268 | 0.4808 | 0.5067 | - | lisansüstü_eğitim_ve.pdf |

---

*Bu rapor `scripts/analyze_reranker_scores.py` tarafindan otomatik uretilmistir.*