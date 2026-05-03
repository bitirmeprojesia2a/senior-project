# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 12:43:56
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 40.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 6562.6 ms |
| Medyan Sure | 2744.7 ms |
| Intent Analizi Aktif | 7/7 |
| Force LLM Sentez | 5/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=7, query_failures=0, agent_tasks=9, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 1/4 | 1451.3 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 6778.3 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 28943.1 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 3079.5 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 1297.1 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 2744.7 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 1643.9 | - |

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
- **Ajan Sureleri**: graduation_agent=1176ms; student_affairs_orchestrator=1252ms
- **API Sureleri**: api_total=1437ms; dispatch=1284ms; compose=4ms; telemetry=10ms
- **Sure**: 1451.3 ms
- **API Response Time**: 1312.2 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Soru:
Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

Yanit:
Devam zorunluluğu ile ilgili olarak madde 17 ve 19'ye bakıldığında, öğrenci başarısız olduğu bir seçmeli ders yerine, sonraki dönemde/yılda devam etmek kaydıyla, bir başka seçmeli dersi alabilir. Ancak, dönem içi değerlendirme ve devam zorunluluğu için madde 17 ve devam ediyor olan öğrenciler için en az % 70 oranındaki devam zorunluluğu geçerlidir. Bu kapsamda, başarılı olduğunuz ders yerine diğer seçmeli dersi almak ile devam zorunluluğunuzda bir değişim yaşanmaz.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: tuition_agent=72ms; finance_orchestrator=921ms; regulation_agent=3936ms; academic_programs_orchestrator=4518ms
- **API Sureleri**: api_total=6747ms; dispatch=4637ms; global_llm=1164ms; compose=1172ms; telemetry=12ms
- **Sure**: 6778.3 ms
- **API Response Time**: 6691.2 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Benchmark, ÇAP Başvuru Şartları ve Harç Borcu Ödeme

ÇAP'a başvuru yapıldıktan sonra, öğrenci harç borcu olduğunu bilmelidir. Eğitim-öğretim yılı sonuna kadar ÇAP'a başvurmuş öğrenciler, herhangi bir engel olmaksızın kabul edilirler. ÇAP'te geçici veya sürekli ayrılma ve ilişik kesilme halleri bulunur. Öğrenci ÇAP'ı kendi isteği ile bırakabilir veya başvuru koşullarını sağlayan öğrenciler başka ÇAP başvurusu yapabilirler.

Harç Borcu Ödeme

Öğrenciler, eğitim-öğretim yılı için öğrenim ücreti ödemezler, öğrenci katkı payı ödemek zorundadır. 2025-2026 yılı için yıllık öğrenci katkı payı ücreti 2.397,00 TL, dönemlik ücreti ise 1.198,50 TL'dir.

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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=google_ai/gemini-2.5-flash-lite [fallback]
- **Ajan Sureleri**: international_agent=7266ms; academic_programs_orchestrator=7359ms; registration_agent=1189ms; student_affairs_orchestrator=1308ms
- **API Sureleri**: api_total=28906ms; dispatch=7398ms; global_llm=20449ms; compose=20458ms; telemetry=13ms
- **Sure**: 28943.1 ms
- **API Response Time**: 28832.8 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Kurum içi yatay geçiş, Ondokuz Mayıs Üniversitesi (OMU) içinde aynı düzeydeki farklı diploma programlarına geçişi ifade ederken; kurumlar arası yatay geçiş, farklı bir üniversitenin eşdeğer eğitim veren fakülte, yüksekokul veya bölümünden OMU'ya yapılan geçiştir.

Başvuru şartları ve değerlendirme kriterleri farklılık göstermektedir:
* Kurum içi yatay geçiş için genel not ortalamasının en az 2.80 olması gerekirken, kurumlar arası yatay geçiş için genel not ortalamasının 4 üzerinden en az 2.80 veya 100'lük sistemde en az 72 olması gerekmektedir.
* Kurumlar arası yatay geçiş için başvuran kişinin, geçiş yapmak istediği programla eşdeğer bir diploma programına kayıtlı olması şartı aranır; kurum içi yatay geçişte bu koşul bulunmamaktadır.
* Her iki geçiş türü için de başvuru yapan öğrencinin öğrenim gördüğü yükseköğretim kurumunda herhangi bir disiplin cezası almamış olması gereklidir.

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
- **Ajan Sureleri**: graduation_agent=1950ms; student_affairs_orchestrator=2058ms
- **API Sureleri**: api_total=3046ms; dispatch=2109ms; compose=8ms; telemetry=11ms
- **Sure**: 3079.5 ms
- **API Response Time**: 2988.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Sorunun cevabı:

1. Diploma kaybedenler için: 
- İlk adım olarak yaygın gazetelerden birine diploma kayıp ilanı vermelisiniz. 
- İlgili birimlere kayıp ilanının yer aldığı gazeteye, başvuru dilekçesine ve onaylı nüfus cüzdanı suretine müracaat etmelisiniz. 
- Diploma ücretini yatırdığını gösteren banka dekontu ile birlikte Diploma aldığınız birime müracaat etmelisiniz. 
- Uygulama esasları Madde 17 (1) göre yeni diploma düzenlenir.
- Yeni diploma orijinal diploma gibi olmayacak, üzerine "İkinci Nüsha" bilgisi yer alacak.

2. E-devlette mezuniyet bilgilerinin görünmemesi için:
- E-devletten alınan belgelerde onay şartı aranmayacaktır. 
- E-devletten alınan 1. Başvuru formu çıkan belge, e-devlet üzerinden alacağınız belge olacaktır. 
- Lütfen başvuru formu çıktılarınızı e-devlet üzerinden alın ve belge durumunu kendiniz kontrol edunuz.
- E-Devletteki mezuniyet bilgisine erişmek için ilgili birim tarafından tasdik edilmiş belge bilgilerinizi e-devlet üzerinden güncelleyebilirsiniz.

Belge kayıp ilanı veren ve yeniden diploma düzenlemek isteyen öğrenciler için, diploma ücretini yatırdığını gösteren banka dekontu ile birlikte Diploma aldıkları birime müracaat etmelidirler. Uygulama esasları Madde 17 (2) göre yeniden diploma düzenlenir.

Ayrıca, mahkeme kararına dayalı nüfus kaydı değişikliği olması halinde, diploma yeniden düzenlenir. Madde 18- (1) göre yeniden düzenlenecek diplomalar için mahkeme kararı, diploma ücretini yatırdığını gösteren banka dekontu, kimlik fotokopisi ve dilekçe ile başvurulması gerekir.

Bu konularda net bilgiye erişebilmek için ilgili birime müracaat ediniz.

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
- **Ajan Sureleri**: graduation_agent=1082ms; student_affairs_orchestrator=1157ms
- **API Sureleri**: api_total=1284ms; dispatch=1189ms; compose=9ms; telemetry=14ms
- **Sure**: 1297.1 ms
- **API Response Time**: 1224.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

Sınava kopya çekilmesinin cezası, öğrencinin stajından başarısız sayılmasıdır. Birbirine benzeyen, aynı konuları içeren, kopya izlenimi veren ve ders kitaplarındaki bilgilerden oluşan staj raporu veren öğrencilerin stajları staj değerlendirme formlarına bakılmaksızın tamamen reddedilir.

Disiplin süreci, Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği hükümlerine göre yürütülür. Soruşturma, Fakülte Dekanlığı/Yüksekokul Müdürlüğü veya Meslek Yüksekokulu Müdürlüğünde yapılır ve sonuç, işletmeye yazılı olarak bildirilir.

Tarih: Bilgi bulunamadı. (Herhangi bir spesifik tarih bulunamadı.)

Sayı: Bilgi bulunamadı. (Herhangi bir spesifik sayı bulunamadı.)

Yüzde: Bilgi bulunamadı. (Herhangi bir spesifik yüzde bulunamadı.)

Süre: Bilgi bulunamadı. (Herhangi bir spesifik süre bulunamadı.)

Amaç: Bilgi bulunamadı. (Herhangi bir spesifik amaç bulunamadı.)

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=1667ms; student_affairs_orchestrator=1782ms
- **API Sureleri**: api_total=2693ms; dispatch=1801ms; compose=9ms; telemetry=10ms
- **Sure**: 2744.7 ms
- **API Response Time**: 2645.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Üniversiteyi bırakıp ayrılmak istiyorsanız, aşağıdaki işlemleri takip edin:

Eğer kaydınızı silmek istiyorum:
- Kaydınızı sildirme isteğinizi, öğrenci bilgi sistemi üzerinden, "Kayıt İşlemi" sekmesinden ve "Kayıt Sorgulama" sekmesinden yapabilirsiniz.
- Kaydınızı sildirecek olan öğrenci, ÖSYM tarafından yeniden yerleştirilmediği veya Üniversite tarafından yapılan ölçme ve değerlendirme sonucunda kayıt hakkı kazanmadığı sürece, Üniversiteye tekrar kaydolamaz.
- Kaydınızı sildirdiğiniz tarihte, 7 gün içinde, SKSDB'ye itiraz başvurusunda bulunabilirsiniz. İtiraz başvurusu, başvuru tarihinden sonra toplanan ilk Etkinlik Kurulunda görüşülerek karara bağlanır.

Eğer kaydınızı silmek istemiyorsanız, ama ders kaydınızı yaptırmak veya kaydınızı yenilemek istemiyorsanız:
- Akademik takvimde belirlenen süre içinde, öğrenci bilgi sistemi üzerinden alacağı dersleri seçecek ve ders kaydı, danışman onayı ile kesinleşecektir.
- Akademik takvimde belirlenen süre içinde ders kaydını yapmayan öğrenciler, o dönemde öğrenimine devam etme hakkını kaybederler. Kaybedilen dönem öğrenim süresinden sayılır.

Ayrılma nedenlerinim nelerdir:
- Geçerli bir mazereti olmaksızın, üst üste iki Genel Kurul toplantısına katılmaması,
- Topluluğun amaçlarına aykırı faaliyette bulunulması,
- Verilen görevlerin yerine getirilmemesi durumlarında, Yönetim Kurulu kararı ve Akademik danışman onayı ile üyeliğiniz sonlandırılır.

Ayrılma işlemini takip eden adımlar:
- Üyeliğiniz sonlandırma tarihi, 7 gün içinde SKSDB'ye itiraz başvurusunda bulunabilirsiniz.
- İtiraz başvurusu, başvuru tarihinden sonra toplanan ilk Etkinlik Kurulunda görüşülerek karara bağlanır.

KAYNAK DOGRULAMA:
- [Kaynak 1: öğrenci_toplulukları_yönergesi.pdf]
- [Kaynak 2: yonetmelik_onlisans_lisans_egitim_ogretim.pdf]
- [Kaynak 3: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf]
- [Kaynak 4: işyeri_staj_sözleşmesi.pdf]

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim
... (304 karakter daha)
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
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=1434ms; student_affairs_orchestrator=1511ms
- **API Sureleri**: api_total=1622ms; dispatch=1529ms; compose=8ms; telemetry=12ms
- **Sure**: 1643.9 ms
- **API Response Time**: 1555.7 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Sorunun DOGRUDAN yaniti:

- Ders seçimini, akademik takvimde belirtilen süre içerisinde öğrenci bilgi yönetim sistemi (UOYS) üzerinden internet ortamında yapabilirsiniz.
- Kayıt dönemi başlamadan önce, öğrencilerin transkript/müfredat kontrolüne giderek ders seçimini yapmaları gerektiği, derslere başladığında ise sınıf yoklama listesinde adları yoksa danışmanlarına uğramaları gerektiği bilgisini paylaşılması önerilir.
- Danışman onayını vermek için öğrencinin şahsen gelmesi zorunlu değildir. Öğrenci, internet ortamında ders kaydını yapan Öğrenci Bilgi Yönetim Sistemi üzerinden danışman onayına gönderilebilir.
- Öğrenci, ders kaydını yapmak, yaptığı kaydı danışman onayına göndermek ve onaya gönderdiği kaydın danışman tarafından kesin kayda dönüşmesini takip etmekle yükümlüdür.

KAYNAK İZLENTİLERİ:
- Kayıt dondurma süresinin bitiminde öğrenci, ayrıldığı dönemin/yılın başından başlamak koşuluyla, öğrenimine kaldığı yerden devam edebilir (Kaynak 1 ve 2).
- Kayıt dönemi başlamadan transkript/müfredat kontrolünü yaparak akademik takvimde tanımlanan süre içerisinde ders kaydını yapmaları gerektiği, derslere başladığında ise sınıf yoklama listesinde adları yoksa danışmanlarına uğramaları gerektiği bilgisini paylaşılmalıdır (Kaynak 3).
- Öğrenci, internet ortamında UOYS adresine giriş yaparak ders kaydını yapabilir (Kaynak 5).
- Ders kaydı yapmadığınız dönem eğitim süresinden sayılır (Kaynak 5).
- Güz yarıyılı ders kaydı yaptırmadım, ancak bir sonraki yarıyıl (bahar) ders kaydı yaptırabilirim (Kaynak 5).

Bu soru acıklaca lisans ve ön lisans ders seçimine ilişkinydi, ancak Ondokuz Mayıs Üniversitesi'nin (OMU) ders seçim kuralları hususunda net bilgi yoktur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pd
... (34 karakter daha)
```
