# Kurulum ve Calistirma Rehberi

Bu belge, projenin guncel kod tabani icin pratik kurulum rehberidir. Tarihsel faz dokumanlarindaki bazi anlatilar proje gecmisi acisindan degerlidir, ancak guncel calistirma akisi icin bu dosya, `README.md` ve `AZURE_VM_RUNBOOK.md` once referans alinmalidir.

## 0. Guncel Kisa Akis

Gelistirme makinesinde bugunku onerilen akisi hizlica toparlamak gerekirse:

```powershell
cd "<repo>\university_support_system"
.\venv\Scripts\activate

docker compose up -d postgres redis chromadb

.\venv\Scripts\python.exe -m alembic upgrade head
.\venv\Scripts\python.exe -m scripts.seed_curriculum_data
.\venv\Scripts\python.exe -m scripts.seed_synthetic_data

.\venv\Scripts\python.exe -m scripts.audit_academic_source_coverage --fail-on-missing
```

Full dagitik A2A + GPU targeted runtime icin:

```powershell
.\venv\Scripts\python.exe -m scripts.a2a_rollout --gpu --gpu-scope targeted --transport-protocol jsonrpc --include-announcement --include-event --include-all-specialists --health-timeout-seconds 300
```

Kod degismediyse, sadece servisleri mevcut image ile yeniden kaldirmak icin:

```powershell
.\venv\Scripts\python.exe -m scripts.a2a_rollout --gpu --gpu-scope targeted --skip-build --transport-protocol jsonrpc --include-announcement --include-event --include-all-specialists --health-timeout-seconds 300
```

25 soruluk kalite benchmark'i:

```powershell
.\venv\Scripts\python.exe -m scripts.run_quality_benchmark --use-api --api-base-url http://127.0.0.1:8000 --llm-profile balanced --warmup-mode full --warmup-timeout 90
```

Slack icin tek runtime acik tutulmalidir. A2A Slack:

```powershell
.\venv\Scripts\python.exe -m scripts.slack_runtime up --runtime a2a
.\venv\Scripts\python.exe -m scripts.slack_runtime logs --runtime a2a
```

Monolitik Slack:

```powershell
.\venv\Scripts\python.exe -m scripts.slack_runtime up --runtime inprocess
.\venv\Scripts\python.exe -m scripts.slack_runtime logs --runtime inprocess
```

Slack runtime kapatma:

```powershell
.\venv\Scripts\python.exe -m scripts.slack_runtime stop --runtime a2a
.\venv\Scripts\python.exe -m scripts.slack_runtime stop --runtime inprocess
```

Notlar:

- Docker Desktop sorunluysa once Docker'i kapatip acin; `dockerDesktopLinuxEngine` pipe hatasi uygulama hatasi degil Docker daemon erisim hatasidir.
- Kod, dependency veya data dosyasi degistiyse `--skip-build` kullanmayin; normal build'li rollout gerekir.
- RAG belge icerigi degistiyse ilgili koleksiyon yeniden indekslenmelidir. Structured DB seed veya schedule ingest degistiyse yeniden indeks gerekmez, ilgili seed/ingest komutu yeterlidir.
- Slack'te iki cevap gelirse genellikle iki Socket Mode bot ayni token ile aciktir. `slack-bot-a2a` ve `slack-bot-inprocess` ayni anda calismamali.
- `LLM_QUERY_NORMALIZATION_ENABLED` varsayilan olarak `true` gelir. Kisa capability ifadeleri (`guncel duyur` gibi) routing oncesi kanoniklestirilir; normal sorgularda canonical query routing LLM'in ayni JSON ciktisindan alinir. Gerekirse `.env` icinde `LLM_QUERY_NORMALIZATION_ENABLED=false` ile kapatilabilir.

## 1. On Kosullar

Projeyi lokal ya da VM uzerinde calistirmak icin asagidaki araclar yeterlidir:

| Yazilim | Onerilen surum | Not |
|---|---|---|
| Python | 3.11+ | Ana uygulama |
| Docker | 24+ | PostgreSQL, Redis, ChromaDB, Ollama |
| Docker Compose | 2.20+ | `docker compose` komutu |
| Git | 2.40+ | Repo erisimi |

Kaynak notlari:

- Embedding ve reranker modelleri ilk calistirmada Hugging Face uzerinden iner.
- Ollama modelleri ilk acilista ya da ilk cagrida indirilir.
- CPU dostu kurulum yapacaksaniz daha kucuk Ollama modeli ve `cpu` cihaz secimi kullanabilirsiniz.

## 2. Kodu Elde Etme

Repo erisiminiz varsa:

```powershell
git clone <repo-url>
cd university_support_system\university_support_system
```

Repo private ise ve uzak makinede `git clone` kullanamiyorsaniz iki yol vardir:

1. GitHub auth ile klonlama
2. Lokalde zip alip hedef makineye `scp` ile gonderme

Azure VM uzerindeki ozel akisin adimlari icin [AZURE_VM_RUNBOOK.md](AZURE_VM_RUNBOOK.md) dosyasini kullanin.

## 3. Python Ortami

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Sadece runtime kurmak isterseniz `requirements.txt` kullanabilirsiniz; gelistirme ve test icin `requirements-dev.txt` daha uygundur.

## 4. Docker Servislerini Baslatma

```powershell
docker compose up -d
docker compose ps
```

Beklenen servisler:

- `uni_postgres`
- `uni_redis`
- `uni_chromadb`
- `uni_ollama`

Durum kontrolu icin:

```powershell
docker compose ps
docker compose logs --tail=50 ollama
```

Servisleri durdurmak icin:

```powershell
docker compose down
```

Volume'lari da silmek isterseniz:

```powershell
docker compose down -v
```

## 5. Ortam Degiskenleri

### 5.1 Temel kurulum

```powershell
copy .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

### 5.2 Temiz makinede model indirme ayari

`.env.example` dosyasinda embedding ve reranker varsayilan olarak lokal cache odakli davranir. Yeni bir makinede modelleri online indirmek icin su iki satirin `.env` icinde `false` oldugundan emin olun:

```text
EMBEDDING_LOCAL_FILES_ONLY=false
RERANKER_LOCAL_FILES_ONLY=false
```

Bu iki ayar yoksa ya da `true` ise, indeksleme sirasinda Hugging Face baglantisi yerine "local cache'te bulunamadi" hatasi alirsiniz.

### 5.3 Dusuk kaynakli / CPU dostu profil

Ozellikle Azure CPU VM gibi ortamlarda asagidaki profil daha guvenlidir:

```text
OLLAMA_MODEL=qwen2.5:1.5b
OLLAMA_SECONDARY_MODEL=qwen2.5:1.5b
OLLAMA_PRELOAD_MODELS=qwen2.5:1.5b
LLM_PROFILE=fast
LLM_ROUTING_MODEL=qwen2.5:1.5b
LLM_CONVERSATION_MODEL=qwen2.5:1.5b
EMBEDDING_DEVICE=cpu
RERANKER_DEVICE=cpu
RERANKER_BATCH_SIZE=4
SERVER_DEBUG=false
CONVERSATION_REWRITE_WITH_LLM=false
```

Varsayilan lokal profil ise daha buyuk Ollama modelleri ve `balanced` profil kullanir.

### 5.4 Groq / OpenAI-compatible profil

GPU bulmak zorlasirsa sadece LLM katmanini API provider'a tasiyabilirsiniz. Mevcut kod tabani `OpenAI-compatible` profil ile Groq benzeri servisleri kullanabilecek sekilde ayarlanabilir.

Ornek `.env` degerleri:

```text
LLM_PRIMARY_PROVIDER=openai_compatible
LLM_FALLBACK_PROVIDER=ollama
OPENAI_API_KEY=<API_KEY>
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-8b-instant
OPENAI_PROVIDER_NAME=groq
LLM_ROUTING_MODEL=llama-3.1-8b-instant
LLM_CONVERSATION_MODEL=llama-3.1-8b-instant
```

Notlar:

- Bu profilde FastAPI, PostgreSQL, Redis ve Chroma lokal/CPU tarafta kalir; yalnizca LLM cagrilari API provider'a gider.
- Eger API provider role bazli ayri model kullanmayacaksa `LLM_ROUTING_MODEL` ve `LLM_CONVERSATION_MODEL` alanlarini ayni modelle birakabilirsiniz.
- Groq, OpenAI-compatible endpoint kullandigi icin ayri bir SDK zorunlu degildir; mevcut istemci `OPENAI_BASE_URL` uzerinden calisabilir.

## 6. Veritabani Migration

Docker servisleri ayaktayken:

```powershell
.\venv\Scripts\python.exe -m alembic upgrade head
.\venv\Scripts\python.exe -m alembic current
```

Beklenen son durum:

```text
<revision-id> (head)
```

## 7. Structured Seed Verileri

RAG koleksiyonlarini indekslemek tek basina yeterli degildir. Uygulamanin bir
kismi dogrudan PostgreSQL tablolarindan okur. Bu nedenle migration sonrasinda
asagidaki seed komutlari da calistirilmalidir:

```powershell
.\venv\Scripts\python.exe -m scripts.seed_curriculum_data
.\venv\Scripts\python.exe -m scripts.seed_synthetic_data
```

Bu komutlar su veri alanlarini doldurur:

- `seed_curriculum_data`: `courses`, `course_prerequisites`
- `seed_synthetic_data`: `course_registration_periods`, `tuition_fee_catalog`, `students`, `student_courses`, `tuition`, `payments`, `installments`, `scholarships`, `announcements`, `office_contacts`

Bu adim olmadan su tip cevaplar bos donebilir:

- ders onkosullari
- yariyil ders listeleri
- kayit donemi bilgileri
- harc ve burs akislari

Not:

- `seed_synthetic_data` icindeki duyuru ve iletisim kayitlari demo fixture niteligindedir.
- `office_contacts tablosu bulunamadi` benzeri bir hata alirsaniz migration adimini tekrar calistirin: `python -m alembic upgrade head`.
- Gercek ortama geciste bu alanlarin kurumsal kaynaklardan doldurulmasi gerekir.
- `tuition_fee_catalog` gibi structured kataloglar guncellendiyse sadece kodu rebuild etmek yetmez; `seed_synthetic_data` tekrar calistirilmelidir.
- Ders/mufredat JSON seedleri degistiyse `seed_curriculum_data` veya ilgili `seed_curriculum_from_json` komutu tekrar calistirilmelidir.

## 8. Dokuman Indeksleme

Her departman kendi koleksiyonuna indekslenmelidir. Guncel koleksiyonlar:

- `student_affairs_docs`
- `academic_programs_docs`
- `finance_docs`

Komutlar:

```powershell
.\venv\Scripts\python.exe scripts/index_documents.py --source data/raw/student_affairs --collection student_affairs_docs --reindex
.\venv\Scripts\python.exe scripts/index_documents.py --source data/raw/academic_programs --collection academic_programs_docs --reindex
.\venv\Scripts\python.exe scripts/index_documents.py --source data/raw/academic_programs/ders_programlari --collection academic_schedules_docs --reindex
.\venv\Scripts\python.exe scripts/index_documents.py --source data/raw/finance --collection finance_docs --reindex
```

Belge korpusunu indekslemeden once hizlica denetlemek isterseniz:

```powershell
.\venv\Scripts\python.exe scripts/audit_document_corpus.py
```

Indeksleme sirasinda beklenenler:

- belge yukleme
- metin temizleme
- chunk olusturma
- embedding uretimi
- ChromaDB'ye yazma

Notlar:

- Bozuk PDF'ler artik tum pipeline'i dusurmek yerine loglanip atlanabilir.
- Loader su an `pdf`, `txt` ve `docx` dosyalarini indeksler; eski `doc` ve `xlsx` dosyalari ise loglanir ama indekslenmez.
- `academic_programs_docs` indekslemesi ana mevzuat/mufredat havuzu icindir; `ders_programlari` alt klasoru burada otomatik olarak haric tutulur ve ayri `academic_schedules_docs` koleksiyonuna indekslenmelidir.
- Yapisal schedule verileri icin ayrica `course_schedule_slots` ETL komutu vardir:

```powershell
.\venv\Scripts\python.exe -m scripts.ingest_schedule_slots --source data/raw/academic_programs/ders_programlari --dry-run
.\venv\Scripts\python.exe -m scripts.ingest_schedule_slots --source data/raw/academic_programs/ders_programlari
.\venv\Scripts\python.exe -m scripts.ingest_schedule_slots --html-url "https://example.edu/schedule.html" --html-source-name "schedule.html" --dry-run
```

- Bu ETL yerel PDF ders programlarini `pdfplumber` ile, XLSX programlarini ise OOXML hucre yapisindan okur ve yalnizca gun+saat baglami net satirlari tabloya yazar.
- HTML/tablo kaynakli gelecekteki akislarda Scrapling ayni `course_schedule_slots` tablosunu besleyen ikinci adapter olarak kullanilabilir; mevcut yerel PDF korpusu icin birincil parser degildir.
- `--html-url` yolu opsiyoneldir ve yalnizca `scrapling` paketi kuruluysa kullanilabilir.
- `course_schedule_slots` doluysa sistem `hangi saatte`, `hangi gun`, `derslik` gibi daha net schedule sorularinda bu yapisal tablodan once faydalanabilir.
- `academic_schedules_docs` koleksiyonu indekslenirken haftalik program olmayan katalog/mufredat PDF'leri otomatik olarak haric tutulur; boylece schedule retrieval havuzu daha temiz kalir.
- Announcement kaynaklariyla curriculum/schedule kapsami uyumunu kontrol etmek icin:

```powershell
.\venv\Scripts\python.exe -m scripts.audit_academic_source_coverage --fail-on-missing
```

- Ilk embedding uretiminde `BAAI/bge-m3` indirilecegi icin sure uzayabilir.
- Ilk reranker kullanimi sirasinda `nreimers/mmarco-mMiniLMv2-L6-H384-v1` da indirilebilir.

## 9. Sunucuyu Calistirma ve Kontrol Etme

Bu bolum API'yi lokal gelistirme icin ayaga kaldirmaya ve ilk temel kontrolleri
tek tek dogrulamaya odaklanir.

### 9.1 Calistirmadan once hizli kontrol listesi

Sunucuyu baslatmadan once su adimlarin tamam oldugundan emin olun:

1. `.venv` aktif
2. `docker compose up -d` ile PostgreSQL, Redis, ChromaDB ve Ollama ayakta
3. `python -m alembic upgrade head` calismis
4. Gerekiyorsa seed komutlari tamamlanmis
5. Gerekli dokuman koleksiyonlari indekslenmis

Eksik bir adim varsa API acilsa bile:

- OTP/auth akislari
- structured DB tabanli cevaplar
- RAG retrieval
- benchmark scriptleri

beklenen sekilde calismayabilir.

### 9.2 Uvicorn ile baslatma

Temel komut:

```powershell
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Gelistirme sirasinda kod degisikliginde otomatik yeniden yukleme istiyorsaniz:

```powershell
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Notlar:

- `--reload` gelistirme icindir; benchmark ve daha stabil denemelerde kapali tutmak daha sagliklidir.
- Lokal makinede sadece kendiniz kullanacaksaniz `127.0.0.1` daha guvenlidir.
- Ayni anda baska bir servis `8000` portunu kullaniyorsa farkli bir port secin.

### 9.3 API ayaga kalkinca ilk kontrol komutlari

Kontrol endpoint'leri:

- `GET /`
- `GET /health`
- `GET /docs`

PowerShell ornekleri:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/
Invoke-RestMethod http://127.0.0.1:8000/health
Start-Process http://127.0.0.1:8000/docs
```

Beklenen ana yuzeyler:

- `/query`
- `/auth/request-otp`
- `/auth/verify-otp`
- `/auth/resolve`
- `/auth/logout`
- internal `/a2a/dispatch`

### 9.4 Health endpoint'te neye bakilmali

`/health` icinde pratikte en cok kontrol edilen alanlar:

- uygulama durumunun `healthy` donmesi
- primary LLM provider bilgisinin gelmesi
- modelin gercekten yuklu/mevcut gorunmesi
- `a2a_mode` ve `auth_mode` alanlarinin beklenen degerleri gostermesi

Eger API ayakta ama model bulunamiyorsa, saglik cagrisi artik bunu genel
`healthy` gibi gostermek yerine `model_missing` seviyesinde ayirt etmeye
calisir.

### 9.5 Query endpoint'i hizli deneme

Basit bir sorgu:

```powershell
$body = @{
  query = "CAP basvurusu nasil yapilir?"
  context_id = "manual-check-1"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/query `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

OTP ile dogrulanmis oturumla sorgu:

```powershell
$body = @{
  query = "Not ortalamam kac?"
  context_id = "manual-check-2"
  session_token = "<OTP_VERIFY_SONRASI_DONEN_TOKEN>"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/query `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

### 9.6 Auth endpoint'lerini manuel deneme

OTP isteme:

```powershell
$requestOtp = @{
  student_number = "20210001"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/auth/request-otp `
  -Method Post `
  -ContentType "application/json" `
  -Body $requestOtp
```

OTP dogrulama:

```powershell
$verifyOtp = @{
  student_number = "20210001"
  otp_code = "123456"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/auth/verify-otp `
  -Method Post `
  -ContentType "application/json" `
  -Body $verifyOtp
```

Notlar:

- `request-otp` endpoint'i enumeration riskini azaltmak icin genel mesaj doner; yanit “ogrenci bulundu/bulunmadi” diye acik ayrim yapmayabilir.
- `auth/resolve` session token ile kullanilabilir; sadece `slack_user_id` ile baglam cozumleme internal/trusted kullanim icin tasarlanmistir.
- `/a2a/dispatch` internal entegrasyon yuzeyidir; paylasilan `X-Internal-API-Key` olmadan kullanilamaz.

### 9.7 Sunucuyu hangi durumlarda acmaya gerek yok

Asagidaki testler/senaryolar icin `uvicorn` acmaniz gerekmez:

- `tests/unit/*`
- `tests/unit/test_api.py` cunku `TestClient` kullanir
- `tests/unit/test_conversation_context.py`
- `tests/unit/test_orchestrators.py`

Asagidaki senaryolarda ise sunucu acik olmak faydali veya gerekli olabilir:

- `/docs` uzerinden manuel endpoint denemeleri
- `scripts/live_question_test.py --use-api ...`
- dis istemci veya Postman ile gercek HTTP akisi denemeleri

## 10. Test ve Benchmark Komutlari

`tests/` klasoru iki farkli tur icerik barindirir:

- pytest ile kosulan gercek test dosyalari
- benchmark ve live test scriptlerinin urettigi JSON artefaktlari

Yeni benchmark JSON ciktilari varsayilan olarak `tests/archive/benchmarks/` altina yazilir. Markdown raporlar ise `docs/archive/benchmarks/` altindadir. Bu dosyalar pytest suite'i degildir; rapor/cikti artefaktidir.

### 10.1 Unit / normal testler

Hizli ve mock bagimlilikli temel testler:

```powershell
python -m pytest tests/unit -m "not api and not followup" -v --tb=short
```

Isterseniz tum unit testleri tek seferde de kosabilirsiniz:

```powershell
python -m pytest tests/unit -v --tb=short
```

Bu grup tipik olarak sunucu acik olmadan kosulur.

### 10.2 API testleri

Bu grup FastAPI endpoint'lerini `TestClient` ve mock servislerle test eder.
Gercek ChromaDB, Ollama veya production DB beklemez.

```powershell
python -m pytest tests/unit/test_api.py -v --tb=short
python -m pytest -m api -v --tb=short
```

Bu testler `uvicorn` isteyen entegrasyon testleri degildir; uygulamayi test
prosesinin icinde ayaga kaldirirlar.

### 10.3 Follow-up / conversation testleri

Konusma baglami, follow-up cozumleme, LLM rewrite fallback'i ve memory davranisi:

```powershell
python -m pytest tests/unit/test_conversation_context.py -v --tb=short
python -m pytest -m followup -v --tb=short
```

Bu grup ozellikle su davranislari korumak icin onemlidir:

- kisa ama bagimsiz sorgularin follow-up diye zorlanmamasi
- konu degisirse stale context'in yeni soruyu ele gecirmemesi
- canonical memory cevabinin presentation eklerinden arinmis kalmasi

### 10.4 Orchestrator ve ajan testleri

Departman orkestrasyonu, ajan secimi ve mock tabanli uctan uca akislar:

```powershell
python -m pytest tests/unit/test_orchestrators.py -v --tb=short
python -m pytest tests/unit/test_all_agents.py -v --tb=short
python -m pytest tests/unit/test_system_e2e.py -v --tb=short
```

Bu komutlar da normalde `uvicorn` gerektirmez.

### 10.5 Integration / model testleri

Bu testler indekslenmis koleksiyon, ChromaDB ve bazi durumlarda gercek model
cache'i ister; unit testlere gore daha agir ve ortama duyarli calisir.

```powershell
python -m pytest tests/integration -v --tb=short
python -m pytest tests/integration -m smoke -v --tb=short
python -m pytest tests/integration -m model -v --tb=short
python -m pytest tests/integration -m slow -v --tb=short
```

Pratik gereksinimler:

- `docker compose up -d`
- ilgili koleksiyonlarin indekslenmis olmasi
- model cache'lerinin ortamla uyumlu olmasi

Bu grup, unit testlerden farkli olarak lokal servis durumundan etkilenir.

### 10.6 Sik kullanilan tekil test komutlari

Belirli alanlara hizli odaklanmak icin:

```powershell
python -m pytest tests/unit/test_conversation_context.py -v --tb=short
python -m pytest tests/unit/test_api.py -v --tb=short
python -m pytest tests/unit/test_orchestrators.py -v --tb=short
python -m pytest tests/unit/test_router.py -v --tb=short
python -m pytest tests/unit/test_retriever.py -v --tb=short
python -m pytest tests/unit/test_reranker.py -v --tb=short
```

### 10.7 Yararli CLI scriptleri

Pytest disi kontrol ve benchmark komutlari:

```powershell
.\venv\Scripts\python.exe scripts/hybrid_search_probe.py "Cap basvurusu icin gereken not ortalamasi kactir"
.\venv\Scripts\python.exe scripts/query_db.py "BIL104 dersinin on kosulu nedir"
.\venv\Scripts\python.exe scripts/evaluate_rag.py
.\venv\Scripts\python.exe scripts/followup_benchmark.py
.\venv\Scripts\python.exe scripts/analyze_reranker_scores.py
.\venv\Scripts\python.exe scripts/live_question_test.py --benchmark demo_showcase_stable_turk
.\venv\Scripts\python.exe -m scripts.run_quality_benchmark
```

API uzerinden guncel kalite benchmark'i icin onerilen komut:

```powershell
.\venv\Scripts\python.exe -m scripts.run_quality_benchmark --use-api --api-base-url http://127.0.0.1:8000 --llm-profile balanced --warmup-mode full --warmup-timeout 90
```

Sadece belirli sorulari kosmak icin:

```powershell
.\venv\Scripts\python.exe -m scripts.run_quality_benchmark --use-api --api-base-url http://127.0.0.1:8000 --question Q1 Q7 Q17 Q23 Q25 --llm-profile balanced --warmup-mode full --warmup-timeout 90
```

A2A stack runtime smoke:

```powershell
.\venv\Scripts\python.exe -m scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15 --timeout 120
```

Notlar:

- `scripts/live_question_test.py` hem orchestrator icinden hem de `--use-api` ile HTTP uzerinden kullanilabilir.
- `scripts/run_quality_benchmark.py` ve `scripts/live_question_test.py` pytest degildir; sonuc dosyalarini `tests/` altina yazabilir.
- API benchmark modunda `/health` preflight vardir; API kapaliysa hatali full-error raporu uretmeden durmasi beklenir.
- `--warmup-mode full` API modunda gercek `/query` yolunu isitir. Bu warmup, dagitik A2A agent servislerinin model/retrieval cold-start maliyetini olcumden once azaltmak icindir.
- `scripts/gpu_diagnostics.py` ve benzeri scriptler daha cok ortam/hardware dogrulama yardimcisidir.

Benchmark setlerinin detayli aciklamasi icin [demo_runbook.md](demo_runbook.md) dosyasina bakin.

## 11. Sik Karsilasilan Sorunlar

### 11.1 Ollama modeli bulunamiyor

Belirti:

- `ollama model not found`
- health endpoint model yuklu degil diyor

Cozum:

```powershell
docker compose logs --tail=50 ollama
docker exec uni_ollama ollama list
```

Gerekirse `.env` icindeki `OLLAMA_PRELOAD_MODELS` ve `OLLAMA_MODEL` degerlerini kontrol edin.

### 11.2 Hugging Face offline / local cache hatasi

Belirti:

- `outgoing traffic has been disabled`
- `local_files_only` hatasi

Cozum:

`.env` icinde asagidaki iki ayari `false` yapin:

```text
EMBEDDING_LOCAL_FILES_ONLY=false
RERANKER_LOCAL_FILES_ONLY=false
```

### 11.3 Zip ile tasinan `data/raw` klasorlerinde izin hatasi

Belirti:

- `Permission denied`
- indeksleme `data/raw/...` altina giremiyor

Cozum:

```bash
sudo chown -R azureuser:azureuser ~/app/data
chmod -R u+rwX,go-rwx ~/app/data
```

Kullanici adini kendi VM kullaniciniza gore uyarlayin.

### 11.4 API calisiyor ama portu disaridan acmak istemiyorsunuz

Guvenli test icin SSH tunnel kullanin. Azure tarafindaki ayrintili ornekler [AZURE_VM_RUNBOOK.md](AZURE_VM_RUNBOOK.md) icindedir.

### 11.5 VM yeniden acildi ama API dusmus

`uvicorn` komutunu `tmux` veya `systemd` ile tekrar baslatin. Hedef makinede otomatik kapanma kullaniyorsaniz bu operasyon adimlarini ayri runbook ile saklamaniz onerilir.

## 12. Yararli Referanslar

- [README.md](../README.md)
- [DOKUMANTASYON_OKUMA_SIRASI.md](DOKUMANTASYON_OKUMA_SIRASI.md)
- [PROJE_ANATOMISI_KILAVUZU.md](PROJE_ANATOMISI_KILAVUZU.md)
- [demo_runbook.md](demo_runbook.md)
- [AZURE_VM_RUNBOOK.md](AZURE_VM_RUNBOOK.md)
- [technical_backlog.md](technical_backlog.md)
