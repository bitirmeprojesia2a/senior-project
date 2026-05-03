# Cache Stratejisi

> Durum Notu (Nisan 2026): Bu belge cache kararlarinin aktif strateji notudur. Dagitik A2A modunda cache davranisi sadece tek process performansi degil; Slack follow-up, auth, announcement/event capability agent'lari ve merkezi `retrieval-service` ile birlikte dusunulmelidir. Calistirma komutlari icin `KURULUM_VE_CALISTIRMA.md`, genel mimari icin `A2A_DAGITIK_MIMARI_VE_CALISMA_OZETI.md` okunmalidir.

Bu dokuman, sistemde hangi cache katmanlarinin oldugunu, hangi sorgularin
hangi seviyede cache alabildigini ve neden bazi akislarda bilerek cache
kullanilmadigini ozetler.

## Amac

Cache katmanlari iki farkli hedefe hizmet eder:

- tekrar eden stabil sorgularda gecikmeyi dusurmek
- agir retrieval ve model yuklemelerini tekrar etmemek

Ancak yanlis yerde agresif cache kullanimi, ozellikle follow-up, duyuru ve
kisisel sorgularda hatali cevaplari sabitleyebilir. Bu yuzden strateji
bilincli olarak muhafazakardir.

## Katmanlar

### 1. Question Cache

Dosyalar:

- `src/cache/question_cache.py`
- `src/cache/policy.py`
- `src/orchestrators/main.py`

Bu katman, belirli sorgularda dogrudan son kullanici cevabini TTL ile bellek
icinde tutar.

Mevcut davranis:

- ayni process icinde in-memory lookup yapar
- Redis aciksa ayni cache namespace'ini process'ler arasinda da paylasir
- Redis hit oldugunda sonucu local bellekte de isitip sonraki tekrarlarin
  maliyetini dusurur

Temel ilke:

- lookup muhafazakar
- store daha da muhafazakar

### 2. Retriever Query Cache

Dosyalar:

- `src/rag/query_cache.py`
- `src/rag/retriever.py`

Bu katman, ayni retrieval sorgusunun sonucunu TTL ile tutar.

Bu katman:

- final cevabi degil retrieval ciktisini saklar
- kapsamli sorgularda da guvenli bir hizlandirma saglar
- nihai LLM cevabini sabitlemez
- Redis aciksa process'ler arasinda paylasilabilir

### 3. BM25 Resource Cache

Dosya:

- `src/rag/retriever.py`

Bu katman su nesneleri paylasir:

- BM25 belge listeleri
- BM25 retriever nesneleri

Amac, ayni koleksiyonlar icin indeksleme maliyetini tekrar tekrar odememektir.

### 4. Model Cache

Dosyalar:

- `src/rag/embedder.py`
- `src/rag/reranker.py`

Bu katman:

- embedding modelini
- reranker modelini

ayni process icinde tekrar kullanir.

Not:

- model cache'leri bilincli olarak Redis'e tasinmamistir
- model nesnelerini Redis'e yazmak dogru katman degildir
- multi-instance ortamlarda bu katman halen process-local kalir

### 5. Conversation Cache

Dosya:

- `src/cache/conversation_cache.py`

Bu katman Redis tabanlidir ve follow-up state okumalarini hizlandirmak icin
kullanilir. Kaynak dogruluk modeli PostgreSQL olmaya devam eder; Redis burada
best-effort hizlandirma katmanidir.

## Question Cache Policy

### Lookup Icin Uygun

Asagidaki kosullari saglayan sorgularda question cache lookup denenir:

- anonim sorgu
- follow-up olmayan sorgu
- mevcut konusma baglami kullanmayan sorgu
- announcement olmayan sorgu
- contact olmayan sorgu
- announcement enrichment gerektirmeyen sorgu

### Store Icin Uygun

Lookup uygun olsa bile her cevap cache'e yazilmaz. Store sadece su cevaplarda
yapilir:

- `RoutingStrategy.DIRECT`
- tek departmanli routing
- tek departmanli final cevap
- global synthesis kullanilmamis
- `generation_modes` icinde `llm` yok
- announcement source yok

### Bilerek Cache Almayan Akislar

Asagidaki akislarda tam cevap cache bilerek disarida tutulur:

- authenticated ve kisisel sorgular
- follow-up sorular
- duyuru ve duyuruya benzer sorgular
- contact sorgulari
- coklu departmanli cevaplar
- global synthesis ve LLM agirlikli cevaplar

Bu tasarim, hiz kazanirken yanlis cevabi sabitlememek icin secildi.

## Ikinci Faz Sonucu

Ikinci fazda hedef, basit ve deterministik sorularda full-response cache'i
korurken, kapsamli sorularda sistemi gereksiz yere yanlisa kilitlememekti.

Bu faz sonunda davranis su sekilde netlesti:

- basit, tek departmanli ve kural veya DB agirlikli sorular:
  - `lookup = evet`
  - `store = evet`
- kapsamli ama hala cache'e bakilabilecek sorular:
  - `lookup = evet`
  - `store = hayir`
- baglama duyarli veya tazelik gerektiren sorular:
  - `lookup = hayir`
  - `store = hayir`

Pratikte bu su anlama gelir:

- `CACHE ON` altinda basit sorularda genellikle `miss -> hit -> hit`
- coklu departmanli ve synthesis gerektiren sorularda genellikle
  `miss -> miss -> miss`
- follow-up ve announcement benzeri akislarda genellikle `bypass`

Bu ayrim bilinclidir. Amac, hizlandirma kazanirken genellenmemesi gereken
cevaplari kalici hale getirmemektir.

## Kapsamli Sorular Icin Strateji

Kapsamli sorular icin dogrudan full-response cache onermiyoruz.

Tercih edilen sira:

1. retriever query cache
2. BM25 resource cache
3. model cache
4. sadece cok stabil alt kumelerde full-response cache

Sebep:

- kapsamli sorularda department karisimi degisebilir
- LLM synthesis farkli baglamlarla farkli uretim yapabilir
- follow-up veya ufak query degisimleri anlami kaydirabilir

Bu nedenle kapsamli sorularda bugun icin alt katman cache stratejisi daha
guvenlidir.

## Guvenli Soru Siniflari

### Full-Response Cache Icin Guvenli

Su tip sorular bugunku tasarimda tam cevap cache'i icin guvenlidir:

- tek departmanli, dogrudan DB ve kural cevaplari
- ders kodu, on kosul ve mufredat gibi deterministik akademik sorular
- kayit donemi gibi stabil ogrenci isleri lookup'lari
- ek baglam istemeden verilen finans netlestirme cevaplari

### Lookup Only, Store Yok

Su tip sorularda question cache lookup denenebilir; ancak final cevap cache'e
yazilmaz:

- coklu departmanli sorular
- global synthesis kullanan cevaplar
- `generation_modes` icinde `llm` bulunan cevaplar
- announcement source karisabilen cevaplar

Bu katmanda asil hiz kazanci genellikle:

- retriever query cache
- BM25 resource cache
- embedder ve reranker model cache

uzerinden gelir.

### No-Cache

Su tip sorular bugunku tasarimda bilerek cache disinda tutulur:

- authenticated ve kisisel sorgular
- follow-up akislari
- duyuru ve duyuruya yakin sorgular
- contact ve iletisim sorgulari
- conversation context'e aktif bagimli sorular

## Gozlemlenebilirlik

Question cache durumu telemetry metadata icine yazilir:

- `hit`
- `miss`
- `bypass`

Smoke test scripti:

- `scripts/cache_smoke.py`

Yonetim scripti:

- `scripts/manage_cache.py`

Temel komutlar:

```powershell
.\venv\Scripts\python.exe -m scripts.cache_smoke
```

```powershell
.\venv\Scripts\python.exe -m scripts.cache_smoke --verbose
```

```powershell
.\venv\Scripts\python.exe -m scripts.manage_cache show
```

```powershell
.\venv\Scripts\python.exe -m scripts.manage_cache clear-runtime
```

```powershell
.\venv\Scripts\python.exe -m scripts.manage_cache invalidate-conversation --context-id "ornek-context-id"
```

Beklenen yorum:

- `show` yeni bir Python surecinde calistigi icin process-local runtime
  cache'i genellikle sifirdan baslatir
- bu nedenle local soru veya model cache sayaçlari sifir gorunebilir
- buna karsilik Redis-backed question ve retriever cache boyutlari ayrica
  gorulebilir
- Redis conversation cache ise process-disidir; bu nedenle
  `invalidate-conversation` ayrica anlamlidir

## Onemli Not

`question_cache` ve retriever query cache artik iki katmanlidir:

- local process cache
- opsiyonel Redis-backed paylasimli cache

`embedder` ve `reranker` model cache'leri ise hala process-local cache'tir.

`invalidate-conversation` ise Redis tabanli conversation cache girdisini
gecersiz kilmak icin kullanilir ve process-disidir.

## Test Kapsami

Test dosyalari:

- `tests/unit/test_question_cache.py`
- `tests/unit/test_cache_policy.py`
- `tests/unit/test_retriever.py`
- `tests/unit/test_model_cache.py`
- `tests/unit/test_orchestrators.py`

Bu testler su davranislari kilitler:

- cache acik
- cache kapali
- hit ve miss davranisi
- announcement bypass
- follow-up bypass
- multi-department cevaplarin store edilmemesi
- `llm` uretimli cevaplarin store edilmemesi

Canli smoke beklentisi:

- basit sorularda `CACHE ON` altinda `1 miss + 2 hit`
- kompleks coklu departmanli sorularda `CACHE ON` altinda `hit` beklenmez
- `CACHE OFF` altinda tum turlar `bypass` olmalidir
