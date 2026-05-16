# Shadow Decision Trace Golden Run 20260510_170237

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 0
- Source owner eslesmesi: 0/2
- Hata sayisi: 2
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260510_170237.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260510_170237.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | - | - | - | - | - | 0 | - | 0 | 6088.0 | ERROR |
| GT12 | follow_up_resolution | student_affairs_policy | - | - | - | - | - | 0 | - | 0 | 6092.0 | ERROR |

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260510_170237-cap-followup`
- Trace owner: `-`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- LLM roles: `-`
- LLM usage: `-`
- Hata: `ConnectionRefusedError: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti`

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260510_170237-cap-followup`
- Trace owner: `-`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- LLM roles: `-`
- LLM usage: `-`
- Hata: `ConnectionRefusedError: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti`
