# Sistem Denetim Bulgulari - 2026-04-28

Bu dosya, sistem geneli detayli denetim sirasinda yakalanan bulgulari ve yapilan duzeltmeleri izlemek icin tutulur.

## Kapsam

- RAG veri yukleme, registry ve Chroma tutarliligi
- Merkezi retrieval servisi ve A2A dagitik calisma
- Routing, canonical query, missing slot ve clarification akisi
- Slack ciktisi kalite problemleri
- Prompt, post-processing ve kalite korumalari
- Script/test bakim borclari

## Bulgular ve Duzeltmeler

### 1. Student affairs registry alt klasor reindex ile ezilmis gorunuyor

Durum:
- `data/metadata/doc_registry_student_affairs_docs.json` dosyasi `data/raw/student_affairs` kokunu degil, `data/raw/student_affairs/uygulama esasları` alt klasorunu kaynak olarak gosteriyordu.
- Registry `total_chunks=301` derken canli Chroma koleksiyonu `student_affairs_docs` icin `1786` chunk donduruyor.
- Bu canli RAG aramasini dogrudan bozmayabilir; ancak raporlama, bakım, tekrar indeksleme ve kalite analizi icin yaniltici.

Yapilan:
- `scripts/index_documents.py` icine partial reindex korumasi eklendi.
- Alt klasor ile `--reindex` calistirilirsa artik islem duruyor; bilincli kullanim icin `--allow-partial-reindex` gerekiyor.
- `src/rag/pipeline.py` registry yazimini non-reindex calismalarda merge edecek sekilde guncellendi. Boylece docx-only veya alt klasor upsert calismasi tum registry'yi ezmiyor.
- `scripts/audit_document_corpus.py` registry source root kontrolu ve Chroma/registry chunk sayisi karsilastirmasi yapacak sekilde genisletildi.

Kalan is:
- `student_affairs_docs` icin kok klasorden kontrollu full reindex yapilarak registry'nin kalici olarak duzeltilmesi gerekiyor.

### 2. Rollout `--skip-build` health kontrolu build metadata ile uyumsuzdu

Durum:
- `scripts.a2a_rollout --skip-build` her calismada yeni `A2A_BUILD_ID` bekliyordu.
- Ancak `SERVER_BUILD_ID` Docker image icine build-time ENV olarak gomuluydu; image yeniden build edilmezse container health eski build id donduruyordu.
- Sonuc: servisler healthy olsa bile rollout `Expected build metadata did not appear...` hatasina dusuyordu.

Yapilan:
- A2A compose ortak env bloklarina runtime metadata override eklendi:
  - `SERVER_APP_VERSION`
  - `SERVER_BUILD_ID`
  - `SERVER_BUILD_TIMESTAMP`
  - `SERVER_GIT_SHA`
  - `SERVER_IMAGE_REF`
- Boylece skip-build ile container recreate edildiginde health metadata da rollout'un bekledigi degerle uyumlu olur.

### 3. Routing canonical rewrite kritik anlam dusurebiliyordu

Durum:
- `Final sınavlarının sisteme girilmesinin son günü ne zaman?` gibi sorularda LLM canonical query, kritik `sisteme girilmesi/not girisi/sonuc` ifadesini dusururse soru generic final sinavi tarihine donusebiliyordu.
- Registration agent'in deterministic akademik takvim ayrimi dogruydu; risk canonical rewrite katmanindaydi.

Yapilan:
- `src/orchestrators/query_normalization.py` icindeki `rewrite_is_safe` guard'i guclendirildi.
- Orijinal sorguda grade-entry deadline sinyali varsa canonical sorguda da bu anlam korunmak zorunda.
- Regresyon testi eklendi: `tests/unit/test_query_normalization.py`.

### 4. Slack cevaplarinda yabanci kelime sizintisi icin regresyon testi eklendi

Durum:
- Slack ciktisinda `certain` gibi yabanci kelime sizintisi gorulmustu.
- `response_utils.clean_final_answer` zaten yaygin yabanci kelimeleri temizliyordu; fakat bu ornek testle sabitlenmemisti.

Yapilan:
- `tests/unit/test_response_utils.py` icine `certain -> belirli` temizligini kapsayan regresyon kontrolu eklendi.

### 5. Pytest cache ve gecici klasorler repo kokunde birikiyordu

Durum:
- `.pytest_cache`, `.codex_pytest_tmp` ve cok sayida `pytest-cache-files-*` klasoru goruldu.
- `pytest-cache-files-*` pattern'i ignore edilmiyordu.

Yapilan:
- `.gitignore` ve `.dockerignore` icine `pytest-cache-files-*/` eklendi.

Kalan is:
- Mevcut gecici klasorleri silmek icin once kullanici onayi alinmali.

### 6. A2A rollout testleri merkezi retrieval servisini hesaba katmiyordu

Durum:
- Rollout artik `retrieval-service` servisini `api` ve agent'lardan once ayaga kaldiriyor.
- `tests/unit/test_a2a_rollout.py` eski servis listesini bekledigi icin merkezi retrieval mimarisi test sozlesmesine yansimamis durumdaydi.

Yapilan:
- Rollout unit testleri `retrieval-service` servis ve health hedefini bekleyecek sekilde guncellendi.
- `tests/unit/test_a2a_rollout.py` ve `tests/unit/test_a2a_service_identity.py` birlikte calistirildi; 13 test basarili.

### 7. A2A ic servis allowlist'i bos kalabiliyordu

Durum:
- Compose ortaminda servis kimligi ve HMAC imza zorunlu hale getiriliyordu; ancak `A2A_ALLOWED_CALLER_IDS` bos kalirsa gecerli imzaya sahip herhangi bir internal caller id kabul edilebilirdi.
- Bu, pratikte internal secret ile sinirli olsa da dagitik servis guvenligi icin gereksiz genis bir yuzeydir.

Yapilan:
- A2A compose ortamlarinda varsayilan caller allowlist `main_orchestrator,agent-student-affairs,agent-academic,agent-finance` olarak ayarlandi.
- `.env.example` ayni varsayimi dokumante edecek sekilde guncellendi.

Yapilan ek sertlestirme:
- HMAC imzasi basarili dogrulandiktan sonra `caller_id + target_id + nonce` kombinasyonu process-local replay cache'e yaziliyor.
- Ayni nonce TTL penceresi icinde tekrar gelirse istek reddediliyor.
- Regresyon testleri eklendi: nonce tekrar kullanimini reddetme ve TTL dolduktan sonra ayni nonce'in yeniden kabul edilebilmesi.

Kalan is:
- Coklu replica/production dagitimda process-local cache yeterli olmaz; nonce store Redis gibi merkezi bir yere tasinmali.

### 8. Remote retrieval fallback her hatada local retriever'i yeniden kurabiliyordu

Durum:
- Merkezi retrieval servisi gecici olarak ulasilamazsa agent local `HybridRetriever` fallback'e dusuyordu.
- Fallback nesnesi paylasilmadigi icin her hata aninda embedding/reranker/BM25 kaynaklarini yeniden kurma riski vardi.

Yapilan:
- `src/agents/base.py` icine paylasimli local fallback retriever cache'i eklendi.
- Remote hata aldiginda merkezi retriever denenmeye devam ediyor; ancak local fallback ayni process icinde tekrar tekrar kurulmuyor.
- Regresyon testi eklendi: `TestLLMBypassMechanism.test_remote_retrieval_local_fallback_is_shared`.

### 9. Slack/auth profil guncellemesi ogrenci tipi bilgisini gereksiz silebiliyordu

Durum:
- OTP ile dogrulanmis auth baglami bolum/fakulte bilgisini getiriyor, fakat ogrenci tipi bilgisini ana `students` kaydindan tasimiyordu.
- Profil kaydinda daha once `student_type` tutulduysa, verified upsert `student_type=None` ile bu bilgiyi silebiliyordu.

Yapilan:
- `students` tablosuna nullable `student_type` alani icin migration eklendi.
- `AuthContext`, OTP sonucu, session/slack auth cozumleme ve API query context akisi bu alani tasiyacak sekilde guncellendi.
- `src/db/profile_context.py` guncellendi: dogrulanmis profil guncellemesi ancak yeni `student_type` gercekten geldiyse mevcut ogrenci tipini degistiriyor.
- Seed test ogrencileri varsayilan `domestic` olarak isaretlendi.
- Bu sayede dogrulanmis kullanicida resmi ogrenci tipi biliniyorsa ucret sorularinda gereksiz takip sorusu azalir.

### 10. Model profil ornekleri eski 8B Groq varsayimini tasiyordu

Durum:
- Runtime model cozumleyici rol bazli override destekliyor ve provider namespace'lerini ayiriyor.
- Ancak `.env.example` Groq orneginde 8B modeli ana model gibi gosteriyordu; bu son kalite kararimizla uyumsuzdu.

Yapilan:
- Groq ornekleri 70B model kullanimina hizalandi.
- `OPENAI_ROUTING_MODEL`, `OPENAI_CONVERSATION_MODEL`, `OPENAI_SPECIALIST_SYNTHESIS_MODEL` ve `OPENAI_GLOBAL_SYNTHESIS_MODEL` alanlari ornekte acik hale getirildi.
- `LLM_QUERY_NORMALIZATION_ENABLED` ve timeout ayari `.env.example` icinde gorunur hale getirildi.

Not:
- Kod tarafinda `fast` profil tum rollerde secondary modeli kullanir. `balanced` profil role override varsa onu, yoksa routing/conversation icin secondary modeli kullanir. 70B davranisi icin `.env` tarafinda provider-role override'lari set edilmelidir.

### 11. Ders programi parser sirasi iki kolonlu tablolarin derslik bilgisini dusuruyordu

Durum:
- Geniş unit calismasinda `test_schedule_ingest.py` icindeki iki kolonlu `Ders / Derslik` haftalik program ornekleri eksik slot uretti.
- Kok neden veri degildi; parser sirasi daha genel `single_column_grouped` yorumlayicisinin iki kolonlu tabloyu erken sahiplenmesiydi.
- Sonuc olarak ayni satirdaki derslik kolonlari ayri alan gibi okunmadan kayboluyor, slot sayisi ve `classroom` bilgisi eksik kaliyordu.

Yapilan:
- `src/db/schedule_ingest.py` icinde iki kolonlu grouped parser, daha genel grouped parser'lardan once denenir hale getirildi.
- Bu soru bazli bir yama degil; daha spesifik tablo formatinin daha genel formattan once parse edilmesi saglandi.

Dogulama:
- `tests/unit/test_schedule_ingest.py` hedefli calisti ve `13 passed`.
- `src/db/schedule_ingest.py` icin `py_compile` basarili.

Not:
- Geniş `tests/unit` calismasinda ayrica `tmp_path` kullanan bazi dokuman yukleme testleri Windows/sandbox gecici klasor izinleri nedeniyle `PermissionError/FileNotFoundError` verdi. Bu hatalar uygulama mantigi yerine test calisma ortami gecici klasor problemi olarak ayrica izlenmeli.

## Gozlemler

- Turkce karakterler icin terminalde mojibake gorunuyor; ancak Python unicode kontrollerinde kritik dosyalardaki string literal'lar UTF-8 olarak dogru gorundu.
- Merkezi retrieval fallback mevcut: remote retrieval hata verirse agent local `HybridRetriever` ile tekrar dener. Bu fallback artik process icinde paylasiliyor.
- Routing/prompt hattinda markerlar tamamen kaldirilmadi; fakat mevcut tasarimda markerlar LLM kararini ezmekten cok sinir guvenligi, slot dogrulama ve kritik capability secimi icin kullaniliyor. Yine de her yeni marker eklemesi soru bazli yama riskine karsi testle desteklenmeli.
- Warm-up/cache denetiminde merkezi retrieval acikken agent servislerinin local retrieval warm-up yapmadigi, capability agent'larin LLM warm-up disinda kaldigi ve embedding/reranker/BM25 cache katmanlarinin testle korundugu dogrulandi.
- Geniş unit denemesinde uygulama kaynakli net hata olarak ders programi parser sirasi yakalandi ve duzeltildi; kalan coklu hata grubu gecici test klasoru izin problemine benziyor.

## Bu turda calistirilan hedefli kontroller

- `python -m pytest tests/unit/test_query_normalization.py -o cache_dir=.codex_pytest_tmp`
- `python -m pytest tests/unit/test_all_agents.py -k final_exam_result_entry_deadline -o cache_dir=.codex_pytest_tmp`
- `python -m pytest tests/unit/test_response_utils.py::test_clean_final_answer_replaces_common_foreign_words_inline -o cache_dir=.codex_pytest_tmp`
- `python -m pytest tests/unit/test_a2a_rollout.py tests/unit/test_a2a_service_identity.py -o cache_dir=.codex_pytest_tmp`
- `python -m pytest tests/unit/test_slack_service.py tests/unit/test_slack_app.py -o cache_dir=.codex_pytest_tmp`
- `python -m pytest tests/unit/test_config.py tests/unit/test_retrieval_service.py -o cache_dir=.codex_pytest_tmp`
- `python -m pytest tests/unit/test_all_agents.py::TestLLMBypassMechanism::test_remote_retrieval_local_fallback_is_shared -o cache_dir=.codex_pytest_tmp`
- `python -m pytest tests/unit/test_slack_service.py tests/unit/test_conversation_context.py -o cache_dir=.codex_pytest_tmp`
- `python -m pytest tests/unit/test_curriculum_data.py -o cache_dir=.codex_pytest_tmp`
- `python -m pytest tests/unit/test_all_agents.py::TestTuitionAgent tests/unit/test_tuition_utils.py tests/unit/test_finance_data.py -o cache_dir=.codex_pytest_tmp`
- `python -m pytest tests/unit/test_a2a_service_identity.py tests/unit/test_agent_service.py tests/unit/test_a2a_external.py -o cache_dir=.codex_pytest_tmp`
- `python -m pytest tests/unit/test_startup_warmup.py tests/unit/test_model_cache.py tests/unit/test_cache_policy.py tests/unit/test_question_cache.py tests/unit/test_retriever.py -o cache_dir=.codex_pytest_tmp`
- `python -m py_compile src/a2a/service_identity.py src/api/a2a_dispatch.py src/a2a/external.py`
- `python -m pytest tests/unit/test_router.py tests/unit/test_orchestrators.py tests/unit/test_query_normalization.py tests/unit/test_conversation_context.py tests/unit/test_query_preprocessor.py -o cache_dir=.codex_pytest_tmp`
- `python -m pytest tests/unit/test_schedule_ingest.py -o cache_dir=.codex_pytest_tmp`
- `python -m py_compile src/db/schedule_ingest.py`

## Geniş Unit Calisma Notu

- `python -m pytest tests/unit -o cache_dir=.codex_pytest_tmp` calismasinda `838 passed` goruldu; fakat `tmp_path` kullanan bir grup test Windows/sandbox gecici klasor izinleri yuzunden `PermissionError/FileNotFoundError` verdi.
- Ayni calismada yakalanan uygulama mantigi hatasi `schedule_ingest` parser sirasiydi; hedefli testle duzeltildi.
- Gecici klasor problemi icin ayri bir CI/Windows test ortaminda tekrar kosum onerilir; bu nedenle genis suite sonucu su an "ortam kaynakli kismi kosum" olarak degerlendirilmeli.

### 12. BM25 adaylari hybrid skor hattinda sifir skorla tasiniyordu

Durum:
- Canli Chroma koleksiyonlari uzerinden yapilan diagnostikte BM25 dokuman sayilarinin Chroma count ile uyumlu oldugu goruldu:
  - `student_affairs_docs`: 1786 / 1786
  - `academic_programs_docs`: 5089 / 5089
  - `finance_docs`: 57 / 57
- Yani BM25 bos degildi ve Chroma'dan tum dokumanlari okuyordu.
- Ancak `EnsembleRetriever` rank-fusion ile sirali `Document` dondururken bu fusion skorunu metadata'ya yazmiyor.
- Bizim `deduplicate_documents` fonksiyonumuz skor olarak yalnizca `similarity_score` okuyordu. BM25 kaynakli veya BM25 tarafindan once korunan adaylarda bu alan olmadigi icin skor `0.0` kaliyordu.
- Sonuc: BM25 exact match adaylari gelmesine ragmen sonraki skor siralama, min-score filtreleme ve reranker aday havuzu seciminde gereksiz dezavantaj yasayabiliyordu.

Yapilan:
- `src/rag/candidate_utils.py` icinde similarity skoru olmayan rank-fusion/BM25 adaylari icin `rank_fusion_score = 1 / (retrieval_rank + 2)` uretildi.
- Bu skor `retrieval_score` ve top-level `score` olarak tasiniyor; `score_type=rank_fusion` ile semantic/reranker skorlarindan ayriliyor.
- Semantic skor varsa mevcut davranis korunuyor.

Dogulama:
- `tests/unit/test_retriever.py` icine BM25-only adaylarin artik sifir skorla tasinmadigini garanti eden regresyon testi eklendi.
- `tests/unit/test_retriever.py`: 56 test basarili.
- Canli diagnostikte BM25/rank-fusion adaylarinin artik `score=0.5, 0.3333, ...` gibi skorlarla tasindigi ve reranker oncesi aday havuzuna guclu sekilde girdigi goruldu.

Ek gozlem:
- Lokal diagnostikte `RAG_LLM_QUERY_EXPANSION_ENABLED=true` oldugu icin retrieval basina ayri LLM query expansion cagrisi 8 saniye timeout'a dustu. Bu canli Docker ortaminda API anahtari/ag erisimiyle farkli davranabilir; yine de ayri LLM expansion cagrisi maliyet ve latency riski tasiyor. Daha temiz hedef, routing/normalization LLM'inden gelen canonical/intent bilgisini retrieval planina baglayip bu ayri cagrinin gerekli olmadigi durumlarda kapatmak.

### 13. Corpus icinde baslik-only ve cok kisa chunk gürültüsü var

Durum:
- Canli Chroma diagnostiginde bos chunk yoktu; ancak cok kisa chunk'lar goruldu:
  - `student_affairs_docs`: 9 adet `<50` karakter
  - `academic_programs_docs`: 32 adet `<50` karakter
  - Ornekler: `Amaç`, `Amaç ve kapsam`, `BIRINCI BOLUM ... Amaç`
- Bu parcalar tek basina cevap icin bilgi tasimiyor; embedding/BM25 havuzunu kirletip reranker aday kapasitesini gereksiz tuketebilir.
- Ayrica duplicate exact text orani ozellikle akademik koleksiyonda yuksek gorundu (`academic_programs_docs`: 690 duplicate text). Bunun bir kismi ayni yonetmeligin farkli adlarla tekrar indekslenmesinden kaynaklanabilir.

Yapilan:
- `RAG_MIN_CHUNK_CHARS` ayari eklendi; varsayilan `50`.
- `TextChunker`, pipeline tarafindan bu esik ile kuruldugunda baslik-only/kisa parcalari indekslemeye gondermiyor.
- `.env.example` icine `RAG_MIN_CHUNK_CHARS=50` eklendi.
- Regresyon testi eklendi: `TextChunker(min_chunk_chars=50)` ile `Amaç` gibi baslik-only parcanin atlandigi dogrulaniyor.

Kalan is:
- Bu duzeltme yeni indekslemelerde etkili olur. Mevcut Chroma koleksiyonlarindaki kisa/duplicate chunk'larin temizlenmesi icin kontrollu full reindex gerekir.
- Duplicate kaynaklar icin ikinci bir adim olarak corpus seviyesinde `content_hash`/canonical source dedup denetimi eklenebilir.

### 14. Embedding modeli ve Chroma vektor boyutu icin erken hata kontrolleri eksikti

Durum:
- Embedding modeli `BAAI/bge-m3`, beklenen boyut `1024`.
- Canli Chroma orneklemesinde aktif koleksiyonlardaki vektor boyutlari `1024` olarak dogrulandi:
  - `student_affairs_docs`: ornek boyutlar `1024, 1024, 1024`
  - `academic_programs_docs`: ornek boyutlar `1024, 1024, 1024`
  - `finance_docs`: ornek boyutlar `1024, 1024, 1024`
  - `academic_schedules_docs`: ornek boyutlar `1024, 1024, 1024`
- Yerel model CPU uzerinden yuklenerek ayrica dogrulandi: `loaded_dimension=1024`, test sorgusu embedding boyutu `1024`, normalize vektor normu yaklasik `1.0`.
- Ancak kodda model degisimi veya yanlis `.env` durumunda `EMBEDDING_DIMENSION` ile gercek model boyutu karsilastirilmiyordu.
- Indexing pipeline ve Chroma indexer, embedding sayisi/boyutu ile chunk/id/metadata sayisini yazim oncesinde sistematik dogrulamiyordu.

Risk:
- Model yanlislikla 768/384 boyutlu bir modele degistirilirse sorun Chroma yaziminda veya sorguda gec, belirsiz ve ortam bagimli sekilde patlayabilirdi.
- Eksik/fazla embedding uretilmesi veya batch icinde farkli boyutlu vektor olusmasi durumunda kaynak hata noktasi net gorunmeyebilirdi.

Yapilan:
- `src/rag/embedder.py` model yuklenirken gercek model boyutunu `settings.embedding.dimension` ile karsilastiriyor; uyusmazlikta erken `ValueError` uretiyor.
- `Embedder.embed_texts`, uretilen embedding sayisini input sayisiyla ve her vektor boyutunu model boyutuyla dogruluyor.
- `src/rag/pipeline.py`, embedding uretiminden sonra chunk/embedding sayisi ve boyut tutarliligini kontrol ediyor.
- `src/rag/indexer.py`, Chroma yazimi oncesi `ids/documents/embeddings/metadatas` uzunluklarini ve embedding batch boyut tutarliligini dogruluyor.
- `.env.example` icine `EMBEDDING_DIMENSION=1024` eklendi; boyut artik acik bir deploy kontrati.

Dogrulama:
- `tests/unit/test_embedder.py`, model/config boyut uyumsuzlugu, embedding sayi uyumsuzlugu ve batch boyut uyumsuzlugu icin regresyon testleriyle genisletildi.
- `tests/unit/test_chroma_indexer.py`, Chroma payload sekil dogrulamalari icin eklendi.
- `tests/unit/test_rag_pipeline.py`, pipeline embedding output dogrulamalarini kapsayacak sekilde genisletildi.
- Ilgili testler: `28 passed`.
- `py_compile`: `src/rag/embedder.py`, `src/rag/indexer.py`, `src/rag/pipeline.py` basarili.

Kalan is:
- Gercek `.env` de `.env.example` ile hizalanarak `RAG_LLM_QUERY_EXPANSION_ENABLED=false` yapildi. Lokal diagnostikte bu ayri retrieval-LLM cagrisi timeout/latency riski olusturmustu. Bunu tamamen kaldirmak yerine ileride routing/query-normalization LLM'inden gelen `canonical_query` ve `primary_intent` bilgisini retrieval planina kontrollu baglamak daha temiz gorunuyor.
- Mevcut Chroma corpus icindeki kisa/duplicate chunk temizligi icin full reindex hala gerekli.

### 15. Query expansion tekrarli terim uretiyor ve profil algisi bazi dogal cümleleri kacirabiliyordu

Durum:
- `QueryPreprocessor`, synonym expansion'dan sonra bilesik kelime ayrimi uyguluyordu. Bu dogru; fakat `çift anadal` ve `çift ana dal` gibi iki farkli synonym son adimda ayni forma donusebildigi icin sorguda tekrarli terim olusabiliyordu.
- Ornek: `ÇAP başvurusu nasıl yapılır?` sorgusu `çift ana dal` ifadesini iki kez tasiyabiliyordu.
- `search_planner._detect_student_affairs_query_profile`, bazi profil eslesmelerinde dogal araya kelime giren ifadeleri kacirabiliyordu. Ornek: `Sınav notuma nasıl itiraz ederim?` anlamsal olarak grade objection iken tam kaliplar arasinda olmadigi icin profile `None` kalabiliyordu.

Risk:
- Tekrarli expansion terimleri BM25 agirligini gereksiz saptirabilir.
- Profil algisi kacarsa FAQ/source bias ve reranker query secimi daha zayif calisir; dogru kaynak yine gelebilir ama aday havuzunda daha kirilgan hale gelir.

Yapilan:
- `src/rag/query_preprocessor.py` icine expansion terimlerini compound split sonrasi normalize ederek dedupe eden `_dedupe_expanded_terms` eklendi.
- `src/rag/search_planner.py` profil algisi, yalnizca tam cumle kalibina bagli kalmadan `itiraz + (not|sinav|sonuc)` ve `not + sistem + girmemis/girilmemis` gibi genel niyet sinyallerini yakalayacak sekilde genellestirildi.
- Bu degisiklik cevap uretmez; yalnizca retrieval aday secimini ve kaynak bias'ini daha tutarli hale getirir.

Dogrulama:
- `tests/unit/test_query_preprocessor.py`, `tests/unit/test_search_planner_normalization.py`, `tests/unit/test_retriever.py`: `108 passed`.
- `py_compile`: `src/rag/query_preprocessor.py`, `src/rag/search_planner.py` basarili.
- Unicode escape ile yapilan runtime probe'da:
  - `ÇAP başvurusu nasıl yapılır?` -> expansion `çift ana dal ikinci lisans` ve tekrar yok.
  - `Sınav notuma nasıl itiraz ederim?` -> profile `grade_objection`.
  - `Hocam ders notlarımı sisteme girmemiş` -> profile `grade_entry`.

### 16. Post-reindex Chroma/registry chunk sayisi ayrismasi bulundu

Durum:
- Full reindex sonrasi corpus denetiminde koleksiyonlarin embedding boyutu ve kisa chunk durumu duzgun gorundu:
  - `student_affairs_docs`: Chroma `1777`, vektor boyutu `1024`, `<50` karakter chunk `0`.
  - `academic_programs_docs`: Chroma `5057`, vektor boyutu `1024`, `<50` karakter chunk `0`.
  - `finance_docs`: Chroma `56`, vektor boyutu `1024`, `<50` karakter chunk `0`.
  - `academic_schedules_docs`: Chroma `119`, vektor boyutu `1024`, `<50` karakter chunk `0`.
- Ancak `student_affairs_docs` registry `1802` chunk yazarken Chroma `1777` kayit tutuyordu.
- Rekonstruksiyon diagnostigi, `student_affairs` icin `1802` chunk'a karsilik `1777` unique ID uretildigini gosterdi.
- Cakisan 25 ID'nin kok nedeni ayni dosya adinin farkli klasorlerde ayni icerikle bulunmasiydi:
  - `uygulama_esaslari_diploma_mezuniyet_belgeler.pdf`
  - Bir kopya `uygulama esasları`, digeri `yönergeler` altinda.
- Eski ID uretimi yalnizca `source` dosya adini kullandigi icin klasor baglami kayboluyor, ayni dosya adi + ayni chunk metni Chroma tarafinda ayni ID'ye dusuyordu.

Risk:
- Pipeline raporu ile Chroma gercek kayit sayisi ayrisabiliyor.
- Ayni ID sessizce carpisirsa reindex sonrasi "chunk olustu" sayisi ile "DB'de chunk" sayisi arasinda fark kalabiliyor.
- Registry kaynak takibi dosya adina gore yapildigi icin ayni ada sahip farkli path'ler tek belge gibi ezilebiliyor.

Yapilan:
- `src/rag/document_loader.py`, `load_directory` icinde her belgeye NFC normalize edilmis `relative_path` metadata'si ekliyor.
- `src/rag/pipeline.py`, deterministik chunk ID uretirken artik `relative_path -> file_path -> source` sirasi ile stabil belge kimligi kullaniyor.
- Registry merge ve `chunks_per_source` hesaplari da ayni belge kimligini kullaniyor; registry satirlarina `relative_path` alani eklendi.
- Chroma yazimindan once `_validate_unique_ids` eklendi. ID cakismasi olursa embedding uretimine ve Chroma yazimina gecmeden erken hata uretiliyor.
- Bu cevap kalitesini soru bazli/statik sekilde degistirmiyor; kaynak kimligi ve indeks tutarliligi icin genel altyapi korumasi.

Dogrulama:
- Kisa runtime probe ile ayni `same.txt` dosya adinin `a/same.txt` ve `b/same.txt` altinda iki farkli `relative_path` aldigi dogrulandi.
- Ayni metin + ayni dosya adi + farkli `relative_path` icin iki farkli chunk ID uretildigi dogrulandi.
- `student_affairs` corpus'u embedding uretmeden yeniden yuklenip parcalandi: `docs=106`, `chunks=1802`, `unique_ids=1802`, `duplicate_id_groups=0`.
- `py_compile`: `src/rag/document_loader.py`, `src/rag/pipeline.py` basarili.
- Hedefli hash-ID testleri basarili; `test_load_directory_with_subdirs` Windows gecici klasor izin problemi yuzunden bir kosumda ortam hatasi verdi, dogrudan runtime probe ile ayni davranis dogrulandi.

Kalan is:
- Bu duzeltmenin Chroma/registry sayilarina yansimasi icin ozellikle `student_affairs_docs` yeniden indekslenmeli.
- Duplicate exact text halen corpus kalite konusu olarak kalabilir. Bunlari otomatik silmek kaynak/citation kaybi yaratabilecegi icin simdilik sadece kimlik cakismasi onlendi; ileride canonical document/alias tasarimi ile ayrica ele alinmali.

### 17. Context expansion ayni dosya adli farkli path'leri karistirabilirdi

Durum:
- `HybridRetriever.enrich_results`, bir aday sub-chunk ise ayni `source` ve `madde_no` degerine sahip diger sub-chunk'lari BM25 dokuman cache'inden toplayip MADDE baglamini genisletiyor.
- `source` yalnizca dosya adi oldugu icin ayni dosya adina sahip iki farkli klasor/path varsa, context expansion ayni maddenin parcalarini farkli kopyalardan veya farkli kaynaklardan karistirabilirdi.
- Bu risk, post-reindex ID cakisma bulgusuyla ayni kok nedene sahipti: belge kimligi dosya adi seviyesinde fazla zayifti.

Yapilan:
- `src/rag/retriever.py` icine `_metadata_identity_key` eklendi.
- Context expansion artik sub-chunk eslestirmede `relative_path -> file_path -> source` kimligini kullaniyor.
- Boylece ayni `source` dosya adina sahip ama farkli `relative_path` altindaki belgeler birbirinin MADDE baglamina katilmiyor.

Dogrulama:
- `tests/unit/test_retriever.py` icine ayni `source=ortak.pdf` fakat farkli `relative_path` degerlerine sahip iki dokuman icin regresyon testi eklendi.
- Hedefli testler basarili:
  - `test_enrich_results_uses_relative_path_for_same_filename`
  - `test_enrich_results_merges_adjacent_sub_chunks_for_same_madde`
- `py_compile`: `src/rag/retriever.py`, `src/rag/document_loader.py`, `src/rag/pipeline.py` basarili.

### 18. Candidate dedup anahtari da ayni dosya adli farkli path'leri ezebilirdi

Durum:
- `src/rag/candidate_utils.py` icindeki `_candidate_dedup_key`, aday tekillestirme anahtarini `source + madde_no + chunk_index + sub_chunk` uzerinden kuruyordu.
- `source` sadece dosya adi oldugu icin ayni ada sahip farkli klasorlerdeki belgelerin ayni madde/chunk numaralari birbirini duplicate gibi ezebilirdi.
- Bu durum ozellikle ayni dosyanin farkli kategori/path altinda bulundugu corpuslarda aday havuzunu sessizce daraltabilir.

Yapilan:
- Dedup anahtari `relative_path -> file_path -> source -> file_name -> source_url` sirasi ile belge kimligi sececek sekilde guncellendi.
- Ayni kaynak dosya adina sahip farkli path'ler artik retrieval aday tekillestirmede ayri belge olarak korunuyor.

Dogrulama:
- `test_dedup_keeps_same_filename_different_relative_path` eklendi.
- Hedefli testler basarili:
  - `test_dedup_keeps_same_filename_different_relative_path`
  - `test_enrich_results_uses_relative_path_for_same_filename`
- `py_compile`: `src/rag/candidate_utils.py`, `src/rag/retriever.py` basarili.

### 19. BM25 tokenizasyonu Turkce ek ve ASCII varyant recall'inda zayifti

Durum:
- BM25 preprocess probe'unda bazi dogal sorgularin tokenlari yeterince genellenmiyordu:
  - `Sınav notuma nasıl itiraz ederim?` -> `notuma` olarak kaliyor, `not` eslesmesi zayifliyordu.
  - `Öğrencilik haklarım neler?` -> `haklar` olarak kaliyor, `hak` seviyesine inmiyordu.
  - `ÇAP` gibi Turkce karakterli/kisaltmali tokenlar ASCII yazilmis belge/sorgu varyantlariyla (`cap`) tek token seviyesinde bulusmuyordu.
- Semantic retrieval ve reranker bu eksigi kismen telafi edebilir; fakat BM25 exact-match aday havuzunu zayiflatir.

Yapilan:
- `turkish_bm25_preprocess`, her token icin Turkce karakterli stem yaninda ASCII-normalize stem varyantini da ekliyor.
- `_turkish_stem`, en fazla iki tur suffix stripping yapacak sekilde guncellendi; `haklarım -> hak`, `sınavlarının -> sınav`, `notuma -> not` gibi yaygin cekimli formlar daha iyi yakalaniyor.
- Ek listesine `larım/lerim`, `larımız/lerimiz`, `uma/üme/ime/ıma`, `um/üm` gibi ogrenci sorgularinda sik gorulen sahiplik/yönelme formlari eklendi.
- Tekrarlanan tokenlar `_dedupe_tokens` ile sirasi korunarak temizleniyor.

Dogrulama:
- Runtime probe sonrasi ornekler:
  - `Sınav notuma nasıl itiraz ederim?` -> `sinav`, `not`, `itiraz`
  - `ÇAP başvurusu nasıl yapılır?` -> `çap`, `cap`, `başvuru`, `basvuru`
  - `Öğrencilik haklarım neler?` -> `ogrenci`, `hak`
- `tests/unit/test_retriever.py::TestTurkishBm25Preprocess` genisletildi.
- Hedefli testler: `13 passed`.
- `py_compile`: `src/rag/retriever.py`, `tests/unit/test_retriever.py` basarili.

### 20. Reranker skip konfigleri davranisla hizali degildi

Durum:
- `.env` icinde `RAG_SKIP_RERANKER_FOR_STUDENT_AFFAIRS_PROCEDURAL=true` ve `RAG_SKIP_RERANKER_FOR_ACADEMIC_PROGRAMS_PROCEDURAL=true` kalmisti.
- Guncel `HybridRetriever._should_skip_reranker` mantigi bu alanlari kullanmiyor; reranker yalnizca aday sayisi `top_k` kadar veya daha azsa atlanıyor.
- Bu nedenle `.env` degerleri fiili davranisi degistirmiyor, ancak operator/gelistirici icin yanlis beklenti olusturuyordu.

Yapilan:
- `.env` degerleri guncel davranisla hizalanarak `false` yapildi.
- Mevcut strateji: cevap kalitesi icin procedural sorgularda da reranker aktif kalsin; yalnizca rerank edilecek anlamli fazla aday yoksa skip edilsin.

Kapanis:
- `RAG_SKIP_RERANKER_FOR_*` alanlari artik `config.py` ve aktif `.env` icinden kaldirildi.
- Guncel policy: reranker, yalnizca aday sayisi zaten `top_k` kadar veya daha az oldugunda atlanir.

### 21. Merkezi retrieval servisinde `/enrich` hatasi ajan cevabini dusurebilirdi

Durum:
- Ajanlar merkezi retrieval kullanirken remote `/search` basarisiz olursa local fallback'e dusuyordu.
- Ancak remote `/search` basarili olup remote `/enrich` basarisiz olursa ayni fallback uygulanmiyordu.
- `/enrich` aslen MADDE/sub-chunk baglam genisletme adimi oldugu icin bu noktadaki gecici network/servis hatasinin tum ajan cevabini dusurmesi dagitik mimari icin gereksiz kirilganlikti.

Yapilan:
- `src/agents/base.py` icinde `retriever.enrich_results` cagrisi da try/except ile korundu.
- `RETRIEVAL_SERVICE_ENABLED=true` ve `RETRIEVAL_SERVICE_FALLBACK_TO_LOCAL=true` iken remote enrich hatasinda paylasilan local fallback retriever kullaniliyor.
- Boylece remote search sonucu elde edildiyse, context expansion adimi local olarak deneniyor; local fallback de olmazsa mevcut hata politikasi korunuyor.

Dogrulama:
- `test_remote_enrich_local_fallback_is_shared` eklendi.
- Hedefli testler basarili:
  - `test_remote_enrich_local_fallback_is_shared`
  - `test_remote_retrieval_local_fallback_is_shared`
- `py_compile`: `src/agents/base.py`, `tests/unit/test_all_agents.py` basarili.

### 22. Evidence source_id path baglamini kullanmiyordu

Durum:
- Structured evidence ve claim guard hattinda `source_id`, gorunen `source_name` ve icerik kirpimi uzerinden uretiliyordu.
- Ayni dosya adi ve ayni/benzer icerik farkli path'lerde bulunursa, diagnostik/claim-guard izleme kimligi fazla kaba kalabilirdi.
- Bu cevap kalitesinden cok denetlenebilirlik ve kaynak izleme tutarliligi riskiydi.

Yapilan:
- `src/quality/evidence.py`, source ID uretirken `relative_path -> file_path -> source_url -> source_name` sirasi ile kaynak kimligi kullaniyor.
- Gorunen `source_name` degismedi; kullaniciya kaynak adini gostermeye devam ediyoruz.

Dogrulama:
- `test_extract_evidence_items_source_id_uses_relative_path_identity` eklendi.
- Hedefli testler basarili:
  - `test_extract_evidence_items_source_id_uses_relative_path_identity`
  - `test_source_id_is_deterministic`
- `py_compile`: `src/quality/evidence.py`, `tests/unit/test_evidence.py` basarili.

### 23. Belirsiz basvuru tarihi clarification'i genel departman mesajina dusebiliyordu

Durum:
- Router, `sey basvuru ne zaman` gibi belirsiz basvuru tarihi sorularini dogru sekilde `CLARIFICATION` olarak isaretliyordu.
- Ancak bu kural tabanli override `IntentAnalysis.missing_slots` tasimadigi icin orkestrator, mevcut missing-slot mekanizmasindan gecemiyor ve kullaniciya ozel `Hangi basvuru turu?` sorusu yerine genel departman secim mesaji donebiliyordu.
- Bu davranis dogru niyet tespit edilmesine ragmen kullanici deneyimini zayiflatiyordu.

Yapilan:
- `src/routing/router.py` icindeki belirsiz basvuru tarihi override'i, LLM intent yoksa domain-genel bir `IntentAnalysis` uretiyor.
- `required_slots=["application_type"]` ve `missing_slots=["application_type"]` set ediliyor.
- Boylece nihai karar yine clarification, fakat cevap uretimi mevcut `build_missing_slot_clarification_message` mekanizmasi uzerinden ozel soruya donusuyor.
- Bu soru bazli cevap hack'i degil; basvuru tarihi niyetinde eksik semantik slotun yapisal olarak tasinmasi.

Dogrulama:
- `test_route_vague_application_timing_to_clarification` genisletildi; artik `missing_slots == ["application_type"]` bekleniyor.
- Hedefli testler basarili:
  - `test_route_vague_application_timing_to_clarification`
  - `test_route_exam_date_query_to_student_affairs_calendar`
  - `test_query_normalization_preserves_grade_entry_deadline`
- `py_compile`: `src/routing/router.py`, `tests/unit/test_router.py` basarili.

### 24. Docker A2A profilinde merkezi retrieval fallback'i istemeden local modele donebilirdi

Durum:
- Dagitik A2A mimarisinde uzman ajanlar merkezi `retrieval-service` uzerinden arama/rerank yapacak sekilde tasarlandi.
- Kod seviyesinde `RETRIEVAL_SERVICE_FALLBACK_TO_LOCAL=true` destegi var; bu lokal gelistirme icin kullanisli.
- Ancak Docker A2A servislerinde bu deger acik bir sekilde set edilmediginde varsayilan `true` kalabiliyordu.
- Retrieval servisi gecici olarak dusunce her specialist container'in kendi local `HybridRetriever`/embedding/reranker kaynaklarini yuklemeye calismasi riski vardi. Bu, hem isil/yuk maliyetini artirir hem de merkezi retrieval kararini fiilen delmis olur.

Yapilan:
- Tum A2A Docker compose ortak ortam bloklarina:
  - `RETRIEVAL_SERVICE_FALLBACK_TO_LOCAL: ${RETRIEVAL_SERVICE_FALLBACK_TO_LOCAL:-false}`
  eklendi.
- Boylece Docker dagitik profilinde retrieval servisi zorunlu merkezi bilesen gibi davranir; servis yoksa hata net gorunur, specialist'ler sessizce local model yuklemez.
- Lokal Python/inprocess gelistirme varsayilani degistirilmedi; gerekirse `.env` ile fallback tekrar acilabilir.

Dogrulama:
- Degisen compose dosyalari PyYAML ile parse edildi: `yaml-ok`.
- Tum `docker-compose.a2a-existing-infra*.yml` dosyalarinda `RETRIEVAL_SERVICE_FALLBACK_TO_LOCAL` satiri dogrulandi.

### 25. Ders kaydi surec sorulari source-only kisayola fazla kolay dusebiliyordu

Durum:
- Kayit ajaninda kaynak guvenliyse LLM sentezini atlayip en iyi belge parcasini dogrudan donduren `source-only` yol var.
- Bu yol basit belge/kural sorularinda hizli ve guvenli; ancak `ders kaydi nasil yapilir`, `danisman onayi nasil isler`, `ders kaydindan danisman onayina kadar sureci anlat` gibi cok adimli surec sorularinda ham chunk cevabi eksik veya parca parca kalabiliyor.
- Bu, soru bazli bir hata degil; `course registration + process signal` sinifindaki sorularin dogasi geregi sentez gerektirmesi.

Yapilan:
- `src/agents/student/registration_utils.py` icinde `is_course_registration_process_query(query_text)` dogru ise `should_force_registration_llm_synthesis` artik `True` donuyor.
- Boylece ders kaydi/ders secimi + surec/nasil/danisman/onay sinyali iceren sorular kaynak metni dogrudan basmak yerine specialist LLM sentezine gidiyor.
- Kural yine karar yardimcisi olarak kaliyor; cevabi sabitleyen statik metin eklenmedi.

Dogrulama:
- `test_should_force_registration_llm_synthesis_for_course_registration_process` eklendi.
- Hedefli testler basarili:
  - `test_should_force_registration_llm_synthesis_for_course_registration_process`
  - `test_should_force_registration_llm_synthesis_for_multi_step_withdrawal_process`
  - `test_should_skip_registration_llm_synthesis_does_not_short_circuit_discipline_queries`
- `py_compile`: `src/agents/student/registration_utils.py`, `tests/unit/test_registration_utils.py` basarili.

### 26. Not goruntuleme proseduru ile kisisel not verisi ayrimi regressiona karsi sabitlendi

Durum:
- Slack testlerinde `Sinav notlarimi nereden gorebilirim?` benzeri bir soru zaman zaman kisisel akademik ozet gibi cevaplanabiliyordu.
- Guncel kural katmani bu soruyu kisisel veri saymiyor; cunku `nereden/gorebilirim` prosedur sinyali, `notlarim` sahiplik sinyalini bastiriyor.
- Risk, ileride bu ayrimin bozulmasi ve genel prosedur sorularinin gereksiz auth/VT akisini tetiklemesi.

Yapilan:
- `tests/unit/test_graduation_utils.py` eklendi.
- `Sinav notlarimi nereden gorebilirim?` sorusunun kisisel veri sayilmadigi, `Not ortalamam kac?` sorusunun kisisel veri sayildigi testle garanti altina alindi.

Dogrulama:
- Hedefli testler basarili:
  - `test_grade_viewing_location_is_not_personal_data_query`
  - `test_grade_average_value_is_personal_data_query`
- `py_compile`: `tests/unit/test_graduation_utils.py`, `src/agents/student/graduation_utils.py` basarili.

### 27. Specialist LLM promptunda Turkce disi dolgu kelime riski azaltildi

Durum:
- Slack testlerinde bir cevapta `certain` gibi Ingilizce dolgu kelimesi gorulmustu.
- `clean_final_answer` bu tur kelimeleri temizleyebiliyor; ancak en saglikli katman, LLM'e baslangicta bu davranisi yasaklamak.

Yapilan:
- `src/agents/base.py` icindeki tum specialist LLM sentezlerinde ortak kullanilan cevap yazim kurallarina Turkce disi dolgu/yer tutucu kelime kullanmama kurali eklendi.
- Bu, kaynak/cevap mantigini statiklestirmiyor; yalnizca dil hijyeni icin ortak stil kuralini guclendiriyor.

Kalan not:
- Docker/Slack tarafinda ayni kelime tekrar gorulurse ilk supheli stale image veya eski bot process olur; cunku lokal `clean_final_answer` zaten bu kelimeyi temizliyor.

### 28. A2A rollout skip-build modunda eski container build metadata'si kalabiliyordu

Durum:
- `scripts.a2a_rollout`, her calismada yeni `A2A_BUILD_ID` uretip health endpointlerinde bu build ID'nin gorunmesini bekliyor.
- Ancak `docker compose up --no-build -d` mevcut container'i her durumda yeniden yaratmak zorunda degil.
- Bu durumda servisler calisiyor ve Docker healthcheck `Healthy` gorunuyor olsa bile uygulama icindeki `/health` eski `SERVER_BUILD_ID` ile cevap verebilir; rollout scripti de bunu hakli olarak "beklenen build gelmedi" diye hata sayar.

Yapilan:
- Rollout up komutu artik `--force-recreate` ile uretiliyor:
  - `docker compose ... up --no-build --force-recreate -d ...`
- Boylece build yapilmasa bile yeni environment/build metadata container'a deterministik sekilde uygulanir.

Dogrulama:
- `_compose_up_args` yardimcisi ve `test_compose_up_args_force_recreates_services_for_fresh_build_metadata` testi eklendi.
- Hedefli testler basarili:
  - `test_compose_up_args_force_recreates_services_for_fresh_build_metadata`
  - `test_health_matches_build[...]`
- `py_compile`: `scripts/a2a_rollout.py`, `tests/unit/test_a2a_rollout.py` basarili.

### 29. Reindex sonrasi Chroma/registry tutarliligi dogrulandi

Durum:
- Onceki denetimde `student_affairs_docs` icin registry `1802`, Chroma `1777` gorunuyordu.
- Kok neden, ayni dosya adina sahip farkli path'lerdeki belgelerin chunk ID uretiminde path baglaminin kullanilmamasiydi.

Son kontrol:
- `scripts.audit_document_corpus` calistirildi.
- Koleksiyon tutarliligi:
  - `academic_programs_docs`: Chroma `5057`, registry `5057`, OK
  - `academic_schedules_docs`: Chroma `119`, registry `119`, OK
  - `finance_docs`: Chroma `56`, registry `56`, OK
  - `student_affairs_docs`: Chroma `1802`, registry `1802`, OK
- `student_affairs_docs` detay kontrolu:
  - toplam kayit: `1802`
  - unique ID: `1802`
  - duplicate ID: `0`
  - `relative_path` eksik: `0`
  - `50` karakter alti chunk: `0`

Kalan not:
- Korpusta exact duplicate text gruplari var (`257` grup, `299` ekstra chunk). Bunlar artik ID hatasi degil; ayni mevzuatin farkli dosya adlariyla bulunmasi, `v2/v3` form kopyalari ve ayni yonergenin ASCII/Turkce ad varyantlari gibi veri tekrarlari.
- Bu tekrarlar cevap kalitesinde context kalabaligi yaratabilir. Su an silinmedi; cunku veri kaybi olmadan, kaynak-oncelik/dedup politikasi ile kontrollu ele almak daha guvenli.

### 30. Path-aware registry formati yalnizca reindex edilen koleksiyona yansiyor

Durum:
- Pipeline artik `relative_path` metadata'si uretiyor ve ID/registry kimliginde path baglamini kullaniyor.
- `student_affairs_docs` yeni reindex ile bu formata gecti.
- Ancak `academic_programs_docs`, `academic_schedules_docs` ve `finance_docs` registry dosyalari onceki indexlemeden kalma formatta; `documents[]` kayitlarinda `relative_path` yok.

Son kontrol:
- `student_affairs_docs`: `relative_path` eksik `0/106`
- `academic_programs_docs`: `relative_path` eksik `201/201`
- `academic_schedules_docs`: `relative_path` eksik `27/27`
- `finance_docs`: `relative_path` eksik `5/5`
- Bu uc koleksiyonda su an duplicate filename gorunmuyor; bu nedenle acil Chroma count kaybi riski dusuk.

Oneri:
- Path-aware ID/registry davranisinin tum sisteme homojen yansimasi icin academic, schedule ve finance koleksiyonlari da yeni pipeline ile reindex edilmeli.
- Bu ozellikle ileride ayni dosya adi farkli alt klasorlere eklenirse sessiz ID carpismasini onlemek icin onemli.

### 31. Student affairs desteklenen ama indexe girmeyen dosyalar ayrildi

Durum:
- `student_affairs` altinda desteklenen uzantili (`.pdf`, `.txt`, `.docx`) `109` dosya var.
- Registry'de `106` belge var. Unicode NFC normalize edilerek karsilastirildiginda gercek eksik sayisi `3`.

Eksiklerin nedeni:
- `birimler/kurullar.txt`
  - Dosya boyutu `0`, `file_too_short`.
- `uygulama esasları/bitirme_projesi_hazırlama_sunma_ve_değ_ilkeleri_eğitim_komisyonu_kurulu_kararı.pdf`
  - PDF metni `0` karakter cikiyor, `file_too_short`.
- `uygulama esasları/mup_fakülte_kurulu_kararı.pdf`
  - PDF parser hatasi: `Invalid dictionary construct`.

Degerlendirme:
- Bu uc dosya sessiz ID/registry kaybi degil; loader seviyesinde okunamayan veya bos icerik.
- Eger bu belgeler cevap kalitesi icin onemliyse PDF OCR/repair veya alternatif metin kaynagi gerekir. Mevcut text-extraction pipeline ile indekslenemezler.

### 32. Ders programi sorgularinda announcement short-circuit fazla genisti

Durum:
- Slack testlerinde `Ders programi`, `Elektrik elektronik muhendisligi ders programi var mi?` ve benzeri sorular dogrudan duyuru agent'ina gidebiliyordu.
- Bunun iki nedeni vardi:
  - `looks_like_announcement_query` icinde `ders programi` gibi direct lookup marker'lari tek basina announcement sayiliyordu.
  - Routing few-shot orneginde `Elektrik elektronik muhendisligi ders programi var mi?` sorusu `target_capability=announcement` olarak ogretilmisti.
- Yeni ders programi VT/schedule hattimiz oldugu icin bu karar artik fazla genis kaliyor. Duz ders programi sorusu once `academic_programs/curriculum` hattinda yapilandirilmis schedule verisini denemeli; kullanici acikca `duyuru`, `link`, `ilan`, `yayinlandi mi` gibi sinyal verdiginde announcement'a gitmeli.

Yapilan:
- `src/orchestrators/query_policy.py` icinde announcement short-circuit daraltildi.
- `ders programi` artik yalnizca acik duyuru/link/yayin sinyali varsa announcement sayiliyor.
- Sinav programi gibi gercek duyuru/PDF lookup sorgulari korunuyor:
  - `Bahar donemi final sinavi programi` halen announcement lookup.
- `src/llm/prompt_templates.py` icindeki routing few-shot ornegi guncellendi:
  - `Elektrik elektronik muhendisligi ders programi var mi?` artik `academic_programs`, `primary_intent=course_schedule`, `target_capability=none`.

Dogrulama:
- Yeni `tests/unit/test_query_policy.py` eklendi.
- Yeni curriculum regression testi eklendi:
  - `Fizik ders programi var mi?` login/ogrenci bolumu olmadan bolumu sorgudan cikartip structured schedule response uretiyor.
- Hedefli testler basarili:
  - `tests/unit/test_query_policy.py`
  - `TestRegistrationAgent::test_final_exam_result_entry_deadline_uses_academic_calendar_pdf`
  - `TestCurriculumAgent::test_department_schedule_query_infers_department_without_login_context`
- `tests/unit/test_router.py` tamamen basarili: `47/47`.

Not:
- `tests/unit/test_schedule_hybrid_support.py` icindeki `tmp_path` kullanan iki test Windows temp/base temp izin hatasi nedeniyle calisamadi; ayni dosyadaki tmp gerektirmeyen iki test basarili. Bu kod regresyonu degil, test ortaminda temp dizini yazma/okuma izni sorunu.

### 33. Genel akademik takvim tarihi sorgularinda RAG kaynak siralamasi guclendirildi

Durum:
- Gercek index uzerinden probe yapildiginda `Final sinavlarinin sisteme girilmesinin son gunu ne zaman?` benzeri sorgularda dogru kaynak olan `2025_2026_genel_akademik_takvim.pdf` bulunuyordu.
- Ancak ham RAG siralamasinda `sik_sorulan_sorular.txt` icindeki sinav itirazi cevabi bazen ilk siraya cikabiliyordu.
- Ana uygulama akisinda `RegistrationAgent.build_general_exam_calendar_answer` bu soruyu RAG'a birakmadan structured PDF row extraction ile dogru cevapliyor:
  - guz: `19 Ocak 2026`
  - bahar: `16 Haziran 2026`
- Buna ragmen fallback/RAG-only yollarda LLM'e ilk kanit olarak itiraz cevabinin gitmesi riskliydi.

Yapilan:
- `src/rag/search_planner.py` icinde genel akademik takvim tarihi sorgulari icin kaynak-turu onceligi eklendi.
- Bu mekanizma cevap uretmez; yalnizca retrieval sonucunda akademik takvim/takvimler kaynagini one alir ve FAQ kaynagini bu niyet icin hafif geri iter.
- Not itirazi gibi FAQ'nin dogru kaynak oldugu sorular korunur.

Dogrulama:
- Yeni test dosyasi:
  - `tests/unit/test_search_planner.py`
- Basarili testler:
  - `test_academic_calendar_date_query_prefers_calendar_source_over_faq`
  - `test_non_calendar_query_does_not_penalize_faq_source`
  - `TestRegistrationAgent::test_final_exam_result_entry_deadline_uses_academic_calendar_pdf`
- Gercek index probe:
  - `Final sinav sonuclarinin internete girilmesi icin son tarih nedir?`
  - Ilk iki sonuc artik akademik takvim kaynagindan geliyor; ilgili takvim satiri LLM baglamina daha temiz tasiniyor.

### 34. LLM tabanli kanit secici katmani eklendi

Durum:
- RAG hatti once aday belgeleri embedding/BM25 ve reranker ile siraliyordu; specialist LLM sentezi de bu siralamanin ilk N kaynagini baglama aliyordu.
- Bu dogru mimari olsa da pratikte bazi sorgularda ilk skorlanan kaynak genel veya yan konuya ait olabiliyor, ikinci/ucuncu kaynak ise cevabin asil tarih, form, kosul veya istisnasini daha iyi tasiyabiliyordu.
- Sorun reranker'i devre disi birakmak degil; reranker aday havuzunu iyi daraltiyor. Eksik parca, son sentez baglamina girecek kanitlari "cevap kullanisliligi" acisindan bir kez daha secmekti.

Yapilan:
- `src/quality/evidence_selector.py` eklendi.
- Yeni katman specialist RAG sentezinden hemen once calisir:
  - Deterministik evidence extraction adaylari olusturur.
  - LLM'e sadece aday kanitlari ve kullanici sorusunu JSON secim gorevi olarak verir.
  - LLM cevap uretmez; yalnizca `selected_ids`, `ranking` ve kisa gerekce dondurur.
  - Secilen kaynaklar final synthesis context'ine girer.
- Reranker sirasi tamamen atilmadi:
  - LLM selector hata verirse, timeout olursa, gecersiz JSON donerse veya bos secim yaparsa eski deterministic siralama aynen kullanilir.
  - LLM cok az kaynak secerse ilk deterministic kaynaklardan guvenli backfill yapilir.
- Direct RAG erken cikisi selector ile uyumlu hale getirildi:
  - Selector acik ve yeterli aday havuzu varsa sistem artik tek yuksek skorlu kaynagi dogrudan dondurmez.
  - Bu sayede "ilk kaynak skor olarak iyi ama ikinci/ucuncu kaynak cevabi daha dogrudan tasiyor" problemi selector katmanina ulasir.
  - Aday sayisi yetersizse eski direct RAG hizli yolu korunur.
- Yeni model rolu eklendi:
  - `evidence_selection`
  - `LLM_EVIDENCE_SELECTION_MODEL`, `OPENAI_EVIDENCE_SELECTION_MODEL`, `GOOGLE_AI_EVIDENCE_SELECTION_MODEL` override'lari desteklenir.
- Yeni RAG ayarlari eklendi:
  - `RAG_LLM_EVIDENCE_SELECTION_ENABLED=true`
  - `RAG_LLM_EVIDENCE_SELECTION_TIMEOUT_SECONDS=10`
  - `RAG_LLM_EVIDENCE_SELECTION_MIN_CANDIDATES=4`
  - `RAG_LLM_EVIDENCE_SELECTION_MAX_CANDIDATES=10`
  - `RAG_LLM_EVIDENCE_SELECTION_MAX_SELECTED=5`
- Startup warm-up rol listesine `evidence_selection` eklendi:
  - API/orchestrator runtime icin default roller: `routing,evidence_selection,final_refinement,specialist_synthesis`
  - Specialist servislerde routing disarida tutulur; `evidence_selection`, `final_refinement` ve `specialist_synthesis` isitilir.

Neden bu yol secildi:
- Bu, "soru bazli statik kural" degil; tum RAG sorularinda ayni genel kanit secimi problemini cozen yatay bir katman.
- Reranker mantigina aykiri degil; modern RAG mimarilerinde retriever/reranker sonrasinda LLM tabanli context compression veya evidence selection uygulanabilir.
- Nihai cevabi daha uzun baglama bogmak yerine, LLM sentezine daha temiz ve dogrudan kanit tasir.
- Merkezi retrieval/reranker servis mimarisiyle uyumlu: retrieval servisi aday uretir, specialist agent cevap niyetine gore final evidence context'ini secer.

Dogrulama:
- Yeni test dosyasi:
  - `tests/unit/test_evidence_selector.py`
- Basarili testler:
  - LLM selector ikinci kaynagi daha yararli buldugunda onu one aliyor.
  - Gecersiz JSON durumunda eski kanit siralamasina geri donuyor.
  - LLM aday havuzunda olmayan kaynak ID'si dondururse eski kanit siralamasina geri donuyor.
  - Ayar kapatildiginda selector cagrisi devre disi kaliyor.
  - Yeterli aday havuzu varsa direct RAG selector/synthesis yolunu bypass edemiyor.
- Hedefli testler basarili:
  - `tests/unit/test_evidence_selector.py`
  - `tests/unit/test_config.py`
  - `tests/unit/test_startup_warmup.py`
  - `tests/unit/test_agent_evidence.py`
  - `TestRegistrationAgent::test_final_exam_result_entry_deadline_uses_academic_calendar_pdf`

Not:
- Bu katman kaliteyi artirma adimi; cevap uydurma yetkisi yok. Cevap uretimi halen specialist synthesis ve claim guard tarafinda kalir.
- Token ve gecikme maliyeti yaratir, fakat yalnizca yeterli aday sayisi varsa devreye girer ve timeout/fallback ile sistemi bloke etmez.

### 35. Konusma baglami akademik takvim sorularini gereksiz follow-up sayabiliyordu

Durum:
- Slack denemelerinde `Final sinavlari ne zaman?` gibi tam ve genel akademik takvim sorulari, onceki konusma topic'i varsa bazen follow-up gibi degerlendirilebiliyordu.
- Bu durumda conversation LLM'i gereksiz clarification uretebilir veya onceki topic departman ipucunu tasiyabilirdi.
- Bu sorun cevap bilgisinden degil, konusma baglami karar siralamasindan kaynaklaniyordu.

Yapilan:
- `src/db/conversation_context.py` icine genel akademik takvim tarihi sorulari icin bagimsiz-soru guard'i eklendi.
- Guard yalnizca genel tarih/takvim niyetini ayirir:
  - final/yariyil sonu/donem sonu/butunleme/ara sinav sinyali
  - ne zaman/tarih/takvim/son gun/girilme/not girisi sinyali
- `program` iceren sorgular bu guard'a sokulmaz; bolum/ders bazli sinav programi duyuru veya program akisi korunur.
- Bu LLM'i devreden cikaran genel bir statik cevap degildir; LLM'e yanlis onceki topic baglami gonderilmesini engelleyen intent-siniri korumasidir.

Dogrulama:
- Yeni testler eklendi:
  - `test_resolve_query_treats_academic_calendar_question_as_standalone`
  - `test_resolve_query_treats_exam_result_entry_deadline_as_standalone`
- Hedefli testler basarili:
  - `tests/unit/test_conversation_context.py`
  - `tests/unit/test_router.py`
  - `TestRegistrationAgent::test_general_final_exam_query_uses_academic_calendar_pdf`
  - `TestRegistrationAgent::test_final_exam_result_entry_deadline_uses_academic_calendar_pdf`

### 36. Rollout health kontrolu retrieval warm-up durumunu eski build gibi raporlayabiliyordu

Durum:
- `retrieval-service` health endpoint'i warm-up bitmeden `status=warming` donduruyor, fakat ayni payload icinde dogru `build_id` bilgisini yayinliyordu.
- `scripts/a2a_rollout.py` health kontrolu sadece `ok/healthy` status'lerini build eslesmesi sayiyordu.
- Sonuc olarak servis yeni container/build ile ayaga kalkmis olsa bile, uzun suren retrieval/reranker warm-up nedeniyle rollout "build metadata gorunmedi" hatasina dusebiliyor ve hata mesajinda son gorulen status/build ayirt edilemiyordu.

Yapilan:
- Rollout health eslestirme mantigi `warming` status'unu da build metadata acisindan gecerli kabul edecek sekilde duzenlendi.
- Hata mesaji iyilestirildi:
  - Her bekleyen servis icin son gorulen `status`
  - Son gorulen `build_id`
  artik hata metnine ekleniyor.
- Bu degisiklik Docker healthcheck'i veya uygulama readiness sozlesmesini gevsetmez; yalnizca rollout'un "yeni build container'a uygulanmis mi?" kontrolunu warm-up surecinden ayirir.

Dogrulama:
- `tests/unit/test_a2a_rollout.py` icine yeni payload senaryolari eklendi:
  - API health shape: `app.build.build_id`
  - agent/retrieval health shape: `build.build_id`
  - `status=warming` + dogru build id
- Basarili testler:
  - `tests/unit/test_a2a_rollout.py`
  - `tests/unit/test_agent_service.py`
  - `tests/unit/test_a2a_discovery.py`
  - `tests/unit/test_a2a_service_identity.py`
  - `tests/unit/test_retrieval_service.py`

### 37. Uzman A2A transport'u departman transport'una gore daha kirilgandi

Durum:
- Ana orkestrator -> departman servisi HTTP hattinda retry, retry backoff ve circuit breaker vardi.
- Departman servisi -> uzman agent HTTP hattinda ise tek deneme yapiliyordu.
- Bu durum tam dagitik A2A modunda gecici container/network gecikmesini dogrudan `uzman ajan ulasilamadi` cevabina dusurebiliyordu.

Yapilan:
- `src/a2a/specialist_transport.py` icindeki `HttpA2ASpecialistTransport` icin departman transport'uyla paralel dayaniklilik davranisi eklendi:
  - `retry_count`
  - `retry_backoff_seconds`
  - retryable HTTP status'leri: `502/503/504`
  - timeout icin ayri hata kodu: `a2a_specialist_transport_timeout`
  - tekrarlayan request hatalarinda circuit breaker: `a2a_specialist_circuit_open`
- Basarisiz durumda local specialist'e sessiz fallback yapilmadi.
- Bu merkezi/dagitik kararini korur: `A2A_SPECIALIST_MODE=http` ise uzmanlar yalnizca HTTP A2A ile cagrilir; hata daha dayanıklı sekilde yonetilir.

Dogrulama:
- `tests/unit/test_a2a_helpers.py` icine yeni testler eklendi:
  - timeout sonrasi retry ile basari
  - tekrar eden request failure sonrasi circuit breaker acilmasi
- Basarili testler:
  - `tests/unit/test_a2a_helpers.py`
  - `tests/unit/test_a2a_rollout.py`

### 38. LLM cevap temizleyicide birlesik Turkce onay ifadesi kacabiliyordu

Durum:
- Slack ciktisinda `danisman onayıgereken` gibi bosluksuz birlesmis ifade goruldu.
- `clean_final_answer` icinde bu sinifa ait temizlik vardi, ancak Unicode/encoding varyantlarina karsi test kapsami zayifti.
- Bu, cevap bilgisini degistiren statik kural degil; LLM'in yazim artefaktini temizleyen post-processing hijyenidir.

Yapilan:
- `src/orchestrators/response_utils.py` icinde `onayıgereken/onayigereken` varyantlari icin ek, Unicode guvenli temizlik eklendi.
- `certain` gibi yabanci kelime sizintilari icin zaten test oldugu dogrulandi; Slack'te hala gorulmesi durumunda kuvvetli suphe eski container/image veya temizleme hattindan gecmeyen eski response path olur.

Dogrulama:
- `tests/unit/test_response_utils.py` icine yeni test eklendi:
  - `test_clean_final_answer_separates_joined_turkish_approval_phrase`
- Basarili test:
  - `tests/unit/test_response_utils.py`

### 39. Evidence selector guclu modele baglanmamisti

Durum:
- Yeni eklenen LLM destekli evidence selector, `model_role="evidence_selection"` kullansa da `.env` tarafinda role-ozel override olmadigi icin balanced profilde `OPENAI_MODEL` degerine, yani 8B modele dusebiliyordu.
- Bu katmanin amaci "ilk siradaki belge mi, ikinci belge mi daha dogrudan cevap veriyor?" sorusunu semantik olarak tartmak oldugu icin zayif modele dusmesi kalite riskiydi.

Yapilan:
- Lokal `.env` icine `LLM_EVIDENCE_SELECTION_MODEL=llama-3.3-70b-versatile` eklendi.
- `.env.example` icinde hem genel `LLM_EVIDENCE_SELECTION_MODEL` hem de provider-ozel `OPENAI_EVIDENCE_SELECTION_MODEL` ornekleri dokumante edildi.

Neden statik degil:
- Burada kural tabanli kaynak secimi yapilmadi.
- Tam tersine, mevcut retriever/reranker aday havuzunu LLM'in daha iyi semantik secmesi icin dogru modele bagladik.
- Hata halinde selector deterministik siralamaya guvenli fallback yapiyor.

Dogrulama:
- `tests/unit/test_evidence_selector.py` selectorun LLM secimini, hatali JSON fallback'ini ve bilinmeyen id fallback'ini dogruluyor.
- Hedefli test paketi basarili: `tests/unit/test_evidence_selector.py`.

### 40. Not goruntuleme sorusu kisisel akademik ozet akimina kayabiliyordu

Durum:
- "Not ortalamam kac?" kisisel veri sorusudur.
- "Sinav notlarimi nereden gorebilirim?" ise kisisel not degerini istemez; portal/prosedur sorusudur.
- Slack testlerinde bu sinif bazen mezuniyet/akademik ozet akimina dusup GNO/kredi cevabi verebiliyordu.

Yapilan:
- Routing policy icine not goruntuleme/prosedur ayrimi eklendi.
- Ayrim yalnizca not goruntuleme nesnesi (`sinav notlarimi`, `notlarimi nereden`, vb.) ile prosedurel goruntuleme sinyali (`nereden`, `nasil`, `gorebilirim`, `goruntuleyebilirim`, vb.) birlikte varsa calisir.
- Sonuc `student_affairs + registration_query` olur; boylece soru graduation/akademik ozet agent'ina kaymaz.

Neden statik degil:
- Bu bir soru-cevap ezberi degil; kisisel veri ile prosedur niyetini ayiran guvenlik siniri.
- Cevabin icerigini hala ilgili ajan/RAG uretir.

Dogrulama:
- Yeni test: `tests/unit/test_router.py::TestDepartmentRouter::test_route_grade_visibility_question_to_registration_not_personal_summary`
- Mevcut test: `tests/unit/test_graduation_utils.py::test_grade_viewing_location_is_not_personal_data_query`
- Hedefli test paketi basarili:
  - `tests/unit/test_router.py`
  - `tests/unit/test_query_policy.py`
  - `tests/unit/test_query_normalization.py`
  - `tests/unit/test_conversation_context.py`
  - `tests/unit/test_evidence_selector.py`
  - `tests/unit/test_graduation_utils.py`

### 41. Not goruntuleme sorusunda RAG staj kaynaklarini one cikarabiliyordu

Durum:
- Gercek retrieval smoke kontrolunde `"Sinav notlarimi nereden gorebilirim?"` sorgusu cache baypas edilmeden eski siralamayi, cache baypas edilince ise yeni siralamayi gosterdi.
- Eski/cached siralamada ilk kaynaklar staj raporu belgeleriydi; bu, BM25/semantic sinyallerin `not`, `form`, `degerlendirme` gibi kelimeler uzerinden staj belgelerine fazla yaklasabildigini gosterdi.
- Cache baypasli yeni kontrolde staj belgeleri demote edildi; ancak eldeki ham kaynaklarda bu soruya dogrudan "notlar su ekrandan gorulur" diyen guclu bir belge bulunmadigi icin sistemin bu sinifta fazla emin cevap uretmemesi gerekiyor.

Yapilan:
- `src/rag/search_planner.py` icine `grade_visibility` arama profili eklendi.
- Bu profil:
  - not goruntuleme/prosedur sorgularini yakalar,
  - `ogrenci_bilgi`, `otomasyon`, `ubys`, `not`, `sinav`, `ogrenci_isleri` gibi kaynak sinyallerini destekler,
  - staj/yatay gecis/muafiyet/topluluk gibi yakin ama ilgisiz kaynaklari demote eder.
- `src/rag/query_preprocessor.py` icinde not goruntuleme sorgularina sadece retrieval amacli `ogrenci bilgi sistemi`, `ogrenci otomasyon sistemi`, `UBYS`, `sinav sonucu` genisletmeleri eklendi.
- `src/rag/retriever.py` bu profil icin genisletilmis sorguyu reranker'a verir ve aday havuzunu buyutur.

Ek guvenlik:
- LLM evidence selector artik adaylarin hicbiri soruyu dogrudan desteklemiyorsa `insufficient_evidence=true` diyebiliyor.
- `src/agents/base.py` bu durumda belge baglami olmadan LLM'e cevap urettirmiyor; guvenli "yeterli bilgi bulunamadi" cevabina donuyor.
- Bu, "yanlis belgeyle cevap uretme" yerine "belge yoksa cevap verme" davranisini guclendirir.

Neden statik degil:
- Belirli soruya hazir cevap yazilmadi.
- Deterministik kisim yalnizca retrieval aday havuzunun bariz off-topic kaynaklarla kirlenmesini azaltir.
- Son kanit secimi yine LLM tarafindan semantik olarak yapilir; deterministik katman LLM'in "kanit yetersiz" kararini guvenli cevap akimina baglar.

Dogrulama:
- Cache baypasli smoke kontrolde not goruntuleme sorgusunda staj kaynaklari ilk bes sonuctan cikti.
- Yeni testler:
  - `tests/unit/test_search_planner_normalization.py::test_detect_student_affairs_query_profile_finds_grade_visibility_queries`
  - `tests/unit/test_search_planner_normalization.py::test_apply_query_profile_source_bias_demotes_staj_for_grade_visibility`
  - `tests/unit/test_evidence_selector.py::test_evidence_selector_can_reject_all_candidates`
- Basarili hedefli test paketi:
  - `tests/unit/test_evidence_selector.py`
  - `tests/unit/test_search_planner_normalization.py`
  - `tests/unit/test_search_planner.py`
  - `tests/unit/test_query_preprocessor.py`
  - `tests/unit/test_router.py`

### 42. Indeksleme sonrasi retriever cache eski siralama dondurebiliyordu

Durum:
- Gercek retrieval smoke kontrolunde ayni sorgu once `hybrid_search_cache_hit` ile eski/stale siralamayi dondurdu.
- `HybridRetriever` query cache'i hem bellek ici hem de Redis-backed calisabiliyor.
- Indeksleme veya source-bias kod degisikligi sonrasi cache temizlenmezse, sistem bir sure yeni indeks/siralama yerine eski sonuc setini kullanabilir.
- Bu durum ozellikle Slack testlerinde "kod dogru ama cevap eski gibi" hissi yaratir.

Yapilan:
- `IndexingPipeline.run()` basarili Chroma write/count sonrasinda retrieval cache invalidation calistiracak sekilde guncellendi.
- Temizlenenler:
  - Redis/in-memory retriever query cache (`clear_shared_query_cache`)
  - process-local BM25 document/retriever cache (`HybridRetriever.clear_resource_cache`)
- Ayrica mevcut analiz ortaminda `scripts.manage_cache clear-runtime` calistirilarak var olan runtime cache temizlendi.

Neden statik degil:
- Cevap mantigi veya routing degismedi.
- Bu, indeks ve arama katmanlari arasindaki tutarlilik garantisini guclendiren operasyonel bir onlem.

Dogrulama:
- Yeni test: `tests/unit/test_rag_pipeline.py::TestPipelineCollectionResolution::test_indexing_invalidates_retrieval_caches`
- Hedefli test paketi basarili:
  - `tests/unit/test_rag_pipeline.py::TestPipelineCollectionResolution::test_indexing_invalidates_retrieval_caches`
  - `tests/unit/test_evidence_selector.py`
  - `tests/unit/test_search_planner_normalization.py`
  - `tests/unit/test_router.py`
- Not: Tum `test_rag_pipeline.py` dosyasi bu ortamda `.codex_pytest_tmp` yazma izni nedeniyle basarisiz oldu; hedefli cache invalidation testi ayni dosya icinden basariyla calisti.

### 43. Bagil/mutlak degerlendirme sorusunda dogru yonerge aday havuzuna girmiyordu

Durum:
- Gercek retrieval smoke kontrolunde `"Bagil degerlendirme sistemi ile mutlak degerlendirme arasindaki fark nedir..."` sorgusu `academic_programs` kapsami ile calistiginda ilk sonuclar lisansustu, pedagojik formasyon, dis hekimligi ve genel sinav yonetmeligi kaynaklariydi.
- Kök neden cevap uretimi degil, aday uretimiydi: `bagil_degerlendirme` yonergeleri fiziksel olarak `student_affairs_docs` koleksiyonunda indeksliydi; `academic_programs_docs` icinde bu belge yoktu.
- Bu nedenle akademik agent tek koleksiyonla arama yaptiginda dogru kaynak hic aday havuzuna giremiyordu.

Yapilan:
- `src/rag/query_preprocessor.py` icinde bagil/mutlak degerlendirme sorgulari retrieval amacli olarak `bagil degerlendirme yonergesi`, `bagil not sistemi`, `mutlak not sistemi` gibi kaynak terimleriyle genisletildi.
- `src/rag/search_planner.py` icinde bagil/mutlak degerlendirme konu sinyali eklendi.
- Akademik agent bu konuya explicit `academic_programs` kapsami ile gelse bile arama plani artik `academic_programs_docs` yanina `student_affairs_docs` koleksiyonunu da ekliyor.
- Kaynak relevance katmani, dogru bagil degerlendirme yonergelerini ustte tutup lisansustu/pedagojik/dis hekimligi gibi yakin ama zayif kaynaklari geriye itiyor.

Neden statik degil:
- Cevaba "10 ve alti mutlak, 11 ve uzeri bagil" gibi hazir metin yazilmadi.
- Yapilan is, dogru kaynak koleksiyonunun aday havuzuna girmesini saglamak ve konuya ait kaynaklari tercih etmek.
- Cevabin nihai kapsami hala retrieval, reranker ve LLM evidence selection/synthesis tarafindan belirleniyor.

Dogrulama:
- Cache baypasli gercek retrieval smoke sonrasi ilk sonuclar:
  - `yonerge_bagil_degerlendirme.pdf`
  - `bagil_degerlendirme_yonergesi.pdf`
  - ayni yonergenin bagil/mutlak tanim maddeleri
- Yeni testler:
  - `tests/unit/test_search_planner_normalization.py::test_detect_query_topic_finds_relative_and_absolute_grading_terms`
  - `tests/unit/test_search_planner_normalization.py::test_query_preprocessor_expands_relative_and_absolute_grading_terms`
  - `tests/unit/test_search_planner_normalization.py::test_apply_source_relevance_prefers_bagil_degerlendirme_yonergesi`
  - `tests/unit/test_search_planner_normalization.py::test_plan_search_departments_adds_student_affairs_sources_for_bagil_academic_query`

### 44. Mezuniyet + ilisik kesme sorgusunda disiplin/ceza gorev tanimi ust siraya cikabiliyordu

Durum:
- `"Mezuniyet icin gerekli tum kosullari ve ilisik kesme surecini..."` sorgusunda ilk sonuc bir sure `ogrenci_isleri_birimi.txt` icindeki disiplin cezasi/uzaklastirma/ilisik kesme cezasi gorev tanimiydi.
- Bu kaynakta "ilisik kesme" geciyor ama kullanicinin sordugu mezuniyet/UBYS/kayit sildirme surecini dogrudan anlatmiyor.
- Bu, kelime eslesmesi dogru olsa bile semantik gorev baglaminin yanlis oldugu bir RAG kirlenmesi.

Yapilan:
- `withdrawal` kaynak profili icindeki cok genis `ogrenci_isleri` boost'u daraltildi.
- `disiplin`, `uzaklastirma`, `ceza` baglami withdrawal/kayit sildirme sorularinda negatif kaynak sinyali olarak eklendi.
- FAQ, ilisik kesme, kayit sildirme formu ve UBYS odakli kaynaklar ayni sekilde desteklenmeye devam ediyor.

Neden statik degil:
- Belirli bir cevap uretilmedi; sadece semantik olarak farkli bir "ilisik kesme cezasi" baglami, gonullu kayit sildirme/mezuniyet isleminden ayrildi.
- LLM yine kaynaklardan sentez yapiyor; deterministik kisim yalnizca yanlis baglamdaki adaylari geri itiyor.

Dogrulama:
- Cache baypasli real retrieval smoke sonrasi ilk sonuc `sik_sorulan_sorular.txt` icindeki "Mezuniyet ve Ilisik Kesme Islemlerimi UBYS'den Nasil Baslatabilirim?" blogu oldu.
- Sonraki kaynaklarda kayit sildirme FAQ, onlisans/lisans yonetmeligi ve diploma/mezuniyet uygulama esaslari gorundu.
- Yeni test:
  - `tests/unit/test_search_planner_normalization.py::test_apply_query_profile_source_bias_demotes_discipline_admin_duties_for_withdrawal`

### 45. Ders programi sorulari gereksiz yere duyuru akimina kacabiliyordu

Durum:
- Slack smoke testlerinde `"Fizik ders programi var mi?"` sorgusu ders programi verisi yerine duyuru aramasina dusup `Deneme Dersi` gibi alakasiz duyurular dondurebiliyordu.
- Kök neden `ders programi + var mi` kalibinin duyuru niyeti sayilmasiydi.
- Oysa kullanici bolum/program baglami veriyorsa once yapilandirilmis ders programi/schedule verisi denenmeli; duyuru akimi ancak "duyurusu", "link", "yayinlandi", "nereden takip" gibi acik duyuru sinyali varsa calismali.

Yapilan:
- `src/orchestrators/query_policy.py` icinde ders programi icin duyuru niyeti daraltildi.
- `var mi` tek basina artik ders programi sorgusunu duyuruya tasimiyor.
- `"Ders programi linki olan duyuru var mi?"` ve `"ders programi duyurusu var mi?"` gibi acik duyuru/link sorgulari hala duyuru akiminda kaliyor.

Neden statik degil:
- Belirli bolum veya cevap sabitlenmedi.
- Sadece niyet ayrimi duzeltildi: program verisi isteyen soru akademik/schedule hattina, duyuru/link isteyen soru announcement hattina gidiyor.

Dogrulama:
- Policy/router smoke:
  - `"Fizik ders programi var mi?"` -> `announcement_policy=False`, `academic_programs`, `COURSE_QUERY`
  - `"Elektrik elektronik muhendisligi ders programi var mi?"` -> `announcement_policy=False`, `academic_programs`, `COURSE_QUERY`
  - `"Ders programi linki olan duyuru var mi?"` -> `announcement_policy=True`
- Testler:
  - `tests/unit/test_query_policy.py`
  - `tests/unit/test_orchestrators.py::test_announcement_latest_fallback_is_only_for_generic_latest_queries`

### 46. Yapilandirilmis ders programi eslesmesi bolum adi varyasyonlarina ve gun siralamasina hassasti

Durum:
- Ders programi DB yardimcisi bolum adini normalize etse de tam esitlik uzerinden karsilastiriyordu.
- Bu, `Elektrik-Elektronik Muhendisligi Bolumu` ile `Elektrik Elektronik Muhendisligi` gibi ayni bolumu gosteren varyasyonlarda satirlarin kacmasina yol acabilirdi.
- Ayrica DB yardimcisi satirlari dogru siralasa bile `CurriculumAgent` cevap olustururken `day_of_week` alanini alfabetik siraliyordu; Turkce hafta sirasi bozulabilirdi.
- Canli DB smoke kontrolu denenmis, fakat lokal Postgres kapali oldugu icin `ConnectionRefusedError` alindi. Bu nedenle bu madde kod yolu ve unit seviyesinde dogrulandi; canli veri dogrulamasi servis ayaga kalkinca tekrar yapilmali.

Yapilan:
- `src/db/schedule_data.py` icinde bolum adi eslesmesi icin noktalama, tire ve `bolumu/programi/lisans` gibi son ekleri yok sayan ortak match key eklendi.
- Ders programi satirlari icin `Pazartesi -> Pazar` hafta sirasi kullanilan ortak `schedule_row_sort_key` eklendi.
- `src/agents/academic/curriculum_agent.py` artik kendi alfabetik siralamasini kullanmak yerine bu ortak schedule sort key'i kullaniyor.
- Hem DB model satirlari hem de serialize edilmis dict satirlari ayni siralama mantigindan geciyor.

Neden statik degil:
- Belirli bolum veya ders icin ozel cevap yazilmadi.
- Duzeltme, yapilandirilmis veriye ulasma ve veriyi kullaniciya dogru sira ile sunma katmaninda genel bir normalizasyon/formatlama iyilestirmesi.

Dogrulama:
- Yeni testler:
  - `tests/unit/test_schedule_data.py::test_department_match_key_normalizes_punctuation_and_suffixes`
  - `tests/unit/test_schedule_data.py::test_schedule_sort_key_uses_weekday_order_before_time`
  - `tests/unit/test_schedule_data.py::test_schedule_row_sort_key_matches_serialized_schedule_rows`
- Agent seviyesi hedefli testler:
  - `tests/unit/test_all_agents.py::TestCurriculumAgent::test_precise_schedule_query_prefers_structured_schedule_rows`
  - `tests/unit/test_all_agents.py::TestCurriculumAgent::test_generic_department_schedule_query_uses_structured_rows`
  - `tests/unit/test_all_agents.py::TestCurriculumAgent::test_department_schedule_query_infers_department_without_login_context`
- Ek kontrol:
  - `python -m py_compile src/db/schedule_data.py src/agents/academic/curriculum_agent.py`

### 47. Query preprocessing ve yabanci kelime temizleme katmani unicode/LLM sizintisi acisindan kontrol edildi

Durum:
- Terminal ciktisinda `query_preprocessor.py` ve testlerde mojibake gibi gorunen karakterler suphe olusturdu.
- Gercek risk: eger dosya icerigi bozuk olsaydi `CAP`, `Ogrenci Isleri`, `Bagil degerlendirme`, `Kayit dondurma` gibi Turkce sorgular synonym expansion almadan retrieval'e giderdi.
- Ayrica Slack ciktisinda daha once gorulen `certain` gibi Ingilizce kalintilarinin prompt mu yoksa post-processing mi kaynakli oldugu kontrol edildi.

Yapilan:
- Unicode escape ile gercek Turkce sorgular smoke edildi; `CAP`, `Ogrenci Isleri`, `Bagil degerlendirme`, `Kayit dondurma`, `Ders kaydi` expansion'lari dogru calisti.
- `tests/unit/test_query_preprocessor.py` icine gercek unicode sorgular icin regresyon testi eklendi.
- `tests/unit/test_schedule_ingest.py` icine gercek Turkce gun/bolum metni regresyon testleri eklendi.
- `response_utils.clean_final_answer` katmaninda `certain`, `following`, `information` gibi yabanci kelime sizintilarinin temizlendigi ve prompt-like ic basliklarin kaldirildigi testlerle dogrulandi.

Neden statik degil:
- Kullanici sorusuna cevap yazan sabit kural eklenmedi.
- Yapilan is, var olan normalizasyon/temizleme katmaninin gercek Turkce unicode girdilerle calistigini garanti eden test kapsamini guclendirmek.

Dogrulama:
- `tests/unit/test_query_preprocessor.py`
- `tests/unit/test_schedule_ingest.py`
- `tests/unit/test_schedule_data.py`
- `tests/unit/test_response_utils.py`
- `tests/unit/test_llm_query_expander.py`

### 48. Canli schedule DB'de dosya adindan veya aciklama cumlesinden turemis kirli department kayitlari bulundu

Durum:
- Docker/API ayaktayken canli PostgreSQL `course_schedule_slots` tablosu kontrol edildi.
- Toplam `1641` schedule satiri vardi; ancak department alaninda su tur kirli degerler goruldu:
  - `2526baharbiyolojidp`
  - `2526baharfizikson`
  - `2526baharilkmatsonnn`
  - `2025_2026_bahar_ders_programı_güncel_xlsx_ders_programı`
  - `derstir. Bu dersin`
- Kok neden: kaynak metinden bolum adi cikarilamayinca ingest fallback olarak dosya adini veya yanlis preview cumlesini department kabul edebiliyordu.
- Bu, bugun her soruyu bozmayabilir; fakat ileride "bolum ders programi" eslesmelerinde, listeleme/raporlama islerinde ve schedule kapsam analizinde kirli bolum isimleri uretebilir.

Yapilan:
- `src/db/schedule_ingest.py` icine inferred department plausibility kontrolu eklendi.
- Dosya adi/preview metni bolum adi gibi gorunmuyorsa artik `bilinmiyor` kabul ediliyor ve schedule slotlari DB'ye yazilmiyor.
- Acik ve betimleyici dosya adlari icin genel filename temizleyici eklendi:
  - `2025_2026_bahar_resim_is_ogretmenligi_ders_programi.xlsx` -> `Resim Is Ogretmenligi`
  - `25_26_bahar_sinif_egt_ders_prog.pdf` -> `Sinif Ogretmenligi`
  - `okl_lisans_...` -> `Okul Oncesi Ogretmenligi`
- Kompakt/kriptik adlar (`2526baharfizikson` gibi) otomatik bolum sayilmiyor; bunlar icin explicit metadata veya `--department` ile bilincli ingest gerekir.

Yapilmayan:
- Canli DB'ye yazma islemi yapilmadi.
- `scripts.ingest_schedule_slots --dry-run` sonucu yeni kuralla `35` kaynaktan `18` tanesi bos olmayan sonuc verdi ve `1175` satir cikardi.
- Bu sayi mevcut `1641` satirdan dusuk oldugu icin, kayipsiz temizlik yapmadan once kriptik kaynaklar icin canonical source metadata/override karari gerekiyor.

Neden statik degil:
- Belirli soruya cevap yazilmadi.
- Bu, kaynak ingest metadata hijyeni: sahte bolum adi uretilmesini engeller, dogru bolum bilgisi olmayan dosyalari explicit metadata gerektiren kaynak olarak isaretler.

Dogrulama:
- Canli DB sayimi:
  - `course_schedule_slots = 1641`
  - `tuition_fee_catalog = 16`
- Dry-run:
  - `python -m scripts.ingest_schedule_slots --source data/raw/academic_programs/ders_programlari --dry-run`
- Testler:
  - `tests/unit/test_schedule_ingest.py`
  - `tests/unit/test_schedule_data.py`
- Compile:
  - `python -m py_compile src/db/schedule_ingest.py src/db/schedule_data.py src/agents/academic/curriculum_agent.py`

### 49. RAG fallback ve canli retrieval-service build durumu ayrildi

Durum:
- Canli `retrieval-service` health endpoint'i saglikli gorundu; embedding ve reranker CUDA uzerinde isitilmis durumda.
- Ancak canli build id `codex-20260428-162104`; yerel kodda daha sonra yapilan search planner ve schedule ingest duzeltmeleri bu container'a henuz yansimis degil.
- Bu nedenle canli smoke testte `Bagil degerlendirme...` sorgusu yalniz `academic_programs_docs` icinden arama yapmis gibi davranip lisansustu/uzaktan egitim kaynaklarini one cikardi.
- Yerel planner ayni sorguda `academic_programs_docs` ve `student_affairs_docs` koleksiyonlarini primary olarak planliyor; yani bu spesifik semptom kod mantigindan cok stale container/build problemi.

RAG akisi:
- Retrieval ilk asamada planlanan primary koleksiyonlarda BM25 + Chroma adaylarini topluyor.
- Adaylar dedupe ediliyor, kaynak/topic/profil biaslari uygulanıyor.
- Cross-encoder reranker aday havuzunu tekrar siraliyor.
- Son sentezden once LLM evidence selector, aday kanitlar arasindan cevaba en dogrudan destek olanlari seciyor veya `insufficient_evidence` diyebiliyor.
- Yani sistem normalde "ilk 3 belgeyi korlemesine kullan" seklinde calismiyor; fakat dogru kaynak havuzunun ilk basta adaylara girmesi hala kritik.

Onemli bulgu:
- `HybridRetriever._collect_candidates()` fallback koleksiyonlarini yalnizca primary koleksiyonlardan hic aday donmezse calistiriyor.
- Primary koleksiyon aday doner ama adaylar zayif/alakasizsa fallback otomatik devreye girmiyor.
- Bu bilincli olarak genis fallback gurultusunu ve latency'yi azaltan bir tercih; kalite problemi varsa oncelikli cozum gerekli koleksiyonu planner tarafinda primary havuza almak.
- Bu nedenle `bagil/mutlak degerlendirme` gibi sinir konularda yaptigimiz dogru yaklasim fallback'i genisletmek degil, ilgili `student_affairs_docs` kaynagini primary plana eklemek.

Yapilmayan:
- Fallback'i her zayif skorda otomatik acan genel bir kural eklenmedi.
- Bunun yerine mevcut mimari tercihi dokumante edildi: fallback bos primary durumunun emniyetidir; zayif primary durumunda planner/evidence selector/reranker iyilestirmeleri tercih edilir.

Operasyonel not:
- Yerel kod degisikligi canli A2A/Docker davranisina yansisin diye image rebuild ve rollout gerekir.
- Sadece `--skip-build` ile kalkmak, eski image icinde kalinan durumlarda planner/retrieval duzeltmelerini canli sisteme tasimaz.

### 50. Reranker model konfigrasyonu aktif ortam, kod varsayilani ve dokumanlarda tutarsizdi

Durum:
- Aktif `.env` ve benchmark ciktisi reranker olarak `nreimers/mmarco-mMiniLMv2-L6-H384-v1` kullaniyor.
- `src/rag/reranker.py` icindeki kalibrasyon yorumu da bu model icin hesaplanan parametrelere isaret ediyor.
- Buna ragmen `src/core/config.py`, `.env.example`, `README.md` ve bazi teknik dokumanlarda eski `seroe/bge-reranker-v2-m3-turkish-triplet` modeli varsayilan/onerilen model gibi gorunuyordu.
- Risk: temiz kurulumda veya arkadasin makinesinde `.env` eksikse farkli reranker modeliyle kalkilabilir; kalite, skor kalibrasyonu ve local-files-only model cache davranisi degisebilir.

Yapilan:
- Kod varsayilani `nreimers/mmarco-mMiniLMv2-L6-H384-v1` ile guncellendi.
- `.env.example` ayni modelle hizalandi.
- `README.md`, `docs/KURULUM_VE_CALISTIRMA.md`, `docs/kapsamli_chromadb_kilavuzu.md` ve `docs/FAZ_1_TEKNIK_DOKUMANTASYON.md` icindeki eski reranker referanslari guncellendi.

Neden statik degil:
- Soru bazli davranis veya sabit cevap eklenmedi.
- Bu, model/runtime konfigurasyonunun tek kaynaga hizalanmasi; ayni kodun farkli ortamda farkli reranker ile calismasini engeller.

Dogrulama:
- Aktif `.env`:
  - `RERANKER_MODEL=nreimers/mmarco-mMiniLMv2-L6-H384-v1`
- Canli `retrieval-service`:
  - `embedding_device=cuda`
  - `reranker_device=cuda`
  - `warmup.complete=true`
- Chroma/registry sayilari:
  - `student_affairs_docs = 1802`
  - `academic_programs_docs = 5057`
  - `finance_docs = 56`
  - `academic_schedules_docs = 119`

### 51. Full index oncesi corpus ve akademik kaynak kapsami tekrar denetlendi

Durum:
- `scripts.audit_document_corpus` ile raw corpus, registry ve Chroma sayilari tekrar kontrol edildi.
- Chroma/registry tutarliligi tum aktif koleksiyonlarda `OK`.
- `scripts.audit_academic_source_coverage --fail-on-missing` genel tracked duyuru kaynaklari icin curriculum/schedule kapsamini `ok` verdi.
- Ancak Fizik schedule tarafinda bahar donemi hala `2526baharfizikson` gibi kriptik kaynak adiyla raporlaniyor.

Bulgu:
- Chroma tarafinda full reindex guvenli gorunuyor; registry ile canli Chroma sayilari tutarli.
- Structured `course_schedule_slots` tablosu icin durum farkli: yeni ingest hijyeni kriptik dosya adlarini otomatik bolum saymayacagi icin dogrudan DB yazimi mevcut kirli satirlari temizlerken toplam satir sayisini azaltabilir.
- Bu nedenle full test oncesi:
  - RAG/Chroma koleksiyonlari reindex edilebilir.
  - Schedule structured ETL once `--dry-run` ile calistirilmali.
  - DB'ye yazma adimi, kriptik kaynaklar icin explicit source metadata/override tamamlaninca yapilmali.

Dogrulama:
- Raw kaynak sayilari:
  - `data/raw/student_affairs`: 115 dosya
  - `data/raw/academic_programs`: 248 dosya
  - `data/raw/academic_programs/ders_programlari`: 35 dosya
  - `data/raw/finance`: 6 dosya
- Unsupported dosyalar:
  - `.xlsx`: 4
  - `.doc`: 4
  - extension yok: 3 (`.gitkeep` dahil)
- Chroma/registry:
  - `student_affairs_docs`: 1802/1802
  - `academic_programs_docs`: 5057/5057
  - `finance_docs`: 56/56
  - `academic_schedules_docs`: 119/119
