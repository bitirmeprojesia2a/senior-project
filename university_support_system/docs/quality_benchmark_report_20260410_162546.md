# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 16:25:46
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 3

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 33.3% |
| Anahtar Bilgi Kapsami | 57.1% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 7927.4 ms |
| Medyan Sure | 6358.7 ms |
| Intent Analizi Aktif | 2/3 |
| Force LLM Sentez | 2/3 |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | OK | YANLIS (rag) | 2/5 | 2043.5 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | OK | OK | 3/5 | 6358.7 | - |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | OK | YANLIS (rag) | 3/4 | 15379.9 | - |

## Soru Detaylari

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'student_affairs'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/5
  - [ ] burs
  - [ ] kesilme
  - [x] kurum
  - [x] bildiri
  - [ ] harç
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 2043.5 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
Yatay gecis sureci icin en ilgili kaynakta su bilgi yer aliyor:
MADDE 6 - (1) Üniversitemize yatay geçişler, diğer yükseköğretim kurumlarındaki aynı düzeydeki eşdeğer diploma programlarından yapılır. PP.1.2.PRS.0048, R0, Temmuz Sayfa 2 / 5 2025 (2) Kurumlar arası yatay geçişlerde öğrencinin kayıtlı olduğu programda genel not ortalamasının 4 lük sistem kullanan üniversiteler için en az 2.80, 100 lük sistem kullanan üniversiteler için en az 72 olması gerekir. Transkriptinde iki not sistemi de var ise 100 lük sistemdeki notu kullanılır. (3) Üniversitemizdeki ön lisans ve lisans programları için belirlenen yatay geçiş kontenjanları ile başvuru ve değerlendirme takvimi, Yükseköğretim Kurulu ve Üniversitemiz internet sayfasında ilan edilir. (4) Ön lisans programlarında yatay geçiş kontenjanları ile başvuru ve değerlendirme takvimi ikinci yarıyıl için Ocak ayı, üçüncü yarıyıl için ise Temmuz ayında ilan edilir. (5) Lisans programlarından dört yıllık eğitim verenlerde ikinci ve üçüncü sınıflar için; beş yıllık eğitim verenlerde ikinci, üçüncü ve dördüncü sınıflar için; altı yıllık eğitim verenlerde ikinci, üçüncü, dördüncü ve beşinci sınıflar için yatay geçiş kontenjanları ile başvuru ve değerlendirme takvimi Temmuz ayında ilan edilir. (6) Her yıl düzenli olarak ikinci, üçüncü, dördüncü ve beşinci sınıflar için ÖSYM giriş genel kontenjanı 50 ve 50 den az olan programlarda iki, 51 ve 100 arası olan programlarda üç, 101 ve üzerinde olan programlarda ise dört kurumlar arası yatay geçiş kontenjanı Yükseköğretim Kurulu tarafından belirlenir. Bununla birlikte Üniversitemizdeki ilgili birim kurulları, geçişin yapılacağı programın giriş yılındaki kontenjanı ile yatay geçiş kontenjanı belirlenen yarıyıla kadar programdan ilişiği kesilen veya ayrılan öğrenci sayıları ile bu yarıyıl içinde yatay geçiş yoluyla gelmiş olan öğrenci sayıları arasındaki farkı aşmayacak biçimde ilave kontenjan belirleyebilirler. İlave kontenjan belirlenmesi hâlinde bu kontenjanlar en geç Haz
... (1468 karakter daha)
```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/5
  - [x] kurum içi
  - [x] kurumlar arası
  - [ ] Ek Madde
  - [x] GANO
  - [ ] YKS
- **Intent Analizi**: complexity=comparison, force_llm=True, is_personal=False, query_type=comparative
- **Sure**: 6358.7 ms
- **Kaynak Sayisi**: 4

**Yanit:**
```
Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farkları aşağıdaki gibidir:

1. Başvuru Şartları: Kurum içi yatay geçiş için, adayların üniversitenin ilgili programında genel not ortalamasının 4 lük sistem kullanan üniversiteler için en az 2.80, 100 lük sistem kullanan üniversiteler için en az 72 olması gerekir. (Kaynak 2: yonerge_onlisans_lisans_yatay_gecis.pdf)
2. Yabancı Dil Bilgi: Kurum içi yatay geçiş için, adayların yabancı dil bilgi düzeyi dikkate alınmaz. (Kaynak 2: yonerge_onlisans_lisans_yatay_gecis.pdf)
3. Kontenjanlar: Kurumlar arası yatay geçiş için, öğrencilerin yurt dışında öğrenim gördüğü yükseköğretim kurumunun ve eğitimin yapıldığı programın ön lisans veya lisans olduğu dikkate alınır. (Kaynak 1: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf)
4. Başvuru ve İlan: Kurumlar arası yatay geçiş için, yükseköğretim kurumları arasındaki yatay geçiş kontenjanları Yükseköğretim Kurulu tarafından belirlenir. (Kaynak 1: ön_lisans_ve_lisans_yatay_geçiş_yönergesi.pdf)

Başvuru şartı ve değerlendirme kriterleri arasında aşağıdaki farklılıklar bulunur:

1. Başvuru Süresi: Kurum içi yatay geçiş için, başvuru ve değerlendirme takvimi ilgiliprogram için Ocak ayı veya Temmuz ayında ilan edilir. (Kaynak 2: yonerge_onlisans_lisans_yatay_gecis.pdf)
2. Değerlendirme Puanı: Kurum içi yatay geçiş için, değerlendirmede adayın başvuru yaptığı programın puan türünde almış olduğu ÖSYM puanı ve 100 lük sistem GANO’su dikkate alınır. (Kaynak 2: yonerge_onlisans_lisans_yatay_gecis.pdf)

Yabancı dil bilgi düzeyi, yurt dışı yatay geçiş kontenjanı ve yabancı dil bilgi düzeyi için elimdeki kaynaklarda net bilgi bulunamadı.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RA
... (182 karakter daha)
```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 3/4
  - [x] kayıt dondurma
  - [ ] sayılma
  - [x] süre
  - [x] hak
- **Sure**: 15379.9 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Eldeki en ilgili kaynakta su bilgi yer aliyor:
MADDE 31- (1) Öğrencilerin belgelendirecekleri önemli mazeretlerinin veya eğitimöğretimlerine katkıda bulunacak Üniversite dışı burs, staj, araştırma ve benzeri imkânların ortaya çıkması hâlinde, ilgili birimin yönetim kurulu kararı ile bir defada en fazla iki dönem/bir yıl olmak üzere, öğrenim süresi boyunca en fazla dört dönem/iki yıl kaydı dondurulabilir. Bu şekilde kayıt donduran öğrenci, öğrenimine devam edemez ve kayıt dondurduğu döneme/yıla ait sınavlara giremez. Kayıt dondurma süresinin bitiminde öğrenci; ayrıldığı dönemin/yılın başından başlamak koşuluyla, öğrenimine kaldığı yerden devam eder. Kayıt dondurulan dönem/dönemler, süre hesabında dikkate alınmaz. (2) Öğrenimini uzun süre engelleyecek önemli bir hastalık veya ilgili yönetim kurulunca kabul edilen haklı ve geçerli bir nedenle ve belgelendirilmek kaydıyla verilen izin, 8 inci maddede yer alan süreye eklenir. Kayıt dondurma süresinin bitiminde öğrenci; ayrıldığı dönemin/yılın başından başlamak koşuluyla, öğrenimine kaldığı yerden devam eder. (3) Haklı ve geçerli mazeretler şunlardır: a) Öğrencilerin sağlık kuruluşlarından alacakları ve öğrenimlerine en az bir dönem devam etmeleri yönünde sağlık engeli bulunduğunu belirten heyet raporuyla belgelendirilmiş bulunan sağlıkla ilgili mazeretleri. b) İlçelerde kaymakamlıklar, illerde valilikler tarafından verilecek bir belge ile belgelenmiş olması koşuluyla; öğrencinin öğrenimini en az bir dönem olumsuz etkileyecek düzeydeki tabii afetler veya maddi imkânsızlıklar. c) Belgelendirilmek şartıyla, birinci derecede akrabalarının ölümü veya ağır hastalığı gibi durumlarda bakacak başka bir kimsenin bulunmaması. ç) 18/8/2012 tarihli ve 28388 sayılı Resmî Gazete’de yayımlanan Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği hükümlerine göre; azami süreyi aşmamak kaydıyla öğrencinin öğrencilik sıfatını kaldırmayan veya ihracını gerektirmeyen mahkûmiyet veya tutukluluk hâlleri. d) Öğrencinin tecil hakkını kaybetmesi 
... (625 karakter daha)
```
