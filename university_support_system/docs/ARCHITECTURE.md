# Mimari

Bu doküman public sürüm için sistemin yüksek seviyeli mimarisini açıklar. Özel
kaynak listeleri, canlı ortam ayarları, benchmark arşivleri ve iç karar notları
public repoda yer almaz.

## Tasarım Hedefleri

Sistem beş ana hedef etrafında tasarlanmıştır:

1. **Kaynaklı cevap üretmek:** Cevaplar kurum belgelerine, yapılandırılmış
   verilere veya yüklenen belgeye dayanmalıdır.
2. **Doğru sorumluyu bulmak:** Her soru doğru departman veya uzman akışına
   gitmelidir.
3. **Bağlamı korumak:** Kısa takip soruları thread/DM bağlamıyla
   ilişkilendirilebilmelidir.
4. **Belgeyi ayırmak:** Yüklenen dosyalar genel RAG kaynaklarıyla karışmadan
   ayrı değerlendirilmelidir.
5. **Güvenli fallback vermek:** Kanıt zayıfsa sistem uydurmak yerine bunu açıkça
   söylemelidir.

## Katmanlı Yapı

```text
İstemci Katmanı
  - Slack mesajları
  - REST API istekleri
  - yüklenen dosyalar

Uygulama Katmanı
  - FastAPI endpointleri
  - Slack event işleme
  - auth/session yardımcıları
  - dosya yükleme işleme

Bağlam ve Planlama Katmanı
  - thread/DM bağlamı
  - yüklenen belge ayrımı
  - belge anlama
  - çoklu konu planlayıcı
  - routing politikası

Orkestrasyon Katmanı
  - ana orkestratör
  - departman yönlendirme
  - uzman yönlendirme
  - final cevap koordinasyonu

Ajan Katmanı
  - departman ajanları
  - uzman ajanlar
  - duyuru/takvim yetenek ajanları

Bilgi Katmanı
  - vector retrieval
  - yapılandırılmış veri sorguları
  - belge fact'leri
  - ders programı/takvim verisi
  - reranking
  - LLM sentezi
```

## İstek Yaşam Döngüsü

### 1. Girdinin Alınması

Sistem mesajı Slack veya REST API üzerinden alır. Slack akışında mesajın auth
komutu mu, dosya yükleme mi, yoksa normal soru mu olduğu kontrol edilir.

### 2. Yüklenen Belge Kararı

Konuşmada aktif bir belge varsa, uploaded-document arbiter yeni sorunun hangi
hedefe gitmesi gerektiğine karar verir:

- yüklenen belge,
- genel kurum RAG akışı,
- belge + RAG hibrit akışı,
- netleştirme mesajı.

Bu katman, belgeye sorulması gereken bir sorunun genel kaynaklara kaçmasını
engellemek için vardır.

### 3. Bağlam Çözümleme

Sistem son konuşma durumunu kontrol eder:

- önceki konu,
- seçilmiş duyuru listesi,
- eksik bilgi,
- aktif transkript veya belge,
- thread/DM ayrımı.

Bu bilgiler şu tarz kısa mesajları yorumlamak için kullanılır:

```text
Peki tarihleri ne?
2. duyuruyu özetle
Belgeye göre cevaplar mısın?
Diğerleri boş mu?
```

### 4. Routing ve Planlama

Basit sorularda router en uygun departmanı veya yeteneği seçer.

Uzun ve çok konulu sorularda çoklu konu planlayıcı mesajı alt görevlere
bölebilir.

```text
Ana Orkestratör
  -> Çoklu Konu Planlayıcı
  -> Paralel alt görevler
      - öğrenci işleri / kayıt
      - öğrenci işleri / staj
      - akademik programlar / müfredat
      - finans / ödeme
      - takvim veya duyuru yeteneği
  -> Final sentez
```

### 5. Retrieval veya Yapılandırılmış Sorgu

Seçilen her ajan kendi kaynak ailesini kullanır. Soruya göre şu kaynaklardan
yararlanılabilir:

- belge chunk'ları üzerinde vector search,
- yapılandırılmış tablo sorgusu,
- akademik takvim sorgusu,
- duyuru sorgusu,
- yüklenen belge fact'leri,
- transkript fact'leri.

### 6. Final Sentez

Final cevap eldeki kanıtları birleştirir. Demo/debug modunda üretim türü, kaynak
özeti ve görünür ajan akışı da gösterilebilir.

## Ajan Sahipliği

Üniversite odaklı profil şu sorumluluk alanlarını kullanır:

| Alan | Örnekler |
| --- | --- |
| Öğrenci işleri | kayıt, mezuniyet, staj, yaz okulu |
| Akademik programlar | müfredat, önkoşul, ders programı, yönergeler |
| Finans | ücret, ödeme, harç/borç konuları |
| Duyuru/etkinlik | duyurular, etkinlikler, tarih odaklı akışlar |
| Yüklenen belge QA | transkript ve genel belge soruları |

Bu ayrım sistemi gereksiz karmaşıklaştırmak için değil, yanlış kaynak
seçimlerini azaltmak için yapılmıştır.

## Yüklenen Belge Mimarisi

Yüklenen belgeler normal RAG'dan önce ayrı bir belge anlama katmanından geçer.

```text
Yüklenen dosya
  -> metin/OCR çıkarımı
  -> belge türü sınıflandırma
  -> fact çıkarımı
      - alanlar
      - tablolar
      - transkript dersleri
      - tarih/sonuç/durum bilgileri
  -> belge soru sınıflandırma
  -> belge cevabı veya belge + RAG hibrit cevabı
```

Public-safe örnek belge kategorileri:

- transkript,
- ders programı belgesi,
- form belgesi,
- öğrenci durum belgesi,
- sonuç/sertifika belgesi,
- akademik takvim,
- genel belge.

Çıkarım güveni düşükse sistem kesin cevap vermemeli, sınırlı veya uyarılı cevap
üretmelidir.

## Çoklu Konu Planlama

Çoklu konu planlayıcı, birden fazla bağımsız konu içeren uzun sorular için
tasarlanmıştır.

Örnek soru:

```text
Yaz okulunda ders almak istiyorum ama stajım da var. Harç borcum varsa kayıt
yapabilir miyim, kaç ders alabilirim ve ÇAP açısından neye dikkat etmeliyim?
```

Olası alt görevler:

| Alt görev | Sahip |
| --- | --- |
| Yaz okulu ders sınırı | Öğrenci işleri / yaz okulu |
| Stajla çakışma | Öğrenci işleri / staj |
| Harç borcu ve kayıt | Öğrenci işleri + finans |
| ÇAP koşulları | Akademik programlar |
| Mezuniyet etkisi | Öğrenci işleri / mezuniyet |

Bir alt görevde kaynak zayıfsa yalnız o bölümde "net bilgi bulunamadı" denir.
Diğer bölümler normal şekilde cevaplanabilir.

## Duyuru ve Takvim Akışı

Duyuru akışı şunları destekler:

- güncel duyuruları listeleme,
- numara veya başlıkla duyuru seçme,
- seçilen duyuruyu özetleme.

Takvim akışı, ilgili takvim kaynağı varsa tarih sorularını cevaplar. Her tarih
sorusu duyuru araması değildir; akademik takvim soruları takvim farkındalığı
gerektirir.

## Dinamik Kurum Katmanı

Dinamik kurum katmanı, kuruma özel yapılandırmayı mümkün olduğunca core
runtime'dan ayırmayı hedefler.

Bu katmanda şu kavramlar bulunur:

- kurum/proje profili,
- aktif domain,
- aktif ajanlar,
- kaynak kataloğu,
- desteklenen yetenekler,
- replay/demo seti.

Amaç, mevcut üniversite senaryosunu bozmadan farklı kurumlar için ayrı destek
sistemleri hazırlanabilmesini kolaylaştırmaktır.

## Hata ve Fallback Davranışı

Beklenen güvenli fallback durumları:

- ilgili kaynak bulunamadı,
- yüklenen belge güvenilir biçimde okunamadı,
- istenen alan var ama boş görünüyor,
- soru belge ve kurum kaynakları arasında belirsiz kaldı,
- çok konulu sorunun bir alt başlığında yeterli kanıt yok.

Bu durumlarda sistem sınırlamayı açıkça belirtmelidir.

## Public Repo Sınırı

Public repo kodu ve mimariyi içerir; özel runtime verilerini içermez. Şu
dosyalar lokal kalır:

- ham kurum belgeleri,
- öğrenci belgeleri,
- veritabanı dump'ları,
- model cache'leri,
- benchmark arşivleri,
- özel raporlar ve trace dosyaları.
