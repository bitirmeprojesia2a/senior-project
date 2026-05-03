# Technical Backlog

Bu dosya, halen acik olan teknik iyilestirmeleri toplar. Tamamlanan buyuk refactor ve deployment adimlari burada tekrar "aktif is" gibi listelenmez; yalnizca gercekten acik maddeler tutulur.

## Aktif Sonraki 3 Adim

1. Sistem derin denetim matrisi: `docs/SISTEM_DERIN_DENETIM_PLANI.md` sirasina gore LLM, routing, Slack/auth, A2A, DB/corpus ve deployment hatlarini kod + veri + runtime diagnostik ile tek tek denetlemek.
2. LLM cagri zinciri sadeleştirme: query normalization, routing LLM, retrieval query expansion ve synthesis cagrilarinin gereksiz tekrarlarini, timeout davranisini ve model role cozumlemesini olcmek.
3. Canli Slack/A2A regresyon seti: Slack'te denenmis kritik sorulari otomatik API benchmark veya integration smoke setine almak.

## Strateji Notu

- GPU erisimi operasyonel olarak problemli kalirsa, LLM katmanini self-hosted Ollama'ya mecbur birakmamak.
- `src/llm/openai_client.py` yolunu Groq gibi OpenAI-compatible provider ile calisacak sekilde kullanmak; FastAPI, PostgreSQL, Redis, Chroma ve retrieval servis CPU/GPU ortamindan bagimsiz kalabilir.
- Bu sayede "GPU gerekli tek bilesen LLM inference" varsayimi ayrisir; demo ve teslim akisi icin CPU backend + API LLM kombinasyonu resmi fallback stratejisi olarak korunur.
- Kisa sureli agir testlerde gerekirse RunPod/Vast.ai benzeri GPU ortamlarina gecis ikinci asama opsiyon olarak tutulur.

## Durum Notu

- Azure CPU uzerinde calisan kurulum ve runbook mevcut; kalici servis yonetimi ve HTTPS katmani henuz eklenmedi.
- Conversation memory, role-based model split, announcement/event capability agent'lari, specialist agent servisleri, merkezi retrieval servisi ve Slack A2A akisi aktif kod tabanina dahil.
- Benchmark altyapisi genisledi; bundan sonraki ihtiyac ham sonucu toplamak degil, Slack/API/A2A runtime'lari arasinda tutarli regresyon karsilastirmasi yapmaktir.

## Bugunden Kalan Net Maddeler

- `student_affairs_docs` registry'sinin kok klasorden kontrollu full reindex ile kalici duzeltilmesi; mevcut Chroma sayisi ile registry sayisi farkli gorunuyor.
- A2A HMAC nonce replay cache artik process-local olarak var; coklu replica/production dagitimda bunu Redis tabanli merkezi nonce store'a tasimak gerekiyor.
- `Final sinavlari ne zaman?` gibi genel takvim sorularinda bolum bazli program mi yoksa akademik takvim mi istendigini daha temiz ayiran regresyon seti.
- `sey basvuru ne zaman` gibi belirsiz sorularin eski thread context'ine veya alakasiz eski tarihli RAG parcacigina dusmesini engelleyen ambiguity guard'inin daha fazla test edilmesi.
- `yemekhane ucreti ne kadar?` icin kaynak/veri eksigi. Bu bilgi sisteme alinacaksa structured tablo veya guncel duyuru kaynagi gerekir; RAG uydurma cevap vermemeli.
- `announcement/event` precision backlog'u: `seminer`, `bugunku etkinlik`, `bolum duyurusu` gibi sorgularda uygun bolum/fakulte filtresi ve zaman penceresi daha kontrollu olculmeli.
- Raw veri tarafindaki bozuk Turkce dosya adlarinin ve mevcut indexte gorunen mojibake source adlarinin tam temizligi icin reindex plani.
- `scripts/run_api_profile.sh` ve deployment profillerinin shell-safe `.env` davranisi ile Azure'da tekrar dogrulanmasi; profile dosyalariyla manuel `uvicorn` akisinin ayni sonucu verdiginin teyidi.
- Docker/Slack canli E2E ve 25 soru kalite benchmark'inin son mimari degisikliklerden sonra tekrar calistirilmasi.

## Orta Oncelik

- `src/routing/router.py` ve `src/orchestrators/main.py` uzerindeki karar akislarini daha da inceltmek; LLM'in urettigi `canonical_query`, `primary_intent`, `required_slots` ve `missing_slots` sinyallerinin hangi deterministik guard'lardan gececegi daha net testlenmeli.
- `src/llm/openai_client.py` tarafini `base_url` benzeri OpenAI-compatible provider gecisleri icin daha esnek hale getirmek.
- `src/llm/llm_service.py` icinde provider secimini daha acik hale getirip `Ollama primary -> Groq/OpenAI-compatible primary` gecislerini env bazli yapilandirilabilir hale getirmek.
- Groq benzeri provider'lar icin kucuk bir entegrasyon notu hazirlayip gerekli `.env` degiskenlerini ve model eslestirmelerini belgelemek.
- Groq/OpenAI-compatible geciste `/health`, deployment profilleri ve runbook belgelerini yeni provider secimini acik gosterecek sekilde guncellemek.
- Groq veya baska API provider'a gecildiginde `routing`, `conversation`, `specialist_synthesis` ve `global_synthesis` rollerinin ayni model mi yoksa farkli model/profil mi kullanacaginin netlestirilmesi.
- Retrieval bias katmaninin `transkript`, `burs`, `erasmus`, `yatay gecis`, `staj`, `takvim` gibi yuksek hacimli query aileleri icin ayrik benchmark setleriyle olculmesi.
- `RAG_LLM_QUERY_EXPANSION_ENABLED=true` kullanildiginda retrieval basina ayri LLM cagrisi timeout/latency riski tasiyor; routing/normalization sinyaliyle birlestirme veya varsayilan kapali kullanimi tekrar degerlendirilmeli.
- `_expand_candidate_context` tarafindaki tam-madde birlestirme mantiginin performans ve kapsam acisindan yeniden ele alinmasi; BM25 cache full-scan yerine daha dogrudan bir madde indeksine gecis.
- Dagitim tarafinda tekrarlanabilir bootstrap script'leri ve daha otomatik bir VM ilk kurulum akisi eklemek.
- HTTP benchmark sonuclari, Slack A2A canli denemeleri ve in-process benchmark sonuclarini ayri raporlayip karisik yorumu azaltmak.
- Duyuru ve retrieval verisinin kademeli yeniden indekslenmesi icin daha operasyonel bir komut seti eklemek.

## Dusuk Oncelik

- Best-effort hata bloklarindaki bazi genel `except Exception` kullanimlarini daha spesifik hata tiplerine indirmek.
- Geriye donuk uyumluluk icin tutulan bazi export modullerini sadeletirmek.
- Tekrar eden benchmark/analiz artefaktlarini ileride `docs/archive/benchmarks/` altinda toplamak; faz dokumanlari yerinde korunmalidir.
- Warm-up varsayilanlarini dagitim tipine gore daha akilli hale getirmek.
- Azure disi alternatif ortamlar icin (Colab, Studio Lab, DigitalOcean GPU, Groq-only deployment) kisa bir karar tablosu veya operasyon notu hazirlamak.
