# Nisan 2026 Routing, RAG ve Follow-up Guncelleme Notlari

> Durum Notu (Nisan 2026): Bu belge 13 Nisan civarindaki routing/RAG/follow-up iyilestirmelerinin tarihsel kaydidir. Sonraki calismalarda routing LLM `canonical_query`, `primary_intent`, `required_slots` ve `missing_slots` sinyalleri uretmeye; deterministik katman da bunlari clarification ve guard kararlarinda kullanmaya basladi. En guncel mimari icin `A2A_DAGITIK_MIMARI_VE_CALISMA_OZETI.md` okunmalidir.

Bu belge, 13 Nisan 2026 civarinda benchmark sonuclarina ve canli follow-up testlerine bakilarak yapilan degisiklikleri tek yerde toplar.

Amac yalnizca "hangi dosya degisti" bilgisini vermek degildir. Bu not, ekipte yeni okuyacak bir kisinin su uc soruya cevap bulabilmesi icin yazilmistir:

1. Hangi problem gozleniyordu?
2. Bu problemi kapatmak icin ne degistirildi?
3. Bu degisikligin sistem davranisina beklenen etkisi nedir?

Bu nedenle asagidaki maddeler, benchmark dalgasinda yapilan routing ve RAG degisikliklerini de, sonrasinda follow-up motoru etrafinda yapilan dayaniklilik ve kalite iyilestirmelerini de birlikte anlatir.

## 1. Genel Resim

Bu donemde iki buyuk iyilestirme ekseni vardi:

* **Routing ve retrieval kalitesi:** Yanlis departmana gitme, alakasiz belge secme, halusinasyon ve bozuk LLM JSON ciktilari.
* **Cok turlu konusma kalitesi:** Follow-up sorularin baglam kaybetmesi, kisa sorularin standalone sanilmasi, rewrite'in konuyu bozmasi, sosyal kisa cevaplarin anlamsiz QA akisina dusmesi.

Yapilan degisiklikler de temelde bu iki eksene dagilmaktadir.

## 2. Routing Katmani ve Niyet Tespiti

Ilgili dosyalar:

* `src/routing/routing_policy.py`
* `src/routing/router.py`

### 2.1 Soru Turunu Daha Dogru Tespit Etme

Routing policy tarafinda marker setleri genisletildi.

Bunun iki temel nedeni vardi:

* Bazi sorular yeterince ozellestirilmedigi icin yanlis departmana gidiyordu.
* LLM routing bazi durumlarda parse edilemediginde sistem kural tabanli fallback'e dusuyor, fakat bu fallback ince ayrimlari kaciriyordu.

Bu kapsamda:

* **Sinav hakki / formal rule marker'lari** genisletildi.
  `sinav hakki`, `kac kez sinav`, `butunleme hakki`, `final sinavi sart` gibi kaliplar `academic_programs` tarafina daha dogru yonlenmeye basladi.
* **Duyuru marker'lari** eklendi.
  `guncel duyuru`, `son duyuru`, `yeni duyuru`, `duyuru var mi` gibi sorgularin mevcut belge koleksiyonlari ile dogrudan yanitlanamayacagi netlestirildi.
* **Kisisel veri marker'lari** genisletildi.
  `not ortalamam`, `kalan ders`, `akts durumu`, `staj durumum`, `kayit durumum` gibi yapilarin kisisel veri sinyali tasidigi daha tutarli yakalanmaya baslandi.

### 2.2 Yanlis Override ve Cakisma Duzeltmeleri

Router tarafinda birkac kritik override duzeltmesi yapildi:

* **Kisisel veri alias bug'i** duzeltildi.
  Kural var olmasina ragmen yanlis import/alias nedeniyle bazi override'lar fiilen hic calismiyordu.
* **Kisisel veri -> student_affairs override'i** sertlestirildi.
  Boylece `academic_programs`a kayan bazi kisisel durum sorgulari dogru departmana cekildi.
* **CAP vs Erasmus cakismasi** engellendi.
  Onceden `program + basvuru` benzeri ortak sinyaller bazen Erasmus sorusunu CAP override'ina sokuyordu.
  Buna `not has_international_markers(...)` guard'i eklendi.
* **Ikinci departman ekleme mantigi** sikilastirildi.
  Eski davranista dusuk skorlu ikinci departmanlar da gereksiz yere parallel routing'e dahil olabiliyordu.
  Bunun icin:
  * minimum ikinci departman skoru eklendi
  * birinci departmanla maksimum skor farki daraltildi
  * hic uygun ikinci departman yoksa tek en iyi departmana dusme davranisi netlestirildi

### 2.3 Duyuru Sorgulari Icin Ozel Akis

Duyuru sorulari artik normal RAG akisina sokulmak yerine `CLARIFICATION` stratejisine yonlendiriliyor.

Bunun nedeni su:

* `Guncel duyurular neler?` tipi bir soru, statik belge arama sorusu degildir.
* Bu tip sorular canli veri, web, API veya ayrica guncellenen bir duyuru kaynagi gerektirir.
* Belge tabanli RAG bunu dogrudan bilmedigi icin alakasiz PDF veya yonergelerden yanit uretmeye calisiyordu.

Yeni davranis, "mevcut kaynakla cevaplayamiyorum"u daha dogru yerde soylemeye yoneliktir.

## 3. Groq JSON Dayanikliligi ve Prompt Daraltma

Ilgili dosyalar:

* `src/llm/prompt_templates.py`
* `src/routing/router.py`

Canli testlerde Groq tarafinda `json_validate_failed` tipinde hatalar goruldu.
Ozellikle routing veya yapisal cikti istenen prompt'larda model bazen:

* fazla uzun reasoning uretiyor
* kacis karakterleri ekliyor
* bozuk JSON blogu donduruyordu

Bu sorunu azaltmak icin iki seviyeli yaklasim uygulandi:

### 3.1 Prompt Daraltma

Yapisal cikti prompt'unda `reasoning` alani:

* kisaltilmis
* karakter kullanimi sinirlanmis
* ornekle desteklenmis

Bunun amaci modelin serbest, uzun, kacis karakteri iceren aciklamalar uretmesini azaltmaktir.

### 3.2 Regex Tabanli Kurtarma

`router.py` icinde JSON parse hata verirse artik dogrudan kural tabanli fallback'e dusulmuyor.
Once cevap icinden regex ile kurtarilabilir bir JSON blogu aranip ayiklanmaya calisiliyor.

Bu sayede:

* "neredeyse dogru" olan LLM cevaplari tamamen cope gitmiyor
* gereksiz fallback sayisi azaltiliyor
* routing kalitesi ozellikle orta karmasikliktaki sorularda daha stabil kaliyor

## 4. RAG, Reranker ve Halusinasyon Kalkanlari

Ilgili dosyalar:

* `src/agents/base.py`
* `src/rag/reranker.py`
* `.env`

Bu alandaki ana hedef, "ilgili gibi gorunen ama aslinda alakasiz belge" problemine karsi katmanli koruma kurmakti.

### 4.1 FAQ Blok Secimi Iyilestirildi

FAQ blok secimi artik yalnizca ham ortak kelime sayisina bakmiyor.

Eklenen iyilestirmeler:

* yaygin ve ayirt edici olmayan kelimeler dusuk agirlik aliyor
* bloktaki soru kismi daha yuksek agirlik aliyor
* daha belirleyici query token'lari daha fazla etkili oluyor

Beklenen etki:

* `kayit` gibi cok genel kelimeler, alakasiz bloklari gereksiz sekilde one cikarmasin
* `ucret`, `yenileme`, `devam`, `bagil degerlendirme` gibi ayirt edici kelimeler daha belirleyici olsun

### 4.2 LLM Context Filtreleme

Reranker dusuk skor vermis bir kaynagi, LLM sentezine dogrudan vermek artik daha zor.

Yeni davranis:

* belirli bir skordan dusuk kaynaklar
* ek bir keyword overlap testinden geciyor
* sorgu ile kaynak arasinda anlamli bir ortaklik yoksa o kaynak LLM context'ine hic eklenmiyor

Bu, "LLM gormese uyduramayacagi" alakasiz kaynaklari en erken noktada kesmeye yarar.

### 4.3 `_compute_keyword_overlap`

Bu yardimci metod, query ile kaynak arasindaki temel anahtar kelime ortusmesini olcer.
Asagidaki sebeple eklendi:

* reranker skoru tek basina her zaman yeterli degil
* ozellikle Turkce'de benzer gorunen ama farkli baglamdaki kelimeler yaniltici olabiliyor

Bu metod hem LLM context filtrelemede hem de dusuk kaliteli kaynaklari elemede kullaniliyor.

### 4.4 Prompt Tarafinda Halusinasyon Kurallari

Hem genel QA prompt'unda hem de specialist synthesis prompt'unda su ilke netlestirildi:

* alakasiz kaynak varsa yok say
* tarihler, sayilar, yuzdeler, sureler ancak kaynakta acikca varsa kullan
* kaynakta olmayan spesifik veriyi tahmin etme

Bu degisiklikler, ozellikle "ilgili gorunen ama aslinda farkli prosedure ait kaynaklar" nedeniyle olusan uydurma cevaplari azaltmak icin yapildi.

### 4.5 Reranker Modeli ve Kalibrasyon

Reranker tarafi benchmark sonuclarina gore yenilendi:

* model cok dilli `nreimers/mmarco-mMiniLMv2-L6-H384-v1` olarak degisti
* yeni modele uygun kalibrasyon shift/scale degerleri guncellendi
* direct-RAG, LLM-min ve no-useful esikleri bu yeni dagilima gore ayarlandi

Bu degisikliklerin nedeni:

* onceki modelin Turkce semantikte bazi sorularda yanlis belgeyi one cikarmasi
* eski esiklerin yeni skor dagilimi ile uyumsuz kalmasi

### 4.6 Sentez Modeli Yukseltmesi

`.env` tarafinda specialist ve global synthesis modeli `llama-3.3-70b-versatile` olarak yukseltilmistir.

Buradaki gerekce:

* sentez asamasi Turkce'yi daha iyi anlamali
* alakasiz kaynagi ayirt etmede daha guclu olmali
* spesifik bilgi cekme ve "bulunamadi" deme karari daha isabetli olmali

Bu degisiklik, routing modelinden farkli olarak kalite odakli bir upgrade'dir.

## 5. Follow-up Motoru ve Conversation Context Stabilizasyonu

Ilgili dosya:

* `src/db/conversation_context.py`

Bu alandaki degisiklikler, `scripts/followup_benchmark.py` ile gorulen cok turlu konusma hatalarina cevap olarak yapildi.

### 5.1 Kisa ve Sinyalsiz Sorgularin Follow-up Olarak Degerlendirilmesi

Onceden:

* `Taksitle odeyebilir miyim?`
* `Not ortalamasi kac olmali?`

gibi kisa ama baglama bagli sorular, acik marker yoksa standalone sayilabiliyordu.

Yeni davranis:

* state varsa
* soru cok kisa ve baglama bagimliysa
* LLM / heuristic follow-up ihtimali icin aday olarak ele aliniyor

Bu sayede onceki konu baglami daha sik korunuyor.

### 5.2 Heuristic Kararin LLM Tarafindan Ezilmesini Engelleme

Onceden heuristic "bu follow-up" dedikten sonra LLM `is_follow_up=false` dondururse sistem yine standalone'a kayabiliyordu.

Yeni davranis:

* guclu heuristic follow-up karari artik LLM tarafindan keyfi sekilde geri alinmiyor

Bu duzeltme, ozellikle kisa marker'li sorularda onemliydi.

### 5.3 Rewrite Dogrulama: Baglam Koruma

Follow-up rewrite artik yalnizca gramer olarak degil, baglam olarak da kontrol ediliyor.

Kontrol edilen basliklar:

* aktif topic korunuyor mu
* rewrite yeni ve ilgisiz bir topic enjekte ediyor mu
* rewrite fazla genisliyor mu
* rewrite mevcut follow-up'i daha dogru bir standalone sorguya ceviriyor mu

Uygun degilse rewrite reddediliyor ve heuristic fallback kullaniliyor.

### 5.4 Soru Tipi Korunumu

Yeni guard ile rewrite'in soru tipini bozmasi engellendi.

Korunan tipler arasinda:

* `ne zaman`
* `ne kadar`
* `var mi`
* `nedir`
* `nasil`
* `nereden`

Ornek etki:

* `Ne zaman yapilir?` -> `Nasil yapilir ve ne zaman?` gibi gereksiz genislemeler reddediliyor
* `GNO sarti var mi?` -> `ne zaman` tipine kayan rewritelar reddediliyor

### 5.5 Topic Specificity ve Rewrite Seed'leri

Topic cikarimi daha spesifik olmaya getirildi.
Ayrica topic adlarindan kullaniciya daha dogal gelen rewrite seed'leri uretildi.

Ornekler:

* `Yatay ve Dikey Gecis` -> `yatay gecis`
* `Kayit Dondurma ve Silme` -> `kayit dondurma`
* `CAP / Cift Anadal` -> `cap basvurusu`
* `Staj ve Uygulamali Egitim` -> `staj`

Bu degisikliklerin amaci, `topic hakkinda: ...` gibi zayif fallback'ler yerine daha arama-dostu, daha islevsel sorgular uretmektir.

### 5.6 Bos Clarification ve Zayif Ara Cevaplari Bastirma

LLM follow-up cagrisi bazen `needs_clarification=true` ve bos veya dusuk kaliteli departman/icerik dondurebiliyordu.

Yeni davranis:

* eger heuristic rewrite guvenilir bicimde yapilabiliyorsa
* LLM clarification cikisi kabul edilmiyor

Bu, `departments=[]` gibi araya giren garip cevaplarin kullaniciya yansimasini azaltir.

### 5.7 Pronoun-Led Follow-up Guard

`bunun`, `onun`, `bunlar`, `onlar` gibi zamirle gelen follow-up'larda LLM bazen onceki cevaptaki alt detaya yapisip aktif konuyu bozuyordu.

Ornek hata:

* onceki konu CAP basvurusu
* onceki alt detay not ortalamasi
* yeni soru: `Bunun icin hangi belge gerekli?`
* yanlis rewrite: `CAP not ortalamasi icin hangi belge gerekli?`

Yeni guard:

* rewrite aktif topic disinda yeni detay token'lari ekliyorsa reddediliyor
* gerekirse heuristic rewrite'a dusuluyor

Bu degisiklik, ozellikle CAP follow-up zincirinde kritik fayda sagladi.

### 5.8 Kisa Follow-up'larda Object Drift Guard

Pronoun icermeyen ama cok kisa ve baglama duyarli sorularda da benzer bir bozulma goruldu.

Ornek:

* `Suresi ne kadar?`
* LLM bunu bazen `staj basvurusu suresine ne kadar zaman var?` gibi gereksiz detayli bir nesneye ceviriyordu

Yeni guard:

* kisa, baglama bagli follow-up'larda
* heuristic anchor'in disinda yeni nesne/detail token gelirse
* rewrite reddediliyor ve fallback devreye giriyor

Bu guard, soru tipini korurken nesne kaymasini ayri bir problem olarak ele alir.

## 6. Kisa Sosyal Cevaplar Icin No-op / Acknowledgement Akisi

Ilgili dosya:

* `src/orchestrators/main.py`

`Evet`, `Tamam`, `Tesekkurler`, `Sagol`, `Hayir` gibi kisa sosyal cevaplar onceden normal QA akisina girip anlamsiz belge aramalarina sebep olabiliyordu.

Yeni davranis:

* bu tip sorgular routing'e gitmiyor
* kisa, dogrudan acknowledgement cevabi donuyor

Bu, follow-up sisteminin gereksiz yere "sosyal cevap"lari bilgi sorgusu sanmasini engeller.

## 7. Registration Tarafinda Kaynak Secimi ve Source-only Guvenligi

Ilgili dosyalar:

* `src/agents/student/registration_utils.py`
* `src/agents/student/registration_agent.py`

Bu bolum, "rewrite dogru ama secilen chunk yanlis" problemi icin guclendirildi.

### 7.1 Sonuc Siralama Mantigi Zenginlestirildi

Registration sonuc secimi artik yalnizca tek skorla yapilmiyor.
Su faktorler birlikte ele aliniyor:

* topic match
* conflicting topic penalty
* query aspect match
* FAQ / micro-scenario penalty
* reranker skoru

Bu sayede ayni genel topic icinde bile daha dogru belge parcasi secilebiliyor.

### 7.2 Query Aspect Modeli Eklendi

Registration sorgulari icin temel alt niyetler ayristirildi:

* `document`
* `timing`
* `condition`
* `quota`
* `fee`
* `process`

Boylece sistem su ayrimi daha iyi yapabiliyor:

* "hangi belge gerekli?"
* "ne zaman yapilir?"
* "kosullari nelerdir?"
* "kontenjan var mi?"
* "ucreti nedir?"

### 7.3 FAQ ve Personal Micro-scenario Chunk Penalty

Bazi FAQ veya SSS parcaciklari, gercek soruyu dogrudan yanitlamayan, fazla dar ve kisi odakli mikro senaryolar tasiyordu.

Ornek sinyaller:

* `ogrencisiyim`
* `miyim`
* `zorunda miyim`
* `sss`
* `faq`

Bu tip chunk'lar, ozellikle zaman/belge/kosul gibi daha genel sorularda geri plana itilmeye baslandi.

### 7.4 Source-only Cevaplar Icin Guvenlik Filtresi

`registration_agent.py` tarafinda source-only mod daha ihtiyatli hale getirildi.

Yeni davranis:

* secilen sonuc, query aspect ile uyumsuzsa
* veya yanlis FAQ / micro-scenario parcasi ise
* artik dogrudan authoritative cevap olarak yuzeye cikmiyor

Bunun yerine:

* daha guvenli aday varsa o seciliyor
* yoksa daha durust bir fallback / daraltma mesaji donuluyor

Bu degisiklik, `B-Tur3` ve `B-Tur4` benzeri kayit dondurma follow-up'larinda gozlenen yanlis chunk sorunlarini azaltmak icin yapildi.

### 7.5 CAP ve Staj Topic Cakismalarina Karsi Penalty

Bazi registration belgeleri, farkli alt konu kelimeleri nedeniyle yanlis soruya siziyordu.

Ozellikle:

* CAP sorusuna staj belgesi
* belge sorusuna ilgisiz procedure chunk'i

gibi durumlara karsi conflict penalty ve topic ayristirma mantigi guclendirildi.

## 8. Finance / Tuition Tarafinda Politika vs Kisisel Sorgu Ayrimi

Ilgili dosya:

* `src/agents/finance/tuition_utils.py`

Buradaki ana sorun, bazi genel politika sorularinin kisisel auth gerektiren sorgu gibi yorumlanmasiydi.

Ornek:

* `Taksitle odeyebilir miyim?`

Bu soru:

* ozel bakiye sorgusu degildir
* genel odeme politikasini sorar

Bu nedenle `tuition_utils.py` tarafinda:

* `odeyebilir miyim`
* `taksitle`
* `taksitli`

gibi kaliplar politika override'ina dahil edildi veya testlerle guvence altina alindi.

Beklenen etki:

* sistem bu soruyu gereksiz kimlik dogrulama akisina sokmaz
* yine de `harc borcum var mi` gibi gercek kisisel sorgular kisisel olarak kalir

## 9. Cevap Temizligi ve Dil Kalitesi

Ilgili dosya:

* `src/orchestrators/response_utils.py`

Canli kosularda bazi cevaplarda yabanci kelime sızıntilari ve bozuk Unicode gorunumleri gozlendi.

Bu nedenle:

* `following`
* `informatie`
* `several`
* `siguientes`
* `once_online`
* `por favor`
* `ademas`
* `tambien`

gibi kaliplar icin ek temizlik yapildi.

Ayrica `unicodedata` tabanli ek bir normalizasyon katmani eklendi.
Bu katman:

* Turkce icin gerekli karakterleri korumaya calisir
* yabanci diacritic sızıntilari normalleştirir
* `he thong` turevi bozulmalari `sistem` gibi daha anlamli bir karsiliga cekebilir

Amac, belge veya LLM cikisindan gelen yabanci/bozuk kelime kalintilarini son kullanici cevabinda azaltmaktir.

## 10. Sentez ve Degerlendirme Tarafindaki Ek Iyilestirmeler

Ilgili dosyalar:

* `src/orchestrators/synthesis_utils.py`
* `src/orchestrators/query_policy.py`
* `src/evaluation/key_fact_matching.py`
* `scripts/run_quality_benchmark.py`

Bu donemde yalnizca routing ve follow-up degil, benchmark yorumlamasi ve sentez tarafi da iyilestirildi.

Yapilan ek adimlar:

* global synthesis girdisi daha notr hale getirildi
* kismen yararli ama tam cevap olmayan bazi department cevaplari da senteze alinabilir hale getirildi
* `kayit dondurma + harc/ucret` turu sorularda finance katkisi daha guclu tutuldu
* key fact matching tarafinda sayi, hafta, aksan ve yazim varyantlari normalize edildi

Bu degisiklikler benchmark sonuclarinin daha anlamli okunmasi ve otomatik kalite olcumunun daha adil olmasi icin yapildi.

## 11. Test Kapsami

Ilgili test dosyalari:

* `tests/unit/test_conversation_context.py`
* `tests/unit/test_registration_utils.py`
* `tests/unit/test_response_utils.py`
* `tests/unit/test_tuition_utils.py`

Eklenen / guncellenen testler su davranislari kilitler:

* kisa sinyalsiz follow-up tespiti
* LLM'nin heuristic follow-up kararini ezememesi
* context kaybettiren rewrite'in reddi
* soru tipi degistiren rewrite'in reddi
* bos clarification cevabinin bastirilmasi
* pronoun-led rewrite detail drift reddi
* kisa follow-up object drift reddi
* CAP vs staj topic conflict secimi
* belge/timing/kosul sorgularinda daha dogru registration chunk secimi
* FAQ / micro-scenario source-only penalty
* taksit sorusunun kisisel sayilmamasi
* yabanci kelime ve Unicode sızıntilarinin temizlenmesi

Not:

* Bu donemde uzun benchmark ve E2E kosulari kullanici tarafinda manuel kosturulmustur.
* Kod degisikligi sonrasi hizli dogrulama icin sentaks / import seviyesi kontroller de uygulanmistir.

## 12. Pratik Etki Olarak Neler Degisti?

Bu degisikliklerden sonra sistemin hedeflenen davranisi su sekilde toparlanabilir:

* Routing, dusuk kaliteli ikinci departmanlari daha az ekler.
* Duyuru sorulari statik belge aramasina zorlanmaz.
* Kisisel veri sorulari daha dogru departmana gider.
* Alakasiz dusuk kaliteli kaynaklar LLM'e daha az gosterilir.
* Follow-up motoru kisa sorularda onceki konuyu daha iyi korur.
* Rewrite, konuyu veya soru tipini bozdugunda fallback'e dusulur.
* `Evet`, `Tesekkurler` gibi sosyal mesajlar anlamsiz QA akisina girmez.
* Registration source-only cevaplari daha guvenli secilir.
* Taksit gibi politika sorulari gereksiz auth akisina dusmez.
* Son kullanici cevabinda yabanci kelime ve bozuk Unicode kalintilari azalir.

## 13. Halen Izlenmesi Gereken Noktalar

Bu belge "her sey tamamen bitti" demek icin degil, mevcut resmi netlestirmek icin yazildi.
Asagidaki maddeler halen dikkatle takip edilmelidir:

* registration tarafinda bazi zaman/kosul sorularinda yanlis FAQ chunk'in yeniden yuzeye cikma riski
* international ve Erasmus tarafi sentez kalitesinin dalgalanmasi
* rate limit veya provider bozulumunda fallback davranisinin kaliteye etkisi
* yabanci kelime sızıntilarinin nadir edge-case'leri
* follow-up rewrite'larinda LLM'in ara sira gereksiz detay ekleme egilimi

Ozellikle son eklenen dar korumalarin tam E2E etkisi, yeni benchmark ve follow-up kosularinda tekrar izlenmelidir.

## 14. Ozet

Bu donemdeki degisikliklerin ortak temasi sunlardir:

* sistemi daha "akilli" yapmak kadar daha "ihtiyatli" yapmak
* alakasiz kaynagi daha erken elemek
* follow-up'ta konuyu koruyup gereksiz LLM yaraticiligini sinirlamak
* kural tabanli fallback'leri daha guvenilir hale getirmek
* zayif veya yari dogru durumlarda daha durust cevap vermek

Kisa ifade ile:

* **Routing daha secici**
* **RAG daha filtreli**
* **Follow-up daha dayanikli**
* **Source-only cevaplar daha temkinli**
* **Cevap metni daha temiz**

Bu belge, ilgili benchmark raporlari ve teknik dokumanlarla birlikte okunursa Nisan 2026'daki iyilestirme dalgasinin teknik mantigi daha rahat takip edilebilir.
