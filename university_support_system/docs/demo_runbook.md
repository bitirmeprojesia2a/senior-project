# Demo Runbook

> Not: Bu belge demo, Slack denemesi ve benchmark operasyonu icin gunceldir. Kurulum ve altyapi hazirligi icin once `README.md`, `KURULUM_VE_CALISTIRMA.md` ve gerekiyorsa `AZURE_VM_RUNBOOK.md` okunmalidir.

## 1. Varsayilan Demo Mimarisi

Bugunku ana demo yolu dagitik A2A runtime'dir:

- `api`
- `retrieval-service`
- department orchestrator agent'lari
- specialist agent'lar
- `agent-announcement`
- `agent-event`
- istege bagli `slack-bot-a2a`

Monolitik `inprocess` Slack modu halen fallback ve karsilastirma icin tutulur; ayni Slack token setiyle iki bot ayni anda acilmamalidir.

## 2. Full A2A Rollout

Calisma klasoru:

```powershell
cd "C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system"
```

Kod, dependency veya data degistiyse build'li rollout:

```powershell
.\venv\Scripts\python.exe -m scripts.a2a_rollout --gpu --gpu-scope targeted --transport-protocol jsonrpc --include-announcement --include-event --include-all-specialists --health-timeout-seconds 300
```

Sadece mevcut image ile servisleri yeniden kaldirmak icin:

```powershell
.\venv\Scripts\python.exe -m scripts.a2a_rollout --gpu --gpu-scope targeted --skip-build --transport-protocol jsonrpc --include-announcement --include-event --include-all-specialists --health-timeout-seconds 300
```

`--skip-build`, kod degisikligi Docker image'ina girmeyecegi icin sadece imaj zaten guncelse kullanilmalidir.

## 3. Slack Runtime

A2A Slack bot:

```powershell
.\venv\Scripts\python.exe -m scripts.slack_runtime up --runtime a2a
.\venv\Scripts\python.exe -m scripts.slack_runtime logs --runtime a2a
```

Monolitik Slack bot:

```powershell
.\venv\Scripts\python.exe -m scripts.slack_runtime up --runtime inprocess
.\venv\Scripts\python.exe -m scripts.slack_runtime logs --runtime inprocess
```

Kapatma:

```powershell
.\venv\Scripts\python.exe -m scripts.slack_runtime stop --runtime a2a
.\venv\Scripts\python.exe -m scripts.slack_runtime stop --runtime inprocess
```

Kontrol:

- Slack'te iki cevap gelirse iki runtime birden acik olabilir.
- `Duyurular agent servisine ulasilamadi` gorulurse `agent-announcement` health ve A2A endpoint profile kontrol edilmelidir.
- Kisisel sorular icin `login <ogrenci_no>` ve `verify <ogrenci_no> <kod>` akisi gerekir.

## 4. Hizli Kalite Benchmark

25 soruluk kalite seti:

```powershell
.\venv\Scripts\python.exe -m scripts.run_quality_benchmark --use-api --api-base-url http://127.0.0.1:8000 --llm-profile balanced --warmup-mode full --warmup-timeout 90
```

Kisa smoke seti:

```powershell
.\venv\Scripts\python.exe -m scripts.run_quality_benchmark --use-api --api-base-url http://127.0.0.1:8000 --question Q1 Q7 Q17 Q23 Q25 --llm-profile balanced --warmup-mode full --warmup-timeout 90
```

A2A stack smoke:

```powershell
.\venv\Scripts\python.exe -m scripts.a2a_docker_stack_smoke --expect-protocol jsonrpc --min-active 15 --timeout 120
```

## 5. Slack Uzerinden Denenecek Soru Seti

Capability ve guncel veri:

- `guncel duyur`
- `bugünkü etkinlikler neler`
- `yaklaşan seminer var mı`
- `Elektrik elektronik mühendisliği ders programı var mı?`

Ogrenci isleri / RAG:

- `Ders kaydı nasıl yapılır?`
- `Sınav notuma nasıl itiraz ederim?`
- `Yatay geçişle geldim, muafiyet başvurusu ne zaman yapılır?`
- `Okulu dondurdum dönüşte ders seçimini nasıl yapacağım?`
- `Staj başvurusu nasıl yapılır?`
- `Staj yapmazsam mezun olabilir miyim?`

Structured DB / follow-up:

- `Diş hekimliği dönem ücreti ne kadar?`
- `Türk öğrenciyim`
- `Yabancı öğrenciler için ne kadar?`
- `Elektrik elektronik mühendisliği öğrenim ücreti ne kadar?`
- `Olasılık ve istatistiğe giriş dersi hangi sınıfta?`
- `BIL104 dersinin ön koşulu var mı?`

Auth gerektiren:

- `Harc borcum ne kadar?`
- `Not ortalamam kaç?`
- `Kaç AKTS tamamladım?`

Belirsiz/negatif test:

- `Naber`
- `şey başvuru ne zaman`
- `harç mı ders mi bilmiyorum`
- `Final sınavları ne zaman?`
- `Fizik`
- `Fizik bölümü final sınavları`

Bu sorularda amac sadece dogru cevabi degil, sistemin eksik slot isteme, belirsiz sorguda clarification uretme ve eski konu baglamina gereksiz takilmama davranisini da gormektir.

## 6. Sunumda Duz Dille Soylenebilecekler

- Sistem artik Slack/API uzerinden tek monolit degil, A2A servisleriyle dagitik calisabiliyor.
- Retrieval/reranking agirligi merkezi `retrieval-service` uzerinde toplandi; her agent'in model isitmasi gerekmiyor.
- Duyuru ve etkinlikler klasik RAG'den ayrildi; capability agent olarak calisiyor.
- Ucret, ders plani, on kosul ve kayit donemi gibi yapilandirilmis bilgiler veritabanindan geliyor.
- Mevzuat ve prosedur sorulari RAG + LLM senteziyle cevaplanir; kaynak ozeti her cevapta korunur.
- Routing LLM artik sadece departman secmiyor; canonical query, intent ve eksik slot sinyali de uretiyor. Deterministik katman bu sinyali guvenlik ve structured-data guard'lariyla denetliyor.

## 7. Guven Seviyesi

- `demo_showcase_stable_turk`: en guvenli demo seti.
- `demo_showcase_international`: uluslararasi ogrenci farkini gosterir.
- `demo_showcase_broad_turk`: daha fazla ajan ve soru tipi gosterir.
- `demo_showcase_llm_turk`: LLM sentezini gosterir, etkileyici ama daha risklidir.
- `demo_followup_turk`: context/follow-up davranisini gosterir.

CLI demo komutlari halen kullanilabilir, fakat canli sunumda Slack A2A modu bugunku mimariyi daha iyi gosterir.
