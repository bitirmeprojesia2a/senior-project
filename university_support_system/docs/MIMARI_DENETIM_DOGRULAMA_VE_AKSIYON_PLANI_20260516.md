# Mimari Denetim Dogrulama ve Aksiyon Plani

Tarih: 2026-05-16

Bu dokuman, dis analiz raporundaki iddialarin kod tabaninda yeniden kontrol edilmesiyle hazirlandi. Amac raporu otomatik olarak kabul etmek degil; dogru, kismi, yanlis veya onceligi dusuk bulgulari ayirmak ve mimari refactor planini risk/etki temelli siraya koymaktir.

## 1. Kisa Sonuc

Raporun ana mesaji dogru: sistem guclu bir teknik temele sahip olsa da karar katmani, kalite gate'leri, guvenlik ve deployment alanlarinda production'a gecmeden once ele alinmasi gereken ciddi riskler var.

## Hızlı Fix Paketi Sonrasi Ertelenen Notlar

Bu bolum, 2026-05-16 hizli P0/P1 fix turundan sonra bilincli olarak ertelenen buyuk isleri kayit altinda tutar. Bu isler dogru yon, fakat bu turda refactor ve migration kapsam disi birakildi.

1. Guvenlik migration paketi: OTP hash formatinin HMAC/PBKDF2'ye tasinmasi, session token'in HTTP-only cookie modeline alinmasi, auth endpoint rate limit'i ve nonce store'un Redis'e alinmasi birlikte ele alinmali. Tek satirlik fix gibi gorunse de migration/backward compatibility gerektirir.
2. Mimari refactor paketi: MainOrchestrator, conversation context ve karar katmani bolme isi davranis riski yuksek oldugu icin bu hizli pakete alinmadi. Once golden trace ve smoke setleri genisletilmeli, sonra micro-orchestrator/pipeline ayrimi yapilmali.
3. Deployment/CI sertlestirme paketi: Docker secret/root user/resource limit duzeltmeleri ve CI'da full test/coverage/lint/typecheck gate'leri bir sonraki stabilizasyon fazina not edildi. Bunlar runtime cevabi hemen degistirmez, ama production guvenligi ve regresyon yakalama icin kritik.

En onemli dogrulanan riskler:

- MainOrchestrator tek basina cache, routing, dispatch, synthesis, quality, telemetry ve decision tracing islerini tasiyor.
- Router yorumlarda LLM-first gibi anlatiliyor, fakat rule decision her istekte hesaplanip fallback/override olarak merkezi rol oynuyor.
- Judge parse edilemeyen JSON'u `approved=True` kabul ediyor; bu kalite gate'inin fail-open calismasi demek.
- `coverage.uncovered` hatali alan erisimi; dogru alan `missing_intents`.
- OTP hash salt/secret kullanmadan SHA-256 ile saklaniyor.
- Auth endpoint'lerinde gercek endpoint-level rate limiting yok.
- Session token response body ve request body icinden tasiniyor; HTTP-only cookie yok.
- A2A timeout'lari retry dongusunu atlayabiliyor.
- CI sadece hedefli 6 test dosyasini calistiriyor; coverage/lint/typecheck CI gate'i yok.
- Docker root user ile calisiyor; compose dosyalarinda default secret/parola var.
- 13 compose dosyasi gercek bir maintenance riski olusturuyor.

Keskinlestirilmesi gereken iddialar:

- "A2A signature secret None ise fail-open" iddiasi tam dogru degil. Require signature aciksa endpoint reddediyor; asil risk imzanin default kapali olmasi ve secret'in internal API key'e dusmesi.
- "CI sadece 6 test calistiriyor" ifadesi yanlis; 6 test dosyasi calistiriyor, bu dosyalarda cok sayida test var. Sorun yine de buyuk: test envanterinin cogu CI disinda.
- `answer_coverage` combined text kullanimi dogru ama su an daha cok diagnostic/shadow sinyalini yaniltma riski tasiyor; dogrudan her cevabi bozuyor diye siniflanmamali.
- `evidence_selector` fenced JSON konusunda kirilgan ama fallback deterministic listeye donuyor; bu P0 degil.
- Reranker failure siralamasi sadece ham listeyle cagrilirsa tehlikeli; retriever akisinda adaylar genelde onceden skorla siralanmis.

## 2. P0: Hemen Duzeltilecek Runtime/Kalite Bug'lari

### P0.1 Duplicate `department` key

Dosya: `src/agents/base.py`

Durum: Dogru. Evidence packet icinde `department` iki kez yaziliyor.

Neden onemli: Python dict son key'i korur; bug bugun ayni degeri yazdigi icin semptom sessiz, fakat ileride ilk alana farkli anlam yuklenirse veri kaybi olur. Ayrica duplicate-key lint kurali olmadigini gosterir.

Plan:

1. Ikinci duplicate key'i kaldir.
2. Ruff/flake8 icin duplicate dict key kuralini CI'a ekle.
3. Evidence packet snapshot testine duplicate-key regression testi ekle.

### P0.2 Announcement mojibake

Dosya: `src/agents/announcement/agent.py`

Durum: Dogru. `_normalize_optional_text` icinde `"hayÄ±r"` var; dogru deger `"hayır"` olmali.

Neden onemli: Turkce false marker'i eslesmez. Bu ozellikle metadata'da kullanici "hayır" benzeri input verdiginde opsiyonel alanin yanlis normalize edilmesine yol acar.

Plan:

1. `"hayÄ±r"` degerini `"hayır"` ile degistir.
2. `hayir`, `hayır`, `false`, `0`, `no` icin unit test ekle.
3. Kaynak dosyalarda mojibake taramasi yapan hafif CI script'i ekle.

### P0.3 Judge parse failure fail-open

Dosya: `src/quality/judge.py`

Durum: Dogru. JSON parse edilemezse `JudgeResult(approved=True, action="accept")` donuyor.

Neden onemli: Judge'in gorevi riskli cevabi durdurmak. Parse hatasinda onay vermek, kalite katmaninin en kotu anda devreden cikmasidir. LLM "```json" veya aciklamali cevap urettiginde hatali cevap otomatik kabul edilebilir.

Plan:

1. Parse failure icin `approved=False`, `action="rewrite_only"` veya "judge_unavailable" status'u don.
2. MainOrchestrator'da judge parse failure ve judge call failure'i ayri telemetry event olarak kaydet.
3. Unit test: malformed JSON, prose+JSON, empty response.
4. Runtime politikasi: judge unavailable ise cevabi tamamen bloklamak yerine sadece yuksek riskli durumlarda safe fallback mesaji kullan.

### P0.4 Intent coverage alan hatasi

Dosya: `src/orchestrators/main.py`

Durum: Dogru. `coverage.uncovered` okunuyor; `IntentCoverageResult` alan adi `missing_intents`.

Neden onemli: AttributeError broad except ile yutuluyor. Sonuc olarak judge'a eksik intent listesi gecmiyor; cok niyetli sorularda "cevap bir parcayi atlamis" sinyali kayboluyor.

Plan:

1. `coverage.uncovered` -> `coverage.missing_intents`.
2. Broad `except: pass` yerine `except Exception as exc: logger.warning(...)`.
3. Multi-intent query icin judge context testi ekle.

### P0.5 Shared internal dispatch context

Dosya: `src/api/query_flow.py`

Durum: Kismi ama onemli. Public `/query` UUID uretiyor; internal A2A dispatch context yoksa `"api-a2a-context"` sabitini kullaniyor.

Neden onemli: Context id conversation/profile/trace baglaminda kullanilirsa farkli internal istekler ayni context'e yazabilir. Bu veri karismasi ve debug trace karismasi riskidir.

Plan:

1. Sabit fallback yerine `str(uuid4())` kullan.
2. Internal caller context vermiyorsa telemetry'de `generated_context_id=true` isaretle.
3. Regression test: context_id bos iki dispatch farkli context uretmeli.

## 3. P1: Guvenlik Sertlestirme

### P1.1 OTP hash

Dosyalar: `src/db/auth_utils.py`, `src/db/auth.py`, `src/db/auth_models.py`

Durum: Dogru. OTP `sha256(code)` ile saltsiz saklaniyor.

Neden onemli: 6 haneli OTP alani 1 milyon olasilik. DB dump veya log sizintisinda hash'ler cok hizli brute-force edilir.

Plan:

1. En az HMAC-SHA256 kullan: `HMAC(server_secret, otp_code + session_specific_salt)`.
2. Modelde `code_salt` veya `hash_version` alani ekle.
3. Eski OTP'ler TTL kisa oldugu icin migration sade olabilir: eski aktif OTP'leri invalid say.
4. Verify path'te constant-time compare korunmali.

### P1.2 Rate limiting

Dosya: `src/api/main.py`

Durum: Kismi. Ogrenci bazli OTP cooldown var ama IP/user endpoint-level limiter yok.

Neden onemli: OTP spam, student number enumeration ve LLM quota exhaustion riskleri devam eder.

Plan:

1. Redis tabanli sliding-window limiter ekle.
2. `/auth/request-otp`: IP + student_number + slack_user_id boyutlarinda limit.
3. `/auth/verify-otp`: IP + student_number boyutlarinda limit.
4. `/query`: IP/context/user bazli daha genis quota.
5. Limit asiminda genel hata mesaji don; ayrinti logda kalsin.

### P1.3 Session token tasima modeli

Dosyalar: `src/api/main.py`, `src/db/schemas.py`

Durum: Dogru. Session token body'de donuyor ve body'den aliniyor; HTTP-only cookie yok.

Neden onemli: Browser tabanli kullanimda XSS token'i okuyabilir. Slack/API senaryosunda body token pratik olabilir ama web client icin guvenli varsayilamaz.

Plan:

1. Web/API ayrimi yap: browser icin HTTP-only, Secure, SameSite=Strict cookie; internal/Slack icin Authorization header.
2. Response body token'i compatibility icin gecici tut ama deprecated isaretle.
3. Logout cookie temizlemeli ve DB session invalidate etmeli.

### P1.4 A2A replay cache ve imza politikasi

Dosyalar: `src/a2a/service_identity.py`, `src/core/config.py`, `src/api/a2a_dispatch.py`

Durum: Replay cache process-local dogru. Fail-open iddiasi kismi/yanlis.

Neden onemli: Multi-worker/multi-replica deployment'ta ayni nonce baska process'te tekrar kabul edilebilir. Imza default kapaliysa HMAC korumasi operator fark etmeden devre disi kalabilir.

Plan:

1. Nonce store'u Redis'e tasi.
2. Production profile'da `A2A_REQUIRE_REQUEST_SIGNATURE=true` zorunlu olsun.
3. `request_signature_secret or internal_api_key` fallback'ini production'da reddet; ayri secret sart.
4. Body hash'i Python object serialization yerine wire bytes uzerinden hesapla.

### P1.5 Deployment guvenligi

Dosyalar: `Dockerfile`, `docker-compose*.yml`

Durum: Dogru.

Neden onemli: Root container, default DB password, host'a acik Redis/Chroma ve hardcoded workflow secret'lari savunmada kolay elestirilir.

Plan:

1. Dockerfile'a non-root `appuser` ekle.
2. Default secret/parolalari bos yap; operator set etmeden container fail etmeli.
3. Redis/Chroma host port exposure'i local profile disinda kapat.
4. Compose health/resource limits ekle.
5. GitHub Actions secret'larini `${{ secrets.* }}` ile kullan.

## 4. P2: Karar Katmani ve Orchestrator Mimari Refactor

### P2.1 MainOrchestrator'i bol

Durum: Dogru. `MainOrchestrator` 3600+ satir; `handle_query` tek basina cok genis bir is akisi tasiyor.

Neden onemli: Bug analizinde "hangi katman karar verdi?" sorusu cevaplanamiyor. Cache, routing, dispatch ve quality ayni method icinde oldugu icin testler buyuk fixture/mock istiyor.

Onerilen tasarim: Pipeline pattern.

Asamalar:

1. `RequestContextBuilder`: auth/profile/context/standalone query.
2. `CacheStage`: exact/semantic/cache bypass kararlarini verir.
3. `RoutingStage`: router result + override diagnostics + decision contract.
4. `CapabilityStage`: deterministic capability plan/execution.
5. `DispatchStage`: department/specialist/A2A dispatch.
6. `SynthesisStage`: single/multi department synthesis.
7. `QualityStage`: evidence validation, coverage, judge, final filter.
8. `ResponseStage`: API/Slack-safe response formatting.

Gecis stratejisi:

1. Once mevcut `handle_query` icindeki bloklari private methodlara degil, stage class'lara tasiyacak adapter yaz.
2. Her stage `QueryPipelineContext` dataclass alir ve dondurur.
3. Ilk PR davranis degistirmeden telemetry parity testi ekler.
4. Sonraki PR'larda stage unit testleri ile eski mock yuku azaltir.

### P2.2 Routing override shadow mode

Durum: Dogru/kismi. Kod LLM-first diye belgelenmis ama rule decision her zaman hesaplanir. `_apply_routing_overrides(..., llm_primary=True)` korumasi var fakat cagri yok.

Neden onemli: LLM dogru karar verse bile debug mental modeli bozuluyor. Rule fallback ne zaman ana karar oldu, override ne zaman devreye girdi, hangi marker etkili oldu net degil.

Plan:

1. Router sonucuna `decision_source` ekle: `llm`, `rule_fallback`, `authoritative_override`, `conversation_hint`, `capability_shortcut`.
2. Authoritative override'lari kategoriye ayir: safety, structured-data, legacy-hotfix, ambiguity.
3. Legacy-hotfix override'lari shadow mode'a al: karar degistirmesin, sadece "ne derdi" telemetry yazsin.
4. `_apply_routing_overrides(..., llm_primary=True)` gercek LLM path'te kullanilsin.
5. Golden trace setiyle "override kaldirilinca ne bozuluyor?" olculsun.

### P2.3 Conversation context sadeleme

Durum: Dogru. Dosya 3000+ satir, cok sayida marker ve branch var.

Neden onemli: Follow-up rewrite hem pahali hem de "LLM'e sor ama 8 heuristic ile reddet" modeline kaymis. Bu regresyon riskini ve edge-case sayisini artiriyor.

Plan:

1. Context classification, query rewrite, topic inference, profile persistence, stale-state policy ve diagnostics ayrilsin.
2. Ilk refactor: sadece saf fonksiyonlari `conversation/heuristics.py` altina tasima.
3. Ikinci refactor: `ConversationDecision` typed object uret.
4. Uzun vadede LLM-first veya small-classifier follow-up tespiti tez karsilastirmasi olarak denenebilir.

## 5. P3: RAG ve Quality Iyilestirmeleri

### P3.1 Parent-child chunking

Durum: Raporun bu onerisi degerli.

Neden onemli: Mevcut chunker FAQ/MADDE/BOLUM varyantlarinda kirilgan. Kucuk chunk retrieval precision'i artirirken synthesis icin baglam yetersiz kalabilir.

Plan:

1. Child chunk: 256-512 karakter.
2. Parent chunk: 1500-2500 karakter veya madde/FAQ answer blogu.
3. Retrieval child skoruyla yapilir, synthesis parent context alir.
4. Eski index ile A/B benchmark: key fact coverage, source precision, latency.

### P3.2 Chunker regex genisletme

Durum: Dogru.

Plan:

1. MADDE regex: `MADDE 5`, `MADDE 5.`, `MADDE-5`, `Madde 5 -` varyantlari.
2. BOLUM regex: ASCII Turkish, Roman numeral, numeric section varyantlari.
3. FAQ regex: 120 karakter limitini kaldir veya 240'a cek; 2 soru varsa da split edebilsin.
4. Unit test fixture'lari gercek PDF text ciktilarindan olustur.

### P3.3 Retrieval fallback threshold

Durum: Dogru/kismi. Fallback collection sadece primary hic aday yoksa calisiyor.

Neden onemli: Primary aday var ama skor dusuk/off-topic ise fallback denenmiyor. Bu "yanlis ama bos olmayan" retrieval'i final cevaba tasir.

Plan:

1. Fallback trigger'i `not candidates` yerine `top_score < threshold` veya `evidence_coverage_low` yap.
2. Source-owner policy ile fallback'in hangi collection'dan gelecegi kaydedilsin.
3. Golden trace: akademik takvim, kayit, ucret, duyuru blocked query'leri.

### P3.4 Evidence/coverage/judge semantigi

Durum: Bazi bulgular dogru ama oncelik farkli.

Plan:

1. `answer_coverage`: answer-only ve evidence-only marker'lari ayri raporla.
2. `evidence_selector`: fenced JSON + prose icinden JSON extraction ekle.
3. `insufficient_evidence=True` durumunda bos liste yerine "blocked synthesis" status'u uret; sentez katmani bunu bilsin.
4. Judge prompt ve truncate limitleri contract metadata kaybetmeyecek sekilde yeniden duzenlensin.

## 6. P4: A2A, LLM Service ve Performans

### P4.1 HTTP client pooling

Durum: Dogru. A2A transport ve OpenAI-compatible client her request'te `httpx.AsyncClient` aciyor.

Neden onemli: TLS/connection setup latency ve kaynak tuketimi artar.

Plan:

1. App lifespan'da shared AsyncClient olustur.
2. Transport siniflari client'i dependency olarak alsin.
3. Testlerde mock transport veya injected client kullanilsin.

### P4.2 Timeout retry ve circuit breaker

Durum: A2A icin dogru/kismi. Timeout retry loop'u atlayabiliyor; backoff linear ve jitter yok.

Plan:

1. Timeout'u retryable error olarak ele al.
2. Exponential backoff + jitter ekle.
3. Circuit breaker'a HALF_OPEN state ekle.
4. `_circuit_state` class-level dict icin asyncio lock veya process-wide Redis state dusun.

### P4.3 Cache sinirlari

Durum: Dogru. BM25 resource cache ve query cache max-size konusunda zayif.

Plan:

1. BM25 document/retriever cache icin LRU veya collection-count limit.
2. Query cache icin TTL + max entries.
3. Cache size telemetry threshold alarmi.
4. Request coalescing: ayni cache key icin ayni anda gelen LLM/retrieval isteklerini tek coroutine'e indir.

## 7. P5: Test ve CI

Durum: Raporun ana iddiasi dogru. CI 6 test dosyasi calistiriyor; coverage/lint/typecheck CI'da yok.

Plan:

1. CI job 1: `ruff` veya mevcut flake8/isort.
2. CI job 2: `mypy src/ --ignore-missing-imports` baslangicta non-blocking olabilir.
3. CI job 3: tum unit testleri.
4. CI job 4: integration smoke.
5. Coverage threshold baslangic %50, sonra %70.
6. `tests/e2e` icin minimum senaryolar:
   - Public query happy path.
   - OTP auth flow.
   - Follow-up rewrite + department routing.
   - A2A timeout fallback.
7. `tests/security` icin minimum senaryolar:
   - OTP rate limit.
   - Replay nonce.
   - Missing signature.
   - Cookie/session behavior.

## 8. P6: Veri Modeli ve Deployment Sadelestirme

### P6.1 Monetary Float -> Numeric

Durum: Dogru. Finance modellerinde para alanlari `Float`.

Neden onemli: Finansal tutarlar binary float ile kucuk yuvarlama hatalari uretebilir.

Plan:

1. `Numeric(12, 2)` veya ihtiyaca gore precision.
2. Migration + data cast.
3. Format utility Decimal kabul etmeli.

### P6.2 Unique constraint eksikleri

Durum: Dogru/kismi.

Plan:

1. `Installment`: `(tuition_id, installment_number)` unique.
2. `StudentCourse`: `(student_id, course_id, semester)` unique.
3. `CoursePrerequisite`: `prerequisite_group` primary key'e dahil edilmeli mi is kuraliyla netlestir; ayni prerequisite farkli gruplarda tutulacaksa mevcut PK bunu engeller.

### P6.3 Compose profiles

Durum: Dogru. 13 compose file var.

Plan:

1. Tek `docker-compose.yml` + profiles: `infra`, `api`, `a2a`, `slack`, `gpu`, `specialists`.
2. Ortak env anchor'lari.
3. Secret defaultlari bos.
4. Local/demo/prod ayrimi env dosyalariyla yapilsin.

## 9. Alternatif Mimari Onerilerinin Degerlendirmesi

Uygulanmasi en mantikli olanlar:

- Pipeline/Micro-orchestrator: En yuksek bakim ve test getirisi.
- Parent-child chunking: RAG kalite artisi icin makul maliyet.
- Function calling veya Pydantic structured output: Planner/judge JSON parse kirilganligini azaltir.
- Request coalescing: Dusuk maliyetli performans kazanimi.
- RAGAS offline evaluation: Tez icin guclu olcum bolumu.
- Single compose + profiles: Deployment karmasasini hizli azaltir.

Simdilik uygulanmamasi gerekenler:

- Full event-driven architecture: Request-response UX icin fazla agir.
- gRPC/protobuf A2A: Bu olcekte debug ve build maliyeti getirir.
- Kubernetes/service mesh: Bitirme projesi kapsami icin fazla operasyonel yuk.
- CrewAI/AutoGen gibi framework'e gecis: Mevcut orchestrator zaten multi-agent semantigi kurmus; framework migration'i asil sorunu cozmeyebilir.
- Pure LLM routing: Rule guard'lar tamamen kalkarsa deterministik structured-data ve safety sinyalleri kaybolur.

Tez/yenilik icin opsiyonel ama degerli:

- Semantic similarity cache.
- Multi-stage routing coarse-to-fine benchmark.
- Graph RAG sadece structured curriculum/policy relation'lari icin.
- pgvector migration: infra sadeletir ama re-index ve benchmark gerektirir.

## 10. Onerilen Uygulama Sirası

### Faz 0: Davranis degistirmeyen guardrails

Sure: 1-2 gun

- Duplicate key, mojibake, `missing_intents`, judge parse default fix.
- Regression testleri.
- Decision trace'e `decision_source` alanlari.

### Faz 1: Guvenlik minimumu

Sure: 3-5 gun

- OTP HMAC/hash version.
- Auth rate limiting.
- A2A production signature policy.
- Docker non-root ve default secret cleanup.

### Faz 2: CI kalite kapisi

Sure: 2-4 gun

- Tum unit testleri CI.
- Coverage report.
- Lint/typecheck en azindan non-blocking baslasin.

### Faz 3: Routing observability ve override sadeleme

Sure: 1 hafta

- Override taxonomy.
- Shadow mode.
- Golden trace karsilastirmasi.
- Gereksiz override silme.

### Faz 4: Orchestrator pipeline

Sure: 2-4 hafta

- Stage context dataclass.
- Cache/Routing/Dispatch/Synthesis/Quality stage ayrimi.
- Mevcut davranis parity testleri.

### Faz 5: RAG kalite

Sure: 2-3 hafta

- Chunker regex fixleri.
- Parent-child chunking A/B.
- Fallback threshold.
- Offline RAGAS/key-fact benchmark.

### Faz 6: Performans ve deployment

Sure: 1-2 hafta

- AsyncClient pooling.
- Backoff+jitter+half-open.
- LRU cache.
- Compose profiles.

## 11. Risk Azaltma Prensibi

Bu sistemde asil risk tek bir bug degil; ayni soruya birden fazla katmanin karar vermesi ve karar kaynaginin belirsiz kalmasi. Bu yuzden buyuk refactor'a baslamadan once her query icin su alanlarin trace edilmesi kritik:

- `original_query`
- `effective_query`
- `conversation_rewrite_decision`
- `router_llm_decision`
- `rule_decision`
- `override_decision`
- `final_departments`
- `capability_plan`
- `dispatch_targets`
- `synthesis_owner`
- `quality_gate_results`
- `final_answer_source`

Bu trace olmadan mimari sadeleme kör ucar; trace ile hangi legacy kuralin gercekten degerli, hangisinin sadece eski regresyon korkusundan kaldigi olculebilir.
