# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 04:10:27
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 61.9% |
| Temiz Kalite Orani | 80.0% |
| Ortalama Sure | 7751.0 ms |
| Medyan Sure | 6903.1 ms |
| Intent Analizi Aktif | 5/5 |
| Force LLM Sentez | 5/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 15553.1 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 7148.7 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 4446.6 | uydurma_riski |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 4703.3 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 1/3 | 6903.1 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **API Sureleri**: api_total=15507ms; dispatch=5095ms; final_llm=5820ms; compose=0ms
- **Sure**: 15553.1 ms
- **API Response Time**: 15501.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Muafiyet başvurunuzu yapıp karar çıkana kadar derslere devam etmeniz önem arz etmektedir. Birim Yönetim Kurulu’nun muafiyet talebini uygun görmesi ve muaf olunan derslerin sisteme işlenmesi sonrasında, danışmanınız ile birlikte alacak olduğunuz derslere kaydınız yapılır. 
- Daha önce aldığınız ve başarılı olduğunuz derslerden muafiyet talebinde bulunabilirsiniz.
- Muafiyet başvurunuz sonuçlanıncaya kadar dönem derslerine devam etmeniz önerilir.
- Muafiyet kararının çıkmasıyla birlikte, muaf olunan dersler belirlenir ve ders kayıtları buna göre güncellenir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
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
- **API Sureleri**: api_total=7102ms; dispatch=5610ms; final_llm=1419ms; compose=0ms
- **Sure**: 7148.7 ms
- **API Response Time**: 7093.4 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, akademik takvimde belirtilen süre içerisinde öğrenci bilgi sistemi üzerinden ders kaydını yapabilirsiniz. Danışman onay süreci için, seçtiğiniz dersleri danışmanınıza göndermeniz gerekir. Danışmanınız, gerekli kontrolleri yaptıktan sonra onaylama veya listeden çıkartma işlemlerini gerçekleştirecektir. 
- Danışman onay işleminden sonra, kayıtlanmış olduğunuz dersleri kontrol etmeniz önerilir.
- Müfredat bilgilerini transkriptinizle karşılaştırmalarınızı önerilir.
- Akademik takvimde belirtilen süre içinde ders kaydını yapmayan öğrenciler, o dönemde öğrenimine devam etme hakkını kredisi sınırını aşmamak şartı ile bir üst sınıftan ders alabilirler.

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
- **API Sureleri**: api_total=4405ms; dispatch=2512ms; final_llm=1839ms; compose=0ms
- **Sure**: 4446.6 ms
- **API Response Time**: 4395.0 ms
- **Kaynak Sayisi**: 8
- **Uyarilar**: uydurma_riski

**Yanit:**
```
Merhaba, öncelikle öğrenci kaydı sürecini anlatacağım. İlk kez üniversite kaydını yaptıran bir öğrenci olarak, ders kaydından danışman onayına kadar tüm süreci başından sonuna anlatayım.

Ders kaydı yapma süreci; ÖSYS üzerinden başlatılır. İlk olarak öğrencinin akademik takvimde belirtilen süre içerisinde ders kaydı yapması gerekir. Bu süre genellikle ders başlangıcı tarihinden önce başlar ve daha sonraları başlar. Ders kaydını, «Öğrenci Bilgi Sistemi» üzerinden realizar etmelisiniz.

Öncelikle, başarısız olduğunuz ve alamadığınız alt dönem derslerini öncelikle seçmelisiniz. Sonra AKTS kredileri toplamını hesaplayabilirsiniz; GANO'su 1,80-2,49 arası olan öğrenciler için

Ders seçimini tamamladıktan sonra, akademik danışmanınızla iletışime geçerek ders seçiminizi onaylatmanız gerekir. Eğer danışmanınıza ulaşmazsanız, bölüm başkanınıza veya Dekan/Müdürüne durumu bildirmek suretiyle akademik takvimde belirtilen süre içerisinde danışman onayını mutlaka yaptırınız.

Bilgi kaynağında belirtildiği üzere, öğrenci bilgi yönetim sisteminden öğrencilere toplu ya da bireysel mesaj gönderilerek bu durum paylaşılabilir.

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
- **API Sureleri**: api_total=4653ms; dispatch=2267ms; final_llm=979ms; compose=0ms
- **Sure**: 4703.3 ms
- **API Response Time**: 4649.6 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Siz üniversiteyi bırakmak istiyorsanız, öncelikle İlişik Kesme Sürecini başlatmanız gerekmektedir. 

Bu sürecin başlatılması için UBYS'ye giriş yaparak "İlişik Kesme Talebinde Bulun" seçeneğini kullanabilirsiniz. İlişik kesme formunu doldurduktan sonra onaylayarak ve öğrenim gördüğünüz birime teslim ederek sürecinizi tamamlamanız mümkün. Lütfen unutmayın ki İlişik kesme sürecinin tamamlanması mezuniyetinizi anlamına gelmez; ancak E-Devlet üzerinden mezuniyet durumunuza ulaşabilirsiniz.

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
- **Key Facts**: 1/3
  - [ ] danışman
  - [ ] bölüm
  - [x] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **API Sureleri**: api_total=6854ms; dispatch=2691ms; final_llm=1284ms; compose=0ms
- **Sure**: 6903.1 ms
- **API Response Time**: 6851.4 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Siz ders notlarınızı sisteme girmemiş gibi bir durumda bulundunuz. Bu durumda öğretim elemanınıza ulaşarak durumu bildirmelisiniz. Eğer öğretim elemanınıza ulaşamazsanız, ilgili birimin yöneticilerine veya Öğrenci İşleri Daire Başkanlığına başvurabilirsiniz. Ayrıca, oidb@omu.edu.tr adresine e-posta yoluyla sorununuzu iletebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans.pdf
```
