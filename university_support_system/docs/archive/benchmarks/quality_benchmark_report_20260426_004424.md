# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-26 00:44:24
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 96.0% |
| Anahtar Bilgi Kapsami | 75.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3959.9 ms |
| Medyan Sure | 4027.3 ms |
| Intent Analizi Aktif | 24/25 |
| Force LLM Sentez | 21/25 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=22, query_failures=0, agent_tasks=43, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 3/4 | 5944.2 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 3/3 | 4483.9 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 2/4 | 2302.0 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 4/4 | 2854.2 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 4027.3 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 4941.1 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 5/5 | 3811.3 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 4274.6 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 5/5 | 4224.7 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 4017.9 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 1/4 | 4062.7 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 2/4 | 2335.9 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 5403.0 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 2/4 | 3382.9 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 3/3 | 4783.6 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 4543.5 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 4/5 | 3042.6 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 4/4 | 2332.1 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 5/6 | 6020.5 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 3938.8 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 2/5 | 4532.0 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 2369.9 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 3957.9 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 2731.9 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 3/3 | 4678.5 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] üç hafta
  - [x] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=3222ms; student_affairs_orchestrator=3423ms; curriculum_agent=3167ms; academic_programs_orchestrator=3400ms
- **API Sureleri**: api_total=5934ms; dispatch=3617ms; final_llm=1020ms; compose=1091ms; telemetry=11ms
- **Sure**: 5944.2 ms
- **API Response Time**: 5860.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Eğitim öğretimin başladığı tarihten itibaren üç hafta içinde daha önce öğrenim gördüğü yükseköğretim kurumlarında aldığı ve başarılı olduğu dersler için muaf olmak istediği dersleri içeren bir dilekçe, onaylı transkript ve onaylı ders içerikleriyle birlikte ilgili birime başvurmanıznecessary. Muafiyet başvurunun sonuçlanmasını beklerken, dönem derslerine devam etmeniz önem arz etmektedir. Birim Yönetim Kurulu’nun muafiyet talebini uygun görmesi ve muaf olunan derslerin sisteme işlenmesi sonrasında, danışman ile birlikte alacak olunan derslerin kaydı yapılır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: internship_agent=2091ms; student_affairs_orchestrator=2181ms; curriculum_agent=2682ms; academic_programs_orchestrator=2751ms
- **API Sureleri**: api_total=4468ms; dispatch=2791ms; final_llm=729ms; compose=755ms; telemetry=14ms
- **Sure**: 4483.9 ms
- **API Response Time**: 4393.8 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Tek ders sınavına girebilmek için stajınızı tamamlamış olmanız gerekmez. Sınavda başarılı sayılmak için minimum not CC'dir. Başarı notu için en az 60 olması da önemlidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: sürekli_eğitim_merkezi_sertifikaya_yönelik_eğitim_programları_yönetmeliği.txt
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
- **Ajan Sureleri**: graduation_agent=2096ms; student_affairs_orchestrator=2195ms
- **API Sureleri**: api_total=2290ms; dispatch=2214ms; compose=3ms; telemetry=9ms
- **Sure**: 2302.0 ms
- **API Response Time**: 2232.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Başarısız olduğunuz seçmeli ders yerine yeni seçtiğiniz seçmeli derse devam şartınız doğacaktır. Yani, yeni seçilen derse en az %70'ine (teorik saatler için) veya en az %80'ine (ders uygulamaları, atölye ve laboratuvarlar için) devam etmeniz zorunludur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_yaz_okulu_egitim_ogretim.pdf
```

### Q4: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: hard
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] transkript
  - [x] dahil
  - [x] ortalama
  - [x] tamamlamıştır
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: regulation_agent=2646ms; academic_programs_orchestrator=2740ms
- **API Sureleri**: api_total=2840ms; dispatch=2761ms; compose=4ms; telemetry=17ms
- **Sure**: 2854.2 ms
- **API Response Time**: 2788.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Pedagojik formasyon dersleri öğrenci transkriptlerine dahil edilecek ve mezuniyet ortalamasına dahil edilecektir. Diplomaların arkasına “Pedagojik formasyon eğitimini tamamlamıştır.” ifadesi yazılacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt
- Belge: lisans_pedagojik_formasyon_derslerine_ilişkin.pdf
- Belge: uygulama_esaslari_lisans_pedagojik_formasyon.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
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
- **Ajan Sureleri**: international_agent=2513ms; academic_programs_orchestrator=2608ms; registration_agent=2520ms; student_affairs_orchestrator=2593ms; tuition_agent=15ms; finance_orchestrator=125ms
- **API Sureleri**: api_total=4017ms; dispatch=2652ms; final_llm=1208ms; compose=1246ms; telemetry=12ms
- **Sure**: 4027.3 ms
- **API Response Time**: 3966.2 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Öğrenim ücretinizi üniversiteye yatırmalısınız. İkamet izni için Göç İdaresi İl Müdürlüğü'ne başvurmanız ve gerekli belgeleri hazırlamanız gerekiyor. Bu belgeler arasında disiplin durumunu gösterir belge, not çizelgesi (transkript) yer alıyor. Ayrıca, kayıt işlemlerinizin tamamlanmış olması, öğrenim ücretinizin iade edilmemesi koşuluna tabi olduğunu unutmayın. Ögrenci Isleri'ne veya finans birimi ile iletişime geçerek öğrenim ücreti ile ilgili detaylı bilgi alabilirsiniz.

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
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_konukevi_uygulama_yönergesi.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs', 'student_affairs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: tuition_agent=5ms; finance_orchestrator=56ms; regulation_agent=2305ms; academic_programs_orchestrator=2358ms; registration_agent=2484ms; student_affairs_orchestrator=2559ms
- **API Sureleri**: api_total=4930ms; dispatch=2613ms; final_llm=1207ms; compose=1238ms; telemetry=17ms
- **Sure**: 4941.1 ms
- **API Response Time**: 4869.7 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
ÇAP başvuru şartları şunlardır: programında yer alan tüm dersleri almış ve başarmış olmanız, başvurusu sırasındaki ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında en az ilk %20'sinde bulunmanız gerekir. Ayrıca, ana dal not ortalamasına öncelik verilir. Harç borcunuzu ödeyerek ÇAP başvuru şartlarından olan "ana dal diploma programında kayıtlı olmak" koşulunu sağlayebilirsiniz. 
Ödeme işlemi sonrasında başvurunuzu yapabilirsiniz. 
ÇAP başvurularının değerlendirilmesinde öncelikle ana dal not ortalamasına, ortalamanın aynı olması durumunda ise genel not ortalamasına göre sıralama yapılır.

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
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```

### Q7: Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra ders kaydını nasıl yapacağım, danışmanın onay süreci nasıl işliyor?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 5/5
  - [x] harç
  - [x] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2594ms; student_affairs_orchestrator=2652ms; tuition_agent=5ms; finance_orchestrator=56ms
- **API Sureleri**: api_total=3786ms; dispatch=2693ms; final_llm=986ms; compose=1019ms; telemetry=17ms
- **Sure**: 3811.3 ms
- **API Response Time**: 3725.0 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Harç ücretini yatırdıktan sonra, akademik takvimde belirlenen süre içinde öğrenci bilgi sisteminden ders kaydınızı yapabilirsiniz. Öncelikle başarısız olduğunuz ve almadığınız alt dönem derslerini alacak şekilde kaydınızı yapmalısınız. Ardışıklik gerektiren dersler için danışman onayınız gerekli olacaktır. Danışmanınızla görüşerek ders kaydınızı onaylatabilirsiniz. 
- Danışmanınıza ulaşamıyorsanız, bölüm başkanınıza veya Dekan/Müdürüğe başvurabilirsiniz.
- Hiçbir yetkiliye ulaşılamadığı takdirde, oidb@omu.edu.tr adresine sistemle ilgili sorununuzu ilgili odeme kanali yolu ile iletebilirsiniz.
- Kayıt dönemi başlamadan transkript/müfredat kontrolü önemlidir.

(Not: Bu cevaptaki bazi bilgiler kaynaklarda dogrudan teyit edilemedi; ilgili birimden dogrulama yapmaniz onerilir.)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [x] bildiri
  - [ ] harç
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2546ms; student_affairs_orchestrator=2663ms; tuition_agent=2620ms; finance_orchestrator=2699ms
- **API Sureleri**: api_total=4255ms; dispatch=2732ms; final_llm=1401ms; compose=1422ms; telemetry=20ms
- **Sure**: 4274.6 ms
- **API Response Time**: 4174.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Burs aldığınız kurumla iletişim kurmanız gerekmektedir. Bursunuzun devri veya kesilip kesilmeyeceği konusunda bilgiye ulaşmak için bunu yapmanız önerilir. Ayrıca, kayıtlı olduğunuz üniversiteden başka bir üniversiteye geçiş yaptığınız takdirde de bursunuz kesilebilir. Bursunuzun devam etmesi için üniversite değişikliğini bildirir dilekçe ile kayıt yaptırdığınız üniversiteye ait öğrenci belgesini burs aldığınız kuruma bildirmanız önemlidir. 
Ayrıca, 
- genel not ortalamasının en az 2.80 olması,
- disiplin cezası almış olmanızın yatay geçiş başvurunuzu etkileyebileceği 
hususlarına dikkat etmeniz gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: idari_ve_mali_işler_birimi.txt
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs', 'finance'] (beklenen: ['academic_programs', 'student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 5/5
  - [x] azami
  - [x] ek
  - [x] süre
  - [x] katkı payı
  - [x] öde
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=2905ms; academic_programs_orchestrator=2999ms; graduation_agent=2900ms; student_affairs_orchestrator=2987ms; tuition_agent=2898ms; finance_orchestrator=2985ms
- **API Sureleri**: api_total=4205ms; dispatch=3069ms; final_llm=1001ms; compose=1040ms; telemetry=26ms
- **Sure**: 4224.7 ms
- **API Response Time**: 4129.1 ms
- **Kaynak Sayisi**: 15

**Yanit:**
```
4. sınıf öğrencisi olan sizlerin program süresini 1 yıl aştığınız durumda, son sınıf öğrencisi olmak koşuluyla, kayıtlı olduğunuz öğretim programından mezun olabilmek için ek süre verilir. Azami eğitim süresi sonunda mezun olamayan öğrencilere ilave iki dönem ek süre verilir ve bu sürede katkı payı ödenir.

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
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: engelli_öğrenciler_eğitim_öğretim_uygulamaları.pdf
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
- **Ajan Sureleri**: graduation_agent=3706ms; student_affairs_orchestrator=3788ms
- **API Sureleri**: api_total=4009ms; dispatch=3807ms; compose=2ms; telemetry=19ms
- **Sure**: 4017.9 ms
- **API Response Time**: 3955.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Bu dersi tekrar almak için ders kaydının yapıldığı dönemde tekrar alabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
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
- **Ajan Sureleri**: registration_agent=2785ms; student_affairs_orchestrator=2859ms; tuition_agent=5ms; finance_orchestrator=62ms
- **API Sureleri**: api_total=4052ms; dispatch=2901ms; final_llm=962ms; compose=978ms; telemetry=17ms
- **Sure**: 4062.7 ms
- **API Response Time**: 3899.3 ms
- **Kaynak Sayisi**: 2

**Yanit:**
```
Kayıt dondurma işlemlerinde, kayıt dondurulan süre içinde öğrenim ücreti ödenmez. Ancak, kayıt dondurmadan önce öğrenim ücretini yatırmış olmanız gerekir. İkinci öğretim öğrencisi olarak, belirli bir yüzdelik dilimde olduğunuz takdirde öğrenim ücretinden muaf olabilirsiniz. Belgelerde belirtilen %10 oranına giren öğrencilerin öğrenim ücreti ödenmez. Kayıt dondurulan süre, eğitim süresinden sayılır. 

- Öğrenim ücreti hakkında daha detaylı bilgi için ilgili mevzuata başvurmanız gerekir.
- Kayıt dondurmadan önce öğrenim ücretinin ödenip ödenmediğine dikkat etmeniz önemlidir.
- Öğrenim ücretinden muafiyet için belirli şartları karşılamış olmanız gerekir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] transkript
  - [x] Ek Madde
  - [ ] başvuru yapabilir
  - [ ] GANO
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=2149ms; student_affairs_orchestrator=2220ms
- **API Sureleri**: api_total=2324ms; dispatch=2241ms; compose=5ms; telemetry=11ms
- **Sure**: 2335.9 ms
- **API Response Time**: 2266.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Hazırlık sınıfındaysanız, Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapamazsınız. Çünkü, bu belgelere göre yatay geçiş için transkriptin olmasınecessary görünüyor ve hazırlık sınıfı öğrencilerinin transkripti yok.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=2902ms; academic_programs_orchestrator=2977ms; registration_agent=2524ms; student_affairs_orchestrator=2616ms
- **API Sureleri**: api_total=5385ms; dispatch=3017ms; final_llm=1323ms; compose=1366ms; telemetry=14ms
- **Sure**: 5403.0 ms
- **API Response Time**: 5310.4 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasında bazı farklar vardır. Kurum içi yatay geçiş, aynı üniversite içerisinde farklı bölümler arasında yapılırken, kurumlar arası yatay geçiş farklı üniversiteler arasında yapılır. Başvuru şartları olarak, genel not ortalamasının belirli bir seviyede olması, disiplin cezası almamış olmak ve ilan edilen kontenjan ve şartlar çerçevesinde başvurunun yapılması önemlidir. Değerlendirme kriterleri olarak, genel not ortalamasının yanı sıra, öğrencinin kayıt olduğu programdaki genel not ortalamasının da dikkate alınır. 
Bunlara ek olarak:
- İkinci öğretimden sadece ikinci öğretim diploma programlarına yatay geçiş yapılabilir, 
- Uzaktan öğretim programlarından uzaktan öğretim programlarına yatay geçiş yapılabilir, 
- Bir dönemde en fazla 2 yatay geçiş başvurusu yapılabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
```

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] bağıl
  - [x] mutlak
  - [ ] 10
  - [ ] öğrenci sayısı
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=2248ms; academic_programs_orchestrator=2321ms
- **API Sureleri**: api_total=3374ms; dispatch=2345ms; compose=4ms; telemetry=12ms
- **Sure**: 3382.9 ms
- **API Response Time**: 3329.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bağıl değerlendirme sistemi, öğrencilerin birbirleriyle kıyaslanarak değerlendirilmesini ifade eder. Mutlak değerlendirme sistemi ise, öğrencilerin belli bir standart veyameasure göre değerlendirilmesini ifade eder. 

Farklı öğrenci sayılarında hangisinin uygulanacağına ilişkin net bir bilgi bulunmamaktadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: yonerge_uluslararasi_ogrenci_kabul.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
```

### Q15: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] diploma eki
  - [x] transkript
  - [x] yerine geçmez
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=2620ms; student_affairs_orchestrator=2694ms; curriculum_agent=2648ms; academic_programs_orchestrator=2719ms
- **API Sureleri**: api_total=4772ms; dispatch=2761ms; final_llm=955ms; compose=982ms; telemetry=10ms
- **Sure**: 4783.6 ms
- **API Response Time**: 4724.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Diploma eki, uluslararası saydamlığı pekiştirmeyi hedefleyen ve elde edilmiş yeti ve becerilerin ifade edildiği bir belgedir. Diploma eki, transkript (not çizelgesi) veya diploma yerine geçmez. 
- Diploma ekinin amacı, kişinin takip edip başarıyla tamamladığı öğrenimin yapısını, düzeyini, bağlamını, içeriğini ve statüsünü tarif etmektir.
- Transkript ise, öğrencinin aldığı derslerin notlarına ve kredilerine ilişkin bir belgedir.
- Diploma eki, mezuniyet tanggalere ve diploma programı bilgisine ilişkin bilgileri içerirken, transkript öğrencinin eğitimi boyunca almış olduğu tüm derslerin notlarını ve kredilerini içerir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2661ms; student_affairs_orchestrator=2745ms; curriculum_agent=2630ms; academic_programs_orchestrator=2715ms
- **API Sureleri**: api_total=4535ms; dispatch=2778ms; final_llm=857ms; compose=912ms; telemetry=11ms
- **Sure**: 4543.5 ms
- **API Response Time**: 4488.9 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kayıt dondurma, önemli nedenlerin veya eğitim öğretimlerine katkıda bulunacak imkanların ortaya çıkması halinde ilgili yönetim kurulu kararı ile öğrenime ara vermelerine olanak tanıyan bir süreçtir. Kayıt yaptırmamak ise, akademik takvimde belirlenen süre içinde ders kaydını yapmamayı ifade eder. 
Her iki durumda da öğrencilik hakları etkilenir. Kayıt dondurma durumunda, öğrenim süresi uzayabilir. Kayıt yaptırmazsanız, o dönemde öğrenimine devam etme hakkı ortadan kalkar. Ayrıca, kayıt yaptırmayan öğrencilerin bir sonraki dönemde eğitimlerine devam edebilmeleri için tekrar kayıt yaptırmaları gerekli olabilecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_programları.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: yonerge_uzaktan_egitim_onlisans_lisans.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] UBYS
  - [x] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2875ms; student_affairs_orchestrator=2934ms
- **API Sureleri**: api_total=3032ms; dispatch=2954ms; compose=10ms; telemetry=10ms
- **Sure**: 3042.6 ms
- **API Response Time**: 2981.7 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Ders kaydı sürecini tamamlamak için, akademik takvimde belirtilen süre içinde öğrenci bilgi sistemi üzerinden ders kaydınızı yapınız. Ders seçimini tamamladığınızda, akademik danışmanınızla iletişime geçerek ders seçimini onaylatınız. 
Öğrenciler, her döneme başlarken akademik takvimde belirlenen süre içinde öğrenci bilgi sistemi üzerinden ders kaydını yapar. Akademik takvimde belirtilen süre içinde ders kaydını yapmayan öğrenciler o dönemde öğrenimlerine devam edemez.
Öğrencilerin öncelikle başarısız oldukları ve alamadıkları alt dönem derslerini alması gerekir. AKTS kredileri toplamı ise GANO’ya göre değişir: GANO’su 1,80-2,49 arası olan öğrenciler için
Danışman onayını sağlamak için öğrenci bilgi yönetim sistemi üzerinden mesaj gönderilebilir. Danışman onayını verificar etmek için öğrencinin şahsen gelmesi gerekmez, sistem üzerinden onaylama veya iade etme hakkını kullanabilir. 
Danışman onayından emin olunmalıdır, çünkü danışman onayı olmayan ders kayıtları geçersizdir ve bu durumda ders ve sınavlara katılamazsınız. 
Danışman onayı işlemi tamamlandıktan sonra, kayıtlanmış olduğunuz dersleri tek tek kontrol ediniz. Sizin danışman onayına göndermiş olduğunuz derslerden bir veya birkaçı danışmanınız tarafından listeden çıkartılmış olabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Ajan Sureleri**: registration_agent=2171ms; student_affairs_orchestrator=2219ms
- **API Sureleri**: api_total=2315ms; dispatch=2237ms; compose=5ms; telemetry=9ms
- **Sure**: 2332.1 ms
- **API Response Time**: 2262.3 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Sınav notunuza itiraz etmek için akademik takvimde belirtilen sınav not girişlerinin öğrenci otomasyon sistemine girilmesinin son gününden itibaren beş iş günü içerisinde ilgili birime (Bölüm Başkanlığına) dilekçe vererek itiraz edebilirsiniz. İtiraz üzerine sınav kağıdı incelenir ve işlem yazılı ve gerekçeli olarak gerçekleştirilir. Ayrıca, öğretim elemanı tarafından fark edilen maddi hataya ilişkin sınav not bildirim/not düzeltme formu notların ilanından sonra düzenlenebilir. İtiraz sonuçları, ilgili birim tarafından Öğrenci İşleri Daire Başkanlığına bildirilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 5/6
  - [x] ders
  - [x] staj
  - [x] GANO
  - [x] 2,00
  - [x] ilişik kesme
  - [ ] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=2703ms; student_affairs_orchestrator=2814ms; curriculum_agent=3517ms; academic_programs_orchestrator=3594ms
- **API Sureleri**: api_total=6006ms; dispatch=3645ms; final_llm=1134ms; compose=1168ms; telemetry=13ms
- **Sure**: 6020.5 ms
- **API Response Time**: 5953.6 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Mezuniyet için gerekli koşullar şunlardır: Kayıtlı olduğunuz öğretim programının ders, uygulama, staj gibi tüm gereklerini OMU Eğitim Öğretim ve Sınav Yönetmeliği hükümlerine göre başarıyla tamamlamanız, GANO'nuzun 2,00 veya daha yüksek olması. İlişik kesme süreci ise UBYS üzerinden "İlişik Kesme Talebinde Bulun" seçeneğinden veya şahsen başvurarak ilişik kesme formunu doldurup onaylattıktan sonra öğrenim gördüğünüz birime teslim ederek başladılabiliyor. 
Aşağıdaki hususlara dikkat etmelisiniz:
- Mezuniyet durumunuzu E-Devlet üzerinden kontrol etmeniz gerekiyor.
- Öğrenim ücretini ödemek koşuluyla, geçici kayıt hakkı veriliyor, ancak bu hak kesin kayıt anlamına gelmez. 
- Öğrencilerin kayıtları vekaleten yapılamıyor ve bestimmeli belgeleri imzalamaları zorunludur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: özel_öğrenci_yönergesi.pdf
- Belge: yonerge_uluslararasi_ogrenci_kabul.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=2759ms; student_affairs_orchestrator=2819ms
- **API Sureleri**: api_total=3922ms; dispatch=2850ms; compose=5ms; telemetry=10ms
- **Sure**: 3938.8 ms
- **API Response Time**: 3839.3 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Diplomunuzu kaybetmeniz durumunda, nüfus cüzdanınız ile birlikte Öğrenci İşleri Daire Başkanlığı diploma birimine müracaat edebilirsiniz. Kendiniz gelemiyor iseniz noter vekaleti vererek vekilinize aldırabilir veya kamu kurumunda çalışıyorsanız resmi yazı ile talep edildiği takdirde kurumunuza resmi yazı ile gönderilmektedir.

E-devlette mezuniyet bilgilerinizin görünmüyor olması konusunda ise belge parcaklarından direkt çözüm bulunmuyor. Bu konuda daha fazla bilgi için Öğrenci İşleri Daire Başkanlığına başvurmanız .

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [x] %40
  - [ ] %60
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=2391ms; student_affairs_orchestrator=2450ms; curriculum_agent=2680ms; academic_programs_orchestrator=2762ms
- **API Sureleri**: api_total=4506ms; dispatch=2800ms; final_llm=1568ms; compose=1617ms; telemetry=17ms
- **Sure**: 4532.0 ms
- **API Response Time**: 4435.4 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Uzaktan eğitim yoluyla alınan derslerin sınav ve başarı değerlendirmesi, yüz yüze derslerden farklı değildir. Koşullar elverdiği ölçüde tüm sınavların yüz yüze yapılması esastır. Uzaktan verilen dersler için dönem içi değerlendirme, başarıya etkisi, uzaktan eğitimde %40'tan fazla olamaz. Ayrıca, sınavlar çevrimiçi olarak da yapılabilir veya rapor sunma gibi yöntemler kullanabilir. 
- Sınavlar yüz yüze ve yazılı olarak yapılır.
- Uzaktan eğitim ön lisans, lisans tamamlama ve lisans öğrencilerinin dönem içi sınavlarının nasıl yapılacağına senato tarafından karar verilir.
- Uzaktan verilen derslerin başarı değerlendirmesi, örgün verilen derslerin başarı değerlendirmesi ile aynı hükümlere tabidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2158ms; student_affairs_orchestrator=2220ms
- **API Sureleri**: api_total=2353ms; dispatch=2266ms; compose=5ms; telemetry=9ms
- **Sure**: 2369.9 ms
- **API Response Time**: 2298.4 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Sınavda kopya çekilmesinin cezası ve disiplin süreci, Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve ilgili mevzuata göre belirlenir. Sınava girerken cep telefonu ile ilgilenen öğrenciye kopya muamelesi yapılır. Disiplin sürecine ilişkin hükümler 11.03.2023 tarihli resmi gazetede yayımlanan 2547 sayılı Yükseköğretim Kanunu'na göre düzenlenir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] ilişik kesme
  - [x] UBYS
  - [x] form
  - [x] birim
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2981ms; student_affairs_orchestrator=3065ms
- **API Sureleri**: api_total=3945ms; dispatch=3094ms; compose=4ms; telemetry=10ms
- **Sure**: 3957.9 ms
- **API Response Time**: 3895.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Kaydınızı sildirmek için iki seçenek bulunmaktadır. İlk olarak, UBYS üzerinden talepte bulunarak ilişik kesmeini başlatabilirsiniz. İkinci seçenek ise şahsen başvurup ilişik kesme formunu doldurarak, belirtilen merkezlerde onaylattıktan sonra öğrenim gördüğünüz birime teslim etmektir. Her iki durumda da kaydınızın silinmesiyle öğrencilik hakkınız sona erecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2539ms; student_affairs_orchestrator=2610ms
- **API Sureleri**: api_total=2721ms; dispatch=2635ms; compose=7ms; telemetry=13ms
- **Sure**: 2731.9 ms
- **API Response Time**: 2667.3 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Okulumu dondurup 1 yıl ara verdikten sonra dönüşte, akademik takvimde belirtilen sürelerde "Öğrenci Bilgi Sistemi" üzerinden ders kaydını yapabilirsiniz. Ders seçimini tamamladığınızda, akademik danışmanınızla iletişime geçerek ders seçimini onaylatmanız gerekir. Ayrıca, ders kaydını yaparken GANO'nuzu dikkate almak önemlidir. GANO'nuz 1,80-2,49 arası olan öğrenciler için

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: yaz_okulu_eğitim_öğretim.pdf
- Belge: öğrenci_konseyi_yönergesi.pdf
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] danışman
  - [x] bölüm
  - [x] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2039ms; student_affairs_orchestrator=2098ms; curriculum_agent=2225ms; academic_programs_orchestrator=2333ms
- **API Sureleri**: api_total=4658ms; dispatch=2393ms; final_llm=1008ms; compose=1035ms; telemetry=16ms
- **Sure**: 4678.5 ms
- **API Response Time**: 4588.3 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Ders notlarınız sistemde görünmüyorsa, danışmanınıza ulaşarak durumunuzu bildirebilirsiniz. Danışmanınıza ulaşılamazsa, bölüm başkanınıza ve gerekli durumlarda Dekan/Müdürünüze başvurabilirsiniz. Ayrıca oidb@omu.edu.tr adresine de soru veya sorunuzu e-posta yoluyla iletebilirsiniz. 
- Danışmanınıza durumunuzu bildirmelisiniz.
- Bölüm başkanınıza ve Dekan/Müdürünüze başvurabilirsiniz.
- oidb@omu.edu.tr adresine e-posta yoluyla iletebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: tütün_kullanımı_genelgesi.pdf
- Belge: döküman_kontrolü_ve_kayıt_yönetimi_prosedürü.pdf
- Belge: tıp_fakültesi_akademik_öğrenci_danışmanlığı_yönergesi.pdf
- Belge: eğitim_öğretim_perfomansını_değerlendirme_prosedürü.pdf
```
