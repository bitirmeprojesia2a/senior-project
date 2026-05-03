# Codex Proje Baglami

## 2026-05-03 Guncel Handoff / Yeni Sohbet Icin Okuma Onceligi

Bu bolum, yeni bir Codex/LLM sohbetine gecildiginde once okunmasi gereken guncel ozet olarak eklendi. Alttaki uzun tarihce degerlidir ama bazi kararlar eskimistir; yeni calismalarda once bu bolumu esas al.

### Repo ve Calisma Dizini

- Ana repo: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system`
- Uygulama kok dizini: `C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system`
- PowerShell kullaniliyor. Komutlari genelde uygulama kok dizininden calistir.
- `rg` bu ortamda zaman zaman access denied verebiliyor; gerekirse PowerShell `Get-ChildItem | Select-String` kullan.
- Kod degisikligi yaparken manuel editlerde `apply_patch` tercih et.

### Son Mimari Karar

Sistem bir OMU universite destek botudur. Slack sadece giris kanali/adaptordur; is mantigi Slack dosyalarina gomulmemeli. Ana akis:

`Slack/API -> MainOrchestrator -> Router/Policy -> DepartmentOrchestrator -> SpecialistAgent/CapabilityAgent -> RAG/VT/LLM -> final response`

Guncel hedef mimari:

- Department servisleri: `student_affairs`, `academic_programs`, `finance`
- Student specialists: `registration_agent`, `graduation_agent`, `internship_agent`, `student_life_agent`
- Academic specialists: `curriculum_agent`, `regulation_agent`, `international_agent`
- Finance specialists: `tuition_agent`, `scholarship_agent`
- Capability agents: `announcement_agent`, `event_agent`
- Docker/A2A runtime aktif olarak kullaniliyor; `A2A_TRANSPORT_PROTOCOL=jsonrpc` tercih ediliyor.
- Slack bot `slack-bot-a2a` servisi ayrica recreate edilmeli; `scripts.a2a_rollout` Slack container'ini recreate etmez.

### Kritik Guncel Ilkeler

- Kaynak varsa specialist LLM sentezi varsayilan yoldur. Source-only cevap sadece LLM timeout/failure veya kontrollu fallback olmalidir.
- Tek departman cevaplarinda uzman LLM sentezi acik kalmali. Cok departmanli cevaplarda global synthesis gercekten farkli departman cevaplarini toparlamak icin kullanilir.
- Duyuru/haber/ilan/link akisi sadece acik duyuru niyeti varsa primary akisa girmeli. Prosedur sorularinda duyuru ancak kontrollu ek bilgi olabilir.
- Routing hibrit: LLM/semantic routing yardimci olabilir ama deterministik override son soz hakkina sahip olmali. Kisisel veri, auth, odeme/harc, akademik takvim, acik duyuru niyeti, idari/prosedur gibi net is kurallari override edebilir.
- Markerlar daginik buyumemeli; yeni marker eklenirse merkezi policy/helper katmanina eklenmeli ve normalized text ile test edilmeli.
- GANO/AKTS su an deterministic tabloya cevirmedik. Aklimizda: LLM bu araliklari cikarabilmeli; once judge/evidence kalite kapisi ile iyilestirme denenecek. Gerekirse sonradan deterministic fact extractor eklenebilir.

### Son Kalite Katmani: Evidence, Intent Coverage ve LLM-as-a-Judge

2026-05-02/03 itibariyla kalite hatti su sekilde dusunulmeli:

1. Retrieval/RAG sonucu gelir.
2. Evidence extraction ve evidence selection yapilir.
3. `intent_coverage` cok parcali soruda alt niyetlerin kaynaklarla kapsanip kapsanmadigini marker tabanli kontrol eder.
4. Specialist LLM cevap sentezler.
5. `claim_guard` kaynakla bariz desteklenmeyen iddialari temizlemeye calisir.
6. `answer_filter` yabanci/bozuk tokenlari yakalar; gerekiyorsa rewrite-only retry yapar.
7. `LLM-as-a-Judge` sadece riskli cevaplarda calisir:
   - sayi/tarih/ucret/AKTS/GANO,
   - mevzuat/uygunluk,
   - "bilgi bulunamadi" cevaplari,
   - dusuk intent coverage,
   - yabanci token supheleri,
   - cok departmanli veya yuksek riskli cevaplar.
8. Judge aksiyonlari:
   - `accept`: cevap kalir.
   - `rewrite_only`: ayni evidence ile tek retry.
   - `retrieve_again`: judge `suggested_query` verirse tek ek retrieval + tek retry.
   - `ask_clarification`: eksik bilgi varsa kisa netlestirme cevabi.
9. Maksimum 1 quality loop vardir. Sonsuz agent loop yok; latency kontrolu icin bu sinir korunmali.

Ilgili dosyalar:

- `src/agents/base.py`: common RAG + LLM + claim guard + answer_filter + judge entegrasyonu.
- `src/quality/judge.py`: risk detection ve JSON judge promptu.
- `src/quality/answer_filter.py`: yabanci/bozuk token tespiti.
- `src/quality/intent_coverage.py`: cok parcali soru alt niyet kapsama kontrolu.
- `src/quality/claim_guard.py`: kaynak destek kontrolu.
- `src/quality/evidence.py`: structured evidence item, source_id, selected sentences.
- `src/quality/evidence_selector.py`: LLM evidence selection.

### Son Duzeltilen Problem Alanlari

#### A2A Specialist fallback

Onceki root cause: specialist servisleri bazen `EvidenceItem.__init__ missing source_id/department/...` ile hata veriyor ve kullaniciya `agent servisine ulasilamadi` donuyordu. Son durumda:

- EvidenceItem fallback constructor alanlari tamamlandi.
- Direct A2A failed `DepartmentResponse(success=False)` path'i exception beklemeden RAG fallback deneyebiliyor.
- Parallel ve sequential dispatch fallback ortak `_is_transport_error` helper'i ile calisiyor.
- Transport diagnostics metadata: endpoint, attempt, timeout_seconds, http_status, circuit_state, error_code gibi alanlar `transport_*` prefix'iyle tasiniyor.
- Hassas sorgularda (kisisel veri/odeme) RAG fallback yapilmamali.

Ilgili dosyalar:

- `src/orchestrators/department.py`
- `src/orchestrators/department_dispatch.py`
- `src/a2a/responses.py`

#### Ders programi ve derslik

- Ders programlari sinif sinif gruplanarak verilmeli: `1. sinif`, `2. sinif`, `3. sinif`, `4. sinif`, gerekirse `Sinif/grup belirtilmeyen`.
- Gozlenen sorun: course title lookup'ta derslik bazen eklenmiyordu. `curriculum_agent` icinde fallback zinciri olmasi gerekir:
  - course_code + department,
  - course_name + department,
  - department + semester/current term.
- Bulunamazsa sessiz gecme: `Derslik bilgisi ders programi verisinde bulunamadi.` de.
- Telemetry/log: `schedule_lookup_method`, rows_found/term_filter izlenmeli.

Ilgili dosyalar:

- `src/agents/academic/curriculum_agent.py`
- `src/db/schedule_data.py`
- `src/agents/academic/curriculum_utils.py`

#### Follow-up / conversation context

- Kisa takip sorulari onceki konu ile standalone query'ye genisletilmeli:
  - `Basvuruyu nasil yapacagim peki?` -> `Mazeret sinavina nasil basvuracagim?`
  - `Hangi derslikte?` -> onceki ders adi + derslik sorusu.
  - `Ucretli mi?` -> onceki konu yaz okulu ise `Yaz okulu ucretli mi?`
- Telemetry/log icinde su alanlar gorunmeli:
  - `original_query`
  - `standalone_query`
  - `is_follow_up`
  - `topic`
  - `rewrite_method`

Ilgili dosyalar:

- `src/db/conversation_context.py`
- `src/llm/prompt_templates.py`
- `src/orchestrators/main.py`
- `src/cache/policy.py`

#### Yaz okulu ve cok parcali sorular

- Yaz okulu ozelinde degil, genel prosedur promptunda cok parcali soru kuralini koru.
- Soru `ne zaman + kimler + nasil + ucret + belge + sart` gibi birden fazla alt niyet tasiyorsa cevap alt basliklara bolunmeli.
- Kaynakta tarih yoksa tarih uydurma; `akademik takvim/duyuru ile ilan edilir` gibi temkinli cevap ver.
- `intent_coverage` dusukse judge veya retrieve-again devreye girebilir.

#### Onlisans CAP

- Bu alan hassas/yoruma acik. Kaynaklarda `ana dal lisans programi` vurgusu ile `onlisans 120 AKTS` ifadesi birlikte gorulebiliyor.
- Bot kesin `yapamazsiniz` dememeli. Daha temkinli cevap:
  - CAP esas olarak ana dal lisans programi uzerinden tanimlaniyor.
  - Onlisans ifadesi geciyorsa kesin uygunluk ilgili yil kontenjan/protokol/birim karariyla dogrulanmalidir.
  - Ilgili birimin CAP/YAP duyurusu ve OIDB kontrol edilmeli.

#### Yabanci/bozuk tokenlar

Gozlenen ornekler: `appropriate`, `necesario`, `enen`, `tonabilir`, Korece/Japonca/Devanagari kalintilari. Bunlar:

- `src/orchestrators/response_utils.py` clean-up katmaninda temizlenebilir.
- `src/quality/answer_filter.py` tarafindan risk sinyali olarak yakalanabilir.
- Yakalanirsa ayni evidence ile rewrite-only retry denenir.
- Tek tek kelime eklemek son care; genel kalite guard + judge daha onemli.

#### Duyuru scope ve limit

- Genel duyurular 5 adet gosterilir; `limit=6` cekilip `has_more` ile `... ve daha fazla duyuru var` mesaji verilir.
- Source summary 5 kaynakla sinirlanir.
- EEM alias varyantlari eklendi: `elektrik elktronik`, `elektrik-elektronik`, `eem bolumu`, `eem muhendisligi`.
- Matematik ogretmenligi gibi birimler genel OMU duyurusuna dusuyorsa alias/unit scope listesi eksiktir; `src/db/announcements.py` ve gerekirse `src/db/events.py` icindeki unit/faculty alias listeleri kontrol edilmeli.

### Model Karari / Deneme Notu

Mevcut sorunlarin cogu model kapasitesinden once evidence/retrieval/prompt/judge katmani ile ilgili. Yine de `openai/gpt-oss-120b` modeli `llama 70b` yerine denemeye deger aday olarak goruldu:

- MoE oldugu icin toplam 120B olmasina ragmen token basina aktif maliyet daha dusuk olabilir.
- Uzun context ve structured/judge islerinde avantajli olabilir.
- Ancak Turkce kalite mutlaka A/B test edilmeli.
- Tam gecis yapmadan once sadece `specialist_synthesis` ve `judge` rollerinde denenmeli; embedding/reranker degistirilmemeli.
- Harmony/chat template dogru uygulanmali; yanlis template cevap kalitesini bozar.

### Rollout Komutlari

Uygulama kok dizininden:

```powershell
cd "C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system"

.\venv\Scripts\python.exe -m compileall src -q
.\venv\Scripts\python.exe -m pytest tests/unit/test_hotfix_validation.py -v

.\venv\Scripts\python.exe -m scripts.a2a_rollout --include-student --include-academic --include-announcement --include-event --include-all-specialists --transport-protocol jsonrpc --health-timeout-seconds 240

$env:A2A_TRANSPORT_PROTOCOL="jsonrpc"
docker compose -f docker-compose.slack.yml up --no-build --force-recreate -d slack-bot-a2a

docker exec uni_redis redis-cli FLUSHDB
```

Not: `FLUSHDB` Redis secili DB'sindeki soru/cevap cache, conversation/session cache, retriever/query cache, gecici runtime state ve Redis'te tutuluyorsa OTP gibi kisa sureli kayitlari siler. PostgreSQL, ChromaDB, indeksler, dosyalar ve Docker image'lari silmez.

Canli smoke:

```powershell
.\venv\Scripts\python.exe -m scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15 --expect-agent registration_agent --expect-agent regulation_agent --expect-agent curriculum_agent --query "Ders kaydı nasıl yapılır?" --jsonrpc-query "Önlisans öğrencisiyim çap yapabiliyor muyum?"
```

### Son Regression Testleri

Guncel hotfix/quality test dosyasi:

- `tests/unit/test_hotfix_validation.py`

Son bilinen sonuc:

- `compileall src -q`: basarili
- `pytest tests/unit/test_hotfix_validation.py -q`: 29 passed
- Pytest cache uyarilari `.pytest_cache` yazma izniyle ilgili; test basarisini bozmaz.

### Slack'te Ozellikle Tekrar Denenecek Sorular

Yeni degisiklikten sonra ciktilar su sorularla yorumlanmali:

- `Ders kaydı nasıl yapılır?`
- `Ders kaydı yapmayı unuttum ek süre var mı?`
- `Mazeret sınavlarına nasıl katılabilirim?`
- Follow-up: `Başvuruyu nasıl yapacağım peki?`
- `Mazeret sınavına nasıl başvuracağım?`
- `Muafiyet kararı çıkana kadar derslere devam etmeli miyim?`
- `Olasılık ve istatistiğe giriş dersi hangi sınıfta?`
- Follow-up: `Hangi derslikte?`
- `Yaz okulu ne zaman ve kimler katılabilir?`
- `Yaz okulu şartları neler?`
- `Ücretli mi yaz okulu?`
- `Önlisans öğrencisiyim çap yapabiliyor muyum?`
- `Her dönem kaç AKTS hakkım var`
- `3,28 GANO için kaç AKTS hakkım var`
- `Güncel duyurular neler?`
- `Elektrik elktronik mühendisliği güncel duyurular nelerdir?`
- `Matematik öğretmenliği duyuruları`
- `Fizik duyuruları`

### Yeni Modelin Dikkat Etmesi Gereken Backlog

- GANO/AKTS henuz deterministic degil. Judge bunu duzeltemezse fact extractor veya policy table dusun.
- Judge ek maliyet getirir; her cevapta calistirma. Risk detection ve maksimum 1 retry siniri korunmali.
- `retrieve_again` judge aksiyonu tek ek retrieval ile sinirli kalmali.
- Duyuru alias listeleri genislemeye acik; ozellikle Matematik Ogretmenligi gibi birimlerde scope kacabiliyor.
- RAG kalitesi kotuyse once evidence/ranking/coverage loglarina bak; hemen model degistirme.
- Slack bot rebuild/recreate unutulursa Docker servisleri guncel olsa bile Slack eski kodla cevap verebilir.

> Nisan 2026 dokuman hijyeni notu: Gecmis calismalara ait benchmark, latency, RAG evaluation ve reranker analiz artefaktlari artik ana `docs/` ve `tests/` kokleri yerine `docs/archive/benchmarks/` ile `tests/archive/benchmarks/` altinda tutulur; yeni benchmark ciktilari da varsayilan olarak bu klasorlere yazilir.

Bu dosya, projede ilerlerken baglamdan kopmamak icin kisa teknik pusuladir. Kod degistirirken once buradaki kurallari kontrol et.

## Temel Mimari

Kullanici giris kanallari API, CLI testleri ve Slack adapteridir. Slack akisi:

`src.slack.app -> src.slack.service -> AuthService/MainOrchestrator -> departman ajanlari -> final cevap`

Ana karar noktasi `src.orchestrators.main.MainOrchestrator` icindedir. Router sadece departmani ve task tipini belirler; canli duyuru/etkinlik gibi akislar router'a gitmeden short-circuit olabilir.

Departman uzmanlari `src.agents.base.BaseSpecialistAgent` uzerinden RAG + LLM + kaynak ozeti sozlesmesini kullanir. Bir uzman ajana uzun statik cevap yapistirmak son care degildir; kaynak secimi, DB verisi, routing veya policy katmani duzeltilmelidir.

## Normalizasyon

Turkce karakter ve case normalizasyonu merkezi olarak `src.core.text_normalization.normalize_text()` ile yapilir. `var mi` / `var mı`, `programi` / `programı`, `ogrenci` / `öğrenci` gibi eslesmeler icin once metni normalize et.

Yeni marker eklerken:

- Normalize edilmis metinde dogrudan `in` kontrolu yapiliyorsa marker'lari ASCII-normal formda tut.
- Ham metinle calisiliyorsa `contains_any_normalized()` kullan.
- Ayni marker'in Turkce ve ASCII varyantlarini ayni tuple'a ekleme; bu gurultu ve bakim maliyeti yaratir.

## Cevap Uretim Kurali

VT'de net veri varsa cevap VT'den gelmeli. Ornek: mufredat, onkosul, duyuru, etkinlik, ders programi slotlari.

RAG, resmi belge veya dokuman kaynaklari icin kullanilir. RAG sonuclari alakasizsa ajan icine statik metin eklemek yerine:

- Router'in dogru uzmana gittigini kontrol et.
- Query expansion veya search planner'in dogru koleksiyonu kullandigini kontrol et.
- Kaynak secim/ranking helper'ini iyilestir.
- Gerekirse dusuk guven veya bos sonuc icin kontrollu "kaynak bulunamadi" cevabi ver.

LLM sadece kaynaklari sentezlemeli; kaynaksiz prosedur uydurmamali.

Prompt duzeltmelerinde kelimeye ozel yama yapmak yerine genel davranis ilkesi tercih et: cevap kisa olabilir ama kaynakta sorunun cevabi icin gerekli resmi ad, belge/sistem/islem adi, kosul ve adimlar anlam kaybina yol acacak sekilde kesilmemelidir. Routing veya follow-up JSON promptlarina bu tarz cevap uretim uyarisi ekleme; karar sinyalini kirletebilir.

Coklu departman cevaplarinda final cevap govdesi filtrelenmis/guvenilir cevaplardan kurulabilir; ancak `departments_involved` gercek cagrilan departman izini kaybetmemelidir. No-info veya zayif bir branch kullanici cevabini kirletmeden metadata'da gorunebilir.

## Duyuru ve Etkinlikler

Duyurular ve etkinlikler kullanici ozel olarak sordugunda gelmeli. Genel cevaplara gereksizce eklenmemeli.

Kapsam belirleme:

- Genel OMU duyurulari icin faculty/unit bos olabilir.
- Bolum/fakulte baglamli sinav programi, ders programi, tek ders, butunleme gibi sorgularda ogrencinin faculty/unit bilgisi ile daraltma tercih edilir.
- Konu spesifik duyuruda latest fallback dikkatli kullanilir; alakasiz son duyuru cevap olarak donmemeli.
- Etkinliklerde kullanici baska bir bolum/fakulte adi verdiyse oturumdaki ogrenci bolumu zorla scope'a eklenmemeli. Query icindeki bolum/fakulte alias'larini `src.db.events` kendisi cozebilir.
- Yeni duyuru/etkinlik kaynak presetleri eklenince unit/faculty alias listeleri de senkron tutulmali. Aksi halde DB'de veri olsa bile "Fizik duyurulari" gibi sorgular dogru unit'e daralmayabilir.
- Acik etkinlik niyetinde conversation resolver beklenmemeli; event short-circuit hizli VT akisidir. Etkinlik bulunamazsa kaynak uydurma, ama "etkinlik aramasi / uygun kayit bulunamadi" seklinde veri yolu seffafligi ver.
- 2026-04-21 guncel mimari: `announcement` ve `event` artik ayri capability agent/service olarak da ayaga kalkabilir. `docker-compose.a2a-existing-infra-capabilities.yml` ve `scripts.a2a_rollout --include-announcement --include-event` bu servisleri canli HTTP A2A topolojisine ekler.
- MainOrchestrator urun mantiginda duyuru/etkinlik niyetleri hala ozel hizli akis gibi dusunulur; ancak dagitim siniri artik capability service olabilir. Yani "duyuru/event unutuldu mu?" sorusunun cevabi hayir: canli Docker smoke'ta `announcement_agent` ve `event_agent` remote `/a2a/dispatch` ile dogrulandi.
- `burs basvurusu ne zaman?` gibi finance + announcement karmasi sorular hala acik backlog'tur. Buradaki sorun A2A transport degil; announcement retrieval/policy hassasiyeti ve son cevapta announcement branch'in nasil kullanildigi ile ilgilidir.

## Mufredat ve Ders Verisi

Mufredat ve onkosul verisi `courses`, `course_prerequisites` ve ilgili DB helper'larindan gelir. SSD gibi ortak secmeli dersler bolum derslerinden ayrilmali, "ortak dersler" veya "secmeli gruplar" olarak sunulmalidir.

Ders programi `course_schedule_slots` satirlarindan gelir. Bir bolum icin slot yoksa RAG'e dusup alakasiz PDF parcalariyla cevap verme; kontrollu bicimde yapilandirilmis ders programi satiri bulunamadigini soyle.

## Erasmus / Uluslararasi Sorular

Erasmus ve gelen/giden degisim sorulari `InternationalAgent` altinda kaynakli cevap uretmelidir. "Gelen Erasmus ogrencisi kayit" gibi sorgularda dogru kaynak chunk'i genellikle "Gelen ogrenci" ve "kayitlari ilgili bolum tarafindan Ogrenci Isleri Otomasyon Sistemine yapilir" ifadelerini tasir.

Bu tur sorular icin statik prosedur yazma. Dogru yaklasim:

- Router'da uluslararasi + kayit sureci sinyalini Academic Programs'a yonlendir.
- "UBYS kaydi" gibi ogrenci isleri marker'i gecse bile sorguda Erasmus/uluslararasi + kayit sureci birlikte varsa `academic_programs` oncelikli olmali.
- Erasmus + burs/hibe sorulari coklu departman kabul edilir: `academic_programs` basvuru/prosedur icin, `finance` hibe/burs finansal bilgi icin cagrilir. Finance branch alakasiz genel burs kaynaklarini donmemeli; uluslararasi/hibe baglamina uymayan kaynaklar filtrelenmelidir.
- `regulation_utils` icinde gelen/giden degisim baglamina gore kaynak ranking'ini iyilestir.
- Erasmus hibe/miktar sorularinda sabit TL/Euro tutar kaynakta olmayabilir. Bu durumda tutar uydurma; kaynakta "hibe miktari, odeme usulu ve tarihi her yil Ulusal Ajans tarafindan belirlenir" deniyorsa bunu acikca soyle. Bu sorularda dogru ogrenci hibe parcasi genelde MADDE 12 / Ulusal Ajans / iki taksit / %80 / Ogrenci Hibe Sozlesmesi ifadelerini tasir; personel hareketliligi hibe parcasi ogrenci hibesinin onune gecmemeli.
- Erasmus hibe + basvuru gibi cok parcali sorularda top-5 RAG sonucu dogru MADDE 12 parcasini kacirabilir. `InternationalAgent` bu baglamda daha genis aday havuzu ister; sonuc yine kaynak/ranking tabanli olmali, statik prosedur eklenmemeli.
- Cevap kaynakli RAG olarak donsun.

## Kisisel Veri ve Auth

Not ortalamam, harc borcum, burs aliyor muyum gibi acik kisisel veri sorulari conversation resolver veya genel LLM beklemeden dogrudan ilgili departmana gitmeli ve oturum yoksa auth guard cevabi donmelidir. "Ne kadar?" gibi miktar sorulari, "borcum/harcim/odemem/bursum" sahiplik eki tasiyorsa prosedurel soru degil kisisel veri sorusudur.

Mezuniyet/diploma/ilisik kesme baglami harc/borc/odeme ile birlikte soruluyorsa bu hem idari surec hem finans yukumlulugu sayilir; `student_affairs + finance` paralel route edilmelidir. Oturum yoksa iki branch de auth guard dondurebilir.

"Bursum kesilir mi?", "harc odemem gerekir mi?", "kayit dondurunca ucret gerekir mi?" gibi sorular sahiplik eki tasisa bile kisisel veri sorgusu degil politika/senaryo sorusudur; auth guard'a dusmemeli, RAG/LLM kaynak sentezine gitmelidir.

Kayit/donem/harc kelimeleri birlikte geciyor diye RegistrationAgent hemen VT kayit donemi cevabi vermemeli. Soru "ders kaydini nasil yapacagim", "danisman onay sureci", "kayit dondurma", "basindan sonuna" gibi surec/politika sinyalleri tasiyorsa period lookup atlanmali ve kaynakli LLM sentezi tercih edilmelidir.

Genel ogrenci haklari/kurallari ayrimi: devamsizlik, butunleme, devam kosulu ve ders tekrari gibi ogrenci isleri yonetmelik sorulari `student_affairs`; pedagojik formasyon ders/program kurallari `academic_programs`; azami/ek sure + katkı payi sorulari `academic_programs + student_affairs + finance` olarak ele alinmalidir.

Kalite benchmark yorumlarken Chroma `localhost:8100`, PostgreSQL ve Redis durumunu once dogrula. Chroma kapaliyken RAG 0 kaynakla "kural/kaynak yok" moduna duser; bu sonuc kod kalite regresyonu olarak okunmamalidir.

LLM sentez icin normal/aktif yol Groq uzerinden `openai_compatible` API'dir. Groq limit/timeout durumlari icin Google AI Gemini OpenAI-compatible endpoint'i artik ayri `google_ai` fallback provider olarak kullanilabilir (`LLM_FALLBACK_PROVIDER=google_ai`, `GOOGLE_AI_API_KEY`, `GOOGLE_AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai`). Google fallback'te hiz icin varsayilan `GOOGLE_AI_REASONING_EFFORT=none` kullanilir; kalite/benchmark denemelerinde bu ayar bilincli degistirilmelidir. Docker icindeki Ollama su an ana uretim yolu degildir; sadece lokal fallback veya izole dogrulama icin dusunulmelidir. Groq/Google testi yaparken ag erisimi, API anahtari ve provider health durumunu ayri dogrula.

Benchmark tekrarlarinda question cache ve retriever cache eski cevabi maskeleyebilir. Retrieval/ranking veya prompt degisikligi olctugunde cache'i kapat (`CACHE_QUESTION_CACHE_ENABLED=false`, `CACHE_RETRIEVER_QUERY_CACHE_ENABLED=false`, Redis cache bayraklari false) ya da sorguyu bilincli farklilastir.

## Slack

Slack sadece giris kanali olmali; is mantigi Slack'e gomulmemeli. Slack servisinin gorevi mesaj parse etmek, OTP/login/logout yonetmek, MainOrchestrator'a context ve kimlik bilgisiyle sormak ve cevabi Slack formatina cevirmektir.

Slack'te link unfurl kapali tutulur; aksi halde cevaplar gereksiz kartlarla sisiyor.

## A2A Durumu

2026-04-21 itibariyla proje artik sadece "A2A uyumlu task sozlesmesi" seviyesinde degil. Ana API, departman orkestrator servisleri (`student_affairs`, `academic_programs`, `finance`), capability servisleri (`announcement`, `event`) ve finance pilot uzman servisleri (`tuition_agent`, `scholarship_agent`) Docker uzerinde ayri HTTP A2A servisleri olarak dogrulandi. Varsayilan gelistirme davranisi yine guvenli sekilde `inprocess` kalabilir; dagitik mod `A2A_MODE=http` ve rollout overlay'leri ile acilir.

Guncel sinirlar:

- `MainOrchestrator -> DepartmentOrchestrator` HTTP A2A hatti canli Docker'da dogrulandi.
- `MainOrchestrator -> capability agent` HTTP A2A hatti announcement/event icin dogrulandi.
- `DepartmentOrchestrator -> SpecialistAgent` hatti finance pilotundan sonra student affairs ve academic programs icin de rollout/compose seviyesinde genellestirildi. `A2A_SPECIALIST_MODE=http` ilgili departman orkestratorune verildiginde uzman agent secimi ayni kalir, sadece secilen uzman HTTP A2A servisi olarak cagrilir.
- A2A agent servisleri artik standarda daha yakin discovery ve RPC yuzeyi de sunar: `/.well-known/agent.json` ve `/.well-known/agent-card.json` AgentCard dondurur; `POST /a2a` JSON-RPC `message/send` kabul eder ve sonuc olarak A2A `Task` dondurur. Eski internal `/a2a/dispatch` bozulmadan kalir.
- `A2A_TRANSPORT_PROTOCOL=rest|jsonrpc` ile HTTP client tarafi secilebilir. Default `rest` oldugu icin canli davranis korunur; `jsonrpc` secildiginde department, capability ve specialist HTTP transportlari `/a2a` uzerinden `message/send` kullanir.
- Specialist HTTP timeout'u departmanlar arasi kisa timeout'tan ayridir. `A2A_SPECIALIST_TIMEOUT_SECONDS` guncel kodda kullanilir; canli mevcut imajla geriye uyum icin finance specialist overlay'i `A2A_TIMEOUT_SECONDS=${A2A_SPECIALIST_TIMEOUT_SECONDS:-60}` de set eder. Yavas RAG/LLM uzmanlari 10 sn'de timeout olup in-process fallback ile ayni isi iki kez yapmamali.
- Finance specialist pilotu genel altyapi pilotudur; burs/harc cevap kalitesi veya retrieval hassasiyeti ayri urun backlog'u olarak ele alinmalidir. Student/academic specialist overlay'leri de ayni prensiple ele alinmali: once transport/topoloji dogrulanir, sonra cevap kalitesi benchmark'i ayri kosulur.

Transport abstraction baslatildi: `src.a2a.transport` icinde in-process, HTTP ve shadow transport siniflari var. `A2A_MODE=inprocess|http|shadow` ile seciliyor; default `inprocess` oldugu icin mevcut Slack/API davranisi korunur. HTTP transport `/a2a/dispatch` uyumlu JSON veya JSON-RPC `/a2a` `message/send` kullanabilir; A2A task artifact'i artik genel `omu.agent_response.v1` semantigini tasir, eski `omu.department_response.v1` ise legacy schema/extension olarak korunur. Session token HTTP payload'a tasinmaz. `A2A_MODE=http` iken `MainOrchestrator` yerel departman agent'larini kurmak yerine hafif `RemoteDepartmentTarget` nesneleri kullanir; remote servisleri cagirirken agir ajan/model yuklemez.

Ayrik agent service iskeleti baslatildi: `src.api.agent_service.create_agent_service_app` tek departman servisi kurar; `AGENT_DEPARTMENT=student_affairs|academic_programs|finance` ile secilir. Endpointler: `/health`, `/agent-card`, `/metrics`, `/a2a/dispatch`. `scripts/run_agent_service.py` ile ayri process olarak baslatilir. Public API ve agent service ortak `src.api.a2a_dispatch.A2ADispatchRequest` sozlesmesini kullanir.

A2A HTTP canary icin `scripts/a2a_http_canary.py` var. Ayakta olan agent service'e health/card/metrics ve opsiyonel dispatch smoke testi yapar; canli dispatch icin `SERVER_INTERNAL_API_KEY` veya `A2A_INTERNAL_API_KEY` gerekir.

Ayri process dogrulamasi icin `scripts/a2a_two_process_smoke.py` var. Bu script tek departman agent service process'i baslatir, HTTP canary'yi calistirir, sonucu JSON basar ve process'i temiz kapatir. PowerShell ortam degiskeni mirasinda sorun yasandiginda manuel iki terminal yerine once bu runner tercih edilebilir. Finance varsayilan canary kisisel harc borcu auth-guard akisini kullanir; bu A2A sozlesmesini RAG cevap kalitesiyle karistirmadan test eder. Model cold-start sirasinda dispatch zaman asimina ugrarsa `--request-timeout 180` gibi daha uzun bir canary timeout'u kullan.

Ana orkestrator HTTP A2A dogrulamasi icin `scripts/a2a_main_http_smoke.py` var. Bu script finance agent service'i ayri process olarak baslatir, parent process'te `MainOrchestrator`'u HTTP mod davranisiyla calistirir ve `MainOrchestrator -> HttpA2A -> finance agent service` zincirini auth-guard finans sorusu ile test eder.

HTTP transport endpoint eksikligi veya remote servis baglanti hatasinda exception firlatmak yerine `DepartmentResponse(success=False, error="a2a_endpoint_missing|a2a_transport_failed")` dondurur. In-process transport hatalari saklanmaz; bu kontrollu davranis sadece remote A2A servis siniri icindir.

Docker A2A canary icin `Dockerfile`, `.dockerignore`, `docker-compose.a2a.yml` ve mevcut infra'ya baglanmak icin `docker-compose.a2a-existing-infra.yml` var. Overlay sadece `api` ve `agent-finance` servislerini ekler; tum departmanlari ayni anda bolmez. Bu finance-only bir mimari degil, dusuk riskli canary asamasidir. Mevcut-infra uzerinde ikinci asama icin `docker-compose.a2a-existing-infra-student.yml` finance'a ek olarak `agent-student-affairs` servisini acar. Tam rollout denemesi icin `docker-compose.a2a-full.yml` ek overlay'i `agent-student-affairs` ve `agent-academic` servislerini de acar. Academic service RAG/model yukleri nedeniyle en son ayrilmalidir. `docker compose ... config` `.env` secret'larini konsola basabilir, bu ciktiyi kullaniciya aynen aktarma.

Academic icin mevcut-infra uzerinde kontrollu overlay `docker-compose.a2a-existing-infra-academic.yml` eklendi. Bunu calistirmadan once model cache preflight yap; academic RAG/model cold-start finance/student'dan daha agir olabilir.

A2A compose dosyalarinda API ve agent servisleri ayni `university_support_system-app:latest` image'ini kullanir. Canary compose'larinda warmup kapali, embedding/reranker CPU'ya sabittir; bu testlerin amaci once HTTP A2A transport hattini dogrulamaktir. Model/RAG performansi ve Groq/OpenAI-compatible uretim kalitesi ayri olculmelidir.

Rollout gorunurlugu icin build metadata artik image seviyesinde tasinir: `Dockerfile` `APP_VERSION`, `BUILD_ID`, `BUILD_TIMESTAMP`, `GIT_SHA`, `IMAGE_REF` build arg'larini alip bunlari `SERVER_*` env'lerine bake eder. A2A compose overlay'leri bu arg'lari ortak sekilde gecer ve servis bazli `SERVER_RUNTIME_LABEL` atar; boylece calisan API/agent health'lerinden hangi build'in canli oldugu okunabilir.

Docker build davranisi da sadeleştirildi: A2A overlay'lerinde agent servislerinden `build:` bloklari kaldirildi, sadece `api` servisi shared image'i build eder. Finance/student/academic agent'lari ayni lokal `university_support_system-app:latest` image'ini kullanir. Bu hem ayni oturumda gereksiz coklu build'i azaltir hem de "neden ayni kod icin farkli image'lar olustu" karmasasini dusurur.

`Dockerfile` tarafinda BuildKit cache mount acildi. apt ve pip icin cache hedefleri tanimli; builder cache silinmedigi veya Docker tamamen sifirlanmadigi surece her rebuild'de dependency'lerin bastan inmesi beklenmez. Buna ragmen ilk cold build veya kayip builder cache durumunda yeniden indirme gorulebilir; bu altyapi davranisidir, kod regressionsu degildir.

2026-04-22 build notu: apt katmani pratikte cok yavas Debian indirmesine takilabildigi icin `build-essential` ve `curl` kurulumu varsayilan kapatildi. Dockerfile `INSTALL_BUILD_TOOLS=false` ile hizli wheel-based build yapar; yeni bir dependency native compile isterse `scripts.a2a_rollout --install-build-tools` veya `A2A_INSTALL_BUILD_TOOLS=true` ile apt araclari bilerek acilir.

Bu operasyon akisini standartlastirmak icin `scripts/a2a_rollout.py` eklendi. Script build metadata uretir, shared image'i bir kez build eder ve secili servisleri `--no-build` ile recreate eder. Varsayilan canary finance'tir; `--include-student` ve `--include-academic` ile tam department-level rollout kolayca tekrar edilebilir. Bundan sonra A2A Docker rollout'ta elle uzun compose komutlari yerine once bu script tercih edilmelidir.

2026-04-22 devam notu: `scripts.a2a_rollout` student ve academic uzman servislerini de destekler. Yeni bayraklar `--include-student-specialists`, `--include-academic-specialists` ve `--include-all-specialists`; specialist bayragi ilgili departman orkestratorunu otomatik dahil eder. Eklenen servisler student affairs icin `registration_agent`, `graduation_agent`, `internship_agent`, `student_life_agent`; academic programs icin `curriculum_agent`, `regulation_agent`, `international_agent`tir. Bu degisiklik lokal olarak dogrulandi: `py_compile` gecti, hedef A2A unit seti `70 passed` verdi ve tum existing-infra department/capability/specialist compose overlay'leri `docker compose ... config --quiet` ile schema seviyesinde gecti. Ilk Docker denemesinde daemon erisimi yoktu; Docker geri gelince normal build'li rollout 15 dakikalik terminal timeout'una takildi. Bu tur uygulama image'i gerektirmeyen compose/topoloji genisletmesi oldugu icin mevcut image ile `--skip-build --build-id codex-20260421-231619 --transport-protocol jsonrpc --include-announcement --include-event --include-all-specialists` kosuldu ve basarili oldu. Canli `/a2a/topology`: `agent_count=15`, `active_count=15`, `stale_count=0`, `a2a_transport_protocol=jsonrpc`. Public smoke: `Ders kaydı ne zaman başlıyor?` -> `student_affairs/vt`, `İkinci dönem dersleri ne?` -> `academic_programs/vt`, `Erasmus ile gelen öğrenci OMÜye geldiğinde kaydı nasıl yapılır?` -> `academic_programs/rag+llm`. Specialist loglarinda `registration_agent`, `curriculum_agent`, `international_agent` icin `POST /a2a HTTP/1.1" 200 OK` goruldu; yani department orchestrator -> specialist remote JSON-RPC hatti canli dogrulandi.

2026-04-22 sonraki dogrulama: `AgentResponse` semantik temizligi canli Docker image'a tasindi. Build id `codex-agent-response-20260422` ile `--transport-protocol jsonrpc --include-announcement --include-event --include-all-specialists` no-build recreate sonrasi 15/15 servis healthy oldu; `/a2a/topology` default cevap `agent_count=15`, `active_count=15`, `stale_count=0`, `a2a_transport_protocol=jsonrpc` verdi. Direct `registration_agent` JSON-RPC `/a2a` smoke'unda task metadata `response_schema=omu.agent_response.v1`, `legacy_response_schema=omu.department_response.v1`; structured data artifact `student_affairs_agent_response_data`, schema `omu.agent_response.v1`, extensions `omu.agent_response.v1, omu.department_response.v1` dondu. Public `/query` smoke'lari `Ders kaydi ne zaman basliyor? -> student_affairs/vt`, `Ikinci donem dersleri ne? -> academic_programs/vt`, `Guncel duyurular neler? -> announcement/vt` olarak gecti. Profil bilgileriyle API uzerinden `demo_showcase_stable_turk` benchmark'i `6/6 yonlendirme`, `6/6 kalite`, `0 hata` verdi. Profil verilmeden kosulan API benchmark'inin onboarding cevabina dusmesi beklenen davranistir; bunu A2A regresyonu diye okuma. Build sirasinda apt kurulumu gercekten atlandi (`INSTALL_BUILD_TOOLS=false`, apt RUN yaklasik 2 sn); ancak Docker base image ve pip cache cold oldugu icin ilk build yine uzun surebilir. Bu durumda sorun apt araclarindan degil, Docker builder/base/pip cache'in o makinede sicak olmamasindan kaynaklanir.

2026-04-22 mimari temizlik: published A2A service target modeli `src.api.agent_service` icinden `src.a2a.targets` modulune tasindi. `SpecialistTarget`, `AgentServiceTarget`, `resolve_agent_service_target` ve `agent_target_kind` artik API entrypoint'e gomulu degil; main/department/capability/specialist ayrimi ortak A2A katmanindan okunur. Schema stringleri de `src.a2a.schemas` icinde `AGENT_RESPONSE_SCHEMA`, `DEPARTMENT_RESPONSE_SCHEMA` ve `USER_QUERY_RESPONSE_SCHEMA` olarak merkezi hale getirildi. Lokal dogrulama: `py_compile` gecti; `tests/unit/test_a2a_rollout.py tests/unit/test_a2a_helpers.py tests/unit/test_agent_service.py tests/unit/test_api.py -q` toplam `71 passed` verdi. Canli Docker build `codex-a2a-targets-20260422` ile 29 sn surdu; base/apt/pip katmanlari `CACHED` geldi. Recreate sonrasi 15/15 servis healthy, `/a2a/topology` `agent_count=15`, `active_count=15`, `stale_count=0`, `a2a_transport_protocol=jsonrpc` dondu. Public `/query` smoke `Ikinci donem dersleri ne? -> academic_programs/vt`; main orchestrator direct `/a2a` JSON-RPC smoke `response_schema=omu.user_query_response.v1` ve `main_orchestrator_response_data` artifact schema'sini dogruladi.

2026-04-22 devam temizligi: A2A sinirinda aktif okuma yolu `extract_agent_response` semantigine cekildi. `extract_department_response` sadece legacy/backward-compatible alias olarak kalmali; yeni transport, capability, specialist ve orchestrator task okumalari generic AgentResponse adini kullanmali. Lokal dogrulama: `py_compile` gecti; `tests/unit/test_a2a_helpers.py tests/unit/test_agent_service.py tests/unit/test_orchestrators.py tests/unit/test_api.py -q` toplam `99 passed` verdi. Bu davranis degisikligi degil, isim/contract tutarliligi temizligidir. Canli Docker build `codex-a2a-extract-agent-20260422` ile cache'li gecti; base/apt/pip katmanlari `CACHED`, sadece `src` ve `data` katmanlari yenilendi. No-build recreate sonrasi 15/15 servis ayni build id ile healthy oldu, `/a2a/topology` `agent_count=15`, `active_count=15`, `stale_count=0`, `a2a_transport_protocol=jsonrpc` dondu. Public `/query` smoke `Ikinci donem dersleri ne? -> academic_programs/vt`; direct main `/a2a` JSON-RPC smoke `response_schema=omu.user_query_response.v1`, `main_orchestrator_response_data` artifact schema `omu.user_query_response.v1` olarak gecti.

2026-04-22 AgentCard siniri temizligi: published service card ve standart A2A AgentCard uretimi `src.api.agent_service` icinden `src.a2a.agent_cards` modulune tasindi. `agent_service` eski importlari geriye uyumlu tutar ama yeni A2A card/discovery semantigi ortak A2A katmanindan okunmali. Bu da davranis degisikligi degil; servis entrypoint dosyasini inceltme ve A2A contract kodunu API'den ayirma adimidir. Lokal dogrulama: `py_compile` gecti; hedef suite `99 passed` verdi. Canli Docker build `codex-a2a-agent-card-20260422` cache'li gecti; base/apt/pip katmanlari `CACHED`. No-build recreate sonrasi 15/15 servis ayni build id ile healthy oldu. `/a2a/topology`: `agent_count=15`, `active_count=15`, `stale_count=0`, `a2a_transport_protocol=jsonrpc`. Public `/query` smoke `Ikinci donem dersleri ne? -> academic_programs/vt`, direct main `/a2a` schema smoke `omu.user_query_response.v1`, finance tuition AgentCard smoke `name=OMU Tuition Agent`, `skill_id=tuition_agent` olarak gecti.

2026-04-22 execution siniri temizligi: agent service icindeki department/capability/specialist JSON-RPC ve legacy dispatch yurutme mantigi `src.api.agent_service_execution` modulune tasindi. `src.api.agent_service` artik daha cok FastAPI yuzeyi, metrics ve presence/registry sorumlulugunu tasir; handler yurutme fonksiyonlari yeni moduldedir. Bu is sirasinda Docker healthcheck'te ince bir dayaniklilik problemi yakalandi: `/health` registry presence refresh'i beklerken Postgres/DNS yavas ise 3 sn healthcheck timeout'una dusuyordu. Presence refresh artik best-effort ve 1 sn timeout'lu; health/card/dispatch endpointleri registry yavasligina bagimli olarak unhealthy olmamali. Lokal hedef suite `99 passed` verdi. Canli Docker build `codex-a2a-execution-health-20260422` cache'li gecti; base/apt/pip `CACHED`. Ilk recreate health timeout yuzunden basarisiz oldu, health/presence fix sonrasi no-build recreate 15/15 health OK verdi. Topology `agent_count=15`, `active_count=15`, `stale_count=0`, `a2a_transport_protocol=jsonrpc`; public academic VT smoke, main `/a2a` schema smoke ve tuition AgentCard smoke basarili.

Script artik rollout sonrasi health endpoint'lerini de poll eder ve beklenen `build_id` yeni health cevabinda gorulmeden basarili saymaz. Yani A2A Docker rollout dogrulamasinda sadece container'in "started" olmasi yeterli kabul edilmez; dogru build'in canli yuzeye cikmasi da kontrol edilir.

Ek olarak script artik legacy image adaylarini da tanir. Varsayilan davranis raporlama yapmaktir; eski `university_support_system-api` veya `university_support_system-agent-*` image'lari ancak `--cleanup-legacy-images` verilirse silinir. Bu, temizlik operasyonunu gorunur ve kontrollu tutar.

Docker mevcut-infra canary dogrulamasi yapildi: `docker-compose.a2a-existing-infra.yml config --quiet` gecti; `uni_a2a_agent_finance` healthy oldu; API `/health` `a2a_mode=http` ve Groq primary healthy dondu; public `/query` profil metadata'siyle "Harc borcum ne kadar?" sorgusunda `departments_involved=["finance"]` ve auth guard cevabi dondu. Finance agent logunda `POST /a2a/dispatch HTTP/1.1 200 OK` goruldu; yani `MainOrchestrator -> HTTP A2A -> finance agent service` Docker uzerinde dogrulandi.

Finance + student affairs mevcut-infra canary de denendi: `docker-compose.a2a-existing-infra.yml -f docker-compose.a2a-existing-infra-student.yml config --quiet` gecti, `agent-student-affairs` healthy oldu ve multi-department sorguda hem student affairs hem finance agent loglarinda `POST /a2a/dispatch HTTP/1.1 200 OK` goruldu. Ilk denemede student affairs RAG aramasinda container icinde `BAAI/bge-m3` cache yolu yanlis oldugu icin model yuklenemedi; dogru cozum `MODEL_CACHE_HOST_DIR` ile host `.cache` dizinini `/models` altina baglamak ve `SENTENCE_TRANSFORMERS_HOME=/models/huggingface/hub` kullanmak. Bu ayarla `BAAI/bge-m3` offline yuklendi, sicak multi-department sorguda student affairs `RAG + LLM` ve finance `VT` cevabi birlikte dondu. Cold-start ilk sorguda 10 sn A2A timeout'a takilabildigi icin Docker canary API timeout'u 30 sn tutulmali.

Academic programs mevcut-infra canary de finance/student ile ayni A2A API altinda denendi: `docker-compose.a2a-existing-infra-academic.yml` overlay'iyle `agent-academic` healthy oldu; "ikinci donem dersleri ne" sorgusu `departments_involved=["academic_programs"]`, `generation_modes=["vt"]` ve 2. yariyil dersleri cevabiyla dondu. Academic agent logunda `/a2a/dispatch 200 OK` goruldu. Bu test academic VT yolunu ve HTTP transport'u dogrular; academic RAG/LLM kalitesi ve cold-start maliyeti ayrica olculmelidir.

Academic RAG/LLM smoke da calistirildi: "Erasmus ile gelen ogrenci OMUye geldiginde kaydi nasil yapilir?" sorgusu HTTP A2A uzerinden `academic_programs`, `rag+llm` ve 3 kaynakla dondu; agent logunda BGE, reranker, Chroma ve Groq cagrilari goruldu. Teknik zincir calisiyor, ancak cevap kalitesi sorunlu: gelen Erasmus kaydi sorusunda giden ogrenci/hibe parcalari one cikti ve cevap hem prosedur uretip hem "net bilgi bulunamadi" dedi. Bu A2A transport hatasi degil; InternationalAgent retrieval/ranking veya answer-consistency borcu olarak izlenmeli. Ozellikle incoming exchange ranking tam icerik/metadata uzerinden yapilmali; sadece ilk karakter penceresi incoming basligini kacirabilir.

Bu incoming Erasmus kalite borcu icin kaynak ranking kurali guclendirildi: sadece "Gelen Erasmus ogrencileri" basligi yeterli sayilmiyor; "kayitlari ilgili bolum", "Ogrenci Isleri Otomasyon", "ogrenci numarasi" ve "ogrenci kimlik karti" gibi gercek incoming prosedur sinyalleri daha ust siraya aliniyor. Teste, hibe chunk'inin sonunda incoming basligi yapisik olsa bile gercek incoming kayit chunk'inin secilmesi senaryosu eklendi. Bu kod degisikligi Docker image rebuild edilmeden calisan container'a yansimaz.

2026-04-21'de latest kodu Docker canary'ye yansitmak icin `docker compose ... up --build -d api agent-academic` denendi ancak 10 dakika timeout'a dustu. Mevcut `uni_a2a_api` ve agent container'lari dusmedi/healthy kaldi, fakat recreate olmadi; dolayisiyla canli Docker academic servisi bu ranking fix'ini henuz icermiyor. Bir sonraki Docker dogrulamasi oncesi build sureci ayri ele alinmali veya cache durumunu gormek icin `docker compose build --progress=plain api` kontrollu calistirilmali.

2026-04-21'de Docker rebuild cache'li sekilde tekrar alindi: `docker compose ... build api` bu kez apt/pip katmanlarini cache'den kullandi, sadece `src` ve `data` katmanlari yeniden kopyalandi ve image hizli sekilde guncellendi. Ardindan `docker compose ... up --no-build -d api agent-academic` ile A2A API ve academic agent yeni image ile recreate edildi; compose bagimlilik nedeniyle finance ve student affairs agent'lari da birlikte recreate etti.

Bu rebuild sonrasi ayni canli HTTP A2A smoke tekrar denendi: `POST http://localhost:8000/query` uzerinden "Erasmus ile gelen ogrenci OMUye geldiginde kaydi nasil yapilir?" sorgusu artik `departments_involved=["academic_programs"]`, `generation_modes=["rag"]` ve dogru incoming source ile dondu. Cevapta `uluslararasi_isbirlikleri_protokoller...` kaynagindan gelen degisim ogrencilerinin kayitlarinin ilgili bolum tarafindan Ogrenci Isleri Otomasyon Sistemine yapildigi, ogrenci numarasi verildigi ve kimlik karti cikarildigi bilgileri yer aldi. Yani duzeltme soru-ozel statik cevap degil; incoming exchange prosedur sinyali + ayni MADDE alt parcalarini merge eden enrichment + source-only guard birlesimiyle calisti.

Bu incoming Erasmus duzeltmesinin genel mantigi: tek bir phrase'e ozel cevap yapistirmak degil, ayni konu icindeki `basvuru / kayit / ders secimi / taninma` gibi prosedur asamalarini ve `giden / gelen` ayrimini kaynak siralamasinda ayirt etmek. Real document'ta registration bilgisi ayni MADDE'nin alt parcalarinda geldigi icin `enrich_results` sonrasi siralama kontrol edilmelidir; ham Chroma preview tek basina yanlis sonuca goturebilir.

Docker smoke sirasinda `GET /health` API health cevabinda Groq primary `unhealthy` gorundu. Incoming Erasmus sorgusu buna ragmen gecti cunku uzman ajan LLM sentezine gitmeden `RAG` source-only cevabi uretti. LLM'e bagimli kalite testlerinde Groq/network durumu ayrica dogrulanmali; bu sonuc A2A transport veya retrieval fix'inin bozuk oldugu anlami tasimaz.

2026-04-21'de kontrollu agent-down smoke da yapildi. `uni_a2a_agent_finance` container'i gecici olarak durduruldu ve coklu route edilen "Kayit yenileme doneminde harc ucretimi yatirdiktan sonra ders kaydini nasil yapacagim, danismanin onay sureci nasil isliyor?" sorgusu `POST /query` ile tekrar kosuldu. Sonuc beklenen gibi degrade oldu: `student_affairs` branch'i `RAG + LLM` cevap dondurmeye devam etti, `finance` branch'i ise `Finans agent servisine su anda ulasilamadi` seklinde kontrollu `kural` fallback'i verdi. Sistem tamamen patlamadi ve tek bir down agent tum parallel cevabi bozmadı.

Bu testten sonra `uni_a2a_agent_finance` yeniden baslatildi; `GET http://localhost:8103/health` `status=ok` dondu ve container tekrar `healthy` oldu. A2A HTTP modunda parallel branch hata toleransi temel seviyede dogrulandi; sonraki adim shadow karsilastirmalarini temsilci soru setiyle genisletmek olabilir.

2026-04-21'de shadow mode temsili soru setiyle de olculdu. Ilk denemede tum remote shadow branch'ler `a2a_transport_failed` gorunuyordu; root cause cevap kalitesi degil, local shadow parent'in Docker agent servislerine `X-Internal-API-Key` gondermemesiydi. Compose tarafinda `local-a2a-secret` kullanildigi icin local testte `settings.server.internal_api_key` ve `settings.a2a.internal_api_key` ayni degerle set edilince `academic_vt`, `academic_incoming_exchange`, `student_affairs` ve `finance` branch'lerinde in-process ile HTTP shadow sonuclari tekrar hizalandi.

Shadow testinde ikinci ve daha ince bir auth farki daha bulundu: finance gibi kisisel veri sorularinda in-process yol parent'in dogrulanmis `student_id` baglamini kullanirken, remote agent service `resolve_auth_inputs` icinde session/slack mapping olmadigi durumda `student_id` ve `is_authenticated=True` bilgisini dusuruyordu. Bu yuzden finance auth query shadow branch'i `authentication_required` fallback'ine dusuyordu. Cozum soru-ozel degil, genel bir ic-dispatch auth duzeltmesi oldu: internal A2A dispatch icin `resolve_auth_inputs(..., allow_trusted_identity_claims=True)` yolu eklendi ve bu sadece internal API key ile korunan dispatch hattinda acildi. Public `/query` akisi degismedi.

Bu auth forwarding duzeltmesi sonrasi `tests/unit/test_agent_service.py` ve `tests/unit/test_a2a_helpers.py` gecti; Docker image rebuild edilip agent servisleri recreate edildikten sonra `Harc borcum ne kadar?` shadow retest'inde `primary_success=True`, `shadow_success=True` ve `same_answer=True` goruldu. Yani department-level A2A icin olculen temsilci shadow senaryolarinda ana fark artik transport/auth katmanindan degil, gercekten kalite farki varsa ancak icerik seviyesinde aranmalidir.

2026-04-21'de canli benchmark araci da iyilestirildi. `scripts/live_question_test.py` API modunda artik `httpx` varsayilan 5 saniyelik timeout yerine 30 saniye kullanir; bu sayede agir RAG/LLM sorularinda sahte `ReadTimeout` benchmark hatalari azalir. Ayrica exception formatlamasi zenginlestirildi; bos `HATA:` yerine exception tipi, request ve varsa HTTP status/body bilgisi yazdirilir. Bu bir urun davranisi degisikligi degil, tanilama araci duzeltmesidir.

Ayni gun canli HTTP A2A API uzerinden profil baglamiyla benchmark tekrar olculdu. `demo_showcase_stable_turk` seti `6/6 yonlendirme`, `6/6 kalite`, `0 hata` verdi. Bu, department-level A2A'nin demo/stable soru setinde guvenli calistigini gosterir.

`demo_showcase_broad_turk` seti timeout fix'inden sonra `9/11 yonlendirme`, `11/11 kalite`, `0 hata` verdi. Kalan iki fark A2A tasima hatasi degil, urun policy/routing backlog'udur:

- `Devam zorunlulugu var mi?` mevcutte `student_affairs + academic_programs` route oluyor. Devam/devamsizlik gibi genel ogrenci haklari sorulari `student_affairs` merkezli olmali; burada policy ve benchmark beklentisi tekrar hizalanmali.
- `Burs basvurusu ne zaman?` mevcutte `finance + announcement`e gidiyor. Announcement branch burs duyurularini yakaliyor ama bazen alakasiz bir `basvuru` duyurusunu da one cikarabiliyor. Bu, announcement retrieval / query intent precision borcu olarak ele alinmali; A2A transport problemi degildir.

2026-04-21'de A2A HTTP transport hardening de yapildi. `A2ASettings` icine `retry_count` ve `retry_backoff_seconds` eklendi. `HttpA2ADepartmentTransport` artik timeout, `httpx.RequestError` ve retryable `HTTPStatusError` (`502/503/504`) durumlarinda kontrollu retry uygular; `403/404` gibi kalici hatalarda gereksiz tekrar yapmaz. Timeout ve genel ulasilamiyor fallback cevaplari korunur. Bu degisiklik `tests/unit/test_a2a_helpers.py` ile su davranislar icin dogrulandi:

- timeout sonrasi ikinci denemede basarili donme,
- `403` gibi retry edilmemesi gereken HTTP statuslerinde tek denemede kontrollu failure,
- mevcut timeout / endpoint missing / connection failure fallback'lerinin korunmasi.

Ayni hardening turunda hafif bir circuit-breaker/cooldown da eklendi. `A2A_CIRCUIT_BREAKER_THRESHOLD` ve `A2A_CIRCUIT_BREAKER_COOLDOWN_SECONDS` ayarlari ile ayni endpoint ard arda gecici hataya dusuyorsa transport kisa sure o servise yeni HTTP istek gondermeden `a2a_circuit_open` fallback'i dondurur. Bu devre sadece timeout / `RequestError` / retryable `5xx` tiplerinde acilir; `403` gibi kalici hatalar circuit'i trip etmez. `tests/unit/test_a2a_helpers.py` icine "iki kez baglanti hatasi -> ucuncu cagri circuit open" testi eklendi ve gecti.

Bu hardening sonrasi `tests/unit/test_a2a_helpers.py` + `tests/unit/test_agent_service.py` toplam 18 test gecti. Hafif canli smoke olarak `GET /health` tekrar `a2a_mode=http` ve Groq healthy dondu; `Ders kaydi ne zaman basliyor?` sorgusu da student affairs HTTP A2A yolunda normal sekilde cevap verdi. Yani retry + circuit-breaker eklenmesi mevcut HTTP A2A akislarini bozmus gorunmuyor.

Local `.env` icine `MODEL_CACHE_HOST_DIR=C:/Users/ÖMER FARUK DERİN/.cache` eklendi ve compose gecici PowerShell env olmadan bu mount'u kullanarak dogrulandi. Dockerfile'da model cache env'leri dependency install katmanindan sonra tanimlandi; boylece ileride cache/env degisikligi pip install katmanini gereksiz invalidate etmesin.

Model cache preflight icin `scripts/a2a_model_cache_check.py` eklendi. Healthcheck yerine deployment oncesi elle/CI'da calistirilmali; embedding ve reranker model artefact'lerinin `local_files_only` ayarlariyla yuklenebildigini JSON olarak raporlar.

HTTP A2A transport timeout hatalarini baglanti/servis yok hatalarindan ayirir. `httpx.TimeoutException` durumunda `a2a_transport_timeout` ve "agent servisi zamaninda yanit veremedi" mesaji doner; connection/HTTP diger hatalar `a2a_transport_failed` olarak kalir.

2026-04-21'de discovery/registry tarafinda da ilk gercek adim atildi. `agent_registry` tablosunda zaten bulunan `endpoint` ve `capabilities` alanlari artik A2A icin aktif kullaniliyor:

- `TelemetryService.ensure_agent(...)` `endpoint` ve `capabilities` alabilir; bu alanlar verilmediginde mevcut kaydi bosaltmaz.
- `create_agent_service_app(...)` startup'ta ve her internal dispatch oncesinde kendi departman orkestrator kaydini `agent_registry` icine `endpoint + capabilities` ile yazar.
- Bu `capabilities` payload'i artik `service_build` ve `service_runtime_label` metadata'sini de icerir. Yani registry kaydina bakarak da endpoint'in hangi build/runtime etiketiyle yayinlandigi gorulebilir; rollout kontrolu sadece health endpoint'ine bagli kalmaz.
- `HttpA2ADepartmentTransport` endpoint cozumlerken once `A2A_*_URL` env degerine bakar; env bos ise `agent_registry` icinden ayni departmanin en guncel `department_orchestrator` endpoint'ini discovery fallback olarak kullanir.

Bu discovery mekanizmasi henuz tam TTL/health tabanli dynamic registry degil; env override hala onceliklidir. Ama artik HTTP A2A icin "endpoint mutlaka env'de olmali" zorunlulugu kirilmistir. Bu fark cevap optimizasyonu degil, dogrudan A2A altyapi sertlestirmesidir.

2026-04-21'de discovery katmani bir adim daha sertlestirildi: `A2A_DISCOVERY_TTL_SECONDS` eklendi ve `TelemetryService.resolve_department_endpoint(...)` artik stale heartbeat'li registry endpoint'lerini yok sayiyor. Yani registry'de kayit gorunse bile `last_heartbeat` cok eskiyse transport onu aktif servis gibi kullanmiyor.

Ayni turda `agent_service` tarafinda `/health` ve `/agent-card` endpoint'leri de `register_presence()` cagirir hale getirildi. Boylece servis sadece startup'ta ve dispatch alinca degil, health/card trafiklerinde de heartbeat tazeler. Bu, discovery'nin yalanci stale vermesini azaltir ve Docker / smoke / service monitor akislariyla daha uyumludur.

Discovery bundan sonra sadece registry satirina bakmiyor: 2026-04-21'de `HttpA2ADepartmentTransport` registry'den cozulmus endpoint'i kullanmadan once kisa bir `/health` probe'u yapar hale getirildi. Bu davranis `A2A_DISCOVERY_HEALTHCHECK_ENABLED`, `A2A_DISCOVERY_HEALTHCHECK_TIMEOUT_SECONDS` ve `A2A_DISCOVERY_HEALTHCHECK_CACHE_SECONDS` ile ayarlanir. Health sonucu kisa sure cache'lenir; healthy endpoint tekrar tekrar probe edilmez, unhealthy endpoint ise dispatch'e gecmeden elenir.

Bu turda ek testler de eklendi: `tests/unit/test_agent_service.py` agent service startup'inda registry'ye endpoint yazimini; `tests/unit/test_a2a_helpers.py` ise env endpoint olmadiginda registry fallback discovery ile HTTP dispatch'i dogruluyor. 2026-04-21 itibariyla `tests/unit/test_a2a_helpers.py` + `tests/unit/test_agent_service.py` birlikte `20 passed` verdi.

Ek olarak `tests/unit/test_telemetry.py` ile discovery helper'inin fresh endpoint, stale endpoint ve heartbeat olmayan kayit davranislari da sabitlendi. Bu noktadan sonra discovery "env -> registry fresh endpoint -> yoksa fallback failure" sirasiyla dusunulmeli.

Health-verified discovery eklendikten sonra `tests/unit/test_a2a_helpers.py` + `tests/unit/test_agent_service.py` + `tests/unit/test_telemetry.py` toplam `26 passed` verdi. Hafif canli smoke'ta API health yine `a2a_mode=http` ve Groq healthy dondu; `Ders kaydi ne zaman basliyor?` sorgusu da normal student affairs VT cevabiyla calisti. Bu degisiklik mevcut HTTP A2A akislarini bozmus gorunmuyor.

2026-04-21'de build metadata health yuzeyine de tasindi: API root `/`, API `/health` ve agent service `/health` + `/agent-card` artik `version/build_id/build_timestamp/git_sha/image_ref` metadata'sini dondurur. Bu, "kod guncellendi mi / hangi image calisiyor" sorusunu endpoint cevabindan gormeyi saglar; rollout belirsizligini azaltir.

Bu turda `py_compile` ve `tests/unit/test_api.py`, `tests/unit/test_agent_service.py`, `tests/unit/test_a2a_helpers.py`, `tests/unit/test_telemetry.py` birlikte 39 test gecti. Ayni zamanda tum aktif A2A compose kombinasyonlari `docker compose ... config --quiet` ile de schema olarak gecti.

Ayni gun bu metadata'yi canli container'larda dogrulamak icin rebuild/recreate tekrar baslatildi, ancak oturum kullanici tarafindan kesildi. Ertesi devam turunda Docker daemon'a erisilemedigi icin canli rebuild tamamlanamadi; dolayisiyla yerel kod/compose hazir olsa da health cevabinda yeni build alanlarini canli Docker uzerinde tekrar gormek icin Docker geri geldikten sonra `build` + `up --no-build` adimi yeniden kosulmali.

One-off gercek DB smoke ile de `student_affairs_orchestrator` kaydinin `http://localhost:8102` endpoint'i ve `omu.department_response.v1` capability bilgisiyle guncellendigi goruldu. Yani discovery verisi sadece unit testte degil, canli `agent_registry` kaydinda da yazilabiliyor.

Shadow mode artik daha olculebilir: `ShadowDepartmentTransport.wait_for_pending()` smoke testlerde background karsilastirmanin bitmesini beklemek icin var; logda context, primary/shadow success, mode, source sayisi, error, cevap uzunlugu, same_answer ve elapsed_ms bulunur. `scripts/a2a_main_shadow_smoke.py` finance agent service'i ayri process olarak baslatip `MainOrchestrator`'i `A2A_MODE=shadow` ile test eder. 2026-04-21'de `--port 8113 --internal-key local-a2a-secret` ile calisti; main cevap in-process auth guard olarak dondu, shadow pending task 0'a indi ve agent logunda `/a2a/dispatch 200 OK` goruldu.

Gercek A2A gecisinde hedef:

- `MainOrchestrator` departmanlari dogrudan import ederek cagirmamali; once transport abstraction, sonra HTTP A2A client kullanmali.
- A2A servisleri genel `AgentResponse` artifact sozlesmesini dondurmeli; mevcut Python payload'i geriye uyum icin `DepartmentResponse` modeliyle okunabilir kalmali.
- In-process yol demo ve gelistirme icin `A2A_MODE=inprocess` olarak korunur. `A2A_MODE=http` veya `A2A_SPECIALIST_MODE=http` secildiginde gizli local fallback calismamali; remote endpoint yoksa/hata verirse structured `success=False` A2A cevabi uretilmelidir.
- Slack yine sadece adapter kalmali; A2A Slack katmanina tasinmamali.
- BGE/reranker gibi agir modeller her servis tarafindan ayri ayri yuklenirse RAM/VRAM maliyeti artar; geciste RAG/model yukleme stratejisi ozellikle kontrol edilmeli.

2026-04-21 mimari karari guncellendi: `announcement` ve `event` artik local helper akisi olarak kalmayacak; ayri capability agent/service hedefi resmi hale geldi. Bu karar koda da yansitildi: `agent_service` capability target'larini (`announcement`, `event`) ayaga kaldirabiliyor, `EventAgent` eklendi, `announcement/event` icin HTTP capability transport eklendi ve mevcut-infra Docker overlay'ine `agent-announcement` + `agent-event` servisleri eklendi. Bundan sonra A2A dusunulurken sadece department-level degil, **department orchestrator + capability agent** topolojisi esas alinmali.

2026-04-21 aksaminda bu capability gecisi canli Docker ortaminda da smoke edildi. `python -m scripts.a2a_rollout --include-announcement --include-event` sonrasi:

- `http://localhost:8104/health` -> `service=agent-announcement`, `capability=announcement`
- `http://localhost:8105/health` -> `service=agent-event`, `capability=event`
- `http://localhost:8000/health` -> API healthy, `a2a_mode=http`

Ardindan profil baglamli public `/query` istekleri ile iki gercek senaryo kosuldu:

- `Guncel duyurular neler?` -> `departments_involved=["announcement"]`
- `Bu hafta etkinlik var mi?` -> `departments_involved=["event"]`

En kritik teyit: ilgili container loglarinda her iki capability servisi icin de `POST /a2a/dispatch ... 200 OK` satiri goruldu. Yani announcement/event su anda yalnizca local fallback degil; ana API bunlari gercek HTTP A2A capability servisi olarak kullanabiliyor.

Ayni gece full dagitik rollout da tamamlandi: `python -m scripts.a2a_rollout --include-student --include-academic --include-announcement --include-event`. Sonuc olarak asagidaki servislerin tamami ayni build ile healthy oldu:

- `api`
- `agent-finance`
- `agent-student-affairs`
- `agent-academic`
- `agent-announcement`
- `agent-event`

Build metadata: `build_id=codex-20260421-193903`.

Bu full topoloji uzerinde profil baglamli bes temsilci smoke query de gecti:

- `Ders kaydi ne zaman basliyor?` -> `student_affairs`
- `Erasmus ile gelen ogrenci OMUye geldiginde kaydi nasil yapilir?` -> `academic_programs`
- `Harc ucreti ne kadar?` -> `finance`
- `Guncel duyurular neler?` -> `announcement`
- `Bu hafta etkinlik var mi?` -> `event`

Bu nokta onemli: A2A tarafinda artik yalnizca tekil canary degil, **department orchestrator + capability agent** topolojisinin tamami ayni anda canli Docker ortaminda smoke edilmis durumda.

Acik kalan ana operasyonel borc: full rollout build'i halen pratikte cache'den yeterince yararlanmiyor; apt/pip dependency katmanlari yeniden indirilmis gorundu. Bu, mimari dogrulama problemi degil ama deployment hizi/maliyeti problemi olarak not edilmeli.

Bu cache probleminin muhtemel root cause'u da 2026-04-21 gecesi netlestirildi: Dockerfile'da `BUILD_ID`, `BUILD_TIMESTAMP`, `GIT_SHA`, `IMAGE_REF` gibi her rollout'ta degisen build metadata arg/ENV'leri dependency install katmanlarindan once tanimliydi. `scripts.a2a_rollout` her seferinde yeni `build_id` urettigi icin bu metadata degisimi apt/pip katmanlarini da invalidate ediyordu. Cozum olarak build metadata ENV'leri Dockerfile'in sonuna tasindi; boylece sonraki rollout'larda metadata degisse bile `requirements.txt` ayni kaldigi surece pip/apt katmanlari yeniden kosmamalidir. APT `update` metadata trafiginin bir kismi yine gorulebilir, fakat asıl pahali olan tam dependency reinstall'in kesilmesi beklenir.

Bu duzeltme ayni gece iki ard arda `--build-only` rollout ile canli Docker builder uzerinde dogrulandi. Ilk build, Dockerfile katman zinciri degistigi icin bir kere daha cold cost odedi; hemen sonraki ikinci build ise yeni `build_id` degismesine ragmen `apt` ve `pip` katmanlarini tamamen `CACHED` olarak kullandi ve yaklasik 14 saniyede tamamlandi. Yani sorun builder'in genel olarak cache tutamamasindan degil, bizim metadata'yi Dockerfile'in cok erken safhasinda set etmemizden kaynaklaniyormus.

2026-04-21 gecesinde A2A gorunurlugu icin public admin endpoint de eklendi: `GET /a2a/topology`. Bu endpoint `agent_registry` kayitlarini tek JSON cevapta toplar ve su bilgileri verir:

- `a2a_mode`
- `discovery_ttl_seconds`
- `agent_count`, `active_count`, `stale_count`
- her agent icin `agent_id`, `department`, `role`, `endpoint`, `last_heartbeat`, `is_stale`
- varsa `service_build` ve `service_runtime_label`

Bu endpoint canli Docker stack'te rollout sonrasi dogrulandi ve `department orchestrator` servisleri ile `announcement/event` capability servislerinin ayni `build_id=codex-20260421-200951` altinda calistigi goruldu. Ayni ciktida stale olan kayitlarin cogu local specialist agent kayitlari; yani stale sayisi tek basina hata anlamina gelmiyor, "HTTP servis olarak yayinlanan agent" ile "lokal specialist kaydi" ayrimina bakarak yorumlanmali.

Ardindan `/a2a/topology` varsayilan gorunumu sadeleştirildi: artik default cevap yalnizca endpoint'i olan gerçek A2A servislerini listeler. Local/internal specialist registry kayitlarini gormek icin `GET /a2a/topology?include_internal=true` kullanilir. Canli dogrulama sonucu:

- default `/a2a/topology`: `agent_count=5`, `active_count=5`, `stale_count=0`
- `include_internal=true`: `agent_count=15`, `active_count=15`, `stale_count=10`

Default listedeki 5 servis: `academic_programs_orchestrator`, `announcement_agent`, `event_agent`, `finance_orchestrator`, `student_affairs_orchestrator`. Bu, operasyon aninda ana A2A servis sagligini stale internal kayitlarla karistirmadan okumayi saglar.

2026-04-21 devam notu: lokal `scripts/live_question_test.py --use-api` calistirilirken `src.api.__init__` paketinin `src.api.main`i eager import etmesi yeni capability transport/import zinciriyle circular import uretti. Genel kural olarak `src.api.__init__` side-effect free kalmali; FastAPI app yalnizca lazy `__getattr__` ile yuklenmeli. Bu soru-bazli degil, mimari import siniri: `src.api.a2a_dispatch` gibi saf schema/helper submodule'leri `MainOrchestrator` importunu tetiklememeli.

Bu duzeltmeden sonra ayni canli Docker HTTP A2A stack uzerinde:

- `tests/unit/test_api.py`: 15/15 gecti.
- `demo_showcase_stable_turk --use-api`: 6/6 yonlendirme, 6/6 kalite.
- `kategori 8 --limit 1 --use-api`: event capability 1/1 dogru yonlendi; uygun event kaydi olmadigi icin kontrollu "kayit bulunamadi" cevabi verdi.

Yeni benchmark artefaktlari `tests/live_test_results_20260421_204902.json`, `tests/live_test_profile_20260421_204902.json`, `tests/live_test_results_20260421_204925.json`, `tests/live_test_profile_20260421_204925.json` olarak olustu.

2026-04-21 son A2A turunda protokol yuzeyi `JSON-RPC message/send` hattina tasindi ve canli Docker stack uzerinde dogrulandi. `A2A_TRANSPORT_PROTOCOL=rest|jsonrpc` ayari eklendi; default `rest` kalir, `jsonrpc` secilirse department, capability ve specialist HTTP transportlari internal `/a2a/dispatch` yerine `POST /a2a` JSON-RPC `message/send` kullanir. Agent servisleri `/.well-known/agent.json`, `/.well-known/agent-card.json` ve `POST /a2a` yuzeylerini sunar; eski `/a2a/dispatch` geriye uyum icin korunur.

Canli rollout komutu su sekilde kosuldu: `python -m scripts.a2a_rollout --transport-protocol jsonrpc --include-student --include-academic --include-announcement --include-event --include-finance-specialists --health-timeout-seconds 180`. Son final build `build_id=codex-20260421-231619` ile `api`, `agent-finance`, `agent-student-affairs`, `agent-academic`, `agent-announcement`, `agent-event`, `agent-finance-tuition`, `agent-finance-scholarship` healthy oldu. `/a2a/topology` default cevapta `agent_count=8`, `active_count=8`, `stale_count=0`, `a2a_transport_protocol=jsonrpc` verdi; yani 1 main orchestrator + 3 departman orkestratoru + 2 capability agent + 2 finance specialist published servis olarak gorunuyor.

Smoke dogrulamalari:

- `GET http://127.0.0.1:8110/.well-known/agent.json` artik `OMU Tuition Agent` dondurur; `Agent Agent` tekrar hatasi merkezi isimlendirme helper'iyle giderildi.
- Direct JSON-RPC smoke: `POST http://127.0.0.1:8103/a2a` + `message/send` -> `state=completed`, structured artifact `department=finance`, `generation_mode=vt`.
- Main orchestrator JSON-RPC smoke: `POST http://127.0.0.1:8000/a2a` + `message/send` -> `state=completed`, structured artifact schema `omu.user_query_response.v1`, `departments_involved=["event"]`, `generation_modes=["vt"]`.
- Public API smoke: `POST /query` icinde `Finans harc borcumu nasil odeyebilirim?` -> `departments_involved=["finance"]`, `generation_modes=["vt"]`.
- Announcement/event unutulmadi: AgentCard endpointleri `OMU Duyurular Agent` ve `OMU Etkinlikler Agent` olarak ayri capability servislerini donduruyor. Son build'de profilli public API smoke `Guncel duyurular neler?` -> `departments_involved=["announcement"]`, `Bu hafta etkinlik var mi?` -> `departments_involved=["event"]` verdi; iki container logunda da `POST /a2a HTTP/1.1" 200 OK` goruldu.

Build cache davranisi da son rolloutlarda dogrulandi: `apt` ve `pip` dependency katmanlari `CACHED` geldi; sadece `src`/`data` gibi degisen uygulama katmanlari yeniden paketlendi. Bundan sonra paketlerin her rebuild'de yeniden inmesi beklenmez; Docker builder cache silinirse veya dependency dosyalari degisirse yeniden indirme normaldir.

Bu turda calisan dogrulamalar: `py_compile` ilgili A2A dosyalari icin gecti; `tests/unit/test_agent_service.py`, `tests/unit/test_a2a_helpers.py`, `tests/unit/test_a2a_rollout.py`, `tests/unit/test_orchestrators.py`, `tests/unit/test_api.py`, `tests/unit/test_config.py` toplam `117 passed` verdi. Son isim duzeltmesi sonrasi hedef A2A testleri tekrar `47 passed` verdi. Capability JSON-RPC transport ekinden ve main orchestrator A2A server yuzeyinden sonra `tests/unit/test_a2a_helpers.py tests/unit/test_agent_service.py tests/unit/test_api.py -q` tekrar kosuldu ve `60 passed` verdi. Bilinen uyarilar: pytest cache dizini Windows izin uyarisi ve agent service registry startup testindeki coroutine cleanup warning; bunlar bu A2A protokol degisikliginden kaynaklanmiyor.

Mimari not: capability ve specialist agent'lar ayri servis olarak dogru publish ediliyor ve JSON-RPC uzerinden cagriliyor. Response artifact semantigi generic `omu.agent_response.v1` olarak baslatildi; `DepartmentResponse` zarf/payload'i ve `omu.department_response.v1` legacy extension'i geriye uyumluluk icin korunuyor. Bu cevap optimizasyonu degil, protokol semantigi temizligidir; yeni A2A entegrasyonlari legacy department schema'ya degil generic agent schema'ya bakmali.

2026-04-22 strict A2A mode karari: `A2A_MODE=http` capability cagrilarinda ve `A2A_SPECIALIST_MODE=http` specialist cagrilarinda artik lokal agent'a sessiz fallback yoktur. Announcement/event capability agent'lari veya specialist servisler erisilemezse cevap `success=False`, `generation_mode="kural"` ve `a2a_*_endpoint_missing` / `a2a_*_transport_failed` hata kodlariyla doner. `shadow` modu bilerek lokal sonucu primary dondurup HTTP sonucu karsilastirir; bu, strict HTTP moduyla karistirilmamalidir.

Bu karar `codex-a2a-strict-http-20260422` build'iyle canli Docker stack uzerinde dogrulandi. Full JSON-RPC topoloji `15/15 active` dondu. `tuition_agent` container'i kisa sure durdurulup `Harc ucreti ne kadar?` sorgusu atildiginda cevap local tuition hesaplamasina dusmedi; `Tuition Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir...` kontrollu cevabi dondu. Container tekrar baslatildiktan sonra `agent-finance-tuition` health `ok`, topology yine `15/15 active` oldu.

2026-04-22 A2A gozlenebilirlik paketi: `trace_id`, `span_id`, `parent_span_id` artik main orchestrator -> department orchestrator -> specialist agent ve announcement/event capability agent cagrilarinda ortak metadata olarak tasinir. Public `/query`, main `/a2a` JSON-RPC, internal `/a2a/dispatch`, capability ve specialist dispatch modelleri bu alanlari kabul eder; `query_logs.query_metadata` ve `agent_tasks.payload` icinde trace ozeti tutulur. `scripts/a2a_docker_stack_smoke.py` calisan Docker stack icin `/health`, `/a2a/topology`, public `/query` ve main JSON-RPC `message/send` kontrollerini tek komutta yapar ve JSON-RPC response task'inda `trace_id` korunmazsa fail eder. Bu paket icin `py_compile` gecti; `tests/unit/test_a2a_helpers.py tests/unit/test_orchestrators.py tests/unit/test_api.py tests/unit/test_agent_service.py -q` sonucu `104 passed` verdi. Canli Docker dogrulamasi da `build_id=codex-20260422-204815` ile tamamlandi: apt/pip katmanlari `CACHED`, full JSON-RPC topology `15/15 active, stale_count=0`, public `/query` akademik VT cevabi ve main `/a2a` event JSON-RPC cevabi gecti; response task/artifact/message metadata'sinda ayni `trace_id` goruldu.

2026-04-23 A2A servis kimligi paketi: internal A2A HTTP/JSON-RPC cagrilari artik ortak secret'a ek olarak `X-A2A-Caller-ID` ve `X-A2A-Target-ID` tasir. Agent servisleri ve main `/a2a`/`/a2a/dispatch` yuzeyi beklenen target service id ile gelen target header'ini eslestirir; `A2A_REQUIRE_SERVICE_IDENTITY=true` olursa caller header'i zorunlu olur, `A2A_ALLOWED_CALLER_IDS` verilirse allowlist uygulanir. Lokal default geriye uyum icin kapali kalir; A2A Docker overlay'lerinde varsayilan `true` yapildi. `scripts.a2a_http_canary` ve `scripts.a2a_docker_stack_smoke` yeni header'lari gonderir. Bu soru/cevap optimizasyonu degil, gercek dagitik A2A'da servisler arasi kimlik sinirini netlestiren genel altyapi adimidir.

Canli Docker dogrulamasi ayni gun tamamlandi. Ilk rollout sandbox icinde Docker buildx lock izni nedeniyle durdu; escalated Docker erisimiyle `python -m scripts.a2a_rollout --transport-protocol jsonrpc --include-student --include-academic --include-announcement --include-event --include-all-specialists --health-timeout-seconds 180` basarili calisti. Build `codex-20260423-005702`; apt/pip katmanlari `CACHED`, sadece `scripts`, `src` ve `data` katmanlari yeniden kopyalandi. Tum 15 servis health check'ten ayni build id ile gecti. `scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15 --timeout 120` sonucu topology `agent_count=15`, `active_count=15`, `stale_count=0`; public `/query` akademik VT cevabi, main `/a2a` event JSON-RPC cevabi ve response trace metadata korumasi basarili oldu. Ek negatif auth kontrolunde `POST /a2a` sadece `X-Internal-API-Key` ile, A2A caller identity olmadan `403` dondurdu; yani Docker overlay'indeki `A2A_REQUIRE_SERVICE_IDENTITY=true` runtime'da aktif.

2026-04-23 AgentCard preflight/discovery adimi: A2A transportlari artik `A2A_DISCOVERY_AGENT_CARD_ENABLED=true` iken remote servise is gondermeden once `GET /agent-card` ile lightweight karti okur ve beklenen `service_id`, `service_target_kind`, `service_target` ve `a2a_transport_protocol` / `a2a_jsonrpc` bilgilerini dogrular. Lokal default geriye uyum icin kapali; A2A Docker overlay'lerinde varsayilan acik. Bu, "ajanlar once birbirini taniyor mu?" sorusunu internal servisler icin daha dogru hale getirir: config/registry endpoint'i bulur, AgentCard kimlik/capability/protokol uyumunu dogrular, sonra `/a2a` veya `/a2a/dispatch` cagrilir. Dis agent onboarding hala otomatik degil; AgentCard okunabilir ama trust, allowlist ve servis-auth politikasi ayrica tasarlanmalidir.

Canli Docker dogrulamasi `codex-20260423-010752` build'iyle tekrar tamamlandi. Full JSON-RPC topoloji 15/15 healthy ve `scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15 --timeout 120` basarili oldu. API container'inda `A2A_DISCOVERY_AGENT_CARD_ENABLED=true` goruldu; akademik agent loglarinda remote specialist cagrisi oncesi `GET /agent-card` ve ardindan `POST /a2a` kaydi goruldu. Yani preflight yalnizca config'te degil, runtime'da da aktif.

2026-04-23 devaminda A2A servis-auth bir adim daha sertlestirildi: `A2A_REQUIRE_REQUEST_SIGNATURE=true` iken internal A2A POST cagrilari `X-A2A-Timestamp`, `X-A2A-Nonce`, `X-A2A-Body-SHA256` ve `X-A2A-Signature` header'larini tasir. Imza, canonical JSON body hash + caller id + target id + timestamp + nonce uzerinden HMAC-SHA256 ile uretilir. Lokal default geriye uyum icin kapali; Docker A2A overlay'lerinde varsayilan acik. `A2A_REQUEST_SIGNATURE_SECRET` verilmezse imza secret'i internal API key'den cozulur. Bu shared secret'i tamamen kaldirmiyor, ama artik sadece sabit key bilen herhangi bir client yerine body butunlugu ve zaman penceresi de dogrulanan A2A cagrisi gerekiyor. Dis agent entegrasyonunda da bu mekanizma tek basina trust modeli degil; partner/key rotation/allowlist ayrica tasarlanmalidir.

Bu imza paketi `codex-20260423-012112` build'iyle canli Docker'da dogrulandi. Build cache dogru davrandi: base, apt ve pip katmanlari `CACHED`; sadece `src` ve `data` katmanlari kopyalandi. Full JSON-RPC topoloji 15/15 healthy oldu; `scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15 --timeout 120` imzali main `/a2a` ve public `/query` smoke'larini gecti. Ardindan compose tarafinda `A2A_REQUEST_SIGNATURE_SECRET` default'u bos birakilip no-build recreate yapildi; imza secret'i internal key fallback'iyle cozulurken smoke yine basarili oldu. Ek negatif kontrolde main `/a2a` endpoint'i internal key + caller/target headerlari olmasina ragmen imza header'lari olmadan `403` ve `A2A request signature headers eksik.` dondurdu.

2026-04-23 A2A diagnostics/observability adimi: public `GET /a2a/diagnostics` endpoint'i eklendi. Bu endpoint son pencere icin query sayisi, query failure sayisi, agent task sayisi, agent task failure sayisi, response time ozeti, ajan bazinda total/completed/failed/failure_rate, `latency_sample_count`, avg/max latency, son hata ve recent failure orneklerini dondurur. Agent task telemetry sonucu artik uygun yerlerde `latency_ms` saklar; eski kayitlarda latency olmadigi durumda ortalamanin kac ornekten hesaplandigini `latency_sample_count` netlestirir. `scripts.a2a_docker_stack_smoke.py` artik diagnostics endpoint'ini de kontrol eder.

Bu diagnostics paketi `codex-20260423-014129` build'iyle canli Docker'da dogrulandi. Rollout sirasinda base/apt/pip dependency katmanlari `CACHED` geldi; yalniz `src` ve `data` katmanlari yeniden kopyalandi. Full JSON-RPC topoloji 15/15 healthy oldu. `scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15 --timeout 120` health, topology, public `/query`, main `/a2a` JSON-RPC ve diagnostics kontrollerini gecti. Diagnostics cevabinda `agent_task_count=12`, `agent_task_failure_count=0`, `curriculum_agent` ve `event_agent` icin `latency_sample_count=2`, `recent_failures=[]` goruldu. Lokal dogrulamalar: `py_compile` gecti; genis A2A unit seti `tests/unit/test_a2a_service_identity.py tests/unit/test_a2a_helpers.py tests/unit/test_agent_service.py tests/unit/test_api.py tests/unit/test_orchestrators.py tests/unit/test_telemetry.py -q` sonucu `115 passed` verdi. Bilinen uyarilar oncekiyle ayni: pytest cache Windows izin uyarisi ve agent service registry startup testindeki coroutine cleanup warning.

2026-04-23 CI/e2e otomasyon adimi: `.github/workflows/a2a-docker-e2e.yml` eklendi. Workflow PR ve manuel `workflow_dispatch` ile calisir; hedef A2A unit setini kosar, taze Docker infra (`postgres`, `redis`, `chromadb`) baslatir, Alembic migration + `seed_curriculum_data` + `seed_synthetic_data` calistirir, full JSON-RPC topolojiyi `--include-student --include-academic --include-announcement --include-event --include-all-specialists` ile rollout eder ve `scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15` ile health/topology/public query/main JSON-RPC/diagnostics smoke yapar. Bu, benchmark degil; dagitik A2A topolojisinin CI kapisidir. Statik dogrulama olarak workflow YAML parse edildi ve full compose kombinasyonu CI network ayarlariyla `docker compose ... config --quiet` gecti. GitHub runner uzerinde ilk gercek calistirma henuz yapilmadi.

2026-04-23 A2A state transition history adimi: `src.a2a.state` eklendi ve task metadata'sinda standart `state_transitions` listesi uretilmeye baslandi. Senkron JSON-RPC `message/send` cevaplari artik metadata icinde `submitted -> working -> completed` gecmisini actor, task id, message id ve timestamp ile tasir. `build_query_task` request tarafinda `submitted` kaydi ekler; `build_department_response_task` request gecmisini devralip `working/completed` ekler; main orchestrator response task'i da ayni modeli kullanir. `scripts.a2a_docker_stack_smoke.py` artik main JSON-RPC response metadata'sinda bu son uc transition'i zorunlu kontrol eder. Bu gercek streaming/push degildir; ancak AgentCard'da ilan edilen `stateTransitionHistory=True` kabiliyetinin somut task metadata karsiligidir.

Bu state transition paketi `codex-20260423-015506` build'iyle canli Docker'da dogrulandi. Full JSON-RPC topoloji 15/15 healthy oldu; smoke health/topology/public query/main JSON-RPC/diagnostics kontrollerini gecti ve JSON-RPC result metadata'sinda `state_transitions=[submitted, working, completed]` kronolojik timestamp'lerle goruldu. Lokal genis A2A unit seti tekrar `115 passed` verdi. Build sirasinda base/apt/pip katmanlari `CACHED`; sadece `scripts`, `src` ve `data` katmanlari yeniden kopyalandi.

2026-04-23 kod organizasyonu adimi: main API icinde duran main orchestrator A2A protokol helper'lari `src.api.main_a2a` modulune alindi. Bu modul main AgentCard, lightweight `/agent-card` payload'i, topology icin main agent status payload'i, JSON-RPC `message/send` message metadata/text extraction'i ve `omu.user_query_response.v1` response task uretiminden sorumludur. `src.api.main` route/dependency/auth yuzeyine inceldi. Ayrica main API ve standalone agent service tarafinda tekrar eden JSON-RPC success/error builder'lari `src.a2a.jsonrpc` modulune tasindi. Bu davranis degisikligi degil, "ana orchestrator / HTTP route / A2A protokol helper'i" sinirlarini daha okunur yapan genel refactor'dur.

Bu refactor icin `py_compile` gecti. `tests/unit/test_api.py tests/unit/test_agent_service.py -q` sonucu `40 passed`; genis A2A unit seti tekrar `115 passed` verdi. Bilinen uyarilar degismedi: pytest cache izin uyarisi ve agent service registry startup testindeki coroutine cleanup warning.

2026-04-23 AgentResponse isimlendirme temizligi: published A2A artifact semantigi zaten `omu.agent_response.v1` oldugu icin generic builder adi eklendi. `build_agent_response_task` artik primary helper; eski `build_department_response_task` geriye uyum alias'i olarak durur. Production cagrilari `BaseSpecialistAgent`, department orchestrator, department/specialist HTTP transportlari ve agent service execution tarafinda yeni generic isme tasindi. `extract_agent_response` ana okuma helper'i olarak kalir; `extract_department_response` legacy/uyumluluk icin durur. Bu davranis degisikligi degil, A2A contract dilini "department"tan "agent" semantigine yaklastiran kademeli temizliktir.

Bu isimlendirme turu icin `py_compile` gecti. Hedef testler `tests/unit/test_a2a_helpers.py tests/unit/test_orchestrators.py tests/unit/test_agent_service.py -q` sonucu `90 passed`; genis A2A unit seti `116 passed` verdi. Canli Docker dogrulamasi `codex-20260423-020550` build'iyle tamamlandi: base/apt/pip katmanlari `CACHED`, full JSON-RPC topology 15/15 healthy, stack smoke health/topology/public query/main JSON-RPC/state transitions/diagnostics kontrollerini gecti.

2026-04-23 devam dogrulamasi: Docker tekrar acildiktan sonra mevcut stack once `codex-20260423-020550` build'iyle `scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15 --timeout 120` uzerinden tekrar dogrulandi. API `healthy`, Groq primary `healthy`, `/a2a/topology` `agent_count=15`, `active_count=15`, `stale_count=0`; public `/query`, main `/a2a` JSON-RPC, state transition history ve diagnostics kontrolleri gecti.

Ardindan A2A contract katmanindaki isimlendirme temizligi bir adim daha tamamlandi: `src.a2a.responses` eklendi. A2A-facing kod artik `AgentResponse` alias'i, `validate_agent_response` ve `build_failed_agent_response` yardimcilari uzerinden okunur; runtime payload modeli geriye uyum icin mevcut `DepartmentResponse` modeline dayanmaya devam eder. Department/capability/specialist transportlarinda REST payload validation ve transport failure response uretimi bu generic adapter'a tasindi. Legacy `build_department_response_task`, `extract_department_response`, `DEPARTMENT_RESPONSE_SCHEMA` ve `/a2a/dispatch` REST response modeli geriye uyumluluk icin korunur.

Bu adapter turu icin `py_compile` gecti. Hedef testler `tests/unit/test_a2a_helpers.py tests/unit/test_agent_service.py tests/unit/test_orchestrators.py -q` sonucu `90 passed`; genis A2A unit seti `116 passed` verdi. Degisiklik Docker'a `codex-20260423-113245` build'iyle tasindi; build sirasinda base/apt/pip katmanlari `CACHED`, sadece `src` ve `data` katmanlari kopyalandi. Yeni build uzerinde stack smoke tekrar basarili oldu: health `healthy`, transport `jsonrpc`, topology `15/15 active`, diagnostics `agent_task_failure_count=0`, `recent_failures=[]`. Benchmark calistirilmadi.

2026-04-23 nihai AgentResponse contract temizligi: `AgentResponse` artik `DepartmentResponse` alias'i degil, `src.a2a.responses.AgentResponse` adinda gercek Pydantic modelidir. A2A artifact payload'i agent-semantikli alanlari tasir: `agent_id`, `agent_name`, `agent_role`, `capability`, opsiyonel `department`, `answer`, `sources`, `generation_mode`, `success`, `error`, `metadata`. `department_response_to_agent_response` ve `agent_response_to_department_response` mapper'lari eklendi. `extract_agent_response` generic `AgentResponse`, `extract_department_response` legacy `DepartmentResponse` dondurur. Ic orchestrator/sentez ve legacy REST `/a2a/dispatch` hatti `DepartmentResponse` ile uyumlu kalir; JSON-RPC artifact'in primary semantigi `omu.agent_response.v1`dir.

Bu adim icin yeni unit test eklendi: `extract_agent_response` sonucunun `AgentResponse` oldugu, `DepartmentResponse` olmadigi ve legacy mapper'in eski modele dondugu kilitlendi. Lokal dogrulama: `py_compile` gecti; hedef suite `91 passed`, genis A2A unit seti `117 passed`. Base specialist agent response metadata'si de tamamlandi: announcement/event `agent_role=capability_agent` ve `capability=announcement|event`, diger uzmanlar `agent_role=specialist_agent` olarak yayinlanir.

Canli Docker dogrulamasi `codex-20260423-115742` build'iyle tamamlandi. Build cache dogru calisti: base/apt/pip katmanlari `CACHED`, sadece `src` ve `data` yeniden kopyalandi. Full JSON-RPC topoloji `15/15 active`, `stale_count=0`, API/Groq health `healthy`; stack smoke public query, main JSON-RPC, state transition history ve diagnostics kontrollerini gecti. Ek direkt event agent JSON-RPC kontrolunde structured artifact `schema=omu.agent_response.v1`, payload `agent_id=event_agent`, `agent_role=capability_agent`, `capability=event`, `department=student_affairs`, `answer` alanlariyla dondu ve main `UserQueryResponse` alanlarindan `departments_involved` tasimadigi dogrulandi. Benchmark calistirilmadi.

2026-04-23 dis agent trust/onboarding adimi: A2A JSON-RPC `/a2a` yuzeyi artik internal API key disinda opsiyonel external partner auth yolunu da destekler. Bu yol default kapali (`A2A_EXTERNAL_TRUST_ENABLED=false`) ve yalniz `A2A_EXTERNAL_ALLOWED_AGENT_IDS`, `A2A_EXTERNAL_AGENT_ENDPOINTS` veya `A2A_EXTERNAL_AGENT_SIGNATURE_SECRETS` ile acikca tanimlanan partner caller id'lerini kabul eder. External isteklerde caller/target header'i ve varsayilan olarak per-agent HMAC imzasi gerekir; internal legacy `/a2a/dispatch` disaridan acilmadi. Admin dogrulamasi icin `POST /a2a/external/validate` eklendi; internal API key ile cagrilir, partner AgentCard'ini `/.well-known/agent.json`, `/.well-known/agent-card.json`, `/agent-card` sirasiyla kontrol eder ve service id / URL / target kind / target / JSON-RPC uyumunu dogrular. Bu otomatik dis routing degildir; dis agent sisteme ancak trust policy + AgentCard + imza dogrulamasi ile "tanimlanmis partner" olarak kabul edilir.

Standart AgentCard'lar artik A2A HMAC header'larini `securitySchemes` ve `security` alanlarinda ilan eder; main card icin `SERVER_PUBLIC_URL`, agent service card'lari icin `AGENT_PUBLIC_URL` kullanilabilir. Bu, dis agentlarin hangi endpoint ve auth header'lariyla konusacagini kesfedebilmesi icin genel protokol iyilestirmesidir; secret degeri AgentCard icinde yayinlanmaz. `.env.example` external trust ayarlarini ve `SERVER_PUBLIC_URL` ornegini icerir. Lokal dogrulama: `py_compile` gecti; genis A2A unit seti `125 passed` verdi. Canli Docker dogrulamasi `codex-20260423-123159` build'iyle tamamlandi: dependency katmanlari `CACHED`, full JSON-RPC topology `15/15 active`, `stale_count=0`, stack smoke public query/main JSON-RPC/state transitions/diagnostics kontrollerini gecti. Runtime ek kontrolunde `/.well-known/agent.json` `securitySchemes=a2aCallerId,a2aTargetId,a2aTimestamp,a2aNonce,a2aBodySha256,a2aSignature` dondurdu; `POST /a2a/external/validate` external trust kapaliyken `trusted=false`, `reason=external_trust_disabled` dondurdu.

2026-04-23 benchmark harness notu: kalite benchmark'i artik varsayilan profilli kullanici metadata'si gonderir, API timeout'unu 120 sn yapar ve varsayilan olarak request-level question cache bypass eder (`disable_cache=true`; gerekirse `--allow-cache` ile acilir). Public `/query` payload'i ve `MainOrchestrator.handle_query` bu `disable_cache` alanini tasir; lookup/storage `request_disabled` gerekcesiyle atlanir. Benchmark kalite uyarilari artik A2A servis timeout/circuit fallback cevaplarini `a2a_transport_fallback` olarak isaretler; boylece bu durum "temiz kalite" gibi okunmaz. Gecersiz ara benchmark raporlari temizlendi; canonical son kucuk kategori A raporu `tests/archive/benchmarks/quality_benchmark_20260423_125450.json` ve `docs/archive/benchmarks/quality_benchmark_report_20260423_125450.md` dosyalaridir. Yeni build `codex-20260423-125011` ile Docker stack smoke gecti; kategori A sonucu cache bypass ile `dept=4/4`, `mode=3/4`, `facts=8/15`, `clean_quality=3/4` verdi. Kalan ana sinyal cevap optimizasyonundan once genel A2A/RAG performansidir: bir academic specialist branch 60 sn `a2a_transport_fallback` timeout'a dustu.

2026-04-23 benchmark gozlemlenebilirlik notu: `UserQueryResponse` artik opsiyonel `diagnostics.llm_usage` alani tasir. `LLMService` aktif query profiler'a her generate/stream cagrisi icin `model_role`, `provider`, `provider_label`, `model`, `path=primary|fallback|primary_model_fallback`, `status` ve gerekiyorsa fallback/error metadata'si yazar; user-facing response builder'lari bu listeyi response'a tasir. Boylece `scripts/run_quality_benchmark.py` ve `scripts/compare_a2a_latency.py` soru bazinda routing / conversation / specialist_synthesis / global_synthesis icin hangi provider-modelin kullanildigini gosterebilir. Cache hit response'u eski/stale diagnostics tasimamak icin `diagnostics=None` ile dondurulur.

2026-04-23 gec saat performans bulgusu: API benchmark'inin eski warm-up akisi `--use-api` modunda bile lokal `MainOrchestrator` icinde `Test sorgusu` calistiriyordu; bu Docker/A2A API stack'ini ve remote specialist servislerini isitmadigi icin "Warm-up 200ms" gorunurken ilk gercek sorular cold-start maliyeti aliyordu. Hedefli benchmarkta cache kapali ilk kosuda `graduation_agent`, `registration_agent`, `international_agent` ve `regulation_agent` ilk agir islerinde 39-51 sn arasi latencyle gorundu; hemen sonraki warm kosuda ayni agent task sayisi calismasina ragmen sureler saniyelere dustu. Yani fark sadece question cache degil, remote servis/model/retriever warm-state etkisi. `scripts/run_quality_benchmark.py` artik API modunda warm-up'i gercek `/query` yolundan yapar ve `--warmup-selected-questions` ile secili benchmark sorularini olcumden once temsilci prewarm olarak kosturabilir. Remote A2A agent servisleri de profiler snapshot/LLM kullanimini `diagnostics.remote_profiles` ve `diagnostics.llm_usage` uzerinden final response'a tasir; benchmarkta `Ajan Sure` ve `LLM` satirlari yeni build ile gorunmelidir.

2026-04-23 observability devam notu: benchmark sirasinda kullanici cevabinda A2A transport fallback gorulmesine ragmen diagnostics'in 10 dakikalik pencerede failure gostermedigi bir bosluk fark edildi. Main orchestrator artik remote department branch `success=False` ve `error` kodu `a2a_` ile basliyorsa bunu `main_orchestrator -> <department>_orchestrator` agent task failure olarak telemetry'ye yazar. Kullanici netlestirme veya normal no-info durumlari failure sayilmaz. Lokal genis A2A unit seti `128 passed`; degisiklik `codex-20260423-130509` build'iyle Docker'a tasindi ve full JSON-RPC stack smoke gecti.

2026-04-23 external mock ve benchmark tooling notu: gercek dis partner endpoint'i olmadigi durumda `scripts/a2a_external_mock_smoke.py` lokal ayri HTTP server olarak mock external A2A agent baslatir. Bu mock `/.well-known/agent.json` AgentCard'i, `/a2a` JSON-RPC endpoint'i, external allowlist validation ve inbound HMAC imza dogrulamasini tek turda test eder. Manuel smoke `trusted=true`, inbound auth `ok`, mock JSON-RPC `completed` verdi; unit testi `tests/unit/test_a2a_external_mock_smoke.py` ile kilitlendi. Guncel genis A2A unit seti bu test dahil `129 passed`.

Benchmark tarafinda API yokken 25 soruluk sahte all-error raporu uretilmesini engellemek icin `scripts/run_quality_benchmark.py` API modunda `/health` preflight yapar; API/Docker kapaliysa rapor uretmeden durur. Invalid full benchmark raporu temizlendi. Problem siniflandirma icin `scripts/summarize_quality_benchmark.py` eklendi; sonuc JSON'unu `infra_error`, `a2a_transport_fallback`, `routing_mismatch`, `generation_mode_mismatch`, `low_fact_coverage`, `no_sources`, `quality_warning`, `slow_response`, `clean_pass` siniflarina ayirir. Mevcut son gecerli kategori A raporu icin ozet `docs/archive/benchmarks/quality_benchmark_problem_summary_20260423_125450.md` dosyasinda. Docker daemon bu turda kapaliydi (`dockerDesktopLinuxEngine` bulunamadi); full runtime benchmark Docker/API tekrar ayaga kalkinca kosulmali.

2026-04-23 Docker tekrar acildiktan sonra mevcut `codex-20260423-130509` stack'i canli dogrulandi. API `/health` `healthy`, Groq primary `healthy`, `A2A_MODE=http`, `A2A_TRANSPORT_PROTOCOL=jsonrpc` dondu. `scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15 --timeout 120` gecti: topology `agent_count=15`, `active_count=15`, `stale_count=0`, public `/query`, main `/a2a` JSON-RPC, state transitions ve diagnostics kontrolleri basarili; diagnostics `agent_task_failure_count=0`, `recent_failures=[]`.

Ardindan full API kalite benchmark'i cache bypass ile kosuldu: `tests/archive/benchmarks/quality_benchmark_20260423_174611.json` ve `docs/archive/benchmarks/quality_benchmark_report_20260423_174611.md`. Ozet metrikler: departman dogrulugu `25/25 (100%)`, uretim modu `24/25 (96%)`, anahtar bilgi kapsami `70/100 (70%)`, temiz kalite `24/25 (96%)`, ortalama sure `11300 ms`, medyan sure `10446 ms`, hata `0`. Bu sonuc A2A gecisinin ana transport/routing katmaninda oturdugunu, kalan ana kalite borcunun cevap sentezinde kaynaklardaki kritik kosullari eksiksiz tasima oldugunu gosterir. Otomatik problem siniflandirma `docs/archive/benchmarks/quality_benchmark_problem_summary_20260423_174611.md` dosyasina yazildi: `low_fact_coverage=14`, `clean_pass=10`, `generation_mode_mismatch=1`, `quality_warning=1`. Soruya ozel/statik cozum yerine genel sonraki hedefler: kaynak evidence paketini ve LLM sentez promptlarini "kosul, istisna, sure, basvuru kanali, belge, yetkili birim" gibi resmi detaylari kesmeyecek sekilde iyilestirmek; paraphrase ve process-chain sorularda query expansion/retrieval'i semantik niyete gore guclendirmek; rule-vs-LLM mode politikasini tek kalan mode mismatch icin genel karar kriterleriyle netlestirmek.

Benchmark sonrasi `/a2a/diagnostics` 60 dakikalik pencerede `query_failure_count=0` ama `agent_task_failure_count=4` gosterdi. Recent failure ornekleri Q5 preview'una bagliydi: main -> `student_affairs_orchestrator` ve main -> `academic_programs_orchestrator` `a2a_transport_timeout`, bu iki departman icinde `registration_agent` ve `international_agent` `a2a_specialist_transport_failed`. Ancak bu 60 dakikalik pencere onceki denemeleri de icerir; bu yuzden dogrudan `20260423_174611` full benchmark'ina atfedilmemeli. Genel cozum olarak `scripts/run_quality_benchmark.py` API modunda benchmark oncesi/sonrasi `/a2a/diagnostics` snapshot alip JSON/Markdown rapora `diagnostics` ve `a2a_*_failure_delta` metrikleri yazacak sekilde guncellendi. `scripts/summarize_quality_benchmark.py` de yeni `run_level_signals` bolumunde `a2a_diagnostics_failures` sinyalini raporlar.

Delta mekanizmasi `tests/archive/benchmarks/quality_benchmark_20260423_175741.json` tek Q5 kosusuyla dogrulandi: `overview_before.agent_task_failure_count=4`, `overview_after.agent_task_failure_count=4`, `a2a_agent_task_failure_delta=0`, `agent_task_count` deltasi `3` oldu. Yani mevcut stack ayni sorguda yeni A2A failure uretmedi; onceki 60 dakikalik diagnostics failure'lari pencere artigi olarak kaldi. Stack smoke tekrar kosuldu ve gecti: API health `healthy`, topology `15/15 active`, public query academic VT, main JSON-RPC event task, state transitions ve diagnostics endpoint'i calisiyor.

A2A SLA ayari da genellestirildi: `A2A_DEPARTMENT_TIMEOUT_SECONDS` eklendi ve `HttpA2ADepartmentTransport` artik main -> department cagrilarinda bu degeri kullanir; unset ise geriye uyum icin `A2A_TIMEOUT_SECONDS` kullanir. Docker A2A API overlay'lerinde default `A2A_DEPARTMENT_TIMEOUT_SECONDS=75` olarak set edildi. Gerekce: department servisleri kendi icinde specialist HTTP cagrilarina `A2A_SPECIALIST_TIMEOUT_SECONDS=60` butcesi verebiliyor; main tarafinin department branch'i 30 saniyede kesmesi katmanlar arasi SLA uyumsuzlugu olusturuyordu. Capability ve specialist timeoutlari ayni kalir; bu soru-bazli degil, dagitik A2A timeout butcesi ayrimidir.

Bu SLA degisikligi `codex-20260423-180227` build'iyle canli Docker'a tasindi. Rollout sirasinda base/apt/pip katmanlari `CACHED`, sadece `scripts`, `src` ve `data` katmanlari yeniden kopyalandi. Tum 15 servis ayni build id ile healthy oldu; stack smoke tekrar gecti (`15/15 active`, JSON-RPC, state transitions, diagnostics). Canli API container env kontrolu `A2A_TIMEOUT_SECONDS=30` ve `A2A_DEPARTMENT_TIMEOUT_SECONDS=75` gosterdi. Yeni build uzerinde delta'li Q5 benchmark'i `tests/archive/benchmarks/quality_benchmark_20260423_180605.json` olarak kosuldu: sure `30922.7 ms`, `a2a_query_failure_delta=0`, `a2a_agent_task_failure_delta=0`, `agent_task_count` deltasi `3`. Problem summary bu kosuyu `slow_response` olarak siniflandirdi, transport failure olarak degil. Bu, timeout butcesi ayriminin A2A branch'i kesmeden tamamlamaya izin verdigini, ama yavas RAG/LLM branch maliyetinin hala ayri performans borcu oldugunu gosterir.

2026-04-23 latency ayrimi icin `scripts/compare_a2a_latency.py` eklendi. Bu script ayni benchmark sorularini HTTP A2A API ve lokal in-process yolundan warmup + measured repeat ile koşturur; JSON/Markdown rapora sureleri, departments, generation modes, kaynak sayisi ve HTTP A2A diagnostics delta'yi yazar. Ilk API-only smoke `tests/archive/benchmarks/a2a_latency_compare_20260423_182732.json` sonucunda Q5 HTTP A2A `4173.5 ms` ve failure delta olmadan tamamlandi. Daha sonra `warmups=1`, `repeats=1` tam karsilastirma `tests/archive/benchmarks/a2a_latency_compare_20260423_183034.json` olarak kosuldu: HTTP A2A measured `7080.0 ms`, in-process measured `38910.6 ms`, HTTP diagnostics delta `queries=1`, `agent_tasks=3`, `agent_task_failures=0`. Bu sonuc transport'un ana yavaslik oldugunu desteklemiyor; aksine Docker HTTP A2A warm servisler daha hizli gorundu. Ancak not: lokal in-process kosuda Groq/OpenAI-compatible baglantilari sandbox/dis ortam nedeniyle `All connection attempts failed` verdi; bu yuzden bu karsilastirma "ayni network/provider kosullarinda kesin oran" degil, transport overhead'in baskin olmadigina dair operasyonel sinyaldir. Tam adil karsilastirma icin ayni Docker network/provider kosullarinda ikinci bir API container'i `A2A_MODE=inprocess` ile ayaga kaldirip HTTP A2A container'i ile yan yana olcmek gerekir.

2026-04-23 repo hijyen notu: proje dizinindeki gecici pytest/cache/log klasorleri, `tests/live_test_*` dump'lari ve dokumanlarda referanslanmayan eski benchmark raporlari temizlendi. Kanonik olarak tutulan benchmark artefact'lari su an `tests/archive/benchmarks/quality_benchmark_20260423_125450.json`, `tests/archive/benchmarks/quality_benchmark_20260423_174611.json`, `tests/archive/benchmarks/quality_benchmark_20260423_175741.json`, `tests/archive/benchmarks/quality_benchmark_20260423_180605.json`, `tests/archive/benchmarks/a2a_latency_compare_20260423_182732.json`, `tests/archive/benchmarks/a2a_latency_compare_20260423_183034.json` ile bunlara eslik eden `docs/archive/benchmarks/quality_benchmark_report_20260423_125450.md`, `docs/archive/benchmarks/quality_benchmark_problem_summary_20260423_125450.md`, `docs/archive/benchmarks/quality_benchmark_report_20260423_174611.md`, `docs/archive/benchmarks/quality_benchmark_problem_summary_20260423_174611.md`, `docs/archive/benchmarks/a2a_latency_compare_20260423_182732.md` ve `docs/archive/benchmarks/a2a_latency_compare_20260423_183034.md` dosyalaridir. Yeni benchmark kosulari tekrar yigilma uretirse once dokumanlarda alintilanan son kanonik set korunmali, geri kalan uretilmis ciktilar temizlenebilir.

2026-04-23 ek hijyen/guvenlik notu: repo icinde kalan `docker-compose.a2a*` ve `docker-compose.a2a-existing-infra*` overlay dosyalari gereksiz degil; rollout script'i, CI e2e akisi ve dokumantasyon tarafindan aktif kullaniliyor. `data/raw` altinda ayni icerigin normalize edilmis ve Turkce karakterli dosya adlariyla tekrar eden belge ciftleri var; bunlar ilk bakista duplicate gorunse de ingestion/erişim davranisini etkileyebilecegi icin otomatik silinmemeli. Kalan belirgin tek lokal artefact `university_support.dump` dosyasidir; runtime tarafinda referansi yok, `.dockerignore` ile zaten build disinda tutuluyor. Ancak bu dosya muhtemel yedek/export oldugu icin ihtiyac teyit edilmeden silinmemeli.

2026-04-23 workspace kokunde inner repo disinda duran `ubys_*` HTML/JS/JSON snapshot dosyalari da incelendi. Bunlar aktif kod yolunda referanslanmayan, UBYS portalindan alinmis tek seferlik arastirma artefact'lariydi; `src/db/ubys_curriculum.py` ve ilgili export/seed script'leri bu ham snapshot dosyalarina bagli degil. Kullanici onayi ile kok dizinden silindiler; benzer durumda ayni adla geri gorunen UBYS dosyalari once referans taramasiyla dogrulanip sonra temizlenebilir.

2026-04-24 performans/kalite inceleme notu: `quality_benchmark_20260424_001431` cold run ile `quality_benchmark_20260424_001852` selected-warm run karsilastirildi. Cold run'daki 45-60 sn gecikmelerin ana nedeni A2A protokol overhead'i degil; remote specialist servislerinde ilk istek sirasinda `rag.embedder.load_model`, `rag.reranker.load_model`, embedding encode ve rerank cold-start maliyeti. Q13 cold run'da gercek `a2a_specialist_transport_failed` ve 60 sn timeout vardi; warmed run'da yeni A2A failure delta `0`. Ancak warmed run'da da Q6/Q20/Q22 gibi sorularda toplam API suresi ile gorunen remote agent suresi arasinda bosluk vardi. Kök neden gozlemlenebilirlik eksigi: public `/query` API process'inde main profiler aktif degildi ve filtrelenen departman branch'lerinin remote profile'lari final diagnostics'ten dusuyordu. `UserQueryResponse.diagnostics.local_profile` eklendi, `/query` route'u tum API akisini `QueryProfiler` ile sarar hale geldi, benchmark da `API Sure` satirinda `dispatch`, `global_llm`, `compose`, `telemetry` kirilimini yazacak sekilde guncellendi.

2026-04-24 kalite genel duzeltmesi: "okulumu dondurup", "universiteyi birakip ayrilmak" gibi inflected idari islemler registration uzmanina dusmeyebiliyor ve "ilisik kesme" ifadesi ogrenci toplulugu uyeligi metinleriyle karisabiliyordu. Soruya ozel statik cevap eklenmedi; genel routing/ranking iyilestirildi. Student affairs keyword routing ve routing policy `dondur/ilisik/ayril/birak` koklerini registration kapsaminda ele alir. Registration source ranking, ogrenci toplulugu/uyelik/SKSDB metinlerini kayit sildirme/kayit dondurma sorularinda ilgisiz kaynak olarak cezalandirir ve source-only cevapta reddeder. Multi-step idari surec sorulari (`tum islem`, `surec`, `adim adim`, `dikkat et`, `ne yapmaliyim`) registration agent icin LLM senteze zorlanir; tek parca net kaynakta hala source-only yol korunabilir. Lokal dogrulama: `py_compile` gecti; hedef suite `tests/unit/test_orchestrators.py tests/unit/test_api.py tests/unit/test_agent_service.py tests/unit/test_registration_utils.py tests/unit/test_router.py -q` sonucu `133 passed` verdi.

2026-04-24 API benchmark yorumlama/kalite notu: `quality_benchmark_20260424_005947` ciktisinda `Intent Analizi: 0/7` ve `Force LLM Sentez: 0/7` raporlanmasi gercek davranis degil, benchmark extraction eksigiydi. API mode'da routing intent'i `diagnostics.local_profile.attributes.routing.intent` altinda geliyordu; script sadece lokal profiler snapshot'ina baktigi icin bos sayiyordu. `scripts/run_quality_benchmark.py` artik API-side local profile'dan routing attrs okur. Ayrica registration agent LLM baglamina gitmeden once `should_reject_registration_source_only_result` ile ilgisiz topluluk/uyelik kaynaklarini filtreler; ders kaydi sureci ranking'i de kayit dondurma donusu baglaminda `kayit dondurma suresinin bitiminde`, `ayrildigi donemin/yilin`, `kaldigi yerden devam` gibi resmi donus kuralini ders kaydi kaynaklariyla birlikte one alir. `kopya/disiplin/sorusturma/tutanak` sinyalleri genel ogrenci isleri kural/prosedur routing'ine eklendi ve bu override authoritative yapildi; boylece sinavda kopya gibi disiplin sureci sorulari gereksiz academic curriculum branch'ine dagilip 30-40 sn maliyet uretmez. Promptlarda da kaynakta gecmeyen portal/menü/odeme kanali/form adi uydurmama uyarisi finans, registration ve multi-department sentez icin netlestirildi. Lokal dogrulama: `py_compile` gecti; hedef suite `tests/unit/test_orchestrators.py tests/unit/test_api.py tests/unit/test_agent_service.py tests/unit/test_registration_utils.py tests/unit/test_router.py -q` sonucu `136 passed` verdi. Bilinen uyarilar ayni: Windows pytest cache izin uyarisi ve agent service registry cleanup warning.

2026-04-25/26 RAG, warm-up ve Slack A2A notu: dagitik A2A topolojisinde her agent'in kendi embedding/reranker modelini cold-start etmesi hem isinma maliyeti hem de Docker/GPU kaynak baskisi uretiyordu. Bu nedenle temiz mimari yonu merkezi retrieval/reranker servisi oldu: agir embedding/reranker modeli tek yerde isinmali, agent'lar belge arama/rerank icin merkezi servise baglanmali. Bu, hem sektor pratiklerine daha yakin hem de "her specialist kendi modeliyle yasasin" yaklasimindan daha az maliyetli. Gecici mevcut topolojide warm-up kaldirilmadi; API modunda gercek `/query` uzerinden full warm-up ve secili sorularla prewarm tercih edilir. Docker ac/kapa yaparken once kaynak tuketimini dusun; gereksiz rebuild/restart yapma.

2026-04-25/26 model politikasi: sureler kabul edilebilir seviyeye dustugu icin balanced profilde tek departmanli sentez/final refinement da 70B modele tasindi. Routing ve query expansion icin de 70B deneniyor; routing gecikmesi sorun yaratirsa routing tekrar daha ucuz modele alinabilir, ama query expansion'in 70B olmasi kalite icin degerli goruluyor. `.env` model rollerini degistirirken benchmark logundaki `LLM:` satirlarindan gercek role/model kullanimini mutlaka kontrol et; "balanced sectim" demek tum rollerin otomatik 70B oldugu anlamina gelmez.

2026-04-27 LLM cagrisi sadeleştirme notu: routing LLM artik `canonical_query`, `primary_intent` ve `target_capability` alanlarini da dondurur; bu nedenle genel sorgularda ayri query normalization/expansion LLM cagrisi yapmak yerine routing ciktisi kullanilmalidir. Ayri normalizer yalnizca `guncel duyur` gibi cok kisa capability parcaciklari icin pre-routing koruma olarak kalir. Cok departmanli dispatch'te global synthesis final cevabi uretecegi icin specialist ajan LLM sentezi varsayilan olarak kapali tutulur; `force_llm_synthesis` artik yalnizca tek departmanli akista specialist LLM'i yeniden acar. Bu, "specialist LLM ozeti + global LLM ozeti" seklindeki cift sentez maliyetini ve ozeti tekrar ozetleme riskini azaltmak icindir.

2026-04-25/26 Slack notu: Slack iki runtime ile calisabilir. `--runtime inprocess` lokal monolitik akistir; `--runtime a2a --a2a-endpoint-profile local --transport-protocol jsonrpc` lokal A2A endpointlerine baglanan bottur. Docker Slack icin `docker-compose.slack.yml` kullanilir, ancak A2A Slack'in agent endpointlerine erisebilmesi icin A2A auth/signature env'leri de dogru tasinmalidir. Slack tarafinda `Can not decode content-encoding: br` hatasi aiohttp/brotli uyumsuzlugudur; HTTP accept-encoding veya dependency tarafi incelenmelidir. Slack'te "Duyurular agent servisine ulasilamadi" veya genel `Kural` fallback'i gorulurse once A2A endpoint/profile/auth uyumuna bak.

2026-04-25/26 statik kapilari azaltma karari: eski sistemde sure kaygisi nedeniyle cok sayida erken heuristic gate vardi. Artik latency daha iyi oldugu icin dusuk bilgi iceren selam/yardim mesajlari haricinde semantik ama keyword'suz sorgular LLM routing'e birakilmali. Announcement follow-up baglami net konu degisimlerinde yapismamali; `staj`, `ders kaydi`, `mufredat`, `sinifta`, `yemekhane` gibi yeni konu sinyalleri duyuru akisindan cikmali. `yemekhane ucreti` gibi ogrenim ucreti olmayan fee sorgulari tuition clarification'a dusmemeli. Ders adi gecen "hangi sinifta/yarıyil" sorgulari ders kodu istemeden curriculum DB title lookup ile cevaplanabilmeli.

Son hedefli dogrulama: routing, tuition, curriculum, orchestrator ve curriculum-data unit seti `154 passed` verdi. Bilinen lokal uyarilar Windows `.pytest_cache` izin uyarilaridir; davranisi etkilemedi. Git durumu bu workspace'te dosyalari untracked gosterebilir, bu yuzden diff/stat yorumlarken repo kokunu ve takip durumunu kontrol et.

2026-04-26 Slack canli cikti duzeltmesi: "Dis hekimligi donem ucreti ne kadar?" sonrasi "Turk ogrenciyim" cevabinda profil/faculty bilgisinin onceki soru entity'sini ezmesi engellendi. Kisa ogrenci tipi cevap fragment'leri tuition follow-up ise LLM/profil drift'ine birakilmadan onceki somut soruyla deterministik birlestirilir. Asil Slack kok nedeni de bulundu: DM mesajlarinda `context_id` her mesaj `ts` degeriyle degistigi icin ikinci mesaj onceki soruyu goremiyordu. DM context artik `slack:<channel_id>:<user_id>` seklinde sabit; thread'li kanal mesajlari yine `thread_ts` kullanir. Ayrica "Bahar donemi final sinavi programi" gibi program/takvim baslikli sinav sorgulari announcement direct lookup sayilir; "final not girilmesinin son gunu ne zaman?" gibi takvim/prosedur sorulari bu kapsama alinmaz. Hedef test paketleri `166 passed` ve Slack/conversation/tuition icin `27 passed` verdi.

2026-04-26 Slack auth/tuition takip notu: logout sonrasi kisisel veri donmesi, Slack kullanicisina ait birden fazla aktif `VerificationSession` kalabilmesinden kaynaklandi. Logout artik tek token yerine ilgili Slack kullanicisinin tum aktif oturumlarini pasif hale getirir; bu sinir korunmali, aksi halde eski aktif session tekrar auth context uretebilir. Ucret follow-up tarafinda ikinci kok neden `augment_query_for_department` icinde profil fakültesinin sorgu basina eklenmesiydi: kullanici acikca "Dis hekimligi" gibi birim yazdigi halde login profili "Muhendislik Fakultesi" sorguyu golgeliyordu. Finans query augmentation artik sorguda acik requested unit varsa profil fakültesi prefix'i eklemez; generic "donem ucreti ne kadar?" gibi sorularda profil hala kullanilir. Cache package import-order da sabitlendi; `from src.cache import question_cache` artik import sirasina gore modul yerine obje dondurme riskini tasimaz. Hedef test seti `85 passed` verdi. Tum `tests/unit` kosusu sandbox/izin yuzunden tamamlanamadi: `.codex_pytest_tmp` ve Windows temp yazma izinleri ile onceki A2A rollout test beklentileri nedeniyle 794 passed noktasinda timeout/fail verdi; bu yeni Slack/tuition patch'inin davranis kirilimi degil.

2026-04-26 Slack ucret ikinci takip notu: PDF'de bulunan `Dis Hekimligi Fakultesi` ucret satirlari structured `data/metadata/tuition_fee_catalog.json` katalogunda eksikti. 2025-2026 Turk ogrenci satiri yillik `3.057,00 TL` (donemlik PDF'de yok/null), uluslararasi satir yillik `203.000,00 TL` (donemlik `-`/null) olarak eklendi. Katalog senkronizasyonu `scripts.seed_synthetic_data` ile DB'ye tasinmali; sadece kod rebuild etmek mevcut Postgres tablosunu guncellemez. `TuitionAgent` katalog miss durumunda artik "veritabaninda bulunmuyor" diye erken donmez; RAG/LLM yoluna duser. `extract_requested_unit` muhendislik bolum adlarini (`... muhendisligi`) `muhendislik fakultesi` birimine map eder. Slack event duplicate icin process-ici dedupe eklendi, fakat iki ayri Slack bot container'i ayni tokenla aciksa yine iki cevap gelir; canlida tek runtime (`slack-bot-a2a` veya `slack-bot-inprocess`) acik tutulmali. Hedef regression seti `99 passed` verdi; pytest cache izin uyarisi davranis hatasi degil.

2026-04-26 akademik kaynak kapsami notu: duyuru preset'lerinde bolum bazli bulunan `omu_bil_muh` kaynaginin karsiligi olarak Bilgisayar Muhendisligi mufredat ve haftalik ders programi verisi eksikti. Resmi Bilgisayar Muhendisligi sayfalarindan 2025-2026 bahar/guz lisans ders programi PDF'leri `data/raw/academic_programs/ders_programlari/2025_2026_bahar_bilgisayar_muhendisligi_lisans_ders_programi.pdf` ve `data/raw/academic_programs/ders_programlari/2025_2026_guz_bilgisayar_muhendisligi_lisans_ders_programi.pdf` olarak eklendi. `scripts.ingest_schedule_slots` ile bahar `87`, guz `95` slot PostgreSQL `course_schedule_slots` tablosuna yazildi. UBYS ders bilgi paketi de `data/curriculum/bilgisayar_muhendisligi_seed.json` olarak export edildi; 391 ders ve 2 program slotu icerir. Tam onkosul cekimi 10 dakikada tamamlanmadigi icin bu dosya onkosulsuzdur; DB'ye `scripts.seed_curriculum_from_json ... --courses-only` ile basildi ve eski elle seed'lenmis BIL onkosullari korunmustur. Bu yuzden JSON seed katmanina `--courses-only`/bos prerequisite scope destegi eklendi. UBYS'den gelen noktalı-I gibi Turkce ders kodu varyantlari seed sirasinda `resolve_course_code` ile kanonik ASCII koda normalize edilir; aksi halde ayni ders icin paralel kayitlar olusabilir. Canli DB'de Bilgisayar icin kanonik dersler ve schedule slotlari dogrulandi; eski secmeli grup/staj kayitlari da geriye uyumluluk icin duruyor.

2026-04-26 akademik kaynak kapsami devam: Bilgisayar ile sinirli kalmamasi icin duyuru preset'lerinde bolum/birim olarak takip edilen diger akademik kaynaklar da kontrol edildi. EEM, Fizik, Fen Bilgisi Ogretmenligi ve Matematik Ogretmenligi icin yerel PDF ders programlari canonical bolum adlariyla tekrar ingest edildi; dosya adindan tureyen `2526baharfenguncel` gibi department degerlerine guvenilmemeli. Istatistik lisans bahar/guz ders programlari resmi `ist-fen.omu.edu.tr` duyurularindan indirildi ve `data/raw/academic_programs/ders_programlari/2025_2026_bahar_istatistik_lisans_ders_programi.pdf`, `data/raw/academic_programs/ders_programlari/2025_2026_guz_istatistik_lisans_ders_programi.pdf` olarak eklendi. DB slot kapsami: Bilgisayar `bahar=87/guz=95`, EEM `bahar=163`, Fizik `guz=132` (mevcut lokal kaynaklardan), Istatistik `bahar=105/guz=27`, Fen Bilgisi `bahar=37`, Matematik Ogretmenligi `bahar=26`. Müzik Ogretmenligi ve Resim Is Ogretmenligi icin mufredat seed'i var ama haftalik ders programi PDF'i henuz bulunup ingest edilmedi; `omu_guzel_sanatlar_egitim` preset'i faculty/unit geneli oldugu icin bu alt bolumlerin resmi ders programi kaynaklari ayrica bulunmali. `omu_muhendislik`, `omu_fen`, `omu_egitim`, `omu_main` gibi `unit_name=None` preset'ler fakulte/merkez genel duyuru kaynagidir; "tum fakulte bolumleri" anlamina gelmez, bolum kapsami icin ayrica bolum URL/preset gerekir.

Bu kapsami gozle takip etmek yerine `python -m scripts.audit_academic_source_coverage` komutu eklendi. Komut duyuru preset'leri, `data/curriculum/*_seed.json` dosyalari ve `course_schedule_slots` tablosunu karsilastirir; normalde rapor basip `0` doner. CI/strict kontrol icin `--fail-on-missing` kullanilabilir. Guncel raporda tek eksik sinyal `omu_guzel_sanatlar_egitim` icin schedule coverage'dir.

2026-04-27 Slack/RAG kalite devami: son canli Slack denemelerinde kalan sorunlar soru-bazli cevap yazmadan sistemik olarak ele alindi. Ucret follow-up tarafinda DB seed eksik veya stale ise `data/metadata/tuition_fee_catalog.json` structured katalogu fallback olarak okunur; bu sayede PDF'den cikarilmis `Dis Hekimligi Fakultesi` gibi birimler Postgres tablosu guncellenmemis olsa bile bulunabilir. Bu fallback statik cevap degil, ayni normalize edilmis katalog kaynagini DB sorgusu kacirinca kullanan veri katmanidir. Duyuru/ders programi kapsaminda explicit query scope profil bilgisinden once gelir: "Elektrik elektronik muhendisligi ders programi var mi?" gibi sorgularda login profili Bilgisayar olsa bile duyuru scope'u EEM olarak cozulur. Conversation follow-up tarafinda "isler karisti", "bilmiyorum", "ogrencilik haklarim" gibi konu koparan/bağımsız ifadeler onceki harc konusuna yapismaz; bare "Turk", "yabanci ogrenciyim" gibi cevap parcalari ise yalniz onceki konu gercekten ogrenim ucreti/harc ise birlestirilir.

2026-04-27 intent/prompt koruma notu: `final sinavlari ne zaman?` gibi genel akademik takvim sorulari tek ders final programi sorusu gibi yorumlanmamali. Routing ve registration/general QA promptlari bu niyeti koruyacak sekilde guncellendi: genel sinav tarihi sorusunda "hangi ders?" diye sormak yerine akademik takvim kaynagi kullanilir; spesifik "final sinavi programi" / "ders programi" sorgulari ise duyuru/schedule akisina gidebilir. Bu da statik tarih cevabi degil, yanlis niyet donusumunu engelleyen genel guardrail'dir.

2026-04-27 mufredat sunumu notu: Bilgisayar 2. yariyil gibi ders listesi sorgularinda UBYS/DB ayni yariyilda Almanca/Fransizca/Ingilizce/Yabanci Dil satirlarini ayri zorunlu ders gibi basabiliyordu. Curriculum agent artik yabanci dil alternatiflerini ana ders listesinden ayirip `Yabanci dil secenekleri` grubu olarak sunar ve toplam ders/grup sayisini buna gore hesaplar. Bu soru-bazli hack degil; `course_code`/`course_name` yapisina dayali genel ders katalogu formatlamasidir. Hedef regresyon seti `87 passed` verdi; Windows `.pytest_cache` izin uyarilari davranisi etkilemedi. Tum `tests/unit` halen yerel izin/sandbox ve bazi eski A2A rollout beklentileri nedeniyle guvenilir tek komut degil; hedefli suite'lerle ilerle.

2026-04-27 Slack canli cikti analizi devami: "Fizik ders programi var mi?" sorgusunun Muhendislik deneme dersi duyurularina dusmesinin nedeni explicit unit scope'un login profilindeki fakultesiyle karismasiydi; explicit unit varsa profil faculty otomatik eklenmez. "sey basvuru ne zaman" gibi belirsiz zayif follow-up'lar onceki harc/tuition konusuna yapistirilmaz. LLM cevap temizleyici artik `cumle bulunamadi` / `yonlendir` gibi ic talimat sızıntılarını kullaniciya gostermeden user-facing no-info diline cevirir ve Slack'te yarim kalan son cümle/parçayı düşürür. Prompt guardrail'i de `final sinavlari` = `yariyil sonu/donem sonu sinavlari` eslemesini kullanacak ve ic talimat yazmayacak sekilde netlestirildi. Hedef test seti `35 passed`; Windows `.pytest_cache` izin uyarilari yine davranisi etkilemedi. Kalan veri/RAG borclari: yemekhane ucreti veri kaynagi yok, staj formu sorusunda kaynaklar bolumler arasi tutarsiz ifade uretebiliyor, kisisel AKTS sorusunda mevcut VT cevabi "kredi" etiketiyle donuyor.

2026-04-27 Slack ikinci canli test notu: `Final sinavlari ne zaman?` RAG kaynakta takvim PDF'ini buldugu halde LLM satirdaki `Yariyil Sonu Sinavlari` tarihlerini cikaramiyordu. Registration agent artik genel final/butunleme tarih sorularinda `data/raw/student_affairs/takvimler/2025_2026_genel_akademik_takvim.pdf` dosyasindaki resmi satiri structured olarak okur; hardcoded tarih yok, PDF satiri parse edilir. `Sinav notlarimi nereden gorebilirim?` gibi yer/prosedur sorulari kisisel akademik ozet shortcut'ina sokulmaz. `sey basvuru ne zaman` gibi hangi basvuru turu oldugu belirsiz timing sorulari RAG'a gidip rastgele eski tarih uretmek yerine clarification'a duser. Hedef testler `5 passed`; Windows pytest cache izin uyarisi davranisi etkilemedi.

2026-04-27 routing slot notu: LLM routing ciktisina `required_slots` ve `missing_slots` alanlari eklendi. Amac marker listesini buyutmek degil; LLM'in semantik olarak "bu niyet icin hangi bilgi eksik?" kararini yapisal tasimak. Deterministic katman bu alanlari ileride auth/DB/tool guardrail olarak kullanmali; yani LLM niyeti belirler, deterministik kisim yalnizca guvenlik, kaynak varligi ve eksik slot uygulamasini dogrular.

2026-04-27 missing slot uygulama notu: `missing_slots` artik ana orkestrator tarafindan dispatch oncesi kullanilir. Oturum metadata'sinda zaten dolu olan slotlar (`student_type`, `student_faculty`, `student_department`, `auth`) eksik sayilmaz. Kalan eksik slotlar kullaniciya netlestirme mesaji olarak doner; ornegin `student_type` eksiginde Turk/uluslararasi ogrenci sorulur, `application_type` eksiginde hangi basvuru turu sorulur. Bu katman niyet tespiti yapmaz; LLM'in slot kararini yalnizca guvenli soru metnine cevirir.

2026-04-27 Slack canli test takip notu: `Final sinavlari ne zaman?` sorusunda routing LLM bazen `faculty_or_program` eksik slotu dondurdu; akademik takvim (`primary_intent=academic_calendar`) icin missing-slot clarification bypass edildi. `Final sinavlarinin sisteme girilmesinin son gunu ne zaman?` sorusu artik final sinav araligi yerine `Yariyil Sonu Sinav Sonuclarinin Internetten Girilmesinin Son Gunu` satirini parse eder: guz `19 Ocak 2026`, bahar `16 Haziran 2026`. Ayrica final cevap temizleme sozlugune `certain -> belirli` eklendi ve `onayigereken` bosluk artefakti duzeltildi.

2026-04-30 Slack/A2A operasyon notu: Slack bot normal A2A rollout komutunun icinde otomatik yonetilen servis gibi dusunulmemeli. Docker Slack icin dogru giris `scripts.slack_runtime` helper'idir; A2A runtime icin `python -m scripts.slack_runtime up --runtime a2a`, log icin `python -m scripts.slack_runtime logs --runtime a2a`, kapatma icin `python -m scripts.slack_runtime stop --runtime a2a` kullanilir. Bu helper A2A compose overlay'lerini ve `docker-compose.slack.yml` dosyasini birlikte kullanarak `slack-bot-a2a` servisini kaldirir. `slack-bot-inprocess` yalniz monolitik fallback/karsilastirma icindir; iki runtime ayni Slack token ile ayni anda acik kalirsa duplicate cevap beklenen bir Socket Mode sonucudur. Orphan uyarisi gorulurse once `scripts.slack_runtime status/stop --runtime a2a` ile gercek Slack container durumu kontrol edilmeli; rastgele `docker compose ... up slack-bot` gibi servis adi olmayan komut verilmemelidir.

2026-04-30 evidence/sentez notu: Evidence katmani genel olarak kapatilmadi. `RegistrationAgent` icinde yalniz `Ders kaydi nasil yapilir?` gibi ders kaydi surec sorularinda ekstra `evidence_selection` LLM cagrisi atlanir; kaynaklar yine ranking/filter yoluyla secilir ve final `specialist_synthesis` LLM'i calismaya devam eder. Bu karar "LLM'siz statik cevap" degil; ayni soruda iki LLM katmani calisip ilk selector/provider beklemesi latency olusturdugu icin dar kapsamli maliyet azaltmadir. Geniş RAG/prosedur sorularinda evidence selector varsayilan olarak acik kalir. Bu davranis `tests/unit/test_all_agents.py::TestLLMBypassMechanism::test_registration_course_process_keeps_synthesis_but_skips_selector` ile kilitlidir.

2026-04-30 ders programi notu: Haftalik ders programi cevaplari `course_schedule_slots` VT satirlarindan gelir ve artik sinif/grup bazinda siralanarak sunulur. Bolum/program eslesmesinde daha uzun ve daha somut alias once yakalanmalidir; ornegin `Fizik Egitimi` ifadesi yalniz `Fizik` kisaltilmasina dusmemeli, `Elektrik-Elektronik Muhendisligi` login profilindeki Bilgisayar Muhendisligi ile ezilmemelidir. Donem bilgisi varsa (`guz`, `bahar`) sonuc o doneme daraltilir; donem yoksa mevcut/tercih edilen donem politikasi kullanilir ve cevap basliginda donem yazilir. Sinif parser'inda `III.SINIF` gibi ifadeler `I.SINIF` ile karismasin diye regex ve uzun-eslesme onceligi korunmalidir.

2026-04-30 duyuru/etkinlik sync notu: Duyuru ve etkinlik kaynaklarini hizli guncellerken detail sayfalarina tek tek gitmeden liste verisini yenilemek icin `--skip-details`, mevcut DB kayitlarini gecici kaynak eksiginde pasiflestirmemek icin `--no-deactivate` kullanilabilir. `scripts.sync_announcements` ve `scripts.sync_events` icinde explicit `--max-items` artik preset degeri tarafindan ezilmez. Son canli guncellemede ana/bolum duyuru preset'leri ve etkinlik preset'leri tek tek 20 item civari guvenli modda cekildi; bazi etkinlik kaynaklari eski tarihli ya da sadece kategori sayfasi dondurebilir. `bugunku/yaklasan etkinlik` cevabinda sonuc yoksa once kaynaktaki gelecek tarihli etkinlik varligi ve parser kalitesi kontrol edilmeli; kaynak yokken etkinlik uydurulmamali.

## Degisiklik Yapmadan Once Kontrol Listesi

- Baglam sikismasi veya uzun aradan sonra once bu dosyayi hizlica oku.
- Bu davranis zaten merkezi bir helper ile cozuluyor mu?
- Turkce karakter varyanti eklemek yerine normalizasyon kullaniliyor mu?
- Statik cevap yerine kaynak/DB/ranking/policy duzeltmesi mumkun mu?
- Canli smoke test, unit test ve gerekirse py_compile calisti mi?
- Degisiklik Slack'e ozel mi, yoksa genel orchestrator/ajan sozlesmesini mi etkiliyor?
