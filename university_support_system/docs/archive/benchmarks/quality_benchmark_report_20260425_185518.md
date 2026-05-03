# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 18:55:18
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 96.0% |
| Anahtar Bilgi Kapsami | 68.0% |
| Temiz Kalite Orani | 96.0% |
| Ortalama Sure | 3497.1 ms |
| Medyan Sure | 3436.5 ms |
| Intent Analizi Aktif | 24/25 |
| Force LLM Sentez | 21/25 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=25, query_failures=0, agent_tasks=43, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 0/4 | 3827.5 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 2/3 | 3967.1 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 3/4 | 2410.3 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 4/4 | 2656.6 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 3287.4 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 4311.0 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 3436.5 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 2752.4 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 5/5 | 3032.6 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 2918.3 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 1/4 | 2508.2 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 4/4 | 2876.8 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 5264.7 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 4/4 | 4598.6 | uydurma_riski |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 3/3 | 4203.4 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 4202.8 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 2/5 | 3991.5 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 3/4 | 2592.7 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 3/6 | 4020.5 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 3521.8 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 2/5 | 3073.0 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 2790.7 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 4086.1 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 0/4 | 3035.5 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 2/3 | 4060.3 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 0/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [ ] derslere devam
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1682ms; student_affairs_orchestrator=1772ms; curriculum_agent=1617ms; academic_programs_orchestrator=1669ms
- **API Sureleri**: api_total=3815ms; dispatch=1802ms; final_llm=981ms; compose=1015ms; telemetry=16ms
- **Sure**: 3827.5 ms
- **API Response Time**: 3759.6 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, kayıt yaptırdıktan sonra muafiyet başvurusunu yapmalıdır. Muafiyet kararının alınması süreci, ders ekleme/çıkarma süresinin sonrasına sarkması durumunda, ders kayıt işlemi Öğrenci İşleri personellerince yerine getirilir. Karar çıkana kadar dönem derslerine devam edilmesi önemlidir. Birim Yönetim Kurulu’nun muafiyet talebini uygun görmesi ve muaf olunan derslerin sisteme işlenmesi sonrasında, danışman ile birlikte alacak olacağınız derslere kaydınız yapılır.

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
- **Key Facts**: 2/3
  - [x] staj
  - [x] tamamla
  - [ ] CC
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: internship_agent=1780ms; student_affairs_orchestrator=1860ms; curriculum_agent=1316ms; academic_programs_orchestrator=1374ms
- **API Sureleri**: api_total=3943ms; dispatch=1892ms; final_llm=1155ms; compose=1181ms; telemetry=9ms
- **Sure**: 3967.1 ms
- **API Response Time**: 3881.2 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Tek ders sınavına girebilmek için stajınızı tamamlamış olmanız gerekmez. Sınavda başarılı sayılmak için minimum notunuz 50 olmalıdır. 
- Stajınızı tamamlamadan bile tek ders sınavına girebilirisiniz.
- Tek ders sınavına başvurabilmeniz için o derse kayıt yaptırmış olmanız gerekmez.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
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
- **Key Facts**: 3/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [x] yeni
  - [x] ders
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=1286ms; student_affairs_orchestrator=1381ms
- **API Sureleri**: api_total=2397ms; dispatch=1401ms; final_llm=906ms; compose=928ms; telemetry=12ms
- **Sure**: 2410.3 ms
- **API Response Time**: 2346.3 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Başarısız olduğunuz seçmeli ders yerine yeni seçtiğiniz seçmeli derse devam şartınız doğacaktır. Fakat daha önce başarısız olduğunuz seçmeli dersi tekrar alıyorsanız ve devam koşulu zaten yerine getirilmişse, yeniden devam koşulu aranmaz. Ayrıca, derslere devam durumunda, teorik saatlerin en az % 70'ine devam etmeniz zorunludur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
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
- **LLM Kullanimi**: final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: regulation_agent=1573ms; academic_programs_orchestrator=1664ms
- **API Sureleri**: api_total=2644ms; dispatch=1683ms; final_llm=872ms; compose=891ms; telemetry=13ms
- **Sure**: 2656.6 ms
- **API Response Time**: 2597.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Pedagojik formasyon dersleri sizin transkriptinize dahil edilir ve mezuniyet ortalamasına dahil edilir. Diplomanın arkasına "Pedagojik formasyon eğitimini tamamlamıştır" ifadesi yazılır. Pedagojik formasyon eğitimi dersleri 40 AKTS'den oluşur ve üçüncü yarı yıldan itibaren alınmaya başlar. Alınan pedagojik formasyon dersleri transkriptte yer alır ve mezuniyet ortalamasına dahil edilir.

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
- **Ajan Sureleri**: international_agent=1945ms; academic_programs_orchestrator=2018ms; registration_agent=1947ms; student_affairs_orchestrator=2026ms; tuition_agent=7ms; finance_orchestrator=76ms
- **API Sureleri**: api_total=3273ms; dispatch=2075ms; final_llm=1087ms; compose=1122ms; telemetry=14ms
- **Sure**: 3287.4 ms
- **API Response Time**: 3215.6 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Öğrenim ücretini yatırmanız gereken yer konusunda bilgi bulunamadı, ancak finans birimi ile iletişim kurmanız öneriliyor. İkamet izni için gereken belgeler arasında sağlık raporu, not çizelgesi (transkript) ve dilekçe yer alıyor. Ayrıca, özel durumlarda ilgili belgeleri de sunmanız gerekebilir. Samsun Göç İdaresi Müdürlüğü'nden öğrenci ikamet izni almanız zorunludur. 

İlgili belgeler:
- Sağlık raporu
- Not çizelgesi (transkript)
- Dilekçe
- Özel durumlarda ilgili belgeler 

Öğrenci ikamet izni almanız için Samsun Göç İdaresi Müdürlüğü'ne başvuru yapmanız gerekiyor.

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
- **Departman**: ['finance', 'student_affairs', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=conditional
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: tuition_agent=6ms; finance_orchestrator=59ms; registration_agent=1723ms; student_affairs_orchestrator=1794ms; regulation_agent=1772ms; academic_programs_orchestrator=1825ms
- **API Sureleri**: api_total=4300ms; dispatch=1915ms; final_llm=1472ms; compose=1505ms; telemetry=21ms
- **Sure**: 4311.0 ms
- **API Response Time**: 4239.7 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
ÇAP programına başvurabilmek için önce harç borcunuzu ödemelisiniz. ÇAP başvuru şartları arasında ana dal diploma programının ilgili sınıfında bulunmanız, programında yer alan tüm dersleri almış ve başarmış olmanız, başvurusu sırasındaki ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal not ortalamasına göre en az ilk %20'sinde yer almanız gereklidir. 
Aşağıdaki koşullara dikkat etmeniz gerekmektedir:
- Ana dal not ortalamasına göre öncelik verilir.
- Harç borcunuz varsa, bunu öncelikle ödemeniz gerekir.
- ÇAP'a başvuruda bulunmadan önce harç borcunuzu ödemelisiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: VT
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: ön_lisans_ve_lisans.pdf
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
- **Ajan Sureleri**: registration_agent=1825ms; student_affairs_orchestrator=1923ms; tuition_agent=6ms; finance_orchestrator=56ms
- **API Sureleri**: api_total=3417ms; dispatch=1983ms; final_llm=1311ms; compose=1338ms; telemetry=22ms
- **Sure**: 3436.5 ms
- **API Response Time**: 3343.4 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, akademik takvimde belirtilen süre içinde ders kaydını yapmanız gerekiyor. Öncelikle başarısız olduğunuz ve alamadığınız alt dönem derslerini alın, ardından muafiyet aldığınız veya ardisiklik gerektiren dersler için danışman onayı gerekiyor. GANO'nuzu dikkate alarak AKTS kredileri toplamı kadar artırabilirsiniz. Danışmanınız, öğrenci bilgi yönetim sisteminden size toplu veya bireysel mesaj göndererek bilgilendirmede bulunabilir.

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
  - [ ] kesilme
  - [x] kurum
  - [x] bildiri
  - [x] harç
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1646ms; student_affairs_orchestrator=1743ms; tuition_agent=1249ms; finance_orchestrator=1345ms
- **API Sureleri**: api_total=2729ms; dispatch=1778ms; final_llm=847ms; compose=871ms; telemetry=18ms
- **Sure**: 2752.4 ms
- **API Response Time**: 2665.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bursunuz, yeni üniversiteye geçiş yaptığınız takdirde kesilebilir. Bursunuzun devam etmesi için üniversite değişikliğini bildirir dilekçe ile kayıt yaptırdığınız üniversiteye ait öğrenci belgesini burs aldığınız kuruma bildiriniz. 
Yatay geçiş yaptığınız yeni üniversitede harç ödemek zorunda kalıp kalmayacağınız konusunda bilgi almanız gerekecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: sık_sorulan_sorular.txt
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
- **Ajan Sureleri**: curriculum_agent=1899ms; academic_programs_orchestrator=1985ms; graduation_agent=1646ms; student_affairs_orchestrator=1702ms; tuition_agent=1536ms; finance_orchestrator=1604ms
- **API Sureleri**: api_total=3007ms; dispatch=2029ms; final_llm=858ms; compose=891ms; telemetry=15ms
- **Sure**: 3032.6 ms
- **API Response Time**: 2949.2 ms
- **Kaynak Sayisi**: 15

**Yanit:**
```
Evet, ek süre hakkınız vardır. Program süresini aşmanız durumunda ilgili dönem katkı payı ücreti ödenir. Azami eğitim süresi sonunda mezun olamayan öğrencilere, ilave iki dönem ek süre verilir. Bu süre içinde öğrenimlerini tamamlayamayan öğrencilerin programı ile ilişikleri kesilir. Ek süre içerisinde öğrenimlerine devam edecek öğrencilerin katkı payını ödemesi gerekmektedir.

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
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
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
- **LLM Kullanimi**: final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=1476ms; student_affairs_orchestrator=1535ms
- **API Sureleri**: api_total=2898ms; dispatch=1559ms; final_llm=1092ms; compose=1110ms; telemetry=16ms
- **Sure**: 2918.3 ms
- **API Response Time**: 2830.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Bunun yerine, devamsızlıktan kaldığınız dersi tekrar almaya mecbursunuz. Devamsızlıktan kaldığınız dersi tekrar almak için, devam koşulu yerine getirilmemiş tekrar derslerine devam etmek esastır. 
- Devam zorunluluğunun yerine getirilmesi gerekir.
- Bütünleme sınavı, dönem/yıl sonu sınavlarının ardından yapılır.
- Ders geçme sisteminin uygulandığı birimlerde bütünleme sınavı yapılır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Ajan Sureleri**: registration_agent=1353ms; student_affairs_orchestrator=1419ms; tuition_agent=6ms; finance_orchestrator=64ms
- **API Sureleri**: api_total=2486ms; dispatch=1452ms; final_llm=943ms; compose=956ms; telemetry=18ms
- **Sure**: 2508.2 ms
- **API Response Time**: 2429.0 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Kayıt dondurmak istediğiniz dönem için harç ücretini yatırmak zorunda değilsiniz. Kayıt dondurma süreniz eğitim süresinden sayılır mı sorusuna ilişkin bir bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **LLM Kullanimi**: final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=1144ms; student_affairs_orchestrator=1244ms
- **API Sureleri**: api_total=2860ms; dispatch=1263ms; final_llm=1518ms; compose=1535ms; telemetry=7ms
- **Sure**: 2876.8 ms
- **API Response Time**: 2814.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Hazırlık sınıfı okuyan ve Ek Madde-1 kapsamında merkezi yerleştirme puanı ile yatay geçiş başvurusu yapmak isteyen adaylar, transkriptleri olmadan da başvuru yapabilirler. Ek Madde-1 kapsamında yapılan yatay geçiş başvurularında öğrencinin GANO'su değerlendirme aşamasında etkili değildir. Dolayısıyla, transkriptiniz olmasa da Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilirsiniz. 
- Başvuru türüne bakılmaksızın bir dönemde en fazla 2 yatay geçiş başvurusu yapılabilir.
- Bir üniversiteye yatay geçiş yapıp geri dönmek mümkündür.
- Bir dönemde en fazla iki yatay geçiş başvurusu yapabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2154ms; student_affairs_orchestrator=2213ms; curriculum_agent=2159ms; academic_programs_orchestrator=2217ms
- **API Sureleri**: api_total=5247ms; dispatch=2258ms; final_llm=1885ms; compose=1922ms; telemetry=12ms
- **Sure**: 5264.7 ms
- **API Response Time**: 5192.6 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçişte, programa ve kontenjana bağlı olarak farklı değerlendirme kriterleri uygulanabilir. Örneğin, ikinci öğretimden sadece ikinci öğretim diploma programlarına yatay geçiş yapılabileceği gibi, uzaktan öğretim programlarından uzaktan öğretim programlarına da yatay geçiş yapılabilir. Kurumlar arası yatay geçişte de genel not ortalamasının en az 2,80 olması gerekir. Ayrıca, disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez. Her iki tür yatay geçiş başvurusunda da, programa ve kontenjana bağlı olarak farklı değerlendirme kriterleri uygulanabilir. 

Ayrıca, 
- Kurum içi yatay geçiş için, öğrencinin kayıtlı olduğu programda bitirdiği dönemlere ait genel not ortalamasının 4 üzerinden en az 2,80 olması gerekir.
- Özel yetenek sınavı ile öğrenci kabul edilen diploma programlarına kurum içi yatay geçiş için başvurunun değerlendirilmesinde genel not ortalamasının en az 2,80 olmasının yanı sıra, programa özgü başka şartlar da olabilir.
- Bir dönemde en fazla 2 yatay geçiş başvurusu yapılabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=2170ms; academic_programs_orchestrator=2236ms; graduation_agent=1679ms; student_affairs_orchestrator=1754ms
- **API Sureleri**: api_total=4577ms; dispatch=2299ms; final_llm=1199ms; compose=1255ms; telemetry=13ms
- **Sure**: 4598.6 ms
- **API Response Time**: 4511.1 ms
- **Kaynak Sayisi**: 9
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Bağıl değerlendirme sistemi, öğrencilerin başarı düzeyini, o dersi alan diğer öğrencilerin puanlarını dikkate alarak belirler. Mutlak değerlendirme sistemi ise sabit bir not ölçeğine dayanır. Öğrenci sayısı 10 ve altında ise mutlak değerlendirme sistemi, 11 ve üzeri öğrenci sayısı için ise bağıl değerlendirme sistemi uygulanır. 
- Mutlak değerlendirme, öğrencilerin başarmesinin objektif kriterlere dayandırılmasına dayanır.
- Bağıl değerlendirme sistemi, öğrencilerin birbirleriyle kıyaslanarak sıralandırılmasına dayanan bir değerlendirme sistemidir.
- Öğrenci sayısı 10 ve üzeri olduğunda, büyük sınıf mevcudiyetlerinde genellikle bağıl değerlendirme sistemi uygulanır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: bağıl_değerlendirme_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=2000ms; student_affairs_orchestrator=2073ms; curriculum_agent=2112ms; academic_programs_orchestrator=2161ms
- **API Sureleri**: api_total=4189ms; dispatch=2195ms; final_llm=1076ms; compose=1120ms; telemetry=40ms
- **Sure**: 4203.4 ms
- **API Response Time**: 4074.2 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Diploma eki, yükseköğretim diplomasına ek olarak verilen bir belgedir ve elde edilmiş yeti ve becerilerin ifade edildiği, akademik ve mesleki tanınmasını sağlamaya yönelik bir belgedir. Transkript ise not çizelgesidir. Diploma eki, transkript veya diploma yerine geçmez. 
Diploma eki, kişinin takip edip başarıyla tamamladığı öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek üzere verilir. 
Diploma eki ve transkript arasındaki fark, diploma ekinin mezun olan öğrencilere diploma ile birlikte verilen bir belge olup, öğretim ve değerlendirme sistemine ait bilgileri içerirken, transkript ise öğrencinin aldığı tüm derslerin notlarını ve kredilerini gösteren bir belgedir.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1998ms; student_affairs_orchestrator=2079ms; curriculum_agent=1936ms; academic_programs_orchestrator=2041ms
- **API Sureleri**: api_total=4175ms; dispatch=2123ms; final_llm=1069ms; compose=1107ms; telemetry=16ms
- **Sure**: 4202.8 ms
- **API Response Time**: 4102.8 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Kayıt dondurma ve kayıt yaptırmama arasında temel fark, kayıt dondurma durumunda süre hesabında dikkate almama durumudur. Kayıt dondurulan dönemler, eğitim-öğretim süresine dahil edilmez. Öte yandan, kayıt yaptırmadığınız durumlarda, o dönemde öğreniminize devam etmiyorsunuz demektir. Her iki durumda da öğrencilik haklarınız etkilenir. 
- Kayıt dondurma, önemli mazeretler veya eğitim-öğretime katkıda bulunacak imkanların ortaya çıkması halinde mümkün olur ve ilgili yönetim kurulu kararı ile gerçekleşir.
- Kayıt yaptırmazsanız, o dönem öğrenim görmediğiniz için öğrencilik haklarınızı tam olarak kullanamıyorsunuz.
- Kayıt dondurulan dönem/dönemler, süre hesabında dikkate alınmaz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: yonerge_uzaktan_egitim_onlisans_lisans.pdf
- Belge: ön_lisans_ve_lisans_programları.pdf
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [ ] UBYS
  - [ ] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2281ms; student_affairs_orchestrator=2335ms
- **API Sureleri**: api_total=3980ms; dispatch=2358ms; final_llm=1511ms; compose=1540ms; telemetry=14ms
- **Sure**: 3991.5 ms
- **API Response Time**: 3922.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Ders kaydını yapmak için öğrenci bilgi sistemine girerek ders kaydınızı yaparsınız. Öncelikle başarısız olduğunuz ve alamadığınız alt dönem derslerini alırsınız. GANO'nuzu dikkate alarak AKTS tutarınızı belirleyebilirsiniz. Ayrıca muafiyet aldığınız derslerin AKTS'si kadar üst dönemlerden ders alabilirsiniz, ancak ön koşullu ya da sistematik olarak ardışıklık gerektiren dersler için danışman onayı gerekir. Ders kaydınızı yaptıktan sonra, danışman onayına gönderir ve onayının kesin kayda dönüşmesini takip edersiniz. Danışman tarafından iade edilen ders kayıt teklifini yeniden düzenleyerek danışmanınıza onaylatırsınız. 
- Danışmanınıza ulaşamazsanız, bölüm başkanına veya Dekan/Müdürüne durumu bildirilebilir.
- Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine ilgili odeme kanali ile iletebilirsiniz.
- Danışman onayını vermek için öğrencinin şahsen gelmesi zorunlu değildir, öğrenci bilgi yönetim sistemi üzerinden internet ortamında ders kaydını yaptığı takdirde danışman onayına sistem üzerinden gönderebilir.

(Not: Bu cevaptaki bazi bilgiler kaynaklarda dogrudan teyit edilemedi; ilgili birimden dogrulama yapmaniz onerilir.)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] itiraz
  - [x] beş iş günü
  - [x] dilekçe
  - [ ] bölüm başkanlığı
- **LLM Kullanimi**: final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1409ms; student_affairs_orchestrator=1473ms
- **API Sureleri**: api_total=2577ms; dispatch=1495ms; final_llm=960ms; compose=985ms; telemetry=18ms
- **Sure**: 2592.7 ms
- **API Response Time**: 2503.0 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Sınav sonuçlarına karşı itiraz edebilirsiniz. İtiraz sürecinde, akademik takvimde belirtilen sınav not girişlerinin öğrenci otomasyon sistemine girilmesinin son gününden itibaren 5 iş günü içerisinde ilgili birime dilekçe vererek itiraz edebilirsiniz. 
İtiraz üzerine sınav kağıdınız incelenir ve yazılı ve gerekçeli olarak gerçekleştirilir. Ayrıca, öğretim elemanı tarafından fark edilen maddi hataya ilişkin sınav not bildirim/not düzeltme formu notların ilanından sonra düzenlenebilir. 
İtiraz sonucunun ortaya çıkması için 3 iş günü beklemeniz gerekmektedir.

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
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/6
  - [ ] ders
  - [ ] staj
  - [x] GANO
  - [x] 2,00
  - [x] ilişik kesme
  - [ ] diploma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=1764ms; student_affairs_orchestrator=1872ms
- **API Sureleri**: api_total=4005ms; dispatch=1903ms; final_llm=1173ms; compose=1190ms; telemetry=16ms
- **Sure**: 4020.5 ms
- **API Response Time**: 3914.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Mezuniyet için gerekli koşulları sağlamak ve ilişik kesme sürecini başlatabilmek için öncelikle mezun olabilme koşullarını sağlamalısınız: öğretim programının tüm gereklerini başarıyla tamamlamanız ve GANO'nuzun 2,00 veya daha yüksek olması gerekmektedir. İlişik kesme sürecini başlatmak için UBYS üzerinden "İlişik Kesme Talebinde Bulun" seçeneğinden İlişik Kesme Sürecini başlatabilir veya şahsen başvurarak ilişik kesme formunu doldurup, form üzerinde belirtilen merkezlerde onaylattıktan sonra öğrenim gördüğünüz birime teslim edebilirsiniz. Mezuniyet durumunuzun E-Devlet üzerinden kontrol edilmesini sağlamak önemlidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=1674ms; student_affairs_orchestrator=1750ms
- **API Sureleri**: api_total=3510ms; dispatch=1774ms; final_llm=827ms; compose=842ms; telemetry=19ms
- **Sure**: 3521.8 ms
- **API Response Time**: 3449.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Diplomanızı kaybetmeniz durumunda, nüfus cüzdanınız ile birlikte ilgili birim diploma birimine müracaat etmeniz halinde diplomanızı alabilirsiniz. Kendiniz gelemiyor iseniz noter vekaleti vererek vekilinize aldırabilir veya kamu kurumunda çalışıyorsanız resmi yazı ile talep edildiği takdirde kurumunuza resmi yazı ile gönderilmektedir. E-devlette mezuniyet bilgilerinizi görülememesi için ise elimizdeki kaynaklarda net bilgi bulunamadı.

(Not: Bu cevaptaki bazi bilgiler kaynaklarda dogrudan teyit edilemedi; ilgili birimden dogrulama yapmaniz onerilir.)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
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
- **Ajan Sureleri**: graduation_agent=1325ms; student_affairs_orchestrator=1394ms; curriculum_agent=1461ms; academic_programs_orchestrator=1518ms
- **API Sureleri**: api_total=3060ms; dispatch=1590ms; final_llm=1371ms; compose=1399ms; telemetry=14ms
- **Sure**: 3073.0 ms
- **API Response Time**: 3012.3 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Uzaktan eğitim yoluyla alınan derslerin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı değildir. Koşullar elverdiği ölçüde tüm sınavların yüz yüze yapılması esastır. Uzaktan eğitim öğrencilerinin dönem içi sınavlarının nasıl yapılacağına senato tarafından karar verilir. 
Ayrıca, 
- Uzaktan verilen dersler için dönem içi değerlendirme, başarıya etkisi, uzaktan eğitimde %40'tan fazla olamaz.
- Kismi uzaktan olan derslerin sınavları çevrimiçi olarak da yapılabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_egitim_onlisans_lisans.pdf
- Belge: lisansüstü_eğitim_ve.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1484ms; student_affairs_orchestrator=1541ms
- **API Sureleri**: api_total=2777ms; dispatch=1560ms; final_llm=1103ms; compose=1128ms; telemetry=17ms
- **Sure**: 2790.7 ms
- **API Response Time**: 2706.9 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Sınavda kopya çekilmesinin cezası, Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre belirlenir. Cep telefonu ile sınav sırasında ilgilenen öğrenciye kopya muamelesi yapılır. Disiplin suçlarına ilişkin hükümler 2547 sayılı Yükseköğretim Kanunu'na göre düzenlenir. Universidaden ilişiğin kesilmesi de dahil olmak üzere çeşitli yaptırımlar uygulanabilir.
- Sınavlarda kopya vermek ve çekme girişiminde bulunmak da bir disiplin suçudur.
- Sınava giren öğrencilerin, sınav görevlileri tarafından yapılan yoklama işleminden sonra ve sınav salonundan çıkana kadar cep telefonu kullanmaları veya herhangi bir şekilde ilgilenmeleri yasaklanmıştır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1660ms; student_affairs_orchestrator=1725ms
- **API Sureleri**: api_total=4070ms; dispatch=1777ms; final_llm=1437ms; compose=1461ms; telemetry=14ms
- **Sure**: 4086.1 ms
- **API Response Time**: 4005.3 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Üniversiteden ayrılma talebinizi UBYS üzerinden "İlişik Kesme Talebinde Bulun" seçeneğinden başlatabilirsiniz. Ayrıca şahsen başvurarak ilişik kesme formunu doldurup, belirtilen merkezlerde onaylattıktan sonra öğrenim gördüğünüz birime teslim edebilirsiniz. İlişik kesme sürecinin tamamlanması mezun olunduğu anlamına gelmez, mezuniyet ve diploma basım işlemlerinin başlatılması için yapılmaktadır. Mezuniyet durumunuzu E-Devlet üzerinden kontrol etmeniz gerekmektedir. Kaydınızın silinmesiyle birlikte öğrencilik hakkınız sona erecektir. 

Ayrıca dikkat etmeniz gereken hususlar arasında;
- İlişik kesme talebinde bulunma
- İlişik kesme formunu doldurup onaylattırma
- Mezuniyet durumunuzu E-Devlet üzerinden kontrol etme bulunmaktadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
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
- **LLM Kullanimi**: final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1569ms; student_affairs_orchestrator=1647ms
- **API Sureleri**: api_total=3025ms; dispatch=1671ms; final_llm=1267ms; compose=1281ms; telemetry=12ms
- **Sure**: 3035.5 ms
- **API Response Time**: 2969.2 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Öğrenci bilgi sistemi üzerinden akademik takvimde belirtilen sürelerde ders kaydını yapabilir ve ders seçimini tamamladığında akademik danışmanıyla iletişime geçerek ders seçimini onaylatmalıdır. Ayrıca, başarısız olduğu ve alamadığı alt dönem derslerini öncelikle seçmelisiniz. AKTS kredileri toplamı, genel not ortalamınıza göre artırılabilir. Öğrenimine kaldığı yerden devam edeceksiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: öğrenci_konseyi_yönergesi.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/3
  - [x] danışman
  - [ ] bölüm
  - [x] oidb@omu.edu.tr
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1790ms; student_affairs_orchestrator=1846ms
- **API Sureleri**: api_total=4046ms; dispatch=1865ms; final_llm=1033ms; compose=1043ms; telemetry=25ms
- **Sure**: 4060.3 ms
- **API Response Time**: 3978.0 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Ders notlarınız sisteme girilmemişse, durumunuzu Öğrenci İşleri Daire Başkanlığına başvurarak bildirebilirsiniz. Ayrıca, danışmanınıza veya ilgili birime ulaşabilirsiniz. Birim yöneticilerine veya teknik destek ekibine ulaşamamanız durumunda, oidb@omu.edu.tr adresine e-posta yoluyla sorunuzu iletebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
