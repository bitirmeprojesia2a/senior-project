# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 13:51:31
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 40.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3291.5 ms |
| Medyan Sure | 2619.9 ms |
| Intent Analizi Aktif | 7/7 |
| Force LLM Sentez | 5/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=7, query_failures=0, agent_tasks=9, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 1/4 | 966.1 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 6499.1 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 5854.7 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 3600.6 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 2374.8 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 2619.9 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 1125.6 | - |

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
- **Ajan Sureleri**: graduation_agent=807ms; student_affairs_orchestrator=872ms
- **API Sureleri**: api_total=959ms; dispatch=892ms; compose=3ms; telemetry=8ms
- **Sure**: 966.1 ms
- **API Response Time**: 909.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli ders seçerseniz, devam zorunluluğunuz devam edecektir. Ancak, başarısız oldunuz dersi yerine geçen ders için harfli başarı notu verilecektir.

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
- **Key Facts**: 3/4
  - [ ] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: tuition_agent=8ms; finance_orchestrator=149ms; regulation_agent=3657ms; academic_programs_orchestrator=3911ms
- **API Sureleri**: api_total=6470ms; dispatch=3986ms; global_llm=1386ms; compose=1417ms; telemetry=12ms
- **Sure**: 6499.1 ms
- **API Response Time**: 6395.8 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Merhaba, başvurunuz üzerine size yardımcı olmaktan memnuniyet duyuyoruz. ÇAP programına başvuru şartları ve harç borcunu ödeme konularında bilgi istemiştiniz.

Harç borunuz varsa öncelikle borcunuzu ödemeniz gerekir. ÇAP programına başvurabilmek için ana dal not ortalamanıza göre en az ilk %20 oranında olması gerekiyor ve bizzat başvuru yaparken bu durumun onaylanması gerekiyor. Ek olarak, bir başka programa yatay geçiş yaptıysanız ÇAP ile ilişiğiniz kesilecektir. ÇAP'a başvurmak için gereken tüm adımlar için lütfen ÇAP programının resmi websitesini ziyaret etmeniz gerekecektir.

Ödenmemiş borcunuzla birlikte başvuruda bulunamayacağınızı unutmayın, bu nedenle borçlarınızı ödemeniz ve tüm başvuru şartları ile koşulları karşıladığınızdan emin olmanız gerekecek.

Kredi Borcu ve Ödeme Seçenekleri

Sizde öğrenim ücreti için Turk Öğrenci Katkı Payı ödemeli değilsiniz. Baska bir konu da ilgili olarak bilgi verilmektedir.

Bu konudaki tüm bilgileri eksiksiz ve doğru bir şekilde elde etmek açısından, başvurunuz sürecinde ilgili personellerle iletişime geçmeniz ve onay süreçlerinin tamamlanması önem taşıyor.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: international_agent=3193ms; academic_programs_orchestrator=3295ms; registration_agent=2891ms; student_affairs_orchestrator=2983ms
- **API Sureleri**: api_total=5837ms; dispatch=3328ms; global_llm=1381ms; compose=1436ms; telemetry=114ms
- **Sure**: 5854.7 ms
- **API Response Time**: 5662.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içinde veya dışarda öğrenci olarak olduğunuzu fark etmediğime göre, kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farkları açıklayacağım.

Kurum içi yatay geçiş, farklı birimlerin aynı üniversitede bulunan öğrencilerin programa geçiş yapmasını sağlayan bir geçiştir. Bu geçiş için, öğrencinin kayıtlı olduğu programda bitirdiği dönemlere ait genel not ortalamasının 4 üzerinden en az 2,80 olması gerekir. Eğer öğrenci, aynı üniversitenin içinde farklı bir programa geçmek istiyorsa, genel not ortalamasının 2,80 olması gerektiği gibi, özel yetenek sınavı ile öğrenci kabul edilen diploma programlarına kurum içi yatay geçiş başvurusunda da bu durumun belgelendirilmesi gerekir. Disiplin cezası almış öğrencilerin yatay geçiş başvuruları da kabul edilmemektedir.

Diğer yandan, kurumlararası yatay geçiş ile başka bir üniversiteye öğrenci geçişi sağlanmaktadır. Bu geçiş için de öğrencinin genel not ortalaması, başvurduğu tarihteki durum, yatay geçiş kontenjanları, taban puanları gibi şartlar geçerlidir. 

Bunlara ek olarak, öğrenci hangi programa geçmek istiyorsa, bu programa eşdeğer olması gerekmektedir. 

Umarım sizlere faydalı bir bilgi olmuştur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
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
- **Ajan Sureleri**: graduation_agent=2239ms; student_affairs_orchestrator=2307ms
- **API Sureleri**: api_total=3591ms; dispatch=2325ms; compose=6ms; telemetry=9ms
- **Sure**: 3600.6 ms
- **API Response Time**: 3546.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Siz, diplomanızı kaybettikten sonra yeniden düzenlenmesi ve e-devlette mezuniyet bilgilerinizin görünmemesini önleyebilirsiniz olarak hareket edebilirsiniz. 

1. Diplomanızı yeniden düzenlemek için, mahkeme kararı, diploma ücretini yatırdığını gösteren banka dekontu, kimlik fotokopisi ve dilekçenizi iletip başvurmalkalısınız. Bu şekilde diploma yeniden düzenlenecek ve size teslim edilecektir.
 
2. E-devlette mezuniyet bilgilerinizi görünmesini sağlamak için, mezuniyet bilgilerinizin güncel olmasını sağlayacak şekilde diploma yeniden düzenlenmesi işlemini tamamladıktan sonra, e-devlet üzerinden durumunuza bakabilirsiniz ve durumunuz güncellenebilirse mezuniyet bilgilerin de görünmesi muhtemel olacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
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
- **Ajan Sureleri**: graduation_agent=2197ms; student_affairs_orchestrator=2258ms
- **API Sureleri**: api_total=2365ms; dispatch=2280ms; compose=14ms; telemetry=18ms
- **Sure**: 2374.8 ms
- **API Response Time**: 2312.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Siz, sınavda kopya çekilmesinin cezasını ve disiplin süreci hakkında bilgi istiyorsunuz. Bu hususta, ilk olarak belirttiğim kaynaklar, kopya çekilmesiyle ilgili disiplin suçu halinde ne gerektiğini anlatıyorlar. 

Sınavda kopya çekilmesinin cezası, 15 dakikadan daha kısa süre içinde yoklama işlemi tamamlanmadan ve sınav görevlisinden izin almadan cep telefonu ile ilgilenecek öğrenci için kopya muamelesi yapılacak olmasıdır. 

Disiplin sürecine geçmeden önce, bu durum işletme tarafından Fakülte Dekanlığı/Yüksekokul Müdürlüğüne veya Meslek Yükselmek Komisyonuna bildirilecek, ve öğrenci hakkında disiplin soruşturması yapılmaya başlanacaktır.

Bu hususta, Fakülte Dekanlığı/Yüksekokul Müdürlüğü veya Meslek Yükselmek Komisyonu tarafından, olayın incelenmesi ve gerekli yasal prosedürlerin işletilmesi gerekecek. 

Sonuç olarak, sınavda kopya çekilmesinin cezası, kopya muamelesi ve disiplin sürecine geçildikten sonra, işletme tarafından Fakülte Dekanlığı/Yüksekokul Müdürlüğüne veya Meslek Yükselmek Komisyonuna bildirilmesi ve bu komisyon tarafından yapılacak olan soruşturmadır. 

Bilgi bulunamadı.

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
- **Ajan Sureleri**: registration_agent=1550ms; student_affairs_orchestrator=1624ms
- **API Sureleri**: api_total=2609ms; dispatch=1671ms; compose=10ms; telemetry=12ms
- **Sure**: 2619.9 ms
- **API Response Time**: 2546.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Siz kaydınızı sildirmek istiyorsunuz. Bunun için aşağıdaki adımları takip edin:

* Üniversite ile iliğiniz kesilmeden önce öğrenci bilgi sistemi üzerinden kaydınızı sildirmenize gerek vardır. Bunu yapmamanız halinde, öğrenci bilgi sistemi sizden onay almadan ilginiz kesilebilecek.
* Aylık ödeme tarihlerini takip etmek çok önemlidir. Aylık ödemelerini zamanında yapılmazsa, kaydınızı sildirirken dikkat etmeniz gereken hususlar arasında aylık ödemeleri yaptırmanız da vardır.
* İlgili mevzuata göre kaydınızı sildirirken, öğrenci bilgi sisteminde bulunan ders kayıtları, kayıt yenileme ve staj ilişkin bilgilerde dikkatli olduğunuz önemlidir.
* Kaydınızı sildirirken dikkate almanız gereken diğer önemli husus, akademik takvimde belirtilen saatler arasında kaydı yapmanızdır.
* Kaydı yaptırmadığınız takdirde, kaydınızı sildirme talebinizi yerine getirmeden önce, ilgili mevzuata göre kayıt hakkınızın kaybettimine neden olmaktadır.
* Bu nedenle, kaydınızı sildireceğiniz durumları dikkate alarak ve bu adımları eksiksiz olarak yerine getirerek, kaydınızı sildirebilir ve tüm işlemleri eksiksiz olarak yaptırabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] kayıt
  - [x] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=967ms; student_affairs_orchestrator=1028ms
- **API Sureleri**: api_total=1114ms; dispatch=1048ms; compose=5ms; telemetry=13ms
- **Sure**: 1125.6 ms
- **API Response Time**: 1068.9 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Ders seçimini yapabilmek için öncelikle akademik takvimde belirtilen süre içerisinde ders kaydını yapmak zorundasınız. Bu süreci öğrenci bilgi yönetim sisteminden takip edebilirsiniz. 

Ders kaydı yapma sürecini tamamladıktan sonra, akademik takvimde belirtilen süre içerisinde danışman onayını alın. 

Ders kaydıyla ilgili detaylı bilgi için, ön lisans ve lisans eğitim-öğretim yönetmeliğini inceleyebilirsiniz.

Daha detaylı bilgilere ihtiyacınız varsa, öğrenci bilgi yönetim sistemindeki akademik takvim veya kayıt yenileme sürecindeki kuralları kontrol edebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
```
