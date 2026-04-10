# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 16:23:18
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 6

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 66.7% |
| Uretim Modu Dogrulugu | 16.7% |
| Anahtar Bilgi Kapsami | 36.7% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 6502.4 ms |
| Medyan Sure | 6894.4 ms |
| Intent Analizi Aktif | 5/6 |
| Force LLM Sentez | 5/6 |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | YANLIS (rag) | 3/5 | 1664.8 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | YANLIS (kural) | 1/5 | 1258.4 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | YANLIS | YANLIS (rag) | 2/5 | 7524.7 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | OK | 3/4 | 6264.1 | - |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | OK | YANLIS (rag) | 1/5 | 13600.1 | - |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | YANLIS (rag) | 1/6 | 8702.0 | - |

## Soru Detaylari

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 3/5
  - [x] burs
  - [x] kesilme
  - [x] kurum
  - [ ] bildiri
  - [ ] harç
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 1664.8 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Yatay gecis sureci icin en ilgili kaynakta su bilgi yer aliyor:
Yatay geçiş yaparsam bursumu devredebilir miyim, bursum kesilir mi? Bursunuzun devri veya kesilip kesilmeyeceği konusunda bilgiye ulaşmak için burs aldığınız kurumla iletişim kurmanız gerekmektedir. Başka bir üniversiteye geçiş yapmak istiyorum. Gerekli belgeleri nereden temin edebilirim? Üniversitemizden başka bir üniversiteye geçiş yapmak isteyen öğrenciler, istenen belgeleri E-Devlet üzerinden, UBYS öğrenci bilgi ekranından veya öğrenim gördükleri fakülte/yüksekokuldan temin edebilirle Yatay geçişle yabancı uyruklu öğrenci alıyor musunuz? Kontenjan tablosunda yabancı uyruklu öğrenci kontenjanı bulunan programlara yatay geçiş başvurusu yapabilirsiniz. Yurt dışında öğrenim görüyorum. Yatay geçiş yapabilir miyim? Yurt dışı öğrenci kontenjanı olduğu belirtilen programlara yatay geçiş başvurusu yapabilirsiniz.

(Kaynak: sık_sorulan_sorular.txt)

Finans:
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Finans: Kural
- Ogrenci Isleri: RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['finance'] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: kural (beklenen: llm) - YANLIS
- **Key Facts**: 1/5
  - [ ] azami
  - [x] ek
  - [ ] süre
  - [ ] katkı payı
  - [ ] öde
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 1258.4 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Ogrenim ucreti ogrenci turune ve birime gore degisiyor. Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin.

Uretim Turu:
- Kural
```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 7524.7 ms
- **Kaynak Sayisi**: 8

**Yanit:**
```
Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar, başvuru şartları ve değerlendirme kriterleri aşağıdaki gibidir:

Kurum İçi Yatay Geçişler

Kurum içi yatay geçişler, Üniversite içi programa geçmek amacıyla yapılır. Başvurular, Akademik Takvim çerçevesinde yapılır. Yerinizin en yakın öğrenci işleri birimi ile iletişime geçmek yeterlidir.

Kurumlar Arası Yatay Geçişler

Kurumlar arası yatay geçişler, yurt içi veya yurt dışı yükseköğretim kurumlarından Üniversite'ye yapılır. Başvuru süreci daha karmaşık olabilir. Aşağıdaki adımları izleyin:

1. Başvuru Şartları: Başvurulara katılabilmek için en az iki akademik yıl öğrenim gördüğünüz programın taban puanına sahip olmanız gerekmektedir.
2. Başvuru Süresi: Yurt dışı yatay geçiş kontenjanları Yükseköğretim Kurulu'na en geç Haziran ayının otuzuncu günü mesai saati bitimine kadar bildirilir.
3. Başvuru Formu: Başvuru formunu, öğrenci işleri biriminin internet sayfasından indirerek doldurmanız gereklidir.
4. Belgeler: Öğreniminizle ilgili tüm belgeleri öğrenci işleri birime teslim etmeniz gerekir.
5. Değerlendirme: Başvuruları değerlendirmek için, Akademik Programlar birimine başvurun.
6. Kabul: Kabul edilen adaylar, Akademik Programlar birimi tarafından bilgi verilecektir.

Ayrıca

- Yurt dışı yatay geçiş kontenjanları, her bir program için kurumlar arası yatay geçiş kontenjanının yarısını aşmayacak şekilde belirlenir.
- Yurt dışı yükseköğretim kurumları kontenjanları, Senato tarafından belirlenir.
- Yurt dışı yatay geçiş başvuruları, yurt dışı yatay geçiş kontenjanı kapsamı dışında değerlendirilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Akademik Programlar: RAG

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf
- Belge: yonerge_onlisans_lisans_yatay_gecis.pdf
- Belge: ön_lisans_ve_lisans_yatay_geçiş_yönerg
... (142 karakter daha)
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [x] hak
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 6264.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Kayıt dondurma ile kayıt yaptırmamak arasındaki farklar ve öğrenci haklarının nasıl etkilenacağı hakkında bilgi için, Ondokuz Mayis Universitesi (OMU) öğrenci işleri biriminden yararlanabilirsiniz.

Kayıt dondurma, öğrenime katkıda bulunacak önemli mazeretler veya eğitim-öğretimine katkıda bulunacak Üniversite dışı burs, staj, araştırma ve benzeri imkânların ortaya çıkması hâlinde gerçekleşebilir. Böyle bir durumda, öğrenci öğrenimine devam edemez ve kayıt dondurduğu döneme/yıla ait sınavlara giremez. Kayıt dondurulan süreler, öğrenim süresi hesabında dikkate alınmaz. Kayıt dondurma süresinin bitiminde öğrenci, ayrıldığı dönemin/yılın başından başlamak koşuluyla, öğrenimine kaldığı yerden devam edebilir.

Ayrıca bu konuda kaynaklarda net bilgi bulunmamış, başka bir ifadeyi kullanmak gerekirse "Bu konuda elimdeki kaynaklarda net bilgi bulunamadı".

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: sık_sorulan_sorular.txt
```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/5
  - [ ] UBYS
  - [ ] ders seçimi
  - [ ] danışman
  - [x] onay
  - [ ] yoklama
- **Sure**: 13600.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
Öğrencinin kayıt olmak istediği derste değişiklik yaptığımda öğrenciye bilgi vermek zorunda mıyım? Evet. Öğrenci ders kaydının kesin kayda dönüştüğünü görüp, dersleri tek tek kontrol etmeyebilir. Bu durumda ise sizin tarafınızdan değiştirilmiş dersi fark etmeme sonucunda, seçmemiş olduğu derse devam etme gibi olumsuz durumlar meydana gelmektedir. O nedenle ders değişikliği ile ilgili olarak öğrenci ile bilgi paylaşılması önemlidir. Öğrenci tarafından onaya gönderilen ve tarafımca onayı gerçekleştirilen ders kaydının, doğru olup olmadığını öğrenci ile birlikte ne zaman kontrol edebilirim? Akademik takvimde tanımlanan ekle-sil haftasında kontrol edebilir, hata varsa düzeltme yoluna gidebilirsiniz. Kesin kayda dönüştürdüğüm fakat değişiklik yapmak istediğim kaydı nasıl açtırabilirim? Biriminizde görevli, yetkilendirilmiş personellere ulaşarak kesin kaydı açtırabileceksiniz.

(Kaynak: sık_sorulan_sorular.txt)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ders_yeterlik_muafiyet_ve_intibak_yönergesi.pdf
```

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 1/6
  - [x] ders
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [ ] ilişik kesme
  - [ ] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 8702.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
MADDE 32- (1) Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre yükseköğretim kurumlarından çıkarma cezası almış olanlar ve kendi istekleri ile kaydını sildiren öğrencilerin Üniversite ile ilişiği kesilir. (2) Dört yıl üst üste olmak kaydıyla, katkı payı ve öğrenim ücreti ödemeyenlerle kayıt yenilememiş durumda olan lisans öğrencilerinin; ilgili birimlerin teklifi ve Senato kararı ile YÖK’ün onaylaması durumunda, Üniversite ile ilişiği kesilir. (3) 8 inci maddenin üçüncü ve dördüncü fıkraları kapsamındaki öğrencilerden başarısız oldukları ders sayısını bire indiremeyenlerin Üniversite ile ilişiği kesilir. (4) Yazılı isteği üzerine kaydını sildiren öğrenci; ÖSYM tarafından yeniden yerleştirilmediği veya Üniversite tarafından yapılan ölçme ve değerlendirme sonucunda kayıt hakkı kazanmadığı sürece, Üniversiteye tekrar kaydolamaz. YEDİNCİ BÖLÜM Çeşitli ve Son Hükümler Tebligat ve adres bildirme

(Kaynak: ön_lisans_ve_lisans.pdf)

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
- Belge: 2025_2026_ek_madde_1_güz_yarıyılı_kayıt_için_gerekli_belgeler.pdf
```
