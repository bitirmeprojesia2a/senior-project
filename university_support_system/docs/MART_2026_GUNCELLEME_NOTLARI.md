# Mart 2026 Guncelleme Notlari

Bu dokuman, proje uzerinde Mart 2026 boyunca yapilan guncellemeleri, dogrulamalari ve kalan teknik borclari tek yerde toplar. Bazi eski faz dokumanlarinda yer alan anlatilar tarihsel baglam tasidigi icin, mevcut repo durumunu degerlendirirken bu belge oncelikli referans kabul edilmelidir.

## 1. Mimari ve Sozlesme Guncellemeleri

### 1.1 Departman Sozlesmesi

Aktif cekirdek artik dort ana departman tanir:

* `finance`
* `it_support`
* `student_affairs`
* `academic_programs`

Bu noktada onemli standardizasyon:

* Eski `it` ismi, veri klasorleri ve koleksiyonlarla uyumlu olacak sekilde `it_support` olarak standartlastirildi.
* `academic_programs` artik yalnizca prompt veya loader seviyesinde degil, cekirdek sozlesmenin parcasi olarak ele alinmaktadir.

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
* `it_support_docs`

Kaynak klasor -> koleksiyon eslemesi:

* `data/raw/student_affairs` -> `student_affairs_docs`
* `data/raw/academic_programs` -> `academic_programs_docs`
* `data/raw/finance` -> `finance_docs`
* `data/raw/it_support` -> `it_support_docs`

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
* `it_support`
* `student_affairs`
* `academic_programs`

Not:

* LLM katmani hazirdir, ancak aktif retrieval secimi yalnizca LLM'e bagimli olacak sekilde zorlanmamistir.
* Mevcut repo yuzeyinde retrieval planlamasinin onemli bir kismi halen kural tabanli ve deterministik kalir.

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

Bu nedenle repo icinde ayrismis bir test stratejisi belgelenmistir:

* `smoke`
* `model`
* `slow`

## 6. Dokumantasyon Temizligi

Su belgeler Mart 2026 guncel duruma gore revize edilmistir:

* `README.md`
* `docs/KURULUM_VE_CALISTIRMA.md`
* `docs/FAZ_1_TEKNIK_DOKUMANTASYON.md`
* `docs/FAZ_2_TEKNIK_DOKUMANTASYON.md`
* `docs/PROJE_ANATOMISI_KILAVUZU.md`

Bazi eski belgelerde tarihsel baglam korunurken, bu belge onlari tamamlayan ve yer yer override eden bir merkez not olarak eklenmistir.

## 7. Mevcut Guclu Yonler

* RAG cekirdegi moduler ve ayri sorumluluklara bolunmus durumda.
* Dinamik departman ve koleksiyon yapisi tek-koleksiyon bagimliligini azaltmis durumda.
* LLM katmaninda health, fallback, stream ve JSON dogrulama yetenekleri net.
* GPU hazirligi kod ve ortam seviyesinde dogrulanmis durumda.
* Test katmani ozellikle unit seviyede guclu.

## 8. Kalan Teknik Borclar

### 8.1 Yapi

* Merkezi departman kaydi sayesinde departman taniminin cekirdek kod yuzeyine yayilmasi daha kontrollu hale gelmistir.
* Buna ragmen yeni departman icin veri klasoru, soru havuzu ve integration kapsamini genisletme ihtiyaci devam eder.

### 8.2 RAG Degerlendirme Metodu

* Degerlendirme tarafinda dosya adi heuristiklerine dayali kisimlar halen vardir.
* Icerik tabanli veya daha saglam etiketli bir olcum modeli gelecekte daha dogru olur.

### 8.3 Test Stratejisi

* Agir integration testleri gunluk gelistirme akisinda pahali kalabilir.
* Daha net smoke/model/slow ayrimi ve buna uygun komutlar uzun vadede repo ergonomisini iyilestirir.

## 9. Not Edilen Gelecek Iyilestirme

Ozellikle not dusulen sonraki teknik hedef:

* Merkezi departman kaydini kullanarak yeni departmanlar icin veri, evaluation ve integration genisletmesini daha otomasyonlu hale getirmek
* Eklenen departmanin tum kod parcalarinda tutarli sekilde taninmasini surdurmek

Bu madde mevcut backlog icinde halen onemli bir mimari ergonomi adayidir.
