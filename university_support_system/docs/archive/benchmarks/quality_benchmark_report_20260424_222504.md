# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 22:25:04
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 96.0% |
| Uretim Modu Dogrulugu | 96.0% |
| Anahtar Bilgi Kapsami | 66.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 11796.5 ms |
| Medyan Sure | 10417.2 ms |
| Intent Analizi Aktif | 24/25 |
| Force LLM Sentez | 21/25 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=25, query_failures=0, agent_tasks=41, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 2/4 | 17421.8 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 3/3 | 21867.5 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 2/4 | 9000.6 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 3/4 | 10281.1 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 16221.1 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 2/4 | 16692.6 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 11553.5 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 3/5 | 11402.1 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 4/5 | 16702.5 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 9202.5 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 1/4 | 8057.9 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 4/4 | 7696.7 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 15222.9 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 4/4 | 11539.4 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 3/3 | 9397.5 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 4/4 | 9639.8 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 1/5 | 10263.8 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 4/4 | 8451.8 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 2/6 | 12863.7 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 8893.2 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | YANLIS | OK | 2/5 | 7945.8 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 10417.2 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 14086.9 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 0/4 | 9458.9 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 3/3 | 10630.7 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] üç hafta
  - [x] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=14249ms; academic_programs_orchestrator=14348ms; registration_agent=14296ms; student_affairs_orchestrator=14386ms
- **API Sureleri**: api_total=17421ms; dispatch=14426ms; global_llm=1621ms; compose=1691ms; telemetry=12ms
- **Sure**: 17421.8 ms
- **API Response Time**: 17301.4 ms
- **Kaynak Sayisi**: 11

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, Dekanlığa/Müdürlüğe muafiyet dilekçesi vererek muafiyet başvurusunu yapmalıdır. Muafiyet başvurusu sonuçlanıncaya kadar, bu derse kayıt yaptırıp devam etmeniz önem arz etmektedir. Birim Yönetim Kurulu’nun muafiyet talebini uygun görmesi ve muaf olunan derslerin sisteme işlenmesi sonrasında, danışmanınız ile birlikte alacak olduğunuz derslere kaydınız yapılır. 
- Daha önce aldığınız ve başarılı olduğunuz derslerden muaf olmak için muafiyet başvurusu yapılmaktadır.
- Muafiyet başvurusu sonuçlanıncaya kadar derslere devam etmeniz önemlidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
```

### Q2: Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi ve sınavda başarılı sayılmam için minimum not kaç?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] staj
  - [x] tamamla
  - [x] CC
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: internship_agent=18711ms; student_affairs_orchestrator=19475ms; curriculum_agent=13955ms; academic_programs_orchestrator=14060ms
- **API Sureleri**: api_total=21837ms; dispatch=19575ms; global_llm=1232ms; compose=1256ms; telemetry=9ms
- **Sure**: 21867.5 ms
- **API Response Time**: 21791.5 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Tek ders sınavına girebilmek için stajınızı tamamlamış olmanız gerekmez. Sınavda başarılı sayılmak için minimum not CC olmalıdır. 

Ayrıca, tek ders sınavına ilişkin şartları ve başarı koşullarını incelemeniz önerilir. 
Sınav başvurusuyla ilgili detaylı bilgi bulunmamaktadır. 
Sınav haklarınızla ilgili olarak akademik takvime göre açılan sınavlara girme hakkınız vardır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: yonerge_uluslararasi_ogrenci_kabul.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
```

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] değiştirebilir
  - [ ] devam koşulu
  - [x] yeni
  - [x] ders
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=8771ms; student_affairs_orchestrator=8889ms
- **API Sureleri**: api_total=8979ms; dispatch=8911ms; compose=3ms; telemetry=9ms
- **Sure**: 9000.6 ms
- **API Response Time**: 8928.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Başarısız olduğunuz seçmeli ders yerine yeni seçtiğiniz seçmeli derse devam şartınız doğacaktır. Başarısız olduğunuz seçmeli ders yerine bir başka seçmeli dersi alabilirsiniz, ancak bu durumda da yeni seçilen derse devam etmeniz zorunludur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q4: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: hard
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] transkript
  - [x] dahil
  - [x] ortalama
  - [ ] tamamlamıştır
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: regulation_agent=10041ms; academic_programs_orchestrator=10129ms
- **API Sureleri**: api_total=10266ms; dispatch=10172ms; compose=4ms; telemetry=9ms
- **Sure**: 10281.1 ms
- **API Response Time**: 10193.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Pedagojik formasyon dersleri transkripte dahil ediliyor. Mezuniyet ortalamasına da etkisi var. Diplomada, tüm pedagojik formasyon eğitimi derslerini tamamlayan öğrenciler için "pedagojik formasyon eğitimi tamamladı" ibaresi yer alıyor. Ancak tüm dersleri tamamlamayan öğrencilerin diplomalarında bu eğitimini tamamladığına dair ifade yer almayacak, sadece transkriptinde aldığı dersler yer alacak. (MADDE 5, lisansı pedagojik formasyon derslerine ilişkin)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt
- Belge: lisans_pedagojik_formasyon_derslerine_ilişkin.pdf
- Belge: uygulama_esaslari_lisans_pedagojik_formasyon.pdf
```

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs', 'finance'] (beklenen: ['academic_programs', 'finance', 'student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] ücret
  - [x] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: international_agent=14714ms; academic_programs_orchestrator=14791ms; registration_agent=14519ms; student_affairs_orchestrator=14596ms; tuition_agent=7ms; finance_orchestrator=74ms
- **API Sureleri**: api_total=16206ms; dispatch=14858ms; global_llm=1238ms; compose=1267ms; telemetry=9ms
- **Sure**: 16221.1 ms
- **API Response Time**: 16153.8 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Öğrenim ücretini Üniversite'ye ödemeniz gerekir. Ödemenin nasıl ve nereye yapılacağı konusunda finans birimi ile iletişime geçmeniz önerilir. İkamet izni için Göç İdaresi İl Müdürlüğü'nden öğrenci ikamet izni almanız zorunludur. Bu işlemler için gerekli belgelerin tam listesi verilmemiştir, ancak not çizelgesi (transkript) ve dilekçe ile başvuru yapmanız gerekir. İlgili birimlere başvurarak detailed bilgi alabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: uluslararası_öğrenci_ikamet_işlemleri.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: uluslararası_öğrenci.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
- Belge: öğrenci_konukevi_uygulama_yönergesi.pdf
- Belge: yonerge_onlisans_lisans_staj.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] not ortalaması
  - [ ] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: tuition_agent=8ms; finance_orchestrator=70ms; registration_agent=12568ms; student_affairs_orchestrator=12633ms; regulation_agent=12588ms; academic_programs_orchestrator=12654ms
- **API Sureleri**: api_total=16666ms; dispatch=12722ms; global_llm=1477ms; compose=1521ms; telemetry=12ms
- **Sure**: 16692.6 ms
- **API Response Time**: 16599.5 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
ÇAP programına başvurabilmeniz için katkı payı/öğrenim ücreti borcunuzu ödemelisiniz. Ana dal programınızın ilgili sınıfında bulunmanız, ana dal not ortalamanızın 4,00 üzerinden en az 3,00 olması ve başvuru sıralamasında en az ilk %20'de bulunmanız gerekmektedir. Ayrıca, kayıt olduğu programdan azami süre içinde mezun olamayan öğrenciler için %10 oranında katkı payı/öğrenim ücreti ödemesi gerekmektedir. Ödeme işleminiz için kurumun ilgili bölümleriyle iletişime geçiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: VT
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
```

### Q7: Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra ders kaydını nasıl yapacağım, danışmanın onay süreci nasıl işliyor?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=9535ms; student_affairs_orchestrator=9602ms; tuition_agent=6ms; finance_orchestrator=54ms
- **API Sureleri**: api_total=11549ms; dispatch=9637ms; global_llm=1800ms; compose=1827ms; telemetry=13ms
- **Sure**: 11553.5 ms
- **API Response Time**: 11478.5 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, akademik takvimde belirtilen süre içinde öğrenci bilgi sistemi üzerinden ders kaydını yapabilirsiniz. Ders kaydını tamamladıktan sonra, akademik danışmanınızla iletişime geçerek ders seçimini onaylatmanız gerekmektedir. Danışman onay sürecinde, seçtiğiniz derslerden bazıları danışmanınız tarafından listeden çıkarılabilir. 
- Ders kaydı yaparken, erfolgreich olduğunuz ve alamadıkları alt dönem derslerini öncelikle almanız gerekmektedir.
- AKTS kredileri toplamı; GANO'su 1,80-2,49 arası olan öğrenciler için
- Akademik takvimde belirtilen süre içinde ders kaydını yapmayan öğrenciler, o dönemde öğrenimlerine devam etme hakkını kaybetmeyebilirler.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [ ] bildiri
  - [ ] harç
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=11179ms; student_affairs_orchestrator=11254ms; tuition_agent=9385ms; finance_orchestrator=9456ms
- **API Sureleri**: api_total=11388ms; dispatch=11305ms; compose=3ms; telemetry=11ms
- **Sure**: 11402.1 ms
- **API Response Time**: 11330.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bursunuzun devri veya kesilip kesilmeyeceği konusunda bilgiye ulaşmak için burs aldığınız kurumla iletişim kurmanız gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: ön_lisans_ve_lisans.pdf
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs', 'finance'] (beklenen: ['academic_programs', 'student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [ ] azami
  - [x] ek
  - [x] süre
  - [x] katkı payı
  - [x] öde
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=15170ms; academic_programs_orchestrator=15247ms; graduation_agent=14777ms; student_affairs_orchestrator=14866ms; tuition_agent=12661ms; finance_orchestrator=12781ms
- **API Sureleri**: api_total=16698ms; dispatch=15330ms; global_llm=1251ms; compose=1298ms; telemetry=11ms
- **Sure**: 16702.5 ms
- **API Response Time**: 16651.5 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Program süresini aşmanız durumunda, ilgili dönem katkı payı ücreti ödenir. 4. sınıf öğrencisi olduğunuz için ek süre hakkınız var ve bu sürede katkı payı ödersiniz._contributörların ödemekle yükümlü oldukları katkı payı/öğrenim ücreti ile ilgili hususlar 2547 sayılı Kanunun 46. maddesine göre belirlenir. Ek süre boyunca katkı payı ödemeniz zorunlu görünüyor.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM
- Finans: RAG + LLM

Kaynak Ozeti:
- Belge: tıp_fakültesi_tıp_doktorluğu_programı.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: öğretim_üyesi_yetiştirme_programı_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
```

### Q10: Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [x] tekrar
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=8871ms; student_affairs_orchestrator=8940ms
- **API Sureleri**: api_total=9179ms; dispatch=8980ms; compose=2ms; telemetry=6ms
- **Sure**: 9202.5 ms
- **API Response Time**: 9132.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Bu dersi, dersin açıldığı proxima dönemin başlangıcında tekrar alabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [x] öğrenim ücreti
  - [ ] gerek yok
  - [ ] yönetim kurulu
  - [ ] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=6705ms; student_affairs_orchestrator=6783ms; tuition_agent=6ms; finance_orchestrator=48ms
- **API Sureleri**: api_total=8041ms; dispatch=6811ms; global_llm=1157ms; compose=1176ms; telemetry=12ms
- **Sure**: 8057.9 ms
- **API Response Time**: 8000.1 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Kayıt dondurmak istediğiniz dönemde harç ücretini ödemeniz gerekmez. Kayıt dondurduğunuz süre, eğitim sürenizden sayılır. 
- Kayıt dondururken katkı payı veya öğrenim ücreti ödemeniz gerekmez.
- Eğitim süreniz azami süre hesabında kayıt dondurma odu dahil edilir.
- Öğrenim ücreti ve katkı payı ile ilgili bilgiler finans birimi tarafından verilmiştir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] transkript
  - [x] Ek Madde
  - [x] başvuru yapabilir
  - [x] GANO
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=7549ms; student_affairs_orchestrator=7596ms
- **API Sureleri**: api_total=7681ms; dispatch=7615ms; compose=4ms; telemetry=9ms
- **Sure**: 7696.7 ms
- **API Response Time**: 7631.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Hazırlık sınıfındaysanız ve transkriptiniz yoksa, Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilirsiniz. Transkriptiniz olmadan da başvuru yapabilirsiniz. Ek Madde-1 kapsamında yapılan yatay geçiş başvurularında GANO'su değerlendirme aşamasında etkili değildir. Bir döneme en fazla 2 yatay geçiş başvurusu yapılabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: sık_sorulan_sorular.txt
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=11629ms; student_affairs_orchestrator=11693ms; curriculum_agent=12162ms; academic_programs_orchestrator=12280ms
- **API Sureleri**: api_total=15209ms; dispatch=12365ms; global_llm=1398ms; compose=1470ms; telemetry=23ms
- **Sure**: 15222.9 ms
- **API Response Time**: 15096.2 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
Kurum içi yatay geçiş ve kurumlar arası yatay geçiş arasındaki farklar, başvuru şartları ve değerlendirme kriterleri farklılık gösterir. Kurum içi yatay geçiş için genel not ortalamasının 4 üzerinden en az 2,80 olması gerekir. Kurumlar arası yatay geçişte ise öğrencinin kayıt olduğu yıldaki merkezi yerleştirme puanının, geçmek istediği programın taban puanına eşit ya da yüksek olması durumunda herhangi bir başarı şartı aranmaz. 
Ayrıca, 
- Disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez.
- Programların kurum içi kontenjanları ve aynı birimdeki programlar ile diğer birimlerdeki kontenjanlar da değerlendirme sürecinde önemli rol oynar.
- Kurum içi yatay geçişte, genel not ortalamasının 4.00 üzerinden 2,50 olması gerekir ve yatay geçiş başvuruları, sadece ilan edilen süre içerisinde yapılır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
```

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] bağıl
  - [x] mutlak
  - [x] 10
  - [x] öğrenci sayısı
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=10415ms; student_affairs_orchestrator=10497ms; curriculum_agent=10470ms; academic_programs_orchestrator=10534ms
- **API Sureleri**: api_total=11503ms; dispatch=10588ms; compose=5ms; telemetry=8ms
- **Sure**: 11539.4 ms
- **API Response Time**: 11458.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark, Notların hesaplanması ve dağıtılma şeklini ifade eder. Bağıl değerlendirme, öğrencilerin birbirleriyle kıyaslanarak notlandırılmasına dayanırken, mutlak değerlendirme, öğrencilerin belirli bir standarda göre notlandırılmasına dayanır. 
Bağıl değerlendirmeye katılan öğrenci sayısı 10 ve altında ise, öğrenci otomasyon sistemi ham başarı puanını mutlak değerlendirme yaparak notlar verilir. Öğrenci sayısı 10 ve üstünde ise, bağıl değerlendirme sistemi kullanılır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: bağıl_değerlendirme_yönergesi.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonerge_bagil_degerlendirme.pdf
```

### Q15: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] diploma eki
  - [x] transkript
  - [x] yerine geçmez
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=8285ms; student_affairs_orchestrator=8342ms
- **API Sureleri**: api_total=9378ms; dispatch=8383ms; compose=6ms; telemetry=8ms
- **Sure**: 9397.5 ms
- **API Response Time**: 9315.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Diploma eki ile transkript arasındaki fark, diploma ekinin kişinin takip edip başarıyla tamamladığı öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmesi iken, transkript kişinin not çizelgesini gösterir. Diploma eki transkript veya diploma yerine geçmez. 

Diploma eki, yurtdışında daha okunabilir ve mukayese edilebilir bir diploma, akademik güzergahının ve yurtiçinde ve yurtdışında edindiği yeti ve becerilerin tam bir tarifi, başarı ve yetilerinin nesnel ve adil değerlendirmesi, geleceğe yönelik olarak yurtdışında iş ve eğitim imkanlarına daha rahat ulaşma olanağı, iş bulma olanaklarını artırma kazanımlarını elde edebilmenizi sağlar.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] kayıt dondurma
  - [x] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=8398ms; student_affairs_orchestrator=8486ms
- **API Sureleri**: api_total=9631ms; dispatch=8531ms; compose=6ms; telemetry=12ms
- **Sure**: 9639.8 ms
- **API Response Time**: 9577.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Kayıt dondurma ile kayıt yaptırmamak arasında bir fark vardır. Kayıt dondurulan süreler eğitim-öğretimden sayılmaz. Kaydını donduran öğrencilerin eğitim-öğretimden sayılmayan bu süreler, öğrencilik haklarını etkilemez. Ancak kayıt yaptırmayan öğrenciler, o dönemde öğrenimine devam etme hakkını kaybeder. Kaydını sildirmek ise öğrencilik hakkının sona ermesi anlamına gelir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/5
  - [ ] UBYS
  - [ ] ders seçimi
  - [x] danışman
  - [ ] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=10075ms; student_affairs_orchestrator=10162ms
- **API Sureleri**: api_total=10248ms; dispatch=10185ms; compose=5ms; telemetry=7ms
- **Sure**: 10263.8 ms
- **API Response Time**: 10207.6 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
İlk kez üniversite kaydını yaptıran bir öğrenci olarak, akademik takvimde belirtilen süre

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
```

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] itiraz
  - [x] beş iş günü
  - [x] dilekçe
  - [x] bölüm başkanlığı
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=8197ms; student_affairs_orchestrator=8261ms
- **API Sureleri**: api_total=8413ms; dispatch=8317ms; compose=8ms; telemetry=11ms
- **Sure**: 8451.8 ms
- **API Response Time**: 8365.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Sınav sonuçlarına, akademik takvimde belirtilen sınav not girişlerinin öğrenci otomasyon sistemine girilmesinin son gününden itibaren beş iş günü içerisinde ilgili birime (Bölüm Başkanlığına) dilekçe vererek itiraz edebilirsiniz. İtiraz üzerine sınav kağıdı incelenir ve işlem yazılı ve gerekçeli olarak yapılır. Ayrıca, öğretim elemanı tarafından fark edilen maddi hataya ilişkin sınav not bildirim/not düzeltme formu notların ilanından sonra düzenlenebilir. Yeniden incelemeye ثلاث iş günü içinde itiraz edilebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans.pdf
```

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/6
  - [ ] ders
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [x] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=11895ms; student_affairs_orchestrator=11970ms
- **API Sureleri**: api_total=12853ms; dispatch=11988ms; compose=7ms; telemetry=9ms
- **Sure**: 12863.7 ms
- **API Response Time**: 12810.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Mezuniyet için gerekli koşulları yerine getirmeniz ve ilişik kesme sürecini başlatmanız gerekmektedir. İlişik kesme sürecini başlatmak için Öğrenci Bilgi Ekranındaki Diğer menüsü altında yer alan "İlişik Kesme Talebinde Bulun" seçeneğini kullanmanız gerekir. İlişik kesme sürecinin tamamlanması, mezun olunduğu anlamına gelmez, mezuniyet ve diploma basım işlemlerinin başlatılması için yapılır. Mezuniyet durumunuzu E-Devlet üzerinden kontrol etmeniz gerekir.

Aşağıdaki adımları takip edebilirsiniz:
- Öğrenim gördüğünüz eğitim-öğretim programında bütün şartları yerine getirmelisiniz.
- Öğrenci Bilgi Ekranındaki Diğer menüsü altında yer alan "İlişik Kesme Talebinde Bulun" seçeneğini kullanınız.
- İlişik kesme süreci tamamlanınca, mezuniyet ve diploma basım işlemleri başlatılır.
- Mezuniyet durumunuzu E-Devlet üzerinden kontrol ediniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: öğrenci_işleri_birimi.txt
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=factual
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=7881ms; student_affairs_orchestrator=7943ms
- **API Sureleri**: api_total=8873ms; dispatch=7968ms; compose=4ms; telemetry=15ms
- **Sure**: 8893.2 ms
- **API Response Time**: 8819.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Diploma kaybettığınız için mahkeme kararı, diploma ücretini yatırdığını gösteren banka dekontu, kimlik fotokopisi ve dilekçe ile başvurmanız halinde diploma yeniden düzenlenir. Mezuniyet bilgilerinizin e-devlette görünmüyor olması durumunda bu konuyla ilgili verilen belgelerde bir hüküm bulunmamaktadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
```

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs', 'academic_programs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [x] %40
  - [ ] %60
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=6907ms; academic_programs_orchestrator=6993ms
- **API Sureleri**: api_total=7931ms; dispatch=7046ms; compose=4ms; telemetry=9ms
- **Sure**: 7945.8 ms
- **API Response Time**: 7889.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Koşullar elverdiği ölçüde tüm sınavların yüz yüze yapılması esastır. Uzaktan verilen dersler için dönem içi değerlendirme, başarıya etkisi %40'tan fazla olamaz. Kismi uzaktan olan derslerin sınavları çevrimiçi olarak da yapılabilecek olup, masa, rapor sunma gibi yöntemlerden biri veya birkaçı kullanılarak yapılmış olabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
- Belge: uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=10213ms; student_affairs_orchestrator=10293ms
- **API Sureleri**: api_total=10392ms; dispatch=10314ms; compose=7ms; telemetry=16ms
- **Sure**: 10417.2 ms
- **API Response Time**: 10338.1 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Sınavda kopya çekilmesinin cezası ve disiplin süreci, 11.03.2023 tarihli resmi gazetede yayımlanan 2547 sayılı Yükseköğretim Kanunu'na göre belirlenmektedir. Ancak, belirtilen belgelerde kopya çekme cezasının cu the detayları yer almamaktadır. Disiplin süreci ve kopya çekmenin kesin cezası için ilgili yükseköğretim kurumunun disiplin hükümlerine başvurmak gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] ilişik kesme
  - [x] UBYS
  - [x] form
  - [x] birim
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=10914ms; student_affairs_orchestrator=10987ms; tuition_agent=8724ms; finance_orchestrator=8804ms
- **API Sureleri**: api_total=14077ms; dispatch=11054ms; global_llm=1542ms; compose=1578ms; telemetry=15ms
- **Sure**: 14086.9 ms
- **API Response Time**: 14023.1 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Üniversiteyi bırakıp ayrılmak istiyorsanız, UBYS üzerinden "İlişik Kesme Talebinde Bulun" seçeneğinden ilişik kesme sürecini başlatabilirsiniz. Ayrıca, şahsen başvurarak ilişik kesme formunu doldurup, belirtilen merkezlerde onaylattıktan sonra öğrenim gördüğünüz birime teslim etmek de yeterli olacaktır. 
Ayrıca dikkat etmeniz gereken hususlar:
* Kaydınızın silinmesi ile birlikte öğrencilik hakkınız sona erecektir.
* Kayıt işlemlerinin iptal edilmesi durumunda, dönemin kayıt ücreti iade edilmeyecektir.
* Disiplin cezası alan öğrencilerin bursları kesilebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 0/4
  - [ ] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=9259ms; student_affairs_orchestrator=9325ms
- **API Sureleri**: api_total=9419ms; dispatch=9349ms; compose=4ms; telemetry=12ms
- **Sure**: 9458.9 ms
- **API Response Time**: 9365.2 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Ders seçimini akademik takvimde belirtilen sürelerde "Öğrenci Bilgi Sistemi" üzerinden yapacak ve sonrasında akademik danışmanınızla iletişime geçerek ders seçimini onaylatacaksınız.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: öğrenci_konseyi_yönergesi.pdf
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] danışman
  - [x] bölüm
  - [x] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=9521ms; student_affairs_orchestrator=9592ms
- **API Sureleri**: api_total=10621ms; dispatch=9624ms; compose=3ms; telemetry=16ms
- **Sure**: 10630.7 ms
- **API Response Time**: 10563.8 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Danışmanınıza ulaşarak durumunuzu bildirmelisiniz. Eğer danışmanınıza ulaşamazsanız, bölüm başkanınıza başvurabilirsiniz. Bölüm başkanınıza da ulaşamazsanız, Dekan/Müdürünüze durumu bildirmelisiniz. Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
```
