# Kurulum

Bu rehber public repo için lokal geliştirme ortamının nasıl hazırlanacağını
anlatır. Gerçek kurum verisi, model cache dosyaları, vector store verisi ve
secret değerleri repoya dahil değildir.

## Gereksinimler

- Python 3.11+
- Docker Desktop
- Docker Compose
- PostgreSQL / Redis / ChromaDB için Docker veya kendi servisleriniz
- OpenAI-compatible bir LLM provider veya lokal model ayarı
- Slack entegrasyonu test edilecekse Slack app bilgileri

## Repo Yapısı

```text
app/                         uygulama ve servis kodları
scripts/                     seed, indexleme, rollout ve yardımcı scriptler
tests/                       public-safe unit testler
docs/                        public dokümantasyon
data/raw/                    lokal kaynak belgeleri, git dışında
data/models/                 lokal model cache'i, git dışında
data/chroma/                 lokal vector store, git dışında
```

`data/` altındaki çalışma klasörleri bilinçli olarak ignore edilir. Bunlar
public kaynak dosyası değil, lokal runtime girdileridir.

## Python Ortamı

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-dev.txt
```

Sadece runtime bağımlılıkları gerekiyorsa deployment yapınıza göre runtime
requirements dosyası kullanılabilir. Lokal geliştirme ve test için
`requirements-dev.txt` daha uygundur.

## Ortam Değişkenleri

Lokal ortam dosyasını oluşturun:

```powershell
copy .env.example .env
```

Tipik alanlar:

```env
LLM_PROVIDER=
LLM_MODEL=
DATABASE_URL=
REDIS_URL=
SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
SLACK_APP_TOKEN=
```

`.env` dosyasını commit etmeyin.

## Docker Servisleri

Temel compose stack'i başlatmak için:

```powershell
docker compose up -d
docker compose ps
```

Windows üzerinde Docker çalışmıyorsa `dockerDesktopLinuxEngine` pipe hatası
görülebilir. Docker Desktop'ı açıp tekrar deneyin.

## Kendi Verinizi Ekleme

Public repoda gerçek kurum belgeleri bulunmaz. Lokal belgelerinizi
organizasyonunuza göre `data/raw/` altına ekleyebilirsiniz.

Örnek:

```text
data/raw/student_affairs/
data/raw/academic_programs/
data/raw/finance/
```

Belgeleri ekledikten sonra kendi profiliniz ve kaynak kataloğunuza uygun
seed/indexleme scriptlerini çalıştırmanız gerekir.

## Model Cache

Model dosyaları repoda tutulmaz. Lokal embedding veya reranker modeli
kullanıyorsanız bunları `data/models/` altında veya Hugging Face cache
dizininizde tutabilirsiniz.

Notlar:

- CPU ortamlarında güvenli varsayılan precision kullanılmalıdır.
- GPU ortamlarında destekleniyorsa FP16 açılabilir.
- İnternet erişimi sınırlıysa servisleri başlatmadan önce model cache'i
  hazırlanmalıdır.

## Testleri Çalıştırma

Tüm public-safe unit testler:

```powershell
pytest tests/unit -q
```

Odaklı örnekler:

```powershell
pytest tests/unit/test_uploaded_document_arbiter.py -q
pytest tests/unit/test_transcript_service.py -q
pytest tests/unit/test_multi_intent_planner.py -q
pytest tests/unit/test_dynamic_platform.py -q
```

Sadece dokümantasyon değişikliklerinde tüm Docker stack'i kaldırmak genelde
gerekmez.

## Smoke Kontrolleri

Yararlı lokal kontroller:

```powershell
git status --short
pytest tests/unit -q
docker compose ps
```

Slack açıksa aynı token setiyle tek bot instance'ının çalıştığından emin olun.

## Sık Görülen Sorunlar

| Belirti | Olası neden |
| --- | --- |
| Docker pipe hatası | Docker Desktop çalışmıyor. |
| Servis unhealthy | Eksik env değeri, yanlış env tipi veya hazır olmayan bağımlılık. |
| Model indirme başlıyor | Lokal model cache eksik. |
| Slack cevapları çift geliyor | Aynı Slack app token'ı ile birden fazla bot çalışıyor. |
| RAG doğru cevap bulamıyor | Kaynak belgeler eklenmemiş veya indexlenmemiş. |

## Public Güvenlik Kontrol Listesi

Paylaşmadan önce:

- `.env` commit edilmemeli,
- `data/raw/` commit edilmemeli,
- yüklenen öğrenci dosyaları commit edilmemeli,
- veritabanı dump'ları commit edilmemeli,
- model cache dosyaları commit edilmemeli,
- kişisel veri içeren ekran görüntüleri sansürlenmeli.
