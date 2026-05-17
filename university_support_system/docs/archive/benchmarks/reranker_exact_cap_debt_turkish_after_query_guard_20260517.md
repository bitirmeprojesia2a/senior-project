# Reranker Skor Dagilim Analizi

**Tarih:** 2026-05-17 18:32
**Model:** seroe/bge-reranker-v2-m3-turkish-triplet
**Device:** cuda
**Torch dtype:** float16->torch.float16
**Kalibrasyon:** shift=0.0405, scale=0.5
**Toplam Soru:** 1
**Toplam Skor Ornegi:** 10
**Toplam sure:** 30.0s
**Kapsam:** Candidate pool + reranker analizi; final threshold/filtering adimlari buna dahil degildir.

---

## Top-1 Source Owner Ozeti

- Expected department match: 0/0
- Top-1 source owner dagilimi: student_affairs_policy=1

---

## Tum Skorlar (Tum Adaylar)

### Ham Reranker Skorlari (Logit)

| Metrik | Deger |
|--------|-------|
| count | 10 |
| min | 0.0002 |
| p10 | 0.0003 |
| p25 | 0.0004 |
| median | 0.0006 |
| mean | 0.001 |
| p75 | 0.0017 |
| p90 | 0.0021 |
| max | 0.0024 |
| std | 0.0008 |

### Kalibre Edilmis Skorlar (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 10 |
| min | 0.4799 |
| p10 | 0.4799 |
| p25 | 0.48 |
| median | 0.4801 |
| mean | 0.4803 |
| p75 | 0.4806 |
| p90 | 0.4808 |
| max | 0.481 |
| std | 0.0004 |

### Duz Sigmoid Skorlar (Referans)

| Metrik | Deger |
|--------|-------|
| count | 10 |
| min | 0.5 |
| p10 | 0.5001 |
| p25 | 0.5001 |
| median | 0.5002 |
| mean | 0.5002 |
| p75 | 0.5004 |
| p90 | 0.5005 |
| max | 0.5006 |
| std | 0.0002 |

---

## Top-1 Skorlar (Her Sorunun En Iyi Adayi)

### Ham Top-1 Skorlari (Logit)

| Metrik | Deger |
|--------|-------|
| count | 1 |
| min | 0.0024 |
| p10 | 0.0024 |
| p25 | 0.0024 |
| median | 0.0024 |
| mean | 0.0024 |
| p75 | 0.0024 |
| p90 | 0.0024 |
| max | 0.0024 |
| std | 0.0 |

### Kalibre Top-1 Skorlari (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 1 |
| min | 0.481 |
| p10 | 0.481 |
| p25 | 0.481 |
| median | 0.481 |
| mean | 0.481 |
| p75 | 0.481 |
| p90 | 0.481 |
| max | 0.481 |
| std | 0.0 |

### Duz Sigmoid Top-1 Skorlari (Referans)

| Metrik | Deger |
|--------|-------|
| count | 1 |
| min | 0.5006 |
| p10 | 0.5006 |
| p25 | 0.5006 |
| median | 0.5006 |
| mean | 0.5006 |
| p75 | 0.5006 |
| p90 | 0.5006 |
| max | 0.5006 |
| std | 0.0 |

---

## Sigmoid Kalibrasyon Onerisi

- **Formul:** `sigmoid((score - 0.0006) / 0.5000)`
- **Shift (median):** 0.0006
- **Scale (IQR):** 0.5
- **Onerilen direct-RAG esigi:** 0.501
- **Onerilen min-source esigi:** 0.5

---

## Soru Bazli Detaylar

### Harc borcum olsaydi CAP'a basvurabilir miydim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0024 | 0.4810 | 0.5006 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 2 | 0.0021 | 0.4808 | 0.5005 | tuition_fee_catalog | sık_sorulan_sorular.txt |
| 3 | 0.0020 | 0.4807 | 0.5005 | student_affairs_policy | ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf |
| 4 | 0.0008 | 0.4802 | 0.5002 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 5 | 0.0007 | 0.4801 | 0.5002 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 6 | 0.0006 | 0.4801 | 0.5002 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 7 | 0.0004 | 0.4800 | 0.5001 | student_affairs_policy | çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf |
| 8 | 0.0004 | 0.4799 | 0.5001 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 9 | 0.0003 | 0.4799 | 0.5001 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 10 | 0.0002 | 0.4799 | 0.5000 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |

---

*Bu rapor `scripts/analyze_reranker_scores.py` tarafindan otomatik uretilmistir.*