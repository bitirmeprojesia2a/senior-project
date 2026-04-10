# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 16:24:36
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 3

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 66.7% |
| Uretim Modu Dogrulugu | 66.7% |
| Anahtar Bilgi Kapsami | 43.8% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 2636.1 ms |
| Medyan Sure | 3276.2 ms |
| Intent Analizi Aktif | 2/3 |
| Force LLM Sentez | 2/3 |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | YANLIS (kural) | 1/5 | 1135.0 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 3276.2 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 3/6 | 3497.0 | - |

## Soru Detaylari

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['finance'] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 1/5
  - [ ] azami
  - [x] ek
  - [ ] süre
  - [ ] katkı payı
  - [ ] öde
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 1135.0 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Ogrenim ucreti ogrenci turune ve birime gore degisiyor. Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin.

Uretim Turu:
- Kural
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [ ] UBYS
  - [x] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3276.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ders kaydından danışman onayına kadar sürecin başından sonuna kadar tüm adımları açıklamak isterim:

1. Öğrenci Kaydı: Öğretim yılında kayıtlı olmadığınız halde, kaydınızı yaptırmak istediğinizde, Önlisans veya Lisans öğrencisi olmanız için gereken adımları tamamlayıp ön kayıt başvuru formunu doldurmaya başlıyorsunuz. Bu formu doldurduktan sonra, kayıt onayı için başvurunuza yanıt alıyorsunuz.

2. Ders Seçimi: Ön kayıt sürecinde sizde ders seçme işlemi gerçekleştiriyorsunuz ve size sunulan ders seçeneğine bağlı olarak, ilgili dersleri seçip, kayıt olmak istediğiniz dersleri belirlemeyi sağlıyorsunuz. Daha sonra bu seçilen dersleri, kayıt olmak istediğiniz derse ait kodları ile birlikte kayıt sisteminde kaydectirebilirsiniz.

3. Ders Değişikliği: Kayıt olmak istediğiniz derste değişiklik yapma ihtimalinizi düşündüğünüzde, Önlisans veya Lisans programınız olan öğrenci kayıt sisteminin "Ders Değişitirmek" sekmesine girebilirsiniz. Bu alanda belirlenen kuralların doğrultusunda ve öğrencilerin değişikliğini belirlemesine imkan tanınacaktır.

4. Ders Kaydının Onaylanması: Belirlenen kurallara uygun olarak, kayıt olmak istediğiniz dersteki öğrenci kaydınızı onaylıyorsunuz. Kayıt olmak istediğiniz derste değişiklikler yaptığınızda, kayıt sisteminde belirttiğiniz değişiklikleri onaylıyorsunuz.

5. Ders Muafiyet: Bu, öğrencilerin belirli bir dersten muaf olmasını sağlayan prosedürü ifade eder. Bu prosedürde, Önlisans veya Lisans eğitimine devam eden öğrenciler, kayıtlı oldukları programdan ders muafiyetine başvurabilirler.

6. Ders Yeterlik: Belirlenen kurallar çerçevesinde, öğrenciler tarafından, önlisans veya lisans eğitimine devam eden öğrenciler, belirli bir dersten yeterliliği sağlamak için başvurularını gerçekleştiriyorlardı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorula
... (62 karakter daha)
```

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/6
  - [x] ders
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [x] ilişik kesme
  - [x] diploma
- **Sure**: 3497.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Mezuniyet için gerekli koşulları ve ilişik kesme sürecini adım adım açıklıyorum:

Mezuniyet Koşulları:

1. Hazırlık hariç dört yarıyıl süreli meslek yüksekokullarında bir mesleğe yönelik olarak yürütülmekte olan programlardan mezun olan öğrenciler için "Önlisans Diploması" alır.
2. Türk Ceza Kanununun ikinci kitabının birinci babında yer alan cürümler sebebiyle hüküm giyenler veya disiplin cezası alarak yükseköğretim kurumlarından uzaklaştırılanlar hariç olmak üzere, 2547 sayılı Kanun hükümleri uyarınca bir lisans programının en az ilk dört yarıyılının bütün derslerinden başarılı olanlara "Önlisans Diploması" veya "Lisans Diploması" verir.
3. Hazırlık hariç, dört yıl süreli fakülte ve yüksekokul lisans programlarından mezun olan öğrenciler için "Lisans Diploması" alır.
4. Ana daldaki mezuniyetlerine bağlı olarak ikinci ana dal lisans programını tamamlayan öğrenciler için "Çift Ana Dal Lisans Diploması" verir.
5. Ana daldaki mezuniyetlerine bağlı olarak yandal lisans programlarını tamamlayan öğrenciler için "Yandal Sertifikası" alır.
6. Enstitülerdeki tezli veya tezsiz yüksek lisans programlarını tamamlayanlara "Tezli Yüksek Lisans Diploması" veya "Tezsiz Yüksek Lisans Diploması" verir.
7. Enstitülerdeki doktora veya sanatta yeterlik programlarını tamamlayanlara "Doktora" veya "Sanatta Yeterlik Diploması" eder.

İlişik Kesme Koşulları:

1. Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre yükseköğretim kurumlarından çıkarma cezası almış olanlar ile kendi istekleri ile kaydını sildiren öğrencilerin Ondokuz Mayıs Üniversitesi ile ilişiği kesilir.
2. Dört yıl üst üste olmak kaydıyla, katkı payı ve öğrenim ücreti ödemeyen veya kayıt yenilemeyen lisans öğrencilerinin ilgili birimlerin teklifi ve Senato kararı ile Ondokuz Mayıs Üniversitesi'nin onaylaması durumunda, Ondokuz Mayıs Üniversitesi ile ilişiği kesilir.
3. 8. inci maddenin üçüncü ve dördüncü fıkraları kapsamındaki öğrencilerden başarısız oldukları ders sayısını bire ind
... (1158 karakter daha)
```
