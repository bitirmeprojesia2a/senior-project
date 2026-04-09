# Kurulum ve Calistirma Rehberi

Bu belge, projenin guncel kod tabani icin pratik kurulum rehberidir. Tarihsel faz dokumanlarindaki bazi anlatilar proje gecmisi acisindan degerlidir, ancak guncel calistirma akisi icin bu dosya, `README.md` ve `AZURE_VM_RUNBOOK.md` once referans alinmalidir.

## 1. On Kosullar

Projeyi lokal ya da VM uzerinde calistirmak icin asagidaki araclar yeterlidir:

| Yazilim | Onerilen surum | Not |
|---|---|---|
| Python | 3.11+ | Ana uygulama |
| Docker | 24+ | PostgreSQL, Redis, ChromaDB, Ollama |
| Docker Compose | 2.20+ | `docker compose` komutu |
| Git | 2.40+ | Repo erisimi |

Kaynak notlari:

- Embedding ve reranker modelleri ilk calistirmada Hugging Face uzerinden iner.
- Ollama modelleri ilk acilista ya da ilk cagrida indirilir.
- CPU dostu kurulum yapacaksaniz daha kucuk Ollama modeli ve `cpu` cihaz secimi kullanabilirsiniz.

## 2. Kodu Elde Etme

Repo erisiminiz varsa:

```powershell
git clone <repo-url>
cd university_support_system\university_support_system
```

Repo private ise ve uzak makinede `git clone` kullanamiyorsaniz iki yol vardir:

1. GitHub auth ile klonlama
2. Lokalde zip alip hedef makineye `scp` ile gonderme

Azure VM uzerindeki ozel akisin adimlari icin [AZURE_VM_RUNBOOK.md](AZURE_VM_RUNBOOK.md) dosyasini kullanin.

## 3. Python Ortami

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Sadece runtime kurmak isterseniz `requirements.txt` kullanabilirsiniz; gelistirme ve test icin `requirements-dev.txt` daha uygundur.

## 4. Docker Servislerini Baslatma

```powershell
docker compose up -d
docker compose ps
```

Beklenen servisler:

- `uni_postgres`
- `uni_redis`
- `uni_chromadb`
- `uni_ollama`

Durum kontrolu icin:

```powershell
docker compose ps
docker compose logs --tail=50 ollama
```

Servisleri durdurmak icin:

```powershell
docker compose down
```

Volume'lari da silmek isterseniz:

```powershell
docker compose down -v
```

## 5. Ortam Degiskenleri

### 5.1 Temel kurulum

```powershell
copy .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

### 5.2 Temiz makinede model indirme ayari

`.env.example` dosyasinda embedding ve reranker varsayilan olarak lokal cache odakli davranir. Yeni bir makinede modelleri online indirmek icin su iki satirin `.env` icinde `false` oldugundan emin olun:

```text
EMBEDDING_LOCAL_FILES_ONLY=false
RERANKER_LOCAL_FILES_ONLY=false
```

Bu iki ayar yoksa ya da `true` ise, indeksleme sirasinda Hugging Face baglantisi yerine "local cache'te bulunamadi" hatasi alirsiniz.

### 5.3 Dusuk kaynakli / CPU dostu profil

Ozellikle Azure CPU VM gibi ortamlarda asagidaki profil daha guvenlidir:

```text
OLLAMA_MODEL=qwen2.5:1.5b
OLLAMA_SECONDARY_MODEL=qwen2.5:1.5b
OLLAMA_PRELOAD_MODELS=qwen2.5:1.5b
LLM_PROFILE=fast
LLM_ROUTING_MODEL=qwen2.5:1.5b
LLM_CONVERSATION_MODEL=qwen2.5:1.5b
EMBEDDING_DEVICE=cpu
RERANKER_DEVICE=cpu
RERANKER_BATCH_SIZE=4
SERVER_DEBUG=false
CONVERSATION_REWRITE_WITH_LLM=false
```

Varsayilan lokal profil ise daha buyuk Ollama modelleri ve `balanced` profil kullanir.

### 5.4 Groq / OpenAI-compatible profil

GPU bulmak zorlasirsa sadece LLM katmanini API provider'a tasiyabilirsiniz. Mevcut kod tabani `OpenAI-compatible` profil ile Groq benzeri servisleri kullanabilecek sekilde ayarlanabilir.

Ornek `.env` degerleri:

```text
LLM_PRIMARY_PROVIDER=openai_compatible
LLM_FALLBACK_PROVIDER=ollama
OPENAI_API_KEY=<API_KEY>
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-8b-instant
OPENAI_PROVIDER_NAME=groq
LLM_ROUTING_MODEL=llama-3.1-8b-instant
LLM_CONVERSATION_MODEL=llama-3.1-8b-instant
```

Notlar:

- Bu profilde FastAPI, PostgreSQL, Redis ve Chroma lokal/CPU tarafta kalir; yalnizca LLM cagrilari API provider'a gider.
- Eger API provider role bazli ayri model kullanmayacaksa `LLM_ROUTING_MODEL` ve `LLM_CONVERSATION_MODEL` alanlarini ayni modelle birakabilirsiniz.
- Groq, OpenAI-compatible endpoint kullandigi icin ayri bir SDK zorunlu degildir; mevcut istemci `OPENAI_BASE_URL` uzerinden calisabilir.

## 6. Veritabani Migration

Docker servisleri ayaktayken:

```powershell
python -m alembic upgrade head
python -m alembic current
```

Beklenen son durum:

```text
<revision-id> (head)
```

## 7. Structured Seed Verileri

RAG koleksiyonlarini indekslemek tek basina yeterli degildir. Uygulamanin bir
kismi dogrudan PostgreSQL tablolarindan okur. Bu nedenle migration sonrasinda
asagidaki seed komutlari da calistirilmalidir:

```powershell
python -m scripts.seed_curriculum_data
python -m scripts.seed_synthetic_data
```

Bu komutlar su veri alanlarini doldurur:

- `seed_curriculum_data`: `courses`, `course_prerequisites`
- `seed_synthetic_data`: `course_registration_periods`, `tuition_fee_catalog`, `students`, `student_courses`, `tuition`, `payments`, `installments`, `scholarships`, `announcements`, `office_contacts`

Bu adim olmadan su tip cevaplar bos donebilir:

- ders onkosullari
- yariyil ders listeleri
- kayit donemi bilgileri
- harc ve burs akislari

Not:

- `seed_synthetic_data` icindeki duyuru ve iletisim kayitlari demo fixture niteligindedir.
- Gercek ortama geciste bu alanlarin kurumsal kaynaklardan doldurulmasi gerekir.

## 8. Dokuman Indeksleme

Her departman kendi koleksiyonuna indekslenmelidir. Guncel koleksiyonlar:

- `student_affairs_docs`
- `academic_programs_docs`
- `finance_docs`

Komutlar:

```powershell
python scripts/index_documents.py --source data/raw/student_affairs --collection student_affairs_docs --reindex
python scripts/index_documents.py --source data/raw/academic_programs --collection academic_programs_docs --reindex
python scripts/index_documents.py --source data/raw/finance --collection finance_docs --reindex
```

Indeksleme sirasinda beklenenler:

- belge yukleme
- metin temizleme
- chunk olusturma
- embedding uretimi
- ChromaDB'ye yazma

Notlar:

- Bozuk PDF'ler artik tum pipeline'i dusurmek yerine loglanip atlanabilir.
- Ilk embedding uretiminde `BAAI/bge-m3` indirilecegi icin sure uzayabilir.
- Ilk reranker kullanimi sirasinda `seroe/bge-reranker-v2-m3-turkish-triplet` da indirilebilir.

## 9. API'yi Calistirma

```powershell
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Kontrol endpoint'leri:

- `GET /`
- `GET /health`
- `GET /docs`

Beklenen ana yuzeyler:

- `/query`
- `/auth/request-otp`
- `/auth/verify-otp`
- `/auth/resolve`
- `/auth/logout`
- `/a2a/dispatch`

## 10. Test ve Benchmark Komutlari

### Testler

```powershell
python -m pytest tests/unit -v --tb=short
python -m pytest tests/integration -v --tb=short
python -m pytest tests/integration -m "smoke or model" -v --tb=short
python -m pytest tests/integration -m slow -v --tb=short
```

### Yararli CLI scriptleri

```powershell
python scripts/test_hybrid_search.py "Cap basvurusu icin gereken not ortalamasi kactir"
python scripts/query_db.py "BIL104 dersinin on kosulu nedir"
python scripts/evaluate_rag.py
python scripts/live_question_test.py --benchmark demo_showcase_stable_turk
```

Benchmark setlerinin detayli aciklamasi icin [demo_runbook.md](demo_runbook.md) dosyasina bakin.

## 10. Sik Karsilasilan Sorunlar

### 10.1 Ollama modeli bulunamiyor

Belirti:

- `ollama model not found`
- health endpoint model yuklu degil diyor

Cozum:

```powershell
docker compose logs --tail=50 ollama
docker exec uni_ollama ollama list
```

Gerekirse `.env` icindeki `OLLAMA_PRELOAD_MODELS` ve `OLLAMA_MODEL` degerlerini kontrol edin.

### 10.2 Hugging Face offline / local cache hatasi

Belirti:

- `outgoing traffic has been disabled`
- `local_files_only` hatasi

Cozum:

`.env` icinde asagidaki iki ayari `false` yapin:

```text
EMBEDDING_LOCAL_FILES_ONLY=false
RERANKER_LOCAL_FILES_ONLY=false
```

### 10.3 Zip ile tasinan `data/raw` klasorlerinde izin hatasi

Belirti:

- `Permission denied`
- indeksleme `data/raw/...` altina giremiyor

Cozum:

```bash
sudo chown -R azureuser:azureuser ~/app/data
chmod -R u+rwX,go-rwx ~/app/data
```

Kullanici adini kendi VM kullaniciniza gore uyarlayin.

### 10.4 API calisiyor ama portu disaridan acmak istemiyorsunuz

Guvenli test icin SSH tunnel kullanin. Azure tarafindaki ayrintili ornekler [AZURE_VM_RUNBOOK.md](AZURE_VM_RUNBOOK.md) icindedir.

### 10.5 VM yeniden acildi ama API dusmus

`uvicorn` komutunu `tmux` veya `systemd` ile tekrar baslatin. Hedef makinede otomatik kapanma kullaniyorsaniz bu operasyon adimlarini ayri runbook ile saklamaniz onerilir.

## 11. Yararli Referanslar

- [README.md](../README.md)
- [DOKUMANTASYON_OKUMA_SIRASI.md](DOKUMANTASYON_OKUMA_SIRASI.md)
- [PROJE_ANATOMISI_KILAVUZU.md](PROJE_ANATOMISI_KILAVUZU.md)
- [demo_runbook.md](demo_runbook.md)
- [AZURE_VM_RUNBOOK.md](AZURE_VM_RUNBOOK.md)
- [technical_backlog.md](technical_backlog.md)
