# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 00:14:32
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 71.4% |
| Anahtar Bilgi Kapsami | 36.0% |
| Temiz Kalite Orani | 71.4% |
| Ortalama Sure | 38056.2 ms |
| Medyan Sure | 48024.0 ms |
| Intent Analizi Aktif | 0/7 |
| Force LLM Sentez | 0/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 4 |

## A2A Diagnostics Delta

- Overview delta: queries=7, query_failures=0, agent_tasks=12, agent_task_failures=4

| Agent | Role | Task Delta | Failed Delta | Last Error |
|-------|------|------------|--------------|------------|
| academic_programs_orchestrator | department_orchestrator | 1 | 1 | a2a_specialist_transport_failed |
| international_agent | specialist_agent | 1 | 1 | a2a_specialist_transport_failed |
| registration_agent | specialist_agent | 2 | 1 | a2a_specialist_transport_failed |
| student_affairs_orchestrator | department_orchestrator | 1 | 1 | a2a_specialist_transport_failed |

Recent failure samples:
- `student_affairs_orchestrator`: a2a_specialist_transport_failed - Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?
- `academic_programs_orchestrator`: a2a_specialist_transport_failed - Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?
- `registration_agent`: a2a_specialist_transport_failed - Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?
- `international_agent`: a2a_specialist_transport_failed - Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 1/4 | 59931.9 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 48024.0 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | YANLIS (kural) | 0/5 | 61676.8 | a2a_transport_fallback |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 4526.4 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 74234.3 | uydurma_riski |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 14187.4 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 3812.6 | - |

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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=59393ms; student_affairs_orchestrator=59634ms
- **Sure**: 59931.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli ders seçerek devam zorunluluğunuz nasıl değişir sorusunun cevabı:

Devam zorunluluğu ile ilgilendiğiniz madde 17'de açıklanan koşullara göre belirlenir. Bu maddeye göre, öğrencilerin yüz yüze yürütülen derslerin teorik saatlerinin en az % 70'ine, ders uygulamaları, atölye ve laboratuvarların ise en az % 80'ine devam etmeleri zorunludur.

Sorunuzun cevabı için özellikle madde 17'de açıklanan devamsızlık oranına göre devam zorunluluğunu yerine getireceğiniz dersi seçiyorsanız, durumunuzdaki devamsızlık sınırı % 50 olarak belirlenir. Ancak bu durum, ilgili birim yönetim kurulunca uygun bulunması durumunda, ulusal veya uluslararası düzeyli bilimsel ya da sportif amaçlı kamp ya da diğer organizasyonlarda fiilen görev almış olan ve bunu belgelendirmiş olan öğrenciler için aranmaz.

Yaz döneminde derslere devam zorunluluğu ise madde 13'de açıklanmaktadır. Yaz döneminde açılan dersler için en az bir ara sınav ve dönem sonu sınavı yapılır; ara sınava ve dönem sonu sınavına sadece yaz dönemine kayıtlı öğrenciler girer. Bu durumda, devamsızlık sınırı % 50 olarak belirlenir, ancak ilgili birim yönetim kurulunun kararı ve Senatonun onayıyla bu oran değiştirilebilir.

Daha önceki sorularınıza göre belirttiğim bilgilerden hareketle, sorunuzun cevabı şöyledir:

Soru: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

Yanit: 

Devam zorunlülüğü ile ilgili olarak madde 17'de açıklanan koşul ve oranlara göre devam zorunluluğunuz değişmez. Sorununuzun cevabı için özellikle bu maddeye göre devam zorunluluğunu yerine getireceğiniz dersi seçtiğiniz taktirde devamsızlık sınırı % 50 olarak belirlenir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- 
... (86 karakter daha)
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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: tuition_agent=108ms; finance_orchestrator=635ms; regulation_agent=44670ms; academic_programs_orchestrator=45987ms
- **Sure**: 48024.0 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Benchmark, ÇAP Programına Başvuru Şartları ve Harç Borç Ödeme

Başvuru Şartları

- ÇAP başvurusunda bulunmak için, öğrencinin başvuru sırasındaki ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk % 20'sinde bulunması gereklidir.
- Belirtilen koşula sahip bir öğrenci, harç borcu bulunan halde de ÇAP başvurusunda bulunabilir.

Harç Borç Ödeme

- Harç borcu olan bir öğrenci, ÇAP başvurusunda bulunabilir.
- Harç borcu olan öğrencinin harç borcunu ÖİDB ve öğrencinin kendi programı ile ilişkili diğer kurumlardan alması gerekebilir.

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
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/5
  - [ ] kurum içi
  - [ ] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Ajan Sureleri**: academic_programs_orchestrator=60229ms; student_affairs_orchestrator=60198ms
- **Sure**: 61676.8 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: a2a_transport_fallback

**Yanit:**
```
Benchmark, Ogrenci Isleri:
Kayit Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Akademik Programlar:
Uluslararasi Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Uretim Turu:
- Akademik Programlar: Kural
- Ogrenci Isleri: Kural

Kaynak Ozeti:
- Veritabani kaydi: ogrenci isleri
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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=2865ms; student_affairs_orchestrator=2963ms
- **Sure**: 4526.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Soru:
Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

Yaniti:
Evet, diploma kaybeden öğrenciler, yaygın gazetelerden birine diploma kayıp ilanı verirler ve bunu başvuru dilekçesi, onaylı nüfus cüzdanı sureti ve diploma ücretini yatırdıklarını gösteren banka dekontu ile diploma aldıkları birime müracaat ederler. Bu öğrencilere ilk diplomada yer alan bilgileri içeren yeni bir diploma düzenlenir ve üzerinde İkinci Nüsha olduğu bilgisi yer alır.[1]

Kayıp ilanının yer aldığı gazete, başvuru dilekçesi, onaylı nüfus cüzdanı sureti, diploma ücretini yatırdıklarını gösteren banka dekontu ve diploma aldıkları birime müracaat ile diploma yenileyebilirsiniz. 

E-devlette mezuniyet bilgilerinin görünmemesi durumunu da çözebilirsiniz. E-Devlet üzerinden gelen belgeler onay şartı aranmayacaktır. Ancak, belgelerin asilliği önemlidir. Belgelerin eksik veya onaysız geldiği durumlarda kayıt işlemi yerine getirilmeyecektir. [2]

Diploma yenileyabilmek için, yaygın gazeteden diploma kayıp ilanı verilmeli; başvuru dilekçesi, onaylı nüfus cüzdanı sureti, diploma ücretini yatırdıklarını gösteren banka dekontu ile diploma aldıkları birime müracaat edilmelidir. [1]
[1] Uygulama Esasları - Diploma-Mezuniyet Belgeleri.pdf (MADDE 17)

[2] 2025-2026 Ek Maddesi 1 - Güz Yarıyılı Kayıt için Gerekli Belgeler.pdf (Eksik veya onaysız belge/belgeler ile gelen öğrenciler ile beyanlarında hata olanların kayıt işlemi yerine getirilmeyecektir. E-Devlet üzerinden alınan belgelerde onay şartı aranmayacaktır.)

Kaynak Doğrulama Kuralları:

1. Uygulama Esasları - Diploma-Mezuniyet Belgeleri.pdf
2. 2025-2026 Ek Maddesi 1 - Güz Yarıyılı Kayıt için Gerekli Belgeler.pdf

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belge
... (82 karakter daha)
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: curriculum_agent=59741ms; academic_programs_orchestrator=70523ms; graduation_agent=3443ms; student_affairs_orchestrator=3691ms
- **Sure**: 74234.3 ms
- **Kaynak Sayisi**: 10
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Benchmark, Sınavda kopya çekilmesinin cezası ve disiplin süreci hakkında bilgi.

Sınavda kopya çekilmesinin cezası, öğrencinin sınav yerinden çıkarılması ve eğitim programında başarısız sayılmaktır. Disiplin süreci ise, kopya çekmeye teşebbüs edenlerin, kopya verenlerin ve kopya alanların durum tutanağı ile birlikte sınav yerinden çıkarılması ve disiplin soruşturması başlatılmasıdır.

Bu durumlar gerçekleştiğinde, öğrenci uyarılır ve genellikle durum tutanağı imzalar. İtiraz edebilir, disiplin soruşturması açılır ve işlemin başlatılması için çeşitli koşullar mevcuttur.

Sorulardan bir tanesi olan “kopya çekme suçu gerçekleştiğinde, öğrenciye hangi adımlar uygulanır?” kısmı için 5. Adim olarak “Sınav görevlisi, öğrenciyi uyarır,” ifadesi verilmiştir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_ortak_sınav_yönergesi.pdf
- Belge: hizmet_içi_eğitim_yönergesi.pdf
- Belge: özel_yetenek_sınavı_yönergesi.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: koruma_ve_güvenlik_müdürlüğü_ulaşım_güvenliği_yönergesi.pdf
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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=12532ms; student_affairs_orchestrator=12860ms
- **Sure**: 14187.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Üniversiteyi bırakıp ayrılmak istediğinizde aşağıdaki işlemleri gerçekleştirmek gerekir:

1. Öğretim Planınızı Tamamlamanız Gerekmektedir:
Üniversiteyi bırakmak istediğinizde, eğitim planınıza göre derslerinizin tamamını alınmış olmanız gerekir. Aksi takdirde, kayıt yaptırmaya devam edecektir.

2. Kaydınızı Silebilme Şartınız Olmalıdır:
Kayıt sildirme talebinde bulunabilmeniz için ÖSYM tarafından yeniden yerleştirilmeniz ve/veya Üniversite tarafından ölçme ve değerlendirme sonucunda kayıt hakkı kazanmanız zorunludur.

3. Üyeliğinizin Kesilmesini Talep Edebilme Şartınız Olmalıdır:
Üniversiteyi bırakmak istediğinizde, üyeliğinizi sonlandırabilmeniz için Yazı ile başvurma şartını sağlamalısınız.

4. Etkinlik Kuruluna İtiraz Başvurusu Yapabilmeniz gerekir:
Üniversiteyi bırakmak istediğinizde, üyeliğinize son verilmesiyle ilgili itirazınız olabileceği durumunda, SKSDB'ye itiraz başvurusunda bulunabilirsiniz. İtiraz başvurusu, başvuru tarihinden sonra toplanan ilk Etkinlik Kurulunda görüşülerek karara bağlanır.

5. Kayıt Sildirme İzninizin Oluşması Gerekmektedir:
Kayıt sildirme talebinde bulunmadan önce, Üniversiteye ait belgede yer alan "Kayıt Sildirme İzni" almalısınız. Aksi takdirde, Üniversiteye tekrar kaydolmanız olası değildir.

6. Kayıt Sildirme Süreci Tamamlanmalıdır:
Kayıt sildirme talebinde bulunmadan önce, kayıt sildirme sürecinizin tamamlanmış olduğunu doğrulamalısınız. Aksi takdirde, kayıt yaptırmaya devam edecektir.

Bu işlemlerin tamamının gerçekleştirilmesinden sonra, Üniversiteyi bırakmak istediğiniz için başvuruda bulunabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: öğrenci_toplulukları_yönergesi.pdf
- Belge: ön_lisans_ve_lisans.pdf
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
  - [ ] yenileme
  - [ ] UBYS
  - [x] müfredat
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=3399ms; student_affairs_orchestrator=3656ms
- **Sure**: 3812.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sıra geldi soruya yanıt verme işlemine başlamak:

Belgelerde yer almasına göre, lisans öğrencileri bir defada iki dönem/iki yıl olmak üzere, öğrenim süresi boyunca en fazla dört dönem/iki yıl kaydı dondurabilir. Kayıt donduran öğrenci, öğrenimine devam edemez ve kayıt dondurduğu döneme/yıla ait sınavlara giremez. Kayıt dondurma süresinin bitiminde öğrenci ayrıldığı dönemin/yılın başından başlamak koşuluyla öğrenimine kaldığı yerden devam eder.

Bu kuralı uygulayarak bir sonraki adımı gerçekleştirdiğimde:
1. Kayıt dondurma süresinin bitiminde öğrenci, ayrıldığı dönemin/yılın başından başlamak koşuluyla öğrenimine kaldığı yerden devam edebilmesi için, ders seçimini, akademik takvimde belirlenen süre içinde yapması gerektiği anlaşılabilir.

Bu bilgiler doğrultusunda:
- 1 dönem/yıl başında akademik takvimde belirlenen süre içinde ders kaydını yapmayan öğrenciler, o dönemde öğrenimlerine devam etme hakkını kaybederler.
- Kaydedilen bir dönem/yıl için belirlenmiş olan AKTS kredileri ile bunların yarısının toplamından fazla olamayan dersleri seçmek zorundadır.
- Kayıt döneminde başlamadan transkript/müfredat kontrolünü yaparak akademik takvimde tanımlanan süre içerisinde ders kaydını yapmaları gerektiği, derslere başladığında ise sınıf yoklama listesinde adları yoksa danışmanlarına uğramaları gerektiği bilgisini paylaşması gerekir.

Yukardaki bilgilendirmeler doğrultusunda, OMU öğrencileri için:
- Kayıt dönemi başlamadan transkript/müfredat kontrolünü yaparak, akademik takvimde tanımlanan süre içerisinde ders kaydını yapmaları gerektiği, derslere başladığında ise sınıf yoklama listesinde adları yoksa danışmanlarına uğramaları gerektiği bilgisini öğrencilere paylaşacaklardır.

Bu konuya yönelik bilgilendirmenin nasıl yapılacağına dair bilgiler:
- Öğrenci bilgi yönetim sisteminden öğrencilere toplu ya da bireysel mesaj gönderilerek yapabilirsiniz.
- Bilgilendirmeye ek olarak, kayıt dönemi başlamadan transkript/müfredat kontrolünü yaparak akademik takvimde tanımlan
... (812 karakter daha)
```
