# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 22:52:24
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 4

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 75.0% |
| Anahtar Bilgi Kapsami | 64.3% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 2286.0 ms |
| Medyan Sure | 2166.8 ms |
| Intent Analizi Aktif | 4/4 |
| Force LLM Sentez | 4/4 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=4, query_failures=0, agent_tasks=5, agent_task_failures=0

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 3/5 | 1854.6 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 2/5 | 3404.9 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 1405.5 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 4/4 | 2479.1 | - |

## Soru Detaylari

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
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1522ms; student_affairs_orchestrator=1732ms
- **API Sureleri**: api_total=1844ms; dispatch=1753ms; compose=6ms; telemetry=13ms
- **Sure**: 1854.6 ms
- **API Response Time**: 1786.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
İlk kez üniversite kaydını yaptıran bir öğrenci olarak, akademik takvimde belirtilen sürelerde ders kaydını yapmalısınız. Ders kaydını, "Öğrenci Bilgi Sistemi" üzerinden realizar ve ders seçimini tamamladığınızda akademik danışmanınızla iletişime geçerek ders seçimini onaylatmalısınız. Akademik takvimde belirtilen süre içinde ders kaydını yapmanız gerekmektedir. 

Ders kaydında üç önemli hususa dikkat etmelisiniz: müfredat durum kontrolü, akademik takvimde belirtilen süre içinde kaydın tamamlanması ve danışman onayı. Eğer danışmanınıza ulaşamazsanız, bölüm başkanınıza veya Dekan/Müdürünüze durumu bildirmek suretiyle akademik takvimde belirtilen sürede danışman onayını yaptırabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: engelli_öğrenciler_eğitim_öğretim_uygulamaları.pdf
```

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [x] %40
  - [ ] %60
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile; global_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: graduation_agent=921ms; student_affairs_orchestrator=1110ms; curriculum_agent=1487ms; academic_programs_orchestrator=1673ms
- **API Sureleri**: api_total=3390ms; dispatch=1785ms; global_llm=1479ms; compose=1508ms; telemetry=10ms
- **Sure**: 3404.9 ms
- **API Response Time**: 3318.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi, yüz yüze derslerden farklı değildir. Sınavlar, zorunlu haller dışında, yüz yüze yapılır ve dönem içi değerlendirme uzaktan eğitimde %40'tan fazla olamaz. Ancak, sınavlar çevrimiçi veya yüz yüze olarak yapılabilir ve sunum, rapor gibi yöntemler de kullanılabilir. 
- Uzaktan eğitimde dönem içi değerlendirme \%40'tan fazla olamaz.
- Sınavlar çevrimiçi veya yüz yüze olarak yapılabilir.
- Sunum, rapor gibi yöntemler de kullanılabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
- Belge: uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1245ms; student_affairs_orchestrator=1304ms
- **API Sureleri**: api_total=1395ms; dispatch=1322ms; compose=3ms; telemetry=12ms
- **Sure**: 1405.5 ms
- **API Response Time**: 1346.0 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Kopya çekilmesi disiplin suçu olarak değerlendirilir. Disiplin süreçleri, 11.03.2023 tarihli resmi gazetede yayımlanan 2547 sayılı Yükseköğretim Kanunu hükümlerine göre işler.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1313ms; student_affairs_orchestrator=1386ms
- **API Sureleri**: api_total=2464ms; dispatch=1405ms; compose=6ms; telemetry=42ms
- **Sure**: 2479.1 ms
- **API Response Time**: 2372.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Üniversiteyi bırakmak istediğinizde ilişik kesme süreci başlatabilirsiniz. UBYS üzerinden "İlişik Kesme Talebinde Bulun" seçeneğinden Relation Kesme Sürecini başlatabilirsiniz. Ayrıca şahsen başvurarak ilişik kesme formunu doldurup, merkezlerde onaylattıktan sonra öğrenim gördüğünüz birime teslim edebilirsiniz. Kaydınızın silinmesi ile birlikte öğrencilik hakkınız sona erer. Mezuniyet durumunuzu E-Devlet üzerinden kontrol etmeniz de gerekmektedir. İlişik kesmenin mezun olunduğu anlamına gelmediğini, mezuniyet ve diploma basım işlemlerinin başlatılması için yapıldığını unutmayınız.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
