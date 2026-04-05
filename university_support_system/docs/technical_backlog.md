# Technical Backlog

Bu dosya, ana yol haritasi disinda kalan ama unutulmamasi gereken teknik iyilestirmeleri toplar.
Yuksek oncelikli 3 is ayrica burada kayitli; orta ve dusuk oncelikli maddeler daha sonra ele alinabilir.

## Aktif Sonraki 3 Adim

1. Konusma baglami ve follow-up hafizasi eklemek.
2. Retrieval/performance tarafinda son optimizasyon turunu yapmak.
3. `qwen2.5:7b` ve `qwen2.5:3b` icin gorev bazli model ayirimi eklemek.

Durum notu:
- Konusma baglami icin veri modelleri, servis, orchestrator entegrasyonu ve ilk testler eklendi; canli dogrulama ve ince ayar kaldi.
- Retrieval tarafina follow-up source/topic hint boost'u eklendi; daha derin cold-start ve benchmark optimizasyonu halen acik.
- Gorev bazli model ayriminda `conversation` rolu ve `.env` ayarlari eklendi; canli karsilastirma benchmarklari daha sonra yapilacak.

## Orta Oncelik

- `src/routing/router.py` hala buyuk; karar agacini daha kucuk builder/policy parcaciklarina ayirmak faydali olur.
- `src/api/main.py` daha sade ama endpoint seviyesinde hala bir miktar akis yogunlugu var; query/auth/profile endpointleri daha da inceltilebilir.
- `src/db/telemetry.py` best-effort olarak dogru calisiyor ama repository/service ayirimi ile daha okunur hale getirilebilir.
- `src/rag/retriever.py` icinde import agirligi dusmesine ragmen `HybridRetriever` halen agir; ucuncu parti bagimlilik zinciri daha detayli profillenmeli.
- Gercek HTTP benchmark ile in-process benchmark sonuclari ayri raporlanmali; demo ve performans tartismalarinda karisiklik olusmasin.

## Dusuk Oncelik

- Best-effort koruma bloklarindaki bazi `except Exception` yakalamalari daha sonra ozel hata tiplerine indirilebilir.
- Bazi test dosyalarinda Turkce yorum/metinlerde encoding kaynakli bozuk karakterler var; davranisi bozmuyor ama okunabilirlik icin temizlenmeli.
- Domain export modulleri (`src/agents/*/agents.py`, `src/db/models.py`) uyumluluk icin tutuluyor; ileride dogrudan yeni modul yollarina gecilip bu katmanlar sadeletilebilir.
- Warm-up ayarlari varsayilan olarak kapali; dagitim senaryosuna gore daha iyi defaultlar daha sonra degerlendirilebilir.
