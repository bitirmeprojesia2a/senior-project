# FAZ 0 — Kuruluş ve Ortak Altyapı: Teknik Dokümantasyon

**Proje:** Üniversite Kurumsal Destek Sistemi  
**Doküman Tarihi:** 25 Şubat 2026  
**Doküman Sürümü:** 2.1 (Doğrulanmış — 40/40 test geçti)  
**Yazar:** Geliştirme Ekibi  
**Durum:** ✅ Tamamlandı  

---

## 1. Amaç ve Kapsam

Bu doküman, projenin kuruluş fazında (FAZ 0) gerçekleştirilen **tüm** teknik çalışmaları detaylı olarak kayıt altına almaktadır. FAZ 0, projenin temelini oluşturan altyapı kararlarını, klasör organizasyonunu, veritabanı modellerini, ortak arayüz tanımlamalarını, test altyapısını ve kalite denetimi sürecini kapsamaktadır.

**Bu dokümanın hedef kitlesi:** Projeye yeni katılan geliştiriciler, tez danışmanı ve jüri üyeleri. Okuyan kişi hiçbir ön bilgi gerektirmeden tüm mimari kararları, teknik detayları ve akışları anlayabilmelidir.

**FAZ 0 kapsamında tamamlanan iş kalemleri:**
1. Teknoloji seçimleri ve gerekçeleri
2. Proje klasör yapısı tasarımı
3. Merkezi konfigürasyon sistemi (`Pydantic Settings v2`)
4. Uygulama sabitleri ve enum tanımlamaları
5. Veritabanı ORM modelleri (`SQLAlchemy 2.0`)
6. Veritabanı bağlantı yönetimi (lazy initialization)
7. Pydantic iş mantığı şemaları
8. A2A protokol entegrasyonu (`a2a-sdk`)
9. Docker Compose servis altyapısı
10. Migration sistemi (`Alembic`)
11. Test altyapısı ve fixture'lar (`pytest-asyncio`)
12. Kalite denetimi ve standart uyumluluk kontrolü

---

## 2. Prototipten Nihai Sisteme Geçiş Kararları

Prototip aşamasında kullanılan teknolojiler, test ve değerlendirme sonuçlarına dayanarak nihai sistem için güncellenmiştir.

| Bileşen | Prototip | Nihai Sistem | Geçiş Gerekçesi |
|---------|----------|-------------|-----------------|
| **Veritabanı** | SQLite | PostgreSQL 15 | SQLite tek kullanıcılı ortamda başarılıydı ancak eşzamanlı erişim, Row-Level Security (RLS) ve JSONB desteği için PostgreSQL'e geçildi. |
| **Gömme Modeli** | paraphrase-multilingual-MiniLM-L12-v2 | BERTurk (dbmdz/bert-base-turkish-cased) | 35GB Türkçe veriyle eğitilmiş BERTurk modeli Türkçe morfolojik yapıyı daha iyi yakalamaktadır. 768 boyutlu vektörler üretir. |
| **LLM** | Gemini/Claude API (bulut) | Qwen2.5:7B via Ollama (yerel) + OpenAI yedek | Maliyet etkinliği, veri gizliliği ve offline çalışma. 128K token bağlam penceresi. |
| **A2A Protokolü** | Elle yazılmış sınıflar | `a2a-sdk` (Google resmi SDK) | Kalite denetiminde elle yazılan A2A sınıflarının spec ile uyumsuz olduğu tespit edildi. Resmi SDK'ya geçildi. |
| **Kuyruk Sistemi** | InMemoryQueue | Redis 7 | Kalıcılık, öncelik kuyruğu, TTL yönetimi ve yatay ölçeklendirme. |
| **Migration** | Manuel tablo oluşturma | Alembic | Veritabanı şema değişikliklerinin versiyonlanması ve geri alınabilmesi. |
| **Konteyner** | Doğrudan kurulum | Docker Compose | Tüm servislerin tek komutla ayağa kaldırılması. |
| **Test** | Test altyapısı yok | pytest + coverage | Minimum %70 coverage hedefi. Async test desteği. |

---

## 3. Proje Klasör Yapısı

```
university_support_system/
├── src/                           # Tüm kaynak kod
│   ├── __init__.py                # Ana paket (versiyon: 1.0.0)
│   ├── core/                      # Konfigürasyon ve sabitler
│   │   ├── __init__.py            # Export: settings, Department, TaskType, ...
│   │   ├── config.py              # Merkezi ayar yönetimi (Pydantic Settings v2)
│   │   └── constants.py           # Enum sabitleri ve eşik değerleri
│   ├── db/                        # Veritabanı katmanı
│   │   ├── __init__.py            # Export: Base, get_session, init_engine, ...
│   │   ├── models.py              # SQLAlchemy ORM modelleri (15 tablo)
│   │   ├── schemas.py             # Pydantic request/response şemaları
│   │   └── connection.py          # Async engine, lazy init, session, health check
│   ├── a2a/                       # A2A protokol (a2a-sdk üzerinden, FAZ 2)
│   ├── agents/                    # Ajan implementasyonları
│   │   ├── finance/               # Finans: harç, burs, öğrenim ücreti
│   │   ├── it/                    # IT: teknik destek, e-posta, hesap
│   │   └── student/               # Öğrenci İşleri: ders, kayıt, not
│   ├── orchestrators/             # Ana ve departman orkestratörleri
│   ├── rag/                       # RAG pipeline
│   ├── llm/                       # LLM istemcileri (Ollama, OpenAI)
│   ├── routing/                   # Sorgu yönlendirme
│   ├── queue/                     # Redis görev kuyruğu
│   ├── cache/                     # Redis önbellekleme
│   ├── mcp/                       # MCP sunucu/istemci
│   ├── slack/                     # Slack bot
│   ├── api/                       # FastAPI gateway
│   └── security/                  # Güvenlik
├── tests/
│   ├── conftest.py                # Ortak fixture'lar
│   └── unit/
│       ├── test_config.py         # 10 test
│       ├── test_models.py         # 7 test
│       ├── test_schemas.py        # 15 test
│       └── test_connection.py     # 8 test
├── data/raw/{finance,it_support,student_affairs}/
├── migrations/                    # Alembic
├── docker-compose.yml
├── requirements.txt               # Runtime paketler (pinlenmiş sürümler)
├── requirements-dev.txt           # Test + kalite araçları
├── pyproject.toml                 # Tool config
├── Makefile                       # Dev kısayolları
└── .env.example                   # Ortam değişkenleri şablonu
```

---

## 4. Konfigürasyon Sistemi (`src/core/config.py`)

### 4.1 Mimari Karar: Pydantic Settings v2

Konfigürasyon yönetimi için **Pydantic Settings v2** seçilmiştir. Bu kütüphane:
- **Tip güvenliği** sağlar (string `port` yazmaya çalışırsanız derleme zamanında hata alırsınız)
- **Ortam değişkenlerini** otomatik okur
- **Doğrulama** yapar (port aralığı, URL formatı vb.)
- **Varsayılan değerler** ile geliştirme kolaylığı sunar

### 4.2 `env_prefix` Pattern'i — Ortam Değişkeni Eşleştirme

Her alt ayar sınıfı kendi `env_prefix`'ini tanımlar. Bu, pydantic-settings v2'nin **önerilen** kullanım biçimidir:

```python
class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_", extra="ignore")
    host: str = "localhost"   # ← .env'deki POSTGRES_HOST otomatik okunur
    port: int = 5432          # ← .env'deki POSTGRES_PORT otomatik okunur
```

**Mekanizma:** `env_prefix="POSTGRES_"` + alan adı `host` = ortam değişkeni `POSTGRES_HOST`. Pydantic bu eşleştirmeyi otomatik yapar.

### 4.3 Konfigürasyon Yükleme Akışı

```
┌──────────────────────────────────────────────────────────────┐
│ Uygulama Başlangıcı                                         │
│                                                              │
│  1. Python "from src.core.config import settings" çalıştırır│
│  2. Settings() constructor'ı tetiklenir                      │
│  3. Pydantic Settings .env dosyasını okur (env_file=".env") │
│  4. Her alt sınıf kendi env_prefix'ine göre değer arar:     │
│     ● POSTGRES_HOST → PostgresSettings.host                 │
│     ● REDIS_PORT → RedisSettings.port                       │
│     ● OLLAMA_MODEL → OllamaSettings.model                   │
│     ● EMBEDDING_MODEL → EmbeddingSettings.model             │
│     ● SERVER_DEBUG → ServerSettings.debug                    │
│  5. Bulunamazsa varsayılan değer kullanılır                  │
│  6. Tip dönüşümü otomatik yapılır (str→int, str→bool)       │
│  7. @computed_field URL'leri otomatik hesaplar               │
│  8. settings singleton instance tüm modüllerden erişilebilir │
└──────────────────────────────────────────────────────────────┘
```

### 4.4 Alt Konfigürasyon Sınıfları — Detay

| Sınıf | `env_prefix` | Alanlar | Hesaplanan Alanlar | Açıklama |
|-------|-------------|---------|-------------------|----------|
| `PostgresSettings` | `POSTGRES_` | `host`, `port`, `db`, `user`, `password`, `pool_size`, `max_overflow` | `async_url`, `sync_url` | asyncpg ve psycopg2 bağlantı URL'leri `@computed_field` ile otomatik oluşturulur |
| `RedisSettings` | `REDIS_` | `host`, `port`, `db` | `url` | `enabled` alanı `validation_alias="USE_REDIS"` ile ayrıca eşleştirilir |
| `OllamaSettings` | `OLLAMA_` | `host`, `model`, `timeout`, `max_retries` | — | Yerel LLM servisi. Hata dayanıklılığı: 30s timeout, 3 retry |
| `OpenAISettings` | `OPENAI_` | `api_key`, `model` | — | `is_available` property'si API anahtarı kontrolü yapar |
| `ChromaSettings` | `CHROMA_` | `host`, `port` | `url` | Docker'da port `8100` (varsayılan 8000 ile çakışma önlendi) |
| `EmbeddingSettings` | `EMBEDDING_` | `model`, `dimension` | — | BERTurk modeli, 768 boyutlu vektör |
| `RAGSettings` | `RAG_` | `chunk_size`, `chunk_overlap`, `top_k`, `min_similarity` | — | RAG pipeline parametreleri |
| `SlackSettings` | `SLACK_` | `bot_token`, `signing_secret`, `app_token` | — | `is_configured` property'si tüm ayarları kontrol eder |
| `ServerSettings` | `SERVER_` | `host`, `port`, `debug`, `log_level` | — | FastAPI sunucu ayarları |

### 4.5 Tasarım Kararları

1. **`load_dotenv()` kullanılmıyor:** Pydantic Settings, `env_file=".env"` parametresi ile `.env` dosyasını kendi okuyor. `python-dotenv` runtime dependency olarak kalıyor çünkü pydantic-settings bunu alt katmanda kullanıyor.

2. **`@computed_field` vs `@property`:** URL'ler (`async_url`, `sync_url`, `url`) `@computed_field` ile tanımlanmıştır. Sebebi: Pydantic v2'de `@property` alanları `model_dump()` ve JSON serialization'da **görünmez**. `@computed_field` ise serialization'a dahil edilir — bu, config'i loglarken veya debug ederken kritiktir.

3. **`validation_alias`:** `RedisSettings.enabled` alanı `validation_alias="USE_REDIS"` kullanır. Bu, `env_prefix`'ten bağımsız olarak `USE_REDIS` ortam değişkenini doğrudan arar. Normal `alias` kullanılsaydı prefix ile birleşerek `REDIS_USE_REDIS` aranırdı — bu hatalı olurdu.

### 4.6 Ortam Değişkenleri Tam Listesi (`.env.example`)

| Değişken | Varsayılan | Açıklama |
|----------|-----------|----------|
| `POSTGRES_HOST` | `localhost` | PostgreSQL sunucu adresi |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_DB` | `university_support` | Veritabanı adı |
| `POSTGRES_USER` | `postgres` | Kullanıcı adı |
| `POSTGRES_PASSWORD` | `postgres123` | Şifre |
| `REDIS_HOST` | `localhost` | Redis sunucu adresi |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis veritabanı numarası |
| `USE_REDIS` | `true` | Redis aktif/pasif |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Kullanılacak LLM modeli |
| `OPENAI_API_KEY` | *(boş)* | OpenAI API anahtarı (opsiyonel) |
| `OPENAI_MODEL` | `gpt-4o-mini` | Yedek LLM modeli |
| `CHROMA_HOST` | `localhost` | ChromaDB sunucu adresi |
| `CHROMA_PORT` | `8100` | ChromaDB port |
| `EMBEDDING_MODEL` | `dbmdz/bert-base-turkish-cased` | Gömme modeli |
| `RAG_CHUNK_SIZE` | `512` | Doküman parçalama boyutu (karakter) |
| `RAG_CHUNK_OVERLAP` | `64` | Parçalar arası örtüşme |
| `RAG_TOP_K` | `5` | Döndürülecek sonuç sayısı |
| `RAG_MIN_SIMILARITY` | `0.6` | Minimum benzerlik eşiği (0.0–1.0) |
| `SERVER_HOST` | `0.0.0.0` | Sunucu dinleme adresi |
| `SERVER_PORT` | `8000` | Sunucu port |
| `SERVER_DEBUG` | `true` | Debug modu |
| `SERVER_LOG_LEVEL` | `INFO` | Log seviyesi |
| `SLACK_BOT_TOKEN` | *(boş)* | Slack bot token |
| `SLACK_SIGNING_SECRET` | *(boş)* | Slack signing secret |
| `SLACK_APP_TOKEN` | *(boş)* | Slack app-level token |

---

## 5. Uygulama Sabitleri (`src/core/constants.py`)

### 5.1 Enum Tanımlamaları

Tüm sabit değerler Python `Enum` sınıfları olarak tanımlanmıştır. `str, Enum` kalıtımı kullanılarak enum değerleri doğrudan JSON serialization'da kullanılabilir hale getirilmiştir.

#### Department — Sistem Departmanları

```python
class Department(str, Enum):
    FINANCE = "finance"              # Finans departmanı
    IT = "it"                        # Bilgi İşlem departmanı
    STUDENT_AFFAIRS = "student_affairs"  # Öğrenci İşleri departmanı
```

`display_name` property'si ile Türkçe görüntüleme adı döndürülür: `Department.FINANCE.display_name → "Finans"`.

#### TaskType — Görev Tipleri (12 tip)

| Departman | Görev Tipleri |
|-----------|--------------|
| Finans | `tuition_query` (harç), `scholarship_query` (burs), `payment_query` (ödeme) |
| IT | `tech_support` (teknik), `email_support` (e-posta), `account_support` (hesap) |
| Öğrenci İşleri | `course_query` (ders), `registration_query` (kayıt), `academic_query` (akademik) |
| Genel | `procedure_query` (RAG), `data_query` (SQL), `hybrid_query` (RAG+SQL) |

#### InternalTaskStatus — İç Süreç Durumları

```
routing → queued → retrying → timeout
```

**Kritik NOT:** A2A protokolünün resmi `TaskState` enum'u (`submitted`, `working`, `completed`, `failed`, `canceled`, `input-required`) `a2a-sdk` paketinden gelir. `InternalTaskStatus` yalnızca iç süreçler (yönlendirme, kuyruk yönetimi) için tanımlanmıştır ve A2A spec'ini **genişletmez**.

#### Diğer Enum'lar

| Enum | Değerler | Kullanım |
|------|---------|----------|
| `RoutingStrategy` | `direct`, `parallel`, `sequential`, `clarification` | Sorgu yönlendirme stratejisi |
| `ConfidenceLevel` | `high` (>0.7), `medium` (0.4–0.7), `low` (<0.4) | Yönlendirme güven seviyesi |
| `AgentRole` | `main_orchestrator`, `department_orchestrator`, `specialist_agent` | Ajan rolleri |
| `Priority` | 1 (`LOW`) – 5 (`CRITICAL`) | Görev önceliklendirme |

### 5.2 Sabit Eşik Değerleri

```python
# Yönlendirme
ROUTING_HIGH_CONFIDENCE_THRESHOLD = 0.7   # Bu üstünde → doğrudan yönlendir
ROUTING_LOW_CONFIDENCE_THRESHOLD = 0.4    # Bu altında → netleştirme iste

# Kuyruk
QUEUE_MAX_RETRIES = 3                     # Başarısız görevde max deneme
QUEUE_TTL_SECONDS = 1800                  # Görev zaman aşımı (30 dk)
QUEUE_RETRY_DELAYS = [3, 10, 30]          # Kademeli bekleme (saniye)

# Cache
CACHE_DEFAULT_TTL = 300                   # Varsayılan cache süresi (5 dk)

# Performans hedefleri
RAG_RESPONSE_TIME_TARGET_MS = 100         # RAG sorgusu hedef
LLM_RESPONSE_TIME_TARGET_MS = 3000       # LLM yanıtı hedef
E2E_RESPONSE_TIME_TARGET_MS = 5000       # Uçtan uca hedef
```

---

## 6. Veritabanı Katmanı

### 6.1 ORM Modelleri (`src/db/models.py`)

#### 6.1.1 TimestampMixin — Otomatik Zaman Damgası

Tüm modellere `created_at` ve `updated_at` alanlarını ekleyen mixin sınıfıdır:

```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),   # PostgreSQL tarafında NOW() çalıştırılır
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=_utcnow,           # Python tarafında timezone-aware UTC üretilir
        nullable=False
    )
```

**`server_default=func.now()` vs `default=_utcnow`:** `server_default` veritabanı sunucusunun kendi saatini kullanır (INSERT sırasında SQL `DEFAULT NOW()` çalışır). `onupdate=_utcnow` ise Python tarafında çağrılır çünkü PostgreSQL'de UPDATE sırasında otomatik zaman damgası mekanizması yoktur.

#### 6.1.2 SQLAlchemy 2.0 Modern Syntax

Proje, SQLAlchemy'nin en güncel (2.0) sözdizimini kullanmaktadır:

```python
# Eski (1.x) — kullanılmıyor
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

# Yeni (2.0) — projede kullanılan
class Student(TimestampMixin, Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
```

**Avantajlar:** IDE otomatik tamamlama, `mypy` tip kontrolü, daha okunabilir kod.

#### 6.1.3 JSON Kolonları — JSONB Uyumluluğu

```python
departments: Mapped[Optional[dict]] = mapped_column(JSON)
```

`JSON` tipi kullanılmasının sebebi: PostgreSQL'de bu otomatik olarak `JSONB` olarak saklanır (performanslı sorgulama), SQLite testlerinde ise `TEXT` olarak çalışır. Böylece test ortamında ayrı bir tip tanımlamaya gerek kalmaz.

#### 6.1.4 Tablo Listesi ve İlişki Diyagramı

```
┌─────────────┐     ┌──────────────────┐     ┌────────────┐
│  students   │────<│ student_courses  │>────│  courses   │
│             │     └──────────────────┘     └────────────┘
│             │
│             │──── tuition ──── payments
│             │            └──── installments
│             │
│             │──── scholarships
│             │──── user_accounts
│             │──── scholarship_applications
└─────────────┘

┌───────────────┐  ┌──────────────┐  ┌──────────────────────────┐
│  it_tickets   │  │ known_issues │  │ course_registration_     │
│               │  │              │  │ periods                  │
└───────────────┘  └──────────────┘  └──────────────────────────┘

┌─────────────┐  ┌────────────────┐
│ query_logs  │  │ agent_registry │  ← Yeni tablolar (izlenebilirlik)
└─────────────┘  └────────────────┘
```

**Toplam: 15 tablo**, her biri `TimestampMixin` ile `created_at`/`updated_at` otomatik alır.

| Tablo | Alan Sayısı | İndeksler | İlişkiler |
|-------|------------|-----------|-----------|
| `students` | 12 | `student_id` (unique), `department` | courses, tuition, scholarships, account |
| `courses` | 7 | `course_code` (unique), `department` | enrollments |
| `student_courses` | 5 | `student_id`, `course_id` | student, course |
| `tuition` | 8 | `student_id` | student, payments, installments |
| `payments` | 5 | `tuition_id` | tuition |
| `installments` | 5 | `tuition_id` | tuition |
| `scholarships` | 7 | `student_id` | student |
| `scholarship_applications` | 5 | `student_id` | — |
| `available_scholarships` | 6 | — | — |
| `user_accounts` | 9 | `student_id`, `username` (unique) | student |
| `it_tickets` | 7 | `student_id`, `status` | — |
| `known_issues` | 5 | — | — |
| `course_registration_periods` | 4 | — | — |
| `query_logs` | 9 | `user_id`, `created_at` | — | *`metadata` kolonu Python'da `query_metadata` olarak erişilir (SQLAlchemy reserved name)* |
| `agent_registry` | 9 | `agent_id` (unique), `department` | — |

#### 6.1.5 Veri Sözlüğü — Tablo ve Alan Açıklamaları

Her tablonun **neden** var olduğu ve her alanın **ne amaçla** kullanıldığı aşağıda açıklanmıştır.

##### `students` — Öğrenci Ana Tablosu
Sistemdeki tüm öğrencilerin merkezi kaydı. Diğer tabloların çoğu bu tabloya FK ile bağlıdır.

| Alan | Tip | Amaç |
|------|-----|------|
| `student_id` | String(20), UK | Okul numarası (ör: "20210001"). Unique Index — sorgulamalarda birincil arama anahtarı |
| `full_name` | String(100) | Ad Soyad. NOT NULL — her öğrencinin adı olmalı |
| `email` | String(100), UK | Kurumsal e-posta. UK — çift kayıt önlenir |
| `department` | String(100), IDX | Bölüm (ör: "Bilgisayar Mühendisliği"). İndeksli — departman bazlı filtreleme sık yapılır |
| `faculty` | String(100) | Fakülte (ör: "Mühendislik Fakültesi") |
| `grade` | Integer | Sınıf (1–4) |
| `enrollment_year` | Integer | Kayıt yılı (ör: 2021) |
| `registration_status` | String(50) | Kayıt durumu: Aktif, Pasif, Mezun, Donmuş |
| `gpa` | Float | Genel Not Ortalaması (0.0–4.0) |
| `total_credits` | Integer | Toplam alınması gereken kredi |
| `completed_credits` | Integer | Tamamlanan kredi |
| `current_semester` | Integer | Mevcut dönem (1–8) |

##### `courses` — Ders Kataloğu
Üniversitede açılan tüm derslerin listesi.

| Alan | Tip | Amaç |
|------|-----|------|
| `course_code` | String(20), UK | Ders kodu (ör: "BIL301"). Unique Index — sorgulamalarda birincil arama anahtarı |
| `course_name` | String(200) | Ders adı (ör: "Yazılım Mühendisliği") |
| `credits` | Integer | AKTS kredisi (varsayılan: 3) |
| `department` | String(100), IDX | Dersin bağlı olduğu bölüm |
| `semester` | Integer | Müfredatta önerilen dönem |
| `instructor` | String(100) | Dersi veren öğretim üyesi |
| `prerequisite` | String(20) | Ön koşul ders kodu (ör: "BIL201") |

##### `student_courses` — Öğrenci-Ders İlişkisi (Many-to-Many)
Hangi öğrencinin hangi dersi aldığını tutar. Klasik **join table** deseni.

| Alan | Tip | Amaç |
|------|-----|------|
| `student_id` | FK → students | Dersi alan öğrenci |
| `course_id` | FK → courses | Alınan ders |
| `semester` | String(20) | Dersin alındığı dönem (ör: "2025-Güz") |
| `grade` | String(5) | Harf notu (AA, BA, BB, …, FF) |
| `status` | String(20) | Devam, Geçti, Kaldı, Bıraktı |

##### `tuition` — Harç Bilgileri
Her öğrencinin dönemlik harç/öğrenim ücreti durumu. Öğrenci ile **1:1** ilişki.

| Alan | Tip | Amaç |
|------|-----|------|
| `student_id` | FK → students | Harç sahibi öğrenci |
| `semester` | String(20) | İlgili dönem |
| `total_amount` | Float | Toplam harç tutarı (TL) |
| `paid_amount` | Float | Ödenen tutar |
| `has_debt` | Boolean | Borç var mı? (hızlı filtreleme için) |
| `debt_amount` | Float | Kalan borç tutarı |
| `due_date` | DateTime | Son ödeme tarihi |
| `last_payment_date` | DateTime | En son ödeme yapılan tarih |

##### `payments` — Ödeme Geçmişi
Her harç ödemesinin kaydı. Bir harç kaydına **birden fazla ödeme** yapılabilir.

| Alan | Tip | Amaç |
|------|-----|------|
| `tuition_id` | FK → tuition | İlişkili harç kaydı |
| `amount` | Float | Ödeme tutarı |
| `payment_date` | DateTime | Ödeme tarihi (server_default: NOW()) |
| `payment_method` | String(50) | Ödeme yöntemi: Banka, Kredi Kartı, Havale |
| `receipt_no` | String(50), UK | Dekont/makbuz numarası (benzersiz) |

##### `installments` — Taksit Planı
Harçların taksitlendirme detayları.

| Alan | Tip | Amaç |
|------|-----|------|
| `tuition_id` | FK → tuition | İlişkili harç kaydı |
| `installment_number` | Integer | Taksit sırası (1, 2, 3, …) |
| `amount` | Float | Taksit tutarı |
| `due_date` | DateTime | Taksit vade tarihi |
| `status` | String(20) | Bekliyor, Ödendi, Gecikmiş |

##### `scholarships` — Aktif Burslar
Öğrencilere verilen aktif burslar. Bir öğrencinin **birden fazla** bursu olabilir.

| Alan | Tip | Amaç |
|------|-----|------|
| `student_id` | FK → students | Burs sahibi öğrenci |
| `scholarship_name` | String(100) | Burs adı (ör: "Başarı Bursu") |
| `scholarship_type` | String(50) | Tam burs, kısmi burs, yemek bursu vb. |
| `monthly_amount` | Float | Aylık burs tutarı (TL) |
| `start_date` / `end_date` | DateTime | Burs başlangıç ve bitiş tarihi |
| `status` | String(20) | Aktif, Dondurulmuş, Sona Erdi |

##### `scholarship_applications` — Burs Başvuruları
Öğrencilerin burs başvuru kayıtları.

| Alan | Tip | Amaç |
|------|-----|------|
| `student_id` | FK → students | Başvuran öğrenci |
| `scholarship_name` | String(100) | Başvurulan burs adı |
| `application_date` | DateTime | Başvuru tarihi |
| `status` | String(20) | Beklemede, Onaylandı, Reddedildi |
| `notes` | Text | Başvuruyla ilgili notlar/açıklamalar |

##### `available_scholarships` — Başvuruya Açık Burs Kataloğu *(bağımsız tablo)*
Herhangi bir öğrenciye bağlı değil. Üniversitenin sunduğu burs seçeneklerinin listesi.

| Alan | Tip | Amaç |
|------|-----|------|
| `name` | String(100) | Burs adı |
| `description` | Text | Burs açıklaması ve koşulları |
| `monthly_amount` | Float | Aylık tutar |
| `min_gpa` | Float | Minimum GPA şartı |
| `deadline` | DateTime | Son başvuru tarihi |
| `is_active` | Boolean | Başvuruya açık mı? |

##### `user_accounts` — Kullanıcı Hesapları (IT Departmanı)
Üniversite bilgi sistemi hesap bilgileri. Öğrenci ile **1:1** ilişki.

| Alan | Tip | Amaç |
|------|-----|------|
| `student_id` | FK → students | Hesap sahibi öğrenci |
| `username` | String(50), UK | Kullanıcı adı (benzersiz) |
| `email` | String(100) | Hesaba bağlı e-posta |
| `status` | String(20) | Aktif, Pasif, Askıya Alındı |
| `last_login` | DateTime | Son giriş tarihi |
| `is_locked` | Boolean | Hesap kilitli mi? |
| `failed_attempts` | Integer | Başarısız giriş denemesi (3'te kilit) |
| `password_last_changed` | DateTime | Şifre son değiştirilme tarihi |
| `password_expired` | Boolean | Şifre süresi dolmuş mu? |

##### `it_tickets` — IT Destek Talepleri
Öğrencilerin IT departmanına açtığı destek talepleri.

| Alan | Tip | Amaç |
|------|-----|------|
| `student_id` | FK → students | Talebi açan öğrenci |
| `ticket_no` | String(20), UK | Talep numarası (ör: "IT-2026-0042") |
| `category` | String(50) | Kategori: E-posta, WiFi, VPN, Yazılım |
| `subject` | String(200) | Talep başlığı |
| `description` | Text | Detaylı açıklama |
| `status` | String(20), IDX | Açık, İşlemde, Çözüldü, Kapatıldı. İndeksli — status bazlı filtreleme sık |
| `priority` | String(20) | Normal, Yüksek, Acil |

##### `known_issues` — Bilinen Sorunlar (IT Bilgi Bankası) *(bağımsız tablo)*
IT departmanının sık karşılaşılan sorunlar ve çözümleri veritabanı. RAG ile sorgulanacak.

| Alan | Tip | Amaç |
|------|-----|------|
| `category` | String(50) | Sorun kategorisi |
| `title` | String(200) | Sorun başlığı |
| `description` | Text | Sorunun açıklaması |
| `solution` | Text | Çözüm adımları |
| `is_resolved` | Boolean | Sorun çözüldü mü? |

##### `course_registration_periods` — Ders Kayıt Dönemleri *(bağımsız tablo)*
Akademik takvim verisi — ders kayıt dönemlerinin başlangıç ve bitiş tarihleri.

| Alan | Tip | Amaç |
|------|-----|------|
| `semester` | String(20) | Dönem adı (ör: "2026-Bahar") |
| `start_date` / `end_date` | DateTime | Kayıt dönemi başlangıç ve bitiş |
| `is_active` | Boolean | Şu an aktif kayıt dönemi mi? |

##### `query_logs` — Sorgu Logları (İzlenebilirlik) *(bağımsız tablo)*
Kullanıcıların sisteme sorduğu tüm soruların kaydı. Analiz, performans ölçümü ve izlenebilirlik için.

| Alan | Tip | Amaç |
|------|-----|------|
| `user_id` | String(50), IDX | Sorgulayan kullanıcı (FK değil — öğrenci silinse bile log korunmalı) |
| `query_text` | Text | Kullanıcının sorduğu soru |
| `departments` | JSON | Sorgunun yönlendirildiği departmanlar |
| `routing_strategy` | String(50) | Kullanılan yönlendirme stratejisi (direct, parallel, sequential) |
| `confidence_score` | Float | Yönlendirme güven skoru (0.0–1.0) |
| `response_text` | Text | Sistemin verdiği yanıt |
| `response_time_ms` | Float | Yanıt süresi (milisaniye) — performans ölçümü |
| `status` | String(20) | completed, failed, timeout |
| `error` | Text | Hata mesajı (varsa) |
| `metadata` | JSON | Ek bilgi (Python'da `query_metadata` olarak erişilir) |

##### `agent_registry` — Ajan Kayıt Tablosu *(bağımsız tablo)*
A2A protokolünde dinamik ajan keşfi için. Her ajan kendisini bu tabloya kaydeder.

| Alan | Tip | Amaç |
|------|-----|------|
| `agent_id` | String(100), UK | Ajan benzersiz kimliği (ör: "finance-specialist-01") |
| `name` | String(200) | Ajan görüntüleme adı |
| `department` | String(100), IDX | Ajanın bağlı olduğu departman |
| `role` | String(50) | main_orchestrator, department_orchestrator, specialist_agent |
| `description` | Text | Ajanın yeteneklerinin açıklaması |
| `endpoint` | String(500) | Ajanın API endpoint'i |
| `capabilities` | JSON | Ajanın desteklediği görev tipleri (yapılandırılmış veri) |
| `is_active` | Boolean | Ajan aktif mi? |
| `last_heartbeat` | DateTime | Son yaşam sinyali — belirli süre gelmezse ajan çevrimdışı sayılır |
### 6.2 Bağlantı Yönetimi (`src/db/connection.py`)

#### 6.2.1 Lazy Initialization Pattern

Engine, modül import edildiğinde **oluşturulmaz**. İlk kez `get_engine()` çağrıldığında oluşturulur:

```
┌─────────────────────────────────────────────────────────────┐
│ from src.db.connection import get_session  ← Engine YOKTUR  │
│                                                             │
│ async with get_session() as session:     ← İlk çağrı       │
│   ├─ get_session_factory() çağrılır                         │
│   │   └─ get_engine() çağrılır                              │
│   │       └─ _engine is None → create_async_engine()        │
│   │           ├─ URL: settings.postgres.async_url            │
│   │           ├─ pool_size: settings.postgres.pool_size (10) │
│   │           ├─ max_overflow: settings.postgres.max_overflow │
│   │           ├─ pool_timeout: 30s                           │
│   │           ├─ pool_recycle: 1800s (30 dk)                 │
│   │           └─ echo: settings.server.debug                 │
│   ├─ async_sessionmaker() ile session oluşturulur            │
│   ├─ yield session ← Kullanıcı kodu çalışır                 │
│   ├─ Hata yoksa → session.commit()                           │
│   ├─ Hata varsa → session.rollback()                         │
│   └─ Her durumda → session.close()                           │
└─────────────────────────────────────────────────────────────┘
```

**Neden lazy?**
1. `import src.db.connection` çağrıldığında veritabanı bağlantısı **denenmez** → modül yükleme hatası olmaz
2. Testlerde `init_engine("sqlite+aiosqlite:///:memory:")` ile farklı veritabanı kullanılabilir
3. Uygulama başlayana kadar config değerleri hazır olmayabilir

#### 6.2.2 Bağlantı Havuzu (Connection Pool) Parametreleri

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| `pool_size` | 10 | Havuzda sürekli açık tutulacak bağlantı sayısı |
| `max_overflow` | 5 | Havuz dolduğunda ekstra açılabilecek geçici bağlantı (toplam max: 15) |
| `pool_timeout` | 30s | Havuzdan bağlantı beklerken max süre |
| `pool_recycle` | 1800s | Bağlantının yenilenmesi gereken süre (stale connection önlemi) |

**SQLite uyumluluğu:** Testlerde SQLite in-memory veritabanı kullanılır. SQLite `StaticPool` kullandığı için yukarıdaki pool parametreleri **yalnızca PostgreSQL** için uygulanır. `init_engine()` fonksiyonu URL'de `sqlite` algıladığında bu parametreleri otomatik atlar.

#### 6.2.3 Session Yönetimi Akışı

```
get_session() Context Manager
    │
    ├── Başarılı senaryo:
    │   session açılır → iş yapılır → commit() → close()
    │
    └── Hata senaryosu:
        session açılır → iş yapılır → HATA → rollback() → close() → raise
```

#### 6.2.4 Health Check

`check_db_health()` fonksiyonu `SELECT 1` sorgusu ile veritabanı bağlantısını test eder. Yanıt: `{"status": "healthy"|"unhealthy", "latency_ms": float, "details": str}`. FastAPI health check endpoint'i tarafından kullanılacaktır.

### 6.3 Pydantic Şemaları (`src/db/schemas.py`)

**Kritik NOT:** A2A protokol tipleri (`Task`, `Message`, `Artifact`, `AgentCard`, `TextPart`, `DataPart`, `FilePart`, `Role`, `TaskState`) artık bu dosyada **tanımlı değildir**. Bunlar resmi `a2a-sdk` paketinden import edilir:
```python
from a2a.types import AgentCard, Task, TaskState, Message, Part, Role
```

Bu dosyada yalnızca projemize özel iş mantığı şemaları bulunur:

| Şema | Tip | Alanlar | Validasyonlar |
|------|-----|---------|---------------|
| `RAGQuery` | Input | `query`, `department`, `top_k`, `min_similarity` | query: 1–500 char, top_k: 1–20, min_similarity: 0.0–1.0 |
| `RAGSource` | Nested | `content`, `score`, `metadata` | — |
| `RAGResult` | Output | `answer`, `sources[]`, `department`, `response_time_ms` | — |
| `RoutingResult` | Output | `departments[]`, `confidence`, `confidence_level`, `strategy`, `reasoning`, `task_type` | confidence: 0.0–1.0 |
| `DepartmentResponse` | Output | `department`, `answer`, `sources[]`, `db_data`, `success`, `error` | — |
| `UserQueryRequest` | API Input | `query`, `user_id`, `context_id` | query: 1–500 char |
| `UserQueryResponse` | API Output | `answer`, `departments_involved[]`, `sources[]`, `response_time_ms`, `query_id` | — |
| `ServiceHealth` | Health | `name`, `status`, `latency_ms`, `details` | — |
| `SystemHealthResponse` | Health | `status`, `services[]`, `timestamp` | timestamp: otomatik UTC |

---

## 7. A2A Protokol Entegrasyonu

### 7.1 Karar: Resmi SDK'ya Geçiş

Kalite denetimi sırasında, elle yazılmış A2A sınıflarının (`A2AMessage`, `A2ATask`, `AgentCard`, `TextPart` vb.) Google'ın resmi A2A spesifikasyonu ile **uyumsuz** olduğu tespit edilmiştir. Özellikle:
- `TaskStatus` enum değerleri resmi spec ile farklıydı
- `MessageRole` enum'u eksik değerler içeriyordu
- `AgentCard` alanları spec'teki zorunlu/opsiyonel tanımlarla uyuşmuyordu

**Çözüm:** `a2a-sdk==0.2.7` (Google resmi SDK) eklendi. Tüm elle yazılan A2A sınıfları kaldırıldı.

```
# requirements.txt
a2a-sdk==0.2.7

# Kullanım (FAZ 2'de implemente edilecek)
from a2a.types import AgentCard, Task, TaskState, Message, Part, Role
```

### 7.2 İç vs A2A Durumları

```
A2A TaskState (a2a-sdk):        InternalTaskStatus (bizim):
  submitted                       routing
  working         ←→              queued
  completed                       retrying
  failed                          timeout
  canceled
  input-required
```

A2A durumları ajan iletişiminde kullanılır. İç durumlar yönlendirme ve kuyruk yönetimi gibi A2A kapsamı dışındaki süreçler içindir.

---

## 8. Docker Compose Altyapısı

### 8.1 Servis Topolojisi

```
┌─────────────────────────────────────────────┐
│              Docker Compose                  │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │PostgreSQL│  │  Redis   │  │ ChromaDB │  │
│  │  :5432   │  │  :6379   │  │  :8100   │  │
│  │ Alpine   │  │ Alpine   │  │  0.6.3   │  │
│  │ ✓Health  │  │ ✓Health  │  │          │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                              │
│  ┌──────────┐                                │
│  │ Ollama   │  ← GPU opsiyonel (NVIDIA)     │
│  │ :11434   │                                │
│  └──────────┘                                │
└─────────────────────────────────────────────┘
```

### 8.2 Servis Detayları

| Servis | Image | Port | Volume | Health Check | Ek Ayar |
|--------|-------|------|--------|-------------|---------|
| PostgreSQL | `postgres:15-alpine` | `5432` | `uni_postgres_data` | `pg_isready -U postgres` (10s/5s/5) | `restart: unless-stopped` |
| Redis | `redis:7-alpine` | `6379` | `uni_redis_data` | `redis-cli ping` (10s/5s/5) | `appendonly yes` (AOF persistency) |
| ChromaDB | `chromadb/chroma:0.6.3` | `8100→8000` | `uni_chroma_data` | — | `IS_PERSISTENT=TRUE`, `ANONYMIZED_TELEMETRY=FALSE` |
| Ollama | `ollama/ollama:latest` | `11434` | `uni_ollama_data` | — | GPU desteği opsiyonel |

---

## 9. Migration Sistemi (Alembic)

### 9.1 Akış

```
alembic revision --autogenerate -m "açıklama"
    │
    ├─ models.py'deki değişiklikleri algılar
    ├─ migrations/versions/ altına .py dosyası oluşturur
    └─ upgrade() ve downgrade() fonksiyonları otomatik yazılır

alembic upgrade head
    │
    └─ Tüm bekleyen migration'ları uygular

alembic downgrade -1
    │
    └─ Son migration'ı geri alır
```

### 9.2 `migrations/env.py` — Dinamik URL

Alembic, veritabanı URL'sini `.env` dosyasından okur:
```python
from src.core.config import settings
config.set_main_option("sqlalchemy.url", settings.postgres.sync_url)
```

**Neden `sync_url`?** Alembic CLI senkron çalışır, bu yüzden `psycopg2` (senkron driver) kullanılır. Uygulama ise `asyncpg` (asenkron driver) ile `async_url` kullanır.

---

## 10. Test Altyapısı

### 10.1 Test Veritabanı İzolasyonu

```
┌──────────────────────────────────────────────────────┐
│ Her test fonksiyonu için:                             │
│                                                      │
│  1. SQLite in-memory engine oluşturulur               │
│  2. Base.metadata.create_all → tüm tablolar yaratılır │
│  3. Session açılır, test çalışır                      │
│  4. Session.rollback() → değişiklikler geri alınır    │
│  5. Base.metadata.drop_all → tablolar silinir         │
│  6. Engine.dispose() → bağlantı kapatılır             │
│                                                      │
│  ↳ Her test tamamen izole! Birbirini etkilemez.       │
└──────────────────────────────────────────────────────┘
```

**Neden SQLite in-memory?** PostgreSQL çalışıyor olmasını gerektirmeden unit testler herhangi bir ortamda çalıştırılabilir. CI/CD pipeline'ında Docker gerekmez.

### 10.2 pytest-asyncio Konfigürasyonu

`pyproject.toml`'da `asyncio_mode = "auto"` ayarı kullanılmaktadır. Bu sayede:
- `@pytest.mark.asyncio` dekoratörüne **gerek yoktur** (otomatik algılanır)
- Deprecated `event_loop` fixture'ına **gerek yoktur** (pytest-asyncio 0.21+ kendi yönetir)

### 10.3 Mock Servisleri

| Fixture | Mock'lanan Servis | Sağlanan Metodlar |
|---------|-------------------|-------------------|
| `mock_llm_service` | LLM (Ollama/OpenAI) | `generate()`, `generate_json()`, `is_available()` |
| `mock_rag_service` | RAG Pipeline | `query()` → örnek kaynak belge + skor |
| `mock_redis` | Redis Client | `get()`, `set()`, `delete()`, `lpush()`, `rpop()` |

### 10.4 Test Dosyaları ve Sonuçları

**Son çalıştırma:** 25 Şubat 2026 — **40/40 test geçti** ✅ (1.04 saniye)

| Dosya | Test Sayısı | Kapsam |
|-------|:----------:|--------|
| `test_config.py` | 10 | Department enum değerleri ve display_name, InternalTaskStatus tüm durumları, TaskType alt tipleri (finance, IT, student), Priority sıralaması, güven eşik değerleri |
| `test_connection.py` | 8 | Engine başlangıçta None, init_engine ile oluşturma, session factory oluşturma, session commit/rollback/dispose, SQLite izolasyonu |
| `test_models.py` | 7 | Student oluşturma ve varsayılan değerler, Tuition ilişkileri, QueryLog JSONB (`query_metadata`) alanları, AgentRegistry capabilities, `__repr__` metodu |
| `test_schemas.py` | 15 | RAGQuery validasyon (boş/uzun sorgu red, custom top_k), RAGResult oluşturma, RoutingResult çoklu departman, DepartmentResponse varsayılanlar, UserQueryRequest user_id, HealthCheck timestamp |
| **Toplam** | **40** | config + connection + models + schemas |

```
=============================== 40 passed in 1.04s ===============================
```

### 10.5 Test Sırasında Tespit Edilen ve Düzeltilen Sorunlar

| Sorun | Açıklama | Düzeltme |
|-------|----------|----------|
| `QueryLog.metadata` reserved | SQLAlchemy Declarative API'de `metadata` reserved bir attribute | Python attr `query_metadata`, DB kolonu `metadata` olarak ayrıştırıldı: `mapped_column("metadata", JSON)` |
| SQLite pool parametreleri | `pool_size`, `max_overflow`, `pool_timeout` SQLite StaticPool ile uyumsuz | `init_engine()` fonksiyonunda SQLite algılandığında pool parametreleri atlanıyor |

---

## 11. Bağımlılıklar (`requirements.txt` + `requirements-dev.txt`)

Bağımlılıklar **iki dosyaya** ayrılmıştır:
- `requirements.txt` — Yalnızca production'da gereken paketler
- `requirements-dev.txt` — Test ve kod kalitesi araçları (`-r requirements.txt` ile runtime bağımlılıklarını da çeker)

| Kategori | Paket | Sürüm | Neden? |
|----------|-------|-------|--------|
| **Web** | `fastapi` | 0.115.12 | Asenkron API framework |
| | `uvicorn` | 0.34.0 | ASGI sunucu |
| | `httpx` | 0.28.1 | Async HTTP istemci |
| | `pydantic` | 2.11.3 | Veri doğrulama |
| | `pydantic-settings` | 2.9.1 | Ortam değişkeni yönetimi |
| **A2A** | `a2a-sdk` | 0.2.7 | Google resmi A2A SDK |
| **DB** | `sqlalchemy` | 2.0.37 | ORM (async destekli) |
| | `asyncpg` | 0.30.0 | PostgreSQL async driver |
| | `alembic` | 1.14.1 | Migration yönetimi |
| | `psycopg2-binary` | 2.9.10 | PostgreSQL sync driver (Alembic) |
| | `aiosqlite` | 0.20.0 | SQLite async driver (testler) |
| **Cache** | `redis` | 5.2.1 | Kuyruk ve cache |
| **RAG** | `chromadb` | 0.6.3 | Vektör veritabanı *(FAZ 1'de Docker ortamında kurulacak)* |
| | `langchain` | 0.3.14 | RAG orkestrasyon |
| | `langchain-community` | 0.3.14 | Topluluk entegrasyonları |
| | `langchain-text-splitters` | 0.3.4 | Doküman parçalama |
| **Embedding** | `sentence-transformers` | 3.4.1 | SBERT kütüphanesi |
| | `transformers` | 4.48.1 | HuggingFace transformers |
| | `torch` | 2.6.0 | PyTorch (backend) |
| **LLM** | `openai` | 1.59.9 | OpenAI SDK (Ollama uyumlu) |
| **Slack** | `slack-sdk` | 3.34.0 | Slack Web API |
| | `slack-bolt` | 1.22.0 | Slack event framework |
| **Güvenlik** | `PyJWT` | 2.10.1 | JWT token *(python-jose deprecate — CVE düzeltmesi)* |
| | `passlib` | 1.7.4 | Şifre hashleme |
| | `bcrypt` | 4.2.1 | Şifre hash backend (passlib için) |
| **Yardımcı** | `python-dotenv` | 1.0.1 | pydantic-settings alt bağımlılığı |
| | `structlog` | 25.1.0 | Yapılandırılmış loglama |
| | `tenacity` | 9.0.0 | Retry mekanizması |
| **Test** *(dev)* | `pytest` | 8.3.4 | Test framework |
| | `pytest-asyncio` | 0.25.2 | Async test desteği |
| | `pytest-cov` | 6.0.0 | Coverage raporu |
| | `pytest-mock` | 3.14.0 | Mock yardımcıları |
| | `aiohttp` | 3.11.12 | Async HTTP test client |
| **Kalite** *(dev)* | `black` | 24.10.0 | Kod formatlama |
| | `flake8` | 7.1.1 | Linting |
| | `isort` | 5.13.2 | Import sıralama |
| | `mypy` | 1.14.1 | Statik tip kontrolü |

### 11.1 Bağımlılık Değişiklik Günlüğü

| Değişiklik | Eski | Yeni | Gerekçe |
|------------|------|------|---------|
| JWT kütüphanesi | `python-jose==3.3.0` | `PyJWT==2.10.1` | python-jose deprecate edildi, bilinen CVE'ler var |
| Şifre hash backend | *(eksik)* | `bcrypt==4.2.1` | passlib'in bcrypt backend'i eksikti, runtime hatası riski |
| ChromaDB | Doğrudan kurulum | Yorum satırı | `chroma-hnswlib` Windows'ta C++ Build Tools + Windows SDK gerektiriyor; FAZ 1'de Docker ile kurulacak |

---

## 12. Modülerlik ve Genişletilebilirlik

### 12.1 `__init__.py` Export Yapısı

```python
# src/core/__init__.py
from src.core.config import settings
from src.core.constants import Department, TaskType, InternalTaskStatus, ...

# src/db/__init__.py
from src.db.models import Base
from src.db.connection import get_session, init_engine, dispose_engine, ...
```

Bu sayede dışarıdan: `from src.core import settings, Department` veya `from src.db import get_session`.

### 12.2 Yeni Modül Ekleme Rehberi

**Yeni bir servis ayarı eklemek için:**
1. `config.py`'de yeni `XxxSettings(BaseSettings)` sınıfı yaz
2. `Settings` ana sınıfına `xxx: XxxSettings = Field(default_factory=XxxSettings)` ekle
3. `.env.example`'a ilgili değişkenleri ekle

**Yeni bir veritabanı tablosu eklemek için:**
1. `models.py`'de yeni model sınıfı yaz (`TimestampMixin, Base` kalıtımı)
2. `alembic revision --autogenerate -m "açıklama"` çalıştır
3. `alembic upgrade head` ile migration'ı uygula

**Yeni bir enum eklemek için:**
1. `constants.py`'de `str, Enum` sınıfı yaz
2. `__init__.py`'deki `__all__` listesine ekle

---

## 13. Çalıştırma Talimatları

### Windows (PowerShell)

```powershell
# 1. Proje klasörüne git
cd v2

# 2. Ortam değişkenlerini ayarla
Copy-Item .env.example .env

# 3. Python sanal ortam oluştur ve aktifleştir
python -m venv venv
venv\Scripts\Activate.ps1

# 4. Bağımlılıkları kur (dev araçları dahil)
venv\Scripts\pip.exe install -r requirements-dev.txt

# 5. Testleri çalıştır (Docker gerekmez)
venv\Scripts\python.exe -m pytest tests/ -v

# 6. Docker servislerini başlat (FAZ 1+ için gerekli)
docker compose up -d

# 7. Ollama'da Qwen2.5 modelini indir
docker exec uni_ollama ollama pull qwen2.5:7b

# 8. Veritabanı migration'ını çalıştır
python -m alembic upgrade head
```

### Linux / macOS

```bash
cd v2
cp .env.example .env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest tests/ -v
docker compose up -d
```

> **Not:** `chromadb` bağımlılığı Windows'ta yerel kurulumda C++ Build Tools gerektirdiğinden geçici olarak devre dışıdır. FAZ 1'de Docker ortamında sorunsuz kurulacaktır.

---

## 14. Kalite Denetimi Sonuçları

FAZ 0 tamamlandıktan sonra iki aşamalı kapsamlı kalite denetimi gerçekleştirilmiştir.

### 14.1 Mimari ve Kod Denetimi (Aşama 1)

| Sorun | Etki | Düzeltme |
|-------|------|----------|
| Elle yazılmış A2A sınıfları | Spec uyumsuzluğu | `a2a-sdk` resmi SDK'ya geçildi |
| `alias` anti-pattern (config.py) | `env_prefix` ile çakışma | `env_prefix` pattern'e geçildi |
| `env_prefix + alias` çakışması | Ortam değişkeni okunmama | `model_name` → `model`, `validation_alias` |
| `load_dotenv()` gereksiz çağrı | Çift yükleme | Kaldırıldı (pydantic-settings kendi yönetiyor) |
| Deprecated `event_loop` fixture | pytest-asyncio uyarısı | Kaldırıldı (`asyncio_mode=auto` yeterli) |
| `@property` serialization yok | Config dump'da URL gizli | `@computed_field` kullanıldı |

### 14.2 Bağımlılık ve Çalışma Zamanı Denetimi (Aşama 2)

| Sorun | Etki | Düzeltme |
|-------|------|----------|
| `python-jose` deprecated (CVE) | Güvenlik açığı riski | `PyJWT==2.10.1` ile değiştirildi |
| `bcrypt` backend eksik | `passlib[bcrypt]` runtime hatası | `bcrypt==4.2.1` bağımlılığa eklendi |
| `QueryLog.metadata` reserved | SQLAlchemy `InvalidRequestError` | `query_metadata` olarak yeniden adlandırıldı (`mapped_column("metadata", JSON)` ile DB kolonu korundu) |
| SQLite pool parametreleri | `pool_size` testi kırıyordu | `init_engine()` SQLite algılandığında pool parametrelerini atlıyor |
| `chromadb` derleme hatası | Windows SDK eksik (`float.h`) | FAZ 1'de Docker ortamında kurulacak, geçici olarak devre dışı |
| Dev/runtime bağımlılık karışımı | Gereksiz prod bağımlılıkları | `requirements-dev.txt` ile ayrıştırıldı |

### 14.3 Dikkat Gerektiren Noktalar

| Konu | Durum | Aksiyon |
|------|-------|---------|
| `a2a-sdk==0.2.7` | ⚠️ Yeni SDK, API değişebilir | Changelog takip edilmeli, sürüm pinlendi |
| `chromadb` Windows kurulumu | ⚠️ C++ Build Tools + Windows SDK gerekli | FAZ 1'de Docker ortamında çözülecek |
| `pytest-asyncio` deprecation uyarısı | ℹ️ `asyncio_default_fixture_loop_scope` unset | Proje çalışıyor, gelecek sürümlerde `pyproject.toml`'a eklenmeli |
| `langchain-core` backtracking | ℹ️ pip çözümleme yavaş | `langchain-core` sürümü pinlenebilir (0.3.63) |

---

## 15. Sonraki Adımlar (FAZ 1)

FAZ 0 tamamlanmıştır. **FAZ 1 — Veri ve RAG Altyapısı** kapsamında:

1. 3 departman için 60+ sentetik Türkçe doküman üretimi
2. BERTurk ile RAG indeksleme pipeline'ı
3. ChromaDB semantik sorgulama
4. RAGAS metrikleri ile RAG değerlendirmesi
5. PostgreSQL Docker entegrasyonu
6. Redis kuyruk ve cache sistemi

---

*Bu doküman, projenin her fazı tamamlandıkça güncellenecektir.*
