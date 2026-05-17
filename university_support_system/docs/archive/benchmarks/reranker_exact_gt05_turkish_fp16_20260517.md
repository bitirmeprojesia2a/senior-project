# Reranker Skor Dagilim Analizi

**Tarih:** 2026-05-17 18:17
**Model:** seroe/bge-reranker-v2-m3-turkish-triplet
**Device:** cuda
**Torch dtype:** float16->torch.float16
**Kalibrasyon:** shift=0.0405, scale=0.5
**Toplam Soru:** 1
**Toplam Skor Ornegi:** 10
**Toplam sure:** 796.9s
**Kapsam:** Candidate pool + reranker analizi; final threshold/filtering adimlari buna dahil degildir.

---

## Top-1 Source Owner Ozeti

- Expected department match: 0/0
- Top-1 source owner dagilimi: tuition_fee_catalog=1

---

## Tum Skorlar (Tum Adaylar)

### Ham Reranker Skorlari (Logit)

| Metrik | Deger |
|--------|-------|
| count | 10 |
| min | 0.0001 |
| p10 | 0.0001 |
| p25 | 0.0002 |
| median | 0.0003 |
| mean | 0.0003 |
| p75 | 0.0004 |
| p90 | 0.0004 |
| max | 0.0006 |
| std | 0.0002 |

### Kalibre Edilmis Skorlar (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 10 |
| min | 0.4798 |
| p10 | 0.4798 |
| p25 | 0.4798 |
| median | 0.4799 |
| mean | 0.4799 |
| p75 | 0.48 |
| p90 | 0.48 |
| max | 0.4801 |
| std | 0.0001 |

### Duz Sigmoid Skorlar (Referans)

| Metrik | Deger |
|--------|-------|
| count | 10 |
| min | 0.5 |
| p10 | 0.5 |
| p25 | 0.5 |
| median | 0.5001 |
| mean | 0.5001 |
| p75 | 0.5001 |
| p90 | 0.5001 |
| max | 0.5002 |
| std | 0.0 |

---

## Top-1 Skorlar (Her Sorunun En Iyi Adayi)

### Ham Top-1 Skorlari (Logit)

| Metrik | Deger |
|--------|-------|
| count | 1 |
| min | 0.0006 |
| p10 | 0.0006 |
| p25 | 0.0006 |
| median | 0.0006 |
| mean | 0.0006 |
| p75 | 0.0006 |
| p90 | 0.0006 |
| max | 0.0006 |
| std | 0.0 |

### Kalibre Top-1 Skorlari (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 1 |
| min | 0.4801 |
| p10 | 0.4801 |
| p25 | 0.4801 |
| median | 0.4801 |
| mean | 0.4801 |
| p75 | 0.4801 |
| p90 | 0.4801 |
| max | 0.4801 |
| std | 0.0 |

### Duz Sigmoid Top-1 Skorlari (Referans)

| Metrik | Deger |
|--------|-------|
| count | 1 |
| min | 0.5002 |
| p10 | 0.5002 |
| p25 | 0.5002 |
| median | 0.5002 |
| mean | 0.5002 |
| p75 | 0.5002 |
| p90 | 0.5002 |
| max | 0.5002 |
| std | 0.0 |

---

## Sigmoid Kalibrasyon Onerisi

- **Formul:** `sigmoid((score - 0.0003) / 0.5000)`
- **Shift (median):** 0.0003
- **Scale (IQR):** 0.5
- **Onerilen direct-RAG esigi:** 0.5
- **Onerilen min-source esigi:** 0.5

---

## Soru Bazli Detaylar

### CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0006 | 0.4801 | 0.5002 | tuition_fee_catalog | sık_sorulan_sorular.txt |
| 2 | 0.0004 | 0.4800 | 0.5001 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 3 | 0.0004 | 0.4800 | 0.5001 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 4 | 0.0004 | 0.4800 | 0.5001 | student_affairs_policy | çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf |
| 5 | 0.0003 | 0.4799 | 0.5001 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 6 | 0.0002 | 0.4799 | 0.5001 | tuition_fee_catalog | sık_sorulan_sorular.txt |
| 7 | 0.0002 | 0.4799 | 0.5001 | student_affairs_policy | yonerge_onlisans_lisans_yatay_gecis.pdf |
| 8 | 0.0002 | 0.4798 | 0.5000 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 9 | 0.0001 | 0.4798 | 0.5000 | student_affairs_policy | yonerge_onlisans_lisans_yatay_gecis.pdf |
| 10 | 0.0001 | 0.4798 | 0.5000 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |

---

*Bu rapor `scripts/analyze_reranker_scores.py` tarafindan otomatik uretilmistir.*