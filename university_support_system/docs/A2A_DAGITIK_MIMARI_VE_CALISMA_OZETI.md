# A2A Dagitik Mimari ve Son Calisma Ozeti

Bu not, Nisan 2026 boyunca duyuru/etkinlik entegrasyonundan Slack uzerindeki A2A calisma moduna, merkezi retrieval servisine ve son RAG/routing kalite iyilestirmelerine kadar yapilan ana teknik isleri ozetler.

## Mevcut Mimari Durum

Sistem artik tek bir monolitik asistan gibi davranmak zorunda degil. Ana API, departman agent'lari, uzman agent'lar, duyuru/etkinlik capability agent'lari ve merkezi retrieval servisi ayri servisler olarak calisir.

Calisan ana servis gruplari:

- `api`: Kullanici sorgusunu alir, routing/orchestration yapar.
- `retrieval-service`: Embedding/reranking gibi agir RAG islemlerini merkezi hale getirir.
- `agent-student-affairs`: Ogrenci isleri ana orchestrator agent'i.
- `agent-student-registration`, `agent-student-graduation`, `agent-student-internship`, `agent-student-life`: Ogrenci isleri uzman agent'lari.
- `agent-academic`: Akademik programlar ana orchestrator agent'i.
- `agent-academic-curriculum`, `agent-academic-regulation`, `agent-academic-international`: Akademik uzman agent'lari.
- `agent-finance`: Finans ana orchestrator agent'i.
- `agent-finance-tuition`, `agent-finance-scholarship`: Finans uzman agent'lari.
- `agent-announcement`: Duyuru/haber capability agent'i.
- `agent-event`: Etkinlik/seminer capability agent'i.
- `slack-bot-a2a`: Slack'ten gelen mesajlari A2A servislerine baglayan edge client.

Bu yapi demo/bitirme projesi icin "dagitik A2A uyumlu mimari" olarak sunulabilir. Production-grade dis entegrasyon icin Kubernetes, service mesh, gelismis queue/backpressure ve dis partner A2A testleri sonraki adim olarak dokumante edilmelidir.

## Neden Merkezi Retrieval Servisi

Baslangicta her agent kendi embedding/reranker modelini yuklediginde ciddi cold-start ve kaynak maliyeti olusuyordu. Ozellikle GPU/Docker ortaminda her servis icin model isinmasi gereksiz tekrar demekti.

Bu nedenle agir RAG katmani merkezi `retrieval-service` icine tasindi.

Kazanimlar:

- Embedding/reranker modeli tek yerde isinir.
- Agent servisleri daha hafif kalir.
- Warm-up maliyeti azalir.
- GPU/RAM baskisi duser.
- Retrieval davranisi daha tutarli hale gelir.
- Sektor pratiklerine daha yakin bir "shared retrieval service" modeli elde edilir.

Bu karar, "her agent kendi modeline sahip olsun" yaklasimindan daha temiz ve surdurulebilir kabul edildi.

## A2A Standart Uyumluluk Noktalari

Sistemde su A2A uyum parcalari bulunur:

- JSON-RPC `/a2a` endpoint'leri.
- AgentCard/agent discovery metadata.
- Agent identity ve target identity bilgileri.
- HMAC imza/security header altyapisi.
- Health endpoint'lerinde build metadata kontrolu.
- Rollout sirasinda ayni build id'nin tum agent'larda gorulmesini bekleyen dogrulama.
- Department transport ve capability transport ayrimi.
- Internal A2A diagnostics ve agent task failure kayitlari.

Sinirlar:

- Deployment lokal Docker Compose uzerindedir.
- Dis partner agent ile production ortaminda surekli entegrasyon yoktur.
- Retry, queue, autoscaling ve backpressure mekanizmalari sinirlidir.
- Slack bot edge client olarak calisir; A2A stack lifecycle'i ile iliskisi manuel komutlarla yonetilir.

Bu yuzden sistem "production A2A platformu" degil; "A2A uyumlu dagitik prototip ve demo mimarisi" olarak tanimlanmalidir.

## Slack Calisma Modlari

Slack iki sekilde calisabilir:

- `inprocess`: Slack bot lokal monolitik orchestrator kullanir.
- `a2a`: Slack bot A2A endpointlerine HTTP/JSON-RPC ile baglanir.

A2A Slack modu, dagitik mimariyi gercek kullanici arayuzu uzerinden test etmek icin kullanilir. Slack'te onceki mesaj baglami, login/logout, OTP dogrulama, follow-up ucret sorulari ve duyuru/etkinlik capability akislari bu modda dogrulandi.

## Duyuru ve Etkinlik Akisi

Duyuru ve etkinlik sorgulari klasik RAG akisi yerine capability agent'lara yonlendirilir.

Ornekler:

- "guncel duyur"
- "son duyurular neler"
- "bugunku etkinlikler neler"
- "yaklasan seminer var mi"
- "Elektrik elektronik muhendisligi ders programi var mi"

Duyuru agent'i structured announcement DB kayitlarini kullanir. Etkinlik agent'i etkinlik verisini tarih/fakulte/birim kapsamiyla arar.

Bu ayrim yapildi cunku duyuru/etkinlik bilgisi belge RAG'inden farkli olarak zamana duyarlidir ve structured kayit olarak daha dogru islenir.

## Akademik Kaynak Kapsami

Duyuru kaynaklari cekildikten sonra bazi bolumlerde ders programi/mufredat verisinin eksik kaldigi goruldu. Bu nedenle duyuru preset'lerinde takip edilen bolumler icin ders programi ve curriculum kapsami genisletildi.

Eklenen veya kontrol edilen alanlar:

- Bilgisayar Muhendisligi ders programlari ve UBYS curriculum seed.
- Elektrik Elektronik Muhendisligi ders programlari.
- Fizik ders programlari.
- Istatistik ders programlari.
- Fen Bilgisi Ogretmenligi.
- Matematik Ogretmenligi.

Bu kapsam icin `scripts.audit_academic_source_coverage` eklendi. Komut, duyuru kaynaklari ile curriculum/schedule DB kapsamlarini karsilastirir.

## Ucret / Harc Akisi

Ogrenim ucreti sorularinda iki farkli kategori ayrildi:

- Genel ucret miktari: finance/tuition.
- Kisisel harc borcu: auth gerektiren finance VT sorgusu.

Ornek:

- "Dis hekimligi donem ucreti ne kadar?" genel ucret bilgisidir, auth gerekmez ama ogrenci tipi gerekir.
- "Harc borcum ne kadar?" kisisel finans verisidir, login/OTP gerekir.

PDF'den cikarilan structured ucret katalogu kullanilir. Postgres tablosunda eksik olsa bile katalog fallback'i devreye girebilir. Bu sayede Dis Hekimligi gibi DB seed eksigi olan birimler cevaplanabilir.

## Conversation ve Follow-up Duzeltmeleri

Slack DM icin context id once her mesajda degistigi icin follow-up sorular baglam kaybediyordu. DM context sabitlendi:

- DM: `slack:<channel_id>:<user_id>`
- Thread: `thread_ts`

Bu sayede su akilar duzeldi:

- "Dis hekimligi donem ucreti ne kadar?"
- "Turk ogrenciyim"
- "Yabanci ogrenciyim"

Logout sonrasi eski session kalmasi da duzeltildi. Logout artik Slack kullanicisina ait tum aktif session'lari pasif hale getirir.

## Routing ve LLM Karar Katmani

Eski sistemde cok sayida erken heuristic gate vardi. Bunlar hiz icin yararliydi ama semantik esnekligi dusuruyordu.

Yeni yaklasim:

- LLM semantik niyeti belirler.
- Deterministik katman auth, DB, tool ve kaynak guvenligini kontrol eder.
- Marker'lar karar verici ana beyin degil, guvenlik rayi olarak kalir.

Routing LLM artik sunlari dondurur:

- `departments`
- `confidence`
- `complexity`
- `is_personal`
- `force_llm_synthesis`
- `query_type`
- `canonical_query`
- `primary_intent`
- `target_capability`
- `required_slots`
- `missing_slots`

`required_slots` / `missing_slots` eklentisiyle LLM sadece "bu finance" demekle kalmaz; "ogrenci tipi eksik", "basvuru turu eksik", "auth gerekli" gibi semantik eksik bilgi sinyali de verir.

Ana orchestrator, dispatch oncesi `missing_slots` alanini kontrol eder. Oturum metadata'sinda zaten dolu olan slotlar eksik sayilmaz.

Ornek:

- `student_type` eksikse Turk/uluslararasi ogrenci sorulur.
- `application_type` eksikse hangi basvuru turu oldugu sorulur.
- `auth` eksikse OTP login istenir.
- `academic_calendar` niyetinde fakulte/program eksigi dikkate alinmaz; genel akademik takvim sorusu bolume bagli degildir.

## Query Normalization ve Cagri Azaltma

Routing LLM artik `canonical_query` uretebildigi icin her genel sorgu icin ayri query expansion/normalization LLM cagrisi yapmak gereksiz hale geldi.

Yeni prensip:

- Genel sorgularda routing LLM'in `canonical_query` alani kullanilir.
- Kisa capability parcaciklari icin pre-normalization kalir. Ornek: "guncel duyur".
- Cok departmanli cevaplarda specialist LLM ozeti + global LLM ozeti gibi cift sentez varsayilan olmaktan cikarildi.

Bu hem maliyeti hem de "ozeti tekrar ozetleme" riskini azaltir.

## Akademik Takvim Duzeltmeleri

`Final sinavlari ne zaman?` gibi sorularda LLM bazen kaynakta takvim PDF'ini bulsa bile dogru satiri cikaramiyordu.

Bu nedenle registration agent genel akademik takvim sorularinda resmi PDF satirlarini structured parse eder:

- `Yariyil Sonu Sinavlari`
- `Butunleme Sinavlari`
- `Yariyil Sonu Sinav Sonuclarinin Internetten Girilmesinin Son Gunu`

Bu hardcoded tarih degildir; tarih PDF satirindan okunur.

Ornek:

- "Final sinavlari ne zaman?" -> sinav tarih araligi.
- "Final sinavlarinin sisteme girilmesinin son gunu ne zaman?" -> sonuc/not giris son gunu.

## Cevap Kalitesi ve Temizleme

LLM bazen Turkce cevapta yabanci kelime veya ic talimat sizdirabiliyordu. Bunun icin final cevap temizleyici guclendirildi.

Yakalanan ornekler:

- `certain` -> `belirli`
- `cumle bulunamadi`
- `yonlendir`
- `onayigereken` gibi bosluk artefaktlari
- role/system prompt kalintilari

Bu temizlik cevap dogrulugunun yerini tutmaz; sadece kullaniciya giden metinde bariz artefaktlari azaltir.

## Benchmark ve Diagnostics

Kaliteyi olcmek icin `scripts.run_quality_benchmark` kullanilir.

Onemli ozellikler:

- API health preflight.
- Cache bypass.
- A2A diagnostics before/after delta.
- Agent task failure delta.
- LLM role/model loglari.
- Departman dogrulugu, uretim modu, key fact coverage, kalite uyarilari.

Sonraki testlerde dikkat edilecek sorular:

- `Final sinavlari ne zaman?`
- `Final sinavlarinin sisteme girilmesinin son gunu ne zaman?`
- `Dis hekimligi donem ucreti ne kadar?`
- `Turk ogrenciyim`
- `sey basvuru ne zaman`
- `Sinav notlarimi nereden gorebilirim?`
- `Elektrik elektronik muhendisligi ders programi var mi?`

## Bilincli Birakilan Production Hardening Isleri

Su an yapilmamasi tercih edilen, ancak production icin mantikli sonraki adimlar:

- Kubernetes deployment.
- Service mesh.
- Autoscaling.
- Queue/backpressure.
- Distributed tracing standardizasyonu.
- Gercek dis partner A2A agent entegrasyonu.
- Daha gelismis retry/circuit breaker politikalari.
- Slack bot lifecycle'inin A2A stack ile daha otomatik yonetilmesi.

Bu isler demo kalitesini dramatik artirmadan kapsami buyutecegi icin su an bilincli olarak backlog'a birakildi.

## Kisa Degerlendirme

Mevcut sistem:

- RAG tabanli universite destek sistemi olmaktan cikti.
- A2A uyumlu dagitik agent mimarisine yaklasti.
- Slack uzerinden gercek kullanici akislariyla test edilebilir hale geldi.
- Retrieval maliyeti merkezi servise alindi.
- Routing LLM daha fazla semantik sorumluluk aliyor.
- Deterministik katman guvenlik, auth, DB ve kaynak tutarliligi icin kapida duruyor.

Bu haliyle sistem bitirme projesi ve demo icin guclu bir teknik hikaye sunar. Production icin gerekli agir altyapi isleri ayrica dokumante edilmis ve bilincli kapsam disi birakilmistir.

## Arkadasa Anlatilabilecek Detayli Teknik Aciklama

Bu bolum, yukaridaki mimari notun daha anlatimli ve kapsamli versiyonudur. Amac sadece "ne yaptik?" demek degil; neden yaptigimizi, hangi problemi gordugumuzu ve cozumun nasil calistigini aciklamaktir.

### 1. Baslangic Noktasi: Klasik RAG Destek Botu

Sistemin ilk temel mantigi klasik RAG akisi uzerine kuruluydu. Kullanici bir soru soruyordu, sistem sorunun hangi departmana ait oldugunu buluyor, ilgili ChromaDB koleksiyonundan belge parcalari cekiliyor ve gerekirse LLM bu kaynaklara dayanarak cevap uretiyordu.

Bu yapi ogrenci isleri yonetmelikleri, akademik yonergeler, staj belgeleri, muafiyet kurallari gibi statik veya yari-statik belgeler icin mantikliydi. Fakat sistem genisledikce her veri tipinin RAG belgesi gibi davranmadigi goruldu.

Ozellikle su tip veriler farkli davraniyordu:

- Duyurular.
- Haberler.
- Etkinlikler.
- Seminerler.
- Ders programi duyurulari.
- Ucret tablolari.
- Kisisel harc borcu veya not ortalamasi gibi VT verileri.

Bu nedenle sistem sadece "belge ara ve cevapla" yapisindan daha zengin bir agent mimarisine evrildi.

### 2. Duyuru ve Etkinliklerin Ayrilmasi

Duyuru ve etkinlik bilgileri klasik RAG icin uygun degil. Cunku bu bilgiler:

- Tarihe gore siralanmali.
- Guncel/yakin tarihli kayitlar one alinmali.
- Kaynak URL ve ek dosya linkleri korunmali.
- Fakulte, bolum veya birim kapsami ile filtrelenebilmeli.
- "Son duyurular", "guncel duyur", "bugunku etkinlikler" gibi niyetlerde structured lookup yapilmali.

Bu nedenle duyuru ve etkinlik icin ayri capability agent'lar olusturuldu:

- `agent-announcement`: Duyuru, haber, ilan, ders programi duyurusu gibi kayitlari getirir.
- `agent-event`: Etkinlik, seminer, konferans gibi kayitlari getirir.

Ornek:

```text
Kullanici: guncel duyur
Sistem: announcement capability agent'a gider, en guncel duyurulari tarih sirasiyla getirir.
```

```text
Kullanici: bugunku etkinlikler neler
Sistem: event capability agent'a gider, bugun veya yakin tarih icin etkinlik arar.
```

Bu ayrim sayesinde duyuru/etkinlik sorulari RAG'in "benzer belge parcasi" mantigina mahkum kalmadi.

### 3. Duyurulardan Sonra Akademik Kapsam Eksiklerinin Ortaya Cikmasi

Duyuru kaynaklari eklendikten sonra su problem ortaya cikti: bazi bolumlerin duyurulari takip ediliyordu ama ayni bolumlerin ders programi veya curriculum verisi structured DB tarafinda eksikti.

Mesela Bilgisayar Muhendisligi veya Elektrik Elektronik Muhendisligi icin duyuru cekilebiliyor ama "2. yariyil dersleri neler?", "BIL104 on kosulu var mi?", "Olasilik ve istatistige giris hangi yariyilda?" gibi sorularda DB kapsami eksik kalabiliyordu.

Bu nedenle duyuruda takip edilen bolumler icin akademik veri kapsami da genisletildi.

Yapilanlar:

- Bilgisayar Muhendisligi UBYS curriculum seed'i olusturuldu.
- Bilgisayar Muhendisligi haftalik ders programlari ingest edildi.
- Elektrik Elektronik Muhendisligi ders programlari kontrol edildi.
- Fizik, Istatistik, Fen Bilgisi Ogretmenligi ve Matematik Ogretmenligi icin schedule/curriculum kapsami denetlendi.
- Ders kodu normalizasyonu eklendi; Turkce karakterli veya noktalı-I varyantlari kanonik koda indirildi.
- `scripts.audit_academic_source_coverage` ile duyuru preset'leri ve akademik coverage karsilastirilabilir hale getirildi.

Bu is, "soruya gore statik cevap yazmak" degil; veri kapsamini sistematik olarak genisletmekti.

### 4. Monolitikten Dagitik A2A Yapıya Gecis

Sistemin onemli evrimlerinden biri monolitik akistan dagitik A2A agent mimarisine gecis oldu.

Onceki yaklasimda ana orchestrator cok fazla sorumluluk tasiyordu. Routing, departman secimi, RAG, uzman davranislari, sentez ve bazi fallback'ler tek sistem icinde yogunlasiyordu.

Yeni yaklasimda servisler ayrildi:

- Ana API kullanici istegini alir.
- Router sorunun niyetini ve ilgili agent'lari belirler.
- Department orchestrator agent'lari kendi alt uzmanlarina dagitir.
- Specialist agent'lar dar alandaki isi yapar.
- Capability agent'lar duyuru/etkinlik gibi ozel veri kaynaklarini isler.
- Retrieval service agir RAG islerini merkezi olarak ustlenir.

Bu su anlama gelir:

```text
Kullanici -> API -> Router -> Department Agent -> Specialist Agent -> Retrieval/DB/LLM -> Final Answer
```

veya capability icin:

```text
Kullanici -> API -> Router/Normalizer -> Announcement/Event Agent -> Structured DB -> Final Answer
```

### 5. A2A Katmaninda Neler Var

A2A tarafi sadece container ayirmaktan ibaret degil. Sisteme su parcalar eklendi:

- JSON-RPC tabanli `/a2a` endpoint'leri.
- AgentCard/agent discovery metadata.
- Service identity ve target identity kontrolleri.
- HMAC imza/security header altyapisi.
- Department transport ve capability transport ayrimi.
- Health endpoint'lerinde build metadata.
- Rollout sonrasi tum servislerde ayni build id kontrolu.
- A2A diagnostics ve agent task failure kaydi.

Bu sayede sistem bir servis calisti mi diye degil, dogru build ile dogru agent mi calisiyor diye kontrol ediliyor.

Rollout script'i su mantikla calisir:

1. Ortak Docker image build edilir.
2. Build id, timestamp, git sha ve image ref env olarak verilir.
3. Secilen A2A servisleri ayaga kaldirilir.
4. Health endpoint'lerinde beklenen build id gorunene kadar beklenir.
5. Eski image adaylari raporlanir.

Bu, Docker'in eski container/image ile sessizce devam etmesi riskini azaltir.

### 6. Neden Merkezi Retrieval Servisi

Bir ara her agent'in kendi embedding ve reranker modelini tasimasi fikri vardi. Ancak bu yaklasim pratikte maliyetli:

- Her container modeli ayri yukler.
- GPU/RAM tuketimi artar.
- Cold-start suresi uzar.
- Warm-up maliyeti katlanir.
- Ayni retrieval davranisini birden cok yerde tutmak zorlasir.

Bu nedenle merkezi `retrieval-service` tasarimi tercih edildi.

Bu servis embedding/reranking gibi agir islemleri tek yerde yapar. Agent'lar domain mantigini ve cevap stratejisini yurutur, retrieval icin merkezi servise baglanir.

Bu mimari su acidan daha temiz:

- Agent'lar hafifler.
- Retrieval davranisi tutarli olur.
- Model isinma maliyeti azalir.
- GPU kullanimini yonetmek kolaylasir.
- Sektor pratiklerine daha yakindir.

Bu karar sistemin performansini ve dagitik mimari kalitesini ciddi etkiledi.

### 7. Slack Entegrasyonu ve Gercek Kullanici Akisi

Slack tarafinda sistem iki runtime ile calisabilir:

- `inprocess`: Lokal monolitik orchestrator.
- `a2a`: A2A endpointlerine JSON-RPC ile baglanan Slack bot.

A2A Slack modu, dagitik topolojiyi gercek kullanici arayuzunden test etmeyi saglar. Kullanici Slack'e mesaj yazar; bot A2A API/agent servisleriyle konusur ve cevabi Slack'e yollar.

Slack'te onemli problemler cozuldu:

- DM context id her mesajda degisiyordu; follow-up kayboluyordu.
- Logout sonrasi eski auth session kalabiliyordu.
- Iki Slack runtime ayni anda aciksa cift cevap riski vardi.
- Ucret follow-up'inda login profili kullanicinin acikca sordugu bolumu ezebiliyordu.

DM context sabitlendi:

```text
slack:<channel_id>:<user_id>
```

Thread'li kanal mesajlarinda ise `thread_ts` kullanilmaya devam eder.

Bu sayede:

```text
Kullanici: Dis hekimligi donem ucreti ne kadar?
Bot: Turk ogrenci misiniz, uluslararasi ogrenci misiniz?
Kullanici: Turk ogrenciyim
Bot: Dis Hekimligi Fakultesi / Turk ogrenci ucretini verir.
```

akisi dogru calisir.

### 8. Auth, OTP ve Kisisel Veri Ayrimi

Sistemde genel bilgi ile kisisel veri ayrimi kritik hale getirildi.

Genel bilgi ornekleri:

- `Ders kaydi nasil yapilir?`
- `Dis hekimligi donem ucreti ne kadar?`
- `Sinav notuma nasil itiraz ederim?`
- `Sinav notlarimi nereden gorebilirim?`

Kisisel veri ornekleri:

- `Not ortalamam kac?`
- `Harc borcum ne kadar?`
- `Kac AKTS tamamladim?`
- `Stajim ne durumda?`

Kisisel veri sorularinda Slack OTP login gerekir. Kullanici login degilse sistem cevap uretmez; dogrulama ister. Bu deterministik katmanin gorevidir.

Bu ayrim neden onemli?

LLM "not ortalamam kac?" sorusuna tahmini cevap uretmemeli. Gercek veri VT'den gelmeli ve kullanici dogrulanmis olmali.

### 9. Ucret ve Harc Akisi

Ogrenim ucreti ile harc borcu ayrildi.

Ogrenim ucreti:

- Genel veri.
- Fakulte/program ve ogrenci turune gore degisir.
- Auth gerektirmez.
- Tuition table veya structured catalog'dan gelir.

Harc borcu:

- Kisisel veri.
- Student id/auth gerektirir.
- Finans VT sorgusu ile gelir.

Ornek:

```text
Kullanici: Elektrik elektronik muhendisligi ogrenim ucreti ne kadar?
Bot: Turk ogrenci misiniz, uluslararasi ogrenci misiniz?
```

```text
Kullanici: Harc borcum ne kadar?
Bot: Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor.
```

Bu ayrim hem dogruluk hem de gizlilik icin gerekliydi.

### 10. Routing LLM ve Deterministik Guardrail Dengesi

Eski sistemde cok sayida heuristic marker vardi. Bunlar hiz icin iyiydi ama semantik esnekligi azaltiyordu.

Yeni prensip:

```text
LLM semantik niyeti belirler.
Deterministik katman guvenlik, auth, DB, kaynak ve tool uygunlugunu kontrol eder.
```

Yani deterministik katman LLM'in anlam kararini her zaman ezmez. Sadece su konularda kesin kapidir:

- Kisisel veri icin auth.
- DB/tool varligi.
- Eksik slot.
- Kaynak yoksa uydurma engeli.
- Duyuru/etkinlik gibi capability route.
- Akademik takvim gibi structured resmi veri.

Bu denge sayesinde sistem hem daha esnek hem daha guvenli hale geldi.

### 11. Routing Ciktisinin Zenginlestirilmesi

Routing LLM artik sadece departman secmiyor. Su alanlari donduruyor:

```json
{
  "departments": ["student_affairs"],
  "confidence": 0.88,
  "complexity": "simple",
  "is_personal": false,
  "force_llm_synthesis": false,
  "query_type": "factual",
  "canonical_query": "Final sinavlari genel akademik takvime gore ne zaman?",
  "primary_intent": "academic_calendar",
  "target_capability": "none",
  "required_slots": [],
  "missing_slots": [],
  "reasoning": "genel akademik takvim tarihi"
}
```

Bu alanlar sayesinde:

- Query normalization ayri LLM cagrisi olmadan yapilabilir.
- Duyuru/etkinlik capability ayrimi daha net olur.
- Kisisel veri ayrimi daha iyi yapilir.
- Eksik bilgi sorulari daha dogal hale gelir.

### 12. `required_slots` ve `missing_slots`

Bu son eklenen onemli iyilestirmedir.

LLM artik "bu soruyu cevaplamak icin hangi bilgi eksik?" bilgisini yapisal olarak dondurur.

Ornek:

```text
Kullanici: Elektrik elektronik muhendisligi ogrenim ucreti ne kadar?
```

LLM:

```json
{
  "primary_intent": "tuition",
  "required_slots": ["student_type", "faculty_or_program"],
  "missing_slots": ["student_type"]
}
```

Ana orchestrator bunu gorur ve finance agent'a eksik bilgiyle gitmez. Once kullaniciya sorar:

```text
Turk ogrenci misiniz, uluslararasi ogrenci misiniz?
```

Fakat oturum metadata'sinda bilgi zaten varsa eksik sayilmaz.

Ornek:

- User login olmus ve `student_type=Turk ogrenci` varsa `student_type` missing kabul edilmez.
- `student_faculty` veya `student_department` varsa program/fakulte slotu dolu sayilabilir.
- `auth` slotu login varsa eksik degildir.

Bir istisna da eklendi:

`academic_calendar` niyetinde fakulte/program eksigi dikkate alinmaz. Cunku genel akademik takvim bolume bagli degildir.

### 13. Akademik Takvim Parser

Canli testlerde `Final sinavlari ne zaman?` sorusu bazen RAG kaynakta PDF'i buldugu halde LLM tarafindan net cevaplanamiyordu. Cunku resmi PDF'te "final" kelimesi yerine "Yariyil Sonu Sinavlari" yaziyor.

Bu nedenle registration agent'a structured PDF parser eklendi.

Bu parser:

- Akademik takvim PDF'ini okur.
- Ilgili satiri bulur.
- Tarihleri regex ile cikarir.
- Cevabi VT/structured kaynak olarak verir.

Desteklenen satirlar:

- `Yariyil Sonu Sinavlari`
- `Butunleme Sinavlari`
- `Yariyil Sonu Sinav Sonuclarinin Internetten Girilmesinin Son Gunu`

Bu farkli sorulari dogru ayirir:

```text
Final sinavlari ne zaman?
```

Bu sinav tarih araligini verir.

```text
Final sinavlarinin sisteme girilmesinin son gunu ne zaman?
```

Bu not/sonuc giris son gununu verir.

Bu cozum hardcoded tarih degildir; resmi PDF satirindan okur.

### 14. Cevap Sentezi ve Cift LLM Cagrisini Azaltma

Bir ara sistemde specialist agent LLM sentezi ve sonra global synthesis LLM sentezi birlikte calisabiliyordu. Bu hem maliyetli hem de riskliydi. Cunku ozetin tekrar ozetlenmesi kaynak detaylarini kaybettirebiliyor.

Yeni prensip:

- Cok departmanli cevaplarda global synthesis ana birlestirmeyi yapar.
- Specialist LLM sentezi varsayilan olarak azaltildi.
- `force_llm_synthesis` yalniz gerekli tek departmanli karmasik akislarda kullanilir.

Bu sayede cevaplar daha hizli ve daha az tekrarli hale geldi.

### 15. Cevap Temizleme

LLM bazen kullaniciya gitmemesi gereken metinler uretebiliyor:

- Ingilizce kelime sizintisi.
- Prompt/rol kalintisi.
- `cumle bulunamadi`.
- `yonlendir`.
- `Test,` prefixleri.
- Yarim kalan cumle.
- Tekrar eden satirlar.

Final answer cleaner bunlari temizler.

Son canli testte gorulen:

```text
certain
```

kelimesi icin:

```text
certain -> belirli
```

donusumu eklendi.

Ayrica:

```text
onayigereken -> onayi gereken
```

bosluk artefakti duzeltildi.

### 16. Benchmark ve Diagnostics

Sistemin kalitesi sadece manuel Slack testleriyle degil, benchmark ile de olculuyor.

`scripts.run_quality_benchmark` sunlari yapar:

- API health preflight.
- Warm-up.
- Cache bypass.
- 25 soruluk kalite benchmark'i.
- Departman dogrulugu.
- Uretim modu dogrulugu.
- Anahtar bilgi kapsami.
- Temiz kalite kontrolu.
- LLM role/model raporu.
- A2A diagnostics before/after delta.
- Agent task failure delta.

Bu onemli cunku dagitik sistemlerde kullanici cevabi dogru gorunse bile arka planda agent timeout veya fallback yasanabilir. Diagnostics delta bu tur gizli problemleri gosterir.

### 17. Canli Slack Testlerinden Ogrenilenler

Slack testleri su problemleri yakaladi:

- `guncel duyur` once yanlis route olabiliyordu; capability normalizer ile duzeldi.
- `Staj basvuru adimlari` bazen duyuruya dusuyordu; announcement topic shift kurallari iyilestirildi.
- `Diş hekimliği dönem ücreti` follow-up'i profil fakültesine kayiyordu; explicit unit onceliklendirildi.
- `Final sınavları ne zaman?` fakülte sormaya basladi; academic calendar slot bypass eklendi.
- `Final sınavlarının sisteme girilmesinin son günü` yanlis satiri okuyordu; sonuc giris satiri parser'a eklendi.
- `Sınav notlarımı nereden görebilirim` kisisel GNO cevabina dusuyordu; prosedur olarak ayrildi.
- `şey başvuru ne zaman` RAG'dan eski tarih uretmeye calisiyordu; application type clarification'a alindi.

Bu testler sistemin sadece benchmark sorularina degil, gercek kullanici yazimlarina da daha dayanikli olmasini sagladi.

### 18. Neyi Bilerek Yapmadik

Su an sistem iyi bir demo/bitirme projesi seviyesinde. Ancak production platformu icin bazi isler bilerek ertelendi:

- Kubernetes deployment.
- Service mesh.
- Autoscaling.
- Queue/backpressure.
- Gelismis distributed tracing.
- Gercek external A2A partner entegrasyonu.
- Production retry policy.
- Slack bot lifecycle otomasyonu.

Bunlar degerli ama su an kapsam buyutur. Bizim hedefimiz once calisan, test edilebilir, mimari olarak tutarli dagitik A2A prototipi sabitlemekti.

### 19. Sistemin Su Anki En Dogru Tanimi

Sistemi soyle anlatmak en dogrusu:

```text
Bu proje, klasik RAG tabanli universite destek botundan A2A uyumlu dagitik agent mimarisine evrildi. Ana API, departman agent'lari, uzman agent'lar, duyuru/etkinlik capability agent'lari ve merkezi retrieval servisi ayri calisiyor. Slack uzerinden gercek kullanici akisiyla test edilebiliyor. LLM routing semantik niyet, capability ve eksik slotlari belirliyor; deterministik katman auth, DB, kaynak ve tool guvenligini sagliyor. Production-grade Kubernetes/service mesh gibi altyapi isleri bilincli olarak sonraki asamaya birakildi.
```

Bu ifade hem iddiali hem de teknik olarak durustur.
