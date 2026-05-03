# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 13:22:37
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 40.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 6546.1 ms |
| Medyan Sure | 4312.0 ms |
| Intent Analizi Aktif | 7/7 |
| Force LLM Sentez | 5/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=7, query_failures=0, agent_tasks=9, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 1/4 | 1133.4 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 8584.3 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 20380.0 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 6931.1 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 4312.0 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 2669.5 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 1812.5 | - |

## Soru Detaylari

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] değiştirebilir
  - [ ] devam koşulu
  - [ ] yeni
  - [x] ders
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=769ms; student_affairs_orchestrator=900ms
- **API Sureleri**: api_total=1124ms; dispatch=936ms; compose=15ms; telemetry=39ms
- **Sure**: 1133.4 ms
- **API Response Time**: 958.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Devam zorunluluğu, başarısız olan ders için değil, başka bir seçmeli ders için geçerlidir. Yani, başarısız olduğunuz seçmeli dersten bağımsız olarak başka bir seçmeli ders alabilirsiniz.

Bu konudaki düzenlemeler; Kanit 2: yaz_okulu_eğitim_öğretim.pdf MADDE 12 (1) ve (2) ve Kanit 3: yonetmelik_onlisans_lisans_egitim_ogretim.pdf MADDE 17 (1) ile belirtilmiştir.

KAYNAK DOGRULAMA KURALLARI:
- Kanit 2: yaz_okulu_eğitim_öğretim.pdf tam olarak soruya ilgili olduğu için bilgilerin tamamını kullanabiliriz.
- Kanit 3: yonetmelik_onlisans_lisans_egitim_ogretim.pdf da soruya destekleyici bilgi sunuyor.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yaz_okulu_eğitim_öğretim.pdf
- Belge: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: tuition_agent=10ms; finance_orchestrator=75ms; regulation_agent=2465ms; academic_programs_orchestrator=2541ms
- **API Sureleri**: api_total=8559ms; dispatch=2577ms; global_llm=5424ms; compose=5448ms; telemetry=24ms
- **Sure**: 8584.3 ms
- **API Response Time**: 8496.1 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
ÇAP programına başvurmak isteyen öğrencilerin başvuru şartları ve harç borcu ödeme processi ile ilgili olarak aşağıdaki genel olarak dikkat edilmesi gereken durumlar bulunmaktadır.

ÇAP Başvuru Şartları

1. Ana Dal Not Ortalaması: Ana dal not ortalaması %20'sinin altında olan öğrencilerin başvuru kabul edilmemektedir. Aynı zamanda, başvuru sahibinin asgari %20'sinde bulunduğunu ve ana daldan en az ilk %20'sinde bulunması gerekmektedir.
2. Birim Koşulları: Soruşturmaya konu harç borcu ödemesi de bu kanallardan yapabilirsiniz. Ondokuz Mayıs Üniversitesi web sitesinde belirtilen ödemeler başlıklı makalenin altında harç borcu ödemesi nasıl yapıldığını bulabilirsiniz.

Harç Borcu Ödemesi

1. Ödeme Bilgileri: Ondokuz Mayıs Üniversitesi web sitesinden ödeme kanalları açıklanmakta olup, başvuruya konu harç borcu ödemesini de bu kanallardan yapabilirsiniz.
2. Fiyat Bilgileri: Öğrenim ücreti için Türk öğrenci / Mühendislik Fakültesi bilgisi veritabanında kayitli. Yillik ücret: 2.397,00 TL. Donemlik ücret: 1.198,50 TL.
3. Ödeme Kanalları: Ondokuz Mayıs Üniversitesi web sitesinde belirtilen ödemeler başlıklı makalenin altında harç borcu ödemesi nasıl yapıldığını bulabilirsiniz.

Not: Harç borcunuzun bulunup edilmemesini başvuru sırasında kontrol etmeniz gerekmektedir.

Dikkat Edilmesi Gerekenler

- Başvuru sırasında harç borcunun bulunup edilmemesini kontrol etmeniz gerekmektedir.
- Başvurular sırasında başvuru sahibinin ana dal not ortalaması %20'sinin altındaki öğrencilerde başvuru kabul edilmemektedir.
- Başvuru sahibinin asgari %20'sinde bulunduğunu ve ana daldan en az ilk %20'sinde bulunması gerekmektedir.

Kaynaklar

- yonerge_cift_anadal_yandal.pdf
- 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: VT
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Veritaba
... (132 karakter daha)
```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=8201ms; student_affairs_orchestrator=8272ms; international_agent=4639ms; academic_programs_orchestrator=4740ms
- **API Sureleri**: api_total=20368ms; dispatch=8423ms; global_llm=9119ms; compose=9174ms; telemetry=23ms
- **Sure**: 20380.0 ms
- **API Response Time**: 20285.0 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki temel farklar aşağıdaki gibidir:

Kurum İçi Yatay Geçiş
- Sadece aynı üniversite içindeki farklı bir enstitüye geçiş yapılır.
- Yatay geçiş başvurusunda bulunacak öğrenci, ilgili anabilim/anasanat dalı her yarıyılda yatay geçiş yapabilir.
- İlk yarı yılın sonundaki dereceye göre yatay geçiş yapabilir.
- Not ortalamasının ilk yarı yılının sonundaki derecesi en az 2,80 olmalıdır.
- Yatay geçiş başvurusu yapabilmek için genel not ortalamasının en az 2,80 olması gerekir.
- Başvuru süresi 10 gün ve 01.08.2025 - 06.08.2025 tarihleri arasında yapılır.
- Yatay geçiş sonuçları 15.08.2025 tarihinde açıklanacaktır.
- Disiplin cezası almış öğrencilerin yurt içi yatay geçiş başvuruları kabul edilmez.

Kurumlar Arası Yatay Geçiş
- Yerleştirme sınavı, yabancı dil sınavı, özel yetenek sınavı ile öğrenci kabul edilen diploma programlarına kurum içi yatay geçiş yapılmaz.
- Yatay geçiş başvuruları, aynı puan türündeki programlara geçiş için genel not ortalamasının %60’ı ve merkezi yerleştirme puanının %40’ı, farklı puan türlerindeki programlara geçiş için genel not ortalamasının %30’ı ve merkezi yerleştirme puanının %70’si kullanılır.
- Yatay geçmiş başvuruları, "Yükseköğretim Kurulu" tarafınca onaylanan üniversiteye yapılır.
- Yatay geçiş için başvuru süresi, derslere başlama tarihinden önce yapılmalıdır.
- Yatay geçiş sonuçları 25.08.2025 tarihinde açıklanacaktır.
- Yatay geçiş hakkından yararlanmak için, uluslararası öğrencilerin izinli sayılması gerekir.
- Yatay geçiş başvuruları, tekrar yatay geçiş başvurusunu yapan öğrenciler için 80 gün geçmemek kaydı ile yapılabilir.
- Disiplin cezası almış öğrencilerin yurt dışı yatay geçiş başvuruları kabul edilmez.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim b
... (541 karakter daha)
```

### Q20: Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] 2. nüsha
  - [x] diploma
  - [x] e-devlet
  - [ ] YÖKSİS
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=4526ms; student_affairs_orchestrator=4639ms
- **API Sureleri**: api_total=6922ms; dispatch=4657ms; compose=16ms; telemetry=12ms
- **Sure**: 6931.1 ms
- **API Response Time**: 6856.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Lisans ve on lisans mezuniyet süreçleri
Mezuniyet bilgilerinizin görünmemesine ve diplomanızın kaybolmasına neden olan sorunu çözmeniz için aşağıdaki adımları takip edebilirsiniz:
- Diploma Kaybı: Diplomanızın kaybolduğunu bildirdiniz, ancak belge baglaminizde diploma için bir tanımı göremedik. Diploma eki neden gereklidir bilgisine baktığımızda, yeni diploma ve sertifikasyon şekilleri gelişmekte ve ülkeler eğitim sistemlerini değiştirmektedir, ama bu bilgi diplomanın kaybolduğunu çözmeye yardım etmemektedir. Bu yüzden diplomanızın kopmuş olup olmadığını, veya kopan diplomada bir kopyayı aldığını denetlemeniz gerekir.

Sorunun DOGRUDAN cevabı için diploma eki neden gereklidir bilgisini çözebilmek için daha kapsamlı bilgiler gerekmektedir. Diplomunuzun kaybolduğunu bildirdiğinizde ve diploma eki bilgisi soruyla tamamen ilgili olmadığından dolayı; kisi deneyimi, genel bilgi birikimi gibi ifadeleri kullanmamamız gerekiyor. Diploma eki bilgisi soruyla TAMAMEN ILGISIZSE o bilgiyi CIKARMAYIP "Bu konuda elimdeki kaynaklarda net bilgi bulunamadı" deyip cevabı verilmelidir. 

E-devlette mezuniyet bilgilerinizin görünmemesine neden olan sorun ise diploma için değil, e-devlet sistemindeki kaydedilmemiş veya yanlış kaydedilmiş verileri iletilmiş olmasından kaynaklanabilir. Diplomanızda herhangi bir sıkıntı olmayan durumlarda; diplomanızın kayıp olmadığını, kaybedilmiş olunduğunu denetlemeden, diploma eki bilgisi sorusuna cevapsız kalındığı gibi bu soruda da cevapsız kalıncaya kadar diplomanızı yeniden diploma eki ile birlikte sunmanız gerektiğini bilmek gereklidir. 

Bu konudaki detay hakkında daha kapsayıcı bilgi için destek almak için [Bilgi Hattı](https://omu.edu.tr/saglikli-yol/) ile iletişime geçebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_bel
... (117 karakter daha)
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=4126ms; student_affairs_orchestrator=4188ms
- **API Sureleri**: api_total=4297ms; dispatch=4211ms; compose=14ms; telemetry=10ms
- **Sure**: 4312.0 ms
- **API Response Time**: 4237.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınavda kopya çekilmesinin cezası: Soru, cevabı belirtmemek anlamına gelmez. Cevap: Kopya verme ve çekme girişiminde bulunmak bir disiplin suçudur ve bu suçun tespitine öğrenciye 15 dakikadan daha kısa süre olmamak üzere, yoklama işlemi tamamlanmadan ve sınav görevlisinden izin almadan ve sınav salonundan çıkana kadar cep telefonu ile herhangi bir şekilde ilgilenen öğrenciye kopya muamelesi yapılır. ( Kaynak: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf )

Disiplin Süreci: Öğrencilerin işletmelerde disiplin soruşturmasını gerektirecek davranışlarda bulunmaları halinde, bu durum işletme tarafından Fakülte Dekanlığı/Yüksekokul Müdürlüğü veya Meslek Eğitim Merkezleri tarafından değerlendirilir. İşletmelerce rapor teslim edilmemesi halinde staj geçersiz sayılır. ( Kaynak: işyeri_staj_sözleşmesi.pdf )

- Kaynak: işyeri_staj_sözleşmesi.pdf 
- Kaynak: staj_ilkeleri_23122019_inş_müh.pdf

Not: Bu soruyla ilgili kaynakların tamamı tamamen ilgili görünmemektedir. Kaynaklardan bazıları soru ile kısmen ilgili gibi görünse de, soru ile tam olarak alakalı olmayabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: staj_ilkeleri_23122019_inş_müh.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 0/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [ ] birim
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=1621ms; student_affairs_orchestrator=1719ms
- **API Sureleri**: api_total=2654ms; dispatch=1738ms; compose=10ms; telemetry=14ms
- **Sure**: 2669.5 ms
- **API Response Time**: 2597.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Evet, üniversiteyi bırakmak istiyorsanız önce Öğrenci Bilgi Sistemi'nden (OBS) işlemlerini gerçekleştirmeniz gerekir. Bu, aşağıdaki adımları içerir:

1. OBS'ye girin ve "Kayıt İşlemleri" sekmesinden "Kaydını Sildirmek" seçeneğini seçin.
2. Sistemin size sunduğu seçeneklerden birini seçin. Bu seçeneklerin neler olduğu OBS'den bilgi alınabilir.

Kayakta belirtildiği gibi, kaydı silmek için öğrencinin üniversite ile ilişiği keseceği dikkate alınmalıdır. Ancak, bu prosedürün tüm detayları için OBS'den bilgi alınmalıdır. Dikkatli davranılmalıdır, çünkü kaydı silmek üzerine bir süre sonra ödemenin yapılması ve diğer yasal prosedürler için zaman kaybetmemek önemlidir.

Kaynağı:
- YÖK ve Üniversite tarafından belirlenen ilkeler çerçevesinde yükseköğretim programları kayıt hakkı kaybeden öğrencinin OBS'de kaydı silme seçeneğine sahip olduğu belirtiliyor. (Ön_Lisans_Ve_Lisans_Eğitim_Öğretim_Yönetmeliği, MADDE 9)
- Bir öğrencinin ÖSYM tarafından yeniden yerleştirilmediği sürece üniversiteye tekrar kayıt olmayı planlaması gerektiği de açıklanıyor. (Ön_Lisans_Ve_Lisans_Eğitim_Öğretim_Yönetmeliği, MADDE 9)
- Kayıt yenileme zaman aşımı 14/7/2019 ve 1/12/2020 tarihlerinde belirlenmiştir. (Ders Kayıt, Kayıt Yenileme)
- Ders kaydı, süre sınırlaması bulunan bir durumdur. Kayıt yenileme işlemleri 14/7/2019 ve 1/12/2020 tarihlerinde belirlenmiştir. (Ders Kayıt, Kayıt Yenileme)
 
Dikkat edilmesi gereken hususlar:
- Üniversite ile ilgisini kesmek istiyorsanız OBS'den kaydı sildirmek zorundasınız.
- Ancak bu prosedürden sonra, ÖSYM tarafından yeniden yerleştirilmeyen öğrenci üniversiteye tekrar kayıt olamaz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] kayıt
  - [ ] yenileme
  - [x] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=1628ms; student_affairs_orchestrator=1686ms
- **API Sureleri**: api_total=1792ms; dispatch=1718ms; compose=7ms; telemetry=8ms
- **Sure**: 1812.5 ms
- **API Response Time**: 1743.1 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Evet, ders seçimini yapabilirsiniz. İnternet ortamında ubys.omu.edu.tr adresine giriş yapmak sureti ile interneti bulunan her yerden yapabilirsiniz.

Ders kaydını yaptırmadığımız dönem eğitim süresinden sayılır mı?

Evet, ders kaydı yapmadığınız dönemler de eğitim süresinden sayılmaktadır.

Güz yarıyılı ders kaydı yaptırmadım. Bir sonraki yarıyıl (bahar) ders kaydı yaptırabilir miyim?

Evet, ancak akademik takvimde belirtilen süre içinde yapmanız gerekmektedir. Ayrıca, akademik takvimde tanımlanan süre içerisinde ders kaydını yapmanız gerektiği bilgisini öğrenci bilgi yönetim sisteminden alabilirsiniz.

Fakat sorun çözülmeden ders kaydınızı tamamlamayınız.

Ders kaydım danışman onayını bekliyor, ne yapmalıyım?

Onayın alınması için öğrenci bilgi yönetim sistemi üzerinden internet ortamında ders kaydını yapan öğrenci, danışman onayına sistem üzerinden gönderebilmektedir. Danışman onayı için öğrencinin şahsen gelmesi gerektiği yönünde bağlayıcı bir hüküm bulunmamaktadır. Ancak, öğrenci danışman onayın ardından kaydını tamamlamalıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
```
