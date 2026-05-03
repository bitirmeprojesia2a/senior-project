# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 22:56:28
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 80.0% |
| Anahtar Bilgi Kapsami | 52.9% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3260.2 ms |
| Medyan Sure | 2513.6 ms |
| Intent Analizi Aktif | 5/5 |
| Force LLM Sentez | 4/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=5, query_failures=0, agent_tasks=8, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 3/4 | 5994.1 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | OK | 1/4 | 3682.1 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 4/5 | 2513.6 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 1638.7 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 2472.7 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] üç hafta
  - [x] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=2470ms; academic_programs_orchestrator=2662ms; registration_agent=2553ms; student_affairs_orchestrator=2747ms
- **API Sureleri**: api_total=5982ms; dispatch=2891ms; final_llm=1835ms; compose=1904ms; telemetry=12ms
- **Sure**: 5994.1 ms
- **API Response Time**: 5854.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Eğitim öğretimin başladığı tarihten itibaren üç hafta içinde daha önce öğrenim gördüğü yükseköğretim kurumlarında aldığı ve başarılı olduğu dersler için muafiyet başvurusunda bulunabilirsiniz. Muafiyet kararının alınması süreci tamamlanana kadar dönem derslerine devam etmeniz önemlidir. Bu süre zarfında mağdur olmamanız için ders kayıt işleminiz Öğrenci İşleri personellerince yerine getirilir.

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
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
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
- **Ajan Sureleri**: registration_agent=1915ms; student_affairs_orchestrator=2036ms; tuition_agent=16ms; finance_orchestrator=240ms
- **API Sureleri**: api_total=3652ms; dispatch=2085ms; final_llm=1424ms; compose=1457ms; telemetry=15ms
- **Sure**: 3682.1 ms
- **API Response Time**: 3578.6 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Kayıt dondurduğunuz süre eğitim süresinden sayılır. Kayıt dondurma işlemi için katkı payı/öğrenim ücreti ödemesi gereken öğrenciyseniz, bu ücreti ödemek zorundasınız. Ancak, kayıt olduğu programdan azami süre içinde mezun olamayan öğrencilerden yan dal/çift ana dal öğrencileri dersleri alıp başarılı olan ve başarı ortalamasına göre yapılan sıralamada ilk %10'a giren ikinci öğretim öğrencileri katkı payı/öğrenim ücreti ödemek zorundadır. 
- Kayıt dondurma işlemlerinde eğitim süresine etki edecek. 
- Öğrenim ücreti ödemeniz gerekebilir, bu durum sizin için geçerli ise ücret ödemeniz gerekir. 
- Yönetmeliklere göre kayıt dondurma işlemleri ve eğitim süresininine ilişkin kurallar geçerlidir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
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
- **Ajan Sureleri**: registration_agent=2267ms; student_affairs_orchestrator=2375ms
- **API Sureleri**: api_total=2504ms; dispatch=2409ms; compose=8ms; telemetry=8ms
- **Sure**: 2513.6 ms
- **API Response Time**: 2452.6 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Öğrenci bilgi sistemi üzerinden akademik takvimde belirtilen süre içinde ders kaydını yapar ve ders seçimini tamamladığında akademik danışmanıyla iletişime geçerek ders seçimini onaylatır. Akademik takvimde belirtilen süre içinde ders kaydını yapmayan öğrenciler, o dönemde öğrenimlerine devam edemez. Öncelikle başarısız oldukları ve alamadıkları alt dönem derslerini alacaklardır. AKTS kredileri toplamı, GANO’suna göre belirlenir. Danışman onayı için öğrencinin şahsen gelmesi gerektiği yönünde bağlayıcı bir hüküm bulunmamaktadır. Danışman onayına sistem üzerinden gönderebilirsiniz. Danışman tarafından iade edilen ders kayıt teklifini, akademik takvimde belirtilen sürede yeniden düzenleyerek danışmanınıza onaylatmakla yükümlüdür. Danışman onayından emin olunuz, danışman onayı olmayan ders kayıtları geçersizdir. Danışman onay işlemi tamamlandıktan sonra, kayıtlanmış olduğunuz dersleri tek tek kontrol ediniz.

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

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1468ms; student_affairs_orchestrator=1525ms
- **API Sureleri**: api_total=1627ms; dispatch=1546ms; compose=3ms; telemetry=11ms
- **Sure**: 1638.7 ms
- **API Response Time**: 1577.8 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Sınavda kopya çekilmesinin cezası hakkında net bilgi bulunamadı. Disiplin süreci ise Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre işler.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: ön_lisans_ve_lisans.pdf
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
- **Ajan Sureleri**: registration_agent=2278ms; student_affairs_orchestrator=2338ms
- **API Sureleri**: api_total=2451ms; dispatch=2359ms; compose=6ms; telemetry=11ms
- **Sure**: 2472.7 ms
- **API Response Time**: 2379.6 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Öğrenci Bilgi Sistemi üzerinden akademik takvimde belirtilen sürelerde ders kaydını yaparsınız. Ders seçimini tamamladığınızda, akademik danışmanınızla iletişime geçerek ders seçimini onaylatırsınız. Öğrenciler, her dönem/yıl başında öncelikle başarısız oldukları ve alamadıkları alt dönem derslerini seçerler. Akademik takvimde belirtilen süre içinde yapacağınız ders kaydında, GANO’nuzun seviyesine göre AKTS kredisini göz önünde bulundurursunuz. GANO’su 1,80-2,49 arası olan öğrenciler için

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
