# Reranker Skor Dagilim Analizi

**Tarih:** 2026-05-17 18:17
**Model:** BAAI/bge-reranker-v2-m3
**Device:** cuda
**Torch dtype:** float16->torch.float16
**Kalibrasyon:** shift=0.0652, scale=0.5
**Toplam Soru:** 1
**Toplam Skor Ornegi:** 10
**Toplam sure:** 789.3s
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
| min | 0.0002 |
| p10 | 0.0002 |
| p25 | 0.0003 |
| median | 0.0006 |
| mean | 0.0005 |
| p75 | 0.0008 |
| p90 | 0.0008 |
| max | 0.001 |
| std | 0.0003 |

### Kalibre Edilmis Skorlar (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 10 |
| min | 0.4675 |
| p10 | 0.4675 |
| p25 | 0.4676 |
| median | 0.4677 |
| mean | 0.4677 |
| p75 | 0.4678 |
| p90 | 0.4679 |
| max | 0.4679 |
| std | 0.0001 |

### Duz Sigmoid Skorlar (Referans)

| Metrik | Deger |
|--------|-------|
| count | 10 |
| min | 0.5 |
| p10 | 0.5 |
| p25 | 0.5001 |
| median | 0.5001 |
| mean | 0.5001 |
| p75 | 0.5002 |
| p90 | 0.5002 |
| max | 0.5002 |
| std | 0.0001 |

---

## Top-1 Skorlar (Her Sorunun En Iyi Adayi)

### Ham Top-1 Skorlari (Logit)

| Metrik | Deger |
|--------|-------|
| count | 1 |
| min | 0.001 |
| p10 | 0.001 |
| p25 | 0.001 |
| median | 0.001 |
| mean | 0.001 |
| p75 | 0.001 |
| p90 | 0.001 |
| max | 0.001 |
| std | 0.0 |

### Kalibre Top-1 Skorlari (Runtime)

| Metrik | Deger |
|--------|-------|
| count | 1 |
| min | 0.4679 |
| p10 | 0.4679 |
| p25 | 0.4679 |
| median | 0.4679 |
| mean | 0.4679 |
| p75 | 0.4679 |
| p90 | 0.4679 |
| max | 0.4679 |
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

- **Formul:** `sigmoid((score - 0.0006) / 0.5000)`
- **Shift (median):** 0.0006
- **Scale (IQR):** 0.5
- **Onerilen direct-RAG esigi:** 0.5
- **Onerilen min-source esigi:** 0.5

---

## Soru Bazli Detaylar

### CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?

| # | Ham Skor | Kalibre | Sigmoid | Source Owner | Kaynak |
|:-:|:--------:|:-------:|:-------:|--------------|--------|
| 1 | 0.0010 | 0.4679 | 0.5002 | tuition_fee_catalog | sık_sorulan_sorular.txt |
| 2 | 0.0008 | 0.4679 | 0.5002 | student_affairs_policy | çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf |
| 3 | 0.0008 | 0.4678 | 0.5002 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 4 | 0.0007 | 0.4678 | 0.5002 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 5 | 0.0006 | 0.4678 | 0.5002 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 6 | 0.0005 | 0.4677 | 0.5001 | student_affairs_policy | yonerge_onlisans_lisans_yatay_gecis.pdf |
| 7 | 0.0003 | 0.4676 | 0.5001 | tuition_fee_catalog | sık_sorulan_sorular.txt |
| 8 | 0.0003 | 0.4676 | 0.5001 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 9 | 0.0002 | 0.4675 | 0.5000 | student_affairs_policy | yonerge_cift_anadal_yandal.pdf |
| 10 | 0.0002 | 0.4675 | 0.5000 | student_affairs_policy | yonerge_onlisans_lisans_yatay_gecis.pdf |

---

*Bu rapor `scripts/analyze_reranker_scores.py` tarafindan otomatik uretilmistir.*