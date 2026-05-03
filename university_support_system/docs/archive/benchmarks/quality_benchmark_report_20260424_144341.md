# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 14:43:41
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 96.0% |
| Anahtar Bilgi Kapsami | 55.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3413.9 ms |
| Medyan Sure | 1869.5 ms |
| Intent Analizi Aktif | 24/25 |
| Force LLM Sentez | 21/25 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=25, query_failures=0, agent_tasks=40, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 7152.2 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 3/3 | 9220.8 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 1/4 | 860.4 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 2/4 | 1461.4 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 1869.5 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 10105.4 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 2484.2 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 3/5 | 1287.0 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 4/5 | 2279.0 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 1118.0 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 1/4 | 1447.2 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 3/4 | 814.3 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 3643.8 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 3/4 | 8309.3 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 3/3 | 2191.9 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 1493.4 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 1/5 | 1521.0 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 1/4 | 836.6 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 3/6 | 1618.4 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 10199.6 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 3/5 | 8164.6 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 1315.2 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 1898.2 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 1208.2 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 0/3 | 2848.9 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'announcement'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=6212ms; student_affairs_orchestrator=6302ms
- **API Sureleri**: api_total=7149ms; dispatch=6329ms; compose=24ms; telemetry=14ms
- **Sure**: 7152.2 ms
- **API Response Time**: 7071.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, kayıt işlemlerinin tamamlanmasından sonra muafiyet başvurusunu yapmalıdır. Ancak, karar çıkana kadar derslere devam etmesi gerekmektedir.

Ilgili duyurular:
1. 2025-2026 Eğitim Öğretim Yılı Bahar Yarıyılı Yatay Geçiş Yedek sonuçları (2026-02-13)
 Kayıt hakkı kazanan adaylar, aşağıda yer alan kayıt duyurusunu dikkatlice inceleyerek belirtilen tarihlerde, kayıt için gerekli belgelerle birlikte şahsen başvurarak kayıtlarını yaptırabilirler. Eksik veya onaysız belge ile başvuran öğrencilerin ya da başvuru esnasındaki beyan...
 Detay: https://www.omu.edu.tr/tr/icerik/duyuru/2025-2026-egitim-ogretim-yili-bahar-yariyili-yatay-gecis-yedek-sonuclari
 Ek baglanti: Yedek Kayıt Duyurusu (Kayıt Tarihleri, Kayıt Yerleri ve Gerekli Belgeler) - https://oidb.omu.edu.tr/tr/haberler/2025-2026-eitim-retim-yl-bahar-yaryl-yatay-gei-yedek-sonular/Yedek%20Kay%C4%B1t%20Duyurusu%20(Kay%C4%B1t%20Tarihleri,%20Kay%C4%B1t%20Yerleri%20ve%20Gerekli%20Belgeler).pdf
 Ek baglanti: Yedekten Kayıt Hakkı Kazanan Öğrenci Listesi - https://oidb.omu.edu.tr/tr/haberler/2025-2026-eitim-retim-yl-bahar-yaryl-yatay-gei-yedek-sonular/Yedekten%20Kay%C4%B1t%20Hakk%C4%B1%20Kazanan%20%C3%96%C4%9Frenci%20Listesi.pdf
2. 2025 - 2026 Güz Dönemi Yatay Geçiş Başvuru Sonuçları
 2025 - 2026 Güz Dönemi Yatay Geçiş Başvuru Sonuçları aşağıdaki gibidir.
 Detay: https://eem-muhendislik.omu.edu.tr/tr/haberler/2025-2026-guz-donemi-yatay-gecis-basvuru-sonuclar
 Ek baglanti: Yatay Geciş Sonuçları.pdf - https://eem-muhendislik.omu.edu.tr/tr/haberler/2025-2026-guz-donemi-yatay-gecis-basvuru-sonuclar/YATAY_GEÇİŞ_0_İNGİLİZCE_1[1].pdf
3. 2025-2026 eğitim öğretim yılı bahar yarıyılı yatay geçiş sonuçları (2026-02-09)
 2025-2026 Eğitim Öğretim Yılı Bahar Yarıyılı Yatay Geçiş Sonuçları
 Detay: https://www.omu.edu.tr/tr/icerik/duyuru/2025-2026-egitim-ogretim-yili-bahar-yariyili-yatay-gecis-sonuclari

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim
... (725 karakter daha)
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
- **Ajan Sureleri**: internship_agent=774ms; student_affairs_orchestrator=875ms; curriculum_agent=7751ms; academic_programs_orchestrator=7827ms
- **API Sureleri**: api_total=9173ms; dispatch=7871ms; global_llm=649ms; compose=676ms; telemetry=32ms
- **Sure**: 9220.8 ms
- **API Response Time**: 9099.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Tek ders sınavına girebilmek için stajınızı tamamlamış olmanız gerekmez. Mezuniyetiniz için sadece o dersin kalmış olması ve müfredatınızda tanımlı bütün dersleri almış olmanız yeterlidir. Sınava girebilmek için bu koşulları sağlamalısınız. 
Sınavda başarılı sayılmak için en az CC notu almanız gerekir.

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
- **Ajan Sureleri**: graduation_agent=676ms; student_affairs_orchestrator=758ms
- **API Sureleri**: api_total=843ms; dispatch=777ms; compose=3ms; telemetry=8ms
- **Sure**: 860.4 ms
- **API Response Time**: 798.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli dersi alırsanız, devam zorunluluğu devam etmektedir. Başka bir seçmeli dersi alabilmek için danışmanın onayıyla, sonraki dönemde/yılda devam etmek kaydıyla, başka bir seçmeli dersi alabilirsiniz.

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
- **Key Facts**: 2/4
  - [x] transkript
  - [ ] dahil
  - [x] ortalama
  - [ ] tamamlamıştır
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: regulation_agent=1206ms; academic_programs_orchestrator=1311ms
- **API Sureleri**: api_total=1439ms; dispatch=1351ms; compose=3ms; telemetry=9ms
- **Sure**: 1461.4 ms
- **API Response Time**: 1375.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Pedagojik formasyon dersleri transkriptte yer alır. Öğrencinin mezuniyet ortalamasına etkileri vardır. Diplomada, pedagojik formasyon eğitimini tamamlamış olan öğrencilerin diplomalarında ilgili ifade yer alır, tamamlamayanların ise sadece transkriptinde aldığı dersler yer alacaktır.

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
- **Ajan Sureleri**: registration_agent=668ms; student_affairs_orchestrator=738ms; tuition_agent=6ms; finance_orchestrator=111ms; international_agent=761ms; academic_programs_orchestrator=865ms
- **API Sureleri**: api_total=1856ms; dispatch=909ms; global_llm=828ms; compose=836ms; telemetry=11ms
- **Sure**: 1869.5 ms
- **API Response Time**: 1790.5 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Öğrenim ücretinizi yatırmak için gereken bilgileri Öğrenci İşleri veya ilgili birimden öğrenebilirsiniz. İkamet izni için gereken belgeler konusunda da Öğrenci İşleri'ne başvurmanız önerilir. Öğrenim ücreti ödemeye ilişkin olarak finanzi bölümünden alınan bilgiye göre, yillik ucret 2.397,00 TL, donemlik ucret 1.198,50 TL'dir. Öğrenim ücreti ve ikamet izni işlemleriyle ilgili bilgi alabilmek için Öğrenci İşleri'ne başvurmanız gerekir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: tuition_agent=5ms; finance_orchestrator=55ms; regulation_agent=1260ms; academic_programs_orchestrator=1316ms; registration_agent=8296ms; student_affairs_orchestrator=8388ms
- **API Sureleri**: api_total=10092ms; dispatch=8449ms; global_llm=1069ms; compose=1100ms; telemetry=11ms
- **Sure**: 10105.4 ms
- **API Response Time**: 10041.8 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
ÇAP başvuru şartları arasında ana dal genel not ortalamasının 4,00 üzerinden 2,75'in altına düşmemesi ve ana dal not ortalamasına göre % 20 dentro bulunan öğrencilerin başvurularının değerlendirmesinde öncelik verilmesi yer alıyor. Harç borcunuzun ödenmesi için, öncesinde borç miktarınızı öğrenmeniz ve ödemenin ilgili birim tarafından nasıl yapıldığını öğrenmeniz gerek.

Aşağıdaki bilgiler dikkate alınmalı:
* Ana dal genel not ortalamasının 4,00 üzerinden 2,75'in altına düşmemesi
* Ana dal not ortalamasına göre % 20 dentro bulunan öğrencilerin başvurularının değerlendirmesinde öncelik verilmesi
* Bir defaya mahsus ana dal genel not ortalaması iki kez 4,00 üzerinden 2,75'in altına düşen öğrencinin de ikinci ana dal kayıt işlemlerinin iptal edilebileceği

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
- **Ajan Sureleri**: registration_agent=1408ms; student_affairs_orchestrator=1509ms; tuition_agent=8ms; finance_orchestrator=104ms
- **API Sureleri**: api_total=2439ms; dispatch=1553ms; global_llm=743ms; compose=768ms; telemetry=41ms
- **Sure**: 2484.2 ms
- **API Response Time**: 2341.8 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, akademik takvimde belirtilen süre içerisinde ders kaydını yapmanız gerekir. Ders kaydı yaparken, öncelikle başarısız olduğunuz ve alamadığınız alt dönem derslerini almanız önerilir. Ders kaydı yaparken, AKTS kredileri toplamı, genel akademik not ortalamınıza göre belirlenir. Danışman onay süreci için, özellikle ön koşullu veya ardışıklık gerektiren dersler için danışmanınıza başvurmanız gerekir. 
- GANO'su 1,80-2,49 arası olan öğrenciler için 6 AKTS,
- GANO'su 2,50-2,99 arası olan öğrenciler için 10 AKTS,
- GANO'su 3,00-3,49 arası olan öğrenciler için 12 AKTS 
ve GANO'su 3,50 ve üzerinde olan öğrenciler için ise 15 AKTS tutarı kadar artırılabilir.

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
- **Key Facts**: 3/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [ ] bildiri
  - [ ] harç
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1092ms; student_affairs_orchestrator=1151ms; tuition_agent=894ms; finance_orchestrator=958ms
- **API Sureleri**: api_total=1264ms; dispatch=1185ms; compose=3ms; telemetry=11ms
- **Sure**: 1287.0 ms
- **API Response Time**: 1217.0 ms
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
- **Ajan Sureleri**: international_agent=967ms; academic_programs_orchestrator=1025ms; registration_agent=841ms; student_affairs_orchestrator=904ms; tuition_agent=685ms; finance_orchestrator=773ms
- **API Sureleri**: api_total=2268ms; dispatch=1067ms; global_llm=1070ms; compose=1111ms; telemetry=27ms
- **Sure**: 2279.0 ms
- **API Response Time**: 2196.2 ms
- **Kaynak Sayisi**: 13

**Yanit:**
```
Program süresini 1 yıl aşmanız durumunda, ilave iki dönem ek süre hakkınız bulunmaktadır. Bu süre içinde öğrenimlerinizi tamamlayamayan sizlere, katkı payı/öğrenim ücreti ödenmesi gerekmektedir. Ek süre içinde %10 oranında katkı payı/öğrenim ücretini ödemeniz gerekecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM
- Finans: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
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
- **Departman**: ['student_affairs', 'announcement'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [x] tekrar
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=656ms; student_affairs_orchestrator=737ms
- **API Sureleri**: api_total=1092ms; dispatch=770ms; compose=24ms; telemetry=17ms
- **Sure**: 1118.0 ms
- **API Response Time**: 1002.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Bir dersten devamsızlıktan kalan öğrenci o dersin bütünleme sınavına giremez. Devamsızlıktan kalan bir dersi tekrar almak için, dersin yeni bir döneminin açıldığını beklemelisiniz. Devam koşulu yerine getirilmemiş tekrar derslerine devam etmek esastır.

Ilgili duyurular:
1. 📢 Girişimcilik ve Yenilikçilik Dersinin Derslikleri Hakkında
 Girişimcilik ve Yenilikçilik dersinin dersliklerini öğrenmek için görseli inceleyebilirsiniz.
 Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/girisimcilik-ve-yenilikcilik-dersinin-derslikleri-hakkinda
2. İngilizce II ve İleri İngilizce II Derslerinin Mazeret Sınavları Hakkında
 İngilizce II ve İleri İngilizce II derslerinden mazeret sınavına girecek olan öğrencilerimiz 13 Mayıs Salı günü Saat 09:00'da MF103'te sınava girebilirler.
 Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/ingilizce-ii-ve-ileri-ingilizce-dersleri-mazeret-sinavlari-hakkinda
3. TBFİZ124 Fizik II ve TBFİZ122 Fizik II Dersini Alan Öğrencilerin Dikkatine!
 Laboratuvardan devam almış fakat ders tekrarı olan öğrencilerin laboratuvar notunu belirlemek üzere, LABORATUVAR SINAVI YAPILACAKTIR. Sınavın duyurusu için tıklayınız.
 Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/duyuru-tbfiz124-fizik-ii-ve-tbfiz122-fizik-ii-dersini-alan-ogrencilerin-dikkatine
 Ek baglanti: DUYURU 2025 BAHAR - https://bil-muhendislik.omu.edu.tr/tr/haberler/duyuru-tbfiz124-fizik-ii-ve-tbfiz122-fizik-ii-dersini-alan-ogrencilerin-dikkatine/DUYURU_2025_BAHAR.pdf

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
- Duyuru kaydi: 📢 Girişimcilik ve Yenilikçilik Dersinin Derslikleri Hakkında (https
... (531 karakter daha)
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
- **Ajan Sureleri**: registration_agent=688ms; student_affairs_orchestrator=737ms; tuition_agent=4ms; finance_orchestrator=46ms
- **API Sureleri**: api_total=1438ms; dispatch=768ms; global_llm=596ms; compose=603ms; telemetry=12ms
- **Sure**: 1447.2 ms
- **API Response Time**: 1389.8 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Kayıt dondurma isteginiz durumunda, kayıt dondurma süresi eğitim sürenizden sayılır. Kayıt dondurmadan önce o dönem için katkı payı/öğrenim ücretini yatırmanız gerekmektedir.

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
  - [ ] başvuru yapabilir
  - [x] GANO
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=627ms; student_affairs_orchestrator=715ms
- **API Sureleri**: api_total=794ms; dispatch=734ms; compose=3ms; telemetry=8ms
- **Sure**: 814.3 ms
- **API Response Time**: 751.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Hazırlık sınıfındaysanız ve transkriptiniz yoksa da, Ek Madde-1 kapsamında merkezi yerleştirme puanı ile yatay geçiş başvurusu yapabilirsin. Bu başvurularda transkript olmadan da başvurabilirsin ve öğrencinin GANO'su değerlendirme aşamasında etkili değildir.

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
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: international_agent=1832ms; academic_programs_orchestrator=1922ms; registration_agent=1391ms; student_affairs_orchestrator=1456ms
- **API Sureleri**: api_total=3611ms; dispatch=2017ms; global_llm=985ms; compose=1061ms; telemetry=12ms
- **Sure**: 3643.8 ms
- **API Response Time**: 3548.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçiş ve kurumlar arası yatay geçiş arasındaki farklar, kontenjanlar ve başvuru şartları bakımından farklılıklar gösterir. Her iki tür yatay geçiş için de genel not ortalamasının 4 üzerinden en az 2,80 olması gerekir. Kurum içi yatay geçişte, programların aynı birimdeki ve diğer birimlerdeki kontenjanları dikkate alınır. Kurumlar arası yatay geçişte ise, başvuru yapılan üniversitenin taban puanları ve genel not ortalaması dikkate alınır. 
Aşağıdaki noktalarda da farklılıklar bulunur:
- Kurum içi yatay geçiş başvurularında öğrencinin disiplin cezası almamış olması ve eğitim kurumunda herhangi bir sorun olmaması gereklidir.
- Yatay geçiş başvuruları, üniversitenin akademik takviminde belirtilen süre içerisinde yapılır.
- Kurumlar arası yatay geçişte, aynı puan türündeki programlara geçiş için genel not ortalamasının ve merkezi yerleştirme puanının belirli oranları dikkate alınır.

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
- **Ajan Sureleri**: curriculum_agent=7696ms; academic_programs_orchestrator=7787ms
- **API Sureleri**: api_total=8300ms; dispatch=7807ms; compose=4ms; telemetry=10ms
- **Sure**: 8309.3 ms
- **API Response Time**: 8255.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark, mutlak değerlendirmede öğrencilerin sınavlardan aldıkları notların öngörülen ağırlıklara göre hesaba katılmasıyla belirlenen ham başarı notunun 4’lük not sistemindeki karşılığını ifade etmesidir. Bağıl değerlendirmede ise öğrencilerin birbirleriyle kıyaslanarak değerlendirilmesi söz konusudur. 

Hangi öğrenci sayısında hangisinin uygulanacağı konusunda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
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
- **Ajan Sureleri**: graduation_agent=1540ms; student_affairs_orchestrator=1625ms
- **API Sureleri**: api_total=2166ms; dispatch=1666ms; compose=8ms; telemetry=10ms
- **Sure**: 2191.9 ms
- **API Response Time**: 2112.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Diploma eki, öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek üzere verilir. Diploma eki, transkript (not çizelgesi) veya diploma yerine geçmez. Transkript, öğrenim süresince alınan derslerin ve notların ayrıntılı bir şekilde gösterildiği belgedir. Diploma eki ve transkript arasındaki temel fark, diploma ekinin öğrenimin genel yapısını ve elde edilen yeti ve becerilerin tanımı açısından daha geniş bir perspektif sunmasıdır. Dolayısıyla, diploma eki transkript yerine kullanılamaz. 

Diploma eki, özellikle yurt dışında eğitim veya iş fırsatları için daha okunabilir ve karşılaştırılabilir bir diploma sunar, akademik güzergahın ve yeti ve becerilerin nesnel bir değerlendirmesini sağlar.

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
- **Key Facts**: 3/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=787ms; student_affairs_orchestrator=888ms
- **API Sureleri**: api_total=1483ms; dispatch=913ms; compose=6ms; telemetry=9ms
- **Sure**: 1493.4 ms
- **API Response Time**: 1439.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Kayıt dondurma ve kayıt yaptırmama arasındaki fark, kayıtlı olunan dönemde öğrenimini tam zaman için durdurmak ile öğrenimine hiç kaydetmeden devam etmemektir. Kayıt dondurulan dönemler, süre hesabında dikkate alınmaz. Kayıt yaptırmayan öğrenciler ise o dönemde öğrenimine devam etme hakkını kaybetmektedir. Her iki durumda da öğrencilik hakları ve süreler farklılık göstermektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
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
- **Ajan Sureleri**: registration_agent=1222ms; student_affairs_orchestrator=1301ms
- **API Sureleri**: api_total=1510ms; dispatch=1358ms; compose=7ms; telemetry=9ms
- **Sure**: 1521.0 ms
- **API Response Time**: 1413.4 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kayıt işlemleri, akademik takvimde belirlenen süre içinde yapılır. Öğrenciler öncelikle başarısız oldukları ve alamadıkları alt dönem derslerini alırlar. GANO'su 1,80-2,49 arası olan öğrenciler için

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
- **Ajan Sureleri**: graduation_agent=657ms; student_affairs_orchestrator=728ms
- **API Sureleri**: api_total=819ms; dispatch=747ms; compose=2ms; telemetry=13ms
- **Sure**: 836.6 ms
- **API Response Time**: 770.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
İtiraz süresi 3 iş günüdür. İtiraz sonuçları notların yeniden düzenlenmesini içerebilir. İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz.

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
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/6
  - [x] ders
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [x] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=1015ms; student_affairs_orchestrator=1091ms
- **API Sureleri**: api_total=1606ms; dispatch=1112ms; compose=5ms; telemetry=10ms
- **Sure**: 1618.4 ms
- **API Response Time**: 1555.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Mezuniyet için öğrenim gördüğü eğitim-öğretim programında yer alan bütün şartları yerine getirerek mezuniyet hakkı kazanılır. Öğrencinin üniversite ile ilişiği, kaydını sildirmesi, yok’un onaylaması durumunda veya ders sayısını bire indirememesi halinde kesilir. Mezuniyet için gereken koşulların yerine getirilmesi veilişik kesme süreci kapsamında, öğrencinin kayıt hakkını kaybetmemesi için zamanında başvurması ve istenen belgeleri tamamlaması gerekmektedir. Kayıt yenileme ve ders kaydı işlemlerinin yapılmış olması da önemlidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
```

### Q20: Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] 2. nüsha
  - [x] diploma
  - [x] e-devlet
  - [ ] YÖKSİS
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=665ms; student_affairs_orchestrator=751ms; international_agent=8341ms; academic_programs_orchestrator=8396ms
- **API Sureleri**: api_total=10172ms; dispatch=8436ms; global_llm=1135ms; compose=1170ms; telemetry=12ms
- **Sure**: 10199.6 ms
- **API Response Time**: 10112.4 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Diplomanızı kaybederseniz, mahkeme kararı, diploma ücretini yatırdığını gösteren banka dekontu, kimlik fotokopisi ve dilekçe ile başvurduğunuz takdirde diploma yeniden düzenlenecektir. Mezuniyet bilgilerinizin e-devlette görünmemesi durumunda, Mezuniyetten sonra oluşabilecek sorunlar için ilgili bir hüküm bulunmamaktadır. 

Bununla ilgili olarak:
- Diploma Kayıp ilanı için yaygın gazetelerden birine başvuru yapılması gerekebilir.
- Mezuniyet bilgilerinin görünmemesi için ayrıca bir işlem yapma ihtiyacı duyulabilir, ancak bu konuda daha fazla bilgi almak için ilgili birimden yardım alınmalıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: tyb.pdf
- Belge: yurda_giriş_çıkış_belgesi.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
```

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs', 'academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [x] uzaktan
  - [ ] %20
  - [x] %80
  - [x] %40
  - [ ] %60
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=810ms; academic_programs_orchestrator=906ms; graduation_agent=6576ms; student_affairs_orchestrator=6643ms
- **API Sureleri**: api_total=8122ms; dispatch=6733ms; global_llm=778ms; compose=822ms; telemetry=16ms
- **Sure**: 8164.6 ms
- **API Response Time**: 8065.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Uzaktan eğitim yoluyla alınan derslerin sınav ve başarı değerlendirmesi, yüz yüze derslerden farklı değildir. Zorunlu haller dışında, tüm derslerin sınavları yüz yüze yapılır. Ancak, bazı durumlarda çevrimiçi sınav türünden hangisinin uygulanacağı ders ile ilgili olarak belirlenir. Uzaktan eğitimde dönem içi değerlendirme, başarılıya etkisi %40'tan fazla olamaz. 
- Uzaktan eğitim öğrencilerinin dönem içi sınavlarının nasıl yapılacağına senato tarafından karar verilir.
- Derslere devam durumu, öğretim elemanınca yapılan yoklamalarla tespit edilir.
- Derslerin teorik saatlerinin en az %70'ine, ders uygulamaları, atölye eğitim derslerinde ise en az %80 veya %90'ına devam etmek gerekir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
- Belge: uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=1139ms; student_affairs_orchestrator=1196ms
- **API Sureleri**: api_total=1288ms; dispatch=1214ms; compose=4ms; telemetry=10ms
- **Sure**: 1315.2 ms
- **API Response Time**: 1237.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınavda kopya çekilmesinin cezası disiplin suçu olarak kabul edilir. Disiplin süreci, 11.03.2023 tarihli resmi gazetede yayımlanan 2547 sayılı Yükseköğretim Kanunu hükümlerine göre işler. Buna göre, sınav görevlileri kopya çekme girişiminde bulunulan tespit eder ve gerekli işlemler yapılır. 
Sınav salonunda cep telefonu ile herhangi bir şekilde ilgilenen öğrenciye de kopya muamelesi yapılır.

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
- **Ajan Sureleri**: registration_agent=1069ms; student_affairs_orchestrator=1284ms
- **API Sureleri**: api_total=1887ms; dispatch=1313ms; compose=11ms; telemetry=65ms
- **Sure**: 1898.2 ms
- **API Response Time**: 1756.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Kaydınızı sildirmek istiyorsanız, yazılı isteğinizi universiteye iletmeniz gerekir. Yazılı isteğiniz üzerine kaydınız silinecektir. Ancak, ÖSYM tarafından yeniden yerleştirilmediğiniz sürece universiteye tekrar kayıt yaptıramazsınız. Ayrıca, kayıt silme işlemi aftermathsınız universite ile ilişkinizi keser.

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
- **Key Facts**: 1/4
  - [x] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=976ms; student_affairs_orchestrator=1075ms
- **API Sureleri**: api_total=1193ms; dispatch=1100ms; compose=11ms; telemetry=13ms
- **Sure**: 1208.2 ms
- **API Response Time**: 1123.2 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kayıt dondurma süresinin bitiminde, öğrenimine kaldığı yerden devam edersiniz. Ders seçimini yapmak için, öncelikle başarısız olduğunuz ve alamadığınız alt dönem derslerini seçmelisiniz. Akademik takvimde belirlenen süre içinde ders kaydınızı yapabilirsiniz. GANO'nuzu dikkate alarak, AKTS kredileri toplamı doğrultusunda ders seçebilirsiniz. Örneğin, GANO'nuz 1,80-2,49 arası ise 6 AKTS, 2,50-2,99 arası ise 10 AKTS, 3,00-3,49 arası ise 12 AKTS ve 3,50 ve üzerinde ise 15 AKTS tutarı kadar artırabilirsiniz. Ayrıca, muafiyet aldığınız derslerin AKTS'si kadar üst dönemlerden ders alabilirsiniz, ancak ön koşullu ya da sistematik olarak ardışıklık gerektiren dersler için danışman onayına ihtiyacınız vardır.

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
- **Key Facts**: 0/3
  - [ ] danışman
  - [ ] bölüm
  - [ ] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=2151ms; student_affairs_orchestrator=2210ms
- **API Sureleri**: api_total=2840ms; dispatch=2228ms; compose=3ms; telemetry=11ms
- **Sure**: 2848.9 ms
- **API Response Time**: 2802.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Söz konusu vanua ilişkin bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
