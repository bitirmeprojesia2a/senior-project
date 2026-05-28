# A2A PROTOKOLÜ İLE KURUMSAL DESTEK VE İŞ AKIŞI SİSTEMİ

Bu proje; RAG, LLM tabanlı cevap sentezi, Slack entegrasyonu ve çok ajanlı
orkestrasyon kullanan bir kurumsal destek sistemidir.

Sistem ilk olarak üniversite öğrenci destek senaryoları üzerinden geliştirildi.
Öğrenci işleri, akademik programlar, finans, ders programı, duyuru, akademik
takvim, staj, yaz okulu, mezuniyet koşulları ve yüklenen öğrenci belgeleri gibi
konularda soru cevaplayabilir. Daha sonra aynı mimarinin farklı kurumlara da
uyarlanabilmesi için profil tabanlı dinamik altyapı hazırlanmıştır.

> Public sürüm notu: Bu repoda gerçek kurum belgeleri, kişisel öğrenci
> dosyaları, veritabanı dump'ları, model cache dosyaları, benchmark arşivleri ve
> secret değerleri bulunmaz.

## Neden Böyle Bir Sistem?

Kurum destek süreçleri pratikte dağınıktır. Kullanıcı kısa bir takip sorusu
sorabilir, transkript yükleyebilir, aynı mesajda birden fazla konuya değinebilir
veya cevabı bir yönetmelikten değil akademik takvimden bekleyebilir. Bu nedenle
soruyu doğrudan tek bir LLM çağrısına göndermek yeterli değildir.

Bu sistem, cevap üretmeden önce şu kararları vermeye çalışır:

- Soru genel kurum kaynaklarına mı ait, yoksa yüklenen belgeyle mi ilgili?
- Cevabın sahibi hangi departman veya uzman ajan?
- Cevap için belge parçası, yapılandırılmış tablo, takvim, duyuru veya hibrit
  kaynak kullanımı mı gerekiyor?
- Soru önceki konuşmanın devamı mı?
- Soru alt başlıklara bölünecek kadar uzun ve karmaşık mı?

## Temel Özellikler

### 1. Kaynaklı RAG Cevapları

Retrieval katmanı indekslenmiş belgelerde arama yapar ve ilgili parçaları cevap
sentezi adımına gönderir. Amaç, cevabın doğru kaynak ailesine dayanması ve
debug/demo çıktılarında kaynak özetinin görülebilmesidir.

### 2. Departman ve Uzman Ajanlar

Sistem sorumlulukları departmanlara ve uzman akışlara ayırır. Örnek alanlar:

- öğrenci işleri,
- akademik programlar,
- finans,
- duyuru ve etkinlik,
- kayıt işlemleri,
- mezuniyet,
- staj/yaz okulu,
- müfredat/önkoşul,
- öğrenim ücreti/ödeme.

Bu ayrım, bir finans sorusunun alakasız bir yönetmelikten veya bir transkript
sorusunun genel kurum belgelerinden cevaplanmasını azaltmak için kullanılır.

### 3. Yüklenen Belge İşleme

Slack üzerinden yüklenen dosyalar normal RAG akışından önce ayrı bir belge
anlama katmanından geçer. Bu katman şu belge türlerini yorumlayabilir:

- transkript,
- form,
- öğrenci durum belgesi,
- akademik takvim,
- sonuç/sertifika türü belgeler,
- genel PDF belgeleri.

Transkriptlerde ders, kredi, AKTS, not, GNO ve başarılı/başarısız ders bilgileri
çıkarılabilir. Genel belgelerde belge özeti, alan-değer listesi ve belgeye göre
soru cevaplama desteklenir.

### 4. Konuşma Bağlamı ve Takip Soruları

Slack tarafında thread/DM bağlamı tutulur. Sistem önceki mesajları, seçilen
duyuru listesini, eksik bilgi durumunu ve aktif belgeyi kullanarak kısa takip
sorularını yorumlamaya çalışır.

Örnek:

```text
Kullanıcı: ÇAP başvuru şartları nelerdir?
Kullanıcı: Peki tarihleri ne?
```

İkinci soru, yeni ve kopuk bir tarih sorusu olarak değil, ÇAP başvuru tarihleri
takip sorusu olarak ele alınabilir.

### 5. Çoklu Konu Planlama

Uzun sorular birden fazla bağımsız konu içerebilir. Çoklu konu planlayıcı bu
soruları alt başlıklara ayırıp ilgili uzmanlara yönlendirebilir.

Örnek:

```text
Yaz okulunda ders almak istiyorum, stajım da var, harç borcum varsa kayıt
yapabilir miyim, kaç ders alabilirim, ÇAP ve önkoşul açısından neye dikkat
etmeliyim?
```

Olası alt başlıklar:

- yaz okulu koşulları,
- stajla çakışma,
- harç borcu ve ders kaydı,
- ders/önkoşul kısıtları,
- ÇAP koşulları,
- mezuniyet etkisi.

### 6. Duyuru ve Takvim Akışları

Sistem duyuru listeleme, seçilen duyuruyu özetleme ve uygun durumlarda akademik
takvimden tarih cevabı üretme akışlarını destekler.

### 7. Dinamik Kurum Altyapısı

Dinamik altyapı, aynı kod tabanının ileride farklı kurumlara uyarlanabilmesi
için hazırlanmıştır. Yeni bir kurum kendi birimlerini, ajanlarını, kaynak
kataloğunu ve desteklediği soru tiplerini tanımlayabilir.

## Mimari Özet

```text
İstemci Katmanı
  - Slack
  - REST API
  - yüklenen dosyalar

Uygulama Katmanı
  - FastAPI
  - Slack servisi
  - auth/session yardımcıları

Bağlam ve Planlama
  - konuşma hafızası
  - yüklenen belge ayrımı
  - belge anlama
  - çoklu konu planlayıcı

Orkestrasyon
  - ana router
  - departman yönlendirme
  - uzman yönlendirme
  - final cevap koordinasyonu

Bilgi Katmanı
  - vector retrieval
  - yapılandırılmış veri
  - belge fact'leri
  - takvim/duyuru verisi
  - LLM sentezi
```

Detaylar için [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) dosyasına bakın.

## Kurulum

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
```

`.env` dosyasına kendi LLM, veritabanı ve Slack bilgilerinizi ekleyin. Secret
değerlerini commit etmeyin.

Daha ayrıntılı bilgi için [docs/SETUP.md](docs/SETUP.md) dosyasına bakın.

## Veri Hazırlama

Public repoda gerçek kurum belgeleri bulunmaz. Kendi kaynaklarınızı lokal olarak
`data/raw/` altına ekleyip ilgili seed/indexleme scriptlerini çalıştırmanız
gerekir.

Örnek lokal yapı:

```text
data/raw/student_affairs/
data/raw/academic_programs/
data/raw/finance/
```

Bu klasörler git dışında tutulur.

## Test

```powershell
pytest tests/unit -q
```

Odaklı test örnekleri:

```powershell
pytest tests/unit/test_uploaded_document_arbiter.py -q
pytest tests/unit/test_transcript_service.py -q
pytest tests/unit/test_multi_intent_planner.py -q
pytest tests/unit/test_dynamic_platform.py -q
```

## Dokümantasyon

- [Mimari](docs/ARCHITECTURE.md)
- [Kurulum](docs/SETUP.md)
- [Slack entegrasyonu](docs/SLACK.md)
- [Dinamik kurum altyapısı](docs/DYNAMIC_PLATFORM.md)
- [Demo rehberi](docs/DEMO_GUIDE.md)

## Public Repo Sınırları

Bu repo kodu ve mimariyi göstermek için hazırlanmıştır. Şu dosyalar lokal
kalmalıdır:

- `.env`
- `data/raw/`
- `data/models/`
- `data/chroma/`
- veritabanı dump'ları
- benchmark arşivleri
- özel raporlar
- yüklenen öğrenci belgeleri

## Güvenlik Notları

Yüklenen dosyalar kişisel veri içerebilir. Ekran görüntülerinde ve demo
raporlarında öğrenci numarası, kimlik numarası, e-posta adresi, notlar ve
doğrulama kodları sansürlenmelidir. LLM cevapları özellikle resmi veya kritik
süreçlerde kaynak özetleriyle birlikte değerlendirilmelidir.
