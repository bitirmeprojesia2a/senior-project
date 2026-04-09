# Universite Kurumsal Destek Sistemi

> RAG, LLM, OTP/session auth ve uygulama ici A2A orkestrasyonu ile universite destek sorgularini cevaplayan cok departmanli destek sistemi.

## Proje Ozeti

Bu repo artik sadece "RAG cekirdegi" degil; calisan bir uygulama yuzeyi sunar. Guncel kod tabaninda:

- `finance`, `student_affairs` ve `academic_programs` departmanlari aktif olarak desteklenir
- duyuru sorgulari ayri announcement akisi ile ele alinir
- OTP/session tabanli kimlik dogrulama endpoint'leri vardir
- cok turlu konusma baglami ve follow-up cozumu bulunur
- FastAPI giris noktasi, ic A2A dispatch ve benchmark/demo scriptleri calisir durumdadir

Slack, dis HTTP A2A genisletmeleri ve daha ileri dagitim katmanlari halen gelistirilebilir alanlar olarak durmaktadir; ancak ana uygulama akisi calismayan iskelet seviyesinde degildir.

## Guncel Ozellikler

- Hibrit retrieval: BM25 + ChromaDB semantic search + cross-encoder reranker
- Rol bazli LLM kullanimi: routing, conversation, specialist synthesis ve global synthesis icin ayri model tercihleri
- Announcement kisa yolu: duyuru sorgularini gereksiz akademik retrieval'a sokmadan ayri ele alma
- Conversation memory: context id uzerinden follow-up cozumleme ve kaynak/topic hint kullanimi
- Profile/auth akisi: OTP isteme, dogrulama, session resolve ve logout endpoint'leri
- Telemetry: query log, ajan gorevleri ve orchestrator seviyesinde gozlenebilirlik
- Demo ve benchmark scriptleri: showcase, follow-up ve profile context senaryolari
- Docker tabanli lokal kurulum ve Azure VM runbook'u

## Guncel Mimari

```text
Kullanici / istemci
    |
    v
FastAPI giris katmani
  - /query
  - /auth/*
  - /a2a/dispatch
    |
    v
Query / auth / profile helper akislari
    |
    v
MainOrchestrator
  - conversation resolve
  - department routing
  - announcement fallback
  - multi-department synthesis
    |
    v
Departman ajanlari
  - finance
  - student_affairs
  - academic_programs
  - announcement
    |
    v
RAG + LLM katmani
  - document loader / preprocessor / chunker
  - embedding / retriever / reranker
  - Ollama primary
  - OpenAI fallback
    |
    v
Yanit + kaynaklar + telemetry + conversation memory
```

## Teknoloji Yigini

| Bilesen | Teknoloji | Not |
|---|---|---|
| Dil | Python 3.11+ | Ana uygulama dili |
| Web/API | FastAPI | Aktif giris yuzeyi |
| ORM ve migration | SQLAlchemy 2 + Alembic | Aktif |
| Veritabani | PostgreSQL 15 | Aktif |
| Cache / yan servisler | Redis 7 | Aktif servis, kullanim senaryoya gore degisir |
| Vektor veritabani | ChromaDB | Aktif |
| Yerel LLM | Ollama | Varsayilan primary provider |
| Yedek LLM | OpenAI HTTP fallback client | API key varsa devreye girer |
| Embedding | BAAI/bge-m3 | Varsayilan embedding modeli |
| Reranker | seroe/bge-reranker-v2-m3-turkish-triplet | Varsayilan reranker |
| Konteyner | Docker Compose | Lokal ve VM kurulumlarinda kullanilir |

## Hizli Baslangic

### 1. Python ortami

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

### 2. Ortam degiskenleri

```powershell
copy .env.example .env
```

Temiz bir makinede Hugging Face modellerinin indirilebilmesi icin gerekirse su iki ayari ekleyin:

```text
EMBEDDING_LOCAL_FILES_ONLY=false
RERANKER_LOCAL_FILES_ONLY=false
```

### 3. Docker servisleri

```powershell
docker compose up -d
docker compose ps
```

### 4. Veritabani migration

```powershell
python -m alembic upgrade head
```

### 5. Structured seed verileri

RAG indeksleri tek basina yeterli degildir. Su komutlar PostgreSQL icindeki
ders, onkosul, kayit donemi, ogrenim ucreti ve demo ogrenci verilerini yukler:

```powershell
python -m scripts.seed_curriculum_data
python -m scripts.seed_synthetic_data
```

Bu adim ozellikle su sorgular icin gereklidir:

- `BIL104 dersinin on kosulu nedir?`
- `1. yariyil dersleri nelerdir?`
- kayit donemi / harc / burs sorgulari

Not:

- `seed_curriculum_data` `courses` ve `course_prerequisites` tablolarini doldurur.
- `seed_synthetic_data` `course_registration_periods`, `tuition_fee_catalog`, `students`, `tuition`, `payments`, `installments`, `scholarships`, `announcements` ve `office_contacts` tablolarini demo verilerle doldurur.
- Duyuru ve iletisim kayitlari demo amaclidir; gercek ortama gecerken gercek kaynaklarla degistirilmelidir.

### 6. Departman indeksleme

```powershell
python scripts/index_documents.py --source data/raw/student_affairs --collection student_affairs_docs --reindex
python scripts/index_documents.py --source data/raw/academic_programs --collection academic_programs_docs --reindex
python scripts/index_documents.py --source data/raw/finance --collection finance_docs --reindex
```

### 7. API'yi calistirma

```powershell
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Kontrol icin:

- `GET /`
- `GET /health`
- `GET /docs`

Detayli kurulum ve sorun giderme icin [docs/KURULUM_VE_CALISTIRMA.md](docs/KURULUM_VE_CALISTIRMA.md) dosyasini kullanin.

## Proje Yapisi

```text
university_support_system/
|-- src/
|   |-- api/               # FastAPI girisi ve query/auth/profile helper akislari
|   |-- agents/            # Akademik, finans, ogrenci isleri ve duyuru ajanlari
|   |-- orchestrators/     # Ana orchestrator ve moduler dispatch/synthesis yardimcilari
|   |-- routing/           # DepartmentRouter ve routing policy
|   |-- rag/               # Loader, chunker, retriever, reranker, index pipeline
|   |-- llm/               # Ollama/OpenAI istemcileri ve LLM service
|   |-- db/                # ORM modelleri, auth, profile, conversation ve telemetry
|   |-- notifications/     # OTP e-posta gonderim yardimcilari
|   |-- slack/             # Slack tarafindaki entegrasyon temeli
|   |-- a2a/, cache/, queue/, security/, mcp/
|   `-- core/              # Konfigrasyon, sabitler ve ortak yardimcilar
|-- scripts/               # Index, benchmark, evaluate ve test CLI scriptleri
|-- tests/                 # Unit ve integration testleri
|-- docs/                  # Guncel ve tarihsel dokumantasyon
|-- data/                  # Raw dokumanlar ve metadata
|-- docker-compose.yml
|-- alembic.ini
|-- pyproject.toml
`-- requirements*.txt
```

## Dokumantasyon

| Dokuman | Amac |
|---|---|
| [docs/DOKUMANTASYON_OKUMA_SIRASI.md](docs/DOKUMANTASYON_OKUMA_SIRASI.md) | Hangi belgenin guncel, hangisinin tarihsel oldugunu gosteren giris noktasi |
| [docs/KURULUM_VE_CALISTIRMA.md](docs/KURULUM_VE_CALISTIRMA.md) | Guncel lokal kurulum, indeksleme, test ve sorun giderme rehberi |
| [docs/PROJE_ANATOMISI_KILAVUZU.md](docs/PROJE_ANATOMISI_KILAVUZU.md) | Mevcut modullerin sorumluluk haritasi |
| [docs/demo_runbook.md](docs/demo_runbook.md) | Demo ve benchmark senaryolarini calistirma notlari |
| [docs/AZURE_VM_RUNBOOK.md](docs/AZURE_VM_RUNBOOK.md) | Azure VM uzerinde kurulum ve operasyon notlari |
| [docs/technical_backlog.md](docs/technical_backlog.md) | Halen acik teknik iyilestirme listesi |
| [docs/MART_2026_GUNCELLEME_NOTLARI.md](docs/MART_2026_GUNCELLEME_NOTLARI.md) | Mart 2026 donemindeki mimari degisim ozeti |
| `docs/FAZ_0_*`, `docs/FAZ_1_*`, `docs/FAZ_2_*`, `docs/FAZ_3_*` | Tarihsel faz kayitlari; guncel operasyon dokumani olarak degil, referans arka plan olarak okunmalidir |

## Lisans

Bu proje bir bitirme projesidir.
