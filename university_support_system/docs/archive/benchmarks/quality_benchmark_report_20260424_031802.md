# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 03:18:02
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 40.0% |
| Temiz Kalite Orani | 85.7% |
| Ortalama Sure | 8385.3 ms |
| Medyan Sure | 6527.1 ms |
| Intent Analizi Aktif | 7/7 |
| Force LLM Sentez | 5/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 2/4 | 1499.4 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 7477.0 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 25649.1 | uydurma_riski |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 4651.4 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 5129.0 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 6527.1 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 7763.9 | - |

## Soru Detaylari

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [ ] yeni
  - [x] ders
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=1458ms; dispatch=1427ms; compose=0ms
- **Sure**: 1499.4 ms
- **API Response Time**: 1452.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Bu konuda elimdeki kaynaklarda net bilgi bulunamadi.
Ancak, kaynaklardan bazıları bazı durumlarda devam zorunluluğunun hafifletilmesine dair bilgiler vermektedir:
- Yaz okulunda derslere devam zorunludur.(Kaynak 2: yonetmelik_onlisans_lisansegitim_ogretim.pdf | Kaynak 4: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf)
- Tekrar edilen derslerde, alınan en son not geçerlidir ve YANO/GANO hesabında bu son not kullanılır.(Kaynak 2: yonetmelik_onlisans_lisansegitim_ogretim.pdf | Kaynak 4: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf)
Devam koşulu yerine getirilmemiş tekrar derslerine devam esastır. % 70 gibi kriterlere gore devam zorunlulugu olabilir. (Kaynak 3: yonetmelik_onlisans_lisansegitim_ogretim.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yonerge_yaz_okulu_egitim_ogretim.pdf
- Belge: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs', 'student_affairs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=factual
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=7419ms; dispatch=3009ms; global_llm=2866ms; compose=0ms
- **Sure**: 7477.0 ms
- **API Response Time**: 7403.3 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, ÇAP programına başvurabilmek için, yükseköğretim kurumuna kaydolmak ve harç borcu bulunmadan önce yükseköğretim kurumuna kaydolmak gereklidir. Ancak, harç borcu bulunan başvurular değerlendirilmemektedir.

Harç borcu bulunan öğrenciler, yükseköğretim kurumunda bir diploma programına kaydolduktan sonra harç borcu ödeyebilme seçeneği bulunuyor. Öğrenciler ilk iki yıla ait öğrenim ücretini ödeyemeyen öğrencilere ödemenin süresi tanınmaktadır. Öğrenim ücretinin ödemenin süresi, ilgili akademik birim tarafından belirlendiği gibi, akademik ücrete taban puanını geçme zorunluluğu bulunmamaktadır.

Lisansüstü derslere devam etmek isteyen öğrencilerin %10 öğrenim ücreti ödemeleri gerekir. Ödemenin süresi, 12.000 TL ye kadar katkı payı/öğrenim ücreti ödemesi gerekiyor. Öğrenim ücretinin tamami, öğrenim ücretinin ödenmesiyle tamamlanmaktadır.

Harç borcu için, öğrenciler öğrenci borçlarını ödeyebilmek için https://yurtdisikayit.omu.edu.tr/ portalından e-kayıt başvurusu gerçekleştiriyor. Öğrenciler, öğrenci borçlarını ödeyebilmek için e-başvuru formunu dolduranlar, öğrenci borçlarını ödeyebilmek için www.omu.edu.tr/ portalından e-başvuru formunu dolduranlar, öğrenciler öğrenci borçlarını ödeyebilmek için www.omu.edu.tr/portalinden öğrenci borçlarını ödeyebilmek için www.omu.edu.tr/portalından e-başvuru formunu doldurduklarında, öğrenciler e-başvuru formunu doldurduklarında, öğrenciler öğrenci borçlarını ödeyebilmek için öğrenci borçlarını ödeyebilmek için www.omu.edu.tr/portalinden öğrenci borçlarını ödeyebilmek için www.omu.edu.tr/portalinden e-başvuru formunu doldurur. e-başvuru formunu doldurduklarında, öğrenciler öğrenci borçlarını ödeyebilmek için öğrenci borçlarını ödeyebilmek için www.omu.edu.tr/portalinden öğrenci borçlarını ödeyebilmek için www.omu.edu.tr/portal/fromu öğrenci borçlarını ödeyebilmek için www.omu.edu.tr/portal/fromu öğrenci borçlarını ödeyebilmek için öğrenci borçlarını ödeyebilmek için öğrenci borçlarını ödeyebilmek için öğrenci borçlarını öde
... (1180 karakter daha)
```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=google_ai/gemini-2.5-flash-lite [fallback]
- **API Sureleri**: api_total=25613ms; dispatch=3366ms; global_llm=21026ms; compose=0ms
- **Sure**: 25649.1 ms
- **API Response Time**: 25607.6 ms
- **Kaynak Sayisi**: 10
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Benchmark, Kurum içi ve kurumlar arası yatay geçiş arasındaki temel fark, geçişin aynı üniversite içindeki programlar arasında mı yoksa farklı üniversiteler arasındaki programlar arasında mı yapıldığıdır.

Her iki geçiş türü için de bazı ortak başvuru şartları ve değerlendirme kriterleri bulunmaktadır:

* Genel not ortalamasının en az 2.80 olması gerekmektedir.
* Öğrencinin kayıtlı olduğu programda disiplin cezası almamış olması şartı aranır. Disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez ve bu durumu başvuru sırasında belgelendirmesi gerekir.
* Yatay geçiş yapılabilecek programın, öğrencinin mevcut programıyla eşdeğer olması gerekmektedir.
* Özel yetenek sınavı ile öğrenci kabul eden programlara yatay geçiş için de genellikle genel not ortalamasının en az 2.80 olması istenir.

Ancak, kurum içi ve kurumlar arası yatay geçişte bazı farklılıklar da mevcuttur:

* Kurum İçi Yatay Geçiş: Genellikle öğrencinin kayıtlı olduğu programda belli bir başarıyı göstermesi ve puan türündeki en düşük taban puandan az olmaması istenir.
* Kurumlar Arası Yatay Geçiş: Farklı üniversitelerden Ondokuz Mayıs Üniversitesi'ne (OMÜ) geçiş yapmak isteyen öğrenciler için geçerlidir. Bazı durumlarda, örgün öğretim yapan programlar için merkezi yerleştirme puanının %30'u ve genel not ortalamasının %70'i gibi değerlendirme yöntemleri de kullanılabilir.

Ayrıca, ilk yıl veya mezuniyet yılı hariç tutulmak üzere, öğrencinin ara dönemlerinde veya tez yazım aşamasında yatay geçiş yapması mümkün olmamaktadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçi
... (234 karakter daha)
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
- **API Sureleri**: api_total=4599ms; dispatch=2938ms; compose=0ms
- **Sure**: 4651.4 ms
- **API Response Time**: 4582.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, - Diplomamızı kaybettikten sonra, diploma eki gerekli görüldüğü için bu duruma karşı önlem olarak, diplomanın eki olan diploma onay belgesi ile mezuniyet işlemlerini tamamlamanız gerekir.
- Daha çok bilgiye ihtiyaç duyarsanız, diploma eki gerekip gerekmediğine ilişkin bilgiler içeren [kaynak 1: sık_sorulan_sorular.txt](https://doc.omu.edu.tr/sık_sorulan_sorular.txt/) dosyasını inceleyebilirsiniz.
- E-devlette mezuniyet bilgilerimin görünmemesi durumu, diploma eki gerekip gerekmediğine bağlıdır. Sorununuzu [kaynak 2: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf](https://doc.omu.edu.tr/uygulama_esaslari_diploma_mezuniyet_belgeler.pdf) dosyasında bulabilirsiniz. 
- E-devlette mezuniyet bilgilerinin görünmemesi, e-devlette diploma eki gerekli görüldüğü takdirde bu durumun gerçekleşeceği anlamına gelmektedir.
- E-devlette diploma eki gerekli görüldüğü takdirde diploma eki olan diploma onay belgesiyle bu durumun giderilmesi gerekir.

Sadece diploma ektir. Belgenizi kaybederiniz mi?
- Diplomamızı kaybettikten sonra diploma ekinde olduğu üzere diploma onay belgesi ile mezuniyet işlemlerimizi tamamlamamız gerekiyor.
- E-devlette mezuniyet bilgilerim görünmüyorsa bu durum, diploma eki gereken durumlarda oluşurmaktadır. Bu durumu gidermek için diploma ekinde olduğu üzere diploma onay belgesi ile e-devlette mezuniyet bilgilerinin görünmesini sağlayabilirsiniz.

Kisisel akademik verilerim (GNO, not, kredi):
- GNO ve notlarınız [kaynak 3: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf](https://doc.omu.edu.tr/2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf) kaynağında yer almaz. Lütfen bu konuda daha ayrıntılı bilgiye ihtiyacınız olursa bize iletişime geçiniz.

Kisisel akademik verilerim (GNO, not):
- Notlarınız [kaynak 3: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf](https://doc.omu.edu.tr/2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf) kaynağında yer almaz. Lütfen bu konuda daha ayrıntılı
... (1341 karakter daha)
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=5098ms; dispatch=5029ms; compose=0ms
- **Sure**: 5129.0 ms
- **API Response Time**: 5094.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sınavda kopya çekilmesinin cezası kopya muamelei yapılmasıdır. 
Kopya muamelesi yapılan öğrenciye, sınav kağıtlarında herhangi bir değişiklik yapması (karalamak, yırtmak, sayfaları ayırmak vb.) ve sınav sırasında veya sınav salonundan çıkana kadar cep telefonu ile ilgilenmesi yasaklanır.
Disiplin süreci Fakülte Dekanlığı/Yüksekokul Müdürlüğü veya Meslek Yüksekokulu Dekanlığı tarafından yürütülür. 
Ayrıca, işletmelerde disiplin soruşturmasını gerektirecek davranışlarda bulunan öğrenciler, işletme tarafından Fakülte Dekanlığı/Yüksekokul Müdürlüğü veya Meslek Yüksekokulu Dekanlığı'a bildirilir.
Kopyada ceza ve disiplin süreci ile alakalı bilgilere mühendislik_fakültesi_sınav_uygulama_kuralları.pdf kaynağında ulaşılabilmektedir.

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=6500ms; dispatch=5301ms; compose=0ms
- **Sure**: 6527.1 ms
- **API Response Time**: 6494.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Üniversiteyi bırakmak istiyorsanız, lütfen aşağıdaki adımları takip ediniz.

Dikkatli Olmanız Gereken Hususlar:

- Kaydı silme talebinizi yazılı isteğinizle ilgili bölüm müdürlüğüne başvurduğunuzda kaydı silinen öğrenci, ÖSYM tarafından yeniden yerleştirilmediği sürece, Üniversiteye tekrar kaydolamaz. (Kaynak 1: ön_lisans_ve_lisans.pdf, Madde 32)
- Kayıt yenileme işlemini, her dönem/yıl başında akademik takvimde belirlenen süre içinde yapabilmeniz gerekir. Sömestr başlangıcında 14 Temmuz 2019 gününün akşamına kadar ve son sınıfta öğrenciler 1 Aralık 2020 gününün akşamına kadar kayıt yenileme işlemini yapabilirler (Kaynak 2: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf, Madde 10)
- Kayıt silme işleminde, akademik takvimde belirtilen süre içinde başvurmanız ve istenen belgelerin tamamlayarak tamamlamış olması gerekir.

Önemli Notlar:

- Kayıt silme işlemini gerçekleştirdiğinizde, öğrenci ile Üniversitesi arasındaki ilişki kesilir.
- Kayıt silinen öğrencilerin ÖSYM tarafından yeniden yerleştirilmediği sürece, Üniversiteye tekrar kaydola-maları mümkün olmayacaktır.

Kaynak Bilgileri:

- Kaynak Bilgisi 1: ön_lisans_ve_lisans.pdf, Madde 32, Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği
- Kaynak Bilgisi 2: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf, Madde 10, Ön Lisans ve Lisans Eğitim Öğretim Yönetmeliği
- Kaynak Bilgisi 3: işyeri_staj_sözleşmesi.pdf, Madde 6, İşyeri Staj Sözleşmesi

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
  - [x] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=7739ms; dispatch=7694ms; compose=0ms
- **Sure**: 7763.9 ms
- **API Response Time**: 7736.2 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Ders kaydı, akademik takvimde belirtilen süre içinde yapılırsa yapabilirsiniz ama 1 yıl önce dondurmayından dolayı daha önce yapamadığın Güz yarıyılı derslerini artık yapamazsın. Bu seneki Ders kayıtlarında yer alan derslerden seçim yaparak ders kaydı yapabilirsin.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
