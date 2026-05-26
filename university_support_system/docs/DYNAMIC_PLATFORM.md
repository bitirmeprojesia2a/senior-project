# Dinamik Kurum Altyapısı

Dinamik kurum altyapısı, aynı destek sistemi kod tabanının farklı kurumlara veya
organizasyonlara uyarlanabilmesi için hazırlanan profil tabanlı temeldir.

Bu yapı mevcut üniversite senaryosunun yerine geçmek için değil, çalışan sistemi
koruyarak gelecekte farklı kurumlara daha rahat uyarlanabilmek için
tasarlanmıştır.

## Motivasyon

Dinamik katman olmadan her yeni kurum için koda özel kurallar, özel ajan adları,
özel kaynak yolları ve özel routing koşulları eklemek gerekir. Bu yaklaşım demo
için çalışabilir; fakat proje büyüdükçe kırılgan hale gelir.

Dinamik altyapı yaklaşımı, kuruma özel bilgileri şu yapılara taşımayı hedefler:

- profil dosyaları,
- kaynak katalogları,
- aktif ajan listeleri,
- desteklenen yetenekler,
- demo/replay setleri.

## Temel Kavramlar

| Kavram | Anlamı |
| --- | --- |
| Tenant/profil | Belirli bir kurum veya proje yapılandırması. |
| Domain | Üniversite desteği, şirket içi destek veya kamu hizmeti gibi genel alan. |
| Agent pack | O profil için aktif departman ve uzmanlar. |
| Source catalog | Profile ait belge, API, tablo veya web kaynakları. |
| Source adapter | Kaynağın nasıl okunacağı: PDF, web, SQL, API, Slack upload vb. |
| Capability | Policy QA, ücret sorgusu, program sorgusu veya belge QA gibi desteklenen iş türü. |

## Örnek Profil Türleri

### Üniversite Destek Profili

- öğrenci işleri,
- akademik programlar,
- finans,
- duyurular,
- akademik takvim,
- transkript analizi,
- ders programları.

### Şirket İçi Destek Profili

- insan kaynakları,
- IT destek,
- bordro/ödeme,
- onboarding,
- iç duyurular,
- departman iletişimleri.

### Kamu Hizmeti Profili

- hizmet başvuruları,
- gerekli belgeler,
- randevu tarihleri,
- birim iletişimleri,
- kamu duyuruları.

## Beklenen Profil Hazırlama Akışı

```text
Profil oluştur
  -> domain seç
  -> agent pack etkinleştir
  -> kaynak kataloğu tanımla
  -> yapılandırmayı doğrula
  -> kaynakları indexle
  -> replay/demo testleri çalıştır
  -> güvenlik ve veri sınırlarını kontrol et
```

## Mevcut Sistemle İlişkisi

Mevcut üniversite destek runtime'ı ana çalışan senaryo olarak kalır. Dinamik
katman bunun çevresinde kontrollü bir hazırlık katmanıdır.

Önemli sınırlar:

- Public demo profilleri gerçek kurum verisi içermez.
- Dinamik profiller özel üniversite kaynak dosyalarına bağımlı olmamalıdır.
- Yeni kurum kendi kaynaklarını ve doğrulama verilerini getirmelidir.
- Canlı kullanım için ayrıca güvenlik ve operasyon kontrolü gerekir.

## Public Olarak Neler Bulunabilir?

Public repoda şunlar bulunabilir:

- profil şemaları veya örnekleri,
- private veri içermeyen dummy demo profiller,
- doğrulama scriptleri,
- kişisel veri içermeyen test fixture'ları,
- mimari dokümantasyon.

Public repoda şunlar bulunmamalıdır:

- gerçek kurum belgeleri,
- kişisel kullanıcı dosyaları,
- production secret değerleri,
- veritabanı dump'ları,
- model cache,
- özel benchmark trace'leri.

## Sınırlamalar

Bu katman tam bir SaaS ürünü değil, mimari temel ve demo hazırlık katmanıdır.
Production seviyesinde çok kiracılı bir platform için ayrıca şunlar gerekir:

- daha güçlü tenant izolasyonu,
- kaynak yönetimi için admin panel,
- rol tabanlı erişim kontrolü,
- audit logları,
- veri saklama ve silme politikaları,
- kaynak onay akışı,
- deployment izleme.
