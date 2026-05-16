# Shadow Decision Trace Golden Run 20260510_151501

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 8
- Trace kaydi: 1
- Source owner eslesmesi: 0/8
- Hata sayisi: 7
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260510_151501.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260510_151501.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | - | - | - | - | - | 0 | - | 0 | 6157.0 | ERROR |
| GT02 | curriculum | curriculum_catalog | - | - | - | - | - | 0 | - | 0 | 6065.8 | ERROR |
| GT03 | finance | tuition_fee_catalog | - | - | - | - | - | 0 | - | 0 | 6067.8 | ERROR |
| GT04 | student_affairs_policy | student_affairs_policy | - | - | - | - | - | 0 | - | 0 | 6066.2 | ERROR |
| GT06 | international_policy | international_policy | - | - | - | - | - | 0 | - | 0 | 6050.0 | ERROR |
| GT09 | personal_auth | personal_student_data | tuition_fee_catalog | - | department_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | observed: kept=-; pruned=-; reason=single_branch | 0 | 44904.1 | CHECK |
| GT11 | follow_up_seed | student_affairs_policy | - | - | - | - | - | 0 | - | 0 | 6080.7 | ERROR |
| GT12 | follow_up_resolution | student_affairs_policy | - | - | - | - | - | 0 | - | 0 | 6061.5 | ERROR |

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260510_151501-GT01`
- Trace owner: `-`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- LLM roles: `-`
- LLM usage: `-`
- Hata: `ConnectionRefusedError: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti`

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-20260510_151501-GT02`
- Trace owner: `-`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- LLM roles: `-`
- LLM usage: `-`
- Hata: `ConnectionRefusedError: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti`

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-20260510_151501-GT03`
- Trace owner: `-`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- LLM roles: `-`
- LLM usage: `-`
- Hata: `ConnectionRefusedError: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti`

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260510_151501-GT04`
- Trace owner: `-`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- LLM roles: `-`
- LLM usage: `-`
- Hata: `ConnectionRefusedError: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti`

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-20260510_151501-GT06`
- Trace owner: `-`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- LLM roles: `-`
- LLM usage: `-`
- Hata: `ConnectionRefusedError: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti`

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-20260510_151501-GT09`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- Selected specialists: `tuition_agent`
- Specialist selector: `finance:tuition_agent/contract, legacy=tuition_agent:match`
- Branch gate: `observed: kept=-; pruned=-; reason=single_branch`
- LLM roles: `-`
- LLM usage: `-`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz. Üretim Türü: - Kural - Routing: direct - Pipeline: finance

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260510_151501-cap-followup`
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
- Context: `shadow-golden-20260510_151501-cap-followup`
- Trace owner: `-`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- LLM roles: `-`
- LLM usage: `-`
- Hata: `ConnectionRefusedError: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti`
