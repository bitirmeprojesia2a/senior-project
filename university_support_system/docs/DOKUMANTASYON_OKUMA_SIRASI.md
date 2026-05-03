# Dokumantasyon Okuma Sirasi

Bu dosya, `docs/` altindaki belgeleri guncel operasyon, mimari karar, tarihsel kayit ve uretilmis rapor olarak ayirir. Projede cok sayida ara benchmark ve faz notu oldugu icin yeni baslayan biri once bu sirayi izlemelidir.

## 1. Guncel Ana Referanslar

1. [README.md](../README.md)
   - Projenin genel amaci, modul haritasi ve ana dokumantasyon girisi.
2. [A2A_DAGITIK_MIMARI_VE_CALISMA_OZETI.md](A2A_DAGITIK_MIMARI_VE_CALISMA_OZETI.md)
   - Nisan 2026 sonunda gelinen dagitik A2A, merkezi retrieval, Slack, routing/follow-up ve veri akisi ozeti.
3. [KURULUM_VE_CALISTIRMA.md](KURULUM_VE_CALISTIRMA.md)
   - Lokal kurulum, seed, rollout, Slack runtime, benchmark ve sik sorunlar icin guncel operasyon rehberi.
4. [SLACK_ENTEGRASYON.md](SLACK_ENTEGRASYON.md)
   - Slack `inprocess` ve `a2a` runtime kullanimi, Socket Mode, auth ve sorun giderme notlari.
5. [demo_runbook.md](demo_runbook.md)
   - Sunum, canli Slack/API denemeleri ve hizli kalite kontrol sorulari.
6. [PROJE_ANATOMISI_KILAVUZU.md](PROJE_ANATOMISI_KILAVUZU.md)
   - Aktif modullerin kompakt sorumluluk haritasi.
7. [SCRIPTS_VE_TESTLER_ENVANTERI.md](SCRIPTS_VE_TESTLER_ENVANTERI.md)
   - `scripts/` ve `tests/` klasorlerinin aktif araclari, benchmark cikti politikasi ve silme/yeniden adlandirma adaylari.

Bu belgeler bugunku calisma davranisini anlatan ana settir.

## 2. Bakim ve Operasyon Notlari

- [AZURE_VM_RUNBOOK.md](AZURE_VM_RUNBOOK.md)
  - Azure VM uzerinde kurulum, tmux, SSH tunnel ve yeniden acilis adimlari.
- [technical_backlog.md](technical_backlog.md)
  - Halen acik teknik iyilestirmeler; tamamlanmis buyuk isler burada aktif is gibi tutulmamalidir.
- [CODEX_PROJE_BAGLAMI.md](CODEX_PROJE_BAGLAMI.md)
  - Codex/agent baglam dosyasi. Kullanici dokumani degil; uzun calismalarda kopmamak icin teknik hafiza olarak kullanilir.

## 3. Mimari Karar ve Gecis Belgeleri

Bu belgeler halen degerlidir fakat bazilari bugunku durumu degil, gecis surecini anlatir:

- [A2A_GECIS_PLANI.md](A2A_GECIS_PLANI.md)
  - Gercek A2A mimarisine gecisin fazlarini ve alinan teknik kararlarin tarihsel izini anlatir.
- [A2A_ANNOUNCEMENT_EVENT_KARAR_NOTU.md](A2A_ANNOUNCEMENT_EVENT_KARAR_NOTU.md)
  - Announcement/event capability agent kararinin ilk notu. Guncel uygulama ozeti icin artik `A2A_DAGITIK_MIMARI_VE_CALISMA_OZETI.md` tercih edilmelidir.
- [CACHE_STRATEJISI.md](CACHE_STRATEJISI.md)
  - Cache kararlarinin arka planini verir; son runtime davranisi icin kod ve kurulum dokumani kontrol edilmelidir.

## 4. Tarihsel Faz Belgeleri

Asagidaki belgeler proje gecmisini ve sistemin faz faz nasil evrildigini anlatmak icin saklanir. Arsiv/cop belge degildir; bitirme projesi anlatiminda teknik gelisim hikayesini destekler. Yine de guncel operasyon komutu veya nihai mimari karari gerekiyorsa ana referanslar once okunmalidir:

- `FAZ_0_TEKNIK_DOKUMANTASYON.md`
- `FAZ_1_TEKNIK_DOKUMANTASYON.md`
- `FAZ_2_TEKNIK_DOKUMANTASYON.md`
- `FAZ_3_AJAN_MIMARISI.md`
- `MART_2026_GUNCELLEME_NOTLARI.md`
- `NISAN_2026_ROUTING_FOLLOWUP_GUNCELLEME_NOTLARI.md`
- `TUM_PROJE_KOD_ANALIZI.md`
- `kapsamli_chromadb_kilavuzu.md`

Bu dosyalarda "planlandi", "iskelet", "sonraki faz" veya eski monolitik varsayimlar bulunabilir. Her faz dosyasinin basina Nisan 2026 itibariyla "Guncel Konumlandirma" notu eklendi; once o not okunmali, sonra detaylara inilmelidir.

## 5. Uretilmis Benchmark ve Analiz Ciktilari

`docs/archive/benchmarks/` altindaki `quality_benchmark_report_*.md`, `quality_benchmark_problem_summary_*.md`, `a2a_latency_compare_*.md`, `rag_evaluation_report.*`, `reranker_score_analysis.*` gibi dosyalar belirli kosularin snapshot ciktilaridir.
`tests/archive/benchmarks/` altindaki `quality_benchmark_*.json` ve `a2a_latency_compare_*.json` dosyalari da ayni kosularin makine okunabilir sonucudur.

Okuma prensibi:

- En yeni rapor bile canli sistemin garantili kalitesi degil, sadece o kosunun sonucudur.
- Eski raporlar problem tarihcesi icin degerlidir ama aktif kalite hedefi yerine gecmez.
- Yeni benchmark Markdown raporlari varsayilan olarak `docs/archive/benchmarks/` altina yazilir.
- Cok sayida eski rapor teslim paketinden haric tutulabilir; ana `docs/` klasorunde aktif rehber gibi tutulmamalidir.

## 6. Arsiv/Silme Karari Icin Yardimci Belge

Arsiv adaylari ve silinmemesi gereken dosyalar icin [DOKUMAN_ENVANTERI_VE_ARSIV_ADAYLARI.md](DOKUMAN_ENVANTERI_VE_ARSIV_ADAYLARI.md) dosyasina bakin. Bu dosya silme islemi yapmaz; sadece adaylari ve gerekceleri listeler.
