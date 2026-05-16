# Shadow Decision Trace Golden Run 20260512_203852

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 2
- Trace kaydi: 2
- Source owner eslesmesi: 2/2
- Hata sayisi: 0
- Answer validator riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260512_203852.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260512_203852.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | 1 | 125020.5 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | - | main_orchestrator | student_affairs, academic_programs | academic_programs:regulation_agent/task_type, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:required_values_preserved | 2 | 65271.3 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=3
- Provider hatalari: groq=3
- Fallback cagrilari: 0

## Answer Validator Ozeti

- Kayit: 2 | pass=2 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: query_does_not_require_value_check=1, required_values_preserved=1

## Notlar

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260512_203852-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- LLM roles: `global_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/global_synthesis/primary/error`
- Cevap preview: Benchmark, Kaynaklarda bu konuda şu bilgiler yer alıyor: - bakilmaksizin bir donemde en fazla 2 yatay gecis basvurusu yapilabilir - (2) bir alt sinifa/yari yila yapilan basvurular kabul edilmez - larinin ilk iki yariyili ile son iki yariyilina yatay gecis yapilamaz - kinci ogretime kontenjan sinirlamasi olmaksizin yatay gecis yapilabilir - den sadece ikinci ogretim diploma programlarina yatay gecis yapilabilir --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: staj_ilkeleri_23122019_inş_müh.pdf - Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf (2 pa...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260512_203852-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `-`
- Selected specialists: `regulation_agent`
- Specialist selector: `academic_programs:regulation_agent/task_type, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Answer validator: `shadow/pass:required_values_preserved`
- LLM roles: `conversation, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/error; groq/llama-3.3-70b-versatile/final_refinement/primary/error`
- Cevap preview: Benchmark, Kaynaklarda bu konuda şu bilgiler yer alıyor: - ana dal not ortalamasinin 4,00 uzerinden en az 3,00 olmasi ve ana dal diploma programinin ilgili sinifinda basari siralamasi itibari ile en az ilk % 20'sinde bulunmasi gerekir - % 20 - asari siralamasi itibari ile en az ilk % 20'sinde bulunmasi gerekir - edilerek birim yonetim kurulu karari ile senato tarafindan belirlenir - i anda birden fazla ikinci ana dal diploma programina kayit yapilamaz --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - RAG - Routing: parallel - Pipeline: academic_programs Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf
