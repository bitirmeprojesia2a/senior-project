# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 00:59:47
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 40.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 10596.0 ms |
| Medyan Sure | 6130.4 ms |
| Intent Analizi Aktif | 0/7 |
| Force LLM Sentez | 0/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=7, query_failures=0, agent_tasks=11, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 2/4 | 1686.6 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 8739.4 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 11817.6 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 6130.4 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 41424.6 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 2904.3 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 1469.3 | - |

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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=1427ms; student_affairs_orchestrator=1505ms
- **API Sureleri**: api_total=1678ms; dispatch=1543ms; compose=5ms; telemetry=8ms
- **Sure**: 1686.6 ms
- **API Response Time**: 1577.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Devam zorunluluğunuz değişmez çünkü seçmeli dersi seçtiğinizde, başarısız olduğunuz dersin yerine devam zorunluluğunu yerine getirmelisiniz. Bu, Yönetmelik'te belirtilen şartlar doğrultusunda, devam koşulu yerine getirmemekten sonra dersi almanızı sağlar.

Belge Baglami kaynaklardan:
[Kaynak 1: yonetmelik_onlisans_lisans_egitim_ogretim.pdf]
MADDE 19- (1) …öğrenci; danışmanın onayıyla, başarısız olduğu bir seçmeli ders yerine, sonraki dönemde/yılda devam etmek kaydıyla, bir başka seçmeli dersi alabilir.
Dönem içi değerlendirme
[Kaynak 2: yonetmelik_onlisans_lisans_egitim_ogretim.pdf]
MADDE 17- (1) Bir öğrencinin izinli sayıldığı süre de dahil, toplam devamsızlık süresi, bir dersin o dönemdeki/yıldaki toplam saatinin % 50'sini aşamaz.

Bu durumda, devamsızlık hesabında dikkate alınacak süre %50'si geçmeyecektir.

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
- **Departman**: ['finance', 'academic_programs', 'student_affairs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: tuition_agent=17ms; finance_orchestrator=399ms; regulation_agent=6545ms; academic_programs_orchestrator=6834ms; registration_agent=3958ms; student_affairs_orchestrator=4040ms
- **API Sureleri**: api_total=8692ms; dispatch=6890ms; global_llm=836ms; compose=850ms; telemetry=13ms
- **Sure**: 8739.4 ms
- **API Response Time**: 8610.6 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
Benchmark, Başvuru şartlarından biri olan harç borcunuzu ödemesini ardından, başvurulabilecek yarı yıl'a göre başvurmanız gerekmektedir. 

Eğer harç borunuz varsa, öğrenci bilgisayarınıza giriş yaptıktan sonra "Harç ve Ödenecek Maliyetler" sekmesine tıklayarak borç tutarınızı görüntüleyecek ve ödemenizi gerçekleştireceksiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: VT
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=5130ms; student_affairs_orchestrator=5214ms; international_agent=10616ms; academic_programs_orchestrator=10770ms
- **API Sureleri**: api_total=11807ms; dispatch=10832ms; compose=8ms; telemetry=11ms
- **Sure**: 11817.6 ms
- **API Response Time**: 11734.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Bu cevap, OMU Ogrenci Isleri kapsaminda kayit islemleri icin uretilmistir.

Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar:

* Kurum içi yatay geçiş: Ondokuz Mayıs Üniversitesi içinde aynı düzeydeki diğer diploma programlarına geçiş.
* Kurumlar arası yatay geçiş: Ondokuz Mayıs Üniversitesi dışındaki bir üniversite, yüksek teknoloji enstitüsü veya bir üniversiteeye bağlı olmaksızın vakıflar tarafından kurulan meslek yüksekokullarından Ondokuz Mayıs Üniversitesi içindeki eşdeğer eğitim veren fakülte, yüksekokul veya bölüme yapılan geçiş.

Başvuru şartları:

* Kurum içi yatay geçiş: Öğrencinin kayıtlı olduğu programda bitirmiş olduğu dönemlere ait genel not ortalamasının en az 2.80 olması gerekir.
* Kurumlar arası yatay geçiş: Öğrencinin kayıtlı olduğu programda bitirmiş olduğu dönemlere ait genel not ortalamasının; 4’lük sistem kullanan üniversiteler için en az 2.80, 100’lük sistem kullanan üniversiteler için en az 72 olması gerekmektedir.

Değerlendirme kriterleri:

* Kurum içi yatay geçiş: Öğrencinin genel not ortalaması, derslerin tamamını başarmış olma şekli vb.
* Kurumlar arası yatay geçiş: Öğrencinin genel not ortalaması, merkezi yerleştirme sınav puanı, diploma programının taban puanı vb.

Yürürlük tarihi: 2025-2026 bahar yarıyılı yatay geçiş ilan metni.

Bu konuda elimdaki kaynaklarda net bilgi bulunmadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=5015ms; student_affairs_orchestrator=5133ms
- **API Sureleri**: api_total=6104ms; dispatch=5160ms; compose=7ms; telemetry=9ms
- **Sure**: 6130.4 ms
- **API Response Time**: 6053.3 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Sorunuzun cevabı, diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor konularını içermektedir. Aşağıdaki yanıtı verebiliriz:

Diplomayı kaybettiniz: 
- Diplomasını kaybedenler, yaygın gazetelerden birine diploma kayıp ilanı verirler.
- Kayıp ilanının yer aldığı gazete, başvuru dilekçesi, onaylı nüfus cüzdanı sureti ve diploma ücretini yatırdıklarını gösteren banka dekontu ile diploma aldıkları birime müracaat ederler.
- İlk diplomada yer alan bilgileri içeren yeni bir diploma düzenlenir ve üzerinde İkinci Nüsha olduğu bilgisi yer alır.

E-devlette mezuniyet bilgilerim görünmüyor: 
- Diplomalar, düzenlenmesi tarihinde görevde bulunan dekan/müdür ve rektör tarafından imzalanmış olmalıdır.
- Islak imzalı belgelerin fotoğrafı, e-posta çıktısı vb. kabul edilmemekte olup, belgenin aslının getirilmesi gerekmektedir.
- E-devlet üzerinden alınan belgelerde onay şartı aranmayacaktır, ancak diploma için onay şartı aranacaktır.

Ayrıca, diplomalarınızı alma hakkı olan öğrencilere, diplomanın düzenlenmesi için e-devlet sistemine giriş yapılır. Bu sırada e-devlet sistemine girildiğinde "diploma kayıp" sekmesine tıklanır. Sözlük ve diploma kayıp ilanı ekinde yer alan belgelerin aslı ile birlikte bu sekme doldurularak diploma başvuru yapılmaktadır.

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
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=1903ms; student_affairs_orchestrator=3826ms; curriculum_agent=36122ms; academic_programs_orchestrator=39071ms
- **API Sureleri**: api_total=41388ms; dispatch=39152ms; global_llm=1329ms; compose=1342ms; telemetry=15ms
- **Sure**: 41424.6 ms
- **API Response Time**: 41336.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Sınavda Kopya Çekilmesinin Cezası ve Disiplin Süreci

Sınavda kopya çekilmesinin cezası olarak kopya muamelesidir. Bu suça yönelik işlem, sınav esnasında öğrencinin kopya verme veya çekme girişimi yapıldığında uyarıda bulunmaksızın uygulanabilir. Hatta, sınav esnasında öğrencinin cep telefonu ile ilgilenmesi dahi kopya muamelesi yapılabilir.

Kopya çekilmesinin cezası, sınav geçersiz sayılır ve ilgili kişiye kanaat işlem yapılır. Disiplin süreci, tutanaktan sonra sınav yerinden ayrılması takip eder.

Disiplin Sürecinin Adımları:

1. Kopya muamelesi yapılan öğrenci uyarıda bulunmaksızın işlem uygulamaya alınabilir.
2. İşlem uygulanmasından sonra öğrencinin sınav yerinden ayrılması gerekir.
3. Ayrılış tarihine göre öğrencinin sınav geçersiz sayılması sonucuna ulaşılır.

Kaynak:

- 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesi
- Ondokuz Mayıs Üniversitesi Mühendislik Fakültesi Sınav Yönergesi

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: staj_ilkeleri_23122019_inş_müh.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
- Belge: mühendislik_fakültesi_ortak_sınav_yönergesi.pdf
- Belge: hizmet_içi_eğitim_yönergesi.pdf
- Belge: özel_yetenek_sınavı_yönergesi.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: etik_ilkeleri_ve_iş_etik_kurulu_yönergesi.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=1744ms; student_affairs_orchestrator=1871ms
- **API Sureleri**: api_total=2862ms; dispatch=1894ms; compose=10ms; telemetry=14ms
- **Sure**: 2904.3 ms
- **API Response Time**: 2798.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Üniversiteyi bırakıp ayrılmak isteyen öğrenci için aşağıdaki adımlar dikkat edilmesi gereken hususları kapsamaktadır:

1. Yazılı talebi: Öğrenci, yazı ile Üniversiteye talebini iletmemelidir. Yasa ve yönetmelikler gereği, öğrencinin kendi talebine ilişkin bir belge olmalıdır.

2. Üst üste iki Genel Kurul toplantısı: Öğrencinin üst üste iki Genel Kurul toplantısına katılmaması durumunda Yönetim Kurulu tarafından üyeliği sonlandırılabilir.

3. Topluluğun amaçlarına aykırı faaliyette bulunma: Öğrencinin topluluğun amaçlarına aykırı faaliyette bulunması durumunda, Yönetim Kurulu tarafından üyeliği sonlandırılabilir.

4. Görevlerin yerine getirilmemesi: Öğrencilerin verdikleri görevleri yerine getirmemeleri durumunda Yönetim Kurulu tarafından üyeliği sonlandırılabilir.

5. Kayıt yaptırmama ve kayıt yenilememe: Öğrenciler, akademik takvimde belirtilen süre içinde öğrenci bilgi sistemi üzerinden alacağı dersleri seçmek ve kayıt yaptırmak zorundadır. Süresi içinde ders kaydını yapmayan öğrenciler, o dönemde öğrenimine devam etme hakkını kaybeder.

6. Üniversite ile ilişiği kesme: Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre yükseköğretim kurumlarından çıkarma cezası almış olanlar ve kendi istekleri ile kaydını sildiren öğrencilerin Üniversite ile ilişiği kesilir.

7. Tekrar kaydolma: Öğrenciler, yazılı isteği üzerine kaydını sildiren öğrenci, ÖSYM tarafından yeniden yerleştirilmediği veya Üniversite tarafından yapılan ölçme ve değerlendirme sonucunda kayıt hakkı kazanmadığı sürece, Üniversiteye tekrar kaydolamaz.

Bu hususa ilişkin ayrıntılı bilgilere [KAYNAK 1: öğrenci_toplulukları_yönergesi.pdf], [KAYNAK 2: ön_lisans_ve_lisans.pdf], [KAYNAK 3: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf], [KAYNAK 4: işyeri_staj_sözleşmesi.pdf] ve [KAYNAK 5: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf] kaynak belgeleri başvurularak ulaşılabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabili
... (321 karakter daha)
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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=1242ms; student_affairs_orchestrator=1302ms
- **API Sureleri**: api_total=1442ms; dispatch=1328ms; compose=5ms; telemetry=26ms
- **Sure**: 1469.3 ms
- **API Response Time**: 1358.2 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Yanlış bir geri dönüşte ders seçimi nasıl yapacağım?
Ders kayıtlarınızı öğrenci bilgi yönetim sistemi üzerinden yapabilirsiniz. Ders kaydı yaptırmadığınız dönem eğitim süresinden sayılır mı? Evet, ders kaydı yapmadığınız dönemler de eğitim süresinden sayılmaktadır. Bir önceki yarıyıl ders kaydı yaptırmadım. Bir sonraki yarıyıl (bahar) ders kaydı yaptırabilir miyim? Evet, bir sonraki yarıyıl ders kaydı yaptırabilir. Ama önünüzde açıklamada belirtilen koşullara dikkat etmeniz gerekmektedir.
Ders kayıtlı dönemde AKTS kredisi sınırını aşmamak şartı ile üst sınıftan/sınıflardan ders alabilir misiniz? Evet, ders kaydı yaptırdığınız dönem/yılda almakla yükümlü olduğunuz derslerin toplam AKTS kredisi bir dönemde/yılda alınabilecek toplam AKTS kredisinin altında ise dönemdeki/yıldaki AKTS kredisi sınırını aşmamak şartı ile üst sınıftan/sınıflardan ders alabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
