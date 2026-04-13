# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-13 18:14:26
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 50.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 4947.2 ms |
| Medyan Sure | 4947.2 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Surec Zinciri (Uctan Uca Prosedur)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q19 | Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecin... | OK | OK | 3/6 | 4947.2 | - |

## Soru Detaylari

### Q19: Mezuniyet için gerekli tüm koşulları ve ilişik kesme sürecini adım adım açıklar mısın?

- **Kategori**: E_process_chain
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['student_affairs']) - OK
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/6
  - [x] ders
  - [ ] staj
  - [ ] GANO
  - [ ] 2,00
  - [x] ilişik kesme
  - [x] diploma
- **Intent Analizi**: complexity=process_chain, force_llm=True, is_personal=False, query_type=procedural
- **Sure**: 4947.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Mezuniyet için gerekli koşulları ve ilişik kesme sürecini adım adım açıklamak için aşağıdaki bilgileri sağladım:

1. Mezuniyet için gereken koşullar: Öğrenim gördüğü eğitim-öğretim programında yer alan bütün şartları yerine getirerek mezuniyet hakkı kazanan öğrencilere verilmek üzere ön lisans ve lisans diplomaları Öğrenci İşleri Daire Başkanlığı tarafından hazırlanır. (Kaynak 3: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf, Madde 7)

2. İlişik kesme süreci:
 a. Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği ve diğer ilgili mevzuat hükümlerine göre yükseköğretim kurumlarından çıkarma cezası almış olanlar ile kendi istekleri ile kaydını sildiren öğrencilerin Üniversite ile ilişiği kesilir. (Kaynak 1: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf, Madde 32)
 b. Dört yıl üst üste katkı payı ve öğrenim ücreti ödemeyenler ve kayıt yenilememiş durumda olan öğrencilerin, ilgili birimlerin teklifi ve Senato kararı ile YÖK’ün onaylaması durumunda Üniversite ile ilişikleri kesilir. (Kaynak 1: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf, Madde 32)
 c. 8 inci maddenin üçüncü ve dördüncü fıkraları kapsamındaki öğrencilerden başarısız oldukları ders sayısını bire indiremeyenlerin Üniversite ile ilişiği kesilir. (Kaynak 1: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf, Madde 32)

Bu bilgilerden anlaşılacağı üzere, mezuniyet koşulları ve ilişik kesme süreci belirlenmiş kurallara göre gerçekleşir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: ön_lisans_ve_lisans_eğitim_öğretim_yönetmeliği.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
```
