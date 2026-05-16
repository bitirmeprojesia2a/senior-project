# A2A Toplu Mimari Plani

Bu belge, mimari denetimden sonra kabul edilen guncel uygulama sirasini tutar.

## Ilk 10 Madde

1. Runtime authority omurgasi netlestirilecek; davranis belirleyen alanlar `diagnostic_contract` olarak kalmayacak.
2. Capability-first yapi guclendirilecek; agent icindeki ozel kararlar typed capability katmanina tasinacak.
3. Slack security/privacy siniri kurulacak; kisisel veri ve dosya akislari public kanalda cevaplanmayacak.
4. Akademik takvim ve duyuru akisi ayrilacak; tarih sorularinda once takvim, sonra scoped duyuru aranacak.
5. Duyuru listesi ve detay/ozet akisi versioned ref ile calisacak.
6. Bolum/program belirtilen sorularda ilgili bolum belgeleri scoped evidence olarak retrieval havuzuna dahil edilecek.
7. Onkosul, ders programi ve iletisim akislari capability-owner sozlesmesiyle sertlestirilecek.
8. Yanlis cevap analizinde once retrieval/source-owner/capability raporu uretilecek.
9. Golden trace ve Slack replay regresyon seti genisletilecek.
10. Rollout kabul kapilari tek Slack bot, golden trace ve dar Slack replay ile dogrulanacak.

## Duyuru Cache Karari

Duyuru cevaplari genel full-response cache olarak saklanmayacak. Bunun yerine duyuru detay ve ozet akisi `announcement_id + content_hash/updated_at` tabanli versioned ref kullanacak. Duyuru guncellenirse eski conversation ref'i gecersiz sayilacak ve kullanicidan guncel listeyi yenilemesi istenecek.

## Bolum Ozel Belgeleri

Kullanici bolum/program belirtmediyse bolum ozel belgeleri genel cevabi domine etmeyecek. Kullanici bolum/program belirttiyse ilgili `bolum`/`bolum_adi` metadata'sina sahip belgeler retrieval'da boost alacak ve scoped evidence olarak kullanilacak. Genel universite yonetmeligi/policy otoritesi korunacak.

## En Sona Alinacak Buyuk Maddeler

Bu maddeler ilk 10 madde uygulanip test edilip dogrulandiktan sonra ele alinacak:

1. Turkish reranker FP16 shadow benchmark, model secimi ve kalibrasyon.
2. Hybrid model routing.
3. Token/cevap uzunlugu optimizasyonu.
4. Dinamik cok-kurum mimarisi.
