# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 17:56:17
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 80.0% |
| Anahtar Bilgi Kapsami | 35.7% |
| Temiz Kalite Orani | 80.0% |
| Ortalama Sure | 3049.2 ms |
| Medyan Sure | 2846.9 ms |
| Intent Analizi Aktif | 4/5 |
| Force LLM Sentez | 4/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=5, query_failures=0, agent_tasks=7, agent_task_failures=0

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 4680.8 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 1/4 | 2343.1 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 2376.5 | zayif_kaynak_destegi |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 2998.5 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 1/3 | 2846.9 | - |

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
- **Ajan Sureleri**: international_agent=3148ms; academic_programs_orchestrator=3269ms; registration_agent=2026ms; student_affairs_orchestrator=2118ms; tuition_agent=10ms; finance_orchestrator=112ms
- **API Sureleri**: api_total=4663ms; dispatch=3348ms; global_llm=1198ms; compose=1226ms; telemetry=20ms
- **Sure**: 4680.8 ms
- **API Response Time**: 4596.2 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Öğrenim ücretini üniversite tarafından belirtilen banka hesaplarına yatırmanız gerekiyor. İkamet izni için gerekli belgeler arasında pasaport, öğrenci belgesi, öğrenim ücretinin ödendiğini gösteren belge ve diğer gerekli belgeler bulunuyor. 
- Not çizelgesi (transkript) ve dilekçe ile başvuru yapmanız da necessario podria.
- Öğrencilerin diğer belgeleri temin etmeleri ve bunları kanıtlayarak ibraz etmeleri zorunludur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM
- Finans: VT

Kaynak Ozeti:
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
- Belge: ön_lisans_ve_lisans_programları.pdf
- Belge: sık_sorulan_sorular.txt
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
- **Ajan Sureleri**: registration_agent=2176ms; student_affairs_orchestrator=2245ms
- **API Sureleri**: api_total=2328ms; dispatch=2264ms; compose=4ms; telemetry=10ms
- **Sure**: 2343.1 ms
- **API Response Time**: 2284.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Sınav notuna itraz etmek için 15 gün süre tanınmıştır. İtirazlar, Ondokuz Mayıs Üniversitesi Ön Lisans ve Lisans Eğitim-Öğretim Yönetmeliğine uygun olarak yapılır. İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz. Yeniden incelemeye 3 iş günü içinde itiraz edilebilir. Notları öğretim elemanı düzenler ve not bildirim/not düzeltme formu doldurur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ders_yeterlilik_sınavı_uygulama_yönergesi.pdf
- Belge: yonerge_yuzde_on_basari_degerlendirme.pdf
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
- **Ajan Sureleri**: registration_agent=2073ms; student_affairs_orchestrator=2163ms
- **API Sureleri**: api_total=2355ms; dispatch=2206ms; compose=3ms; telemetry=11ms
- **Sure**: 2376.5 ms
- **API Response Time**: 2272.6 ms
- **Kaynak Sayisi**: 5
- **Uyarilar**: zayif_kaynak_destegi

**Yanit:**
```
Sınavda kopya çekilmesinin cezası, disiplin suçu olarak değerlendirilir. Disiplin süreci, 2547 sayılı Yükseköğretim Kanunu hükümlerine göre yürütülür.

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1590ms; student_affairs_orchestrator=1666ms
- **API Sureleri**: api_total=2981ms; dispatch=1689ms; compose=10ms; telemetry=17ms
- **Sure**: 2998.5 ms
- **API Response Time**: 2907.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Üniversite ile ilişiğinizi kesmek için yazılı isteğinizi belirtmeniz. Bunun üzerine, universite ile ilişiğiniz kesilir. Ancak, ÖSYM tarafından yeniden yerleştirilmediğiniz sürece Üniversiteye tekrar kaydolamazsınız. Ayrıca, yükseköğretim kurumları öğrenci disiplin yönetmeliği ve diğer ilgili mevzuat hükümlerine göre kaydını sildiren öğrencilerin universite ile ilişiği kesilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/3
  - [ ] danışman
  - [x] bölüm
  - [ ] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1620ms; student_affairs_orchestrator=1674ms
- **API Sureleri**: api_total=2836ms; dispatch=1693ms; compose=3ms; telemetry=14ms
- **Sure**: 2846.9 ms
- **API Response Time**: 2791.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ders notlarınızı sisteme girmemiş olan hocanızla görüşmenizi öneririm. Hocanızla irtibata geçerek notların sisteme girilmesini isteyebilirsiniz. Eğer hocanızla irtibat kuramazsanız bölüm başkanınıza veya Dekan/Müdürlüğe durumunuzu bildirebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
