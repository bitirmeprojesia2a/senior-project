# Faz 0 Kontrollu Mimari Omurga Plani

Bu dokuman, mevcut sistemi hemen yeniden yazmadan once karar mekanizmasini
gorunur, olculebilir ve kontrollu hale getirmek icin hazirlanan Faz 0 planidir.

Ana ilke:

- Once mevcut davranisi gozlemle.
- Sonra karar sozlesmesini shadow olarak uret.
- Golden sorgularda mevcut davranis ile shadow karari karsilastir.
- Davranis degisikligini ancak farklar anlasildiktan ve onay alindiktan sonra yap.

Bu fazda runtime davranisi degistirilmez. Kod refactor'u, cache acma, router/planner
birlesimi veya eski kurallarin silinmesi Faz 0 kapsami disindadir.

## 1. Hedef

Sistemin ana hedefi Slack/API/A2A uzerinden gelen universite destek sorularini
dogru kaynak ailesine yonlendirmek, yeterli kanit toplamak ve son cevabi mumkun
oldugunca LLM tabanli merkezi sentez ile uretmektir.

Mevcut sistemde LLM router, capability planner, conversation rewrite, missing-slot
policy, departman ici specialist secimi, retrieval source bias, evidence selector,
global synthesis ve judge katmanlari karar surecine katilir. Bunlarin tamamini tek
hamlede kaldirmak risklidir. Bu yuzden Faz 0'in amaci bu katmanlari once ortak bir
karar sozlesmesine baglamak ve yetki sinirlarini netlestirmektir.

## 2. Secilen Yon

Baslangic icin tercih edilen model:

```text
Unified Decision Contract, staged producers
```

Bu modelde router ve capability planner fiziksel olarak ayri kalabilir, fakat
urettikleri sinyaller tek bir `DecisionContract` icinde toplanir.

Planlanan mantik:

```text
Request
  -> Conversation resolution
  -> LLM Router producer
  -> Capability Planner producer
  -> Deterministic validators
  -> Shadow DecisionContract
  -> Mevcut dispatch/retrieval/synthesis akisi
```

Faz 0'da `DecisionContract` mevcut akisi yonetmez; sadece mevcut akisle yan yana
uretilir ve karsilastirma icin kullanilir.

## 3. DecisionContract V0 Taslagi

`DecisionContract` tek bir sorgu icin sistemin "ne yapmayi planladigini" temsil
eder. Bu nesne ileride A2A servisleri arasinda da tasinabilir olmalidir.

Taslak alanlar:

```text
contract_version
query.original
query.effective
query.normalized
conversation.is_follow_up
conversation.active_topic
conversation.frame
intent.primary
intent.secondary
intent.confidence
intent.complexity
intent.is_personal
intent.requires_auth
departments.primary
departments.secondary
task_type
specialist_hint
source_owner.primary
source_owner.fallbacks
capabilities.allowed
capabilities.selected
capabilities.params
slots.required
slots.missing
slots.clarification_policy
retrieval.collections_primary
retrieval.collections_fallback
retrieval.source_hints
retrieval.must_answer
evidence.preferred_sources
evidence.avoid_sources
answer.final_owner
answer.synthesis_policy
answer.judge_policy
cache.lookup_policy
cache.store_policy
latency_budget.class
latency_budget.max_expected_seconds
validators.applied
validators.warnings
producer_trace.router
producer_trace.capability_planner
producer_trace.deterministic_rules
```

Ilk iterasyonda bu alanlarin tamamini kodda zorunlu yapmak gerekmez. Oncelik:

- `query`
- `intent`
- `departments`
- `source_owner`
- `capabilities`
- `slots`
- `answer`
- `producer_trace`

## 4. Katman Yetki Siniflandirmasi

Mevcut katmanlar su statulerden birine ayrilacak:

- `decision_authority`: semantik karar uretir.
- `validator`: karari guvenlik, auth, slot veya kaynak onceligi acisindan denetler.
- `executor`: DB/RAG/capability calistirir, semantik karar vermez.
- `synthesizer`: kanittan son cevap uretir.
- `legacy_candidate`: eski davranis; shadow karsilastirmadan sonra tutulur veya kaldirilir.

Ilk siniflandirma:

| Katman | Mevcut Rol | Hedef Rol |
| --- | --- | --- |
| Conversation rewrite | Follow-up cozer, bazen sorguyu yeniden yazar | Validator + context producer |
| LLM router | Ana departman/intent karari | Decision authority |
| Rule routing fallback | LLM hata/low confidence durumda rota verir | Validator/fallback |
| Capability planner | Tool/source/evidence metadata uretir | Decision producer, router override yok |
| Missing-slot policy | Clarification mesaji uretir | Validator |
| Department keyword routing | Specialist secer | Legacy candidate |
| Specialist agent guards | Kaynak ve cevap guvenligi | Validator/executor |
| Retrieval source bias | Kaynaklari agirliklandirir | Executor policy |
| Evidence selector | Kanit secimi yapar | Evidence producer |
| Global synthesis | Final cevap uretir | Synthesizer |
| Main judge | Son cevap denetler | Validator |

## 5. SourceOwnershipRegistry V0 Taslagi

Kaynak sahipligi, "bu bilgi hangi sistemden gelmeli?" sorusunu merkezi hale getirir.
Structured kaynak varsa RAG'e gore onceliklidir. RAG, structured veri yoksa veya
politika aciklamasi gerekiyorsa devreye girer.

Taslak alanlar:

```text
source_owner_id
description
primary_source_type
primary_executor
fallback_source_types
allowed_departments
required_slots
auth_required
freshness_policy
rag_collections
capabilities
answer_policy
disallow_sources
notes
```

Ilk registry adaylari:

| Source owner | Primary | Fallback | Not |
| --- | --- | --- | --- |
| `personal_student_data` | Auth DB | Yok | Auth olmadan cevaplanmaz |
| `tuition_fee_catalog` | Finance DB/catalog | RAG policy | Ucret rakami structured kaynaktan gelmeli |
| `curriculum_catalog` | Curriculum DB | Yok/RAG explanation | Ders varligi, donem, AKTS DB oncelikli |
| `weekly_schedule` | Schedule DB/parser | Yok | Program sorularinda RAG son care olmali |
| `academic_calendar` | Calendar capability/structured | Announcement/RAG | Tarih structured oncelikli |
| `announcement_search` | Announcement DB | Yok | Guncellik/zaman filtresi kritik |
| `event_search` | Event DB | Yok | Yaklasan/gecmis ayrimi kritik |
| `student_affairs_policy` | RAG policy docs | Contact fallback | Yonetmelik/prosedur cevaplari |
| `international_policy` | RAG policy docs | Contact fallback | Yabanci ogrenci belgeleri/surecleri |
| `office_contact` | Static/contact registry | RAG source | Iletisim sorulari LLM sentezden muaf olabilir |

## 6. Golden Trace Formati

Her kritik sorgu icin asagidaki trace ciktisi hedeflenir:

```text
trace_id
runtime_mode
channel
original_query
effective_query
context_id
is_authenticated
conversation_resolution
router_decision
capability_planner_decision
shadow_decision_contract
contract_vs_runtime_diff
selected_departments
selected_specialists
source_owner_runtime
retrieval_collections
retrieval_candidate_count
top_evidence_sources
final_answer_owner
generation_modes
llm_call_count
llm_roles_used
latency_breakdown
judge_result
final_answer_summary
warnings
```

Bu trace, davranis degisikligi yapmadan once su sorulari cevaplar:

- Router ne dedi?
- Capability planner ne dedi?
- Runtime gercekte kimi cagirdi?
- Source ownership beklenenle uyumlu mu?
- LLM kac defa cagrildi?
- Latency hangi katmanda harcandi?
- Final cevap hangi kanita dayandi?

## 7. Golden Sorgu Aileleri

Ilk regresyon seti en az su aileleri kapsamalidir:

- Akademik takvim: final, kayit, ders ekle-sil, tek ders, yaz okulu.
- Curriculum: ders var mi, AKTS, onkosul, donem dersleri, follow-up.
- Finance: harc ucreti, odeme, ikinci ogretim, yabanci ogrenci ucreti.
- Student affairs policy: CAP, yatay gecis, muafiyet, kayit dondurma, disiplin.
- International: kayit belgeleri, ikamet, TOMER/YOS/denklik.
- Announcement: guncel duyuru, bolum duyurusu, belge/ek link.
- Event: bugunku etkinlik, yaklasan seminer, fakulte filtresi.
- Personal/auth: borc, transkript, ders kaydi gibi auth gerektiren sorular.
- Follow-up: "peki ne zaman?", "hangi belgeler?", "ben Turk ogrenciyim" gibi kisa cevaplar.
- Ambiguous: "sey basvuru ne zaman", "takvim ne zaman", "ucret ne kadar" gibi eksik slotlu sorular.

## 8. Migration Guardrail'leri

Faz 0 sonrasi davranis degisikligi yapmadan once su kosullar aranir:

- Golden trace formatinda en az 25 kritik sorgu raporlanmis olmali.
- Her sorguda runtime karari ile shadow contract farki gorunur olmali.
- Source owner farklari tek tek siniflandirilmeli: runtime dogru, contract dogru,
  ikisi de eksik, veri eksik.
- LLM call count ve latency baseline'i cikmali.
- A2A modu ana runtime kabul edilerek smoke/regresyon ayrimi yapilmali.
- Inprocess sadece karsilastirma/debug icin korunmali.

Stop kurallari:

- Kisisel veri auth disina cikiyorsa refactor durur.
- Structured kaynak yerine RAG rakam/tarih uyduruyorsa refactor durur.
- Shadow contract golden setin buyuk bolumunde runtime'dan kotu karar veriyorsa
  contract semasi revize edilir.
- Latency baseline belirgin sekilde artarsa yeni LLM cagrisi eklenmez.

## 9. Acik Kararlar

Bu maddelerde uygulama oncesi kullanici onayi alinacak:

1. `DecisionContract` kodda Pydantic model olarak mi baslasin, yoksa once sadece
   diagnostik JSON olarak mi uretilsin?
2. Shadow trace nereye yazilsin: mevcut telemetry/log yapisina mi, ayri dosya/JSONL
   raporuna mi?
3. Source ownership registry once statik YAML/JSON dosyasi mi olsun, yoksa Python
   config modeli olarak mi baslasin?
4. Department keyword routing ne zaman davranis disina alinacak: hemen shadow'a mi,
   yoksa golden farklar goruldukten sonra mi?
5. Capability planner `on` kalip sadece contract'a mi yazsin, yoksa Faz 0 boyunca
   `shadow` modda ikinci bir gozlem olarak mi denensin?

## 10. Onerilen Sonraki Adim

Onerilen en kontrollu sonraki adim:

1. Bu dokumani onayla veya revize et.
2. Sonra sadece diagnostik amacli `DecisionContract` modeli ve trace builder ekle.
3. Runtime cevabini degistirme.
4. A2A golden sorgularda mevcut runtime ile shadow contract'i karsilastir.
5. Fark raporunu inceledikten sonra ilk davranis refactor'una karar ver.
