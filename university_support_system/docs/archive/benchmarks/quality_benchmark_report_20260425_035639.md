# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-25 03:56:39
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 0.0% |
| Anahtar Bilgi Kapsami | 42.9% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 72965.3 ms |
| Medyan Sure | 77197.4 ms |
| Intent Analizi Aktif | 3/5 |
| Force LLM Sentez | 3/5 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | YANLIS (rag) | 2/4 | 77197.4 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | YANLIS (vt) | 2/5 | 65425.1 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | YANLIS (rag) | 2/5 | 64851.2 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | YANLIS (rag) | 0/4 | 79074.1 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | YANLIS (rag) | 3/3 | 78278.6 | - |

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
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant, google_ai/gemini-2.5-flash [fallback]; specialist_synthesis=groq/llama-3.3-70b-versatile, google_ai/gemini-2.5-flash [fallback]
- **API Sureleri**: api_total=77116ms; dispatch=32611ms; final_llm=32309ms; compose=0ms
- **Sure**: 77197.4 ms
- **API Response Time**: 77103.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
Üniversitenize dikey/yatay geçiş yolu ile kayıt yaptırdım. Üniversitenizden muaf olduğum dersleri ve almam gereken dersleri nasıl öğrenebilirim? Üniversitemize bağlı programlara kayıt yaptırıp muafiyet başvurusunda bulunan her öğrenci için ilgili birimlerin muafiyet ve intibak komisyonu tarafından bir muafiyet çizelgesi hazırlanarak yönetim kurulu kararıyla birlikte öğrenciye tebliğ edilir. Üniversitenize dikey geçiş/yatay geçiş/Merkezi Yerleştirme sınavı ile kayıt hakkı kazandım. Kaçıncı sınıftan devam edebilirim? Yatay geçişle gelen öğrenciler, başvurdukları yarıyıla; dikey geçişle gelen öğrenciler, beşinci yarıyıla; merkezi yerleştirme sınavları ile gelen öğrenciler ise birinci yarıyıla intibak ettirilir. Yapılan muafiyet ve intibak komisyonu kararına itiraz etmek istiyorum. Ne yapmalıyım? Muafiyet işleminin kesinleşip tarafınıza bildirildiği tarihten itibaren en geç bir hafta içinde ilgili birime dilekçe ile itirazda bulunabilirsiniz.

(Kaynak: sık_sorulan_sorular.txt)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
```

### Q7: Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra ders kaydını nasıl yapacağım, danışmanın onay süreci nasıl işliyor?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: vt (beklenen: llm) - YANLIS
- **Key Facts**: 2/5
  - [ ] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [ ] onay
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: specialist_synthesis=groq/llama-3.3-70b-versatile, google_ai/gemini-2.5-flash [fallback]; global_synthesis=groq/llama-3.3-70b-versatile, google_ai/gemini-2.5-flash [fallback]
- **API Sureleri**: api_total=65349ms; dispatch=32882ms; final_llm=32409ms; compose=0ms
- **Sure**: 65425.1 ms
- **API Response Time**: 65342.3 ms
- **Kaynak Sayisi**: 6

**Yanit:**
```
Ogrenci Isleri:
Eldeki en ilgili kaynakta su bilgi yer aliyor:
Öğrenci bilgi yönetim sisteminden öğrencilere toplu ya da bireysel mesaj göndererek yapabilirsiniz. Kayıt dönemi başlamadan transkript/müfredat kontrolünü yaparak akademik takvimde tanımlanan süre içerisinde ders kaydını yapmaları gerektiği, derslere başladığında ise sınıf yoklama listesinde adları yoksa danışmanlarına uğramaları gerektiği bilgisi paylaşılmalıdır.

(Kaynak: sık_sorulan_sorular.txt)

Finans:
Kayit yenileme ucreti icin Turk ogrenci / Mühendislik Fakültesi bilgisi veritabaninda kayitli. Yillik ucret: 2.397,00 TL. Donemlik ucret: 1.198,50 TL.

(Kaynak: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Finans: VT

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Veritabani kaydi: ogrenim ucreti tablosu
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/5
  - [ ] UBYS
  - [ ] ders seçimi
  - [x] danışman
  - [ ] onay
  - [x] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant, google_ai/gemini-2.5-flash [fallback]; specialist_synthesis=groq/llama-3.3-70b-versatile, google_ai/gemini-2.5-flash [fallback]
- **API Sureleri**: api_total=64808ms; dispatch=32634ms; final_llm=32093ms; compose=0ms
- **Sure**: 64851.2 ms
- **API Response Time**: 64803.7 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
Öğrenci bilgi yönetim sisteminden öğrencilere toplu ya da bireysel mesaj göndererek yapabilirsiniz. Kayıt dönemi başlamadan transkript/müfredat kontrolünü yaparak akademik takvimde tanımlanan süre içerisinde ders kaydını yapmaları gerektiği, derslere başladığında ise sınıf yoklama listesinde adları yoksa danışmanlarına uğramaları gerektiği bilgisi paylaşılmalıdır.

(Kaynak: sık_sorulan_sorular.txt)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_akademik_danışmanlık.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [ ] birim
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant, google_ai/gemini-2.5-flash [fallback]; specialist_synthesis=groq/llama-3.3-70b-versatile, google_ai/gemini-2.5-flash [fallback]
- **API Sureleri**: api_total=79006ms; dispatch=33937ms; final_llm=33002ms; compose=0ms
- **Sure**: 79074.1 ms
- **API Response Time**: 78996.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
MADDE 32- (1) Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre yükseköğretim kurumlarından çıkarma cezası almış olanlar ve kendi istekleri ile kaydını sildiren öğrencilerin Üniversite ile ilişiği kesilir.

(Kaynak: yonetmelik_onlisans_lisans_egitim_ogretim.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 3/3
  - [x] danışman
  - [x] bölüm
  - [x] oidb@omu.edu.tr
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=conditional
- **LLM Kullanimi**: final_refinement=groq/llama-3.1-8b-instant, google_ai/gemini-2.5-flash [fallback]; specialist_synthesis=groq/llama-3.3-70b-versatile, google_ai/gemini-2.5-flash [fallback]
- **API Sureleri**: api_total=78235ms; dispatch=32972ms; final_llm=33184ms; compose=0ms
- **Sure**: 78278.6 ms
- **API Response Time**: 78223.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
Öğrencinin almak istediği dersin, ders kayıt ekranında çıkmaması durumunda danışman olarak ne yapabilirim? Öğrenci İşleri Daire Başkanlığı bünyesinde faaliyet gösteren ve biriminize bakmakla yükümlü görevlilere ulaşmanız halinde sorununuz çözümlenebilecektir. Yoğunluk nedeni ile kendilerine ulaşamamanız durumunda; Başkanlık yöneticilerine, Öğrenci ve akademik personellere otomasyon sistemine teknik destek vermek amacı ile oluşturulan oidb@omu.edu.tr adreslerinden birine ulaşarak yaşadığınız sorunu bildirmeniz ve iletişim numaranızı bırakmanız durumunda sorununuza çözüm üretilecek ve geri dönüş yapılacaktır. Eğer ders kontenjanında dolu uyarısı alırsam ne yapmam gerekir? Öncelikle kontenjan tanımlanmış diğer grup dersleri denemelisiniz. Tüm grup ders kontenjanların dolu olması halinde durumu bölüm başkanına bildirmeniz gerekmektedir.

(Kaynak: sık_sorulan_sorular.txt)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```
