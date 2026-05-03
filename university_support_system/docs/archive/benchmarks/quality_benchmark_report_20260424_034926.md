# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 03:49:26
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 40.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 9273.9 ms |
| Medyan Sure | 9054.7 ms |
| Intent Analizi Aktif | 7/7 |
| Force LLM Sentez | 5/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 1/4 | 1920.0 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 14777.2 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 1/5 | 12925.1 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 9054.7 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 8353.7 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 10069.7 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 7817.0 | - |

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
- **API Sureleri**: api_total=1869ms; dispatch=1793ms; compose=0ms
- **Sure**: 1920.0 ms
- **API Response Time**: 1862.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, - Başarısız olduğu bir seçmeli ders yerine, devam zorunluluğu yerine getirilen ancak başarısız olunan dersler için, devamsızlık zorunluluğu yerine getirilmez, ancak alındığı dersler için harfli başarı notu verilir. (Kaynak 2: yonetmelik_onlisans_lisans_egitim_ogretim.pdf, Guven: yuksek, Madde 12)
- Başka yükseköğretim kurumlarının derelerini alma şartıyla, devamsızlık zorunluluğu yerine getirilmez. (Kaynak 2: yonetmelik_onlisans_lisans_egitim_ogretim.pdf, Guven: yuksek, Madde 12)
- Yaz okulunda devam zorunluluğu yerine getirilen ancak başarısız olunan dersler için, devamsızlık zorunluluğu yerine getirilmez, ancak alındığı dersler için harfli başarı notu verilir. (Kaynak 4: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf, Guven: yuksek, Madde 13)
- Başarısız olduğu seçmeli ders yerine başka bir seçmeli ders seçtik olunca, devamsızlık zorunluluğu yerine getirilmez. (Kaynak 2: yonetmelik_onlisans_lisans_egitim_ogretim.pdf, Guven: yuksek, Madde 12)

Bilgi Bilgisi:
Kısaca söylemek gerekirse, başarısız olduğu seçmeli ders yerine başka bir seçmeli ders seçtik olunca, devam zorunluluğu yerine getirilmez.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=14737ms; dispatch=3097ms; global_llm=7490ms; compose=0ms
- **Sure**: 14777.2 ms
- **API Response Time**: 14730.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, ÇAP Programına başvurabilmek için bazı koşullar gerekir:

- Başvuruda bulunulan yarı yıla kadar ana dal lisans programında yer alan tüm dersleri almış ve başarmış olmak,
- Başvuruda bulunulan yarıyıla kadar ana dal not ortalamasının en az 3,00 olması,
- Ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk % 20'sinde bulunmak,
- Aynı anda birden fazla ikinci ana dal diploma programına kayıt yapılmaz, ancak aynı anda ikinci ana dal diploma programı ile YDP’ye kayıt yapılabilir.

Harç Borcu Ödemesi
----------------

* Öğrenciler, harç borcu ödemesi için ÖİDB'nin internet sayfasında bulunan ilgili linkten elektronik olarak başvuruda bulunabilirler.
* Yıllık öğrenim ücreti 2.397,00 TL, dönemlik öğrenim ücreti 1.198,50 TL'dir.
* Öğrenciler, öğrenim ücreti ödemesi için öğrenci isleri ve bursluluk bilgilerini kontrol edebilirler.
Bilgi bulunamadı: ÇAP Programına başvurabilmek için harç borcu ödemesi için hangi belge ve prosedürün kullanılacağına dair belirli bir bilgi yoktur.
Bilgi bulunamadı: ÇAP Programına başvurabilmek için hangi tarihlerde başvuruda bulunacağına dair belirli bir bilgi yoktur.

Bilgilendirme: ÇAP başvuru koşulları, ÇAP'a kabul edilmeye hak kazanan öğrencilerin listesi akademik takvimdeki kayıt yenileme döneminin başlangıcında kesinleşir.

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
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/5
  - [x] kurum içi
  - [ ] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=12881ms; dispatch=3538ms; global_llm=8081ms; compose=0ms
- **Sure**: 12925.1 ms
- **API Response Time**: 12875.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Yürüyüş geçişleri iki çeşit halinde bulunmaktadır: Kurum içi yatay geçiş ve Kurumlararası yatay geçiş.

Kurum içi yatay geçiş, öğrencinin kayıtlı olduğu programme ait bitirdiği dönemler için 4'lük sistemin 2,80 puanının altında olması gerektiği gibi herhangi bir genel not ortalaması sınırı bulunmamaktadır. Buna karşın, öğrencinin kayıtlı olduğu programa ait bitirdiği dönemlerin genel not ortalamasının 4'lük sistemin minimum 2.80, ya da 100'lük sistemin minimum 72 puan olması gereklidir. Geçiş başvurusu yapabilmek için genel not ortalamasının en az 2.80 olması gerekir.

Kurumlararası yatay geçiş, farklı bir üniversiteye öğrencinin geçiş yapılmasını sağlayan bir kurumdur. Öğrencinin kayıtlı olduğu programa ait bitirdiği dönemler için 4'lük sistemin minimum 2.80 ve 100'lük sistemin minimum 72 puanının alınması gereklidir. 

Geçiş değerlendirme kriteri olarak iki farklı geçiş yönteminin kullanıldığı görülmektedir. Kurum içi geçiş için genel not ortalaması ve derslerin tamamının alınması gereklidir. Kurumlararası geçiş için ise genel not ortalaması, derslerin tamamının alınması, disiplin cezasının olmaması ve kayıt durumunun geçerli olması gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=9020ms; dispatch=4849ms; compose=0ms
- **Sure**: 9054.7 ms
- **API Response Time**: 9014.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, ## Soru: 
Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

## Yanıt: 
Eksik veya onaysız belge/belgeler ile gelen öğrenciler ile beyanlarında hata olanların kayıt işlemi yerine getirilmeyecektir.

## Kaynak Bilgisi: 
[Kaynak 3: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf | Guven: yuksek]
Islak imzalı belgelerin fotoğrafı, e-posta çıktısı vb. kabul edilmemekte olup, belgenin aslının getirilmesi gerekmektedir.

## Yanıt: 
Aslında kaybetmiş olmanızın önemli bir sorun olduğu söylenemez; ancak belgenizin olması şarttır. 

Bu nedenle belgenizin yedeklerini kontrol edin, belgenizi bulana kadar da yeni bir diploma almayı düşünebilirsiniz. E-devletteki mezuniyet bilgilerin görünmemesi de aynı sebepledir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=8322ms; dispatch=8275ms; compose=0ms
- **Sure**: 8353.7 ms
- **API Response Time**: 8317.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sınavda kopya çekilmesinin cezası, sınav görevlilerince öğrenciye kopya muamelesi uygulanması ve disiplin soruşturmasına başlanılmasıdır.

Benchmark:
Sınav görevlileri, öğrencinin sınav esnasında ve salonundan çıkana kadar cep telefonu ile ilgilenmesine kopya muamelesi yapabilirler.

[Kaynak 2: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf | Guven: yuksek]

Disiplin Soruşturması Nasıl İşler?
Sınavda kopya çekilmesinin cezası, sınav görevlilerince öğrenciye kopya muamelesi uygulanması ve disiplin soruşturmasına başlanılmasıdır. Disiplin soruşturması, Ondokuz Mayıs Üniversitesi Disiplin Yönetmeliği gereğince yürütülmektedir. 

Benchmark:
Her öğrenci, sınavda kendisine ait malzemeleri kullanmak zorundadır ve hesap makinesi, kalem, silgi veya kullanımına izin verilen tablo gibi araç ve gereçlerin başka bir öğrenci ile paylaşılması yasaktır.

Cezanın Belirlenmesi
Cezayın belirlenmesi, sınav görevlisinin inceleme ve değerlendirmesi ile yapılmaktadır. Öncelikle öğrencinin sınav sırasında davranışının incelenmesinden başlanır. Eğer öğrencinin davranışları sınav kurallarına uygun değilse, cezaya tabi tutulur.

Benchmark:
Gözetmenler öğrencilerin yerlerini değiştirebilir veya sınav kurallarına aykırı davranışlarda bulunanları salondan çıkartabilir.

Sonuç
Sınavda kopya çekilmesinin cezaları, sınav görevlilerin inceleme ve değerlendirmeleridir. Disiplin soruşturması, Ondokuz Mayıs Üniversitesi Disiplin Yönetmeliği gereğince yürütülmektedir.

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
- **Key Facts**: 1/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [x] birim
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=10044ms; dispatch=2877ms; compose=0ms
- **Sure**: 10069.7 ms
- **API Response Time**: 10034.3 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Yanitlamaya Başlatıyorum
Ayrılmak istediğinizde bazı kurallara uymanız gerekli. Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliğine gore kaydolmuş öğrenciler, üniversiteyle ilişiği kesmek için 4 farklı durumda buluna biliyorlar. 

1. Yükseköğretim kurumlarından çıkarma cezası almış olanlar ve kaydını sildiren öğrencilerin ilişiği kesilir.
2. Dört year üst üste olmak kaydıyla, katkı payı ve öğrenim ücreti ödemeyenlerle kayıt yenilememiş durumda olan öğrencilerin, ilgili birimlerin teklifi ve Senato kararı ile YÖK'ün onaylaması durumunda, üniversiteyle ilişiği kesilir.
 4. Yazılı isteği üzerine kaydını sildiren öğrencinin, ÖSYM tarafından yeniden yerleştirilmediği veya üniversite tarafından yapılan ölçme ve değerlendirme sonucunda kayıt hakkı kazanmadığı sürece, üniversiteye tekrar kaydolamaz.
 
Yapmanız gereken işlemler;
- Kaydınızı sildirmek için yazılı bir istek vermek.
- İlgili birime teklifler sunulacak ve sonrasında Senato kararı alınacak.
- YÖK'ün onaylaması sonrasında üniversiteyle ilişiğiniz kesilecek.

Kaydımı sildireceğim ama tekrar üniversiteye dönebilir miyim?

Hayir, üniversiteye dönebilir miyim? ÖSYM tarafından yeniden yerleştirilmediğiniz sürece veya üniversite tarafından ölçme ve değerlendirme sonucunda kayıt hakkını kazandıramazsınız.

Kaydımı sildireceğim ne tür etkileriyle karşılayacağım?

İki durumda karşılaşabilirsiniz; 

- İlgili birine teklifler sunulacak ve sonrasında Senato kararı alınacak ve YÖK'ün onaylaması sonrasında üniversiteyle ayrılmış olacaksınız.
- Eğer öğrenciyse, ÖSYM tarafından yeniden yerleştirilmediğiniz sürece üniversiteye geri dönebilirsiniz.
 
Bu konuyu öğrenmek için [Kaynak 1: yonetmelik_onlisans_lisans_egitim_ogretim.pdf](Guven: yüksek), [Kaynak 2: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf](Guven: yüksek), [Kaynak 3: işyeri_staj_sözleşmesi.pdf](Guven: yüksek) dosyalarını inceledim.

Ön lisans ve lisans programlarında kayıt yaptıracakları derslerin AKTS kredileri toplamı, kayıt yaptıracakları dönem/yı
... (1104 karakter daha)
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
- **API Sureleri**: api_total=7787ms; dispatch=7731ms; compose=0ms
- **Sure**: 7817.0 ms
- **API Response Time**: 7782.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Ders seçimini yapabilmeniz için akademik takvimde belirtildiği gibi öğrenci bilgi yönetim sistemine giriş yaparak, ubys.omu.edu.tr adresine giriş yapmak sureti ile interneti bulunan her yerden yapabilirsiniz.

Kullanılan Kaynak: 
[Kaynak 1: sık_sorulan_sorular.txt | Guven: dusuk]
Ders kaydını nerede yapabilirim? İnternet ortamında ubys.omu.edu.tr adresine giriş yapmak sureti ile interneti bulunan her yerden yapabilirsiniz.

Benchmark: 
Academik takvimde belirtildiği şekilde öğrenci bilgi yönetim sistemine girerek ders seçimi yapabilirsiniz.
Ders seçimi yapabilmeniz için 6 AKTS kadar üst dönemlerden ders alabilir; ancak akademik takvimde belirtilen süre içinde yapabilirsiniz. Bu sure icinde sistematik olarak ardisiklik gerektiren dersler icin danisman onayi gerekir.

[Kaynak 4: ön_lisans_ve_lisans.pdf | Guven: yuksek]
6 akts; 10 akts; 12 akts; 15 akts; dilmesi kosuluyla, akademik takvimde belirtilen sure icinde yapilabilir; ik olarak ardisiklik gerektiren dersler icin danisman onayi gerekir.
Ders seçimlerinden sonra öğrenci bilgi yönetim sistemine giriş yaparak, danışman onayına göndermek ve onayladığı kaydın danışman tarafından kesin kayda dönüşmesini takip etmelisiniz. 

[Kaynak 3: sık_sorulan_sorular.txt | Guven: yuksek]
Danışman onayı için öğrencinin şahsen gelmesi gerektiği yönünde bağlayıcı bir hüküm bulunmamaktadır.

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
