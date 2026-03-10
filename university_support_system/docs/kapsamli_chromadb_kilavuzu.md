# Kapsamlı ChromaDB ve RAG Mimari Kılavuzu

Bu belge, üniversite destek sisteminin ardındaki "Akıllı Arama" (RAG - Retrieval-Augmented Generation) mekanizmasının tam olarak nasıl yapılandırıldığını detaylandırır. 

Sistem, geleneksel ağır kütüphaneler (`LangChain` vb.) kullanmak yerine tamamen modüler, hafif ve özelleştirilmiş bir yapıda tasarlanmıştır.

---

## 1. Mimari Karar: `httpx` Üzerinden REST API İletişimi

Projede ağır `chromadb` Python kütüphanesi yerine, doğrudan Docker上で (Docker üzerinde) koşan ChromaDB sunucusuna **HTTP REST API (`httpx`)** ile istek atılan hafif bir mimari tercih edilmiştir ([src/rag/indexer.py](file:///c:/Users/%C3%96MER%20FARUK%20DER%C4%B0N/Desktop/bitirme%20projesi/university_support_system/university_support_system/src/rag/indexer.py)).

**Neden Geleneksel/Standart Kurulum Değil?**
* **Performans & Boyut:** Eğitim dokümanlarındaki `pip install chromadb` komutu, projeye SQLite, FastAPI, ONNX runtime gibi yüzlerce MB'lık ağır bağımlılık yükler. REST API yaklaşımı ise sıfır bağımlılıkla (yalnızca `httpx`) çalışır.
* **Microservice (Mikroservis) Uyumluluğu:** ChromaDB bağımsız bir sunucu olarak çalıştığı için, yazılımın asıl gövdesi çok daha az bellek (RAM) harcar. Sunucular ayrıştırılmıştır (Decoupled Architecture).

---

## 2. Veritabanının Konumu: Docker Volumes

ChromaDB veritabanı dosyaları (koleksiyonlar, vektörler ve SQLite dosyaları) bilgisayardaki açık (C:\) dizinlerde **saklanmaz**. 

[docker-compose.yml](file:///c:/Users/%C3%96MER%20FARUK%20DER%C4%B0N/Desktop/bitirme%20projesi/university_support_system/university_support_system/docker-compose.yml) üzerinde yapılan ayarlama sayesinde, tüm veriler **Docker'ın korumalı birimi olan `uni_chroma_data`** (Volume) içerisinde saklanır.
* Proje dosyalarını silseniz bile (bu volume silinmediği sürece) vektörleriniz güvende kalır.
* Sıfırlamak isterseniz: `docker volume rm uni_chroma_data` komutu kullanılır.

---

## 3. Koleksiyon (Collection) Yönetimi

İlişkisel veritabanlarındaki (Örn: PostgreSQL) **"Tablo"** kavramının ChromaDB'deki karşılığı **"Koleksiyon (Collection)"**dur.

Sistem yeni bir PDF sisteme eklendiğinde veya bir arama yapıldığında şu döngüyü işletir:
1. [get_collection_id()](file:///c:/Users/%C3%96MER%20FARUK%20DER%C4%B0N/Desktop/bitirme%20projesi/university_support_system/university_support_system/src/rag/indexer.py#112-117) çağrılır.
2. ChromaDB'ye sorgunun veya indeksleme kaynağının bağlı olduğu departmana ait koleksiyonun olup olmadığı sorulur. Örnekler: *"student_affairs_docs"*, *"academic_programs_docs"*, *"finance_docs"*, *"it_support_docs"*.
3. Eğer koleksiyon henüz yoksa [create_collection()](file:///c:/Users/%C3%96MER%20FARUK%20DER%C4%B0N/Desktop/bitirme%20projesi/university_support_system/university_support_system/src/rag/indexer.py#55-95) devreye girer, POST isteğiyle yeni bir koleksiyon oluşturur ve ID'sini döner.
4. Bu aşamadan sonra tüm okuma/yazma işlemleri bu Koleksiyon ID'si üzerinden (*Multi-tenant yapı*) gerçekleşir.

---

## 4. Özel Parçalama (Chunking) Stratejisi: `MADDE-Aware`

Yapay zekanın devasa PDF'leri anlayabilmesi için bu dosyaların küçük anlamlı parçalara (Chunk) bölünmesi gerekir. Projedeki en profesyonel kısımlardan biri [src/rag/chunker.py](file:///c:/Users/%C3%96MER%20FARUK%20DER%C4%B0N/Desktop/bitirme%20projesi/university_support_system/university_support_system/src/rag/chunker.py) içerisindeki **MADDE Koruması (MADDE-Aware Text Splitter)** yapısıdır.

* **Sorun:** Geleneksel chunking sistemleri metni körleme bir şekilde 500 kelimede bir keser. Bir yönetmelik maddesinin yarısı başka parçada, yarısı başka parçada kalınca LLM bağlamı (context) kaybeder.
* **Çözüm (Projedeki Yapı):** Sistem `_MADDE_RE = re.compile(r"^(MADDE|Madde)\s+(\d+)\s*[-–—]"` Regex (Düzenli İfade) kurallarıyla metni önce **maddelere göre** böler. 
* Eğer madde çok uzunsa mecburen alt parçalara ayrılır (`sub_chunks`). Fakat zekice bir yöntemle; bu alt parçaların başına orijinal `[MADDE X]` başlığı tekrar eklenir. Böylece kopukluk yaşanmaz.

---

## 5. ChromaDB'de Veriler Nasıl Saklanıyor? (Şema)

[indexer.py](file:///c:/Users/%C3%96MER%20FARUK%20DER%C4%B0N/Desktop/bitirme%20projesi/university_support_system/university_support_system/src/rag/indexer.py) içerisindeki [upsert_documents](file:///c:/Users/%C3%96MER%20FARUK%20DER%C4%B0N/Desktop/bitirme%20projesi/university_support_system/university_support_system/src/rag/indexer.py#138-152) metodu ile veriler (100'erli paketler halinde - Batch Write) ChromaDB'ye basılır. Bir kayıt şu **4 temel sütundan** oluşur:

### A. [id](file:///c:/Users/%C3%96MER%20FARUK%20DER%C4%B0N/Desktop/bitirme%20projesi/university_support_system/university_support_system/src/rag/indexer.py#112-117) (Kimlik)
Her parçanın eşsiz kimliği (Örn: `yonetmelik_61`). Veri tekrarını (duplicate) önlemek için kullanılır (Idempotent yapı).

### B. `embedding` (Anlamsal Vektör)
BGE-M3 (BAAI/bge-m3) modeli kullanılarak, o cümleyi temsil eden **1024 boyutlu ondalık sayı listesi**. LLM'ler kelimeleri değil, bu sayı haritalarındaki yönleri okuyarak anlamı çözer.
* Örnek: `[0.012, -0.450, 0.880, 0.111, ...]`

### C. [document](file:///c:/Users/%C3%96MER%20FARUK%20DER%C4%B0N/Desktop/bitirme%20projesi/university_support_system/university_support_system/src/rag/indexer.py#120-137) (Orijinal Metin)
Öğrenciye gösterilecek ve yapay zekaya kaynak olarak verilecek asıl Türkçe metin (Metne ilişitirilen MADDE başlıkları dahil).

### D. [metadata](file:///c:/Users/%C3%96MER%20FARUK%20DER%C4%B0N/Desktop/bitirme%20projesi/university_support_system/university_support_system/src/rag/indexer.py#261-273) (Etiket Sözlüğü)
Sistemin en can alıcı noktasıdır. JSON formatında şu filtreleme bilgileri tutulur:
```json
{
    "source": "yonetmelik.pdf",                     // Orijinal dosyanın adı
    "department": "student_affairs",                 // Departman (dosya yolundan otomatik)
    "subcategory": "yonergeler_egitim",              // Alt klasör bilgisi
    "bolum": "elektrik_elektronik_muhendisligi",     // Akademik bölüm (dosya adından tespit)
    "bolum_adi": "Elektrik-Elektronik Mühendisliği", // Bölüm görüntüleme adı
    "chunk_index": 12,                               // Kaçıncı parça olduğu
    "chunk_count": 85,                               // Toplam parça sayısı
    "madde_no": "31",                                // (Varsa) Yönetmelik Madde No
    "bolum_yapisal": "ALTINCI BÖLÜM",               // (Varsa) Yönetmelik Bölüm Adı
    "sub_chunk": "2/3"                               // Uzun maddelerin alt bölüm durumu
}
```

---

## 6. Arama ve Yeniden Sıralama (Reranking) İşleyişi 

Kullanıcı, "ÇAP ortalaması kaç?" diye sorduğunda süreç şöyle işler:

1. **Embedding:** Soru BGE-M3 modeline girer, 1024 boyutlu "Soru Vektörü" elde edilir.
2. **Dense Retrieval (Ana Sorgu):** ChromaDB, soru vektörüne en yakın 20-30 adet adayı getirir ([query](file:///c:/Users/%C3%96MER%20FARUK%20DER%C4%B0N/Desktop/bitirme%20projesi/university_support_system/university_support_system/src/rag/indexer.py#201-234) fonksiyonu ile).
3. **Reranking (Pırlanta Filtresi):** Sisteminize eklenmiş olan `seroe/bge-reranker-v2-m3-turkish-triplet` (Özel Türkçe modeli) devreye girer. ChromaDB'den gelen 30 adayı alır, kullanıcının sorusuyla çapraz okuma yaparak, *gerçekten konuya yanıt veren* **en iyi 5 parçayı** filtreler ve sıralar (hibrit arama).
4. **LLM Nesli:** Son olarak, bu seçilmiş 5 kaynak metin (metadata'daki "Madde 31" gibi referanslarla birlikte) Ana Dil Modeline (Ollama vb.) gönderilir.
5. LLM şöyle bir cümle kurar: *"Yönetmeliğin 6. Bölüm, 31. maddesine göre ÇAP ortalaması en az..."*
