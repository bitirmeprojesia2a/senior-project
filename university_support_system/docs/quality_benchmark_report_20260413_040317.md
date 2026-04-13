# Reranker Kalite Benchmark Raporu

- **Tarih**: 2026-04-13 04:03:17
- **Reranker Modeli**: nreimers/mmarco-mMiniLMv2-L6-H384-v1
- **Toplam Soru**: 2

## Ozet Metrikler

| Metrik | Deger |
|--------|-------|
| Departman Dogrulugu | 100.0% |
| Uretim Modu Dogrulugu | 0.0% |
| Anahtar Bilgi Kapsami | 77.8% |
| Temiz Kalite Orani | 100.0% |
| Ortalama Sure | 36717.6 ms |
| Medyan Sure | 36717.6 ms |
| Intent Analizi Aktif | 0/2 |
| Force LLM Sentez | 0/2 |

## Capraz Departman Paralel Islem

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q7 | Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra der... | OK | YANLIS (rag) | 3/5 | 42229.0 | - |

## Kosullu Senaryo Bazli

| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |
|---|------|------|-----|-------|-----------|----------|
| Q11 | İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak ist... | OK | YANLIS (rag) | 4/4 | 31206.2 | - |

## Soru Detaylari

### Q7: Kayıt yenileme döneminde harç ücretimi yatırdıktan sonra ders kaydını nasıl yapacağım, danışmanın onay süreci nasıl işliyor?

- **Kategori**: B_cross_department_parallel
- **Zorluk**: medium
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 3/5
  - [ ] harç
  - [ ] UBYS
  - [x] ders
  - [x] danışman
  - [x] onay
- **Sure**: 42229.0 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
En ilgili ogrenci isleri kaynaginda su bilgi yer aliyor:
Müfredat kontrolü nedir ve ne zaman yapmalıyım? Öğrenci bilgi yönetim sisteminde yer alan müfredat bilgileri ve transkriptinize ulaşarak, her kayıt dönemi başında alıp başarılı olduğunuz dersleri müfredatınızla karşılaştırmanız gerekmektedir. Danışman onay bittikten sonra yapmam gereken bir şey var mı? Danışman onayı işlemi tamamlandıktan sonra, kayıtlanmış olduğunuz dersleri tek tek kontrol ediniz. Sizin danışman onayına göndermiş olduğunuz derslerden bir veya birkaçı danışmanınız tarafından listeden çıkartılmış olabilir. Sınıf yoklama listesine imza atmalı mıyım? Evet, sistemden alınan ve üzerinde adınızın yer aldığı sınıf yoklama listesine devam/devamsızlık imzasını atınız. Sınıf yoklama listesinde adımız yoksa ne yapmalıyız? Listede adınız yoksa kaydınızda sorun vardır demektir ve derhal danışmanınızla görüşünüz.

(Kaynak: sık_sorulan_sorular.txt)

Finans:
Ogrenim ucreti ogrenci turune ve birime gore degisiyor. Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Finans: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
```

### Q11: İkinci öğretim öğrencisiyim ve bir dönem kayıt dondurmak istiyorum. Bu dönem harç ücretimi yatırmak zorunda mıyım ve kayıt dondurduğum süre eğitim süresinden sayılır mı?

- **Kategori**: C_conditional_scenario
- **Zorluk**: hard
- **Departman**: ['student_affairs', 'finance'] (beklenen: ['student_affairs', 'finance']) - OK
- **Uretim Modu**: rag (beklenen: llm) - YANLIS
- **Key Facts**: 4/4
  - [x] öğrenim ücreti
  - [x] gerek yok
  - [x] yönetim kurulu
  - [x] sayılma
- **Sure**: 31206.2 ms
- **Kaynak Sayisi**: 5

**Yanit:**
```
Ogrenci Isleri:
En ilgili ogrenci isleri kaynaginda su bilgi yer aliyor:
II. Öğretim öğrencisiyim. Kayıt dondurmak istediğimde harç ücretimi yatırmak zorunda mıyım? Kayıt dondurma isteğinizin ilgili yönetim kurulunca kabul edilmesi durumunda öğrenim ücretini yatırmanıza gerek yoktur. Kayıt dondurma ile kayıt yaptırmamak arasında bir fark var mı? Kayıt dondurduğunuz süreler eğitim-öğretimden sayılmaz. Kaydımı sildirmek için ne yapmam gerekir? UBYS üzerinden talepte bulunarak ilişik kesme süreci başlatabilir ve ilişiğinizin kesilmesini sağlayabilirsiniz. Bunun yanı sıra şahsen başvurarak tarafınızca doldurulacak ilişik kesme formunu, form üzerinde belirtilen merkezlerde onaylattıktan sonra öğrenim gördüğünüz birime teslim etmeniz yeterli olacaktır. Kaydınızın silinmesi ile birlikte öğrencilik hakkınız sona erer.

(Kaynak: sık_sorulan_sorular.txt)

Finans:
Ogrenim ucreti ogrenci turune ve birime gore degisiyor. Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin.

---
Daha iyi yardimci olabilmem icin sorunuzu daha detayli aciklayabilirsiniz ya da ilgili sekreterin iletisim bilgilerini paylasirim. "Iletisim bilgisi" yazarak ulasabilirsiniz.

Uretim Turu:
- Ogrenci Isleri: RAG
- Finans: Kural

Kaynak Ozeti:
- Belge: sık_sorulan_sorular.txt
- Belge: ön_lisans_ve_lisans.pdf
- Belge: yonetmelik_onlisans_lisans_egitim_ogretim.pdf
- Belge: 2025_2026_güz_yarıyılı_yatay_geçiş_ı̇lan_metni.pdf
```
