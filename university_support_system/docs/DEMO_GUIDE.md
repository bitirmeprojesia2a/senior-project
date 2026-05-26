# Demo Rehberi

Bu rehber, özel veri paylaşmadan sistemin ana yeteneklerini göstermek için
kullanılabilecek senaryoları listeler.

## 1. Genel RAG Sorusu

Amaç: sistemin kurum belgelerinden kaynaklı cevap ürettiğini göstermek.

Örnek:

```text
Yaz okulu şartları nelerdir?
```

Beklenen davranış:

- cevap ilgili kaynaklara dayanır,
- debug/demo modunda kaynak özeti görünür,
- kaynakta olmayan detaylar uydurulmaz.

## 2. Takip Sorusu ve Bağlam

Amaç: kısa takip sorularının önceki konuyla ilişkilendirildiğini göstermek.

Örnek:

```text
ÇAP başvuru şartları nelerdir?
Peki başvuru tarihleri ne?
```

Beklenen davranış:

- ikinci soru ÇAP tarihleri takip sorusu olarak anlaşılır,
- uygunsa takvim veya ilgili kaynak kullanılır.

## 3. Eksik Bilgi Tamamlama

Amaç: sistemin eksik bilgiyi tahmin etmek yerine kullanıcıdan istediğini
göstermek.

Örnek:

```text
Fizik öğretmenliği ücreti ne kadar?
```

Öğrenci türü gerekiyorsa sistem Türk/uluslararası gibi eksik bilgiyi istemeli,
kullanıcı cevap verdikten sonra sonucu tamamlamalıdır.

## 4. Yapılandırılmış Veri Sorgusu

Amaç: sistemin sadece belge chunk'ı değil, yapılandırılmış veri veya scoped
kaynak kullanabildiğini göstermek.

Örnekler:

```text
Bilgisayar Mühendisliği ders programı nedir?
Fizik öğretmenliği ücreti ne kadar?
Bu dersin önkoşulu var mı?
```

Beklenen davranış:

- uygunsa yapılandırılmış kaynak tercih edilir,
- cevap kısa ve kaynak farkındalığıyla verilir.

## 5. OTP / Kişisel İşlem

Amaç: kişisel veri koruma akışını göstermek.

Örnek:

```text
Hangi dersleri aldım?
```

Beklenen davranış:

- kişisel veri gerekiyorsa doğrulama istenir,
- ekran görüntülerinde OTP/e-posta/öğrenci numarası sansürlenir.

## 6. Transkript Yükleme

Amaç: transkript analizini göstermek.

Örnek:

```text
Mezun olmam için kaç AKTS gerekiyor, bu transkripti inceleyip cevaplar mısın?
```

Takip soruları:

```text
Hangi dersleri almışım?
Kaç tane AA dersim var?
Kaldığım ders var mı?
Mezuniyet için kaç AKTS kaldı?
```

Beklenen davranış:

- sistem transkript fact'lerini çıkarır,
- takip soruları yüklenen transkript bağlamını kullanır,
- public ekran görüntülerinde kişisel alanlar sansürlenir.

## 7. Genel Belge Yükleme

Amaç: transkript dışı belge anlama yeteneğini göstermek.

Örnek:

```text
Bu belge nedir?
Belgede hangi alanlar var ve değerleri ne?
Bu belgeyi nereye teslim etmeliyim?
```

Beklenen davranış:

- belge özeti yüklenen dosyadan üretilir,
- alan/değer cevapları çıkarılan belge fact'lerinden gelir,
- prosedür sorularında gerekirse belge + kurum RAG hibrit akışı kullanılır.

## 8. Çoklu Ajan / Çoklu Konu Sorusu

Amaç: paralel uzman yönlendirmesini göstermek.

Örnek:

```text
Bilgisayar Mühendisliği öğrencisiyim. Yaz okulunda ders almak istiyorum ama
aynı dönemde zorunlu stajım da var; harç borcum varsa kayıt yaptırabilir miyim,
yaz okulunda kaç ders alabilirim ve ÇAP/önkoşul açısından dikkat etmem gereken
şartlar nelerdir?
```

Beklenen davranış:

- soru alt başlıklara ayrılır,
- birden fazla departman/uzman çalışabilir,
- final cevap konu başlıklarına göre düzenlenir,
- demo/debug modunda ajan akışı paralelliği gösterir.

## 9. Kanıt Yok / Güvenli Cevap

Amaç: sistemin kaynak yokken uydurmadığını göstermek.

Örnek:

```text
Kaynaklarda olmayan özel bir tarih veya belgede bulunmayan bir alan sor.
```

Beklenen davranış:

- sistem bilginin bulunamadığını veya güvenilir çıkarılamadığını söyler,
- hangi ek bilgi veya kaynağın gerektiğini belirtebilir.

## Ekran Görüntüsü Güvenliği

Rapor veya public repo için ekran görüntüsü eklemeden önce şunları sansürleyin:

- öğrenci numarası,
- kimlik numarası,
- e-posta adresi,
- OTP kodu,
- gerekiyorsa notlar,
- yüklenen belgelerdeki kişisel alanlar,
- özel Slack workspace/kanal bilgileri.
