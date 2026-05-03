# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 02:36:40
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 71.4% |
| Anahtar Bilgi Kapsami | 32.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 4345.6 ms |
| Medyan Sure | 2758.5 ms |
| Intent Analizi Aktif | 7/7 |
| Force LLM Sentez | 5/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | OK | OK | 2/4 | 2258.2 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | YANLIS (vt) | 0/4 | 3685.3 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 14750.2 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 2758.5 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 1684.0 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 3253.8 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 2/4 | 2029.1 | - |

## Soru Detaylari

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [ ] yeni
  - [x] ders
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=2204ms; dispatch=2147ms; compose=0ms
- **Sure**: 2258.2 ms
- **API Response Time**: 2186.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Devam zorunluluğunuz değişmez, ancak başarısız olduğunuz ders yerine seçtiğiniz başka dersin devam zorunluluğu yerine getirilir.

Benchmark: Yaz okulunda derslere devam zorunludur (MADDE 12 – (1), Kaynak: yonerge_yaz_okulu_egitim_ogretim.pdf)

Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli ders seçerseniz, devam zorunluluğunuz aynı kalmış olur. Başarısız olduğunuz ders için devam zorunluluğu yerine getirilmemiş olduğu için, devam zorunluluğu yerine getirilmemiş tekrar dersine devam esastır (MADDE 17- (1), Kaynak: yonetmelik_onlisans_lisans_egitim_ogretim.pdf)

Benchmark: Devam koşulu yerine getirilmemiş tekrar derslerine devam esastır (MADDE 17- (1), Kaynak: yonetmelik_onlisans_lisans_egitim_ogretim.pdf)

Yaz okulunda devam zorunluluğu yerine getirilen ancak başarısız olunan dersler için, alınan en son not geçerlidir ve YANO/GANO hesabında bu son not kullanılır (MADDE 12 – (2), Kaynak: yonerge_yaz_okulu_egitim_ogretim.pdf).

Benchmark: Tekrar edilen derslerde, alınan en son not geçerlidir ve YANO/GANO hesabında bu son not (MADDE 12 – (2), Kaynak: yonerge_yaz_okulu_egitim_ogretim.pdf).

Başarısız ettiğiniz seçmeli ders yerine başka bir seçmeli ders seçerseniz, devam zorunluluğu yerine getirilmemiş tekrar derslerine devam esastır (MADDE 17- (1), Kaynak: yonetmelik_onlisans_lisans_egitim_ogretim.pdf).

Benchmark: Devam koşulu yerine getirilmemiş tekrar derslerine devam esastır (MADDE 17- (1), Kaynak: yonetmelik_onlisans_lisans_egitim_ogretim.pdf).

Özetle, başarılı olmadığı seçmeli ders yerine başka bir seçmeli ders seçmek, devam zorunluluğunu etkilemez.

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
- **Uretim Modu**: vt (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] not ortalaması
  - [ ] harç
  - [ ] ödeme
  - [ ] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=3653ms; dispatch=2421ms; compose=0ms
- **Sure**: 3685.3 ms
- **API Response Time**: 3651.3 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Benchmark, Ogrenim ucreti icin Turk ogrenci / Mühendislik Fakültesi bilgisi veritabaninda kayitli. Yillik ucret: 2.397,00 TL. Donemlik ucret: 1.198,50 TL.

(Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf)

Uretim Turu:
- VT

Kaynak Ozeti:
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant; global_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=14714ms; dispatch=5818ms; global_llm=7566ms; compose=0ms
- **Sure**: 14750.2 ms
- **API Response Time**: 14702.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Benchmark, Kurum içi yatay geçiş ve kurumlar arası yatay geçiş arasındaki farklar:

Kurum içi yatay geçiş, aynı ede öğrenim yapan öğrencilerin farklı programlara katılmasıdır.

Bu geçiş için öğrenciler, genel olarak iki yılın derslerini ve son iki yarıyıldaki notlarını göz önünde bulundururlar. Öğrenciler, her dönem en fazla iki kat kat geçiş başvurusunda bulunabilir. Bu durum, öğrencilerin son iki yarıyılda aldıkları notlarının 4'lük sistemde en az 2.80 düzeyinde olması gerektiğini belirtir.

Kurum içi yatay geçiş başvuruları, ilana uygun olarak yapılır. Yatay geçişler, aynı diploma programının eşdeğer düzeyde farklı bir programına yapılan geçiştir.

Ayrıca, aynı diplomanın farklı bir programına yapılan yatay geçişte, öğrencinin ilk iki yarıyılda aldığı derslerini ve son iki yarıyıldaki notlarını göz önünde bulundurmalıdır. Bu geçiş başvuruları, ilana uygun olarak yapılır.

Bu durum, öğrencilerin ilk iki yarıyılda aldıkları ilk iki yarıyıldaki derslerini ve son iki yarıyıldaki notlarını göz önünde bulundurmasını gerektirir. Bu nedenle, öğrenciler, ilk iki yarıyıldaki derslerini ve son iki yarıyıldaki notlarını göz önünde bulundurmalıdır.

Not: Finans departmanına ait diğer bilgiler bu soruyla ilgili değildir ve kullanılmamıştır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
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
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=2720ms; dispatch=1435ms; compose=0ms
- **Sure**: 2758.5 ms
- **API Response Time**: 2716.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Her iki sorun için de yapmanız gerekenler farklıdır.

1. Diplomayı kaybeden için:
Diplomasını kaybeden öğrenciler, yaygın gazetelerden birine diploma kayıp ilanı vermek zorundadır. Bu ilanı yaparak, diploma yenisi alınabilir. (Kaynak-2, MADDE 17- (1))

2. E-devlette mezuniyet bilgilerinin görünmemesi için:
Bu sorunu çözmek için diploma eki (Islak imzalı belgelerin fotoğrafı, e-posta çıktısı vb.) zorunludur. Bu eki yaparak, mezuniyet bilgilerinizi e-devlette görünebilir hale getirebilirsiniz. (Kaynak-4)

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı:
Diploma eki zorunluluğu ile e-devlette mezuniyet bilgileri için görünebilmesi arasındaki ilişki, elimdeki kaynaklardan net olarak anlaşılabilmiyorsa.

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
- **API Sureleri**: api_total=1643ms; dispatch=1585ms; compose=0ms
- **Sure**: 1684.0 ms
- **API Response Time**: 1637.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Benchmark, - Cezasi: Kopya çekilmesinin cezası, öğrenciye sınav kağıtlarında herhangi bir değişiklik yapmak (karalamak, yırtmak, sayfaları varsa birbirinden ayırmak vb.) ve zarar verilmesi, sınav sırasında ve sınav salonundan çıkana kadar cep telefonu ile herhangi bir şekilde ilgilenmesi durumunda kopya muamelesi yapılır.
- Disiplin Süreci: Bu durum işletme tarafından Fakülte Dekanlığı/Yüksekokul Müdürlüğü veya Meslek Yükselme ve DeğerlendirmeBirimi tarafından incelenir ve disiplin soruşturması gerektirecek davranışlarda bulunulduğu durumlarda gerekli adımlar atılır.

Benchmark: Ondokuz Mayıs Üniversitesi (OMU) Mühendislik Fakültesi'sinde sınavlarda kopya çekilmesinin cezasının belirlenmesine ilişkin kurallar.

* Kaynak 2: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf (Guven: yuksek)
* Kaynak 3: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf (Guven: yuksek)
* Kaynak 4: işyeri_staj_sözleşmesi.pdf (Guven: yuksek)
* Kaynak 5: staj_ilkeleri_23122019_inş_müh.pdf (Guven: yuksek)

Not: Bu sorunun cevabı Ondokuz Mayıs Üniversitesi (OMU) Mühendislik Fakültesi'ne ait olan belgelerde açıkça belirtilmiştir.

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
- **LLM Kullanimi**: routing=groq/llama-3.1-8b-instant; specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=3220ms; dispatch=2010ms; compose=0ms
- **Sure**: 3253.8 ms
- **API Response Time**: 3215.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Benchmark, Soru Nedir: Üniversiteyi bırakma işlemleri
ÜNİVERSİTEYE BAYILMA İŞLEMLERİ

- Üniversite ile ilişiğiniz kesilmesi için ilk olarak öğrenci bilgi sistemine giriş yapın. 
- Burada "Kayıt Bilgileri" sekmesine tıklayabilir veya "Ayrılma ve Yeniden Kaydolma" sayfasına giderek "Kaydı Sil" butonuna basabilirsiniz.

- Kayıt bilgilerinizin silinmesi için öğrenci bilgi sisteminden alınan bildirim üzerine, onaylamamanız durumunda Üniversite ile ilişiğiniz kesilecektir. 
- Ayrılma veya silme işlemleri ile üniversite ile ilişiğiniz kesildiğini unutmayın

- Kaydını sildiren öğrenciler, ÖSYM tarafından yeniden yerleştirilemedikleri sürece Üniversiteye tekrar kaydolamazlar.

- ÖSYM tarafından yeniden yerleştirilmedikleri sürece Üniversiteye tekrar kaydolamazlar.
- Bu konularda elimdeki kaynaklarda net bilgi bulunamdı.

Kaynak: [Kaynak 1: yonetmelik_onlisans_lisans_egitim_ogretim.pdf | Guven: yuksek]
[Kaynak 2: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf | Guven: yuksek]
[Kaynak 3: işyeri_staj_sözleşmesi.pdf | Guven: yuksek]
[Kaynak 4: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf | Guven: yuksek]

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: işyeri_staj_sözleşmesi.pdf
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] kayıt
  - [ ] yenileme
  - [x] UBYS
  - [x] müfredat
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.1-8b-instant
- **API Sureleri**: api_total=2001ms; dispatch=1947ms; compose=0ms
- **Sure**: 2029.1 ms
- **API Response Time**: 1994.9 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Benchmark, Ders kaydını yeniden yapabilmeniz için akademik takvimde belirtilen süre zarfında (dokümanlarda yer almayan bu süre için belirsizlik yaratan ama kaynaklarından hareketle de bu soruya net bir cevap vermeye çalışıyoruz) öğrenci bilgi yönetim sistemi üzerinden internet ortamında ubys.omu.edu.tr adresine giriş yapmak sureti ile interneti bulunan her yerden yapabilirsiniz.

Bu süre içinde yapmadığınız dönemlerin eğitim süresinden de sayılacağından, GANO'su 1,80-2,49 arası olan öğrenciler için 6 AKTS, GANO'su 2,50-2,99 arası olan öğrenciler için 10 AKTS, GANO'su 3,00-3,49 arası olan öğrenciler için 12 AKTS ve GANO'su 3,50 ve üzerinde öğrenciler için 15 AKTS dilmesi koşuluyla, ders kaydını yeniden yapabilirsiniz.

İkolar veya ardışık dersler için danışman onayına tabi olacağınızdan, akademik takvimde belirtilen süre zarfında transkript/müfredat kontrolünü yaparak, danışman onayınıza uygun ders seçimi yapmanız gerekmektedir.

Danışman onayına gönderilen ders kaydı öğrenci bilgi yönetim sistemi üzerinden sistem üzerinden gönderebilmektedir. Danışman onayı için öğrencinin şahsen gelmesi gerekmemektedir.

- Kaynak 2: sık_sorulan_sorular.txt (Guven: yuksek)
- Kaynak 3: sık_sorulan_sorular.txt (Guven: yuksek)
- Kaynak 4: ön_lisans_ve_lisans.pdf (Guven: yuksek)
- Kaynak 5: yonetmelik_onlisans_lisans_egitim_ogretim.pdf (Guven: dusuk)

KAYNAK DOGRULAMA KURALLARI:
Belge baglaminda belirtilen kaynaklari dogruladim, ancak bu soruya cok net bir cevap vermedim.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
