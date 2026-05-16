# Codex Proje Baglami

Bu dosya yeni bir Codex/LLM sohbetine gecildiginde once okunacak kisa teknik handoff dosyasidir. Eski tarihce yerine guncel kararlar, riskler ve calisma komutlari burada tutulur.

## Calisma Ilkesi: Her Karari Elestirel Dogrula

Bu projede onceki kararlar dogru kabul edilmemelidir. Bu dosya bile mutlak kaynak degildir; yeni sohbet once dosyayi okur, sonra kod/log/test ile dogrular.

Zorunlu yaklasim:

- Kullanici veya onceki Codex bir cozum onerirse dogru varsayma.
- "Bunu neden boyle yapmistik?" sorusunu mutlaka sor.
- Eski karar hala gecerli mi, yoksa yeni mimariyle celisiyor mu kontrol et.
- Kodda aktif mi, yoksa sadece artik/legacy iz mi dogrula.
- Bir sorun icin yalnizca verilen cozum yolunu degil, daha iyi yeni yaklasimlari da ara.
- Soru bazli patch atmak yerine sistemik cozum ara.
- LLM karar verici olmali mi, deterministic guard mi olmali, yoksa VT/RAG source ownership mi eksik; bunlari ayir.
- "Calisiyor gibi" gorunen Slack cevabini yeterli sayma; kaynak, route, capability, final synthesis ve cache katmanlarini kontrol et.

Yeni sohbette alinacak her karar icin mini kontrol:

```text
1. Bu karar hangi sorunu cozuyor?
2. Bu karar yeni bir statik/hardcoded kapi mi ekliyor?
3. Eski baska bir kural ile cakisir mi?
4. LLM kararini mi iyilestiriyor, yoksa LLM'i bypass mi ediyor?
5. Kaynak sahipligi dogru mu?
6. Follow-up/clarification etkisi ne?
7. Eski golden Slack akislarini bozar mi?
8. Bunu feature flag/shadow/fallback ile daha guvenli yapabilir miyiz?
```

Asla yapma:

- "Kullanici boyle istedi, direkt uygulayalim" refleksiyle mimari karar degistirme.
- Bir Slack ornegine bakip genel kural ekleme.
- Kaynakta olmayan cevabi prompt'a veya koda gomerek duzeltme.
- Router/capability/clarification gibi ana karar katmanlarini test etmeden degistirme.

## Repo ve Ortam

- Ana repo: `C:\Users\OMER FARUK DERIN\Desktop\bitirme projesi\university_support_system`
- Uygulama kok dizini: `C:\Users\OMER FARUK DERIN\Desktop\bitirme projesi\university_support_system\university_support_system`
- Shell: PowerShell.
- Komutlari genelde uygulama kok dizininden calistir.
- Kod aramada once `rg` kullan.
- Manuel dosya editi icin `apply_patch` tercih et.
- Lokal unit testler venv ile calisir: `.\venv\Scripts\python.exe -m pytest ...`

## Urun ve Ana Akis

Bu proje OMU universite destek botudur. Slack sadece giris kanali/adaptordur; is mantigi Slack dosyalarina gomulmemelidir.

Guncel ana akis:

```text
Slack/API
-> MainOrchestrator
-> legacy Router
-> DepartmentOrchestrator / SpecialistAgent
-> VT veya RAG
-> main/global final synthesis ve kalite katmanlari
-> UserQueryResponse
```

Departmanlar:

- `student_affairs`
- `academic_programs`
- `finance`

Specialist ajanlar:

- Student: `registration_agent`, `graduation_agent`, `internship_agent`, `student_life_agent`
- Academic: `curriculum_agent`, `regulation_agent`, `international_agent`
- Finance: `tuition_agent`, `scholarship_agent`
- Capability/surface: `announcement_agent`, `event_agent`

## En Onemli Guncel Karar

Router ve capability planner birlestirme denemesi geri alindi.

Dogru mevcut davranis:

1. Router ana karar katmanidir.
2. Capability planner router'i atlamaz.
3. Capability planner routing/departman kararini degistirmez.
4. Capability planner router sonrasinda capability/parametre/answer_contract/evidence_contract metadata'si uretir.
5. `CAPABILITY_PLANNER_PRE_ROUTE_ENABLED` varsayilani `False`.

Ilgili dosyalar:

- `src/orchestrators/main.py`
- `src/capabilities/planner.py`
- `src/capabilities/models.py`
- `src/capabilities/registry.py`
- `src/core/config.py`

Planner promptunda artik `departments` isteme kurali ve ornekleri yoktur. Model hala eski payload'lari parse edebilsin diye `CapabilityAction.departments` alani kalabilir, ancak prompt bunu uretmeye tesvik etmez.

Guncel kritik ayrinti:

- `CAPABILITY_PLANNER_MODE=on` default ise planner sadece router'in sectigi departman capability'lerini degil, `CAPABILITY_PLANNER_SCOPE` icindeki tum capability ailelerini gorebilir (`academic_programs,student_affairs,finance,announcement,event`).
- Bu, routing'i degistirmek icin degil, router sonrasi hangi capability/policy metadata'si yararli olabilir diye genis whitelist vermek icindir.
- Bu yuzden "router academic_programs secti, planner student_affairs.policy_lookup secti" gibi bir telemetry gorulebilir. Bu tek basina route override demek degildir; metadata'nin hangi agent tarafindan tuketildigi ayrica kontrol edilmeli.
- Pre-route helper kodu (`_maybe_plan_capability_pre_route`, `_routing_from_capability_payload`) hala dosyada durur ama default kapali ve normal akista router'in yerine gecmemelidir. Bu helper tekrar baglanirsa eski router+capability birlestirme regresyonlari geri gelebilir.
- `.env` icinde `CAPABILITY_PLANNER_*` satirlari yoksa bile `src/core/config.py` default'lari uygulanir: `mode="on"`, `scope="academic_programs,student_affairs,finance,announcement,event"`, `pre_route_enabled=False`, `confidence_threshold=0.45`.

## COK ONEMLI: Eski Yapi Hala Sistemde Duruyor

Bu projede gecmisten kalan cok sayida karar katmani var. Yeni bir hata analizinde "LLM boyle karar verdi" varsayimi yapma. Once hangi katmanin karar verdigini dogrula.

Sistemde halen bulunabilen karar kaynaklari:

1. Conversation context / follow-up rewrite
   - Dosya: `src/db/conversation_context.py`
   - Kullanici sorusunu `standalone_query` / `effective_query` olarak yeniden yazabilir.
   - Onceki konu, bolum, ders, kaynak ve departman ipuclarini tasir.
   - Risk: Kisa cevaplar (`Bilgisayar Muhendisligi`, `turk`, `peki kac AKTS?`) yanlis onceki konuya baglanabilir veya hic baglanmayabilir.

2. Legacy router
   - Dosyalar: `src/routing/router.py`, `src/routing/routing_policy.py`, `src/llm/prompt_templates.py`
   - LLM routing + rule/policy override karisimi vardir.
   - Router ana karar katmani olarak kalmali, ama icinde hala deterministik override'lar bulunabilir.
   - Risk: LLM kararindan sonra rule override departman degistirebilir veya clarification'a cekebilir.

3. MainOrchestrator erken kapilari
   - Dosya: `src/orchestrators/main.py`
   - Announcement/event short-circuit veya gate davranislari halen var.
   - Bu kapilar explicit duyuru/etkinlik niyetinde hizli VT akisina sokabilir.
   - Risk: Prosedur sorulari yanlislikla duyuru aramasina kacarsa kullaniciya duyuru listesi gelir.

4. DepartmentOrchestrator keyword routing
   - Dosya: `src/orchestrators/department.py`
   - Departman icindeki uzman ajan secimi icin `keyword_routing` vardir.
   - Factory dosyalari: `src/orchestrators/department_factories.py`
   - Risk: Departman dogru olsa bile uzman ajan yanlis secilebilir.

5. Specialist agent local guards
   - Dosyalar: `src/agents/student/*`, `src/agents/academic/*`, `src/agents/finance/*`
   - Her agent icinde bazi erken VT cevaplari, filtreler, no-info davranislari ve RAG ranking helper'lari vardir.
   - Risk: Ana router dogru olsa bile agent icinde LLM'e gitmeden deterministic cevap donebilir.

6. Capability planner / executor
   - Dosyalar: `src/capabilities/*`
   - Router sonrasinda capability metadata'si uretir.
   - Executor whitelisted deterministik fonksiyonlari calistirir.
   - Risk: Capability kayit bulamazsa ham "Bulunamadi" cevabi kullaniciya kacmamali; fallback kontrol edilmeli.

7. RAG search planner / retriever
   - Dosyalar: `src/rag/search_planner.py`, `src/rag/retriever.py`, `src/rag/pipeline.py`
   - Hangi koleksiyonlardan ve kac adayla arama yapilacagini belirler.
   - Risk: Dogru departman secilse bile yanlis belge ailesi yukari cikabilir.

8. Evidence / quality katmanlari
   - Dosyalar: `src/quality/evidence.py`, `src/quality/evidence_selector.py`, `src/quality/claim_guard.py`, `src/quality/answer_filter.py`, `src/quality/judge.py`
   - Kaynak secimi, claim guard, foreign token temizligi, judge/retry gibi davranislar burada.
   - Risk: Kaynakta bilgi varken evidence paketi eksik kalabilir veya LLM yanlis sentez yapabilir.

Bu nedenle bir Slack hatasi incelenirken minimum kontrol sirasi:

```text
1. original_query ne?
2. conversation effective/standalone query ne?
3. router hangi departments/strategy/task_type/intent verdi?
4. capability planner calisti mi, ne uretmis?
5. capability executor calisti mi, records var mi?
6. hangi department/specialist agent cagrildi?
7. RAG hangi kaynaklari secti?
8. final synthesis/judge/claim_guard cevabi degistirdi mi?
9. Slack cache veya eski container ihtimali var mi?
```

## Legacy/Kural Tabanli Katmanlarin Ayrintili Haritasi

Bu bolum ozellikle onemli: "legacy" burada "kesinlikle kullanilmiyor" demek degildir. Bazi legacy katmanlar hala aktif ana akista calisir, bazilari feature flag arkasinda pasiftir, bazilari da safety net/post-process olarak durur. Yeni sohbette bunlari tek tek dogrulamadan "sistem LLM kararli calisiyor" deme.

### Aktif legacy: Router override katmani

Dosya:

- `src/routing/router.py`

Ozellikle bakilacak fonksiyonlar:

- `_apply_routing_overrides(...)`
- `_compute_routing_override(...)`
- `_apply_conversation_hints(...)`

Ne yapiyor:

- Router LLM kararindan sonra veya rule kararinin uzerinde departman/strategy/task_type degistirebilir.
- Router icinde rule-based karar her zaman hesaplanir; LLM basarisiz/timeout/invalid JSON olursa fallback olarak kullanilir.
- Cok dusuk bilgi iceren bazi mesajlarda LLM routing atlanabilir veya fallback one cikabilir.
- Bazi override'lar `authoritative` gibi davranir; yani LLM baska bir sey dese bile rota degisebilir.
- `llm_primary=True` olsa bile authoritative override'lar tamamen devre disi olmayabilir.
- Kisa/ambiguous basvuru tarihi gibi sorularda clarification'a cekebilir.
- CAP + harc, yaz okulu, tek ders, AKTS/GANO, akademik takvim, uluslararasi, burs/harc, duyuru, etkinlik gibi bircok intent icin marker tabanli yonlendirme vardir.

Risk:

- LLM dogru departman dese bile override yanlis departmana veya `CLARIFICATION` sonucuna goturebilir.
- "Akademik takvimde derslerin bitimi" gibi net VT sorusu RAG'a veya tersine "tek ders kurali" duyuru aramasina kayabilir.
- LLM yaniti parse edilemezse veya provider timeout olursa "eski kural tabanli router" sessizce ana karar olur.
- Router `intent.force_llm_synthesis` ve `intent.target_capability` alanlarini da etkiler; bu alanlar sonradan capability gate veya final synthesis davranisini degistirebilir.
- Bir hata incelenirken sadece planner/agent loguna bakmak yetmez; router override sonucu mutlaka kontrol edilmeli.

Bu katman "eski" ama hala ana karar uzerinde etkili olabilir. Kaldirmak risklidir; once shadow telemetry ile hangi override'in hangi soruda calistigi loglanmali.

### Aktif legacy: Query policy ve clarification kapilari

Dosyalar:

- `src/orchestrators/query_policy.py`
- `src/orchestrators/main.py`
- `src/db/conversation_context.py`

Ne yapiyor:

- Eksik slot kontrolu yapabilir: `student_type`, `faculty`, `program`, `application_type`, `course_code`, `department` vb.
- Kullaniciya "hangi basvuru turu?", "fakulte/bolum belirtir misiniz?", "Turk ogrenci misiniz?" gibi clarification dondurebilir.
- Bu clarification bazen LLM planindan once, bazen routing sonrasi metadata ile tetiklenebilir.

Risk:

- Uluslararasi kayit belgeleri gibi program istememesi gereken sorularda fakulte/bolum sorabilir.
- Ucret sorularinda ogrenci turu follow-up'i dogru baglanmayabilir.
- Bolum adini tek basina yazan kullanici yeni konu acmis gibi algilanabilir veya onceki yanlis soruya baglanabilir.
- Clarification cevabi gelince onceki asil intent kaybolabilir; sonraki mesajda context zinciri dogru tasinmazsa bot baska alana kayar.

Yeni cozumlerde bu katmana "bir if daha ekle" refleksiyle yaklasma. Once clarification hangi katmandan cikti, missing slot gercekten gerekli mi, LLM planinda `missing_slots` dogru mu kontrol et.

Guncel query_policy karar aileleri:

- Missing slot clarification:
  - `build_missing_slot_clarification_message(...)` LLM/router intentindeki `missing_slots` alanini user-facing mesaja cevirir.
  - `auth`, `student_type`, `application_type`, `faculty_or_program`, `department_or_program`, `program`, `course_name` gibi slotlar burada islenir.
  - `intent.primary_intent == "academic_calendar"` ise missing slot clarification donmez.
  - Uluslararasi kayit/basvuru/belge/evrak sorularinda program/fakulte/course slotlari dusurulur.
  - Ucret/tutar sorusu degilse student_type/faculty slotlari finance icin bile dusurulebilir.
- Akademik departman clarification:
  - `requires_academic_department_clarification(...)` yalniz academic course query gibi durumlarda departman/program isteyebilir.
  - Genel kural/policy sorularinda (`basvuru`, `katilabilir`, `mezun`, `kosul`, `tarih`, `takvim`, `surec`) departman istememesi hedeflenir.
- Announcement primary flow:
  - `looks_like_announcement_query(...)` sadece acik duyuru/haber/ilan/link niyetinde true olmali.
  - Akademik takvim tarih marker'lari varsa ve explicit duyuru yoksa announcement'a kacmamali.
  - `ders programi` sadece duyuru/link/yayinlandi gibi ek niyetle announcement'a gitmeli; yoksa curriculum/schedule VT daha dogru.
- Procedural announcement block:
  - `should_block_announcement_primary_flow(...)` tek ders, yaz okulu, CAP, staj, muafiyet, ders kaydi, yatay gecis, mezuniyet gibi prosedur sorularini duyuru-only akistan korumaya calisir.
  - Explicit `duyuru/ilan/haber/link` varsa blok kalkabilir.
- Related announcement:
  - `should_fetch_related_announcements(...)` prosedur cevabina ek duyuru getirip getirmemeyi belirler.
  - Ana cevap policy/RAG olurken, duyuru sadece destekleyici olabilir.
- Latest fallback:
  - `should_allow_announcement_latest_fallback(...)` "son/guncel duyurular" gibi genel sorgularda latest fallback'e izin verir.
  - Konu spesifik `tek ders`, `sinav programi`, `ders programi` gibi sorgularda generic latest fallback kapali olmalidir.
- Announcement follow-up:
  - `should_keep_announcement_follow_up(...)` kisa follow-up'lari duyuru flow'unda tutabilir (`detay`, `ozet`, `link`, `tarih`, `hangisi`, `ilk/ikincisi`).
  - Topic shift marker'i varsa announcement context birakilmali.

Risk:

- Bu katman LLM degildir; marker setleri aktif karar verir.
- Bir prosedur sorusu "duyuru" kelimesini sadece baglam olarak kullansa bile yanlis primary announcement flow'a girebilir veya tam tersi gercek duyuru sorusu engellenebilir.
- Akademik takvim/tarih sorulari hem `calendar.academic_date`, hem RAG, hem announcement marker'lariyla temas edebilir; hangi guard'in calistigi logdan dogrulanmali.
- Missing slot temizleme kurallari soru bazli gibi gorunse de genis davranis etkiler; yeni slot kurali eklemeden once golden flow testleri kosulmali.

### Aktif legacy: Department icindeki keyword routing

Dosyalar:

- `src/orchestrators/department.py`
- `src/orchestrators/department_factories.py`

Ne yapiyor:

- Router yalnizca departmani secince, departman icinde hangi specialist agent'a gidilecegini `keyword_routing` ile belirler.
- Student tarafinda `kayit`, `akademik takvim`, `yaz okulu`, `tek ders`, `staj`, `topluluk`, `konukevi`, `gano`, `akts` gibi marker'lar vardir.
- Academic tarafinda `mufredat`, `ders`, `onkosul`, `akts`, `erasmus`, `uluslararasi`, `yonetmelik` gibi marker'lar vardir.
- Finance tarafinda `harc`, `odeme`, `borc`, `burs`, `yemek bursu`, `kismi zamanli` gibi marker'lar vardir.

Risk:

- Departman dogru olsa bile agent yanlis secilebilir.
- "Bilgisayar Muhendisligi 5. yariyil dersleri" curriculum yerine regulation veya generic RAG'a kayabilir.
- "Ogrenci toplulugu" student_life yerine registration veya generic student affairs path'e kayabilir.
- "Uluslararasi ogrenci kayit belgeleri" international_agent yerine registration/policy lookup'a dusebilir.

Bu katman hala aktif kabul edilmeli. Capability planner dogru metadata uretse bile DepartmentOrchestrator keyword secimi baska agent'a gonderebilir mi diye logla.

Guncel factory davranisi ozeti (`src/orchestrators/department_factories.py`):

- Student Affairs:
  - Fallback agent `registration_agent`.
  - `PROCEDURE_QUERY` default `registration_agent`.
  - `mezuniyet`, `transkript`, `diploma`, `bagil` -> `graduation_agent`.
  - `staj`, `bitirme`, `mup`, `sanayi` -> `internship_agent`.
  - `kimlik`, `topluluk`, `konukevi`, `engelli`, `konsey` -> `student_life_agent`.
  - `cap`, `yaz okulu`, `tek ders`, `gano`, `akts hakki`, `ders yuku`, `akademik takvim`, `muafiyet`, `yatay`, `disiplin`, `itiraz` -> genelde `registration_agent`.
- Academic Programs:
  - Fallback agent `international_agent`.
  - `COURSE_QUERY` default `curriculum_agent`.
  - `PROCEDURE_QUERY` default `regulation_agent`.
  - `mufredat`, `ders`, `onkosul`, generic `akts` -> `curriculum_agent`.
  - `akts hakki`, `kredi siniri`, `ders yuku`, `gano`, `cap`, `tek ders`, `yonerge`, `yonetmelik`, `devam zorunlulugu` -> `regulation_agent`.
  - `erasmus`, `uluslararasi`, `yabanci`, `ikamet`, `denklik`, `tomer`, `yos`, `kontenjan` -> `international_agent`.
- Finance:
  - Fallback agent `tuition_agent`.
  - `harc`, `odeme`, `taksit`, `dekont`, `borc` -> `tuition_agent`.
  - `burs`, `yemek bursu`, `kismi zamanli` -> `scholarship_agent`.

Bu tablo karar kaynagi olarak degil denetim haritasi olarak kullanilmali. Yeni bir sorun ciktiginda "hangi keyword hangi ajani secti" logla, sonra bu mapping gercek ihtiyaca uygun mu sorgula.

### Aktif legacy: Core marker ve intent guard dosyalari

Dosyalar:

- `src/core/query_markers.py`
- `src/core/query_intent_guards.py`
- `src/orchestrators/query_normalization.py`

Ne yapiyor:

- Sorgudaki terimleri normalize eder veya niyet marker'lari cikarir.
- Bazi kisitli sorgularda LLM destekli query normalization calisabilir.
- Announcement/event gibi hedef capability sinyalleri uretilebilir.

Risk:

- Kisa sorgularda normalization semantigi bozabilir.
- Eski marker listesi yeni capability planina ters dusebilir.
- Normalization sonucu `target_capability=announcement/event` gibi erken gate'leri tetikleyebilir.

Not:

- `settings.llm.query_normalization_enabled=True` gorunebilir; bu, tum routing LLM planner ile yapiliyor demek degildir.
- Query normalization ana planner degil, yardimci/onceleyici sinyal katmanidir.

### Aktif veya yari-aktif legacy: MainOrchestrator short-circuit/gate davranislari

Dosya:

- `src/orchestrators/main.py`

Bakilacak yerler:

- Announcement gate / event gate.
- Calendar capability execution.
- Capability planner apply/fallback bloklari.
- `build_evidence_packet_fallback_answer(...)` kullanimi.

Ne yapiyor:

- Bazi VT/capability akislarini departman dispatch'ten once veya farkli bir yoldan calistirabilir.
- Announcement/event aramalari normal department agent akisi gibi davranmayabilir.
- Capability sonucu bos geldiginde fallback yapilip yapilmadigi her capability icin ayni olmayabilir.
- Router intent'inden gelen `target_capability` announcement/event gate'lerini acabilir.
- Query normalization sonucu router ile "merged" calisir; ayri bir pre-normalization LLM cagrisi gibi gorunmeyebilir ama canonical query etkisi yine vardir.
- Question cache lookup ve storage kararlarini da bu katman uygular.

Risk:

- "Bulunamadi" gibi ham VT cevabi final sentez/fallback olmadan kullaniciya gidebilir.
- Duyuru/etkinlik kaydi RAG ile de VT ile de mevcutsa hangi source owner'in kullanildigi belirsizlesebilir.
- Bir soru policy/RAG cevabi isterken duyuru listesi donebilir.
- Capability planner acikken question cache lookup su an `capability_planner_enabled` gerekcesiyle bypass edilebilir; cache hit beklerken sistem yeniden cevap uretir.
- Capability planner kapatilirsa cache davranisi degisebilir; eski hatali cevap cache'ten gelebilir.

Bu katmani degistirmek sistem geneline yayilir. Her degisiklikte announcement, event, calendar, curriculum ve student policy golden akislarini beraber kos.

### Aktif legacy: Specialist agent local policy/profile/helper katmanlari

Dosya aileleri:

- `src/agents/student/registration_agent.py`
- `src/agents/student/registration_utils.py`
- `src/agents/student/student_life_agent.py`
- `src/agents/student/internship_agent.py`
- `src/agents/academic/curriculum_agent.py`
- `src/agents/academic/curriculum_utils.py`
- `src/agents/academic/international_agent.py`
- `src/agents/finance/tuition_agent.py`
- `src/agents/finance/tuition_utils.py`
- `src/capabilities/finance_executor.py`

Ne yapiyor:

- Agent icinde query profile, source boost, deterministic extraction, local fallback, preferred/avoid source gibi davranislar olabilir.
- Student registration tarafinda tek ders, yaz okulu, ek AKTS, mezuniyet, ders alma gibi policy lookup davranislari vardir.
- Curriculum tarafinda ders adi/bolum/yarıyil/kod cikarma ve VT lookup helper'lari vardir.
- Finance tarafinda ogrenci turu, birim/fakulte, ucret tablosu eslestirme gibi deterministic katmanlar vardir.

Risk:

- Planner dogru capability dese bile agent kendi local profile'i ile baska retrieval query uretir.
- RAG kaynaklari dogru olsa bile agent-level fallback "kaynak bilgisi final cevap icin hazirlandi" gibi ham metni kullaniciya kacirabilir.
- Finance clarification dogru ciksa bile ogrenci turu follow-up'i kaybolursa ucret tablosu yanlis eslesebilir.
- Curriculum'da bolum adi ders adi gibi algilanabilir veya tersi olabilir.

Bu dosyalarda yapilan her patch "sadece bu soru" gibi gorunse bile genelde source ranking, follow-up ve clarification davranisini etkiler.

### Aktif legacy: RAG source bias ve evidence packing

Dosyalar:

- `src/rag/search_planner.py`
- `src/rag/retriever.py`
- `src/rag/pipeline.py`
- `src/quality/evidence.py`
- `src/quality/evidence_selector.py`
- `src/orchestrators/evidence_utils.py`

Ne yapiyor:

- Hangi koleksiyon/belge ailesinden kac chunk gelecegini belirler.
- Preferred/avoid source, conversation source refs, department source score gibi bias uygulayabilir.
- Long context'i evidence packet'e sikistirir.

Guncel aktif bias/boost noktalarindan bazilari:

- `src.rag.retriever._apply_conversation_hints(...)`
  - `conversation_source_refs` source alaninda gecerse score'a `CONVERSATION_SOURCE_HINT_BOOST` ekler.
  - `topic_hint` content icinde gecerse topic boost ekler.
  - Follow-up icin yararli ama eski kaynak ipucu yeni konuya yapisirsa yanlis belgeyi yukari tasir.
- `src.agents.base._apply_plan_evidence_source_bias(...)`
  - `evidence_contract.preferred_sources` marker'i source/title/file/content icinde gecerse `+0.22` boost verir.
  - `evidence_contract.avoid_sources` marker'i gecerse score'u `*0.30` ile dusurur.
  - Sadece plan_context varsa calisir; legacy RAG akisini dogrudan etkilemez.
  - Ancak planner prompt ornekleri preferred/avoid kaynaklari belirledigi icin prompt bias'i gercek ranking bias'ina donusur.
- `src.agents.base._apply_evidence_boost(...)`
  - Regex tabanli eski boost/demote katmanidir.
  - Mezuniyet AKTS, tarih, belge, ucret, AKTS/GANO, tek ders gibi soru tipleri icin content sinyallerine score ekler veya dusurur.
  - Bu LLM degildir; source ranking'e statik etki yapar.
- `src.rag.search_planner` icindeki source relevance, finance source penalty, education-level penalty, student-affairs FAQ bias ve profile shaping katmanlari RAG sonucunu reranker oncesi/sonrasi etkileyebilir.

Risk:

- Dogru belge var ama yanlis chunk secildigi icin cevap eksik veya yanlis olur.
- Ayni belge icinde kritik madde alt satirlarda kalip kesilebilir.
- Diger belgelerden dusuk alakali chunk'lar dogru belgeyi bastirabilir.
- "Daha genis retrieval" cozum gibi gorunur ama final LLM'e giden paket hala eksikse ise yaramaz.
- Plan preferred/avoid kaynaklari yanlis veya fazla dar ise dogru belge dusurulebilir.
- Reranker yuksek score verdi diye dusuk term-overlap kaynaklar tutulabilir.

Bu katmanda hedef "her seyi LLM'e basmak" degil; ilgili belge/madde blokunu butun tasimak, dusuk alakali baska belgeleri azaltmak ve kesmeyi madde/belge sinirinda yapmak olmali.

### Aktif legacy/safety: ClaimGuard, answer_filter, response cleanup

Dosyalar:

- `src/quality/claim_guard.py`
- `src/quality/answer_filter.py`
- `src/orchestrators/response_utils.py`
- `src/orchestrators/synthesis_utils.py`
- `src/orchestrators/user_response_builders.py`

Ne yapiyor:

- Bazi yanlis claim'leri temizleyebilir veya cevabi yeniden yazdirabilir.
- Foreign token/garip dil karisimlarini temizlemeye calisabilir.
- LLM final sentez calismazsa evidence fallback answer uretebilir.
- Kullaniciya giden son `UserQueryResponse` cevabini temizler, kisaltir, tekrar eden satirlari ayiklar.
- `settings.server.response_debug_enabled` aciksa `Uretim Turu` ve `Kaynak Ozeti` sonradan eklenir; kapaliysa Slack/API cevabinda bu ozetler gorunmeyebilir.
- `append_generation_summary`, `append_source_summary`, `collect_generation_modes` gibi helper'lar hangi yolun kullanildigi algisini etkiler.
- `response_eligible_for_global_synthesis` announcement cevaplarini global synthesis disinda tutar.

Risk:

- Dogru cevabi fazla budayabilir.
- Yanlis cevabi "daha temiz" hale getirip guvenilir gibi gosterebilir.
- Fallback cevap kullaniciya ham kaynak bullet'i olarak gidebilir.
- "Final Sentez: LLM" gozukse bile oncesinde veya sonrasinda statik cleanup uygulanmis olabilir.
- `Kaynak Ozeti` cevabin icinde kullanilan tum kanitlari degil, response/source listesinden formatlanan yuzey ozeti gosterir; kaynak ozeti dogruysa bile LLM o kaynaktaki dogru maddeyi kullanmamis olabilir.
- `generation_modes` yapisal alan olarak `llm`, `rag`, `vt`, `kural` donebilir ama Slack'teki debug ozeti config'e baglidir.

Bu katmanlar safety net olarak kalabilir ama soru ozel bilgi duzeltmesi buraya gomulmemeli.

### Aktif legacy/runtime: Slack komut parser ve API profil zorunlulugu

Dosyalar:

- `src/slack/service.py`
- `src/slack/formatting.py`
- `src/api/query_flow.py`
- `src/api/profile_flow.py`
- `src/db/profile_context.py`

Ne yapiyor:

- Slack mesajlari once `help`, `login`, `verify`, `logout`, `query` olarak ayrilir.
- Slack context id DM'de `channel:user`, kanal/thread'de `channel:thread_ts` mantigiyla olusur.
- Slack girisli genel sorular profil zorunluluguna takilmayabilir; API endpoint ise anonim kullanicidan profil isteyebilir.
- API profil akisi ad soyad, ogrenci no, bolum, fakulte, ogrenci tipi/uyruk bilgisini kaydedebilir.
- Kayitli profil sonraki sorulara `student_department`, `student_faculty`, `student_type` olarak sizabilir.

Risk:

- Slack'te calisan akis API'de profil-onboarding cevabina takilabilir veya tersi olabilir.
- Thread/DM context id farki nedeniyle ayni kullanicinin iki farkli sohbet hafizasi olabilir.
- Profildeki bolum/fakulte acikca sorulan baska bolumu ezmemeli; bu ozellikle ders programi, ucret ve duyuru/etkinlik filtrelerinde kontrol edilmeli.
- `turk`, `uluslararasi`, `muhendislik fakultesi` gibi kisa cevaplar profil bilgisi mi, clarification cevabi mi, yeni konu mu ayristirilmelidir.

Yeni test yaparken Slack ile API davranisini ayni sanma. Hangi giris kanalinin kullanildigini, context id'yi ve profil/auth metadata'sini logdan dogrula.

### Flag arkasinda veya geri alinmis legacy/deneysel yapilar

Config ve dosyalar:

- `src/core/config.py`
- `src/capabilities/planner.py`
- `src/orchestrators/main.py`
- `src/agents/base.py`

Bilinen flag'ler:

- `settings.capability_planner.pre_route_enabled = False`
- `settings.llm.specialist_synthesis_enabled = False`
- `settings.rag.llm_evidence_selection_enabled = False`

Ne anlama gelir:

- Pre-route planner kodu duruyor ama varsayilan kapali. Yanlislikla acilirsa router + capability tek karar denemesi benzeri regresyonlar geri gelebilir.
- Specialist synthesis kodu duruyor ama varsayilan kapali. Acilirsa her specialist kendi LLM sentezini uretir; global final synthesis ile cift sentez/uyusmazlik riski olusur.
- LLM evidence selection kodu duruyor ama varsayilan kapali. Acilirsa chunk secimi LLM'e kayar; latency ve maliyet artar, ama bazi kaynak kacirma sorunlarini azaltabilir.

Bu flag'leri degistirirken once su sorulari cevapla:

```text
1. Bu flag hangi eski problemi cozmek icin kapatildi/acildi?
2. Slack golden akislarinda hangi regresyon olmustu?
3. Yeni telemetry ile shadow test yaptik mi?
4. Fallback var mi?
5. Maliyet/LLM cagri sayisi etkisi nedir?
```

### Data source ownership legacy karisikligi

Bazi veri aileleri hem VT'de hem RAG'da bulunabilir:

- Duyurular
- Etkinlikler
- Akademik takvim
- Ders programi / mufredat
- Harc/ucret tablolari
- Uluslararasi ogrenci belgeleri

Risk:

- VT'de net kayit varken RAG yanlis belge secebilir.
- RAG dogru mevzuat cevabi verirken VT "Bulunamadi" diyebilir.
- Duyuru sorusu ile policy sorusu ayni kelimeyi tasidigi icin source owner karisabilir.

Yeni mimari kararinda once source owner belirlenmeli:

```text
Bu soru icin birincil kaynak VT mi?
VT yoksa RAG fallback mi?
RAG birincilse hangi belge ailesi tercih edilmeli?
VT ve RAG celisirse hangisi kazanir?
Kaynak ozetinde kullanilmayan/yanlis source gosteriliyor mu?
```

### Yeni sohbette mutlaka tekrar calistirilacak legacy audit komutu

```powershell
rg -n "def _apply_routing_overrides|def _compute_routing_override|keyword_routing|pre_route_enabled|specialist_synthesis_enabled|llm_evidence_selection_enabled|force_llm_synthesis|build_evidence_packet_fallback_answer|ClaimGuard|answer_filter|query_normalization|missing_slots|CLARIFICATION|short_circuit|target_capability" src tests
```

Bu komutun sonucu okunmadan "legacy kalmadi" deme. Cikan her eslesmeyi su siniflardan birine ayir:

- Aktif ana karar katmani.
- Aktif safety/validation katmani.
- Aktif source ranking/evidence katmani.
- Flag arkasinda pasif deneysel katman.
- Sadece test/telemetry/artik iz.

## LLM Ana Karar Verici mi?

Kisa cevap: su anda tamamen degil.

Olmasi istenen uzun vadeli hedef:

- LLM semantik niyet, gerekli slot ve dogru capability/policy kararini versin.
- Deterministik katman sadece guvenlik, whitelist, kaynak varligi ve validation yapsin.
- Soru bazli "su kelime varsa su route" kararlar ana karar mekanizmasi olmasin.

Guncel gercek durum:

- Router LLM kullaniyor ama rule/policy override katmanlari hala var.
- Capability planner LLM kullaniyor ama router ana kararini degistirmiyor.
- Conversation follow-up LLM kullanabilir ama bazi deterministic filtreler ve topic kurallari vardir.
- Announcement/event ve bazi VT akislarinda LLM kararindan once veya sonra deterministic short-circuit bulunabilir.
- Specialist synthesis kapali oldugu icin bazi agent cevaplari LLM sentezi olmadan source-only/evidence olarak donebilir.
- Final/global sentez ve judge her durumda garanti degildir; risk/config/akis durumuna baglidir.

Yeni sohbette bu mutlaka dogrulanmali:

- "LLM ana karar verici olsun" hedefi hala isteniyor mu?
- Eger isteniyorsa hangi katmanlar shadow/fallback, hangileri ana karar olmali?
- Pre-route planner tekrar acilacaksa eski Slack regresyonlari icin once golden test kosulmali.
- Router ile capability tek LLM cagrisi tekrar denenmemeli; denenirse once shadow telemetry ile uyusma orani izlenmeli.

## Tum LLM Katmanlari ve Ne Yaptiklari

Bu sistemde potansiyel LLM cagri noktalarini tek tek bilmek cok onemli.

### 1. Conversation / Follow-up Resolver

Amac:

- Kisa takip sorularini onceki baglamla standalone hale getirmek.
- Ornek: `Kac AKTS?` -> `BIL203 Veri Yapilari dersi kac AKTS?`
- Ornek: `turk` -> onceki soru ogrenim ucreti ise `Turk ogrenci icin ... ucreti`

Dosyalar:

- `src/db/conversation_context.py`
- `src/llm/prompt_templates.py`
- `src/cache/conversation_cache.py`

Riskler:

- Bolum bilgisi cevaplari (`Bilgisayar Muhendisligi`) yeni konu sanilabilir veya onceki soruya baglanmayabilir.
- Ogrenci turu cevaplari (`turk`, `uluslararasi`) yanlis onceki finance/registration konusuna baglanabilir.
- Follow-up fazla eski konuya yapisirsa "CAP basvuru tarihi" yerine "harc odeme tarihi" gibi cevap gelebilir.
- Follow-up hic baglanmazsa gereksiz bolum/fakulte/ogrenci turu clarification sorulur.

Kontrol edilecek log/metadata:

- `original_query`
- `effective_query`
- `standalone_query`
- `is_follow_up`
- `used_context`
- `active_topic`
- `department_hints`
- `source_hints`

### 2. Router LLM

Amac:

- Departmanlari belirlemek.
- Task type ve intent alanlarini uretmek.
- Gerekirse canonical query uretmek.
- Missing slots uretmek.

Dosyalar:

- `src/routing/router.py`
- `src/routing/routing_policy.py`
- `src/llm/prompt_templates.py`

Router cikti alanlari:

- `departments`
- `strategy`: `DIRECT`, `PARALLEL`, `CLARIFICATION`, vb.
- `confidence`
- `task_type`
- `intent.primary_intent`
- `intent.target_capability`
- `intent.required_slots`
- `intent.missing_slots`
- `intent.canonical_query`

Riskler:

- LLM dogru departmani verse bile rule override sonucu degistirebilir.
- Missing slot gereksiz clarification'a neden olabilir.
- `academic_programs` ve `student_affairs` arasinda policy sorulari cok karisiyor.
- `finance` sadece ucret tutari olmali; harc borcu/policy sorularinda finance branch yanlis calisabilir.

### 3. Capability Planner LLM

Amac:

- Router sonrasinda, secili scope icinde whitelisted capability secmek.
- Parametreleri cikarmak.
- `answer_contract` ve `evidence_contract` uretmek.

Dosyalar:

- `src/capabilities/planner.py`
- `src/capabilities/models.py`
- `src/capabilities/registry.py`
- `src/capabilities/executor.py`

Artik yapmamasi gerekenler:

- Departman/routing karari vermemeli.
- Router'i bypass etmemeli.
- Routing'i sonradan degistirmemeli.

Riskler:

- Capability yanlis secilirse agent icinde RAG/policy yolu bozulabilir.
- Parametre daraltilirsa takvim gibi exact row matching kayit bulamayabilir.
- Records yoksa ham no-info cevabi kullaniciya kacabilir.

### 4. Query Expansion / Evidence Selection LLM

Durum:

- `settings.rag.llm_evidence_selection_enabled = False`
- Query expansion da her yerde aktif degil; config ve role ayarlarina bak.

Amac:

- Daha iyi kaynak secmek veya sorguyu genisletmek.

Risk:

- Ek maliyet ve latency.
- Yanlis expansion alakasiz kaynaklari yukari cikarabilir.

### 5. Specialist Synthesis LLM

Durum:

- `settings.llm.specialist_synthesis_enabled = False`
- Agent icinde `force_llm_synthesis=True` olsa bile global ayar kapaliysa specialist LLM calismayabilir.
- Testlerde eski davranis gerekiyorsa monkeypatch ile aciliyor.

Amac:

- Tek specialist kaynaklarini dogrudan dogal dile cevirmek.

Neden kapatildi:

- Specialist LLM + global final LLM iki kere sentez yapiyor, hem maliyet hem hata artiyor.
- Ana cevap ownership'i main/global senteze tasinmak istendi.

Risk:

- Specialist source-only cevap kullaniciya direkt giderse kaba/eksik gorunebilir.
- Final/global synthesis devreye girmeyen bazi akislarda cevap kalitesi dusebilir.
- Main orchestrator `final_answer_owner="main_orchestrator"` ve `specialist_response_mode="evidence_packet"` gonderirse `BaseSpecialistAgent` final cevap yazmak yerine evidence handoff cevabi uretir: `Kaynak bilgisi final cevap icin hazirlandi.` Bu normalde kullaniciya gitmemeli; global synthesis veya fallback evidence builder bunu nihai cevaba cevirmeli.
- Bu metin Slack'te gorunurse global synthesis/fallback/timeout/eligibility zincirinde problem vardir.

Cok onemli istisna:

- `LLM_SPECIALIST_SYNTHESIS_ENABLED=False` olsa bile `CurriculumAgent._build_capability_answer(...)`, `CAPABILITY_PLANNER_SYNTHESIZE_WITH_LLM=True` ise capability records'u dogal dile cevirmek icin LLM cagirabilir.
- Bu cagrida `model_role="specialist_synthesis"` kullanilir, ama klasik `BaseSpecialistAgent._generate_answer(...)` path'indeki specialist synthesis flag'inden bagimsizdir.
- Yani "specialist synthesis kapali, hic specialist_synthesis model_role cagrisi olmaz" yanlistir.
- Ders programi/mufredat/course detail cevaplarinda LLM maliyeti veya uydurma davranisi araniyorsa `CAPABILITY_PLANNER_SYNTHESIZE_WITH_LLM` de kontrol edilmeli.

### 6. Main / Global Final Synthesis LLM

Amac:

- Department cevaplarini final user-facing cevaba cevirmek.
- Sadece cok departmanli cevaplarda degil, anlamli source/db_data olan tek departman cevaplarinda da calisabilir.
- `should_use_global_synthesis(...)` contact query degilse, meaningful response varsa, kaynak/db_data varsa ve tum meaningful response'lar kaynaksiz degilse true donebilir.
- Announcement/event formatli cevaplar ve contact istekleri gibi bazi ozel path'ler global synthesis disinda kalabilir.
- Global synthesis prompt'u `evidence_packet`, selected sources, extracted facts ve answer summary kullanir; prompta ne girdigi kaynak ozetiyle bire bir ayni olmak zorunda degildir.
- Global synthesis basarisiz olursa `build_evidence_packet_fallback_answer(...)` gibi fallback'ler devreye girebilir; bu fallback kaynak cumlelerinden kisa bir cevap toplar ama LLM kadar iyi sentez yapmaz.
- Main judge sadece `settings.llm.main_judge_enabled=True` ve global synthesis kullanildiysa veya cok departmanli/riskli durum varsa calisir; her cevap judge'dan gecmez.
- Cok departmanli cevaplarda gereksiz branch'leri filtrelemek.
- Kaynaklara sadik, kisa ve net cevap uretmek.

Risk:

- Kaynak paketi eksikse dogru cevabi uretemez.
- Foreign token sorunu burada da ortaya cikabilir.
- "Kaynakta yok" demesi gereken yerde uydurabilir veya tersine kaynakta olan bilgiyi goremez.

### 7. Judge LLM

Amac:

- Riskli cevaplari denetlemek.
- Gerekirse rewrite/retrieve-again/clarification isteyebilmek.

Durum:

- Config ve risk detection'a bagli; her cevapta calismayabilir.
- Maksimum retry/loop siniri korunmali.

Risk:

- Ek maliyet.
- Judge yanlis retry veya gereksiz clarification isteyebilir.

### 8. Final Refinement / Answer Filter

Amac:

- Bozuk token, ic talimat sizintisi, yarim cumle gibi problemleri temizlemek.

Dosyalar:

- `src/quality/answer_filter.py`
- `src/orchestrators/response_utils.py`
- `src/quality/claim_guard.py`

Risk:

- Regex/temizleme tek basina model problemini cozmez.
- Cok agresif temizlik anlam kaybina yol acabilir.

## Clarification ve Missing Slot Sorunlari

Bu alan en riskli bolgelerden biri. Yeni sohbet bunu ozellikle incelemeli.

Gozlenen problem tipleri:

1. Gereksiz bolum/fakulte sorma
   - Ornek: `Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?`
   - Bu soru icin fakulte/bolum cogu zaman zorunlu degildir.
   - Yanlis missing slot sonucunda bot `Fakulte, bolum veya program belirtir misiniz?` diyebilir.

2. Gereksiz ogrenci turu sorma
   - Ucret/harc tutari icin Turk/uluslararasi gerekli olabilir.
   - Ama policy/prosedur sorularinda her zaman gerekli degil.

3. Ogrenci turu follow-up cevaplarinin kacmasi
   - `Muzik ogretmenligi ucreti ne kadar?` -> `turk`
   - Burada `turk`, onceki finance sorusuna baglanmali.
   - Ama onceki konu finance degilse `turk` tek basina yeni konu sayilmamali.

4. Bolum cevabinin yeni konu sayilmasi
   - Bot bolum sorarsa `Bilgisayar Muhendisligi` cevabi onceki soruya slot olarak baglanmali.
   - Ama sonraki yeni soru baska bir konuysa bu bolum cevabi onceki asil soru yerine gecmemeli.
   - Dogru yaklasim: slot cevabi conversation state'te tutulur ama onceki asil intent kaybolmaz.

5. Program degisimi
   - `Bilgisayar muhendisliginde var mi?` onceki ders adini tasimali ama programi degistirmeli.
   - Yanlis: `Elektrik-Elektronik icin Bilgisayar Muhendisligi 5. yariyil...`
   - Dogru: yeni program + onceki soru nesnesi.

6. Short follow-up insufficient context
   - `Kac AKTS?`, `On kosulu ne?`, `Basvuru tarihleri ne?`
   - Onceki course/application/policy baglami yoksa clarification gerekir.
   - Varsa dogrudan cozumlenmeli.

Ilgili dosyalar:

- `src/db/conversation_context.py`
- `src/llm/prompt_templates.py`
- `src/orchestrators/main.py`
- `src/routing/router.py`

Yeni calismada yapilmasi gereken:

- Clarification kararlarina telemetry ekle veya mevcut loglari incele.
- Hangi slotun neden eksik sayildigini cevap/logda izlenebilir yap.
- Slot cevabi ile yeni konu ayrimini test et.
- Ogrenci turu, bolum/program, application_type, course_code slotlari icin golden flow yaz.

## Eski Statik Kararlar ve Sizma Riski

Sistemde "LLM karar versin" hedefi olsa da asagidaki statik/deterministik kararlar hala ana akisa sizabilir:

- Router rule overrides.
- `routing_policy.py` marker listeleri.
- Department keyword routing.
- Announcement/event short-circuit gate.
- Registration timing/calendar helpers.
- Finance requested unit/student type extraction.
- Curriculum program/course alias extraction.
- ClaimGuard/answer_filter regex duzeltmeleri.
- RAG search planner source bias / department scoring.
- Conversation context topic/department carry-over filtreleri.

Bu kararlar tamamen kotu degil; guvenlik ve veri dogrulama icin bazilari gerekli. Ama yeni davranis tasarlarken sunu ayir:

- Guvenlik/validation guard'i: Kalabilir.
- Ana semantik karar: Mumkunse LLM veya plan-aware karar olmali.
- Soru ozel cevap/route hack'i: Kacin.

## Yeni Sohbette Ilk Yapilacak Audit

Yeni bir kapsamli iyilestirme sohbetinde once su audit yapilmali:

```powershell
rg -n "short_circuit|keyword_routing|missing_slots|CLARIFICATION|target_capability|capability_planner|force_llm_synthesis|specialist_synthesis_enabled|llm_evidence_selection_enabled" src tests
```

Sonra su sorular cevaplanmali:

- Router LLM cikti verdikten sonra hangi policy override'lar calisiyor?
- Capability planner hangi durumlarda calisiyor, hangi durumlarda apply oluyor?
- Capability planner records yoksa fallback garanti mi?
- Specialist synthesis kapali oldugu icin hangi akislarda source-only cevap kullaniciya direkt gidiyor?
- Main/global synthesis hangi durumlarda devreye girmiyor?
- Clarification hangi katmanda uretiliyor: conversation, router, missing_slots, agent, finance?
- Department keyword routing hangi agent'i seciyor?
- RAG source bias hangi belgeleri yukari cikariyor?

Bu audit tamamlanmadan yeni statik fix ekleme.

## LLM Cagri Politikasi

Guncel niyet: gereksiz LLM cagrisini azaltmak ama routing guvenligini bozmak degil.

Varsayilan akista:

1. Router LLM cagrisi calisir.
2. Capability planner LLM cagrisi router sonrasinda calisabilir.
3. Specialist LLM sentezi varsayilan olarak kapali.
4. Global/main final synthesis ve judge/quality katmanlari duruma gore calisir.

Config:

- `settings.llm.specialist_synthesis_enabled = False`
- `settings.rag.llm_evidence_selection_enabled = False`
- `settings.capability_planner.pre_route_enabled = False`

Specialist ajanlar kaynak/evidence packet veya source-only cevap hazirlayabilir; son kullanici cevabini ana/global sentez toparlar. Eski testlerde specialist LLM bekleniyorsa test icinde `specialist_synthesis_enabled=True` ile legacy mod acilir.

Guncel cagri sayisi icin dikkat:

- `CONVERSATION_REWRITE_WITH_LLM=true` ise follow-up veya conversation rewrite icin ek LLM cagrisi olabilir.
- `LLM_QUERY_NORMALIZATION_ENABLED=true` ise query normalization ana akisi etkileyebilir; bu router'dan ayri bir semantik sinyal katmanidir.
- Router LLM ana departman/task/intent karari icin calisir; rule fallback/override hala vardir.
- Capability planner LLM router sonrasi calisir; `mode=on` ise scope genis oldugu icin her soru icin ek cagrinin maliyeti olabilir.
- Specialist synthesis kapali olsa bile final/global synthesis LLM cagrisi beklenebilir.
- Curriculum capability synthesis aciksa (`CAPABILITY_PLANNER_SYNTHESIZE_WITH_LLM=true`) curriculum capability records icin ek LLM cagrisi olabilir; bu klasik specialist synthesis flag'inden bagimsizdir.
- Main judge aciksa final cevaptan sonra ek judge LLM cagrisi olabilir.
- RAG query expansion ve LLM evidence selection kapaliysa bu iki ekstra LLM cagrisi beklenmez; acilirsa maliyet artar.
- Announcement/event sync islemleri canli soru aninda degil sync scriptleri sirasinda LLM summary/refiner cagrisi yapabilir; runtime soru maliyetiyle karistirma.

## Model Bilgisi

`.env` guncel durumda:

- Primary provider: `openai_compatible`
- Base URL: Groq OpenAI-compatible endpoint
- Ana model: `llama-3.3-70b-versatile`
- Routing/conversation/query expansion/evidence/final/specialist/global rolleri de ana model olarak bunu kullanacak sekilde ayarli.
- Fallback provider: `google_ai`
- Fallback model: `gemini-3-flash-preview`

Foreign token sorunu (`beberapa`, `moeglich`, `tanggal`, vb.) buyuk olasilikla model davranisiyla ilgili. Regex temizligi var ama asil cozum daha stabil final/global model denemesi olabilir.

## Capability Sistemi

LLM SQL yazmaz. Planner sadece whitelisted capability JSON'u uretir. Executor deterministik calisir.

Onemli capabilities:

- `calendar.academic_date`
- `finance.tuition_fee`
- `student_affairs.policy_lookup`
- `international.policy_lookup`
- `curriculum.semester_courses`
- `schedule.weekly_program`
- `course.exists_in_program`
- `course.prerequisites`
- `course.detail`
- `announcement.search`
- `event.search`

Capability planner sonucunda kayit yoksa, kullaniciya ham `Bulunamadi` basma. Mumkunse legacy/RAG fallback'e dus.

Capability mimarisinin kritik ayrintilari:

- Registry: `src/capabilities/registry.py`
- Planner: `src/capabilities/planner.py`
- Executor dispatcher: `src/capabilities/executor.py`
- Ortak modeller: `src/capabilities/models.py`
- Policy executor: `src/capabilities/policy_executor.py`

Planner davranisi:

- `plan_capability_action(...)` kendisine verilen departman/scope listesinden kullanilabilir capability listesini cikarir.
- `MainOrchestrator._maybe_plan_capability(...)` icinde `mode in {"on", "shadow"}` ise planner'a `CAPABILITY_PLANNER_SCOPE` icindeki tum capability aileleri verilir. `pilot` modunda ise router sonucuyla scope kesistirilir ve daha dar calisir.
- LLM cagrisi `model_role="routing"` ve `llm_profile="fast"` ile yapilir. Bu nedenle capability planner kalitesi routing model/profile kalitesiyle yakindan iliskilidir.
- Planner promptu JSON-only ister ama response icinden `{...}` parse fallback'i vardir; invalid JSON olursa planner yok sayilir.
- `CapabilityAction.departments` alani modelde hala vardir ama guncel prompt bunu istemez. Eski payload uyumlulugu icin kalmis olabilir.
- Validation missing param bulursa action tamamen atilmayabilir; `missing_params` action'a yazilir. Sonraki katmanin bunu nasil kullandigi ayrica kontrol edilmelidir.

Cok onemli risk:

- Planner promptunda cok sayida ornek vardir. Bunlar dogrudan cevap gommez ama semantik karari, `topic`, `must_answer`, `preferred_sources`, `avoid_sources` alanlarini ciddi sekilde yonlendirebilir.
- Bu ornekler soru bazli hack'e donusebilir. Ozellikle `tek ders`, `yaz okulu`, `ogrenci toplulugu`, `uluslararasi kayit belgeleri`, `akademik takvim` gibi ornekler genel davranisi etkiler.
- Kodda su anda bu ornekler gercekten vardir: `student_community_closure`, `student_community_advisor_requirement`, `international_registration_documents`, `single_exam_eligibility`, `summer_school_solution`, takvim tarihleri.
- Bu ornekler answer_contract/evidence_contract urettigi icin retrieval siralamasini ve judge davranisini da etkiler. "LLM serbest karar verdi" diye yorumlama; prompt bias'i aktif karar mekanizmasinin parcasidir.
- Yeni sorunlarda once "registry description mu yanlis, planner prompt ornegi mi fazla spesifik, executor mu yetersiz, yoksa agent/RAG mi yanlis?" diye ayir.
- Prompt ornegi eklemek cevap gommek degildir ama yine de statik karar bias'i ekler. Bunu ucuz fix olarak kullanma; gerekirse capability description ve evidence contract mantigini genellestir.

Executor davranisi:

- `EXECUTOR_MAP` whitelist disinda fonksiyon calistirmaz.
- Unknown/invalid capability `fallback_allowed=True` ile doner.
- Missing required params durumunda `fallback_allowed` bazen false olabilir; bu kullaniciya clarification mi yoksa fallback mi gidecek sorusunu etkiler.
- Deterministik VT executor'lari records dondurur; policy executor'lari genelde records dondurmaz, sadece metadata/plan hazirlar.
- `student_affairs.policy_lookup` ve `international.policy_lookup` SQL/RAG sorgusunu burada yapmaz. Bunlar ilgili specialist agent'a `policy_lookup_plan_ready` metadata'si tasir.
- Policy executor success + `records=[]` beklenen davranistir. Asil retrieval `RegistrationAgent._prepare_policy_lookup_task(...)`, `InternationalAgent` plan-aware hazirliklari ve `BaseSpecialistAgent.handle_department_task(...)` icindeki RAG aramasinda olur.
- Bu nedenle policy sorularinda "executor kayit dondurmedi" diye hata arama; onun yerine `retrieval_query`, `conversation_source_refs`, `answer_contract`, `evidence_contract`, `plan_decision` metadata'si agent'a tasinmis mi kontrol et.
- Deterministik capability tarafinda ise `records=[]` cok daha kritik sinyaldir: takvim, ders programi, course detail, ucret gibi alanlarda no-record ya veri eksigi ya parametre/normalize hatasi ya da fallback tasarimi sorunudur.

Deterministik capability fallback farki:

- Tum deterministic capability'ler no-record durumunda ayni davranmaz.
- `calendar.academic_date` Student Affairs/Registration tarafinda bazi akislarla legacy `build_general_exam_calendar_answer(...)` veya RAG'e dusme sansi bulabilir.
- Curriculum capability path'i daha kati davranir:
  - `CurriculumAgent.handle_department_task(...)` icinde `_try_handle_capability_plan(...)` local prerequisite/title/schedule helper'larindan once calisir.
  - `execute_capability_action(...)` success donerse `CurriculumAgent` cogunlukla direkt `DepartmentResponse(generation_mode="vt")` uretir.
  - `course.exists_in_program`, `course.detail`, `course.prerequisites`, `curriculum.semester_courses`, `schedule.weekly_program` executor'lari no-record durumunda genelde `authoritative_no_records=True` ve `fallback_allowed=False` doner.
  - `CurriculumAgent._build_capability_answer(...)` records bos ve `authoritative_no_records=True` ise LLM sentezine gitmeden deterministic "kayit bulunamadi" metnini doner.
- Bu yuzden ders/mufredat/ders programi sorularinda "Bulunamadi" cevabi sadece veri yok anlamina gelmeyebilir; program normalize hatasi, term/class_year filtresi, follow-up context kaybi veya seed/parse eksigi de olabilir.
- Curriculum no-record cevaplarinda RAG fallback otomatik varsayilmamali. Bu tasarim alakasiz PDF cevabini azaltir ama yanlis dar parametrelerde dogru bilgiyi kacirabilir.

Curriculum no-record denetim sorulari:

```text
1. Planner hangi capability'yi secti?
2. Params icinde program/course/semester/class_year/term dogru mu?
3. Program degisiminde eski program uzerine mi ekledi?
4. Executor raw_count/filtered_count metadata'si ne diyor?
5. `authoritative_no_records=True` yuzunden RAG fallback kapanmis mi?
6. Seed/parse DB'de ilgili program/donem gercekten var mi?
```

Bu ayrim cok onemli:

```text
Deterministik capability = executor gercek kayit dondurur.
Policy capability = executor yalnizca plan/contract metadata dondurur; asil RAG agent icinde olur.
```

Bu yuzden policy capability icin "executor success ama records=[]" hata degildir. Ancak deterministik capability icin records bos ise no-record/fallback/clarification davranisi ayrica tasarlanmalidir.

### Policy Lookup Metadata Farki: Student Affairs vs International

Iki policy capability ayni tipte gorunse de agent hazirliklari bire bir ayni degil.

`RegistrationAgent._prepare_policy_lookup_task(...)`:

- `student_affairs.policy_lookup` action'ini okur.
- `params.query`, `topic`, `question_type`, `answer_contract.must_answer`, `preferred_sources` alanlarini birlestirip genis `retrieval_query` olusturur.
- `preferred_sources` degerlerini `conversation_source_refs` icine ekler.
- `force_llm_synthesis=True`, `policy_lookup`, `plan_decision`, `answer_contract`, `evidence_contract` metadata'si tasir.

`InternationalAgent._prepare_policy_lookup_task(...)`:

- `international.policy_lookup` action'ini okur.
- `preferred_sources` degerlerini `conversation_source_refs` icine ekler.
- `retrieval_query` su anda temel olarak `params.query` veya kullanici sorusudur; Student Affairs kadar topic/must_answer ile genisletilmez.
- `force_llm_synthesis=True`, `policy_lookup`, `plan_decision`, `answer_contract`, `evidence_contract` metadata'si tasir.

Risk:

- Uluslararasi kayit belgelerinde dogru kaynak ailesi secilse bile retrieval_query yeterince zengin degilse konukevi/ozel ogrenci gibi kaynaklar yine yukari cikabilir.
- Student policy tarafinda zengin retrieval query daha iyi ama prompt bias'i daha guclu olabilir.
- Bu iki agent davranisi "policy lookup ayni calisiyor" diye varsayilmamali.

### Student Life / Ogrenci Toplulugu Ozel Katmani

Dosya:

- `src/agents/student/student_life_agent.py`

Bu ajan genel `BaseSpecialistAgent` gibi gorunse de icinde aktif ozel mantiklar vardir.

Ogrenci toplulugu sorulari:

- Query marker'lari: `ogrenci toplulug`, `topluluk`, `kulup`, `sksdb`, `etkinlik kurulu`, `uyelik`, `uye`.
- Bu marker'lar gelirse `_search_top_k(...)` 12'ye cikar.
- `_filter_results_for_answer(...)` once ogrenci toplulugu kaynaklarini secer.
- Pozitif kaynak marker'lari: `ogrenci_topluluk`, `topluluklari_yonergesi`, `etkinlik kurulu`, `sksdb`, `mesleki topluluk`, `sosyal topluluk`, `akademik danisman`.
- Negatif kaynak marker'lari: `guvenlik`, `ic denetim`, `risk ve firsat`, `egitim komisyonu`, `isyeri staj`, `staj sozlesmesi`.

Risk:

- Bu filtreler dogru belge ailesini yukari tasimak icin yararli ama hala keyword tabanlidir.
- "Toplulugun kapatilmasi" gibi sorularda dogru belge secilse bile madde bloklari eksik parcalanirsa LLM sadece 1-2 madde sayabilir.
- Student community prompt/capability ornekleri + StudentLife filtreleri ust uste binince bir soru fazla spesifik bias alabilir.
- Ilk Slack cevabinda `Sorunuzun hangi alana ait oldugunu belirleyemedim` cikmasi router/department routing asamasinda kalmis olabilir; StudentLife agent'a gelmeden cevap kesilmis olabilir.

Kimlik karti kaybi:

- `_is_lost_identity_card_query(...)` kimlik/kart + kayip/kaybett/kaybol marker'lariyla calisir.
- Bu soru icin `_should_force_llm_synthesis(...)` true olabilir.
- `_build_source_only_answer(...)` icinde kimlik kaybi icin sabit, kaynak-temelli bir cevap metni vardir.

Risk:

- Bu cevap kaynakta olmayan bilgiyi uydurmak icin degil, belirli form/dekont bilgisini source-only modda temiz anlatmak icin yazilmis legacy/special-case bir katmandir.
- Yine de "hardcoded answer var mi?" denetiminde bu dosya mutlaka kontrol edilmeli.

StudentLife hata analiz sirasinda:

```text
1. Router student_affairs secti mi?
2. Department keyword routing `student_life_agent` secti mi?
3. StudentLife top-k 12 uygulandi mi?
4. Filtre sonrasi kac `ogrenci_topluluklari_yonergesi` chunk'i kaldi?
5. Chunk'lar tam madde/blok mu, yoksa kosullar parcali mi?
6. Global synthesis/ClaimGuard cevabi kisaltti veya degistirdi mi?
```

## Veri Kaynaklari, Kaynak Sahipligi ve VT/RAG Karmasasi

Bu sistemde en buyuk pratik sorunlardan biri ayni bilginin birden fazla yerde bulunmasi veya bulunmasi gerekirken yanlis katmandan aranmasidir. Yeni sohbette bu konu ozellikle detayli incelenmeli.

Kaynak tipleri:

1. PostgreSQL / VT structured tablolar
   - Ders programi slotlari.
   - Mufredat / ders plani.
   - Ders onkosulu / AKTS gibi course detail kayitlari.
   - Ogrenim ucreti katalogu / seed verisi.
   - Duyuru kayitlari.
   - Etkinlik kayitlari.
   - Bazi akademik takvim structured parse sonuclari.

2. RAG / Chroma dokuman parcalari
   - Yonetmelikler.
   - Yonergeler.
   - SSS metinleri.
   - Akademik takvim PDF parcalari.
   - Ders programi PDF parcalari.
   - Duyuru/haber icerikleri eger indekslenmisse.
   - Basvuru ilanlari ve PDF duyuru metinleri.

3. Local metadata / JSON kataloglari
   - `data/metadata/*`
   - `data/curriculum/*_seed.json`
   - Tuition fee kataloglari.
   - Announcement/event preset ve alias kaynaklari.

4. Conversation/cache/runtime state
   - Redis question cache.
   - Conversation cache.
   - Follow-up state.
   - Auth/session/OTP gibi gecici veriler.

5. PDF/raw dosyadan runtime parse
   - Akademik takvim gibi bazi durumlarda PDF direkt okunup satir parse ediliyor.

### Hangi Kaynak Authoritative?

Genel kural:

- Structured VT varsa once VT kullan.
- VT kaydi kesin ve guncelse RAG ayni konuda sadece destekleyici olmali.
- Policy/mevzuat/prosedur sorularinda resmi yonerge/yonetmelik RAG kaynagi authoritative olabilir.
- Duyuru/etkinlikte guncellik ve link icin VT kaydi authoritative olabilir; uzun metin/icerik ozeti icin RAG veya kaydin detail content'i gerekebilir.
- VT bos ise "RAG'a dus" her zaman dogru degil. Bazen VT boslugu gercek veri yok anlamina gelir; bazen de seed/sync eksikligi anlamina gelir.

Yeni sorun analizinde sorulacak ilk kaynak sorulari:

```text
Bu bilgi structured VT'de var mi?
Varsa hangi tablo/helper uzerinden okunuyor?
Ayni bilgi RAG indeksinde de var mi?
VT ve RAG birbirini celisiyor mu?
Kaynak guncelligi hangisinde daha iyi?
Agent hangi kaynagi secmis?
Final cevap kaynaklardan hangisini kullanmis?
```

### Duyuru Kaynaklari Ozellikle Karmasik

Duyurularda ayni bilgi birkac yerde bulunabilir:

- `announcements` VT kaydi: baslik, tarih, URL, birim/fakulte/unit, ozet/detail.
- RAG dokuman parcasi: duyuru metni veya PDF/HTML icerigi indekslenmisse.
- Announcement agent: VT search/list/latest mantigi.
- General RAG: "tek ders", "basvuru", "sinav programi" gibi kelimelerle duyuru PDF'lerini veya eski duyurulari getirebilir.

Riskler:

- Prosedur sorusu duyuru search'e kacarsa kullaniciya duyuru listesi gelir.
- Duyuru sorusu RAG'a kalirsa eski veya alakasiz PDF parcasi cevaplanabilir.
- VT latest fallback konu disi en son duyuruyu dondurebilir.
- Unit/faculty alias eksikse VT'de duyuru olsa bile bulunamayabilir.
- Duyuru VT'de var ama RAG'da yoksa uzun metin ozeti yetersiz kalabilir.
- RAG'da eski duyuru var, VT'de yeni duyuru var ise guncellik problemi olur.

Dogru yon:

- Kullanici acikca `duyuru/haber/ilan/guncel` diyorsa announcement VT search oncelikli.
- Kullanici policy/prosedur soruyorsa duyuru sadece ek bilgi olabilir, ana cevap yonerge/SSS/RAG veya policy lookup olmali.
- `tek ders sinav tarihi` gibi tarihli, duyuruya dayali sorularda announcement search mantikli olabilir.
- `Hic almadigim dersten tek derse girebilir miyim?` gibi uygunluk/policy sorusunda duyuru listesi yanlis.

Ilgili dosyalar:

- `src/agents/announcement/agent.py`
- `src/orchestrators/announcement_utils.py`
- `src/db/announcements.py`
- `src/orchestrators/main.py`
- `scripts/sync_announcements.py`
- `data/metadata/*announcement*`

### Etkinlik Kaynaklari

Etkinlikler de duyuruya benzer ama ayri tutulmali:

- `events` VT kaydi tarih/saat/lokasyon/link icin oncelikli.
- Event RAG veya HTML detail varsa icerik ozeti destekleyici olabilir.
- `bugunku etkinlik`, `yaklasan seminer`, `konferans var mi` gibi sorular VT/event agent'a gitmeli.
- Akademik/prosedur sorulari "etkinlik" kelimesi gecmiyorsa event'e kacmamali.

Ilgili dosyalar:

- `src/agents/event/agent.py`
- `src/orchestrators/event_utils.py`
- `src/db/events.py`
- `scripts/sync_events.py`

### Akademik Takvim Kaynaklari

Akademik takvim hem RAG'da PDF parcasi olarak bulunabilir hem de runtime structured parse ile okunabilir.

Gozlenen sorun:

- RAG bazen takvim PDF'ini buluyor ama LLM satirdaki tarihi cikaramiyor.
- Capability/VT bazen parametre daralmasi yuzunden kayit bulamiyordu.

Dogru yon:

- Ders baslama/bitis, final, butunleme, not giris gibi takvim satirlarinda structured parse tercih edilmeli.
- PDF satirinda lisans/onlisans ayrimi yoksa "genel akademik takvim" diye ifade edilmeli; ayrim uydurulmamalidir.
- Structured parse kayit bulamazsa ham `Bulunamadi` yerine fallback veya temkinli cevap.

### Ders Programi / Mufredat / Course Detail

Bu alanlarda structured VT authoritative olmali.

- Ders programi: `course_schedule_slots`
- Mufredat/yariyil dersleri: courses/curriculum seed tablolari
- Onkosul/AKTS: course detail / prerequisites tablolari

Riskler:

- RAG ders programi PDF parcasi cevap olarak kullanilirsa sinif/bolum/donem karisabilir.
- VT'de kayit varken RAG alakasiz bolum PDF'i getirebilir.
- Program alias normalize edilmezse bolum bulunamaz.
- Program degisimi follow-up'ta eski programla birlesebilir.

Dogru yon:

- VT varsa VT cevap.
- VT yoksa kontrollu no-info; RAG'e dusmeden once bunun gercekten istenip istenmedigi degerlendirilmeli.
- Ders programi RAG'i sadece veri eksikligi analizi veya kaynak destek icin kullanilmali, ana cevap olarak degil.

### Ogrenim Ucreti / Harc

Ogrenim ucreti tutari structured katalog/VT'den gelmeli.

Riskler:

- PDF katalogda var ama Postgres seed stale olabilir.
- Program/fakulte alias eksikse kayit bulunamayabilir.
- Ogrenci turu net degilse tutar yanlis olabilir.
- Harc borcu/policy sorusu ucret tutari capability'sine kacabilir.

Dogru yon:

- Tutar sorusu: finance VT/katalog.
- Politika/prosedur/borc uygunlugu: RAG/policy lookup.
- Turk/uluslararasi clarification yalniz tutar icin gerekliyse sorulmali.

Finance capability/agent ayrintisi:

- `finance.tuition_fee` capability sadece acik tutar sorulari icin tasarlanmistir.
- `src/capabilities/finance_executor.py` icinde `_is_explicit_fee_amount_query(...)` tutar marker'i arar: `ne kadar`, `kac tl`, `tutar`, `ucret`, `ogrenim ucreti`, `katki payi`, `donem/yillik ucret`.
- Ayni executor policy/prosedur marker'lari gorurse capability'den geri cekilir: `basvuru`, `sart`, `kosul`, `nasil`, `hangi banka`, `odeme yontemi`, `olsaydi/olursam`, `gerekir mi`, `odenmezse`, `iade`, `muafiyet`, `burs`.
- Bu geri cekilme `fallback_allowed=True` ile RAG/policy yoluna sans vermek icindir.
- `student_type` veya `unit_name` eksikse executor `missing_params` + `fallback_allowed=False` donebilir; bu durumda clarification davranisi query_policy/finance agent tarafindan kontrol edilmeli.
- `TuitionAgent` once kisisel harc sorgusunu auth ile ayirir, sonra capability planini dener, sonra `needs_fee_context_clarification(...)` ile Turk/uluslararasi + birim sorabilir.
- Profildeki `student_type` ve `student_faculty/student_department` generic ucret sorularinda kullanilir; kullanici acikca baska birim veya ogrenci turu yazarsa profil onu ezmemeli.

Finance hata analizinde:

```text
1. Soru tutar mi, policy/prosedur mu?
2. Capability `finance.tuition_fee` secildiyse query param'i tutar marker'i iceriyor mu?
3. Student type explicit mi, profilden mi geldi, yoksa missing mi?
4. Unit/faculty alias katalogda nasil normalize edildi?
5. Executor not_found mu dondu, yoksa agent clarification mi sordu?
6. RAG'e dustuyse ucret tablosu mu yoksa harc yonergesi/SSS mi geldi?
```

### International Kaynaklari

Uluslararasi ogrenci kayit/basvuru sorularinda genel student affairs veya konukevi kaynaklari yanlis yukari cikabiliyor.

Dogru kaynak ailesi:

- uluslararasi ogrenci yonergesi
- uluslararasi ogrenci kabul/basvuru dokumanlari
- kayit/evrak teslim belgeleri

Kacinilacak kaynaklar:

- konukevi
- ozel ogrenci
- yemek bursu
- pedagojik formasyon
- konu disi fakulte yonergeleri

Bu alan icin `international.policy_lookup` vardir, ama router ve retrieval kaynak secimi yine dogrulanmali.

### Student Affairs Policy Kaynaklari

Tek ders, yaz okulu, ek AKTS, mezuniyet, ders alma, CAP gibi policy sorularinda:

- RAG kaynaklari onemlidir.
- `student_affairs.policy_lookup` plan metadata'si retrieval'i zenginlestirir.
- Cevap statik gomulmez.

Risk:

- Top-k azsa dogru madde kacabilir.
- Kaynak ayni belgenin yanlis maddesinden gelebilir.
- LLM "kaynak bilgisi final cevap icin hazirlandi" gibi ic metni cevap olarak basabilir; bu LLM timeout/fallback veya synthesis kapali akisa isaret edebilir.

### Kaynak Secimi Icin Genel Tasarim Notu

Ideal uzun vadeli tasarim:

```text
Planner/Router: Bilgi turunu belirler.
Source Resolver: Bu bilgi turu icin authoritative kaynak ailesini secer.
Executor/Retriever: Sadece o kaynak ailesinden veri getirir.
Evidence Packager: Tam madde/bloklari koruyarak LLM'e verir.
Final LLM: Kaynaklardan cevaplar.
Judge/Guard: Plan + evidence + answer uyumunu denetler.
```

Su an bu ayrim tam oturmus degil. Bazi kararlar agent icinde, bazi kararlar router'da, bazi kararlar RAG search planner'da, bazi kararlar capability planner'da. Yeni sohbette bu mimari sadeleme ana hedeflerden biri olabilir.

## Aktif Olmayan / Geri Alinan / Kapatilan Kararlar

Bunlari bilmek onemli, cunku kodda izleri kalabilir.

1. Router + capability tek LLM karar denemesi
   - Geri alindi.
   - Sebep: Slack canli testlerinde route kararsizligi ve `Bulunamadi` gibi VT no-record cevaplarinin kullaniciya kacmasi.
   - Guncel durum: Router ana karar; planner routing'i ezmez.

2. Pre-route capability planner
   - Varsayilan kapali: `pre_route_enabled=False`.
   - Sebep: Capability planner'in department/routing karari uretmesi ana router'i bypass ediyordu.
   - Kodda helper'lar kalabilir; aktif sanma.

3. Planner promptunda `departments` uretme
   - Prompttan kaldirildi.
   - Sebep: Planner route sahibi degil.
   - Modelde parse alani kalabilir; backward compatibility.

4. Specialist LLM synthesis default
   - Kapali: `specialist_synthesis_enabled=False`.
   - Sebep: Specialist LLM + global LLM cift sentez maliyeti ve hata artisi.
   - Risk: Main/global synthesis devreye girmeyen yollarda source-only cevap gorulebilir.

5. LLM evidence selector default
   - Kapali: `llm_evidence_selection_enabled=False`.
   - Sebep: Ek LLM maliyeti ve latency.
   - Risk: Evidence secimi daha cok deterministic ranking/filter kalitesine bagli.

6. Soru bazli statik cevap ekleme
   - Bilerek tercih edilmiyor.
   - Sebep: Her yeni soru icin patch sistemi kirilganlastiriyor.
   - Dogru cozum: routing, source ownership, retrieval, evidence packing veya judge duzeltmesi.

7. Duyuru/event'i her basvuru/tarih sorusunda kullanma
   - Dogru degil.
   - Sadece acik duyuru/etkinlik niyetinde veya gercekten tarihli duyuru araniyorsa kullanilmali.

8. RAG'i her VT miss durumunda otomatik ana cevap yapmak
   - Her zaman dogru degil.
   - Ders programi/mufredat gibi structured alanlarda VT miss gercek veri yok veya seed eksik olabilir; RAG alakasiz belge getirebilir.

## Kaynak Sorunlari Icin Debug Sirasi

Bir cevap yanlis kaynak kullaniyorsa su sirayla ilerle:

```text
1. Soru hangi bilgi turu? (VT, RAG policy, duyuru, etkinlik, takvim, finans tutari)
2. Bu bilgi icin authoritative kaynak ne olmali?
3. Router hangi departmani secmis?
4. Capability planner hangi capability'yi secmis?
5. Executor records donmus mu?
6. RAG hangi koleksiyon/kaynaklardan aramis?
7. Top-k icinde dogru belge var mi?
8. Evidence packager dogru madde/bloklari korumus mu?
9. Final LLM dogru evidence'i kullanmis mi?
10. Judge/claim_guard cevabi degistirmis mi?
11. Cache/eski container etkisi olabilir mi?
```

Bu siralama atlanirsa genelde yanlis yere patch atiliyor.

## Auth, Profil, Cache ve Runtime State Katmanlari

Kaynak dogru olsa bile cevap yanlis cikabilir; cunku profil/auth/cache state sorguyu veya cevabi degistirebilir.

### Auth / OTP / Session

Ilgili dosyalar:

- `src/db/auth.py`
- `src/db/auth_models.py`
- `src/api/profile_flow.py`
- `src/slack/*` varsa Slack auth baglanti katmani

Riskler:

- Logout sonrasi eski verification session aktif kalabilir.
- Slack user id ile student mapping yanlis veya stale olabilir.
- Kisisel veri sorulari auth yoksa kesinlikle genel RAG cevabi ile cevaplanmamali.
- OTP/session state Redis ve Postgres arasinda karisabilir.

Kontrol:

- Slack user id hangi student_id'ye cozulmus?
- `is_authenticated` metadata dogru mu?
- `student_department`, `student_faculty`, `student_type` nereden geliyor?
- Logout tum aktif session'lari kapatiyor mu?

### Profile Context

Profil bilgisi kullanisli ama tehlikelidir.

Dogru:

- Kullanicinin bolumu/fakultesi sadece soru generic ise yardimci slot olarak kullanilmali.
- Kullanici acikca baska bolum/fakulte yazarsa profil onu ezmemeli.

Risk:

- Login profili Bilgisayar iken kullanici EEM sorarsa cevap Bilgisayar'a kayabilir.
- Ucret sorusunda profil fakultesi, kullanicinin yazdigi birimi golgeleyebilir.
- Conversation follow-up'ta eski profil/birim yeni konuya yapisabilir.

### Redis / Question Cache

Redis cache testlerde cok sik yaniltir.

Cache temizleme:

```powershell
docker exec uni_redis redis-cli FLUSHDB
```

Bu temizler:

- question/answer cache
- conversation cache
- runtime gecici state
- Redis'te tutuluyorsa bazi OTP/session cache'leri

Bu temizlemez:

- PostgreSQL
- ChromaDB
- dosyalar
- Docker image
- local JSON kataloglari

Bir degisiklikten sonra Slack eski cevabi veriyorsa:

1. Redis flush yap.
2. Slack runtime restart yap.
3. Dogru container'in calistigini kontrol et.
4. Ayni token ile iki Slack runtime acik mi kontrol et.

### Question Cache ve Conversation Cache

Ilgili dosyalar:

- `src/cache/policy.py`
- `src/cache/question_cache.py`
- `src/cache/conversation_cache.py`
- `src/db/conversation_context.py`

Riskler:

- Eski hatali cevap cache'ten gelebilir.
- Conversation context eski topic/department/source refs tasiyabilir.
- Question cache route/capability degisimlerinden sonra eski final cevabi dondurebilir.

Guncel question cache policy:

- `evaluate_question_cache_lookup(...)` su durumlarda lookup'u kapatir:
  - `disable_cache=True`
  - cache config kapali
  - authenticated query
  - contextual follow-up veya conversation context kullanimi
  - announcement/event/contact/related announcement query
  - `settings.capability_planner.enabled` true ise `reason="capability_planner_enabled"`
- Yani capability planner `mode=on|pilot|shadow` iken normal question cache lookup bekleme; sistem her seferinde yeniden route/planner/RAG calistirabilir.
- `evaluate_question_cache_storage(...)` global synthesis, multi-department, LLM-generated answer, announcement/event source gibi durumlarda cevabi cache'e yazmaz.
- Bu cache policy maliyet ve latency analizinde onemli: "Neden ayni soru tekrar LLM'e gidiyor?" sorusunun cevabi capability planner acik olmasi olabilir.

Yeni testte once cache temizligi yapmadan sonuca guvenme.

## A2A / Docker / Transport Katmani

Slack testleri lokal unit testlerden farkli davranabilir. Cunku Slack genelde Docker/A2A runtime ile calisir.

Katmanlar:

```text
slack-bot-a2a
-> API / A2A endpoint
-> department services / specialist services
-> Postgres / Redis / Chroma
```

Riskler:

- Kod lokal degisti ama Docker container eski image/code ile calisiyor olabilir.
- Slack bot restart edilmedi.
- A2A service endpoint veya auth/signature uyumsuz.
- Bir specialist service down ise fallback path calisir veya "agent servisine ulasilamadi" gorunur.
- Inprocess Slack ve A2A Slack ayni anda aciksa duplicate cevap gelir.
- Docker compose dosyasi yanlis secildiyse capability/specialist service seti beklenenden farkli olur.
- A2A transport endpoint health durumunu kisa sure cache'leyebilir; servis yeni kalkti/indi ise eski health sonucu etkileyebilir.
- A2A helper'lar legacy `DepartmentResponse` payload'larini yeni AgentResponse artifact'lerine cevirir. Bu legacy schema hala uyumluluk icin vardir; "artik kullanilmiyor" varsayma.
- `settings.a2a.mode == "shadow"` gibi modlarda primary response kullaniciya giderken shadow response sadece loglanabilir; Slack ekraninda shadow sonucu gorunmez.
- Remote specialist metadata'si `force_llm_synthesis`, `conversation_source_refs`, `capability_planner`, `final_answer_owner` gibi alanlari tasir; bu alanlardan biri dusmezse remote/local davranis ayrisabilir.

Kontrol komutlari:

```powershell
.\venv\Scripts\python.exe -m scripts.slack_runtime status --runtime a2a
.\venv\Scripts\python.exe -m scripts.slack_runtime logs --runtime a2a
docker compose ps
docker ps
```

A2A smoke gerekiyorsa ilgili smoke scriptlerini kullan; yalniz smoke basarili diye Slack botun guncel oldugu varsayilmaz.

### Remote Retrieval Service Katmani

Ilgili dosyalar:

- `src/rag/remote.py`
- `src/core/config.py` -> `RetrievalServiceSettings`
- `src/agents/base.py` icindeki retriever olusturma/fallback path'leri

Davranis:

- `RETRIEVAL_SERVICE_ENABLED=true` ise specialist ajanlar lokal `HybridRetriever` yerine `RemoteHybridRetriever` kullanabilir.
- Remote retriever `/search` ve `/enrich` endpoint'lerine `query`, `top_k`, `department`, `source_hints`, `topic_hint`, `student_department` payload'i yollar.
- `RETRIEVAL_SERVICE_FALLBACK_TO_LOCAL=true` ise remote hata/timeout durumunda lokal retriever'a dusulebilir.
- Remote servis kendi Chroma/reranker/cache/model durumuna sahipse lokal testle Slack/Docker sonucu farkli olabilir.

Risk:

- Lokal kodda source ranking duzelse bile remote retrieval service eski image/config ile calisiyor olabilir.
- Remote servis `source_hints` veya `topic_hint` semantigini lokal kodla ayni uygulamiyor olabilir.
- Remote `/enrich` farkli chunk komsulugu veya metadata dondururse final evidence pack degisir.
- Remote hata verip lokal fallback'e dusunce loglarda tek bir RAG akisi gibi gorunebilir; `retrieval_service` telemetry kontrol edilmeli.

Denetim:

```text
1. `RETRIEVAL_SERVICE_ENABLED` aktif mi?
2. Remote servis hangi image/git_sha ile calisiyor?
3. Search payload'inda source_hints/topic_hint/student_department var mi?
4. Remote result metadata'si lokal result metadata'siyle ayni mi?
5. Fallback local'e dustu mu?
```

Ilgili dosyalar:

- `src/a2a/transport.py`
- `src/a2a/specialist_transport.py`
- `src/a2a/helpers.py`
- `src/a2a/targets.py`
- `src/a2a/external.py`
- `src/api/a2a_dispatch.py`
- `src/api/agent_service_execution.py`
- `scripts/a2a_*`

## RAG, Reranker, Evidence Packing Detaylari

RAG tarafinda dogru cevap icin sadece "dogru belge var" yetmez. Dogru chunk, dogru madde ve yeterli kapsam LLM'e gitmelidir.

Katmanlar:

- Search department/source planning.
- Vector retrieval.
- Candidate dedup.
- Reranking.
- Source bias / evidence contract boost/penalty.
- Evidence packing.
- Final synthesis.

Riskler:

- Top-k azsa dogru madde kacabilir.
- Ayni belgenin yanlis maddesi yukari cikabilir.
- Baska belge daha yuksek score alabilir.
- Dedup ayni kaynak altindaki faydali chunk'i silebilir.
- Evidence packing madde/blok ortasinda keserse LLM kosullari eksik gorur.
- LLM'e tum genis sonuc verilirse alakasiz kaynaklar cevabi kirletebilir.

Dogru yon:

- Gerekirse ayni kaynak icinden komsu chunk/madde bloku genislet.
- Alakasiz baska kaynaklari azalt.
- Kesilecekse belge/madde sinirinda kes; rastgele cumle ortasinda kesme.
- Plan/evidence contract varsa preferred/avoid source sinyallerini kullan.
- RAG'i genisletirken final LLM'e her seyi doldurmak yerine "tam ama ilgili blok" ver.

Ilgili dosyalar:

- `src/rag/retriever.py`
- `src/rag/search_planner.py`
- `src/rag/candidate_utils.py`
- `src/quality/evidence.py`
- `src/quality/evidence_selector.py`

## Final Cevap Ownership ve Cevap Sentezi

Kimin final cevabi yazdigi net degilse hata analizi eksik kalir.

Olasiliklar:

1. VT deterministic answer direkt doner.
2. Specialist source-only/evidence cevabi doner.
3. Specialist LLM synthesis doner.
4. Main/global synthesis department cevaplarini toparlar.
5. Announcement/event formatter direkt liste cevabi doner.
6. Clarification builder direkt soru doner.
7. Cache eski final cevabi doner.

Her hata analizinde su sor:

- Final answer owner kim?
- Generation mode ne?
- `departments_involved` ne?
- `sources` hangi kaynaklardan?
- Specialist LLM calisti mi?
- Global synthesis calisti mi?
- Judge calisti mi?
- ClaimGuard/answer_filter cevabi degistirdi mi?

Kritik risk:

- `specialist_synthesis_enabled=False` iken bazi kaynak hazirlama metinleri kullaniciya sizabilir.
- `Kaynak bilgisi final cevap icin hazirlandi` gibi cevaplar final synthesis veya timeout/fallback sorununa isaret eder.

## Telemetry / Log / Diagnostics Beklentisi

Bu proje artik log olmadan saglikli debug edilemez.

Aranacak alanlar:

- `query_log_id`
- `original_query`
- `effective_query`
- `standalone_query`
- `routing.departments`
- `routing.strategy`
- `routing.intent`
- `capability_planner`
- `capability records count`
- `department_responses`
- `generation_modes`
- `sources`
- `final_answer_owner`
- `judge action`
- `cache hit/miss`
- `transport diagnostics`

Eksikse yeni calismada telemetry eklemek patch atmaktan daha degerli olabilir.

Telemetry hakkinda onemli ayrintilar:

- `src/db/telemetry.py` QueryLog ve AgentTask payload'larini sanitize/compact eder.
- `answer_preview`, `reasoning_preview`, `query_text`, `resolved_query`, `source_refs` gibi alanlar kirpilir; tam prompt/evidence degildir.
- Conversation source refs en fazla kisa preview olarak tutulabilir; tam kaynak listesini temsil etmeyebilir.
- Telemetry yazimi best-effort tasarlanmistir; telemetry hatasi ana urun akisini kirmayabilir.
- A2A remote agent profilleri `remote_profile`, `remote_profiles`, `remote_agent_id`, `remote_agent_role` metadata'si ile gelebilir.
- `UserQueryResponse.diagnostics` local/remote profiler snapshot tasiyabilir; ancak Slack adapter kullaniciya sadece `response.answer` parcalarini yollar.
- Bu nedenle Slack ekraninda diagnostics gorunmez; API/debug response veya log/DB kaydi ayrica incelenmelidir.

Debug ederken "kaynak ozetinde X var" ile "telemetry/evidence X'i final LLM'e verdi" ayni sey degildir. Kaynak ozeti yuzey formatter ciktisidir; telemetry preview kisaltilmis olabilir; final synthesis promptu ayri kontrol edilmelidir.

## Model Degisimi ve Prompt Degisimi Karari

Foreign token ve garip dil karisimlari icin tek tek regex eklemek son care.

Oncelik:

1. Kaynak/evidence paketi dogru mu?
2. Prompt LLM'e kaynak disi uydurma alani birakiyor mu?
3. Final/global model kalitesi yeterli mi?
4. Judge/answer_filter sadece riskli yerlerde mi calisiyor?
5. Model degisimi A/B test edildi mi?

Model degistirirken:

- Once final/global synthesis rolunde dene.
- Routing modelini degistirmek route davranisini ciddi etkiler; golden Slack akislarini kosmadan yapma.
- Fallback provider model namespace'lerini karistirma.
- `.env` degisti diye container guncel varsayma; restart gerekir.

## Known Unknowns / Mutlaka Dogrulanacaklar

Bu dosyada anlatilanlara ragmen su alanlar yeni sohbette kod/log ile tekrar dogrulanmali:

- Main/global synthesis hangi durumlarda kesin calisiyor?
- Specialist source-only cevaplar kullaniciya hangi path'lerde direkt gidiyor?
- Capability planner mode `on` iken apply/fallback davranisi her agent'ta tutarli mi?
- Announcement/event VT ile RAG indeksleri senkron mu?
- International policy sorulari her zaman `InternationalAgent` kaynaklarina gidiyor mu?
- Finance clarification sadece gercek ucret tutari sorularinda mi geliyor?
- Conversation state bolum/program cevabini slot olarak mi, yeni konu olarak mi tutuyor?
- A2A specialist servisleri lokal kodla ayni commit/versiyonda mi?
- `UserQueryResponse.diagnostics` canli Slack tarafinda gorunur mu, yoksa sadece API/debug icin mi?

## Veri Seed, Migration ve Senkronizasyon Borclari

Kod dogru olsa bile Postgres/Chroma/JSON veri durumu eskiyse Slack sonucu yanlis olur. Yeni sohbette "kodda duzelttik" demeden once verinin nereden geldigi kontrol edilmeli.

Veri katmanlari:

- PostgreSQL runtime tablolari.
- ChromaDB/RAG indeksleri.
- `data/raw/...` dosyalari.
- `data/metadata/...` kataloglari.
- `data/curriculum/*_seed.json`.
- Sync scriptleriyle cekilen duyuru/etkinlik kaynaklari.
- Alembic migration'lar.
- Ders programi PDF/HTML parse sonucunda olusan structured schedule rows.
- UBYS/export kaynakli curriculum JSON payload'lari.

Riskler:

- JSON katalog guncellenmis ama Postgres seed edilmemis olabilir.
- Raw PDF eklenmis ama Chroma indeksine alinmamis olabilir.
- Duyuru/etkinlik sync yeni kayitlari VT'ye almis ama RAG indeksinde yoktur.
- RAG indeksinde eski belge kalmis, raw dosya guncellenmis olabilir.
- Migration lokal DB'de var ama Docker DB'de uygulanmamis olabilir.
- Seed scriptleri bos prerequisite veya duplicate course code uretebilir.
- Ders programi parse edilmis ama `academic_year`, `term` veya `department` override'i yanlis verilmis olabilir.
- Curriculum seed `--courses-only` ile calismis olabilir; bu durumda onkosul/prerequisite verisi eksik kalabilir.
- Chroma reindex yanlis alt klasorle yapildiysa tum koleksiyon eksik belgelerle yeniden yazilmis olabilir.

Kontrol edilecek dosyalar/komutlar:

- `migrations/versions/*`
- `scripts/seed_*`
- `scripts/sync_announcements.py`
- `scripts/sync_events.py`
- `scripts/ingest_*`
- `scripts/index_documents.py`
- `scripts/seed_curriculum_from_json.py`
- `scripts/seed_curriculum_from_ubys.py`
- `scripts/export_curriculum_from_ubys.py`
- `scripts/hybrid_search_probe.py`
- `scripts/compare_collections.py`
- `scripts/audit_document_corpus.py`
- `scripts/audit_academic_source_coverage.py`
- `data/metadata/doc_registry*.json`
- `data/metadata/tuition_fee_catalog.json`
- `data/curriculum/*_seed.json`

Yeni veri eklenince sor:

```text
Raw dosya var mi?
Metadata registry guncel mi?
Postgres tablosuna seed edildi mi?
Chroma/RAG indeksine girdi mi?
Docker runtime ayni DB/volume'u mu kullaniyor?
Slack testinden once servis restart/cache flush yapildi mi?
```

Script/ingestion ayrintilari:

- `scripts/index_documents.py`
  - Varsayilan kaynak `data/raw/student_affairs`.
  - Kaynak klasore gore Chroma collection otomatik cozer.
  - Alt klasorle `--reindex` calistirmak tum koleksiyonu sadece o alt klasorle degistirebilir; `--allow-partial-reindex` korumasi bu yuzden var.
  - Yanlis `--collection` veya yanlis source path, dogru belgeyi baska koleksiyona atabilir.

- `scripts/ingest_schedule_slots.py`
  - Ders programlarini PDF veya `--html-url` ile HTML'den structured schedule tablosuna basar.
  - `--academic-year`, `--term`, `--department` override'lari yanlis verilirse VT dogru dersleri yanlis donem/bolum altinda saklayabilir.
  - `--dry-run` sadece parse ozeti verir; PostgreSQL'e yazmaz.
  - Slot cikarilamayan dosyalar varsa "VT'de yok" cevabi kod hatasi degil parse/format uyumsuzlugu olabilir.

- `scripts/seed_curriculum_from_json.py`
  - Curriculum/course/prerequisite JSON payload'ini PostgreSQL'e yazar.
  - `--courses-only` kullanilirsa prerequisite kayitlari yazilmaz/temizlenmez; onkosul sorulari eksik cikabilir.
  - Seed sonucundaki `missing_courses` ve `missing_prerequisites` uyarilari mutlaka okunmali.

- `scripts/sync_announcements.py` ve `scripts/sync_events.py`
  - VT kayitlarini gunceller ama RAG indeksini otomatik ayni anda guncelliyor varsayma.
  - Parser preset/source metadata yanlis ise duyuru/etkinlik dogru scope/fakulte/birimle kaydolmayabilir.
  - Duyuru/etkinlik kayitlari source URL/detail link tasiyabilir; final formatter bunu kullanir.

Genel kural: "Kaynakta var" cumlesi tek basina yetmez. Hangi kaynakta var?

```text
Raw PDF'de mi var?
Chroma chunk'inda mi var?
Reranker son top-k'ya girdi mi?
Evidence packet'e girdi mi?
PostgreSQL structured tabloda mi var?
Capability executor bu tabloyu mu okuyor?
Final LLM promptuna girdi mi?
```

## Structured VT / Parse Verisi Detayli Denetim Haritasi

Bu bolum ozellikle "VT'den geliyor ama bilgi garip", "kaynakta var ama sistem bulamiyor", "takvim/onkosul/ders programi neden bazen calisiyor bazen calismiyor" gibi durumlar icin yazildi. Yeni sohbette sadece LLM promptuna bakmak yetmez; bu structured verilerin gercek kaynagi ve seed/parse durumu mutlaka kontrol edilmeli.

### Akademik Takvim: Gercek Tablo Degil, Runtime PDF Parse

Akademik takvim capability'si `calendar.academic_date` adiyla VT gibi gorunebilir, fakat mevcut akis dogrudan normalize edilmis bir `academic_calendar_dates` tablosu okumuyor.

Ilgili dosyalar:

- `src/capabilities/calendar_executor.py`
- `src/agents/student/registration_utils.py`
- `data/raw/student_affairs/takvimler/2025_2026_genel_akademik_takvim.pdf`

Mevcut davranis:

- `calendar_executor.execute_calendar_action(...)`, `build_general_exam_calendar_answer(query)` fonksiyonunu cagirir.
- `registration_utils.py` icinde `_ACADEMIC_CALENDAR_PDF` hardcoded olarak `2025_2026_genel_akademik_takvim.pdf` dosyasina bakar.
- PDF metni runtime okunur, satirlar normalize edilir ve `_extract_calendar_row(label)` ile hedef satir bulunur.
- `Derslerin Bitimi`, `Derslerin Baslamasi`, `Yariyil Sonu Sinavlari`, `Butunleme Sinavlari`, not giris son gunu gibi label'lar marker tabanli bulunur.
- Soru bahar/guz sinyali tasiyorsa ilgili kolon secilir; tasimiyorsa guz ve bahar birlikte verilebilir.

Riskler:

- Bu yil bilgisi hardcoded 2025-2026 dosyasina bagli. Yeni yil geldi ama dosya/parse guncellenmediyse cevap stale olur.
- PDF text extraction satiri kirarsa `_extract_calendar_row` ilgili label'i bulamayabilir.
- Soru `son ders tarihi`, `derslerin bitimi`, `ders bitis` gibi marker disinda bir ifadeyle gelirse capability kayit bulamayabilir.
- "Lisans programlarinda" gibi ifade PDF satirinda lisans/onlisans ayrimi yoksa sadece genel takvim olarak cevaplanmali; sistem ayrim uydurmamali.
- Capability no-record donerse bazen fallback RAG, bazen ham "Bulunamadi" gorunebilir. Bu fark executor/fallback/formatter davranisindan kaynaklanabilir.

Debug sirasi:

1. PDF dosyasi Docker runtime icinde var mi?
2. PDF metni gercekten extract ediliyor mu?
3. Aranan label PDF satirinda tek satir olarak gorunuyor mu?
4. Kullanici sorusu `_COURSE_END_CALENDAR_MARKERS` veya ilgili marker'a dusuyor mu?
5. Capability result `records=[]` ise `fallback_allowed` nasil set edilmis?
6. RAG fallback acildiysa top-k icinde `2025_2026_genel_akademik_takvim.pdf` var mi?

Uzun vadeli dogru tasarim:

- Akademik takvim PDF'den runtime parse yerine structured bir takvim tablosuna seed edilmeli.
- Satir label'i, guz tarihi, bahar tarihi, hedef ogrenci grubu, akademik yil, source path ve confidence alanlari tabloya yazilmali.
- Capability sadece bu tabloyu okumali; PDF parse seed/audit asamasinda kalmali.

### Course Registration Periods: Akademik Takvimle Ayni Sey Degil

`course_registration_periods` tablosu ders kayit pencereleri icindir; genel akademik takvim satirlariyla karistirilmamali.

Ilgili dosyalar:

- `src/db/registration_data.py`
- `src/db/student_models.py`

Mevcut davranis:

- `fetch_active_registration_period()` sadece `is_active=True` olan en son kaydi getirir.
- `fetch_preferred_registration_period()` once bugunun tarih araligina dusen kaydi, sonra yaklasan kaydi, sonra active kaydi, en son son kaydi secer.

Riskler:

- Birden fazla active kayit varsa son id kazanir.
- Docker DB eskiyse aktif donem yanlis kalabilir.
- Akademik takvimdeki ders baslangic/bitis sorusu bu tabloyla cevaplanmamali.

### Mufredat / Course Catalog: `courses`

Mufredat ve ders plani sorularinin ana structured kaynagi `courses` tablosudur.

Ilgili dosyalar:

- `src/db/student_models.py`
- `src/db/curriculum_data.py`
- `src/db/curriculum_seed.py`
- `src/db/ubys_curriculum.py`
- `scripts/seed_curriculum_from_json.py`
- `scripts/seed_curriculum_from_ubys.py`
- `scripts/export_curriculum_from_ubys.py`
- `data/curriculum/*_seed.json`

Tablo alanlari:

- `course_code`: unique. Bu global unique oldugu icin ayni kod farkli bolumlerde kullanilirsa conflict riski vardir.
- `course_name`
- `credits`
- `akts`
- `department`
- `semester`: string donem/semester bilgisi.
- `curriculum_semester`: numeric yariyil bilgisi.
- `course_type`: zorunlu, teknik secmeli, secmeli grup, lab, sosyal vb.
- `elective_group`
- teori/uygulama/lab saatleri.

Kritik ayrim:

- `semester` ve `curriculum_semester` ayni sey degildir.
- `5. yariyil dersleri` gibi sorular genelde `curriculum_semester=5` ile cozulmeli.
- Haftalik ders programi sorusu `courses` degil `course_schedule_slots` okumali.

Riskler:

- Eski migration/legacy schema durumunda `akts` eksikse helper fallback olarak `credits` degerini `akts` gibi map edebilir; bu yanlis AKTS cevabi uretir.
- `COURSE_CODE_ALIASES` eski/yeni ders kodlarini eslestirir. Alias eksikse onkosul veya AKTS bulunamayabilir.
- Shared curriculum marker'lari ortak dersleri baska bolumlere dahil edebilir; bu bazen dogru, bazen listeyi sisiren davranistir.
- Secmeli grup satirlari ile secmeli ders secenekleri birlikte donerse cevap "kayitli ders/grup sayisi" olarak fazla gorunebilir.
- `program` veya `department` normalize edilmezse dogru bolum bulunmaz.
- Seed JSON'da course type/elective group eksikse final liste secmeli/zorunlu ayrimini yanlis sunabilir.

Kontrol edilmesi gerekenler:

- Ilgili program icin `courses.department` degeri beklenen normalize adla ayni mi?
- `curriculum_semester` dolu mu?
- `akts` sifir veya credits'e esit otomatik fallback mi?
- Eski ders kodu alias'a ihtiyac duyuyor mu?
- Secmeli grup rows ve secmeli option rows birlikte mi geliyor?

### On Kosul / AKTS Course Detail: `course_prerequisites`

On kosul bilgisi `course_prerequisites` many-to-many tablosundan gelir. AKTS ise asil course kaydindan gelir; onkosul executor'u cevapta course detail ile birlikte gosterebilir.

Ilgili dosyalar:

- `src/db/student_models.py`
- `src/db/curriculum_data.py`
- `src/capabilities/curriculum_executor.py`
- `scripts/seed_curriculum_from_json.py`
- `scripts/seed_curriculum_from_ubys.py`

Mevcut model:

- `course_prerequisites.course_id` hedef ders.
- `course_prerequisites.prerequisite_id` on kosul ders.
- `prerequisite_group` ayni derste birden fazla grup kosulu icin kullanilabilir.

Riskler:

- On kosulun yazilabilmesi icin hem hedef ders hem prerequisite ders `courses` tablosunda mevcut olmali.
- Seed script `--courses-only` ile calistiysa course kayitlari var ama prerequisite kayitlari yoktur.
- Seed ciktisindaki `missing_courses` / `missing_prerequisites` uyarilari okunmadiysa Slack'te "onkosul yok" veya eksik cevap gorunebilir.
- Course code unique/global oldugu icin ayni kod baska bolumde varsa yanlis course_id'ye baglanma riski vardir.
- Eski/yeni kod alias eksikse `BIL203`, `BIL205`, `BIL215` gibi cevaplarda tutarsizlik gorulebilir.
- "Bu dersin on kosulu var mi?" follow-up'i onceki course_code'u kaybettiyse RAG policy'ye dusup genel on kosul maddesi anlatabilir.

Debug sirasi:

1. Hedef course_code `courses` tablosunda var mi?
2. Hedef course row dogru department/program'a ait mi?
3. `course_prerequisites` hedef course_id icin kayit iceriyor mu?
4. Prerequisite course row silinmis veya seed edilmemis mi?
5. Capability planner `curriculum.course_prerequisites` secti mi, yoksa RAG/policy'ye mi dustu?
6. Follow-up frame son course_code'u tasiyor mu?

### Haftalik Ders Programi: `course_schedule_slots`

Ders programi/haftalik program sorulari `course_schedule_slots` tablosundan gelmeli.

Ilgili dosyalar:

- `src/db/student_models.py`
- `src/db/schedule_data.py`
- `src/db/schedule_ingest.py`
- `src/db/schedule_scrapling.py`
- `scripts/ingest_schedule_slots.py`
- `src/capabilities/curriculum_executor.py`

Tablo kimligi:

- `academic_year`
- `term`
- `department`
- `course_key`
- `schedule_group`
- `section`
- `day_of_week`
- `start_time`
- `classroom`

Alanlar:

- `course_code`
- `course_name`
- `end_time`
- `instructor`
- `source_document`
- `source_url`
- `is_active`

Riskler:

- `academic_year`, `term`, `department` override'lari yanlis verildiyse dogru satirlar yanlis donem/bolum altinda saklanir.
- Fetch aktif satirlari alir; eski satirlar `is_active=False` ise gorunmez.
- Department normalize edilir ama yine de normalized equality beklenir; alias eksikse kayit bulunamaz.
- `term` degeri `guz`, `bahar`, `2025-2026 bahar` gibi tutarsiz yazildiysa capability yanlis term arayabilir.
- Unique identity `classroom` uzerinden de ayrisir; ayni ders birden fazla derslik/lab ile gorunebilir.
- Parser HTML/PDF'de ders adini course_code'a ceviremeyebilir; `course_key` ile arama gerekir.
- Ders programi PDF'i RAG'da da varsa VT miss sonrasi RAG alakasiz sinif/bolum ders programi verebilir.

Debug sirasi:

1. `course_schedule_slots` icinde ilgili `department`, `academic_year`, `term` var mi?
2. Satirlar `is_active=True` mi?
3. Sorudaki `4. sinif`, `7. yariyil`, `guz/bahar`, `ilk/ikinci donem` dogru term/semester'e map ediliyor mu?
4. Program degisimi follow-up'ta eski programla birlesiyor mu?
5. `course_code` bos ama `course_key` dolu mu?
6. Source document dogru PDF/HTML mi?

### Ogrenim Ucreti / Harc Kataloglari

Ucret tutari sorulari structured katalogdan gelmeli; harc borcu/prosedur/policy sorulari sadece tutar capability'sine zorlanmamali.

Ilgili dosyalar:

- `src/db/finance_data.py`
- `src/db/finance_models.py`
- `src/db/scholarship_models.py`
- `src/db/student_models.py`
- `src/capabilities/finance_executor.py`
- `data/metadata/tuition_fee_catalog.json`
- `migrations/versions/f91c2b7d4e11_add_tuition_fee_catalog.py`

Mevcut davranis:

- Once DB katalogu aranir.
- DB miss olursa JSON fallback kullanilabilir.
- `student_type` domestic/international olarak normalize edilir.
- Unit/program/fakulte adlari normalize edilir.
- Burs basvuru/veri modelleri ayri `scholarships` ve `scholarship_applications` tablolarindadir; ucret kataloguyla karistirilmamali.

Riskler:

- DB stale ama JSON guncel olabilir veya tersi.
- `active` olmayan DB kaydi gorunmez.
- Program/fakulte alias eksikse kayit bulunamaz.
- `Muzik ogretmenligi ucreti` gibi program sorusu fakulteye map edilirken yanlis birim secilebilir.
- `harc borcum varsa basvurabilir miyim` gibi uygunluk sorulari tutar tablosundan degil policy/RAG'den cevaplanmali.

### Duyuru VT ve RAG Ayrimi

Duyurular hem structured VT'de hem RAG/dokuman tarafinda bulunabilir. Bu iki kaynak otomatik senkron varsayilmamali.

Ilgili dosyalar:

- `src/db/announcements.py`
- `src/db/announcement_sources.py`
- `src/capabilities/announcement_executor.py`
- `src/agents/announcement/agent.py`
- `src/orchestrators/announcement_utils.py`
- `scripts/sync_announcements.py`
- `scripts/cleanup_synthetic_announcements.py`
- `migrations/versions/1a2b3c4d5e6f_add_announcement_sync_tables.py`
- `migrations/versions/2f8a6b1c4d7e_add_announcement_links_table.py`
- `migrations/versions/8b2f4d6c1a9e_add_announcement_unit_name.py`

Riskler:

- Duyuru sync VT'yi gunceller ama RAG indeksini guncellemez.
- RAG'da eski duyuru kalabilir.
- Unit/faculty alias map eksikse duyuru yanlis scope ile doner veya hic donmez.
- `allow_latest_fallback` konu disi son duyuruyu cevap diye getirebilir.
- Prosedur sorulari "basvuru", "tek ders", "tarih" geciyor diye duyuru listesine kacmamalidir.
- Link/title/summary VT'de var ama full detail RAG'da yoksa LLM detay uydurabilir.

Debug sirasi:

1. Soru gercekten duyuru/haber/ilan mi, yoksa policy/prosedur mu?
2. `announcement.search` capability secildi mi?
3. Unit/faculty filter hangi alias'a donustu?
4. Latest fallback calisti mi?
5. VT kaydinin source_url/detail link'i var mi?
6. Ayni duyuru RAG'da da indeksli mi, degil mi?

### Etkinlik VT ve RAG Ayrimi

Etkinlik/seminer/konferans/workshop sorulari duyuru ile karistirilmamali.

Ilgili dosyalar:

- `src/db/events.py`
- `src/db/event_sources.py`
- `src/capabilities/event_executor.py`
- `src/agents/event/agent.py`
- `src/orchestrators/event_utils.py`
- `scripts/sync_events.py`
- `migrations/versions/4e9d2c7b1a6f_add_event_sync_tables.py`

Riskler:

- Event tarihleri `starts_at`, `ends_at`, `all_day` alanlarina baglidir; timezone veya null tarihler sonuclari etkiler.
- Duyuru olarak yayinlanan etkinlik event tablosuna girmemis olabilir.
- Unit/faculty alias duyurular gibi eksik kalabilir.
- "Bugun/yaklasan" filtreleri current date/time'a bagli oldugu icin test tarihi onemlidir.

### Kisisel Ogrenci Verisi / Profil

Kisisel cevaplar icin structured tablolar olabilir ama bunlar OTP/session/profile baglamina baglidir. Genel bilgi sorulariyla karistirilmamali.

Ilgili veri aileleri:

- `students`
- `student_courses`
- `tuition_payments` / `tuition` familyasi
- `scholarship_applications`
- conversation/session/profile tablolar.

Riskler:

- Kullanici OTP ile bagli degilse sistem genel RAG cevabi vermeli veya yetkilendirme istemeli.
- Profildeki bolum/fakulte baska bolum sorusunu ezmemeli.
- Slack thread ve DM context id farklari ayni kullanici icin farkli hafiza yaratabilir.
- `src/db/student_academic_data.py` sadece hizli ozet dondurur; tam transkript yerine gecmez. Recent course limit varsayimi nedeniyle mezuniyet/AKTS gibi kararlar icin tek basina yeterli kabul edilmemeli.

### Ofis / Sekreter / Iletisim Kayitlari

Kullanici "iletisim bilgisi", "sekreter", "kiminle goruseyim" gibi sordugunda structured ofis kayitlari devreye girebilir.

Ilgili dosyalar:

- `src/db/office_contacts.py`
- `src/db/support_models.py`
- `migrations/versions/e7b4f2a1c9d0_add_office_contacts_table.py`

Tablo:

- `office_contacts`

Alanlar:

- `unit_name`
- `department`
- `person_name`
- `title`
- `phone_ext`
- `email`
- `related_agents`
- `is_active`

Mevcut davranis:

- `fetch_office_contacts(...)` departman veya agent_id bazli aktif kayitlari getirir.
- Tablo migration uygulanmamis veya DB'de yoksa helper hata firlatmak yerine bos liste doner ve kisa sureli missing-table cache tutar.

Riskler:

- Migration Docker DB'de yoksa iletisim ozelligi sessizce devre disi kalir.
- `related_agents` yanlis seed edildiyse dogru agent cevabinda iletisim onerisi gorunmez.
- `department` enum/string degeri agent departmaniyla bire bir eslesmezse kayit filtrede dusmez.
- `is_active=False` kayitlar gorunmez.

### Agent Registry, Query Log ve Task Tablolari

Bu tablolar kullaniciya ana bilgi kaynagi olarak verilmez; debug, A2A ve telemetry icindir. Yine de sistem davranisini anlamak icin onemlidir.

Ilgili dosyalar:

- `src/db/support_models.py`
- `src/db/query_logger.py`
- A2A/orchestrator katmanlari.

Tablolar:

- `agent_registry`
- `query_logs`
- `agent_tasks`

Riskler:

- `agent_registry` stale ise A2A specialist endpoint veya capability bilgisi eski kalabilir.
- `query_logs` metadata alaninda route/capability/fallback bilgisi tutulabilir ama Slack yuzeyinde gorunmeyebilir.
- `agent_tasks` failed kalirsa main cevap fallback ile uretilmis olabilir; sadece final cevaba bakarak hangi specialist calisti anlasilmaz.
- Lokal ve Docker DB farkliysa telemetry baska runtime'a ait olabilir.

### Structured Veri Icin Genel Audit Kontrol Listesi

Bir bilgi "VT'de var" denmeden once su listeyi tamamla:

```text
1. Hangi tablo veya runtime parse kaynagi authoritative?
2. Bu bilgi Postgres tablosunda mi, JSON fallback'te mi, raw PDF'de mi, Chroma'da mi?
3. Migration Docker DB'de uygulanmis mi?
4. Seed/sync scripti Docker runtime DB'sine yazmis mi?
5. Kaydin akademik_yil/donem/department/student_type/unit_name alanlari beklenen normalize degerlerde mi?
6. Kayit active/is_active filtresinden geciyor mu?
7. Capability executor gercekten bu kaynagi mi okuyor?
8. Executor records donuyor mu, no-record mu, fallback_allowed mi?
9. Final LLM promptuna kayitlar girdi mi?
10. Response formatter ham no-record mesajini kullaniciya kaciriyor mu?
```

Bu audit sonucunda kaynak eksikse prompt duzeltme yapma. Once seed, migration, sync, alias veya source ownership duzelt.

## Config / Env Flag Haritasi

Bu proje davranisinin buyuk kismi env/config ile degisir. Yeni sohbet config'i okumadan davranis varsaymamali.

Onemli config alanlari:

- `LLM_PRIMARY_PROVIDER`
- `LLM_FALLBACK_PROVIDER`
- `OPENAI_MODEL`
- `OPENAI_ROUTING_MODEL`
- `OPENAI_CONVERSATION_MODEL`
- `OPENAI_GLOBAL_SYNTHESIS_MODEL`
- `OPENAI_SPECIALIST_SYNTHESIS_MODEL`
- `GOOGLE_AI_MODEL`
- `LLM_MAIN_JUDGE_ENABLED`
- `LLM_SPECIALIST_SYNTHESIS_ENABLED`
- `LLM_SPECIALIST_JUDGE_ENABLED`
- `LLM_QUERY_NORMALIZATION_ENABLED`
- `LLM_QUERY_NORMALIZATION_TIMEOUT_SECONDS`
- `RAG_LLM_EVIDENCE_SELECTION_ENABLED`
- `RAG_LLM_QUERY_EXPANSION_ENABLED`
- `RAG_SOURCE_RELEVANCE_PENALTY_ENABLED`
- `RAG_QUERY_PROFILE_SOURCE_BIAS_ENABLED`
- `RAG_EDUCATION_LEVEL_PENALTY_ENABLED`
- `RAG_STUDENT_AFFAIRS_FAQ_BIAS_ENABLED`
- `RETRIEVAL_SERVICE_ENABLED`
- `RETRIEVAL_SERVICE_FALLBACK_TO_LOCAL`
- `CAPABILITY_PLANNER_MODE`
- `CAPABILITY_PLANNER_PRE_ROUTE_ENABLED`
- `CAPABILITY_PLANNER_CONFIDENCE_THRESHOLD`
- `CAPABILITY_PLANNER_SCOPE`
- `CAPABILITY_PLANNER_SYNTHESIZE_WITH_LLM`
- `CONVERSATION_ENABLED`
- `CONVERSATION_REWRITE_WITH_LLM`
- `CONVERSATION_RESET_ON_BUILD`
- `CACHE_ENABLED`
- `CACHE_QUESTION_CACHE_ENABLED`
- `CACHE_REDIS_QUESTION_CACHE_ENABLED`
- `SERVER_RESPONSE_DEBUG_ENABLED`
- `SERVER_RUNTIME_LABEL`
- `SERVER_BUILD_ID`
- `A2A_MODE`
- `A2A_SPECIALIST_MODE`
- `A2A_TRANSPORT_PROTOCOL`
- `A2A_DISCOVERY_HEALTHCHECK_ENABLED`
- `A2A_DISCOVERY_AGENT_CARD_ENABLED`
- `A2A_REQUIRE_SERVICE_IDENTITY`
- `A2A_REQUIRE_REQUEST_SIGNATURE`
- `AGENT_DEPARTMENT`
- `AGENT_SPECIALIST_ID`

Dosya:

- `src/core/config.py`
- `.env`
- `.env.example`

Riskler:

- Lokal `.env` ile Docker env farkli olabilir.
- `.env.example` guncel ama `.env` degil veya tersi.
- `.env` icinde bir flag yok diye kapali varsayma; `src/core/config.py` default degeri devreye girer. Ornek: capability planner default `mode="on"` ve `scope` genistir.
- Test monkeypatch ayari gercek runtime davranisini temsil etmeyebilir.
- Provider fallback calisinca farkli model namespace'i kullanilir; prompt/model davranisi degisir.
- `SERVER_RESPONSE_DEBUG_ENABLED` kapaliysa Slack ekraninda uretim/kaynak ozetleri gorunmeyebilir.
- `CONVERSATION_RESET_ON_BUILD` veya Redis temizligi, follow-up testlerinin sonucunu degistirebilir.
- `RETRIEVAL_SERVICE_ENABLED` aciksa RAG yerel retriever yerine remote retrieval service kullanabilir; fallback davranisi ayri kontrol edilmeli.
- `A2A_MODE`, `A2A_SPECIALIST_MODE`, `AGENT_DEPARTMENT`, `AGENT_SPECIALIST_ID` yanlis kombinasyonda ise lokal/API/Slack farkli agent seti calistirir.
- `CAPABILITY_PLANNER_SYNTHESIZE_WITH_LLM` ve `LLM_SPECIALIST_SYNTHESIS_ENABLED` farkli katmanlari etkiler; ayni sey degildir.
- `CAPABILITY_PLANNER_PRE_ROUTE_ENABLED` default false olsa da pre-route helper kodlari dosyada durur. Aktiflestirilirse routing davranisi kokten degisir; bunu basit config degisikligi gibi gorme.
- `LLM_SPECIALIST_SYNTHESIS_TIMEOUT_SECONDS` ve `LLM_GLOBAL_SYNTHESIS_TIMEOUT_SECONDS` `.env.example` ile `src/core/config.py` default'unda farkli gorunebilir. Runtime icin daima gercek settings objesini veya container env'ini kontrol et.

Debug icin:

```powershell
Select-String -Path .env -Pattern "^(LLM_|OPENAI_|GOOGLE_AI_|CAPABILITY_|RAG_).*"
```

Ama API key/secret degerlerini asla cevaba yazma.

## Normalizasyon, Encoding ve Mojibake

Turkce karakter, ASCII fallback ve mojibake bu projede surekli risk.

Ilgili dosyalar:

- `src/core/text_normalization.py`
- `src/rag/query_preprocessor.py`
- `src/orchestrators/response_utils.py`
- `src/quality/answer_filter.py`

Riskler:

- `ÇAP`, `cap`, `çapı`, `Capa` ayni anlamda yakalanmayabilir.
- `Elektrik Elektronik`, `Elektrik-Elektronik`, `EEM` aliaslari kacabilir.
- Windows console encoding `?` karakteri uretebilir; lokal pipe sonucu gercek app davranisi olmayabilir.
- Dosya daha once mojibake olmus olabilir (`Ã–`, `Ä±`, vb.).
- Foreign token temizligi cevap dilini bozabilir.

Kural:

- Yeni marker eklemeden once normalize helper kullan.
- Ayni marker'in hem Turkce hem ASCII varyantini gereksizce cogaltma.
- Model kaynakli foreign token sorununu regex listesiyle sonsuza kadar yamama.
- Testlerde hem Turkish hem ASCII formu kullan.

## Response Formatting ve Source Summary

Cevap kalitesi sadece dogru bilgi degil; dogru format ve kaynak ozeti de onemli.

Beklenen:

- Kullaniciya ham internal metadata gosterilmemeli.
- `Kaynak bilgisi final cevap icin hazirlandi` gibi ara metin cikmamali.
- `Bulunamadi` tek kelime cevap olmamali.
- Duyuru listelerinde linkler dogru ve sinirli olmali.
- Source summary alakasiz 10 belgeyle sisirilmemeli.
- VT cevabiysa kaynak ozeti `Veritabani kaydi: ...` veya ilgili PDF kaynagi seffaf olmali.
- RAG cevabiysa kaynaklar gercekten cevabi desteklemeli.

Ilgili dosyalar:

- `src/orchestrators/user_response_builders.py`
- `src/orchestrators/response_utils.py`
- `src/db/schemas.py`
- `src/agents/base.py`
- `src/capabilities/academic_formatting.py`

Riskler:

- Specialist source-only cevabi final cevaba ham gelebilir.
- Source summary dogru kaynak yerine retrieval'daki alakasiz kaynaklari gosterebilir.
- Duyuru/event cevabi genel RAG formatina sokulursa link/liste bozulabilir.
- Cok departmanli cevaplarda no-info branch ana cevabi kirletebilir.

## Golden Slack Akis Seti

Yeni mimari degisikligi yapmadan once en az bu akislari elle veya scriptle dene. Sadece tek soru degil, ardışık follow-up onemli.

### Akademik takvim

```text
Bilgisayar muhendisligi icin bahar donemi son ders tarihi nedir?
Akademik takvimde derslerin bitimi ne zaman?
Lisans programlarinda DERSLERIN BITIMI 22 Mayis 2026 mi?
```

### Tek ders / yaz okulu

```text
Hic almadigim bir dersten tek derse girebilir miyim?
Matematik dersi yuzunden kesin okulum uzuyor nasil cozebilirim?
Yaz okulu uzerinden uretebilecegimiz bir cozum var mi kalmamak icin?
Bir dersten kaldim okulum uzayacak yaz okulunda bu dersi alabilir miyim ve bu dersi basarirsam uzamayi engelleyebilir miyim?
```

### Ders / mufredat follow-up

```text
Elektrik Elektronik Muhendisligi mufredatinda Veri Yapilari dersi var mi?
Bilgisayar muhendisliginde var mi peki?
Bu dersin on kosulu var mi?
BIL203
Kac AKTS?
Peki 5. yariyildaki dersler neler?
Elektrik elektronik muhendisligi icin nasil?
```

### Ucret / ogrenci turu clarification

```text
Muzik ogretmenligi ucreti ne kadar?
turk
Dis hekimligi donem ucreti ne kadar?
uluslararasi
```

### CAP / harc / basvuru tarihi follow-up

```text
Capa basvurabilir miyim?
Harc borcum olsaydi basvurabilir miydim?
Basvuru tarihleri ne peki?
capi sordum
```

### Ogrenci toplulugu

```text
Yeni ogrenci toplulugu kurabilir miyim?
Kac kurucu uye gerekir?
Danisman sart mi?
Toplulugun kapatilmasi hangi durumda olur?
```

### International

```text
Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?
Muhendislik fakultesi
Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?
```

### Duyuru / etkinlik

```text
Guncel duyurular neler?
Bilgisayar muhendisligi tek ders sinav duyurusu var mi?
Bugunku etkinlikler neler?
Yaklasan seminer var mi?
```

Bu akislar gecmeden "sistem duzeldi" deme.

## Rollback / Feature Flag Stratejisi

Buyuk davranis degisikligini direkt ana akisa koyma.

Tercih sirasi:

1. Shadow telemetry.
2. Feature flag default off.
3. Pilot dar scope.
4. Golden Slack akis testleri.
5. Default on.

Ozellikle riskli degisiklikler:

- Router karar mantigi.
- Capability planner scope/mode.
- Pre-route planner.
- Missing slot clarification.
- Conversation follow-up rewrite.
- Announcement/event short-circuit.
- Source ownership/RAG collection selection.
- Global synthesis ownership.

Bu alanlarda rollback kolay olmali.

## Ana Mimari Borclar

Yeni sohbet bu borclari da akilda tutmali:

1. Source ownership merkezi degil.
   - Hangi bilgi turu VT, hangisi RAG, hangisi duyuru/event net merkezi map'e baglanmali.

2. Clarification karar kaynaklari daginik.
   - Conversation, router missing_slots, finance, agent guards ayri ayri clarification uretebiliyor.

3. Follow-up state karmasik.
   - Slot cevabi, yeni konu, program degisimi ve eski topic ayrimi daha temiz state machine gerektiriyor.

4. Specialist/global synthesis ownership net degil.
   - Hangi path kullaniciya source-only cevabi dogrudan verir, hangisi global senteze gider haritalanmali.

5. Duyuru/event ve RAG ayrimi tam oturmamis.
   - Duyuru VT ve RAG ayni anda bilgi tasiyor; policy sorulari duyuruya kacabiliyor.

6. Telemetry UI/debug eksik.
   - Slack sonucunu aciklamak icin route/capability/source/final owner bilgilerinin kolay gorunmesi gerekiyor.

7. Model kaynakli dil kalitesi.
   - Foreign tokenlar icin regex yerine model/prompt/evidence kalitesi stratejisi netlesmeli.

8. Docker/lokal farki.
   - Lokal test geciyor ama Slack Docker eski kod/veri/config kullanabiliyor.

## Deferred C: Stateful Handoff / Active Domain State Machine

Bu buyuk mimari secenek simdilik uygulanmayacak; once router-first A2A mimarisi
icinde typed context frame, selector-context izolasyonu ve source hint hygiene
oturtulacak.

C secenegi su bulgular B fazlarindan sonra devam ederse tekrar gundeme alinmali:

- Follow-up sorulari hala aktif konu/ajan kararsizligi yasiyorsa.
- Ayni kullanici ayni konuda art arda sordugunda router her turda gereksiz
  yeniden karar verip latency/maliyet uretiyorsa.
- OTP, basvuru sureci, belge toplama, slot doldurma gibi cok asamali akislar
  tek router karariyla temiz yonetilemiyorsa.
- Bir uzman ajanin kullaniciyla birkac tur boyunca dogrudan konusmasi
  gerekiyorsa.
- A2A dagitik runtime'da `active_domain` / `active_agent` state'ini tasimak
  kacinilmaz hale gelirse.

Bu secenek acilirsa hedef "tum sistemi yikmak" degil; current router/subagent
modelinin yanina kontrollu, stateful handoff katmani ekleyip hangi akislarin
handoff'a, hangilerinin router/paralel dispatch'e ait oldugunu netlestirmek
olmali.

## Deferred Capability-Specific Extractor

Bu secenek simdilik uygulanmayacak. CAP not ortalamasi gibi policy cevaplarinda
once genel mimari iyilestirme tercih edildi: source-constrained evidence recall
ve kontrollu reranker aday genisletmesi.

Capability-specific extractor tekrar su durumda gundeme alinmali:

- Dogru source owner, dogru capability ve dogru kaynak ailesi secildigi halde
  ayni tip sayisal/kuralli cevaplar tekrar tekrar kaciyorsa.
- RAG + reranker dogru chunk'i buluyor ama final sentez sikca "bilgi yok" veya
  yanlis sayisal deger uretiyorsa.
- Belirli capability'ler icin cevap sekli dogasi geregi deterministikse
  (or. basvuru sarti, not esigi, tarih araligi, ucret kalemi).

Bu acilirsa extractor ana karar mekanizmasi olmamali; LLM/router/capability
contract kararindan sonra, sadece secilmis capability ve kaynak ailesi icinde
kanit cikarma/validation katmani olarak calismali.

## Evidence Handoff Soft Line Break Bulgusu

GT11/GT12 CAP follow-up incelemesinde router, source owner ve capability dogru
secildigi halde final cevap once "not ortalamasi net degil" diyebildi. Kok
neden retrieval degil, evidence handoff katmaniydi:

- RAG dogru CAP Madde 5 chunk'ini buluyordu.
- PDF metni `ana dal not\nortalamasinin 4,00 uzerinden en az 3,00...`
  seklinde satir ortasindan bolunebiliyordu.
- Evidence sentence selector bu soft line break'i sert cumle siniri gibi gorup
  `3,00` iceren parcayi final synthesis prompt'una tasimayabiliyordu.
- Bu nedenle final LLM dogru chunk varken somut sayiyi goremiyordu.

Guncel duzeltme generic evidence katmaninda yapildi:

- Evidence seciminden once PDF soft line break'leri birlestiriliyor.
- `not ortalamasi / GNO` esikleri factual claim olarak ayrica cikariliyor.
- Bu, capability-specific extractor degildir; mevcut LLM karar omurgasindan
  sonra kanitin dogru tasinmasini saglayan genel bir normalization/grounding
  duzeltmesidir.

Benzer bulgu tekrar ederse once evidence packet/prompt icinde somut sayi var
mi kontrol edilmeli. Prompt icinde sayi varsa problem final LLM/judge; prompt
icinde sayi yoksa problem retrieval veya evidence extraction katmanindadir.

## Evidence-Answer Validator B+C Hibrit Karari

GT12 CAP follow-up bulgusundan sonra secilen yol soru-bazli extractor yazmak
degil, genel evidence-answer tutarlilik katmani kurmaktir.

Bu karardaki B+C, yukaridaki "Deferred C: Stateful Handoff" karariyla ayni
sey degildir:

- B: Deterministic Evidence-Answer Validator.
- C: Validator risk gorurse mevcut LLM main judge'i conditional olarak
  tetikleme.

Bu katman yeni bir judge degildir ve ana karar mekanizmasinin yerine gecmez.
LLM/router/capability/source-owner kararlari yine ana omurgadir. Validator
yalnizca final cevap ile secilmis evidence arasinda yuksek sinyalli sayi,
tarih, ucret, AKTS/GANO/not ortalamasi gibi degerlerin korunup korunmadigini
kontrol eder.

Ilke:

- Kanitta somut deger varsa ve final cevap bu degeri "net degil/bulunamadi"
  diye reddediyorsa `fail`.
- Kanitta somut deger varsa ve final cevap baska bir somut deger veriyorsa
  `fail`.
- Kanitta gerekli deger var ama cevapta eksikse `check`.
- `check/fail` durumunda yeni bir LLM katmani calismaz. 2026-05
  shadow-first rollout ile `main_judge` force sadece `contract_enforce`
  modunda ve contract acik deger korunumu istediginde yapilabilir.
- Trace/golden raporda `answer_validation_result` ayri gorunur; boylece owner,
  capability ve selector dogruyken cevap kaniti kaciriyor mu net izlenir.

Bu katman future capability-specific extractor icin de sinyal uretir: ayni
capability/source ailesinde validator surekli ayni degerleri yakaliyorsa, o
zaman yukaridaki deferred extractor secenegi tekrar degerlendirilmelidir.

### 2026-05 Shadow-First Rollout Guncellemesi

Validator genis enforce olarak calismamalidir. Guncel rollout karari:

- Varsayilan mod `ANSWER_VALIDATION_MODE=shadow`.
- `off`: validator hic calismaz.
- `shadow`: sadece profiler/decision trace/golden raporuna sonuc yazar.
- `contract_enforce`: yalniz answer/evidence contract veya capability acikca
  sayi/tarih/ucret/AKTS/GNO gibi deger korunumu gerektiriyorsa mevcut
  `main_judge` force edilebilir.

Bu kararin sebebi: broad validator CAP/GNO icin yararli olsa da takvim
satirlarinda coklu tarih, ucretlerde binlik ayirac ve ders kayitlarinda
AKTS/kredi ayrimi gibi alanlarda false positive uretebilir.

Guncel ilke:

- Validator karar verici degil, once observability/guardrail katmanidir.
- Shadow trace ayni capability/source ailesinde tekrar eden deger kacirma
  gosterirse capability-specific extractor pilotu tekrar acilabilir.
- Stateful handoff bu problem icin simdilik acilmayacak; yalniz follow-up
  active domain/agent kararsizligi tekrar ederse gundeme alinacak.
- LLM final synthesis/final refinement provider hatasina duserse deterministik
  fallback de evidence/source fact'larindan query-alakali kritik degerleri
  korumalidir. GT12'de `3,00` kacirma sinyali bu yolla kapatildi; bu bir
  soru bazli rule degil, LLM hata yolunun evidence contract disiplinine
  uymasi kararidir.

### 2026-05 Golden Warmup/Timeout Stabilizasyon Karari

Shadow golden kosucusu runtime urun davranisini degistirmeden test gurultusunu
ayirmalidir:

- `scripts.run_shadow_trace_golden` varsayilan olarak warmup yapmaz.
- Ihtiyac halinde `--warmup-mode retrieval|llm|full` ile opt-in warmup acilir.
- Provider retry runtime `LLMService` icinde degil, golden harness seviyesinde
  `--provider-retry-count` ve `--provider-retry-backoff` ile uygulanir.
- Raporlarda warmup elapsed, provider hata nedeni (`rate_limit`,
  `json_validate_failed`, `timeout`, `connection`) ve capability planner/routing
  timeout sinyalleri ayri gorunmelidir.
- Bu faz source-owner strict mode, stateful handoff veya capability-specific
  extractor acmak icin kullanilmaz; sadece canli golden sinyalini temizler.

### 2026-05 Specialist Ownership Registry Karari

GT12 retrieval-warmup kosusunda provider/timeout gurultusu temizlendikten sonra
kalan bulgu soru bazli degil mimari kabul edildi: source owner ve capability
dogruyken specialist/evidence/synthesis hatti yanlis kanita kayabiliyor.

Guncel karar:

- Specialist secimi merkezi `Specialist Ownership Registry` uzerinden
  okunacak.
- LLM/router/capability planner ana karar mekanizmasi olmaya devam eder.
- Registry, karar verici degil; secilmis capability/source-owner/topic
  kontratini departman icindeki en guvenli specialist'e baglayan deterministic
  guardrail ve trace katmanidir.
- `student_affairs.policy_lookup` icin default uzman `registration_agent`.
- CAP, cift anadal/yandal, GANO/GNO/not ortalamasi, basvuru sartlari,
  yatay gecis, muafiyet/intibak, yaz okulu, tek ders, mazeret, AKTS/kredi
  siniri ve ders yuku policy baglamlari `registration_agent` sahibidir.
- `graduation_agent` yalniz acik diploma/transkript/mezuniyet islemi/
  mezuniyet tamamlama/bagil degerlendirme konularinda secilmelidir.
- "Mezuniyet" kelimesi CAP/GANO/not ortalamasi baglaminda tek basina
  `graduation_agent` secimi icin yeterli degildir.
- Academic Programs branch'i CAP/GANO gibi policy sorularinda
  `regulation_agent` ile destek evidence verebilir; final ownership'i tek
  basina ele gecirmemelidir.
- Legacy keyword selector silinmedi; fallback ve shadow karsilastirma icin
  korunur.

Mapping audit ilkesi:

- Yeni veya degisen capability/topic mapping'leri LLM cagirmayan unit matrix
  ile korunmalidir.
- Matrix en az CAP/GANO, yatay gecis/muafiyet, mezuniyet belge, staj/MUP,
  ogrenci toplulugu, curriculum AKTS/on kosul ve harc ucreti orneklerini
  kapsamalidir.
- Validator shadow sonuclari ayni source family'de tekrarlayan deger kacirma
  gosterirse capability-specific extractor pilotu tekrar karar konusu yapilir;
  aksi halde extractor acilmaz.

### 2026-05 Source Owner / Corpus Placement Bridge Karari

GT11/GT12 sonrasinda kalan ince bulgu selector degildi: `student_affairs_policy`
owner ve `registration_agent` dogruyken registration branch bazi CAP/GANO
kanitlarini bulamiyordu. Kok neden ownership ile corpus placement'in ayni sey
varsayilmasiydi:

- Final cevap ownership'i `student_affairs_policy`.
- Secilmesi gereken specialist `registration_agent`.
- Fakat CAP/cift anadal/yandal yonergeleri ham corpus'ta
  `academic_programs_docs` altinda indeksli.
- Academic branch bu yuzden kanit bulabiliyor; student affairs branch ise kendi
  koleksiyonunda aradigi icin "no_info" uretebiliyordu.

Guncel karar:

- Source owner cevabin yetkili kaynak ailesini soyler; corpus placement kanitin
  hangi Chroma koleksiyonunda durdugunu soyler. Bunlar ayrik kavramlar olarak
  ele alinacak.
- `src/core/source_owner_collections.py` source-owner tabanli kanit bridge'ini
  merkezi tutar.
- `student_affairs_policy` CAP/cift anadal/yandal/GANO/not ortalamasi/ozel
  ogrenci/uzaktan egitim gibi akademik-policy corpus marker'lari tasiyorsa
  `academic_programs_docs` destek evidence collection olarak aranabilir.
- Bu bridge final owner'i, router kararini veya specialist secimini degistirmez;
  sadece dogru owner'in kanita ulasabilecegi destek corpus'u acar.
- Retriever metadata'sinda `retrieval_collection`,
  `retrieval_collection_role=source_owner_support` ve
  `source_owner_collection_bridge` gorunmelidir. Boylece trace'te "dogru owner,
  destek corpus'tan kanit aldi" ile "academic branch final ownership'i ele
  gecirdi" ayrimi yapilabilir.
- Plain student-affairs query'leri icin bridge kapali kalir; sadece marker,
  topic veya preferred source sinyali olan cross-corpus policy sorgularinda
  devreye girer.

Bu karar source owner strict mode acmak anlamina gelmez. Corpus metadata kalitesi
olculmeden strict ownership uygulanmayacak; bridge once observability ve dogru
evidence recall icin kullanilacak.

### 2026-05 Owner-Primary Branch Restoration Karari

GT12 CAP follow-up kosularinda yeni bir mimari bulgu olustu: source owner
`student_affairs_policy` ve capability `student_affairs.policy_lookup` dogru
secildigi halde conversation/router hattindan yalniz `academic_programs`
departmani gelebiliyordu. Branch gate tek departman gorunce `single_branch`
deyip cikiyor, bu nedenle source owner sozlesmesinin primary owner branch'i
geri ekleme sansi olmuyordu.

Bu karar router'i ezmek icin alinmadi. Dogru ayrim:

- Router ana karar katmani olarak kalir.
- Router'in sectigi branch silinmez.
- Capability + source owner birlikte net bir owner-primary branch gerektiriyorsa
  ve o branch dispatch listesinden eksikse, branch gate bu branch'i geri ekler.
- Trace'te `original_departments`, `restored_departments`, `kept_departments`
  ve `reason` alanlariyla bu davranis acik gorunur.

Ilk kontrollu restore kurallari:

- `student_affairs_policy + student_affairs.policy_lookup -> student_affairs`
- `tuition_fee_catalog + finance.tuition_fee -> finance`
- `international_policy + international.policy_lookup -> academic_programs`
- `academic_calendar + calendar.academic_date -> student_affairs`

Bu bir strict source owner modu degildir. Branch restoration yalniz dispatch
omurgasini tamamlar; kaynak secimi, evidence arbitration, synthesis ve validator
ayri calismaya devam eder. Academic branch CAP/GANO gibi policy sorularinda
destek branch olarak kalabilir; final ownership'i tek basina ele gecirmemelidir.

Bu karari tekrar degerlendir:

- Restore edilen branch sikca `no_info` donuyorsa.
- Response time veya RAG maliyeti kabul edilemez artiyorsa.
- Source owner registry yanlis owner urettigi icin gereksiz branch ekliyorsa.
- A2A remote runtime'da `restored_departments` metadata'si tasinmiyor veya
  specialist secimi beklenen primary agent'a gitmiyorsa.

Golden acceptance artik sadece owner eslesmesine bakmamali; capability,
primary department, primary specialist ve provider error sinyallerini de
`CHECK` sebebi yapmalidir. Bu sayede "cevap dogru ama mimari yanlis" durumlari
`OK` diye saklanmaz.

### 2026-05 Generic Policy Evidence Frame / Alignment Karari

Policy belgelerinde ayni PDF icinde farkli hukum facet'leri ve hedef programlar
bulunabilir: basvuru sureci, uygunluk, tarih, belge, mezuniyet/tamamlama,
diploma, ilisik kesme, yatay gecis, muafiyet, staj, topluluk, CAP/cift anadal
ve yandal gibi. GT11/GT12 raporlarinda owner/specialist dogruyken final cevap
farkli facet/program degerlerini ayni cevapta birlestirebildi.

Guncel karar:

- Policy frame yeni bir karar verici degildir; LLM/router/capability kararindan
  sonra evidence arbitration ve observability sinyali uretir.
- `src/core/policy_facets.py` registry formatindadir:
  - `FACET_RULES`: `application_process`, `eligibility`, `date_window`,
    `required_documents`, `completion_or_graduation`, `termination`,
    `appeal_or_exception`, `fee_or_payment`, `credit_load`.
  - `PROGRAM_RULES`: `double_major`, `minor`, `horizontal_transfer`,
    `exemption_adjustment`, `summer_school`, `single_exam`, `internship`,
    `student_community`, `international_registration`.
- Query icin `policy_facet` frame'i uretilir: `facet`, `facets`,
  `target_program`, `target_programs`, `value_aspects`,
  `prefer_evidence_markers`, `avoid_evidence_markers`.
- Her evidence chunk icin `policy_alignment` uretilir:
  `status=match|neutral|weak_conflict|conflict`, matched/conflict facet ve
  programlar, score delta/multiplier.
- Final synthesis prompt'u `evidence_packet.policy_facet` ve
  `selected_sources/facts.policy_alignment` alanlarini gorur. Alignment
  `conflict` veya `weak_conflict` ise o kanittaki sayi/kosul ana cevap sonucu
  gibi kullanilmamalidir.
- Validator da `policy_alignment.status=conflict|weak_conflict` olan evidence
  icindeki sayiyi "cevapta korunmasi gereken deger" saymaz. Bu, yandal 2,00
  esiginin CAP 3,00 sorusunda zorunlu deger gibi gorunmesini engeller.
- Planner `must_answer` icine yanlislikla `mezuniyet sarti` eklese bile query
  facet'i daha guvenilir sinyal kabul edilir; bu LLM planner hatasini kaynak
  seciminde yumusatmak icindir.
- Policy frame registration agent'a ozel kalmaz; ayni capability metadata'sini
  alan academic support branch de bu facet'i gormelidir. Aksi halde
  `academic_programs:regulation_agent` destek kaniti CAP ve yandal esiklerini
  ayni final cevapta birlestirebilir.

Bu katman soru bazli cevap uretmez; ayni kaynak icinde dogru hukum parcasini
LLM'e daha temiz tasimak icin kullanilir. Eger buna ragmen ayni facet'te sayisal
degerler kacarsa capability-specific extractor yeniden gundeme alinabilir.

## Yeni Sohbete Baslarken Onerilen Ilk Mesaj

Yeni sohbette ilk is olarak sunu yaptir:

```text
docs/CODEX_PROJE_BAGLAMI.md dosyasini oku.
Sonra router, capability planner, conversation context, clarification, source ownership ve final synthesis katmanlarini koddan dogrula.
Onceki kararlarin dogru oldugunu varsayma.
Slack'teki son hatalar icin once route/capability/source/final-owner telemetry haritasi cikar, sonra plan oner.
```

## Akademik Takvim

`2025_2026_genel_akademik_takvim.pdf` satirindan structured parse yapiliyor.

Dosyada gorulen ilgili satirlar:

```text
DERSLERIN BASLAMASI 22 Eylul 2025 09 Subat 2026
DERSLERIN BITIMI 02 Ocak 2026 22 Mayis 2026
```

PDF metninde bu satir genel tablo gibi gorunuyor; `Lisans` ve `Onlisans` ayrimi ayni satirda ayri ayrilmis degil.

Ilgili kod:

- `src/agents/student/registration_utils.py`
- `src/agents/student/registration_agent.py`
- `src/capabilities/calendar_executor.py`
- `src/capabilities/academic_formatting.py`

Takvim sorusunda planner genis parametre uretse bile kullanicinin orijinal ifadesindeki `derslerin bitimi`, `son ders tarihi`, `final`, `butunleme`, `not giris` gibi satir sinyalleri korunmali.

## Policy Lookup ve Retrieval

Policy sorularinda cevap gommek yasak. Dogru yaklasim:

- Planner `topic`, `question_type`, `must_answer`, `preferred_sources`, `avoid_sources` gibi plan metadata'si uretir.
- Retrieval query, kullanici sorusu + LLM planindaki `topic/must_answer/preferred_sources` ile zenginlestirilir.
- Bu cevap gommek degildir; yalnizca dogru belge parcasi bulma sinyalidir.

Ornek:

```text
Kullanici: Hic almadigim bir dersten tek derse girebilir miyim?
Retrieval sinyali: tek ders, hic alinmamis ders, devam sarti, mezuniyet icin tek ders kalma kosulu
```

Ilgili dosya:

- `src/agents/student/registration_agent.py`

## Bilinen Hassas Akislar

Slack testlerinde ozellikle tekrar izlenecekler:

- `Bilgisayar muhendisligi icin bahar donemi son ders tarihi nedir?`
- `Lisans programlarinda DERSLERIN BITIMI 22 Mayis 2026 mi?`
- `Akademik takvimde derslerin bitimi ne zaman?`
- `Hic almadigim bir dersten tek derse girebilir miyim?`
- `Yaz okulu uzerinden kalmamak icin cozum var mi?`
- `Yeni ogrenci toplulugu kurabilir miyim?`
- `Toplulugun kapatilmasi hangi durumda olur?`
- `Danisman sart mi?`
- `Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?`
- `Elektrik Elektronik Muhendisligi mufredatinda Veri Yapilari dersi var mi?`
- `Bilgisayar muhendisliginde var mi peki?`
- `Bu dersin on kosulu var mi?`
- `Kac AKTS?`

Beklenti: Router once dogru departmani secmeli; capability planner route'u ezmemeli.

## Mufredat, Ders Programi, On Kosul

VT verisi onceliklidir:

- Mufredat / ders plani: `courses`, curriculum helpers
- Ders programi: `course_schedule_slots`
- On kosul: `course_prerequisites`

Haftalik ders programi sorularinda RAG'e dusup alakasiz PDF ile cevap verme. VT'de yoksa kontrollu "kayit bulunamadi" cevabi ver.

Follow-up baglaminda:

- `Bu dersin on kosulu var mi?` onceki course code/name ile cozulmeli.
- `Kac AKTS?` onceki course detail/on kosul kaydindaki course code ile cozulmeli.
- Program degisimi olursa eski programin ustune ekleme; yeni programla devam et.

## Duyuru ve Etkinlik

Duyuru/haber/ilan sorulari acik niyet varsa `announcement` akisina gitmeli. Prosedur sorulari sirf "basvuru" veya "tek ders" geciyor diye duyuru listesine kacmamali.

Etkinlik/seminer/konferans sorulari `event` akisina gitmeli.

Duyuru/etkinlik icin latest fallback dikkatli kullanilmali; konu disi son kayit cevap olarak donmemeli.

## Finans ve Harc

`finance.tuition_fee` yalniz ucret tutari icin kullanilmali.

Harc borcu, odeme yontemi, basvuru uygunlugu gibi policy/prosedur sorulari finance capability'ye zorlanmamali; RAG/policy lookup ile cevaplanmali.

Ogrenci turu eksikse Turk/uluslararasi clarification normaldir.

## International

Uluslararasi/yabanci ogrenci kayit, basvuru, kabul, ikamet, belge/evrak sorularinda `international.policy_lookup` dogru capability'dir.

Bu sorular gereksiz fakulte/bolum clarification istememeli; kaynaklar uluslararasi ogrenci belgelerinden gelmelidir. Konukevi, ozel ogrenci, yemek bursu gibi konu disi kaynaklar dusurulmelidir.

## UserQueryResponse ve Telemetry

`UserQueryResponse` alanlari:

- `answer`
- `departments_involved`
- `generation_modes`
- `sources`
- `response_time_ms`
- `query_id`
- `diagnostics`

`RoutingStrategy` (`DIRECT`, `PARALLEL`, vb.) UserQueryResponse'a dogrudan tasinmiyor. Profiler/telemetry tarafinda tutuluyor.

Onemli:

- `generation_modes` kullaniciya gosterilen `Uretim Turu` ile bire bir ayni kaynak degildir; debug flag ve response formatter bunu yuzey metnine cevirir.
- `sources` response objesinde tasinir ama Slack kullanicisi sadece `answer` metnini gorur.
- `diagnostics` API/test icin degerlidir; Slack mesajinda otomatik gorunmez.
- `departments_involved` yuzey departmanlarini gosterir. Announcement/event gibi surface department'ler gercek internal owner'dan farkli gorunebilir.
- `agents_involved` her zaman dolu olmayabilir; A2A remote profile ayrica metadata/diagnostics icinde aranmalidir.
- `routing_strategy` final response builder'a parametre olarak gidebilir ama ana `UserQueryResponse` alanlarinda dogrudan kalici bir alan gibi varsayma; profiler/log tarafini kontrol et.

## Test ve Dogrulama

## Mayis 2026 Mimari Toparlama Kararlari

Bu fazda amac soru bazli yamalar eklemek degil, karar omurgasini offline
olarak denetlenebilir hale getirmektir.

- Source owner routing policy merkezi registry'ye tasindi. Branch dispatch,
  `source_owner + capability` kontratindan primary/support branch bilgisini
  okur; router'in yerine gecmez, eksik primary branch'i guardrail olarak geri
  ekler.
- Golden trace icin offline structural audit eklendi. LLM/API limitleri
  doluyken eski golden JSON/JSONL dosyalari yeniden siniflandirilabilir; owner,
  capability, primary department, primary specialist ve provider hata sinyalleri
  birlikte raporlanir.
- GT11 benzeri surec sorulari icin numeric validator'dan ayri shadow-only
  answer coverage kontrolu eklendi. Bu katman judge degildir ve enforce etmez;
  cevap dogru owner'dan gelse bile yanlis facet'e kayarsa trace/raporda CHECK
  sinyali uretir.
- GT12 sonrasi semantic kalite bulgusu: `3,00` cevaba girmesi tek basina
  yeterli degil. Tekil sayisal deger sorularinda cevap `2,00`, `3,00`,
  `2,50` gibi birden fazla esigi ana cevap gibi verirse structural omurga
  temiz olsa bile `answer_value_conflict` shadow kontrolu CHECK uretmelidir.
  Bu katman enforce etmez ve ikinci judge degildir; evidence value arbitration
  ve final synthesis kalitesini gozlemler. Olcek degeri (`4,00 uzerinden`) ve
  yuzdelik ek sart (`ilk %20`) conflict sayilmamali; farkli program/facet
  esikleri ancak acikca ayrilmazsa competing value kabul edilmelidir.
- LLM API key rotasyonu process-wide pool ile yapilmalidir. `OPENAI_API_KEY`
  ve benzeri provider key alanlari virgulle ayrilmis coklu key kabul eder, ama
  secret hicbir zaman trace'e yazilmaz; sadece `api_key_fingerprint`,
  `api_key_index`, `api_key_count` ve provider hatalarindan cikarilan masked
  `provider_org_fingerprint` raporlanir. 429 durumunda ilgili key kisa sureli
  cooldown'a alinabilir. Groq limitleri siklikla organization seviyesinde
  oldugu icin key dagilimi ile org fingerprint ayni anda izlenmelidir; cok key
  varsa bile ayni organization kotasi dolabilir.
- 14 Mayis 2026 API key fallback karari: Groq 429 mesajlarindaki `Please try
  again in ...` suresi parse edilerek gercek cooldown uygulanir; `50m`/`1h`
  gibi TPD bekleme sureleri artik 60 saniyeye dusurulmez. 429 hata mesajindan
  masked `provider_org_fingerprint` cikarilabiliyorsa ilgili key bu org ile
  eslenir ve ayni org'a ait oldugu daha once ogrenilmis keyler birlikte
  cooldown'a alinir. Bu secret saklamaz; sadece fingerprint ve cooldown
  diagnostigi tutar. Sinir: key'in hangi org'a ait oldugu ancak provider hata
  mesajindan ogrenilebilir, bu nedenle daha once hic denenmemis bir key'in org'u
  onceden bilinmez.
- A2A metadata parity sertlestirildi. `branch_dispatch_gate`, source owner ve
  decision contract ile birlikte remote department/specialist payload'larinda
  tasinmalidir.
- 14 Mayis 2026 A2A parity karari: distributed golden'da final owner/capability
  dogru olsa bile `specialist_selection.selected_by`/selector nedeni remote
  trace'te `unknown` kalirsa sonuc OK sayilmaz, `specialist_selector_diagnostics_missing`
  ile CHECK olur. Bu, cevap kalitesini degil metadata parity eksigini gosterir.
  Smoke harness default caller id'si Docker allowlist ile uyumlu olacak sekilde
  `main_orchestrator` yapildi; aksi halde JSON-RPC smoke gereksiz 403 uretir.
  `codex-a2a-parity-20260514` rebuild'inden sonra topoloji 15/15 healthy
  goruldu. GT04 distributed golden'da selector diagnostics duzeldi, fakat Groq
  baglanti/timeout gürültüsü capability planner'i dusurdugu icin canli golden
  halen provider sagligi temizken tekrar edilmelidir.
- Corpus/source-owner strict mode hala acik degil. Once
  `scripts.audit_source_owner_corpus` ile metadata ve bridge ihtiyaci
  denetlenecek; strict/advisory karari bu audit'ten sonra verilecek.
- Contract-aware cache henuz acilmayacak. Cache geri donerse key icinde
  normalized question, source owner, capability, policy facet, model/profile,
  corpus/index version ve answer contract version bulunmali.
- 14 Mayis 2026 retrieval latency karari: GT04 distributed A2A'da gecikmenin
  ana kaynagi LLM degil, `branch x specialist x primary search x multi-query x
  source-constrained recall x reranker` fan-out zinciridir. Bu bulgu ilk
  kosularda CPU-only existing-infra rollout uzerinden goruldu; hedef runtime
  aslinda GPU/FP16 BGE reranker profilidir. Kalici cozum iki parcali kalir:
  once A2A existing-infra stack GPU overlay ve `A2A_TORCH_VARIANT=gpu` ile
  dogru cihaza alinmali, sonra contract-aware `Retrieval Execution Policy`
  primary/support branch butcesini kalite guardrail'i olarak sinirlamaya devam
  etmelidir. Timeout artisi sadece diagnostik kosul olarak kullanilabilir.
- 14 Mayis 2026 A2A timeout/fallback karari: `a2a_transport_timeout` veya
  `a2a_specialist_transport_timeout` goruldugunde local/RAG fallback otomatik
  baslatilmayacak. Bu timeout, uzak branch'in halen retrieval/reranker
  kuyruğunda calisiyor olabilecegini gosterir; fallback ayni isi ikinci kez
  yukleyip kuyrugu buyutebilir. Timeout sonucu trace'te `branch_timeout` ve
  `fallback_skipped_reason=transport_timeout` olarak kalacak. Ayrica CPU
  reranker global concurrency default'u `2` yapildi; aday limitleri kalite
  guardrail'i olarak kalir, tek global kuyrukla iki A2A branch'in birbirini
  20-30 saniye bekletmesi hedeflenmez.
- 14 Mayis 2026 retrieval warmup karari: aktif A2A existing-infra stack'inde
  retrieval-service startup warmup'i CPU reranker ile calisirsa ilk golden veya
  Slack istegi warmup kuyruğuna carpisip `RemoteHybridRetriever` tarafinda
  `ReadTimeout` uretebilir. Bu yuzden `docker-compose.a2a-existing-infra.yml`
  icinde retrieval-service icin `SERVER_WARMUP_INCLUDE_RERANKER=false` yapildi
  ve healthcheck artik `/health` cevabinda `status == healthy` gorene kadar
  servisleri dependent healthy saymayacak. Reranker warmup gerekirse golden
  harness'teki opt-in `--warmup-mode retrieval/full` ile kontrollu kosulacak.

- 14 Mayis 2026 A2A retrieval policy wire karari: `branch_role` ve
  `retrieval_execution_policy` alanlari main -> department -> specialist
  zincirinde task metadata olarak tasinmak zorunda. Bu alanlar dusunce
  `support-lite` devre disi kaliyor, primary/support branch eski top_k ve
  reranker candidate limitleriyle calisip GT04 gibi policy sorularinda 60-75s
  timeout uretebiliyor. Bu yuzden hem department request task hem specialist
  task builder icin explicit passthrough testleri eklendi. Ayrica golden
  structural checker artik primary branch timeout'unu `OK` saymayacak;
  `primary_branch_timeout` / `branch_timeout` olarak `CHECK` uretir.
- 14 Mayis 2026 GPU rollout notu: aktif manual build komutu GPU overlay'i
  kullanmadigi icin `university_support_system-app:latest` CPU-only torch ile
  build edildi (`TORCH_VARIANT=cpu`, `BASE_IMAGE=python:3.11-slim`) ve
  existing-infra compose dosyalari `EMBEDDING_DEVICE=cpu` /
  `RERANKER_DEVICE=cpu` degerlerini set etti. GPU hedefi icin compose dosya
  sirasinin sonuna `docker-compose.a2a-app-gpu.yml` eklenmeli ve build env'de
  `A2A_TORCH_VARIANT=gpu`,
  `A2A_BASE_IMAGE=pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime` olmali.
  `docker-compose.a2a-app-gpu.yml` targeted scope'ta sadece merkezi
  `retrieval-service` icin `EMBEDDING_DEVICE=cuda` ve `RERANKER_DEVICE=cuda`
  override eder; bu A2A mimaride tercih edilen profil, cunku uzman ajanlar
  remote retrieval kullanir.
- 14 Mayis 2026 GPU/FP16 dogrulama: targeted GPU overlay ile rebuild sonrasi
  `uni_a2a_retrieval_service` icinde `torch.cuda.is_available=True`,
  GPU=`NVIDIA GeForce RTX 3050 Laptop GPU`, `torch=2.6.0+cu124`,
  `EMBEDDING_DEVICE=cuda`, `RERANKER_DEVICE=cuda`,
  `EMBEDDING_TORCH_DTYPE=float16`, `RERANKER_TORCH_DTYPE=float16` dogrulandi.
  `uni_a2a_agent_student_registration`, `uni_a2a_agent_academic_regulation`
  ve `uni_a2a_api` icin Docker `DeviceRequests=null`; GPU sadece merkezi
  retrieval-service'e bagli. GT04 distributed golden `20260514_182641` OK:
  primary `registration_agent`, support `regulation_agent:lite`, `mqe=0`,
  `early=strong_primary_evidence`, timeout yok.
- 14 Mayis 2026 warmup geri alimi: GPU/FP16 retrieval-service dogrulandiktan
  sonra `SERVER_WARMUP_INCLUDE_RERANKER=true` tekrar acildi. CPU-only yanlis
  rollout'ta kapatma gecici bir onlemdi. Healthcheck zaten `/health`
  `status == healthy` olana kadar dependent servisleri healthy saymadigi icin
  golden/canli testler warmup bittikten sonra kosulmali.
- 14 Mayis 2026 Slack A2A build guardrail: `scripts.slack_runtime --runtime a2a
  --build` komutu `docker-compose.slack.yml` uzerinden ortak
  `university_support_system-app:latest` tag'ini yeniden build eder. Slack
  servisi GPU kullanmasa da bu tag retrieval/API tarafinda da paylasildigi icin
  CPU tabanli build, sonraki A2A recreate'lerinde GPU/FP16 profilini bozabilir.
  Bu nedenle Slack compose build arg'lari A2A build arg'lariyla hizalandi ve
  `slack_runtime` helper'i A2A stack ile calisirken varsayilan olarak
  `A2A_TORCH_VARIANT=gpu` ve
  `A2A_BASE_IMAGE=pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime` set eder.
  Son karar: `slack_runtime --build` fail-fast yapar; shared image build ve
  servis recreate isi `scripts.a2a_rollout` ile yapilmalidir. `slack_runtime`
  sadece mevcut image ile Slack botunu acip kapatir. Sadece Slack-only/inprocess
  debug gerekiyorsa `--no-a2a-stack` veya `--runtime inprocess` ayri tutulmali.
- 14 Mayis 2026 Slack A2A protocol guardrail: Slack A2A botu JSON-RPC
  transport ile calisirken department agent-card'lari `rest` ilan ederse
  dispatcher servisi daha cagirmadan `transport_protocol_mismatch` uretir ve
  kullaniciya "agent servisine ulasilamadi" mesaji gider. Bu durum servis
  down degil, compose/env protokol uyumsuzlugudur. A2A compose default'lari
  `A2A_TRANSPORT_PROTOCOL=jsonrpc` olarak hizalandi ve `slack_runtime`
  A2A stack ile calisirken ayni default'u set eder. Agent-card kontrolunde
  Slack, academic, finance ve student affairs ayni protocol'u ilan etmelidir.
- 14 Mayis 2026 Slack A2A kalite sertlestirme karari: Slack smoke testindeki
  sorunlar soru bazli yama olarak degil, `context discipline + structured owner
  authority + fee scope + announcement/calendar boundary + answer quality`
  ekseninde ele alindi. Mevcut kullanici mesajindaki acik entity eski context'i
  ezer; course/curriculum/schedule/calendar/tuition gibi structured owner'lar
  RAG'e gereksiz dusmez; yaz okulu/CAP/Erasmus/iade gibi special fee scope'lar
  normal ogrenim ucreti katalog cevabi ile doldurulmaz; `takvimde hangi
  tarihler` benzeri takipler explicit duyuru yoksa announcement'a kaymaz.
  Offline Slack replay audit eklendi:
  `.\venv\Scripts\python.exe -m scripts.audit_slack_replay --input tests\fixtures\slack_diagnostic_cases.json`.
- 14 Mayis 2026 devam karari: `ConversationFrame v2` frame alanlari
  (`operation`, `source_owner`, `capability`, `policy_facet`, `question_type`,
  typed `entities`, `temporal_scope`) routing contract'ina tasindi. Eski
  `department_hints/source_hints` yalnizca `same_topic`, `answer_slot` veya
  `correction` gibi guvenli operasyonlarda ve yeterli confidence ile router'a
  hint olarak verilir. `icin500`, `Eylul2026`, `ICIN240` gibi para/tarih/AKTS
  parcalari course entity sayilmaz; course code kabulunde prefix guard ve
  curriculum executor validasyonu birlikte kullanilir.
- Special fee scope karari: `summer_school_fee`, `cap_extra_fee`,
  `erasmus_fee` normal `tuition_fee_catalog` cevabiyla doldurulmayacak.
  Finance agent regular catalog/RAG yolunu bu scope'larda bloklar; source owner
  registry de planner yanlislikla `finance.tuition_fee` uretse bile primary
  owner olarak `student_affairs_policy` secer, tuition catalog'u sadece fallback
  olarak izlenebilir kilar.
- Announcement fallback karari: explicit/scoped announcement sorgularinda
  generic latest fallback tum giris yollarinda ayni politikayla tasinir.
  `Bilgisayar Muhendisligi duyurulari` gibi scoped query'ler rastgele genel
  duyuru listesine dusmemeli; kaynak yoksa authoritative no-record gorunmelidir.

Yeni offline komutlar:

```powershell
.\venv\Scripts\python.exe -m scripts.audit_shadow_trace_structural --input tests\archive\benchmarks\shadow_decision_trace_golden_20260513_154712.json
.\venv\Scripts\python.exe -m scripts.audit_source_owner_corpus --metadata-dir data\metadata
.\venv\Scripts\python.exe -m scripts.audit_slack_replay --input tests\fixtures\slack_diagnostic_cases.json
```

Sik kullanilan hedefli testler:

```powershell
.\venv\Scripts\python.exe -m pytest tests\unit\test_capabilities.py -q
.\venv\Scripts\python.exe -m pytest tests\unit\test_registration_utils.py -q
.\venv\Scripts\python.exe -m pytest tests\unit\test_all_agents.py::TestRegistrationAgent -q
```

Son ilgili dogrulamalar:

- `tests/unit/test_capabilities.py`: 47 passed
- `tests/unit/test_capabilities.py tests/unit/test_registration_utils.py tests/unit/test_all_agents.py::TestRegistrationAgent`: 94 passed
- 14 Mayis 2026 context/source-authority sertlestirme hedefli regresyon:
  `tests/unit/test_conversation_context.py tests/unit/test_tuition_utils.py tests/unit/test_capabilities.py::test_tuition_agent_blocks_regular_catalog_for_special_fee_scope tests/unit/test_capabilities.py::test_tuition_agent_ignores_finance_capability_for_policy_query tests/unit/test_decision_contract.py tests/unit/test_query_policy.py tests/unit/test_announcement_agent.py tests/unit/test_announcements.py tests/unit/test_orchestrators.py::test_announcement_gate_params_are_passed_to_existing_agent tests/unit/test_retrieval_execution_policy.py`: 138 passed

Windows `.pytest_cache` izin uyarilari test davranisini bozmaz.

## Docker / Slack Runtime

Projede birden fazla compose dosyasi var:

- `docker-compose.yml`
- `docker-compose.slack.yml`
- `docker-compose.a2a.yml`
- `docker-compose.a2a-existing-infra.yml`
- `docker-compose.a2a-existing-infra-capabilities.yml`
- specialist varyantlari

Slack runtime icin helper kullan:

```powershell
.\venv\Scripts\python.exe -m scripts.slack_runtime status --runtime a2a
.\venv\Scripts\python.exe -m scripts.slack_runtime restart --runtime a2a
.\venv\Scripts\python.exe -m scripts.slack_runtime logs --runtime a2a
```

Cache temizleme:

```powershell
docker exec uni_redis redis-cli FLUSHDB
```

`FLUSHDB` Redis secili DB'sindeki soru/cevap cache, conversation/session cache ve gecici runtime state'i temizler. PostgreSQL, ChromaDB, dosyalar ve Docker image'lari silmez.

14 Mayis 2026 karari: Final LLM sentezi timeout, provider 429 veya provider
erisimi nedeniyle basarisiz olursa ham RAG/evidence fallback kullaniciya
gosterilmez. Bu durumda gecici ve kontrollu hata mesaji donulur:
"Su anda cevabi guvenilir bicimde sentezleyemiyorum. Lutfen birkac dakika
sonra tekrar deneyin." Ham fallback cevaplar yanlis guven olusturdugu ve Slack
conversation state'ini kirlettigi icin kapatildi. VT/deterministic cevaplar ve
gercek "kaynakta net bilgi yok" durumlari bu karardan etkilenmez.

Iki Slack runtime ayni token ile ayni anda acik kalirsa duplicate cevap beklenir. Tek runtime calistir.

## Degisiklik Yapmadan Once Kontrol Listesi

- Router ana karar mi kaliyor?
- Capability planner route'u eziyor mu? Ezmemeli.
- Soru ozel statik cevap mi ekliyorsun? Eklememelisin.
- Cevap VT/RAG kaynagina dayaniyor mu?
- Retrieval sorunuysa once source ranking/evidence/query sinyalini duzelt.
- Turkish/ascii normalizasyonu merkezi helper ile mi yapiliyor?
- Slack testinden once Redis cache temizlendi mi ve Slack container restart edildi mi?
- Hedefli unit test veya en az py_compile calisti mi?
