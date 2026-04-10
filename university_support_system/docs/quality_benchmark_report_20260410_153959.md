# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:39:59
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 0.0% |
| Uretim Modu Dogrulugu | 0.0% |
| Anahtar Bilgi Kapsami | 0.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 6949.8 ms |
| Medyan Sure | 6949.8 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q22 | Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci n... | YANLIS | YANLIS (llm) | 0/0 | 6949.8 | - |

## Soru Detaylari

### Q22: Sınavda kopya çekilmesinin cezası nedir ve disiplin süreci nasıl işler?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'academic_programs'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: kural) - YANLIS
- **Key Facts**: 0/0
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=False, query_type=factual
- **Sure**: 6949.8 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Sınavda kopya çekilmesinin cezası ve disiplin süreci hakkında bilgi alacaksınız.

Sınav görevlisinin veya ilgili öğretim elemanının uyarısında bulunmaksızın öğrenciye işleme yapması durumunda, öğrenci kopya çekilmesinin cezasını alacaktır. Kopya verme ve çekme girişiminde bulunan öğrenciler, sınav görevlileri veya ilgili öğretim elemanları tarafından tespit edilebilir ve uyarıda bulunabilir. Uyarıda bulunmaksızın öğrenci hakkında işlem yapan sınav görevlisi veya ilgili öğretim elemanı, öğrencinin kopya verme veya çekme davranışının tespit edildiği sınavı geçersiz sayabilir. Bu durumda, öğrenci aynı sınavdan aldıkları notu kaybeder. Öğrenci ayrıca disiplin soruşturması sonucunda cezaya çarptırılabilir.

Sınavda kopya çekilmesinin cezası aşağıda belirtilmiştir:

* Kopya çekilen, kopyaya teşebbüs edilen, kopya verilen, alınıp kopyalama yapılan ve kopyalama yardım eden öğrenciler hakkında, sınav görevlilerince düzenlenen bireysel sınav iptal tutanağı düzenlenerek gerekli yasal işlemler başlatılır.
* Öğrencinin dersi veren öğretim üyesi veya eğitim görevli tarafından geçersiz sayılması
* Eğitim görevlilerinin düzenlediği tutanağa göre gerekli yasal işlemlerin başlatılması

Bu bilgileri temel alarak, öğrenci disiplin soruşturması sonucunda cezaya çarptırılabilecektir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Akademik Programlar: RAG + LLM

Kaynak Ozeti:
- Belge: mühendislik_fakültesi_sınav_uygulama_kuralları.pdf
- Belge: mbm_güncel_staj_ilkeleri_ve_uygulama_esasları_güncel.pdf
- Belge: mühendislik_fakültesi_ortak_sınav_yönergesi.pdf
- Belge: sürekli_eğitim_merkezi_yönergesi.pdf
- Belge: hizmet_içi_eğitim_yönergesi.pdf
- Belge: özel_yetenek_sınavı_yönergesi.pdf
```
