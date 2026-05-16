# Faz 8 - Golden Trace Specialist Selector Visibility

## Karar

Faz 8'de runtime davranisi degistirilmedi. Bu fazin amaci, Faz 7'de aktif
hale gelen contract-first specialist selector kararini golden trace raporlarinda
gorunur yapmaktir.

Claude/Groq/yerel LLM testi calistirmadan sadece trace veri modeli ve rapor
uretimi genisletildi.

## Eklenen Trace Alanlari

`DecisionTraceRecord.runtime` artik su alanlari tasir:

- `selected_specialists`
- `specialist_selections`

`specialist_selections` her department response icin mumkunse Faz 7 selector
diagnostic payload'unu aynen saklar:

- `selected_agent_id`
- `selected_by`
- `reason`
- `contract.agent_id`
- `task_type.agent_id`
- `legacy_keyword.agent_id`
- `legacy_keyword.matches_selected`
- `legacy_keyword.used_as_fallback`

Eger eski bir response sadece `selected_agent_id` tasiyorsa trace bunu
`omu.specialist_selection.legacy` olarak isaretler. Boylece yeni ve eski akisin
ayrimi raporda kaybolmaz.

## Golden Trace Rapor Degisikligi

`scripts/run_shadow_trace_golden.py` artik her satir icin sunlari raporlar:

- `trace_selected_specialists`
- `trace_specialist_selections`
- `trace_specialist_selection_summary`
- `trace_specialist_selector_mismatches`

Markdown tabloya iki kolon eklendi:

- `Specialist Selector`
- `Mismatch`

Ornek ozet formati:

```text
student_affairs:registration_agent/contract, legacy=internship_agent:diff
```

Bu, contract-first selector gercek agent secimini yaparken eski keyword
selector'in farkli bir agent secip secmeyecegini hizli gormeyi saglar.

## Neden Bu Faz Once Geldi?

Selector mapping'ini sertlestirmeden veya registry/config haline getirmeden
once, gercek golden akislarda yeni selector'in legacy'den nerede ayrildigini
olcmek gerekiyor. Bu faz o gozlemi maliyetsiz ve tekrarlanabilir hale getirir.

## Sonraki Karar Noktasi

Faz 9 icin iki makul yol var:

1. `specialist selector mapping` koddan ayrilip registry/config haline getirilsin.
2. Once golden trace calistirilip mismatch tablosuna gore hangi mapping'lerin
   dogru, hangilerinin riskli oldugu belirlensin.

Oneri: once pahali olmayan kucuk/orta golden trace kosusu ile mismatch tablosunu
gorelim; sonra registry/config refactor'una daha net veriyle gecelim.
