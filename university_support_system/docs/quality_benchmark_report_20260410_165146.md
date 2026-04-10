# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 16:51:46
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 3

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 33.3% |
| Uretim Modu Dogrulugu | 66.7% |
| Anahtar Bilgi Kapsami | 75.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3871.2 ms |
| Medyan Sure | 4096.9 ms |
| Intent Analizi Aktif | 3/3 |
| Force LLM Sentez | 3/3 |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | YANLIS | OK | 3/3 | 3328.7 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | YANLIS | YANLIS (rag) | 3/4 | 4187.9 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 3/5 | 4096.9 | - |

## Soru Detaylari

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['finance', 'academic_programs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] ücret
  - [x] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3328.7 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Soru:
Kısa ve net olarak, internacional öğrenci kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ikamet izni için hangi belgeleri hazırlamalıyım?

Finans:
Ogrenim ucreti ogrenci turune ve birime gore degisiyor. Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - YANLIS
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 3/4
  - [ ] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 4187.9 ms
- **Kaynak Sayisi**: 7

**Yanit:**
```
ÇAP programa başvurmak isteyen bir öğrenci tarafından gelen soru ve departman ara yanıtlarını inceleyerek birleşik bir cevap oluşturulur:

Öncelikle, Önlisans ve Lisans Yatay Geçiş Yönergelerine göre, ÇAP programına başvurmak isteyen öğrencilerden bir şartı taşıması gerekir: akademik takvimde belirtilen süreler içinde her eğitim-öğretim döneminde/yılında, ilgili mevzuatta belirlenen öğrenci katkı payını/öğrenim ücretini ödemeleri gerekir. 

Öğrenci, harç borcu bulunmadan ÇAP başvuru şartlarını yerine getirmelidir. Ögrenci Isleri departmanında verilen bilgiye göre öğrencinin harç borcu olduğunu öğrenirse ve bu borcu ödemeyeceğini belirtirse, ders kaydı yaptıramaz ve öğrencilik haklarından yararlanamaz; ancak bu dönemler/yıllar öğrenim süresinden sayılır.

Ama ÇAP başvuru için diğer bir seçenek öğrencinin, ilgili döneme ilişkin olarak ilgili mevzuat ile belirlenen katkı payını/öğrenim ücretini ödeyerek öğrenimlerine devam etmek için kayıt yaptırıp, öğrenime devam etmesi. Bu sayede öğrenci harç borcunu ödeyip, ÇAP'a başvurabilir.

Akademik Programlar departmanının verdiği bilgiye göre, ÇAP'tan geçici veya sürekli ayrılma ve ilişik kesilme hâlleri arasında öğrencinin ÇAP başvurusunu yaptıktan sonra önceki programını bırakması ve yeni bir programa geçmesi de bulunmakta. Öyleyse, ÇAP'a öğrenci başvurmak istiyor ve harç borcunun olduğunu öğrenirse, harç borcunu ödemeyeceğini belirtmek yerine bir başka seçenek olarak öğrenci önceki programını bırakıp, ÇAP programa başvurabilir.

Özetle, harç borcu olan bir öğrenci, ÇAP programına başvurmak için iki yol seçebilir: 

1.  Önceki programını bırakacak ve harç borcunu ödeyerek yeni bir programa kaydolacağı için ÇAP'ya yeni bir başvuru yapacaktır. 

2.  İlgili döneme ilişkin katkı payını/öğrenim ücretini ödeyerek, öğrenimine devam etmek ve ÇAP programına başvurmak için öğrencilik kaydını yenileyecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini payla
... (450 karakter daha)
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [x] azami
  - [x] ek
  - [x] süre
  - [ ] katkı payı
  - [ ] öde
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=factual
- **Sure**: 4096.9 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Ogrenci Isleri:
Sayın öğrenci, öğreniminizi tamamlamınız için tanınan azami süreniz 7 yıldır. Bu süreyi aşan öğrenciler ders, uygulama, staj ve sınavlara katılabilirler; ancak öğrencilik haklarından yararlanamazlar. Ek süre hakları ile ilgili ayrıntılı bilgileri aldığım kaynaklarından öğreniyorum.

Ancak, ek sürece hak kazanıp kazanamayacağınızı öğrenmek istediğimizi belirttiğiniz için, bu konuda elimdeki kaynaklarda net bilgi bulunamadı. Bu nedenle, ilgili bölümün yöneticilerine danışılarak daha doğru bilgi verilebilir.

Finans:
Ogrenim ucreti ogrenci turune ve birime gore degisiyor. Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: yüzde_on_başarı_değerlendirme_yönergesi.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
```
