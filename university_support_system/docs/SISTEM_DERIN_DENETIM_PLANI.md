# Sistem Derin Denetim Plani

Bu dosya, sistemin bundan sonraki incelemelerinde "test gecti" seviyesinde kalmamak icin izlenecek standart denetim cercevesini tanimlar. Her modul icin kod yolu, veri yolu, runtime davranisi, sessiz fallback, kalite etkisi ve dogrulama bicimi birlikte incelenir.

## Denetim Standardi

Her alan icin su sorular cevaplanmadan "tamam" denmez:

- Kod yolu: Soru/istek hangi fonksiyonlardan geciyor, hangi karar noktalarinda dallaniyor?
- Veri yolu: Hangi tablo, Chroma koleksiyonu, Redis cache, dosya veya API kullaniliyor?
- Runtime davranisi: Lokal, Docker, A2A, Slack ve benchmark kosumlari ayni mekanizmayi mi kullaniyor?
- Sessiz fallback: Hata olursa sistem neye dusuyor, bu dusus loglaniyor mu, yanlis cevabi maskeleyebilir mi?
- Skor/kalite etkisi: Retrieval, reranker, evidence, confidence ve final synthesis sinyalleri birbirini dogru etkiliyor mu?
- Veri kalitesi: Eksik, duplicate, stale, cok kisa, alakasiz veya yanlis metadata'li veri var mi?
- Konfigurasyon: `.env`, `.env.example`, compose, script ve dokumanlar ayni varsayimlari mi tasiyor?
- Guvenlik/gizlilik: Auth, session, internal A2A imza, personal data ve Slack davranisi dogru sinirlanmis mi?
- Gozlenebilirlik: Log, health, benchmark ve diagnostik ciktisi problemi tespit etmeye yetiyor mu?
- Kanit: Unit test + hedefli diagnostik + gerekiyorsa canli API/Slack smoke ciktisi var mi?

## Ana Denetim Hatlari

### 1. Retrieval / RAG / Index

Kapsam:
- `src/rag/*`
- `src/api/retrieval_service.py`
- Chroma koleksiyonlari
- registry metadata dosyalari
- indexing scriptleri

Kontrol edilecekler:
- Chroma count, registry count ve BM25 document count tutarli mi?
- BM25, semantic retrieval ve reranker sinyalleri final skora dogru tasiniyor mu?
- Query expansion, source bias, education-level penalty ve FAQ trimming yanlis adaylari one cikariyor mu?
- Kisa/duplicate/alakasiz chunk'lar reranker havuzunu kirletiyor mu?
- Remote retrieval ile local fallback ayni semantigi koruyor mu?

Durum:
- BM25 rank-fusion skor kaybi bulundu ve duzeltildi.
- Baslik-only kisa chunk filtreleme eklendi; mevcut index icin full reindex gerekiyor.

### 2. Routing / Query Normalization / Conversation Context

Kapsam:
- `src/routing/*`
- `src/orchestrators/query_normalization.py`
- `src/orchestrators/conversation_context.py`
- Slack follow-up context

Kontrol edilecekler:
- LLM canonical query kritik anlamlari dusuruyor mu?
- Missing slot sinyalleri otomatik clarification'a dogru baglaniyor mu?
- Belirsiz follow-up sorular eski thread context'ine yanlis yapisiyor mu?
- Announcement/event/curriculum/finance capability short-circuit kararlarinda yanlis pozitif var mi?
- Routing LLM ve deterministik guard is bolumu dogru mu?

Onemli riskler:
- `sey basvuru ne zaman` gibi belirsiz sorgular eski konuya veya alakasiz RAG parcasina dusebilir.
- `guncel duyur` gibi bozuk/eksik ifadelerde LLM rewrite ve capability routing uyumu ayrica olculmeli.

### 3. Specialist Agents / Orchestrators / Synthesis

Kapsam:
- `src/agents/*`
- `src/orchestrators/main.py`
- `src/quality/*`
- `src/llm/prompt_templates.py`

Kontrol edilecekler:
- Agent top_k, evidence filtering, direct RAG ve LLM synthesis karar esikleri gercek cevap kalitesini destekliyor mu?
- Multi-department cevaplarda iyi kaynak kotu kaynak tarafindan bastiriliyor mu?
- "Bilgi bulunamadi" cevaplari gercekten veri eksigi mi, yoksa retrieval/filtreleme hatasi mi?
- LLM'e giden context yeterli ve temiz mi?
- Post-processing yabanci kelime, eksik cumle, kaynak disi iddia gibi riskleri yakaliyor mu?

Kalite gate notu:
- Contract/source/value ihlalleri cevap guvenilirligini bozar; bunlar deterministik fallback yoksa bloke edilir.
- Dil/format kalitesi iki seviyeli ele alinacak: acik bozuk token veya yabanci alfabe cevapta kalirsa bloke edilir; daha yumusak supheli Ingilizce/suffix turu pürüzlerde once repair denenir, repair timeout olursa temizlenmis cevap kullaniciya gosterilebilir.
- Bu politika tekrar gozden gecirilecek. Canlida "sentezleyemiyorum" orani artarsa kalite gate sebep kirilimi ve ornek cevaplar uzerinden esikler yeniden kalibre edilecek.

Contract cevap politikasi:
- Contract ihlali fallback'leri soru bazli metin gomerek buyutulmeyecek.
- `contract_answer_policy` once fact/state plani uretir (`verified_total_akts`, `answer_status`, `direct_debt_bar_found` gibi); kullanici metni tek renderer'dan cikar.
- LLM ileride bu plani dogal dile cevirebilir, fakat validator planin zorunlu fact/state sinirlarini korur. Yeni senaryoda oncelik yeni metin eklemek degil, yeni contract state/fact tanimlamaktir.

### 4. Structured DB / Finance / Curriculum / Schedule

Kapsam:
- `src/db/*`
- `src/agents/finance/*`
- curriculum, tuition, schedule, UBYS seed/ingest

Kontrol edilecekler:
- RAG yerine VT cevaplamasi gereken sorular dogru yerde kesiliyor mu?
- Follow-up slot cozumleme yanlis bolum/ogrenci tipi kullanabilir mi?
- Program/fakulte kataloglari statik map mi, DB mi, yoksa normalize edilmis canonical alan mi?
- Schedule parser farkli PDF/tablo tiplerinde dogru calisiyor mu?
- Eski tarihli takvim veya program verisi guncel veri gibi sunuluyor mu?

Durum:
- Schedule parser iki kolonlu tablo sirasi duzeltildi.
- Ogrenci tipi profile/query onceligi finance ucret akisinda duzeltildi.

### 5. Announcement / Event Capability

Kapsam:
- `src/agents/announcement/*`
- `src/agents/event/*`
- sync scriptleri
- duyuru/etkinlik DB tablolari

Kontrol edilecekler:
- Guncel/yaklasan/zaman filtreleri dogru mu?
- Bolum/fakulte filtresi sorgudan veya login profilinden dogru aliniyor mu?
- Duyuru ile akademik bilgi sorulari birbirine karisiyor mu?
- Ek dosya/link ozeti dogru ve yeterli mi?
- Eski duyurular yanlislikla "guncel" diye geliyorsa neden?

Ertelenen tasarim notu:
- Duyuru probe'una paralel bir `department_scoped_document_probe` tasarlanacak.
- Genel policy sorularinda once universite/genel yonetmelik cevabi korunacak; kullanici bolum/program belirtirse veya oturumda guvenilir bolum varsa bolum ozel staj, bitirme, uygulama esasi, form ve ders belgeleri destekleyici kanit olarak aranacak.
- Bolum belgesi merkezi yonetmeligi otomatik ezmeyecek; yalniz "bolum uygulamasi/ek sart" olarak, yuksek guven ve dogru bolum eslesmesi varsa cevaba eklenecek.
- Dusuk guvenli veya baska bolume ait belge cevaba sokulmayacak; telemetry'de aday/elenme sebebiyle izlenecek.

### 6. Slack Runtime / Auth / Personal Data

Kapsam:
- `src/slack/*`
- `src/db/auth.py`
- `src/api/profile_flow.py`
- `src/api/query_flow.py`

Kontrol edilecekler:
- Login/logout/session davranisi Slack thread ve user bazinda dogru mu?
- Kisisel veri sorulari auth olmadan cevaplanmiyor mu?
- Follow-up context logout sonrasi temizleniyor mu?
- A2A Slack ve inprocess Slack ayni cevap semantigini koruyor mu?
- Duplicate Slack cevap uretimi veya orphan bot sureci kalabiliyor mu?

### 7. A2A / Distributed Services / Deployment

Kapsam:
- `src/a2a/*`
- `src/api/a2a_dispatch.py`
- compose dosyalari
- rollout scriptleri

Kontrol edilecekler:
- Servis kimligi, HMAC imza, nonce replay ve allowlist gercekten tum internal endpointlerde calisiyor mu?
- Retrieval-service merkezi calisiyor mu, agentlar kendi modelini gereksiz yukluyor mu?
- Health metadata skip-build ve build senaryolarinda uyumlu mu?
- Docker orphan/old container problemleri tekrar ureyebilir mi?
- Production standardina yaklasmak icin restart policy/log/observability eksikleri neler?

Durum:
- Process-local nonce replay cache eklendi; multi-replica icin Redis nonce store halen acik borc.

### 8. LLM Providers / Model Routing / Cost-Latency

Kapsam:
- `src/llm/*`
- `.env`, `.env.example`
- role-based model ayarlari

Kontrol edilecekler:
- Routing, query normalization, query expansion, specialist synthesis ve global synthesis gereksiz ayri cagrilar yapiyor mu?
- Model role override'lari gercek runtime'da beklendigi gibi cozuluyor mu?
- Timeout olunca sistem hangi fallback'e dusuyor?
- 8B/70B kararlarinin kalite ve sure etkisi benchmarkla ayriliyor mu?
- API key rotation, provider base URL ve error handling guvenilir mi?

Aktif risk:
- `RAG_LLM_QUERY_EXPANSION_ENABLED=true` ise retrieval basina ayri LLM cagrisi latency/cost riski tasir. Routing/normalization LLM sinyaliyle birlestirme tekrar degerlendirilmeli.

Ertelenen deney notu:
- Turkish BGE / FP16 reranker denemesi bu fazin sonuna alindi. Once mevcut
  contract, final-owner, quality gate ve replay stabil hale getirilecek; sonra
  `scripts/compare_reranker_models.py` uzerinden mevcut reranker ile ayni
  fixture setinde A/B kalibrasyon yapilacak. Canli default model yalniz
  precision/latency kazanimi testle gorulurse degisecek.

### 9. Scripts / Tests / Benchmark / Docs

Kapsam:
- `scripts/*`
- `tests/*`
- `docs/*`

Kontrol edilecekler:
- Eski scriptler yanlis varsayimla kullaniciyi bozuyor mu?
- Benchmark ciktisi hangi runtime'i olctugunu acik soyluyor mu?
- Testler mock nedeniyle gercek runtime risklerini kaciriyor mu?
- Dokumanlar eski mimariyi anlatip bugunku sistemi yanlis temsil ediyor mu?

## Oncelik Sirasi

1. LLM query expansion ve routing-normalization cagrilarinin maliyet/timeout/kalite etkisi.
2. Retrieval corpus temizligi ve full reindex planinin guvenli komut seti.
3. Slack auth/logout/follow-up context ve A2A Slack/inprocess Slack farklari.
4. Announcement/event precision ve bolum/zaman filtresi.
5. Finance/curriculum/schedule structured data kapsam ve stale data riski.
6. A2A production hardening ve Redis tabanli nonce store.
