# Slack Entegrasyonu

Slack, prototipin ana etkileşim arayüzüdür. Normal soru-cevap, takip soruları,
OTP tarzı doğrulama, dosya yükleme, transkript analizi ve demo amaçlı ajan akışı
gösterimi bu arayüz üzerinden yapılabilir.

## Mesaj Akışı

```text
Slack mesajı
  -> Slack servisi
  -> komut / dosya / bağlam kontrolleri
  -> gerekiyorsa yüklenen belge ayrımı
  -> ana orkestratör
  -> ajanlar / retrieval / yapılandırılmış veri / LLM
  -> Slack cevabı
```

## Ortam Değişkenleri

```env
SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
SLACK_APP_TOKEN=
```

Socket Mode kullanılıyorsa `SLACK_APP_TOKEN` gerekir. HTTP tabanlı Slack
kurulumlarında public endpoint ve signing-secret doğrulaması ayrıca yapılır.

## Lokal Çalıştırma

Örnek lokal komut:

```powershell
python -m scripts.run_slack_bot --runtime inprocess
```

Servis tabanlı deployment için önce gerekli Docker servislerinin sağlıklı
olduğunu kontrol edin:

```powershell
docker compose ps
```

## Konuşma Bağlamı

Slack entegrasyonu konuşma seviyesinde bağlam tutar:

- Thread ve DM bağlamı ayrıdır.
- Yeni thread yeni konuşma gibi davranabilir.
- Kısa takip soruları önceki konuya bağlanabilir.
- Yüklenen belge bağlamı sonraki belge soruları için korunur.
- Auth komutları yüklenen belge bağlamını silmemelidir.

Bağlam gerektiren örnekler:

```text
Peki tarihleri ne?
Belgeye göre cevaplar mısın?
2. duyuruyu özetle
Diğer alanlar boş mu?
```

## Yüklenen Dosyalar

Slack dosya akışı normal kurum RAG akışından önce değerlendirilir. Sistem önce
sorunun yüklenen belgeyle mi yoksa genel kurum kaynaklarıyla mı ilgili olduğuna
karar verir.

Desteklenen örnekler:

| Belge türü | Örnek sorular |
| --- | --- |
| Transkript | Kaç AKTS tamamlanmış? Hangi derslerden kalmışım? |
| Form | Hangi alanlar dolu? Bu form ne için kullanılır? |
| Akademik takvim | Sınavlar veya başvurular ne zaman? |
| Sonuç/sertifika | Sonuç ne? Belge ne zaman alınmış? |
| Genel PDF | Belgeyi özetle veya içeriğine göre cevapla. |

Belge istenen alanı içermiyorsa veya değer güvenilir biçimde okunamıyorsa cevap
bunu açıkça söylemelidir.

## OTP ve Kişisel Akışlar

Bazı akışlarda kimlik doğrulaması gerekebilir. Demo veya raporda:

- öğrenci numarası,
- e-posta adresi,
- OTP kodu,
- özel belge alanları,
- ham yüklenen dosyalar

gizlenmelidir.

## Ajan Akışı Çıktısı

Demo modunda bot cevabın nasıl üretildiğini gösterebilir.

Örnek:

```text
Ana Orkestratör -> Paralel:
  [Öğrenci İşleri Orkestratörü -> Kayıt İşleri Uzman Ajanı]
  [Akademik Programlar Orkestratörü -> Müfredat Uzman Ajanı]
  [Finans Orkestratörü -> Öğrenim Ücreti Uzman Ajanı]
-> Ana Orkestratör
```

Bu çıktı, karmaşık soruların tek bir düz prompt yerine farklı uzmanlara
bölündüğünü göstermek için kullanılır.

## Demo Senaryoları

İyi Slack demo senaryoları:

1. Genel bir yönetmelik/policy sorusu sormak.
2. Önceki cevaba bağlı kısa takip sorusu sormak.
3. Eksik bilgiyle soru sorup sistemin bilgi istemesini göstermek.
4. Ücret, önkoşul veya ders programı gibi yapılandırılmış bir değer sormak.
5. Kişisel işlem için OTP doğrulamasını tetiklemek.
6. Transkript yükleyip transkripte özel sorular sormak.
7. Genel belge yükleyip alan/değer bilgisi istemek.
8. Kaynak bulunamayan durumda sistemin uydurmadığını göstermek.

Daha geniş demo listesi için [DEMO_GUIDE.md](DEMO_GUIDE.md) dosyasına bakın.

## Güvenlik Notları

- Aynı Slack token setiyle birden fazla bot çalıştırmayın.
- Slack token veya signing secret commit etmeyin.
- Özel Slack kanal çıktılarını sansürlemeden paylaşmayın.
- Yüklenen dosyaları aksi kanıtlanmadıkça kişisel veri kabul edin.
