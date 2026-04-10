# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:40:40
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 25.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3653.2 ms |
| Medyan Sure | 3653.2 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q23 | Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve di... | OK | OK | 1/4 | 3653.2 | - |

## Soru Detaylari

### Q23: Üniversiteyi bırakıp ayrılmak istiyorum, tüm işlemleri ve dikkat etmem gereken hususları söyler misin?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [ ] ilişik kesme
  - [ ] UBYS
  - [x] form
  - [ ] birim
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 3653.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Tüm işlemlerinizi ve dikkat etmem gereken hususları aşağıda listeleyin:

1. Yök Belge İmza Sertifikası:
- Önlisans ve lisans programlarında derslere devam edebilmek için, Yök Belge İmza Sertifikası almak zorunludur.
- Yök Belge İmza Sertifikası alma prosedürü ve koşulları için https://www.yok.gov.tr adresini ziyaret edebilirsiniz.

2. Ders Değişikliği:
- Danışmanınız, kayıt olmak istediğiniz derslerde değişiklik yapma hakkı vardır (Kaynak 1).
- Danışmanın bu hakkı kullanma şeklini ve koşullarını danışmanınız ile görüşerek belirleyiniz.

3. İntibak İşlemi:
- İntibak işlemi, kayıtlı olduğunuz programda aldığınız ve muaf sayılacaklarınızın tespiti için Komisyon tarafından incelenerek belirlenir (Kaynak 2).
- İntibak işlemini nasıl yaptığınızı öğrenmek için https://omu.edu.tr adresini ziyaret edebilirsiniz.

4. Taban Puan Hesaplama:
- Taban puan hesaplaması, öğrenci seçme ve yerleşme sistemi (ÖSYS) tarafından yapılan merkezi sınava göre hesaplanır.
- Nasıl hesablandıracaklarını öğrenmek için https://www.osym.gov.tr adresini ziyaret edebilirsiniz.

5. Kurum İçi Yatay Geçiş:
- Aynı düzeydeki diploma programlarına geçiş için kurum içi yatay geçiş formunu doldurunuz.
- Bu formu nereden ve nasıl aldığınızı öğrenmek için https://omu.edu.tr adresini ziyaret edebilirsiniz.

6. Kurumlararası Yatay Geçiş:
-Bir üniversite, yüksek teknoloji enstitüsü ya da vakıf tarafından kurulan meslek yüksekokullarından OMU’daki eşdeğer eğitim veren fakülte, yüksekokul veya bölüme yapılan geçişi için Kurumlararası Yatay Geçiş belgesi alma işlemlerini tamamlayınız.
- https://omu.edu.tr adresini ziyaret ederek, nasıl yaptığınızı öğrenmek için buradan detaylı bilgi sahibi olabilirsiniz.

7. Ders Yeterlik, Muafiyet ve İntibak Yönergesi:
- Bu yönergeye göre, intibak işlemlerini nasıl gerçekleştireceğiniz ilgili bölüm ile görüştükten sonra bu işlemleri nasıl tamamlayacağınızı öğrenebilirsiniz.
- Bu bilgi kaynakları https://omu.edu.tr sitesini ziyaret edip buradan detaylı bilgiye ulaşabilirsiniz.

Bu i
... (592 karakter daha)
```
