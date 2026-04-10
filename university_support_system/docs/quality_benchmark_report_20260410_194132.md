# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 19:41:32
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 3

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 66.7% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 83.3% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 7215.1 ms |
| Medyan Sure | 5609.8 ms |
| Intent Analizi Aktif | 3/3 |
| Force LLM Sentez | 3/3 |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | YANLIS | OK | 3/3 | 10754.2 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | OK | 3/4 | 5281.4 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | OK | OK | 4/5 | 5609.8 | - |

## Soru Detaylari

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['academic_programs', 'student_affairs'] (beklenen: ['academic_programs', 'finance', 'student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/3
  - [x] ücret
  - [x] ikamet
  - [x] belge
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 10754.2 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Ogrenci Isleri:
Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretini nereye yatırmalısınız ve ikamet izni için hangi belgeleri hazırlamalısınız?

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı. Lütfen Öğrenci İşleri'ne başvurunuz.

Akademik Programlar:
Sen Ondokuz Mayis Universitesi (OMU) için uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

Bu konuya ilişkin bilgi, Ondokuz Mayis Universitesi'nin uluslararası öğrenci kılavuzunda yer almaktadır. Uluslararası öğrencilerin kayıt işlemleri iki farklı yöntemle yapılır: önceden elektronik ortamda sunulan geçici kaydı takiben, istenilen belgelerin Öğrenci İşleri Daire Başkanlığı’na şahsen teslim edilmesiyle kesin kayda dönüşecek şekilde; veya elektronik ortamda kesin kayıt yaparak. 

Öne kayıt yapılan öğrencilere, uluslararası öğrenim ücretini ödemeleri veya OMÜ TÜRKÇE ücretini ödemeleri koşuluyla ön kayıt hakkı verilir. Ancak, özel yetenek sınavı ile öğrenci alınacak programlara yerleşen öğrencilere ön kayıt hakkı verilmez.

Kesin kayıt için, öğrencinin şahsen Öğrenci İşleri Daire Başkanlığına başvurarak belge teslim etmeleri gerekir. Ayrıca, öğrencilerin, Üniversite'ye yaptırmış oldukları geçici kayıtlarını kesin kayda dönüştürme aşamasında Türkiye'de yasal kalış süresi içerisinde olduklarını belgeler ile ibraz etmeleri gereklidir. 

Bu konuya ilişkin daha fazla bilgi için, Uluslararası Öğrenci Ön Kayıt: Öğrencilere kesin kayıt hakkı vermez (Kaynak 1: uluslararası_öğrenci.pdf); veya uluslararası öğrenci alım kılavuzunda (Kaynak 2: uluslararası_öğrenci_yönergesi.pdf) yer alan ilgili madde ve yönetmeliklere bakabilirsiniz.

Bu konuda elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Ogrenci I
... (225 karakter daha)
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [ ] not ortalaması
  - [x] harç
  - [x] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 5281.4 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
ÇAP programına başvurmak istediğinizde harç borcu bulunan durumda başvurabilir misiniz?

Evet, ÇAP programına başvurabilirsiniz. Ancak borcunuzu ödemelisiniz. Bu işlemini yapabilmek için, bankada hesabınız olması kaydıyla, ÖİDB'nin internet sayfasında yer alan "Öğrenci Kart Bilgisi" sayfasından ödemenizi gerçekleştirebilirsiniz. ÇAP programına başvurmak için, doğruöğretim ücretini ödeyin.

Ögrenci Turu ve Birime Göre Ödemenin Yapılması:

- Öğrenci Türü: Türk öğrenci misiniz?
  - Evinizde oturuyorsanız: "Türk Öğrenci Ödemesi" yapılmaktadır. 
  Fiyat ve Ödeme Şartları:
  - Başvurulan programa (ÇAP) göre ödeme tutarları değişebilir.
  - Fakülte veya Bölüm bilginiz de önemlidir.

Ayrıca, harç borcunun önündeki herhangi bir problemi ortadan kaldırmanız da mümkün. ÖİDB'nin internet sayfasında yer alan "Öğrenci Kart Bilgisi" sayfasından işleminizi gerçekleştirebilirsiniz.

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
- **Departman**: ['finance', 'student_affairs', 'academic_programs'] (beklenen: ['academic_programs', 'student_affairs', 'finance']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 4/5
  - [ ] azami
  - [x] ek
  - [x] süre
  - [x] katkı payı
  - [x] öde
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 5609.8 ms
- **Kaynak Sayisi**: 13

**Yanit:**
```
Ogrenci Isleri:
Sorunuza göre, 4. sınıf öğrencisi olmanız ve program süresini 1 yıl aştığınız durumunda, ilk olarak ÖSYS (Üniversite Burs ve Yardımlaşma Kurumu) kaynaklarını incelemek gereklidir. Bu kaynaktan sonra, Ondokuz Mayıs Üniversitesinin belirlemiş olduğu kurallara ve yönetmeliklerine bakılacaktır. 

Ayrıca, konuya göre kaynak olarak sunulan dokümanda, 'MADDE 13- (1)...' başlığını takip eden metin de yardımcı olacaktır.

Akademik Programlar:
Siz, Tıp Fakültesi'nin 6 yıllık normal eğitim-öğretim süresini aştınız. Ek süre hakkınızın olup olmadığını ve bu sürede katkı payı ödemenizi soruyorsunuz.

Belgelerimize göre, Tıp Fakültesi'nde normal eğitim-öğretim süresi 6 yıldır. Siz 4. sınıfa gelmişsiniz, bu nedenle 2 sınıfa daha devam etmeniz gerekiyor. Ek süre hakkınız vardır, ancak bu ek süre boyunca katkı payı ödemeniz gerekecek.

Öğrencilerine en fazla bir yıl süre ile izin verilebilir, ancak bu süre eğitim süresinden sayılmaz. Ancak, sizin durumda olduğu gibi katkı payı ödemeniz gerekecek. Bu konudaki bilgiler kaynaklarda yer almaktadır.

Yanıt: 
Tıp Fakültesi'nde normal eğitim-öğretim süresi 6 yıl, siz de 4. sınıfa gelmişsiniz. Ek süre hakkınız vardır, ancak bu ek süre boyunca katkı payı ödemeniz gerekecektir.

Finans:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: 2025_2026_yılı_türk_öğrenci_katkı_payı_öğrenim_ücretleri.pdf
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönet
... (265 karakter daha)
```
