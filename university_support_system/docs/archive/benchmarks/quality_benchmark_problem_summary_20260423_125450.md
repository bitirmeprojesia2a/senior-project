# Quality Benchmark Problem Summary

- Source: `tests\quality_benchmark_20260423_125450.json`
- Generated: 2026-04-23 17:19:44
- Total questions: 4

## Metrics

- `dept_accuracy`: 100.0
- `mode_accuracy`: 75.0
- `key_fact_coverage`: 53.3
- `clean_quality_pct`: 75.0
- `avg_time_ms`: 30088.0
- `median_time_ms`: 21744.1
- `intent_analysis_active`: 0
- `force_llm_synthesis_count`: 0

## Problem Classes

### low_fact_coverage (3)

- Recommendation: Retrieval/ranking ve LLM sentez promptlarini kaynakta bulunan gerekli resmi kosullari kesmeyecek sekilde iyilestir.
- Questions: Q1, Q3, Q4

### a2a_transport_fallback (1)

- Recommendation: A2A diagnostics, specialist timeout, model/RAG cold-start ve concurrency sinirlarini incele.
- Questions: Q4

### clean_pass (1)

- Recommendation: Genel kalite analizinde ele al.
- Questions: Q2

### generation_mode_mismatch (1)

- Recommendation: VT/RAG/LLM karar politikasini ve force-LLM kosullarini gozden gecir.
- Questions: Q4

### no_sources (1)

- Recommendation: Ilgili veri/dokuman kapsamı, koleksiyon secimi ve dusuk-guven kaynak filtrelerini kontrol et.
- Questions: Q4

### quality_warning (1)

- Recommendation: Kalite uyarisi tipine gore genel prompt, kaynak guveni veya transport davranisini incele.
- Questions: Q4

### slow_response (1)

- Recommendation: Yavas branch'leri diagnostics latency ve LLM/RAG sureleriyle eslestir; timeout artirmadan once maliyeti bul.
- Questions: Q4

## Category Details

### A_multi_source_synthesis

- Count: 4
- Avg elapsed ms: 30088.0
- Q1: labels=low_fact_coverage; facts=2/4; mode=llm; elapsed=16303.7ms
- Q2: labels=clean_pass; facts=3/3; mode=llm; elapsed=25374.6ms
- Q3: labels=low_fact_coverage; facts=3/4; mode=llm; elapsed=18113.6ms
- Q4: labels=a2a_transport_fallback, generation_mode_mismatch, low_fact_coverage, no_sources, quality_warning, slow_response; facts=0/4; mode=kural; elapsed=60560.2ms
