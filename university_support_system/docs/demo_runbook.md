# Demo Runbook

Bu dosya, sistemin yarin sunumda hizli ve kontrollu sekilde gosterilebilmesi icin hazirlandi.

## Guven Seviyesi

- `demo_showcase_stable_turk`
  - agirlikli olarak VT ve deterministic akislar kullanir
  - sunum icin en guvenli settir
- `demo_showcase_international`
  - uluslararasi ogrenci baglamini gostermek icin guvenlidir
  - ucret sorusu yine VT'den gelir
- `demo_showcase_broad_turk`
  - daha fazla farkli soru tipi ve ajan gostermek icin uygundur
  - canli kalitesi iyi ama sure olarak biraz daha uzayabilir
- `demo_showcase_broad_international`
  - uluslararasi ogrenci baglaminda daha cesitli soru repertuvari sunar
- `demo_showcase_llm_turk`
  - LLM sentezi ve coklu departman cevabini gosterir
  - en etkileyici ama en riskli settir
  - cevaplar kaynaklara dayali ozet niteligindedir; yonerge metninin bire bir kopyasi degildir
- `demo_followup_turk`
  - ayni context icinde follow-up sorularin onceki turla birlikte cozulmesini gosterir
  - yeni konusma hafizasi ozelligini gostermek icin en dogru settir

## Follow-up Ozelligi Icin Not

Bu ozelligin kalici calismasi icin yeni migration uygulanmis olmali:

```powershell
venv\Scripts\python.exe -m alembic upgrade head
```

## Hizli Test Paketi

Sunumdan once su komut yeterlidir:

```powershell
venv\Scripts\python.exe -m pytest tests\unit\test_router.py tests\unit\test_all_agents.py tests\unit\test_api.py tests\unit\test_orchestrators.py tests\unit\test_a2a_helpers.py tests\unit\test_system_e2e.py tests\unit\test_announcement_agent.py -q
```

## Sunum Komutlari

Calisma klasoru:

```powershell
cd "C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system"
```

### 1. Onboarding gosterimi

```powershell
venv\Scripts\python.exe scripts\live_question_test.py --benchmark demo_onboarding --use-api
```

### 2. En guvenli Turk ogrenci gosterimi

```powershell
venv\Scripts\python.exe scripts\live_question_test.py --benchmark demo_showcase_stable_turk --use-api --full-name "Test Ogrenci" --student-number "22060388" --student-department "Bilgisayar Muhendisligi" --student-faculty "Muhendislik Fakultesi" --student-type "Turk ogrenci"
```

### 3. Uluslararasi ogrenci farkli cevap gosterimi

```powershell
venv\Scripts\python.exe scripts\live_question_test.py --benchmark demo_showcase_international --use-api --full-name "Test Ogrenci" --student-number "22060388" --student-department "Bilgisayar Muhendisligi" --student-faculty "Muhendislik Fakultesi" --student-type "Uluslararasi ogrenci"
```

### 4. Daha cesitli Turk ogrenci gosterimi

```powershell
venv\Scripts\python.exe scripts\live_question_test.py --benchmark demo_showcase_broad_turk --use-api --full-name "Test Ogrenci" --student-number "22060388" --student-department "Bilgisayar Muhendisligi" --student-faculty "Muhendislik Fakultesi" --student-type "Turk ogrenci"
```

### 5. Daha cesitli uluslararasi gosterim

```powershell
venv\Scripts\python.exe scripts\live_question_test.py --benchmark demo_showcase_broad_international --use-api --full-name "Test Ogrenci" --student-number "22060388" --student-department "Bilgisayar Muhendisligi" --student-faculty "Muhendislik Fakultesi" --student-type "Uluslararasi ogrenci"
```

### 6. LLM sentez gosterimi

```powershell
venv\Scripts\python.exe scripts\live_question_test.py --benchmark demo_showcase_llm_turk --use-api --full-name "Test Ogrenci" --student-number "22060388" --student-department "Bilgisayar Muhendisligi" --student-faculty "Muhendislik Fakultesi" --student-type "Turk ogrenci"
```

### 7. Follow-up / konusma baglami gosterimi

```powershell
venv\Scripts\python.exe scripts\live_question_test.py --benchmark demo_followup_turk --use-api --full-name "Test Ogrenci" --student-number "22060388" --student-department "Bilgisayar Muhendisligi" --student-faculty "Muhendislik Fakultesi" --student-type "Turk ogrenci" --llm-profile balanced
```

## Sunumda Duz Dille Soylenebilecekler

- Ucret ve kayit donemi gibi yapilandirilmis bilgiler artik veritabanindan geliyor.
- Ders listesi ve on kosul gibi bilgiler bolum baglami ile veriliyor.
- Duyurular ayri bir veri yolundan geliyor.
- CAP gibi prosedur sorularinda sistem birden fazla departmandan bilgi toplayip tek cevapta birlestiriyor.
- Bu son grup cevaplar kaynaklara dayali ozet cevaplardir; mevzuat metninin bire bir yeniden basimi degildir.
