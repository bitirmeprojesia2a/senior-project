# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 18:38:35
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 6

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 66.7% |
| Anahtar Bilgi Kapsami | 66.7% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 2031.2 ms |
| Medyan Sure | 1868.0 ms |
| Intent Analizi Aktif | 4/6 |
| Force LLM Sentez | 3/6 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=6, query_failures=0, agent_tasks=9, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | YANLIS (rag) | 2/4 | 1324.1 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 3228.1 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 4/4 | 1298.6 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 1185.7 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 2411.8 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 2/3 | 2738.8 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/4
  - [ ] üç hafta
  - [x] dilekçe
  - [x] komisyon
  - [ ] derslere devam
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant
- **Ajan Sureleri**: registration_agent=5ms; student_affairs_orchestrator=57ms
- **API Sureleri**: api_total=1317ms; dispatch=75ms; compose=10ms; telemetry=11ms
- **Sure**: 1324.1 ms
- **API Response Time**: 1261.1 ms
- **Kaynak Sayisi**: 1

**Yanit:**
```
Yatay gecis sureci icin en ilgili kaynakta su bilgi yer aliyor:
Üniversitenize dikey/yatay geçiş yolu ile kayıt yaptırdım. Üniversitenizden muaf olduğum dersleri ve almam gereken dersleri nasıl öğrenebilirim? Üniversitemize bağlı programlara kayıt yaptırıp muafiyet başvurusunda bulunan her öğrenci için ilgili birimlerin muafiyet ve intibak komisyonu tarafından bir muafiyet çizelgesi hazırlanarak yönetim kurulu kararıyla birlikte öğrenciye tebliğ edilir. Üniversitenize dikey geçiş/yatay geçiş/Merkezi Yerleştirme sınavı ile kayıt hakkı kazandım. Kaçıncı sınıftan devam edebilirim? Yatay geçişle gelen öğrenciler, başvurdukları yarıyıla; dikey geçişle gelen öğrenciler, beşinci yarıyıla; merkezi yerleştirme sınavları ile gelen öğrenciler ise birinci yarıyıla intibak ettirilir. Yapılan muafiyet ve intibak komisyonu kararına itiraz etmek istiyorum. Ne yapmalıyım? Muafiyet işleminin kesinleşip tarafınıza bildirildiği tarihten itibaren en geç bir hafta içinde ilgili birime dilekçe ile itirazda bulunabilirsiniz.

(Kaynak: sık_sorulan_sorular.txt)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
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
- **Ajan Sureleri**: international_agent=1436ms; academic_programs_orchestrator=1522ms; registration_agent=1450ms; student_affairs_orchestrator=1516ms; tuition_agent=6ms; finance_orchestrator=86ms
- **API Sureleri**: api_total=3196ms; dispatch=1615ms; global_llm=1463ms; compose=1497ms; telemetry=11ms
- **Sure**: 3228.1 ms
- **API Response Time**: 3133.6 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Öğrenim ücretinizi üniversiteye yatırmalısınız. Ikamet izni için Goc Idaresi Il Mudurlugu'nden ogrenci ikamet izni almaniz zorunludur. Ikamet izni için gerekli belgelerin tam listesi verilmemekle birlikte, kesin kayıt işleminden sonra ilgili mercilere belgelerin teslim edilmesi zorunludur. 
- Kesin kayıt işleminden sonra ikamet izni için gerekli belgeleri teslim etmelisiniz.
- Not çizelgesi (transkript) ve dilekçe ile başvuru yapmanız gerekir.
- Üniversitenin ilgili biriminden alacağınız belgelerle başvurunuzu desteklemelisiniz.

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
- **Ajan Sureleri**: registration_agent=1101ms; student_affairs_orchestrator=1167ms
- **API Sureleri**: api_total=1272ms; dispatch=1190ms; compose=5ms; telemetry=9ms
- **Sure**: 1298.6 ms
- **API Response Time**: 1215.6 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınav notuna itiraz etmek için akademik takvimde belirtilen sınav not girişlerinin öğrenci otomasyon sistemine girilmesinin son gününden itibaren beş iş günü içerisinde ilgili birime (Bölüm Başkanlığına) dilekçe vererek başvurabilirsin. İtiraz üzerine sınav kağıdın incelenir ve işlem yazılı ve gerekçeli olarak yapılır. Not düzeltme itiraz formu ilgili birim yönetim kurulu kararıyla Öğrenci İşleri Daire Başkanlığına gönderilir. İtiraz süresi bittikten sonra bildirilen not ve not düzeltmeleri dikkate alınmaz.

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
- **Ajan Sureleri**: registration_agent=989ms; student_affairs_orchestrator=1056ms
- **API Sureleri**: api_total=1171ms; dispatch=1083ms; compose=2ms; telemetry=9ms
- **Sure**: 1185.7 ms
- **API Response Time**: 1109.4 ms
- **Kaynak Sayisi**: 2

**Yanit:**
```
Sınavda kopya çekilmesinin cezası ve disiplin süreci hakkında net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: öğrenci_konukevi_uygulama_yönergesi.pdf
- Belge: öğrenci_işleri_birimi.txt
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
- **Intent Analizi**: complexity=complex, force_llm=False, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.3-70b-versatile
- **Ajan Sureleri**: registration_agent=1315ms; student_affairs_orchestrator=1383ms
- **API Sureleri**: api_total=2390ms; dispatch=1403ms; compose=3ms; telemetry=9ms
- **Sure**: 2411.8 ms
- **API Response Time**: 2338.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Üniversiteden ayrılmak için kimlik kartını iade etmek zorunludur. Kimlik kartını iade etmeden ayrılanların ilişiği kesilmez. Ayrıca, Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre kaydını sildiren öğrencilerin üniversite ile ilişiği kesilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: kimlik_kartı_yönergesi.pdf
- Belge: öğrenci_işleri_birimi.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yaz_okulu_eğitim_öğretim.pdf
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
- **Ajan Sureleri**: registration_agent=1553ms; student_affairs_orchestrator=1637ms
- **API Sureleri**: api_total=2725ms; dispatch=1657ms; compose=4ms; telemetry=11ms
- **Sure**: 2738.8 ms
- **API Response Time**: 2596.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Söz konusu sorunla ilgili olarak Öğrenci İşleri Daire Başkanlığı bünyesinde faaliyet gösteren ve biriminize bakmakla yükümlü görevlilere ulaşabilirsiniz. Yoğunluk nedeni ile görevlilere ulaşamamanız durumunda, oidb@omu.edu.tr adresine sorunünüzü bildirerek iletişim numaranızı bırakabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
```
