# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 00:18:52
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 71.4% |
| Anahtar Bilgi Kapsami | 40.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 14804.8 ms |
| Medyan Sure | 17488.7 ms |
| Intent Analizi Aktif | 0/7 |
| Force LLM Sentez | 0/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=7, query_failures=0, agent_tasks=9, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 1/4 | 1398.9 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 27951.6 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 7895.7 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 27988.0 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 17488.7 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | YANLIS (rag) | 0/4 | 1283.4 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 19627.2 | - |

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
- **Ajan Sureleri**: graduation_agent=1224ms; student_affairs_orchestrator=1301ms
- **Sure**: 1398.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Soru:
Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

Yanit:
Evet, başarısız olduğunuz seçmeli ders yerine başka bir seçmeli ders seçebilir ve devam zorunluluğunuz devam eder. Ancak, devam zorunluluğu yerine getirmediğiniz dersler için devam zorunluluğu zorunludur.

Kaynak:
[Kaynak 2: yonetmelik_onlisans_lisans_egitim_ogretim.pdf]
MADDE 17-(1) öğrenciler yüz yüze yürütülen derslerin teorik saatlerinin en az % 70’ine devam etmeleri zorunludur. Bu oranlar, uzaktan eğitim yoluyla verilen örgün eğitim derslerinde aynı sırayla % 80 ve % 90 olarak uygulanır.

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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: tuition_agent=9ms; finance_orchestrator=91ms; regulation_agent=6459ms; academic_programs_orchestrator=6565ms
- **Sure**: 27951.6 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Benchmark, ÇAP Programına Başvuru Şartları ve Harç Borç Ödeme
Nedir ve Ne Kadar Ödenir?
ÇAP programına başvuru yapmak için harç borcunuzun ödendiğini kanıtlamanız gerekir. Ödemeyi yaptıktan sonra, ÇAP programına başvurunuzu devam edebilirsiniz.

Bu süreçte dikkat edacağınız en önemli şey, öğrenci bilgilerinizi güncellemek ve harç borcu ödeme koşullarını yerine getirmektir. Örnegin, her akademik yılın hükmü çerçevesinde harç borcunu ödememizin önemi bulunur.

Belirtilen Bilgi:
Açık olan bilginin ışığına göre öğrenci bilgisi güncellenmelidir ve öğrencinin ödemesi için gerekli süreç tamamlanmalıdır.

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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=2650ms; student_affairs_orchestrator=2780ms
- **Sure**: 7895.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar:

- Kurum içi yatay geçiş, aynı üniversitedeki farklı diploma programlarına yapılan geçiştir.
- Kurum içi yatay geçiş başvuruları, kurum içi kontenjanlara göre değerlendirilir ve geçiş kontenjanları, diploma programının son dört yıla ait taban puanları ve başvuru şartları, son başvurunun kabul edileceği günden en az 15 gün öncesinde kurumun web sayfasında ilan edilir.
- Kurum içi yatay geçiş için öğrencinin kayıtlı olduğu programda bitirdiği dönemlere ait genel not ortalamasının 4 üzerinden en az 2,80 olması ve öğrencinin müfredatında yer alan bütün dersleri almış olması gerekir. 
- Disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez.
 
Buna karşı, 
- Kurumlar arası yatay geçiş ise bir üniversiteden farklı bir üniversite veya yüksek teknoloji enstitüsüne yapılan geçiştir.
- Kurumlararası yatay geçiş için öğrencinin kayıtlı olduğu programda bitirmiş olduğu dönemlere ait genel not ortalamasının 4’lük sistem kullanan üniversiteler için en az 2,80, 100’lük sistem kullanan üniversiteler için en az 72 olması gerekir.
- Kurumlararası yatay geçiş için öğrencinin müfredatında yer alan bütün derslerini almış olması ve geçişin eşdeğer diploma programlarına yapılması gerekir. 
 
Bu konularda, başvuru birim komisyonlarınca değerlendirilerek uygun görülen sınıfa öğrencinin intibakı yapılır ve yatay geçişte derslerin tamamını başarmış olma şartı aranmaz.
 
Not: Bu konularda Ondokuz Mayıs Üniversitesi'nin web sayfaları ile ilgili bilgiler 1.1.2.1.6 (2025-2026 Bahar Yatay Geçiş İlan Metni) ve 1.2.1.1.2 (2025-2026 Güz Yarıyıl Yatay Geçiş İlan Metni) kaynaklarında belirtilmiştir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_ya
... (75 karakter daha)
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
- **Ajan Sureleri**: graduation_agent=15732ms; student_affairs_orchestrator=15829ms
- **Sure**: 27988.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Sporun cevabı:

- Diplomamı kaybettim:
 Öncelikle, OMU Opretmenlik Sistemine (OPS) giriş yapınız ve "Diploma" sekmesine tıklayarak "Diploma Kaybı Bildirimi" formunu doldurunuz. Bu formda, neden diplomamı kaybettirdiğiniz ve neler yaptığınızı belirtiniz. Kaybettirdiğiniz diplomanın türünü ve sayısını da belirtiniz.

 Daha sonra, ilgili bölümüne (Fakülte veya Bölümü) başvurunuz ve diploma kaybı bildirimini onlara iletiniz.

- E-devlette mezuniyet bilgilerim görünmedi:
 Öncelikle, OMU Opretmenlik Sistemine (OPS) giriş yapınız ve "Kariyer" sekmesine tıklayarak "Mezuniyet" formuna bakınız. Eğer e-devlette mezuniyet bilgilerinizi görüntülemiyorsanız, "Diploma Kaybı Bildirimi" formunu doldurmanız gerekebilir. Bu formu doldurduktan sonra, ilgili bölümüne (Fakülte veya Bölümü) başvurunuz ve mezuniyet bilgi kaydınızı düzellettiriniz.

 E-devlette mezuniyet bilgilerinizi güncellemek için; OPS sistemi üzerinden "Kariyer" sekmesine tıklayınız, "Mezuniyet" formuna bakınız, varsa diploma kaybı bildirimini silmeye çalışınız, tekrar başvurunuz ve "Mezuniyet Bildirim" formunu doldurunuz.

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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: graduation_agent=3824ms; student_affairs_orchestrator=4703ms
- **Sure**: 17488.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Sınavda kopya çekilmesinin cezası:
Cevap: Kopya çekilmesinin cezası, sınav görevlisinin tespitine göre öğrencinin disiplin suçu olarak belirlenir. Bu durum, öğrencinin kopya çektiğinin tespiti üzerine uyarıda bulunulmaksızın işlem yapılmasını sağlamaktadır.

Disiplin süreci nasıl işler?
Cevap: Disiplin süreci, öğrencinin sınavda kopya çektiğinin tespit edilmesine bağlı olarak başlatılır. Görev alınan gözetmen veya ilgili öğretim elemanı, öğrenci ile ilgili işlemleri görür. Bu süreçte, öğrencinin disiplin suçu işlemiş olması nedeniyle, öğrenci hakkında işlem yapılabilir.

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
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [ ] birim
- **Ajan Sureleri**: registration_agent=4ms; student_affairs_orchestrator=92ms
- **Sure**: 1283.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, En ilgili ogrenci isleri kaynaginda su bilgi yer aliyor:
MADDE 18 - (1) Öğrencinin mezuniyet ve benzeri nedenlerle Üniversitemiz ile ilişiğinin kesilmesi gibi olağan süreçler dışında; a) Öğrencinin yazılı talebi, b) Geçerli bir mazereti olmaksızın, üst üste iki Genel Kurul toplantısına katılmaması, c) Topluluğun amaçlarına aykırı faaliyette bulunulması, ç) Verilen görevlerin yerine getirilmemesi, durumlarında, Yönetim Kurulu kararı ve Akademik danışman onayı ile üyeliği sonlandırılır. Üyelikten çıkarılan öğrenci tebliğ tarihinden itibaren 7 gün içinde SKSDB’ye itiraz başvurusunda bulunabilir. İtiraz başvurusu, başvuru tarihinden sonra toplanan ilk Etkinlik Kurulunda görüşülerek karara bağlanır. (2) Uyarma ve kınama dışında başkaca bir disiplin cezası alan öğrencinin üyeliği cezanın verildiği tarihte kendiliğinden sona erer. (3) Üyeliğine son verilen öğrenci aynı topluluğa yeniden üye olamaz. Toplulukların adı ve logosu

(Kaynak: öğrenci_toplulukları_yönergesi.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

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
- **Ajan Sureleri**: graduation_agent=19424ms; student_affairs_orchestrator=19495ms
- **Sure**: 19627.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Siz 1 yıl boyunca okulumdan uzakta kaldınız ve şimdi ders eklemeye hazırsınız. İşte size bilgi:

1. Kayıt dönemi başlayana kadar transkript/müfredat kontrolü yaparak akademik takvimde tanımlanan süre içerisinde ders kaydını yapma ihtiyacınız vardır.

Kaynak: [Kaynak 5: sık_sorulan_sorular.txt]

2. Ders kaydını yaptıktan sonra, derslere başladığında sınıf yoklama listesinde adınız yoksa danışmanınıza uğramalısınız.

Kaynak: [Kaynak 5: sık_sorulan_sorular.txt]

3. Derslerini uzaktan eğitim yoluyla alabilmek için, ders kayıt esnasında dersler olarak UZAKTAN EĞİTİM ve YÜZYÜZE EĞİTİM şeklinde iki alternatif sunulacaktır. Dilediğiniz eğitim şeklini ilk kayıt aşamasında tercih etmelisiniz.

Kaynak: [Kaynak 5: sık_sorulan_sorular.txt]

4. Kayıt dondurma işlemi için gerekli koşulların sağlanmasını ve ilgili birim yönetim Kurulu kararını beklemenizi gerektirir. 

Kaynak: [Kaynak 1: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf]

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
```
