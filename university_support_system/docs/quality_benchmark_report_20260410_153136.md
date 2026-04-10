# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-10 15:31:36
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 0.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 75.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 2096.1 ms |
| Medyan Sure | 2096.1 ms |
| Intent Analizi Aktif | 0/1 |
| Force LLM Sentez | 0/1 |

## Cok-Kaynakli Sentez (Ayni Departman)

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q4 | Pedagojik formasyon dersleri transkripte dahil ediliyor mu, ... | YANLIS | OK | 3/4 | 2096.1 | - |

## Soru Detaylari

### Q4: Pedagojik formasyon dersleri transkripte dahil ediliyor mu, mezuniyet ortalamasına etkisi var mı ve diplomada nasıl bir ibare yer alıyor?

- **Kategori**: A_multi_source_synthesis
- **Zorluk**: hard
- **Departman**: ['student_affairs'] (beklenen: ['academic_programs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 3/4
  - [x] transkript
  - [x] dahil
  - [x] ortalama
  - [ ] tamamlamıştır
- **Sure**: 2096.1 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Yanıtı aşağıdaki şekilde oluşturabiliriz:

Pedagojik formasyon dersleri transkripte dahil ediliyor mu? Elbette dahil ediliyor. Transkript kontrolünün yapıldığında müfredatta yer alan tüm derslerin kaydı ve başarılması önemli olduğu için, pedagojik formasyon dersleri de bu kapsamda değerlendiriyor.

Mezuniyet ortalamasına etkisi var mı? Evet, mezuniyet ortalamasına bir etkisi var diyebiliriz. Müfredat transkript kontrolünün yapılması, öğrencinin mezuniyet hakkı elde edebilmesi için tüm dersleri almak ve başarılı olmak zorunda olması nedeniyle, pedagojik formasyon dersi de dahil olmak üzere tüm derslere olumlu katkı sağlıyor.

Diplomada nasıl bir ibare yer alıyor? Diplomada "Öğrenci Mezunu" ibaresi yer alır. Además, diploma eki ile yurtdışında daha okunabilir ve mukayese edilebilir bir diploma, akademik güzergâhının ve yurtiçinde ve yurtdışında edindiği yeti ve becerilerin tam bir tarifi, başarı ve yetilerinin nesnel ve âdil değerlendirmesi, geleceğe yönelik olarak yurtdışında iş ve eğitim imkânlarına daha rahat ulaşma olanağı, İş bulma olanaklerini artırma kazanımları elde edilebilir.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- RAG + LLM

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
- Belge: 2025_2026_bahar_yatay_geçiş_ilan_metni.pdf
```
