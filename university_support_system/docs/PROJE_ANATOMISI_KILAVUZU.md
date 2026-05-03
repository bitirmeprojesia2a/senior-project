# Universite Kurumsal Destek Sistemi
# Proje Anatomisi ve Modul Kilavuzu

Bu belge, guncel repo yapisini ve aktif modullerin sorumluluklarini kisa bir harita olarak ozetler. Ayrintili nihai mimari anlatimi icin `A2A_DAGITIK_MIMARI_VE_CALISMA_OZETI.md`, calistirma komutlari icin `KURULUM_VE_CALISTIRMA.md`, dokuman sirasi icin `DOKUMANTASYON_OKUMA_SIRASI.md` esas alinmalidir.

> Nisan 2026 notu: Bu kilavuz artik arsiv adayi degil, kompakt modul haritasi olarak tutulur. Ancak A2A servis topolojisi, merkezi `retrieval-service`, Slack A2A runtime ve capability agent ayrimi gibi detaylari tam anlatmak icin yeni A2A mimari ozetiyle birlikte okunmalidir.

## 1. Ust Duzey Akis

Guncel sorgu akisi kabaca soyledir:

1. Istemci FastAPI uzerinden `/query` ya da ilgili auth endpoint'ine gelir.
2. API katmani auth, profile ve conversation baglamini cozer.
3. `MainOrchestrator` routing LLM ve deterministic guard'lar ile canonical query, intent, departmanlar, eksik slotlar ve synthesis ihtiyacini belirler.
4. A2A modunda departman/capability servislerine HTTP/JSON-RPC transport ile gidilir; inprocess modda ayni mantik lokal nesnelerle calisir.
5. RAG ihtiyaci olan akislarda agir embedding/reranking isi merkezi `retrieval-service` uzerinden paylastirilabilir.
6. Ilgili departman, uzman veya capability agent cevabi uretir.
7. Gerekirse cevaplar tek cikti haline sentezlenir, telemetry yazilir ve kaynaklar donulur.

## 2. `src/` Dizini

### `src/api/`

Dis dunyaya acilan FastAPI katmanidir.

- `main.py`: uygulama giris noktasi, health endpoint'leri, auth endpoint'leri, `/query` ve internal `/a2a/dispatch`
- `query_flow.py`: query ve dispatch tarafinda ortak baglam cozumleme yardimcilari
- `profile_flow.py`: kullanici profil baglami ve buna bagli yardimci akislar

Bu klasor artik "planli iskelet" degil, aktif uygulama yuzeyidir.

### `src/orchestrators/`

Sorgunun departmanlar arasinda nasil akacagini belirleyen katmandir.

- `main.py`: `MainOrchestrator`
- `department.py`: departman orchestrator yapisi
- `department_dispatch.py`: departmanlara gorev dagitimi
- `department_factories.py`: departman orchestrator olusturuculari
- `department_task_utils.py`: departman gorev yardimcilari
- `announcement_utils.py`: announcement kisa yolu ve cevap yardimcilari
- `query_policy.py`: clarification, announcement detection ve synthesis kurallari
- `response_utils.py`: departman cevaplarini birlestirme
- `synthesis_utils.py`: global synthesis prompt ve karar mantigi
- `task_builders.py`: gorev olusturma yardimcilari
- `user_response_builders.py`: son kullaniciya donecek payload uretimi

Bu klasor son refactor ile ciddi oranda modulerlestirildi; onceki tek parca orchestrator mantigi parcalanmis durumdadir.

### `src/agents/`

Uzman ajanlar burada bulunur. Ajanlar artik domain bazli alt klasorlere ayrilmistir.

- `academic/`
  - `curriculum_agent.py`
  - `regulation_agent.py`
  - `international_agent.py`
- `finance/`
  - tipik olarak tuition ve scholarship odakli ajanlar
- `student/`
  - registration, graduation, internship ve student life odakli ajanlar
- `announcement/`
  - duyuru sorgulari icin ayri ajan akisi
- `base.py`
  - ortak ajan temel siniflari

### `src/routing/`

Departman secimi ve yuksek seviyeli yonlendirme bu klasorde bulunur.

- `router.py`: `DepartmentRouter`
- `routing_policy.py`: karar kurallari ve policy yardimcilari

### `src/rag/`

Dokuman yukleme, isleme, retrieval ve indeksleme burada yer alir.

- `document_loader.py`: `.pdf` ve `.txt` yukleme
- `text_preprocessor.py`: temizlik ve tekrarli satir ayiklama
- `chunker.py`: chunk olusturma
- `embedder.py`: embedding modeli ve vektor uretimi
- `indexer.py`: ChromaDB yazma/okuma katmani
- `pipeline.py`: indeksleme pipeline'i
- `retriever.py`: hibrit retrieval
- `reranker.py`: cross-encoder reranking
- `candidate_utils.py`: candidate listesi yardimcilari
- `query_preprocessor.py`: sorgu genisletme ve on isleme
- `query_cache.py`: sorgu cache mantigi
- `search_planner.py`: retrieval plani yardimcilari
- `warmup.py`: opsiyonel warm-up davranislari

### `src/llm/`

LLM servis katmani burada bulunur.

- `llm_service.py`: birincil/yedek provider mantigi ve health kontrolu
- `ollama_client.py`: yerel Ollama istemcisi
- `openai_client.py`: yedek OpenAI HTTP istemcisi
- `prompt_templates.py`: routing, synthesis ve diger prompt sabitleri

LLM kullanimi rol bazlidir; `.env` uzerinden routing, conversation ve synthesis modelleri ayri belirlenebilir.

### `src/db/`

Veritabani, auth, profile ve telemetry katmanlari burada toplanir.

Temel dosyalar:

- `connection.py`: SQLAlchemy engine ve session yonetimi
- `model_base.py`: ortak ORM temel sinifi
- `models.py`: geriye donuk ortak export noktasi
- `schemas.py`: Pydantic semalari
- `telemetry.py`: query log ve best-effort telemetry

Domain bazli moduller:

- `auth.py`, `auth_models.py`, `auth_queries.py`, `auth_utils.py`
- `conversation_context.py`, `conversation_models.py`
- `profile_context.py`
- `student_models.py`, `student_academic_data.py`, `registration_data.py`
- `finance_models.py`, `finance_data.py`, `scholarship_models.py`
- `curriculum_data.py`
- `announcements.py`, `office_contacts.py`, `personal_data.py`, `support_models.py`

Bu klasor ilk fazlara gore daha moduler hale gelmistir; tum ORM ve servis mantigi tek dosyada tutulmamaktadir.

### `src/core/`

Sistem genelindeki ortak ayarlar ve sabitler burada bulunur.

- `config.py`: ortam degiskenlerini `settings` nesnesine donusturur
- `constants.py`: departmanlar, gorev tipleri ve diger sabitler
- `profiling.py`, `messages.py` gibi yardimci moduller

### Diger klasorler

- `src/notifications/`: OTP ve e-posta gonderim yardimcilari
- `src/slack/`: Slack entegrasyonu ile ilgili temel katman
- `src/cache/`, `src/queue/`, `src/security/`, `src/mcp/`, `src/a2a/`: yardimci ya da gelecekte genisletilecek alanlar

## 3. `scripts/` Dizini

Gunluk operasyon ve benchmark komutlari burada bulunur.

- `index_documents.py`: departman indeksleme
- `evaluate_rag.py`: retrieval kalitesi olcumu
- `query_db.py`: CLI sorgu denemesi
- `hybrid_search_probe.py`: retrieval denemeleri
- `live_question_test.py`: demo ve benchmark preset'leri
- `compare_collections.py`: koleksiyon kiyaslama
- `seed_curriculum_data.py`, `seed_synthetic_data.py`: veri tohumlama yardimcilari
- `profile_benchmarks.json`: demo ve benchmark preset tanimlari

## 4. `tests/` Dizini

Testler iki ana grupta toplanir:

- `tests/unit/`: moduler birim testleri
- `tests/integration/`: servis, retrieval ve model entegrasyon testleri

Integration tarafta `smoke`, `model` ve `slow` marker'lari kullanilir. Dokuman icinde sabit test sayisi vermek yerine guncel envanteri `pytest --collect-only` ile dogrulamak daha sagliklidir.

## 5. `data/` Dizini

- `data/raw/`: indeksleme icin ham dokumanlar
- `data/metadata/`: indeksleme sonrasi registry ve metadata artefaktlari

Cross-platform zip ve VM transfer senaryolarinda bu klasorde izin ve karakter kodlama kaynakli sorunlar gorulebilir; operasyon notlari icin kurulum rehberi ve Azure runbook'a bakin.

## 6. `docs/` Dizini

Bu klasorde iki tur belge vardir:

1. Guncel operasyon belgeleri
   - `KURULUM_VE_CALISTIRMA.md`
   - `AZURE_VM_RUNBOOK.md`
   - `demo_runbook.md`
   - `technical_backlog.md`
2. Tarihsel veya donemsel referanslar
   - `FAZ_0_TEKNIK_DOKUMANTASYON.md`
   - `FAZ_1_TEKNIK_DOKUMANTASYON.md`
   - `FAZ_2_TEKNIK_DOKUMANTASYON.md`
   - `FAZ_3_AJAN_MIMARISI.md`
   - `MART_2026_GUNCELLEME_NOTLARI.md`

## 7. Ozet

Repo guncel durumda:

- calisan FastAPI giris yuzeyi olan
- modulerlestirilmis orchestrator katmanina sahip
- conversation context ve auth akislarini destekleyen
- benchmark ve demo scriptleri bulunan
- lokal ve Azure uzerinde calistirilabilir

bir sistemdir. Kod tabanini anlamaya baslarken once `README.md`, sonra bu dosya, ardindan ilgili domain klasoru okumak en hizli yaklasimdir.
