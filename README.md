# University Support System

LLM, RAG ve çok ajanlı orkestrasyon kullanan kurumsal destek sistemi prototipi.

Proje ilk olarak üniversite öğrenci destek senaryoları için geliştirildi. Daha
sonra Slack entegrasyonu, belge ve transkript yükleme, takip sorusu yönetimi,
duyuru/akademik takvim akışları, uzun sorular için çoklu uzman yönlendirmesi ve
farklı kurumlara uyarlanabilir profil altyapısı eklendi.

## Projenin Amacı

Kurum destek sistemlerinde kullanıcı soruları çoğu zaman tek bir temiz belgeye
karşılık gelmez. Bir öğrenci aynı konuşmada harç borcu, ders kaydı, yaz okulu,
staj çakışması, mezuniyet AKTS'si veya yüklediği transkript hakkında soru
sorabilir. Klasik bir chatbot bu durumda bağlamı kaçırabilir, yanlış kaynağa
gidebilir veya belgeden cevaplaması gereken soruyu genel kaynaklardan
cevaplayabilir.

Bu proje daha kontrollü bir akış kurmayı hedefler:

1. Kullanıcının niyetini ve konuşma bağlamını anlamak.
2. Sorunun genel kurum kaynaklarına mı, yoksa yüklenen belgeye mi ait olduğunu
   ayırmak.
3. Soruyu doğru departman ve uzman ajanlara yönlendirmek.
4. Doğru kaynak ailesinden kanıt toplamak.
5. Cevabı kaynak bilgisi ve gerekirse ajan akışıyla birlikte üretmek.

## Temel Yetenekler

| Alan | Açıklama |
| --- | --- |
| RAG cevapları | Kurum belgelerinden kaynaklı cevap üretir. |
| Çok ajanlı yönlendirme | Öğrenci işleri, akademik programlar, finans, duyuru ve uzman ajanlara yönlendirir. |
| Belge yükleme | Slack üzerinden yüklenen transkript ve genel belgeleri işler. |
| Transkript analizi | Ders, kredi, AKTS, not, GNO, başarılı/başarısız ders bilgilerini çıkarır. |
| Takip soruları | Thread/DM bağlamını kullanarak kısa devam sorularını yorumlar. |
| Duyuru akışı | Güncel duyuruları listeler ve seçilen duyuruyu özetler. |
| Takvim soruları | Uygun durumlarda akademik takvim kaynaklarından tarih cevabı üretir. |
| Çoklu konu planlama | Uzun soruları alt başlıklara ayırıp birden fazla uzmanı çalıştırabilir. |
| Dinamik kurum altyapısı | Aynı sistemin farklı kurumlara uyarlanabilmesi için profil tabanlı temel sunar. |

## Yüksek Seviyeli Mimari

```text
Slack / REST API / Yüklenen Dosyalar
        |
        v
Uygulama Katmanı
        |
        v
Bağlam ve Planlama
  - konuşma bağlamı
  - belge/rag ayrımı
  - çoklu konu planlayıcı
        |
        v
Ana Orkestratör
        |
        +--> Departman ajanları
        +--> Uzman ajanlar
        +--> Duyuru/takvim yetenekleri
        +--> Belge anlama katmanı
        |
        v
Retrieval / Yapılandırılmış Veri / LLM Sentezi
        |
        v
Cevap + kaynak özeti + opsiyonel ajan akışı
```

## Klasör Yapısı

```text
university_support_system/
  app/                 uygulama kodları
  scripts/             seed, indexleme, rollout ve yardımcı scriptler
  tests/               public sürüm için güvenli unit testler
  docs/                public dokümantasyon
  data/                lokal runtime verileri, git dışında
```

Başlamak için:

- [Uygulama README'i](university_support_system/README.md)
- [Mimari açıklama](university_support_system/docs/ARCHITECTURE.md)
- [Kurulum rehberi](university_support_system/docs/SETUP.md)
- [Slack entegrasyonu](university_support_system/docs/SLACK.md)
- [Dinamik kurum altyapısı](university_support_system/docs/DYNAMIC_PLATFORM.md)
- [Demo rehberi](university_support_system/docs/DEMO_GUIDE.md)

## Hızlı Kurulum

```powershell
cd university_support_system
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
```

`.env` dosyasına kendi LLM, veritabanı ve Slack ayarlarınızı girin. Secret
değerlerini repoya eklemeyin.

## Test

```powershell
cd university_support_system
pytest tests/unit -q
```

## Public Sürüm Kapsamı

Bu public repoda bilinçli olarak şu dosyalar yer almaz:

- gerçek kurum belgeleri,
- kişisel öğrenci dosyaları,
- veritabanı dump'ları,
- vector store verileri,
- model cache dosyaları,
- özel benchmark arşivleri,
- Slack veya LLM secret değerleri.

Sistemi kendi kurum verinizle çalıştırmak için belgelerinizi lokal olarak
`data/raw/` altına ekleyip ilgili seed/indexleme scriptlerini çalıştırmanız
gerekir.

## Güvenlik ve Veri Notu

Yüklenen dosyalar kişisel veri içerebilir. Demo ekran görüntülerinde ve rapor
çıktılarında öğrenci numarası, kimlik numarası, e-posta adresi, not bilgileri ve
doğrulama kodları sansürlenmelidir.
