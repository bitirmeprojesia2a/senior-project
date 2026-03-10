# FAZ 2 — LLM Servis Altyapısı: Teknik Dokümantasyon

**Proje:** Üniversite Kurumsal Destek Sistemi  
**Doküman Tarihi:** 6 Mart 2026  
**Yazar:** Geliştirme Ekibi  
**Durum:** ✅ Tamamlandı  

---

## 1. Amaç ve Kapsam

Bu doküman, projenin İkinci Fazında (FAZ 2) gerçekleştirilen **LLM (Büyük Dil Modeli) Servis Altyapısı** çalışmalarını detaylandırmaktadır. 

FAZ 2, sistemin kalbini oluşturacak olan yerel yapay zeka entegrasyonunu hedefler. Temel amacımız dış kaynaklara (OpenAI, Claude vb.) bağımlılığı en aza indiren, veri gizliliğini (öğrenci verisi yerelde kalır) sağlayan ve **SDK-minimized (SDK bağımlılığını azaltan)** bir mimariyle hata toleranslı (Fault-Tolerant) bir LLM katmanı yaratmaktır.

**FAZ 2 Kapsamında Tamamlanan İş Kalemleri:**
1. Ollama Docker entegrasyonu ve `Qwen2.5:7B` modelinin kurulması
2. `OllamaClient` HTTP REST API entegrasyonu (SDK bağımsız)
3. `OpenAIClient` gelişmiş Fallback (yedekleme) mekanizması
4. `LLMService` orkestratör sınıfının uygulanması
   - Katı JSON doğrulama motoru
   - 30 saniye Timeout yönetimi
   - Exponential Backoff (katlanarak artan) 3 tekrarlı Retry mekanizması
   - Context window koruması (128K Token warning layer)
5. `tests/unit/test_llm_service.py` ile 100% Core coverage

---

## 2. Mimari Kararlar ve Teknoloji Seçimleri

### 2.1 Yerel LLM Engine: Ollama + Qwen2.5:7B
Projede ağır bir framework kullanmak yerine **Ollama** tercih edilmiştir.  
Bunun en büyük faydaları şunlardır:
- Standart bir Docker container'ı içerisinde dışarıya bağımlı olmayan yalıtılmış bir sunucu sağlar.
- Model olarak **Qwen2.5:7B** seçilmiştir. 128k context-window boyutuna sahip olup JSON çıktılarındaki başarı oranı ve Türkçe desteği 7B parametre standardına göre oldukça yüksektir.

### 2.2 İletişim Protokolü: Yalnızca HTTP (`httpx`)
İstemci implementasyonunda Ollama veya OpenAI Python SDK'leri kullanılmamıştır; iletişim `httpx` ile kurulmuştur. `requirements.txt` içinde `openai` paketi tanımlı olsa da mevcut istemci akışı bu SDK'ye dayanmaz.  
**Nedeni:**
- İstemci katmanını SDK davranışlarına sıkı bağlamamak.
- Asenkron iletişimde tam kontrol sahibi olmak. Timeout ve Stream davranışlarını projenin custom (özel) ihtiyaçlarına göre belirleyebilmek.

### 2.3 Retry Stratejisi: `tenacity`
Model zaman aşımına uğradığında veya Docker geçici olarak yanıt vermediğinde, sistem anında çökmez. `tenacity` modülüyle **Exponential Backoff** (2 saniye, 4 saniye, 8 saniye... vb.) mantığıyla sorguyu 3 kere otomatik dener.

---

## 3. Bileşenlerin İç Yapısı ve Akış

Yeni oluşturulan `src/llm/` modülü 4 temel dosyadan oluşur.

```text
src/llm/
├── prompt_templates.py  # Sistem genelindeki prompt kalıpları
├── ollama_client.py     # Yerel model iletişimi
├── openai_client.py     # Yedek (Fallback) ağ iletişimi
└── llm_service.py       # Akış ve orkestrasyon sınıfı
```

### 3.1 Gelişmiş LLM Orkestrasyonu Akışı (`generate` Metodu)

Kullanıcı "ÇAP koşulları nedir?" diye sorduğunda sistemin işletim akışı şu şekildedir:

```text
┌────────────────────────────────────────────────────────┐
│  LLMService.generate(prompt="ÇAP nedir?", json_mode)   │
└──────────┬─────────────────────────────────────────────┘
           │
           ▼
1. Token Kontrolü (_check_token_limit)
   Eğer metin 100.000 token sınırını aşıyorsa Logger uyarı atar.
           │
           ▼
2. Ollama'ya İstek Gönder (Exponential Backoff devrede)
   - Başarılıysa? → 4. Adıma atla
   - Hata (Timeout/Connection)? → 3. Kez tekrarla
   - 3. Kez de Hata mı aldı? → 3. Adıma Geç (Fallback)
           │
           ▼
3. Fallback: OpenAI'a Yönlendirme
   Sistem ayarlarına bakar: self.use_fallback (api_key var mı?)
   - Evetse: openai_client.generate() çağrılır.
   - Hayırsa: Exception fırlatılır (Tüm LLMler Çöktü!)
           │
           ▼
4. JSON Doğrulaması (Eğer json_mode=True istenmişse)
   - Gelen HTTP yanıtı string'dir. _validate_json() ile JSON'a çevrilmeye çalışılır.
   - Başarısız olursa LLMServiceError fırlatılır ve model çıktısına güvenilmez.
           │
           ▼
        RETURN str
```

### 3.2 İstemciler (Clients)

#### OllamaClient
- `POST /api/generate`: Standart text ve JSON üretim endpointi.
- `GET /api/tags`: Modelin health-check (sağlık kontrolü) sistemi için. Sistem, beklenen modelin `qwen2.5:7b` Ollama cache belleğinde yüklü olup olmadığını doğrular.

#### OpenAIClient
- Gelen formatik prompt metnini (system prompt, user prompt) OpenAI'nin kabul ettiği `[{"role": "system", "content": "..."}]` mesaj listesine dönüştürür.
- Kendi timeout limitini işletir.

---

## 4. Özel Modlar ve Yetenekler

### 4.1 Yapılandırılmış Yanıt Garantisi (JSON Modu)
A2A mimarisinin (ve routing mantığının) kusursuz çalışabilmesi için modellerin serbest metin üretmemesi, öngörülebilir çıktılar vermesi gereklidir. Bu, `json_mode=True` parametresiyle sağlanır.

*Kusursuz çalışan bir Prompt Şablonu (prompt_templates.py) desteği ile şu çıktı alınır:*
```json
{
    "departments": ["student_affairs"],
    "confidence": 0.9,
    "reasoning": "Soru ÇAP ile ilgili olduğu için..."
}
```
Sistem, `_validate_json()` üzerinden modelin "Anladım, işte JSON formatınız:" tarzı başlıklar/eklemeler yapıp yapmadığını JSON decoder ile denetler.

### 4.2 Streaming Desteği (Şelale Akışı)
Uzun cevaplı durumlarda kullanıcının 15-20 saniye siyah ekran izlemesini engellemek için `generate_stream` asenkron generator'ı hazırlandı.
Tokenlar üretildikçe Chunk by Chunk (parça parça) web/slack arayüzüne itilmeye hazır haldedir.

---

## 5. Sağlık Durumu (Health Raporu)
Ana sistem `get_health()` fonksiyonu ile aşağıdaki raporu döndürerek DevOps takibi yapmayı kolaylaştırır:

```json
{
    "status": "healthy",
    "primary": {
        "name": "ollama",
        "status": "healthy",
        "model_loaded": true
    },
    "fallback": {
        "name": "openai",
        "available": true,
        "status": "healthy"
    }
}
```

## 6. Güvenlik ve Hata Yönetimi
Projenin çökmesini engellemek adına LLM süreçlerinde oluşan _tüm hatalar_ sarmalanmıştır:
- `httpx.TimeoutException` → `OllamaClientError`
- `OllamaClientError` 3 kere üst üste alındığında → `OpenAI'ya soft switch`
- Her iki server da kopuksa → Kontrollü `LLMServiceError` exception döner ve A2A agent bu durumda kullanıcıya anlamlı bir hata mesajı ("Şu an yoğunluk var") döner.

## 7. Sonuç
Bu modülün inşa edilmesi ile Üniversitesi Sistemimiz; gelen sorguları NLP (Doğal Dil İşleme) kullanarak "Akıllı Anlamak" ve istenilen formatta yanıt çevirmek için tam otonom bir yapıya kavuşmuştur. Sistem kendi içerisinde kendini failover (yedekleme) yapabildiği için operasyonel kesinti oranı minimuma indirilmiştir.

---

## 8. MART 2026 GUNCELLEME NOTLARI

Bu bölüm, FAZ 2 sonrasında LLM katmanında yapılan ek dokümantasyon güncellemelerini içerir.

### 8.1 Prompt ve Departman Uyumu

* `prompt_templates.py` içindeki `DEPARTMENT_ROUTING_SYSTEM_PROMPT` artık şu departmanları içerir:
  * `finance`
  * `it_support`
  * `student_affairs`
  * `academic_programs`
* Bu prompt, çok departmanlı RAG çekirdeği ile uyumlu hale getirilmiştir.

### 8.2 Aktif LLM Yetkinlikleri

Mevcut LLM katmanında aktif olarak bulunan fakat önceki özetlerde daha az görünür kalan yetenekler:

* `OllamaClient.get_health()` ile modelin gerçekten yüklenmiş olup olmadığını doğrulayan sağlık kontrolü
* `OpenAIClient.get_health()` ile yedek servis kullanılabilirliği kontrolü
* `generate_stream()` ile hem Ollama hem OpenAI tarafında akış tabanlı üretim desteği
* `json_mode=True` ile yapılandırılmış çıktı zorlaması ve `LLMService._validate_json()` ile katı JSON doğrulaması

### 8.3 Orkestrasyonun Güncel Konumu

LLM tabanı aktif ve kullanılabilir durumdadır; ancak mevcut repo çalışma yüzeyinde RAG sorgu planlamasının önemli kısmı halen kural tabanlı yürür. Yani:

* LLM katmanı hazırdır
* departman yönlendirme prompt'u mevcuttur
* fakat aktif retrieval seçiminde yalnızca LLM'e bağımlı bir routing zorunlu değildir

Bu tercih, sistemin yerel çalışabilirliğini ve deterministik davranışını korumak için yapılmıştır.

### 8.4 Belgelenen Açık Noktalar

* Health check, fallback ve streaming akışları kodda mevcuttur ve bu dokümanda artık açıkça belirtilmiştir.
* Departman yönlendirme prompt'u artık merkezi departman kaydından üretilebilir durumdadır; yeni departman eklerken prompt ve çekirdek sözleşme uyumsuzluğu riski azaltılmıştır.
