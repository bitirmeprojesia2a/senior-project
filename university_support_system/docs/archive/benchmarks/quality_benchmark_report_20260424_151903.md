# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 15:19:03
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 92.0% |
| Anahtar Bilgi Kapsami | 53.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 9389.9 ms |
| Medyan Sure | 8102.0 ms |
| Intent Analizi Aktif | 24/25 |
| Force LLM Sentez | 21/25 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=25, query_failures=0, agent_tasks=40, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 7440.1 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 2/3 | 15005.7 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 1/4 | 6503.9 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 3/4 | 23443.5 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | YANLIS (vt) | 1/3 | 9771.8 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 9755.3 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 7478.0 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 9103.8 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 5/5 | 14005.7 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 6193.0 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 1/4 | 7264.3 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 3/4 | 7003.2 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 1/5 | 11061.2 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 3/4 | 8102.0 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 2/3 | 10040.3 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 8462.5 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 1/5 | 7408.4 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 1/4 | 7476.7 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 3/6 | 11627.7 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 8273.6 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 2/5 | 10699.6 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 7222.5 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 7504.1 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 6166.2 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 1/3 | 7733.6 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=6669ms; student_affairs_orchestrator=6722ms
- **API Sureleri**: api_total=7476ms; dispatch=6745ms; compose=2ms; telemetry=9ms
- **Sure**: 7440.1 ms
- **API Response Time**: 7377.8 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu 26.01.2026 tarihinden sonra yapabilir. Karar çıkana kadar derslere devam etmesi gereken bir bilgi belge parcacinda yer almamaktadir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: internship_agent=12558ms; student_affairs_orchestrator=12985ms; curriculum_agent=9218ms; academic_programs_orchestrator=9308ms
- **API Sureleri**: api_total=14856ms; dispatch=13055ms; global_llm=670ms; compose=693ms; telemetry=12ms
- **Sure**: 15005.7 ms
- **API Response Time**: 14706.0 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Tek ders sınavına girebilmek için stajınızı tamamlamış olmanız gerekmez. Ancak sınavda başarılı sayılmak için minimum not olarak en az CB almanız gerekiyor. 

Sınavlarda başarılı sayılmak için, 
- ders notunun en az CB olması gerekiyor,
- bazı durumlarda not ortalamasının da belli seviyede olması gerekebiliyor. 
Bu durumlar departman tarafından belirlenir.

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
- **Key Facts**: 1/4
  - [ ] değiştirebilir
  - [ ] devam koşulu
  - [ ] yeni
  - [x] ders
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=6211ms; student_affairs_orchestrator=6358ms
- **API Sureleri**: api_total=6472ms; dispatch=6388ms; compose=3ms; telemetry=10ms
- **Sure**: 6503.9 ms
- **API Response Time**: 6415.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli dersi aldıysanız, sonraki dönemde/yılda devam etme koşuluyla, devam zorunluluğunuz devam eder.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yaz_okulu_eğitim_öğretim.pdf
- Belge: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf
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
- **Ajan Sureleri**: regulation_agent=23001ms; academic_programs_orchestrator=23289ms
- **API Sureleri**: api_total=23403ms; dispatch=23309ms; compose=4ms; telemetry=11ms
- **Sure**: 23443.5 ms
- **API Response Time**: 23342.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Pedagojik formasyon dersleri transkripte dahil ediliyor. Alınan pedagojik formasyon dersleri transkriptte yer alır ve mezuniyet ortalamasına dahil. Diplomada bu eğitimi tamamladığına dair ifade yer alması için derslerin hepsinin alınması zorunlu. Pedagojik formasyon eğitimi derslerini seçmeli ders olarak alan ancak tümünü tamamlamayan öğrencilerin diplomalarında bu eğitimi tamamladığına dair ifade yer almayacak, öğrencinin sadece transkriptinde aldığı dersler yer alacaktır.

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
- **Uretim Modu**: vt (beklenen: llm) - YANLIS
- **Key Facts**: 1/3
  - [x] ücret
  - [ ] ikamet
  - [ ] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: tuition_agent=8ms; finance_orchestrator=95ms; international_agent=9488ms; academic_programs_orchestrator=9604ms; registration_agent=9323ms; student_affairs_orchestrator=9436ms
- **API Sureleri**: api_total=9758ms; dispatch=9671ms; compose=2ms; telemetry=15ms
- **Sure**: 9771.8 ms
- **API Response Time**: 9704.8 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Ogrenim ucreti icin Turk ogrenci / Mühendislik Fakültesi bilgisi veritabaninda kayitli. Yillik ucret: 2.397,00 TL. Donemlik ucret: 1.198,50 TL.

(Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf)

Uretim Turu:
- VT

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: tuition_agent=6ms; finance_orchestrator=66ms; regulation_agent=7940ms; academic_programs_orchestrator=8014ms
- **API Sureleri**: api_total=9734ms; dispatch=8078ms; global_llm=796ms; compose=818ms; telemetry=17ms
- **Sure**: 9755.3 ms
- **API Response Time**: 9677.0 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
ÇAP başvuru şartları arasında ana dal not ortalamasının 4,00 üzerinden 2,75'in altına düşmemesi ve başvuru değerlendirilmesinde ana dal not ortalamasına öncelik verilmesi yer alır. Ayrıca, ana dal genel not ortalaması iki kez 2,75'in altına düşen öğrencinin ikinci ana dal ile ilişiği kesilir. Harç borcu bulunması durumunda, borcun ödenmesi gerekmektedir. Harç borcu ödeme yöntemi veya sürecine ilişkin bilgilerin nerede bulunabileceği konusu hakkında ise bilgi bulunmamaktadır.

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
- **Ajan Sureleri**: registration_agent=6403ms; student_affairs_orchestrator=6517ms; tuition_agent=20ms; finance_orchestrator=70ms
- **API Sureleri**: api_total=7458ms; dispatch=6552ms; global_llm=828ms; compose=841ms; telemetry=10ms
- **Sure**: 7478.0 ms
- **API Response Time**: 7414.8 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, akademik takvimde belirtilen süre içerisinde ders kaydını yapmalısınız. Ders kaydını, başarısız olduğunuz ve almadığınız alt dönem derslerini dikkate alarak yapmalısınız. Ardışıklık gerektiren dersler için danışman onayınız gerekir. Danışmanınızla irtibata geçerek, ders kaydını yapabilirsiniz. AKTS kredileri toplamınızı artırabilmek için GANO'nuzu dikkate alabilir ve buna göre 6, 10, 12 veya 15 AKTS artırabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonerge_yuzde_on_basari_degerlendirme.pdf
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
  - [ ] bildiri
  - [x] harç
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=8024ms; student_affairs_orchestrator=8105ms; tuition_agent=6751ms; finance_orchestrator=6856ms
- **API Sureleri**: api_total=9062ms; dispatch=8165ms; global_llm=782ms; compose=816ms; telemetry=12ms
- **Sure**: 9103.8 ms
- **API Response Time**: 9004.6 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Yatay geçiş yapmanız durumunda bursunuz kesilir. Yeni üniversitede harç ödemeniz gerekir. Bursunuzun devri veya kesilip kesilmeyeceği konusunda bilgiye ulaşmak için burs aldığınız kurumla iletişim kurmanız gerekmektedir. 
- Bursun devri hakkında bilgi almak için burs aldığınız kurumla iletişime geçmelisiniz.
- Yeni üniversitede öğrenim görürken harç ödemeniz gerekecektir. 
- İlgili işlemler için gerekli belgeler ve prosedürler ve Öğrenci İşleri Daire Başkanlığına başvurmanız gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
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
- **Ajan Sureleri**: international_agent=12602ms; academic_programs_orchestrator=12666ms; registration_agent=13046ms; student_affairs_orchestrator=13115ms; tuition_agent=10816ms; finance_orchestrator=10926ms
- **API Sureleri**: api_total=13977ms; dispatch=13164ms; global_llm=689ms; compose=737ms; telemetry=11ms
- **Sure**: 14005.7 ms
- **API Response Time**: 13926.6 ms
- **Kaynak Sayisi**: 13

**Yanit:**
```
Program sürenizi 1 yıl aştığınız için azami eğitim süresi sonunda mezun olamayan öğrenciler için tanınan ek süre hakkınız vardır. Bu süre içinde katkı payı ödemeniz gerekir. En fazla iki dönem ek süre verilir. fraekke

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
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
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
- **Ajan Sureleri**: graduation_agent=5834ms; student_affairs_orchestrator=5931ms
- **API Sureleri**: api_total=6176ms; dispatch=5989ms; compose=4ms; telemetry=7ms
- **Sure**: 6193.0 ms
- **API Response Time**: 6129.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Bu dersi, dönem/yıl sonu ve bütünleme sınavına girebilmek için zamanında ders kaydının yapılmış ve devam zorunluluğunun yerine getirilmiş olması gerekir. Dolayısıyla, devamsızlıktan kaldığınız bir dersi, sonraki dönemde ders kaydı yaptıktan sonra tekrar alabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: bağıl_değerlendirme_yönergesi.pdf
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
- **Ajan Sureleri**: registration_agent=6211ms; student_affairs_orchestrator=6325ms; tuition_agent=6ms; finance_orchestrator=105ms
- **API Sureleri**: api_total=7251ms; dispatch=6353ms; global_llm=813ms; compose=829ms; telemetry=13ms
- **Sure**: 7264.3 ms
- **API Response Time**: 7194.2 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Kayıt dondurmak istediğiniz dönemde harç ücretini ödemek zorunda değilsiniz. Ancak kayıt dondurduğunuz süre eğitim sürenizden sayılır. Eğitim süreniz sırasında katkı payı veya öğrenim ücreti ödemeniz gerekebilir. Detaylı bilgiler için öğrenci işleri birimine başvurabilirsiniz.
- Kayıt dondurma işlemi wahrendi eğitim süreniz hesaplanırken dikkate alınır.
- Dönemlik ödemeniz gereken ücretin belli bir kısmını ödemezsiniz ancak eğitim süreniz etkilenir.

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
- **Key Facts**: 3/4
  - [x] transkript
  - [x] Ek Madde
  - [x] başvuru yapabilir
  - [ ] GANO
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=6826ms; student_affairs_orchestrator=6883ms
- **API Sureleri**: api_total=6981ms; dispatch=6910ms; compose=3ms; telemetry=9ms
- **Sure**: 7003.2 ms
- **API Response Time**: 6933.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Hazırlık sınıfında okuyorsanız ve transkriptiniz yoksa da Ek Madde-1 ile başka bir üniversiteye yatay geçiş başvuru yapabilirsiniz. Ek Madde-1 kapsamında yapılan yatay geçiş başvurularında transkript olmadan da başvuru yapılabilir.

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
- **Key Facts**: 1/5
  - [x] kurum içi
  - [ ] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=9194ms; student_affairs_orchestrator=9259ms; international_agent=9238ms; academic_programs_orchestrator=9329ms
- **API Sureleri**: api_total=11041ms; dispatch=9398ms; global_llm=991ms; compose=1024ms; telemetry=10ms
- **Sure**: 11061.2 ms
- **API Response Time**: 10988.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçiş ve kurumlararası yatay geçiş arasındaki farklar, başvurulacak kurum ve şartlara göre değişmektedir. Kurum içi yatay geçiş, aynı üniversitede (Örneğin Ondokuz Mayis Universitesi) farklı bir diploma programına geçiş yapmak iken, kurumlararası yatay geçiş farklı bir üniversiteden aynı veya farklı bir diploma programına geçiş yapmak anlamına gelir. 
Her iki jenis yatay geçiş için de genel not ortalamasının en az 2,80 olmasıgerekmektedir. Disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez. 

Değerlendirme kriterleri olarak, öğrencinin kayıtlı olduğu programda bitirdiği dönemlere ait genel not ortalaması ve ilgili diploma programının kontenjanları ve taban puanları gibi faktörler değerlendirme kriterleri arasında yer alır. Kurumlararası yatay geçiş başvurularında not ortalamasının en az 2,80 olması gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
```

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] bağıl
  - [x] mutlak
  - [ ] 10
  - [x] öğrenci sayısı
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=7366ms; academic_programs_orchestrator=7471ms
- **API Sureleri**: api_total=8095ms; dispatch=7491ms; compose=4ms; telemetry=11ms
- **Sure**: 8102.0 ms
- **API Response Time**: 8050.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bağıl değerlendirme sistemi ve mutlak değerlendirme arasındaki fark, notların hesaplanmasında öğrencilerin performanslarına göre sıralanması ya da mutlak bir standartın kullanılmasıdır. Bağıl değerlendirme sistemi, öğrencilerin birbirleriyle karşılaştırılarak notlandırılmasını içerirken, mutlak değerlendirme sistemi belirli bir standarda göre notları belirler.

Hangi öğrenci sayısında hangi sistemi uygulanacağına ilişkin bilgi bulunmamaktadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
```

### Q15: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/3
  - [x] diploma eki
  - [x] transkript
  - [ ] yerine geçmez
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=8382ms; student_affairs_orchestrator=8461ms; international_agent=8353ms; academic_programs_orchestrator=8450ms
- **API Sureleri**: api_total=10027ms; dispatch=8534ms; global_llm=918ms; compose=944ms; telemetry=13ms
- **Sure**: 10040.3 ms
- **API Response Time**: 9975.8 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Diploma eki, sizin takip edip başarıyla tamamladığınız öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek üzere verilir. Transkript ise not çizelgesidir. Dolayısıyla, diploma eki transkript yerine kullanılamaz. 
- Diploma eki, yurtdışında daha okunabilir ve mukayese edilebilir bir diploma, akademik güzergahınızın ve yurtiçinde ve yurtdışında edindiğiniz yeti ve becerilerin tam bir tarifi, başarı ve yetilerinizi nesnel ve adil değerlendirmesi, geleceğe yönelik olarak yurtdışında iş ve eğitim imkanlarına daha rahat ulaşma olanağı, iş bulma olanaklarını artırma kazanımlarını elde etmeye yardımcı olur.
- Transkript belgelerinizi bölüm/program sekreterliklerine veya Öğrenci İşleri Daire Başkanlığına başvurarak alabilirsiniz.
- Diploma eki ise diploma ile birlikte verilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: avrupa_birliği_eğitim_ve_gençlik_programları_hayat_boyu_öğrenme_erasmus.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=7767ms; student_affairs_orchestrator=7881ms
- **API Sureleri**: api_total=8427ms; dispatch=7913ms; compose=6ms; telemetry=9ms
- **Sure**: 8462.5 ms
- **API Response Time**: 8389.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Kayıt dondurma ve kayıt yaptırmamak arasında önemli bir fark vardır. Kayıt dondurulan dönemler, süre hesabına dahil edilmez. Diğer bir ifadeyle, kayıt dondurulan sürelearnedeniyle educational öğretim süresi uzamaz. 

Kayıt yaptırmazsanız, akademik takvimde belirlenen süre içinde ders kaydını yapmayan öğrenciler, o dönemde öğrenimine devam etme hakkını kaybetmiş olurlar. 

Her iki durumda da, öğrencilik haklarınız etkilenebilir. Ancak, kayıt dondurma durumunda, öğrencilik statünüz korunurken, kayıt yaptırmazsanız öğrenimine devam etme hakkınız askıya alınabilir. 

Kayıt yaptırmazsanız, öğrenimine devam edebilirsiniz, ancak akademik takvimde belirlenen süre içinde ders kaydını yapmış olmanız gerekir. Ek olarak, kayıt yaptırmamanız halinde, merkezi yerleştirme puanı ile yatay geçiş başvurusu yapabilirsiniz, ancak bu durumda GANO değerlendirmesi yapılmaz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
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
- **Ajan Sureleri**: registration_agent=7227ms; student_affairs_orchestrator=7283ms
- **API Sureleri**: api_total=7393ms; dispatch=7303ms; compose=9ms; telemetry=17ms
- **Sure**: 7408.4 ms
- **API Response Time**: 7338.5 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
İlk kez üniversite kaydını yaptıran bir öğrenci olarak, önce akademik takvimde belirlenen süre içinde öğrenci bilgi sistemine girerek ders kaydını yapmak gerekir. Ders kaydı yapılırken, öncelikle başarısız olduğunuz ve almadığınız alt dönem derslerini seçmelisiniz. Daha sonra genel akademik not ortalamınıza (GANO) göre, bestimmüş olan AKTS kredilerini dikkate alarak ders kaydınızı yapabilirsiniz. Bu kapsamda, GANO'su 1,80-2,49 arası olan öğrenciler için

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
```

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [x] itiraz
  - [ ] beş iş günü
  - [ ] dilekçe
  - [ ] bölüm başkanlığı
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=7295ms; student_affairs_orchestrator=7375ms
- **API Sureleri**: api_total=7457ms; dispatch=7394ms; compose=4ms; telemetry=10ms
- **Sure**: 7476.7 ms
- **API Response Time**: 7414.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
İtiraz süresi 15 gündür. Sınav sonuçlarına itiraz, Ondokuz Mayıs Üniversitesi Ön Lisans ve Lisans Eğitim-Öğretim Yönetmeliğine uygun olarak yapılır. Yeniden inceleme için 3 iş günü içinde itiraz edilebilir. Öğretim elemanı tarafından fark edilen maddi hataya ilişkin sınav not bildirim/not düzeltme formu, notların düzeltilmesi için kullanılır. Başvuru süreci ve olası sonuçları hakkında daha detaylı bilgi için ilgili birim yöneticilerine başvurabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ders_yeterlilik_sınavı_uygulama_yönergesi.pdf
- Belge: yonerge_yuzde_on_basari_degerlendirme.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/6
  - [x] ders
  - [x] staj
  - [ ] GANO
  - [ ] 2,00
  - [x] ilişik kesme
  - [ ] diploma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=9141ms; student_affairs_orchestrator=9229ms; international_agent=9103ms; academic_programs_orchestrator=9202ms
- **API Sureleri**: api_total=11613ms; dispatch=9285ms; global_llm=1757ms; compose=1798ms; telemetry=32ms
- **Sure**: 11627.7 ms
- **API Response Time**: 11538.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Mezuniyet için gerekli koşulları tamamlamış olmakIsRequired. Mezuniyet için gerekli koşullar şunlardır: Öğrencinin yükseköğretim kurumları öğrenci disiplin yönetmeliği ve diğer ilgili mevzuat hükümlerine uygun davranması, ders sayısını bire indirebilmesi, kaydını sildirmeyen ve onaylanmayan durumlarda, yabancı dil öğretimi yapan programlarda başarılı olması. İlişik kesme süreci ise şunları içerir: Kaydını sildiren öğrencilerin, yok’un onaylaması durumunda, ders sayısını bire indiremeyenlerin, yabancı dil öğretimi yapan programlarda başarısız olanların üniversite ile ilişiğinin kesilmesi. Mezuniyet koşullarını tamamlamış olmak ve kayıt işlemlerinin tamamlanmış olması gerekir. Öğrencinin kayıtlandığı eğitim programlarının tüm genel ve özel koşullarını kabul etmiş sayılırlar. Kesin kayıtlar çevrim içi veya şahsen başvuru yoluyla yapılabilir. Ögrenim ücretini ödemiş olmak kaydının kesinleşmesi koşuludur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: özel_öğrenci_yönergesi.pdf
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=7531ms; student_affairs_orchestrator=7625ms
- **API Sureleri**: api_total=8245ms; dispatch=7687ms; compose=3ms; telemetry=10ms
- **Sure**: 8273.6 ms
- **API Response Time**: 8194.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Diplomanın kaybedilmesi durumunda ilgili okul veya kurumdan yeni bir diploma talep edilmesi gerekebilir. Mezuniyet bilgilerinin e-devlette görünmemesi durumunda, öğrenim gördüğü eğitim-öğretim programında yer alan bütün şartların yerine getirilip getirilmediğini kontrol etmek ve gerekirse ilgili okul veya üniversiteye başvurmak gerekir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=8968ms; student_affairs_orchestrator=9038ms; curriculum_agent=8980ms; academic_programs_orchestrator=9063ms
- **API Sureleri**: api_total=10678ms; dispatch=9093ms; global_llm=1005ms; compose=1038ms; telemetry=11ms
- **Sure**: 10699.6 ms
- **API Response Time**: 10627.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Uzaktan eğitim yoluyla alınan derslerin sınav ve başarı değerlendirmesi, yüz yüze derslerden farklı değildir. Sınavları, zorunlu haller dışında, yüz yüze yapılır. Derslerin dönem içi sınavlarının nasıl yapılacağına senato tarafından karar verilir. Koşullar elverdiği ölçüde tüm sınavların yüz yüze yapılması esastır. Uzaktan verilen dersler için dönem içi değerlendirme, başarıya etkisi %40'tan fazla olamaz. Bazı sınavlar çevrimiçi olarak da yapılır, ayrıca sunum, rapor gibi yöntemler de kullanılabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
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
- **Ajan Sureleri**: graduation_agent=7008ms; student_affairs_orchestrator=7087ms
- **API Sureleri**: api_total=7200ms; dispatch=7120ms; compose=5ms; telemetry=12ms
- **Sure**: 7222.5 ms
- **API Response Time**: 7151.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınavda kopya çekilmesinin cezası, disiplin suçu olarak belirlenmiştir. Disiplin süreci, 11.03.2023 tarihli resmi gazetede yayımlanan 2547 sayılı Yükseköğretim Kanunu hükümlerine göre işler. 
- Sınava giren öğrenci, sınav görevlisinden izin almadan sınav salonundan çıkana kadar cep telefonu ile ilgilenirse, kopya muamelesi görür.
Sınava giren öğrencilerin, 15 dakikadan daha kısa süre olmamak üzere yoklama işlemi tamamlanmadan ve sınav görevlisinden izin almadan sınav salonundan çıkması durumunda, kopya çekme girişiminde bulunmak bir disiplin suçudur.

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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=6698ms; student_affairs_orchestrator=6876ms
- **API Sureleri**: api_total=7468ms; dispatch=6925ms; compose=10ms; telemetry=25ms
- **Sure**: 7504.1 ms
- **API Response Time**: 7386.2 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Üniversiteyi bırakmak isteyen öğrencilerin kaydını sildirmesi gerekir. Kaydı silinen öğrencilerin üniversite ile ilişiği kesilir. Yazılı isteği üzerine kaydını sildiren öğrenci, ÖSYM tarafından yeniden yerleştirilmediği sürece üniversiteye tekrar kaydolamaz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
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
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=5891ms; student_affairs_orchestrator=5984ms
- **API Sureleri**: api_total=6115ms; dispatch=6011ms; compose=9ms; telemetry=17ms
- **Sure**: 6166.2 ms
- **API Response Time**: 6037.8 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kayıt dondurma süresinin bitiminde, ayrıldığınız dönemin/yılın başından başlamak koşuluyla öğrenimine kaldığı yerden devam edersiniz. Ders seçimini yaparken, öncelikle başarısız olunan dersleri almanızdır. Akademik takvimde belirtilen süre içinde ders kaydını yapmak ve danışman onayına göndermekle yükümlüsünüz. Danışman onayına gönderdiğiniz kaydın danışman tarafından kesin kayda dönüşmesini takip etmekle de yükümlüsünüz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/3
  - [x] danışman
  - [ ] bölüm
  - [ ] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=6911ms; student_affairs_orchestrator=7018ms
- **API Sureleri**: api_total=7712ms; dispatch=7059ms; compose=3ms; telemetry=11ms
- **Sure**: 7733.6 ms
- **API Response Time**: 7664.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sorunuzla ilgili bilgi bulunamadı. Belge parçalarında ders kayıtları, akademik takvim, danışman onayları ve muafiyet başvuruları gibi konulara dair bilgiler mevcut, ancak ders notlarının sisteme girilmemesi durumunda yapılacak işlemler hakkında konkret bir bilgi bulunmuyor.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
