# Technical Backlog

Bu dosya, halen acik olan teknik iyilestirmeleri toplar. Tamamlanan buyuk refactor ve deployment adimlari burada tekrar "aktif is" gibi listelenmez; yalnizca gercekten acik maddeler tutulur.

## Aktif Sonraki 3 Adim

1. Deployment hardening: `uvicorn` calistirma akisini `systemd`, reverse proxy ve daha guvenli restart prosedurleri ile urunlestirmek.
2. Performance tuning: lokal, Azure CPU ve olasi kisa sureli GPU testlerini ayni benchmark diliyle olcmek.
3. Veri ve path normallestirme: tasinabilirlikte bozulabilen Turkce klasor ve dosya adlari ile encoding davranislarini temizlemek.

Kisa vadeli strateji notu:

- Eger GPU erisimi operasyonel olarak problemli kalirsa, LLM katmanini self-hosted Ollama'ya mecbur birakmamak.
- `src/llm/openai_client.py` yolunu Groq gibi OpenAI-compatible bir provider ile calisacak sekilde kullanmak; FastAPI, PostgreSQL, Redis ve Chroma CPU tarafinda kalmaya devam edebilir.
- Bu sayede "GPU gerekli tek bilesen LLM inference" varsayimi ayrisir; demo ve teslim akisi icin CPU backend + API LLM kombinasyonu resmi fallback stratejisi olarak korunur.
- Sunum gunu veya kisa sureli agir testlerde gerekirse RunPod/Vast.ai benzeri kisa sureli GPU ortamlarina gecis ikinci asama opsiyon olarak tutulur.

Durum notu:

- Azure CPU uzerinde calisan bir kurulum ve runbook artik mevcut; kalici servis yonetimi ve HTTPS katmani henuz eklenmedi.
- Conversation memory, role-based model split ve announcement akisi gibi onceki buyuk maddeler artik aktif kod tabanina dahil.
- Benchmark altyapisi genisledi; bundan sonraki ihtiyac ham sonucu toplamak degil, ortamlar arasi tutarli karsilastirma yapmaktir.

## Bugunden Kalan Net Maddeler

- `transkript`, `ogrenci belgesi`, `diploma eki`, `burs` benzeri sorgularda yeni eklenen FAQ/source bias kurallarinin Azure CPU ortaminda tekrar dogrulanmasi.
- `Erasmus programina nasil basvururum?` benzeri uluslararasi prosedur sorularinda retrieval dogru belgeyi bulsa bile sentez kalitesinin zayif kalmasi; international agent ve ilgili belge parcasi seciminin iyilestirilmesi.
- `student_affairs` tarafinda `MUP`, `staj`, `genel is akisları` gibi belgelerin alakasiz prosedur sorularina sizmasini azaltacak ek source/topic filtreleri.
- Raw veri tarafindaki bozuk Turkce dosya adlarinin ve mevcut indexte gorunen mojibake source adlarinin tam temizligi icin reindex plani.
- `scripts/run_api_profile.sh` ve deployment profillerinin shell-safe `.env` davranisi ile Azure'da tekrar dogrulanmasi; profile dosyalariyla manuel `uvicorn` akisinin ayni sonucu verdiginin teyidi.

## Orta Oncelik

- `src/routing/router.py` ve `src/orchestrators/main.py` uzerindeki karar akislarini daha da inceltmek.
- `src/llm/openai_client.py` tarafini `base_url` benzeri OpenAI-compatible provider gecisleri icin daha esnek hale getirmek.
- `src/llm/llm_service.py` icinde provider secimini daha acik hale getirip `Ollama primary -> Groq/OpenAI-compatible primary` gecislerini env bazli yapilandirilabilir hale getirmek.
- Groq benzeri provider'lar icin kucuk bir entegrasyon notu hazirlayip gerekli `.env` degiskenlerini ve model eslestirmelerini belgelemek.
- Groq/OpenAI-compatible geciste `/health`, deployment profilleri ve runbook belgelerini yeni provider secimini acik gosterecek sekilde guncellemek.
- Groq veya baska API provider'a gecildiginde `routing`, `conversation`, `specialist_synthesis` ve `global_synthesis` rollerinin ayni model mi yoksa farkli model/profil mi kullanacaginin netlestirilmesi.
- Retrieval bias katmaninin bugun eklenen ogrenci belgeleri/burs kurallarinin otesine gecip `transkript`, `burs`, `erasmus`, `yatay gecis`, `staj` gibi yuksek hacimli query aileleri icin ayrik benchmark setleriyle olculmesi.
- `_expand_candidate_context` tarafindaki tam-madde birlestirme mantiginin performans ve kapsam acisindan yeniden ele alinmasi; BM25 cache full-scan yerine daha dogrudan bir madde indeksine gecis.
- Dagitim tarafinda tekrarlanabilir bootstrap script'leri ve daha otomatik bir VM ilk kurulum akisi eklemek.
- HTTP benchmark sonuclari ile in-process benchmark sonuclarini ayri raporlayip karisik yorumu azaltmak.
- Duyuru ve retrieval verisinin kademeli yeniden indekslenmesi icin daha operasyonel bir komut seti eklemek.

## Dusuk Oncelik

- Best-effort hata bloklarindaki bazi genel `except Exception` kullanimlarini daha spesifik hata tiplerine indirmek.
- Geriye donuk uyumluluk icin tutulan bazi export modullerini sadeletirmek.
- Tarihsel faz dokumanlarini ileride tek bir "archive" girisi altinda toplamak.
- Warm-up varsayilanlarini dagitim tipine gore daha akilli hale getirmek.
- Azure disi alternatif ortamlar icin (Colab, Studio Lab, DigitalOcean GPU, Groq-only deployment) kisa bir karar tablosu veya operasyon notu hazirlamak.
