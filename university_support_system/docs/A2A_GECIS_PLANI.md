# Gercek A2A Gecis Plani

> Durum Notu (Nisan 2026): Bu belge A2A'ya gecis surecinin tarihsel plan ve karar kaydidir. Dosyanin erken bolumlerinde "henuz yok", "baslandi", "iskelet" gibi ifadeler gecis anindaki durumu anlatir. Bugunku nihai ozet icin `A2A_DAGITIK_MIMARI_VE_CALISMA_OZETI.md`, calistirma komutlari icin `KURULUM_VE_CALISTIRMA.md` okunmalidir.

Bu plan mevcut "A2A uyumlu task sozlesmesi" yapisini gercek dagitik agent-to-agent mimarisine tasimak icindir.

## Mevcut Durum

- `src.a2a.helpers` A2A `Task`, `Message`, `Artifact` ve generic `AgentResponse` semantikli response artifact sarmalama/cozme yardimcilarini iceriyor; `DepartmentResponse` payload'i geriye uyumluluk icin okunabilir kalir.
- `src.api.main` icinde `/a2a/dispatch` internal endpoint'i var, ama bu endpoint yine ayni uygulama process'indeki `MainOrchestrator.department_orchestrators` nesnelerini kullaniyor.
- `src.orchestrators.department_dispatch.dispatch_to_departments` departman orkestratorlerini dogrudan Python nesnesi olarak cagiriyor.
- `agent_registry`, `query_logs` ve `agent_tasks` tablolarinda telemetry/registry temeli var.

Sonuc: Sozlesme ve telemetry zemini hazir; dagitik network transport, servis discovery, timeout/fallback ve deployment ayrimi henuz yok.

## Gecisten Once Duzeltilecek Kucuk Borclar

Canli test turunda gorulen ve A2A oncesi duzeltilmesi daha guvenli olan noktalar:

- Erasmus burs/hibe sorulari sadece `finance` yerine `academic_programs + finance` paralel route edilmeli.
- "Harc borcum ne kadar?" gibi kisisel finans sorulari generic harc ucreti aciklamasina degil auth guard'a dusmeli.
- Acik etkinlik sorulari conversation follow-up LLM cozumleyicisini beklememeli; event short-circuit daha erken calismali.
- Event veri tazelik/pencere davranisi kontrol edilmeli; veri yoksa benchmark "kaynak yok" uyarisi dogru mu, yoksa veri cekme/parser mi sorunlu ayrilmali.
- RAG cevaplari Slack'te fazla uzun cikiyor; ozellikle kaynak-only yanitlar kisaltilmali.

## Hedef Mimari

```
Slack/API/CLI
  -> MainOrchestrator
  -> DepartmentRouter
  -> A2ATransport
       -> in-process fallback veya HTTP client
       -> department agent service
          -> DepartmentOrchestrator
          -> SpecialistAgent
          -> AgentResponse artifact
             -> legacy-compatible DepartmentResponse payload
```

Slack, API ve CLI tarafinda is mantigi degismemeli. Degisen kisim sadece `MainOrchestrator -> department orchestrator` arasindaki transport olmali.

## Faz 1: Sozlesmeyi Sabitle

- `AgentResponse` response artifact sozlesmesi dagitik servisler icin resmi contract kabul edilecek; mevcut `DepartmentResponse` payload'i legacy uyumluluk icin korunacak.
- `A2AQueryPayload` icindeki alanlar netlestirilecek: `query_text`, `context_id`, `task_type`, auth/profile metadata, conversation metadata, `query_log_id`, `force_llm_synthesis`, `is_personal_query`.
- Response artifact'i icin yeni schema `omu.agent_response.v1`; eski `omu.department_response.v1` schema/extension olarak korunacak.
- Contract test eklenecek: her agent servisi gelen task'i parse edip valid AgentResponse artifact'i dondurebilmeli.

## Faz 2: Transport Abstraction

Yeni bir transport katmani eklenmeli:

- `InProcessDepartmentTransport`: bugunku dogrudan Python cagrisini yapar.
- `HttpA2ADepartmentTransport`: endpoint'e A2A task veya uyumlu JSON gonderir.
- `A2A_MODE=inprocess|http|shadow` env ayari eklenir.

Ilk asamada default `inprocess` kalmali. Boylece demo akisi bozulmadan HTTP yolunu ekleyebiliriz.

Durum: baslandi ve ilk iskelet tamamlandi.

- `src.a2a.transport` icinde `InProcessDepartmentTransport`, `HttpA2ADepartmentTransport` ve `ShadowDepartmentTransport` eklendi.
- `src.orchestrators.department_dispatch` artik departmanlari transport abstraction uzerinden cagiriyor.
- Default `A2A_MODE=inprocess`; mevcut davranis bozulmadan korunuyor.
- `A2A_MODE=http` iken `MainOrchestrator` yerel departman agent'larini kurmak yerine hafif `RemoteDepartmentTarget` nesneleri kullaniyor; boylece ana API remote servisleri cagirirken agir ajan/model yuklemez.
- HTTP transport `/a2a/dispatch` uyumlu JSON payload veya JSON-RPC `/a2a` `message/send` kullanabiliyor ve sonucu generic `AgentResponse` A2A task artifact'ine sariyor.
- `session_token` HTTP payload'a tasinmiyor; sadece cozulmus ogrenci/profile metadata'si gidiyor.
- `A2A_*` env ayarlari `.env.example` icine eklendi.
- Izole dogrulama: `test_a2a_helpers.py`, `test_orchestrators.py`, `test_config.py` toplam 60 test geciyor.

## Faz 3: Agent Service Entrypoint

Departman servisleri icin ayri calisabilecek bir FastAPI entrypoint olusturulacak:

- `/health`
- `/agent-card`
- `/a2a/dispatch`
- `/metrics` veya basit latency/status endpoint'i

Servis env ile hangi departmani yukleyecegini bilir:

- `AGENT_DEPARTMENT=academic_programs`
- `AGENT_DEPARTMENT=student_affairs`
- `AGENT_DEPARTMENT=finance`
- Ileride `announcement` ve `event` icin ayri servis opsiyonu.

Baslangicta tek kod tabani, farkli process/env ile calisan servisler yeterli.

Durum: baslandi ve ilk iskelet tamamlandi.

- `src.api.agent_service.create_agent_service_app` tek departman icin FastAPI servisi kuruyor.
- `AGENT_DEPARTMENT=student_affairs|academic_programs|finance` ile departman seciliyor.
- Endpointler eklendi: `/health`, `/agent-card`, `/metrics`, `/a2a/dispatch`.
- Standarda yakin A2A yuzeyi de eklendi: `/.well-known/agent.json`, `/.well-known/agent-card.json` ve JSON-RPC `POST /a2a`. Bu yuzey `message/send` metodunu kabul eder ve sonuc olarak A2A `Task` dondurur.
- `scripts/run_agent_service.py` tek departman servisini baslatmak icin eklendi.
- `scripts/a2a_http_canary.py` calisan agent service icin `/health`, `/agent-card`, `/metrics` ve istege bagli `/a2a/dispatch` smoke testi yapar.
- `scripts/a2a_two_process_smoke.py` agent service'i ayri Python process olarak baslatir, HTTP canary'yi calistirir ve servisi temiz kapatir. Bu, PowerShell env mirasi sorunlarina takilmadan gercek process sinirini dogrulamak icindir.
- Finance canary varsayilan sorgusu kisisel harc borcu auth-guard akisini kullanir; bu sayede A2A smoke testi cevap kalitesi/RAG kaynak kalitesiyle karismadan hizli ve deterministik kalir.
- `scripts/a2a_main_http_smoke.py` finance agent service'i ayri process olarak baslatir, parent process'te `MainOrchestrator`'u `A2A_MODE=http` davranisiyla calistirir ve `MainOrchestrator -> HttpA2A -> finance agent service` zincirini dogrular.
- `src.api.a2a_dispatch` icine ortak `A2ADispatchRequest` ve internal access kontrolu tasindi; public API ve agent service ayni contract'i kullaniyor.
- `src.orchestrators.defaults.build_department_orchestrator` tek departman orkestratoru kurabiliyor.
- `A2A_TRANSPORT_PROTOCOL=rest|jsonrpc` eklendi. Default `rest` kalir; `jsonrpc` secilirse department HTTP transport `/a2a` uzerinden `message/send` kullanir ve donen A2A `Task` artifact'inden `DepartmentResponse` okur.
- Izole dogrulama: agent service JSON-RPC `message/send`, well-known AgentCard, REST dispatch ve JSON-RPC transport testleri eklendi.

Ilk canary icin onerilen komutlar:

```
$env:AGENT_DEPARTMENT="finance"
$env:AGENT_SERVICE_ID="agent-finance"
$env:AGENT_PUBLIC_URL="http://localhost:8103"
$env:SERVER_PORT="8103"
$env:SERVER_INTERNAL_API_KEY="<local-secret>"
.\venv\Scripts\python.exe -m scripts.run_agent_service
```

Ana API tarafinda:

```
$env:A2A_MODE="http"
$env:A2A_FINANCE_URL="http://localhost:8103"
$env:SERVER_INTERNAL_API_KEY="<local-secret>"
```

Agent servisi ayaktayken smoke:

```
.\venv\Scripts\python.exe -m scripts.a2a_http_canary --department finance --url http://localhost:8103 --internal-key "<local-secret>"
```

Tek komutla ayri process smoke:

```
.\venv\Scripts\python.exe -m scripts.a2a_two_process_smoke --department finance --internal-key "<local-secret>"
```

Ana orkestrator uzerinden HTTP A2A smoke:

```
.\venv\Scripts\python.exe -m scripts.a2a_main_http_smoke --internal-key "<local-secret>"
```

Ana orkestrator uzerinden shadow A2A smoke:

```
.\venv\Scripts\python.exe -m scripts.a2a_main_shadow_smoke --port 8113 --internal-key "<local-secret>"
```

Bu smoke kullanici cevabinin in-process yoldan geldigini, HTTP A2A sonucunun ise arka planda tamamlandigini dogrular. Docker'da ayni kodu kullanmak icin image rebuild gerekir; paket katmanlari gereksiz invalidate edilmemeli.

Calisan Docker stack uzerinden toplu A2A smoke:

```
.\venv\Scripts\python.exe -m scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 8
```

Bu komut `GET /health`, `GET /a2a/topology`, profilli public `POST /query` ve main orchestrator `POST /a2a` JSON-RPC `message/send` akisini ayni turda dener. JSON-RPC task metadata'sinda `trace_id` korunmazsa smoke hata verir.

Model cold-start yavas ise:

```
.\venv\Scripts\python.exe -m scripts.a2a_two_process_smoke --department finance --internal-key "<local-secret>" --request-timeout 180
```

## Faz 4: Discovery ve Registry

Mevcut `agent_registry` kullanilarak servis discovery kurulabilir:

- Servis acilista kendi `agent_id`, `department`, `endpoint`, `capabilities`, `version` bilgisini yazar.
- Periyodik heartbeat `last_heartbeat` gunceller.
- MainOrchestrator HTTP modunda aktif endpoint'i registry'den bulur.
- TTL gecmis veya health check basarisiz endpoint devre disi kabul edilir.

Basit baslangic icin env endpoint listesi de desteklenebilir:

- `A2A_ACADEMIC_PROGRAMS_URL=http://agent-academic:8101`
- `A2A_STUDENT_AFFAIRS_URL=http://agent-student:8102`
- `A2A_FINANCE_URL=http://agent-finance:8103`

Durum: baslandi.

- `TelemetryService.ensure_agent(...)` artik `endpoint` ve `capabilities` bilgisini de saklayabiliyor; bu alanlar verilmediginde mevcut registry kaydini bosaltmiyor.
- Ayrik `agent_service` startup'inda ve her internal dispatch oncesinde kendi departman orkestrator kimligini `agent_registry` tablosuna `endpoint + capabilities` ile yazar; bu sayede discovery bilgisi servis tarafinda uretilir.
- Registry'ye yazilan `capabilities` artik sadece dispatch schema bilgisini degil, `service_build` ve `service_runtime_label` metadata'sini de tasir. Boylece discovery kaydindan da hangi build/runtime kombinasyonunun publish edildigi okunabilir; yeni kolon eklemeden rollout gozlemlenebilirligi artar.
- `HttpA2ADepartmentTransport` endpoint cozumlerken once `A2A_*_URL` env override'ina bakar, deger yoksa `agent_registry` icinden ayni departmana ait aktif `department_orchestrator` endpoint'ini discovery fallback olarak kullanir.
- Unit testlerle hem registry'ye kayit yazma hem de env endpoint yokken registry fallback discovery dogrulandi.
- Discovery icin artik freshness kapisi da var: `A2A_DISCOVERY_TTL_SECONDS` sureden daha eski `last_heartbeat` tasiyan registry endpoint'i stale kabul edilir ve transport tarafinda yok sayilir.
- `agent_service` `/health` ve `/agent-card` isteklerinde de registry presence tazeler; boylece idle ama saglikli servisler sadece dispatch geldigi icin degil health/card trafiklerinde de canli gorunebilir.
- Discovery bir adim daha sertlestirildi: registry'den bulunan endpoint kullanilmadan once kisa bir `/health` probe'undan geciriliyor. `A2A_DISCOVERY_HEALTHCHECK_ENABLED`, `A2A_DISCOVERY_HEALTHCHECK_TIMEOUT_SECONDS` ve `A2A_DISCOVERY_HEALTHCHECK_CACHE_SECONDS` ile bu davranis kontrol ediliyor.
- Health probe sonucu kisa sure cache'lenir; boylece her dispatch'te tekrar `/health` vurulmaz. Unhealthy veya erisilemeyen discovered endpoint yok sayilir ve transport `a2a_endpoint_missing` fallback'ine iner.

Not:

- `announcement` ve `event` akislari su an department transport zincirinin parcasi degil; `MainOrchestrator` icinde short-circuit olarak ayrik calisir.
- 2026-04-21 itibariyla mimari hedef guncellendi: `announcement` ve `event` local ozel akis olarak kalmayacak, ayri **capability agent/service** olarak ele alinacak.
- Bu karar department-level A2A'yi bozmuyor; department orchestrator servislerine ek olarak capability servisleri de olacak.
- Ilk teknik adim tamamlandi: `agent_service` artik `announcement` ve `event` target'larini ayaga kaldirabiliyor, `event` ilk kez gercek `EventAgent` sinirina tasindi ve capability HTTP transport eklendi.
- `burs basvurusu ne zaman?` gibi finance + announcement karmasi sorular hala retrieval/policy backlog'udur; servislesme bunu otomatik kapatmaz ama capability sinirini netlestirir.
- Guncel karar cercevesi `docs/A2A_ANNOUNCEMENT_EVENT_KARAR_NOTU.md` icinde tutulur.

## Faz 4.5: Departman Icinden Uzman Agent Servislerine Gecis

Department-level A2A dis siniri oturduktan sonra ikinci dagitim seviyesi departman orkestratorunun kendi specialist agent'larini ayri A2A servis olarak cagirabilmesidir. Ilk pilot finance uzerinden yapildi; bunun sebebi soru bazli cevap eklemek degil, daha deterministik ve dusuk maliyetli bir departmanda transport sozlesmesini denemektir.

Durum: finance pilotu baslatildi ve canli Docker'da dogrulandi. Ayni contract
student affairs ve academic programs uzmanlari icin de compose/rollout
seviyesinde genellestirildi; bu son genisletmenin canli Docker smoke'u Docker
daemon erisimi geri geldiginde yapilmalidir.

- `src.a2a.specialist_transport` eklendi. `InProcessSpecialistTransport` mevcut davranisi korur; `HttpA2ASpecialistTransport` secilen uzman agent'i `/a2a/dispatch` ile remote servise gonderir.
- `A2A_SPECIALIST_MODE=inprocess|http` eklendi. Default `inprocess`; sadece ilgili departman orkestrator servisine `http` verildiginde specialist HTTP yolu kullanilir. `http` secildiginde uzman agent gizli olarak in-process calistirilmaz; remote hata kontrollu `success=False` A2A cevabidir.
- Specialist HTTP transport da `A2A_TRANSPORT_PROTOCOL=jsonrpc` secildiginde `/a2a/dispatch` yerine `/a2a` JSON-RPC `message/send` kullanabilir. Bu sayede finance orkestratoru hem server hem client davranisini daha gercek A2A modeline yaklastirir.
- `A2A_SPECIALIST_ENDPOINTS` formati `tuition_agent=http://agent-finance-tuition:8110,scholarship_agent=http://agent-finance-scholarship:8111` seklindedir. Env endpoint yoksa specialist endpoint discovery icin `agent_registry` fallback'i de kullanilabilir.
- `agent_service` artik `AGENT_SPECIALIST_ID` ile tek uzman agent servisi olarak calisabilir. `AGENT_DEPARTMENT=finance` + `AGENT_SPECIALIST_ID=tuition_agent|scholarship_agent` kombinasyonu finance uzmanlarini ayri servis yapar.
- `docker-compose.a2a-existing-infra-finance-specialists.yml` overlay'i `agent-finance-tuition` ve `agent-finance-scholarship` servislerini ekler, `agent-finance` orkestratorune de specialist HTTP endpointlerini verir.
- `scripts.a2a_rollout --include-finance-specialists` full topolojiye finance uzman servislerini dahil eder. 2026-04-21 canli dogrulamada topology `agent_count=7`, `active_count=7`, `stale_count=0` verdi: 3 departman orkestratoru, 2 capability agent, 2 finance specialist agent.
- Tuition smoke'ta ana API -> finance orchestrator -> `agent-finance-tuition` remote A2A zinciri loglarda `POST http://agent-finance-tuition:8110/a2a/dispatch 200 OK` olarak goruldu.
- Scholarship smoke'ta ilk denemede 10 sn default specialist timeout yuzunden remote istek timeout'a dusup in-process fallback ayni isi tekrar yapti. Bu genel transport policy borcu olarak duzeltildi: `A2A_SPECIALIST_TIMEOUT_SECONDS` eklendi, mevcut imajla geriye uyum icin overlay `A2A_TIMEOUT_SECONDS=${A2A_SPECIALIST_TIMEOUT_SECONDS:-60}` de set ediyor. No-build recreate sonrasi finance container runtime `A2A_TIMEOUT_SECONDS=60` dondu ve scholarship dispatch fallback uyarisi olmadan `POST http://agent-finance-scholarship:8111/a2a/dispatch 200 OK` ile tamamlandi.
- `docker-compose.a2a-existing-infra-student-specialists.yml` overlay'i `registration_agent`, `graduation_agent`, `internship_agent` ve `student_life_agent` servislerini ekler; `agent-student-affairs` orkestratorune specialist HTTP endpointlerini verir.
- `docker-compose.a2a-existing-infra-academic-specialists.yml` overlay'i `curriculum_agent`, `regulation_agent` ve `international_agent` servislerini ekler; `agent-academic` orkestratorune specialist HTTP endpointlerini verir.
- `scripts.a2a_rollout` artik `--include-student-specialists`, `--include-academic-specialists` ve `--include-all-specialists` bayraklarini destekler. Specialist bayragi kullanildiginda ilgili departman orkestratoru da otomatik rollout'a dahil edilir.
- Bu genisletme soru bazli cevap optimizasyonu degil; departman ici uzman sinirlarini finance pilotundaki A2A contract ile ayni dagitik servis modeline tasima adimidir.
- 2026-04-22 lokal dogrulama: `py_compile` gecti; `tests/unit/test_a2a_rollout.py tests/unit/test_api.py tests/unit/test_a2a_helpers.py tests/unit/test_agent_service.py` birlikte `70 passed` verdi. Tum existing-infra department/capability/specialist compose overlay'leri `docker compose ... config --quiet` ile schema olarak gecti. Canli Docker rollout dogrulanamadi; Docker daemon `dockerDesktopLinuxEngine` pipe'i bulunamadigi icin erisilemedi.
- 2026-04-22 canli Docker dogrulamasi: Docker geri geldikten sonra normal build'li `--include-all-specialists` rollout 15 dakikalik terminal timeout'una takildi ve canli image degismedi. Bu turde uygulama kodu degil compose/topoloji degistigi icin mevcut `university_support_system-app:latest` ile `--skip-build --build-id codex-20260421-231619 --transport-protocol jsonrpc --include-announcement --include-event --include-all-specialists` kosuldu ve basarili oldu. Health check 15 servisin tamaminda gecti.
- Ayni canli dogrulamada default `/a2a/topology` `agent_count=15`, `active_count=15`, `stale_count=0`, `a2a_transport_protocol=jsonrpc` dondu. Published topoloji artik 1 main orchestrator, 3 department orchestrator, 2 capability agent, 2 finance specialist, 4 student affairs specialist ve 3 academic programs specialist servisini iceriyor.
- Public `/query` smoke'lari da kosuldu: `Ders kaydı ne zaman başlıyor?` -> `student_affairs/vt`, `İkinci dönem dersleri ne?` -> `academic_programs/vt`, `Erasmus ile gelen öğrenci OMÜye geldiğinde kaydı nasıl yapılır?` -> `academic_programs/rag+llm`. `registration_agent`, `curriculum_agent` ve `international_agent` container loglarinda bu sorgular icin `POST /a2a HTTP/1.1" 200 OK` goruldu; yani department orchestrator -> specialist agent cagrilari remote JSON-RPC hatti uzerinden calisti.

## Faz 5: Guvenilirlik

HTTP transport icin zorunlu davranislar:

- Her departman cagrisinda timeout: baslangic icin 6-10 sn, VT-first cevaplarda daha dusuk.
- Transient network hatalarinda sinirli retry.
- Paralel routing'de bir departman basarisizsa diger yanitlar korunur.
- Tum departmanlar basarisizsa kontrollu hata doner.
- `task_id`, `context_id`, `query_log_id` idempotency ve izleme icin tasinir.
- In-process yol yalnizca `A2A_MODE=inprocess` ve bilerek karsilastirma yapan `shadow` akisi icin korunur. Strict `http` modunda local fallback yoktur.

Durum: baslandi.

- HTTP transport endpoint eksikligi veya remote HTTP hatasinda exception fırlatmak yerine valid `DepartmentResponse(success=False)` artifact'i donduruyor.
- `a2a_endpoint_missing` ve `a2a_transport_failed` hata kodlari eklendi; bu sayede paralel route edilen sorgularda diger departman cevaplari korunabilir.
- Unit test: endpoint eksikligi ve HTTP connect hatasi valid failed response olarak dogrulandi.

## Faz 6: Guvenlik ve PII

- Internal endpoint'lerde mevcut `X-Internal-API-Key` veya HMAC servis token zorunlu olmali.
- OTP/session token agent servislerine gereksiz tasinmamali; `MainOrchestrator` kimlik baglamini cozer, agent'a sadece gerekli profile metadata gider.
- `student_number`, `full_name` gibi alanlar telemetry'de zaten compact/sanitize ediliyor; dagitik loglarda da ayni kural uygulanmali.
- Slack user id ve session token yalniz auth boundary tarafinda kalmali.

## Faz 7: Model ve Kaynak Stratejisi

En buyuk teknik risk model/resource tekraridir:

- `academic_programs` RAG, BGE embedding, reranker ve Chroma baglantilarini yukluyor.
- Her departman ayri process olursa ayni modeller RAM/VRAM'de tekrar yuklenebilir.
- Ilk geciste RAG agir is yapan servis sayisi sinirli tutulmali.
- Alternatif olarak retrieval/rerank merkezi bir servis olarak kalabilir; departman servisleri bu servise istek atar.

Pragmatik ilk secim: HTTP A2A'yi once daha hafif bir departmanda veya finance/student gibi daha az model agirlikli akista dene; academic_programs icin model warmup ve GPU etkisini sonra olc.

## Faz 8: Shadow ve Canary Gecis

1. `shadow` mod: main cevap icin in-process sonucu kullanir, HTTP sonucu arka planda uretip farklari loglar.
2. Tek departman canary: once `finance` veya `announcement/event` HTTP moda alinir.
3. Multi-department canary: `academic_programs + finance` gibi paralel route senaryolari denenir.
4. Tam HTTP mod: tum departmanlar HTTP transport ile cagirilir.
5. Demo/emniyet icin `A2A_MODE=inprocess` kalir; `A2A_MODE=http` secildiginde local fallback calismaz.

## Faz 9: Test Plani

- Unit: A2A payload serialize/deserialize, `DepartmentResponse` extract, HTTP timeout, fallback.
- Contract: Her agent servisi `/a2a/dispatch` ile valid cevap donduruyor mu?
- E2E: API `/query` -> HTTP A2A -> departman servisi -> final cevap.
- Failure: Bir agent down iken paralel routing davranisi.
- Auth: Kisisel soru agent'a auth metadata ile gidiyor mu, session token sizmiyor mu?
- Performance: cold start, warm query, parallel query latency.

## Faz 10: Docker Compose

Gecis icin compose'a su servisler eklenebilir:

- `api`: Slack/API/MainOrchestrator
- `agent-finance`
- `agent-student-affairs`
- `agent-academic`
- `postgres`
- `redis`
- `chroma`

Ilk iterasyonda sadece bir agent servisini ayirmak yeterli. Tum servisleri ayni anda bolmek gereksiz risk yaratir.

Durum: baslandi.

- `Dockerfile` eklendi; ayni image hem API hem ayrik agent service icin kullanilabilir.
- `.dockerignore` eklendi; `.env`, virtualenv, cache, dump ve log artefaktlari image context'ine girmez.
- `docker-compose.a2a.yml` overlay eklendi. Base altyapi servislerini korur, `api` ve `agent-finance` servislerini ekler.
- `docker-compose.a2a-full.yml` overlay eklendi. Finance canary sabit kaldiktan sonra `agent-student-affairs` ve `agent-academic` servislerini de ayri process olarak acar.
- `docker-compose.a2a-existing-infra.yml` overlay eklendi. Zaten calisan Postgres/Redis/Chroma servisleri baska bir compose projesindeyse ayni external network'e baglanip sadece `api` ve `agent-finance` canary servislerini acar.
- `docker-compose.a2a-existing-infra-student.yml` overlay eklendi. Mevcut-infra finance canary uzerine ikinci HTTP departman olarak `agent-student-affairs` ekler; academic RAG servisini baslatmadan multi-department A2A dogrulamasi yapmayi saglar.
- `docker-compose.a2a-existing-infra-academic.yml` overlay eklendi. Mevcut-infra uzerinde academic programs servisini ayri HTTP agent olarak acar; model cache preflight yapilmadan calistirilmemelidir.
- `docker-compose.a2a-existing-infra-capabilities.yml` overlay eklendi. Mevcut-infra uzerinde `agent-announcement` ve `agent-event` capability servislerini ayri HTTP agent olarak acar.
- API ve agent servisleri ayni `university_support_system-app:latest` image'ini kullanir; ayni kod tabani icin ayri API/agent image'i uretmek build farki ve cache karmasasi yaratabilir.
- Rollout gorunurlugu icin build metadata image seviyesine tasindi. `Dockerfile` artik `APP_VERSION`, `BUILD_ID`, `BUILD_TIMESTAMP`, `GIT_SHA`, `IMAGE_REF` build arg'larini alip bunlari `SERVER_*` env'leri olarak image icine bake eder; boylece calisan container health'inden gercek build kimligi okunabilir.
- A2A compose overlay'leri (`docker-compose.a2a*.yml`) bu build arg'larini ortak sekilde gecer ve servis bazli `SERVER_RUNTIME_LABEL` atar. Boylece health yanitinda `api-a2a-http`, `agent-finance`, `agent-student-affairs`, `agent-academic` gibi runtime kimlikleri ayirt edilebilir.
- Build maliyetini azaltmak icin agent servislerinden `build:` bloklari kaldirildi. Artik shared image sadece `api` servisi uzerinden build edilir; finance/student/academic agent'lari ayni `university_support_system-app:latest` image'ini tekrar kullanir. Boylece ayni compose komutunda coklu servis icin ayri ayri image build etme riski azalir.
- `Dockerfile` BuildKit cache mount kullanir: apt list/cache ve pip wheel cache katmanlari korunur. Builder cache temizlenmedigi surece her rebuild'de paketlerin bastan indirilmesi beklenmez; kaynak kod degisip dependency dosyalari sabit kaldiginda en pahali katman reuse edilmelidir.
- 2026-04-22 build operasyonu: apt araclari (`build-essential`, `curl`) varsayilan image build'inden cikarildi ve `INSTALL_BUILD_TOOLS=false` default'u eklendi. Normal rollout wheel tabanli dependency install ile hizli kalir; native compile gereken yeni dependency eklenirse `scripts.a2a_rollout --install-build-tools` veya `A2A_INSTALL_BUILD_TOOLS=true` kullanilir.
- Bu akisi standartlastirmak icin `scripts/a2a_rollout.py` eklendi. Script build metadata uretir, shared image'i bir kez `build api` ile uretir ve secilen servisleri `up --no-build -d ...` ile recreate eder. Varsayilan finance rollout'tur; `--include-student`, `--include-academic`, `--include-announcement` ve `--include-event` ile department/capability servisleri eklenebilir.
- Rollout script'i recreate sonrasi health endpoint'lerini de poll eder ve beklenen `build_id` gorulmeden basarili saymaz. Boylece "container kalkti ama eski image mi calisiyor" belirsizligi azalir.
- Script varsayilan olarak legacy image adaylarini (`university_support_system-api`, `university_support_system-agent-*`) raporlar; sadece `--cleanup-legacy-images` acikca verilirse bunlari siler. Yani cleanup otomatik ve surprizli degildir.
- A2A compose overlay'lerinde `SERVER_WARMUP_ENABLED=false`, `SERVER_WARMUP_INCLUDE_RERANKER=false`, `EMBEDDING_DEVICE=cpu`, `RERANKER_DEVICE=cpu` set edilir. Canary'nin amaci once HTTP A2A hattini dogrulamaktir; model/RAG cold-start maliyeti ayri olculmelidir.
- Student affairs mevcut-infra canary'de HTTP dispatch basarili oldu. `MODEL_CACHE_HOST_DIR` ile host HuggingFace cache'i container'a baglaninca `BAAI/bge-m3` offline yuklenebiliyor; Windows lokal cache icin pratik deger `C:/Users/<kullanici>/.cache`.
- Docker canary API'sinde `A2A_TIMEOUT_SECONDS=${A2A_CANARY_TIMEOUT_SECONDS:-30}` kullanilir. Ilk cold-start embedding/BM25/LLM kurulumu 10 sn'yi asabildigi icin 10 sn timeout transport'u yanlis negatif gosterebilir.
- Academic programs mevcut-infra canary'de `agent-academic` healthy oldu ve VT tabanli "ikinci donem dersleri" sorgusu HTTP A2A uzerinden basarili dondu. Bu, academic servisin remote dispatch sozlesmesini dogrular; academic RAG/LLM icin ayrica kaynakli sorgu smoke testi kosulmalidir.
- Academic RAG/LLM smoke testi de HTTP A2A uzerinden calisti; BGE/reranker/Chroma/Groq zinciri tamamlandi. Ancak "gelen Erasmus ogrencisi kaydi" sorgusunda incoming/giden-hibe kaynaklari karisti. Bu rollout'u durduran transport problemi degil, academic RAG kalite borcudur; canary raporunda ayri izlenmelidir.
- Gercek rollout oncesi model artefact stratejisi netlesmeli: image'a prebake, volume ile HF cache mount, ya da kontrollu online download.
- `api` overlay'de `A2A_MODE=http` ve `A2A_FINANCE_URL=http://agent-finance:8103` ile calisir.
- `agent-finance` `scripts.run_agent_service` ile `AGENT_DEPARTMENT=finance` olarak baslar.
- `docker compose -f docker-compose.yml -f docker-compose.a2a.yml config` ile compose semasi dogrulandi. Not: Bu komut `.env` degerlerini genislettigi icin secret'lari konsola basabilir; paylasmadan once temizle.

Ilk compose canary:

```
docker compose -f docker-compose.yml -f docker-compose.a2a.yml up --build api agent-finance
```

Mevcut infra zaten ayaktaysa:

```
docker compose -f docker-compose.a2a-existing-infra.yml up --build -d
```

Mevcut infra uzerinde finance + student affairs canary:

```
docker compose -f docker-compose.a2a-existing-infra.yml -f docker-compose.a2a-existing-infra-student.yml up --build -d
```

Mevcut infra uzerinde finance + academic canary:

```
docker compose -f docker-compose.a2a-existing-infra.yml -f docker-compose.a2a-existing-infra-academic.yml up --build -d
```

Not: Bu komut transport'u dogrular; student/academic RAG kalitesi icin container'in embedding/reranker modellerine erisebildigi ayrica dogrulanmalidir.

Model cache preflight:

```
python -m scripts.a2a_model_cache_check --device cpu --pretty
```

Docker icinde calistirirken `MODEL_CACHE_HOST_DIR` host cache'ine baglanmali ve image guncel scriptleri icerecek sekilde rebuild edilmelidir.

Tam A2A rollout denemesi:

```
docker compose -f docker-compose.yml -f docker-compose.a2a.yml -f docker-compose.a2a-full.yml up --build
```

Not: Academic service embedding/reranker/RAG modelleri nedeniyle finance canary'ye gore daha agir calisir. Bu yuzden once finance, sonra student affairs, en son academic ayrimi tercih edilir.

## Onerilen Uygulama Sirasi

1. Canli testte gorulen kucuk routing/auth/event performans borclarini kapat.
2. `A2A_MODE` ve transport abstraction ekle, default `inprocess` kalsin.
3. HTTP client + internal `/a2a/dispatch` contract testlerini yaz.
4. Ayrik `agent_service` entrypoint'i ekle.
5. Finance veya announcement/event ile ilk HTTP canary yap.
6. Shadow mod ile in-process ve HTTP cevaplarini karsilastir.
7. Academic programs'i en son ayir; model/RAG maliyetini olcerek karar ver.

## Basari Kriterleri

- Mevcut unit testler ve live smoke testler bozulmaz.
- `A2A_MODE=inprocess` bugunku davranisi korur.
- `A2A_MODE=http` en az bir departmani ayri process'ten cevaplatir.
- Paralel route edilen sorguda iki farkli agent servisi ayni anda calisir.
- Agent down senaryosunda sistem kontrollu cevap verir, process patlamaz.
- Telemetry'de `query_log_id`, `task_id`, departman ve latency takip edilebilir.

## Guncel Karar Cizgisi

Tamam sayilabilecek kisimlar:

- In-process, HTTP ve shadow transport katmanlari mevcut.
- API, finance, student affairs ve academic agent servisleri ayri container/process olarak ayaga kalkabiliyor.
- Finance auth-guard, student affairs RAG+LLM, academic VT ve academic RAG+LLM yollari HTTP A2A uzerinden en az birer kez dogrulandi.
- Varsayilan davranis hala `A2A_MODE=inprocess`; demo/gelistirme akisi korunuyor.

Tamam sayilmamasi gereken kisimlar:

- Registry tabanli service discovery henuz yok; endpointler env/compose ile veriliyor.
- HTTP retry/circuit-breaker seviyesi henuz minimal; timeout ve failed response var ama tam dayaniklilik degil.
- Latest code Docker image'a rebuild edilmeden canli container'lara yansimiyor.
- 2026-04-21'de latest kod icin cache'li `up --build` denemesi 10 dakika timeout'a dustu; container'lar healthy kaldi ama recreate olmadi. Sonraki denemede `docker compose ... build api` cache'li sekilde hizli tamamlandi ve `up --no-build -d api agent-academic` ile yeni image canli servislere tasindi.
- API root `/`, API `/health` ve agent service `/health` + `/agent-card` artik `version/build_id/build_timestamp/git_sha/image_ref` metadata'sini dondurur. Bu, "hangi kod/image canli" sorusunu health cevabindan okumayi saglar ve A2A rollout'unu daha deterministik yapar.
- Bu degisiklik icin `py_compile` gecti; `tests/unit/test_api.py`, `tests/unit/test_agent_service.py`, `tests/unit/test_a2a_helpers.py`, `tests/unit/test_telemetry.py` toplam 39 test gecti. `docker compose ... config --quiet` ile tum A2A compose kombinasyonlari da schema seviyesinde dogrulandi.
- Ayni gun bu build metadata'yi canli Docker container'lara tasimak icin rebuild/recreate tekrar baslatildi ancak oturum kullanici tarafindan yarida kesildi. Sonraki devam turunda Docker daemon'a erisilemedigi icin canli health dogrulamasi tamamlanamadi; kod ve compose hazir, fakat son adim Docker geri geldiginde yeniden `build` + `up --no-build` ile kosulmali.
- Academic RAG cevap kalitesi icin incoming Erasmus registration borcu kapatildi: `enrich_results` sonrasi tam MADDE metni birlesiyor, incoming exchange ranking dogru source'u one cekiyor ve canli Docker A2A smoke artik `RAG` modunda kayit / ogrenci numarasi / kimlik karti cevabini dogru kaynaktan donduruyor.
- API health'te Groq primary zaman zaman `unhealthy` gorunebiliyor; source-only `RAG` cevaplar bundan etkilenmese de LLM bagimli smoke'lar ayri izlenmeli.
- Agent-down degrade davranisi da canli test edildi: finance agent container'i gecici durduruldugunda coklu route edilen query tamamen bozulmadi; student affairs cevabi korunurken finance branch'i kontrollu ulasilamiyor fallback'i verdi. Finance agent yeniden baslatildiginda health tekrar `ok` oldu.
- Shadow mode temsilci soru setiyle dogrulandi: ilk 403 sorunu internal API key eksikliginden kaynaklaniyordu, local shadow parent ile Docker agent servisleri ayni anahtarla calistirildiginda `academic_vt`, `academic_incoming_exchange`, `student_affairs` ve `finance` branch'lerinde `same_answer=True` goruldu.
- Internal A2A auth forwarding de sertlestirildi: trusted internal dispatch baglaminda parent tarafinda zaten dogrulanmis `student_id/is_authenticated` bilgisi remote agent service'e korunarak tasiniyor. Bu sayede finance auth shadow retest'inde in-process ve HTTP shadow cevaplari tekrar birebir hizalandi. Public `/query` akisi bu guveni kullanmiyor.
- 2026-04-21'de canli benchmark tooling'i de sertlestirildi: `scripts/live_question_test.py` artik API modunda `httpx` varsayilan 5 saniyelik timeout yerine 30 saniyelik timeout kullanir ve exception durumunda bos `HATA:` yerine tip / request / status / body bilgisini yazdirir. Bu degisiklik sahte timeout negatiflerini azaltmak ve A2A sorunlarini urun kalite sorunlarindan ayirmak icin yapildi.
- Bu tooling duzeltmesinden sonra `demo_showcase_stable_turk` benchmark'i canli HTTP A2A API uzerinden profil baglamiyla `6/6 yonlendirme`, `6/6 kalite` olarak gecti. Bu set department-level A2A zincirinin demo/stable yolunda saglam oldugunu gosterir.
- Daha genis `demo_showcase_broad_turk` benchmark'i ayni kosullarda `9/11 yonlendirme`, `11/11 kalite`, `0 hata` verdi. Kalan farklar artik transport degil, urun policy/routing backlog'u olarak gorunmeli: `Devam zorunlulugu var mi?` sorgusu `student_affairs + academic_programs` asiri route ediyor; `Burs basvurusu ne zaman?` sorgusu ise `finance + announcement`e gidip burs duyurulariyla birlikte alakasiz bir basvuru duyurusunu da one cikariyor.
- HTTP A2A transport sertlestirildi: `A2A_RETRY_COUNT` ve `A2A_RETRY_BACKOFF_SECONDS` ayarlari eklendi. Transport artik timeout, connection ve retryable `5xx` (`502/503/504`) durumlarinda kontrollu retry yapar; `403/404` gibi kalici hatalarda gereksiz tekrar yapmaz. Timeout/failure durumlari local fallback degil, structured `success=False` A2A cevabi uretir.
- HTTP A2A transport icin hafif circuit-breaker/cooldown da eklendi: `A2A_CIRCUIT_BREAKER_THRESHOLD` ve `A2A_CIRCUIT_BREAKER_COOLDOWN_SECONDS`. Ayni endpoint ard arda gecici olarak dusuyorsa transport kisa sure yeni istek gondermeyip `a2a_circuit_open` hata cevabi verir; bu davranis sadece timeout/request/retryable-5xx tipi gecici servis hatalarinda tetiklenir. `403` gibi kalici hatalar devreyi acmaz.
- Registry/discovery fallback da ilk adimda aktif: env endpointler hala en yuksek oncelikli override olarak kalir, ancak endpoint verilmediginde transport artik `agent_registry` uzerinden departman servisini cozumleyebilir. Bu, tam dynamic discovery degil ama env'e zorunlu bagimliligi azalttigi icin A2A rollout'unu daha dayanikli hale getirir.
- Full benchmark skoru A2A gecisinden sonra tekrar olculmeden "kalite tamam" denmemeli.
- 2026-04-21 capability rollout canli Docker uzerinde de dogrulandi. `python -m scripts.a2a_rollout --include-announcement --include-event` ile `api`, `agent-finance`, `agent-announcement` ve `agent-event` yeni build ile recreate edildi; rollout health check'i hem capability servisleri hem API icin beklenen `build_id`'yi gordu.
- Ayni gun public API uzerinden profil baglamli iki gercek smoke sorgu kosuldu: `Guncel duyurular neler?` ve `Bu hafta etkinlik var mi?`. Birinci sorgu `departments_involved=["announcement"]`, ikinci sorgu `departments_involved=["event"]` olarak dondu.
- Capability servislerinin gercekten remote A2A ile kullanildigi container loglariyla da teyit edildi. Ilk REST uyum turunda `POST /a2a/dispatch`, 2026-04-21 son JSON-RPC turunda ise `uni_a2a_agent_announcement` ve `uni_a2a_agent_event` loglarinda ilgili sorgular icin `POST /a2a HTTP/1.1" 200 OK` kaydi goruldu. Yani announcement/event capability agent'lari artik sadece kodda mevcut degil, canli API akisinda da aktif ve JSON-RPC `message/send` hattindan calisabiliyor.
- 2026-04-21 gecesinde full dagitik topoloji de tek build altinda yeniden ayağa kaldirildi: `python -m scripts.a2a_rollout --include-student --include-academic --include-announcement --include-event`. Bu rollout sonrasi `api`, `agent-finance`, `agent-student-affairs`, `agent-academic`, `agent-announcement` ve `agent-event` servislerinin tamami ayni `build_id=codex-20260421-193903` ile healthy goruldu.
- Full rollout sonrasi bes temsilci smoke sorgu birlikte dogrulandi: `Ders kaydi ne zaman basliyor?` -> `student_affairs`, `Erasmus ile gelen ogrenci OMUye geldiginde kaydi nasil yapilir?` -> `academic_programs`, `Harc ucreti ne kadar?` -> `finance`, `Guncel duyurular neler?` -> `announcement`, `Bu hafta etkinlik var mi?` -> `event`. Yani department orchestrator servisleri ile capability servisleri ayni anda aktif topolojide birlikte cevap verebildi.
- Bu full rollout sirasinda Docker build halen cold dependency install yapiyor gorundu; yani BuildKit cache mountlari tanimli olsa da pratikte apt/pip katmanlari her seferinde yeterince reuse edilmiyor. Bu, cevap kalitesi degil ama operasyonel rollout maliyeti backlog'u olarak kayda alinmali.
- 2026-04-21 gecesi bu rollout cache borcu icin ilk yapisal duzeltme de yapildi: Dockerfile'daki rollout-basina degisen `BUILD_ID/BUILD_TIMESTAMP/GIT_SHA/IMAGE_REF` metadata ENV'leri dependency install katmanlarindan sonra olacak sekilde sona tasindi. Boylece rollout script'inin her seferinde yeni build metadata vermesi artik apt/pip install katmanlarini zorunlu olarak invalidate etmemelidir. Sonraki rollout'ta bunun pratik etkisi tekrar dogrulanmali.
- Bu etki de ayni gece dogrulandi: ilk build Dockerfile degistigi icin bir kez daha pahali calisti, fakat hemen sonraki ikinci `python -m scripts.a2a_rollout --build-only ...` denemesinde `RUN apt-get ...` ve `RUN pip install ...` katmanlari tamamen `CACHED` gorundu. Yani metadata ordering duzeltmesi cache sorununu fiilen cozmeye basladi.
- 2026-04-21 gecesi operasyonel gorunurluk de tamamlandi: public `GET /a2a/topology` endpoint'i eklendi. Bu endpoint `agent_registry` kayitlarini stale/fresh yorumu ile birlikte listeler ve rollout/build dogrulamasini tek yerden okumayi saglar.
- Canli Docker rollout sonrasi `/a2a/topology` cevabi `a2a_mode=http`, `agent_count=15`, `active_count=15`, `stale_count=10` olarak goruldu. Buradaki stale kayitlarin buyuk kismi ayri HTTP servis olarak yayinlanmayan eski/local specialist agent kimlikleridir; asıl onemli olan department orchestrator ve capability servislerinin fresh endpoint + build metadata ile gorunmesidir.
- Bu karisikligi azaltmak icin `/a2a/topology` default gorunumu servis-odakli hale getirildi. Varsayilan cevap artik sadece endpoint'i olan yayinlanmis A2A servislerini dondurur; internal/local specialist kayitlar icin `include_internal=true` gerekir. Canli dogrulamada default cevap `agent_count=5`, `active_count=5`, `stale_count=0` verdi; `include_internal=true` ise onceki tam registry gorunumunu (`agent_count=15`, `stale_count=10`) korudu.
- 2026-04-21 devaminda lokal benchmark script'i API modunda calisirken import boundary problemi yakalandi: `src.api.__init__` paket importunda `src.api.main`i eager yukledigi icin capability transport -> `src.api.a2a_dispatch` -> `src.api` -> `src.api.main` -> `MainOrchestrator` dongusu olusuyordu. `src.api.__init__` lazy ve side-effect free hale getirildi; API unit testleri tekrar 15/15 gecti.
- Ayni degisiklikten sonra canli HTTP A2A API uzerinden `demo_showcase_stable_turk` tekrar kosuldu ve `6/6 yonlendirme`, `6/6 kalite`, `0 hata` verdi. Ayrica event capability icin `kategori 8 --limit 1` smoke'u `1/1` dogru yonlendi; uygun etkinlik kaydi bulunmadigi durumda kontrollu "kayit bulunamadi" cevabi uretildi.
- Finance specialist servis pilotu da eklendi. `docker-compose.a2a-existing-infra-finance-specialists.yml` ve `--include-finance-specialists` ile `tuition_agent` ve `scholarship_agent` ayri published A2A servisleri olarak gorunur. Topology canli dogrulamada `agent_count=7`, `active_count=7`, `stale_count=0` verdi.
- Specialist-service smoke'ta tuition uzmani remote A2A ile basarili dondu. Scholarship uzmani ilk denemede kisa timeout nedeniyle in-process fallback'e dusunce `A2A_SPECIALIST_TIMEOUT_SECONDS` ve geriye uyumlu `A2A_TIMEOUT_SECONDS=60` overlay ayari eklendi; no-build recreate sonrasi scholarship remote dispatch fallback'siz 200 OK dondu.
- A2A servis yuzeyi artik daha gercek A2A modeline yaklastirildi: `/.well-known/agent.json`, `/.well-known/agent-card.json` ve `POST /a2a` JSON-RPC `message/send` canli servislerde mevcut. Eski internal `/a2a/dispatch` geriye uyum icin durur.
- `A2A_TRANSPORT_PROTOCOL=rest|jsonrpc` hem compose overlay'lerine hem `scripts.a2a_rollout --transport-protocol ...` parametresine baglandi. Default `rest`; `jsonrpc` secilince main API -> department agent, main API -> capability agent ve finance department -> specialist agent cagrilari `/a2a` JSON-RPC `message/send` kullanir.
- 2026-04-21 final JSON-RPC rollout komutu: `python -m scripts.a2a_rollout --transport-protocol jsonrpc --include-student --include-academic --include-announcement --include-event --include-finance-specialists --health-timeout-seconds 180`. Final build `codex-20260421-231619` ile 8 container healthy oldu.
- Final topology: default `/a2a/topology` son dogrulamada `agent_count=8`, `active_count=8`, `stale_count=0`, `a2a_transport_protocol=jsonrpc` verdi. Published servisler: 1 main orchestrator, 3 department orchestrator, 2 capability agent, 2 finance specialist agent.
- Final smoke: direct `POST http://127.0.0.1:8103/a2a` JSON-RPC `message/send` `state=completed`, structured `department=finance`, `generation_mode=vt` dondurdu. Public `/query` finance smoke'u da `departments_involved=["finance"]`, `generation_modes=["vt"]` ile gecti.
- Capability JSON-RPC smoke da ayni build uzerinde gecti: profilli `POST /query` ile `Guncel duyurular neler?` -> `departments_involved=["announcement"]`, `Bu hafta etkinlik var mi?` -> `departments_involved=["event"]`. Announcement ve event container loglarinda bu cagrilarin `POST /a2a` uzerinden geldigi goruldu.
- `/health` ve `/a2a/topology` artik `a2a_transport_protocol` alanini dondurur. Canli topology cevabinda published tum servislerin capabilities alaninda `a2a_transport_protocol="jsonrpc"` goruldu.
- Ana API artik `OMU Main Orchestrator` A2A agent card'ini `/.well-known/agent.json` ve `/.well-known/agent-card.json` uzerinden yayinlar; `POST /a2a` JSON-RPC `message/send` ile kullanici sorgusunu alir ve `omu.user_query_response.v1` structured artifact'i dondurur. Canli smoke: `Bu hafta etkinlik var mi?` -> `task_state=completed`, `departments_involved=["event"]`, `generation_modes=["vt"]`.
- AgentCard isimlendirmesi genellestirildi; specialist hedefin display name'i zaten `Agent` ile bitiyorsa ikinci kez `Agent` eklenmez. `agent-finance-tuition` artik `OMU Tuition Agent` dondurur.
- Build cache dogrulandi: final rolloutlarda `apt` ve `pip` katmanlari `CACHED` geldi. Yalnizca degisen uygulama/data katmanlari rebuild oldu.
- Mimari borc kismen kapatildi: capability/specialist agent'lar ayri servis/topology kaydi olarak dogru calisiyor ve response artifact semantigi generic `omu.agent_response.v1` olarak baslatildi. `DepartmentResponse` payload'i ve `omu.department_response.v1` legacy extension'i geriye uyumluluk icin korunuyor; yeni entegrasyonlar generic AgentResponse semantigine gore ilerlemeli.
- 2026-04-22 canli Docker dogrulamasi: `build_id=codex-agent-response-20260422` ile full specialist topoloji yeniden ayaga kalkti. Health check 15 servisin tamaminda gecti; `/a2a/topology` default cevap `agent_count=15`, `active_count=15`, `stale_count=0`, `a2a_transport_protocol=jsonrpc`. Direct specialist JSON-RPC smoke `registration_agent` icin structured data artifact schema'sini `omu.agent_response.v1` ve legacy extension'i `omu.department_response.v1` olarak dogruladi. Public `/query` smoke'lari student affairs VT, academic programs VT ve announcement VT yollarinda basarili dondu. Profil bilgileriyle API uzerinden `demo_showcase_stable_turk` benchmark'i `6/6 yonlendirme`, `6/6 kalite`, `0 hata` verdi.
- Ayni build turunda apt araclari default kapali dogrulandi: Dockerfile `INSTALL_BUILD_TOOLS=false` iken apt RUN sadece cache/model dizinini hazirladi ve yaklasik 2 saniyede gecti. Bu turde base image ve pip katmani cold oldugu icin build yine uzun surdu; bundan sonra "paket indiriyor" gorunumu apt install'dan degil Docker base/pip cache'in sicak olmamasindan kaynaklanabilir.
- 2026-04-22 kod siniri temizligi: `SpecialistTarget` ve service target helper'lari `src.a2a.targets` modulune, response schema sabitleri `src.a2a.schemas` modulune alindi. Boylece API entrypoint sadece servis sunumu yapar; target semantigi ortak A2A katmaninda durur. `AGENT_RESPONSE_SCHEMA`, legacy `DEPARTMENT_RESPONSE_SCHEMA` ve main `USER_QUERY_RESPONSE_SCHEMA` tek yerden okunur. Lokal hedef suite `71 passed` verdi. Bu temizlik `codex-a2a-targets-20260422` build'iyle Docker'a tasindi; build cache base/apt/pip katmanlarini kullandi, full 15 servis healthy oldu ve main `/a2a` response schema smoke'u gecti.
- 2026-04-22 devam temizligi: active A2A task extraction artik `extract_agent_response` uzerinden yapiliyor; `extract_department_response` geriye uyum icin duruyor. Bu, `DepartmentResponse` Python payload modelini kaldirmiyor; sadece published A2A contract'in generic `AgentResponse` oldugunu kod seviyesinde de netlestiriyor. Lokal hedef suite `tests/unit/test_a2a_helpers.py tests/unit/test_agent_service.py tests/unit/test_orchestrators.py tests/unit/test_api.py -q` ile `99 passed` verdi. Docker build `codex-a2a-extract-agent-20260422` cache'li gecti; base/apt/pip katmanlari `CACHED`. Full 15-servis no-build recreate sonrasi tum health check'ler ayni build id ile gecti; `/a2a/topology` `15/15 active`, public `/query` academic VT smoke'u ve direct main `/a2a` `omu.user_query_response.v1` schema smoke'u basarili oldu.
- 2026-04-22 AgentCard siniri temizligi: service card ve standart AgentCard builder'lari `src.a2a.agent_cards` modulune alindi. API agent service bu fonksiyonlari import ederek eski public importlari korur, ama card/discovery sozlesmesi artik A2A katmaninda durur. Lokal hedef suite `99 passed` verdi. Docker build `codex-a2a-agent-card-20260422` cache'li gecti; full 15-servis recreate sonrasi tum health check'ler ayni build id ile basarili oldu. Topology `15/15 active`, public academic VT smoke, direct main `/a2a` schema smoke ve finance tuition AgentCard smoke (`OMU Tuition Agent`) basarili.
- 2026-04-22 execution siniri temizligi: `src.api.agent_service_execution` eklendi. Department/capability/specialist JSON-RPC `message/send` yurutmesi ve legacy `/a2a/dispatch` execution helper'lari bu module alindi; `agent_service` FastAPI yuzeyi, metrics ve registry presence sorumluluguna inceldi. Bu turda `/health` icinde registry presence refresh'in healthcheck'i bloke etmemesi de saglandi: presence refresh best-effort ve 1 sn timeout'lu. Ilk Docker recreate bu nedenle unhealthy olmustu; fix sonrasi `codex-a2a-execution-health-20260422` build'iyle full 15-servis recreate ve health check basarili oldu. Topology `15/15 active`, public academic VT smoke, direct main `/a2a` schema smoke ve tuition AgentCard smoke basarili.
- 2026-04-22 strict HTTP mode tamamlandi: capability ve specialist HTTP transportlari endpoint yok/remote hata durumunda artik local agent'a fallback yapmaz, structured `success=False` A2A cevabi uretir. Lokal hedef suite `104 passed` verdi. Canli Docker build `codex-a2a-strict-http-20260422` ile full 15-servis JSON-RPC topoloji healthy oldu; `tuition_agent` container'i durdurulup harc sorgusu atildiginda cevap local tuition fallback'e dusmedi ve kontrollu `yalnizca A2A HTTP uzerinden calisir` hata cevabini verdi. Container yeniden baslatildi, topology tekrar `15/15 active` oldu.
- 2026-04-22 trace ve Docker stack smoke paketi tamamlandi: `trace_id/span_id/parent_span_id` main, department, specialist, announcement ve event A2A hop'larinda tasiniyor; telemetry payload'lari bu trace ozetini sakliyor. `scripts.a2a_docker_stack_smoke` calisan stack icin `/health`, `/a2a/topology`, public `/query` ve main `/a2a` JSON-RPC `message/send` kontrollerini tek komutta yapar. Canli build `codex-20260422-204815` ile full topology `15/15 active`, `stale_count=0`, `a2a_transport_protocol=jsonrpc`; smoke response task/artifact/message metadata'sinda ayni `trace_id` dogrulandi. Build sirasinda apt/pip katmanlari `CACHED` geldi.
- 2026-04-23 servis kimligi sertlestirmesi eklendi: A2A transportlari `X-A2A-Caller-ID` ve `X-A2A-Target-ID` header'larini gonderir. Main ve agent service A2A endpointleri target header'i beklenen servis kimligiyle eslestirir; `A2A_REQUIRE_SERVICE_IDENTITY=true` caller header'ini zorunlu yapar, `A2A_ALLOWED_CALLER_IDS` optional allowlist'tir. A2A Docker overlay'leri bu zorunlulugu varsayilan acik calistirir; lokal/inprocess kullanim geriye uyum icin kapali kalir. Smoke scriptleri de yeni kimlik header'larini tasir.
- Runtime dogrulama da tamamlandi: `codex-20260423-005702` build'iyle full JSON-RPC topoloji 15/15 healthy oldu. Stack smoke topology/public query/main JSON-RPC/trace kontrollerini gecti. `POST /a2a` endpoint'i sadece shared secret ile, caller identity olmadan cagrildiginda `403` dondurdu; boylece servis kimligi zorunlulugu canli Docker overlay'inde de aktif goruldu.
- 2026-04-23 AgentCard preflight eklendi: A2A transportlari `A2A_DISCOVERY_AGENT_CARD_ENABLED=true` iken remote endpoint'e is gondermeden once `GET /agent-card` okur ve beklenen service id, target kind, target ve transport protokolunu dogrular. Bu kontrol department, capability ve specialist transportlarinda ortaktir. Lokal default kapali; A2A Docker overlay'lerinde varsayilan acik.
- Runtime dogrulama `codex-20260423-010752` build'iyle yapildi: full JSON-RPC topoloji 15/15 healthy, stack smoke basarili. API env'inde `A2A_DISCOVERY_AGENT_CARD_ENABLED=true`; akademik agent loglarinda remote specialist `POST /a2a` cagrisi oncesi `GET /agent-card` goruldu. Internal servisler icin artik config/registry endpoint bulma + AgentCard kimlik/capability/protokol dogrulama + A2A task gonderme sirasi uygulanir. Dis agentlarla otomatik guven/onboarding halen yoktur; bunun icin ayrica trust/allowlist/auth modeli gerekir.
- 2026-04-23 request-signature katmani eklendi: `A2A_REQUIRE_REQUEST_SIGNATURE=true` iken internal A2A POST istekleri timestamp, nonce, canonical body hash ve HMAC-SHA256 signature header'lari tasir. Department, capability, specialist transportlari ve smoke scriptleri bu header'lari uretir; main ve agent service `/a2a` + `/a2a/dispatch` yuzeyleri dogrular. Lokal default kapali; Docker A2A overlay'lerinde varsayilan acik. `A2A_REQUEST_SIGNATURE_SECRET` verilmezse imza secret'i internal API key'den cozulur.
- Runtime dogrulama `codex-20260423-012112` build'iyle tamamlandi: full JSON-RPC topoloji 15/15 healthy, stack smoke basarili. `A2A_REQUEST_SIGNATURE_SECRET` bos default'a cekildikten sonra no-build recreate ile internal key fallback'i de dogrulandi. Eksik imzali main `/a2a` cagrisi `403` ve `A2A request signature headers eksik.` cevabi dondurdu. Bu, shared secret + caller/target kimliginin uzerine body butunlugu ve zaman penceresi ekleyen genel servis-auth sertlestirmesidir; cevap optimizasyonu degildir.
- 2026-04-23 diagnostics/observability endpoint'i eklendi: `GET /a2a/diagnostics` son pencere icin query/task sayilarini, failure sayilarini, response time ozetini, ajan bazinda total/completed/failed/failure_rate, `latency_sample_count`, avg/max latency, son hata ve recent failure orneklerini dondurur. Agent task telemetry sonucu artik `latency_ms` saklayabilir; `latency_sample_count` eski latency'siz kayitlar varken ortalamanin kac ornekten hesaplandigini acik eder.
- Runtime dogrulama `codex-20260423-014129` build'iyle tamamlandi: base/apt/pip katmanlari `CACHED`, full JSON-RPC topoloji 15/15 healthy. `scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15 --timeout 120` health/topology/public query/main JSON-RPC ve diagnostics kontrollerini gecti. Diagnostics cevabinda `agent_task_count=12`, `agent_task_failure_count=0`, `curriculum_agent` ve `event_agent` icin `latency_sample_count=2`, `recent_failures=[]` goruldu. Lokal hedef ve genis A2A unit dogrulamalari sirasiyla `63 passed` ve `115 passed` verdi.
- 2026-04-23 CI/e2e kapisi eklendi: `.github/workflows/a2a-docker-e2e.yml` PR ve manuel tetikte hedef A2A unit setini, taze infra + Alembic migration + seedleri, full JSON-RPC A2A rollout'u ve `scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15` smoke'unu kosar. Bu kalite benchmark'i degil, dagitik topolojinin otomatik e2e guvencesidir. Lokal statik dogrulama: workflow YAML parse edildi ve full compose config CI network ayarlariyla gecti; GitHub runner'da ilk gercek workflow calistirmasi henuz yapilmadi.
- 2026-04-23 state transition history eklendi: `src.a2a.state` task metadata'sinda standart `state_transitions` listesi uretir. Request task `submitted`, response task `submitted -> working -> completed` gecmisini actor/task/message/timestamp bilgileriyle tasir. Main JSON-RPC response ve department/specialist/capability response task'lari bu modeli kullanir. Smoke script artik main JSON-RPC result metadata'sinda son uc state'in `submitted, working, completed` olmasini zorunlu kontrol eder.
- Runtime dogrulama `codex-20260423-015506` build'iyle tamamlandi: full JSON-RPC topoloji 15/15 healthy, stack smoke basarili ve state transition history canli response'ta goruldu. Lokal genis A2A unit seti tekrar `115 passed` verdi. Bu streaming/push degil; ama AgentCard'da ilan edilen `stateTransitionHistory=True` kabiliyetinin somut, test edilen metadata karsiligidir.
- 2026-04-23 kod siniri temizligi: main orchestrator A2A helper'lari `src.api.main_a2a` modulune alindi; `src.api.main` route/dependency/auth yuzeyine inceldi. Main API ve standalone agent service tarafindaki JSON-RPC success/error builder tekrarÄ± `src.a2a.jsonrpc` ortak modulune tasindi. Lokal dogrulama: `py_compile` gecti; hedef API/agent service testleri `40 passed`, genis A2A unit seti tekrar `115 passed`.
- 2026-04-23 AgentResponse isimlendirme temizligi: `build_agent_response_task` primary helper olarak eklendi; `build_department_response_task` geriye uyum alias'i olarak duruyor. Production cagrilari generic isme tasindi, `extract_agent_response` ana okuma helper'i olarak korunuyor. Lokal hedef testler `90 passed`, genis A2A unit seti `116 passed`. Runtime dogrulama `codex-20260423-020550`: full JSON-RPC topology 15/15 healthy, stack smoke state transition ve diagnostics kontrolleriyle basarili.
- 2026-04-23 Docker tekrar acildiktan sonra canli stack once mevcut `codex-20260423-020550` build'iyle yeniden dogrulandi: API health `healthy`, Groq primary `healthy`, full JSON-RPC topology `15/15 active`, stack smoke public query/main JSON-RPC/state transitions/diagnostics kontrolleri basarili.
- 2026-04-23 A2A AgentResponse adapter adimi tamamlandi: `src.a2a.responses` modulunde `AgentResponse` alias'i, `validate_agent_response` ve `build_failed_agent_response` yardimcilari eklendi. A2A-facing transport katmanlari artik generic contract adini kullanir; mevcut `DepartmentResponse` payload modeli, legacy REST `/a2a/dispatch` ve legacy schema extension geriye uyumluluk icin korunur. Bu davranis degisikligi degil, agent sozlesmesini kod seviyesinde daha okunur hale getiren contract temizligidir.
- Bu adapter adimi icin `py_compile` gecti; hedef testler `90 passed`, genis A2A unit seti `116 passed`. Degisiklik `codex-20260423-113245` build'iyle Docker'a tasindi; dependency katmanlari `CACHED`, sadece `src` ve `data` yeniden kopyalandi. Yeni build uzerinde stack smoke tekrar basarili: transport `jsonrpc`, topology `15/15 active`, diagnostics failure `0`, recent failure yok. Benchmark calistirilmadi.
- 2026-04-23 AgentResponse adapter alias olmaktan cikarildi: `src.a2a.responses.AgentResponse` artik gercek generic Pydantic modelidir. Primary A2A artifact `omu.agent_response.v1` agent-semantikli payload tasir (`agent_id`, `agent_name`, `agent_role`, `capability`, opsiyonel `department`, `answer`, `sources`, `success`, `metadata`). `DepartmentResponse` sadece ic orchestrator/sentez ve legacy REST uyumlulugu icin mapper arkasinda kalir.
- `extract_agent_response` generic model, `extract_department_response` legacy model dondurur. Yeni unit test bu ayrimi kilitler. Lokal dogrulamalar: `py_compile` gecti; hedef suite `91 passed`, genis A2A unit seti `117 passed`.
- Runtime dogrulama `codex-20260423-115742` build'iyle tamamlandi: dependency katmanlari `CACHED`, full JSON-RPC topology `15/15 active`, diagnostics failure `0`, recent failure yok. Direkt event agent JSON-RPC kontrolunde artifact `schema=omu.agent_response.v1`, payload `agent_id=event_agent`, `agent_role=capability_agent`, `capability=event` ve `answer` alanlariyla dondu; main `UserQueryResponse` alanlariyla karismadigi dogrulandi. Benchmark calistirilmadi.
- 2026-04-23 dis agent trust/onboarding altyapisi eklendi. JSON-RPC `/a2a` endpointleri internal API key yolunu korurken, API key yoksa kapali-varsayilan external partner auth yolunu deneyebilir. External yol `A2A_EXTERNAL_TRUST_ENABLED=true`, explicit allowlist ve varsayilan HMAC imza ister; target id eslesmesi zorunludur. Legacy `/a2a/dispatch` internal-only kalir.
- `POST /a2a/external/validate` admin endpoint'i eklendi. Internal API key ile calisir, allowlisted partner icin endpoint/AgentCard dogrular ve standart `/.well-known/agent.json`, `/.well-known/agent-card.json`, geriye uyumlu `/agent-card` yollarini dener. Bu endpoint dis agent'i otomatik route'a eklemez; sadece trust/onboarding kararini dogrulanabilir hale getirir.
- Standart AgentCard'lar HMAC tabanli A2A header'larini `securitySchemes` olarak yayinlar. Main orchestrator card URL'i icin `SERVER_PUBLIC_URL`, standalone servisler icin `AGENT_PUBLIC_URL` kullanilabilir. `.env.example` external trust ayarlarini icerir. Lokal dogrulama: `py_compile` gecti; genis A2A unit seti `125 passed` verdi. Docker runtime dogrulamasi `codex-20260423-123159` build'iyle tamamlandi: full JSON-RPC topology `15/15 active`, diagnostics failure `0`, stack smoke basarili. Runtime ek kontrolunde main `/.well-known/agent.json` HMAC `securitySchemes` alanlarini yayinladi ve `POST /a2a/external/validate` external trust kapaliyken `external_trust_disabled` dondurdu.
- 2026-04-23 dis agent + benchmark devam dogrulamasi: external trust ve benchmark cache-bypass degisiklikleri `codex-20260423-125011` build'iyle Docker'a tasindi. Full JSON-RPC topoloji `15/15 active`, stack smoke health/topology/public query/main JSON-RPC/state transitions/diagnostics kontrolleri basarili oldu. Benchmark harness varsayilan olarak profilli payload + `disable_cache=true` kullanir ve A2A transport fallback cevaplarini `a2a_transport_fallback` uyarisi olarak ayirir. Kategori A kucuk API benchmark'i cache bypass ile `dept=4/4`, `mode=3/4`, `facts=8/15`, `clean_quality=3/4` verdi; tek basarisiz mod, 60 sn specialist HTTP timeout'undan kaynaklanan genel performans/timeout sinyalidir.
- 2026-04-23 observability devam adimi: main orchestrator remote department branch'lerinden `success=False` ve `error` kodu `a2a_` ile baslayan cevap alirsa bunu agent task failure olarak `main_orchestrator -> department_orchestrator` seviyesinde kaydeder. Bu, kullanici cevabinda gorunen A2A transport fallback'in diagnostics ekraninda kaybolmamasini saglar; normal no-info veya clarification durumlari failure sayilmaz. Lokal genis A2A unit seti `128 passed`; runtime build `codex-20260423-130509` ile full JSON-RPC stack smoke tekrar basarili oldu.
- 2026-04-23 external mock smoke eklendi: `scripts/a2a_external_mock_smoke.py` lokal HTTP mock partner agent baslatir, AgentCard discovery + allowlist validation + inbound HMAC auth + mock `/a2a` JSON-RPC response akisini dogrular. Unit testi `tests/unit/test_a2a_external_mock_smoke.py` ile kilitlendi. Guncel genis A2A unit seti `129 passed`. Bu, gercek dis partner gelene kadar external onboarding sozlesmesini ucuz ve deterministik tutan testtir; gercek partner geldiginde ayni policy `A2A_EXTERNAL_*` env'leri ve `/a2a/external/validate` ile calistirilir.
- 2026-04-23 benchmark tooling: `scripts/run_quality_benchmark.py` API modunda `/health` preflight yapar; Docker/API kapaliyken rapor uretmez. `scripts/summarize_quality_benchmark.py` benchmark JSON'unu genel problem siniflarina ayirir. Docker daemon bu turda kapali oldugu icin full runtime benchmark beklemede; son gecerli kucuk kategori A siniflandirmasi `docs/archive/benchmarks/quality_benchmark_problem_summary_20260423_125450.md`.
- 2026-04-23 full runtime benchmark Docker/API tekrar acildiktan sonra `codex-20260423-130509` stack'i uzerinde kosuldu. Once `scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15 --timeout 120` gecti: topology `15/15 active`, stale yok, diagnostics failure yok. Ardindan `scripts.run_quality_benchmark --use-api --api-base-url http://127.0.0.1:8000 --api-timeout 120 --llm-profile fast --cold-start` tamamlandi. Raporlar: `tests/archive/benchmarks/quality_benchmark_20260423_174611.json`, `docs/archive/benchmarks/quality_benchmark_report_20260423_174611.md`, `docs/archive/benchmarks/quality_benchmark_problem_summary_20260423_174611.md`.
- Benchmark sonucu A2A transport/routing acisindan saglam: departman dogrulugu `25/25 (100%)`, uretim modu `24/25 (96%)`, temiz kalite `24/25 (96%)`, hata `0`. Anahtar bilgi kapsami `70/100 (70%)` oldugu icin bundan sonraki problem A2A'nin "gercek olup olmamasi" degil, genel RAG/evidence/sentez kalitesidir. Problem siniflari: `low_fact_coverage=14`, `clean_pass=10`, `generation_mode_mismatch=1`, `quality_warning=1`. Bu sinyal soru-bazli statik yamaya degil, retrieval context paketleme ve LLM sentez talimatlarinda kaynak kosullarinin eksiksiz korunmasina yonlendirmeli.
- Benchmark sonrasi 60 dakikalik diagnostics penceresi ayrica `agent_task_failure_count=4` gosterdi; recent failure ornekleri Q5 preview'una bagli iki departman branch timeout'u ve iki specialist transport failure idi. Bu pencere onceki denemeleri de icerdigi icin dogrudan `20260423_174611` full benchmark'ina atfedilmemeli. Buna karsi benchmark harness'i genel olarak guncellendi: API modunda baslangic/bitis `/a2a/diagnostics` snapshot'i alinir, JSON/Markdown rapora `diagnostics` delta ve `a2a_query_failure_delta` / `a2a_agent_task_failure_delta` metrikleri yazilir. Summarizer da `run_level_signals.a2a_diagnostics_failures` sinyalini uretir.
- Delta mekanizmasi `tests/archive/benchmarks/quality_benchmark_20260423_175741.json` tek Q5 kosusuyla dogrulandi: `a2a_agent_task_failure_delta=0`, `agent_task_count` deltasi `3`. Ek runtime kontrolunde 1 dakikalik diagnostics penceresi temiz dondu ve stack smoke tekrar basarili oldu. Dolayisiyla topoloji ayakta; kalan borc benchmark yukunde bazi RAG/specialist branch'lerin timeout riskidir.
- Bu timeout riski icin SLA ayari ayrildi: `A2A_DEPARTMENT_TIMEOUT_SECONDS` eklendi ve main -> department transportu artik bu degeri kullanir; unset ise `A2A_TIMEOUT_SECONDS` ile geriye uyum korunur. Docker A2A API overlay'lerinde default `75s` verildi. Boylece department icindeki `A2A_SPECIALIST_TIMEOUT_SECONDS=60` butcesi varken main branch'in 30 saniyede erken kesilmesi engellenir; capability/specialist timeoutlari degistirilmedi.
- SLA ayrimi `codex-20260423-180227` build'iyle canli Docker'a tasindi. Build cache dogru davrandi: base/apt/pip katmanlari `CACHED`, sadece `scripts/src/data` kopyalandi. Full 15 servis healthy, stack smoke basarili. API container env'i `A2A_TIMEOUT_SECONDS=30`, `A2A_DEPARTMENT_TIMEOUT_SECONDS=75` olarak dogrulandi. Yeni build uzerinde delta'li Q5 benchmark'i `tests/archive/benchmarks/quality_benchmark_20260423_180605.json` sonucunda `a2a_agent_task_failure_delta=0`, `agent_task_count_delta=3`, sure `30922.7 ms`; summarizer bu kosuyu `slow_response` sinifina koydu. Yani artik failure degil, performans maliyeti olarak izlenmeli.
- Latency ayrimi icin `scripts/compare_a2a_latency.py` eklendi. Q5 uzerinde ilk olcumler: API-only HTTP A2A `4173.5 ms`; warmup+measured karsilastirmada HTTP A2A `7080.0 ms`, lokal in-process `38910.6 ms`, HTTP A2A diagnostics delta `agent_task_failures=0`. Bu, mevcut yavasligin A2A transport'tan ziyade RAG/LLM/model/provider kosullarindan geldigini gosterir. Not: lokal in-process kosuda Groq/OpenAI-compatible provider baglanti hatalari oldugu icin bu oran kesin transport overhead'i degildir; tam adil test icin ayni Docker network'unde `A2A_MODE=inprocess` calisan ikinci API container'i ile karsilastirma yapilmalidir.

Pragmatik sonraki sira:

1. A2A transport/topoloji, servis kimligi, imza, AgentCard preflight, diagnostics, state transition history, CI e2e kapisi ve temel kod/contract sinirlari full specialist topolojide canli dogrulandi.
2. Dis agent trust/onboarding modeli kod ve Docker runtime seviyesinde dogrulandi; dis partneri gercekten baglamak icin sonraki adim ortamda allowlist + endpoint + secret tanimlayip validation endpoint'ini gercek partner AgentCard'i ile calistirmaktir.
3. Full benchmark artik kosuldu; bundan sonra A2A transport gecisini cevap optimizasyonu ile karistirma. Yeni iyilestirmeler benchmark'ta genel problem siniflarini dusurmeli: ozellikle `low_fact_coverage` ve tek kalan `generation_mode_mismatch`.
4. LLM bagimli smoke'lar icin Groq/API health durumunu ayri izle. Groq limit/timeout riski icin `google_ai` provider'i Gemini OpenAI-compatible endpoint'iyle ayri fallback slotu olarak kullanilabilir; Google model adlari Groq/OpenAI model namespace'ine karistirilmamalidir. Google fallback hiz odakliysa `GOOGLE_AI_REASONING_EFFORT=none` kullanilir.
