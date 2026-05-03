# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 02:44:39
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 61.9% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 12010.6 ms |
| Medyan Sure | 11172.0 ms |
| Intent Analizi Aktif | 5/5 |
| Force LLM Sentez | 5/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=5, query_failures=0, agent_tasks=8, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 2/4 | 16773.0 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 9424.1 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 11172.0 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 11565.8 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 0/3 | 11118.0 | - |

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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=7998ms; student_affairs_orchestrator=8144ms; curriculum_agent=12029ms; academic_programs_orchestrator=12653ms
- **API Sureleri**: api_total=16763ms; dispatch=12790ms; final_llm=2404ms; compose=2444ms; telemetry=9ms
- **Sure**: 16773.0 ms
- **API Response Time**: 16663.8 ms
- **Kaynak Sayisi**: 11

**Yanit:**
```
Muafiyet başvurunuzu Dekanlığa/Müdürlüğe dilekçe vererek yapmalısınız. Muafiyet kararının alınması süreci ders ekleme/çıkarma süresinin sonrasına sarkması durumunda, ders kayıt işlemi Öğrenci İşleri personellerince yerine getirilir. Muafiyet başvurusu sonuçlanıncaya kadar, bu derse kayıt yaptırıp devam etmeniz önemlidir. Birim Yönetim Kurulu’nun muafiyet talebini uygun görmesi ve muaf olunan derslerin sisteme işlenmesi sonrasında, danışman ile birlikte alacak olduğunuz derslere kaydınızı yaptırabilirsiniz. 
- Daha önce aldığınız ve başarılı olduğunuz derslerden muaf olabileceksiniz.
- Muafiyet talebi ilgili yönetim kurulu tarafından karara bağlanıncaya kadar derslere devam etmelisiniz.
- Muaf olunan dersler için size ücret iadesi yapılmaz.

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
- **Ajan Sureleri**: registration_agent=7880ms; student_affairs_orchestrator=7978ms; tuition_agent=18ms; finance_orchestrator=130ms
- **API Sureleri**: api_total=9383ms; dispatch=8067ms; final_llm=1208ms; compose=1230ms; telemetry=9ms
- **Sure**: 9424.1 ms
- **API Response Time**: 9329.6 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, akademik takvimde belirlenen süre içinde öğrenci bilgi sistemine girerek ders kaydınızı yapabilirsiniz. Danışman onay süreci, ders kaydınızı tamamladıktan sonra devreye girer. Danışmanınız, sizin seçtiğiniz dersleri onaylayacak veya gerekli gördüğü durumlarda bazı dersleri listeden çıkaracaktır. 
- Kayıtlanmış olduğunuz dersleri kontrol etmeniz ve transkriptinizle müfredat bilgilerinizi karşılaştırmanız önemlidir. 
- Bu şekilde, başarısız olduğunuz veya alamadığınız dersleri ve ardisiklik gerektiren dersleri danışman onayına tabi tutabilirsiniz.
- Derslere başladığınızda, sınıf yoklama listesinde adınız yoksa danışmanınıza uğramanız gerekeceği bilgisini de göz önünde bulundurmanız gerekir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Ajan Sureleri**: registration_agent=9792ms; student_affairs_orchestrator=9848ms
- **API Sureleri**: api_total=11158ms; dispatch=9867ms; final_llm=1212ms; compose=1236ms; telemetry=6ms
- **Sure**: 11172.0 ms
- **API Response Time**: 11113.4 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Öğrenci, ilk kayıt yaptırdıktan sonra ders kaydı işlemlerini başlatacak. Bunun için öncelikle öğrenci bilgi yönetim sistemi üzerinden ders seçimi yapacaktır. Daha sonra akademik danışmanıyla iletişime geçerek ders seçimini onaylatacaktır. 

### Ders Kaydı Süreçleri

1. Ders Seçimi Yapın: Öncelikle öğrenci bilgi yönetim sistemi üzerinden seçeceğiniz derslere göre müfredat durumunu kontrol edin.
2. Ders Seçimini Onaylatmak için Akademik Danışmanınızla İletişime Geçin: Danışman onayı için öğrenci bilgisayarından ya da akademi danışmanının bilgisayarından sistem üzerinden gönderebilir.
3. Ders Kaydınız Onaylanıncaya Kadar Bekleyin: Danışman onayını aldığınızda ders kaydınızı tamamlamış sayılacaksınız.
4. Kaydın Sorgulanması: Kaydın tamamlanması için akademik takvimde belirtilen süreler içerisinde action almalısınız.
5. Eksiklik Var Mı? : Eğer akademik danışmanınıza ulaşamazsanız, bölüm başkanı ya da Dekan/Müdürlüğe durumunuzu bildirmelisiniz.

Ders kayıtlarınızı eğitim gördüğünüz birim ait akademik takvimde belirtilen süre içinde yapmanız gerekmektedir.

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=9553ms; student_affairs_orchestrator=9645ms
- **API Sureleri**: api_total=11508ms; dispatch=9664ms; final_llm=907ms; compose=929ms; telemetry=17ms
- **Sure**: 11565.8 ms
- **API Response Time**: 11444.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Üniversiteyi bırakmak istiyorsanız, ilk adımı atmak için öğrenci hizmetlerinden İlişik Kesme Sürecini başlatabilirsiniz. Bunun için UBYS'de Diğer menüsüne giderek "İlişik Kesme Talebinde Bulun" seçeneğini tıklayabilir veya şahsen başvurarak ilişik kesme formunu, form üzerinde belirtilen merkezlerde onaylattıktan sonra öğrenim gördüğünüz birimlere teslim edebilirsiniz.

İçeren bilgiler:
- İlişik Kesme Sürecini UBYS'den başlatmak için "Diğer" menüsüne gitmek
- Sahip olarak ilişik kesme formunu tamamlamak
- İlişik Kesme Sürecini başlatmak için UBYS'de talepte bulunmak
- Şahsen başvurulacak ilişik kesme formunu onaylatmak

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=9376ms; student_affairs_orchestrator=9431ms
- **API Sureleri**: api_total=11109ms; dispatch=9452ms; final_llm=742ms; compose=752ms; telemetry=13ms
- **Sure**: 11118.0 ms
- **API Response Time**: 11064.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ders notlarını sisteme girmeden ne yapabilirim?

Öğrenci İşleri Daire Başkanlığına başvurarak yardım alabilir veya öğretim elemanınıza durumunuzu bildirebilirsiniz. Bu sayede, öğretim elemanı tarafından fark edilen maddi hataya ilişkin sınav not bildirim/not düzeltme formu düzenlenebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
```
