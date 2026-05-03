# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 13:40:36
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 76.2% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 9228.8 ms |
| Medyan Sure | 3747.4 ms |
| Intent Analizi Aktif | 4/5 |
| Force LLM Sentez | 4/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=5, query_failures=0, agent_tasks=8, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 2/4 | 28102.6 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 2613.1 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 3747.4 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 3147.4 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 3/3 | 8533.4 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] üç hafta
  - [x] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1279ms; student_affairs_orchestrator=1443ms; curriculum_agent=20244ms; academic_programs_orchestrator=23840ms
- **API Sureleri**: api_total=28077ms; dispatch=24089ms; final_llm=1121ms; compose=1214ms; telemetry=1047ms
- **Sure**: 28102.6 ms
- **API Response Time**: 26890.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, daha önce aldığı ve başarılı olduğu dersler için Dekanlığa/Müdürlüğe muafiyet dilekçesi vermelidir. Muafiyet başvurunun sonuçlanıncaya kadar bu derse kayıt yaptırıp devam etmelidir. Birim Yönetim Kurulu’nun muafiyet talebini uygun görmesi ve muaf olunan derslerin sisteme işlenmesi sonrasında, danışman ile birlikte alacak olduğu derslere kaydı yapılır. 
- Muafiyet başvurunun sonuçlanıncaya kadar derslere devam etmeniz önem arz etmektedir.
- Daha önce alınan ve başarılı olunan derslerden muafiyet başvurusu yapılabilir.
-Muafiyet kararı alınması süreci Akademik takvimde belirtilen ders ekleme/çıkarma süresinin sonrasına sarkması durumunda, ders kayıt işlemi Öğrenci İşleri personellerince yerine getirilir.

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
- Belge: bilgisayar_derslerinin_muafiyeti_sınav_yönergesi.pdf
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
- **Ajan Sureleri**: registration_agent=1305ms; student_affairs_orchestrator=1415ms; tuition_agent=65ms; finance_orchestrator=903ms
- **API Sureleri**: api_total=2602ms; dispatch=1466ms; final_llm=1038ms; compose=1058ms; telemetry=11ms
- **Sure**: 2613.1 ms
- **API Response Time**: 2540.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, akademik takvimde belirlenen süre içinde ders kaydını yapmanız gerekir. Ders kaydında müfredat durum kontrolü, akademik takvimde belirtilen süre içinde kaydın tamamlanması ve danışman onayı önemlidir. Danışman onay sürecinde, danışmanınız tarafından listeden çıkartılmış dersler olabilir, bu nedenle kaydettiğiniz dersleri tek tek kontrol etmeniz önerilir. Ayrıca, her kayıt dönemi başında alınacak dersleri müfredatınızla karşılaştırmanız ve başarılı olduğunuz dersleri transkriptinize ulaşarak kontrol etmeniz gerekmektedir. 
- Müfredat durum kontrolü yapınız.
- Akademik takvimde belirtilen süre içinde kaydınızı tamamlayınız.
- Danışman onay sürecinde tüm derslerinizi kontrol ediniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [ ] UBYS
  - [x] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2041ms; student_affairs_orchestrator=2099ms
- **API Sureleri**: api_total=3737ms; dispatch=2121ms; final_llm=1492ms; compose=1532ms; telemetry=11ms
- **Sure**: 3747.4 ms
- **API Response Time**: 3664.6 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Ders Kaydı ve Danışman Onayları İle İlgili Süreci
==============================================

Selamlıyorum, sorunuzun cevapını vermeni istesem de, sürecinizi adım adım anlatabilirim. İlgilendiğiniz konuyla ilgili olarak adım adım süreçleri sizin için özetlenecektir.

İlk olarak, akademik takvimde belirtilen sürelerde ders kaydınızı yapmanız necesario durumudur. Ders seçimini tamamladığınızda akademik danışmanınızla iletişime geçerek ders seçimini onaylatmanız gerekecek. Akademik takvimde belirtilen sürelerde ders kaydını yapmayan öğrenciler öğrenimlerine devam edemezler.

Ders kaydı yaparken, öncelikle başarısız olduğunuz ve alamadığınız alt dönem derslerini alırsınız. Ayrıca, genel akademik not ortalamız (GANO) değerimiz göre ek ders alabilirsiniz.

Danışman onayını almaya gerek varsa, sistem üzerinden gönderebilirsiniz, yoksa akademik takvimde belirtilen sürede danışman onayını yaptırabilirsiniz. Danışman onay işleminden sonra kayıtlanmış olduğunuz dersleri kontrol edip transkriptinizi müfredatınızla karşılaştırmanız gerekecek.

Bu bilgiler ışığında sürecinizi özetlenebilir:

1. Akademik takvimde belirtilen sürelerde ders kaydınızı yapın.
2. Ders seçimini tamamladıktan sonra akademik danışmanınızla iletişime geçin.
3. Ders kaydı yaparken, öncelikle başarısız olduğunuz ve alamadığınız alt dönem derslerini alın.
4. Danışman onayında sistem üzerinden gönderebilirsiniz, yoksa akademik takvimde belirtilen sürede danışman onayını yaptırabilirsiniz.
5. Danışman onay işleminden sonra kayıtlanmış olduğunuz dersleri kontrol edip transkriptinizi müfredatınızla karşılaştırın.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1320ms; student_affairs_orchestrator=1384ms
- **API Sureleri**: api_total=3124ms; dispatch=1414ms; final_llm=879ms; compose=894ms; telemetry=11ms
- **Sure**: 3147.4 ms
- **API Response Time**: 3063.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Üniversiteden ayrılmak istiyorsanız, tüm işlemleri ve dikkat etmen gereken hususları siz için özetledik. 

Üniversiteden ayrılmak için ilk adım, ilgili kesme süresini başlatmaktır. Bunu UBYS üzerinden "İlişik Kesme Talebinde Bulun" seçeneğinden veya şahsen başvurarak ilişik kesme formunu doldurup onaylatarak öğrenim gördüğünüz birime teslim edebilirsiniz. 

Mezuniyet durumunuzu E-Devlet üzerinden kontrol etmeniz gerekir.

Bunları unutmayın:
- Kaydınızın silinmesiyle birlikte öğrencilik hakkınız sona erecek
- Üniversitesi ile iliğiniz kesilecek
- İlişik kesme formunu onaylatmanız gerekiyor

Eğer kaydınızı sildirmek için UBYS üzerinden talepte bulunarak ilişik kesme süreci başlatabilir ve ilişiğinizin kesilmesini sağlayabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1742ms; student_affairs_orchestrator=1839ms
- **API Sureleri**: api_total=8523ms; dispatch=1884ms; final_llm=816ms; compose=829ms; telemetry=9ms
- **Sure**: 8533.4 ms
- **API Response Time**: 8476.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Hocamın notlarınızı sisteme girmesini engelleyen bir durum var gibi gözüküyor. Bu durumda, önce hocanızla iletişime geçip durumunuzu bildirmelisiniz. Eğer hocanızı bulamazsanız, bölüm başkanınıza veya akademik danışmanınıza başvurabilirsiniz. Bu adımdan sonra, öğrenci işleri daire başkanlığına oidb@omu.edu.tr adresine e-posta göndererek sorununuzu bildirebilirsiniz, ardından ise daha detaylı bir işlem beklemem gerekir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
