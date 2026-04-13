# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-13 17:09:22
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 25

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 0.0% |
| Uretim Modu Dogrulugu | 0.0% |
| Anahtar Bilgi Kapsami | 0.0% |
| Temiz Kalite Orani | 0.0% |
| Ortalama Sure | 6110.3 ms |
| Medyan Sure | 6111.0 ms |
| Intent Analizi Aktif | 0/25 |
| Force LLM Sentez | 0/25 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q1 | Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zam... | YANLIS | YANLIS (error) | 0/4 | 6203.5 | exception |
| Q2 | Tek ders sınavına girebilmek için stajımı tamamlamış olmam g... | YANLIS | YANLIS (error) | 0/3 | 6122.8 | exception |
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | YANLIS (error) | 0/4 | 6092.5 | exception |
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | YANLIS | YANLIS (error) | 0/4 | 6117.6 | exception |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q5 | Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücreti... | YANLIS | YANLIS (error) | 0/3 | 6087.8 | exception |
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | YANLIS | YANLIS (error) | 0/4 | 6117.9 | exception |
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | YANLIS | YANLIS (error) | 0/5 | 6111.0 | exception |
| Q8 | Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum ke... | YANLIS | YANLIS (error) | 0/5 | 6118.9 | exception |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q9 | 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek sü... | YANLIS | YANLIS (error) | 0/5 | 6089.0 | exception |
| Q10 | Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebi... | YANLIS | YANLIS (error) | 0/4 | 6087.0 | exception |
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | YANLIS | YANLIS (error) | 0/4 | 6140.7 | exception |
| Q12 | Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile ba... | YANLIS | YANLIS (error) | 0/4 | 6084.4 | exception |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | YANLIS | YANLIS (error) | 0/5 | 6107.8 | exception |
| Q14 | Bağıl değerlendirme sistemi ile mutlak değerlendirme arasınd... | YANLIS | YANLIS (error) | 0/4 | 6127.3 | exception |
| Q15 | Diploma eki ile transkript arasındaki fark nedir? Diploma ek... | YANLIS | YANLIS (error) | 0/3 | 6130.4 | exception |
| Q16 | Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? H... | YANLIS | YANLIS (error) | 0/4 | 6135.5 | exception |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q17 | İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders ... | YANLIS | YANLIS (error) | 0/5 | 6104.3 | exception |
| Q18 | Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ... | YANLIS | YANLIS (error) | 0/4 | 6111.1 | exception |
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | YANLIS | YANLIS (error) | 0/6 | 6117.5 | exception |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | YANLIS | YANLIS (error) | 0/4 | 6106.1 | exception |
| Q21 | Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başar... | YANLIS | YANLIS (error) | 0/5 | 6068.0 | exception |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | YANLIS | YANLIS (error) | 0/0 | 6072.5 | exception |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | YANLIS | YANLIS (error) | 0/4 | 6115.5 | exception |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | YANLIS | YANLIS (error) | 0/4 | 6107.4 | exception |
| Q25 | Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne y... | YANLIS | YANLIS (error) | 0/3 | 6081.2 | exception |

## Soru Detaylari

### Q1: Yatay geçişle gelen bir öğrenci, muafiyet başvurusunu ne zaman yapmalı ve karar çıkana kadar derslere devam etmeli mi?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6203.5 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q2: Tek ders sınavına girebilmek için stajımı tamamlamış olmam gerekir mi ve sınavda başarılı sayılmam için minimum not kaç?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/3
- **Sure**: 6122.8 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6092.5 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q4: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['academic_programs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6117.6 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q5: Uluslararası öğrenci olarak kayıt yaptırırken öğrenim ücretimi nereye yatırmam gerekiyor ve ayrıca ikamet izni için hangi belgeleri hazırlamalıyım?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['academic_programs', 'finance', 'student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/3
- **Sure**: 6087.8 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['academic_programs', 'finance']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6117.9 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q7: Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra ders kaydını nasıl yapacağım, danışmanın onay süreci nasıl işliyor?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/5
- **Sure**: 6111.0 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q8: Burslu öğrenciyim ve yatay geçiş yapmak istiyorum. Bursum kesilir mi, yeni üniversitede harç ödemem gerekir mi?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/5
- **Sure**: 6118.9 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q9: 4. sınıf öğrencisiyim ve program süresini 1 yıl aştım. Ek süre hakkım var mı ve bu sürede katkı payı öder miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['academic_programs', 'student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/5
- **Sure**: 6089.0 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q10: Devamsızlıktan kaldığım bir dersin bütünleme sınavına girebilir miyim? Giremiyorsam bu dersi ne zaman tekrar alabilirim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6087.0 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['student_affairs', 'finance']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6140.7 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q12: Hazırlık sınıfındayım ve transkriptim yok. Ek Madde-1 ile başka bir üniversiteye yatay geçiş yapabilir miyim?

- **Kategori**: C_conditional_scenario
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6084.4 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/5
- **Sure**: 6107.8 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q14: Bağıl değerlendirme sistemi ile mutlak değerlendirme arasındaki fark nedir ve hangi öğrenci sayısında hangisi uygulanır?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['academic_programs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6127.3 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q15: Diploma eki ile transkript arasındaki fark nedir? Diploma eki transkript yerine kullanılabilir mi?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/3
- **Sure**: 6130.4 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q16: Kayıt dondurma ile kayıt yaptırmamak arasında ne fark var? Her iki durumda da öğrencilik haklarım nasıl etkilenir?

- **Kategori**: D_comparison
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6135.5 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q17: İlk kez üniversite kaydını yaptıran bir öğrenci olarak ders kaydından danışmanın onayına kadar tüm süreci başından sonuna anlatır mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/5
- **Sure**: 6104.3 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q18: Sınav notuma itiraz etmek istiyorum. Başvuru süreci, süresi ve olası sonuçları nelerdir?

- **Kategori**: E_process_chain
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6111.1 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/6
- **Sure**: 6117.5 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q20: Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6106.1 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q21: Uzaktan eğitim yoluyla alınan 5-i derslerinin sınav ve başarı değerlendirmesi yüz yüze derslerden farklı mıdır?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['student_affairs', 'academic_programs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/5
- **Sure**: 6068.0 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Sure**: 6072.5 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6115.5 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
- **Sure**: 6107.4 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```

### Q25: Hocam benim ders notlarımı sisteme girmemiş, bu durumda ne yapabilirim?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: easy
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: error (beklenen: llm) - YANLIS
- **Key Facts**: 0/3
- **Sure**: 6081.2 ms
- **Kaynak Sayisi**: 0
- **Uyarilar**: exception
- **Hata**: [WinError 1225] Uzaktaki bilgisayar ağ bağlantısını reddetti

**Yanit:**
```

```
