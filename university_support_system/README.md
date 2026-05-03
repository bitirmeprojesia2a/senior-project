# Universite Kurumsal Destek Sistemi

> RAG, LLM, OTP/session auth ve uygulama ici A2A orkestrasyonu ile universite destek sorgularini cevaplayan cok departmanli destek sistemi.

## Proje Ozeti

Bu repo artik sadece "RAG cekirdegi" degil; calisan bir uygulama yuzeyi sunar. Guncel kod tabaninda:

- `finance`, `student_affairs` ve `academic_programs` departmanlari aktif olarak desteklenir
- duyuru ve etkinlik sorgulari ayri capability agent akislari ile ele alinir
- OTP/session tabanli kimlik dogrulama endpoint'leri vardir
- cok turlu konusma baglami ve follow-up cozumu bulunur
- FastAPI giris noktasi, ic A2A dispatch ve benchmark/demo scriptleri calisir durumdadir

Slack, dis HTTP A2A genisletmeleri ve daha ileri dagitim katmanlari halen gelistirilebilir alanlar olarak durmaktadir; ancak ana uygulama akisi calismayan iskelet seviyesinde degildir.

## Guncel Ozellikler

- Hibrit retrieval: BM25 + ChromaDB semantic search + cross-encoder reranker
- Rol bazli LLM kullanimi: routing, conversation, specialist synthesis ve global synthesis icin ayri model tercihleri
- Capability kisa yolu: duyuru ve etkinlik sorgularini gereksiz akademik retrieval'a sokmadan ayri ele alma
- Conversation memory: context id uzerinden follow-up cozumleme ve kaynak/topic hint kullanimi
- Profile/auth akisi: OTP isteme, dogrulama, session resolve ve logout endpoint'leri
- Telemetry: kisa preview ve yapisal metadata uzerinden query log / ajan gorevi gozlenebilirligi
- A2A topology: yayinlanan departman/capability servislerini ve internal registry kayitlarini ayri izleme
- Demo ve benchmark scriptleri: showcase, follow-up ve profile context senaryolari
- Docker tabanli lokal kurulum ve Azure VM runbook'u

## Guncel Mimari

```text
Kullanici / istemci
    |
    v
FastAPI giris katmani
  - /query
  - /auth/*
  - internal /a2a/dispatch
  - /a2a/topology
    |
    v
Query / auth / profile helper akislari
    |
    v
MainOrchestrator
  - conversation resolve
  - department routing
  - capability routing
  - multi-department synthesis
    |
    v
A2A servisleri
  - main orchestrator: api
  - department orchestrator: finance
  - department orchestrator: student_affairs
  - department orchestrator: academic_programs
  - capability agent: announcement
  - capability agent: event
    |
    v
RAG + LLM katmani
  - document loader / preprocessor / chunker
  - embedding / retriever / reranker
  - OpenAI-compatible/Groq primary
  - Google AI Gemini OpenAI-compatible API fallback
  - Ollama local fallback
    |
    v
Yanit + kaynaklar + telemetry + conversation memory
```

## Teknoloji Yigini

| Bilesen | Teknoloji | Not |
|---|---|---|
| Dil | Python 3.11+ | Ana uygulama dili |
| Web/API | FastAPI | Aktif giris yuzeyi |
| ORM ve migration | SQLAlchemy 2 + Alembic | Aktif |
| Veritabani | PostgreSQL 15 | Aktif |
| Cache / yan servisler | Redis 7 | Aktif servis, kullanim senaryoya gore degisir |
| Vektor veritabani | ChromaDB | Aktif |
| API LLM | OpenAI-compatible / Groq | Aktif dagitimda varsayilan LLM yolu |
| API fallback LLM | Google AI Gemini OpenAI-compatible API | Groq limit/timeout durumunda opsiyonel yedek yol |
| Yerel LLM | Ollama | Lokal fallback veya izole dogrulama icin |
| Embedding | BAAI/bge-m3 | Varsayilan embedding modeli |
| Reranker | nreimers/mmarco-mMiniLMv2-L6-H384-v1 | Varsayilan reranker |
| Konteyner | Docker Compose | Lokal ve VM kurulumlarinda kullanilir |

## Hizli Baslangic

### 1. Python ortami

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

### 2. Ortam degiskenleri

```powershell
copy .env.example .env
```

Temiz bir makinede Hugging Face modellerinin indirilebilmesi icin gerekirse su iki ayari ekleyin:

```text
EMBEDDING_LOCAL_FILES_ONLY=false
RERANKER_LOCAL_FILES_ONLY=false
```

### 3. Docker servisleri

```powershell
docker compose up -d
docker compose ps
```

Dagitik A2A rollout icin paylasilan image'i tek sefer build edip secili
agent servislerini `--no-build` ile yeniden ayaga kaldirmak daha dogrudur:

```powershell
python -m scripts.a2a_rollout
python -m scripts.a2a_rollout --include-student --include-academic
python -m scripts.a2a_rollout --include-student --include-academic --include-announcement --include-event
python -m scripts.a2a_rollout --include-student --include-academic --include-announcement --include-event --include-finance-specialists
python -m scripts.a2a_rollout --include-announcement --include-event --include-all-specialists
python -m scripts.a2a_rollout --transport-protocol jsonrpc --include-announcement --include-event --include-all-specialists
```

Bu helper:

- build metadata (`build_id`, `build_timestamp`, `git_sha`) uretir
- shared `university_support_system-app:latest` image'ini bir kez build eder
- secili A2A servislerini ayni image ile recreate eder
- rollout sonrasinda `/health` endpoint'lerinde yeni `build_id`nin gorunmesini bekler
- eski `university_support_system-api` / `university_support_system-agent-*` image adaylarini raporlar; istenirse `--cleanup-legacy-images` ile temizler

Boylece her agent icin ayri ayri build tetiklenmez.
Docker layer cache normal kosullarda `apt` ve `pip` katmanlarini yeniden indirmeden
kullanir; `requirements*.txt`, Dockerfile'in dependency bolumu veya cache durumu
degismediyse rebuild hizli gecmelidir.
Docker image varsayilan olarak `build-essential` / `curl` gibi apt build araclarini
kurmaz; mevcut dependency seti wheel odakli oldugu icin normal rollout'ta bu daha
hizlidir. Yeni bir dependency native compile isterse helper `--install-build-tools`
ile eski apt kurulumunu bilerek acabilirsiniz:

```powershell
python -m scripts.a2a_rollout --install-build-tools --include-announcement --include-event
```

Sadece compose/topoloji degistiyse ve mevcut image yeterliyse gereksiz rebuild
beklememek icin ayni helper `--skip-build` ile kullanilabilir:

```powershell
python -m scripts.a2a_rollout --skip-build --build-id <canli-build-id> --transport-protocol jsonrpc --include-announcement --include-event --include-all-specialists
```

Bu mod yeni kodu image'a tasimaz; yalnizca mevcut image ile servisleri recreate
eder. Uygulama kodu veya dependency degistiyse normal build'li rollout tercih
edilmelidir.

A2A servis durumunu kontrol etmek icin:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/a2a/topology
Invoke-RestMethod "http://127.0.0.1:8000/a2a/topology?include_internal=true"
python -m scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 8
```

Slack botu normal monolitik runtime veya dagitik A2A runtime ile baslatilabilir:

```powershell
# Lokal monolitik Slack bot
python -m scripts.run_slack_bot --runtime inprocess

# Lokal makinede calisan A2A agent endpointlerine baglanan Slack bot
python -m scripts.run_slack_bot --runtime a2a --a2a-endpoint-profile local --transport-protocol jsonrpc
```

Docker uzerinden Slack runtime'larini ayri servisler olarak acip kapatmak icin:

```powershell
# A2A stack ayaktayken Slack botu dagitik A2A modda baslat/kapat
python -m scripts.slack_runtime up --runtime a2a
python -m scripts.slack_runtime stop --runtime a2a

# Monolitik Slack botu Docker'da baslat/kapat
python -m scripts.slack_runtime up --runtime inprocess
python -m scripts.slack_runtime stop --runtime inprocess

# Log ve durum
python -m scripts.slack_runtime logs --runtime a2a
python -m scripts.slack_runtime status --runtime a2a
```

Ayni Slack app tokenlariyla iki Socket Mode botunu ayni anda calistirmayin. Iki surumu ayni anda Slack'te denemek isterseniz ikinci Slack app icin `SLACK_A2A_BOT_TOKEN`, `SLACK_A2A_SIGNING_SECRET`, `SLACK_A2A_APP_TOKEN` tanimlayip A2A botunu `SLACK_ENV_PREFIX=SLACK_A2A` ile baslatin.

Varsayilan topology cevabi yalnizca yayinlanan gercek A2A servislerini gosterir.
Ana API artik `main_orchestrator` olarak kendi `/.well-known/agent.json` ve
`POST /a2a` JSON-RPC yuzeyini de yayinlar; bu nedenle full A2A rollout
topolojisinde main orchestrator + departman orkestratorleri + capability
agent'lar + specialist agent'lar birlikte gorunur.
Finance specialist servisleri aciksa varsayilan topology cevabinda
`tuition_agent` ve `scholarship_agent` da yayinlanan A2A servisleri olarak
gorunur. `include_internal=true` ise endpoint'i olmayan internal/local uzman
ajan kayitlari dahil tum registry kayitlarini denetim icin dondurur.

Agent servisleri ayrica A2A discovery ve JSON-RPC yuzeyi sunar:

```powershell
Invoke-RestMethod http://127.0.0.1:8103/.well-known/agent.json
```

Varsayilan HTTP transport `A2A_TRANSPORT_PROTOCOL=rest` ile eski internal
`/a2a/dispatch` sozlesmesini kullanir. Deneysel/standarda daha yakin yol icin
`A2A_TRANSPORT_PROTOCOL=jsonrpc` secildiginde transport `/a2a` uzerinden
JSON-RPC `message/send` kullanir. Bu secim department, capability ve specialist
servis cagrilarinda ayni transport sozlesmesini uygular. Rollout helper'da
bunun karsiligi `--transport-protocol jsonrpc` parametresidir.

A2A internal cagrilari ortak secret'a ek olarak `X-A2A-Caller-ID` ve
`X-A2A-Target-ID` servis kimligi header'larini da tasir. Normal lokal modda bu
katman geriye uyumlu kalir; Docker A2A overlay'lerinde
`A2A_REQUIRE_SERVICE_IDENTITY=true` varsayilan gelir. Istege bagli
`A2A_ALLOWED_CALLER_IDS` verilirse yalniz izinli servis kimlikleri kabul edilir.

Docker A2A overlay'lerinde `A2A_DISCOVERY_AGENT_CARD_ENABLED=true` ile transport
remote endpoint'e is gondermeden once `/agent-card` okur ve beklenen service id,
target kind, target ve transport protokolunu dogrular. Boylece internal
servisler once kimlik/capability/protokol uyumundan gecip sonra `/a2a` veya
`/a2a/dispatch` cagrisi alir. Dis agent onboarding otomatik degildir; dis
entegrasyon icin endpoint'e ek olarak trust/allowlist/auth politikasi gerekir.

Docker A2A overlay'lerinde `A2A_REQUIRE_REQUEST_SIGNATURE=true` de varsayilan
aciktir. Bu modda internal A2A POST istekleri body hash, timestamp, nonce ve
HMAC-SHA256 signature header'lari tasir. Lokal gelistirme default'u kapali
kalir. `A2A_REQUEST_SIGNATURE_SECRET` verilmezse imza secret'i internal API
key'den cozulur; dis agent entegrasyonunda bu imza mekanizmasi endpoint trust, key
rotation ve allowlist politikasi ile birlikte ele alinmalidir.

A2A runtime sagligini failure/latency odakli izlemek icin diagnostics endpoint'i
de vardir:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/a2a/diagnostics?window_minutes=60&recent_limit=10"
```

Bu cevap query/task sayilarini, failure sayilarini, response time ozetini,
ajan bazinda failure rate'i, `latency_sample_count` ile avg/max latency'yi ve son
failure orneklerini dondurur. `scripts.a2a_docker_stack_smoke` JSON-RPC smoke
kosarken bu endpoint'i de kontrol eder.

A2A task metadata'si `state_transitions` listesi de tasir. Senkron JSON-RPC
`message/send` cevaplarinda beklenen gecis `submitted -> working -> completed`
seklindedir; smoke script main JSON-RPC response uzerinde bu gecmisi dogrular.
Bu streaming/push degil, `stateTransitionHistory` kabiliyetinin test edilen
metadata karsiligidir.

GitHub Actions tarafinda `.github/workflows/a2a-docker-e2e.yml` full A2A e2e
kapisi olarak bulunur. Workflow taze Docker infra baslatir, migration/seed
adimlarini calistirir, full JSON-RPC A2A topolojiyi rollout eder ve stack smoke
ile topology, public query, main JSON-RPC ve diagnostics kontrollerini kosar.

### 4. Veritabani migration

```powershell
python -m alembic upgrade head
```

### 5. Structured seed verileri

RAG indeksleri tek basina yeterli degildir. Su komutlar PostgreSQL icindeki
ders, onkosul, kayit donemi, ogrenim ucreti ve demo ogrenci verilerini yukler:

```powershell
python -m scripts.seed_curriculum_data
python -m scripts.seed_synthetic_data
```

Bu adim ozellikle su sorgular icin gereklidir:

- `BIL104 dersinin on kosulu nedir?`
- `1. yariyil dersleri nelerdir?`
- kayit donemi / harc / burs sorgulari

Not:

- `seed_curriculum_data` `courses` ve `course_prerequisites` tablolarini doldurur.
- `seed_synthetic_data` `course_registration_periods`, `tuition_fee_catalog`, `students`, `tuition`, `payments`, `installments`, `scholarships`, `announcements` ve `office_contacts` tablolarini demo verilerle doldurur.
- `seed_synthetic_data` sirasinda `office_contacts tablosu bulunamadi` benzeri bir hata gorurseniz once `python -m alembic upgrade head` calistirin, sonra seed komutunu tekrar deneyin.
- Duyuru ve iletisim kayitlari demo amaclidir; gercek ortama gecerken gercek kaynaklarla degistirilmelidir.

### 6. Departman indeksleme

```powershell
python scripts/index_documents.py --source data/raw/student_affairs --collection student_affairs_docs --reindex
python scripts/index_documents.py --source data/raw/academic_programs --collection academic_programs_docs --reindex
python scripts/index_documents.py --source data/raw/academic_programs/ders_programlari --collection academic_schedules_docs --reindex
python scripts/index_documents.py --source data/raw/finance --collection finance_docs --reindex
```

Not: indeksleyici su anda `pdf`, `txt` ve `docx` dosyalarini okur. `doc` ve `xlsx`
dosyalari loglanir ama indekslenmez.
Ana `academic_programs_docs` indekslemesinde `ders_programlari` alt klasoru otomatik olarak
haric tutulur; schedule belgeleri ayri `academic_schedules_docs` koleksiyonuna gitmelidir.
Yapisal schedule verisi gerekiyorsa `course_schedule_slots` tablosu
ayri ETL ile beslenmelidir. Ilk adim olarak yerel PDF timetable belgeleri icin:

```powershell
python scripts/ingest_schedule_slots.py --source data/raw/academic_programs/ders_programlari --dry-run
python scripts/ingest_schedule_slots.py --source data/raw/academic_programs/ders_programlari
python scripts/ingest_schedule_slots.py --html-url "https://example.edu/schedule.html" --html-source-name "schedule.html" --dry-run
```

Bu ETL muhafazakar davranir; gun ve saat bilgisi net olmayan tablolari atlar.
HTML/tablo kaynakli gelecek akislarda Scrapling ayni tabloyu
beslemek icin ikinci adapter katmani olarak kullanilabilir. Bu yol opsiyoneldir
ve yalnizca `scrapling` paketi kuruluysa kullanilir.
`course_schedule_slots` doldugunda `hangi saatte`, `hangi gun` ve `derslik`
tipindeki daha net schedule sorulari artik bu yapisal veriyle cevaplanabilir.
`academic_schedules_docs` indekslemesinde haftalik program olmayan katalog/mufredat
PDF'leri de otomatik olarak haric tutulur.

Audit icin:

```powershell
python scripts/audit_document_corpus.py
```

### 7. API'yi calistirma

```powershell
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Kontrol icin:

- `GET /`
- `GET /health`
- `GET /docs`

Not:

- `/a2a/dispatch` uygulama ici/internal kullanim icindir; public entegrasyon giris noktasi olarak dusunulmemelidir.
- `/auth/resolve` session token ile kullanilabilir; sadece `slack_user_id` ile cozumleme internal/trusted cagrilar icin uygundur.
- Gelistirme sirasinda otomatik yeniden yukleme isterseniz `--reload` kullanabilirsiniz:

```powershell
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

- Hemen kontrol icin PowerShell ornekleri:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/
Invoke-RestMethod http://127.0.0.1:8000/health
```

Detayli kurulum ve sorun giderme icin [docs/KURULUM_VE_CALISTIRMA.md](docs/KURULUM_VE_CALISTIRMA.md) dosyasini kullanin.

## Testler

Projede testleri amaca gore ayirmak daha sagliklidir; `tests/` klasoru icinde
hem gercek pytest suite'leri hem de benchmark/livetest cikti artefaktlari vardir.
JSON ve Markdown rapor dosyalari pytest tarafindan kosulan testler degildir.

### Unit / normal testler

Mock bagimliliklarla hizli calisan ana test grubu:

```powershell
python -m pytest tests/unit -m "not api and not followup" -v --tb=short
```

Tum unit testleri:

```powershell
python -m pytest tests/unit -v --tb=short
```

### API testleri

FastAPI endpoint'lerini `TestClient` ve mock servislerle dogrular:

```powershell
python -m pytest tests/unit/test_api.py -v --tb=short
python -m pytest -m api -v --tb=short
```

Bu testler `uvicorn` gerektirmez.

### Follow-up / conversation testleri

Konusma baglami, follow-up cozumleme ve memory davranisini hedefler:

```powershell
python -m pytest tests/unit/test_conversation_context.py -v --tb=short
python -m pytest -m followup -v --tb=short
```

Bu grup ozellikle su davranislari korur:

- kisa ama bagimsiz sorgularin follow-up'a zorlanmamasi
- konu degisince stale context'in yeni soruya yapismamasi
- canonical memory cevabinin presentation eklerinden arinmis kalmasi

### Orchestrator ve ajan testleri

```powershell
python -m pytest tests/unit/test_orchestrators.py -v --tb=short
python -m pytest tests/unit/test_all_agents.py -v --tb=short
python -m pytest tests/unit/test_system_e2e.py -v --tb=short
```

Bunlar da normalde `uvicorn` istemez; mock bagimliliklarla kosarlar.

### Integration / model testleri

Bu grup ChromaDB, indekslenmis koleksiyonlar ve bazi senaryolarda gercek model cache'i ister:

```powershell
python -m pytest tests/integration -v --tb=short
python -m pytest tests/integration -m smoke -v --tb=short
python -m pytest tests/integration -m model -v --tb=short
python -m pytest tests/integration -m slow -v --tb=short
```

Bu grup sunucu acik olmadan kosabilir ama lokal servisler ve indekslenmis veri ister.

### Sik kullanilan tekil test komutlari

```powershell
python -m pytest tests/unit/test_conversation_context.py -v --tb=short
python -m pytest tests/unit/test_api.py -v --tb=short
python -m pytest tests/unit/test_orchestrators.py -v --tb=short
python -m pytest tests/unit/test_router.py -v --tb=short
python -m pytest tests/unit/test_retriever.py -v --tb=short
python -m pytest tests/unit/test_reranker.py -v --tb=short
```

### Benchmark ve demo scriptleri

Bunlar pytest degildir; `tests/` altinda sonuc JSON'lari uretir:

```powershell
python scripts/live_question_test.py --benchmark demo_showcase_stable_turk
python scripts/run_quality_benchmark.py
```

API uzerinden benchmark denemek isterseniz:

```powershell
python scripts/live_question_test.py --benchmark demo_showcase_stable_turk --use-api
```

Sunucu calistirma, manuel endpoint denemeleri ve daha ayrintili test siniflandirmasi icin
[docs/KURULUM_VE_CALISTIRMA.md](docs/KURULUM_VE_CALISTIRMA.md) dosyasindaki
`Sunucuyu Calistirma ve Kontrol Etme` ve `Test ve Benchmark Komutlari` bolumlerine bakin.

### Capability agent rollout

Announcement ve event artik department disi capability agent olarak da ayaga kalkabilir:

```powershell
python -m scripts.a2a_rollout --include-announcement --include-event
python -m scripts.a2a_rollout --include-student --include-academic --include-announcement --include-event
```

Bu servisler ayni `agent_service` entrypoint'i ve ayni shared Docker image ile calisir; farklari `AGENT_DEPARTMENT=announcement|event` ile capability hedefi secmeleridir.

### Specialist agent rollout

Departman orkestratorleri icindeki uzmanlar da ayri A2A servisleri olarak
calistirilabilir. Tek tek acmak icin departman bazli bayraklari, tum mevcut
uzman servisleri birlikte acmak icin `--include-all-specialists` kullanin:

```powershell
python -m scripts.a2a_rollout --include-finance-specialists
python -m scripts.a2a_rollout --include-student-specialists
python -m scripts.a2a_rollout --include-academic-specialists
python -m scripts.a2a_rollout --include-announcement --include-event --include-all-specialists
```

Bu mod ilgili departman orkestratorune `A2A_SPECIALIST_MODE=http` verir ve
secili uzman servisleri ayni `agent_service` entrypoint'iyle ayaga kaldirir:
finance icin `tuition_agent` / `scholarship_agent`, student affairs icin
`registration_agent` / `graduation_agent` / `internship_agent` /
`student_life_agent`, academic programs icin `curriculum_agent` /
`regulation_agent` / `international_agent`. Varsayilan transport internal
`/a2a/dispatch`, `--transport-protocol jsonrpc` secilirse JSON-RPC `/a2a`
`message/send` yoludur. Specialist RAG/LLM cagri sureleri departman
transport'undan daha uzun olabildigi icin overlay `A2A_SPECIALIST_TIMEOUT_SECONDS`
varsayilanini 60 saniye tutar.

## Proje Yapisi

```text
university_support_system/
|-- src/
|   |-- api/               # FastAPI girisi ve query/auth/profile helper akislari
|   |-- agents/            # Akademik, finans, ogrenci isleri, duyuru ve etkinlik ajanlari
|   |-- orchestrators/     # Ana orchestrator ve moduler dispatch/synthesis yardimcilari
|   |-- routing/           # DepartmentRouter ve routing policy
|   |-- rag/               # Loader, chunker, retriever, reranker, index pipeline
|   |-- llm/               # Ollama/OpenAI istemcileri ve LLM service
|   |-- db/                # ORM modelleri, auth, profile, conversation ve telemetry
|   |-- notifications/     # OTP e-posta gonderim yardimcilari
|   |-- slack/             # Slack tarafindaki entegrasyon temeli
|   |-- a2a/, cache/, queue/, security/, mcp/
|   `-- core/              # Konfigrasyon, sabitler ve ortak yardimcilar
|-- scripts/               # Index, benchmark, evaluate ve test CLI scriptleri
|-- tests/                 # Unit ve integration testleri
|-- docs/                  # Guncel ve tarihsel dokumantasyon
|-- data/                  # Raw dokumanlar ve metadata
|-- docker-compose.yml
|-- alembic.ini
|-- pyproject.toml
`-- requirements*.txt
```

## Dokumantasyon

| Dokuman | Amac |
|---|---|
| [docs/DOKUMANTASYON_OKUMA_SIRASI.md](docs/DOKUMANTASYON_OKUMA_SIRASI.md) | Hangi belgenin guncel, hangisinin tarihsel oldugunu gosteren giris noktasi |
| [docs/A2A_DAGITIK_MIMARI_VE_CALISMA_OZETI.md](docs/A2A_DAGITIK_MIMARI_VE_CALISMA_OZETI.md) | Dagitik A2A, merkezi retrieval servisi, Slack A2A modu ve son routing/RAG iyilestirmelerinin kapsamli ozeti |
| [docs/KURULUM_VE_CALISTIRMA.md](docs/KURULUM_VE_CALISTIRMA.md) | Guncel lokal kurulum, indeksleme, test ve sorun giderme rehberi |
| [docs/SLACK_ENTEGRASYON.md](docs/SLACK_ENTEGRASYON.md) | Slack `inprocess` / `a2a` runtime, Socket Mode ve sorun giderme notlari |
| [docs/demo_runbook.md](docs/demo_runbook.md) | Demo ve benchmark senaryolarini calistirma notlari |
| [docs/AZURE_VM_RUNBOOK.md](docs/AZURE_VM_RUNBOOK.md) | Azure VM uzerinde kurulum ve operasyon notlari |
| [docs/technical_backlog.md](docs/technical_backlog.md) | Halen acik teknik iyilestirme listesi |
| [docs/DOKUMAN_ENVANTERI_VE_ARSIV_ADAYLARI.md](docs/DOKUMAN_ENVANTERI_VE_ARSIV_ADAYLARI.md) | Hangi dokumanlarin aktif, tarihsel veya arsiv adayi oldugunu gosteren temizlik notu |
| [docs/PROJE_ANATOMISI_KILAVUZU.md](docs/PROJE_ANATOMISI_KILAVUZU.md) | Kompakt modul sorumluluk haritasi; ayrintili A2A/retrieval durumu icin yeni mimari ozetiyle birlikte okunmali |
| [docs/MART_2026_GUNCELLEME_NOTLARI.md](docs/MART_2026_GUNCELLEME_NOTLARI.md) | Mart 2026 donemindeki mimari degisim ozeti |
| `docs/FAZ_0_*`, `docs/FAZ_1_*`, `docs/FAZ_2_*`, `docs/FAZ_3_*` | Tarihsel faz kayitlari; guncel operasyon dokumani olarak degil, referans arka plan olarak okunmalidir |

## Lisans

Bu proje bir bitirme projesidir.
