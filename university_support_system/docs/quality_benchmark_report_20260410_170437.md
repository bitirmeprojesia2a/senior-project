# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 17:04:37
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 3

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 33.3% |
| Uretim Modu Dogrulugu | 66.7% |
| Anahtar Bilgi Kapsami | 75.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3198.4 ms |
| Medyan Sure | 3468.4 ms |
| Intent Analizi Aktif | 3/3 |
| Force LLM Sentez | 3/3 |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | YANLIS | OK | 3/3 | 4420.2 | - |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | OK | YANLIS (rag) | 2/4 | 1706.7 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | OK | 4/5 | 3468.4 | - |

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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4420.2 ms
- **Kaynak Sayisi**: 14

**Yanit:**
```
Ogrenci Isleri:
Soru:
Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

Cevap:
Soruyla ilgili direkt bilgi bulunamadığından, öğrenci işleri birimi ile iletişime geçilmesi tavsiye edilir.

Akademik Programlar:
Soru:
Uluslararası öğrenci olarak kayıt yaptırarken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

Cevap:
İlgili belgeleri sunamayan, Türkiye'de yasal kalış hakkına sahip olmayan veya yasal kalış süresi ihlali içerisinde bulunan öğrencilerin geçici kaydı yapılmış olsa dahi kesin kayıtları yapılmaz. Öncelikle, uluslararası öğrenci olarak kayıt yaptırmak için öğrenim ücretini Öndokuz Mayis Üniversitesi'nin (OMU) ilgili web sayfasında bulunan ve Uluslararası Öğrenci Alım Kılavuzunda yer alan hesabına yatırmanız gerekir.

İkamet izni için hazırlamanız gereken belgeleri belirlemek için OMU'nun Uluslararası Öğrenci Ön Kayıt ve kayıt işlemlerinin detaylarını incelemelisiniz. İlgili belgeleri sunamayan öğrencilerin kaydı yapılmayacaktır.

Bu konudaki daha detaylı bilgi için OMU'nun Öğrenci İşleri Daire Başkanlığı'na ulaşılabilir.

Finans:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Akademik Programlar: RAG + LLM
- Finans: Kural
- Ogrenci Isleri: RAG + LLM

Kaynak Ozeti:
- Belge: uluslararası_öğrenci.pdf
- Belge: uluslararası_öğrenci_yönergesi.pdf
- Belge: ön_kayıt_kılavuzu_başvuru_adımları.pdf
- Belge: 2025_2026_yılı_uluslararası_öğrenci_öğrenim_ücretleri_2025_yılı_ilk_kayıt.pdf
- Belge: idari_ve_mali_işler_birimi.txt
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
- Belge: sık_sorulan_sorular.txt
- Belge: öğrenci_işleri_birimi.txt
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: ['finance', 'academic_programs'] (beklenen: ['academic_programs', 'finance']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 2/4
  - [x] not ortalaması
  - [ ] harç
  - [ ] ödeme
  - [x] başvuru
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 1706.7 ms
- **Kaynak Sayisi**: 3

**Yanit:**
```
Akademik Programlar:
Eldeki en ilgili kaynakta su bilgi yer aliyor:
MADDE 9 - (1) ÇAP'tan geçici veya sürekli ayrılma ve ilişik kesilme hâlleri şunlardır: a) Öğrenci, ÇAP'ı kendi isteği ile bırakabilir. b) ÇAP'a kayıtlı öğrenciler, başvuru koşullarını sağlamak şartıyla başka ÇAP başvurusu yapabilirler ve önceki programı bırakmak kaydı ile yeni bir programa geçebilirler. c) Kendi ana dalı olan programdan başka programa yatay geçiş yapan öğrencinin ÇAP’la ilişiği kesilir. ç) Ana dal programında izinli sayılan öğrenci, talep aranmaksızın ÇAP’ta da izinli sayılır. ÇAP'ta dersin açılmaması veya çakışma olması gibi nedenlerle ders alamayacak olan öğrencilere ÇAP veren bölümün önerisi ve ÇAP’ın bağlı olduğu birim yönetim kurulu kararı ile dönem izni verilebilir. d) Öğrenci ÇAP’tan ayrıldığında, başarısız olduğu ÇAP derslerini tekrarlamak zorunda değildir. e) ÇAP'tan ayrılan öğrenciler, aynı ÇAP'a tekrar başvuramaz. f) Tüm ÇAP öğrenimi süresince öğrencinin ana dal genel not ortalaması, bir defaya mahsus olmak üzere 4,00 üzerinden en fazla 2,50’ye kadar düşebilir. Genel not ortalaması bir defa dahi bunun (2.50'nin) altına düşen öğrencinin ikinci ana dal diploma programından kaydı silinir. Ayrıca ana dal genel not ortalaması iki kez 4,00 üzerinden 2,75’in altına düşen öğrencinin de ikinci ana dal diploma programından kaydı silinir. g) ÇAP’ta iki yarı yıl üst üste ders almayan öğrencinin ikinci ana dal diploma programından kaydı silinir. (2) ÇAP’tan kaydı silinen öğrencilerin başarılı oldukları; ancak ana dal programlarında sayılmayan dersleri, genel not ortalamasına dâhil edilmeksizin transkriptlerinde ve diploma eklerinde yer alır. BEŞİNCİ BÖLÜM Yan Dal Programı, Yan Dal Programına Başvuru, Kabul ve Kayıt Şartları Yan dal programı açılması

(Kaynak: yonerge_cift_anadal_yandal.pdf)

Finans:
Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz.

---
Daha iyi yard
... (333 karakter daha)
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
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=factual
- **Sure**: 3468.4 ms
- **Kaynak Sayisi**: 10

**Yanit:**
```
Akademik Programlar:
Sayın öğrenci, 4. sınıfını tamamladıktan sonra programa devam zorunluluğu olan derslerden (İngilizce, Türk Dili I-II, Atatürk İlkeleri ve İnkılap Tarihi) başarısız olan öğrenciler bir üst sınıfa devam edebilir. Ancak bu durumun etkisi 1 yıla kadar uzayabilir.

Kullanılan kaynaklar, Tıp Fakültesi'nin normal eğitim-öğretim süresini 6 yıl olarak tanımladığını ve 1 yıla kadar uzayabilen bir süre olduğunu belirtmektedir. Ayrıca bu süre, katkı payı/öğrenim ücreti ödenmesiyle birlikte öğrenim süresi içerisinde sayılır.

Belgeden elde edilen bilgileri analiz ettiğimizde, 1 yılı geçmemek kaydıyla programa devam edebilir ve katkı payı/öğrenim ücreti ödemeye devam edersiniz.

Finans:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

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
- Belge: öğretim_üyesi_yetiştirme_programı_yönergesi.pdf
- Belge: çift_ana_dal_ikinci_lisans_ve_yan_dal_programı.pdf
- Belge: önlisans_ve_lisans_düzeyindeki_programlar_arasında_geçiş_yönergesi.pdf
```
