# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 14:51:44
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 71.4% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 5036.7 ms |
| Medyan Sure | 3759.0 ms |
| Intent Analizi Aktif | 5/5 |
| Force LLM Sentez | 5/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=5, query_failures=0, agent_tasks=8, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 9903.7 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 4677.3 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 3239.1 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 3759.0 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 3/3 | 3604.6 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [x] dilekçe
  - [ ] komisyon
  - [ ] derslere devam
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=4171ms; academic_programs_orchestrator=5192ms; registration_agent=7577ms; student_affairs_orchestrator=7665ms
- **API Sureleri**: api_total=9891ms; dispatch=7708ms; final_llm=979ms; compose=1029ms; telemetry=13ms
- **Sure**: 9903.7 ms
- **API Response Time**: 9841.1 ms
- **Kaynak Sayisi**: 11

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, daha önce aldıkları dersler için Dekanlığa/Müdürlüğe muafiyet dilekçesi vermelidir. Muafiyet başvurunun sonuçlanıncaya kadar bu derslere kayıt yaptırıp devam etmek önemlidir. Birim Yönetim Kurulu’nun muafiyet talebini uygun görmesi ve muaf olunan derslerin sisteme işlenmesi sonrasında, danışman ile birlikte alacak olunacak derslere kaydı yapılır. 
- Muafiyet başvurunun sonuçlanıncaya kadar dönem derslerine devam etmek önemlidir.
- Daha önce alınan ve başarılı olunan derslerden muafiyet tanınır.
- Muaf olunan dersler için öğrencilere ücret iadesi yapılmaz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
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
- **Ajan Sureleri**: registration_agent=2486ms; student_affairs_orchestrator=2663ms; tuition_agent=22ms; finance_orchestrator=169ms
- **API Sureleri**: api_total=4649ms; dispatch=2760ms; final_llm=1726ms; compose=1748ms; telemetry=40ms
- **Sure**: 4677.3 ms
- **API Response Time**: 4529.0 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Harç ücretini yatırdıktan sonra akademik takvimde belirtilen süre içinde öğrenci bilgi sisteminden ders kaydını yapabilirsiniz. Danışman onay süreci, ders kaydınızı yaptıktan sonra devreye girer. Danışmanınız, sizin seçtiğiniz dersleri onaylar veya reddeder. 
- Ders kaydınızı yaptıktan sonra, kayıtlanmış olduğunuz dersleri tek tek kontrol ediniz.
- Danışman onay süreci tamamlandıktan sonra, öğrenci bilgi yönetim sisteminde yer alan müfredat bilgileri ve transkriptinize ulaşarak, her kayıt dönemi başında alıp başarılı olduğunuz dersleri müfredatınızla karşılaştırmanız gerekmektedir.
- Ardışıklik gerektiren dersler için danışman onayı gerekir.

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
- **Ajan Sureleri**: registration_agent=2098ms; student_affairs_orchestrator=2195ms
- **API Sureleri**: api_total=3228ms; dispatch=2217ms; final_llm=887ms; compose=899ms; telemetry=9ms
- **Sure**: 3239.1 ms
- **API Response Time**: 3144.7 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Selam! Öğrenci olarak ders kaydından danışman onayına kadar süreç hakkında bilgi almak istediniz.

Tüm adımlarını izleyeceksiniz: 

Birincisi, dönem içerisinde almanız gereken ve almadığınız alt dönem derslerini almanız gerekiyor. Daha sonra, akademik takvimde belirtilen süreler içerisinde "Öğrenci Bilgi Sistemi" üzerinden ders kaydı yapabilirsiniz. 

Ders seçiminizi tamamladığınızda, akademik danışmanınıza ulaşarak ders seçimini onaylatmanız gerekmektedir. Danışmanınıza ulaşmazsanız, bölüm başkanınıza atau Dekan/Müdürünüze durumu bildirmek suretiyle akademik takvimde belirtilen sürede danışman onayını yaptırabilirsiniz.

Bilgi bulunamadı.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1852ms; student_affairs_orchestrator=1920ms
- **API Sureleri**: api_total=3740ms; dispatch=1954ms; final_llm=927ms; compose=952ms; telemetry=21ms
- **Sure**: 3759.0 ms
- **API Response Time**: 3669.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Bakmakla yükümlü olduğum üniversite olarak, üniversiteyi bırakıp ayrılmak isteğini dikkate alıyorum. İşte gerekli adımlar:

Bilindiği gibi öğrenci ilişkini kesmek, "Üniversite Bilişim Sistemleri (UBYS)" üzerinden "İlişik Kesme Talebinde Bulun" seçeneğinden başlatabilir veya şahsen başvurarak ilişik kesme formunu doldurup onaylattıktan sonra öğrenim gördüğünüz birime teslim edebilirsiniz.

İlişik kesme formu, UBYS sisteminde bulunmuyor. Ancak, ilişkik kesme formu doldurup onaylattıktan sonra öğrenim gördüğünüz birime teslim edebilirsiniz.
Son olarak, mezuniyet durumunuzu E-Devlet üzerinden kontrol edmeniz önemlidir. 

İsterseniz, ilişkik kesme sürecini tamamlamak için bize şahsen başvurabilirsiniz.

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
- **Key Facts**: 3/3
  - [x] danışman
  - [x] bölüm
  - [x] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1756ms; student_affairs_orchestrator=1831ms
- **API Sureleri**: api_total=3593ms; dispatch=1856ms; final_llm=865ms; compose=894ms; telemetry=18ms
- **Sure**: 3604.6 ms
- **API Response Time**: 3540.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Ders notlarını sisteme girmemiş olan öğretim elemanı ile iletişime geçerek sorunu bildirmelisiniz. Eğer öğretim elemanınıza ulaşamazsanız, bölüm başkanına başvurarak yardım isteyebilirsiniz. Ayrıca, birim yöneticilerine veya Öğrenci İşleri Daire Başkanlığına da `oidb@omu.edu.tr` adresine e-posta göndererek yaşadığınız sorunu iletebilirsiniz. 

Detaylar:
- İlk olarak danışmanınız ile iletişime geçin.
- Eğer iletişim kuramıyorsanız, bölüm başkanınıza başvuruda bulunun.
- Sorununu Öğrenci İşleri Daire Başkanlığına da bildirebilirsiniz.
- E-posta adresini ve daha fazla detay bilgisini, ilgili departmanın sorumluluk alanına ait bilgiye sahip olmadigimiz için veremiyoruz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
