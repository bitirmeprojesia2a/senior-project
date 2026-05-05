# NVIDIA API Model Deneme Notlari

Tarih: 2026-05-03

Bu notlar, NVIDIA hosted OpenAI-compatible API uzerinden proje icin denenmis modellerin hiz ve kullanilabilirlik gozlemlerini ozetler. Testler kisa Turkce bir ogrenci destek sorusu ile, mevcut RAG/A2A sisteminden ayri ham LLM cagrisi olarak yapildi. Slack tarafindaki gercek denemelerde MiniMax kaynakli uzun bekleme, A2A specialist timeout sonrasinda `RAG_FALLBACK:RAG` cevabina dusulmesine neden oldu.

## Denenen Modeller

| Model | Sonuc | Sure | Not |
| --- | --- | ---: | --- |
| `minimaxai/minimax-m2.7` | Timeout | 90 sn+ | `routing`, `specialist_synthesis` ve `global_synthesis` rollerinde 90 sn icinde cevap donmedi. Slack akisi yaklasik 240 sn specialist timeout bekleyip RAG fallback'e dustu. |
| `openai/gpt-oss-120b` | Basarili | 3.06 sn | En hizli cevap veren NVIDIA modeli oldu. Cevap kalitesi Groq yapisina gore yeterli bulunmazsa kullanilmamali. |
| `qwen/qwen3-next-80b-a3b-instruct` | Basarili | 11-25 sn | Cevap verdi ama `gpt-oss-120b` kadar hizli degildi. Ikinci aday olarak degerlendirilebilir. |
| `z-ai/glm-5.1` | Timeout | 45 sn+ | Kisa testte cevap donmedi. |
| `moonshotai/kimi-k2.6` | Timeout | 45 sn+ | Kisa testte cevap donmedi. |

## Karar

Mevcut proje icin Groq tabanli eski yapi hiz ve kalite acisindan daha iyi bulundu. NVIDIA API entegrasyonu kalici yapilmadi; aktif ortam Groq ayarlarina geri alindi.

## Gelecekte Kullanilacaksa

- NVIDIA modelleri once ham API latency testiyle olculmeli.
- Slack gibi gercek zamanli kanallarda 30-60 sn ustu cevap sureleri kullanici deneyimini bozuyor.
- `minimaxai/minimax-m2.7` bu testte uygun gorunmedi.
- NVIDIA tarafinda tekrar denenecekse ilk adaylar `openai/gpt-oss-120b` ve sonra `qwen/qwen3-next-80b-a3b-instruct` olabilir.
