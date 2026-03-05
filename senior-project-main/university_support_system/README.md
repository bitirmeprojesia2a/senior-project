# Üniversite Kurumsal Destek Sistemi

> A2A protokolü ve RAG teknolojisi ile çoklu ajan kurumsal destek sistemi.

## Proje Hakkında

Bu proje, üniversite destek hizmetlerini (Finans, Bilgi İşlem, Öğrenci İşleri) yapay zeka ajanlarıyla otomatize eden bir kurumsal destek sistemidir.

### Temel Özellikler
- **Çoklu Ajan Mimarisi:** 3 katmanlı hiyerarşik orkestrasyon (Ana Orkestratör → Departman Orkestratörleri → Uzman Ajanlar)
- **A2A Protokolü:** Google'ın Agent-to-Agent protokolü ile standartlaştırılmış ajan iletişimi
- **RAG Sistemi:** BAAI/bge-m3 gömme modeli + BM25 hibrit arama ile Türkçe semantik arama
- **Cross-Encoder Reranking:** Türkçe fine-tune edilmiş cross-encoder ile yüksek doğrulukta yeniden sıralama
- **Hibrit Sorgu:** Vektör (ChromaDB) + BM25 + RRF füzyonu + SQL (PostgreSQL)
- **Sorgu Cache:** TTL tabanlı in-memory cache ile tekrarlanan sorguların hızlı yanıtlanması
- **İdempotent İndeksleme:** Hash tabanlı chunk ID + upsert ile duplike engelleme
- **Değerlendirme Altyapısı:** 20 soruluk test seti, Precision@k metrikleri, otomatik rapor
- **LLM Entegrasyonu:** Qwen2.5 via Ollama (yerel) + OpenAI (yedek)
- **MCP Protokolü:** Standartlaştırılmış araç erişimi
- **Slack Entegrasyonu:** Kullanıcı arayüzü olarak Slack bot

## Mimari

```
Kullanıcı (Slack)
    │
    ▼
Ana Orkestratör ← LLM (Qwen2.5) — Niyet analizi + Yanıt sentezi
    │
    ├── Finans Orkestratörü
    │   ├── HarçAgent (SQL + RAG)
    │   ├── BursAgent (SQL + RAG)
    │   └── ÖğrenimÜcretiAgent (SQL + RAG)
    │
    ├── IT Orkestratörü
    │   ├── TeknikDestekAgent (RAG)
    │   └── EpostaAgent (RAG)
    │
    └── Öğrenci İşleri Orkestratörü
        ├── DersAgent (SQL + RAG)
        └── KayıtAgent (SQL + RAG)
```

## Teknoloji Yığını

| Bileşen | Teknoloji |
|---------|-----------|
| Dil | Python 3.11+ |
| Web Framework | FastAPI |
| Veritabanı | PostgreSQL 15 |
| Vektör DB | ChromaDB |
| Kuyruk/Cache | Redis 7 |
| LLM | Qwen2.5:7B (Ollama) |
| Gömme Modeli | BAAI/bge-m3 (1024-D, 100+ dil) |
| Reranker | seroe/bge-reranker-v2-m3-turkish-triplet |
| Protokoller | A2A + MCP |
| Konteyner | Docker Compose |
| Kullanıcı Arayüzü | Slack Bot |

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

# 6. AI Modellerini indir (opsiyonel — ilk kullanımda otomatik iner)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
python -c "from sentence_transformers import CrossEncoder; CrossEncoder('seroe/bge-reranker-v2-m3-turkish-triplet', max_length=512)"
docker exec uni_ollama ollama pull qwen2.5:7b

# 7. RAG İndeksleme
python scripts/index_documents.py --reindex

# 8. Unit testler (149 test, Docker gerektirmez)
python -m pytest tests/unit/ -v --tb=short

# 9. Integration testler (ChromaDB gerekli)
python -m pytest tests/integration/ -v --tb=short

# 10. Arama testi
python scripts/test_hybrid_search.py "ÇAP başvurusu için gereken not ortalaması kaçtır"

# 11. RAG değerlendirme raporu
python scripts/evaluate_rag.py
```

> Detaylı kurulum rehberi için: [`docs/KURULUM_VE_CALISTIRMA.md`](docs/KURULUM_VE_CALISTIRMA.md)

## Proje Yapısı

```
university_support_system/
├── src/                    # Kaynak kod
│   ├── a2a/               # A2A protokol sınıfları
│   ├── agents/            # Ajan implementasyonları
│   │   ├── finance/       # Finans ajanları
│   │   ├── it/            # IT ajanları
│   │   └── student/       # Öğrenci işleri ajanları
│   ├── orchestrators/     # Orkestratörler
│   ├── rag/               # RAG pipeline (embedder, retriever, reranker, chunker, vb.)
│   ├── llm/               # LLM istemcileri
│   ├── routing/           # Sorgu yönlendirme
│   ├── db/                # Veritabanı katmanı
│   ├── queue/             # Redis kuyruk
│   ├── cache/             # Cache servisi
│   ├── mcp/               # MCP protokolü
│   ├── slack/             # Slack entegrasyonu
│   ├── api/               # FastAPI gateway
│   ├── security/          # Güvenlik katmanı
│   └── core/              # Konfigürasyon ve sabitler
├── tests/                 # Testler
│   ├── unit/              # Unit testler (149 test, 9 dosya — Docker gerektirmez)
│   └── integration/       # Integration testler (17 test — ChromaDB gerekli)
├── data/
│   ├── test/              # rag_test_questions.json (20 test sorusu)
│   └── metadata/          # doc_registry.json (otomatik üretilir)
├── migrations/            # Alembic migration'ları
├── docs/                  # Teknik dokümantasyon
│   ├── FAZ_0_TEKNIK_DOKUMANTASYON.md
│   ├── FAZ_1_TEKNIK_DOKUMANTASYON.md
│   └── KURULUM_VE_CALISTIRMA.md
├── scripts/               # CLI araçları
│   ├── index_documents.py        # Doküman indeksleme
│   ├── evaluate_rag.py           # RAG değerlendirme raporu
│   ├── test_hybrid_search.py     # Hibrit arama testi
│   ├── query_db.py               # Semantik sorgu
│   └── compare_collections.py    # Koleksiyon karşılaştırma
├── docker-compose.yml     # Servis tanımları
├── Makefile               # Geliştirme kısayolları
├── requirements.txt       # Runtime bağımlılıklar
└── requirements-dev.txt   # Geliştirme bağımlılıkları
```

## Testler

```powershell
# Unit testler (149 test — Docker gerektirmez)
python -m pytest tests/unit/ -v --tb=short

# Integration testler (ChromaDB gerekli — yoksa otomatik atlanır)
python -m pytest tests/integration/ -v --tb=short

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
| [`FAZ_0_TEKNIK_DOKUMANTASYON.md`](docs/FAZ_0_TEKNIK_DOKUMANTASYON.md) | Veritabanı, modeller, şemalar, konfigürasyon |
| [`FAZ_1_TEKNIK_DOKUMANTASYON.md`](docs/FAZ_1_TEKNIK_DOKUMANTASYON.md) | RAG pipeline, embedding, retrieval, reranking, testler |
| [`KURULUM_VE_CALISTIRMA.md`](docs/KURULUM_VE_CALISTIRMA.md) | Kurulum, çalıştırma, model indirme, sorun giderme |

## Lisans

Bu proje bir bitirme projesidir.
