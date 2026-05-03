# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 18:56:50
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 6

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 83.3% |
| Anahtar Bilgi Kapsami | 55.6% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 5344.4 ms |
| Medyan Sure | 5531.7 ms |
| Intent Analizi Aktif | 5/6 |
| Force LLM Sentez | 5/6 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=3, query_failures=0, agent_tasks=6, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 7846.9 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 7316.1 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 3/4 | 6532.0 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 4531.4 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 2261.3 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 2/3 | 3578.9 | - |

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
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=5410ms; student_affairs_orchestrator=5506ms; curriculum_agent=4783ms; academic_programs_orchestrator=4870ms
- **API Sureleri**: api_total=7834ms; dispatch=5598ms; global_llm=984ms; compose=1028ms; telemetry=16ms
- **Sure**: 7846.9 ms
- **API Response Time**: 7742.6 ms
- **Kaynak Sayisi**: 11

**Yanit:**
```
Kayıt yaptırdıktan sonra muafiyet başvurusunu yapmalısınız. Karar çıkana kadar derslere devam etmelisiniz. Ayrıca, daha önce aldığınız ve başarılı olduğunuz derslerden muaf tutulma talebinde bulunabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
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
- **Ajan Sureleri**: international_agent=5623ms; academic_programs_orchestrator=5713ms; registration_agent=5120ms; student_affairs_orchestrator=5173ms; tuition_agent=7ms; finance_orchestrator=118ms
- **API Sureleri**: api_total=7288ms; dispatch=5753ms; global_llm=1407ms; compose=1439ms; telemetry=13ms
- **Sure**: 7316.1 ms
- **API Response Time**: 7213.0 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Öğrenim ücretinizi Üniversite'ye ödemelisiniz. İkamet izni için ise Göç İdaresi İl Müdürlüğü'ne başvurmanız ve gerekli belgeleri ibraz etmeniz zorunludur. su sekilde bilgiler dikkate alılarak:
- Not çizelgesi (transkript) ve dilekçe ile başvurmanız gerekir.
- Islak imzalı belgelerin fotoğrafı, e-posta çıktısı vb. belgeleri temin etmeniz gerekebilir.
- Öğrenim ücreti ödemeniz ve gerekli belgeleri ibraz etmeniz durumunda ikamet izni alabilirsiniz.

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
- **Key Facts**: 3/4
  - [x] itiraz
  - [x] beş iş günü
  - [x] dilekçe
  - [ ] bölüm başkanlığı
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=3084ms; student_affairs_orchestrator=3328ms
- **API Sureleri**: api_total=6523ms; dispatch=3856ms; compose=6ms; telemetry=10ms
- **Sure**: 6532.0 ms
- **API Response Time**: 5046.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Sınav sonuçlarına, akademik takvimde belirtilen sınav not girişlerinin öğrenci otomasyon sistemine girilmesinin son gününden itibaren beş iş günü içerisinde ilgili birime dilekçe vererek itiraz edebilirsiniz. İtiraz üzerine sınav kağıdı incelenir ve işlem yazılı ve gerekçeli olarak üç iş günü içinde gerçekleştirilir. Öğretim elemanı tarafından fark edilen maddi hataya ilişkin sınav not bildirim/not düzeltme formu notların ilanından sonra düzenlenir. İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Ajan Sureleri**: registration_agent=3861ms; student_affairs_orchestrator=4378ms
- **API Sureleri**: api_total=4518ms; dispatch=4405ms; compose=6ms; telemetry=30ms
- **Sure**: 4531.4 ms
- **API Response Time**: 4439.8 ms
- **Kaynak Sayisi**: 2

**Yanit:**
```
Sınavda kopya çekilmesinin cezası hakkında net bilgi bulunamadı. Disiplin süreci ile ilgili olarak, disiplin cezaları bilgi yönetim sistemine işlenmekte ve ilgili kurumlara bildirilmektedir. Disiplin cezası alan öğrencilerin yatay geçiş başvuruları kabul edilmez ve bu durumu belgelemeleri gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: öğrenci_işleri_birimi.txt
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [x] birim
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1018ms; student_affairs_orchestrator=1077ms
- **API Sureleri**: api_total=2218ms; dispatch=1108ms; compose=13ms; telemetry=14ms
- **Sure**: 2261.3 ms
- **API Response Time**: 2152.4 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Üniversiteyi bırakmak istediğinizde, kayıt hakkınızı kaybedersiniz. Yazılı isteği üzerine kaydını sildiren öğrenci, ÖSYM tarafından yeniden yerleştirilmediği sürece Üniversiteye tekrar kaydolamaz. Üniversite ile ilişkiniz kesilir. Tüm işlemlerinizi akademik takvimde belirtilen tarihler arasında tamamlamanız gerekmektedir. Ayrıca, ders kaydını yapmayan öğrenci, o yarıyıl kaydını yenilememiş sayılır ve öğrencilik haklarından yararlanamaz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1309ms; student_affairs_orchestrator=1751ms
- **API Sureleri**: api_total=3504ms; dispatch=1789ms; compose=10ms; telemetry=111ms
- **Sure**: 3578.9 ms
- **API Response Time**: 3088.9 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Ders notlarınızın sisteme girilmemesi durumunda,Öğrenci İşleri Daire Başkanlığı bünyesinde faaliyet gösteren ve biriminize bakmakla yükümlü görevlilere ulaşmanız halinde sorununuz çözümlenebilecektir. Yoğunluk nedeni ile kendilerine ulaşamamanız durumunda; Başkanlık yöneticilerine, Öğrenci ve akademik personellere otomasyon sistemine teknik destek vermek amacı ile oluşturulan oidb@omu.edu.tr adreslerinden birine ulaşarak yaşadığınız sorunu bildirmeniz ve iletişim numaranızı bırakmanız durumunda sorununuza çözüm üretilecek ve geri dönüş yapılacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
