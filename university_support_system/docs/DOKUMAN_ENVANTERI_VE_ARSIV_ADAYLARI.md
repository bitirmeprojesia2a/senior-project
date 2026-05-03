# Dokuman Envanteri ve Arsiv Adaylari

Bu not, `docs/` altindaki belgelerin hangilerinin aktif referans, hangilerinin tarihsel kayit veya arsiv adayi oldugunu ayirir. Bu dosya herhangi bir silme islemi yapmaz; temizlik karari icin gerekceli liste sunar.

## Aktif Kalmasi Gerekenler

- `DOKUMANTASYON_OKUMA_SIRASI.md`: Dokuman setinin giris noktasi.
- `A2A_DAGITIK_MIMARI_VE_CALISMA_OZETI.md`: En guncel dagitik A2A, merkezi retrieval, Slack ve routing/RAG ozeti.
- `KURULUM_VE_CALISTIRMA.md`: Guncel rollout, seed, Slack, benchmark ve sorun giderme komutlari.
- `SLACK_ENTEGRASYON.md`: Slack runtime ve Socket Mode operasyon notlari.
- `demo_runbook.md`: Canli demo, benchmark ve Slack test sorulari.
- `technical_backlog.md`: Aktif acik isler.
- `PROJE_ANATOMISI_KILAVUZU.md`: Kompakt modul ve sorumluluk haritasi; ayrintili A2A topoloji icin mimari ozetle birlikte okunmali.
- `AZURE_VM_RUNBOOK.md`: Azure/VM operasyonu devam ettigi surece aktif kalmali.
- `CODEX_PROJE_BAGLAMI.md`: Kullanici dokumani degil, fakat uzun Codex oturumlari icin teknik hafiza olarak tutulmali.

## Aktif Degil Ama Saklanmasi Degerli Olanlar

- `A2A_GECIS_PLANI.md`: A2A'ya gecisin tarihsel plani. Bugunku durumu tamamen yansitmasa da karar gecmisi icin degerli.
- `A2A_ANNOUNCEMENT_EVENT_KARAR_NOTU.md`: Announcement/event capability agent kararinin ilk kaydi. Guncel ozetle birlikte okunmali.
- `CACHE_STRATEJISI.md`: Cache kararlarinin arka plani.
- `quality_root_cause_analysis_20260424.md`: RAG/routing kalite problemlerinin kok neden analizi.
- `NISAN_2026_ROUTING_FOLLOWUP_GUNCELLEME_NOTLARI.md`: Conversation/follow-up donemi icin tarihsel kayit.
- `MART_2026_GUNCELLEME_NOTLARI.md`: Mart donemi mimari gecislerinin tarihsel kaydi.
- `FAZ_0_TEKNIK_DOKUMANTASYON.md`: Kurulus, ortak altyapi ve ilk teknik temel.
- `FAZ_1_TEKNIK_DOKUMANTASYON.md`: RAG pipeline'in kurulumu ve ilk kalite donemi.
- `FAZ_2_TEKNIK_DOKUMANTASYON.md`: LLM servis altyapisinin kurulumu.
- `FAZ_3_AJAN_MIMARISI.md`: Cok ajanli mimarinin ilk kapsamli tasarimi.

## Korumali Tarihsel Dokumanlar

Faz dosyalari artik arsiv/silme adayi olarak degerlendirilmemelidir. Bitirme projesi anlatiminda "ne yaptik, neden yaptik, sistem nasil evrildi?" sorusunu cevapladiklari icin ana dokuman setinde kalmalidir.

Bu belgeler okunurken su ilke uygulanir:

- Faz dosyalari donemsel snapshot'tir.
- Her dosyanin basindaki "Guncel Konumlandirma" notu bugunku mimariye nasil baglandigini anlatir.
- Guncel operasyon komutu veya nihai mimari karari gerekiyorsa `A2A_DAGITIK_MIMARI_VE_CALISMA_OZETI.md` ve `KURULUM_VE_CALISTIRMA.md` esas alinmalidir.

## Arsiv Klasorune Tasima Adaylari

Bu dosyalar silinmek yerine `docs/archive/` altina alinabilir. Boylece ana `docs/` klasoru sade kalir, ama kanit/tarihce kaybolmaz.

- `TUM_PROJE_KOD_ANALIZI.md`
- `kapsamli_chromadb_kilavuzu.md`

Gerekce: Bu belgeler faydali olabilir fakat ya daha guncel dokumanlarla kapsaniyor ya da bugunku A2A servisleri, merkezi retrieval servisi, Slack A2A modu ve routing/slot mekanizmasi sonrasinda ana referans olmamalidir.

## Uretilmis Rapor Arsiv Adaylari

Asagidaki pattern'ler cok sayida kosu sonucudur ve `docs/archive/benchmarks/` altinda tutulur:

- `quality_benchmark_report_*.md`
- `quality_benchmark_problem_summary_*.md`
- `a2a_latency_compare_*.md`
- `rag_evaluation_report.md`
- `rag_evaluation_report.json`
- `reranker_score_analysis.md`
- `reranker_score_analysis.json`
- `tests/archive/benchmarks/quality_benchmark_*.json`
- `tests/archive/benchmarks/a2a_latency_compare_*.json`

Oneri:

- Son teslimde sadece en anlamli son raporlar veya final benchmark raporu birakilsin.
- Yeni Markdown benchmark/analiz ciktilari varsayilan olarak `docs/archive/benchmarks/` altina yazilsin.
- JSON artefaktlari cok buyukse ve rapor MD dosyasi yeterliyse teslim paketinden haric tutulabilir; fakat silmeden once `README.md`, `docs/` ve script referanslari kontrol edilmeli.

## Silmeye Daha Yakin Adaylar

Dogudan silme icin su an kesin oneri yok. Guvenli yaklasim once arsivlemek, sonra teslim/paket boyutu veya juri dokuman duzeni gerektirirse silmektir.

Silmeye yaklasabilecek dosyalar:

- Eski `quality_benchmark_report_*.md` dosyalarinin birbirini tekrar eden ara kosulari.
- Eski `a2a_latency_compare_*.md` raporlari; eger final A2A benchmark dokumani uretildiyse.
- `rag_evaluation_report.json` ve `reranker_score_analysis.json`; eger ayni bilgi okunabilir `.md` raporda yeterince ozetleniyorsa.

## Silinmemesi Gerekenler

- `CODEX_PROJE_BAGLAMI.md`: Uzun oturumlarda baglam kopmasini onlemek icin gerekli.
- `KURULUM_VE_CALISTIRMA.md`: Operasyonel tek kaynak.
- `A2A_DAGITIK_MIMARI_VE_CALISMA_OZETI.md`: Arkadasa/proje juri ekibine anlatilacak ana teknik ozet.
- `SLACK_ENTEGRASYON.md`: Slack canli demo ve debug icin gerekli.
- `AZURE_VM_RUNBOOK.md`: VM kullanimi devam ediyorsa gerekli.

## Onerilen Temizlik Plani

1. Faz dosyalari yerinde korunur; baslarindaki guncel konumlandirma notlari yeterli kabul edilir.
2. `docs/archive/` ve `docs/archive/benchmarks/` klasorleri yalnizca gercek ara ciktilar icin acilir.
3. Benchmark raporlarindan final/temsil edici olanlar secilir; ara kosular `docs/archive/benchmarks/` altina tasinir.
4. `README.md` ve `DOKUMANTASYON_OKUMA_SIRASI.md` linkleri yeni konumlara gore guncellenir.
5. Son olarak `rg "eski_dosya_adi"` ile repo icinde kirik referans kalmadigi dogrulanir.
