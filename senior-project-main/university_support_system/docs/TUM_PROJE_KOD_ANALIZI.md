# ÜNİVERSİTE KURUMSAL DESTEK SİSTEMİ 
# KÜLLİYAT: TÜM PROJE KOD ANALİZİ VE METOD REFERANS REHBERİ

Bu devasa referans dosyası, projede bulunan (aktif durumdaki) **her bir sınıfın, her bir metodun ve her bir mimari tasarım kararının** en alt seviyede detaylandırılarak, projeyi hiç bilmeyen birine anlatır gibi veya jüri/sunum esnasında referans gösterilmek üzere hazırlanmış "Ana Kod Külliyatı"dır.

---

## BÖLÜM 1: ÇEKİRDEK (CORE) KATMANI
Sistemin beynidir. Tüm konfigürasyonlar (şifreler, portlar) ve değişmez ayarlar (sabitler) burada yaşar.

### 1.1. `src/core/config.py`
Projenin gizli şifrelerini ve ince ayarlarını barındıran konfigürasyon yöneticisidir. Çevresel `.env` dosyasını okuyup Python sınıflarına çevirir (Pydantic). 
*   **`PostgresSettings` Sınıfı:** DB host, port (5432), kullanıcı ve şifresini tutar.
    *   *`async_url` (property):* PostgreSQL'e asenkron bağlanmak için gerekli olan `postgresql+asyncpg://...` metnini otomatik formatlar.
*   **`RedisSettings` Sınıfı:** Kuyruk ve önbellekleme (Cache) için Redis URL (6379) dizgesi oluşturur.
*   **`ChromaSettings` Sınıfı:** Vektör arama motorunun HTTP portunu (8100) ayarlar, `url` isimli computed field (property) ile sunar.
*   **`EmbeddingSettings` Sınıfı:** Yapay zekanın (BAAI/bge-m3) kaç boyutlu (1024-D) matris çıkaracağını ve limitlerini bilir.
*   **`RAGSettings` Sınıfı:** `chunk_size` (1024), `chunk_overlap` (128) ve `top_k` (Aramada dönecek sonuç sayısı: 5) ayarlarını standartlaştırır.
*   **`Settings` Sınıfı (Singleton):** Python dosya yüklenir yüklenmez yukarıdaki tüm küçük ayar sınıflarını (Postgres, RAG vb.) tek bir devasa `settings` nesnesine toplar. Projedeki herkes `from config import settings` yazarak bu tek objeden veri çeker.

### 1.2. `src/core/constants.py`
Sistem genelinde kullanılacak kural isimlerini metin (String) kalabalığından kurtarıp, kod yazarken otomatik tamamlanan `Enum` yapılarına (Sabitlere) dönüştürür.
*   **`Department` (Enum):** FINANCE (Finans), IT (Bilgi İşlem), STUDENT_AFFAIRS (Öğrenci İşleri).
    *   *`display_name` (property):* Enum'un Türkçe görünen adını basar. API'den hata dönerken "Öğrenci İşleri" yazmasını sağlar.
*   **`TaskType` (Enum):** LLM'e giden sorunun tipini tutar (`COURSE_QUERY`, `TUITION_QUERY` vb.).
*   **`RoutingStrategy` (Enum):** Gelen sorunun LLM tarafından ne yapılacağını belirler. (Direkt ilgili departmana gönder `DIRECT`, veya ne dediğini anlamadım soruyu netleştir `CLARIFICATION`).
*   **`ConfidenceLevel` (Enum):** Karar güvenilirliği sınıfı (`HIGH`, `MEDIUM`, `LOW`).
*   **Global Sabit Eşikleri:** `ROUTING_HIGH_CONFIDENCE_THRESHOLD = 0.7`, `RAG_RESPONSE_TIME_TARGET_MS = 100` gibi sınır değerleri. Biri şikayet ederse sistemi yavaşlatan sınır sadece buradan değiştirilip çözülür.

---

## BÖLÜM 2: VERİTABANI (DB) KATMANI
Uygulamanın PostgreSQL ile konuştuğu ve kaydedilecek tabloların çizildiği yerdir.

### 2.1. `src/db/connection.py`
PostgreSQL'e bağlanan Asenkron Motoru (Engine) yönetir. 
*   **Kritik Tasarım (Lazy Init):** Kod import edilir edilmez veritabanı TCP pingi atmasın diye `_engine = None` ile bekletir.
*   **`get_engine()` (Metod):** Eğer motor yoksa `create_async_engine` (SQLAlchemy) ile yaratır, Connection Pool (havuz boyutu=10) tahsis eder.
*   **`get_session_factory()` (Metod):** Gelen her HTTP isteği veya script için geçici bir DB oturumu yaratıcı fabrikası döndürür.
*   **`get_session()` (AsyncContextManager):** Asıl veritabanı okuyucusu budur. Otomatik olarak (Transaction) bir oturum açar (Yield işlemi), yazma başarılıysa `commit()` eder, çökerse anında `rollback()` atar ki sistem kilitlenmesin (Deadlock önleyici).
*   **`check_db_health()` (Metod):** Sisteme "SELECT 1" isimli mikro-sorgu fırlatıp milisaniye cinsinden gecikme (latency) hesaplar. "Ping pong" mantığıdır.

### 2.2. `src/db/models.py`
SQL kodları yazmak yerine, veritabanı tablolarını Python sınıfları (Class) gibi göstermeye yarayan ORM (Object-Relational Mapping) dosyasıdır.
*   **`TimestampMixin` (Sınıf):** Altındaki tüm tablolara zorunlu olarak `created_at` (oluşturulma) ve `updated_at` (güncellenme) saatleri ekler. Hiçbir zaman el ile yazılmaz, veritabanı saati (UTC) otomatik basılır.
*   **Öğrenci İşleri Tabloları:**
    *   `Student`: Öğrencinin kimlik, e‑posta, bölüm/fakülte, sınıf, GNO ve toplam/tamamlanan kredi bilgilerini tutar.
    *   `Course`: Ders kodları, adları, kredileri ve hangi bölüm/yarıyılda açıldığını tutar.
    *   `CoursePrerequisite`: Bir dersin diğer derslere olan önkoşul ilişkisini Many‑to‑Many köprü tablo olarak modeller.
    *   `StudentCourse`: Hangi öğrencinin hangi dersi hangi dönemde aldığını, harf notunu ve durumunu (`enrolled/completed/...`) tutar.
    *   `CourseRegistrationPeriod`: Her dönem için ders kayıt başlangıç/bitiş tarihlerini ve aktiflik bilgisini saklar.
*   **Finans & Burs Tabloları:**
    *   `Tuition`, `Payment`, `Installment`: Öğrencinin dönemlik harç toplamını, yaptığı ödemeleri ve varsa taksit planını tutar. `has_debt` ve `debt_amount` alanları PostgreSQL'de GENERATED kolon olarak otomatik hesaplanır.
    *   `AvailableScholarship`, `Scholarship`, `ScholarshipApplication`: Burs ilan kataloğu, öğrenciye atanmış burslar ve başvuru geçmişini temsil eder.
*   **Kimlik Doğrulama & Duyuru Tabloları:**
    *   `OTPCode`, `VerificationSession`, `SlackStudentMapping`: OTP kodlarının hash'lerini, doğrulanmış oturumları ve Slack kullanıcılarının öğrencilerle eşlemesini tutan runtime tablolardır.
    *   `Announcement`: Üniversite/fakülte/bölüm duyurularının ham metni, LLM özeti ve kaynak URL'sini saklar.
*   **Ajan / Telemetri Tabloları:**
    *   `AgentRegistry`: Aktif yapay zekaların (ana/departman/uzman ajanların) kayıtlı olduğu ajan envanteri tablosudur.
    *   `QueryLog`: Kullanıcının sorduğu her soruyu, yönlendirme stratejisini, güven skorunu ve yanıt süresini (`response_time_ms`) kaydeder; ek JSON bilgiler Python tarafında `query_metadata` alanı üzerinden tutulur.
    *   `AgentTask`: A2A protokolü üzerinden ajanlar arasında dolaşan görevlerin gönderilme, işlenme ve sonuçlanma adımlarını kayıt altına alır.

### 2.3. `src/db/schemas.py`
Modeller veritabanına giderken, Schema'lar kullanıcıdan / frontend'den gelen JSON verilerini filtreleyen güvenlik duvarıdır (Pydantic Doğrulaması).
*   **`RAGQuery` (Schema):** Birisi arama yaparken sisteme sorusunu (`query`), departmanını (`department`) yollamasını zorunlu kılar. `top_k` parametresinin 20'yi aşmamasını otomatik doğrular, aşarsa kullanıcıya "422 Unprocessable Entity" hatası atar.
*   **`RAGSource` (Schema):** RAG yapıldığında, bulunan kaynağın benzerlik skorunu ve adını sisteme temiz paketler.
*   **`RoutingResult` (Schema):** LLM, öğrencinin sorusunu incelediğinde sisteme "bu soru Finance'a aittir, güvenim 0.95" (`confidence`) isimli bir paket döndürür. Bu sınıf LLM'in cevabını kurala sokar.
*   **`SystemHealthResponse` (Schema):** API çöktüğünde veya bakım (health) istendiğinde servislerin ms cinsinden listesini sunuculara fırlatır.

---

## BÖLÜM 3: RAG (VEKTÖR ARAMA) KATMANI
Projenin Faz 1 kalbidir. Yönetmeliklerin PDF/TXT okumalarından başlar, ChromaDB'ye matris olarak inmesine ve geri kelime-benzerlik (Hibrit) olarak bulunmasına kadar her şeyi yönetir.

### 3.1. `src/rag/document_loader.py`
*   **`Document` Sınıfı:** Yüklenen belgeyi tutar. İçerisinde `char_count` ve `word_count` property'leri (istatistik sağlayıcılar) barındırır.
*   **`DocumentLoader` Sınıfı & Metodları:** 
    *   `load_file()`: Dosya uzantısına bakar (pdf, txt). Eğer 50 karakterden az (min_content) sayfa çıkarsa fırlatıp atar (Kapak sayfası / Boş sayfa filtresi).
    *   `load_directory()`: Özyinelemeli olarak klasörü (ve alt klasörleri) gezer. Klasör adını "Kategori" olarak `Metadata`'ya kaydeder (Örn: "yonerge_cift_anadal.pdf" dosyası "yönergeler" dizinindeyse Category=yönergeler olur).
    *   `_load_pdf()`: **pdfplumber** motoru kullanılarak her sayfanın metni çıkarılıp çift enter (`\n\n`) ile puzzle gibi birleştirilir.
    *   `_load_txt()`: Türkiye'deki eski Windows dosyaları için muazzam bir Fallback'tir. Önce `UTF-8` dener, hata alırsa Windows ANSI `cp1254` ile dener.

### 3.2. `src/rag/text_preprocessor.py`
Algoritma ve RegEx dolu Metin Temizlikçisi. Vektörün kirli cümleler ezberlemesini önler.
*   **RegEx Kuralları:** Dosyadaki `RE_DOC_REFERENCE` (sayfa 1/6 silici), `RE_KONTROLSUZ` ("Bu belgenin fiziki hali geçersizdir" gibi imza altı yazı silicileri) barındırır.
*   **`clean(text)` (Metod):** Hammaddeyi sırasıyla tüm alt temizleyicilere gönderir.
*   **`_remove_header_footer_repeats(text)` (Algoritma):** Metni satır satır yırtar. Python sözlüğü (Dict) içinde o satır belgede kaç kez geçiyor diye frekans sayar. Eğer 3'ten fazla geçiyorsa (T.C. ONDOKUZ MAYIS yazısı gibi) "Bu bir Header'dır ve anlamı yoktur" diyerek tamamını uzay boşluğuna yollar.

### 3.3. `src/rag/chunker.py`
Yasal metinleri Yapay Zeka sınırlarında (max 1024 karakter) porsiyonlayan şeften (MADDE-Aware Algoritması) sorumludur.
*   **Standart:** Çoğu amatör proje dümdüz 1000 karakter geldiğinde yazıyı "bıçak gibi" keser (Kelimenin veya maddenin ortası fark etmez). Chunk'lar anlamsızlaşır.
*   **`TextChunker` Sınıfı & Metodları:**
    *   `_split_by_madde()`: Önce PDF belgesini "MADDE 1 -", "MADDE 2 -" bularak onlara göre böler. Böylece 1 madde tek porsiyon olur.
    *   `split_text()` (Zorunlu ayırma): Eğer MADDE 6 o kadar uzundur ki 3000 karakterdir (bölmek zorundayız), onu da 1000'erlik 3 alt parçaya böler. **Ancak**, bölünen 2. ve 3. parçanın başına enjekte olarak `[Ek: Madde 6 Bağlamı]` yazısını aşılar. Bu sayede LLM sadece 3. parçayı okuduğunda o cümlenin Madde 6'nın lafı olduğunu hatırlar.
    *   `get_stats()`: Ortalamada metinlerin yüzde kaçta bölündüğünü ölçen test metodudur.

### 3.4. `src/rag/embedder.py`
Kelimeleri uzay boşluğunda X, Y, Z (gibi uzayan 1024 boyutlu) koordinat düzlemine oturtur. (Yapay zeka embedding i).
*   **`Embedder` Sınıfı & Metodları:** Model olarak `BAAI/bge-m3` kullanır. RAM'de gereksiz yer kaplamasın diye `@property` yapısıyla "Lazy initialization" ile tetiklendiğinde PyTorch üzerinden yüklenir.
*   `embed_texts()`: 100 metin verirsen, aynı anda tensör çarpımlarına sokup Batch (küme) işlemiyle süreyi beşte birine indirir. (Normalize = True kullanılarak, Cosine Similarity hesaplarında vektör uzunluğu 1'e sabitlenir, bu da ChromaDB'nin süper hızlı mesafeler bulmasını sağlar).

### 3.5. `src/rag/indexer.py`
PostgreSQL değil, bu özel vektörlerleri depolamak için **ChromaDB Vektör Veritabanı** motoruyla REST (HTTP/httpx) diliyle konuşan sınıf.
*   **Tasarım Kararı:** ChromaDB'yi paket olarak (`pip install chromadb`) projeye dahil etmek Windows C++ hataları yüzünden yasaklanmıştır. Bunun yerine Docker'daki API ile sadece HTTP POST/GET istekleri atılarak haberleşir (Mikroservis mimari adaptasyonu).
*   **Metodlar:**
    *   `create_collection()`: Veritabanında bir sepet uydurur.
    *   `_batch_write()`: HTTP Payload-Too-Large (Boyut Çok Büyük) hatası almamak için ne kadar devasa olursa olsun veriyi 100'lü sayfalara bölerek veritabanına ekler.
    *   `upsert_documents()`: İçeriğinde hash algoritması koruması vardır. Aynı Chunk, veritabanına bir kez eklendiğinde aynı ID ile ikinci kez gelirse eskisiyle yeniler (Duplicate/Mükerrer kayıdı kökten önler).

### 3.6. `src/rag/query_preprocessor.py`
Yapay zekaya soru gidene kadar sorular üzerinde ameliyat yaparak kurnazlık katan kural motoru. Arama sonucunu %30 iyileştirir.
*   **`_split_compound_words()`:** Kullanıcı soruda bilmeden "anadal" yazarsa, sistem PDF belgesindeki resmi yapıya uysun diye arkada gizlice onu "ana dal" olarak boşlukla böler.
*   **`_expand_synonyms()` (Arama Genişletmesi Algoritması):** Dictionary haritası üzerinden çalışır. "ÇAP yapcam" dersen `çap` kelimesini yakalayıp cümlenin arkasına hayalet olarak `"çift ana dal ikinci lisans"` ekler. ChromaDB "çap" kelimesini bulamasa bile "ikinci lisans" kelimesini yakaladığı PDF'i getirerek doğru cevabı bulur.
*   **`detect_query_type()`:** Sorunun içinde "ne zaman, nerede, nasıl" kelimesi varsa "Bu Soru Prosedüreldir (Yönetmelik/Nasıl yapılır)" flag'i döndürerek LLM'i uyarır.

### 3.7. `src/rag/retriever.py`
Projeyi "İleri seviye RAG (Advanced RAG)" sınıfına sokan Orkestratör beyin. Vektör ile TF-IDF motorlarını tek merkeze toplar.
*   **Algoritma: Hybrid Arama & RRF Puanlaması:** Sadece anlam veya sadece kelime eşleştirmesi aramaz. İkisini paralel aratıp LangChain'in `EnsembleRetriever` özelliği ile sonuçları ağırlıklarla (`bm25_weight=0.5, chroma_weight=0.5` veya parametrik) Reciprocal Rank Fusion matematiğine göre toplar. Hem kelimesi (exact) tutan, hem anlamı tutan belge zirveye çıkar.
*   **Metodlar:**
    *   `turkish_bm25_preprocess(text)`: BM25 arama motoruna özel bir Custom Tokenizer'dır. Virgül/nokta siler, compound kelimeleri ayırır (anadal->ana dal). 
    *   `_apply_source_relevance(results, query)`: False-Positive önleyici harika ceza mekanizmasıdır. "Yaz okulu" aratan birinin listesinde alakasız yere "Staj yönergesi" puan aldıysa; sorudaki kelime kümelerini dökümanın başlığında (Source) arar. Uyuşmazsa `0.75` skor cezası (penalty) çarpanı uygulayarak stajı sıralamada dibe atar.
    *   `search()`: İki arama motorunuda koşturup cevabı verir. Dedup mekanizması (kopya içerik ayıklayıcısı) ile aynı içerikler dönerse sadece Max skorlusunu tutarak çöpe yollar (`sim_score > candidates[idx]["score"]` algoritması).

### 3.8. `src/rag/reranker.py`
Arama yapıldı. Getirilen 20 metin gerçekten öğrencinin yazdığı yediğimiz soruya cevap niteliği taşıyor mu? Bunu kontrol eden asıl denetmen ağ (Cross-Encoder).
*   **Standart (Bi-Encoder vs Cross-Encoder):** 80 bin belge, sorular belli olmadan önce hızlıca (BGE-m3 ile) bağımsız (Bi) vektörlenir... Ancak soru geldiğinde, en iyi 20 sonuç bulunup Cross-Encoder modeline verilir. Bu ağır model, *soruyu* ve *20 cevabın her birini* yan yana koyup harf harf tekrar ilişkilendirme skoru (Score prediction) hesaplar.
*   **`predict()/rerank()` (Metodlar):** 20 sonucun her birini Pytorch batch'ına sokar, Sigmoid skorlarla (-20 ile +10 arası floating-puanlarla) listeyi yeniden dizer. Sadece zirvedeki en mantıklı "Top_K = 5" sonucu RAG'a fırlatır. Kalan (False-Positive) çöpler tamamen silinir.

### 3.9. `src/rag/pipeline.py`
İndeksleme yaparken çalıştırılan Fabrika/Gemi Kaptanı dosyadır.
*   **`run(source_dir)` (Süreç Algoritması):** 
    1) Klasöre git PDF'leri topla (Loader).
    2) Hops, hepsinden header/footer temizle (Preprocessor).
    3) MADDE MADDE böl, metadata logu at. (Chunker).
    4) Model ayağa kaldır (Embedder) vektör çıkar. 
    5) Aynı dosyalar tekrar gelmesin diye metinin Hash (SHA-256) karşılığını ID'si (Kimlik No) yap.
    6) ChromaDB'ye 100'er adet yolla (Indexer).
    7) En son `data/metadata/doc_registry.json` isimli log dosyasına "Saat X'te, Y adet dosyadan, Z adet chunk çıkardım" diyerek istatistik (telemetri) yazıp işlemi bitir!

---

## BÖLÜM 4: BETİKLER (SCRIPTS) KATMANI
RAG ile oynadığımız geliştirici / otomasyon araçlarıdır.

*   **`scripts/index_documents.py`:** Konsoldan veritabanı kurulumu yapar. Argparse kural kütüphanesi ile `python index_documents.py --chunk-size 512 --reindex` gibi argümanları alır ve asıl RAG `pipeline.run()` fonksiyonunu işletir.
*   **`scripts/evaluate_rag.py`:** Otomatik zeka (RAGTest) test sistemidir. İçerisinde 19 tane sahte zorlu öğrenci sorusu (Örn: Hem GANO 1.5 iken ÇAP yapılır mı?) sorup, RAG'ın doğru PDF'i çekip çekmediği sayar. `compute_metrics()` altında *Precision@1* (ilk sonuçta vurdum), *Precision@3* (vites 3te vurdum) metriklerini orantılayıp devasa `docs/rag_evaluation_report.md` rapor dosyasını Markdown'a basar.
*   **`scripts/query_db.py`:** Saf arama denemesidir. Kelimelere, reranker'a falan takılmadan ChromaDB vektör uzayında E5 Prefix ekleyerek ham sorgu testleri atar geliştiriciye CLI çıktıları (Console prints) yollar.
*   **`scripts/test_hybrid_search.py`:** En ileri sistem sorgucusudur. BM25 (Kelime) ve Vector (Anlam) ağırlıklarını dengeler. Terminale "Kayıt dondurma nasıl yapılır?" yazınca, Sinonim sözlüğünün (genişletmenin) kelimeye eklenip eklenmediğini (Debug/Verbose modda) gösterir ve 1-den-5'e kadar skorlayarak Terminaldeki en güzel görünümü basar.
*   **`scripts/compare_collections.py`:** Bilimsel analiz aracı. Veritabanını 3 farklı şekilde (256, 512, 1024 boyutla) kestiğimizde paralel bağlayıp "Hangi kesintide LLM daha nokta atışı hit buldu?" diye tablolaşmış çıktı üretmeye yarar. (Araştırma modülü).

### SONUÇ / PROJE DEĞERLENDİRMESİ
Oluşturulan mimari, basit bir *Prompt -> LLM / LangChain* zincirlemesinin ötesinde; **Bağlantı Havuzlamalı Async Veritabanı (Event-loop non-blocking DB), Pydantic Kalkanlarıyla Korunan Objeler (Domain Driven Design), Lazy Loader Model Yönetimi, RegEx Temizlikçisi ve 3 Taraflı (Keyword + Vector + Reranker) False Positive Eliminasyon** algoritması üzerine inşa edilmiş çok ağır kurumsal standartlı bir "Arama & Bilgi Bulma (RAG)" yazılımıdır. 

Bu rehberi her türlü IT sunumunda, raporlamada veya tez (kavramsal algoritma) açıklamasında kodlarınızın altyapısının arkasındaki muazzam mühendisliği kanıtlamak için direkt olarak referans gösterebilirsiniz.
