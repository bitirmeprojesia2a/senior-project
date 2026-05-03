# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 18:08:16
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 80.0% |
| Anahtar Bilgi Kapsami | 28.6% |
| Temiz Kalite Orani | 80.0% |
| Ortalama Sure | 12594.4 ms |
| Medyan Sure | 7122.8 ms |
| Intent Analizi Aktif | 4/5 |
| Force LLM Sentez | 4/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=5, query_failures=0, agent_tasks=7, agent_task_failures=0

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 7122.8 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 1/4 | 3378.5 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 34042.7 | zayif_kaynak_destegi |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 3966.0 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 0/3 | 14462.1 | - |

## Soru Detaylari

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
- **Ajan Sureleri**: international_agent=4453ms; academic_programs_orchestrator=4513ms; tuition_agent=7ms; finance_orchestrator=92ms; registration_agent=2727ms; student_affairs_orchestrator=2776ms
- **API Sureleri**: api_total=7113ms; dispatch=4555ms; global_llm=2441ms; compose=2472ms; telemetry=17ms
- **Sure**: 7122.8 ms
- **API Response Time**: 7045.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Öğrenim ücretinizi yatırmanız gereken yer belirtilmemiştir. İkamet izni için hangi belgeleri hazırlamanız gerektiği de açıklanmamıştır. Öğrenim ücreti ve ödeme detayları için finans birimi ile iletişime geçmeniz önerilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
- Belge: ön_lisans_ve_lisans_programları.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
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
- **Ajan Sureleri**: registration_agent=3159ms; student_affairs_orchestrator=3242ms
- **API Sureleri**: api_total=3368ms; dispatch=3287ms; compose=4ms; telemetry=17ms
- **Sure**: 3378.5 ms
- **API Response Time**: 3310.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Sınav notuna itiraz etmek için 3 iş günü içinde başvuruda bulunabilirsiniz. İtirazınızın ardından notunuzun yeniden inceleneceği ve possiblye notunuzun düzeltilme ihtimali bulunmaktadır. İtiraz süresi dışında yapılan başvurular dikkate alınmaz. İtiraz proceso Ondokuz Mayıs Üniversitesi Ön Lisans ve Lisans Eğitim-Öğretim Yönetmeliğine uygun olarak yapılır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
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
- **Ajan Sureleri**: registration_agent=33876ms; student_affairs_orchestrator=33933ms
- **API Sureleri**: api_total=34032ms; dispatch=33954ms; compose=3ms; telemetry=10ms
- **Sure**: 34042.7 ms
- **API Response Time**: 33977.7 ms
- **Kaynak Sayisi**: 5
- **Uyarilar**: zayif_kaynak_destegi

**Yanit:**
```
Sınavda kopya çekilmesinin cezası disiplin suçudur. Disiplin Suçlarına İlişkin hükümler 11.03.2023 tarihli resmi gazetede yayımlanan 2547 sayılı Yükseköğretim Kanunu'nda belirtilmiştir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
- Belge: staj_ilkeleri_23122019_inş_müh.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2963ms; student_affairs_orchestrator=3018ms
- **API Sureleri**: api_total=3924ms; dispatch=3051ms; compose=3ms; telemetry=12ms
- **Sure**: 3966.0 ms
- **API Response Time**: 3876.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Üniversiteyi terk etmek istiyorsanız, kaydınızı sildirmek için yazılı istekte bulunmanız gerekir. univerzite ile ilişiğinizi kesmek için bu işlem zorunludur. Kayıt silme işleminin ardından, ÖSYM tarafından yeniden yerleştirilmediğiniz sürece üniversiteye tekrar kaydolamazsınız.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
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
- **Ajan Sureleri**: registration_agent=5009ms; student_affairs_orchestrator=5212ms
- **API Sureleri**: api_total=14451ms; dispatch=5337ms; compose=2ms; telemetry=26ms
- **Sure**: 14462.1 ms
- **API Response Time**: 14346.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu konuda elimdeki kaynaklarda net bilgi bulunamadi. Ogrenci Isleri'ne yonlendir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
