# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-13 02:35:09
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 88.0% |
| Uretim Modu Dogrulugu | 76.0% |
| Anahtar Bilgi Kapsami | 50.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3906.9 ms |
| Medyan Sure | 3289.8 ms |
| Intent Analizi Aktif | 23/25 |
| Force LLM Sentez | 20/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | OK | OK | 1/4 | 24262.0 | - |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | OK | OK | 2/3 | 3666.5 | - |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | YANLIS (rag) | 2/4 | 504.3 | - |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | OK | OK | 3/4 | 4328.2 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | OK | OK | 3/3 | 3763.5 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 2/4 | 4997.0 | - |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | OK | 4/5 | 3201.9 | - |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | OK | 4/5 | 4203.0 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | OK | 4/5 | 2391.1 | - |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | OK | OK | 4/4 | 5320.4 | - |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | YANLIS | OK | 4/4 | 3558.2 | - |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | OK | OK | 1/4 | 2757.9 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 2/5 | 5086.1 | - |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | OK | OK | 4/4 | 3289.8 | - |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | OK | YANLIS (rag) | 3/3 | 1217.9 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | YANLIS (kural) | 0/4 | 1231.4 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | OK | 2/5 | 3568.9 | - |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | OK | YANLIS (rag) | 1/4 | 377.9 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | YANLIS (kural) | 1/6 | 1560.3 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | OK | OK | 1/4 | 2125.8 | - |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | OK | OK | 2/5 | 3667.4 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | OK | YANLIS (llm) | 0/0 | 3052.2 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 0/4 | 2106.2 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 0/4 | 5094.1 | - |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | OK | OK | 0/3 | 2340.8 | - |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] üç hafta
  - [ ] dilekçe
  - [ ] komisyon
  - [x] derslere devam
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 24262.0 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Yatay geçişle gelen bir öğrenci, kayıt yaptırdığı öğretim yılının en geç 3. haftasının sonuna kadar transkripti ve ders içerikleri ile birlikte muafiyet başvurusunu yapmalıdır. 
Muafiyet başvurusu sonuçlanana kadar derslere devam etmesi gerekir. 
Derslerin tamamını başarmış olma şartı aranmaz, ancak daha önce disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_uluslararasi_ogrenci_yatay_gecis.pdf
- Belge: yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf
- Belge: önlisans_lisans_ve_lisansüstü_düzeyindeki_programlara_uluslararası_öğrenci.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: mezunlar_için_pedagojik_formasyon_eğitimi.pdf
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
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/3
  - [x] staj
  - [x] tamamla
  - [ ] CC
- **Intent Analizi**: complexity=simple, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 3666.5 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Tek ders sınavına girebilmek için stajınızı tamamlamış olmanız gerekmez. Bir dersten başarılı olmak için minimum not CB (en az CB) olmalıdır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

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
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/4
  - [ ] değiştirebilir
  - [x] devam koşulu
  - [ ] yeni
  - [x] ders
- **Sure**: 504.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
MADDE 21 – (1) Lisansüstü öğrenci, başarısız olduğu dersleri tekrar almak ve başarmak zorundadır. Devam koşulunun yerine getirilmediği tekrar derslerine devam etmek esastır. Devam mecburiyeti olmayan öğrenciler de yarıyıl içi değerlendirmelerine katılmak zorundadır. Eğitim programının özelliği gerektirdiğinde, anabilim/anasanat dallarının, devam koşulunu sağlayıp başarısız olmuş öğrencilerin derse devam etmesini istemeleri halinde bu uygulama enstitü kurulunun kararı ile gerçekleştirilir. (2) Başarısız olunan dersin zorunlu dersler hariç, takip eden yarıyılda açılmaması veya programdan kaldırılmış olması halinde danışmanın önerisi ve ilgili anabilim/anasanat dalı başkanlığının uygun görüşü ile bu dersin yerine başka bir lisansüstü ders alabilir. Yarıyıl içi değerlendirme ve yarıyıl sonu sınavları

(Kaynak: yonetmelik_lisansustu_egitim_ogretim.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

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
- **Sure**: 4328.2 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Pedagojik formasyon dersleri transkriptte yer alır, mezuniyet ortalamasına dahil edilir ve diplomaların arkasına "Pedagojik formasyon eğitimi aldığı" ibaresi yazılır. 

Bu dersler öğrenciler tarafından seçmeli ders olarak alındığından transkript binnen yer almaktadır. Sadece bir transkript düzenlenecek ve bu dersler bu transkript içinde yer alacaktır. 
Mezuniyet ortalamasına dahil edileceklerdir. 
Diplomalarında "Pedagojik formasyon" ibaresi yer alacaktır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: pedagojik_formasyon_eğitiminin_uygulanmasına_dair_muhtemel_sorular_ve_cevapları.txt
- Belge: lisans_pedagojik_formasyon_derslerine_ilişkin.pdf
- Belge: uygulama_esaslari_lisans_pedagojik_formasyon.pdf
```

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'finance', 'student_affairs'] (beklenen: ['academic_programs', 'finance', 'student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] ücret
  - [x] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3763.5 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Ogrenci Isleri:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

Akademik Programlar:
Ücret yatırma işlemi için spesifik bir bilgi bulunamadı. Ücret yatırma işlemini nereye yapacağınızı öğrenmek için Üniversitesi'nin ilgili web sayfalarını veya Öğrenci İşleri Daire Başkanlığı'nı ziyaret etmeniz önerilir.

İkamet izni için ise Göç İdaresi Başkanlığı'na başvuruda bulunmanız gerekmektedir. İkamet izni belgenizi aldığınızda, bu belgeyi Uluslararası Öğrenci Ofisine teslim etmeniz-required. Ayrıca, ikamet adresinizi değiştirmeniz halinde, bu değişikliği iki iş günü içinde mahalli-resmî makamlarına bildirmekle yükümlü olduğunuz kaydedilmiştir. Ancak, ikamet izni için gerekli belgelerin tam listesi ilgili kaynaklarda bulunamadı. Göç İdaresi Başkanlığı'na başvuruda bulunmadan önce, gerekli belgeleri öğrenmek için ilgili kurumu ziyaret etmeniz önerilir.

Not: Uluslararasi ogrenci harc ucretleri ve odeme detaylari icin finans birimi (tuition_agent) ile iletisime gecmeniz onerilir.

Finans:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Finans: Kural
- Ogrenci Isleri: Kural

Kaynak Ozeti:
- Belge: uluslararası_öğrenci_kayıt_taahhüt_ve_evrak_teslim_formu.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: lisansüstü_eğitim_enstitüsü.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: idari_ve_mali_işler_birimi.txt
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs', 'student_affairs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] not ortalaması
  - [x] harç
  - [ ] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 4997.0 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
ÇAP programına başvurmak için öncelikle Senato tarafından ÇAP açılması uygun görülen birimlerin belirlediği koşulları sağlamak必要. Harç borcu olan öğrencilerin başvuruları hakkında specific bir bilgi bulunmuyor, ancak ÇAP'a başvuru, kabul ve kayıt koşulları arasında eğitim-öğretim yılı sonunda alınacak öğrenci sayılarını belirleme ve birim kuruluna sunma bulunmaktadır. ÇAP'tan geçici veya sürekli ayrılma ve ilişik kesilme hâlleri de bulunmaktadır, ancak bunlar başvuruya değil ÇAP'a kayıtlı olmakla ilgilidir. 

Harç borcunun nasıl ödeneceği về konkrét bir açıklama bulunmuyor. ÇAP başvuruları ile ilgili detaylar için Senato tarafından belirlenen ve birimlerde bulunan koşulları incelemeniz önerilir. 

Bununla birlikte, ÇAP başvuruları için;
- Senato tarafından belirlenen koşullara uygun olmak
- Birimlerin belirlediği koşullara uymak 
gereklidir.

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
- **Sure**: 3201.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Kayıt yenileme döneminde harç ücretini yatırdıktan sonra ders kaydı, öğrenci bilgi sistemi üzerinden yapılmalıdır. Danışman onayı, ders kaydının kesinleşmesi için zorunludur. Öğrenci, akademik takvimde belirtilen süre içinde ders kaydını yapmalıdır. Danışman tarafından onaylanan dersler kesinleşir, danışman tarafından listeden çıkartılan dersler için öğrenci yeniden değerlendirme yapabilir. 

Kayıt işlemleri sırasında, öğrencinin attention etmesi gereken hususlar şunlardır:
- Her dönem başında müfredat durum kontrolü,
- Akademik takvimde belirtilen süre içinde kaydın tamamlanması,
- Danışman onayı işleminin tamamlanması.

Öğrenci, ders kaydını yaptıktan sonra danışmanından onay bekleyecek, danışman onayını aldıktan sonra derslerin kesinleşmesini takip edecektir. Danışmanına ulaşması durumunda, bölüm başkanına veya Dekan/Müdürlüğe başvurarak danışman onayını tamamlaması gerekir. 

Bu konuda herhangi bir sorun veya ulaşamama durumunda, oidb@omu.edu.tr adresine bildirimde bulunulabilir.

Finans:
Ogrenim ucreti ogrenci turune ve birime gore degisiyor. Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
```

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [ ] bildiri
  - [x] harç
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4203.0 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Burslu öğrenciyseniz ve yatay geçiş yapmak istiyorsanız, bursunuzun devri veya kesilip kesilmeyeceği konusunda bilgi sahibi olmak için burs aldığınız kurumla iletişim kurmanız gerekmektedir. Bu konuyla ilgili olarak burs aldığınız kurumla iletişim kurup gerekli bilgiyi almanız önemlidir. 

Bursunuzun durumuna göre yeni üniversitede harç ödemeniz gerekebilir veya bursunuz devam edebilir. Öğrenci harç iadesi için de kendi adınıza açılmış hesaba ait 26 haneli IBAN numaranızı belirtir banka çıktı görüntüsü ile Öğrenci İşleri Daire Başkanlığı harç bürosuna başvurmanız gerekmektedir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

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
- **Sure**: 2391.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Akademik Programlar:
Soru: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

Yanıt: Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

Finans:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: tıp_fakültesi_tıp_doktorluğu_programı.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
- Belge: yonerge_cift_anadal_yandal.pdf
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 5320.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Devamsızlıktan kaldığınız bir dersin bütünleme sınavına giremezsiniz. Bir dersten devamsızlıktan kalan öğrenci o dersin bütünleme sınavına giremez. Dersi tekrar alabilirsiniz, ancak bunun için belirli bir tarih veya şart bulunmamaktadır. Bütünleme sınavına girme hakkını kazanıp da bu sınavlara maddi zorunluluktan dolayı katılamayan öğrenciler için ayrıca bir hüküm yoktur.

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3558.2 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Kayıt dondurma isteğinizin ilgili yönetim kurulunca kabul edilmesi durumunda öğrenim ücretini yatırmanıza gerek yoktur. Kayıt dondurma ile kayıt yaptırmamak arasında fark yoktur, her iki durumda da katkı payı veya öğrenim ücreti ödenmesi gereken bir durum söz konusudur ancak kayıt dondurma durumunda ödemeye gerek yoktur. 
Kayıt dondurduğunuz süre eğitim süresinden sayılmaz. 
Öğrenciler her öğretim yılında katkı payını veya öğrenim ücretini akademik takvimde belirlenen sürede ödemekle yükümlüdürler.

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
- **Key Facts**: 1/4
  - [ ] transkript
  - [x] Ek Madde
  - [ ] başvuru yapabilir
  - [ ] GANO
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 2757.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

Akademik Programlar:
Ek Madde-1 ile başka bir üniversiteye yatay geçiş için specific bir kural bulunmuyor. Ancak, önlisans diploma programlarının hazırlık sınıfına ilk yarıyılı ile son yarıyılına yatay geçiş yapılamayacak. 
Bu konuda elimdeki kaynaklarda, Ek Madde-1 ile yatay geçişe ilişkin net bir bilgi bulunamadı.

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
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 5086.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Kurum içi yatay geçiş, aynı üniversite içindeki farklı diploma programları arasında yapılan geçiştir. Kurumlar arası yatay geçiş ise farklı üniversiteler arasındaki geçişlerdir. Başvuru şartları ve değerlendirme kriterleri arasında farklar bulunmaktadır. 

Örneğin, disiplin cezası almış öğrencilerin yatay geçiş başvuruları kabul edilmez ve bu durumu belgelemeleri gerekir. Ayrıca, öğrenci kayıt dondurmuş ise yatay geçiş başvurusu sırasında bu durumu belgelendirmesi gerekir. 

Kurum içi yatay geçiş kontenjanları, ÖSYM Kılavuzunda öngörülen öğrenci kontenjanının yıllık % 15'ini geçmeyecek biçimde dönemlere bölünerek ilgili yönetim kurulunun önerisi ve Senato'nun kararı ile belirlenir.

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
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi2.pdf
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
- **Intent Analizi**: complexity=comparison, force_llm=False, is_personal=False, query_type=comparative
- **Sure**: 3289.8 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Ogrenci Isleri:
MADDE 5 - Bağıl Değerlendirme uygulama esasları üç farklı yöntemle belirlenir. 1) Bağıl Değerlendirmeye katılan öğrenci sayısı 10 ve altında ise; a) Bir dersi alan öğrencilerden bağıl değerlendirmeye katılan öğrenci sayısı 10 ve altında ise öğrenci otomasyon sistemi ham başarı puanını mutlak değerlendirme yaparak Tablo-1’e göre harf notuna dönüştürür. Tablo-1 Harf Mutlak Değerlendirme Sistemindeki Başarı Notu Anlamı Karşılığı Not Aralıklar 4.00 AA Pekiyi 90-100 3.50 BA Çok İyi 85-89 3.00 BB İyi 75-84 2.50 CB Orta 70-74 2.00 CC Yeterli 60-69 1.50 DC Başarısız 40-59 1.00 DD Başarısız 20-39 0 FF Başarısız 0-19 FD Devamsız b) Ek sınav, mazeret, muafiyet ve benzeri sınav sonuçlarının nota dönüştürülmesi Tablo- 1’e göre yapılır. 2)Bağıl Değerlendirmeye katılan öğrenci sayısı 11-29 arasında ise; a) Öğrencilerin ham başarı puanları ders ortalaması dikkate alınarak Tablo-2’ye göre nota dönüştürülür. Bu dönüştürmede aşağıdaki adımlar izlenir: I. Adım: Bağıl değerlendirmeye katılan öğrencilerin 100 üzerinden ham başarı puanlarının ortalaması hesaplanır. II.Adım: Bu öğrenciler en yüksek puandan en düşük puana doğru sıralanır. III. Adım: Hesaplanan ders ortalamasının Tablo-2’deki “Ders Ortalama Sınırları” sütununda hangi aralıkta olduğu belirlenir. IV.Adım: Harfli not oranları sütunu altında yer alan not için belirlenen yüzde oranlarına göre, her bir harfli nota kaç öğrencinin düştüğü belirlenir. AA notundan başlayarak sıralanan listede öğrencilere not verilir. V. Adım: Bir dersteki öğrenci sayısı ile harfli başarı notuna karşılık gelen yüzdeler sonucu elde edilen öğrenci sayılarının toplamının eşit olmaması durumunda öğrenci lehine davranılır. VI.Adım: Bir derste aynı başarı notuna farklı harfli not verilemez. VII. Adım: Bir harf notuna düşen öğrenci yüzdesi 0.5 ve üstü durumlarda bir üste öteleme yapılır. Örnek: AA notuna düşen öğrenci yüzdesi 13,5 ise bu durumda %14 alınır. PP.1.2.PRS. 0025, R1.1, Haziran 2022 Sayfa 2 / 5 Tablo-2 (AA,BA,BB,CB,CC geçer notu, DC
... (4712 karakter daha)
```

### Q15: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 3/3
  - [x] diploma eki
  - [x] transkript
  - [x] yerine geçmez
- **Intent Analizi**: complexity=simple, force_llm=False, is_personal=False, query_type=comparative
- **Sure**: 1217.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Diploma ekini transkript yerine kullanabilir miyim? Diploma eki transkript (not çizelgesi) veya diploma yerine geçmez. Diploma eki ile hangi kazanımları elde edebilirim? Yurtdışında daha okunabilir ve mukayese edilebilir bir diploma, akademik güzergâhının ve yurtiçinde ve yurtdışında edindiği yeti ve becerilerin tam bir tarifi, başarı ve yetilerinin nesnel ve âdil değerlendirmesi, geleceğe yönelik olarak yurtdışında iş ve eğitim imkânlarına daha rahat ulaşma olanağı, İş bulma olanaklarını artırma kazanımlarını elde debilirsiniz.

(Kaynak: sık_sorulan_sorular.txt)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] kayıt dondurma
  - [ ] sayılma
  - [ ] süre
  - [ ] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=True, query_type=comparative
- **Sure**: 1231.4 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Kural

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
```

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
- **Sure**: 3568.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatmak için aşağıdaki adımları takip edebilirsiniz:

1. Ders kayıtlarını, eğitim gördüğünüz birime ait akademik takvimde belirtilen süreler içerisinde yapmak zorundasınız. Akademik takvimlere Öğrenci İşleri Daire Başkanlığı WEB sayfasından ulaşabilirsiniz.
2. Ders kaydında üç önemli hususa dikkat etmeniz gerekir: her dönem başında müfredat durum kontrolü, akademik takvimde belirtilen süre içinde kaydın tamamlanması ve danışman onayı işlemleri.
3. Danışmanınız kayıt olmak istediğiniz derslerde değişiklik yapma hakkına sahiptir. Ondokuz Mayıs Üniversitesi Ön Lisans ve Lisans Eğitim Öğretim Yönetmeliği hükümleri kapsamında danışman bu hakkını kullanabilir.
4. Devam şartınız olmasa bile derslerin sınavlarına girebilmek için ders kaydı yapmanız gerekmektedir.
5. Danışmanınıza ulaşamaz ve ders kaydınızı onaylatamazsanız, bölüm başkanınıza, bölüm başkanına da ulaşamazsanız Dekan/Müdürünüze durumu bildirmek sureti ile akademik takvimde belirtilen sürede danışman onayını muhakkak yaptırınız. Hiçbir yetkiliye ulaşılamadığı takdirde oidb@omu.edu.tr adresine sistemle ilgili sorununuzu e-posta yolu ile iletebilirsiniz.

Bu adımları takip ederek, ilk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna tamamlayabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ders_yeterlilik_sınavı_uygulama_yönergesi.pdf
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
```

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/4
  - [x] itiraz
  - [ ] beş iş günü
  - [ ] dilekçe
  - [ ] bölüm başkanlığı
- **Sure**: 377.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
MADDE 8 - (1) Sınav sonuçlarına itiraz Ondokuz Mayıs Üniversitesi Ön Lisans ve Lisans Eğitim-Öğretim Yönetmeliğine uygun olarak yapılır. Tebligat adresi

(Kaynak: yonerge_ders_yeterlilik_sinavi_uygulama.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: yonerge_ders_yeterlilik_sinavi_uygulama.pdf
- Belge: yüzde_on_başarı_değerlendirme_yönergesi.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 1/6
  - [ ] ders
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [ ] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 1560.3 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Kural

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
```

### Q20: Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] 2. nüsha
  - [x] diploma
  - [ ] e-devlet
  - [ ] YÖKSİS
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 2125.8 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Bu konuda elimdeki kaynaklarda net bilgi bulunamadi.

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
- **Key Facts**: 2/5
  - [x] uzaktan
  - [ ] %20
  - [ ] %80
  - [x] %40
  - [ ] %60
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 3667.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Ogrenci Isleri:
Uzaktan eğitim yoluyla alınan derslerin sınav ve başarı değerlendirmesi, yüz yüze eğitim alanındaki derslerden farklı değildir. Özellikle MADDE 25 (1)'de belirtilen hükme göre sınavların yüz yüze ve yazılı olarak yapılması esastır ve uzaktan eğitim programlarındaki sınavlar da bu çerçevede değerlendirilir. Ancak, dersin özelliği nedeniyle sınavın sözlü, uygulamalı ya da yazılı/sözlü/uygulamalı olarak karma biçimde yapılmasına öğretim elemanının önerisi ile birim akademik kurulu karar verebilir. Buna ek olarak, MADDE 25 (5)'e göre uzaktan eğitim ön lisans, lisans tamamlama ve lisans öğrencilerinin dönem içi sınavlarının nasıl yapılacağına Senato tarafından karar verilir.

Akademik Programlar:
Uzaktan eğitim yoluyla alınan derslerin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı değildir. Her iki durumda da sınavlar, proje, ödev, öğrenci ürün dosyası, makale kritik etme, rapor hazırlama, rapor sunma gibi yöntemler kullanılarak yapılır. Ancak uzaktan eğitimde sınavlar çevrimiçi olarak da yapılabilir. Yüz yüze eğitimde olduğu gibi uzaktan verilen dersler için dönem içi değerlendirme, dersin özelliğine göre sorumlu öğretim elemanının belirleyeceği sınav, proje, ödev gibi yöntemlerden biri/birkaçı kullanılarak yapılır. Uzaktan eğitimde proje, ödev, öğrenci ürün dosyası, makale kritik etme, rapor hazırlama, rapor sunma gibi sürece yayılmış değerlendirmeler ile gözetimsiz yapılan ölçme değerlendirme etkinliklerinin genel başarıya etkisi %40'tan fazla olamaz.

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
- Belge: lisansüstü_eğitim_ve
... (74 karakter daha)
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3052.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sınavda kopya çekilmesinin cezası net olarak belirtilmemiştir. Ancak, sınav görevlilerinin kopya çekme girişiminde bulunan öğrenciler hakkında işlem yapma yetkisine sahip olduğu belirtilmiştir. Disiplin süreci, 2547 sayılı Yüksek Öğretim Kanununun 54. Maddesine göre yürütülmektedir. Ancak, disiplin sürecinin detayları hakkındaElimdeki kaynaklarda net bilgi bulunamadı.

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
- **Sure**: 2106.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Üniversiteyi bırakmak için gereken işlemler ve dikkat edilmesi gereken hususlar hakkında elimdeki kaynaklarda net bilgi bulunamadı.

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
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 0/4
  - [ ] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 5094.1 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Okulu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimi için Ögrenci Isleri Dairesi'nden yönetim kurulu kararı almanız gerekir. Important mazeretlerinizi veya eğitim-öğretimine katkıda bulunacak olanakların ortaya çıkması halinde bu karar alınabilir. Dönüşte ders seçimi için ilgili birimin yönetim kurulu kararı ile en fazla iki dönem için izin verilebilir. Öğrenci internet sayfasından ders kataloğuna ulaşarak derslerin seçimi yapılır.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: uzaktan_karma_eğitim_yönergesi.pdf
- Belge: avrupa_birliği_eğitim_ve_gençlik_programları_hayat_boyu_öğrenme_erasmus.pdf
- Belge: diş_hekimliği_fakültesı_lisans_eğitim_öğretim_yönergesi.pdf
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
- **Intent Analizi**: complexity=simple, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 2340.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Sorunuzda hocanızın ders notlarınızı sisteme girmemesi durumunda ne yapabileceğiniz sorulmaktadır. Elimdeki kaynaklarda bu konuya ilişkin açık bir bilgi bulunmamaktadır. 

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
```
