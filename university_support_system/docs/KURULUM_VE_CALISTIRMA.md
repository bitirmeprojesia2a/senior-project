# Kurulum ve Çalıştırma Rehberi

**Proje:** Üniversite Kurumsal Destek Sistemi  
**Güncellenme Tarihi:** 26 Mart 2026  
**Python Sürümü:** 3.11+  
**İşletim Sistemi:** Windows 10/11 (Linux/macOS uyumlu notlar dahil)

---

## İçindekiler

1. [Ön Koşullar](#1-ön-koşullar)
2. [Projeyi Klonlama](#2-projeyi-klonlama)
3. [Python Ortamı Kurulumu](#3-python-ortamı-kurulumu)
4. [Docker Servislerini Başlatma](#4-docker-servislerini-başlatma)
5. [Ortam Değişkenleri Konfigürasyonu](#5-ortam-değişkenleri-konfigürasyonu)
6. [Veritabanı Migration](#6-veritabanı-migration)
7. [AI Modellerinin İndirilmesi](#7-ai-modellerinin-i̇ndirilmesi)
8. [RAG Pipeline — Doküman İndeksleme](#8-rag-pipeline--doküman-i̇ndeksleme)
9. [Testleri Çalıştırma](#9-testleri-çalıştırma)
10. [RAG Arama Testleri](#10-rag-arama-testleri)
11. [Uygulamayı Başlatma](#11-uygulamayı-başlatma)
12. [Makefile Kısayolları](#12-makefile-kısayolları)
13. [Sorun Giderme](#13-sorun-giderme)
14. [Ortam Değişkenleri Referansı](#14-ortam-değişkenleri-referansı)

---

## 1. Ön Koşullar

Projeyi çalıştırabilmek için aşağıdaki yazılımların kurulu olması gerekir:

| Yazılım | Minimum Sürüm | Kontrol Komutu | Amaç |
|---------|:--------------:|----------------|------|
| Python | 3.11+ | `python --version` | Ana uygulama dili |
| Docker | 24.0+ | `docker --version` | PostgreSQL, Redis, ChromaDB, Ollama |
| Docker Compose | 2.20+ | `docker compose version` | Çoklu konteyner yönetimi |
| Git | 2.40+ | `git --version` | Kaynak kod yönetimi |

**Disk Alanı Gereksinimleri:**

| Bileşen | Yaklaşık Boyut | Açıklama |
|---------|:--------------:|----------|
| Python venv + bağımlılıklar | ~4 GB | PyTorch ve transformer kütüphaneleri |
| BAAI/bge-m3 (embedding modeli) | ~2.2 GB | İlk çalıştırmada HuggingFace'den indirilir |
| seroe/bge-reranker-v2-m3-turkish-triplet | ~1.1 GB | İlk `rerank()` çağrısında indirilir |
| Qwen2.5:7B (LLM) | ~4.7 GB | Ollama üzerinden indirilir |
| Docker imajları (PostgreSQL, Redis, ChromaDB, Ollama) | ~3 GB | İlk `docker compose up` ile indirilir |
| ChromaDB vektör verisi | ~50 MB | İndeksleme sonrası |
| **Toplam** | **~15 GB** | |

**RAM Gereksinimleri:**

| Bileşen | Minimum RAM | Önerilen |
|---------|:-----------:|:--------:|
| Embedding modeli (BAAI/bge-m3) | 2 GB | 4 GB |
| Cross-encoder reranker | 1 GB | 2 GB |
| Qwen2.5:7B (Ollama) | 6 GB | 8 GB |
| Docker servisleri | 1 GB | 2 GB |
| **Toplam (tümü aktif)** | **10 GB** | **16 GB** |

> **Not:** RAG pipeline (indeksleme, arama, test) sadece embedding ve reranker modeli gerektirir — LLM olmadan da çalışır. Sadece RAG testi için 8 GB RAM yeterlidir.

---

## 2. Projeyi Klonlama

```powershell
git clone <repository-url>
cd university_support_system/university_support_system
```

Proje klasör yapısı:

```
university_support_system/
├── src/                          # Kaynak kod
│   ├── rag/                     # RAG pipeline modülleri
│   ├── db/                      # Veritabanı katmanı
│   ├── agents/                  # Ajan implementasyonları
│   ├── orchestrators/           # Orkestratörler
│   ├── core/                    # Konfigürasyon ve sabitler
│   └── ...                      # api/, llm/, routing/, slack/, vb.
├── tests/                       # Test dosyaları
│   ├── conftest.py              # Test fixture'ları
│   └── unit/                    # Unit testler (206 test)
├── scripts/                     # CLI araçları
├── migrations/                  # Alembic migration'ları
├── docs/                        # Teknik dokümantasyon
├── data/raw/student_affairs/  # Kaynak dokümanlar
├── docker-compose.yml
├── requirements.txt             # Runtime bağımlılıklar
├── requirements-dev.txt         # Geliştirme bağımlılıkları
├── pyproject.toml               # Proje konfigürasyonu
├── Makefile                     # Geliştirme kısayolları
├── alembic.ini                  # Migration konfigürasyonu
└── .env.example                 # Ortam değişkenleri şablonu
```

---

## 3. Python Ortamı Kurulumu

### 3.1 Sanal Ortam Oluşturma

**Windows (PowerShell):**

```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

Başarılı aktivasyonda terminal promptunda `(venv)` göreceksiniz.

### 3.2 Bağımlılıkları Kurma

**Geliştirme ortamı** (testler + kod kalitesi araçları dahil — önerilen):

```powershell
pip install -r requirements-dev.txt
```

**Sadece runtime** (production):

```powershell
pip install -r requirements.txt
```

> **Süre:** İlk kurulumda PyTorch (~2 GB) ve transformer kütüphaneleri indirildiği için **10-30 dakika** sürebilir (internet hızına bağlı).

### 3.3 Kurulumu Doğrulama

```powershell
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import sentence_transformers; print(f'SentenceTransformers: {sentence_transformers.__version__}')"
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "from src.core.config import settings; print(f'Config OK — Embedding: {settings.embedding.model}')"
```

Beklenen çıktı:

```
PyTorch: 2.6.0
SentenceTransformers: 3.4.1
FastAPI: 0.115.12
Config OK — Embedding: BAAI/bge-m3
```

---

## 4. Docker Servislerini Başlatma

Proje 4 Docker servisi kullanır. Hepsi `docker-compose.yml` ile tanımlıdır.

### 4.1 Tüm Servisleri Başlatma

```powershell
docker compose up -d
```

Bu komut aşağıdaki konteynerleri oluşturur:

| Konteyner | İmaj | Port | Amaç |
|-----------|------|:----:|------|
| `uni_postgres` | `postgres:15-alpine` | 5432 | Ana veritabanı |
| `uni_redis` | `redis:7-alpine` | 6379 | Cache ve kuyruk |
| `uni_chromadb` | `chromadb/chroma:0.5.23` | 8100 | Vektör veritabanı |
| `uni_ollama` | `ollama/ollama:latest` | 11434 | Yerel LLM sunucusu |

### 4.2 Servislerin Durumunu Kontrol Etme

```powershell
docker compose ps
```

Tüm servislerin `running (healthy)` durumunda olduğunu doğrulayın.

### 4.3 Servisleri Tek Tek Test Etme

**PostgreSQL:**

```powershell
docker exec uni_postgres pg_isready -U postgres
```

Beklenen: `localhost:5432 - accepting connections`

**Redis:**

```powershell
docker exec uni_redis redis-cli ping
```

Beklenen: `PONG`

**ChromaDB:**

```powershell
curl http://localhost:8100/api/v1/heartbeat
```

Beklenen: `{"nanosecond heartbeat": ...}`

> Windows'ta `curl` yoksa tarayıcıda `http://localhost:8100/api/v1/heartbeat` adresini açın.

**Ollama:**

```powershell
curl http://localhost:11434/api/tags
```

Beklenen: `{"models":[...]}` (başlangıçta boş liste olabilir)

### 4.4 Servisleri Durdurma

```powershell
docker compose down
```

Verileri silmeden durdurmak için yukarıdaki komutu kullanın. Docker volume'ları korunur.

Verileri de silmek için (temiz kurulum):

```powershell
docker compose down -v
```

### 4.5 GPU Desteği (Opsiyonel — Ollama + Embedding + Reranker)

NVIDIA GPU'nuz varsa, iki farklı katmanda hız kazanabilirsiniz:

1. `docker-compose.yml` içindeki Ollama servisinde GPU kullanımı açılarak yerel LLM performansı artırılır.
2. Python tarafındaki embedding ve reranker modelleri için CUDA destekli `torch` kurulup `EMBEDDING_DEVICE` / `RERANKER_DEVICE` ayarları `auto` veya `cuda` olarak bırakılır.

Ollama için örnek Docker ayarı:

```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

---

## 5. Ortam Değişkenleri Konfigürasyonu

### 5.1 `.env` Dosyası Oluşturma

```powershell
copy .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

### 5.2 Varsayılan Değerler

`.env.example` dosyası çalışır durumdaki varsayılan değerlerle gelir. Eğer Docker servislerini varsayılan portlarda çalıştırıyorsanız **`.env` dosyasını düzenlemenize gerek yoktur.**

Değiştirmek isteyebileceğiniz alanlar:

| Değişken | Varsayılan | Ne Zaman Değiştirmeli |
|----------|------------|----------------------|
| `POSTGRES_PASSWORD` | `postgres123` | Production ortamında güçlü şifre kullanın |
| `OPENAI_API_KEY` | *(boş)* | OpenAI yedek LLM kullanacaksanız ekleyin |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Farklı bir LLM denemek istiyorsanız |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | Farklı embedding modeli kullanacaksanız |
| `EMBEDDING_DEVICE` | `auto` | Embedding için `auto`, `cpu` veya `cuda` seçmek isterseniz |
| `RERANKER_DEVICE` | `auto` | Reranker için `auto`, `cpu` veya `cuda` seçmek isterseniz |
| `AUTH_OTP_TTL_MINUTES` | `10` | OTP süresini değiştirmek isterseniz |
| `AUTH_SESSION_TTL_HOURS` | `12` | Doğrulama oturum süresini değiştirmek isterseniz |
| `SLACK_BOT_TOKEN` | *(boş)* | Slack entegrasyonu için gerekli |

### 5.3 Konfigürasyon Doğrulama

```powershell
python -c "
from src.core.config import settings
print(f'PostgreSQL:  {settings.postgres.host}:{settings.postgres.port}')
print(f'Redis:       {settings.redis.host}:{settings.redis.port}')
print(f'ChromaDB:    {settings.chroma.url}')
print(f'Ollama:      {settings.ollama.host}')
print(f'Embedding:   {settings.embedding.model}')
print(f'Emb Device:  {settings.embedding.device}')
print(f'Reranker:    {settings.reranker.model}')
print(f'Rer Device:  {settings.reranker.device}')
print(f'RAG Chunk:   {settings.rag.chunk_size} / {settings.rag.chunk_overlap}')
"
```

---

## 6. Veritabanı Migration

PostgreSQL tabloları Alembic migration'ları ile yönetilir. **Tabloları veritabanına eklemek** için aşağıdaki adımları uygulayın.

**Ön koşul:** Docker servisleri çalışıyor olmalı (`docker compose up -d`). PostgreSQL konteyneri ayaktayken migration çalıştırılır.

### 6.1 Tabloları Oluşturma (Migration Uygulama)

```powershell
python -m alembic upgrade head
```

Bu komut `migrations/` klasöründeki migration dosyalarını sırayla uygulayarak tüm tabloları (students, courses, tuition, scholarships, otp_codes, announcements, agent_registry, query_logs vb.) veritabanında oluşturur.

### 6.2 Tabloların Oluştuğunu Doğrulama

Tabloların gerçekten oluştuğunu görmek için:

```powershell
docker exec uni_postgres psql -U postgres -d university_support -c "\dt"
```

Çıktıda `students`, `courses`, `tuition`, `announcements`, `query_logs` vb. tablolar listelenmelidir.

### 6.3 Migration Durumunu Kontrol Etme

```powershell
python -m alembic current
```

### 6.4 Yeni Migration Oluşturma (Model Değişikliği Sonrası)

```powershell
python -m alembic revision --autogenerate -m "açıklama"
```

### 6.5 Son Migration'ı Geri Alma

```powershell
python -m alembic downgrade -1
```

---

## 7. AI Modellerinin İndirilmesi

Proje 3 farklı AI modeli kullanır. Bu modeller ilk kullanımda otomatik indirilir, ancak önceden indirmek daha iyi bir deneyim sağlar.

### 7.1 Embedding Modeli — BAAI/bge-m3

**Boyut:** ~2.2 GB  
**Kaynak:** HuggingFace  
**İndirme:** İlk `embed_texts()` çağrısında otomatik indirilir.

Önceden indirmek için:

```powershell
python -c "
from sentence_transformers import SentenceTransformer
print('BAAI/bge-m3 indiriliyor...')
model = SentenceTransformer('BAAI/bge-m3')
print(f'Tamamlandi! Boyut: {model.get_sentence_embedding_dimension()}D')
"
```

Beklenen çıktı:

```
BAAI/bge-m3 indiriliyor...
Tamamlandi! Boyut: 1024D
```

**İndirme konumu:** `~/.cache/huggingface/hub/models--BAAI--bge-m3/`

### 7.2 Cross-Encoder Reranker — seroe/bge-reranker-v2-m3-turkish-triplet

**Boyut:** ~1.1 GB  
**Kaynak:** HuggingFace  
**İndirme:** İlk `rerank()` çağrısında otomatik indirilir.

Önceden indirmek için:

```powershell
python -c "
from sentence_transformers import CrossEncoder
print('Reranker indiriliyor...')
model = CrossEncoder('seroe/bge-reranker-v2-m3-turkish-triplet', max_length=512)
print('Tamamlandi!')
"
```

**İndirme konumu:** `~/.cache/huggingface/hub/models--seroe--bge-reranker-v2-m3-turkish-triplet/`

### 7.3 LLM — Qwen2.5:7B (Ollama)

**Boyut:** ~4.7 GB  
**Kaynak:** Ollama model registry  
**Gereksinim:** Ollama Docker konteynerinin çalışıyor olması

```powershell
docker exec uni_ollama ollama pull qwen2.5:7b
```

İndirme tamamlandığını doğrulama:

```powershell
docker exec uni_ollama ollama list
```

Beklenen çıktıda `qwen2.5:7b` modelini görmelisiniz.

> **Not:** LLM, FAZ 2 (doğal dilde cevap üretme) için gereklidir. Sadece RAG pipeline (indeksleme + arama) çalıştırmak için LLM'e ihtiyaç yoktur.

### 7.4 Tüm Modelleri Tek Seferde İndirme

```powershell
# 1) Embedding modeli
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3'); print('Embedding OK')"

# 2) Reranker modeli
python -c "from sentence_transformers import CrossEncoder; CrossEncoder('seroe/bge-reranker-v2-m3-turkish-triplet', max_length=512); print('Reranker OK')"

# 3) LLM (Ollama konteynerinin çalışıyor olması gerekir)
docker exec uni_ollama ollama pull qwen2.5:7b
```

---

## 8. RAG Pipeline — Doküman İndeksleme

RAG sistemi çalışabilmesi için kaynak dokümanların vektörize edilip ChromaDB'ye indekslenmesi gerekir.

### 8.1 Ön Koşullar

- [x] Python venv aktif
- [x] ChromaDB Docker konteynerı çalışıyor (`docker compose ps` ile kontrol edin)
- [x] Kaynak dokümanlar mevcut (`data/raw/student_affairs/` klasörü)

### 8.2 İndeksleme

```powershell
python scripts/index_documents.py --reindex
```

**Parametreler:**

| Parametre | Varsayılan | Açıklama |
|-----------|------------|----------|
| `--source` | `data/raw/student_affairs` | Kaynak doküman klasörü |
| `--chunk-size` | `1024` | Chunk boyutu (karakter) |
| `--chunk-overlap` | `128` | Chunk örtüşmesi (karakter) |
| `--collection` | *(opsiyonel)* | Elle koleksiyon adı verir; verilmezse kaynak klasörden dinamik çözülür |
| `--reindex` | `false` | Mevcut koleksiyonu silip yeniden oluştur |
| `--test-query` | *(yok)* | İndeksleme sonrası test sorgusu |
| `--chroma-url` | Config'den okunur | ChromaDB URL override |

**Beklenen çıktı:**

```
==================================================
🚀 RAG İndeksleme Pipeline
==================================================
   Kaynak:        .../data/raw/student_affairs
   Chunk boyutu:  1024
   Chunk örtüşme: 128
   Koleksiyon:    student_affairs_docs
   Yeniden oluş:  Evet
==================================================
[INFO] 198 dosya yüklendi
[INFO] 5303 chunk oluşturuldu
[INFO] Embedding üretimi başladı...
[INFO] ChromaDB'ye indeksleniyor...
✅ İndeksleme tamamlandı!
```

> **Süre:** İlk indeksleme model indirme ve cihaz durumuna göre ciddi ölçüde değişir. CPU ağırlıklı ilk çalıştırma dakikalar sürebilir; GPU etkin ve model cache hazır olduğunda süre belirgin biçimde azalır.

**Çok departmanlı davranış:**
- `data/raw/student_affairs` → `student_affairs_docs`
- `data/raw/academic_programs` → `academic_programs_docs`
- `data/raw/finance` → `finance_docs`

İsterseniz bu çözümü override ederek `--collection` ile özel bir koleksiyon adı da verebilirsiniz.

### 8.3 Artımlı İndeksleme (İdempotent)

`--reindex` flag'i olmadan çalıştırıldığında, pipeline **upsert** kullanır — aynı belge tekrar eklenmez, sadece değişenler güncellenir:

```powershell
python scripts/index_documents.py
```

Bu, hash tabanlı chunk ID'leri sayesinde mümkündür: aynı kaynak dosya + aynı içerik her zaman aynı ID üretir.

### 8.4 Doküman Kaydı

Her indeksleme sonrası `data/metadata/doc_registry.json` otomatik olarak üretilir. İndekslenen tüm dokümanların envanterini tutar (dosya adı, kategori, chunk sayısı, içerik hash'i).

### 8.5 İndeksleme Sonrası Doğrulama

İndekslemenin başarılı olduğunu test sorgusu ile doğrulayın:

```powershell
python scripts/index_documents.py --test-query "ÇAP başvurusu için gereken not ortalaması"
```

Veya direkt ChromaDB sorgusu:

```powershell
python scripts/query_db.py "ÇAP başvurusu için gereken not ortalaması" --top-k 3
```

---

## 9. Testleri Çalıştırma

### 9.1 Tüm Testler

```powershell
python -m pytest tests/ -v --tb=short
```

**Beklenen çıktı:**

```
tests/unit/test_config.py::TestDepartmentEnum::test_department_values PASSED
...
tests/unit/test_retriever.py::TestQueryCache::test_different_keys_independent PASSED
==================== 206 passed ====================
```

> **Not:** `tests/` tüm alt dizinleri kapsar. ChromaDB çalışmıyorsa integration testler otomatik atlanır.

### 9.2 Sadece Unit Testler

```powershell
python -m pytest tests/unit/ -v --tb=short
```

### 9.3 Belirli Bir Test Dosyası

```powershell
# Sadece RAG retriever testleri
python -m pytest tests/unit/test_retriever.py -v

# Sadece query preprocessor testleri
python -m pytest tests/unit/test_query_preprocessor.py -v

# Sadece embedder testleri
python -m pytest tests/unit/test_embedder.py -v

# Sadece reranker testleri
python -m pytest tests/unit/test_reranker.py -v
```

### 9.4 Belirli Bir Test Sınıfı veya Fonksiyonu

```powershell
# Belirli bir sınıf
python -m pytest tests/unit/test_retriever.py::TestApplySourceRelevance -v

# Belirli bir test fonksiyonu
python -m pytest tests/unit/test_query_preprocessor.py::TestCompoundWordSplitting::test_ciftanadal_splits -v
```

### 9.5 Coverage Raporu

```powershell
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
```

HTML raporu `htmlcov/index.html` dosyasında oluşturulur. Tarayıcıda açarak detaylı coverage bilgisine ulaşabilirsiniz.

### 9.6 Integration Testler (ChromaDB Gerekli)

```powershell
python -m pytest tests/integration/ -v --tb=short
```

Bu testler gerçek ChromaDB ve AI modelleri kullanır. ChromaDB çalışmıyorsa otomatik atlanır.

**Marker bazlı kullanım:**

```powershell
# Hızlı bağlantı ve koleksiyon kontrolleri
python -m pytest tests/integration/ -m smoke -v --tb=short

# Gerçek model kullanan testler
python -m pytest tests/integration/ -m model -v --tb=short

# Uzun süren kalite testleri
python -m pytest tests/integration/ -m slow -v --tb=short
```

### 9.7 Test Dosyaları ve Kapsamları

**Unit Testler (Docker gerektirmez):**

| Test Dosyası | Test Sayısı | Kapsam |
|-------------|:-----------:|--------|
| `test_config.py` | 10 | Enum sabitleri, eşik değerleri |
| `test_connection.py` | 8 | DB connection, session yönetimi |
| `test_models.py` | 7 | ORM modelleri, JSONB ilişkileri |
| `test_schemas.py` | 16 | Pydantic validasyonları |
| `test_rag_pipeline.py` | 29 | DocumentLoader, TextPreprocessor, TextChunker, vb. |
| `test_query_preprocessor.py` | 22 | Bileşik kelime, sinonim, sorgu tipi |
| `test_embedder.py` | 18 | Model algılama, prefix, vektör üretimi, cihaz çözümü |
| `test_reranker.py` | 16 | Cross-encoder sıralama, durum bayrağı, cihaz çözümü |
| `test_retriever.py` | 29 | BM25, departman planlama, source relevance, dedup, cache |
| `test_llm_service.py` | 7 | Fallback, retry ve JSON formasyonu orkestrasyonu |
| `test_ollama_client.py` | 9 | Yerel Ollama REST API işlemleri, streaming |
| `test_openai_client.py` | 11 | Yedek OpenAI ağ bağlantısı testleri, streaming |

**Integration Testler (ChromaDB gerekli):**

| Test Dosyası | Test Sayısı | Kapsam |
|-------------|:-----------:|--------|
| `test_rag_retrieval.py` | 17 | ChromaDB bağlantı, koleksiyon, hibrit arama, reranker doğrulaması, cache, Precision@3 |

### 9.8 RAG Değerlendirme Raporu

Otomatik Precision@k ölçümü ve rapor üretimi:

```powershell
python scripts/evaluate_rag.py
```

Bu komut:
- Ana soru havuzundan departman etiketlerine göre filtreleyerek testleri çalıştırır
- Precision@1, @3, @5 hesaplar
- `docs/rag_evaluation_report.md` ve `.json` dosyalarını üretir

**Güncel soru havuzu:** `data/test/rag_test_questions.json`
- Toplam 30 soru içerir
- 20 soru `student_affairs`
- 10 soru `academic_programs`
- Integration fixture'ları şimdilik yalnızca `student_affairs` alt kümesini kullanır

---

## 10. RAG Arama Testleri

Bu testler gerçek modelleri kullanarak canlı arama yapar. ChromaDB'nin çalışıyor ve indekslenmiş olması gerekir.

### 10.1 Ön Koşullar

- [x] ChromaDB Docker konteynerı çalışıyor
- [x] İndeksleme tamamlanmış (Bölüm 8)
- [x] Embedding modeli indirilmiş (ilk çalıştırmada otomatik)

### 10.2 Hibrit Arama Testi (BM25 + Semantic + Cross-Encoder)

```powershell
python scripts/test_hybrid_search.py "ÇAP başvurusu için gereken not ortalaması kaçtır"
```

**Departman hedefli örnekler:**

```powershell
python scripts/test_hybrid_search.py "Müfredat nedir?" --department academic_programs
python scripts/query_db.py "Harç dekontumu nasıl alırım?" --department finance
python scripts/evaluate_rag.py --department academic_programs
```

**Ek parametreler:**

```powershell
# Tam metin gösterimi
python scripts/test_hybrid_search.py "kayıt dondurma süresi ne kadar" --full

# Ağırlık özelleştirme
python scripts/test_hybrid_search.py "staj süresi" --bm25-weight 0.6 --vector-weight 0.4

# Top-K sayısını değiştirme
python scripts/test_hybrid_search.py "yan dal başvurusu" --top-k 10
```

**Beklenen çıktı:**

```
══════════════════════════════════════════
  Hibrit Arama Testi v3.0
══════════════════════════════════════════
  Sorgu:     ÇAP başvurusu için gereken not ortalaması kaçtır
  BM25:      0.40   Vektör: 0.60
══════════════════════════════════════════

[1] Skor: 0.9602 | Kaynak: yonerge_cift_anadal_yandal.pdf
    MADDE 7 — (1) Çift ana dal programına başvurabilmek için...

[2] Skor: 0.8841 | Kaynak: yonerge_cift_anadal_yandal.pdf
    ...
```

### 10.3 Doğrudan Semantik Sorgu (ChromaDB)

Pipeline'ı bypass ederek sadece ChromaDB üzerinde embedding tabanlı arama:

```powershell
python scripts/query_db.py "Ders kaydı nasıl yapılır?" --top-k 5
```

### 10.4 Koleksiyon Karşılaştırma

Farklı chunk boyutlarının arama kalitesine etkisini görmek için:

```powershell
python scripts/compare_collections.py "Kayıt dondurma nasıl yapılır"
```

---

## 11. Sentetik Öğrenci Verisi Yükleme (Opsiyonel)

Test senaryolarında gerçek veriler yerine örnek (sentetik) öğrenci verisi kullanmak istersen, `scripts/seed_synthetic_data.py` betiği ile PostgreSQL'e hazır kayıtlar ekleyebilirsin. Bu betik yalnızca tablolar **boşsa** veri ekler; aynı betiği ikinci kez çalıştırmak veriyi çoğaltmaz.

### 11.1 Ön Koşullar

- Docker servisleri çalışıyor olmalı (`docker compose up -d`).
- Migration uygulanmış olmalı (`python -m alembic upgrade head`).
- Sanal ortam aktif olmalı.

### 11.2 Sentetik Veriyi Eklemek

```powershell
cd C:\Users\tubas\Desktop\university_support_system
venv\Scripts\activate
docker compose up -d
python -m alembic upgrade head
python scripts/seed_synthetic_data.py
```

Başarılı çalıştırmada aşağıdaki mesajı görürsün:

```text
Synthetic student-focused test data inserted successfully.
```

Betik şu tabloları doldurur:

- `students` → Eğitim, Fen-Edebiyat ve Mühendislik fakültelerinden 9 öğrenci
- `courses` → Her bölüm için örnek dersler
- `student_courses` → Geçmişte alınan ve şu an alınan dersler (not ve durumlarıyla)
- `course_registration_periods` → 2025-Güz ve 2026-Bahar kayıt dönemleri
- `tuition`, `payments`, `installments` → Farklı harç ve taksit senaryoları
- `available_scholarships`, `scholarships`, `scholarship_applications` → Örnek burs ve başvuru kayıtları

Aynı komutu tekrar çalıştırırsan, tablolar boş değilse şu mesajı yazar ve veri eklemez:

```text
Synthetic seed skipped: students or courses already contain data.
```

### 11.3 Eklenen Veriyi Kontrol Etmek

Örneğin eklenen öğrencileri görmek için:

```powershell
docker exec uni_postgres psql -U postgres -d university_support -c "SELECT id, student_id, full_name, faculty, department, class_year, gpa FROM students ORDER BY id;"
```

---

## 12. Uygulamayı Başlatma

> **Not:** FAZ 2 (LLM entegrasyonu) tamamlanmıştır. Mevcut repo içinde artık çalıştırılabilir bir FastAPI uygulama girişi vardır: `src.api.main:app`. `src/slack/` ve benzeri bazı yüzeyler hâlâ iskelet durumundadır.

### 12.1 Mevcut Repo İçin Çalıştırılabilir Akış

```powershell
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

python scripts/index_documents.py --reindex
python -m pytest tests/unit/ -v --tb=short
python -m pytest tests/integration/ -v --tb=short
python scripts/test_hybrid_search.py "ÇAP başvurusu için gereken not ortalaması kaçtır"
python scripts/evaluate_rag.py
```

### 12.2 Tüm Servislerin Çalışma Sırası

Mevcut repo kapsamı için önerilen sıra:

```
1. docker compose up -d              # Altyapı servisleri
2. python -m alembic upgrade head    # Veritabanı tabloları
3. python scripts/index_documents.py # RAG indeksleme (ilk sefer veya güncelleme)
4. python -m pytest ...              # Test ve doğrulama
5. python scripts/evaluate_rag.py    # RAG kalite raporu
```

---

## 13. Makefile Kısayolları

Sık kullanılan komutlar `Makefile` ile kısayollara bağlanmıştır:

| Komut | Açıklama |
|-------|----------|
| `make setup` | İlk kurulum (venv + bağımlılıklar + .env kopyalama) |
| `make install` | Geliştirme bağımlılıklarını kur |
| `make install-prod` | Sadece runtime bağımlılıklarını kur |
| `make test` | Tüm testleri çalıştır |
| `make test-unit` | Sadece unit testleri çalıştır |
| `make test-cov` | Coverage ile testleri çalıştır |
| `make lint` | Kod kalitesi kontrolü (flake8 + mypy) |
| `make format` | Kodu formatla (black + isort) |
| `make db-migrate` | Veritabanı migration uygula |
| `make db-revision MSG="açıklama"` | Yeni migration dosyası oluştur |
| `make docker-up` | Docker servisleri başlat |
| `make docker-down` | Docker servisleri durdur |
| `make docker-logs` | Docker loglarını göster |
| `make docker-restart` | Docker servisleri yeniden başlat |
| `make evaluate` | RAG değerlendirme raporu üret (ChromaDB gerekli) |
| `make clean` | Geçici dosyaları temizle (`__pycache__`, `.pytest_cache`, vb.) |

---

## 13. Sorun Giderme

### 13.1 `ModuleNotFoundError: No module named 'src'`

**Neden:** Python, `src` modülünü bulamıyor. Sanal ortam aktif değil veya yanlış dizindesiniz.

**Çözüm:**

```powershell
# Doğru dizinde olduğunuzdan emin olun
cd university_support_system

# venv aktif mi kontrol edin (prompt'ta (venv) olmalı)
venv\Scripts\activate

# Yeniden deneyin
python -m pytest tests/ -v
```

### 13.2 `ConnectionRefusedError` (ChromaDB / PostgreSQL / Redis)

**Neden:** Docker servisleri çalışmıyor.

**Çözüm:**

```powershell
docker compose ps                  # Durumu kontrol et
docker compose up -d               # Servisleri başlat
docker compose logs chromadb       # ChromaDB loglarını kontrol et
```

### 13.3 İndeksleme sırasında `ChromaDB collection not found`

**Neden:** ChromaDB konteyneri yeniden oluşturulmuş, veriler silinmiş.

**Çözüm:**

```powershell
python scripts/index_documents.py --reindex
```

### 13.4 `torch.cuda.OutOfMemoryError` veya RAM yetersizliği

**Neden:** Embedding modeli veya LLM için yeterli bellek yok.

**Çözüm:**
- Diğer uygulamaları kapatın
- Docker Desktop'ın bellek limitini artırın (Settings → Resources → Memory)
- GPU yoksa CPU modunda çalıştırın (otomatik fallback yapar)

### 13.5 Model İndirme Hataları (HuggingFace Timeout)

**Neden:** HuggingFace sunucularına erişim sorunu veya zaman aşımı.

**Çözüm:**

```powershell
# HuggingFace cache'ini temizleyip tekrar deneyin
pip install huggingface_hub
huggingface-cli cache info

# Proxy arkasındaysanız
set HTTPS_PROXY=http://proxy:port
set HF_HUB_DOWNLOAD_TIMEOUT=300
```

### 13.6 `UnicodeDecodeError` — Türkçe Karakter Sorunları

**Neden:** Windows terminalinde UTF-8 encoding aktif değil.

**Çözüm:**

```powershell
# PowerShell'de UTF-8 etkinleştirme
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

# Kalıcı çözüm: Windows Terminal kullanın (varsayılan olarak UTF-8 destekler)
```

### 13.7 `alembic.util.exc.CommandError: Can't locate revision`

**Neden:** Migration dosyaları ile veritabanı durumu uyumsuz.

**Çözüm:**

```powershell
# Migration durumunu kontrol et
python -m alembic current

# Temiz başlangıç (veriyi siler!)
python -m alembic downgrade base
python -m alembic upgrade head
```

### 13.8 Testler Geçiyor Ama `Command failed to spawn: Aborted`

**Neden:** Cursor IDE terminal limitleri veya shell encoding sorunu.

**Çözüm:** Testleri doğrudan Windows Terminal veya PowerShell'den çalıştırın:

```powershell
cd "C:\Users\...\university_support_system\university_support_system"
venv\Scripts\activate
python -m pytest tests/ -v --tb=short
```

---

## 14. Ortam Değişkenleri Referansı

Tüm konfigürasyon `src/core/config.py` içinde Pydantic Settings v2 ile tanımlıdır. `.env` dosyası veya sistem ortam değişkenleri ile override edilebilir.

### PostgreSQL

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `POSTGRES_HOST` | `localhost` | PostgreSQL sunucu adresi |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_DB` | `university_support` | Veritabanı adı |
| `POSTGRES_USER` | `postgres` | Kullanıcı adı |
| `POSTGRES_PASSWORD` | `postgres123` | Şifre |

### Redis

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `REDIS_HOST` | `localhost` | Redis sunucu adresi |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis veritabanı numarası |
| `USE_REDIS` | `true` | Redis aktif/pasif |

### ChromaDB

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `CHROMA_HOST` | `localhost` | ChromaDB sunucu adresi |
| `CHROMA_PORT` | `8100` | ChromaDB port |

### Embedding Modeli

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | HuggingFace model adı (1024-D, 100+ dil) |
| `EMBEDDING_DEVICE` | `auto` | `auto`, `cpu` veya `cuda`; `auto` CUDA varsa GPU kullanır |

### Cross-Encoder Reranker

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `RERANKER_MODEL` | `seroe/bge-reranker-v2-m3-turkish-triplet` | HuggingFace reranker model adı |
| `RERANKER_DEVICE` | `auto` | `auto`, `cpu` veya `cuda`; embedding cihazından bağımsız seçilebilir |
| `RERANKER_MAX_LENGTH` | `512` | Maksimum token uzunluğu |
| `RERANKER_BATCH_SIZE` | `16` | Batch boyutu |

### Auth / OTP

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `AUTH_OTP_LENGTH` | `6` | Üretilecek OTP kodu uzunluğu |
| `AUTH_OTP_TTL_MINUTES` | `10` | OTP geçerlilik süresi |
| `AUTH_MAX_FAILED_ATTEMPTS` | `5` | Başarısız deneme üst sınırı |
| `AUTH_SESSION_TTL_HOURS` | `12` | Doğrulama oturumu süresi |

### RAG Pipeline

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `RAG_CHUNK_SIZE` | `1024` | Chunk boyutu (karakter) |
| `RAG_CHUNK_OVERLAP` | `128` | Chunk örtüşmesi (karakter) |
| `RAG_TOP_K` | `5` | Arama sonucu sayısı |
| `RAG_MIN_SIMILARITY` | `0.0` | Minimum benzerlik eşiği (0 = filtre yok) |

### Ollama (LLM)

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API adresi |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Kullanılacak LLM modeli |
| `OLLAMA_TIMEOUT` | `30` | İstek zaman aşımı (saniye) |
| `OLLAMA_MAX_RETRIES` | `3` | Maksimum yeniden deneme |

### OpenAI (Yedek LLM)

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `OPENAI_API_KEY` | *(boş)* | API anahtarı (opsiyonel) |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model adı |

### Slack

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `SLACK_BOT_TOKEN` | *(boş)* | Slack bot token'ı |
| `SLACK_SIGNING_SECRET` | *(boş)* | Slack signing secret |
| `SLACK_APP_TOKEN` | *(boş)* | Slack app-level token |

### Sunucu

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `SERVER_HOST` | `0.0.0.0` | Dinlenecek adres |
| `SERVER_PORT` | `8000` | Dinlenecek port |
| `SERVER_DEBUG` | `true` | Debug modu |
| `SERVER_LOG_LEVEL` | `INFO` | Log seviyesi |

---

## Hızlı Başlangıç Özeti (TL;DR)

Tüm adımları sırasıyla çalıştırmak için:

```powershell
# 1. Sanal ortam
python -m venv venv
venv\Scripts\activate

# 2. Bağımlılıklar
pip install -r requirements-dev.txt

# 3. Ortam değişkenleri
copy .env.example .env

# 4. Docker servisleri
docker compose up -d

# 5. Veritabanı
python -m alembic upgrade head

# 6. AI Modelleri (opsiyonel — ilk kullanımda otomatik iner)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
python -c "from sentence_transformers import CrossEncoder; CrossEncoder('seroe/bge-reranker-v2-m3-turkish-triplet', max_length=512)"
docker exec uni_ollama ollama pull qwen2.5:7b

# 7. RAG İndeksleme
python scripts/index_documents.py --reindex

# 8. Unit testler (206 test, Docker gerektirmez)
python -m pytest tests/unit/ -v --tb=short

# 9. Integration testler (20 test, ChromaDB gerekli)
python -m pytest tests/integration/ -v --tb=short

# 10. Arama testi
python scripts/test_hybrid_search.py "ÇAP başvurusu için gereken not ortalaması kaçtır"

# 11. RAG değerlendirme raporu üret
python scripts/evaluate_rag.py
```

---

*Bu rehber, projenin mevcut durumunu (FAZ 0 + FAZ 1 + FAZ 2 çekirdeği tamamlanmış, FAZ 3 için temel A2A/ajan/API iskeleti eklenmiş) yansıtmaktadır. Slack bot katmanı halen iskelet seviyesindedir.*

> Ek güncelleme: 8 Mart 2026 itibarıyla çok departmanlı koleksiyon yapısı, `EMBEDDING_DEVICE` / `RERANKER_DEVICE` ile cihaz seçimi, güncel test envanteri ve `academic_programs` akışı bu rehbere işlenmiştir. Üst başlıktaki tarih tarihsel kaldıysa güncel teknik durum için `docs/MART_2026_GUNCELLEME_NOTLARI.md` de birlikte okunmalıdır.
