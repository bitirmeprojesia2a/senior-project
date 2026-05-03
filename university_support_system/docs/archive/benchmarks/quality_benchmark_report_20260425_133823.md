# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 13:38:23
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 80.0% |
| Uretim Modu Dogrulugu | 80.0% |
| Anahtar Bilgi Kapsami | 52.4% |
| Temiz Kalite Orani | 80.0% |
| Ortalama Sure | 43904.0 ms |
| Medyan Sure | 7580.9 ms |
| Intent Analizi Aktif | 4/5 |
| Force LLM Sentez | 4/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 19 |

## A2A Diagnostics Delta

- Overview delta: queries=15, query_failures=0, agent_tasks=28, agent_task_failures=19

| Agent | Role | Task Delta | Failed Delta | Last Error |
|-------|------|------------|--------------|------------|
| student_affairs_orchestrator | department_orchestrator | 7 | 7 | a2a_endpoint_missing |
| academic_programs_orchestrator | department_orchestrator | 3 | 3 | a2a_specialist_transport_failed |
| finance_orchestrator | department_orchestrator | 2 | 2 | a2a_specialist_transport_failed |
| registration_agent | specialist_agent | 8 | 2 | a2a_specialist_endpoint_missing |
| curriculum_agent | specialist_agent | 1 | 1 | a2a_specialist_transport_failed |
| international_agent | specialist_agent | 1 | 1 | a2a_specialist_transport_failed |
| regulation_agent | specialist_agent | 1 | 1 | a2a_specialist_transport_failed |
| scholarship_agent | specialist_agent | 1 | 1 | a2a_specialist_transport_failed |
| tuition_agent | specialist_agent | 3 | 1 | a2a_specialist_transport_failed |

Recent failure samples:
- `finance_orchestrator`: a2a_specialist_transport_failed - Kismi zamanli calisma ve yemek bursu basvuru sartlari nelerdir?
- `scholarship_agent`: a2a_specialist_transport_failed - Turk ogrenci baglami icin: Kismi zamanli calisma ve yemek bursu basvuru sartlari nelerdir?
- `finance_orchestrator`: a2a_specialist_transport_failed - Burslu ogrenci yatay gecis yaparsa burs ve harc durumu nasil etkilenir?
- `student_affairs_orchestrator`: a2a_endpoint_missing - Burslu ogrenci yatay gecis yaparsa burs ve harc durumu nasil etkilenir?
- `tuition_agent`: a2a_specialist_transport_failed - Turk ogrenci baglami icin: Muhendislik Fakultesi icin: Burslu ogrenci yatay gecis yaparsa burs ve harc durumu nasil etkilenir?

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | YANLIS | YANLIS (error) | 0/4 | 120088.3 | exception |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 80817.5 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 2/5 | 6501.6 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 3/4 | 4531.9 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 2/3 | 7580.9 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 120088.3 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: ReadTimeout: 

**Yanit:**
```

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
- **Ajan Sureleri**: registration_agent=35034ms; student_affairs_orchestrator=35472ms; tuition_agent=35ms; finance_orchestrator=1641ms
- **API Sureleri**: api_total=38357ms; dispatch=35725ms; final_llm=1263ms; compose=1321ms; telemetry=21ms
- **Sure**: 80817.5 ms
- **API Response Time**: 37496.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra, akademik takvimde belirlenen süre içinde öğrenci bilgi yönetim sisteminden ders kaydını tamamlamanız gerekmektedir. Ders kaydında müfredat durum kontrolü ve akademik takvimde belirtilen süre içinde kaydın tamamlanması wichtig hususlardır. Danışman onay süreci için, danışmanınıza ulaşarak ders kaydı onayınızı istemelisiniz. Danışmanınız onayladığında, onaylamış olduğu dersleri kontrol ediniz. Ayrıca, öğrenci bilgi yönetim sisteminde yer alan müfredat bilgileri ve transkriptinize ulaşarak, her kayıt dönemi zacatku alıp başarılı olduğunuz dersleri müfredatınızla karşılaştırmanız gerekmektedir. 

- Danışmanınıza ulaşarak ders kaydı onayınızı istemelisiniz.
- Danışmanınız onayladığında, onaylamış olduğu dersleri kontrol ediniz.
- Öğrenci bilgi yönetim sisteminde yer alan müfredat bilgileri ve transkriptinize ulaşarak, her kayıt dönemi başında alıp başarılı olduğunuz dersleri müfredatınızla karşılaştırabilirsiniz.

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
- **Key Facts**: 2/5
  - [ ] UBYS
  - [ ] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=4053ms; student_affairs_orchestrator=5199ms
- **API Sureleri**: api_total=6471ms; dispatch=5251ms; final_llm=1110ms; compose=1128ms; telemetry=16ms
- **Sure**: 6501.6 ms
- **API Response Time**: 6400.4 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Merhaba! Senin için öğrencelik hayatında önemli bir adıma, ders kaydından danışmanın onayına kadar olan süreci anlatmak için buradayım. Sen ilk kez üniversite kaydını yaptırmışsın ve sen de biliyorsun ki bu yolculuk önemli. Ben sana tamamlaman gereken adımları anlatacağım.

İlk adım öğrenci bilgi sistemininden ders kaydını yapmaktır. Akademik takvime göre belirlenen süre içinde bu sistemi kullanıp ders seçme işlemini tamamlamanız gerekir. Seçmiş olduğunuz dersleri, akademik danışmanınızla iletişime geçin ve bu seçimi onaylatın. Eğer danışmanınız ile iletişime geçemiyorsanız, bölüm başkanınıza veya dekanınıza durumunuzu bildirmeniz yeterli olacaktır. Böylece belirlenen süre içinde danışman onayını alırsınız.

Alınan onay sonrası, kayıt etmiş olduğunuz dersleri tek tek kontrol edin. Bunun için öğrenci bilgi yönetim sisteminde yer alan müfredat bilgilerine ve transkriptinize ulaşarak, her kayıt dönemi başında aldığınız dersleri müfredatınızla karşılaştırın. Bu adım önemli çünkü bazı dersleri kaydettiğinizde ve başarılı olduğunuzda bunları kontrol edeceksiniz.

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
- **Key Facts**: 3/4
  - [x] ilişik kesme
  - [ ] UBYS
  - [x] form
  - [x] birim
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2552ms; student_affairs_orchestrator=2631ms
- **API Sureleri**: api_total=4509ms; dispatch=2654ms; final_llm=976ms; compose=1000ms; telemetry=28ms
- **Sure**: 4531.9 ms
- **API Response Time**: 4368.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
İlişik kesme süreçlerine geçmeden önce, siz üniversiteyi bırakmak hakkında bir soruya cevap verdik.

Üniversiteyi Bırakmak: Eğer üniversiteyi bırakmak istiyorsanız, ÖZYÖK (e-devlet) üzerinden "İlişik Kesme Talebi" seçeneğini kullanarak ilişik kesme sürecini başlatabilirsiniz. Bu sayede kaydınızın silinmesiyle birlikte öğrencilik hakkınız sona erecektir. Ayrıca, şahsen başvurarak ilişik kesme formunu doldurup, belirtilen merkezlerde onaylattıktan sonra öğrenim gördüğünüz birime teslim edebilirsiniz.

Gerekli dikkat edilmesi gereken hususlar şöyledir:

- İlişik kesme talebinizi ÖZYÖK (e-devlet) üzerinden doldurun.
- İlişik kesme formunu doldurup gerekli merkezlerde onaylatın.
- Öğrenim gördüğünüz üniversiteye formu teslim edin.

Dikkat etmeniz gerekenler bunlardır.

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
- **Key Facts**: 2/3
  - [x] danışman
  - [x] bölüm
  - [ ] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; final_refinement=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=4464ms; student_affairs_orchestrator=5337ms
- **API Sureleri**: api_total=7560ms; dispatch=5605ms; final_llm=901ms; compose=921ms; telemetry=20ms
- **Sure**: 7580.9 ms
- **API Response Time**: 7430.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ders notlarınızı sisteme girmeyen öğretmeninize ulaşmakta sorun yaşıyorsanız öncelikle öğretmeninize ulaşarak durumunuzu bildirmelisiniz. Eğer öğretmeninize ulaşılamazsa bölüm başkanınıza veya danışmanınıza başvurarak sorunu çözmeye çalışın. Bilgi bulunamadı.

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
