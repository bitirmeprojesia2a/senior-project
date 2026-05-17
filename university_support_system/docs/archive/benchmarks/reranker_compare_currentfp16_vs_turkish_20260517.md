# Reranker Report Compare

Generated: 2026-05-17 16:38
Baseline: `reranker_shadow_current_fp16_all_20260517`

## Summary

| Report | Model | Device | Dtype | Elapsed | Owner match | Raw median | Top-1 median | Runtime calib | Suggested calib |
|---|---|---:|---|---:|---:|---:|---:|---|---|
| `reranker_shadow_current_fp16_all_20260517` | BAAI/bge-reranker-v2-m3 | cuda | torch.float16 | 101.0s | 33/40 | 0.0595 | 0.6799 | 0.0652/0.5 | 0.0595/0.5 |
| `reranker_shadow_turkish_all_final_20260517` | seroe/bge-reranker-v2-m3-turkish-triplet | cuda | torch.float16 | 55.5s | 33/40 | 0.0386 | 0.6621 | 0.0405/0.5 | 0.0386/0.5 |
| `reranker_shadow_current_all_20260517` | BAAI/bge-reranker-v2-m3 | cuda | None | 702.0s | 33/40 | 0.0595 | 0.6797 | 0.0652/0.5 | 0.0595/0.5 |

## Top-1 Changes vs Baseline

### `reranker_shadow_turkish_all_final_20260517`

- Common queries: 40
- Same top-1 source: 39/40 (97.5%)
- Same top-1 owner: 40/40 (100.0%)
- Missing queries: 0
- Added queries: 0

| Query | Baseline source | Candidate source | Baseline owner | Candidate owner | Scores |
|---|---|---|---|---|---|
| Basarisiz oldugum dersi tekrar almak icin ne yapmaliyim? | sık_sorulan_sorular.txt | ön_lisans_ve_lisans.pdf | student_affairs_policy | student_affairs_policy | 0.5454 -> 0.2908 |

### `reranker_shadow_current_all_20260517`

- Common queries: 40
- Same top-1 source: 40/40 (100.0%)
- Same top-1 owner: 39/40 (97.5%)
- Missing queries: 0
- Added queries: 0

| Query | Baseline source | Candidate source | Baseline owner | Candidate owner | Scores |
|---|---|---|---|---|---|
| Harc iadesi icin IBAN ve dekontla nereye basvurmam gerekir? | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf | kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf | student_affairs_policy | tuition_fee_catalog | 0.0000 -> 0.0000 |

## Owner Distribution

- `reranker_shadow_current_fp16_all_20260517`: -=7, curriculum_catalog=1, international_policy=6, student_affairs_policy=25, tuition_fee_catalog=1
- `reranker_shadow_turkish_all_final_20260517`: -=7, curriculum_catalog=1, international_policy=6, student_affairs_policy=25, tuition_fee_catalog=1
- `reranker_shadow_current_all_20260517`: -=7, curriculum_catalog=1, international_policy=6, student_affairs_policy=24, tuition_fee_catalog=2

Note: This report compares reranker candidate ordering only; final answer replay is still required before production switching.