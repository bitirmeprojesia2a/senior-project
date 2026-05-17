# Dinamik Kurum Platformu Notu

Bu fazdaki temel garanti: mevcut OMU classic runtime degismez. Dinamik
platform katmani ayri bir profil/topoloji dogrulama katmanidir ve mevcut
Slack/API/router/agent akisina otomatik baglanmaz.

## Runtime Ayrimi

- `omu` profili `runtime_strategy: classic_protected` ile tanimlidir.
- Dynamic tenant profilleri `dynamic_shadow` gibi ayri stratejilerle baslar.
- Yeni `src.dynamic_platform` paketi mevcut runtime tarafindan import edilmez.
- Varsayilan Docker/Slack/rollout davranisi aynen korunur.

## Eklenen Kavramlar

- `tenant`: kurum/proje profili.
- `domain_pack`: universite, sirket, kamu hizmeti gibi alan paketi.
- `agent_pack`: tenant icin agent/specialist topolojisi.
- `capability`: agent adindan bagimsiz is yetenegi.
- `source_catalog`: kaynak adapterleri, source owner ve authority bilgisi.
- `Topology Builder`: dry-run agent/capability/source haritasi uretir.

## Ilk Profiller

- `omu`: mevcut OMU classic sisteminin korunmus profili.
- `acme_demo`: okul kavrami kullanmayan demo sirket tenant'i.

## CLI

```powershell
python -m scripts.tenant validate --tenant omu
python -m scripts.tenant plan --tenant acme_demo
python -m scripts.tenant compare-classic --tenant omu
python -m scripts.tenant source-audit --tenant omu
python -m scripts.tenant shadow-decisions --tenant omu
python -m scripts.tenant quality-gates --tenant omu
python -m scripts.tenant runtime-plan --tenant omu
python -m scripts.tenant runtime-env-check --tenant omu --env-file .env.example
python -m scripts.tenant init --tenant beta_demo --display-name "Beta Kurum" --bot-name "Beta Destek Botu" --domain corporate_support --agent-pack corporate_hr_it_support --dry-run
python -m scripts.tenant scaffold --tenant gamma_demo --display-name "Gamma Kurum" --bot-name "Gamma Destek Botu" --domain corporate_support --agent-pack corporate_hr_it_support --dry-run
python -m scripts.tenant export --tenant omu --output tmp\omu_dynamic_export.json
```

`init` yalniz tenant profili ve source catalog iskeleti uretir. `scaffold`
buna ek olarak replay fixture ve kurum runbook iskeleti de hazirlar. Iki komut
da runtime'a baglanmaz; yalniz profil hazirlama aracidir.

`shadow-decisions`, golden fixture'da tanimlanan beklenen capability/agent/source
karar sozlesmelerinin dinamik profilde temsil edilip edilmedigini offline
kontrol eder. Router, agent, RAG, veritabani veya LLM cagirmadigi icin mevcut
OMU cevabini degistirmez.

`source-audit`, source catalog kayitlarinin adapter, authority, owner agent,
source family ve capability sozlesmelerini dis sisteme baglanmadan denetler.
PDF/web/SQL/API/Slack dosyasi gibi kaynaklar kurumdan bagimsiz adapter
sozlesmeleriyle kontrol edilir.

`quality-gates`, `validate`, protected OMU icin `compare-classic`,
`source-audit` ve `shadow-decisions` kontrollerini tek offline kabul kapisinda
toplar. Yeni tenant scaffold edilirken shadow decision fixture da uretilir; bu
fixture doldurulmadan kalite kapisi gecmez.

`runtime-plan`, tenant'in Docker/runtime'a hangi environment degerleriyle
tasinabilecegini raporlar. Bu komut da runtime'i degistirmez. Su an OMU icin
`classic_runtime_active_dynamic_runtime_disabled`, yeni dynamic tenant'lar icin
`dynamic_profile_ready_shadow_only_runtime_not_wired` durumunu acikca gosterir.
Yani farkli kurum profili Docker'a hazirlanabilir, fakat live dynamic routing
ayri runtime adapter fazi baglanmadan aktif olmaz.

Docker servisleri `.env` dosyasini `env_file` olarak aldigi icin tenant runtime
degerleri `.env.example` icinde varsayilan OMU/classic-safe sekilde tutulur.
Farkli tenant icin:

```powershell
python -m scripts.tenant runtime-plan --tenant acme_demo --allow-missing-shadow --env-output tmp\acme_demo.tenant.env
```

Bu dosya dogrudan production'a baglanmaz; tenant env degerlerini incelemek veya
kontrollu olarak `.env` icine tasimak icin kullanilir. `DYNAMIC_PLATFORM_RUNTIME`
`shadow` olsa bile live routing adapter baglanmadigi surece Slack/API davranisi
degismez.

`runtime-env-check`, `.env` veya uretilmis tenant env dosyasinin profil ile
uyumlu olup olmadigini offline kontrol eder:

```powershell
python -m scripts.tenant runtime-env-check --tenant omu --env-file .env.example
python -m scripts.tenant runtime-env-check --tenant acme_demo --allow-missing-shadow --env-file tmp\acme_demo.tenant.env
```

Bu kontrol de servis baslatmaz. Sadece `TENANT_*` ve
`DYNAMIC_PLATFORM_RUNTIME` sozlesmesinin dogru tenant'a ait oldugunu ve live
dynamic runtime'in yanlislikla acilmadigini denetler.

## Devam Etmeden Once Kabul Kapisi

Dynamic platform runtime'a baglanmadan once:

1. OMU classic golden replay gecmeli.
2. Slack replay gecmeli.
3. `python -m scripts.tenant validate --tenant omu` OK vermeli.
4. `python -m scripts.tenant compare-classic --tenant omu` OK vermeli.
5. `python -m scripts.tenant source-audit --tenant omu` OK vermeli.
6. `python -m scripts.tenant shadow-decisions --tenant omu` OK vermeli.
7. `python -m scripts.tenant quality-gates --tenant omu` OK vermeli.
8. `python -m scripts.tenant runtime-plan --tenant omu` env-ready raporu vermeli.
9. `python -m scripts.tenant runtime-env-check --tenant omu --env-file .env.example` OK vermeli.
10. Dynamic config kararlari mevcut hardcoded kararlarla shadow olarak
   karsilastirilmali.

Bu kosullar saglanmadan dynamic tenant platformu production path'e baglanmaz.
