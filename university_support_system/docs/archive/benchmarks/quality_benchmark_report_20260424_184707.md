# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 18:47:07
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 6

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 83.3% |
| Anahtar Bilgi Kapsami | 66.7% |
| Temiz Kalite Orani | 83.3% |
| Ortalama Sure | 4055.9 ms |
| Medyan Sure | 4117.8 ms |
| Intent Analizi Aktif | 5/6 |
| Force LLM Sentez | 5/6 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 2 |

## A2A Diagnostics Delta

- Overview delta: queries=6, query_failures=0, agent_tasks=11, agent_task_failures=2

| Agent | Role | Task Delta | Failed Delta | Last Error |
|-------|------|------------|--------------|------------|
| registration_agent | specialist_agent | 6 | 1 | a2a_specialist_endpoint_missing |
| student_affairs_orchestrator | department_orchestrator | 1 | 1 | a2a_specialist_endpoint_missing |

Recent failure samples:
- `student_affairs_orchestrator`: a2a_specialist_endpoint_missing - Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?
- `registration_agent`: a2a_specialist_endpoint_missing - Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 4655.1 | a2a_transport_fallback |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 5355.3 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 4/4 | 3204.5 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 2885.2 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 2/4 | 4279.4 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 2/3 | 3956.2 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: curriculum_agent=3319ms; academic_programs_orchestrator=3418ms; student_affairs_orchestrator=41ms
- **API Sureleri**: api_total=4648ms; dispatch=3462ms; compose=5ms; telemetry=8ms
- **Sure**: 4655.1 ms
- **API Response Time**: 4596.0 ms
- **Kaynak Sayisi**: 5
- **Uyarilar**: a2a_transport_fallback

**Yanit:**
```
Ogrenci Isleri:
Kayit Agent agent servisine su anda ulasilamadi. Bu modda uzman ajanlar yalnizca A2A HTTP uzerinden calisir; gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin.

Akademik Programlar:
Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu eğitim öğretim yılı başlamadan önce yapmalıdır. Muafiyet talebi ilgili yönetim kurulu tarafından karara bağlanıncaya kadar öğrenciler, muafiyet istenen derslerin zorunlu veya seçmeli olmasına bakılmaksızın, bu derslere devam etmelidir. Öğrenci, daha önce aldığı ve başarılı olduğu derslerden muaf tutulur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: Kural

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Veritabani kaydi: ogrenci isleri
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
- **Ajan Sureleri**: international_agent=3027ms; academic_programs_orchestrator=3177ms; registration_agent=3205ms; student_affairs_orchestrator=3327ms; tuition_agent=7ms; finance_orchestrator=109ms
- **API Sureleri**: api_total=5338ms; dispatch=3454ms; global_llm=1760ms; compose=1792ms; telemetry=11ms
- **Sure**: 5355.3 ms
- **API Response Time**: 5270.8 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Öğrenim ücretini üniversiteye yatırmanız gerekiyor. İkamet izni için Göç İdaresi İl Müdürlüğü'nden öğrenci ikamet izni almanız zorunludur. Belgelerinizi ibraz etmeniz ve şartları yerine getirmeniz gereklidir. 
- not çizelgesi (transkript) ve dilekçe ile başvuruda bulunmanız gerekir.
- Finans birimi ile iletişim kurarak uluslararası öğrenci harç ücretleri ve ödeme detayları hakkında bilgi alabilirsiniz.

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
- Belge: uluslararası_öğrenci.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
- Belge: öğrenci_konukevi_uygulama_yönergesi.pdf
- Belge: yonerge_onlisans_lisans_staj.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
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
- **Ajan Sureleri**: registration_agent=2990ms; student_affairs_orchestrator=3060ms
- **API Sureleri**: api_total=3192ms; dispatch=3079ms; compose=5ms; telemetry=25ms
- **Sure**: 3204.5 ms
- **API Response Time**: 3115.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınav sonuçlarına, akademik takvimde belirtilen sınav not girişlerinin öğrenci otomasyon sistemine girilmesinin son gününden itibaren beş iş günü içerisinde ilgili birime (Bölüm Başkanlığına) dilekçe vererek itiraz edebilirsiniz. İtiraz üzerine sınav kağıdı incelenir, işlem yazılı ve gerekçeli olarak üç iş günü binnenir. İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ders_yeterlilik_sınavı_uygulama_yönergesi.pdf
- Belge: yonerge_yuzde_on_basari_degerlendirme.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2687ms; student_affairs_orchestrator=2761ms
- **API Sureleri**: api_total=2869ms; dispatch=2780ms; compose=2ms; telemetry=8ms
- **Sure**: 2885.2 ms
- **API Response Time**: 2805.6 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Sınavda kopya çekilmesinin cezası ve disiplin süreci hakkında elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: öğrenci_işleri_birimi.txt
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [x] birim
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=3230ms; student_affairs_orchestrator=3293ms
- **API Sureleri**: api_total=4270ms; dispatch=3315ms; compose=6ms; telemetry=10ms
- **Sure**: 4279.4 ms
- **API Response Time**: 4214.9 ms
- **Kaynak Sayisi**: 2

**Yanit:**
```
Üniversite ile ilişkinizi kesmek için kaydınızı sildirmeniz gerekiyor. Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre kaydınız silinebilir. Ayrıca, ders sayınızı bir'e indiremeyenler de üniversite ile ilişikleri kesilir. İlişik kesme işleminin yapılabilmesi için bazı in oluşması gerekir, bu koşullar oluştuğunda üniversite ile ilişkiniz kesilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: öğrenci_işleri_birimi.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2746ms; student_affairs_orchestrator=2801ms
- **API Sureleri**: api_total=3948ms; dispatch=2826ms; compose=5ms; telemetry=9ms
- **Sure**: 3956.2 ms
- **API Response Time**: 3901.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Öğrenci İşleri Daire Başkanlığı bünyesinde faaliyet gösteren ve biriminize bakmakla yükümlü görevlilere ulaşmanız halinde sorununuz çözümlenebilecektir. Yoğunluk nedeni ile kendilerine ulaşamamanız durumunda; Başkanlık yöneticilerine, Öğrenci ve akademik personellere otomasyon sistemine teknik destek vermek amacı ile oluşturulan oidb@omu.edu.tr adreslerinden birine ulaşarak yaşadığınız sorunu bildirmeniz ve iletişim numaranızı bırakmanız durumunda sorununuza çözüm üretilecek ve geri dönüş yapılacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
```
