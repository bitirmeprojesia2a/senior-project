# Golden Trace Comparison

- Baseline: `BAAI-FP16` / `shadow_golden_current_baai_fp16_network_20260517`
- Candidate: `Turkish-FP16` / `shadow_golden_turkish_fp16_network_20260517`
- Baseline statuses: `{'OK': 10, 'CHECK': 1, 'FAIL': 1}`
- Candidate statuses: `{'OK': 11, 'CHECK': 1}`
- Baseline validation: `{'total': 8, 'pass': 7, 'check': 0, 'fail': 1, 'requires_judge': 1, 'enforceable_by_contract': 4, 'by_reason': {'no_query_relevant_required_values': 1, 'no_evidence_claims': 2, 'required_values_preserved': 2, 'answer_conflicts_with_evidence_values': 1, 'query_does_not_require_value_check': 2}}`
- Candidate validation: `{'total': 8, 'pass': 8, 'check': 0, 'fail': 0, 'requires_judge': 0, 'enforceable_by_contract': 3, 'by_reason': {'no_query_relevant_required_values': 2, 'no_evidence_claims': 2, 'required_values_preserved': 2, 'query_does_not_require_value_check': 2}}`
- Baseline provider errors: `{'total': 1, 'by_provider': {'groq': 1}, 'by_reason': {'rate_limit': 1}, 'retryable': 1}`
- Candidate provider errors: `{'total': 0, 'by_provider': {}, 'by_reason': {}, 'retryable': 0}`

## Case Diffs

### GT01 same

- Query: Final sinavlari ne zaman basliyor?

### GT02 same

- Query: BIL203 dersinin AKTS'si ve on kosulu nedir?

### GT03 changed

- Query: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- final_owner: `department_orchestrator` -> `main_orchestrator`

### GT04 same

- Query: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?

### GT05 changed

- Query: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- status: `FAIL` -> `OK`
- validation: `fail` -> `pass`
- baseline validation summary: `shadow/fail:answer_conflicts_with_evidence_values; missing=14`
- candidate validation summary: `shadow/pass:no_query_relevant_required_values`
- baseline preview: Benchmark, Çift anadal programına başvurabilmek için, kayıtlı olduğunuz programın yükümlülüklerini yerine getirmiş olmanız ve bazı akademik koşulları sağlamak gerekir. Bu koşullardan biri, ders geçme sisteminde en az 2,00 genel akademik not ortalaması (GANO...
- candidate preview: Benchmark, CAP başvurunuz için ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. Buna ek olarak, önlisans için 120 AKTS, lisans için 240 AKTS şartını yerine getirmelisiniz. Harc borcunuzu ise üniversite yönetimince belirlenen ödeme k...

### GT06 changed

- Query: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- llm_call_count: `4` -> `5`
- baseline preview: Benchmark, Yabancı öğrenci kaydı için gerekli belgeler arasında pasaport, ikamet izni belgesi, lise diploması ve diğer belgeler bulunmalıdır. İkamet izni için Göç İdaresi e-ikamet sistemi üzerinden alınan ve öğrenci tarafından imzalanmış Başvuru Formu, 18 y...
- candidate preview: Benchmark, Yabancı öğrenci olarak kayıt için gereken belgeler arasında pasaport fotokopisi, lisans veya yüksek lisans mezuniyet belgesi/diploma ve transkriptin dış temsilciliklerden onaylı Türkçe veya İngilizce diline çevrilmiş onaylı örneği bulunur. Yabanc...

### GT07 same

- Query: Bilgisayar muhendisligindeki son duyurular neler?

### GT08 same

- Query: Bu hafta Muhendislik Fakultesinde seminer var mi?

### GT09 same

- Query: Harc borcum var mi?

### GT10 same

- Query: Sey basvuru ne zaman?

### GT11 same

- Query: CAP basvurusu nasil yapilir?

### GT12 same

- Query: Peki not ortalamasi kac olmali?

## Summary

- Changed cases: `3/12`
