# Faz 5 - Legacy Decision Layer Audit

Tarih: 2026-05-10

Bu dokuman Faz 0-4 sonrasinda sistemde halen aktif olan karar katmanlarini
siniflandirir. Amac davranisi hemen degistirmek degil; hangi katmanin ana karar,
hangi katmanin guardrail, hangi katmanin executor ve hangi katmanin mimari borc
oldugunu acik hale getirmektir.

Referans kurallar:

- Ana semantik karar mumkun oldugunca LLM tarafindan verilmelidir.
- Deterministik kurallar ana karar verici olmamalidir; guardrail, validator veya
  executor sinirinda kalmalidir.
- Source ownership merkezi olmali; ayni bilgi farkli pipeline'larda rastgele
  aranip sentezlenmemelidir.
- A2A modu ana hedef oldugu icin metadata kontratlari local ve remote akista ayni
  tasinmalidir.
- Davranis degistiren her sertlestirme golden trace veya hedefli regresyon
  gozlemi olmadan acilmamalidir.

## Kisa Sonuc

Faz 0-4 gercek mimari ilerleme sagladi: Decision Contract, Source Ownership
Registry, router-first capability planner ve source owner evidence policy runtime'a
girdi. Ancak sistemde halen cok sayida aktif karar katmani var.

En kritik bulgu: LLM router ana karar verici gibi konumlanmis olsa da bazi
deterministik katmanlar hala karari fiilen degistirebiliyor. Bu katmanlarin bir
kismi gerekli guardrail, bir kismi executor, bir kismi ise artik Decision Contract
altina alinmasi gereken legacy borc.

Faz 6 icin onerilen ana hareket: yeni davranis icat etmek degil, mevcut runtime
kararlarini tek bir `DecisionContract` omurgasina baglamak. Ilk adim read-only /
advisory olmali; sonra belirli alanlarda balanced/strict modlara gecilmeli.

## Karar Katmani Haritasi

| Katman | Dosya / fonksiyon | Su anki rol | Hedef rol | Risk | Oneri |
| --- | --- | --- | --- | --- | --- |
| Conversation resolver | `src/db/conversation_context.py:1472` | Follow-up rewrite, topic, department hints, source hints uretir | Context producer + validator | Yanlis follow-up eski konu/departman/source'u yeni soruya tasir | Faz 10'da state machine'e alinmali; Faz 6'da contract'a yazilmali |
| Follow-up heuristics | `src/db/conversation_context.py:1958` | LLM'den once follow-up kabul/reddeder | Validator / fallback | Kisa sorular gereksiz context alabilir veya bagimsiz kalabilir | LLM karar alanina "conversation.decision_source" eklenmeli |
| Router LLM | `src/routing/router.py:1022` | Departman, task, intent, slot, target capability karari | Primary decision authority | Model timeout/JSON parse hatasinda fallback devreye girer | Ana karar olarak korunmali; cikti DecisionContract'a dogrudan yazilmali |
| Router rule fallback | `src/routing/router.py:132`, `src/routing/router.py:198` | LLM basarisiz/dusuk guven olunca route'u devralir | Fallback authority | LLM kalitesi iyi olsa bile dusuk confidence yorumuyla rule one gecebilir | Kalabilir; ancak fallback nedeni contract ve trace'e zorunlu yazilmali |
| Router authoritative overrides | `src/routing/router.py:327` | Course code, takvim, uluslararasi, payment overlap vb. route degistirebilir | Guardrail / validator | "LLM ana karar" ilkesini en cok delen katman | Kaldirma degil; once shadow compare, sonra sadece validator/contract warning |
| Router conversation hints | `src/routing/router.py:895` | Onceki departmani route'a ekleyebilir | Context validator | Eski konu yeni soruya yapisabilir | Conversation contract confidence/source ile sinirlanmali |
| Missing slot clarification | `src/orchestrators/query_policy.py:491` | LLM missing_slots'u user-facing mesaja cevirir, bazi slotlari dusurur | Slot validator | Finance/student_type/program slotlari fazla veya eksik clarification uretebilir | Faz 6'da `slots.required/missing/ignored_reason` merkezi hale gelmeli |
| Academic department clarification | `src/orchestrators/query_policy.py:558` | Academic course sorularinda bolum/program ister | Validator | Genel rule/policy sorularinda gereksiz clarification uretebilir | Contract slot policy ile birlestirilmeli |
| Announcement/event marker policy | `src/orchestrators/query_policy.py:601`, `src/orchestrators/query_policy.py:660` | Capability sinyali ve block karari verir | Heuristic signal / validator | Duyuru kelimesi policy sorusunu announcement'a, tersi de olabilir | LLM gate arkasinda kalmali; source owner ile dogrulanmali |
| Early event short-circuit | `src/orchestrators/main.py:204` | Router'dan once event flow'a gidebilir | Capability executor gate | Router bypass riski | Faz 6'da contract'a `capability.pre_route_candidate` olarak yaz; davranisi simdilik koru |
| Early announcement short-circuit | `src/orchestrators/main.py:295` | Router'dan once announcement flow'a gidebilir | Capability executor gate | Policy sorusu duyuruya kayabilir | LLM gate zaten var; strict hale getirme karari Faz 6 sonrasina kalsin |
| Question cache lookup | `src/cache/policy.py:30`, `src/cache/question_cache.py:136` | Route oncesi ve route sonrasi final cevabi bypass edebilir | Runtime optimization | Eski hatali cevap Decision Contract disinda donebilir | Cache key'e contract signature eklenene kadar planner acikken bypass dogru |
| Query normalization via routing intent | `src/orchestrators/main.py:446` | Canonical query uretip effective query'yi degistirir | Query decision producer | Yanlis rewrite tum pipeline'i etkiler | Contract'ta original/effective/canonical/diff zorunlu olmali |
| Capability planner | `src/orchestrators/main.py:1743` | Router sonrasi capability/params/answer/evidence contract uretir | Planner under router authority | Scope genis oldugu icin route disi capability metadata'si uretebilir | Router-first kalmali; apply edilen her action source owner ile dogrulanmali |
| Pre-route planner helpers | `src/orchestrators/main.py:1544` | Default kapali, acilirsa router'i atlayabilir | Disabled experimental path | Eski regresyonlari geri getirebilir | Simdilik kapali kalmali; Faz 13'e kadar silme veya strict flag |
| Source owner registry | `src/core/source_ownership.py` | Source ailesini merkezi cozer | Ownership authority | Registry eksikse unresolved kalir | Faz 6 spine icinde zorunlu alan olmali; unresolved trace warning |
| Source owner policy | `src/core/source_owner_policy.py`, `src/agents/base.py:304` | Evidence'i bias eder, balanced/strict modda bloklayabilir | Evidence validator | Strict erken acilirsa dogru ama etiketsiz kaynak dusurulebilir | Advisory simdilik dogru; Faz 8'de structured owner etiketleri sertlestirilmeli |
| Department specialist selector | `src/orchestrators/department.py:268`, `src/orchestrators/department_factories.py` | Keyword once, task_type sonra, fallback son | Legacy candidate | Router dogru departmani secse bile yanlis uzman secilebilir | Faz 7'de specialist_hint/contract tabanli selector'a gecis |
| RAG fallback on A2A error | `src/orchestrators/department.py:289` | Remote agent hata verirse local/source-only fallback | Resilience fallback | A2A gercek hatasini gizleyebilir; remote/local fark uretir | A2A diagnostics'te acik isaretlenmeli, policy olarak kalabilir |
| Agent local deterministic paths | `src/agents/student/registration_agent.py:56`, `src/agents/academic/curriculum_agent.py:101`, `src/agents/finance/tuition_agent.py:70` | VT/capability/clarification cevaplarini agent icinde uretebilir | Structured executor | Ana karar agent icine dagilir | Faz 7-8'de her path DecisionContract action/source_owner ile calismali |
| Specialist synthesis | `src/agents/base.py:933`, `src/agents/base.py:1340` | Flag'e gore source-only veya LLM synthesis | Executor/synthesizer fallback | Specialist/global cift sentez veya source-only sizmasi | Main final owner korunmali; specialist response mode zorunlu audit edilmeli |
| Global synthesis | `src/orchestrators/query_policy.py:742`, `src/orchestrators/main.py:1215` | Department responses uzerinden final answer | Preferred final synthesizer | Her path global senteze girmiyor | Faz 9'da final answer owner contract ile enforce edilmeli |
| Judge / claim guard | `src/agents/base.py:1143`, `src/orchestrators/main.py:2701` | Riskli cevaplari kontrol eder | Quality validator | Her cevapta calismadigi icin guvenlik algisi yaniltici olabilir | Trace'te judge policy ve skipped reason zorunlu olmali |

## Decision Authority Siniflandirmasi

### Primary decision authority olarak kalacaklar

- Router LLM: departman, intent, task type, missing_slots, target capability.
- Conversation LLM: sadece follow-up semantigi ve standalone query uretimi icin.
- Capability planner LLM: router sonrasinda capability/params/evidence contract uretimi icin.
- Main/global final synthesis LLM: nihai kullanici cevabinin ana sentezleyicisi.

### Validator / guardrail olarak kalacaklar

- Router rule fallback ve authoritative override'lar, ama "karari sessizce ezme"
  davranisi azaltilmali.
- Missing slot ve academic department clarification kurallari.
- Announcement/event block/allow marker'lari.
- Source owner policy.
- Claim guard, answer quality filter, judge.

### Executor olarak kalacaklar

- `calendar.academic_date`, `finance.tuition_fee`, curriculum/course/schedule
  capability executor'lari.
- Announcement/event search agent'lari.
- Personal/student DB lookup path'leri.

### Legacy candidate olanlar

- Department keyword selector.
- Pre-route planner helpers.
- Agent icindeki free-standing deterministic calendar/timing/fee clarification
  kararlarinin kontratsiz halleri.
- Cache key'in Decision Contract imzasi tasimamasi.
- Conversation heuristic'lerinin LLM/context karar kaynagini ayirt etmemesi.

## Faz 6 Icin Onerilen Contract Spine

Faz 6'da davranisi agresif degistirmek yerine mevcut runtime kararlarini tek
omurgaya baglamayi oneriyorum:

1. `DecisionContract` runtime objesi ana akista olusturulsun.
2. Conversation resolver, router, capability planner, source owner ve cache karar
   gerekceleri bu objeye yazilsin.
3. A2A metadata'sinda `decision_contract` veya minimal `decision_contract_ref`
   tasinsin.
4. Agent'lar dogrudan eski metadata alanlarini okumaya devam edebilir; ama yeni
   contract alanlari ayni anda tasinsin.
5. Trace diff uretsin: runtime hangi eski rule ile contract'i degistirdi?
6. Davranis degisikligi sadece advisory warning ile baslasin.

Bu yol, sistemi yikmadan omurgayi yeniler. Gozden kacirma riskini azaltir cunku
eski ve yeni karar ayni anda gorunur.

## Karar Gerektiren Noktalar

### Karar 1 - Faz 6 baslangic modu

Secenek A - Read-only contract spine (onerilen)

- Mevcut davranis korunur.
- Contract runtime metadata ve trace'e yazilir.
- Eski rule'lar sadece "contract_diff" olarak isaretlenir.
- En dusuk regresyon riski.

Secenek B - Balanced contract spine

- Contract bazi alanlarda daha ilk fazda karar kaynagi olur: source_owner,
  final_answer_owner, cache bypass gibi.
- Daha hizli mimari temizlik saglar.
- Golden kapsam henuz 25+ olmadigi icin risk daha yuksek.

Onerim: Secenek A.

### Karar 2 - Router authoritative override politikasi

Secenek A - Simdilik koru, trace'e `override_authority` yaz (onerilen)

- Regresyon riski dusuk.
- Hangi override'in hangi soruda LLM'i ezdigi gorulur.

Secenek B - Non-authoritative override'lari sadece warning yap

- LLM ana karar hedefi hizlanir.
- Eski golden akislar bozulabilir.

Onerim: A ile baslayip golden trace verisine gore B'ye gecmek.

### Karar 3 - Department keyword selector

Secenek A - Shadow specialist selector ekle (onerilen)

- Mevcut keyword selector calisir.
- Yeni contract-based specialist_hint hesaplanir ve fark loglanir.

Secenek B - Pilot scope'ta contract-based selector'i aktif et

- Mimari borc daha hizli azalir.
- Yanlis uzman secimi cevap kalitesini direkt bozabilir.

Onerim: A.

### Karar 4 - Cache stratejisi

Secenek A - Planner/contract aktifken question cache bypass devam etsin

- Kalite guvenli.
- Latency ve maliyet biraz yuksek kalir.

Secenek B - Contract signature cache key'e eklenip cache tekrar acilsin

- Latency iyilesir.
- Signature eksik tasarlanirsa eski hatali cevap donebilir.

Onerim: Faz 6'da signature'i tasarla ama cache'i hemen acma.

### Karar 5 - Source owner policy modu

Secenek A - Advisory kalmaya devam etsin (onerilen)

- Evidence etkilenir ama cevap bloklanmaz.
- Degisimleri gozlemlemek kolay.

Secenek B - Structured owner'larda balanced moda gec

- Calendar/tuition/curriculum gibi kaynak sahipligi daha guclu korunur.
- Metadata/etiket eksigi varsa dogru kaynak elenebilir.

Onerim: Faz 8'de structured source metadata audit sonrasinda balanced.

## Faz 5 Sonrasi Uygulama Sirasi

Onay verilirse Faz 6 icin uygulanacak net isler:

1. Runtime `DecisionContract` builder'i main orchestrator icine read-only olarak
   yerlestir.
2. Router fallback/override/canonical rewrite kararlarini contract producer_trace'e
   detayli yaz.
3. Cache lookup/store kararlarini contract'a bagla, ama davranisi degistirme.
4. A2A task metadata'sina minimal contract payload/ref ekle.
5. Agent base ve department orchestrator contract'i okuyup metadata/evidence
   packet icine tasiyabilsin.
6. Local unit testlerle contract tasinmasini dogrula; pahali LLM/API testi kosma.

## Faz 5 Sonuc Notu

Bu fazin sonucu "eski sistem korunacak" degil. Tam tersi: eski sistemin hangi
parcalarinin gercekten guvenlik bariyeri, hangilerinin mimari borc oldugu ayrildi.
En guvenli ileri adim, davranisi hemen kirpmadan Decision Contract'i runtime
omurgasi yapmak ve her legacy karari bu omurgaya baglayip gorunur hale getirmek.
