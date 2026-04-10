# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 17:28:53
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 3

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 33.3% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 83.3% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 4014.3 ms |
| Medyan Sure | 4431.7 ms |
| Intent Analizi Aktif | 3/3 |
| Force LLM Sentez | 3/3 |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | YANLIS | OK | 3/3 | 4640.6 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 4431.7 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | OK | 4/5 | 2970.7 | - |

## Soru Detaylari

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'finance', 'student_affairs'] (beklenen: ['finance', 'academic_programs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] ücret
  - [x] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4640.6 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Ogrenci Isleri:
Soru cevabı:

İlk olarak kayıt yaptırırken öğrenim ücretini nerede yatırmalıyım sorusuna cevap vereyim. Öğrenim ücreti Ondokuz Mayıs Üniversitesi (OMU) ÖİDB Katkı Payı ve Öğrenim Ücreti Ofisi'nde yatırılmalıdır. Bu konuda elimdeki kaynaklardaki ilgili görev adının "ÖİDB Katkı Payı ve Öğrenim Ücreti Ofisi Personeli" olması ve görev tanımının "öğrencilerin kayıt yaptırdıkları program düzeyinde bilgi yönetim sisteminden borçlandırma işlemini yapmak ve ödemelerini takip etmek" olduğu göz önüne alındığında, öğrenim ücretinin bu ofise yatırılması gerektiği söylenebilir. Ancak, daha net bir cevap için ilgili ofiste yapılacak bir işlem gerektirmektedir. Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

İkamet izni için hangi belgeleri hazırlamalıyım sorusuna cevap veriyorum. İkamet izni için gerekli belgeler arasında öğrenci belgesi ve pasaport bulunmalıdır. Bu konuda elimdeki kaynaklardaki ilgili görev adının "Her eğitim öğretim döneminde yabancı uyruklu öğrencilerin ders kayıtlanma durumunu göç idaresine göndermek" olduğu göz önüne alındığında, ikamet izni için öğrenci belgesi ile pasaport gerekli görülmektedir. Ancak, daha net bir cevap için ilgili işlem gerektirmektedir. Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

Gerekli diğer bilgilere ulaşmak için Öğrenci İşleri'ne yönlendirilebilrz.

Akademik Programlar:
Ön kayıt yaptırırken yurt dışından öğrenci olarak öğrenim ücretini yatırmak durumundasınız. Bu ücreti Üniversite'nin web sitesi aracılığıyla ödemeniz gerekmektedir.

İkamet izni için ise şu belgeleri hazırlamanız gerekecektir:

- Geçerli pasaport,
- Öğrenim hakkı için verilmiş diplomatik veya konsolosluk belgesi,
- Ön kayıt yapıldıktan sonra, ÖİB (Öğrenci İşleri Daire Başkanlığı) tarafından verilecek olan ikamet izni belgesi.

Eğer üniversite tarafından genel akademik takvimle belirlenen ders kayıtlanma tarihlerinden önce derslerini kaydolmak isteyen öğrenci ise, öğrenci işleri bölümüne şahsen başvurmalıdır.

Ön kayıt yaptıran öğrencile
... (1185 karakter daha)
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] not ortalaması
  - [x] harç
  - [ ] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=factual
- **Sure**: 4431.7 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
ÇAP Programına Başvuru Şartları ve Harç Borcu Ödenmesi

ÇAP (Çift Anadal) programına başvurmak istediğinizde, bazı ön koşullarını karşılamalısınız. Bunlar:

- Ana dal lisans programınıza devam ederken, başvurduğunuz yarı yıla kadar ana dal lisans programında yer alan tüm dersleri almış ve başarmış olmanız,
- Başvurduğunuz yarı yıla kadar ana dal not ortalamasının 4.00 üzerinden en az 3.00 olması,
- Ana dal diploma programının ilgili sınıfında başarı sıralaması itibarı ile en az ilk %20'sinde bulunmanız.

Harç borcunuzun nasıl ödeneceğini bilmiyorsanız, bu durumuna bağlı olarak bazı bilgilerimiz var. Resmi internet sitesinde veya öğrenci hizmet birimlerinden bilgi almanızı öneriyoruz. 
Ayrıca OMU harç borçlarınız için resmi internet sitesini ziyaret ederek veya öğrenci hizmet birimlerinden bilgi alabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: yonerge_cift_anadal_yandal.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [ ] azami
  - [x] ek
  - [x] süre
  - [x] katkı payı
  - [x] öde
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 2970.7 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Akademik Programlar:
Sormak istediğiniz soruyu cevaplama imkanlarım var. 

Size göre bu durum, ek süre hakkını kazanmış olmakla birlikte, bu süresi kapsamında katkı payı ödemekten muaf olmayacaksniz.

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
- Belge: öğretim_üyesi_yetiştirme_programı_yönergesi.pdf
- Belge: uluslararası_işbirlikleri_protokoller_kapsamındaki_öğrenci_ve_personel_değişim.pdf
- Belge: tıp_fakültesi_tıp_doktorluğu_programı.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
```
