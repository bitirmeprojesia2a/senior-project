# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-13 02:59:09
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 84.0% |
| Uretim Modu Dogrulugu | 88.0% |
| Anahtar Bilgi Kapsami | 56.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 4285.6 ms |
| Medyan Sure | 3886.7 ms |
| Intent Analizi Aktif | 23/25 |
| Force LLM Sentez | 19/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 20364.0 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | YANLIS (rag) | 2/3 | 6380.3 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | OK | 2/4 | 1938.2 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 3/4 | 4245.1 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | YANLIS | OK | 2/3 | 3925.4 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 5106.1 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 3226.7 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | YANLIS (rag) | 4/5 | 2541.5 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | OK | 4/5 | 3886.7 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 4095.4 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | YANLIS | OK | 4/4 | 3317.3 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 2/4 | 2761.3 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 5058.3 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 4/4 | 4592.7 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | OK | 3/3 | 3618.9 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 2/4 | 4600.1 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 2/5 | 5168.7 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | OK | 2/4 | 1552.7 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 1/6 | 3890.9 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 2/4 | 2400.5 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 1/5 | 4403.9 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 3425.6 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 2040.8 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 2410.2 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 1/3 | 2189.0 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 20364.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, öğrenim gördüğü programlarda yer alan derslerden muafiyet başvurusunu, derslerin başlamasından itibaren ikinci haftanın sonuna kadar yapmalıdır. Muafiyet başvurusu sonuçlanana kadar, öğrenci muafiyet talebinde bulundukları derse/derslere devam etmelidir. 

Muafiyet başvurusu için, ilgili dekanlığa/müdürlüğe ders muafiyet başvuru formu, muafiyet talebinde bulundukları derslerin içerikleri ve onaylı not döküm belgesiyle (transkript) müracaat etmeleri gerekir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: yonerge_ders_yeterlik_muafiyet_intibak.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q2: Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi ve sınavda başarılı sayılmam için minimum not kaç?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/3
  - [x] staj
  - [x] tamamla
  - [ ] CC
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=procedural
- **Sure**: 6380.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Stajınızı tamamlamış olmanız tek ders sınavına girebilmek için zorunlu değildir. Bir dersten başarılı sayılmak için minimum not en az CB olmalıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Akademik Programlar: RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
```

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] değiştirebilir
  - [ ] devam koşulu
  - [x] yeni
  - [x] ders
- **Sure**: 1938.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Soru: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

Başarısız olunan seçmeli dersin yeniden açılmaması halinde, öğrencinin isteği ve danışmanın önerisi doğrultusunda yönetim kurulu kararı ile başka bir seçmeli ders alınabilir. Bu durumda, devam zorunluluğunuz, seçtiğiniz yeni seçmeli dersin devam zorunluluğuna göre değişir. Kaynak Belgeleri: [Kaynak 1: yonetmelik_lisansustu_egitim_ogretim.pdf, MADDE 21-2] ve [Kaynak 2: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf, MADDE 20-6] 

Yani, seçilen yeni dersin türüne göre (seçmeli, zorunlu vs.) devam zorunluluğu değişebilir. Ancak bu konuda daha net ve spesifik bir bilgi Kaynak Belgelerinde bulunmamaktadır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: yabancı_dil_eğitim_öğretimi_yönergesi.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
```

### Q4: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] transkript
  - [x] dahil
  - [x] ortalama
  - [ ] tamamlamıştır
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4245.1 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Pedagojik formasyon dersleri transkript içine dahil ediliyor. Mezuniyet ortalamasına dahil ediliyor. Diplomaların arkasına "Pedagojik Formasyon" ibaresi yer alıyor. 
Pedagojik formasyon dersleri öğrencilerin seçmeli olarak aldıkları derslerden oluşuyor. 
Transkriptte bu derslerin notları ve kredileri gösteriliyor. 
Diplomada pedagojik formasyon eğitimi aldığına dair bilgi bulunuyor.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt
- Belge: lisans_pedagojik_formasyon_derslerine_ilişkin.pdf
- Belge: uygulama_esaslari_lisans_pedagojik_formasyon.pdf
```

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['academic_programs', 'finance', 'student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/3
  - [x] ücret
  - [ ] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3925.4 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Öğrenim ücretini Üniversiteye yatırmalısınız. İkamet izni için gerekli belgeleri hazırlamalısınız. Kayıt işlemine ilişkin koşullar ve kayıt tarihleri Üniversite'nin ilgili web sayfalarında duyurulacaktır.Kayıt işlemleri şahsen başvuru ile kesin kayıt şeklinde yapılacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: Kural

Kaynak Ozeti:
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs', 'student_affairs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 5106.1 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
ÇAP programına başvurmak için önce harç borcunuzu ödemelisiniz. ÇAP başvuru şartları, Senato tarafından belirlenir ve her akademik yıl için öğrenci sayıları birim kuruluna sunulur. ÇAP'a kayıt ve kabul koşulları, birim kurulunun belirlediği şartlara göre yapılır. 

- Öncelikle harç borcunuzu ödeyin.
- ÇAP başvuru koşullarını öğrenmek için ilgili birimi araştırmalısınız. 
- Başvuru koşullarını sağlayarak başka bir ÇAP başvurusu yapabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
```

### Q7: Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra ders kaydını nasıl yapacağım, danışmanın onay süreci nasıl işliyor?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3226.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Kayıt yenileme döneminde harç ücretinizi yatırdıktan sonra, akademik takvimde belirtilen süre içinde öğrenci bilgi sistemi üzerinden alacak olduğunuz dersleri seçmeniz gerekir. Ders kaydınızı seçtikten sonra danışmanınızın onayını almanız gerekmektedir. 

Danışman onay bittikten sonra, kayıtlanmış olduğunuz dersleri tek tek kontrol etmeniz gerekir. Danışmanınız, sizin onayına göndermiş olduğunuz derslerden bir veya birkaçı listeden çıkartılmış olabilir. Bu nedenle, kayıt yaptırdığınız derslerin danışman onayından geçtikten sonra kontrol edilmesinde fayda vardır. 

Eğer danışmanınıza ulaşamazsanız, bölüm başkanınıza, bölüm başkanına da ulaşamazsanız Dekan/Müdürünüze durumu bildirmek sureti ile akademik takvimde belirtilen sürede danışman onayını muhakkak yaptırınız. Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz. 

Bu bilgiler ışığında, kayıt yenileme döneminde harç ücretinizi ödedikten sonra ders seçimi yapacağınızı ve daha sonra danışman onayınızı alacağınızı unutmayınız.

Finans:
Ogrenim ucreti ogrenci turune ve birime gore degisiyor. Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 4/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [ ] bildiri
  - [x] harç
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 2541.5 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Bursunuzun devri veya kesilip kesilmeyeceği konusunda bilgiye ulaşmak için burs aldığınız kurumla iletişim kurmanız gerekmektedir. Yatay geçiş yapmanız durumunda, 
- bursunuzun durumu,
- yeni üniversitede harç ödeme durumunuz
hakkında/neticeyi burs aldığınız kurumdan öğrenebilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG
- Akademik Programlar: RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [ ] azami
  - [x] ek
  - [x] süre
  - [x] katkı payı
  - [x] öde
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 3886.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Normal eğitim-öğretim süreniz altı yıl olup,-contrib payını ödemeniz gerekmektedir. Eğitim sürenizi bir yıl uzatabilirsiniz, ancak bu süre için de katkı payı/öğrenim ücreti ödemeniz gerekecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
```

### Q10: Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] giremez
  - [x] devamsızlık
  - [x] bütünleme
  - [x] tekrar
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=conditional
- **Sure**: 4095.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Bir dersten devamsızlıktan kalan öğrenci o dersin bütünleme sınavına giremez. Dersi tekrar alabilirsiniz, ancak bu konuda özel bir tarih veya koşul verilmemiştir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: yonerge_tip_fakultesi_doktorluk_egitim_sinav.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: bağıl_değerlendirme_yönergesi.pdf
```

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] öğrenim ücreti
  - [x] gerek yok
  - [x] yönetim kurulu
  - [x] sayılma
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 3317.3 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Kayıt dondurma isteğinizin ilgili yönetim kurulunca kabul edilmesi durumunda öğrenim ücretini yatırmanıza gerek yoktur. Kayıt dondurma süreniz eğitim süresinden sayılmaz. Her eğitim-öğretim döneminde katkı payı/öğrenim ücreti ödenmesi zorunludur, ancak kayıt dondurma durumunda bu ödemeye gerek yoktur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
```

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] transkript
  - [x] Ek Madde
  - [ ] başvuru yapabilir
  - [ ] GANO
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 2761.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

Akademik Programlar:
Ek Madde-1 ile yatay geçiş yapabilmek için, önlisans diploma programlarının hazırlık sınıfına ilk yarıyılı ile son yarıyılına yatay geçiş yapılamayacağı belirtildiği için, hazırlık sınıfındaysan ve transkriptin yoksa başka bir üniversiteye yatay geçiş yapamazsın. 

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı, daha detaylı bilgi için Uluslararasi Iliskiler Ofisi'ne başvurman Necessary olabilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: lisansüstü_eğitim_ve.pdf
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
- **Sure**: 5058.3 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçiş ve kurumlar arası yatay geçiş arasındaki farklar, başvuru şartları ve değerlendirme kriterleri farklılık gösterir. disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez, ayrıca kayıt dondurmuş olan öğrencilerin bu durumu belgelendirmesi gerekir. 
Kurum içi yatay geçişlerde, eşdeğer düzeyde diploma programlarına yatay geçiş kontenjanları, ÖSYM Kılavuzunda öngörülen öğrenci kontenjanının yıllık % 15 ini geçmeyecek biçimde dönemlere bölünerek ilgili yönetim kurulunun önerisi ve Senato’nun kararı ile belirlenir.
Yatay geçişler, ilgili enstitü içindeki başka bir enstitü anabilim/anasanat dalından veya eşdeğer eğitim veren yurt içi ve Yükseköğretim Kurulu tarafından tanınan yurt dışı lisansüstü programlar arasında yapılır. 
Kurum içi, kurumlar arası ve Yükseköğretim Kurulu tarafından tanınan yurt dışı yükseköğretim kurumlarının diploma programları arasındaki yatay geçişler, Yükseköğretim Kurulu onayı alınarak önceden ilan edilen kontenjan ve şartlar çerçevesinde yapılır.

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

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/4
  - [x] bağıl
  - [x] mutlak
  - [x] 10
  - [x] öğrenci sayısı
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=factual
- **Sure**: 4592.7 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Bağıl değerlendirme sistemi, öğrencilerin birbirleriyle kıyaslama yöntemiyle değerlendirilmesini sağlar. Mutlak değerlendirme sistemi ise öğrencilerin önceden belirlenmiş olan éxito ölçütlerine göre değerlendirilmesini sağlar. Öğrenci sayısı 10 ve altında ise mutlak değerlendirme sistemi uygulanır. Ancak öğrenci sayısı 10'un üzerinde ise bağıl değerlendirme sistemi uygulanır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: uzaktan_eğitim_tezsiz_yüksek_lisans_programı_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: hizmet_içi_eğitim_yönergesi.pdf
- Belge: yonerge_bagil_degerlendirme.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: bağıl_değerlendirme_yönergesi.pdf
```

### Q15: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] diploma eki
  - [x] transkript
  - [x] yerine geçmez
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 3618.9 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Diploma eki transkript yerine geçmez. Diploma eki, kişinin takip edip başarıyla tamamladığı öğrenimin yapı, düzey, bağlam, içerik ve statüsünü tarif etmek üzere verilir. 
Diploma eki ile hangi kazanımları elde edebileceğiniz, yurtdışında daha okunabilir ve mukayese edilebilir bir diploma, akademik güzergahının tanınması gibi konularda yararlanabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [ ] süre
  - [x] hak
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4600.1 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Kayıt dondurma ve kayıt yaptırmama arasındaki fark, öğrencinin öğrencilik haklarının devam etme şekline bağlıdır. Kayıt dondurma, öğrencinin belgelendireceği önemli mazeret veya eğitim-öğretimine katkıda bulunacak dış imkânlar sebebiyle eğitimine ara vermesi durumudur. Bu durumda, öğrenci daha sonra kayıtlı olduğu programa geri dönebilir. 

Öğrencilik hakları, kayıt dondurma durumunda askıda kalırken, kayıt yaptırmama durumunda ise öğrencilikstatüsünüz etkilenir ve ders kaydı yapılmaz. Her iki durumda da öğrenci bilgi sistemi üzerinden gerekli işlemler yapılmalıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: ön_kayıt_kılavuzu_başvuru_adımları.pdf
- Belge: lisansüstü_eğitim_ve.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: yonerge_uzaktan_egitim_onlisans_lisans.pdf
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [ ] UBYS
  - [ ] ders seçimi
  - [x] danışman
  - [x] onay
  - [ ] yoklama
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 5168.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
İlk kez üniversite kaydını yaptıran bir öğrenci olarak, önce ön kayıt başvurusu yapabilirsiniz. Eğitim Öğretim yılında Ondokuzmayıs Üniversitesini tercih edip kesin kayıt hakkı kazanan adaylar ön kayıt başvurusu yapabilirler. ÖN KAYIT SİSTEMİ İKİ AŞAMALIDIR. 
Ön kaydı tamamladıktan sonra, akademik takvimde belirtilen sürede ders kaydınızı yapmanız gerekir. 
Eğer danışmanınıza ulaşamaz ve ders kaydınızı onaylatamazsanız, bölüm başkanınıza, bölüm başkanına da ulaşamazsanız Dekan/Müdürünüze durumu bildirmek sureti ile akademik takvimde belirtilen sürede danışman onayını muhakkak yaptırınız. 
Ders kaydı sırasında dersin not sistemi, yılı ve döneminin doğru seçilmesi gerekmektedir. Yanlış seçilen not sistemi nedeniyle hatalı not oluşacaktır. 
Son olarak, ödeme aşamasına geçtiğinizde işlemlerinizi sürdürebilmeniz için gerekli bilgilendirme metinlerine yer verilecektir. Bu metinlerde yer alan adımları takip ederek yapacağınız ödeme işlemi dekontunu sisteme yükleyerek ön kaydınızı tamamlayabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ders_yeterlilik_sınavı_uygulama_yönergesi.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: uluslararası_öğrenci.pdf
- Belge: ön_kayıt_kılavuzu_başvuru_adımları.pdf
```

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [x] itiraz
  - [ ] beş iş günü
  - [ ] dilekçe
  - [x] bölüm başkanlığı
- **Sure**: 1552.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınav notuna itiraz etmek için 5 iş günü içerisinde ilgili bölüme yazılı olarak başvurmak gerekir. Yeniden inceleme, ilgili öğretim elemanı tarafından en geç 3 iş günü içinde yapılır ve sonuca göre doldurulan yeniden inceleme formu bölüm başkanlığına teslim edilir. İtiraz olması halinde sınav kâğıdı, ilgili öğretim elemanınca hazırlanmış cevap kâğıdı da dikkate alınarak sınav inceleme komisyonu tarafından incelenir. İşlem, en geç 3 iş günü içinde sonuçlandırılır ve itiraz değerlendirme formu doldurulur. Öğretim elemanı tarafından fark edilen maddi hataya ilişkin sınav not bildirim/not düzeltme formu, notların ilanından itibaren en geç 60 gün içinde ilgili birime sunulur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_ders_yeterlilik_sinavi_uygulama.pdf
- Belge: yüzde_on_başarı_değerlendirme_yönergesi.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/6
  - [ ] ders
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [ ] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3890.9 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Mezuniyet hakkı kazanan öğrencilere diplomaları verilir. Öğrenim gördüğü eğitim-öğretim programında yer alan bütün şartları yerine getirerek mezuniyet hakkı kazanan öğrencilere ön lisans ve lisans diplomaları Öğrenci İşleri Daire Başkanlığı tarafından verilir. Mezuniyetten sonra mahkeme kararına dayalı nüfus kaydı değişikliği olması durumunda, diploma yeniden düzenlenir. Önceki programı terk eden öğrenciler, başvuru koşullarını sağlamak şartıyla başka program başvurusu yapabilirler. İlişik kesilme hâlleri arasında öğrencinin kendi isteği ile programı bırakması bulunur.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: Kural

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
- Belge: zimmetteki_taşınırların_iadesi_hakkında.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: yonerge_uluslararasi_ogrenci_kabul.pdf
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
- **Sure**: 2400.5 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Bu konuda elimdeki kaynaklarda net bilgi bulunamadi. Diplomayı kaybetme ve e-devlette mezuniyet bilgilerinin görünmüyor olmasıyla ilgili prosedürler veya çözüm önerileri için spesifik bilgiler verilmemiştir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
```

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'academic_programs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [ ] %40
  - [ ] %60
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4403.9 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi, yüz yüze derslerden farklı değildir. Koşullar elverdiği ölçüde tüm sınavların yüz yüze yapılması esastır, ancak tümü veya bir kısmı uzaktan olan derslerin sınavları çevrimiçi olarak da yapılabilir. 
- Çevrimiçi veya yüz yüze sınav türünden hangisinin uygulanacağı ders ile ilgili olarak öğretim elemanı tarafından belirlenir.
- Öğrencilerin yüz yüze yürütülen derslerin teorik saatlerinin en az % 70'ine ve ders uygulamaları, atölye ve laboratuvarların ise en az % 80'ine devam etmeleri gerekmektedir.
- Derslere devam durumu, dersin öğretim elemanınca yapılan yoklamalarla tespit edilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: yonerge_uzaktan_karma_egitim.pdf
- Belge: lisansüstü_eğitim_ve_öğretim_yönetmeliği.pdf
- Belge: yonetmelik_lisansustu_egitim_ogretim.pdf
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 3425.6 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Sınavda kopya çekilmesinin cezası, 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesine göre yürütülmektedir. Disiplin süreci, ONDOKUZ MAYIS ÜNİVERSİTESİ MÜHENDİSLİK FAKÜLTESİ SINAVLARDA UYULMASI GEREKEN KURALLARDisiplin Suçlarına İlişkin hükümler kapsamında işler. 
Sınav kağıtlarında herhangi bir değişiklik yapmak veya zarar vermek de yasaktır. 
Disiplin süreci ile ilgili hükümler 11.03.2023 tarihli resmî gazetede yayımlanmıştır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: Kural
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_ortak_sınav_yönergesi.pdf
- Belge: hizmet_içi_eğitim_yönergesi.pdf
- Belge: özel_yetenek_sınavı_yönergesi.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: koruma_ve_güvenlik_müdürlüğü_ulaşım_güvenliği_yönergesi.pdf
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
- **Sure**: 2040.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu konuda elimdeki kaynaklarda net bilgi bulunamadi.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_toplulukları_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: kimlik_kartı_yönergesi.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [x] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2410.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

Soru ile ilgili olarak verilen belge bağlamında net bilgi bulunamadı. Belge bağlamında kayıt dondurma süresinin bitiminde öğrencinin ayrıldığı dönemin/yılın başından başlamak koşuluyla öğrenimine kaldığı yerden devam edeceği belirtiliyor, ancak ders seçimine ilişkin özel bir bilgiden bahsedilmiyor. 

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/3
  - [x] danışman
  - [ ] bölüm
  - [ ] oidb@omu.edu.tr
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 2189.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu konuda elimdeki kaynaklarda net bilgi bulunamadi. Soru not girme ile ilgiliyken, elimdeki kaynaklar daha çok ders kaydı, akademik takvim ve danışman onayına ilişkin bilgilere yer veriyor.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
