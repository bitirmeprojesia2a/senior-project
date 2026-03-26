# Üniversite Kurumsal Destek Sistemi

> RAG ve LLM tabanlı üniversite destek sistemi çekirdeği. Çok ajanlı yapı hedeflenmektedir; mevcut repo ağırlıklı olarak RAG, LLM ve veritabanı katmanlarını içerir.

## Proje Hakkında

Bu repo, üniversite destek senaryoları için geliştirilen sistemin çekirdek bileşenlerini içerir. Mevcut implementasyonun odak noktası:

- kurumsal dokümanlardan bilgi getiren RAG hattı,
- LLM istemcileri ve fallback mekanizması,
- PostgreSQL veri modeli ve şemaları,
- değerlendirme ve test altyapısıdır.

Çok ajanlı orkestrasyon, Slack arayüzü, FastAPI geçidi, Redis tabanlı kuyruk/önbellek ve güvenlik katmanları bu depoda bağımlılık ve klasör düzeyinde hazırlanmış olsa da, şu an aktif çalışma yüzeyi büyük ölçüde çekirdek RAG/LLM kodudur.

### Mevcut Özellikler

- **RAG Sistemi:** BAAI/bge-m3 + BM25 hibrit arama ile Türkçe semantik erişim
- **Cross-Encoder Reranking:** Türkçe için iyileştirilmiş reranker ile sonuç sıralama
- **İdempotent İndeksleme:** Hash tabanlı chunk ID + upsert ile tekrarları önleme
- **Sorgu Cache:** TTL tabanlı in-memory cache
- **LLM Entegrasyonu:** Ollama (birincil) + OpenAI (yedek)
- **Değerlendirme Altyapısı:** Departman etiketli 30 soruluk test havuzu, Precision@k metrikleri, otomatik rapor üretimi
- **SQLAlchemy 2 + Alembic:** tipli ORM modelleri ve migration akışı

### Mart 2026 Güncellemesi

- **Çok departmanlı RAG çekirdeği:** `academic_programs` resmi departman olarak sisteme eklendi. Aktif çekirdek şu anda `student_affairs`, `academic_programs` ve `finance` departmanlarıyla çalışır.
- **Dinamik koleksiyon çözümü:** İndeksleme ve sorgulama hattı artık tek bir sabit koleksiyona bağlı değil. `student_affairs_docs`, `academic_programs_docs` ve `finance_docs` ana departman bazlı koleksiyonlar olarak ele alınır.
- **Metadata iyileştirmesi:** `academic_programs` belgelerinde bölüm (`bolum`) bilgisi metadata olarak tutulur; bir belge birden fazla bölüme işaret ediyorsa `genel` etiketi kullanılır.
- **Script hizalama:** `index_documents.py`, `query_db.py`, `test_hybrid_search.py`, `compare_collections.py` ve `evaluate_rag.py` scriptleri departman/koleksiyon farkındalıklı hale getirildi.
- **Merkezi departman kaydı:** Departman display adı, routing açıklaması, keyword kümesi ve kaynak klasör bilgisi `src/core/constants.py` içinde tek yerde toplanarak yeni departman ekleme maliyeti düşürüldü.
- **Test stratejisi güncellemesi:** Integration testler `smoke`, `model` ve `slow` marker'ları ile ayrıldı. Reranker'ın gerçekten devreye girip girmediğini doğrulayan ek test eklendi.
- **GPU hazırlığı:** Embedding ve reranker tarafına `auto | cpu | cuda` cihaz seçimi eklendi. CUDA destekli `torch` ile birlikte `auto` modu GPU kullanabilir.
- **OTP/session auth akışı:** `/auth/request-otp`, `/auth/verify-otp`, `/auth/resolve` ve `/auth/logout` endpoint'leri eklendi. `/query` ve `/a2a/dispatch` artık `session_token` veya `slack_user_id` üzerinden kimlik bağlamı çözebilir.

Ayrıntılı değişiklik özeti ve güncel teknik durum için: `docs/MART_2026_GUNCELLEME_NOTLARI.md`

### Repo İçinde Henüz Tamamlanmamış Alanlar

- **Çoklu ajan orkestrasyonu:** temel A2A yardımcıları, uzman ajan tabanı, departman orkestratörleri ve ana orkestratör iskeleti kodlandı
- **FastAPI giriş yüzeyi:** `src.api.main:app` altında sağlık, sorgu, ajan listesi ve iç A2A dispatch endpoint'leri eklendi
- **Slack entegrasyonu:** paket ve klasör iskeleti mevcut, aktif entegrasyon yok
- **Redis kuyruk/önbellek:** bağımlılık ve ayarlar mevcut, aktif retrieval cache in-memory çalışıyor

## Mevcut Mimari

```text
Kullanıcı sorgusu
    |
    v
Query Preprocessor
    |
    v
Hybrid Retriever
  - BM25
  - ChromaDB semantic search
  - Cross-encoder reranker
    |
    v
LLM Service
  - Ollama
  - OpenAI fallback
    |
    v
Yanıt + kaynaklar
```

## Teknoloji Yığını

| Bileşen | Teknoloji | Durum |
|---------|-----------|-------|
| Dil | Python 3.11+ | Aktif |
| Veritabanı | PostgreSQL 15 | Aktif |
| Vektör DB | ChromaDB | Aktif |
| LLM | Qwen2.5:7B (Ollama) | Aktif |
| Gömme Modeli | BAAI/bge-m3 | Aktif |
| Reranker | seroe/bge-reranker-v2-m3-turkish-triplet | Aktif |
| Web Framework | FastAPI | Aktif API giriş yüzeyi mevcut |
| Kuyruk/Önbellek | Redis 7 | Ayarlar var, aktif kullanım sınırlı |
| Protokoller | A2A + MCP | A2A yardımcıları ve orkestratör iskeleti aktif, tam ağ entegrasyonu sonraki faz |
| Kullanıcı Arayüzü | Slack Bot | Planlı / iskelet |
| Konteyner | Docker Compose | Aktif |

## Hızlı Başlangıç

### Ön Koşullar

- Python 3.11+
- Docker & Docker Compose
- Git

### Kurulum

```powershell
# 1. Sanal ortam
python -m venv venv
venv\Scripts\activate

# 2. Bağımlılıklar
pip install -r requirements-dev.txt

# 3. Ortam değişkenleri
copy .env.example .env

# 4. Docker servisleri (PostgreSQL, Redis, ChromaDB, Ollama)
docker compose up -d

# 5. Veritabanı migration
python -m alembic upgrade head

# 6. AI modellerini indir (opsiyonel - ilk kullanımda otomatik iner)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
python -c "from sentence_transformers import CrossEncoder; CrossEncoder('seroe/bge-reranker-v2-m3-turkish-triplet', max_length=512)"
docker exec uni_ollama ollama pull qwen2.5:7b

# 7. RAG indeksleme
python scripts/index_documents.py --reindex

# 8. Unit testler (206 test, Docker gerektirmez)
python -m pytest tests/unit/ -v --tb=short

# 9. Integration testler (20 test, ChromaDB gerekli)
python -m pytest tests/integration/ -v --tb=short

# 10. Arama testi
python scripts/test_hybrid_search.py "ÇAP başvurusu için gereken not ortalaması kaçtır"

# 11. RAG değerlendirme raporu
python scripts/evaluate_rag.py

# 12. API'yi çalıştır
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

> GPU kullanacaksanız `EMBEDDING_DEVICE` ve `RERANKER_DEVICE` ayarlarını `cuda` veya `auto` olarak bırakabilirsiniz. Bunun çalışması için kurulu `torch` paketinin CUDA destekli olması gerekir.

> Not: Bu repo içinde artık çalıştırılabilir bir `src.api.main:app` girişi vardır. Slack katmanı halen sonraki faz için iskelet düzeyindedir.

> Detaylı kurulum rehberi için: [`docs/KURULUM_VE_CALISTIRMA.md`](docs/KURULUM_VE_CALISTIRMA.md)

## Proje Yapısı

```text
university_support_system/
|-- src/
|   |-- rag/               # Aktif RAG hattı
|   |-- llm/               # Aktif LLM istemcileri ve servis katmanı
|   |-- db/                # Aktif veritabanı katmanı
|   |-- core/              # Aktif konfigürasyon ve sabitler
|   |-- routing/           # Aktif DepartmentRouter
|   |-- agents/            # Temel uzman ajan iskeleti
|   |-- orchestrators/     # Temel ana/departman orkestratörleri
|   |-- api/               # Aktif FastAPI giriş yüzeyi
|   |-- slack/             # İskelet
|   |-- security/          # İskelet
|   |-- queue/             # İskelet
|   |-- cache/             # İskelet
|   `-- mcp/               # İskelet
|-- tests/
|   |-- unit/              # 206 unit test
|   `-- integration/       # 20 integration test
|-- scripts/               # CLI araçları
|-- migrations/            # Alembic migration'ları
|-- docs/                  # Teknik dokümantasyon
|-- docker-compose.yml
|-- Makefile
|-- requirements.txt
`-- requirements-dev.txt
```

## Testler

```powershell
# Unit testler (206 test - Docker gerektirmez)
python -m pytest tests/unit/ -v --tb=short

# Integration testler (20 test - ChromaDB gerekli)
python -m pytest tests/integration/ -v --tb=short

# Hızlı smoke/model testleri
python -m pytest tests/integration/ -m "smoke or model" -v --tb=short

# Uzun kalite testleri
python -m pytest tests/integration/ -m slow -v --tb=short

# Tüm testler
python -m pytest tests/ -v --tb=short

# Coverage ile
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

# RAG değerlendirme raporu (Precision@k, ChromaDB gerekli)
python scripts/evaluate_rag.py
```

## Dokümantasyon

| Doküman | Açıklama |
|---------|----------|
| [`FAZ_0_TEKNIK_DOKUMANTASYON.md`](docs/FAZ_0_TEKNIK_DOKUMANTASYON.md) | Erken faz veritabanı ve konfigürasyon anlatımı; bazı noktalar güncel koddan sapmış olabilir |
| [`FAZ_1_TEKNIK_DOKUMANTASYON.md`](docs/FAZ_1_TEKNIK_DOKUMANTASYON.md) | RAG pipeline, embedding, retrieval, reranking ve testler |
| [`FAZ_2_TEKNIK_DOKUMANTASYON.md`](docs/FAZ_2_TEKNIK_DOKUMANTASYON.md) | LLM servisi, Ollama, OpenAI fallback ve streaming |
| [`KURULUM_VE_CALISTIRMA.md`](docs/KURULUM_VE_CALISTIRMA.md) | Kurulum, çalıştırma, model indirme, sorun giderme |
| [`PROJE_ANATOMISI_KILAVUZU.md`](docs/PROJE_ANATOMISI_KILAVUZU.md) | Modül bazlı repo anatomisi |

## Lisans

Bu proje bir bitirme projesidir.
