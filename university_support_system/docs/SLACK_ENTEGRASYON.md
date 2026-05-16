# Slack Entegrasyonu

Bu entegrasyon Slack'i yeni bir giris kanali olarak ekler. Mevcut API, agent ve A2A olmayan orkestrator akisi korunur.

## Mimari

Slack iki runtime ile calisabilir:

- `inprocess`: Slack bot lokal monolitik `MainOrchestrator` kullanir.
- `a2a`: Slack bot lokal/Docker A2A endpointlerine baglanir ve dagitik agent topolojisini kullanir.

Akis:

`Slack -> src.slack.app -> SlackBotService -> runtime adapter -> MainOrchestrator/A2A API -> Slack cevabi`

Slack adapter Socket Mode ile calisir. Bu yerel gelistirme icin public HTTPS veya ngrok gerektirmez.

Guncel A2A modunda Slack bot dogrudan agent mantigini yuklemez; `api` uzerinden departman agent'lari, uzman agent'lar, `agent-announcement`, `agent-event` ve merkezi `retrieval-service` ile konusur. Bu nedenle dagitik davranisi Slack'te gostermek icin once A2A stack'in saglikli sekilde ayaga kalkmis olmasi gerekir.

## Ortam Degiskenleri

`.env` icinde su alanlar gerekir:

```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
SLACK_APP_TOKEN=xapp-...
```

Socket Mode icin `SLACK_APP_TOKEN` gerekir. HTTP Events API'ye gecilirse `SLACK_APP_TOKEN` zorunlu olmaz, fakat public HTTPS endpoint gerekir.

## Slack App Ayarlari

Slack app tarafinda:

- Socket Mode aktif olmali.
- Bot token scope'lari: `app_mentions:read`, `chat:write`, `im:history`, `im:read`, `im:write`.
- Event Subscriptions: `app_mention`, `message.im`.

## Lokal Calistirma

```powershell
# Monolitik lokal runtime
.\venv\Scripts\python.exe -m scripts.run_slack_bot --runtime inprocess

# Lokal A2A endpointlerine baglanan runtime
.\venv\Scripts\python.exe -m scripts.run_slack_bot --runtime a2a --a2a-endpoint-profile local --transport-protocol jsonrpc
```

## Docker Calistirma

Full A2A stack ayaktayken A2A Slack botu:

```powershell
.\venv\Scripts\python.exe -m scripts.slack_runtime up --runtime a2a
.\venv\Scripts\python.exe -m scripts.slack_runtime logs --runtime a2a
.\venv\Scripts\python.exe -m scripts.slack_runtime stop --runtime a2a
```

Monolitik Slack botu:

```powershell
.\venv\Scripts\python.exe -m scripts.slack_runtime up --runtime inprocess
.\venv\Scripts\python.exe -m scripts.slack_runtime logs --runtime inprocess
.\venv\Scripts\python.exe -m scripts.slack_runtime stop --runtime inprocess
```

Tek Slack app token setiyle ayni anda iki Socket Mode bot acmayin. Iki ayri versiyonu ayni anda denemek isterseniz ikinci Slack app olusturup A2A bot icin `SLACK_A2A_BOT_TOKEN`, `SLACK_A2A_SIGNING_SECRET`, `SLACK_A2A_APP_TOKEN` kullanin.

Full A2A stack icin onerilen baslatma komutu:

```powershell
.\venv\Scripts\python.exe -m scripts.a2a_rollout --gpu --gpu-scope targeted --transport-protocol jsonrpc --include-announcement --include-event --include-all-specialists --health-timeout-seconds 300
```

Kod degismediyse ayni komut `--skip-build` ile kullanilabilir; kod veya dependency degistiyse `--skip-build` kullanilmamalidir.

Slack kalite replay oncesi pratik sira:

```powershell
.\venv\Scripts\python.exe -m scripts.a2a_rollout --gpu --gpu-scope targeted --skip-build --transport-protocol jsonrpc --include-announcement --include-event --include-all-specialists --slack-service slack-bot-a2a --health-timeout-seconds 300
docker exec uni_redis redis-cli -n 0 FLUSHDB
.\venv\Scripts\python.exe -m scripts.slack_runtime restart --runtime a2a
```

Rollout `dependency failed to start: container uni_a2a_retrieval_service is unhealthy` ile biterse hemen karar vermeyin; GPU warmup bazen Compose health penceresine yetismeyebilir. Asagidaki komutlarla retrieval gercekten hata mi verdi yoksa sonradan `healthy` mi oldu kontrol edilir:

```powershell
docker ps -a --filter "name=uni_a2a_retrieval_service" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
docker logs uni_a2a_retrieval_service --tail 220
docker inspect uni_a2a_retrieval_service --format "{{json .State.Health}}"
```

Retrieval `healthy` oldugu halde API `Created` kaldiysa:

```powershell
docker start uni_a2a_api
docker exec uni_a2a_api python -c "import json, urllib.request; print(json.dumps(json.load(urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=8)), ensure_ascii=False, indent=2))"
docker restart uni_slack_bot_a2a
```

`docker-compose.a2a-app-gpu.yml` ve `docker-compose.a2a-app-gpu-all.yml` tek basina calistirilmaz; bunlar image/build tanimlamayan GPU overlay dosyalaridir. Standalone calistirilirsa `has neither an image nor a build context specified` hatasi normaldir.

## Kullanici Komutlari

- Normal soru: `Ders kaydi ne zaman basliyor?`
- Giris: `login 20210001`
- OTP dogrulama: `verify 20210001 123456`
- Oturum kapatma: `logout`
- Yardim: `help`

Genel sorular giris olmadan yanitlanir. Kisisel sorularda Slack kullanicisi OTP ile ogrenci hesabina baglanmalidir.

## Notlar

- Conversation context Slack thread bazinda tutulur: `slack:<channel_id>:<thread_ts>`.
- Auth aktifse soru cache politikasi mevcut sistemdeki gibi kisisel guvenlik nedeniyle bypass edebilir.
- Docker'da "Can not decode content-encoding: br" hatasi gorulurse aiohttp/brotli uyumsuzlugu veya image dependency farki incelenmelidir.
- Slack'te iki cevap gelirse once `slack-bot-a2a` ve `slack-bot-inprocess` servislerinden yalniz birinin acik oldugunu kontrol edin. Ayni Slack app token seti iki Socket Mode client ile calisirsa duplicate cevap normaldir.
- `scripts.slack_runtime up/restart` ve Slack dahil `scripts.a2a_rollout` secilen runtime'i acmadan once karsi Slack runtime'i stop eder. Bu guard eski/orphan container ihtimalini azaltir; yine de duplicate cevapta `docker ps -a --filter "name=slack"` ilk kontrol komutudur.
- `Duyurular agent servisine ulasilamadi` veya genel `Kural` fallback'i gorulurse A2A endpoint profile, service auth/signature ve agent health kontrol edilmelidir.
- `docker compose` orphan uyarisi genellikle `slack-bot-a2a` servisinin farkli compose dosya kombinasyonu ile ayakta kalmasindan kaynaklanir. Kapatmak icin once `scripts.slack_runtime stop --runtime a2a`, gerekirse ayni compose project altinda `docker compose ... down --remove-orphans` kullanilir.
- Follow-up ucret sorularinda onceki fakulte/bolum baglami Slack thread context'inde tutulur; kullanici yeni konuya gecerse routing/slot mekanizmasi eski baglamin yanlis uygulanmasini engellemek icin eksik bilgi sorabilir.
