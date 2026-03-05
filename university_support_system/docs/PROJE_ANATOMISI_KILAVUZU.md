# Üniversite Kurumsal Destek Sistemi 
# PROJE ANATOMİSİ VE MODÜL KILAVUZU (V1.0)

Bu doküman, projenin sadece belirli bir fazını değil; **tüm mimarisini, dizin yapısını, core (çekirdek), db (veritabanı) ve rag (arama)** modüllerindeki dosyaların tam olarak ne işe yaradığını, içerisindeki metodları ve tasarım kararlarını detaylandıran ana başvuru (reference) kaynağıdır.

---

## 🏗️ GENEL PROJE KLASÖR YAPISI (`src/` dizini)

Sistem modüler ve Domain-Driven Design (DDD) prensiplerine uygun tasarlanmıştır.

*   `src/core/`: Sistem genelinde kullanılan sabitler, konfigürasyonlar ve tipler.
*   `src/db/`: Veritabanı bağlantısı, ORM modelleri, Pydantic doğrulama şemaları.
*   `src/rag/`: Doküman vektörizasyonu, hibrit arama ve LLM'e beslenecek bağlamın çıkarılması.
*   `src/llm/` *(FAZ 2 Planlı)*: LLM bağlantıları ve prompt şablonları.
*   `src/agents/` *(FAZ 2 Planlı)*: Spesifik konularda (IT, Öğrenci İşleri) görev yapacak uzman yapay zekalar.
*   `src/api/` *(FAZ 4 Planlı)*: Dış dünyaya açılan FastAPI gateway.
*   `src/orchestrators/` *(FAZ 3 Planlı)*: Ajanları yöneten ana beyin sınıfları.

Aşağıda, halihazırda kodlanmış ve mimarisi oturtulmuş aktif modüllerin satır satır analizi bulunmaktadır.

---

## 1. ÇEKİRDEK (CORE) KATMANI
Sistemin çalışması için gerekli çevresel değişkenleri ve kod geneli sabitleri tutar.

### 📄 `src/core/config.py`
Projeye ait ortam (Environment/.env) değişkenlerini doğrulanmış sınıflara çevirir. `pydantic-settings` kütüphanesini kullanır. Tip güvenliğini sağlar.

*   **Algoritma / Tasarım:** Pydantic `BaseSettings` kullanılarak `POSTGRES_`, `REDIS_`, `OLLAMA_` gibi prefix'lerle başlayan çevresel değişkenleri RAM'de önbellekler.
*   **İlgili Sınıflar:**
    *   `PostgresSettings`: DB host, port, havuz (pool_size=10) sınırları.
    *   `EmbeddingSettings`: Vektör modelinin (BAAI/bge-m3) boyutunu (1024-D) tutar.
    *   `RerankerSettings`: Cross-encoder modelini ve batch_size sınırlarını belirler.
    *   `RAGSettings`: Chunk_size (1024) ve top_k (5) gibi arama limitlerini barındırır.
    *   `Settings`: En dipteki *Singleton* sınıftır. Tüm projede `from src.core.config import settings` ile tekilleştirilmiş (sadece bir kere initialize edilen) konfigürasyonu dağıtır.

### 📄 `src/core/constants.py`
Uygulamada "sihirli stringleri (magic strings)" önlemek için kullanılan `Enum` ve sabit deposu.
*   **İlgili Enum'lar:**
    *   `Department`: Olası departman adlarını (FINANCE, IT, STUDENT_AFFAIRS) ve Türkçe karşılıklarını (display_name property) barındırır.
    *   `TaskType`: LLM veya Kural Motoru bir soruyu incelediğinde bunun "Ders Sorgusu mu (COURSE_QUERY)" yoksa "Harç Sorgusu mu (TUITION_QUERY)" olduğunu belirten labellerdir.
    *   `RoutingStrategy`: Sorgunun nasıl devam edeceğini belirler (DIRECT, CLARIFICATION vb.).
*   **İlgili Sabitler (Thresholds):** `ROUTING_HIGH_CONFIDENCE_THRESHOLD = 0.7`, `RAG_RESPONSE_TIME_TARGET_MS = 100` gibi kalite ve karar mekanizması eşiklerini metin içinde tutarak kodun modüler olmasını sağlar.

---

## 2. VERİTABANI (DB) KATMANI
PostgreSQL işlemlerinin (Read-Write) asenkron olarak (asyncpg) yönetildiği katman.

### 📄 `src/db/connection.py`
Uygulama ile veritabanı (PostgreSQL) arasındaki köprüyü Asenkron kurar ve yönetir.
*   **Tasarım / Algoritma (Lazy Initialization):** `_engine` değişkeni en başta null (None) olarak durur. Python kodları import edildiği an gidip DB'ye boşuna bağlanmaya çalışmaz. Ne zaman ki veritabanına gerçekten ihtiyaç olursa (`get_engine` çağrılırsa) TCP bağlantısını açar. Bu test yazmayı inanılmaz kolaylaştıran bir mimaridir.
*   **Metodlar:**
    *   `get_session()`: Bir "AsyncContextManager" (yield) dır. Veritabanına bir sorgu girdiği an *session* başlatır, başarıyla biterse *commit*, hata patlarsa veritabanı yorulmasın diye *rollback* fırlatır ve bağlantıyı havuza iade eder.
    *   `check_db_health()`: `SELECT 1` sorgusu atıp veritabanına gidiş-dönüş milisaniyesini (latency) ölçerek "healthy" raporu verir.

### 📄 `src/db/models.py`
Veri tabanındaki tabloların Python sınıflarına döküldüğü (SQLAlchemy ORM) dosyadır. İş mantığının kalbidir.
*   **Ortak Mixin (`TimestampMixin`)**: Tüm ORM modelleri bu sınıfı miras (inherit) alır. Bu sayede her veritabanı satırında `created_at` ve `updated_at` kolonları otomatik açılır ve UTC saatine göre, geliştirici müdahalesi olmadan, zaman damgası basılır.
*   **Öğrenci İşleri Tabloları:**  
    *   `Student`: Öğrencinin kimlik, bölüm/fakülte, sınıf, GNO ve toplam/tamamlanan kredi bilgilerini tutar.  
    *   `Course`: Ders kataloğu; ders kodu, ad, kredi, bölüm ve dönem bilgisi.  
    *   `CoursePrerequisite`: Bir dersin diğer derslere olan **önkoşul** ilişkilerini tutan join tablosu.  
    *   `StudentCourse`: Hangi öğrencinin hangi dersi hangi dönemde aldığını ve notunu tutan Many-to-Many köprüsüdür.  
    *   `CourseRegistrationPeriod`: "Ders kaydı ne zaman yapılır?" sorusunun tarih tarafını tutar (dönem bazlı başlangıç/bitiş).
*   **Finans / Burs Tabloları:**  
    *   `Tuition`, `Payment`, `Installment`: Öğrencinin dönemlik harç toplamını, yaptığı ödemeleri ve varsa taksit planını tutar. `has_debt` ve `debt_amount` alanları PostgreSQL tarafından otomatik hesaplanır.  
    *   `AvailableScholarship`, `Scholarship`, `ScholarshipApplication`: Üniversitenin burs ilanlarını, öğrencinin aktif burslarını ve başvuru geçmişini modeller.
*   **Kimlik Doğrulama ve Duyuru Tabloları:**  
    *   `OTPCode`, `VerificationSession`, `SlackStudentMapping`: OTP tabanlı kimlik doğrulama ve Slack kullanıcılarını öğrencilerle eşleştirmek için kullanılan runtime tablolardır.  
    *   `Announcement`: Üniversite/fakülte duyurularının ham metnini ve LLM özetini saklar; bölüm/fakülte filtresiyle öğrenciye uygun duyurular seçilir.
*   **Ajan / Telemetri Tabloları:**  
    *   `AgentRegistry`: Aktif yapay zekaların (ana/departman/uzman ajanların) kartlarının tutulduğu "ajan envanteri" tablosudur.  
    *   `QueryLog`: Her kullanıcı sorgusunu, yönlendirme stratejisini, güven skorunu ve yanıt süresini kaydeden telemetri tablosudur (Python tarafında `query_metadata` alanı ile ek JSON bağlam tutulur).  
    *   `AgentTask`: A2A protokolünde ajanlar arasında dolaşan görevlerin yaşam döngüsünü (`submitted → processing → completed/failed`) kanıtlayan kayıt tablosudur.

### 📄 `src/db/schemas.py`
API'den gelen veya Controller'lara giden verilerin doğruluğunu, uzunluğunu, tipini kontrol eden koruma zırhı (Pydantic).
*   **Metod / Sınıflar:**
    *   `RAGQuery`: Bir arama yapmadan önce sorunun (minimum 1, max 500 karakter olmak zorunda) kurallarını belirler, top_k'nın 20'yi aşmasına izin vermez.
    *   `UserQueryRequest`: Yeni açılacak API tarafındaki Endpoint şemasıdır.
    *   A2A SDK importları bu alanda yapılmaz, projeye saf iç iş (business logic) verileri burada tutulur.

---

## 3. RAG (RETRIEVAL-AUGMENTED GENERATION) KATMANI
Kurumun yönetmelik/yönerge gibi sabit verilerinden öğrencinin sorularına kanıt getirilmesini sağlayan zeki arama arbedesidir.

### 📄 `src/rag/document_loader.py` (Doküman Yükleyici)
`pdfplumber` veya utf-8 fallback'leriyle `.pdf` / `.txt` belgelerini temizleyerek RAM'e alır. Karakter sayılarını metadata'ya ekler, anlamsız kısa belgeleri (50 karakterden az) otomatik eler.

### 📄 `src/rag/text_preprocessor.py` (Metin Temizleyici)
Belgenin içerisinden gereksiz kalıntıları arındırarak kaliteli bağlam (Context) yaratır:
*   **Header Frekans Analizi:** Belgenin içinde kendini sürekli tekrar eden "T.C. ONDOKUZ MAYIS ÜNİV" tarzı tepelikleri (Header/Footer), 3 kereden fazla geçiyorlarsa otomatik siler.
*   **Regex Kuralları:** Belge ID'lerini (PP.1.0 vb.), sayfa numaralarını ve kontrol uyarılarını filtreler.

### 📄 `src/rag/chunker.py` (Akıllı Metin Parçalayıcı)
*   **MADDE-Aware Algoritması:** Metinleri dümdüz 1000 karakterde kesmez. Regex (`_MADDE_RE`) ile **"MADDE 5 -"** yapılarını anlayıp metni "Maddeler" halinde bloklar.
*   **Bağlam Aşılama:** Eğer 5. Madde çok uzunsa ve 2'ye bölünmek zorundaysa, 2. parçanın en başına da *"MADDE 5"* bilgisini enjekte ederek arama bütünlüğünü korur.

### 📄 `src/rag/embedder.py` (Anlam Vektörü Üretici)
*   **Tembel Yükleme:** 700 MB'lik BAAI/bge-m3 yapay zekasını RAM'e sadece ihtiyaç anında yükler. 
*   **BGE-M3 (1024-D):** 8192 Token window büyüklüğünde, kelimenin anlam dünyasındaki uzay koordinatlarını çıkarır.
*   `embed_texts()`: 100'lük gruplar (Batch) halinde belgeleri matris çarpımına sokar.

### 📄 `src/rag/indexer.py` (ChromaDB Bağlantı REST API'si)
Chromadb istemcisi lokalde ağır ve C++ bağımlılıklarına yol açtığı için saf HTTP (`httpx`) bağlantısıyla Docker'a istek atar.
*   **Batch Write**: 100'lü sayfalama (Pagination) yapar, sunucunun şişmesini engeller. Pydantic-JSON dönüşümünde tip uyuşmazlığını yok eder.
*   **Idempotency:** SHA-256 algoritmasıyla belgenin "İçeriği" üzerinden bir hash ID yaratır. Kod 50 kere çalıştırılsa bile dosya içerikleri değişmedikçe veri tabanına 51. kez eklenmez.

### 📄 `src/rag/query_preprocessor.py` (Sorgu Genişleticisi)
LLM çalışmadan ÖNCE kural tabanlı yapay zeka taklidi yapar.
*   **Sinonim Genişletme:** Öğrenci "çap" yazarsa, sistem sözlüğe bakıp bu sorunun arama stringine hayalet kelime olarak `"çift ana dal"`, `"ikinci lisans"` da yazar ki Vector taramasından kaçmasın.
*   **Tip Skoru:** Sorunun içinde "nasıl", "ne zaman" kelimeleri varsa bunun `procedural` bir görev olduğuna karar verir.

### 📄 `src/rag/retriever.py` (Hibrit Arama & Reranker Beyni)
Sonuçların harmanlandığı orkestratör modülü:
*   **Algoritma (BM25 + Semantic):** "ÇAP" terimi için hem klasik Keyword uyumu (Exact match - BM25), hem de Vektör Cosine Similarity uyumunu yapar. Sonra RRF (Reciprocal Rank Fusion) puanlamasıyla ikisinin birleşim bir listesini oluşturur.
*   **Deduplication Fix:** İki motor aynı sonucu getirdiğinde düşük puanlı olanı silip en yüksekte çıkanı listeye katan koruyucu döngü barındırır.
*   **Source Relevance Penalty:** Yersiz bölümler denk gelirse (örneğin "Yaz okulu" sormuş ama cevap "Kayıt dondurma" yönetmeliğinden geliyorsa) algoritma bu duruma otomatik ceza/düşürme skoru (0.75 vs) verir.

### 📄 `src/rag/reranker.py` (Vektör Doğrulayıcı)
*   Toplanan ilk 20 sonuca "gerçekten sorulan soruya cevap olabiliyor mu?" diye çapraz değerlendirme (`seroe/bge-reranker-vround2-m3-turkish-triplet` Cross-Encoder) yaparak sadece en yetkin 5 sonucu RAG'a onaylar.

---

## SONUÇ VE İLERİYE YÖNELİK BEKLENTİLER
Şu anda kod tabanı; Veritabanı ve Veri İndeksleme konularında State of The Art (SOTA) mimari kullanmaktadır. Solid bağımlılıklara, Lazy Initialization bellek yönetimlerine, Singleton Config nesnelerine, Regex kural algoritmalarına ve DDD dizin anatomisine harfiyen uyulmuştur.

Bundan sonraki fazda (FAZ 2), **`src/llm/`** dizini altına Qwen2.5 bağlantıları kodlanacak ve **`src/agents/`** altında departmanlara yönelik zeka sınıfları tasarlanmaya başlanacaktır.
