# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 18:49:07
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 40.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 4164.5 ms |
| Medyan Sure | 4164.5 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=1, query_failures=0, agent_tasks=1, agent_task_failures=0

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 2/5 | 4164.5 | - |

## Soru Detaylari

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
- **LLM Kullanimi**: final_refinement=groq/llama-3.3-70b-versatile; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=2616ms; student_affairs_orchestrator=2761ms
- **API Sureleri**: api_total=4154ms; dispatch=2808ms; final_llm=1186ms; compose=1244ms; telemetry=27ms
- **Sure**: 4164.5 ms
- **API Response Time**: 4069.8 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Ders kaydını yapmak için akademik takvimde belirlenen süre içinde hareket etmeniz gerekiyor. Önce başarısız olduğunuz veya alamadığınız alt dönem derslerini dikkate alın. AKTS kredileri toplamı, genel akademik ortalamınıza göre belirlenir. GANO'su 1,80-2,49 arası olan öğrenciler için
Ders kaydını yaptıktan sonra, danışman onayına göndermeniz gerekir. 
- Danışman, onaya gönderilen ders kaydını onaylama veya iade etme hakkını kullanabilir.
- Danışman onayını aldıktan sonra, ders kaydınız kesinleşir.
- Eğer danışmanınıza ulaşamaz ve ders kaydınızı onaylatamazsanız, bölüm başkanınıza veya Dekan/Müdürünüze durumu bildirmelisiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
