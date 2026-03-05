# FAZ 1 — RAG Pipeline Teknik Dokümantasyonu

**Proje:** Üniversite Kurumsal Destek Sistemi  
**Doküman Tarihi:** 28 Şubat 2026  
**Doküman Sürümü:** 3.1 (Cache, İdempotent İndeksleme, Değerlendirme Altyapısı)  
**Yazar:** Geliştirme Ekibi  
**Durum:** ✅ Tamamlandı  

---

## 1. Amaç ve Kapsam

Bu doküman, projenin **FAZ 1 (Belge Vektörleştirme ve Bilgi Alma Altyapısı)** kapsamında geliştirilen RAG (Retrieval-Augmented Generation) sisteminin teknik mimarisini, tasarım kararlarını, karşılaşılan sorunları ve uygulanan çözümleri kapsamlı olarak kayıt altına almaktadır.

**Bu dokümanın hedef kitlesi:** Projeye yeni katılan geliştiriciler, tez danışmanı ve jüri üyeleri. Okuyan kişi, RAG pipeline'ının neden ve nasıl bu şekilde tasarlandığını, her bir bileşenin teknik detaylarını ve iteratif iyileştirme sürecini anlayabilmelidir.

**FAZ 1 kapsamında tamamlanan iş kalemleri:**

1. Belge yükleme ve format dönüşümü (`DocumentLoader`)
2. Metin temizleme ve normalizasyon (`TextPreprocessor`)
3. MADDE-aware akıllı parçalama (`TextChunker` v2)
4. Çok dilli embedding üretimi (`Embedder` — BAAI/bge-m3)
5. ChromaDB REST API vektör indeksleme (`ChromaIndexer`)
6. Sorgu ön işleme ve sinonim genişletme (`QueryPreprocessor`)
7. Hibrit arama: BM25 + Semantic + RRF füzyonu (`HybridRetriever`)
8. Cross-encoder yeniden sıralama (`CrossEncoderReranker`)
9. Kaynak uyumluluğu (Source Relevance) mekanizması
10. Sorgu cache (TTL tabanlı in-memory cache)
11. İdempotent indeksleme (hash tabanlı ID + upsert)
12. Doküman kaydı (doc_registry.json) otomatik üretimi
13. RAG değerlendirme altyapısı (20 test sorusu + otomatik rapor)
14. Integration test altyapısı (ChromaDB canlı testler)
15. Komut satırı test ve analiz araçları

---

## 2. Mimari Genel Bakış

### 2.1 Modül Yapısı

RAG sistemi `src/rag/` dizini altında modüler bir yapıda tasarlanmıştır. Her modül tek sorumluluk prensibine (SRP) uyar ve birbirlerine gevşek bağlıdır:

```
src/rag/
├── __init__.py              # Tüm modüllerin export'ları
├── document_loader.py       # PDF/TXT okuma, encoding fallback
├── text_preprocessor.py     # Gürültü temizleme, header silme
├── chunker.py               # MADDE-aware parçalama (v2)
├── embedder.py              # BAAI/bge-m3 vektör üretimi
├── indexer.py               # ChromaDB REST API yazma/okuma
├── pipeline.py              # İndeksleme orkestratörü
├── query_preprocessor.py    # Sorgu normalizasyon ve sinonim genişletme
├── reranker.py              # Cross-encoder yeniden sıralama
└── retriever.py             # Hibrit arama (BM25 + Semantic + Reranking)
```

### 2.2 Veri Akışı — İndeksleme Hattı

```
┌────────────────────────────────────────────────────────────────────┐
│                     İNDEKSLEME PIPELINE'I                         │
│                                                                    │
│  Dosyalar (PDF/TXT)                                                │
│      │                                                             │
│      ▼                                                             │
│  DocumentLoader — Okuma + Encoding fallback (UTF-8 → cp1254)      │
│      │                                                             │
│      ▼                                                             │
│  TextPreprocessor — Header/footer silme, boşluk normalizasyonu     │
│      │                                                             │
│      ▼                                                             │
│  TextChunker (v2) — MADDE sınırı koruma + header ekleme            │
│      │                   + metadata zenginleştirme (madde_no, bolum)│
│      ▼                                                             │
│  Embedder (BAAI/bge-m3) — 1024-D vektör üretimi                   │
│      │                                                             │
│      ▼                                                             │
│  ChromaIndexer — REST API ile ChromaDB'ye batch yazım              │
└────────────────────────────────────────────────────────────────────┘
```

### 2.3 Veri Akışı — Arama Hattı

```
┌────────────────────────────────────────────────────────────────────┐
│                       ARAMA PIPELINE'I                             │
│                                                                    │
│  Kullanıcı Sorusu                                                  │
│      │                                                             │
│      ▼                                                             │
│  QueryPreprocessor — Bileşik kelime ayırma + sinonim genişletme    │
│      │                                                             │
│      ▼                                                             │
│  EnsembleRetriever — BM25 (keyword) ──┐                            │
│      │                                ├── RRF Fusion → Adaylar     │
│      │               ChromaDB (semantic) ┘                         │
│      ▼                                                             │
│  Deduplication — İçerik bazlı tekrar eleme (max skor korunur)      │
│      │                                                             │
│      ▼                                                             │
│  CrossEncoderReranker — seroe/bge-reranker-v2-m3-turkish-triplet   │
│      │                                                             │
│      ▼                                                             │
│  Source Relevance — Konu-kaynak uyumsuzluğuna soft penalty          │
│      │                                                             │
│      ▼                                                             │
│  min_score filtresi → Top-K Sonuç                                  │
└────────────────────────────────────────────────────────────────────┘
```

---

## 3. Model ve Teknoloji Seçimleri

### 3.1 Evrim Tablosu

FAZ 1 sürecinde, iteratif testler ve araştırma sonuçlarına dayanarak model ve yaklaşım değişiklikleri yapılmıştır:

| Bileşen | v1 (İlk Tasarım) | v2 (Mevcut) | Geçiş Gerekçesi |
|---------|------------------|-------------|-----------------|
| **Embedding Modeli** | `dbmdz/bert-base-turkish-cased` (768-D) | `BAAI/bge-m3` (1024-D) | BERTurk yalnızca Türkçe; bge-m3 100+ dilde SOTA, MIRACL benchmark'ta üstün performans, 8192 token penceresi |
| **Ara Model** | `intfloat/multilingual-e5-base` (768-D) | `BAAI/bge-m3` (1024-D) | E5-base 514 token sınırı, prefix zorunluluğu; bge-m3 prefix gerektirmez, daha geniş token penceresi |
| **Chunking** | `RecursiveCharacterTextSplitter` (512 char) | MADDE-aware chunker (1024 char) | Yasal belgelerdeki MADDE başlıkları kesiliyordu, bağlam kaybı yaşanıyordu |
| **Reranking** | Özel heuristik formül | Cross-encoder (`seroe/bge-reranker-v2-m3-turkish-triplet`) | Heuristik formül keyword density'ye aşırı ağırlık veriyordu, context mixing sorunu vardı |
| **BM25 Preprocessing** | Normalize edilmiş `page_content` | Orijinal metin + custom tokenizer | BM25 ve ChromaDB'den gelen `page_content` farklı olduğu için deduplication hatası vardı |

### 3.2 Güncel Model Kartları

#### Embedding: BAAI/bge-m3
| Özellik | Değer |
|---------|-------|
| HuggingFace Adı | `BAAI/bge-m3` |
| Vektör Boyutu | 1024 |
| Maksimum Token | 8192 |
| Dil Desteği | 100+ dil (Türkçe dahil) |
| Prefix Gereksinimi | Yok (E5 ailesi prefix gerektirir, bge-m3 gerektirmez) |
| Benchmark | MIRACL retrieval benchmark'ta SOTA |

#### Reranker: seroe/bge-reranker-v2-m3-turkish-triplet
| Özellik | Değer |
|---------|-------|
| HuggingFace Adı | `seroe/bge-reranker-v2-m3-turkish-triplet` |
| Temel Model | BAAI/bge-reranker-v2-m3 |
| Fine-tune | Türkçe triplet verisi ile |
| MAP (val / test) | 0.79 / 0.789 |
| Maksimum Token | 512 (sorgu + belge birlikte) |
| Batch Size | 16 |

---

## 4. Modül Detayları

### 4.1 Document Loader (`document_loader.py`)

Kaynak dosyaları (PDF, TXT) diskten okuyarak `Document` veri nesnelerine dönüştürür.

**Tasarım Kararları:**
- **pdfplumber seçimi:** `PyPDF2` gibi kütüphaneler tablo sütunlarında ve kenar boşluklarında kelimeleri birbirine yapıştırır. `pdfplumber`, bounding box bilgilerini okuyarak resmi evraklardaki kelime aralıklarını doğru korur.
- **Encoding Fallback:** Öğrenci İşleri'nden temin edilen `.txt` dosyaları eski Windows sistemlerinde `cp1254` (ANSI) formatında oluşturulmuş olabilir. Sistem `UTF-8` denemesinde `UnicodeDecodeError` yakaladığında otomatik olarak `cp1254` ile yeniden dener.
- **Minimum İçerik Filtresi:** `min_content_length=50` ile yalnızca bir başlık içeren veya OCR yapılamamış boş sayfalar elenir.
- **Metadata Toplama:** Her belge için `source` (dosya adı), `category` (üst klasör adı — yönetmelikler, yönergeler, birimler vb.) ve dosya türü saklanır.

### 4.2 Text Preprocessor (`text_preprocessor.py`)

Ham metinlerdeki gürültüyü temizleyerek embedding kalitesini artırır.

**Uygulanan Temizlik Katmanları:**

| Katman | Teknik | Amaç |
|--------|--------|------|
| Boşluk normalizasyonu | `\s+` → tek boşluk | PDF'ten gelen `\t`, `\r\n` farklılıklarını standartlaştırma |
| Sayfa marker temizliği | RegEx (`Sayfa \d+`, `\d+/\d+`) | Bağlamı koparan sayfa numarası ibarelerini silme |
| Mükerrer header algılama | Frekans analizi (eşik: 3+) | Tüm sayfalarda tekrarlanan üstbilgilerin vektör uzayını kirletmesini önleme |

**Mükerrer Header Sorunu Detayı:** "T.C. ONDOKUZ MAYIS ÜNİVERSİTESİ SENATO KARARI" gibi ifadeler her sayfada tekrarlandığında, embedding modeli birbiriyle alakasız belgeleri "ikisi de aynı ifadeyle başlıyor" diye yüksek benzerlik skoruyla eşleştirir (False Positive). Frekans tabanlı algılama bu sorunu çözer.

### 4.3 Text Chunker — MADDE-Aware v2 (`chunker.py`)

Üniversite yönetmelik ve yönergeleri `MADDE` yapısına sahip yasal belgelerdir. v1'deki `RecursiveCharacterTextSplitter`, MADDE başlıklarını ortadan kesiyordu ve bağlam kaybına neden oluyordu.

**v2 Chunking Algoritması:**

```
Girdi: Ham metin
    │
    ▼
1. MADDE sınırlarını tespit et (_MADDE_RE regex)
    │
    ▼
2. BÖLÜM bilgisini tespit et (_BOLUM_RE regex)
    │
    ▼
3. Her MADDE için:
    ├── Uzunluk ≤ chunk_size → Tek chunk olarak kaydet
    └── Uzunluk > chunk_size → Alt parçalara böl:
         ├── İlk parça: Orijinal metin
         └── Sonraki parçalar: "[MADDE X başlığı] " + devam metni
    │
    ▼
4. Metadata zenginleştirme:
    ├── madde_no: "5", "11", vb.
    ├── bolum: "BİRİNCİ BÖLÜM", "ÜÇÜNCÜ BÖLÜM", vb.
    └── sub_chunk: "2/3" (eğer madde bölündüyse)
```

**Kritik İyileştirme — Header Ekleme:** Uzun bir MADDE birden fazla chunk'a bölündüğünde, her alt chunk'ın başına orijinal MADDE başlığı eklenir. Örneğin:

```
Chunk 1: "MADDE 5 - (1) ÇAP'a başvuru, kabul ve kayıt koşulları şunlardır: ..."
Chunk 2: "[MADDE 5 - (1) ÇAP'a başvuru, kabul ve kayıt koşulları şunlardır:] ..."
```

Bu sayede LLM veya kullanıcı, chunk'ın hangi maddeye ait olduğunu chunk'ı tek başına okuyarak bile anlayabilir.

**Konfigürasyon:**

| Parametre | Varsayılan | Açıklama |
|-----------|-----------|----------|
| `chunk_size` | 1024 | Maksimum chunk boyutu (karakter) |
| `chunk_overlap` | 128 | Parçalar arası örtüşme |

### 4.4 Embedder (`embedder.py`)

Metin parçalarını 1024-boyutlu vektörlere dönüştürür.

**Model Adaptörü Mimarisi:**

```python
# Model tipi otomatik algılanır
model_lower = self.model_name.lower()
self._is_e5_model = "e5" in model_lower    # E5 → prefix gerektirir
self._is_bge_model = "bge" in model_lower  # BGE-M3 → prefix gerektirmez
```

| Model Ailesi | Prefix Davranışı |
|-------------|-----------------|
| `intfloat/multilingual-e5-*` | Sorgu: `"query: "` + metin, Belge: `"passage: "` + metin |
| `BAAI/bge-m3` | Prefix yok — metin doğrudan encode edilir |

**Bellek Yönetimi:**
- **Lazy Loading:** Model ilk `embed_texts()` çağrısında yüklenir (700MB+ ağırlıklar)
- **Batch Processing:** OOM (Out of Memory) hatalarını önlemek için `batch_size=32` ile toplu işleme
- **L2 Normalizasyon:** `normalize_embeddings=True` — Dot product ile cosine similarity eşdeğeri sağlanır, arama performansı artar

### 4.5 ChromaDB Indexer (`indexer.py`)

ChromaDB REST API üzerinden vektör veritabanı işlemlerini yönetir.

**Neden REST API?** ChromaDB'nin Python paket kurulumu Windows'ta C++ Build Tools ve özel bağımlılıklar gerektirdiğinden, HTTP tabanlı iletişim tercih edilmiştir. Docker'daki standart ChromaDB imajına `httpx` kütüphanesiyle bağlanılır.

**Teknik Detaylar:**

| Özellik | Değer |
|---------|-------|
| İletişim Protokolü | HTTP/REST (httpx async client) |
| ChromaDB Sürümü | 0.6.3 (Docker) |
| API Yolu | `/api/v1/collections` |
| Batch Size | 100 (HTTP timeout önlemi) |
| Metadata Temizleme | `_clean_metadata()` — yalnızca primitive tipler (str, int, float, bool) |

**Metadata Kısıtlaması:** ChromaDB metadata alanlarında `List`, `Dict`, `None` veya özel objeler kabul etmez. `_clean_metadata()` filtresi tüm değerleri iteratif kontrol ederek uyumsuz tipleri string'e çevirir.

### 4.6 Query Preprocessor (`query_preprocessor.py`)

Kullanıcı sorgularını arama motorları için optimize eder. LLM olmadan, kural tabanlı çalışır.

**İşleme Katmanları:**

```
Kullanıcı Sorusu
    │
    ▼
1. Bileşik Kelime Ayırma
   "anadal" → "ana dal"
   "yandal" → "yan dal"
    │
    ▼
2. Kısaltma ve Sinonim Genişletme
   "ÇAP" → + "çift ana dal" + "ikinci lisans"
   "YDP" → + "yan dal programı"
    │
    ▼
3. Sorgu Tipi Tespiti
   "nasıl yapılır" → procedural
   "kaçtır" / "nedir" → factual
   diğer → general
    │
    ▼
Genişletilmiş Sorgu
```

**Sinonim Sözlüğü Örnekleri:**

| Kullanıcı Yazımı | Genişletme |
|------------------|------------|
| `çap` | çift ana dal, ikinci lisans, ÇAP |
| `yandal` | yan dal, YDP, yan dal sertifika |
| `kayıt dondurma` | kayıt dondurulması, kayıt dondurmak, dönem izni |
| `yaz okulu` | yaz dönemi, yaz okulu eğitimi |
| `not ortalaması` | GNO, genel not ortalaması |

### 4.7 Hybrid Retriever (`retriever.py`) — v3.0

İki farklı arama motorunu birleştiren ve cross-encoder ile yeniden sıralayan ana arama sınıfıdır.

**Tam Arama Akışı:**

```
HybridRetriever.search(query)
    │
    ├─ 1. QueryPreprocessor.preprocess(query)
    │     → Bileşik kelime ayırma + sinonim genişletme
    │
    ├─ 2. EnsembleRetriever.invoke(expanded_query)
    │     ├─ BM25Retriever (keyword eşleşme, Türkçe tokenizer)
    │     └─ ChromaRestRetriever (semantic vektör arama)
    │     → RRF (Reciprocal Rank Fusion) ile birleşim
    │
    ├─ 3. Deduplication
    │     → Aynı içerik BM25 ve ChromaDB'den geldiyse max skor korunur
    │
    ├─ 4. CrossEncoderReranker.rerank(original_query, candidates)
    │     → seroe/bge-reranker-v2-m3-turkish-triplet ile yeniden sıralama
    │
    ├─ 5. Source Relevance (_apply_source_relevance)
    │     → Konu-kaynak uyumsuzluğuna 0.75 penalty
    │
    └─ 6. min_score filtresi → Top-K sonuç döndürme
```

**Oversampling Stratejisi:** `OVERSAMPLE_FACTOR = 4` — Kullanıcı `top_k=5` istediğinde dahili olarak `5 × 4 = 20` aday çekilir, ardından reranking ile en iyi 5 seçilir. Bu, ilk retrieval'da kaçırılan iyi sonuçların kurtarılma şansını artırır.

#### 4.7.1 BM25 Türkçe Tokenizer

BM25 motorunun Türkçe'ye uyarlanması için özel bir tokenizer geliştirilmiştir:

```python
def turkish_bm25_preprocess(text: str) -> List[str]:
    # 1. Küçük harfe çevir
    # 2. Bileşik kelime ayır (anadal → ana dal)
    # 3. Noktalama temizle
    # 4. Tek karakterli token'ları at
    return tokens
```

**Bileşik Kelime Haritası:**

| Bileşik Form | Ayrılmış Form |
|--------------|---------------|
| `anadal` | `ana dal` |
| `yandal` | `yan dal` |
| `çiftanadal` | `çift ana dal` |
| `lisansüstü` | `lisans üstü` |

**Neden `page_content` Orijinal Metin?** v2 öncesinde BM25, normalize edilmiş metin ile çalışıyor ve ChromaDB orijinal metni kullanıyordu. Bu tutarsızlık, aynı belgenin iki farklı versiyonunun deduplication'dan kaçmasına ve semantic skorun sıfırlanmasına neden oluyordu. v3'te BM25'in `page_content`'i orijinal metin, tokenizasyon ise `preprocess_func` içinde yapılmaktadır.

#### 4.7.2 Deduplication — Semantic Skor Korunması

BM25 ve ChromaDB aynı belgeyi döndürebilir. v3'teki deduplication mantığı:

```python
seen_contents: Dict[str, int] = {}  # content_key → candidates listesindeki index

for doc in raw_docs:
    content_key = doc.page_content[:200]
    sim_score = doc.metadata.get("similarity_score", 0.0)

    if content_key in seen_contents:
        idx = seen_contents[content_key]
        if sim_score > candidates[idx]["score"]:
            candidates[idx]["score"] = sim_score  # Max skor korunur
        continue

    seen_contents[content_key] = len(candidates)
    candidates.append(...)
```

**v2 Sorunu:** BM25 belgelerine `similarity_score=0.0` atanıyordu. Eğer BM25 versiyonu önce işlenirse, ChromaDB'nin gerçek semantic skoru kayboluyordu. v3'te `max()` mantığı ile en yüksek skor her zaman korunur.

### 4.8 Cross-Encoder Reranker (`reranker.py`)

Bi-encoder (embedding) modeller sorgu ve belgeyi bağımsız vektörize eder. Cross-encoder ise sorgu-belge çiftini **birlikte** değerlendirir — bu nedenle çok daha doğru relevanslik puanı üretir.

**Çalışma Prensibi:**

```
Girdi: [(sorgu, belge_1), (sorgu, belge_2), ..., (sorgu, belge_n)]
    │
    ▼
CrossEncoder.predict(pairs) → [skor_1, skor_2, ..., skor_n]
    │
    ▼
Skorlara göre azalan sırada sıralama → Top-K döndürme
```

**Neden Özel Heuristik Yerine Cross-Encoder?**

v2'de kullanılan özel `_rerank` metodu şu ağırlıkları kullanıyordu:
- Bigram/trigram keyword sayısı × 0.5
- Pseudo-stem eşleşme oranı × 0.25
- Dosya adı eşleşmesi × 1.0
- Semantic skor × 0.25

Bu formül keyword density'ye aşırı ağırlık veriyordu. Örneğin "diploma not ortalaması" sorulduğunda, "not ortalaması" kelimesi çok geçen ama alakasız ÇAP yönergesi 1. sıraya çıkıyordu. Cross-encoder, sorgu-belge çiftini anlamsal olarak değerlendirdiği için bu tür false positive'leri büyük ölçüde ortadan kaldırmıştır.

**Lazy Initialization:** Model ilk `rerank()` çağrısında yüklenir (~2-5 saniye). Sonraki çağrılar cachelenir.

### 4.9 Source Relevance — Context Mixing Çözümü

**Problem:** "ÇAP başvurusu için gereken not ortalaması kaçtır" sorulduğunda, cross-encoder "not ortalaması" kavramını yatay geçiş yönergesinde de yüksek skorla eşleştiriyordu — çünkü her iki belgede de "genel not ortalamasının X olması gerekir" ifadesi mevcuttur.

**Çözüm — Konu-Kaynak Uyumluluğu:** Reranking sonrası, sorgu konusu ile sonuç kaynağı arasında uyumsuzluk tespit edilirse hafif bir penalty uygulanır.

**Algoritma:**

```
1. Sorgudaki anahtar kelimeleri tespit et
   "ÇAP başvurusu..." → konu: "çap"

2. Her sonucun kaynak dosyasını kontrol et
   "yonerge_cift_anadal_yandal.pdf" → eşleşme var → dokunma
   "yonerge_onlisans_lisans_yatay_gecis.pdf" → eşleşme yok → penalty

3. Off-topic sonuçların skorunu düşür
   skor = skor × 0.75

4. Yeniden sırala
```

**Konu-Kaynak Eşleştirme Haritası:**

| Sorgu Konusu | Beklenen Kaynak Kalıpları |
|-------------|--------------------------|
| `çap`, `çift anadal`, `ikinci lisans` | `cift_anadal`, `çift ana dal`, `çap` |
| `yan dal`, `yandal`, `ydp` | `cift_anadal`, `yan dal`, `yandal` |
| `yatay geçiş` | `yatay_gecis`, `yatay geçiş` |
| `staj` | `staj`, `intörn` |
| `yaz okulu` | `yaz_okulu`, `yaz okulu` |
| `erasmus` | `erasmus`, `değişim`, `uluslararası` |
| `disiplin` | `disiplin` |
| `muafiyet` | `muafiyet` |

**Güvenlik Garantileri:**
- Konu tespiti yapılamayan sorgularda (örn: "devamsızlık sınırı nedir") **hiçbir etki olmaz**
- On-topic sonuçlara **asla dokunulmaz**
- Penalty sadece belirgin uyumsuzluklarda uygulanır (soft, hard filter değil)
- Penalty faktörü yapılandırılabilir (`OFF_TOPIC_PENALTY = 0.75`)

**Ölçülen Etki:**

| Sorgu | Off-topic Sonuç | Önceki Sıra | Sonraki Sıra |
|-------|----------------|-------------|-------------|
| ÇAP not ortalaması | Yatay geçiş yönergesi | #2 (0.863) | #4 (0.647) |
| Yan dal not ortalaması | Yatay geçiş yönergesi | #2 (0.628) | #2 (0.471) |
| Kayıt dondurma süresi | — | — | **Değişiklik yok** |

### 4.10 Sorgu Cache (`_QueryCache`)

Aynı sorgunun kısa süre içinde tekrarlanması durumunda tüm pipeline'ı (BM25 + ChromaDB + Cross-Encoder) tekrar çalıştırmak gereksiz maliyet yaratır.

**Çözüm — TTL Tabanlı In-Memory Cache:**

```
1. Sorgu geldiğinde cache_key = f"{query}::{top_k}" oluştur
2. Cache'te var mı kontrol et:
   a. Varsa ve TTL dolmamışsa → direkt döndür (cache hit)
   b. Yoksa veya TTL dolmuşsa → normal arama yap, sonucu cache'e yaz
3. Varsayılan TTL: 300 saniye (5 dakika)
```

**Tasarım Kararları:**

| Karar | Alternatif | Neden Bu Seçildi |
|-------|-----------|------------------|
| In-memory dict | Redis cache | Redis bağımlılığı eklememek, sadelik |
| TTL ile otomatik expire | Manuel invalidation | Bakım gerektirmez |
| `cache_ttl=0` ile devre dışı | Global flag | Daha esnek, test dostu |

**Performans Etkisi:**
- Cache miss: ~200-500ms (model yüklü ise)
- Cache hit: <1ms
- `search()` her çağrıda `elapsed_ms` loglar (performans izleme)

**Kullanım:**

```python
retriever = HybridRetriever(cache_ttl=300)   # 5 dakika cache (varsayılan)
retriever = HybridRetriever(cache_ttl=0)     # Cache devre dışı
retriever._cache.invalidate()                # Cache'i temizle
```

### 4.11 İdempotent İndeksleme (Hash Tabanlı ID)

**Problem:** `--reindex` flag'i olmadan pipeline tekrar çalıştırıldığında, aynı chunk'lar farklı sıralı ID'lerle (`chunk_000001`, `chunk_000002`) tekrar ekleniyordu — bu duplike oluşturuyordu.

**Çözüm — İçerik Hash Tabanlı ID + Upsert:**

```
1. Her chunk için ID = "chunk_" + SHA-256(kaynak_dosya + "::" + chunk_içeriği)[:16]
2. Aynı kaynak + aynı içerik → her zaman aynı ID
3. --reindex ile: koleksiyon silinir, add() ile eklenir
4. --reindex olmadan: upsert() ile eklenir — aynı ID varsa günceller
```

**ChromaIndexer'a Eklenen `upsert_documents()` Metodu:**

```python
indexer.upsert_documents(
    ids=["chunk_a1b2c3d4e5f67890", ...],
    documents=[...],
    embeddings=[...],
    metadatas=[...],
)
```

Dahili olarak ChromaDB REST API'nin `/api/v1/collections/{id}/upsert` endpoint'ini kullanır.

**Garantiler:**
- Aynı belge 10 kez indekslense bile tek kopya kalır
- Belge içeriği değişirse hash değişir → yeni chunk olarak eklenir
- Farklı kaynaktan gelen aynı metin farklı ID alır (kaynak dosya hash'e dahil)

### 4.12 Doküman Kaydı (`doc_registry.json`)

Her indeksleme sonrası `data/metadata/doc_registry.json` dosyası otomatik olarak üretilir. Bu dosya, indekslenen belgelerin tam envanterini JSON formatında tutar.

**Kayıt Yapısı:**

```json
{
  "generated_at": "2026-02-28T18:30:00+00:00",
  "source_dir": "bitirme veriler - öğrenci işleri",
  "total_documents": 198,
  "total_chunks": 5303,
  "embedding_model": "BAAI/bge-m3",
  "collection_name": "student_affairs_docs",
  "documents": [
    {
      "filename": "yonerge_cift_anadal_yandal.txt",
      "category": "yönetmelikler",
      "file_type": ".txt",
      "char_count": 24530,
      "chunk_count": 42,
      "content_hash": "a1b2c3d4e5f67890"
    }
  ]
}
```

**Kullanım Alanları:**
- İndeksleme sonrası denetim ve doğrulama
- Hangi belgelerin sisteme dahil olduğunun takibi
- Belge versiyon kontrolü (content_hash ile değişiklik tespiti)

---

## 5. Konfigürasyon Sistemi

### 5.1 RAG Ayarları

| Ortam Değişkeni | Varsayılan | Açıklama |
|----------------|-----------|----------|
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | Embedding modeli |
| `EMBEDDING_DIMENSION` | `1024` | Vektör boyutu |
| `RAG_CHUNK_SIZE` | `1024` | Maksimum chunk boyutu (karakter) |
| `RAG_CHUNK_OVERLAP` | `128` | Parçalar arası örtüşme |
| `RAG_TOP_K` | `5` | Döndürülecek sonuç sayısı |
| `RAG_MIN_SIMILARITY` | `0.0` | Minimum skor eşiği (cross-encoder skorları negatif olabilir) |
| `RERANKER_MODEL` | `seroe/bge-reranker-v2-m3-turkish-triplet` | Cross-encoder modeli |
| `RERANKER_MAX_LENGTH` | `512` | Reranker max token (sorgu + belge) |
| `RERANKER_BATCH_SIZE` | `16` | Reranker batch boyutu |

### 5.2 Config Sınıfları

```python
class EmbeddingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMBEDDING_", extra="ignore")
    model: str = "BAAI/bge-m3"
    dimension: int = 1024

class RAGSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAG_", extra="ignore")
    chunk_size: int = 1024
    chunk_overlap: int = 128
    top_k: int = 5
    min_similarity: float = 0.0

class RerankerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RERANKER_", extra="ignore")
    model: str = "seroe/bge-reranker-v2-m3-turkish-triplet"
    max_length: int = 512
    batch_size: int = 16
```

---

## 6. İndeksleme Raporu

Son indeksleme sonuçları (28 Şubat 2026):

| Metrik | Değer |
|--------|-------|
| Kaynak dosya sayısı | 198 |
| Toplam chunk sayısı | 5303 |
| Ortalama chunk boyutu | ~580 karakter |
| Minimum chunk boyutu | 7 karakter |
| Maksimum chunk boyutu | ~1100 karakter |
| Embedding modeli | BAAI/bge-m3 |
| Vektör boyutu | 1024 |
| ChromaDB koleksiyon | `student_affairs_docs` |

---

## 7. Unit Test Altyapısı ve Test Kataloğu

### 7.1 Test Altyapısı

| Özellik | Değer |
|---------|-------|
| Test Framework | pytest 8.3.4 |
| Async Desteği | pytest-asyncio 0.25.2 (`asyncio_mode=auto`) |
| Mock Kütüphanesi | `unittest.mock` (MagicMock, patch) |
| Coverage | pytest-cov 6.0.0 |
| Test Veritabanı | SQLite in-memory (her test izole) |

**Son Çalıştırma:** 28 Şubat 2026 — **149/149 unit test geçti** ✅ (48.19 saniye)

```
==================== 149 passed in 48.19s ====================
```

### 7.2 Test Dosyaları Özeti

#### Unit Testler (`tests/unit/`)

| Test Dosyası | Test Sayısı | Test Edilen Modül | Açıklama |
|-------------|:-----------:|-------------------|----------|
| `test_config.py` | 10 | `src/core/constants.py` | Enum sabitleri, eşik değerleri |
| `test_connection.py` | 8 | `src/db/connection.py` | Lazy init, session yönetimi, dispose |
| `test_models.py` | 7 | `src/db/models.py` | ORM modelleri, ilişkiler, JSONB |
| `test_schemas.py` | 16 | `src/db/schemas.py` | Pydantic validasyonları |
| `test_rag_pipeline.py` | 29 | `src/rag/document_loader.py`, `text_preprocessor.py`, `chunker.py`, `pipeline.py` | Dosya yükleme, temizleme, chunk'lama, hash ID üretimi |
| `test_query_preprocessor.py` | 22 | `src/rag/query_preprocessor.py` | Bileşik kelime ayırma, sinonim genişletme, sorgu tipi |
| `test_embedder.py` | 14 | `src/rag/embedder.py` | Model algılama, prefix ekleme, vektör üretimi |
| `test_reranker.py` | 11 | `src/rag/reranker.py` | Cross-encoder sıralama, skor atama |
| `test_retriever.py` | 25 | `src/rag/retriever.py` | BM25 tokenizer, konu tespiti, source relevance, dedup, cache |
| **Toplam** | **142** | | **9 test dosyası, 10+ modül kapsanır** |

#### Integration Testler (`tests/integration/`)

| Test Dosyası | Test Sınıfı | Test Sayısı | Ön Koşul | Açıklama |
|-------------|-------------|:-----------:|----------|----------|
| `test_rag_retrieval.py` | `TestChromaDBConnectivity` | 2 | ChromaDB çalışıyor | Heartbeat ve collections endpoint |
| | `TestCollectionState` | 3 | Koleksiyon mevcut | Veri sayısı, metadata kontrolü |
| | `TestSemanticSearch` | 2 | Koleksiyon mevcut | ChromaDB direkt sorgu, mesafe doğrulama |
| | `TestHybridSearch` | 7 | Koleksiyon mevcut | Tam pipeline, kaynak doğruluğu, sıralama, performans |
| | `TestQueryCache` | 2 | Koleksiyon mevcut | Cache hit hızı, tutarlılık |
| | `TestTestQuestions` | 1 | Koleksiyon mevcut | 20 soruluk Precision@3 ≥ %70 hedefi |
| **Toplam** | | **17** | | **ChromaDB yoksa otomatik atlanır** |

> **Not:** Unit testler Docker servisi **olmadan** çalışır (tüm ağır bağımlılıklar mock'ludur). Integration testler ise ChromaDB'nin çalışıyor ve indekslenmiş olmasını gerektirir; erişilemezse `pytest.mark.skipif` ile atlanır.

---

### 7.3 Detaylı Test Kataloğu

#### 7.3.1 `test_query_preprocessor.py` — Sorgu Ön İşleme Testleri (22 test)

Kullanıcı sorgularının normalize edilmesi ve zenginleştirilmesi sürecini test eder. LLM olmadan çalışan kural tabanlı mantığın doğruluğunu garanti altına alır.

**TestCompoundWordSplitting** — Bileşik Kelime Ayırma (5 test)

| Test | Açıklama | Girdi | Beklenen Davranış |
|------|----------|-------|-------------------|
| `test_anadal_splits` | "anadal" bileşik kelimesi "ana dal" olarak ayrılır | `"anadal programı"` | Çıktıda `"ana dal"` bulunmalı |
| `test_yandal_splits` | "yandal" bileşik kelimesi "yan dal" olarak ayrılır | `"yandal başvurusu"` | Çıktıda `"yan dal"` bulunmalı |
| `test_ciftanadal_splits` | "çiftanadal" 3 kelimeye ayrılır — uzun eşleşme öncelikli | `"çiftanadal nedir"` | Çıktıda `"çift ana dal"` bulunmalı |
| `test_case_insensitive_split` | Büyük/küçük harf fark etmez | `"ANADAL programı"` | Çıktıda `"ana dal"` bulunmalı |
| `test_no_split_when_already_separated` | Zaten ayrık yazılmışsa dokunulmaz | `"ana dal programı"` | Çıktı değişmemeli |

> **Tespit Edilen Bug ve Düzeltme:** `test_ciftanadal_splits` ilk çalıştırmada fail verdi. `COMPOUND_WORD_SPLITS` sözlüğünde "anadal" anahtarı "çiftanadal"dan önce eşleşiyor, `"çiftanadal"` → `"çiftana dal"` yapıyordu. **Çözüm:** `_split_compound_words` metodunda sözlük anahtarları uzunluğa göre azalan sırada sıralanarak uzun eşleşmelerin öncelik alması sağlandı.

**TestSynonymExpansion** — Sinonim Genişletme (8 test)

| Test | Açıklama | Girdi | Beklenen Davranış |
|------|----------|-------|-------------------|
| `test_cap_expands` | "çap" kısaltması genişletilir | `"çap başvurusu"` | `"çift ana dal"` veya `"ikinci lisans"` eklenmeli |
| `test_ydp_expands` | "ydp" kısaltması genişletilir | `"ydp nedir"` | `"yan dal"` eklenmeli |
| `test_gno_expands` | "gno" kısaltması genişletilir | `"gno hesaplama"` | `"not ortalaması"` veya `"genel not ortalaması"` eklenmeli |
| `test_kayit_dondurma_expands` | Çok kelimeli terim genişletilir | `"kayıt dondurma nasıl yapılır"` | `"dönem izni"` veya `"kayıt dondurmak"` eklenmeli |
| `test_expansion_disabled` | `enable_expansion=False` ile genişletme kapatılır | `"çap başvurusu"` | `"ikinci lisans"` eklenmemeli |
| `test_custom_synonym_map` | Özel sözlük kullanılabilir | `"test sorusu"` (custom: test→deneme) | `"deneme"` veya `"sınama"` eklenmeli |
| `test_no_duplicate_terms` | Orijinal sorguda zaten geçen terimler tekrarlanmaz | `"çift ana dal başvurusu"` | `"ÇAP"` eklenmeli ama `"çift"` tekrarlanmamalı |
| `test_longer_match_takes_priority` | Uzun sinonim anahtarı önce eşleşir | `"çift ana dal programı nedir"` | `"ÇAP"` veya `"ikinci lisans"` eklenmeli |

**TestQueryTypeDetection** — Sorgu Tipi Tespiti (6 test)

| Test | Açıklama | Girdi | Beklenen Çıktı |
|------|----------|-------|----------------|
| `test_procedural_nasil` | "nasıl" anahtar kelimesi prosedürel sorgu | `"kayıt nasıl yapılır"` | `"procedural"` |
| `test_procedural_basvuru` | "başvuru" anahtar kelimesi prosedürel sorgu | `"burs başvuru süreci"` | `"procedural"` |
| `test_procedural_ne_zaman` | "ne zaman" anahtar kelimesi prosedürel sorgu | `"ders kaydı ne zaman"` | `"procedural"` |
| `test_factual_nedir` | "nedir" anahtar kelimesi bilgi sorusu | `"AKTS nedir"` | `"factual"` |
| `test_factual_kactir` | "kaçtır" anahtar kelimesi bilgi sorusu | `"mezuniyet kredisi kaçtır"` | `"factual"` |
| `test_general_query` | Anahtar kelime yoksa genel sorgu | `"üniversite bilgileri"` | `"general"` |

**TestNormalizeForBm25** — BM25 Normalizasyon (3 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_splits_compound_words` | BM25 normalizasyonu bileşik kelimeleri ayırır | `"anadal yandal"` → `"ana dal"` ve `"yan dal"` |
| `test_no_synonym_expansion` | BM25 normalizasyonu sinonim genişletme YAPMAZ | `"çap nedir"` → `"ikinci lisans"` eklenmez |
| `test_empty_input` | Boş girdi boş string döndürür | `""` → `""` |

**TestEdgeCases** — Sınır Durumlar (4 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_empty_query` | Boş string boş döner | `""` → `""` |
| `test_whitespace_only` | Sadece boşluk boş döner | `"   "` → `""` |
| `test_single_word` | Tek kelimelik sorgu çalışır | `"merhaba"` → `"merhaba"` |
| `test_query_with_punctuation` | Noktalama işaretli sorgu çalışır | `"Kayıt dondurma nasıl yapılır?"` → işlenir |

---

#### 7.3.2 `test_embedder.py` — Embedding Üretici Testleri (14 test)

Embedding modelini (`SentenceTransformer`) mock'layarak vektör üretim mantığını test eder. Gerçek model yüklenmez — testler saniyeler içinde tamamlanır.

**Mock Stratejisi:** `SentenceTransformer` mock'u, `encode()` çağrıldığında sabit numpy array döndürür, `get_sentence_embedding_dimension()` ise 3 döndürür.

**TestEmbedderInit** — Constructor Testleri (6 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_default_model_from_config` | Config'den model adı okunur | `embedder.model_name` boş değil |
| `test_custom_model` | Özel model adı geçirilebilir | `"custom/model"` ayarlanır |
| `test_lazy_model_loading` | Model constructor'da yüklenmez | `embedder._model` is None |
| `test_e5_model_detected` | E5 model ailesi algılanır | `_is_e5_model=True`, `_is_bge_model=False` |
| `test_bge_model_detected` | BGE model ailesi algılanır | `_is_bge_model=True`, `_is_e5_model=False` |
| `test_unknown_model_no_prefix` | Bilinmeyen model ailesinde prefix yok | Her iki flag da `False` |

**TestEmbedTexts** — Toplu Embedding Üretimi (6 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_returns_vectors` | 2 metin → 2 vektör döner | `len(results) == 2`, `len(results[0]) == 3` |
| `test_empty_list_returns_empty` | Boş liste → `encode()` çağrılmaz | `results == []`, `encode.assert_not_called()` |
| `test_e5_query_prefix_added` | E5 modelinde sorgu prefix'i eklenir | Encode'a giden metin `"query: "` ile başlar |
| `test_e5_passage_prefix_added` | E5 modelinde belge prefix'i eklenir | Encode'a giden metin `"passage: "` ile başlar |
| `test_bge_no_prefix_added` | BGE modelinde prefix eklenmez | Encode'a giden metin orijinal kalır |
| `test_normalize_embeddings_enabled` | L2 normalizasyon aktif | `encode()` parametresinde `normalize_embeddings=True` |

**TestEmbedSingle** — Tekil Embedding Üretimi (2 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_returns_single_vector` | Tek metin → tek vektör | `isinstance(result, list)`, `len(result) == 3` |
| `test_default_is_query_true` | Varsayılan `is_query=True` | E5 modelinde `"query: "` prefix'i eklenir |

---

#### 7.3.3 `test_reranker.py` — Cross-Encoder Reranker Testleri (11 test)

Cross-encoder modelini (`CrossEncoder`) mock'layarak yeniden sıralama mantığını test eder. Mock model, sabit skorlar döndürür: `[0.9, 0.3, 0.7, 0.1, 0.5]`.

**Mock Stratejisi:** `CrossEncoder.predict()` mock'u sabit numpy array döndürür. 5 aday belge fixture olarak sağlanır (3'ü ÇAP ile ilgili, 2'si alakasız).

**TestRerankerRerank** — Yeniden Sıralama Testleri (6 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_reranks_by_score` | Sonuçlar skora göre azalan sıralanır | `scores == sorted(scores, reverse=True)` |
| `test_top_k_limits_results` | `top_k=3` → en fazla 3 sonuç | `len(results) == 3` |
| `test_scores_assigned_correctly` | Cross-encoder skorları doğru atanır | `results[0]["score"] == 0.9`, `results[1]["score"] == 0.7` |
| `test_empty_candidates` | Boş liste → `predict()` çağrılmaz | `results == []`, `predict.assert_not_called()` |
| `test_single_candidate` | Tek aday → tek sonuç | `len(results) == 1`, `score == 0.85` |
| `test_preserves_metadata` | Metadata alanları korunur | Her sonuçta `"content"` ve `"source"` mevcut |

**TestRerankerInit** — Constructor Testleri (5 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_default_model_from_config` | Config'den model adı okunur | Model adında `"reranker"` veya `"bge"` geçer |
| `test_custom_model` | Özel model adı geçirilebilir | `"custom/model"` ayarlanır |
| `test_custom_max_length` | Özel max length geçirilebilir | `max_length == 256` |
| `test_custom_batch_size` | Özel batch size geçirilebilir | `batch_size == 8` |
| `test_lazy_model_loading` | Model constructor'da yüklenmez | `reranker._model is None` |

---

#### 7.3.4 `test_retriever.py` — Hibrit Arama Testleri (25 test)

Retriever modülünün çekirdek mantığını test eder: BM25 Türkçe tokenizer, sorgu konu tespiti, kaynak uyumluluğu penalty sistemi, deduplication algoritması ve sorgu cache'i. Ağır bağımlılıklar (ChromaDB, Embedder, CrossEncoder) mock'lanır.

**TestTurkishBm25Preprocess** — Türkçe BM25 Tokenizer (7 test)

| Test | Açıklama | Girdi | Beklenen Çıktı |
|------|----------|-------|----------------|
| `test_lowercase` | Tüm tokenlar küçük harfe çevrilir | `"Merhaba DÜNYA"` | Tüm tokenlar lowercase |
| `test_compound_word_split` | "anadal" ayrı tokenlara bölünür | `"anadal programı"` | `["ana", "dal", "programı"]` |
| `test_yandal_split` | "yandal" ayrı tokenlara bölünür | `"yandal başvurusu"` | `"yan"` ve `"dal"` mevcut |
| `test_punctuation_removed` | Noktalama işaretleri temizlenir | `"Kayıt, nasıl yapılır?"` | Virgül ve soru işareti yok |
| `test_single_char_tokens_removed` | Tek karakterli tokenlar atılır | `"A ve B arası"` | `"a"` ve `"b"` yok |
| `test_empty_input` | Boş girdi boş liste döner | `""` | `[]` |
| `test_whitespace_normalization` | Fazla boşluklar normalleştirilir | `"kayıt   dondurma    işlemi"` | `["kayıt", "dondurma", "işlemi"]` |

**TestDetectQueryTopic** — Sorgu Konu Tespiti (7 test)

| Test | Açıklama | Girdi | Beklenen Çıktı |
|------|----------|-------|----------------|
| `test_cap_detected` | "çap" anahtar kelimesi tespit edilir | `"çap not ortalaması"` | `"çap"` |
| `test_yatay_gecis_detected` | "yatay geçiş" tespit edilir | `"yatay geçiş şartları"` | `"yatay geçiş"` |
| `test_staj_detected` | "staj" tespit edilir | `"staj süresi kaç gündür"` | `"staj"` |
| `test_yaz_okulu_detected` | "yaz okulu" tespit edilir | `"yaz okulu harç ücreti"` | `"yaz okulu"` |
| `test_longer_match_preferred` | Uzun kalıp önce eşleşir | `"çift ana dal not ortalaması"` | `"çift ana dal"` (not `"çap"`) |
| `test_no_topic_detected` | Konu bulunamazsa None döner | `"merhaba dünya"` | `None` |
| `test_empty_query` | Boş sorgu None döner | `""` | `None` |

**TestApplySourceRelevance** — Kaynak Uyumluluğu Penalty (7 test)

| Test | Açıklama | Senaryo | Beklenen Davranış |
|------|----------|---------|-------------------|
| `test_on_topic_not_penalized` | On-topic sonuçlara dokunulmaz | ÇAP sorusu + ÇAP kaynağı | Skor değişmez |
| `test_off_topic_penalized` | Off-topic sonuçlar cezalandırılır | ÇAP sorusu + yatay geçiş kaynağı | `skor × 0.75` |
| `test_resorted_after_penalty` | Penalty sonrası yeniden sıralanır | Off-topic #1'de, on-topic #2'de | On-topic #1'e çıkar |
| `test_no_topic_no_change` | Konu tespiti yapılamazsa dokunulmaz | Genel sorgu | Skorlar aynı kalır |
| `test_empty_results` | Boş liste → boş liste | Sonuç yok | `[]` |
| `test_custom_penalty` | Özel penalty faktörü kullanılabilir | `penalty=0.5` | `skor × 0.5` |
| `test_yatay_gecis_topic` | Farklı konu tipi de çalışır | Yatay geçiş sorusu + ÇAP kaynağı | ÇAP kaynağı cezalandırılır |

> **Tespit Edilen Bug ve Düzeltme:** `test_on_topic_not_penalized` ilk çalıştırmada fail verdi. `"ÇİFT ANA DAL PROGRAMI.pdf"` dosya adında Türkçe `İ` karakteri var. Python'da `"İ".lower()` = `"i̇"` (i + combining dot above) üretir — bu `"çift ana dal"` kalıbıyla eşleşmez. **Çözüm:** `_turkish_lower()` yardımcı fonksiyonu eklendi: `İ→i`, `I→ı` dönüşümü `.lower()`'dan önce uygulanır.

**TestDeduplicationLogic** — Tekrar Eleme Mantığı (5 test)

| Test | Açıklama | Senaryo | Beklenen Davranış |
|------|----------|---------|-------------------|
| `test_dedup_removes_duplicate` | Aynı içerik tek sonuç olur | 2× aynı metin | `len(results) == 1` |
| `test_dedup_keeps_max_score` | BM25 (0.0) önce gelirse ChromaDB skoru korunur | BM25=0.0, ChromaDB=0.8 | `score == 0.8` |
| `test_dedup_keeps_max_score_reverse_order` | ChromaDB önce gelirse de max korunur | ChromaDB=0.8, BM25=0.0 | `score == 0.8` |
| `test_dedup_different_content_kept` | Farklı içerikler ayrı kalır | İçerik A + İçerik B | `len(results) == 2` |
| `test_dedup_empty_list` | Boş liste boş döner | Belge yok | `[]` |

**TestQueryCache** — Sorgu Cache Testleri (6 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_put_and_get` | Cache'e yazılan değer okunabilir | `cache.get("key1") == data` |
| `test_miss_returns_none` | Var olmayan anahtar None döner | `cache.get("nonexistent") is None` |
| `test_expired_entry_returns_none` | TTL dolmuş kayıt döndürülmez | `ttl=0` → `sleep` → `None` |
| `test_invalidate_clears_all` | `invalidate()` tüm cache'i temizler | 2 kayıt → `invalidate()` → `size == 0` |
| `test_size_property` | `size` property doğru çalışır | 0 → put → 1 |
| `test_different_keys_independent` | Farklı anahtarlar birbirini etkilemez | `q1::5` ve `q2::5` bağımsız |

---

#### 7.3.5 `test_rag_pipeline.py` — RAG Pipeline Temel Testleri (29 test)

Document Loader, Text Preprocessor ve TextChunker modüllerini test eder. Dosya I/O testleri `tmp_path` fixture'ı ile geçici dizinlerde yapılır.

**TestDocumentLoader** (7 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_load_txt_file` | TXT dosyası yüklenir, metadata doğru | `doc.content`, `metadata["file_type"]`, `metadata["category"]` |
| `test_load_txt_with_cp1254_encoding` | Windows Türkçe encoding fallback çalışır | `"Öğrenci"` içerik okunabilir |
| `test_skip_short_files` | Çok kısa dosyalar atlanır | `doc is None` |
| `test_unsupported_extension` | Desteklenmeyen dosya türleri atlanır | `.xlsx` → `None` |
| `test_load_directory` | Klasördeki tüm uygun dosyalar yüklenir | 2 `.txt` yüklenir, `.xlsx` atlanır |
| `test_load_directory_with_subdirs` | Alt klasör adı kategori olarak alınır | `metadata["category"] == "yönergeler"` |
| `test_nonexistent_directory` | Var olmayan klasör boş liste döndürür | `docs == []` |

**TestDocument** (2 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_char_count` | Karakter sayısı doğru | `"Merhaba Dünya"` → 13 |
| `test_word_count` | Kelime sayısı doğru | `"Bu bir test cümlesidir"` → 4 |

**TestTextPreprocessor** (5 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_normalize_whitespace` | Fazla boşluklar temizlenir | `"Bu   bir    test"` → tek boşluk |
| `test_remove_page_numbers` | Sayfa numaraları kaldırılır | `"Sayfa 1"` silinir |
| `test_remove_repeated_headers` | 4+ kez tekrarlanan satırlar header kabul edilir | 4× header → tamamen silinir |
| `test_empty_input` | Boş/whitespace girdi boş döner | `""` → `""`, `"   "` → `""` |
| `test_clean_batch` | Toplu temizleme çalışır | 2 metin → 2 temiz metin |

**TestTextChunker** (6 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_basic_chunking` | Metin chunk'lara bölünür | `len(chunks) > 1`, boyut sınırı korunur |
| `test_metadata_propagation` | Kaynak metadata her chunk'a kopyalanır | `source`, `category`, `chunk_index`, `chunk_count` mevcut |
| `test_chunk_index_ordering` | Chunk indeksleri sıralı | `chunk.metadata["chunk_index"] == i` |
| `test_empty_text` | Boş metin boş liste döndürür | `[]` |
| `test_get_stats` | İstatistikler doğru hesaplanır | `min_size ≤ avg_size ≤ max_size` |
| `test_split_documents` | Birden fazla doküman chunk'lanır | 2 doc → 2+ chunk, her source mevcut |

**TestChunk** (1 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_char_and_word_count` | Boyut property'leri doğru | `"Üç kelime burada"` → 16 char, 3 word |

**TestContentHashIds** — Hash Tabanlı ID Üretimi (5 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_generates_correct_count` | 3 metin → 3 ID | `len(ids) == 3` |
| `test_ids_start_with_chunk_prefix` | ID'ler `chunk_` ile başlar | `ids[0].startswith("chunk_")` |
| `test_same_content_same_id` | Aynı kaynak + aynı içerik → aynı ID | `ids1[0] == ids2[0]` (idempotent) |
| `test_different_content_different_id` | Farklı içerik → farklı ID | `ids[0] != ids[1]` |
| `test_same_content_different_source_different_id` | Aynı içerik + farklı kaynak → farklı ID | `ids[0] != ids[1]` |

---

#### 7.3.6 `test_rag_retrieval.py` — Integration Testleri (17 test, ChromaDB gerekli)

ChromaDB'nin çalışıyor ve indekslenmiş olmasını gerektirir. Gerçek embedding modeli ve cross-encoder kullanılır. ChromaDB erişilemezse tüm testler otomatik atlanır.

**TestChromaDBConnectivity** — Bağlantı Testleri (2 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_heartbeat` | ChromaDB heartbeat endpoint'i yanıt veriyor | HTTP 200 |
| `test_collections_endpoint` | Koleksiyon listesi alınabiliyor | JSON list döner |

**TestCollectionState** — Koleksiyon Durum Testleri (3 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_collection_exists` | Koleksiyon var ve boş değil | `count > 0` |
| `test_collection_has_expected_count` | Beklenen chunk sayısına sahip | `count > 100` |
| `test_documents_have_metadata` | Metadata alanları mevcut | `"source"` metadata alanı var |

**TestHybridSearch** — Tam Pipeline Testleri (7 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_search_returns_results` | Arama sonuç döndürür | `len(results) > 0` |
| `test_results_have_required_fields` | Sonuçlarda gerekli alanlar var | `content`, `source`, `score` |
| `test_results_sorted_by_score` | Sonuçlar skora göre azalan sıralı | `scores == sorted(reverse=True)` |
| `test_cap_query_returns_cap_source` | ÇAP sorusu ÇAP kaynağı döndürür | Top-3'te ÇAP kaynağı |
| `test_yatay_gecis_query` | Yatay geçiş sorusu doğru kaynak döndürür | Top-3'te yatay geçiş kaynağı |
| `test_top_k_parameter` | `top_k` parametresi çalışır | `top_k=3` → max 3 sonuç |
| `test_performance_under_threshold` | Yanıt süresi 10s altında | `elapsed_ms < 10000` |

**TestQueryCache** — Canlı Cache Testleri (2 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_cache_hit_faster` | Cache hit ilk aramadan hızlı | `second_ms < first_ms` |
| `test_cache_returns_same_results` | Cache tutarlı sonuç döndürür | Kaynak ve skor eşleşir |

**TestTestQuestions** — Değerlendirme Testi (1 test)

| Test | Açıklama | Doğrulanan Davranış |
|------|----------|---------------------|
| `test_at_least_70_percent_precision_at_3` | 20 soruluk test setinde Precision@3 ≥ %70 | `correct / total >= 0.70` |

---

#### 7.3.7 FAZ 0 Testleri (Mevcut, dokunulmadı)

| Test Dosyası | Test Sayısı | Kapsam |
|-------------|:-----------:|--------|
| `test_config.py` | 10 | Department enum, TaskType, Priority, güven eşikleri |
| `test_connection.py` | 8 | Lazy init, session commit/rollback, dispose, SQLite izolasyonu |
| `test_models.py` | 7 | Student, Tuition, QueryLog JSONB, AgentRegistry |
| `test_schemas.py` | 16 | RAGQuery validasyon, RoutingResult, DepartmentResponse, Health |

---

### 7.4 Testlerde Tespit Edilen ve Düzeltilen Buglar

| Bug | Tespit Eden Test | Kök Neden | Düzeltme |
|-----|-----------------|-----------|----------|
| `"çiftanadal"` → `"çiftana dal"` (yanlış) | `test_ciftanadal_splits` | `COMPOUND_WORD_SPLITS` sözlüğünde `"anadal"` anahtarı `"çiftanadal"`dan önce eşleşiyordu | `_split_compound_words` metodunda anahtarlar uzunluğa göre azalan sırada sıralandı |
| Türkçe `İ` karakteri source matching'de eşleşmeme | `test_on_topic_not_penalized` | Python `"İ".lower()` = `"i̇"` (i + combining dot above) üretir, `"çift ana dal"` kalıbıyla eşleşmez | `_turkish_lower()` fonksiyonu eklendi: `İ→i`, `I→ı` dönüşümü `.lower()`'dan önce uygulanır |

---

### 7.5 Retrieval Doğruluk Testi (End-to-End)

8 farklı soru ile yapılan canlı sistem test sonuçları:

| Sorgu | #1 Doğru? | Cevap Top 3? | Skor | Kaynak Doğru? |
|-------|:---------:|:------------:|:----:|:------------:|
| ÇAP başvurusu için gereken not ortalaması kaçtır | ✅ | ✅ | 0.960 | ✅ |
| Sınav sonucuna itiraz süresi kaç gündür | ✅ | 5/5 doğru | 0.980 | ✅ |
| Kayıt dondurma süresi ne kadar | ✅ | ✅ | 0.966 | ✅ |
| Staj süresi kaç gündür | ✅ | ✅ | 0.839 | ✅ |
| Mezuniyet için gereken toplam AKTS kaçtır | Kısmen | ✅ (#3) | 0.833 | ✅ |
| Yan dal programına başvuru için not ortalaması | ✅ | ✅ | 0.685 | ✅ |
| Devamsızlık sınırı nedir | ✅ | ✅ | 0.527 | ✅ |
| Yaz okulunda en fazla kaç ders alınabilir | — | — | — | — |

**Özet:** 7/7 test edilen sorguda cevap top 3 içinde mevcut. 6/7 sorguda #1 sonuç doğru cevabı içeriyor.

### 7.6 Context Mixing Testi

Source Relevance mekanizması öncesi ve sonrası karşılaştırma:

| Sorgu | Off-topic Sonuç | Önceki | Sonrası |
|-------|----------------|--------|---------|
| ÇAP not ortalaması | Yatay geçiş → | #2 | #4 ✅ |
| Yan dal not ortalaması | Yatay geçiş → | #2 (0.628) | #2 (0.471) — fark kapandı |
| Kayıt dondurma | — | Değişiklik yok | Değişiklik yok ✅ |

---

## 8. Karşılaşılan Sorunlar ve Çözümler

### 8.1 Kritik Bug: Semantic Skor Kaybı (Faz 0.1)

**Sorun:** BM25 ve ChromaDB aynı belgeyi döndürdüğünde, eğer BM25 versiyonu (similarity_score=0.0) önce işlenirse, ChromaDB'nin gerçek semantic skoru kayboluyordu. Bu, en ilgili belgelerin düşük skorla sıralanmasına neden oluyordu.

**Kök Neden:** `seen_contents` bir `set` olarak kullanılıyordu ve ilk gelen skor korunuyordu.

**Çözüm:** `seen_contents` bir `Dict[str, int]` (content_key → index) yapısına dönüştürüldü. Tekrar eden içerik bulunduğunda `max(mevcut_skor, yeni_skor)` mantığı uygulanır.

### 8.2 BM25 page_content Tutarsızlığı (Faz 0.2)

**Sorun:** BM25, normalize edilmiş metni `page_content` olarak saklıyordu. ChromaDB ise orijinal metni kullanıyordu. Bu fark nedeniyle aynı belge iki farklı sonuç olarak görünüyordu.

**Çözüm:** BM25'in `page_content`'i orijinal metin yapıldı. Normalizasyon (bileşik kelime ayırma, küçük harf, noktalama temizleme) `preprocess_func` parametresine taşındı.

### 8.3 Heuristik Reranking'in Yetersizliği

**Sorun:** Özel formüldeki `bigram_count × 0.5` ağırlığı, keyword density'si yüksek ama semantik olarak alakasız belgelerin #1'e çıkmasına neden oluyordu. Örneğin "diploma not ortalaması" sorulduğunda, "not ortalaması" kelimesi 3 kez geçen ÇAP yönergesi yatay geçiş yönergesinin önüne geçiyordu.

**Çözüm:** Tüm heuristik formül (`_rerank`, `_turkish_pseudo_stem`, `QUERY_NOISE_WORDS`, `_normalize_turkish`) kaldırıldı. Yerine `seroe/bge-reranker-v2-m3-turkish-triplet` cross-encoder modeli entegre edildi.

### 8.4 MADDE Başlığı Kesilmesi

**Sorun:** `RecursiveCharacterTextSplitter` ile 512 karakterlik chunking yapıldığında, yasal maddelerin başlıkları bir chunk'ta, içeriği bir sonraki chunk'ta kalıyordu. İkinci chunk bağlamsız hale geliyordu.

**Çözüm:** MADDE-aware chunker geliştirildi. Chunk boyutu 1024'e çıkarıldı. Uzun maddeler bölündüğünde her alt chunk'a MADDE başlığı eklendi. Metadata'ya `madde_no` ve `bolum` bilgisi yazıldı.

### 8.5 E5 Model Prefix Sorunu

**Sorun:** `intfloat/multilingual-e5-base` modeline geçildiğinde, embedding kalitesi düşüktü. Nedeni: E5 modelleri sorgu için `"query: "` ve belge için `"passage: "` prefix'i gerektirmektedir. Prefix eklenmeden üretilen vektörler düşük kaliteli eşleşmeler üretiyordu.

**Çözüm:** `Embedder` sınıfına `is_query` parametresi ve model ailesine göre otomatik prefix ekleme mantığı geliştirildi. `BAAI/bge-m3`'e geçişle birlikte prefix ihtiyacı tamamen ortadan kalktı.

### 8.6 Bileşik Kelime Ayırma Sıralama Hatası (Unit Test ile Tespit)

**Sorun:** `"çiftanadal"` girdisi `"çift ana dal"` yerine `"çiftana dal"` olarak ayrılıyordu.

**Kök Neden:** `COMPOUND_WORD_SPLITS` sözlüğü Python dict iteration sırasıyla işleniyordu. `"anadal"` anahtarı `"çiftanadal"`dan önce eşleşerek `"çiftanadal"` → `"çiftana dal"` dönüşümü yapıyordu.

**Çözüm:** `_split_compound_words` metodunda sözlük anahtarları `sorted(..., key=len, reverse=True)` ile uzunluğa göre azalan sırada sıralanarak uzun eşleşmelerin öncelik alması sağlandı.

**Tespit:** `test_query_preprocessor.py::test_ciftanadal_splits`

### 8.7 Python Türkçe İ Karakteri Unicode Sorunu (Unit Test ile Tespit)

**Sorun:** `"ÇİFT ANA DAL PROGRAMI.pdf"` dosya adı, source relevance eşleştirmesinde `"çift ana dal"` kalıbıyla eşleşmiyordu.

**Kök Neden:** Python'da `"İ".lower()` çağrısı `"i"` (U+0069) değil, `"i̇"` (U+0069 + U+0307 combining dot above) üretir. Bu 2 karakterlik string, `"çift ana dal"` kalıbındaki `"i"` ile eşleşmez.

**Çözüm:** `_turkish_lower()` yardımcı fonksiyonu eklendi. `İ→i` ve `I→ı` dönüşümleri `.lower()` çağrısından **önce** uygulanarak Python'un Unicode davranışı düzeltilir:

```python
def _turkish_lower(text: str) -> str:
    return text.replace("İ", "i").replace("I", "ı").lower()
```

**Tespit:** `test_retriever.py::test_on_topic_not_penalized`

**Etki:** Bu bug, Türkçe büyük harf İ içeren tüm dosya adlarında source relevance eşleştirmesini bozuyordu. Düzeltme sonrası `"ÇİFT ANA DAL (İKİNCİ LİSANS) VE YAN DAL PROGRAMI.pdf"` gibi Türkçe karakter içeren dosya adları da doğru eşleşir.

---

## 9. Komut Satırı Araçları

### 9.1 İndeksleme (`scripts/index_documents.py`)

Tüm RAG pipeline'ını baştan sona çalıştırır:

```powershell
# Mevcut indeksi ezerek yeniden oluştur
venv\Scripts\python.exe scripts\index_documents.py --reindex

# Özel parametrelerle
venv\Scripts\python.exe scripts\index_documents.py --chunk-size 1024 --chunk-overlap 128 --collection test_v2
```

### 9.2 Semantik Sorgu (`scripts/query_db.py`)

Pipeline'ı bypass ederek doğrudan ChromaDB'de semantik arama yapar:

```powershell
venv\Scripts\python.exe scripts\query_db.py "Yaz okulu harç ücreti" --top-k 5
```

### 9.3 Hibrit Arama Testi (`scripts/test_hybrid_search.py`)

Tam arama pipeline'ını (BM25 + Semantic + Cross-Encoder) test eder:

```powershell
# Standart test
venv\Scripts\python.exe scripts\test_hybrid_search.py "ÇAP başvurusu için gereken not ortalaması kaçtır"

# Tam metin gösterimi
venv\Scripts\python.exe scripts\test_hybrid_search.py "kayıt dondurma süresi ne kadar" --full

# Ağırlık özelleştirme
venv\Scripts\python.exe scripts\test_hybrid_search.py "staj süresi" --bm25-weight 0.6 --vector-weight 0.4
```

### 9.4 RAG Değerlendirme (`scripts/evaluate_rag.py`)

20 test sorusu üzerinden otomatik Precision@k ölçümü yapar, rapor üretir:

```powershell
# Varsayılan (top-k=5, rapor docs/ altına)
venv\Scripts\python.exe scripts\evaluate_rag.py

# Özel parametreler
venv\Scripts\python.exe scripts\evaluate_rag.py --top-k 3 --output docs/custom_report.md

# Cache devre dışı (her sorgu gerçek arama yapar)
venv\Scripts\python.exe scripts\evaluate_rag.py --no-cache
```

**Çıktılar:**
- `docs/rag_evaluation_report.md` — Markdown formatında detaylı rapor
- `docs/rag_evaluation_report.json` — Makine okunabilir metrikler ve detaylar

**Hesaplanan Metrikler:**
- Precision@1, @3, @5 (kaynak doğruluğu)
- Zorluk seviyesine göre kırılım (easy/medium/hard)
- Ortalama top-1 skor
- Ortalama yanıt süresi (ms)
- Başarısız sorgular ve nedenleri

**Test Soruları:** `data/test/rag_test_questions.json` — 20 soru, 3 zorluk seviyesi, 2 kategori (factual/procedural), beklenen kaynak kalıpları.

### 9.5 Integration Testler

ChromaDB ve gerçek modeller ile canlı testler:

```powershell
# Integration testleri çalıştır (ChromaDB gerekli)
venv\Scripts\python.exe -m pytest tests/integration/ -v --tb=short
```

> ChromaDB erişilemezse testler otomatik atlanır (`skipif`).

---

## 10. Bağımlılıklar

| Paket | Sürüm | Amaç |
|-------|-------|------|
| `sentence-transformers` | 3.4.1+ | Embedding ve cross-encoder modelleri |
| `transformers` | 4.48.1+ | HuggingFace model altyapısı |
| `torch` | 2.6.0+ | PyTorch backend (GPU/CPU) |
| `langchain` | 0.3.14+ | EnsembleRetriever, BM25Retriever |
| `langchain-community` | 0.3.14+ | BM25Retriever implementasyonu |
| `langchain-text-splitters` | 0.3.4+ | RecursiveCharacterTextSplitter (sub-chunking) |
| `rank-bm25` | 0.2.2+ | BM25 algoritma implementasyonu |
| `httpx` | 0.28.1+ | ChromaDB REST API async client |
| `pdfplumber` | 0.11+ | PDF metin çıkarma |
| `structlog` | 25.1.0+ | Yapılandırılmış loglama |
| `pydantic-settings` | 2.9.1+ | Konfigürasyon yönetimi |

---

## 11. Dosya Değişiklik Özeti

| Dosya | Durum | Açıklama |
|-------|-------|----------|
| `src/rag/chunker.py` | Yeniden Yazıldı | MADDE-aware v2 chunking |
| `src/rag/embedder.py` | Güncellendi | BGE-M3 desteği, dinamik prefix mantığı, error handling |
| `src/rag/reranker.py` | Yeni Dosya | Cross-encoder reranker modülü, error handling |
| `src/rag/retriever.py` | Büyük Güncelleme | v3.0 — dedup, BM25 fix, cross-encoder, source relevance, `_turkish_lower()`, `_QueryCache`, performans ölçümü |
| `src/rag/query_preprocessor.py` | Güncellendi | Duplicate sinonim düzeltmesi, compound word sıralama fix |
| `src/rag/pipeline.py` | Güncellendi | Hash tabanlı ID, `upsert_documents`, `doc_registry.json` üretimi, error handling |
| `src/rag/indexer.py` | Güncellendi | `upsert_documents()` ve `_batch_write()` eklendi (idempotent indeksleme) |
| `src/rag/__init__.py` | Güncellendi | CrossEncoderReranker export'u |
| `src/core/config.py` | Güncellendi | RerankerSettings eklendi, EmbeddingSettings güncellendi, min_similarity=0.0 |
| `scripts/test_hybrid_search.py` | Güncellendi | v3 başlığı, `--full` parametresi, karakter sayısı gösterimi |
| `scripts/evaluate_rag.py` | Yeni Dosya | Otomatik RAG değerlendirme — Precision@k, rapor üretimi |
| `data/test/rag_test_questions.json` | Yeni Dosya | 20 soruluk standart test seti (zorluk, kategori, beklenen kaynaklar) |
| `.env.example` | Güncellendi | Güncel model adları, RAG parametreleri, Reranker ayarları |
| `pyproject.toml` | Güncellendi | Integration test marker tanımı |
| `Makefile` | Güncellendi | `evaluate` komutu eklendi |
| `tests/unit/test_query_preprocessor.py` | Yeni Dosya | 22 test — bileşik kelime, sinonim, sorgu tipi, BM25, edge case |
| `tests/unit/test_embedder.py` | Yeni Dosya | 14 test — model algılama, prefix, vektör üretimi |
| `tests/unit/test_reranker.py` | Yeni Dosya | 11 test — cross-encoder sıralama, skor, metadata |
| `tests/unit/test_retriever.py` | Yeni Dosya | 25 test — BM25, konu tespiti, source relevance, dedup, cache |
| `tests/unit/test_rag_pipeline.py` | Güncellendi | 29 test — 5 yeni hash ID üretimi testi eklendi |
| `tests/integration/conftest.py` | Yeni Dosya | ChromaDB erişilebilirlik kontrolü, session-scoped fixture'lar |
| `tests/integration/test_rag_retrieval.py` | Yeni Dosya | 17 test — bağlantı, koleksiyon, hibrit arama, cache, Precision@3 |

---

## 12. Gelecek Adımlar (FAZ 2+)

1. **LLM Entegrasyonu:** Retrieval sonuçlarını LLM'e (Qwen2.5 / Ollama) göndererek doğal dilde cevap üretme
2. **Basit Sorular İçin LLM'siz Cevap:** Yüksek skorlu tek chunk'tan doğrudan cevap çıkarma
3. **Conversation Memory:** Çok turlu diyalog desteği
4. ~~**Değerlendirme Framework'ü:** RAGAS metrikleri ile sistematik RAG değerlendirmesi~~ → ✅ Precision@k tabanlı değerlendirme altyapısı kuruldu (`evaluate_rag.py`). RAGAS metrikleri LLM entegrasyonu sonrası eklenecek.
5. **Ajan Entegrasyonu:** A2A protokolü ile departman ajanlarına bağlantı
6. **Çoklu Departman Verisi:** Finans ve Bilgi İşlem departmanları için doküman seti

---

*Bu doküman, projenin FAZ 1 kapsamındaki tüm teknik çalışmaları yansıtmaktadır. FAZ 2 tamamlandığında güncellenecektir.*
