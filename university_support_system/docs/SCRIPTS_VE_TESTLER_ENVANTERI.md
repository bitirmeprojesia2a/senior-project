# Scripts ve Tests Envanteri

Bu dosya `scripts/` ve `tests/` klasorlerinin Nisan 2026 itibariyle temizlik durumunu, aktif kullanimlarini ve silme/yeniden adlandirma adaylarini kaydeder.

Temel prensip: `scripts/` altindaki dosyalarin bir kismi pytest testi degil, manuel benchmark/diagnostic aracidir. `pyproject.toml` icinde `testpaths = ["tests"]` oldugu icin pytest yalnizca `tests/` klasorunu toplar. Bu karisikligi azaltmak icin aktif manuel scriptlerdeki `test_*.py` adlari kaldirildi.

## Aktif Runtime ve Rollout Scriptleri

Bu dosyalar su an aktif sistemin parcasidir; silinmemeli.

- `scripts/a2a_rollout.py`: Docker A2A stack build/up/health kontrolu. A2A dagitik calistirma icin ana giris.
- `scripts/run_agent_service.py`: A2A agent servislerini baslatan entrypoint.
- `scripts/run_retrieval_service.py`: merkezi retrieval/reranker servis entrypoint'i. Referansi az gorunebilir ama Docker servisinin calisma girisidir.
- `scripts/run_slack_bot.py`: lokal Slack bot girisi.
- `scripts/slack_runtime.py`: Slack runtime modlari ve inprocess/A2A secimi.
- `scripts/a2a_docker_stack_smoke.py`: Docker stack smoke testi; rollout sonrasi saglik/topoloji dogrulamasi.
- `scripts/a2a_http_canary.py`, `scripts/a2a_main_http_smoke.py`, `scripts/a2a_two_process_smoke.py`, `scripts/a2a_external_mock_smoke.py`: A2A transport ve endpoint canary/smoke araclari.
- `scripts/a2a_model_cache_check.py`: container/model cache kontrolu.

## Veri Hazirlama ve Senkronizasyon Scriptleri

Bu dosyalar veri katmani icin aktif veya tekrar kullanilabilir araclar olarak kalmali.

- `scripts/index_documents.py`: dokumanlari chunk/embedding/Chroma indeksine yazan ana indeksleme araci.
- `scripts/seed_synthetic_data.py`: demo/test VT verileri.
- `scripts/seed_curriculum_data.py`: temel mufredat/ders verileri.
- `scripts/seed_curriculum_from_json.py`: UBYS/export JSON ciktilarini veritabanina alma.
- `scripts/export_curriculum_from_ubys.py`: UBYS'den mufredat export araci. Su an referansi az ama veri guncelleme icin gerekli olabilir.
- `scripts/seed_curriculum_from_ubys.py`: UBYS tabanli dogrudan seed akisi. Su an referansi az ama veri guncelleme icin saklanmali.
- `scripts/ingest_schedule_slots.py`: haftalik ders programi slotlarini veritabanina alma.
- `scripts/sync_announcements.py`: duyuru senkronizasyonu.
- `scripts/sync_events.py`: etkinlik senkronizasyonu.

## Benchmark ve Analiz Scriptleri

Bu dosyalar urun runtime'i degil, kalite/performans analizi icindir. Ciktilari artik ana klasorleri kirletmemek icin arsiv klasorlerine yazilir.

- `scripts/run_quality_benchmark.py`: 25 soruluk kalite benchmark'i. JSON cikti: `tests/archive/benchmarks/`. Markdown rapor: `docs/archive/benchmarks/`.
- `scripts/compare_a2a_latency.py`: A2A gecikme karsilastirmasi. JSON cikti: `tests/archive/benchmarks/`. Markdown rapor: `docs/archive/benchmarks/`.
- `scripts/summarize_quality_benchmark.py`: kalite benchmark JSON'larini problem siniflarina ayirir.
- `scripts/evaluate_rag.py`: RAG retrieval/cevap degerlendirme araci. Varsayilan rapor: `docs/archive/benchmarks/rag_evaluation_report.md`.
- `scripts/analyze_reranker_scores.py`: reranker skor dagilimi analizi. Varsayilan rapor: `docs/archive/benchmarks/reranker_score_analysis.md`.
- `scripts/compare_reranker_models.py`: mevcut reranker ile alternatif/base modeli karsilastirma diagnostigi. Referansi az ama model karari verirken faydali.
- `scripts/live_question_test.py`: canli soru/demo kosulari icin genis benchmark araci.

## Manuel Diagnostic Araçlari

Bu dosyalar pytest testi degil, manuel diagnostic/benchmark aracidir. `test_*.py` adlarindan arindirildi; boylece test suite ile karismalari onlendi.

- `scripts/gpu_diagnostics.py`: GPU/model performans diagnostigi. `RERANKER_LOCAL_FILES_ONLY=false` gibi ayarlarla model indirme davranisini tetikleyebilir; dikkatli calistirilmali.
- `scripts/hybrid_search_probe.py`: Chroma hybrid search probe araci.
- `scripts/followup_benchmark.py`: follow-up/context E2E benchmark araci.
- `scripts/announcement_benchmark.py`: duyuru benchmark araci.
- `scripts/cache_smoke.py`: cache smoke araci.
- `scripts/query_db.py`: manuel Chroma sorgu araci; adi net, kalabilir.
- `scripts/compare_collections.py`: Chroma koleksiyon karsilastirma araci; adi net, kalabilir.
- `scripts/manage_cache.py`: cache temizleme/istatistik CLI; aktif yardimci arac.
- `scripts/audit_document_corpus.py`, `scripts/audit_academic_source_coverage.py`: kaynak kapsama ve corpus denetimi icin yararli audit araclari.

## Arsive Alinan Eski Diagnosticler

Kullanici onayindan sonra silmek yerine guvenli bicimde `scripts/archive/` altina tasindi.

- `scripts/archive/diag_announcement.py`: eski duyuru marker/routing problemi icin tek-seferlik diagnostic. Parametre almiyor, sabit query'ler basiyor; yeni duyuru akisi ve benchmark araclariyla kapsami karsilaniyor.
- `scripts/archive/test_reranker_quality.py`: eski manuel reranker testi. Dosyada mojibake/encoding bozulmalari var; ihtiyac artik `compare_reranker_models.py`, `analyze_reranker_scores.py`, `run_quality_benchmark.py` ile daha sistematik karsilaniyor.

## Tests Klasoru Durumu

`tests/` altindaki Python testleri genel olarak aktif regresyon guvencesi veriyor; bu tur incelemede net silme adayi bulunmadi.

- A2A testlerinde gorulen `legacy_response_schema` ve legacy mapper kontrolleri eski sistem kalintisi degil; A2A generic artifact sozlesmesine geciste geriye uyumluluk garantisi.
- Integration testleri Chroma/model cache yoksa `skip` ile atliyor; bu davranis bilincli.
- `tests/archive/benchmarks/` pytest test klasoru degildir; uretilmis JSON benchmark ciktilarinin arsividir.
- Ana `tests/` kokunde uretim ciktilari temizlendi; kokte yalnizca `conftest.py` gibi test altyapisi dosyalari kalmali.

## Yapilan Temizlik

- Eski Markdown benchmark raporlari `docs/archive/benchmarks/` altina alindi.
- Eski JSON benchmark ciktilari `tests/archive/benchmarks/` altina alindi.
- Benchmark/analiz scriptlerinin varsayilan cikti klasorleri bu arsiv yollarina yonlendirildi.
- `.dockerignore` arsiv benchmark ciktilarini Docker build context disinda tutacak sekilde guncellendi.

## Sonraki Karar Noktalari

1. Arsive alinan iki eski diagnostic dosyasi bir sure sonra tamamen silinsin mi?
2. Veri sync/seed scriptleri icin tek bir `docs/VERI_GUNCELLEME_RUNBOOK.md` dosyasi olusturup kullanim sirasini netlestirelim mi?
