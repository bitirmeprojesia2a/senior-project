# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:41:27
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 25.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 2871.2 ms |
| Medyan Sure | 2871.2 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Semantik Anlama (Paraphrase)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q24 | Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçi... | OK | OK | 1/4 | 2871.2 | - |

## Soru Detaylari

### Q24: Okulumu dondurup 1 yıl ara verdikten sonra dönüşte ders seçimini nasıl yapacağım?

- **Kategori**: G_semantic_paraphrase
- **Zorluk**: medium
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 1/4
  - [x] kayıt
  - [ ] yenileme
  - [ ] UBYS
  - [ ] müfredat
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 2871.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Bu soruya yanıt verirken ilk olarak, sen de okulumuzu bırakıp 1 yıl aranınca ve şimdi dönüşte ders seçimini nasıl yapacağınızı düşünelim.

Kayıtlı olduğunuz dönemden ayrıldığınıza dair bir belge bulunduğunu varsayıyorum. Bu belge, kayıt dondurma belgesidir. 

KAYIT DONDURMA BELGESİNİ NASIL ALIRIM?

Kayıt dondurma belgesini alma processi, genel olarak öğrenci işleri biriminizin belirlediği kurallara göre yürür.

Ayrıca, kaydını donduran öğrenci, öğrenimine devam edemez ve kayıt dondurduğu döneme/yıla ait sınavlara giremez.

DÖNÜŞTE DERS SEÇİMİNİ NASIL YAPACAĞIM?

Dönüşte ders seçiminizi yapabilmek için önce kaydınızı devretmelisiniz. Devir alma belgesini almamızın ardından ders seçiminizi yapabilirsiniz.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans.pdf
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: sık_sorulan_sorular.txt
```
