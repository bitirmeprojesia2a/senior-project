# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 01:29:26
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 48.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 5717.7 ms |
| Medyan Sure | 6034.5 ms |
| Intent Analizi Aktif | 7/7 |
| Force LLM Sentez | 5/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 1/4 | 4848.4 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 6034.5 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 12264.1 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 6252.3 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 2739.9 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 6375.4 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 1509.0 | - |

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
- **API Sureleri**: api_total=4758ms; dispatch=4683ms; compose=0ms
- **Sure**: 4848.4 ms
- **API Response Time**: 4753.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli seçersek devam zorunluluğunuz nasıl değişir?

Soru 1: Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli seçersem, devam zorunluluğu ortadan kalkır mı?

Yanit: Hayır, devam zorunluluğu ortadan kalkmaz. Yaz Okulu ve Derslere Devam Yönetmeliği, devam zorunluluğu devam etme zorunluluğunu ortadan kaldırmaz. (Kaynak 2: yonetmelik_onlisans_lisans_egitim_ogretim.pdf, MADDE 17- (1) )

Soru 2: Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli seçersem, devamsızlık hesabında neye göre devam zorunluluğu yerine getirilir?

Yanit: Devamsızlık hesabında, ders veya uygulamaların o dönemdeki/yıldaki toplam saati esas alınır. (Kaynak 2: yonetmelik_onlisans_lisans_egitim_ogretim.pdf, MADDE 17- (1) )

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
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=5984ms; dispatch=2965ms; global_llm=1525ms; compose=0ms
- **Sure**: 6034.5 ms
- **API Response Time**: 5978.2 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, ÇAP programa başvurmak için harç borcu durumuna göre başvuru şartları aşağıdaki gibidir:

Başvuru Şartları

- Başvurunuzun sırasında harç borcu olan öğrenci başvuramaz. Ancak, başvurduğunuz yarı yılında başvuru yapabilmek için harç borcu olmadan önce başvurabilirsin.
- Başvuru yapılan yarı yılın ilk gününe kadar ana dal lisans programında yer alan tüm dersleri almış ve başarmış olmalısın.
- Başvurmanızın sıra zamanında ana dal not ortalamasının en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk % 20'sinde bulunmalısın.

Harç Borcu Ödemesi

- Harç borcunu ödeyemeyen öğrenci başvuru yapamaz.
- Harç borcu olan öğrenciler başvuru yapabilmek için harç borcu olmadan önce başvurabilirler.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: VT
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=12206ms; dispatch=6338ms; global_llm=1823ms; compose=0ms
- **Sure**: 12264.1 ms
- **API Response Time**: 12201.0 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Kurum-ıçi Yatay Geçiş ve Kurumlararası Yatay Geçiş Farkları

Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar şunlardır:

Kurum-ıçi Yatay Geçiş:

Kurum içi yatay geçiş, aynı üniversitedeki farklı bir programa geçiş yapma imkanı sunar. Bu geçiş, öğrencinin aynı üniversitedeki farklı bir enstitü anabilim/anasanat dalından ya da eşdeğer eğitim veren yurt içi yükseköğretim programları arasında yapılır. Başvuru esnasında öğrencinin disiplin cezası almadıktan, kayıt dondurmadıktan ve genel not ortalamasının en az 2.80 olduğu tespit edilmelidir.

Kurumlararası Yatay Geçiş:

Kurumlararası yatay geçiş, farklı bir üniversitedeki aynı düzeydeki bir programa geçiş yapma imkanı sunar. Bu geçiş, yurtiçi veya yurtdışındaki yükseköğretim kurumlarından Üniversiteye yapılır. Başvuru esnasında öğrencinin herhangi bir disiplin cezası almadıktan, kayıt dondurmadıktan ve öğrenim gördüğü yükseköğretim kurumunda genel not ortalamasının en az 2.80 (4'lük sistem) veya en az 72 (100'lük sistem) olduğu tespit edilmelidir.

Bunlardan çıkarılabilen genel bilgiler:

- Her iki geçiş türü için de disiplin cezası ve kayıt dondurma durumları dikkate alınmalıdır.
- Her iki geçiş türü için de genel not ortalaması aranır.
- Her iki geçiş türü için de yatay geçiş başvuruları, ilan edilen süre içerisinde yapılır ve başvuruyla ilgili ön değerlendirmeyi ilgili yönetim kurulları tarafından oluşturulan komisyonlar yapar.
- Yatay geçiş işlemleri ilgili yönetim kurulu kararı ile kesinleşir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Be
... (214 karakter daha)
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=6216ms; dispatch=2094ms; compose=0ms
- **Sure**: 6252.3 ms
- **API Response Time**: 6212.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sizden gelen sorulara verilecek yaniti hazirlamaya calisacagim. Lutfen sorularinizi tekrar sorun.

Soru: 
Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

1. Diplomamı kaybettim. Ne yapmalıyım?

- Diploma kaybı halinde, yaygın gazetelerden birine diploma kayıp ilanını veririz.
- Diploma kayıp ilanının yer aldığı gazete, başvuru dilekçesi ve onaylı nüfus cüzdanı sureti ile diploma aldığımız birime müracaat ederiz.
- Diplomada yer alan bilgileri içeren yeni bir diploma düzenlenir ve üzerinde İkinci Nüsha olduğu bilgisi yer alır.

2. E-devlette mezuniyet bilgilerim görünmüyor. Ne yapmalıyım?

- E-devlette mezuniyet bilgilerinin görünmemesi halinde, mahkeme kararına dayalı nüfus kaydı değişikliği olması durumunda, mahkeme kararı, diploma ücretini yatırdığını gösteren banka dekontu, kimlik fotokopisi ve dilekçe ile başvurulur.
- Diplomanın yeniden düzenlenmesi için, ilgili birime müracaat edilir.

3. Her iki sorun için ne yapmalıyım?

- Her iki sorun için, ilgili birime müracaat edilmeli ve diploma veya mezuniyet bilgilerinin yeniden düzenlenmesi için başvurmalıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
- Belge: ön_lisans_ve_lisans.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=2698ms; dispatch=2652ms; compose=0ms
- **Sure**: 2739.9 ms
- **API Response Time**: 2692.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sorulan soru:
Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

Yanıt:
Sınavda kopya çekilmesinin cezası kopya muamelesidir. Gözetmenler, sınav sırasında öğrencilerin yerlerini değiştirebilir veya sınav kurallarına aykırı davranışlarda bulunanları salondan çıkartabilir.

Belge kaynakları:
- Ondokuz Mayıs Üniversitesi Mühendislik Fakültesi Sınav Uygulama Kuralları
- Mimarlık Fakültesi Staj İlkeleri
- İşyeri Staj Sözleşmesi

Belge kaynaklarından aldığım bilgiler:

- Sınav kağıtlarında herhangi bir değişiklik yapmak, zarar vermek yasaktır (Kaynak 1: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf).
- Sınavlarda kopya vermek ve çekme girişiminde bulunmak bir disiplin suçudur (Kaynak 1: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf).
- Cep telefonları sınav esnasında kapalı tutulur ve sessiz konumda veya uçuş modu olarak bulundurulması dahi yasaktır (Kaynak 2: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf).
- Her öğrenci, sınavda kendisine ait malzemeleri kullanmak zorundadır ve hesap makinesi, kalem, silgi veya kullanımına izin verilen tablo gibi araç ve gereçlerin başka bir öğrenci ile paylaşılması yasaktır (Kaynak 2: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf).
- Sınav salonunda görev yapan gözetmen, sınavın sorunsuz bir biçimde yürütülmesinden sorumludur ve bu konuda tam yetkilidir (Kaynak 2: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf).
- Birbirine benzeyen, aynı konuları içeren, kopya izlenimi veren ve ders kitaplarındaki bilgilerden oluşan staj raporu veren öğrencilerin stajları staj değerlendirme formlarına bakılmaksızın tamamen reddedilir (Kaynak 4: staj_ilkeleri_23122019_inş_müh.pdf).
- Disiplin işlemi, Fakülte Dekanlığı/ Yüksekokul Müdürlüğü tarafından Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği hükümlerine göre yürütülür (Kaynak 5: işyeri_staj_sözleşmesi.pdf).

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklay
... (295 karakter daha)
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [x] birim
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=6332ms; dispatch=5106ms; compose=0ms
- **Sure**: 6375.4 ms
- **API Response Time**: 6325.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Üniversiteyi bırakıp ayrılmak istiyor ve tüm işlemleri öğrenmek istiyorsanız, önce aşağıdaki işlemleri gözden geçirin:

1. İlişkinin Kesilmesi: YÖnetmeliklere göre, öğrencinin yazılı talebi, geçersiz bir mazereti olmaksızın üst üste iki Genel Kurul toplantısına katılmaması, topluluğun amaçlarına aykırı faaliyette bulunması veya verilen görevlerin yerine getirilmemesi durumlarında, Yönetim Kurulu kararı ve Akademik danışman onayı ile üyelik sonlandırılır. Bu durumda, öğrenci tebliğ tarihinden itibaren 7 gün içinde SKSDB’ye itiraz başvurusunda bulunabilir.
2. Kayıt Sildişi: Yazılı isteği üzerine kaydını sildiren öğrenci, ÖSYM tarafından yeniden yerleştirilmediği veya Üniversite tarafından yapılan ölçme ve değerlendirme sonucunda kayıt hakkı kazanmadığı sürece, Üniversiteye tekrar kaydolamaz.
3. Ders Kaydı: Öğrenciler, her dönem/yıl başında akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden alacağı dersleri seçer ve ders kaydı, danışman onayı ile kesinleşir. Ders kaydının kesinleştirilmesi ile ilgili süreci öğrenci takip etmek zorundadır.
4. Kayıt Yenileme: Akademik takvimde belirlenen süre içinde ders kaydını yapmayan öğrenciler, o dönemde öğrenimine devam etme hakkını kaybederler. Süresi içinde ders kaydını yapmayan öğrencilerin kayıtları, mazeretlerinin haklı ve geçerli olduğu ilgili birimin yönetim kurulunca kabul edilmek koşuluyla akademik takvimde belirtilen süre içinde yapılabilir.
5. Kesin Kayıt: Yükseköğretim kurumlarından çıkarma cezası almış olanlar ve kendi istekleri ile kaydını sildiren öğrencilerin Üniversite ile ilişiği kesilir.

İlişkinin kesilmesi ya da öğrencinin kaydını sildirmesi için, ilgili Yönetim Kurulu kararı gereklidir. Bu sürecin detayları için, Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine bakılması gerekir.

Önemli Not: YÖnetmelikler ve kuralların detayları için ilgili kaynaklar incelenebilir.

Kesin kayıt yenileme sürecini öğrenmek için; [Kaynak 2: yonetmelik_onlisans_lisans_egitim_ogreti
... (626 karakter daha)
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] kayıt
  - [ ] yenileme
  - [x] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=1468ms; dispatch=1421ms; compose=0ms
- **Sure**: 1509.0 ms
- **API Response Time**: 1465.4 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Soru: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

Yaniti: Evet, okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini yapabilirsiniz. Kayıt dondurma süresinin bitiminde öğrenci aprendığı dönemin/yılın başından başlamak koşuluyla öğrenimine kaldığı yerden devam eder ve süre hesabına dahil edilmez. (Kaynak 1, Kaynak 2)

Bu durumda, kayıtlı olduğu programın ders seçimi süresini akademik takvimde kontrol etmeniz gerekir. İnternet ortamında ubys.omu.edu.tr adresine giriş yapmak sureti ile ders seçimi yapmak mümkün olacaktır. (Kaynak 3)

Ders seçimi yaptırmanız durumunda, akademik takvimde belirtilen sürede danışman onayına göndermek ve onaylanmadığında sistem üzerinden iade edilen ders kayıt teklifini tekrar düzenlemektir. (Kaynak 4)

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
