# Rapora Eklenecek Teknik Deneme Notlari

Tarih: 2026-05-03 / 2026-05-05

Bu dosya, bitirme raporuna daha sonra eklenecek model, API ve RAG iyilestirme notlarini tek yerde toplar. Ayrintili NVIDIA API denemeleri icin `docs/NVIDIA_API_MODEL_DENEME_NOTLARI.md`, BGE skor dagilimi icin `docs/archive/benchmarks/bge_fp16_reranker_score_analysis.md` dosyalari kaynak alinabilir.

## NVIDIA Hosted API Denemeleri

NVIDIA hosted OpenAI-compatible API, projeye alternatif LLM saglayicisi olarak denenmistir. Amac, Groq tabanli mevcut yapinin hiz ve kalite dengesiyle karsilastirma yapmaktir.

| Model | Gozlem | Sure | Karar |
| --- | --- | ---: | --- |
| `minimaxai/minimax-m2.7` | Slack/A2A akisinda cok yavas kaldi; specialist timeout sonrasi RAG fallback'e dusme gozlemlendi. | 90 sn+ ham cagri, Slack'te yaklasik 240 sn | Uygun degil |
| `openai/gpt-oss-120b` | NVIDIA tarafinda en hizli cevap veren aday oldu. | Yaklasik 3 sn | Alternatif olarak not edildi |
| `qwen/qwen3-next-80b-a3b-instruct` | Cevap verdi fakat gecikme daha yuksekti. | 11-25 sn | Ikinci aday |
| `z-ai/glm-5.1` | Kisa testte cevap donmedi. | 45 sn+ | Uygun degil |
| `moonshotai/kimi-k2.6` | Kisa testte cevap donmedi. | 45 sn+ | Uygun degil |

Sonuc olarak Groq yapisi hiz ve cevap kalitesi acisindan daha uygun bulunmus, NVIDIA entegrasyonu geri alinmistir. NVIDIA tekrar degerlendirilecekse once ham latency testi, sonra Slack/A2A gercek akis testi yapilmalidir.

## Reranker Model Denemeleri

RAG tarafinda ilk kurulumda hiz kaygisi nedeniyle kucuk reranker tercih edilmisti. API tabanli LLM'e gecisle cevap uretim suresi rahatladigi icin daha kaliteli reranker adaylari denenmistir.

| Model | Neden Denendi | Gozlem | Karar |
| --- | --- | --- | --- |
| `nreimers/mmarco-mMiniLMv2-L6-H384-v1` | Eski hizli baseline. Turkce dahil cok dilli MS MARCO turevi, CPU'da makul sure. | Hizliydi, fakat zor Turkce mevzuat/yonerge sorularinda belge secimi sinirli kalabiliyordu. | Geri donus baseline'i olarak korunmali |
| `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` | L6'ya gore daha buyuk ve potansiyel olarak daha kaliteli cok dilli cross-encoder. | Hiz/kalite kazanci beklenen kadar belirgin olmadi; model adinin env'de kalmasi karisiklik yaratti. | Ana aday degil |
| `seroe/bge-reranker-v2-m3-turkish-triplet` | Turkce odakli BGE turevi oldugu icin denendi. | Beklenen kalite farki belirginlesmedi; proje sorgularinda istikrarli ustunluk gorulmedi. | Ana aday degil |
| `BAAI/bge-reranker-v2-m3` | Cok dilli, daha guclu BGE reranker; Turkce destekli ve kalite potansiyeli yuksek. | CUDA + fp16 ile hiz kabul edilebilir seviyeye indi. Skor dagilimi icin kalibrasyon analizi yapildi. | Aktif aday |

## BGE Reranker Kalibrasyon Notu

`BAAI/bge-reranker-v2-m3` icin 40 soru / 400 aday uzerinden skor dagilimi alinmistir.

- Ham skor median: `0.0652`
- Ham top-1 median: `0.6799`
- Onerilen sigmoid formul: `sigmoid((score - 0.0652) / 0.5000)`
- Onerilen direct-RAG esigi: `0.635`
- Onerilen min-source esigi: `0.472`

Mevcut yorum: BGE reranker icin fp16 performansi umut verici; ancak cevap kalitesindeki sorunlarin tamami reranker kaynakli degildir. Bazi durumlarda dogru belge ilk siralara gelse bile cevapta ilgili chunk/fact kullanilmamaktadir. Bu nedenle sonraki iyilestirme odagi sadece reranker degil, evidence selection, chunk genisletme ve final synthesis/judge akisi olmalidir.

## Sonraki RAG Inceleme Basliklari

- Reranker skip su an yalnizca aday sayisi `top_k` veya daha azsa devreye giriyor; agresif bir skip davranisi kalmamis gorunuyor.
- Score penalty/boost sistemi BGE sonrasi tekrar olculmeli. Ozellikle `CAP_OFF_TOPIC_PENALTY` gibi sert cezalar dogru belgeyi asagi itebilir. Bunun icin davranisi degistirmeden asagidaki `.env` bayraklari eklendi:
  - `RAG_SOURCE_RELEVANCE_PENALTY_ENABLED`
  - `RAG_QUERY_PROFILE_SOURCE_BIAS_ENABLED`
  - `RAG_EDUCATION_LEVEL_PENALTY_ENABLED`
  - `RAG_FINANCE_SOURCE_PENALTY_ENABLED`
  - `RAG_STUDENT_AFFAIRS_FAQ_BIAS_ENABLED`
  Varsayilanlar `true`; benchmark sirasinda tek tek `false` yapilarak BGE reranker'in tek basina siralama kalitesi olculebilir.
- 2026-05-04 kisa canli retrieval kiyasinda 6 temsilî sorgu denenmistir. CAP/onlisans ve yaz okulu kapasitesi sorgularinda acik/kapali sonuc ayni kalmistir. Ogrenci belgesi sorgusunda `student_affairs_faq_bias` acikken top-5 tamamen `sik_sorulan_sorular.txt` olarak kalmis, kapaliyken yatay gecis/kayit ilani belgeleri top-5'e girmistir. Sinav notuna itiraz sorgusunda profil bias acikken FAQ + yonetmelik dengesi daha iyi korunmus, kapaliyken FAQ tamamen top-5 disina dusmustur. Akademik takvim sorgusunda source relevance acikken takvim kaynaklari skorda net ayrismis, kapaliyken yine top-2'de kalmistir ama FAQ ile skor farki azalmistir. Bu kisa teste gore ceza/boost sistemini tamamen kaldirmak yerine bayrakli tutup kapsamli benchmark ile parca parca olcmek daha guvenlidir.
- 2026-05-04 ikinci canli retrieval kiyasinda 25 temsilî sorgu ile tum ceza/boost bayraklari acik ve kapali olarak karsilastirilmistir. Normalize kaynak eslesmesiyle acik durumda top-1 isabet `21/25`, top-3/top-5 isabet `23/25`; kapali durumda top-1 isabet `19/25`, top-3/top-5 isabet `22/25` olmustur. Acik durumda `kayit sildirme`, `onlisans CAP` ve `harc odemesi` sorgularinda daha iyi siralama gorulmustur. Kapali durumda yalnizca `katki payi hangi durumda odenir?` sorgusunda top-1 daha iyi gorunmustur. Bu sonuc ceza/boost sistemini tamamen kaldirmak yerine bayrakli koruyup finans tarafindaki `harc odemesi` / `katki payi` ayrimini ayrica kalibre etmenin daha dogru oldugunu gosterir.
- 2026-05-05 genisletilmis retrieval bias kiyasinda 30 temsili sorgu ile tum ceza/boost bayraklari acik ve kapali olarak tekrar karsilastirilmistir. Rapor: `docs/archive/benchmarks/retrieval_bias_compare_30q_20260505.json`. Top-1 siralama `2/30` sorguda degismis, top-3 kaynak kumesi `12/30` sorguda degismistir. Bu sonuc ceza/boost sinyallerinin BGE reranker sonrasinda hala siralamayi etkiledigini, fakat her sorguda belirleyici olmadigini gosterir. Bu nedenle sistemi tamamen kapatmak yerine bayrakli tutmak ve problemli alt profillerde parca parca kapatip olcmek daha guvenlidir. Bu rapordaki sureler latency benchmark olarak yorumlanmamalidir; ilk sorgularda model/cache isinma etkisi gorulebilir.
- Test notu: Lokal script calistirmalarinda `HF_HOME`, `SENTENCE_TRANSFORMERS_HOME` ve `MODEL_CACHE_HOST_DIR` process ortaminda verilmezse reranker cache bulunamayabiliyor. Dogru benchmark icin cache env'leri acikca set edilmelidir.
- Yaz okulu sinif kapasitesi, CAP/onlisans uygunlugu ve kimlik karti kaybi gibi gercek Slack testleri benchmark setine eklenmeli.
- Belge bulunup cevapta bilgi kullanilmiyorsa sorun reranker degil, context/evidence secimi veya sentez prompt'u tarafindadir.

## Cevap Kalitesi ve Final Sentez Notu

- 2026-05-05 itibariyla kaynakli tek departman cevaplari da final refinement katmanindan gececek sekilde korunmustur; cok departmanli sorularda ise global synthesis tek final cevap uretir.
- Final synthesis prompt'unda dogal Turkce vurgusu guclendirildi. Dinamik prompt ve `MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT` ASCII Turkce yerine dogal Turkce talimatlarla guncellendi.
- Genel QA, uzman ajan, finans ve duyuru cevap promptlari da dogal Turkce talimatlara tasindi. Routing/follow-up gibi karar katmanlarindaki normalize/ASCII marker yapisina bu adimda dokunulmadi.
- Final synthesis katmani `answer_summary` ile `evidence/snippet` veya `extracted_facts` celistiginde somut sayi/kosul iceren evidence bilgisini esas alacak sekilde netlestirildi.
- Judge risk tespiti dogal Turkce cevaplari da kapsayacak sekilde genisletildi: `bulunamadi/bulunamadı`, `harc/harç`, `katki payi/katkı payı`, `odeme/ödeme`, `yonerge/yönerge`, `yonetmelik/yönetmelik` formlari birlikte yakalanir.
- Debug gorunurlugu bilincli olarak kapatilmadi; gelistirme/test asamasinda uretim modu ve kaynak ozeti takip edilmeye devam edecek.

## Groq Llama 3.3 ve Gemini 3 Flash Karsilastirma Notu

Tarih: 2026-05-05 / 2026-05-06

Iki model ayni Slack senaryo zincirinde denenmistir: CAP basvuru uygunlugu, harc borcu varken basvuru, basvuru tarihi follow-up'i, CAP duzeltmesi, onlisans/lisans AKTS, program ozelinde AKTS, ders programi ve fizik ogretmenligi ucreti. Sureler `query_logs.response_time_ms` alanindan alinmistir. Gemini 3 Flash icin `3833-3843`, Groq icin `3844-3854` query log araliklari kullanilmistir.

| Model / Provider | Ortalama Sure | Medyan | Min-Max | Kalite Gozlemi | Karar |
| --- | ---: | ---: | ---: | --- | --- |
| `gemini-3-flash-preview` / Google AI | 25.37 sn | 26.23 sn | 9.23-41.44 sn | Ilk CAP cevabi ve bazi sentezler daha akici; fizik ogretmenligi ucreti follow-up'inda dogru fakulteye ulasabildi. Ancak harc borcu turundan sonra baglam finans konusuna kaydi; "Basvuru tarihleri ne peki?" sorusunu ogrenim ucreti tarihleri gibi yorumladi. "capi sordum" duzeltmesinde kismen toparladi ama kaynak ve ifade kalitesi karisik kaldi. Bazi cevaplarda yabanci/bozuk token goruldu. | Kalite potansiyeli var ama canli Slack icin yavas. Kritik kalite profili veya batch testlerde aday olarak tutulabilir. |
| `llama-3.3-70b-versatile` / Groq | 4.23 sn | 4.56 sn | 2.45-6.75 sn | Cok daha hizli. "capi sordum" duzeltmesinden sonra CAP basvuru tarihlerini Gemini 3'e gore daha net toparladi. Lisans AKTS cevabi daha kullanisliydi. Ancak ilk "Basvuru tarihleri ne peki?" sorusunda CAP baglamini kullanmak yerine clarification istedi; onlisans AKTS sorusunda onceki CAP tarih baglami sizdi; fizik ogretmenligi ucreti akisi bir testte onceki Bilgisayar Muhendisligi baglamiyla karisti. | Varsayilan canli kullanim icin daha uygun. Asil sorun modelden cok follow-up/routing state ve VT clarification baglam yonetimi oldugu icin optimizasyon Groq uzerinde devam etmeli. |

Sonuc: Model degistirmek tek basina follow-up sorununu cozmemektedir. Gemini 3 bazi cevaplarda daha iyi metin kalitesi verse de 6 kata yakin daha yavas kalmistir. Canli Slack deneyimi icin Groq + Llama 3.3 daha dengeli gorunmektedir. Odak, model degisiminden once su mimari noktalarda kalmalidir:

- Follow-up state'inde son cevap konusunu degil, kullanicinin duzeltme/ana niyet zincirini daha guvenli takip etmek.
- Finance/tuition clarification akisini onceki "program/birim" ve "asli soru" ile baglamak; kisa "Turk" cevaplarini yalnizca aktif ucret slot'u varsa answer fragment saymak.
- "Basvuru tarihleri ne peki?" gibi eksik sorularda son finans cevabina degil, daha onceki basvuru nesnesine donmeyi saglayan genel referans cozumleme katmani eklemek.
- Final/judge katmaninda yabanci token ve bozuk Turkce temizligini daha siki yapmak; sadece model secimine birakmamak.
