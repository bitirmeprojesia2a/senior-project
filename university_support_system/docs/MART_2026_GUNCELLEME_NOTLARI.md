# Mart 2026 Guncelleme Notlari

Bu dokuman, proje uzerinde Mart 2026 boyunca yapilan guncellemeleri, dogrulamalari ve kalan teknik borclari tek yerde toplar. Bazi eski faz dokumanlarinda yer alan anlatilar tarihsel baglam tasidigi icin, mevcut repo durumunu degerlendirirken bu belge oncelikli referans kabul edilmelidir.

## 1. Mimari ve Sozlesme Guncellemeleri

### 1.1 Departman Sozlesmesi

Aktif cekirdek artik uc ana departman tanir:

* `finance`
* `student_affairs`
* `academic_programs`

Bu noktada onemli durum:

* `academic_programs` artik yalnizca prompt veya loader seviyesinde degil, cekirdek sozlesmenin parcasi olarak ele alinmaktadir.
* `it_support` onceki denemelerden kalan tarihsel bir departman adidir; mevcut aktif cekirdek sozlesme ve veri kaynaklari bu departmani kapsamaz.

Mart 2026 sonundaki ek iyilestirme ile departman tanimi yalnizca enum seviyesinde degil, merkezi bir departman kaydi uzerinden de yonetilmektedir. Bu kayit:

* gosterim adini
* routing aciklamasini
* retriever anahtar kelimelerini
* kaynak klasor bilgisini

tek yerde toplar. Boylece yeni departman eklemek icin degisiklik noktasi azaltmistir.

### 1.2 Koleksiyon Stratejisi

RAG tarafi tek bir sabit koleksiyona bagli degildir. Koleksiyonlar ana departman bazinda dinamik cozulur:

* `student_affairs_docs`
* `academic_programs_docs`
* `finance_docs`

Kaynak klasor -> koleksiyon eslemesi:

* `data/raw/student_affairs` -> `student_affairs_docs`
* `data/raw/academic_programs` -> `academic_programs_docs`
* `data/raw/finance` -> `finance_docs`

Bu dinamik yapi su alanlara yansitilmistir:

* `src/core/constants.py`
* `src/rag/document_loader.py`
* `src/rag/indexer.py`
* `src/rag/pipeline.py`
* `src/rag/retriever.py`
* `scripts/index_documents.py`
* `scripts/query_db.py`
* `scripts/test_hybrid_search.py`
* `scripts/compare_collections.py`
* `scripts/evaluate_rag.py`

### 1.3 Academic Programs Metadata Genislemesi

`academic_programs` belgeleri icin metadata modeli genisletilmistir:

* `department`
* `subcategory`
* `bolum`
* `bolum_adi`

Kural:

* Tek net bolum eslesmesi varsa ilgili bolum kullanilir.
* Belge birden fazla bolume isaret ediyorsa `bolum="genel"` ve `bolum_adi="Genel"` atanir.

## 2. Retrieval ve Test Degerlendirme Guncellemeleri

### 2.1 Rule-Based Routing ve Kontrollu Fallback

Retrieval planlamasi su ilkeye cekilmistir:

* Ilk asamada kural tabanli departman puanlama kullanilir.
* Sorgu acik departman veriyorsa ilgili koleksiyona gidilir.
* Sinyal karisiksa birden fazla aday departman planlanabilir.
* Hardcoded tek koleksiyon bagimliligi azaltilmistir.

Sessiz `student_affairs_docs` varsayimlari cekirdekte buyuk oranda temizlenmistir. Kalan `student_affairs` baglari daha cok:

* is kuralina dayali mevcut soru havuzu
* integration test veri seti
* domain keyword mantigi

### 2.2 Soru Havuzu

`data/test/rag_test_questions.json` artik departman etiketli ortak havuzdur.

Guncel dagilim:

* 20 soru `student_affairs`
* 10 soru `academic_programs`

Integration fixture su an kontrollu sekilde yalnizca `student_affairs` alt kumesini kullanir. Bu, mevcut integration veri setini korumak icin bilincli olarak tutulmustur.

### 2.3 Reranker Dogrulamasi

Reranker hata yutma davranisinin testlerde gorunmez kalmamasi icin `CrossEncoderReranker.last_run_succeeded` alani eklenmistir.

Amac:

* reranker'in gercekten calisip calismadigini test seviyesinde gorulebilir kilmak
* hata oldugunda sadece "sonuc dondu" bilgisiyle yetinmemek

Bu degisiklik su testlerle korunmaktadir:

* `tests/unit/test_reranker.py`
* `tests/integration/test_rag_retrieval.py::TestHybridSearch::test_reranker_runs_successfully`

## 3. LLM Katmani Guncellemeleri

LLM katmani aktif cekirdekte var olan ama onceki dokumanlarda eksik veya daginik kalan yetenekleriyle birlikte tekrar belgelenmistir.

### 3.1 LLM Servis Yetenekleri

Aktif yetenekler:

* `LLMService.get_health()`
* `OllamaClient.get_health()`
* `OpenAIClient.get_health()`
* `LLMService.generate()`
* `LLMService.generate_stream()`
* JSON modu ve `_validate_json()` ile cikti dogrulamasi
* Ollama tarafinda retry
* OpenAI tarafinda kontrollu fallback

### 3.2 Prompt ve Routing Uyumu

`prompt_templates.py` icindeki departman yonlendirme prompt'u guncel cekirdekle hizalanmistir:

* `finance`
* `student_affairs`
* `academic_programs`

Not:

* LLM katmani artik yalnizca istemci/servis seviyesinde degil, `src/routing/router.py` uzerinden aktif routing akisinin parcasi haline gelmistir.
* Belirsiz sorgularda `DepartmentRouter`, kural tabanli skorlamadan sonra `LLMService` ile JSON tabanli yonlendirme fallback'i kullanabilir.
* Buna ragmen aktif retrieval secimi halen yalnizca LLM'e bagimli olacak sekilde zorlanmaz; kural tabanli ve deterministik katman korunur.

## 3.3 A2A ve Ajan Iskeleti

FAZ 3 kapsaminda daha once yalnizca dokumanda duran cok ajanli tasarim icin temel kod iskeleti eklenmistir:

* `src/a2a/helpers.py`
  * `a2a-sdk` tipleri ile `Task`, `Message`, `Artifact` ve `AgentCard` uretimi
* `src/agents/base.py`
  * uzman ajanlar icin ortak taban sinifi
* `src/agents/student/agents.py`
  * `registration_agent`, `graduation_agent`, `internship_agent`, `student_life_agent`
* `src/agents/academic/agents.py`
  * `curriculum_agent`, `regulation_agent`, `international_agent`
* `src/agents/finance/agents.py`
  * `tuition_agent`, `scholarship_agent`
* `src/agents/announcement/agent.py`
  * `announcements` tablosundan aktif duyurulari okuyabilen `announcement_agent`
* `src/orchestrators/main.py`
  * normal departman yanitlarina ilgili duyurulari ekleyebilen ana orkestrator akisi
* `src/orchestrators/department.py`
  * departman orkestrator iskeleti
* `src/orchestrators/main.py`
  * router ile departman orkestratorlerini birlestiren ana orkestrator
* `src/api/main.py`
  * FastAPI giris noktasi
  * `/health`, `/query`, `/agents` ve uygulama ici `/a2a/dispatch` endpoint'leri

Not:

* Bu ilk iskelet, aktif olarak `student_affairs`, `academic_programs` ve `finance` departmanlarina odaklanir.
* `it_support` ajani veya departman orkestratoru bu asamada aktif kod yoluna dahil edilmemistir.

## 4. GPU Hazirligi ve Model Dogrulama

### 4.1 Kod Duzeyi Hazirlik

Embedder ve reranker tarafina acik cihaz secimi eklenmistir.

Yeni ayarlar:

* `EMBEDDING_DEVICE`
* `RERANKER_DEVICE`

Gecerli degerler:

* `auto`
* `cpu`
* `cuda`

`auto` davranisi:

* CUDA gorunurse `cuda`
* aksi halde `cpu`

### 4.2 Mart 2026 Ortam Dogrulamasi

Yerel ortamda asagidaki teknik dogrulamalar yapilmistir:

* `torch 2.6.0+cu124`
* `torch.version.cuda == 12.4`
* `torch.cuda.is_available() == True`
* GPU gorunur: `NVIDIA GeForce RTX 3050 Laptop GPU`

Smoke dogrulamalari:

* `Embedder` `auto -> cuda` cozmus ve 1024 boyutlu embedding uretmistir.
* `CrossEncoderReranker` `auto -> cuda` cozmus, reranking basariyla tamamlanmis ve `last_run_succeeded == True` olmustur.
* `tests/integration/test_rag_retrieval.py::TestHybridSearch::test_reranker_runs_successfully` testi gecmistir.

## 5. Test Envanteri ve Pratik Durum

Guncel test envanteri:

* **206 unit test**
* **20 integration test**

Calisma notlari:

* Unit testler tam olarak gecmektedir.
* Hedefe yonelik reranker integration testi gecmistir.
* Integration smoke katmaninda `academic_programs_docs` mevcutsa bu koleksiyon icin de temel durum dogrulamasi yapilabilir.
* Daha agir integration testleri halen CPU/GPU yukleme, embedding, BM25 hazirligi ve koleksiyon tarama maliyeti nedeniyle gunluk dongude pahali olabilir.
* Yeni router, A2A helper ve orchestrator katmanlari icin ek unit testler eklendi:
  * `tests/unit/test_router.py`
  * `tests/unit/test_a2a_helpers.py`
  * `tests/unit/test_orchestrators.py`

## 6. Telemetry Entegrasyonu

Mart 2026 sonundaki ek entegrasyonlarla birlikte telemetry katmani uygulama akisina baglanmistir:

* `src/db/telemetry.py`
  * `QueryLog` ve `AgentTask` yazimi icin yardimci servis eklendi
* `src/orchestrators/main.py`
  * ana sorgular icin `QueryLog` kaydi olusturur ve sonuc durumunu gunceller
* `src/orchestrators/department.py`
  * uzman ajan cagrisini `AgentTask` kaydi ile izleyebilir

Bu kayitlar "en iyi caba" mantigiyla yazilir:

* veritabani erisimi varsa telemetry kalici olarak kaydedilir
* telemetry yazimi hata verirse kullanici sorgu akisi bozulmaz

## 7. Kisisel Veri Sorgulari

Mart 2026 sonundaki sonraki adimlardan biri olarak bazi uzman ajanlar yalnizca RAG uzerinden degil, kimligi dogrulanmis kullanicilar icin dogrudan veritabani uzerinden de cevap uretebilir hale getirilmistir:

* `tuition_agent`
  * ogrencinin guncel harc, odeme ve borc ozetini DB'den okuyabilir
* `scholarship_agent`
  * ogrencinin aktif burs ve son burs basvurusu bilgisini DB'den okuyabilir
* `graduation_agent`
  * ogrencinin GNO, kredi ve son ders ozetini DB'den okuyabilir

Bu akista genel/prosedurel sorular yine mevcut RAG + LLM yolunda kalir. DB yolu yalnizca:

* `student_id` mevcutsa
* `is_authenticated = true` ise
* sorgu kisisel veri sinifina giriyorsa

aktif olur.

Bu nedenle repo icinde ayrismis bir test stratejisi belgelenmistir:

* `smoke`
* `model`
* `slow`

## 8. OTP ve Session Auth Akisi

Mart 2026 sonundaki sonraki altyapi adimlarindan biri olarak mevcut `otp_codes`,
`verification_sessions` ve `slack_student_mapping` tablolarini kullanan gercek bir
auth servisi eklenmistir:

* `src/db/auth.py`
  * OTP olusturma
  * OTP dogrulama
  * session token uretimi
  * Slack kullanicisi ile ogrenci eslemesi
  * aktif oturumu token veya `slack_user_id` ile cozumleme
* `src/api/main.py`
  * `POST /auth/request-otp`
  * `POST /auth/verify-otp`
  * `POST /auth/resolve`
  * `POST /auth/logout`

Bu degisiklikle birlikte `/query` ve `/a2a/dispatch` endpoint'leri artik:

* dogrudan `student_id` + `is_authenticated` alabilir
* veya `session_token` ile kimlik baglamini otomatik cozumleyebilir
* veya aktif Slack eslemesi varsa `slack_user_id` uzerinden kullaniciyi tanuyabilir

Not:

* e-posta gonderimi su an `email_stub` modunda tutulmustur
* gelistirme modunda OTP preview kodu API yanitina eklenebilir
* gercek SMTP/kurumsal posta entegrasyonu sonraki fazdir

Ek olarak auth payload modelleri tekrar sadece API dosyasinda tutulmayip
`src/db/schemas.py` icinde ortak semalara alinmistir. Boylece auth ve query
istek/yanit modelleri tek yerde toplanmistir.

## 9. Office Contact Hazirligi

Agent fazina gecmeden once iletisim/ofis onerisi icin asgari altyapi
hazirlanmistir:

* `office_contacts` ORM modeli eklendi
* `src/db/office_contacts.py`
  * departman bazli iletisim kaydi getirme
  * ajan bazli filtreleme
  * API/uygulama katmani icin duzlestirilmis payload uretimi

Bu adim simdilik agent cevaplarina baglanmamistir; ancak uzman ajanlar
iletisim bilgisi sunmaya basladiginda kullanilacak veri zemini hazirdir.

## 10. Dokumantasyon Temizligi

Su belgeler Mart 2026 guncel duruma gore revize edilmistir:

* `README.md`
* `docs/KURULUM_VE_CALISTIRMA.md`
* `docs/FAZ_1_TEKNIK_DOKUMANTASYON.md`
* `docs/FAZ_2_TEKNIK_DOKUMANTASYON.md`
* `docs/PROJE_ANATOMISI_KILAVUZU.md`

Bazi eski belgelerde tarihsel baglam korunurken, bu belge onlari tamamlayan ve yer yer override eden bir merkez not olarak eklenmistir.

## 11. Mevcut Guclu Yonler

* RAG cekirdegi moduler ve ayri sorumluluklara bolunmus durumda.
* Dinamik departman ve koleksiyon yapisi tek-koleksiyon bagimliligini azaltmis durumda.
* LLM katmaninda health, fallback, stream ve JSON dogrulama yetenekleri net.
* GPU hazirligi kod ve ortam seviyesinde dogrulanmis durumda.
* Test katmani ozellikle unit seviyede guclu.

## 12. Kalan Teknik Borclar

### 12.1 Yapi

* Merkezi departman kaydi sayesinde departman taniminin cekirdek kod yuzeyine yayilmasi daha kontrollu hale gelmistir.
* Buna ragmen yeni departman icin veri klasoru, soru havuzu ve integration kapsamini genisletme ihtiyaci devam eder.

### 12.2 RAG Degerlendirme Metodu

* Degerlendirme tarafinda dosya adi heuristiklerine dayali kisimlar halen vardir.
* Icerik tabanli veya daha saglam etiketli bir olcum modeli gelecekte daha dogru olur.

### 12.3 Test Stratejisi

* Agir integration testleri gunluk gelistirme akisinda pahali kalabilir.
* Daha net smoke/model/slow ayrimi ve buna uygun komutlar uzun vadede repo ergonomisini iyilestirir.

## 13. Not Edilen Gelecek Iyilestirme

Ozellikle not dusulen sonraki teknik hedef:

* Merkezi departman kaydini kullanarak yeni departmanlar icin veri, evaluation ve integration genisletmesini daha otomasyonlu hale getirmek
* Eklenen departmanin tum kod parcalarinda tutarli sekilde taninmasini surdurmek

Bu madde mevcut backlog icinde halen onemli bir mimari ergonomi adayidir.

## 14. Son Review Notlari

Bugun eklenen LLM/A2A/announcement/kisisel veri akislarinin tekrar gozden gecirilmesi sirasinda sonraya birakilan teknik not:

* kisisel veri snapshot sorgularinda "en guncel kayit" secimi su an agirlikli olarak `id desc` ile yapilmaktadir; donem veya tarih bazli secim daha saglam olur

## 13. Agent Tasarimina Gecerken Notlar

Agent tasarimi fazina gecildiginde asagidaki ilkeler korunmalidir:

* her agent icin gorev siniri net olmali; "hangi sorgu kime ait" belirsiz kalmamali
* genel RAG cevaplari ile kisisel DB cevaplari ayni agent icinde bile ayrik ve acik dallarda tutulmali
* kimlik dogrulama gerektiren akislar acikca isaretlenmeli; sessiz veri sizmasi riski olmamali
* ortak davranislar taban sinifta veya yardimci servislerde kalmali; agentlar arasinda tekrar eden kod buyumemeli
* cross-agent yonlendirme yalnizca kurali net olan durumlarda kullanilmali; aksi halde agent sinirlari bulaniklasir
* announcement, telemetry ve benzeri ortak yardimci akislar agentlara daginik sekilde kopyalanmamali
* her agent icin cevap kaynagi acik olmali: RAG, DB veya hibrit
* yeni agent ekleme merkezi departman kaydi ve mevcut iskelet uzerinden yapilmali; daginik entegrasyon noktalarina geri donulmemeli
* fallback agent kullanimi gecici destek olarak kalmali; asil gorev dagilimi gercek uzman ajanlar uzerine kurulmalidir
* test stratejisi agent tasarimi ile birlikte dusunulmeli; her yeni agent en az temel unit test korumasi ile gelmelidir

## 14. A2A Uygulama Seviyesi Notu

Mart 2026 sonundaki mevcut durum:

* A2A yardimci tipleri ve gorev akisi uygulama icinde aktif olarak kullanilmaktadir
* departman orkestratorleri ve ana orkestrator A2A task modeli uzerinden haberlesir
* API tarafinda `/a2a/dispatch` endpoint'i ile uygulama ici dispatch yuzeyi vardir
* ancak bu yapi tam dagitik, ayri process veya ayri servisler halinde calisan bir dis A2A agi degildir

Bu nedenle bugun icin dogru ifade:

* "uygulama ici A2A iskeleti ve dispatch akisi eklendi"
* "tam dagitik A2A servislesmesi daha sonraki faza birakildi"
