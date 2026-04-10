# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-09 22:20:03
- **Reranker Modeli**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Toplam Soru**: 1

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 0.0% |
| Uretim Modu Dogrulugu | 100.0% |
| Anahtar Bilgi Kapsami | 50.0% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 3273.9 ms |
| Medyan Sure | 3273.9 ms |
| Intent Analizi Aktif | 1/1 |
| Force LLM Sentez | 1/1 |

## Kenar Durumlar ve Negatif Testler

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q20 | Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bil... | YANLIS | OK | 2/4 | 3273.9 | - |

## Soru Detaylari

### Q20: Diplomamı kaybettim ve aynı zamanda e-devlette mezuniyet bilgilerim görünmüyor. Her iki sorun için ne yapmalıyım?

- **Kategori**: F_edge_cases
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs']) - YANLIS
- **Uretim Modu**: llm (beklenen: llm) - OK
- **Key Facts**: 2/4
  - [ ] 2. nüsha
  - [x] diploma
  - [x] e-devlet
  - [ ] YÖKSİS
- **Intent Analizi**: complexity=complex, force_llm=True, is_personal=True, query_type=procedural
- **Sure**: 3273.9 ms
- **Kaynak Sayisi**: 9

**Yanit:**
```
Ogrenci Isleri:
İsterseniz problemi iki ayrı soru olarak ayrılabilir. Birinci soru diplomayı kaybetmenin nasıl anlaşılacağına dair. İkinci soru ise e-devlette mezuniyet bilgisi görülmeyen duruma nasıl çözüm bulunabilir.

Diplomamı kaybetmenin nasıl anlaşılacağına dair:

Diplomayı kaybetmek durumunda kaldığınızda, ilk olarak yaygın gazetelerden birine diploma kayıp ilanı vermelisiniz. Bu ilanın yer aldığı gazete, başvuru dilekçesi, onaylı nüfus cüzdanı sureti ve diploma ücretini yatırdığını gösteren banka dekontu ile diploma aldığınız birime müracaat etmelisiniz. 

Müracaatınız değerlendirildikten sonra, öğrencilere ilk diplomasında yer alan bilgileri içeren yeni bir diploma düzenlenir ve üzerinde İkinci Nüsha olduğu bilgisi yer alır. Bu yöntem, diploma dışındaki belgeler için de uygulanır.

Mezuniyet bilgilerimin e-devlette görünmemesine dair:

Bu konu hakkında elimdeki kaynaklarda net bilgi bulunamadı.

Finans:
Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG + LLM
- Finans: Kural

Kaynak Ozeti:
- Belge: uygulama_esaslari_diploma_mezuniyet_belgeler.pdf
- Belge: ön_lisans_ve_lisans.pdf
- Belge: idari_ve_mali_işler_birimi.txt
- Belge: öğrenci_yemek_bursu_yönergesi.pdf
- Belge: kısmi_zamanlı_öğrenci_çalıştırma_yönergesi.pdf
```
