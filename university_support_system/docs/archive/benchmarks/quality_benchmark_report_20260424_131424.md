# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-24 13:14:24
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 7

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 0.0% |
| Uretim Modu Dogrulugu | 0.0% |
| Anahtar Bilgi Kapsami | 0.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 24.7 ms |
| Medyan Sure | 19.5 ms |
| Intent Analizi Aktif | 0/7 |
| Force LLM Sentez | 0/7 |
| A2A Query Failure Delta | 0 |
| A2A Agent Task Failure Delta | 0 |

## A2A Diagnostics Delta

- Overview delta: queries=0, query_failures=0, agent_tasks=0, agent_task_failures=0

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q3 | Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçe... | YANLIS | YANLIS (unknown) | 0/4 | 9.7 | - |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q6 | ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor... | YANLIS | YANLIS (unknown) | 0/4 | 42.7 | - |

## Karsilastirma Gerektiren

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q13 | Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasınd... | YANLIS | YANLIS (unknown) | 0/5 | 14.0 | - |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | YANLIS | YANLIS (unknown) | 0/4 | 12.4 | - |
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | YANLIS | YANLIS (unknown) | 0/0 | 19.5 | - |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | YANLIS | YANLIS (unknown) | 0/4 | 35.4 | - |
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | YANLIS | YANLIS (unknown) | 0/4 | 38.9 | - |

## Soru Detaylari

### Q3: Başarısız olduğum seçmeli ders yerine başka bir seçmeli seçersem devam zorunluluğum nasıl değişir?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: unknown (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] değiştirebilir
  - [ ] devam koşulu
  - [ ] yeni
  - [ ] ders
- **API Sureleri**: api_total=4ms
- **Sure**: 9.7 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Merhaba, hos geldiniz. Size yardimci olabilmem icin oncelikle ad soyad, ogrenci numarasi, bolum, fakulte ve ogrenci tipi/uyruk bilgilerinizi paylasin.
```

### Q6: ÇAP programına başvurmak istiyorum ama harç borcum bulunuyor. ÇAP başvuru şartları neler ve harç borcumu nasıl ödeyebilirim?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['academic_programs', 'finance']) - YANLIS
- **Uretim Modu**: unknown (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] not ortalaması
  - [ ] harç
  - [ ] ödeme
  - [ ] başvuru
- **API Sureleri**: api_total=7ms
- **Sure**: 42.7 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Merhaba, hos geldiniz. Size yardimci olabilmem icin oncelikle ad soyad, ogrenci numarasi, bolum, fakulte ve ogrenci tipi/uyruk bilgilerinizi paylasin.
```

### Q13: Kurum içi yatay geçiş ile kurumlar arası yatay geçiş arasındaki farklar nelerdir? Başvuru şartları ve değerlendirme kriterleri nasıl farklılık gösterir?

- **Kategori**: D_comparison
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: unknown (beklenen: llm) - YANLIS
- **Key Facts**: 0/5
  - [ ] kurum içi
  - [ ] kurumlar arası
  - [ ] Ek Madde
  - [ ] GANO
  - [ ] YKS
- **API Sureleri**: api_total=4ms
- **Sure**: 14.0 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Merhaba, hos geldiniz. Size yardimci olabilmem icin oncelikle ad soyad, ogrenci numarasi, bolum, fakulte ve ogrenci tipi/uyruk bilgilerinizi paylasin.
```

### Q20: Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: unknown (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] 2. nüsha
  - [ ] diploma
  - [ ] e-devlet
  - [ ] YÖKSİS
- **API Sureleri**: api_total=4ms
- **Sure**: 12.4 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Merhaba, hos geldiniz. Size yardimci olabilmem icin oncelikle ad soyad, ogrenci numarasi, bolum, fakulte ve ogrenci tipi/uyruk bilgilerinizi paylasin.
```

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: unknown (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **API Sureleri**: api_total=6ms
- **Sure**: 19.5 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Merhaba, hos geldiniz. Size yardimci olabilmem icin oncelikle ad soyad, ogrenci numarasi, bolum, fakulte ve ogrenci tipi/uyruk bilgilerinizi paylasin.
```

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: unknown (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [ ] form
  - [ ] birim
- **API Sureleri**: api_total=10ms
- **Sure**: 35.4 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Merhaba, hos geldiniz. Size yardimci olabilmem icin oncelikle ad soyad, ogrenci numarasi, bolum, fakulte ve ogrenci tipi/uyruk bilgilerinizi paylasin.
```

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: [] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: unknown (beklenen: llm) - YANLIS
- **Key Facts**: 0/4
  - [ ] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **API Sureleri**: api_total=11ms
- **Sure**: 38.9 ms
- **Kaynak Sayisi**: 0

**Yanit:**
```
Merhaba, hos geldiniz. Size yardimci olabilmem icin oncelikle ad soyad, ogrenci numarasi, bolum, fakulte ve ogrenci tipi/uyruk bilgilerinizi paylasin.
```
