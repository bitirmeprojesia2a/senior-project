# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 20:28:41
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 5

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 40.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 45.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 4507.8 ms |
| Medyan Sure | 4485.1 ms |
| Intent Analizi Aktif | 4/5 |
| Force LLM Sentez | 3/5 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | OK | 2/4 | 6726.7 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 3/5 | 4485.1 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | YANLIS | OK | 3/4 | 3210.8 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | YANLIS | OK | 1/4 | 5316.8 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 0/3 | 2799.7 | - |

## Soru Detaylari

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [ ] yeni
  - [x] ders
- **Sure**: 6726.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Başarısız olduğunuz seçmeli ders yerine başka bir seçmeli seçersek, devam zorunluluğu değişse de değişmez. Buna göre:

* Kaynak 1'in 1. maddesinde belirtildiği üzere, başarısız olunan dersi tekrar almak ve başarmak zorundasınız. Devam koşulunun yerine getirilmediği tekrar derslerine devam etmek esastır.
* Kaynak 2'nin 4. maddesinde belirtildiği üzere, devam koşulunu yerine getirmemenin cezası, başarısız olduğunuz blok derslere, laboratuvar/klinik öncesi uygulamalara/klinik uygulamalara ve seçmeli derslere devam etmek zorunda kalmanızdır.
* Kaynak 3'ten bir referans bulunamadı, bu nedenle devam zorunluluğunda bir değişiklik olmaz.
* Kaynak 1'in 2. maddesinde belirtildiği üzere, başarısız olunan dersin zorunlu dersler hariç, takip eden yarıyılda açılmaması veya programdan kaldırılmış olursa, danışmanın önerisi ve ilgili anabilim/anasanat dalı başkanlığının uygun görüşü ile bu dersin yerine başka bir lisansüstü ders alabiliriz.

Özetle, başarısız olduğunuz seçmeli ders yerine başka bir seçmeli ders seçmeniz, devam zorunluluğunuzda bir değişiklik getirmez.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
```

### Q7: Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra ders kaydını nasıl yapacağım, danışmanın onay süreci nasıl işliyor?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [ ] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4485.1 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Ders kaydını nasıl yapacağım?

Önceki adımda yatırdığınız öğrenim ücretini kontrol edin. Kayıt yenileme döneminde ders kaydınızı yapabilir ve akademik takvimde belirtilen süreler içinde kaydınızı tamamlamanız gereklidir.

- Belirtilen belgelere göre öğrenim ücretini yatırdıktan sonra,
- Müfredat durum kontrolü yaparak ders kaydınızı yapınız.
- Danışman onayı için transkriptinizi kontrol etmeniz gerekebilir.
- Sınıf yoklama listesinde adınızın olmaması durumunda danışmanınıza uğramanız gerekir.

Öğrenci katkı payı ve öğrenim ücreti, öğrenci türüne göre farklılık gösterir. Öğrenim ücretini doğru fiyat için öğrenim türünüz ve bölminizi kontrol ediniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: Kural

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q10: Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [x] tekrar
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 3210.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına girebilir miyim?

Yinelemem gereken bölümü belirtmedikten önce, OMU lisans programlarından bahseden kaynaklarda yer almayan bir konudur. Kaynak 1: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf'da ise devamsızlıktan kaldığı bir dersin bütünleme sınavına girilebilir mi konusunu değinmiyor. 

Ders tekrarı konusuna ilişkin bilgi için Kaynak 2: lisansüstü_eğitim_ve.pdf ve Kaynak 3: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf incelendiğinde lisansüstü öğrenci için devamsızlık nedenli tekrardan bahseden bir maddeye rastlanmaktadır. Kaynak 2'de lisansüstü öğrencinin başarısız olduğu dersleri tekrar almak ve başarmak zorunda olması, devam mecburiyetinin sağlanması için bahsedilmektedir. 

Buna karşılık Kaynak 3'te, lisans programı için 1, 2 ve 3.sınıftaki öğrenciler için yıl sonu sınav puanı 50 puanın altında veya yıl sonu başarı puanı 70’in altında olan öğrencilerin, yıl sonu sınavından en az 10 gün sonra Bütünleme sınavına girerken, 4 ve 5. sınıf öğrencilerinin blok sonu sınavına bütünleme sınavı hakkını kullanma hakkı bulunduğunu belirtmektedir.

Bu bilgiler ışığında, devamsızlıktan kaldığı bir dersin bütünleme sınavına girebilir miyim sorusunu, lisans programı için daha spesifik cevap almak mümkün gözükmektedir. Bu konudaki net bilgi bulunamadığından dolayı, "Bu konuda elimdeki kaynaklarda net bilgi bulunamadı" yanıtını verebilmemizin uygun görüldüğü düşüncesindeyim.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: yonerge_yabanci_dil_egitim_ogretim.pdf
```

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] öğrenim ücreti
  - [ ] gerek yok
  - [x] yönetim kurulu
  - [ ] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 5316.8 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kayıt dondurduğunuz süre için harç ücretini yatırmak zorunda değilsiniz. Kayıt dondurulan dönemler, eğitim süresi hesabına dahil edilmeyecektir. İkinci öğretim öğrencisi olarak kayıt dondurma isteğiniz, ilgili yönetim kuruluna başvurması halinde kabul edilecektir. Kayıt dondurulan döngüden sonra kaldığınız yerden eğitimine devam edebilirsiniz.

Detaylar:
- Öncelikle kayıt dondurma isteğinizi ilgili yönetim kuruluna başvurarak yapmalısınız.
- Kayıt dondurulan döneme harç ücretini yatırmak zorunda değilsiniz.
- Kayıt dondurulan dönemler, eğitim süresi hesabına dahil edilmeyecektir.
- Kayıt dondurulan döngüden sonra kaldığınız yerden eğitimine devam edebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: uzaktan_eğitim_önlisans_ve_lisans_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
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
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=True, query_type=factual
- **Sure**: 2799.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu durumda ne yapabilirsin?

Ders kaydı yaptırmayı gerektiren durumlar arasında yer aldığın için, sisteme girmemiş ders notlarını eklememeniz gerekir. Hocanızla iletişime geçerek durumunuzu belirterek, notlarınızı eklemelerini isteyebilirsiniz. Ayrıca, öğrenci işleri birimine başvuru yaparak durumunuzu açıklatabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
