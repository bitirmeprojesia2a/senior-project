# A2A Toplu Mimari Plani

Bu belge, mimari denetimden sonra kabul edilen guncel uygulama sirasini tutar.

## Ilk 10 Madde

1. Runtime authority omurgasi netlestirilecek; davranis belirleyen alanlar `diagnostic_contract` olarak kalmayacak.
2. Capability-first yapi guclendirilecek; agent icindeki ozel kararlar typed capability katmanina tasinacak.
3. Slack security/privacy siniri kurulacak; kisisel veri ve dosya akislari public kanalda cevaplanmayacak.
4. Akademik takvim ve duyuru akisi ayrilacak; tarih sorularinda once takvim, sonra scoped duyuru aranacak.
5. Duyuru listesi ve detay/ozet akisi versioned ref ile calisacak.
6. Bolum/program belirtilen sorularda ilgili bolum belgeleri scoped evidence olarak retrieval havuzuna dahil edilecek.
7. Onkosul, ders programi ve iletisim akislari capability-owner sozlesmesiyle sertlestirilecek.
8. Yanlis cevap analizinde once retrieval/source-owner/capability raporu uretilecek.
9. Golden trace ve Slack replay regresyon seti genisletilecek.
10. Rollout kabul kapilari tek Slack bot, golden trace ve dar Slack replay ile dogrulanacak.

## Duyuru Cache Karari

Duyuru cevaplari genel full-response cache olarak saklanmayacak. Bunun yerine duyuru detay ve ozet akisi `announcement_id + content_hash/updated_at` tabanli versioned ref kullanacak. Duyuru guncellenirse eski conversation ref'i gecersiz sayilacak ve kullanicidan guncel listeyi yenilemesi istenecek.

## Bolum Ozel Belgeleri

Kullanici bolum/program belirtmediyse bolum ozel belgeleri genel cevabi domine etmeyecek. Kullanici bolum/program belirttiyse ilgili `bolum`/`bolum_adi` metadata'sina sahip belgeler retrieval'da boost alacak ve scoped evidence olarak kullanilacak. Genel universite yonetmeligi/policy otoritesi korunacak.

## En Sona Alinacak Buyuk Maddeler

Bu maddeler ilk 10 madde uygulanip test edilip dogrulandiktan sonra ele alinacak:

1. Turkish reranker FP16 shadow benchmark, model secimi ve kalibrasyon.
2. Hybrid model routing.
3. Token/cevap uzunlugu optimizasyonu.
4. Dinamik cok-kurum mimarisi (bu madde bu fazdan cikarildi; en son ayri platform fazi olarak ele alinacak).

### Dinamiklestirme Oncesi Uygulama Notu

- Turkish reranker production default degildir; `scripts/analyze_reranker_scores.py` uzerinden `--model`, `--device` ve `--torch-dtype` ile shadow benchmark olarak denenir.
- Cevap uzunlugu hard-limit ile kesilmez; `answer_length` telemetry'si API diagnostics ve golden trace raporlarina yazilir.
- LLM profil isimleri eski `fast|balanced|quality` ile uyumludur. Ek olarak `groq_only`, `hybrid_shadow`, `hybrid_quality` profilleri vardir; `groq_only` high-value lane'i otomatik devreye sokmaz.
- Golden trace raporu artik answer length ozetini de gosterir.

## Uygulanan Sertlestirme Kapilari

- Duyuru listeleme ve "2. duyuruyu ozetle" follow-up'i `source_ref/cache_version` ile baglanir; ref stale ise eski duyuru ozetlenmez.
- Bolum/program belirtilen sorularda `bolum`/`bolum_adi` metadata boost ve scoped recall calisir; genel yonetmelik daha guclu skordaysa ustte kalir.
- Pipeline ciktisi sadece departmanlari degil, secilen uzman ajanlari da gosterir: `Kayit Isleri`, `Mezuniyet`, `Mufredat`, `Mevzuat`, `Ogrenim Ucreti` vb.
- Transkript Slack public kanalda islenirse cevapta kisisel veri notu gorunur; baglam thread bazinda tutulur.
- API diagnostics icinde `answer_debug_report` alanı route, ajan, source/chunk, source_ref/cache_version ve contract bilgilerini tasir.
- Slack replay fixture seti CAP, AKTS, ders programi, ucret, duyuru, transkript, onkosul ve iletisim akislarini kapsayacak sekilde genisletildi.

## Rollout Kabul Sirasi

```powershell
.\venv\Scripts\python.exe -m scripts.a2a_rollout --gpu --gpu-scope targeted --transport-protocol jsonrpc --include-announcement --include-event --include-all-specialists --slack-service slack-bot-a2a --health-timeout-seconds 300
docker ps -a --filter "name=slack" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
docker exec uni_redis redis-cli -n 0 FLUSHDB
.\venv\Scripts\python.exe -m scripts.audit_slack_replay --input tests\fixtures\slack_diagnostic_cases.json
.\venv\Scripts\python.exe -m scripts.run_shadow_trace_golden --profile balanced --cases GT01,GT04,GT12
.\venv\Scripts\python.exe -m scripts.slack_runtime restart --runtime a2a
```

Canli dar Slack replay sirasi: CAP genel kosul, CAP tarih, yatay gecis tarih, AKTS follow-up, ders programi, ucret follow-up, duyuru liste/ozet, transkript AKTS, onkosul ve iletisim.
