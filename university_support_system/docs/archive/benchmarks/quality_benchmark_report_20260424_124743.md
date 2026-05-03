# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 12:47:43
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 85.7% |
| Anahtar Bilgi Kapsami | 44.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 8084.1 ms |
| Medyan Sure | 6363.3 ms |
| Intent Analizi Aktif | 7/7 |
| Force LLM Sentez | 5/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 1/4 | 1792.8 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 4/4 | 8413.4 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 15951.0 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 6363.3 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 2006.2 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 20348.3 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 1713.9 | - |

## Soru Detaylari

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] değiştirebilir
  - [ ] devam koşulu
  - [ ] yeni
  - [x] ders
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=1744ms; dispatch=1696ms; compose=0ms
- **Sure**: 1792.8 ms
- **API Response Time**: 1733.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Devam zorunluluğum değişmez. Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem, ancak devam zorunluluğu yerine getirilen ama başarısız olunan dersler için normal dönemde devam şartı aranır. Normal dönemde devam sağlamadığım dersler için devam zorunluluğu yerine getirilmemiştir.

Benchmark: Madde 19, Yönetmelik On Lisans Lisans Eğitim Öğretim (Kaynak 1)

Yanit detayları kaynaklarda:
- Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem, ilgili yönetim kurulunca kabul edilen başka yükseköğretim kurumlarının derslerinde devam zorunluluğu yerine getirilmemiştir.
- Yaz okulunda derslere devam zorunludur (MADDE 12, Kaynak 2)
- Yaz okulunda alınıp devam zorunluluğu yerine getirilen ancak başarısız olunan dersler için devam zorunluluğu yerine getirilmemiştir.
- Derslere devam durumunun tespit edilmesi eğitimde öğrencilerin yüz yüze yürütülen derslerin teorik saatlerinin en az % 70’ine; ders uygulamaları, atölye ve laboratuvarların ise en az % 80’ine devam etmeleri zorunludur (MADDE 17, Kaynak 3)

- Kaynak 2: Yonerge Yaz Okulu Eğitim Öğretim (Guven: yuksek)
- Kaynak 3: Yönetmelik On Lisans Lisans Eğitim Öğretim (Guven: yuksek)
- Kaynak 4: Yaz Dönemi Eğitim Öğretim Yönetmeliği (Guven: yuksek)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: yonerge_yaz_okulu_egitim_ogretim.pdf
- Belge: yaz_dönemi_eğitim_öğretim_yönetmeliği.pdf
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=8368ms; dispatch=2739ms; global_llm=4397ms; compose=0ms
- **Sure**: 8413.4 ms
- **API Response Time**: 8359.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, ÇAP programına başvurmak istediğinizde harç borunuz var ise başvurunuzu kabul edecek olmak için boraunu ödemeniz gerekir.Başvuru koşulunuzun sağlanmanız da harç borcu ile birlikte ana dal not ortalamasına % 20'nin üzerinde bir başarı sıralamasına sahip olmanız gerekir. Bu koşul sağlanmazsa harç borcu olan kişinin başvurunun kabul edilmez.

Harç borcu ödemek için üniversite yönetimince belirlenen işlemlerin yürütülmesinden sorumluyuz. Yönetmelikteki ilgili maddelere göre harç boru ödemek için üniversite yönetimine başvurmanız yerinde olacaktır.

Bu programa başvuracak öğrenciler iki ana dalın birlikte tamamlaması durumunda bu programdan yaradınlacaktır. ÇAP programına başvuracak öğrenciler, iki ana dal genel not ortalaması iki kez 4,00 üzerinden 2,75'in altına düşerse harç borcu olan öğrencinin de ilişkinin kesme hali oluşmaktadır.
 
Bilgi için 2025-2026 öğrenim yılı için Türk öğrenci öğrenim ücretleri yıllık 2.397,00 TL, dönemlik 1.198,50 TL olarak belirlenmiştir.
Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: VT
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=15871ms; dispatch=6597ms; global_llm=7928ms; compose=0ms
- **Sure**: 15951.0 ms
- **API Response Time**: 15812.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

Kurum içi yatay geçişle, aynı üniversitede farklı programlara geçiş yapılır. Kurumlar arası yatay geçiş ise, farklı üniversitelerin aynı düzeyde diploma programları arasında yapılır.

Kurum içi yatay geçiş için öğrencinin kayıtlı olduğu programda bitirdiği dönemlere ait genel not ortalamasının 4 üzerinden en az 2,80 olması gerekir. Bunun yanı sıra, herhangi bir disiplin cezası almayan adaylar için bu uygulama geçerlidir.

Kurumlararası yatay geçiş için de aynı düzeyde diploma programlarına yatay geçiş için genel not ortalamasının en az 2,80 olması gerekir. Ayrıca, disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez.

Başvuru tarihleri için farklı tarih aralığı bulunabilir; örneğin, kurum içi yatay geçiş başvurusu için 01.08.2025 – 15.08.2025 tarih aralığı dikkate alınabilir. 

Yatay geçiş başvurularının değerlendirilmesinde, farklı puan türlerindeki programlara geçiş için genel not ortalamasının %30'ı ve merkezi yerleştirme puanının %70'i kullanılır.

Bu konuya ilişkin daha fazla bilgi için, ilgili üniversite veya kurulumuza başvurmanız gerekecektir.
- yonerge_onlisans_lisans_yatay_gecis.pdf
- 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf 
- yonerge_uluslararasi_ogrenci_yatay_gecis.pdf

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yone
... (97 karakter daha)
```

### Q20: Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] 2. nüsha
  - [x] diploma
  - [x] e-devlet
  - [ ] YÖKSİS
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=6320ms; dispatch=5080ms; compose=0ms
- **Sure**: 6363.3 ms
- **API Response Time**: 6310.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, ### Soru 1: Diplomamı Kaybettim

Eğer diploma kaybedildiyse, diploma eki istenir.

- Diplomayı hazırlayıcı birimler tarafından tanzim edilen diploma defterine kaydı yoktur.
- Diplomayı kaybeden öğrenci, diploma ekine (fotoğraf, e-posta çıktısı vb.) iletilen diploma talebini doldurarak dilekçeyle üniversiteye başvurmalıdır.

### Soru 2: E-devlette Mezuniyet Bilgileri Görünmüyor

- Mezuniyet bilgisinin e-devlette görünmemesi, diploma kaydı ile ilgili bir sorun olabilir.
- Diploma defterinde öğrencilerin diploma numaralarına göre kaydedilir.
- Diplomayı teslim eden öğrenci, diploma defterine imzasını atmalıdır.
- Diploma defterinde diplomanın teslim edildiği tarih ile diplomayı teslim alanın imzasını atacağı alan bulunur.

### Benchmark

- Diploma defteri, diploma hazırlayan birimler tarafından usulüne uygun olarak tanzim edilir.
- Diploma defterinde diploma hakkında ayrıca bilgiler de kaydedilir.

### Kaynak Bilgisi

- Kaynak 1: Uygulama Esasları - Diploma Mezuniyet Belgeler (Yüksek Güven)
- Kaynak 2: Uygulama Esasları - Diploma Mezuniyet Belgeler (Yüksek Güven)
- Kaynak 3: 2025 - 2026 Eki Madde 1 Güz Yarıyılı Kayıt için Gerekli Belgeler (Yüksek Güven)

### Bilgi Kaynağı

Uygulama Esasları - Diploma Mezuniyet Belgeler (Yüksek Güven) başlıklı kaynak belgedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=1976ms; dispatch=1923ms; compose=0ms
- **Sure**: 2006.2 ms
- **API Response Time**: 1971.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, Benchmark:

* Kopya çekilmesinin cezası ve disiplin süreci ile ilgili olarak kaynaklarda herhangi bir bilgi bulunamadı.
* Ancak, sınavlarda kopya vermek ve çekme girişiminde bulunmak bir disiplin suçudur.

Sınav görevlileri bu suçun tespitine Hiçbir öğrenci, 15 dakikadan daha kısa süre olmamak üzere, yoklama işlemi tamamlanmadan ve sınav görevlisinden izin
KAYNAK 2: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf (Guven: yuksek)
sırasında ve sınav salonundan çıkana kadar cep telefonu ile herhangi bir şekilde ilgilenen öğrenciye kopya muamelesi yapılır.

KAYNAK 3: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf (Guven: yuksek)

Disiplin Suçlarına İlişkin hükümler 11.03.2023 tarihli resmi gazetede yayımlanan 2547 sayılı Yüksek
KAYNAK 4: işyeri_staj_sözleşmesi.pdf (Guven: yuksek)
MADDE 14 – Öğrencilerin işletmelerde disiplin soruşturmasını gerektirecek davranışlarda bulunmaları halinde, bu durum işletme tarafından Fakülte Dekanlığı/Yüksekokul Müdürlüğü veya Meslek
KAYNAK 5: staj_ilkeleri_23122019_inş_müh.pdf (Guven: yuksek)
MADDE 13– (a) Staj çalışmaları Bölüm stajKomisyonu tarafından incelenir ve
 
Bu konusunda elimdeki kaynaklarda net bilgi bulunamadı.

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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=google_ai/gemini-2.5-flash-lite [fallback]
- **API Sureleri**: api_total=20320ms; dispatch=19177ms; compose=0ms
- **Sure**: 20348.3 ms
- **API Response Time**: 20318.0 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Üniversiteyi bırakıp ayrılmak istemeniz durumunda, yazılı isteğiniz üzerine kaydınız silinebilir. Ancak, bu durumda ÖSYM tarafından yeniden yerleştirilmediğiniz sürece Üniversiteye tekrar kaydolamazsınız. Kaydı silinen öğrencilerin üniversite ile ilişiği kesilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [x] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=1680ms; dispatch=1640ms; compose=0ms
- **Sure**: 1713.9 ms
- **API Response Time**: 1677.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Yön Vermiş Olsa Nasıl Yapılabilir?
Bilgi bulunamadı.

Dönüşte Derse Girme Koşulları
Evet, yapabilirsiniz. Derse girme koşulu, dönem başında akademik takvimde belirlenen süre içinde ders kaydını yapmak ve danışman onayını almak. 

Dönüşte Derse Girme Koşullarının Bilgi Kaynakları: 

- Kaynaktan: sık_sorulan_sorular.txt | Guven: dusuk
 - Kaynak: öğrenci bilgi yönetim sisteminden öğrencilere toplu ya da bireysel mesaj göndererek yapabilirsiniz. Kayıt dönemi başlamadan transkript/müfredat kontrolünü yaparak akademik takvimde tanımlanan süre içerisinde ders kaydını yapmaları gerektiği, derslere başladığında ise sınıf yoklama listesinde adları yoksa danışmanlarına uğramaları gerektiği bilgisi paylaşılmalıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
```
