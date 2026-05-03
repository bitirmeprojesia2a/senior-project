# Quality Benchmark Problem Summary

- Source: `tests\quality_benchmark_20260423_174611.json`
- Generated: 2026-04-23 17:50:59
- Total questions: 25

## Metrics

- `dept_accuracy`: 100.0
- `mode_accuracy`: 96.0
- `key_fact_coverage`: 70.0
- `clean_quality_pct`: 96.0
- `avg_time_ms`: 11299.9
- `median_time_ms`: 10445.8
- `intent_analysis_active`: 0
- `force_llm_synthesis_count`: 0

## Problem Classes

### low_fact_coverage (14)

- Recommendation: Retrieval/ranking ve LLM sentez promptlarini kaynakta bulunan gerekli resmi kosullari kesmeyecek sekilde iyilestir.
- Questions: Q1, Q3, Q10, Q11, Q13, Q15, Q16, Q18, Q19, Q20, Q21, Q23, Q24, Q25

### clean_pass (10)

- Recommendation: Genel kalite analizinde ele al.
- Questions: Q2, Q4, Q5, Q6, Q7, Q8, Q9, Q12, Q14, Q17

### generation_mode_mismatch (1)

- Recommendation: VT/RAG/LLM karar politikasini ve force-LLM kosullarini gozden gecir.
- Questions: Q22

### quality_warning (1)

- Recommendation: Kalite uyarisi tipine gore genel prompt, kaynak guveni veya transport davranisini incele.
- Questions: Q13

## Category Details

### A_multi_source_synthesis

- Count: 4
- Avg elapsed ms: 12037.0
- Q1: labels=low_fact_coverage; facts=3/4; mode=llm; elapsed=13825.5ms
- Q2: labels=clean_pass; facts=3/3; mode=llm; elapsed=18013.6ms
- Q3: labels=low_fact_coverage; facts=2/4; mode=llm; elapsed=7304.2ms
- Q4: labels=clean_pass; facts=4/4; mode=llm; elapsed=9004.8ms

### B_cross_department_parallel

- Count: 4
- Avg elapsed ms: 10534.2
- Q5: labels=clean_pass; facts=3/3; mode=llm; elapsed=11606.3ms
- Q6: labels=clean_pass; facts=4/4; mode=llm; elapsed=10596.1ms
- Q7: labels=clean_pass; facts=4/5; mode=llm; elapsed=8556.9ms
- Q8: labels=clean_pass; facts=4/5; mode=llm; elapsed=11377.4ms

### C_conditional_scenario

- Count: 4
- Avg elapsed ms: 11079.6
- Q9: labels=clean_pass; facts=5/5; mode=llm; elapsed=15301.4ms
- Q10: labels=low_fact_coverage; facts=3/4; mode=llm; elapsed=11717.3ms
- Q11: labels=low_fact_coverage; facts=3/4; mode=llm; elapsed=9898.7ms
- Q12: labels=clean_pass; facts=4/4; mode=llm; elapsed=7401.1ms

### D_comparison

- Count: 4
- Avg elapsed ms: 14018.2
- Q13: labels=low_fact_coverage, quality_warning; facts=2/5; mode=llm; elapsed=11701.3ms
- Q14: labels=clean_pass; facts=4/4; mode=llm; elapsed=16349.9ms
- Q15: labels=low_fact_coverage; facts=2/3; mode=llm; elapsed=9568.5ms
- Q16: labels=low_fact_coverage; facts=3/4; mode=llm; elapsed=18453.1ms

### E_process_chain

- Count: 3
- Avg elapsed ms: 8684.1
- Q17: labels=clean_pass; facts=4/5; mode=llm; elapsed=7391.3ms
- Q18: labels=low_fact_coverage; facts=2/4; mode=llm; elapsed=8215.3ms
- Q19: labels=low_fact_coverage; facts=3/6; mode=llm; elapsed=10445.8ms

### F_edge_cases

- Count: 3
- Avg elapsed ms: 13644.4
- Q20: labels=low_fact_coverage; facts=2/4; mode=llm; elapsed=8178.1ms
- Q21: labels=low_fact_coverage; facts=2/5; mode=llm; elapsed=20466.0ms
- Q22: labels=generation_mode_mismatch; facts=0/0; mode=llm; elapsed=12289.0ms

### G_semantic_paraphrase

- Count: 3
- Avg elapsed ms: 8279.0
- Q23: labels=low_fact_coverage; facts=1/4; mode=llm; elapsed=9482.4ms
- Q24: labels=low_fact_coverage; facts=1/4; mode=llm; elapsed=7202.4ms
- Q25: labels=low_fact_coverage; facts=2/3; mode=llm; elapsed=8152.2ms
