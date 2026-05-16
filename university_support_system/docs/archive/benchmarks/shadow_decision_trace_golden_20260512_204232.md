# Shadow Decision Trace Golden Run 20260512_204232

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 3
- Trace kaydi: 3
- Source owner eslesmesi: 3/3
- Hata sayisi: 0
- Answer validator riskli: 0
- LLM profile: balanced
- Question cache: bypass
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260512_204232.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260512_204232.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | - | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=-; pruned=-; reason=single_branch | shadow/pass:no_query_relevant_required_values | 1 | 47425.8 | OK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | - | main_orchestrator | academic_programs | academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match | 0 | observed: kept=-; pruned=-; reason=single_branch | shadow/pass:no_evidence_claims | 0 | 28349.8 | OK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | - | main_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | observed: kept=-; pruned=-; reason=single_branch | shadow/pass:no_evidence_claims | 0 | 28559.3 | OK |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=1
- Provider hatalari: groq=1
- Fallback cagrilari: 0

## Answer Validator Ozeti

- Kayit: 3 | pass=3 | check=0 | fail=0 | requires_judge=0 | contract_enforceable=0
- Nedenler: no_evidence_claims=2, no_query_relevant_required_values=1

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260512_204232-GT01`
- Trace owner: `academic_calendar`
- Capability: `-`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract`
- Branch gate: `observed: kept=-; pruned=-; reason=single_branch`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- LLM roles: `final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/final_refinement/primary/error`
- Cevap preview: Benchmark, Genel akademik takvime gore yariyil sonu/final sinavlari guz donemi icin 03-16 Ocak 2026, bahar donemi icin 01-14 Haziran 2026 tarihlerindedir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - VT - Routing: direct - Pipeline: student_affairs Kaynak Özeti: - Belge: 2025_2026_genel_akademik_takvim.pdf

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-20260512_204232-GT02`
- Trace owner: `curriculum_catalog`
- Capability: `-`
- Selected specialists: `curriculum_agent`
- Specialist selector: `academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match`
- Branch gate: `observed: kept=-; pruned=-; reason=single_branch`
- Answer validator: `shadow/pass:no_evidence_claims`
- LLM roles: `-`
- LLM usage: `-`
- Cevap preview: Benchmark, BIL203 Veri Yapilari (3 kredi, 5 AKTS) dersinin önkoşulları: BIL104 Programlamaya Giris II. Önkoşullu derslerden en az DD alınmış olması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - VT - Routing: direct - Pipeline: academic_programs Kaynak Özeti: - Veritabani kaydi: ders onkosulu

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-20260512_204232-GT03`
- Trace owner: `tuition_fee_catalog`
- Capability: `-`
- Selected specialists: `tuition_agent`
- Specialist selector: `finance:tuition_agent/contract, legacy=tuition_agent:match`
- Branch gate: `observed: kept=-; pruned=-; reason=single_branch`
- Answer validator: `shadow/pass:no_evidence_claims`
- LLM roles: `-`
- LLM usage: `-`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Routing: direct - Pipeline: finance Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu
