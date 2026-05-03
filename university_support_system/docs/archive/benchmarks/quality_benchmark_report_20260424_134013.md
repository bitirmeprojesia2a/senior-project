# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 13:40:13
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 40.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3338.0 ms |
| Medyan Sure | 2231.8 ms |
| Intent Analizi Aktif | 7/7 |
| Force LLM Sentez | 5/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=6, query_failures=0, agent_tasks=10, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 1/4 | 975.2 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 7255.5 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 5967.1 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 3108.2 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 2024.7 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 2231.8 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 1803.4 | - |

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
- **Ajan Sureleri**: graduation_agent=809ms; student_affairs_orchestrator=862ms
- **API Sureleri**: api_total=968ms; dispatch=880ms; compose=3ms; telemetry=9ms
- **Sure**: 975.2 ms
- **API Response Time**: 907.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Siz, başarısız olduğunuz seçmeli ders yerine başka bir seçmeli ders seçerseniz devam zorunluluğunuz değişmez. Yaz okulunda devam zorunluluğu vardır, ancak başarısız olunan dersler için normal dönemde devam zorunlululuğu yerine getirilmez. Başarıyla bitirdiğiniz dersler için ise harfli başarı notu verilir.

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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=factual
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: tuition_agent=11ms; finance_orchestrator=191ms; regulation_agent=4600ms; academic_programs_orchestrator=5040ms; registration_agent=2924ms; student_affairs_orchestrator=3000ms
- **API Sureleri**: api_total=7215ms; dispatch=5157ms; global_llm=1084ms; compose=1116ms; telemetry=13ms
- **Sure**: 7255.5 ms
- **API Response Time**: 7169.0 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Merhaba,

ÇAP programına başvurmak üzeresiniz ama harç borcu var. Başvuru şartları neler ve harç borcunuzu nasıl ödeyebileceğiniz hakkında bilgi almak istiyorsunuz.

Öncelikle, ÇAP programına başvururken bazı şartlar ve kurallar var. Bunlardan bazıları:

* Ana dal not ortalamanız en az ilk % 20'si 4,00 üzerinden 2,75'in altında olmalı.
* Fazla kredi tamamlamış olan öğrencilere öncelik verilir.
* Başarı sıralamasını 1. dan belirlenmiş olmalısınız.

Harç borcunuzu ödemenin yolu da var:

* Öğrenim ücreti için Turk öğrenci Mühendislik Fakültesi bilgisi veritabanında kaydı var. Yıllık ücret 2.397,00 TL, dönemlik ücret 1.198,50 TL.

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
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=2947ms; student_affairs_orchestrator=3045ms; international_agent=3187ms; academic_programs_orchestrator=3288ms
- **API Sureleri**: api_total=5951ms; dispatch=3326ms; global_llm=1641ms; compose=1676ms; telemetry=8ms
- **Sure**: 5967.1 ms
- **API Response Time**: 5900.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl diferenteslik gösterir?

Siz, kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar ve başvuru şartları ile değerlendirme kriterleri hakkında bilgi arıyorsunuz.

Kurum içi yatay Geçiş: 

* Aynı yükseköğretim kurumunda (OMU) farklı bölümlere geçmekle ilgilidir. 
* Eğitim dili Türkçe olan bölümlere geçiş yapılır.
* GENEL NOT ORTALAMASININ %50'Sİ VE MERKEZİ YERLEŞTİRME PUANININ %30'U, veya retim kurumunda herhangi bir disiplin cezası yaşamamış olması gerekir.
* DİĞER BAŞVURULARA GÖRE, YATAY GEÇİŞ KONTENJANLARI, İLGİLİ DİPL PROGRAMININ SON DÖRDÜ YILA AİT TABAN PUANLARI, PROGRAMA GÖRE SAME BİRİMDEKİ PROGRAMLAR İLE BİLERİ BİRİMDE PROGRAMLARIN KURUM İÇİ KONTENJANLARI, üniversitemizin aynı düzey programlar arasındaki yatay geçiş başvurusunda öğrencinin özel yetenek sınavı ile öğrenci kabul edilen diploma programlarına kurum içi yatay geçiş şarttır.

Kurumlararası Yatay Geçiş: 

* Farklı yükseköğretim kurumlarından yatay geçiş applicantsı, Yükseköğretim Kurulu tarafından tanınan yurt dışı lisansüstü programlara geçiş başvurusu kabul edilen uluslararası öğrencinin intibaki yapılırken alacağı ve muafiyeti göz önüne alınır.
* GENEL NOT ORTALAMASININ EN AZ 2.80 OLMASI GEREKİR.
* BAŞVURU ŞARTLARI VE DEĞERLENDİRME KRITERLERİ DE FAZLA ŞARTLAR SAĞLAR.

Sorusanız, en önemli fark olarak başvuruların süresi ve değerlendirme kriterleri sayılabilir.
2025-2026 Bahar Yatay Geçiş İlan Metni, Yükseköğretim Kurulu, Ondokuz Mayıs Üniversitesi Öğretim Kurumları

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: 2025_2026_gü
... (262 karakter daha)
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
- **Ajan Sureleri**: graduation_agent=2029ms; student_affairs_orchestrator=2092ms
- **API Sureleri**: api_total=3097ms; dispatch=2111ms; compose=3ms; telemetry=11ms
- **Sure**: 3108.2 ms
- **API Response Time**: 3046.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Siz diploma kayıp sorununuzu halletmek için Öykü Bürosu'na başvurabilirsiniz. Daha sonra mezuniyet bilgilerinizi güncellemek için e-devlet üzerinden başvuruda bulunabilirsiniz. 
Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor ne yapmalıyım?

Cevap bulunamadı.

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
- **Ajan Sureleri**: graduation_agent=1825ms; student_affairs_orchestrator=1886ms
- **API Sureleri**: api_total=2014ms; dispatch=1905ms; compose=5ms; telemetry=7ms
- **Sure**: 2024.7 ms
- **API Response Time**: 1957.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Siz, sınavda kopya çekilmesinin cezası hakkında bilgi almak istiyorsunuz. Buna göre, yapılan açıklamalar ve düzenlemeler gereği sınav görevlileri, öğrencilere kopya muamelesi yapabilir. Bu durum disiplin suçudur ve öğrencinin sınav görevlisi izin almadan önce yoklama işleminden çıkması durumun tespitine yol açabilir. Cevaplamada belirtildiği gibi, bu durum 15 dakika kısa süre olmamak üzere ve sınav görevlisinden izin alındıktan sonra ve sınav salonundan çıkana kadar ortaya çıkabilir.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

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
- **Ajan Sureleri**: registration_agent=1185ms; student_affairs_orchestrator=1262ms
- **API Sureleri**: api_total=2216ms; dispatch=1296ms; compose=12ms; telemetry=12ms
- **Sure**: 2231.8 ms
- **API Response Time**: 2157.2 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Öncelikle, üniversiteyi bırakmak isteyenlerin dikkat etmesi gereken birkaç önemli şey var:

- Universitel ile ilişiği kesmek istiyorsanız, kaydınızı silmeniz gerekir. Üniversite ile ilişiğiniz kesilir.
- Eğer ders sayinizi bire indiremiyorsanız, üniversite ile ilişiğiniz kesilir.
- Kaydı silmek için akademik takvimde belirtilen süre içinde yazılı isteğinizle üniversiteye başvurmanız gerekir.
- Ayrıca, kaydı sildikten sonra ÖSYM tarafından yeniden yerleştirildikten sonra Üniversiteye tekrar kaydolabilirsiniz.
- Ders kaydını yapmamakta büyük bir sorun yoktur, ancak akademik takvimde belirtilen süre içinde yapılırsa sorun olmaz. 
- Eğer ders kaydı yapamazsanız, o dönemde öğrenimine devam etme hakkınızı kaybedersiniz.
- Öğrenciler, her dönem/yıl başında akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden ders kaydını gerçekleştirebilirler.
- Bir dönem/yıl kayıt yaptıracakları derslerin AKTS kredileri toplamı, kayıt yaptıracakları dönem/yıl içi AKTS kredi yükünü fazla etmekten kaçınmaları gerekir.
- Muafiyet dersleri nedeni ile oluşan notlar, dönemdeki AKTS kredi yükünü fazla artırmaması gerekmektedir.

Bu konuda elimdeki kaynaklarda net bilgi bulunamıdi.

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
- **Ajan Sureleri**: registration_agent=1120ms; student_affairs_orchestrator=1287ms
- **API Sureleri**: api_total=1732ms; dispatch=1389ms; compose=17ms; telemetry=43ms
- **Sure**: 1803.4 ms
- **API Response Time**: 1576.2 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Siz yeniden ders seçimi yapacaksınız. Açıklanan süreçlere göre, ders seçiminde öncelikle başarısız olunan veya alamadığınız dersleri almalısınız. Eğer dilme koşuluyla öğrenci olmak istiyorsanız, akademik takvimde belirtilen süre içinde yapmalısınız. Ayrıca, ikilikten itibaren ardıık gerektiren dersler için danışman onayına dikkat edin.

Kayıt yenileme sırasında 6 AKTS, 10 AKTS, 12 AKTS veya 15 AKTS tutarındaki artırım hakkı bulunduğundan, bu haklardan yararlanabilir ve muafiyet aldığınız derslerin AKTS'sine kadar üst dönemlerden ders alabilirsiniz.

Kayıt dondurma süresinin bitiminde, öğrenimine kaldığı yerden devam edeceksiniz ve süre hesabına dahil edilmeyecektir.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
```
