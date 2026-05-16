# Faz 6 - Decision Contract Runtime Spine

Tarih: 2026-05-10

Bu fazda Faz 5'te onaylanan "Guvenli Gozlem Paketi" uygulandi. Degisikliklerin
tamami read-only mimari izleme ve metadata tasima amaclidir; route, retrieval,
cache, synthesis veya source-owner policy davranisi bilincli olarak
sertlestirilmedi.

## Uygulanan Mimari Karar

Secilen paket:

- Decision Contract modu: read-only.
- Router override'lari: korunur, karar izi contract/trace uzerinden gorunur.
- Specialist selector: mevcut davranis korunur.
- Cache: mevcut bypass/lookup policy korunur.
- Source owner policy: advisory kalir.

Bu fazin hedefi, eski karar katmanlarini hemen kaldirmak degil; karar zincirini
tek runtime omurga uzerinden A2A boyunca gozlemlenebilir hale getirmektir.

## Eklenen Runtime Contract

Yeni metadata semasi:

- `schema`: `omu.decision_contract.v1`
- `mode`: `read_only`
- `stage`: contract'in uretildigi runtime noktasi
- `contract_version`: `DecisionContract.contract_version`
- `contract`: mevcut `DecisionContract` payload'i

Bu payload su karar ailelerini tasir:

- query/original/effective
- conversation follow-up context
- routing departments/intent/task/strategy
- capability planner action
- source owner resolution
- cache lookup/store policy
- final answer owner
- validators/warnings
- producer_trace: router, capability planner, source owner, cache, deterministic rules

## A2A Metadata Zinciri

`decision_contract` asagidaki zincirde tasinabilir hale getirildi:

1. Main orchestrator runtime contract uretir.
2. Department request task metadata'sina eklenir.
3. Department orchestrator bunu specialist metadata'sina aktarir.
4. Specialist A2A REST/JSON-RPC payload'lari bu alani korur.
5. Specialist response metadata/evidence packet icinde contract okunabilir hale gelir.
6. Announcement/event capability request payload'lari da contract alanini tasiyabilir.

Bu sayede A2A dagitik modda remote specialist'e ulasan karar baglami ile local
runtime karar baglami ayni sema altinda incelenebilir.

## Davranis Degistirmeyen Garantiler

- Contract `read_only` modda uretildi.
- Cache policy degismedi.
- Router override/fallback mantigi degismedi.
- Department keyword selector degismedi.
- Source owner policy modu degismedi.
- Specialist/global synthesis kosullari degismedi.
- Contract uretimi hata verirse sadece loglanir; cevap akisi kesilmez.

## Dogrulama

Calistirilan kontroller:

- `python -m py_compile` hedeflenen source dosyalari icin basarili.
- `tests/unit/test_decision_contract.py` basarili.
- A2A department/specialist metadata hedef testleri basarili.
- Source owner/capability/evidence hedef testleri basarili.

Not: Pytest cache yazimi Windows izin uyarisiyla tekrar uyardi; test sonucunu
etkilemedi.

## Faz 7'ye Hazirlik

Bu omurga sayesinde Faz 7'de specialist selection refactor artik daha guvenli
yapilabilir. Onerilen sonraki adim:

1. Mevcut keyword selector calismaya devam eder.
2. Contract-based shadow specialist selector hesaplanir.
3. Eski selector ile shadow selector farklari trace/profiler'a yazilir.
4. Golden akislarda farklar incelenmeden aktif selector degistirilmez.
