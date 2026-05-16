# Shadow Decision Trace Golden Run 20260513_173836

Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.

## Ozet

- Sorgu sayisi: 12
- Trace kaydi: 12
- Source owner eslesmesi: 10/10
- Hata sayisi: 0
- Answer validator riskli: 1
- Value conflict riskli: 0
- Structural check riskli: 2
- LLM profile: balanced
- Question cache: bypass
- Warmup mode: none (0.0 ms)
- Provider retry: count=0 backoff=0.0s
- Trace JSONL: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tmp\shadow_decision_trace_golden_20260513_173836.jsonl`
- Makine okunabilir sonuc: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system\tests\archive\benchmarks\shadow_decision_trace_golden_20260513_173836.json`

## Sorgu Tablosu

| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Answer Check | Coverage | Value Conflict | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| GT01 | academic_calendar | academic_calendar | academic_calendar | - | main_orchestrator | student_affairs | student_affairs:registration_agent/contract | 0 | observed: kept=student_affairs; pruned=-; reason=single_branch | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | capability expected=calendar.academic_date actual=-; provider_error_seen | 3 | 14752.9 | CHECK |
| GT02 | curriculum | curriculum_catalog | curriculum_catalog | course.detail | main_orchestrator | academic_programs | academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match | 0 | observed: kept=academic_programs; pruned=-; reason=single_branch | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | provider_error_seen | 3 | 11908.5 | CHECK |
| GT03 | finance | tuition_fee_catalog | tuition_fee_catalog | finance.tuition_fee | main_orchestrator | finance | finance:tuition_agent/contract, legacy=tuition_agent:match | 0 | observed: kept=finance; pruned=-; reason=single_branch | shadow/pass:no_evidence_claims | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | 2 | 3269.8 | OK |
| GT04 | student_affairs_policy | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:no_query_relevant_required_values | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | 5 | 69225.8 | OK |
| GT05 | cross_department | - | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, finance, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; finance:tuition_agent/task_type, legacy=tuition_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, finance, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:no_query_relevant_required_values | shadow/skipped:-:not_applicable | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | 5 | 10146.9 | OK |
| GT06 | international_policy | international_policy | international_policy | international.policy_lookup | main_orchestrator | academic_programs | academic_programs:international_agent/contract, legacy=international_agent:match | 0 | applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | 3 | 7828.1 | OK |
| GT07 | announcement | announcement_search | announcement_search | - | announcement_agent | announcement | - | 0 | - | - | - | - | - | - | - | 1 | 1884.9 | OK |
| GT08 | event | event_search | event_search | - | event_agent | event | - | 0 | - | - | - | - | - | - | - | 1 | 1394.0 | OK |
| GT09 | personal_auth | personal_student_data | personal_student_data | - | clarification | finance | - | 0 | - | - | - | - | - | - | - | 1 | 2061.7 | OK |
| GT10 | ambiguous | - | - | - | clarification | - | - | 0 | - | - | - | - | - | - | - | 1 | 1741.8 | OK |
| GT11 | follow_up_seed | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | student_affairs, academic_programs | student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match | 0 | observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/pass:query_does_not_require_value_check | shadow/pass:application_process:answer_contains_process_markers | shadow/skipped:not_applicable; primary=-; competing=- | - | - | - | 4 | 10443.2 | OK |
| GT12 | follow_up_resolution | student_affairs_policy | student_affairs_policy | student_affairs.policy_lookup | main_orchestrator | academic_programs, student_affairs | academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match | 0 | observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate | shadow/fail:answer_conflicts_with_evidence_values; missing=2,50 | shadow/pass:eligibility_value:answer_contains_eligibility_markers | shadow/pass:single_primary_threshold; primary=2,50; competing=- | 2,50 | - | - | 6 | 11783.5 | FAIL |

## LLM Kullanim Ozeti

- Provider cagrilari: groq=35
- Provider hatalari: groq=3
- Fallback cagrilari: 0
- Final attempt provider hata sayisi: 3
- Retry history provider hata sayisi: 3
- Provider hata nedenleri: rate_limit=6
- Retryable provider hata sayisi: 6
- Tahmini input token: 90704 (35 cagrida)
- Prompt/system char: 90410/272464
- Role bazli cagri sayisi: conversation=1, final_refinement=2, global_synthesis=7, judge=4, routing=20, specialist_synthesis=1
- Role bazli tahmini input token: conversation=3115, final_refinement=2681, global_synthesis=11843, judge=3741, routing=69130, specialist_synthesis=194

## API Key Dagilimi

- Provider/key dagilimi: -
- Key fingerprint cagrilari: {}
- Provider org fingerprintleri: -
- Fingerprint eksik cagrilar: 35

## Warmup ve Timeout Ozeti

- Warmup: `{"mode": "none", "elapsed_ms": 0.0, "retrieval": {"enabled": false, "status": "skipped"}, "llm": {"enabled": false, "status": "skipped"}}`
- First-case latency ms: `14752.87`
- Timeout sinyalleri: capability_planner=0, routing=0

## Answer Validator Ozeti

- Kayit: 8 | pass=7 | check=0 | fail=1 | requires_judge=1 | contract_enforceable=0
- Nedenler: answer_conflicts_with_evidence_values=1, no_evidence_claims=2, no_query_relevant_required_values=3, query_does_not_require_value_check=2

## Value Conflict Ozeti

- Kayit: 8 | pass=1 | check=0 | skipped=7
- Nedenler: not_applicable=7, single_primary_threshold=1

## Notlar

### GT01 - academic_calendar

- Soru: Final sinavlari ne zaman basliyor?
- Not: Structured calendar vs RAG/announcement ayrimi.
- Context: `shadow-golden-20260513_173836-GT01`
- Trace owner: `academic_calendar`
- Capability: `-`
- Selected specialists: `registration_agent`
- Specialist selector: `student_affairs:registration_agent/contract`
- Branch gate: `observed: kept=student_affairs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Structural checks: `capability expected=calendar.academic_date actual=-; provider_error_seen`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4265; groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~2337; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1062`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_173836-GT01", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}, {"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 6314.139, "capability_planner_timeout_suspected": false, "routing_ms": 6519.313, "routing_timeout_suspected": false, "conversation_ms": 192.467, "final_synthesis_ms": 789.564}`
- Cevap preview: Benchmark, Güz dönemi final sınavları 03-16 Ocak 2026, bahar dönemi final sınavları ise 01-14 Haziran 2026 tarihlerinde olacaktır. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - VT - Routing: direct - Pipeline: student_affairs -> orchestrator Kaynak Özeti: - Belge: 2025_2026_genel_akademik_takvim.pdf

### GT02 - curriculum

- Soru: BIL203 dersinin AKTS'si ve on kosulu nedir?
- Not: Ders katalog/curriculum capability sinyali.
- Context: `shadow-golden-20260513_173836-GT02`
- Trace owner: `curriculum_catalog`
- Capability: `course.detail`
- Selected specialists: `curriculum_agent`
- Specialist selector: `academic_programs:curriculum_agent/contract, legacy=curriculum_agent:match`
- Branch gate: `observed: kept=academic_programs; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=academic_programs`
- Answer validator: `shadow/pass:no_evidence_claims`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Structural checks: `provider_error_seen`
- LLM roles: `routing, specialist_synthesis`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/error/in_tok~4267; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2682; groq/llama-3.3-70b-versatile/specialist_synthesis/primary/success/in_tok~194`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_173836-GT02", "status": "CHECK", "retryable_provider_error": true, "provider_errors": [{"provider": "groq", "role": "routing", "reason": "rate_limit"}]}]`
- Timeout signals: `{"capability_planner_ms": 4123.775, "capability_planner_timeout_suspected": false, "routing_ms": 6394.208, "routing_timeout_suspected": false, "conversation_ms": 7.995, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, BIL203 dersinin AKTS'si 5'dir. BIL203 dersinin ön koşulu BIL104'dir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - VT - Routing: direct - Pipeline: academic_programs

### GT03 - finance

- Soru: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?
- Not: Ucret rakami structured finance katalogundan gelmeli.
- Context: `shadow-golden-20260513_173836-GT03`
- Trace owner: `tuition_fee_catalog`
- Capability: `finance.tuition_fee`
- Selected specialists: `tuition_agent`
- Specialist selector: `finance:tuition_agent/contract, legacy=tuition_agent:match`
- Branch gate: `observed: kept=finance; pruned=-; reason=single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=finance`
- Answer validator: `shadow/pass:no_evidence_claims`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2175`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_173836-GT03", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1610.288, "capability_planner_timeout_suspected": false, "routing_ms": 1518.98, "routing_timeout_suspected": false, "conversation_ms": 7.071, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayıtlı. Yıllık ücret: 2.397,00 TL. Dönemlik ücret: 1.198,50 TL. (Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf) Üretim Türü: - VT - Routing: direct - Pipeline: finance Kaynak Özeti: - Veritabani kaydi: ogrenim ucreti tablosu

### GT04 - student_affairs_policy

- Soru: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- Not: Policy RAG + sure/slot sinyali.
- Context: `shadow-golden-20260513_173836-GT04`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3041; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2203; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~847; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1167`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_173836-GT04", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1760.85, "capability_planner_timeout_suspected": false, "routing_ms": 7854.407, "routing_timeout_suspected": false, "conversation_ms": 7.585, "final_synthesis_ms": 1382.144}`
- Cevap preview: Benchmark, Yatay geçişle gelen öğrenciler, daha önce aldıkları ve başarılı oldukları derslerden muaf olmak için kayıt yaptırdıkları öğretim yılı içerisinde muafiyet başvurularını yapabilirler. Yatay Geçiş İinceleme ve İntibak Komisyonu, öğrencinin muafiyet istediği dersler ile ilgili incelemeyi yaparak, daha önce alınıp başarılı olunan ve muafiyet talep edilen tüm dersler için intibakını düzenler. Öğrenciler, daha önce öğrenim gördükleri yüksek öğretim kurumlarından veya pedagojik formasyon eğitimi sertifika programından aldıkları başarılı oldukları dersler için muafiyet başvurusu yapabilirler. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf - Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf - Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf - Belge: yonerge_dis_hekimligi_lisans_egitim_og...

### GT05 - cross_department

- Soru: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- Not: Academic + finance parallel karar ve final owner.
- Context: `shadow-golden-20260513_173836-GT05`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, tuition_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; finance:tuition_agent/task_type, legacy=tuition_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, finance, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=3; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:no_query_relevant_required_values`
- Answer coverage: `shadow/skipped:-:not_applicable`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4272; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3140; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1762; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~893; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1184`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_173836-GT05", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 1914.751, "capability_planner_timeout_suspected": false, "routing_ms": 2486.631, "routing_timeout_suspected": false, "conversation_ms": 7.0, "final_synthesis_ms": 1510.28}`
- Cevap preview: Benchmark, Çift Ana Dal Programı (ÇAP) başvuru şartlarından bahsedecek olursak, ana dal programında mezuniyet hakkını elde eden ve ÇAP’ı başarıyla tamamlayan öğrenciye ayrıca ikinci ana dalı yaptığı bölümün lisans diploması verilir. Öğrencinin ÇAP’tan mezun olabilmesi için ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. Öğrencilerin önlisans için 120 AKTS, lisans için 240 AKTS şartını yerine getirmesi zorunludur. Ücret borcu ödenmesi konusunda, ödeme seçenekleri ve tutarları hakkında bilgi almak için ÖİDB (Öğrenci İşleri Daire Başkanlığı) ile iletişime geçilebilir. Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Finans: VT - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> finance -> student_affairs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (4 parça) - Veritabani kaydi: ogrenim ucreti tablosu - Belge: öğrenci_işleri_birimi.txt (2 parça)

### GT06 - international_policy

- Soru: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- Not: International policy lookup ve kaynak secimi.
- Context: `shadow-golden-20260513_173836-GT06`
- Trace owner: `international_policy`
- Capability: `international.policy_lookup`
- Selected specialists: `international_agent`
- Specialist selector: `academic_programs:international_agent/contract, legacy=international_agent:match`
- Branch gate: `applied: kept=academic_programs; pruned=student_affairs; reason=international_policy_single_branch`
- Response filter: `kept=1; dropped=0 (-); primary=academic_programs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Structural checks: `-`
- LLM roles: `routing, final_refinement`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4273; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3047; groq/llama-3.3-70b-versatile/final_refinement/primary/success/in_tok~1619`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_173836-GT06", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2469.821, "capability_planner_timeout_suspected": false, "routing_ms": 1847.696, "routing_timeout_suspected": false, "conversation_ms": 7.369, "final_synthesis_ms": 1834.293}`
- Cevap preview: Benchmark, Kayıt için gerekli belgeler, senato tarafından belirlenir. Kesin kayıt, çevrim içi veya şahsi başvuru yoluyla yapılabilir. İkamet izni başvurusunda, talep edilen ikamet izni süresinden 60 gün daha uzun süreli pasaport veya pasaport yerine geçen belgeye sahip olunması gerekmektedir. Kayıt işlemlerine ve koşullarına ilişkin bilgiler, üniversite(web sayfalarında) duyurulur. Kayıt ve ikamet izni hakkında daha ayrıntılı bilgi için Üniversite'nin ilgili web sayfalarını kontrol edebilirsiniz. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - RAG - Routing: parallel - Pipeline: academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_uluslararasi_ogrenci_kabul.pdf - Belge: ikamet_izni_başvuru_adımları_ve_gerekli_belgeler.pdf - Belge: uluslararası_öğrenci_yönergesi.pdf

### GT07 - announcement

- Soru: Bilgisayar muhendisligindeki son duyurular neler?
- Not: Announcement DB short-circuit ve bolum filtresi.
- Context: `shadow-golden-20260513_173836-GT07`
- Trace owner: `announcement_search`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- Response filter: `-`
- Answer validator: `-`
- Answer coverage: `-`
- Value conflict: `-`
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~1985`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_173836-GT07", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": null, "routing_timeout_suspected": false, "conversation_ms": 7.036, "final_synthesis_ms": null}`
- Cevap preview: İlgili duyurular: 1. 2025-2026 Bahar Yarıyılı Ara Sınav Programı 2025-2026 Bahar Yarıyılı Ara Sınav Programı için tıklayınız.. Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/2025-2026-bahar-yariyili-ara-sinav-programi 2. Vefat Haberi - Öğrencimiz Mahfuz AGİL Ondokuz Mayıs Üniversitesi Bilgisayar Mühendisliği Bölümü son sınıf öğrencilerimizden Mahfuz Agil’in vefatını derin bir üzüntüyle öğrenmiş bulunmaktay… Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/vefat-haberi-ogrencimiz-mahfuz-agil 3. 2025-26 Bahar Dönemi Lisans Haftalık Ders Programı - (Güncellendi) 2025–2026 Bahar Dönemi Lisans Haftalık Ders Programı yayımlanmıştır. Son güncelleme 11.02.2026 Ders programını görüntülemek için tıklayınız Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/2025-2026-egitim-ogretim-yili-bahar-yariyili-lisans-haftalik-ders-programi 4. 2025-2026 Eğitim-Öğretim Yılı Tek Ders Sınav Programı 2025-2026 Eğitim-Öğretim Yılı Tek Ders Sınav Programı için tıklayınız. Detay: https://bi...

### GT08 - event

- Soru: Bu hafta Muhendislik Fakultesinde seminer var mi?
- Not: Event DB short-circuit ve zaman penceresi.
- Context: `shadow-golden-20260513_173836-GT08`
- Trace owner: `event_search`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- Response filter: `-`
- Answer validator: `-`
- Answer coverage: `-`
- Value conflict: `-`
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~1959`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_173836-GT08", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": null, "routing_timeout_suspected": false, "conversation_ms": null, "final_synthesis_ms": null}`
- Cevap preview: Bu sorguya uygun guncel veya yakin tarihli etkinlik bulamadim. Isterseniz fakulte, bolum ya da etkinlik turu belirterek tekrar sorabilirsiniz. Kaynak Özeti: - Veritabanı kaydı: etkinlik araması (uygun kayıt bulunamadı)

### GT09 - personal_auth

- Soru: Harc borcum var mi?
- Not: Auth gerektiren kisisel veri guard'i.
- Context: `shadow-golden-20260513_173836-GT09`
- Trace owner: `personal_student_data`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- Response filter: `-`
- Answer validator: `-`
- Answer coverage: `-`
- Value conflict: `-`
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4261`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_173836-GT09", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": 2030.4, "routing_timeout_suspected": false, "conversation_ms": null, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz.

### GT10 - ambiguous

- Soru: Sey basvuru ne zaman?
- Not: Eksik slot/ambiguity davranisi.
- Context: `shadow-golden-20260513_173836-GT10`
- Trace owner: `-`
- Capability: `-`
- Selected specialists: `-`
- Specialist selector: `-`
- Branch gate: `-`
- Response filter: `-`
- Answer validator: `-`
- Answer coverage: `-`
- Value conflict: `-`
- Structural checks: `-`
- LLM roles: `routing`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4262`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_173836-GT10", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": null, "capability_planner_timeout_suspected": false, "routing_ms": 1703.45, "routing_timeout_suspected": false, "conversation_ms": 7.205, "final_synthesis_ms": null}`
- Cevap preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.

### GT11 - follow_up_seed

- Soru: CAP basvurusu nasil yapilir?
- Not: Follow-up icin seed soru.
- Context: `shadow-golden-20260513_173836-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `registration_agent, regulation_agent`
- Specialist selector: `student_affairs:registration_agent/contract, legacy=registration_agent:match; academic_programs:regulation_agent/contract, legacy=regulation_agent:match`
- Branch gate: `observed: kept=student_affairs, academic_programs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/pass:query_does_not_require_value_check`
- Answer coverage: `shadow/pass:application_process:answer_contains_process_markers`
- Value conflict: `shadow/skipped:not_applicable; primary=-; competing=-`
- Structural checks: `-`
- LLM roles: `routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4264; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~2976; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2103; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~894`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_173836-cap-followup", "status": "OK", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 4404.658, "capability_planner_timeout_suspected": false, "routing_ms": 1464.645, "routing_timeout_suspected": false, "conversation_ms": 8.299, "final_synthesis_ms": 1574.308}`
- Cevap preview: Benchmark, Çift anadal programına başvurmak için, ilgili bölümün önerisi ve birim yönetim kurulu kararı ile üç yıl için seçilecek ÇAP danışmanınca izlenir. ÇAP'a hak kazanan öğrencilerin, kayıt işlemleri ile ilgili sürecin nasıl gerçekleştirileceği ÖİDB web sayfasında ilan edilir. Ayrıca, aynı anda birden fazla ikinci ana dal diploma programına kayıt yapılamaz, ancak aynı anda ikinci ana dal diploma programı ile yan dal programa kayıt yapılabilir. ÇAP'tan mezun olabilmek için ana dal genel not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. --- Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz ya da ilgili sekreterin iletişim bilgilerini paylaşırım. "İletişim bilgisi" yazarak ulaşabilirsiniz. Üretim Türü: - Final Sentez: LLM - Ogrenci Isleri: RAG - Akademik Programlar: RAG - Routing: parallel - Pipeline: student_affairs -> academic_programs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (7 parça) - Belge: ön_lisans_ve_lisans_...

### GT12 - follow_up_resolution

- Soru: Peki not ortalamasi kac olmali?
- Not: Onceki CAP baglamina baglanmali.
- Context: `shadow-golden-20260513_173836-cap-followup`
- Trace owner: `student_affairs_policy`
- Capability: `student_affairs.policy_lookup`
- Selected specialists: `regulation_agent, registration_agent`
- Specialist selector: `academic_programs:regulation_agent/contract, legacy=regulation_agent:match; student_affairs:registration_agent/contract, legacy=registration_agent:match`
- Branch gate: `observed: kept=academic_programs, student_affairs; pruned=-; reason=student_affairs_policy_contract_gate`
- Response filter: `kept=2; dropped=0 (-); primary=student_affairs`
- Answer validator: `shadow/fail:answer_conflicts_with_evidence_values; missing=2,50`
- Answer coverage: `shadow/pass:eligibility_value:answer_contains_eligibility_markers`
- Value conflict: `shadow/pass:single_primary_threshold; primary=2,50; competing=-`
- Structural checks: `-`
- LLM roles: `conversation, routing, global_synthesis, judge`
- LLM usage: `groq/llama-3.3-70b-versatile/conversation/primary/success/in_tok~3115; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~4268; groq/llama-3.3-70b-versatile/routing/primary/success/in_tok~3111; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~2194; groq/llama-3.3-70b-versatile/judge/primary/success/in_tok~1107; groq/llama-3.3-70b-versatile/global_synthesis/primary/success/in_tok~1230`
- Provider retry attempts: `[{"attempt": 1, "context_id": "shadow-golden-20260513_173836-cap-followup", "status": "FAIL", "retryable_provider_error": false, "provider_errors": []}]`
- Timeout signals: `{"capability_planner_ms": 2173.104, "capability_planner_timeout_suspected": false, "routing_ms": 1410.3, "routing_timeout_suspected": false, "conversation_ms": 1637.555, "final_synthesis_ms": 1487.427}`
- Cevap preview: Benchmark, ÇAP başvurusu için ana dal not ortalamasının 4,00 üzerinden Üretim Türü: - Final Sentez: LLM - Akademik Programlar: RAG - Ogrenci Isleri: RAG - Routing: parallel - Pipeline: academic_programs -> student_affairs -> orchestrator Kaynak Özeti: - Belge: yonerge_cift_anadal_yandal.pdf (3 parça) - Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf (3 parça)
